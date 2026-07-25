#!/bin/sh
for f in h2_v2_[0-9][0-9]; do
  ( for s in 101 202 303; do
      ./h2_opt.exe -Nmax 1280 -r 24 -thr 0.999 -v -seed $s < $f
    done > $f.out 2>&1 ) &
done
wait
echo RERUN_DONE
