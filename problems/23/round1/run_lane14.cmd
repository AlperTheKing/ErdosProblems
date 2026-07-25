@echo off
"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe" -t -c -q 14 %1/16 | "E:\Projects\ErdosProblems\problems\23\round1\claude_exact_bip.exe" 14 > "E:\Projects\ErdosProblems\problems\23\round1\n14_%1.out" 2>&1
