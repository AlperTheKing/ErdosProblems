@echo off
rem n=14 6-regular enumeration+classification, 110 native chunk pairs (geng res/mod | check_g6)
set GENG=E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe
set CHK=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\check_g6.exe
set OUT=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\n14_chunks
if not exist %OUT% mkdir %OUT%
for /L %%r in (0,1,109) do (
  start /b cmd /c %GENG% -q -d6 -D6 14 %%r/110 ^| %CHK% 14 ^> %OUT%\c%%r.out 2^> %OUT%\c%%r.err
)
echo all 110 chunks launched
