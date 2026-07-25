@echo off
cd /d "E:\Projects\ErdosProblems\problems\23\round1"
python -B claude_decide_full.py %1 %2 --workers %3 > "full_%1_%2.out" 2>&1
echo exitcode=%errorlevel% >> "full_%1_%2.out"
