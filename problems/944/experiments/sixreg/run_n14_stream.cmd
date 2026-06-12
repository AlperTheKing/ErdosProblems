@echo off
setlocal
cd /d E:\Projects\ErdosProblems\problems\944\experiments\sixreg
echo START %DATE% %TIME% > check_n14_done.txt
"E:\Projects\ErdosProblems\sms-win\build\src\smsg.exe" --vertices 14 --dimacs deg6_n14.cnf --all-graphs 2> sixreg_n14.err | check_stream_mt.exe 14 96 > check_n14_live.out 2> check_n14_progress.err
echo EXIT=%ERRORLEVEL% END %DATE% %TIME% >> check_n14_done.txt
