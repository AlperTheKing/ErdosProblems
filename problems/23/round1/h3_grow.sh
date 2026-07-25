#!/bin/bash
# Chained growth: best graph at N-1 + one isolated vertex -> seed for search at N.
# Every reported bip is certified by full Gray-code enumeration inside h3_search2.exe.
START=$1; END=$2; SEEDG6=$3; SECS=$4; TAG=$5
cur="$SEEDG6"
for ((n=START; n<=END; n++)); do
  t=$(( (n*n)/25 + 1 ))
  best=""
  for s in 1 2 3 4; do
    out=$(./h3_search2.exe $n $t $((s*7919+RANDOM)) $SECS 512 40 "$cur" 2>/dev/null | tail -1)
    b=$(echo "$out" | sed -n 's/.*bestbip=\([0-9]*\).*/\1/p')
    g=$(echo "$out" | sed -n 's/.*g6=\(.*\)$/\1/p')
    echo "$TAG n=$n seed=$s bip=$b g6=$g"
    if [ -z "$best" ] || [ "$b" -gt "$best" ]; then best=$b; bestg="$g"; fi
  done
  echo "$TAG BEST n=$n bip=$best 25bip=$((25*best)) n2=$((n*n)) g6=$bestg"
  cur=$(python -c "
import sys
sys.path.insert(0,'.')
from h3_gen import decode_g6, g6
n,E=decode_g6('$bestg')
print(g6(n+1,E))")
done
