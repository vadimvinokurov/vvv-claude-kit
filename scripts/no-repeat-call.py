#!/usr/bin/env python3
"""PostToolUse hook of the vvv-claude-kit plugin: flags worthless repeats.

Wired via hooks/hooks.json for Bash. Per report-04 section 2.1: a rerun that
brings no new information (same command, same output as the previous run of
that command) is annotated with a cue to change mechanism; any change in input
or output resets the count. The annotation is a signal, not a denial — the
agent may continue differently or explain why the repeat was meaningful.

State lives in $TMPDIR/claude-kit-hooks/<session>/no-repeat.json.
Malformed input fails open silently. Tests: tests/test_no_repeat_call.py.
"""

import hashlib
import json
import os
import sys

CUE = (
    "This rerun returned output identical to the previous run of the same "
    "command ({n} identical runs): it brings no new information. Change "
    "mechanism instead — rewrite the file with the editing tools, run a "
    "narrower gate on one module, or delegate per subagent-contract; "
    "token-economy kills a rerun loop at the third strike."
)

STATE_DIR = os.path.join(
    os.environ.get("TMPDIR", "/tmp"), "claude-kit-hooks"
)


def state_path(session_id):
    key = hashlib.sha1(str(session_id).encode("utf-8")).hexdigest()[:16]
    return os.path.join(STATE_DIR, key, "no-repeat.json")


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


def decide(payload):
    tool = payload.get("tool_name") or ""
    if tool != "Bash":
        return None
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return None
    response = payload.get("tool_response")
    resp_hash = hashlib.sha1(
        json.dumps(response, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()

    path = state_path(payload.get("session_id") or "unknown")
    state = load_state(path)
    cmd_key = hashlib.sha1(command.encode("utf-8")).hexdigest()
    entry = state.get(cmd_key)
    if entry and entry.get("resp") == resp_hash:
        entry["count"] = int(entry.get("count", 1)) + 1
        state[cmd_key] = entry
        save_state(path, state)
        return CUE.format(n=entry["count"])
    state[cmd_key] = {"resp": resp_hash, "count": 1}
    save_state(path, state)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    cue = decide(payload)
    if cue:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": cue,
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
