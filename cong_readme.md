# Erdős Problem 699 – Rust Scanner

Rust implementation for exploring Erdős Problem 699 by scanning rows of binomial coefficients and logging weak counterexamples or near misses. The workspace contains:
- `scanner-core`: shared scanning logic (Lucas/Legendre divisibility, bitset helpers, near-miss accounting).
- `scanner-cli`: CLI runner with optional threading, profiling, and resumable JSONL output.

## Problem context
- Reference: https://www.erdosproblems.com/699
- Statement: For every \(1 \leq i < j \leq n/2\), is there always a prime \(p \geq i\) such that \(p\) divides \(\gcd\big(\binom{n}{i}, \binom{n}{j}\big)\)?
- Known baseline: Sylvester–Schur guarantees that for each \(1 \leq i \leq n/2\) there is a prime \(p > i\) dividing \(\binom{n}{i}\).
- Erdős and Szekeres conjectured that the stronger \(p > i\) bound should hold for the gcd condition, with special-case failures. It fails for \(i=2\) when \(n\) is certain powers of two; additional counterexamples exist for \(i=3\).
- Only one counterexample is known for \(i \geq 4\): \(\gcd\big(\binom{28}{5}, \binom{28}{14}\big) = 2^3 \cdot 3^3 \cdot 5\), noted as Problem B31 in Guy (2004).

## Quickstart (pick one)

**Small sanity check (bounded, collects all near misses)**  
`cargo run -p scanner-cli -- --n-max 60 --near-miss-mode all`

**Fast anomaly-only run with automatic run folder (best for long scans)**  
`cargo run -p scanner-cli --release -- --n-min 4 --n-max 1000000 --fast --anomalies-only --profile --workers 12`

- Creates `logs/run-YYYYMMDD-HHMMSS/` with:
  - `scan.jsonl` (only rows with anomalies when `--anomalies-only` is set)
  - `progress.json` (resume metadata)
  - `profile_summary.json` (timing summary)
  - `command.txt` (timestamp + cwd + exact command)
- Resume later by reusing the same folder:  
  `cargo run -p scanner-cli --release -- --run-dir logs/run-YYYYMMDD-HHMMSS --fast --anomalies-only --profile`

**Full profiling sweep (all rows, per-row timings)**  
`cargo run -p scanner-cli --release -- --n-min 4 --n-max 200000 --profile --workers 12`

- Uses the same run folder scheme; per-row profile JSONL/detail files can be set via `--profile-jsonl` and `--profile-detail-jsonl` if needed.

**Strategy/near-miss controls**  
- `--strategy {lucas,legendre}` (default: lucas)  
- `--near-miss-mode {none,count,all}` (default: all). `--fast` now only skips shared-prime materialization; near misses are still collected unless you set `--near-miss-mode none`.
- `--workers N` (default: 1) enables threading when `N > 1`; tune `--chunk-size` (default 50) to adjust task granularity for threaded runs.

## Recent run (10M sweep)

- Command: `target/release/scanner-cli --n-min 4 --n-max 10000000 --fast --anomalies-only --profile --workers 12` (`logs/run-20260103-191520`).
- Coverage: 9,999,997 rows (n = 4..10,000,000) with no weak counterexamples; 8 anomalies written.
- Near-miss rows in `logs/run-20260103-191520/scan.jsonl`: n = 10, 16, 28, 244, 512, 2048, 2188 (3^7 + 1), 1,594,324 (3^13 + 1).
- Per-row timings (from `logs/run-20260103-191520/profile_summary.json`): avg 43.5 ms, median 25.3 ms, p95 148 ms, p99 249 ms, max 2.59 s (n = 5,307,310).
- Stage timings: support build avg 6.90 ms (median 2.28 ms, p95 29.3 ms, max 1.01 s); weak scan avg 36.2 ms (median 22.4 ms, p95 119 ms, max 1.54 s); near-miss accounting avg 0.284 ms (median 0.129 ms, p95 1.00 ms, max 166 ms).

## Targeted family sweeps

- Command: `target/release/scanner-cli --family both --k-min 2 --k-max 27 --m-min 2 --m-max 17 --near-miss-mode all --anomalies-only --profile`.
- Coverage: power-of-two rows up to n = 2^27 (134,217,728) and 3^m+1 rows up to m = 17 (n = 129,140,164).
- Findings: no new anomalies beyond the known set (10, 16, 28, 244, 512, 2048, 2188, 1,594,324); gcd factorizations logged for all near misses.

## Testing
- Core/library tests: `cargo test -p scanner-core`
- CLI tests: `cargo test -p scanner-cli`
- Whole workspace: `cargo test`
