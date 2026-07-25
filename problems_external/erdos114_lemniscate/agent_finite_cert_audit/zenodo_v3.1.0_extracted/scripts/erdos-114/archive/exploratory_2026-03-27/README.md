# Exploratory artifacts from the 2026-03-27 batch run (archived)

This folder holds four `EXP-MM-EHP-007-n{n}-inari_RESULTS.json` files (and their `.sha256` sidecars) for $n \in \{13, 14, 15, 16\}$ that were produced by a single batch run of `ehp_general_ieee1788` on **2026-03-27** (commit `cf26344`). All four rows reach the same anomalous state: `bb_total_evals = 0`, `bb_levels = []`, but `bb_proof_complete = true` and verdict `EHP_N{n}_PROVEN`.

These are **not production certificates** and were never claimed as such.

## What actually happened

The Rust binary `ehp_general_ieee1788` follows a four-step pipeline (reference value → branch-and-bound → outer-domain check → strict-concavity Hessian). At sufficiently high reduced dimension `d = 2(n-1) - 1` (n=13 → d=23, n=14 → d=25, n=15 → d=27, n=16 → d=29), the box-construction step `create_initial_boxes_recursive` returned an empty vector, and the branch-and-bound for-loop short-circuited on its first iteration via `if boxes.is_empty() { proof_complete = true; break; }`.

The original verdict logic at `src/bin/ehp_general_ieee1788.rs:987` was

```rust
let verdict = if proof_complete && outer_safe && hess_all_neg {
    format!("EHP_N{}_PROVEN", degree)
} else {
    format!("EHP_N{}_INCOMPLETE", degree)
};
```

This conflates "BB exhaustively eliminated all boxes via subdivision" with "BB had no boxes to start with." With `proof_complete = true` set via the empty-boxes shortcut, and `outer_safe`/`hess_all_neg` returning `true` from genuine but standalone computation in Steps 1, 3, 4, the verdict happily printed `EHP_N{n}_PROVEN` for all four degrees in 18-46 seconds wall-clock — far below what real BB at those dimensions would require.

## Scope clarification

- **n=15 and n=16** were exploratory probes outside the production scope. The lab's planned ceiling is and was n ≤ 14. These two rows were never going to appear in a public claim.
- **n=14** in this folder is a duplicate-name twin of the canonical run. The canonical n=14 row was re-run cleanly on 2026-04-02 (commit `992c58e`, message: "Upload natively logged, mathematically unbroken n=14 PROVEN footprint certificate") and lives at `results/erdos-114/EXP-MM-EHP-007-n14-inari_RESULTS.json` with `bb_total_evals = 855638016` and a populated `bb_levels`. That is the row referenced by Zenodo DOI 10.5281/zenodo.19480329 and by the DeepMind formal-conjectures PR.
- **n=13** is the production-scope row that the v12 submission packet [explicitly quarantines](../../../Erdos114/proof_path/EXP-MATH-EHP114-SMALL-N-SUBMISSION-READY-PACKET-20260507-12/EXP-MATH-EHP114-SMALL-N-SUBMISSION-READY-PACKET-20260507-12_README.md). The finite-degree theorem there reads `1 ≤ n ≤ 14, n ≠ 13`, and the n=13 row is excluded from the certificate set rather than asserted.

## Verdict-logic fix

The underlying defect has been patched in `src/bin/ehp_general_ieee1788.rs`. The verdict now requires `bb_total_evals > 0 && !level_log.is_empty()` in addition to `proof_complete && outer_safe && hess_all_neg`, with a distinct `EHP_N{n}_INCOMPLETE_BB_NO_OP` verdict reserved for the failure mode this folder documents. Future exploratory probes at any degree cannot reproduce the spurious `_PROVEN` verdict on a no-op BB phase.

The deeper question — why `create_initial_boxes_recursive` returns empty at high `d` — is left open and tracked separately. Likely candidates: an unchecked overflow in box-count computation, a parameter-space pre-flight that prunes too aggressively, or a `coeff_bound` collapse at high reduced dimension. Adding diagnostic logging to the box-construction path is the next step if any future BB run is intended at n ≥ 13.

## Provenance preserved

These files are kept on disk per the H² portfolio's never-delete rule. They are useful as:

1. Counter-examples for any future audit of the verdict logic.
2. Provenance for the n=13 quarantine narrative in the v12 submission packet.
3. Historical context for the 2026-04-02 n=14 reconciliation commit.

They must not be cited, included in any new Zenodo deposit, or referenced as evidence of the EHP conjecture at any of the four degrees.
