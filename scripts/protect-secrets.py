#!/usr/bin/env python3
"""PreToolUse hook of the vvv-claude-kit plugin: blocks agent access to secrets.

Wired up via hooks/hooks.json for every Read/Grep/Glob/Write/Edit/Bash call.
Reads the hook payload JSON on stdin; on denial prints a PreToolUse
permission decision (exit 0), otherwise prints nothing and exits 0.
Malformed input fails open silently.

What is protected (paths match any segment, `..` is resolved; new
locations are added to this list by an explicit change, not heuristics):
- files: `.env`, `.env.*`, `*.pem`, `*.key`  (e.g. `.env.local`, `server.pem`)
- dirs:  `.secrets`, `.secret` — the folder and everything inside it
- always allowed: files ending in `.example` / `.template` (e.g. `.env.example`)

Rules: file-giving tools are denied by path; other Bash commands are
denied when a token names a protected path; `git add/commit/rm/mv/cp/stash`
are decided by the real git index (staged / dirty files), not by the
command text, so a commit message mentioning `.env` stays allowed.
Guards against ordinary agent behavior, not adversarial obfuscation.

Tests: tests/test_protect_secrets.py (run `python3 tests/test_protect_secrets.py`).
"""

import json
import os
import re
import subprocess
import sys

PROTECTED_DIR_NAMES = {".secrets", ".secret"}
SAFE_SUFFIXES = (".example", ".template")

# Tools whose input is a path or pattern string.
TOOLS_WITH_STRING_INPUT = {
    "Read": ("file_path",),
    "Write": ("file_path",),
    "Edit": ("file_path",),
    "Grep": ("path", "pattern"),
    "Glob": ("path", "pattern"),
}

# Bash segments containing these git subcommands are decided by scanning
# the real index (git status --porcelain), not the command text — so a
# legitimate commit message may mention `.env` without being blocked.
GIT_INDEX_SUBCOMMANDS = {"add", "commit", "rm", "mv", "cp", "stash"}

# Shell segment separators for compound commands.
SEGMENT_SPLIT = re.compile(r"\|\||&&|;|\|")
# Token separators within one shell segment.
TOKEN_SPLIT = re.compile("[\\s='\"|:&,()]+")

DENIED_TOOLS_FOR_BASH_MESSAGE = "Protected secrets path blocked: {what}"


def name_protected(name):
    """True if a single path component is a protected file name."""
    if name.endswith(SAFE_SUFFIXES):
        return False
    stem = name.strip("*")  # tolerate glob-style patterns like `.env*`, `*.pem`
    if stem == ".env" or stem.startswith(".env."):
        return True
    if stem.endswith(".pem") or stem.endswith(".key"):
        return True
    return False


def path_segments(raw):
    """Split a path-ish string into resolved dot-path components."""
    segments = []
    for part in raw.split("/"):
        part = part.strip()
        if part in ("", "."):
            continue
        if part == "..":
            if segments:
                segments.pop()
            continue
        segments.append(part)
    return segments


def is_protected_path(raw):
    """True if any component of a path/pattern is a protected name or dir."""
    for segment in path_segments(raw):
        if segment in PROTECTED_DIR_NAMES:
            return True
        if name_protected(segment):
            return True
    return False


def mentions_protected_name(text):
    """True if a free-form string (regex pattern, etc.) names a protected path."""
    normalized = text.replace("\\", "")
    return any(
        is_protected_path(token)
        for token in TOKEN_SPLIT.split(normalized)
        if token
    )


def parse_porcelain(status_output):
    """Paths (one per line, renames resolved) from porcelain output lines."""
    paths = []
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip().strip('"'))
    return paths


def index_has_protected_files(status_output):
    """True if `git status --porcelain` output lists any protected path."""
    return any(is_protected_path(p) for p in parse_porcelain(status_output))


def git_output(args, cwd):
    """stdout of a git command in cwd, or None on any failure."""
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def porcelain_paths(cwd, include_untracked):
    """Paths shown by `git status --porcelain` in cwd, None on git failure."""
    status = git_output(
        ["git", "-c", "core.quotePath=false", "status", "--porcelain"], cwd
    )
    if status is None:
        return None
    lines = status.splitlines()
    if not include_untracked:
        lines = [line for line in lines if not line.startswith("??")]
    return parse_porcelain("\n".join(lines))


def decide_git(tokens, cwd):
    """Decide one shell segment that starts with `git`. None = not denied."""
    subcommands = [t for t in tokens[1:] if t in GIT_INDEX_SUBCOMMANDS]

    def deny_paths(paths, label):
        for path in paths:
            if is_protected_path(path):
                return denied(f"protected secrets files would be {label}: {path}")
        return None

    if not subcommands:
        for token in tokens[1:]:
            if mentions_protected_name(token):
                return denied(f"protected secrets path in command: {token}")
        return None

    for sub in subcommands:
        if sub == "commit":
            staged = git_output(["git", "diff", "--cached", "--name-only"], cwd)
            if staged:
                decision = deny_paths(staged.splitlines(), "committed")
                if decision:
                    return decision
            if "-a" in tokens:
                tracked = porcelain_paths(cwd, include_untracked=False)
                if tracked is not None:
                    decision = deny_paths(tracked, "committed")
                    if decision:
                        return decision
            continue

        if sub == "stash":
            include_untracked = any(t in ("-u", "-a") for t in tokens)
            paths = porcelain_paths(cwd, include_untracked)
            if paths is not None:
                decision = deny_paths(paths, "stashed")
                if decision:
                    return decision
            continue

        # add / rm / mv / cp: operands name the paths directly; only a
        # wildcard operand would pull in other files, so scan the status.
        operands = [
            t for t in tokens[1:]
            if t not in GIT_INDEX_SUBCOMMANDS and not t.startswith("-")
        ]
        decision = deny_paths(operands, "added")
        if decision:
            return decision
        if any(t in (".", "./", "*", "-A", "-a", "-all") for t in tokens):
            wildcard = porcelain_paths(cwd, include_untracked=True)
            if wildcard is not None:
                decision = deny_paths(wildcard, "added")
                if decision:
                    return decision
    return None


def decide_bash(command, cwd):
    decision_or_none = None
    for segment in SEGMENT_SPLIT.split(command):
        tokens = [t for t in TOKEN_SPLIT.split(segment) if t]
        if tokens and tokens[0] == "git":
            decision_or_none = decide_git(tokens, cwd)
        else:
            for token in tokens:
                if is_protected_path(token) or mentions_protected_name(token):
                    decision_or_none = denied(f"protected secrets path in command: {token}")
                    break
        if decision_or_none:
            break
    return decision_or_none or allowed()


def denied(reason):
    return {"decision": "deny", "reason": reason}


def allowed():
    return {"decision": "allow"}


def decide(payload):
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return allowed()

    if tool == "Bash":
        command = tool_input.get("command")
        if isinstance(command, str):
            cwd = payload.get("cwd") or os.getcwd()
            return decide_bash(command, cwd)
        return allowed()

    if tool in TOOLS_WITH_STRING_INPUT:
        for key in TOOLS_WITH_STRING_INPUT[tool]:
            value = tool_input.get(key)
            if isinstance(value, str) and (
                is_protected_path(value) or mentions_protected_name(value)
            ):
                return denied(f"protected secrets path blocked: {key}={value}")
    return allowed()


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    result = decide(payload)
    if result["decision"] == "deny":
        decision = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": result["reason"],
            }
        }
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
