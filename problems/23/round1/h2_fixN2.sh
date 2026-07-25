#!/bin/sh
N=$1
for f in h2_bA_0[0-9] h2_bA_1[0-9] h2_bA_2[0-3]; do
  ( ./h2_opt.exe -Nfix $N -r 10 -thr 0.85 -v -seed $((RANDOM*3+5)) < $f > ${f}.N$N.out 2>&1 ) &
done
for f in h2_bA_2[4-9] h2_bA_3[0-9] h2_bA_4[0-7]; do
  ( ./h2_opt.exe -Nfix $N -r 10 -thr 0.85 -v -seed $((RANDOM*3+9)) < $f > ${f}.N$N.out 2>&1 ) &
done
wait
echo "DONE N=$N"
