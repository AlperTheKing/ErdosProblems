#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round6"
: > P3_sweep.log
while read NAME Q; do
  [ -z "$NAME" ] && continue
  ./P3_psi.exe P3_input.txt "$NAME" "$Q" 8 LT >> P3_sweep.log 2>&1
  echo "done $NAME $Q" >> P3_sweep_progress.txt
done < P3_sweep_cmds.txt
echo "SWEEP COMPLETE" >> P3_sweep.log
