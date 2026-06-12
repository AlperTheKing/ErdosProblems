@echo off
rem a=12 shore filter, 110 native chunk pairs
set GENG=E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe
set CHK=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\enum_shore.exe
set OUT=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\shore12_chunks
if not exist %OUT% mkdir %OUT%
for /L %%r in (0,1,109) do (
  start /b cmd /c %GENG% -q -c -D6 12 33:33 %%r/110 ^| %CHK% 12 ^> %OUT%\c%%r.out 2^> %OUT%\c%%r.err
)
echo launched
