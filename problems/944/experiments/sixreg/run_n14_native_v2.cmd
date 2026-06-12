@echo off
rem n=14 re-verification with different chunking (mod 73) to catch chunk-boundary bugs
set GENG=E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe
set CHK=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\check_g6.exe
set OUT=E:\Projects\ErdosProblems\problems\944\experiments\sixreg\n14_chunks_v2
if not exist %OUT% mkdir %OUT%
for /L %%r in (0,1,72) do (
  start /b cmd /c %GENG% -q -d6 -D6 14 %%r/73 ^| %CHK% 14 ^> %OUT%\c%%r.out 2^> %OUT%\c%%r.err
)
echo all 73 chunks launched
