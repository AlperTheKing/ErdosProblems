#!/bin/sh
# usage: h2_lane.sh N MOD
N=$1; MOD=$2
i=0
while [ $i -lt $MOD ]; do
  ( E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe -q -t -c $N $i/$MOD | ./h2_filter.exe -twinfree > h2_bases_${N}_$i.g6 2> h2_bases_${N}_$i.err ) &
  i=$((i+1))
done
wait
cat h2_bases_${N}_*.g6 > h2_bases_${N}.g6
grep -h kept h2_bases_${N}_*.err | awk -F'kept=' '{s+=$2} END{print "total kept",s}'
wc -l < h2_bases_${N}.g6
