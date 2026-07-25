# Independent referee audit of the bounded skew-Kostka gate

Date: 2026-07-22
Verdict: **CONFIRMS for launch**.

This verdict covers the fixed schedule, exact interpolation contract, failure
semantics, and resume checks. It does not turn a null scan into evidence for
KTT, and it does not certify a negative row before the separate LR replay
required by `../KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md`.

## Scope reconstruction

The Rust enumerator produces exactly 69,218 canonical triples before the
base-count zero filter. A separate Python implementation, sharing neither the
partition enumerator nor the tableau counter, reconstructed the same scope:

```text
1 <= |lambda| <= 12,
ell(lambda) <= 6,
beta contained in lambda,
lambda/beta nonempty,
w a partition of |lambda/beta| with ell(w) <= 6.
```

Sorting `w` loses no cases because a skew Schur function is symmetric, so the
skew-Kostka number and its stretched polynomial are invariant under
permuting the weight. The independent canonical-scope digest is

```text
count  = 69218
SHA256 = 1ac5f598ee8609e59fbde72037c4723789c39cf82825192b85bf05f0e74e0ec2
```

The independent horizontal-strip DP agreed with the pinned Ehrcalc binary on
128 deterministic base cases and 40 additional dilation-two cases (168/168).

The adversarial generator was replayed through all 50,000 rows. It is fixed by
SplitMix64 seed `0x4b54542d4b4f5354`, is duplicate-free, has
`13 <= |lambda| <= 40`, all lengths at most eight, and constructs a nonzero
Pieri chain before sorting the weight. Exact schedule digests are

```text
exhaustive  745581797f8a3d0e216b6e79767a1ec45eb53329a65accef2ab0ea7f3f4d1f68
adversarial f6e2521412b524fb9234d2dac76ceed0271f7300061a75fc95108c050828d20a
combined    6fc8d04b31a8e6b373f816496174f9d3401872cd756cb56ecc0129bc65980010
```

## Polynomial contract

For every nonzero row the scanner ignores the vendor degree as an
interpolation bound and uses the proved ambient bound

```text
U = (ell(w)-1)(ell(lambda)-1).
```

It directly counts `n=0,...,U`, performs exact Newton interpolation over
`Q`, trims only exact trailing zeroes, checks `P(0)=1`, and directly checks the
two held-out values `U+1,U+2`. Any mismatch is an invariant failure, not a
screened case. The separately computed intrinsic dimension is used only as an
additional equality check; it cannot hide a coefficient because all values
through `U` have already been used.

The stale README sample was replayed as a regression: the exact degree is
eight, the constant term is one, and both held-outs pass.

## Failure and resume semantics

Zero base counts, resource caps, policy skips, invariant failures, screened
rows, and negative candidates have disjoint statuses. Resource or policy
skips make the final gate incomplete. A negative row is synchronously copied
before termination and is explicitly labelled a raw candidate. JSONL records
are authoritative; resume truncates only a malformed final row and then
checks the configuration hash, binary hash, schedule position, source index,
instance hash, and full instance data. The lock prevents concurrent writers.

## Replays

```text
cargo test --release --locked --manifest-path kostka_gate/Cargo.toml
  library: 5 passed, 1 ignored
  binary:  3 passed, 1 ignored

cargo test --release --locked --manifest-path kostka_gate/Cargo.toml \
  full_adversarial_schedule_has_contract_size -- --ignored
  PASS (50000/50000)

python kostka_gate/referee/independent_tableau_audit.py
  PASS (scope 69218; tableau comparisons 168/168)
```

The path dependency is clean at Ehrcalc commit
`51c0606810b37944043952fcbe5b3e41d7123273`.

Final audited hashes:

```text
src/lib.rs                 f0b6f565cf243567f68dfdc289a4acd60eb15900cfc02bf4e1b1dd7a86ef339a
src/main.rs                a2b76b66f1635c63bf030d3763230ae9110af17d5b11606926fed5996e5438c7
Cargo.lock                 34934d5a574b98a73d924a55152ca72dacc659728f5a0ea59d34c9fbe07e46de
independent_tableau_audit  ac26ddd69c98be1e6f537ed0d7a6c2f3126cc3b4e1f9516ec9848dc2ed1f0276
ktt-kostka-gate.exe v2     43ae6290ae2814aa1834cc43425771e3c4f3d7a034ce40180a8aa6447c02dc4e
```

The earlier `LNK1104` was reproduced as a Windows file-lock collision between
two concurrent Cargo invocations targeting the same test executable. The
identical test passed after the other invocation exited; it is not a scanner
or mathematics failure.

The first process-level smoke run exposed a separate Windows default-main-stack
limit while generating the frozen schedule, before a manifest or record was
written. The runner now executes `run()` on an explicitly bounded 64 MiB Rust
thread. The complete release and ignored schedule tests were rerun in the
isolated `target-v2` directory after this change; the schedule hashes are
unchanged. The audited launch binary is
`target-v2/release/ktt-kostka-gate.exe` with the v2 hash above.
