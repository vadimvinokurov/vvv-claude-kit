#!/usr/bin/env python3
"""PreToolUse hook of the vvv-claude-kit plugin: third shell edit of a file is denied.

Wired via hooks/hooks.json for Bash. Per report-04 section 2.2 (and
token-economy §3): shell edits of files fight quoting instead of the task; on
the third modification attempt of the same existing file in one session the
hook denies the call and names the editing tools.

Only modifications of files that already exist are counted — creating files
through the shell is legitimate. Denial is bypassable per project: file
.claude/shell-edits-allowlist (in the project cwd), one shell-fnmatch pattern
per line (paths, basenames, e.g. `migrations/*`, `*.generated.ts`).

State lives in $TMPDIR/claude-kit-hooks/<session>/shell-edits.json.
This is a heuristic over command text, guarding against ordinary agent
behavior, not adversarial obfuscation. Malformed input fails open silently.
Tests: tests/test_shell_edit_limit.py.
"""

import fnmatch
import hashlib
import json
import os
import re
import sys

MAX_EDITS = 2  # the third attempt (count would become 3) is denied

STATE_DIR = os.path.join(
    os.environ.get("TMPDIR", "/tmp"), "claude-kit-hooks"
)
ALLOWLIST = os.path.join(".claude", "shell-edits-allowlist")

REDIRECT = re.compile(r"(?<![-\w])[2>&]{0,2}(>>?|>&\d)\s*([^\s;&|<>\"']+)")
DENIED_MESSAGE = (
    "This is the 3rd shell edit of the same file ({path}) in this session. "
    "Shell edits fight quoting instead of the task — use the Write/Edit "
    "tools for this file (token-economy §3). Routed workarounds "
    "(migrations, generated code) go into .claude/shell-edits-allowlist."
)

# Commands whose non-flag operands are edited paths (best effort heuristic).
# `touch` is deliberately absent: it only changes mtime, counting it as an
# edit produced false denials.
EDIT_COMMANDS = {
    "sed": re.compile(r"^sed\b"),
    "perl": re.compile(r"^perl\b"),
    "patch": re.compile(r"^patch\b"),
    "truncate": re.compile(r"^truncate\b"),
}


def state_path(session_id):
    key = hashlib.sha1(str(session_id).encode("utf-8")).hexdigest()[:16]
    return os.path.join(STATE_DIR, key, "shell-edits.json")


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_state(path, state):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def allowlist_patterns(cwd):
    try:
        with open(os.path.join(cwd, ALLOWLIST), "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except Exception:
        return []


def allowed_by(patterns, path):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(
            os.path.basename(path), pattern
        ):
            return True
    return False


def extract_targets(segment, cwd):
    """Existing-file paths the shell segment would modify (best effort)."""
    tokens = segment.split()
    targets = []
    if tokens and tokens[0] == "sed" and any(
        "-i" == t or t.startswith("-i") or t.startswith("--in-place") for t in tokens
    ):
        targets.extend(t for t in tokens[1:] if not t.startswith("-"))
    elif tokens and tokens[0] == "perl" and any(
        t.startswith("-pi") or t.startswith("-pe") or t.startswith("-i") for t in tokens
    ):
        for i, t in enumerate(tokens):
            if t == "-e" and i + 1 < len(tokens):
                targets.extend(x for x in tokens[i + 2:] if not x.startswith("-"))
    elif tokens and tokens[0] in ("patch", "truncate"):
        targets.extend(t for t in tokens[1:] if not t.startswith("-"))
    if tokens and tokens[0] == "tee":
        operands = [t for t in tokens[1:] if not t.startswith("-")]
        for t in operands:
            m = REDIRECT.search(t)
            targets.append(m.group(2) if m else t)
    for match in REDIRECT.finditer(segment):
        targets.append(match.group(2))
    resolved = []
    for raw in targets:
        path = raw.strip("'\"")
        if not path:
            continue
        if not os.path.isabs(path):
            path = os.path.normpath(os.path.join(cwd, path))
        if os.path.isfile(path):
            resolved.append(path)
    return resolved


def count_and_decide(command, cwd, session_id):
    state_file = state_path(session_id)
    state = load_state(state_file)
    counted = []
    for segment in re.split(r"\|\||&&|[|;&]", command):
        for target in extract_targets(segment, cwd):
            if allowed_by(allowlist_patterns(cwd), target):
                continue
            counted.append(target)
    for target in counted:
        n = int(state.get(target, 0))
        if n >= MAX_EDITS:
            return {
                "decision": "deny",
                "reason": DENIED_MESSAGE.format(path=target),
            }
    for target in counted:
        state[target] = int(state.get(target, 0)) + 1
    if counted:
        save_state(state_file, state)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    decision = (
        count_and_decide(command, payload.get("cwd") or os.getcwd(), payload.get("session_id") or "unknown")
        if tool == "Bash" and isinstance(command, str)
        else None
    )
    if decision:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": decision["reason"],
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
