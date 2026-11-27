---
name: release-tag-gate
description: Use when the user asks to set up release gates, tag protection, or a release check for a project: discovers the project's gate commands, asks what a release must run, writes the project's release_gates.sh (filled GATES) and installs a project-local PreToolUse hook that refuses tag publication until the release-gates marker says ok:true for the current HEAD.
---

# Release Tag Gate — install per-project release gates

**What this skill provisions** (all in the project):

1. `release_gates.sh` at the project root (or `scripts/`) — written from this
   skill's `references/release_gates.sh` with the project's `GATES` array filled.
2. The tag gate engine at `.claude/hooks/release_tag_gate.py` (copied from
   this skill's `references/release_tag_gate.py`).
3. Registration in the project's `.claude/settings.json`.

**The protocol it enforces lives in `/release-gates`** — read that skill for
the obligations (tag only on a green matching run; the marker
`.release-gates/last-run.json` carries HEAD, `ok: true` and a timestamp;
a CI failure after green local gates is an environment-diff task, not a
re-push). This skill puts the mechanical enforcement in place.

## Questionnaire (AskUserQuestion — only what the repo cannot decide)

1. **Gate commands.** First discover: test runners and entry points already
   in the repo (`pytest`/`unittest`, `package.json` scripts, `Makefile`
   targets, build/typecheck commands) — propose them as recommended options.
   Then ask which run at release time and in what order; the protocol's
   default order: full test suite → strict type check (stale caches cleared)
   → interface tests → golden comparisons. Allow "Other" for anything
   missing; every gate is one shell command, runnable from the project root.
2. Nothing else: marker format, hook registration and the refusal message
   are fixed by the template.

## Install steps (exact)

1. Write `release_gates.sh` from the reference template; splice the agreed
   commands into `GATES` in release order; `chmod +x`. Every referenced
   command must exist in the repo (verify before writing — a gate that
   isn't runnable is a false marker).
2. `mkdir -p .claude/hooks`, copy this skill's `references/release_tag_gate.py`
   → `.claude/hooks/release_tag_gate.py`.
3. Register in the project's `.claude/settings.json` — merge, never
   overwrite (preserve every key you did not touch; append to an existing
   matcher group when one matches):

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "python3 .claude/hooks/release_tag_gate.py",
      "timeout": 15
    }
  ]
}
```

4. **Run the gates once:** `bash release_gates.sh` → all gates green, marker
   `.release-gates/last-run.json` written with the current HEAD. A red gate
   is reported and installation stops — the user decides between fixing code
   and adjusting GATES (never blank-check a red suite).
5. **Verify the gate:** with the marker green a `git push --tags` payload
   into `python3 .claude/hooks/release_tag_gate.py` → empty output, exit 0;
   after touching a file (HEAD changes) the same payload → deny JSON.
6. Report: gate list, script path, hook registration, marker state; the tag
   publication now requires a fresh green run on the tagged commit.

## Relation to the other skills

- `/release-gates` — the release protocol this hook enforces; reruns, marker
  semantics and incident handling live there.
- Re-running this skill is update mode: re-derive the gates from the repo,
  diff against the installed `GATES`, keep the marker; registration merge is
  idempotent.
- Removal: delete the `Bash` PreToolUse group entry from
  `.claude/settings.json`, `.claude/hooks/release_tag_gate.py`; keep
  `release_gates.sh` and the marker if the project still releases.
- Tests for the engine live in the plugin repo (`tests/test_release_tag_gate.py`).
