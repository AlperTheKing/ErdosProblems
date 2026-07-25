#!/bin/sh
# Q3 round 7: generate the maximal-triangle-free corpora for n = 14, 15 (8-way split, capped at 8 jobs).
cd "E:/Projects/ErdosProblems/problems/23/round7" || exit 1
G="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
"$G" -tc 14 2>/dev/null | ./Q3_engine.exe mtf > mtf14.g6
echo "n=14 mtf $(wc -l < mtf14.g6)"
for r in 0 1 2 3 4 5 6 7; do
  ( "$G" -tc 15 $r/8 2>/dev/null | ./Q3_engine.exe mtf > mtf15_$r.g6 ) &
done
wait
cat mtf15_0.g6 mtf15_1.g6 mtf15_2.g6 mtf15_3.g6 mtf15_4.g6 mtf15_5.g6 mtf15_6.g6 mtf15_7.g6 > mtf15.g6
echo "n=15 mtf $(wc -l < mtf15.g6)"
