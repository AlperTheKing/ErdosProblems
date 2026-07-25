@echo off
cd /d "E:\Projects\ErdosProblems\problems\23\round1"
type seed13.g6 | "E:\Projects\ErdosProblems\problems\23\round1\claude_beam2.exe" 13 26 8000 2000000 > beam2.out 2>&1
