# Exact CUDA fitness engine for sorting networks

This directory contains the CUDA prototype for the direct SN13-44 route.  It
is an exact exhaustive scorer, not a matrix-multiplication program and not a
probabilistic verifier.  Every candidate is simulated on every one of its
`2^n` binary inputs.

The target search was **not** run during the build and calibration documented
here.  In particular, no 13-channel/44-comparator candidate was evaluated.

## Architecture

- A comparator is one packed 16-bit `(low, high)` pair.
- One CUDA block scores one complete candidate network.
- The block's 256 threads stride through all `2^n` binary inputs.
- The comparator list is copied once into block-local shared memory.
- Each output receives an exact pair-inversion count.  The primary score is
  the number of outputs with at least one inversion; the inversion total is a
  secondary, exact integer score.
- A block reduction returns `(failures, inversions)` for every candidate.
- The host-side scalar evaluator uses a separate simulation loop.  `verify`
  compares the complete CPU and GPU scores.  `benchmark` independently
  CPU-audits four spread-out batch entries.  `search` CPU-audits every
  round winner before it can be emitted as a certificate.

The search prototype is fixed-length.  If the requested length is one below
the source length, it begins with every possible one-comparator deletion.
Thereafter it keeps a deduplicated beam and generates comparator replacements
and order mutations.  All children receive the exhaustive GPU score.  Output
uses the simple independently parseable format

```
n 13
0 12
1 10
...
```

## Build

From the repository root:

```
powershell -ExecutionPolicy Bypass -File problems_external\sorting_network_13\gpu\build.ps1
```

The build imports the Visual Studio 2022 x64 environment and compiles for
`sm_120` with CUDA 13.2.  The 2026-07-18 build hashes were:

- `sn_gpu.cu`: `e0d12c935656e8634d149100f60cb8dfda2810063334766a0d8c9090d149f661`
- `sn_gpu.exe`: `b5d9d53c3b9b2d7cd2f155b3442057d98788e30b7fc980e3411172545056ecf3`

## Exact fixture checks

```
problems_external\sorting_network_13\gpu\sn_gpu.exe --mode verify --network problems_external\sorting_network_13\gpu\fixtures\sn12_39.net
problems_external\sorting_network_13\gpu\sn_gpu.exe --mode verify --network problems_external\sorting_network_13\gpu\fixtures\sn13_45.net
```

Both CPU and GPU returned zero failures: 0/4096 for N12L39 and 0/8192 for
N13L45.

## Benchmark

The exact command was:

```
problems_external\sorting_network_13\gpu\sn_gpu.exe --mode benchmark --network problems_external\sorting_network_13\gpu\fixtures\sn13_45.net --batch 4096 --rounds 3 --seed 130045
```

On the RTX 5090 it scored 12,288 N13L45 candidates in 0.001815 GPU seconds
and 0.003520 wall seconds.  That is 6.77 million networks/s or 55.45 billion
binary-input cases/s by kernel time.  Four candidates matched the CPU score.
The batch deliberately retained the valid source at index zero, so its
`best_failures=0` is a fixture check, not a search result.

## Calibration outcome

The same deletion-and-beam path was calibrated only on the known tasks
N12L40 to N12L39 and N13L46 to N13L45.  Across 137,625,688 candidates and
80.224 seconds it did not recover either known target:

| Cohort | Candidates | Final failures | Wall seconds |
|---|---:|---:|---:|
| N12L40 to L39 | 68,812,841 | 4 | 40.312 |
| N13L46 to L45 | 68,812,847 | 10 | 39.912 |

The emitted files are best non-certificates.  The independent Python scalar
and C++ bit-state verifiers both returned 4 failures for
`calibration_sn12_39.net` and 10 for `calibration_sn13_45.net`.

Therefore the result is:

- exact CUDA scorer backend: **GO**;
- this local-search heuristic as a standalone SN13-44 engine: **NO-GO**.

The target-capable code path is present but remains unexecuted.  It would take
the verified N13L45 source, set `--target-length 44`, seed all 45 deletions,
and write a canonical `.net`; it must not be launched without the parent
experiment's explicit authorization and deadline controls.
