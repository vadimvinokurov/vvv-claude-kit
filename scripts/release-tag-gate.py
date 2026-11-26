#!/usr/bin/env python3
"""PreToolUse hook of the vvv-claude-kit plugin: tag publication needs fresh green gates.

Wired via hooks/hooks.json for Bash. Per skills/release-gates/SKILL.md and
report-04 section 2.4: publishing a tag is allowed only when the project's
release-gates script ran successfully on the CURRENT commit — its marker
file .release-gates/last-run.json (written by scripts/release_gates.sh)
carries {"sha": <HEAD>, "ok": true}. Otherwise the push is denied with the
command to run. Local tag creation is not publication and stays allowed; a
push of non-tag refs stays allowed.

Guards against ordinary agent behavior. Git failures fail open silently.
Malformed input fails open silently. Tests: tests/test_release_tag_gate.py.
"""

import json
import os
import re
import subprocess
import sys

MARKER = os.path.join(".release-gates", "last-run.json")
DENIED_TEMPLATE = (
    "Tag publication without fresh green gates is refused (release-gates). "
    "No successful gate run exists for the current HEAD. Run "
    "`bash release_gates.sh` (configuring GATES in the project's copy of "
    "the script first, if it is still the template) and then publish."
)


def git_output(args, cwd):
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except OSError:
        return None
    return proc.stdout if proc.returncode == 0 else None


def push_publishes_tags(tokens, cwd):
    """True if a `git push` segment publishes tag refs (best effort)."""
    if tokens[0:1] != ["git"] or not tokens[1:2] or tokens[1] != "push":
        return False
    operands = [t for t in tokens[2:] if not t.startswith("-")]
    if any("--tags" in t for t in tokens):
        return True
    for token in tokens:
        if token.startswith("refs/tags/"):
            return True
    for operand in operands[1:]:  # first operand is the remote name
        if git_output(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{operand}"], cwd
        ):
            return True
    return False


def gates_current(cwd):
    head = git_output(["git", "rev-parse", "HEAD"], cwd)
    if not head:
        return None  # not a git repo — fail open
    try:
        with open(os.path.join(cwd, MARKER), "r", encoding="utf-8") as f:
            marker = json.load(f)
        if marker.get("ok") is True and marker.get("sha") == head.strip():
            return True
    except Exception:
        pass
    return False


def decide(payload):
    tool = payload.get("tool_name") or ""
    if tool != "Bash":
        return None
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return None
    cwd = payload.get("cwd") or os.getcwd()
    # Same segment splitting as protect-secrets.py: `&&`, `||`, `;`, `|` —
    # so a push late in a `;`-chain is still recognized.
    for segment in re.split(r"\|\||&&|[;|]", command):
        tokens = segment.split()
        if tokens and tokens[0] == "git" and len(tokens) > 1 and tokens[1] == "push":
            if push_publishes_tags(tokens, cwd):
                verdict = gates_current(cwd)
                if verdict is None:
                    return None  # not a git repository — fail open
                return "check" if verdict else "deny"
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    verdict = decide(payload)
    if verdict == "deny":
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": DENIED_TEMPLATE,
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
