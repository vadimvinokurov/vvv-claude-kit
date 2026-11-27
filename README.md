# vvv-claude-kit

A personal collection of skills and hooks for Claude Code, designed as a
companion to the `superpowers` plugin: superpowers owns the process pipelines,
this kit carries the operating layer around them (rules, testability
contracts, token economics, UI pipeline, release gates).

## Install

```text
/plugin marketplace add vadimvinokurov/vvv-claude-kit
```

then in `/plugins` install **vvv-claude-kit** (or with the command):

```text
/plugin install vvv-claude-kit@vvv-claude-kit
```

Installing the plugin also installs its dependencies from the official `anthropic-plugin-directory` marketplace:

- **superpowers** — disciplined skill-driven workflow
- [web-design-guidelines](https://github.com/vercel-labs/agent-skills) — pre-ship web audit; not a plugin dependency, install with `npx skills add vercel-labs/agent-skills --skill web-design-guidelines`

## Updating

The plugin version lives in `.claude-plugin/plugin.json`; after a push — if you installed it, `/plugins` shows an **Update** button for the marketplace.

## Releasing

This repository uses the kit it ships: `.claude/settings.json` in this repo
registers the `release-tag-gate` project-local hook (installed by the kit's
own `/release-tag-gate` skill — dogfooding), root `release_gates.sh` runs all
hook/skill tests and writes the `.release-gates/last-run.json` marker, and
the hook refuses to publish a tag without a green marker for the exact commit
being tagged. The same test list runs on GitHub Actions
(`.github/workflows/tests.yml`).

## What's inside

| Skill | Purpose |
|---|---|
| `testable-apps-development` | 7 rules of headless development: an app = a pure library + auto-generated UI, every feature accepted by commands with no screen. Triggers on any app/feature creation; a three-line exit check at the top of the skill disqualifies refactoring/bugfix work before the rules are read (that work follows the superpowers TDD cycle). `ui-development` is its stated GUI companion: rules 6–7 (screen rendering, visual acceptance) are realized as the golden-render pipeline, the logic layer untouched. |
| `common-rules` | The operating rules for every session: never fabricate, think before coding, simplicity first, surgical changes, goal-driven execution, commit conventions, direct communication style, when to ask versus proceed. Injected into every session by the `load-common-rules` SessionStart hook; also trigger-based by description. |
| `dual-path-oracle` | Obligations for every non-obvious optimization: the naive reference twin ships in the same changeset, a named equality test on identical inputs lives forever (deleting it is a violation), the speedup is measured and recorded; plain orchestration is the boundary rule, not a pass on the rest. |
| `golden-rebaseline` | One triage protocol for any failed golden comparison (component/composite PNGs, data goldens): read the diff before opening artifacts, classify intended vs regression in the task text, an overwrite is accepted only with its before/after record made on the fresh render first, zero-diff-but-visible-change means logic moved, and a brand-new state has no "before". |
| `headless-text-rpc` | The operating mechanics behind `testable-apps-development` rule 6's text RPC: a capability and its check exist as a command before markup, button and command share one handler, argument typing lives at one boundary, test fakes repeat the real command shape, and the state snapshot is the acceptance ground. |
| `release-gates` | A release tag is published only after the project's `release_gates.sh` ran green on the exact commit being tagged (marker file as evidence); the gate list is the script, never memory; after publication a CI failure is an environment-diff task, not another tag push. Installer: `release-tag-gate`; the template script and the project-local gate hook ship in that skill. |
| `token-economy` | Session-side cost rules: every turn is a billed request, so budget tasks, read narrowly (ranges, not files, unless structure is the decision), no shell-escaping edits (Edit/Write, second failed shell edit → rewrite), a gates schedule (scoped file runs while iterating, full suite at milestones, no reruns answering no doubt), the three-strikes kill on failure loops, and the spawn filter (delegate or stay inline) with the minimal spawn prompt contract. |
| `ui-development` | Visual pipeline for agent-developed stateful apps: live component sources in `ui_design/ui_components/` are the single design truth, the design doc and golden PNGs are generated from them (never hand-edited), acceptance runs offline on per-component × variant goldens plus composite screens, and the real window is checked only at milestones. Entry point depends on infra state (pipeline present / hand-made doc → migrate / neither → bootstrap); explicit companion to `testable-apps-development` (logic layer untouched). |
| `protect-secrets` | Per-project secrets guard: an installer skill that asks what to protect, copies the engine to the project's `.claude/hooks/protect_secrets.py` and registers a project-local PreToolUse hook in the project's `.claude/settings.json`. Default coverage: `.env`, `.env.*`, `*.pem`, `*.key`, `.secrets`/`.secret`; `.example`/`.template` stay allowed; git commits decided by the real index. No plugin hook — the guard lives in the project. |
| `release-tag-gate` | Per-project release gate: an installer skill that discovers gate commands, asks what a release must run (full suite → strict type check → interface tests → goldens by default), writes the project's `release_gates.sh` with filled `GATES` and installs the project-local tag hook; publication of a tag is refused until a green marker exists for the tagged commit. Companion protocol: `release-gates`. |

## Hooks

| Hook | Purpose |
|---|---|
| `load-session-rules` | SessionStart hook that injects the session rules into every session's context — `common-rules` (operating policy) and `token-economy` (cost rules and the spawn protocol). Guaranteed present, not probabilistically triggered. |

The plugin ships exactly one hook (`load-session-rules`); project-level
guards are installed per project by the `protect-secrets` and
`release-tag-gate` skills (engine copied into `.claude/hooks/`, registration
merged into the project's `.claude/settings.json`).

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest
.claude-plugin/plugin.json        # plugin manifest (version lives here)
skills/                           # skills (auto-discovered); installer skills carry
                                  # their hook engine + templates in references/
hooks/hooks.json                  # SessionStart-only hook registration (auto-registered)
release_gates.sh                  # THIS repository's own release gates (dogfooding)
.github/workflows/tests.yml       # CI running the same test list
tests/test_protect_secrets.py     # secret-protection hook tests (python3 tests/test_protect_secrets.py)
tests/test_common_rules_skill.py  # common-rules skill migration tests (python3 tests/test_common_rules_skill.py)
tests/test_session_rules_hook.py  # SessionStart session-rules injection wiring tests
tests/test_release_tag_gate.py    # release-tag-gate hook tests (real temp git repo)
```
