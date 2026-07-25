@echo off
"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe" -t -c -q 15 %1/32 | "E:\Projects\ErdosProblems\problems\23\round1\claude_exact_bip.exe" 15 > "E:\Projects\ErdosProblems\problems\23\round1\n15_%1.out" 2>&1
