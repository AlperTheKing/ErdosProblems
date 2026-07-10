$ErrorActionPreference = "Stop"

$repo = "E:\Projects\ErdosProblems"
$formal = Join-Path $repo "formal-conjectures"
$leanRoot = Join-Path $repo "problems\23\lean"
$probe = Join-Path $repo "tmp\codex_package_provider_probe.lean"
$out = Join-Path $repo "tmp\codex_package_provider_probe.out.txt"
$probeCache = Join-Path $repo "tmp\codex_package_provider_probe_o"

Push-Location $repo
try {
  $scanFiles = @(
    "problems/23/lean/Erdos23Delta0/BankedWallForcedEscapeBridge.lean",
    "problems/23/lean/Erdos23Delta0/BankedWallForcedEscapeCert.lean",
    "problems/23/lean/Erdos23Delta0/BankedWallRestrictedSqueezeCert.lean",
    "problems/23/lean/Erdos23Delta0/BankedWallEndgameCert.lean",
    "problems/23/lean/Erdos23Delta0/BankedWallHornQuotient.lean",
    "problems/23/lean/Erdos23Delta0/BankedWallHornEscapeBridge.lean",
    "problems/23/lean/Erdos23Delta0/PackageProviderSkeleton.lean"
  )
  $scan = & rg -n "sorry|admit|native_decide|unsafe|axiom" @scanFiles
  if ($LASTEXITCODE -eq 0) {
    $scan | Tee-Object -FilePath $out
    exit 2
  }
  if ($LASTEXITCODE -gt 1) {
    "FORBIDDEN_SCAN_ERROR" | Tee-Object -FilePath $out
    exit $LASTEXITCODE
  }
  "FORBIDDEN_SCAN_OK" | Tee-Object -FilePath $out

  $baseCache = Join-Path $repo "tmp\claude_lean_o_base_v1"
  New-Item -ItemType Directory -Force -Path $probeCache | Out-Null
  if (Test-Path -LiteralPath $baseCache) {
    $env:LEAN_PATH = "$probeCache$([IO.Path]::PathSeparator)$baseCache"
  } else {
    $env:LEAN_PATH = $probeCache
  }
  Push-Location $formal
  $buildFiles = @(
    "Erdos23Delta0\CertGraph.lean",
    "Erdos23Delta0\FCBridge.lean",
    "Erdos23Delta0\RowPartitionCore.lean",
    "Erdos23Delta0\Rows\RowPartition.lean",
    "Erdos23Delta0\BankedWallLP.lean",
    "Erdos23Delta0\PortHallUncrossing.lean",
    "Erdos23Delta0\BankedWallLPRestricted.lean",
    "Erdos23Delta0\BankedWallRoutingFailure.lean",
    "Erdos23Delta0\ClosedShoreExtraction.lean",
    "Erdos23Delta0\ClosedWeightedHall.lean",
    "Erdos23Delta0\BankedWallW3Skeleton.lean",
    "Erdos23Delta0\BankedWallForcedEscapeBridge.lean",
    "Erdos23Delta0\BankedWallForcedEscapeCert.lean",
    "Erdos23Delta0\BankedWallRestrictedSqueezeCert.lean",
    "Erdos23Delta0\BankedWallHornQuotient.lean",
    "Erdos23Delta0\BankedWallHornEscapeBridge.lean",
    "Erdos23Delta0\BankedWallEndgameCert.lean",
    "Erdos23Delta0\PackageProviderSkeleton.lean"
  )
  foreach ($rel in $buildFiles) {
    $src = Join-Path $leanRoot $rel
    $olean = Join-Path $probeCache ($rel -replace '\.lean$', '.olean')
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $olean) | Out-Null
    if ((Test-Path -LiteralPath $olean) -and
        ((Get-Item -LiteralPath $olean).LastWriteTimeUtc -gt
          (Get-Item -LiteralPath $src).LastWriteTimeUtc)) {
      "SKIP $rel" | Tee-Object -FilePath $out -Append
      continue
    }
    "BUILD $rel" | Tee-Object -FilePath $out -Append
    & lake env lean --root=$leanRoot --o=$olean $src 2>&1 | Tee-Object -FilePath $out -Append
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
  }
  & lake env lean --root=$leanRoot $probe 2>&1 | Tee-Object -FilePath $out -Append
  Pop-Location
  exit $LASTEXITCODE
}
finally {
  if ((Get-Location).Path -ne $repo) {
    Pop-Location
  }
  Pop-Location
}
