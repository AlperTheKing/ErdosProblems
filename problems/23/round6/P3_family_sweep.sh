#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round6"
: > P3_family.log
# certification mode (early exit): does ARCPLUS certify 25*mono <= q^2 for EVERY weighting?
while read NAME Q; do
  [ -z "$NAME" ] && continue
  ./P3_cutfamily.exe P3_input.txt "$NAME" "$Q" 8 ARCPLUS 1 25 >> P3_family.log 2>&1
  echo "arcplus $NAME $Q" >> P3_family_progress.txt
done < P3_family_cmds.txt
# neighbourhood-cut family, for the negative result
while read NAME Q; do
  [ -z "$NAME" ] && continue
  ./P3_cutfamily.exe P3_input.txt "$NAME" "$Q" 8 NBHD 1 25 64 CMP >> P3_family.log 2>&1
  echo "nbhd $NAME $Q" >> P3_family_progress.txt
done < P3_family_cmds_nbhd.txt
echo "FAMILY SWEEP COMPLETE" >> P3_family.log
