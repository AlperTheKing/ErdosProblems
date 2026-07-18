# Canonical N13L44 CPU harness V3 (100 workers)

Canonical launcher: `run_target44_offset100.ps1`. Both earlier 64-worker launchers are superseded and must not be used.

This file records the user's updated compute ceiling of 100 workers on a 64-core/128-thread host. The target remains the direct SN13-44 finite certificate, and the target search is not started by preparation or self-test.

## Exact allocation

The base grid is `6 families x 4 profiles x 4 replicates = 96` workers. Four distinct family/profile cells receive replicate 4, producing exactly 100 unique seeds:

| Extra cell | Seed | Reason |
|---|---:|---|
| lowavg / baseline | 44004005 | Give the new low-average-swap D10 topology an extra calibrated local search. |
| lowavg / explore | 44004205 | Give that topology an extra high-escape search. |
| max32 / gentle | 44005105 | Give the new max-32-swap D10 topology an extra conservative search. |
| max32 / topology | 44005305 | Give that topology an extra structure-changing search. |

This allocation gives each of the four profiles exactly 25 workers. Dobbelaere, END13, SENSO13, and cal131016 receive 16 workers each; lowavg and max32 receive 18 each.

## Verified seed families

| Family | Workers | Canonical fixture SHA-256 | Provenance |
|---|---:|---|---|
| dobbelaere | 16 | `4ca03000a09042e6c6be79a9dc667176dfcf0056e37e2a2c3e28f8916703fc30` | Public SorterHunter N13L45D10 network |
| end13 | 16 | `fb65e2171ed8d696a261a29824b019dc410f86b7527c48739dc6d3bdf7f03698` | Hugues Juille END13 |
| senso13 | 16 | `7299a538f2a9ec4d7380f1d2afa6aeba25fc44fdb62036ec3c5f4fa49f54696d` | Valsalam--Miikkulainen SENSO13 |
| cal131016 | 16 | `2bf0aaba84a7488d7dcbe0c8883e8c0b7a817365b1631826adab063c81dfec72` | Registered local calibration hit |
| lowavg | 18 | `a133374d57e2b056b3574bffc734ff2306c8aa44f326bc32a779d851e63e9397` | `Sort_LS_13_45_10.json`, source JSON SHA-256 `f425b44a...6608` |
| max32 | 18 | `46ec4e448dbde975e94a7bc95a8e90d75a222399fda249b7e8eabadafde56aa6` | `Sort_LS_13_45_10_MAX32.json`, source JSON SHA-256 `af9da40a...57f8` |

Every fixture contains exactly 45 comparators and passed both independent exhaustive verifiers on all 8192 binary inputs with zero failures.

## Preserved V2 safety chain

- `-ConfirmRun` is mandatory; no flag is a dry plan.
- The absolute deadline remains `2026-07-18T21:57:27+03:00`, checked before every launch and every log read; sleeps never exceed the exact remaining milliseconds.
- The process ceiling is checked after every launch and cannot exceed 100.
- Every worker has a deterministic unique seed, rendered configuration, stdout, and stderr path.
- Log monitoring consumes every appended byte exactly once with per-file offsets and partial-line buffers.
- A hit must be a complete canonical N13L44 line with exactly 44 valid pairs and must pass the independent C++ verifier on all 8192 inputs before stop-all.
- The first verified hit triggers one batch stop for all workers.
- The executable, verifier, unbuffered wrapper, six fixture hashes, and upstream commit are pinned before launch.

Dry audit:

```powershell
.\run_target44_offset100.ps1
```

Split-line, 600-decoy, and batch-stop self-test:

```powershell
.\run_target44_offset100.ps1 -SelfTest
```

Actual search (not launched during preparation):

```powershell
.\run_target44_offset100.ps1 -ConfirmRun
```
