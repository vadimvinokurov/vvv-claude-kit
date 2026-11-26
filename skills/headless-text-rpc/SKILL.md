---
name: headless-text-rpc
description: Use when adding an interactive capability to a stateful app (web, desktop) or wiring its checks. The text-RPC obligations: one shared handler for button and command, typing at one boundary, real-shaped command fakes, and the state snapshot as the acceptance ground.
---

# Headless Text RPC — every capability is checkable with no screen

**Why this exists:** the foundation of all honest UI verification. Tests read
state snapshots, a harness drives the screen into a state through commands
before a golden comparison, and the live-window check drives through the same
commands. Without this interface an agent cannot truthfully verify the app and
starts eyeballing markup and guessing. (`testable-apps-development` rule 6
states the requirement; this skill carries its operating mechanics.)

## Obligations

1. **Capability and check before markup.** A new interactive capability exists
   in the text interface before it exists on screen: it ships with a command
   and a check that passes. Evidence: the command returns a full state snapshot
   through which the capability is asserted. Accepting markup whose capability
   has no command is a defect, not a shortcut.

2. **One handler behind both paths.** The button and the text command perform
   the same action because they call the same handler — duplicated logic is a
   violation. Evidence: a test invokes both paths and asserts the state
   snapshot changes identically.

3. **Typing lives at one boundary.** Commands arrive as untyped values; argument
   coercion and validation happen in one place, in the command layer. Nothing
   untyped crosses into the runtime — a `null` or string that silently replaced
   a number inside the runtime is the documented bug class here (untyped arg
   reaching a runtime bridge as null). Evidence: malformed input is rejected at the
   boundary test, never deep inside.

4. **Fakes keep the real shape.** Test doubles for external systems repeat the
   form of the commands those systems actually carry — same call shape, same
   response shape — so harness checks read the same either way. A fake that
   only the test can drive through is a second interface, not a double.

5. **Snapshot is the acceptance ground.** Assertions for capabilities read the
   state snapshot, not rendering internals. A check that cannot be expressed as
   (command → snapshot → assertion) is a design smell: the capability is not
   yet state-first — split it.

## Reference shape (minimal, from the project that produced this skill)

- State model: one struct/record holding all interactive state.
- Snapshot: one command returning the whole state as plain text/JSON.
- Capability: one command end-to-end — parse args (typed at boundary) →
  mutate state through the shared handler → return the new snapshot. The UI
  element calls the same handler; the test calls the same handler.

## Relation to the other skills

- `testable-apps-development` rule 6: this is its "text RPC — always" half,
  made operational.
- `ui-development`: the golden harness drives screens into state through these
  commands; `golden-rebaseline`'s triage assumes a check could have been run
  through them. If a UI state cannot be reached by command, that is the bug
  to fix first.
- `token-economy` §4: capability checks run as the module gate while iterating.
