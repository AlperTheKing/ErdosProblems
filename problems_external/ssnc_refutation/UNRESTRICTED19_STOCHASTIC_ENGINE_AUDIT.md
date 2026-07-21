# Unrestricted order-19 stochastic engine audit

Date: 2026-07-21. No production search was launched during this audit.

## Frozen artifacts

- `engine/unrestricted19_stochastic.cpp`: 57,009 bytes, SHA-256
  `625AAEEE1169ED484A337E18F3DBB9A5DE214A8A45F6F47822494E0BB8CE1906`.
- `engine/unrestricted19_stochastic.exe`: 3,546,130 bytes, SHA-256
  `2DBE7D54FFC29066AA0D82567C2BA0848078C733358F498F6779F7AF2383D71F`.
  It is statically linked apart from `KERNEL32.dll` and `msvcrt.dll`.

Both strict builds passed with no compiler diagnostics:

```powershell
C:\msys64\mingw64\bin\clang++.exe -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror -pthread -o unrestricted19_stochastic.clangcheck.exe unrestricted19_stochastic.cpp
C:\msys64\mingw64\bin\g++.exe -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror -pthread -static -o unrestricted19_stochastic.exe unrestricted19_stochastic.cpp
```

## Search domain and exact predicates

Each state is one trit for every unordered pair: missing, forward, or reverse.
Loop and digon checks are independent of the score. Production lanes retain
minimum out-degree eight and a fixed missing-pair count `q`. The portfolio
cycles through every `q=1,...,19`; `q=0` is excluded by the tournament theorem,
and `q>19` is impossible because minimum out-degree eight requires at least
`19*8=152` present pairs among the 171 unordered pairs.

For each vertex the literal evaluator constructs

```text
new_N2+(v) = (union over u in N+(v) of N+(u)) minus N+(v) minus {v}.
```

The direct objective is the sum of
`max(0, |new_N2+(v)|-|N+(v)|+1)` plus minimum-degree deficits. Its score is
zero exactly for an oriented graph in the degree domain satisfying the strict
inequality at every vertex.

The search energy is independently reported. For degree `d`, let
`need=max(0,19-2d)`, compute the number of literal two-step witnesses for every
nondirect target, sort those counts, and sum the `need` smallest. This energy
is zero exactly when the strict inequalities all hold. The bitset and scalar
set implementations compare the direct objective, smooth energy, complete
second-neighborhood masks, degrees, and row penalties.

## Deterministic calibration

Command:

```powershell
.\unrestricted19_stochastic.exe --self-test --self-test-random 100000 --seed 19081993
```

Exit code was 0, stderr was empty, and the single stdout JSON reported
`SELF_TEST_PASS`, `production_run=false`, and `failures=0`. Exact counts:

- all 59,809 oriented graphs of orders one through five, comprising 298,249
  vertex rows;
- 100,000 raw pair mutations and exact reverts, with 300,000 bitset/scalar
  oracle comparisons;
- 1,309 degree-domain-valid and 98,691 degree-domain-invalid random states;
- 100,000 production fixed-`q` moves and exact reverts, with 200,000
  bitset/scalar comparisons;
- all 19 values of `q`, with 62,047 rejected degree-invalid fixed-`q` moves;
- all six ordered transitions between distinct pair trits;
- explicit rejection of a loop, a digon, and an out-of-range adjacency bit;
- explicit degree-eight acceptance and degree-seven rejection;
- explicit equality rejection and direct-neighbor exclusion from `new_N2+`;
- direct-objective-zero and smooth-energy-zero equivalences;
- exact raw hit JSON contract.

Safety checks returned exit code 2 for no mode, mixed self-test/search options,
and 65 threads. The invalid-thread check did not create its proposed run
directory.

## CLI and atomic result contract

Self-test:

```text
--self-test [--self-test-random N] [--seed S]
```

Production (not invoked during this audit):

```text
[--search] --threads 1..64 --seconds S --seed S --output-dir DIR
```

Optional production controls are `--restart-steps`, `--warmup-steps`, and
`--checkpoint-ms`. The output directory must be absent or empty. The fixed
wall deadline stops every worker. Independent worker seeds and restarts are
derived from the supplied seed.

All run files are written by complete temporary-file replacement:

- `config.json`: enriched configuration and domain-bridge metadata;
- `best_checkpoint.json`: enriched best state, complete ledger, both scores,
  `q`, and exact counters; explicitly not a certificate;
- `summary.json`: enriched terminal status and counters;
- `hit_candidate.json`, only on a raw hit: exactly the two keys `n` and
  `out_neighbors`, with canonical increasing rows and no metadata;
- `hit_metadata.json`, only on a raw hit: separate score, seed, `q`, complete
  ledger, and counters.

A hit is internally replayed by the scalar oracle but is labelled
`RAW_HIT_PENDING_TWO_EXTERNAL_VERIFIERS`. `NO_HIT` and a raw hit pending
external replay exit 0; neither is labelled a resolution. Internal failure
exits 3 and CLI validation failure exits 2.