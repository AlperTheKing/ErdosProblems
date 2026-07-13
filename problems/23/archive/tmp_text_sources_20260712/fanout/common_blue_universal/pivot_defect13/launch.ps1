param([ValidateRange(1,5)][int]$ThrottleLimit=5)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$runtime=Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$lanes=@('laneA_replay','laneB_vertex_slack','laneC_door','laneD_prune','laneE_referee')
$lanes | ForEach-Object -Parallel {
  $lane=Join-Path $using:PSScriptRoot $_
  New-Item -ItemType Directory -Force -Path $lane | Out-Null
  $effective=Join-Path $lane 'effective_prompt.md'
  ((Get-Content (Join-Path $using:PSScriptRoot 'COMMON.md') -Raw)+"`r`n`r`nASSIGNED:`r`n"+(Get-Content (Join-Path $using:PSScriptRoot "$_.prompt.md") -Raw)) | Set-Content -Encoding utf8 $effective
  $proc=Start-Process -FilePath $using:runtime -ArgumentList @('-a','never','exec','-C',$using:root,'-s','workspace-write','--ephemeral','--color','never','-o',(Join-Path $lane 'final.md'),'-') -RedirectStandardInput $effective -RedirectStandardOutput (Join-Path $lane 'stdout.log') -RedirectStandardError (Join-Path $lane 'stderr.log') -WindowStyle Hidden -Wait -PassThru
  $proc.ExitCode | Set-Content -Encoding ascii (Join-Path $lane 'exit_code.txt')
} -ThrottleLimit $ThrottleLimit
