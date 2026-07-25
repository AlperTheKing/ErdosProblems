#!/bin/sh
N=16; MOD=96
i=0
while [ $i -lt $MOD ]; do
  ( E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe -q -t -c $N $i/$MOD | ./h2_filter.exe -twinfree > h2_bases_${N}_$i.g6 2> h2_bases_${N}_$i.err ) &
  i=$((i+1))
done
wait
cat h2_bases_${N}_*.g6 > h2_bases_${N}.g6
echo "N=16 DONE kept=$(wc -l < h2_bases_${N}.g6)"
