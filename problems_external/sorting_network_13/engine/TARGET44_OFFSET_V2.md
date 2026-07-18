# Canonical N13L44 CPU harness (offset monitor v2)

Canonical launcher: `run_target44_offset64.ps1`. The earlier `run_target44_64.ps1` is rejected and must not be launched.

The allocation remains 64 CPU workers: four verified N13L45 families (Dobbelaere, END13, SENSO13, local seed 131016), four parameter profiles, and four independent seeds per family/profile cell.

Safety and certificate rules:

- A safety latch requires `-ConfirmRun`; no flag means a dry plan.
- The absolute deadline is fixed at `2026-07-18T21:57:27+03:00` and is rechecked before every worker launch and every monitored log.
- Sleeps are capped by the exact remaining milliseconds.
- Appended bytes are consumed once per file using a persistent byte offset; incomplete final lines remain buffered for the next read.
- An emitted candidate must be one complete `N=13, L=44` line ending after its network, contain exactly 44 canonical comparators with `0 <= a < b < 13`, and pass the independent exhaustive C++ verifier on all 8192 binary inputs.
- Only a verified candidate triggers one batch stop of every worker.
- The unbuffered executable, independent verifier, wrapper source, four fixtures, and upstream commit are hash/commit pinned before launch.
- The worker ceiling is checked during every launch.

Dry audit:

```powershell
.\run_target44_offset64.ps1
```

Synthetic split-line, 600-decoy, and stop-all test:

```powershell
.\run_target44_offset64.ps1 -SelfTest
```

Actual target run (only after referee PASS):

```powershell
.\run_target44_offset64.ps1 -ConfirmRun
```
