#!/bin/sh
for f in h2_b15_*; do
  ( ./h2_opt.exe -Nmax 1280 -r 10 -thr 0.999 -v -seed $RANDOM < $f > $f.out 2>&1 ) &
done
wait
echo ALLDONE
