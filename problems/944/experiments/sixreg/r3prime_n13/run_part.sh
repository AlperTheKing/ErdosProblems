#!/bin/sh
r=$1
"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe" -c -D6 13 36:36 $r/32 2>/dev/null | "E:/Projects/ErdosProblems/problems/944/experiments/sixreg/r3prime_scan.exe" 3 > part_$r.txt 2>/dev/null
