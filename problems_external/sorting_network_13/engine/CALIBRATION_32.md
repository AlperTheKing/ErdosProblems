# Registered 16+16 calibration run

The harness is CPU-only. It launches 16 independent N12 workers and 16 independent N13 workers, for at most 30 minutes after the final launch.

Deterministic, non-overlapping seeds:

- N12: `121001` through `121016`, target length 39.
- N13: `131001` through `131016`, target length 45.

Every worker receives its own rendered configuration, stdout log, and stderr log. When one worker reaches its cohort target, all workers in that cohort are stopped. The remaining cohort continues until it also succeeds or the common 30-minute deadline expires. The run emits `summary.json` and `workers.csv` beneath a timestamped `logs/calibration-*` directory and returns exit code 2 unless both cohorts succeed.

Safety latch: invoking the script without a flag prints the exact plan and starts no process. The registered computation starts only with:

```powershell
.\run_calibration_32.ps1 -ConfirmRun
```
