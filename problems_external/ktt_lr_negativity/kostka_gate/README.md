# Bounded skew-Kostka falsification gate

This crate implements the single bounded gate authorized by
`../KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md`. It is a counterexample scanner, not a
proof of KTT and not an extensible census campaign.

## Fixed schedule

The schedule is deterministic and has two stages.

1. Enumerate all 69,218 canonical triples `(lambda,beta,w)` before zero
   filtering with `1 <= |lambda| <= 12`, `ell(lambda) <= 6`, `beta` contained
   in `lambda`, nonempty skew shape, and partition weight `ell(w) <= 6` of the
   skew size. The exact base count excludes `K_(lambda/beta,w)=0`; every
   remaining instance is screened.
2. Generate exactly 50,000 distinct adversarial triples with `13 <=
   |lambda| <= 40` and all three lengths at most eight. The generator removes
   a deterministic sequence of horizontal strips from `lambda`; reversing the
   sequence is an explicit Pieri chain, so the unsorted weight is nonzero.
   Sorting the weight preserves the unflagged skew-Kostka number. A base-count
   invariant checks this construction before screening. The generator uses
   SplitMix64 with fixed seed `0x4b54542d4b4f5354` and accepts only exact
   intrinsic dimension at least three.

The two stages are disjoint because the second has `|lambda| >= 13`.

## Exact polynomial contract

For each nonzero instance, the scanner uses the rigorous ambient bound

```text
U = (ell(w)-1)(ell(lambda)-1).
```

It obtains direct exact counts at every `n=0,...,U`, reconstructs the power
coefficients over `Q` by an independent Newton interpolation, trims only exact
trailing zeros, and requires the trimmed degree to equal the separately
computed intrinsic dimension. It hard-fails if `P(0) != 1`. Direct counts at
`U+1` and `U+2` are held out and must agree exactly.

The vendor-reported Ehrhart degree and vendor interpolation routine are not
used to select or reconstruct the polynomial. The maintained counting engine
is a path dependency on `../vendor/ehrcalc`, and `build.rs` plus runtime
preflight both require commit
`51c0606810b37944043952fcbe5b3e41d7123273`.

The state cap is enforced at every DP level. A cap hit is `resource_error`, a
user dimension cutoff is `skipped_policy`, a completed exact check is
`screened_nonnegative` or `negative_candidate`, and zero base coefficients are
`excluded_zero`. Resource errors and policy skips make the gate incomplete;
they are never counted as screened cases.

## Crash and audit contract

`records.jsonl` is append-only and authoritative. Complete records are flushed
before checkpoints; an incomplete final JSON row is truncated on resume.
`checkpoint.json` and `summary.json` are replaced atomically, and an OS file
lock prevents concurrent writers. Resume verifies the manifest, binary hash,
configuration hash, deterministic sequence, and instance hashes.

A negative row is synchronously copied to `negative_candidates.jsonl` before
the scanner stops with exit code 10. It is only a raw candidate: the independent
LR replay and second polynomial reconstruction required by the bridge remain
mandatory. Exit code 3 means the bounded run ended with resource/policy skips;
exit code 4 means an invariant failed.

Even a complete null run makes no mathematical claim about full KTT. Its only
route-level consequence is the registered exit condition:

```text
DEAD: bounded Kostka falsification exhausted -- no theorem-closing bridge.
```

## Build, test, and run

From the repository root:

```powershell
cargo test --manifest-path problems_external/ktt_lr_negativity/kostka_gate/Cargo.toml
cargo build --release --manifest-path problems_external/ktt_lr_negativity/kostka_gate/Cargo.toml
problems_external/ktt_lr_negativity/kostka_gate/target/release/ktt-kostka-gate.exe `
  --output-dir problems_external/ktt_lr_negativity/kostka_gate/runs/gate-v1 `
  --max-states 2000000 --max-certified-dimension 49 --checkpoint-every 100
```

Resume the identical binary and configuration with:

```powershell
problems_external/ktt_lr_negativity/kostka_gate/target/release/ktt-kostka-gate.exe `
  --output-dir problems_external/ktt_lr_negativity/kostka_gate/runs/gate-v1 `
  --max-states 2000000 --max-certified-dimension 49 --checkpoint-every 100 --resume
```

The scanner is sequential and forces `RAYON_NUM_THREADS=1`. The summary records
the full vendor commit, executable SHA-256, configuration SHA-256, final JSONL
SHA-256, status counts, and whether the bounded gate was actually exhausted.
