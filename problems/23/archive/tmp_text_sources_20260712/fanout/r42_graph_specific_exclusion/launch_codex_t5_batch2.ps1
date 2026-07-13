$ErrorActionPreference = "Stop"

$root = "E:\Projects\ErdosProblems"
$driver = Join-Path $root "tmp\fanout\r42_graph_specific_exclusion\rooted_t5_support_cp_sat.py"
$outDir = Join-Path $root "tmp\fanout\r42_graph_specific_exclusion"
$jobs = @(
  @{ Left = 11; Right = 7 },
  @{ Left = 12; Right = 6 },
  @{ Left = 13; Right = 5 }
)

$launched = foreach ($job in $jobs) {
  $stem = "t5_codex_l$($job.Left)_r$($job.Right)_3000"
  $output = Join-Path $outDir "$stem.json"
  $stdout = Join-Path $outDir "$stem.stdout.log"
  $stderr = Join-Path $outDir "$stem.stderr.log"
  $arguments = @(
    $driver,
    "--left", $job.Left,
    "--right", $job.Right,
    "--workers", 8,
    "--max-supports", 3000,
    "--local-classifier", "v",
    "--require-active-scope",
    "--output", $output
  )
  $process = Start-Process -FilePath "python" -ArgumentList $arguments `
    -WorkingDirectory $root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr
  [ordered]@{
    pid = $process.Id
    left = $job.Left
    right = $job.Right
    supportLimit = 3000
    workers = 8
    output = $output
  }
}

$manifest = [ordered]@{
  schema = "CODEX_T5_BATCH_LAUNCH_V1"
  launchedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  totalWorkersAfterLaunch = 64
  jobs = @($launched)
}
$manifest | ConvertTo-Json -Depth 5 |
  Set-Content -LiteralPath (Join-Path $outDir "t5_codex_batch2_launch.json") -Encoding ascii
$manifest | ConvertTo-Json -Depth 5
