---
name: protect-secrets
description: Use when the user asks to protect secrets in a project, set up secret guards, or secure credentials handling (.env, keys, .secrets): asks what to protect, copies the secrets-guard engine into the project (.claude/hooks/protect_secrets.py) and registers a project-local PreToolUse hook in the project's .claude/settings.json.
---

# Protect Secrets — install a per-project secrets guard

**What this skill provisions:** a PreToolUse hook living **in the project**,
not in any plugin: the engine at `.claude/hooks/protect_secrets.py` (copied
from this skill's `references/protect_secrets.py`) registered in the
project's `.claude/settings.json`. The plugin carries no hooks of its own.

**What the engine covers by default** (paths match any path segment; `..`
resolved):

- files: `.env`, `.env.*`, `*.pem`, `*.key`
- dirs: `.secrets`, `.secret` — the folder and everything inside it
- always allowed: basenames ending in `.example` or `.template`
- blocked across Read/Grep/Glob/Write/Edit and Bash; git commits are decided
  by the real index, so a commit message mentioning `.env` stays allowed.
- Guards against ordinary agent behavior, not adversarial obfuscation.

## Questionnaire (AskUserQuestion — only what the repo cannot decide)

1. **Pattern set.** Offer the default set above as recommended; allow
   extensions via "Other" (e.g. `credentials*.json`, `id_rsa*`, `*.p12`,
   `.netrc`, `*.pem`-style vendor keys). Extensions are applied by editing
   the copied engine's `name_protected()` / `PROTECTED_DIR_NAMES` before
   (or after) installation — the template is editable project code.
   `.example`/`.template` exceptions always stay.
2. Nothing else: engine location, registration format and verification are
   fixed steps below.

## Install steps (exact)

1. `mkdir -p .claude/hooks`, copy this skill's
   `references/protect_secrets.py` → `.claude/hooks/protect_secrets.py`
   (apply any extension patterns to the copy first).
2. **Register in the project's `.claude/settings.json`** — merge, never
   overwrite: read the file if it exists and preserve every key you did not
   touch. Add to `hooks.PreToolUse` (create levels as needed; if a group with
   the same matcher exists, append to its `hooks` array):

```json
{
  "matcher": "Read|Grep|Glob|Write|Edit|Bash",
  "hooks": [
    {
      "type": "command",
      "command": "python3 .claude/hooks/protect_secrets.py",
      "timeout": 15
    }
  ]
}
```

3. **Verify with real calls** before reporting done:
   `echo '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | python3 .claude/hooks/protect_secrets.py`
   → deny JSON on stdout; the same with `README.md` → empty output, exit 0.
   Also one Bash probe (`cat .env` payload) → deny.
4. Report: the protected pattern set, where the engine and the registration
   live, the verify results, and that re-running this skill updates the copy
   and merge idempotently.

## Relation to the other skills

- `common-rules` §neverfabricate and `token-economy` §3 are session-side;
  this guard is project-side and mechanical — it does not depend on the
  agent's discipline.
- Removal: delete the PreToolUse group from `.claude/settings.json` and the
  `.claude/hooks/protect_secrets.py` file.
- Tests for the engine live in the plugin repo (`tests/test_protect_secrets.py`).
