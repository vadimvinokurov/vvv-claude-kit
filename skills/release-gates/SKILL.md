---
name: release-gates
description: Use before publishing any release tag or version marker in a project repository. Establishes that a release is published only after the project's release-gates script has run green on the exact commit being tagged - local checks equal CI checks, lists in memory are not gate lists, and a failed tag-push shows which script to run.
---

# Release Gates — a release is published by the script, not by memory

**Why this exists:** the most expensive failure class here was releasing without
locally running the checks CI would run late: the CI caught breakage after
publication, and the release was rebuilt three times in one day. A list of
checks in the agent's head is not a list of checks. (This is the operating
form of the same rule that gates tag publication mechanically — see
`release-tag-gate` hook, `scripts/release_gates.sh`.)

## Obligations

1. **Tag only on a green, matching run.** A release tag is published only after
   the project's `release_gates.sh` has run on the exact commit the tag points
   to, all gates passing. Evidence: `.release-gates/last-run.json` — written by
   the script — carries that commit's SHA, `ok: true`, and a timestamp no older
   than any change since. A gate run on a different commit has no value.

2. **The gate list is the script, never memory.** The release checks live in
   the project's `release_gates.sh`, in the order the release runs them: full
   backend suite → strict type check (with stale caches cleared) → interface
   tests → golden comparisons. If the project has no such script, it is created
   (template ships with the kit) before the first release — that is part of the
   release task, not a separate chore.

3. **A failed push names the run.** When publication is refused, the response
   states the exact command to run (`bash release_gates.sh`) — fixing the
   cause first, re-running the gates, and only then publishing.

4. **Rebuilds are incidents, not retries.** If CI still fails after local gates
   passed on the same commit, the diff between local and CI environments is the
   task — not another blind tag push.

## Setup (once per project)

Copy `scripts/release_gates.sh` from the kit into the project (e.g. the repo
root or `scripts/`), fill the `GATES` array with the project's commands in
release order, and make it executable. The kit's PreToolUse hook
`release-tag-gate` then mechanically refuses tag publication until the script's
marker is fresh.

## Relation to the other skills

- `token-economy` §4: the full suite here is the milestone full run — local
  release gates and CI run the same list; no rerun is spent unless it answers a
  real doubt (env change, stale cache, flake).
- A gate failure during iteration is a normal `token-economy` scoped run, not
  a release event.
