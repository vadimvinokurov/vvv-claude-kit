# vvv-claude-kit

A personal collection of skills and hooks for Claude Code.

## Install

```text
/plugin marketplace add vadimvinokurov/vvv-claude-kit
```

then in `/plugins` install **vvv-claude-kit** (or with the command):

```text
/plugin install vvv-claude-kit@vvv-claude-kit
```

Installing the plugin also installs its dependencies from the official `claude-plugins-official` marketplace:

- **superpowers** — disciplined skill-driven workflow
- **context7** — up-to-date library documentation lookup (MCP)

## Updating

The plugin version lives in `.claude-plugin/plugin.json`; after a push — if you installed it, `/plugins` shows an **Update** button for the marketplace.

## What's inside

| Skill | Purpose |
|---|---|
| `building-testable-apps` | 7 rules of headless development: an app = a pure library + auto-generated UI, every feature accepted by commands with no screen. Triggers on any app/feature creation. |

## Hooks

| Hook | Purpose |
|---|---|
| `load-agent-rules` | SessionStart hook that injects the plugin's agent rules (`common_agent_rules.md`) into the session context on startup. |
| `protect-secrets` | PreToolUse hook that denies agent access to secrets: `.env` and `.env.*`, `*.pem`, `*.key`, and the `.secrets`/`.secret` folders — no reading, editing, or browsing them (including via Bash such as `cat .env`), and no staging or committing them with git. Files ending in `.example` / `.template` (e.g. `.env.example`) stay allowed. The git check looks at the real index, so a commit message that merely mentions `.env` is fine. |

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest
.claude-plugin/plugin.json        # plugin manifest (version lives here)
skills/                           # skills (auto-discovered)
hooks/hooks.json                  # SessionStart + PreToolUse hook registration (auto-registered)
scripts/protect-secrets.py        # the secrets-protection hook script
common_agent_rules.md             # agent rules injected into context at session start (load-agent-rules)
tests/test_protect_secrets.py     # secret-protection hook tests (python3 tests/test_protect_secrets.py)
tests/test_rules_hook.py          # rules-hook wiring tests (python3 tests/test_rules_hook.py)
```
