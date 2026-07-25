#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round6"
: > P3_exactchk.log
while read NAME Q; do
  [ -z "$NAME" ] && continue
  ./P3_cutfamily2.exe P3_input.txt "$NAME" "$Q" 8 ARCPLUS 1 25 64 EXACTCHK >> P3_exactchk.log 2>&1
  echo "exactchk $NAME $Q" >> P3_exactchk_progress.txt
done < P3_exactchk_cmds.txt
echo "EXACTCHK SWEEP COMPLETE" >> P3_exactchk.log
