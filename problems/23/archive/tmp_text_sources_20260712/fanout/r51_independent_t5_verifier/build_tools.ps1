$ErrorActionPreference = 'Stop'

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Resolve-Path (Join-Path $Here '..\..\..')

$CadicalBuild = Join-Path $Repo 'third_party\cadical\build'
$CadicalSrc = Join-Path $Repo 'third_party\cadical\src'
$CadicalExe = Join-Path $Here 'cadical.exe'
$DratExe = Join-Path $Here 'drat-trim.exe'
$LratExe = Join-Path $Here 'lrat-trim.exe'

& g++ -Wall -Wextra -O3 -DNDEBUG -DNUNLOCKED -DNCLOSEFROM `
  '-Wl,--no-insert-timestamp' `
  "-I$CadicalBuild" "-I$CadicalSrc" `
  -o $CadicalExe `
  (Join-Path $CadicalBuild 'cadical.o') `
  (Join-Path $CadicalBuild 'libcadical.a')
if ($LASTEXITCODE -ne 0) { throw "CaDiCaL link failed: $LASTEXITCODE" }

& gcc -O2 '-Wl,--no-insert-timestamp' '-Dgetc_unlocked=getc' '-Dputc_unlocked=putc' `
  -o $DratExe `
  (Join-Path $Repo 'third_party\cadical\test\cnf\drat-trim.c')
if ($LASTEXITCODE -ne 0) { throw "DRAT-trim build failed: $LASTEXITCODE" }

& gcc -O2 '-Wl,--no-insert-timestamp' '-Dgetc_unlocked=getc' '-Dputc_unlocked=putc' `
  -o $LratExe `
  (Join-Path $Here 'lrat_trim_win.c')
if ($LASTEXITCODE -ne 0) { throw "LRAT-trim build failed: $LASTEXITCODE" }

Write-Output "BUILT $CadicalExe"
Write-Output "BUILT $DratExe"
Write-Output "BUILT $LratExe"
