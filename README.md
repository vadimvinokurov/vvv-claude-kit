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
- [web-design-guidelines](https://github.com/vercel-labs/agent-skills) — pre-ship web audit; not a plugin dependency, install with `npx skills add vercel-labs/agent-skills --skill web-design-guidelines`

## Updating

The plugin version lives in `.claude-plugin/plugin.json`; after a push — if you installed it, `/plugins` shows an **Update** button for the marketplace.

## What's inside

| Skill | Purpose |
|---|---|
| `testable-apps-development` | 7 rules of headless development: an app = a pure library + auto-generated UI, every feature accepted by commands with no screen. Triggers on any app/feature creation. `ui-development` is its stated GUI companion: rules 6–7 (screen rendering, visual acceptance) are realized as the golden-render pipeline, the logic layer untouched. |
| `common-rules` | The operating rules for every session: never fabricate, think before coding, simplicity first, surgical changes, goal-driven execution, commit conventions, direct communication style, when to ask versus proceed. Routed from `using-skills` at the start of every conversation. |
| `dual-path-oracle` | Obligations for every non-obvious optimization: the naive reference twin ships in the same changeset, a named equality test on identical inputs lives forever (deleting it is a violation), the speedup is measured and recorded; plain orchestration is the boundary rule, not a pass on the rest. |
| `golden-rebaseline` | One triage protocol for any failed golden comparison (component/composite PNGs, data goldens): read the diff before opening artifacts, classify intended vs regression in the task text, an overwrite is accepted only with its before/after record made on the fresh render first, zero-diff-but-visible-change means logic moved, and a brand-new state has no "before". |
| `headless-text-rpc` | The operating mechanics behind `testable-apps-development` rule 6's text RPC: a capability and its check exist as a command before markup, button and command share one handler, argument typing lives at one boundary, test fakes repeat the real command shape, and the state snapshot is the acceptance ground. |
| `release-gates` | A release tag is published only after the project's `release_gates.sh` ran green on the exact commit being tagged (marker file as evidence); the gate list is the script, never memory; after publication a CI failure is an environment-diff task, not another tag push. Template script ships at `scripts/release_gates.sh`. |
| `subagent-contract` | The contract for delegating work: the spawn test (delegate vs stay inline), the five-field spawn prompt (tracker pointer, file partition, exact gates, call budget with checkpoint, report contract demanding gate outputs), supervision and drift control on the coordinator side, the agent-brief lifecycle (`docs/notes/agent-brief.md`), and the duties of the spawned agent itself. |
| `token-economy` | Session-side cost rules: every turn is a billed request, so budget tasks, read narrowly (ranges, not files, unless structure is the decision), no shell-escaping edits (Edit/Write, second failed shell edit → rewrite), a gates schedule (scoped file runs while iterating, full suite at milestones, no reruns answering no doubt), and the three-strikes kill on failure loops. Pairs with `subagent-contract` for spawning. |
| `ui-development` | Visual pipeline for agent-developed stateful apps: live component sources in `ui_design/ui_components/` are the single design truth, the design doc and golden PNGs are generated from them (never hand-edited), acceptance runs offline on per-component × variant goldens plus composite screens, and the real window is checked only at milestones. Entry point depends on infra state (pipeline present / hand-made doc → migrate / neither → bootstrap); explicit companion to `testable-apps-development` (logic layer untouched). |
| `using-skills` | Skill-discipline mandate: invoke matching skills before any response, hard routes to the plugin's skills (common-rules every conversation, testable-apps-development, TDD for all code). Injected at session start; not meant to trigger by description. |

## Hooks

| Hook | Purpose |
|---|---|
| `load-agent-rules` | SessionStart hook that injects the `using-skills` skill mandate into the session context on startup; from there every conversation is routed to the `common-rules` skill. |
| `protect-secrets` | PreToolUse hook that denies agent access to secrets: `.env` and `.env.*`, `*.pem`, `*.key`, and the `.secrets`/`.secret` folders — no reading, editing, or browsing them (including via Bash such as `cat .env`), and no staging or committing them with git. Files ending in `.example` / `.template` (e.g. `.env.example`) stay allowed. The git check looks at the real index, so a commit message that merely mentions `.env` is fine. |
| `no-repeat-call` | PostToolUse hook on Bash that annotates a rerun which returned output identical to the previous run of the same command — it bought no information — with a cue to change mechanism (editing tools, narrower gate, delegation). Any change in input or output resets the counter; the signal never denies the call. |
| `shell-edit-limit` | PreToolUse hook on Bash that denies the third shell modification of the same existing file in a session (`sed -i`, `tee`, redirects, `patch`…) and names the Write/Edit tools; file **creation** through the shell stays free, and a project may bypass via `.claude/shell-edits-allowlist` (one fnmatch pattern per line). |
| `skill-reminder` | PreToolUse hook on the path tools that adds one line naming the skill applying to the path being touched (mapping in `scripts/skill-reminders.json`, default: UI directories → `ui-development` + `token-economy`). |
| `release-tag-gate` | PreToolUse hook on Bash that refuses publishing a git tag (`push --tags`, `refs/tags/`, a named existing tag) unless the project's `.release-gates/last-run.json` marker says `ok: true` for the current HEAD — the marker is written by the kit's `release_gates.sh` template (skills/release-gates). Local tag creation and branch pushes stay allowed. |

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest
.claude-plugin/plugin.json        # plugin manifest (version lives here)
skills/                           # skills (auto-discovered)
hooks/hooks.json                  # SessionStart + PreToolUse + PostToolUse hook registration (auto-registered)
scripts/protect-secrets.py        # secrets-protection hook (PreToolUse)
scripts/shell-edit-limit.py       # third-shell-edit block (PreToolUse, per-session state)
scripts/release-tag-gate.py       # tag publication gate (PreToolUse, reads .release-gates/last-run.json)
scripts/release_gates.sh          # release-gates template: project fills GATES, marker written here
scripts/skill-reminder.py         # path → skill one-line reminder (PreToolUse)
scripts/skill-reminders.json      # the reminder mapping (data, edited freely)
scripts/no-repeat-call.py         # worthless-rerun annotator (PostToolUse, per-session state)
tests/test_protect_secrets.py     # secret-protection hook tests (python3 tests/test_protect_secrets.py)
tests/test_common_rules_skill.py  # common-rules skill migration tests (python3 tests/test_common_rules_skill.py)
tests/test_using_skills_hook.py   # using-skills injection wiring tests (python3 tests/test_using_skills_hook.py)
tests/test_no_repeat_call.py      # no-repeat annotator hook tests
tests/test_shell_edit_limit.py    # shell-edit-limit hook tests
tests/test_skill_reminder.py      # skill-reminder hook tests
tests/test_release_tag_gate.py    # release-tag-gate hook tests (real temp git repo)
```
