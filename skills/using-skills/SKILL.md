---
name: using-skills
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response; injected unconditionally by the plugin's SessionStart hook, so the description rarely triggers it directly
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it. Then announce "Using [skill] to [purpose]" and follow the skill exactly.

## Relation to superpowers

This plugin works as a **companion to the superpowers plugin**, not a
replacement: superpowers owns the process pipelines (brainstorming → plans →
TDD → debugging → worktrees → code review), and this kit's skills carry the
operating layer those pipelines run inside — `common-rules` (discipline),
`testable-apps-development` + `headless-text-rpc` (what a feature must satisfy
to be done), `token-economy` + `subagent-contract` (request and context
economics of running those pipelines), `ui-development`, `release-gates`, and
the golden/oracle skills. Invoke superpowers skills for the process and this
kit's skills for the discipline around them; neither list is optional when
routed.

**When the two layers disagree, resolve by subject, not by rank:** questions
of *process* (whether to brainstorm, plan, or write a test first) go to
superpowers; questions of *execution discipline* (budgets, gates schedule,
reading, spawning economics) go to this kit. If a routing conflict cannot be
resolved that way, prefer the skill that is more specific to the current tool
or event, and state the choice in one line before proceeding.

## Hard routes (no judgment calls)

- Every conversation → `/common-rules` — the operating rules (never fabricate, think before coding, simplicity, surgical changes, verified goals, commits, communication style, when to ask).
- Any new application, module, or feature → `/testable-apps-development` (new code only — existing code is never rewritten to conform unless explicitly requested).
- Any code at all, including bugfixes in existing code → the `/superpowers:test-driven-development` cycle (RED → GREEN → REFACTOR).

## Red Flags

These thoughts mean STOP — you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "It's a small/trivial change" | The discipline applies to all sizes. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I remember this skill" | Skills evolve. Invoke the current version. |

## Priority

User instructions (CLAUDE.md, direct requests) take precedence over skills, which in turn override default behavior. Skip a skill workflow only when your human partner explicitly tells you to.
