#!/usr/bin/env bash
# Release gates script — template shipped by the vvv-claude-kit plugin.
#
# Per skills/release-gates/SKILL.md: a project copies this script
# (e.g. to the repo root as release_gates.sh), fills the GATES array with its
# own release checks in release order, and runs it before publishing any tag.
#
# The script runs every gate in order and, on success, writes the marker file
# read by the kit's release-tag-gate hook (scripts/release-tag-gate.py):
#   .release-gates/last-run.json  { "sha": <HEAD>, "ok": true, ... }
# On a gate failure the marker is written with "ok": false and the run stops —
# a tag published then will be refused by the hook.

set -u

# ── Fill in: the project's release gates, in release order. ────────────────
# Example (commented):
# GATES=(
#   "pytest tests/ -q"                  # full backend suite
#   "npm run typecheck:strict --btf"    # strict type check, stale caches cleared
#   "npm run test:ui"                   # interface tests
#   "npm run test:goldens"              # golden comparisons
# )
GATES=(
  # "<command 1>"
  # "<command 2>"
)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$PROJECT_DIR"

MARKER_DIR=".release-gates"
MARKER="$MARKER_DIR/last-run.json"
LOG="$MARKER_DIR/last-run.log"
mkdir -p "$MARKER_DIR"

sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "release gates @ $sha  $now" | tee "$LOG"

if [ "${#GATES[@]}" -eq 0 ] || [ -z "${GATES[0]}" ]; then
  echo "ERROR: GATES is empty — fill in the project's release checks before use." | tee -a "$LOG"
  printf '{"sha": "%s", "started": "%s", "ok": false, "error": "GATES empty"}\n' "$sha" "$now" > "$MARKER"
  exit 1
fi

for gate in "${GATES[@]}"; do
  echo "── gate: $gate" | tee -a "$LOG"
  if ! bash -c "$gate" >>"$LOG" 2>&1; then
    echo "── FAIL: $gate  (log: $LOG)" | tee -a "$LOG"
    printf '{"sha": "%s", "started": "%s", "ok": false, "failed_gate": "%s"}\n' \
      "$sha" "$now" "$gate" > "$MARKER"
    exit 1
  fi
done

printf '{"sha": "%s", "started": "%s", "ok": true, "gates": %d}\n' \
  "$sha" "$now" "${#GATES[@]}" > "$MARKER"
echo "── all gates green; marker: $MARKER" | tee -a "$LOG"
