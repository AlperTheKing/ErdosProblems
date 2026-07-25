# Unrestricted order-19 lexicographic C++ v2 integrated contract

Status: specification only. The live v1 source, executable, and run remain unchanged.

## Fixed seed gate

`--seed-file` activates the registered mode. Read one binary buffer with a 64 KiB cap, then hash, strictly parse, round-trip, and gate it before creating output directories, writing config, constructing shared search state, or starting threads. Production accepts only SHA-256 `32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA` and byte count471.

Require exact canonical raw schema with only `n` then `out_neighbors`, terminal LF, no whitespace/BOM/CRLF/trailing bytes, canonical integers, 19 sorted rows, no duplicates/loops/digons, and byte-identical reserialization. Recompute independent bitset and scalar evaluations and require agreement, n19, q5, 166 arcs, minimum outdegree8, objective9, smooth18, failing mask0x6E252, and the registered full ledger. A different semantically equivalent seed fails `SEED_HASH_MISMATCH`.

## CLI and warmup

Add `warmup_steps_given`. Seeded omitted or explicit zero gives effective warmup0; seeded explicit positive fails before artifacts. Unseeded omitted retains5000. Seed mode disables unconditional warmup, fixes q5, and starts each worker and restart from a byte-identical graph copy. Each restart performs one counted bitset reevaluation and checks the cached gate ledger.

## Best ordering and concurrency

For valid domain states assert objective in0..57 and smooth in0..456. Rank is `457*objective+smooth`, in0..26505. Invalid proposals are reverted before rank assertions. Acceptance delta is literal objective delta when nonzero, otherwise smooth delta.

`best_rank_hint` is a load-only atomic fast-path hint initialized to INT_MAX; there is no CAS. The authoritative comparison and all snapshot assignments occur under `best_mutex`. Publish the hint only after the complete snapshot commit. Equal rank never replaces. Checkpoint and summary copy the snapshot under the same mutex and serialize rank from that copy, never from the hint. Install the seed snapshot under the mutex before threads.

## Counters and schedule

Preserve `proposals = invalid_domain + warmup_kept + accepted + rejected` with warmup_kept0, and `evaluations = proposals + restarts`. Gate evaluations are provenance, not search counters. The main-loop temperature samples from3.0 down to0.050059; uphill acceptance is strictly `u < exp(-delta/T)`.

## Output contract

Config/checkpoint/summary use v2 schemas and record fixed q5, seed SHA/bytes/gate ledger, disabled warmup, objective-then-smooth rank, stride457, acceptance rule, and seed origin. The raw hit path and `score_zero` semantics remain unchanged. `hit_candidate.json` contains exactly `n` and `out_neighbors`; both frozen verifiers must accept it before any claim.

## Blocking oracles

Reject before worker launch on seed open/read/size/hash/parser/schema/canonicality/roundtrip/structure/oracle/q/domain/objective/ledger mismatch, or seeded nonzero warmup. Concurrent contenders must yield a mutex snapshot equal to the minimum rank with monotonically non-increasing persisted ranks. Any disagreement closes v2 before production.

## Referee correction: conditional provenance

The output paragraph above applies to registered seeded mode only. In seeded mode, record fixed q5, seed SHA/bytes/ledger, warmup0, and seed origin. In unseeded mode, retain the v1 q1..19 portfolio, q assignment, and effective warmup, and omit or explicitly null all seed-file provenance. Record v2 rank and acceptance metadata in both modes.

## Referee correction: conditional warmup counter

The statement warmup_kept=0 applies only to seeded mode, whose effective warmup is zero. Unseeded mode retains v1 warmup and counts every valid retained warmup proposal normally. In both modes preserve proposals=invalid_domain+warmup_kept+accepted+rejected and evaluations=proposals+restarts.

## Referee correction: integration and race closure

Publish `best_rank_hint` while still holding `best_mutex`, after the complete snapshot commit; delayed outside-lock stores are forbidden. Reject duplicate singleton CLI options, including `--seed-file` and `--warmup-steps`. Validate every parsed neighbor before any bit shift, hash the actual read-once buffer, and compare the seed against frozen independent ledger constants. Install the seed baseline with worker `-1`, rank4131, origin `registered_seed`, and do not count that installation as an improvement.

The v1 launcher is not compatible with this seeded route. A separate v2 launcher must authenticate the 471-byte seed before creating a run directory, pass `--seed-file` to every seeded calibration and production invocation, and reject any config/checkpoint/summary lacking the expected v2 schema, q5, warmup0, seed provenance, lexicographic rank, and acceptance metadata.
