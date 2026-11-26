---
name: golden-rebaseline
description: Use when a comparison against a stored golden fails — component or composite PNGs, data or snapshot goldens. One triage protocol: read the diff first, classify intended vs regression, and overwrite only with a before/after record.
---

# Golden Rebaseline — one protocol for a failed comparison

**Why this exists:** a golden mismatch answers no question by itself. Without a
protocol an agent either silently overwrites goldens and buries a real
regression, or stalls on studying the picture. The protocol makes the decision
auditable and leaves a written trail. (Component/screen goldens live in
`ui-development`; data goldens live in `testable-apps-development` rule 4.
This protocol governs any of them.)

## The protocol (order is physical, not stylistic)

1. **Read the comparison output first.** Extract the percent/size diff and the
   ids of failing cases before opening any image or artifact. Open exactly the
   failing states — a full-rebaseline sweep before triage hides everything.

2. **Classify before acting.** Every mismatch is either **intended** (the
   change was meant to alter the look/behavior — overwrite the golden) or a
   **regression** (the golden is the contract — fix the code). The verdict is
   recorded in the task text, not in the working tree. If the change is
   unattributable to your task's edit, it defaults to regression until
   attributed.

3. **An overwrite is not accepted without its diff record.** Every overwritten
   golden must be accompanied, in the task text, by a before/after summary for
   exactly that case's affected goldens. Once `renders/` is overwritten,
   intended-vs-regression is unfalsifiable — which is why the record is
   written **on the fresh render, before any overwrite**.

4. **Zero-diff but visibly changed means logic moved.** A 0.000% golden diff
   next to a visible change means the changed thing is not markup — the
   semantics changed elsewhere. The mismatch belongs to the logic tests;
   stop rebaselining and run them. (For component goldens: the change is
   logic, not markup — see `ui-development`.)

5. **A brand-new state has no "before".** There is no diff to record for a
   first variant or first golden: its acceptance record is the task's
   recorded decision plus review of the fresh render before the golden is
   committed; that committed golden becomes the contract from then on.

## Boundary

- The traps table in `ui-development` covers the component-golden traps this
  protocol inherits; the protocol applies wherever goldens exist — including
  data/snapshot goldens from `testable-apps-development` rule 4 — and
  cross-references back.
- Re-running the suite after a rebaseline is spent only if it answers a real
  doubt (`token-economy` §4 applies unchanged).
