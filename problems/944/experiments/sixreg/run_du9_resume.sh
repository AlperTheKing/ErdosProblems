#!/bin/bash
# Resumable d_u=9 descent-core hunt completion (profile p9, base geng -d3 -D6 13 33:33, mod-28160).
# Runs every residue in core_hunt9b/missing.txt that lacks a VALID s_<r> shard.
# Validity: s_<r>.txt read=N must equal s_<r>.gerr ">Z N". Resumable: re-run skips valid shards.
# 64 parallel workers (user directive 2026-06-13). NEVER WSL; native geng.exe + core_hunt.exe.
set -u
SR="/e/Projects/ErdosProblems/problems/944/experiments/sixreg"
cd "$SR" || exit 1
OUTDIR="$SR/core_hunt9b"
GENG="E:\\Projects\\ErdosProblems\\tools\\nauty2_8_9\\geng.exe"
PAR=64
export SR OUTDIR GENG

run_one() {
  r="$1"
  o="$OUTDIR/s_$r"
  if [ -f "$o.txt" ] && [ -f "$o.gerr" ]; then
    rd=$(grep -oE "read=[0-9]+" "$o.txt" 2>/dev/null | grep -oE "[0-9]+" | head -1)
    zc=$(grep -oE ">Z +[0-9]+" "$o.gerr" 2>/dev/null | grep -oE "[0-9]+" | head -1)
    [ -n "$rd" ] && [ "$rd" = "$zc" ] && return 0
  fi
  for try in 1 2 3; do
    "$GENG" -d3 -D6 13 33:33 "$r/28160" 2>"$o.gerr" | "$SR/core_hunt.exe" p9 >"$o.out" 2>"$o.txt"
    grep -q ">Z" "$o.gerr" && break
  done
  if grep -qE "P3pass=[1-9]" "$o.txt" 2>/dev/null; then
    echo "SURVIVOR r=$r $(cat "$o.txt")" >> "$OUTDIR/SURVIVORS.txt"
  fi
}
export -f run_one

sort -n "$OUTDIR/missing.txt" | uniq | xargs -P"$PAR" -I{} bash -c 'run_one "$@"' _ {}

# Aggregate over ALL completed s_ shards (one summary line each).
awk '{for(i=1;i<=NF;i++){split($i,a,"=");v[a[1]]+=a[2]}} END{print "AGG shards="NR" read="v["read"]" apexings="v["apexings"]" P1pass="v["P1pass"]" P2pass="v["P2pass"]" P3pass="v["P3pass"]}' "$OUTDIR"/s_*.txt > "$OUTDIR/agg9b.txt"
echo "FINISHED_RUN" >> "$OUTDIR/agg9b.txt"
cat "$OUTDIR/agg9b.txt"
