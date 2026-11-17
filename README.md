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
- **frontend-design**, **ui-ux-pro-max**, **example-skills** (webapp-testing), **interface-design** — UI stack driven by the `ui-development` skill
- [web-design-guidelines](https://github.com/vercel-labs/agent-skills) — pre-ship web audit; not a plugin dependency, install with `npx skills add vercel-labs/agent-skills --skill web-design-guidelines`

## Updating

The plugin version lives in `.claude-plugin/plugin.json`; after a push — if you installed it, `/plugins` shows an **Update** button for the marketplace.

## What's inside

| Skill | Purpose |
|---|---|
| `building-testable-apps` | 7 rules of headless development: an app = a pure library + auto-generated UI, every feature accepted by commands with no screen. Triggers on any app/feature creation. |
| `common-rules` | The operating rules for every session: never fabricate, think before coding, simplicity first, surgical changes, goal-driven execution, commit conventions, direct communication style, when to ask versus proceed. Routed from `using-skills` at the start of every conversation. |
| `ui-development` | Coordinator for any UI task — web and native GUIs: dispatches to the ready UI skills (frontend-design for taste, ui-ux-pro-max for style references, webapp-testing for web verification, interface-design for decision memory, web-design-guidelines for the pre-ship audit), runs the four-stage process (compose → layout → style → verify run/see/drive), and personally owns what the ready skills don't cover: desktop GUIs, quality states (loading/empty/error), the verification loop. Routed from `using-skills` on any UI work. |
| `using-skills` | Skill-discipline mandate: invoke matching skills before any response, hard routes to the plugin's skills (common-rules every conversation, building-testable-apps, ui-development for any UI task, TDD for all code). Injected at session start; not meant to trigger by description. |

## Hooks

| Hook | Purpose |
|---|---|
| `load-agent-rules` | SessionStart hook that injects the `using-skills` skill mandate into the session context on startup; from there every conversation is routed to the `common-rules` skill. |
| `protect-secrets` | PreToolUse hook that denies agent access to secrets: `.env` and `.env.*`, `*.pem`, `*.key`, and the `.secrets`/`.secret` folders — no reading, editing, or browsing them (including via Bash such as `cat .env`), and no staging or committing them with git. Files ending in `.example` / `.template` (e.g. `.env.example`) stay allowed. The git check looks at the real index, so a commit message that merely mentions `.env` is fine. |

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest
.claude-plugin/plugin.json        # plugin manifest (version lives here)
skills/                           # skills (auto-discovered)
hooks/hooks.json                  # SessionStart + PreToolUse hook registration (auto-registered)
scripts/protect-secrets.py        # the secrets-protection hook script
skills/common-rules/SKILL.md      # operating rules for every session (trigger-based, routed from using-skills)
tests/test_protect_secrets.py     # secret-protection hook tests (python3 tests/test_protect_secrets.py)
tests/test_common_rules_skill.py  # common-rules skill migration tests (python3 tests/test_common_rules_skill.py)
tests/test_using_skills_hook.py   # using-skills injection wiring tests (python3 tests/test_using_skills_hook.py)
```
