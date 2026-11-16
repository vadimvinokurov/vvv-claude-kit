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

## Hard routes (no judgment calls)

- Any new application, module, or feature → `/building-testable-apps` (new code only — existing code is never rewritten to conform unless explicitly requested).
- Any code at all, including bugfixes in existing code → the `/superpowers:test-driven-development` cycle (RED → GREEN → REFACTOR).
- Any user interface — building, modifying, fixing → `/developing-ui`.

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
