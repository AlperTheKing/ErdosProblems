#!/usr/bin/env bash
cd /e/Projects/ErdosProblems/tmp/agent_hunt/falsifier_t6 || exit 1
seen=" "
while true; do
  for f in t6_sweep_*.json t5_parity_*.json; do
    [ -e "$f" ] || continue
    case "$seen" in *" $f "*) continue;; esac
    seen="$seen$f "
    python summarize_result.py "$f" 2>&1 || echo "DONE $f parse-fail"
  done
  n=$(ls t6_sweep_*.json 2>/dev/null | wc -l)
  p=$(ls t5_parity_*.json 2>/dev/null | wc -l)
  if [ "$n" -ge 8 ] && [ "$p" -ge 1 ]; then echo "ALL_SWEEPS_DONE"; exit 0; fi
  sleep 20
done
