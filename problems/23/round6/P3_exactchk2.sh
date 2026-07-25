#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round6"
: > P3_exactchk2.log
while read NAME Q; do
  [ -z "$NAME" ] && continue
  case "$NAME" in
    Gamma_*) IN=P3_gamma.txt; FAM=ARCFREE ;;
    *)       IN=P3_input.txt; FAM=ARCPLUS ;;
  esac
  ./P3_cutfamily2.exe "$IN" "$NAME" "$Q" 8 "$FAM" 1 25 64 EXACTCHK >> P3_exactchk2.log 2>&1
  echo "e2 $NAME $Q" >> P3_exactchk2_progress.txt
done < P3_exactchk2_cmds.txt
echo "EXACTCHK2 COMPLETE" >> P3_exactchk2.log
