#!/usr/bin/env python3
"""PreToolUse hook of the vvv-claude-kit plugin: one-line skill reminders.

Wired via hooks/hooks.json for Read/Grep/Glob/Write/Edit. Per report-04
section 2.3: when a call targets a path in a skill-mapped directory, the hook
adds one line naming the skill that applies there — a reminder, never a
summary of the skill. The mapping lives next to this script in
scripts/skill-reminders.json (segments → line) and is data, edited freely.
Malformed input fails open silently. Tests: tests/test_skill_reminder.py.
"""

import json
import os
import sys

MAPPING_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "skill-reminders.json"
)


def load_reminders():
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("reminders", [])
    except Exception:
        return []


def segments(path):
    out = []
    for part in str(path).split("/"):
        part = part.strip().strip('"')
        if part and part not in (".", ".."):
            out.append(part.lower())
    return out


def reminder_for(path):
    psegs = segments(path)
    for entry in load_reminders():
        wanted = {str(s).lower() for s in entry.get("segments", [])}
        if wanted and wanted.intersection(psegs):
            return entry.get("line", "").strip()
    return None


def decide(payload):
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None
    path = tool_input.get("file_path") or tool_input.get("path")
    if not isinstance(path, str):
        return None
    return reminder_for(path)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    line = decide(payload)
    if line:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "additionalContext": line,
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
