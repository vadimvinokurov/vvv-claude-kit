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

## Updating

The plugin version lives in `.claude-plugin/plugin.json`; after a push — if you installed it, `/plugins` shows an **Update** button for the marketplace.

## What's inside

| Skill | Purpose |
|---|---|
| `building-testable-apps` | 7 rules of headless development: an app = a pure library + auto-generated UI, every feature accepted by commands with no screen. Triggers on any app/feature creation. |

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest
.claude-plugin/plugin.json        # plugin manifest (version lives here)
skills/                           # skills (auto-discovered)
hooks/                            # hooks (coming in a later release)
```
