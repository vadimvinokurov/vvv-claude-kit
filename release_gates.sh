#!/usr/bin/env bash
# This repository's own release gates (it uses the kit it ships).
# Per skills/release-gates/SKILL.md: a tag is published only after this
# script ran green on the exact commit being tagged; the marker it writes
# is enforced mechanically by the kit's release-tag-gate hook.

set -u

GATES=(
  "python3 tests/test_protect_secrets.py"
  "python3 tests/test_release_tag_gate.py"
  "python3 tests/test_common_rules_skill.py"
  "python3 tests/test_session_rules_hook.py"
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
