#!/bin/bash
# two-stage rerun of one heavy n=15 class: generate-to-file (retry until >Z), split, classify in 8 parallel chunks
r=$1
G="E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
D="E:\Projects\ErdosProblems\problems\944\experiments\sixreg\n15_q"
for try in 1 2 3 4 5; do
  "$G" -d6 -D6 15 $r/2750 > "$D/f_$r.g6" 2> "$D/f_$r.err"
  if grep -q ">Z" "$D/f_$r.err"; then break; fi
done
if ! grep -q ">Z" "$D/f_$r.err"; then echo "class $r GEN-FAILED"; exit 1; fi
ZC=$(grep -o ">Z *[0-9]*" "$D/f_$r.err" | grep -o "[0-9]*")
split -n l/8 -d "$D/f_$r.g6" "$D/p_${r}_"
pids=()
for p in 0 1 2 3 4 5 6 7; do
  ./check_g6_v2.exe 15 < "$D/p_${r}_0$p" > "$D/pc_${r}_$p.out" 2>/dev/null &
  pids+=($!)
done
wait
TOT=0; NB=0; TC=0; NV=0; VC=0; TG=0
for p in 0 1 2 3 4 5 6 7; do
  L=$(grep "^total=" "$D/pc_${r}_$p.out")
  TOT=$((TOT + $(echo "$L" | grep -o "total=[0-9]*" | grep -o "[0-9]*")))
  NB=$((NB + $(echo "$L" | grep -o "nbhdOdd=[0-9]*" | grep -o "[0-9]*")))
  TC=$((TC + $(echo "$L" | grep -o "threecol=[0-9]*" | grep -o "[0-9]*")))
  NV=$((NV + $(echo "$L" | grep -o "notVC=[0-9]*" | grep -o "[0-9]*")))
  VC=$((VC + $(echo "$L" | grep -o "vcWithCritEdge=[0-9]*" | grep -o "[0-9]*")))
  TG=$((TG + $(echo "$L" | grep -o "TARGET=[0-9]*" | grep -o "[0-9]*")))
  grep -h "TARGET_G6\|VC_WITH_CRIT" "$D/pc_${r}_$p.out" 2>/dev/null
done
if [ "$TOT" -eq "$ZC" ]; then
  echo "class $r OK total=$TOT nbhdOdd=$NB threecol=$TC notVC=$NV vcWithCritEdge=$VC TARGET=$TG"
  rm -f "$D/f_$r.g6" "$D"/p_${r}_0* 
else
  echo "class $r MISMATCH geng=$ZC sum=$TOT"
fi
