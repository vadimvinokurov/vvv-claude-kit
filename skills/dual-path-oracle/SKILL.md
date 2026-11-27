---
name: dual-path-oracle
description: Use when writing or optimizing a non-obvious algorithm, or whenever the task says optimize, speed up, make faster, cut latency or performance: the naive reference twin ships in the same changeset, a named equality test on identical inputs lives forever, the speedup is measured and recorded.
---

# Dual Path Oracle — the naive twin beside every non-obvious optimization

**Why this exists:** an optimization is the most common source of silent
behavior change. The pair "simple version + equality test" turns the opinion
"nothing broke" into an automated check that runs forever, not once at writing
time. (Same applies-when as `testable-apps-development` rule 3: the core
contains a non-obvious or optimized algorithm. Plain CRUD/orchestration has no
such algorithms — that is no reason to skip the other rules.)

## Obligations

1. **The twin ships with the optimization.** The naive reference version — as
   direct and mathematically strict as possible — enters in the same changeset
   as the optimized code. "I removed the fast path in the refactor" is not
   shipping without the twin: the twin outlives the change, because the next
   optimization also claims its protection. Evidence: the twin exists in the
   tree, not in the task text.

2. **The equality test is permanent.** A test with the standard name
   (`<algorithm>_equal_to_naive` or the project's equivalent) feeds identical
   inputs to both versions and asserts Δ ≤ ε. Deleting it is a violation, not
   a cleanup: the test's value is the sound it makes next year, on input the
   author never imagined. Evidence: the test exists, and a test-runner run
   shows it passing both versions.

3. **The speedup is measured and recorded.** Before/after numbers go into the
   project's performance table (or the task text when none exists — then the
   task text is the table). An optimization without a recorded measurement is
   unattributable later.

4. **No twin, no shortcut on the rest.** A module without non-obvious
   algorithms legitimately has no twin — this is the rule's boundary, not a
   pass on the other rules.

## Failure to watch for

Parts of a pipeline without a twin are parts without protection. If an optimized
algorithm shares a stage with an untwinned parser/helper feeding it, the
guardrail ends exactly at the boundary — say so in the task text rather than
letting coverage decay silently.
