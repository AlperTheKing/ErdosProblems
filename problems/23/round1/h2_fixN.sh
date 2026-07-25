#!/bin/sh
N=$1
for f in h2_bA_[0-9][0-9]; do
  ( ./h2_opt.exe -Nfix $N -r 12 -thr 0.85 -v -seed $((RANDOM*7+13)) < $f > ${f}.N$N.out 2>&1 ) &
done
wait
echo "DONE N=$N"
