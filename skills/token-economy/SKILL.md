---
name: token-economy
description: Use when planning or starting any non-trivial task, at every task boundary, before running gates, before reading files or images, and when a tool call fails or repeats three times. Covers session shape, reading budget, edit discipline, gates schedule and budgets. For spawning, invoke subagent-contract.
---

# Token Economy — requests and context (session rules)

**Core principle:** every assistant turn is a billed request that re-reads the whole
conversation. Cost and latency scale with (1) turn count, (2) conversation size,
(3) payload that can't be cache-served (images, fresh files). Keep the conversation
small; never pay twice for information you already have. On request-metered
providers **1 request = 1 assistant turn** — a tool-call budget is a money budget.

**These are defaults with observable exit conditions, not prohibitions.** Each
"never" names the condition that changes the answer; on that condition, do the thing.

## 1. Session shape (the coordinator side)

- Task boundary → fresh session (`/clear`) when the previous task is committed. A
  task = a tracker item (bead id) + the brief pointer, not conversation memory.
- Read the plan (bead + brief + the one spec section) before the first expensive
  tool. **The plan holds pointers; the working tree is the truth when they diverge.**
  For a single fact: scoped grep / line-range read — cheaper than an agent, fresher
  than the plan. Delegate only real mining. Full-file read is right when the
  decision depends on the file's whole structure.
- End the turn at a committed checkpoint — makes usage-limit kills harmless and the
  next replay short.
- The same markers apply to you: if your own turn approaches its call budget,
  checkpoint and end the turn — the coordinator is the conversation that replays on
  every future turn.
- Fixed background noise (exports, large diffs) runs outside your context: redirect
  to an agent, or schedule at session close.

## 2. Reading budget

- Don't re-read content you already hold that hasn't changed. **Re-reading is
  correct** when: the file changed since your read (then the changed range, not the
  file); an Edit failed because the exact text moved (re-read the block); verifying
  a fix. Re-reading the same unchanged range is the process bug.
- Images: read only when the question is genuinely visual and no text metric (diff
  %, element size, evaluate result) answers it — element scope over full window.
  **A screenshot to confirm a fix or watch a suspected failure is a new decision.**
  The same question twice with the same image is what costs money.

## 3. Editing — no shell-escaping into files

- Edit/Write are the default. Avoid `sed -i`, heredoc-fed interpreters,
  in-place stream editors, `tee file` for single-file edits: mangled quoting costs a read+edit
  cycle per attempt (documented: 5–6 failed rounds vs a first-try rewrite).
- Exception: a routine bulk transform Edit can't reach — one script, run **once**,
  then `git diff --stat` + spot checks.
- **Second failed shell edit on the same target → rewrite the whole file (or the
  block) with Write.** Never a third attempt with the same mechanism.

## 4. Gates schedule

| When | Run |
|---|---|
| Iterating on one module | that module's single test file (right cwd) |
| Milestone / before commit | full suite + linters + visual harness, after module tests are green |
| A rerun | only when it answers a **real doubt**: flaky failure, env/dependency change, stale cache, rebase, release requirement |

- Re-running a suite that already confirmed the same code against the same
  environment buys no information and burns a full-context request each time.
- frontend gates from the project's `ui/` (or configured dir), core gates from
  the workspace root — a wrong-cwd run silently tests the wrong environment.

## 5. Budget and metering

- Budget every task before starting: typical module task 30–60 calls; a refactor or
  new subsystem legitimately gets a larger number — write it down. The budget is an
  **alarm, not a quota**: crossing it means checkpoint, reassess, documented
  extension — never silent continuing. The same alarm applies to your own turn.
- If a usage endpoint exists, check `usage_usd` / `request_count` / cache share
  before changing methodology — measured beats estimated.
- A failure loop is money (each wasted call = a full-context request). Kill the
  third identical attempt mechanically: change mechanism — or delegate, which is
  where `subagent-contract` comes in. If that skill cannot be invoked (not
  installed yet), fall back to the brief's spawn template and include, at minimum:
  file partition, exact gates with cwd, a call budget with checkpoint instruction,
  and a report contract demanding gate outputs.

## Rationalization table

| Thought | Reality |
|---|---|
| "One full-suite run first won't hurt" | Let the scoped single-file run narrow the suspect; for a genuinely cross-module change, the milestone full run *is* the scoped gate — once, after module tests are green. |
| "I'll just re-read the file to be sure" | Re-read when the input changed or the exact-match Edit needs the current text — take the range, not the file. |
| "One more heredoc attempt will get the quoting right" | It was the fifth attempt that failed before you. Write tool, whole file. |
| "Screenshots prove it worked" | Numbers from tests/evaluate verify logic at ~1% of the tokens; screenshots accept visuals and show the user what they asked to see. |

## Red flags — stop and change course

- The same tool called 3+ times consecutively on the same target (loop → new mechanism).
- Mining docs/transcripts/many large files in the coordinator conversation
  (delegate — invoke `subagent-contract` for the how).
- A full-suite run where a scoped file run would narrow the suspect, or a rerun that
  answers no real doubt.
- A turn ending with no user-facing status while background work is pending (post
  one line: done / waiting on X + id / resumable at tracker item).
