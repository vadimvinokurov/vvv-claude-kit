---
name: subagent-contract
description: Use when delegating - at the moment of deciding whether to spawn a subagent, when writing or reviewing a spawn prompt, while supervising a running agent, and when you yourself are the spawned agent executing such a task. Carries the spawn test (delegate vs stay inline), the five-field spawn contract, budgets and checkpoints for agents, waiting rules, the project agent-brief lifecycle (docs/notes/agent-brief.md), and what a subagent must report to be accepted. Invoke token-economy for session-side context rules.
---

# Subagent Contract — spawning, supervising, being the agent

**Why this exists:** an agent's noise (test output, file dumps, retries) is cheaper
inside a subagent's own context, which nobody replays; only the summary returns. But
an uncapped subagent is the biggest spending class (documented: agents at 628k+
tokens after cap rules were written). The contract below keeps agents cheap without
making them timid. Session-side context rules (reading, gates, editing) live in
`token-economy` — both sides follow them.

## 1. Spawn test — delegate or stay inline

**Spawn:** would the work cost me more than ~3–5 tool calls or more than one gate
cycle, **and** can I name the file boundary up front (any number of files inside a
boundary I can name)? Yes → delegate. No boundary yet? Finding it is a delegable
first question.

**Delegate:** module builds with test loops; multi-file analysis; gate/debug
cycles; log mining; benchmark runs.

**Stay inline:** edits of roughly ≤5 self-contained calls; shared-file integration
(`lib.rs`, `Cargo.toml`, `App.tsx`); judgment calls needing the live conversation;
a single-fact lookup cheaper than the spawn. An inline task that outgrows this
mid-flight becomes a delegation candidate — don't let an inline task grow into a
fat turn.

**Parallelism:** two or three narrow agents beat one fat one; parallel only with
file boundaries agreed before spawn (pre-created stubs, pre-added dependencies).

## 2. The five-field spawn prompt

A spawn prompt over ~15 lines is a smell: missing context belongs in the brief or
the tracker item, never in the next prompt. The prompt is pointers only — restating
spec semantics inline re-pays the same decode for every agent.

```
<bead id> — read docs/notes/agent-brief.md + <spec section>.
Touch only: <files inside this partition>.
Gates: <exact commands>, from <cwd>.
Budget: ≤ ~50 tool calls (or the ceiling the coordinator set); nearing it —
checkpoint (tracker note: done / remaining) and either stop or ask the coordinator
for one extension with a stated ceiling. Never split the task yourself.
Report: files changed; gates with their actual outputs (command, counts, exit
codes — "all green" is not reporting); risks/follow-ups. Final report in
<owner language>. Hand any wait over ~2 min back as "background, id X" — no
sleep-polling.
```

Fields: (1) tracker item + brief pointer, (2) file partition, (3) exact gates with
cwd, (4) budget with checkpoint instruction, (5) report contract with gate outputs,
owner language, and no sleep-polling.

## 3. If you are the agent spawned by that prompt

- Read the brief + the tracker item first; the plan holds the pointers, the working
  tree is the truth when they diverge.
- Treat your budget as an alarm, not a quota: nearing it, post a tracker note (what
  is done, what remains), then stop or ask the coordinator for one extension with a
  stated ceiling. Never silently split or grow the task.
- Checkpoint to the tracker at every milestone, mid-task included — a dead agent
  without notes is a total loss; with notes, a 5-minute restart.
- Detach background work and wake on its completion notification; no sleep-polling
  (a spin-wait pays your whole context per round for zero output).
- Your report must carry gate outputs, not claims. Spawn with verified model names
  or defaults — no unverified overrides.

## 4. Supervising a running agent (coordinator side)

- Monitor by notification, not by polling; the coordinator's context replays on
  every future turn — an idle check-in costs a full-context request.
- Drift control: ~2× the planned call budget → stop and assess. Clearly converging
  → checkpoint + one extension with a stated ceiling. Not converging → salvage the
  tracker notes, decompose the task, restart in halves. 200+ calls without
  checkpoints is a process bug, not persistence.
- Acceptance: an agent report is accepted only with gate outputs attached, and the
  coordinator runs **one scoped gate** over the touched module before closing the
  item. A summary is trusted only when spot-checkable.

## 5. Agent brief — the project's standing brief (docs/notes/agent-brief.md)

Spawn prompts are pointers (§2); the pointer's target is the project's standing
brief. In a project that has none, **the first session with a first agent task
creates it** at `docs/notes/agent-brief.md` — before or together with the first
spawn. It is updated when new knowledge appears (a rule, a trap, a command), not
only after errors; knowledge learned from an error is one instance of it.

Template (sections, filled per project):

```
# Agent brief
- Layers: which module owns what.
- File partition: which task classes touch which areas.
- Code style: conventions beyond the linter's reach.
- Gates: exact commands, per module, with cwd.
- Known traps: each as a rule + why.
```

One line goes into the project's CLAUDE.md — *layer facts and traps: see*
`docs/notes/agent-brief.md` — the reminder always rides in context while the
content is read on demand. The brief is a plain md file: stable instructions
are cheapest to read on demand with a shared cache prefix; task state stays in
the tracker; CLAUDE.md stays policy-sized, carrying nothing but the pointer.

## Rationalization table

| Thought | Reality |
|---|---|
| "My prompt must be self-contained" | Pointers to brief + tracker item transfer the same context once; restating spec semantics re-pays it per agent. |
| "The agent can monitor the background job itself" | No one should sleep-poll — the wait costs the whole context per round. Detach and wake on the notification. |
| "I'll push through the budget — restarting is expensive" | A note is one call; restarting from it is minutes, whereas a silently dead agent is a total loss. |
| "All green, done" | Gate outputs or it didn't happen; the coordinator will spot-check with a scoped run anyway. |
| "More agents in parallel is faster" | Unbounded parallel spawns without pre-agreed file boundaries collide and re-read each other's work; two or three narrow ones, boundaries first. |

## Red flags

- A spawn prompt over ~15 lines or containing spec semantics (move it to the
  brief/bead).
- An agent (or you, as one) past ~2× budget without a tracker checkpoint.
- Polling a background job — detach and wake instead.
- An agent report with claims and no gate outputs (do not accept it).
- A spawn with an unverified model override.
