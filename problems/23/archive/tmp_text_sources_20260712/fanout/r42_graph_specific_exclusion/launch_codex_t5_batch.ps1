$ErrorActionPreference = "Stop"

$root = "E:\Projects\ErdosProblems"
$driver = Join-Path $root "tmp\fanout\r42_graph_specific_exclusion\rooted_t5_support_cp_sat.py"
$outDir = Join-Path $root "tmp\fanout\r42_graph_specific_exclusion"

$jobs = @(
  @{ Left = 10; Right = 7; Limit = 30000 },
  @{ Left = 11; Right = 6; Limit = 30000 },
  @{ Left = 7; Right = 11; Limit = 3000 },
  @{ Left = 8; Right = 10; Limit = 3000 },
  @{ Left = 9; Right = 9; Limit = 3000 },
  @{ Left = 10; Right = 8; Limit = 3000 }
)

$launched = foreach ($job in $jobs) {
  $stem = "t5_codex_l$($job.Left)_r$($job.Right)_$($job.Limit)"
  $output = Join-Path $outDir "$stem.json"
  $stdout = Join-Path $outDir "$stem.stdout.log"
  $stderr = Join-Path $outDir "$stem.stderr.log"
  $arguments = @(
    $driver,
    "--left", $job.Left,
    "--right", $job.Right,
    "--workers", 8,
    "--max-supports", $job.Limit,
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
    supportLimit = $job.Limit
    workers = 8
    output = $output
    stdout = $stdout
    stderr = $stderr
  }
}

$manifest = [ordered]@{
  schema = "CODEX_T5_BATCH_LAUNCH_V1"
  launchedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  externalWorkers = 8
  launchedWorkers = 48
  totalWorkers = 56
  jobs = @($launched)
}
$manifestPath = Join-Path $outDir "t5_codex_batch_launch.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding ascii
$manifest | ConvertTo-Json -Depth 5
