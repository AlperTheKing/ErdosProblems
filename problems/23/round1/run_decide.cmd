@echo off
cd /d "E:\Projects\ErdosProblems\problems\23\round1"
python -B claude_exact_decide.py %1 %2 --workers %3 > "decide_%1_%2.out" 2>&1
