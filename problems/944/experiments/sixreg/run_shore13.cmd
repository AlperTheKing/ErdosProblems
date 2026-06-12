@echo off
rem a=13 shore filter, 110 native chunk pairs (geng -c -D6 13 36:36)
set GENG=E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe
set CHK=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\enum_shore.exe
set OUT=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\shore13_chunks
if not exist %OUT% mkdir %OUT%
for /L %%r in (0,1,109) do (
  start /b cmd /c %GENG% -q -c -D6 13 36:36 %%r/110 ^| %CHK% 13 ^> %OUT%\c%%r.out 2^> %OUT%\c%%r.err
)
echo launched
