# BUILD_B.md -- Engine B (engineB_lrrule.py) build + validation log

- Date: 2026-07-21T01:36:11
- File: problems_external/ktt_lr_negativity/engine/engineB_lrrule.py
- Python: 3.12.4
- Reproduce: `python engineB_lrrule.py --selftest` (writes this file)
- Random seed: 20260721 (deterministic)
- Total selftest runtime: 10.9 s

## Algorithm (independence statement)

Engine B counts c(nu; lam, mu) directly by the classical
Littlewood-Richardson rule: semistandard skew tableaux of shape nu/lam,
content mu, whose reverse reading word (rows top->bottom, right->left)
is a lattice word. Rows are filled right-to-left, which makes the
placement order equal to the reverse-reading-word order, so the lattice
condition is enforced incrementally at every cell. Memoization:
row-boundary states (row, previous-row overlap slice, content vector)
and in-row states (column, weak-increase bound, content vector, placed
slice inside the next row's overlap). All arithmetic is native Python
big-integer; there is NO floating point in any mathematical decision.
It does NOT use the hive model and reads no other engine code.
CAP_EXCEEDED semantics: printed when the exact count provably exceeds
the user cap (early abort is sound: any completed sub-count is a lower
bound for the total) or when DP states exceed 20000000.

## Validation 1: brute-force Schur-product ground truth

Method: for every pair (lam, mu) with |lam|+|mu| <= 8 (all shapes,
any number of parts), compute s_lam * s_mu in 8 variables where each
Schur polynomial is the direct SSYT monomial sum (textbook definition,
straight shapes, no lattice words, no LR rule), then expand the product
in the Schur basis by exact lex-leading-monomial peeling. 8 variables
>= any relevant number of parts, so the expansion is complete and every
extracted coefficient is the true LR coefficient. Engine B is compared
against this on EVERY triple (lam, mu, nu) with |nu| = |lam|+|mu| <= 8
and nu having r <= 4 parts (including the c = 0 triples).

- pairs (lam, mu) processed: 434
- triples compared (engine vs ground truth, incl. zeros): 4929
- triples with nonzero c: 1025 (max c seen: 2)
- ground-truth coefficients all positive: yes
- mismatches: 0
- phase runtime: 10.0 s
- verdict: PASS (100% match)

## Validation 1c: high-multiplicity spot checks (c >= 3 territory)

The exhaustive |nu| <= 8 window only reaches c = 2, so engine B is
additionally compared against the same 4-variable Schur-product ground
truth on ALL r <= 4 targets of the pairs (3,2,1)x(3,2,1) (|nu| = 12)
and (3,2,1)x(3,3,2,1) (|nu| = 15).

- triples compared: 88
- max multiplicity reached: 4
- mismatches: 0
- phase runtime: 0.0 s
- verdict: PASS

## Validation 2: 30 random c=1 stretched checks (KTW: c=1 => P == 1)

Triples drawn (seed 20260721) from the ground-truth-certified c=1 pool
(3258 distinct triples, |nu| >= 3, r <= 4, pool extended to |nu| in [9, 10] via 4-variable ground truth). Each is checked to give
c(n*nu; n*lam, n*mu) = 1 for all n = 0..5.

  - (4,1 ; 4,1 ; 5,5): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2 ; 6 ; 7,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3 ; 4,1 ; 7,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (5 ; 4,1 ; 8,1,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (6,2 ; 2 ; 6,4): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,1 ; 0 ; 3,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,1 ; 2,1,1 ; 4,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2,1,1,1 ; 2,1,1,1 ; 4,2,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,1,1,1 ; 2,1,1 ; 3,3,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (0 ; 3,3,3,1 ; 3,3,3,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2,1 ; 3,1,1 ; 3,3,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (5,2,1 ; 1 ; 6,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,1,1 ; 2,1 ; 5,1,1,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (4 ; 4,1 ; 5,3,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (1,1,1 ; 4,1,1,1 ; 4,2,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (4,1,1,1 ; 3 ; 4,4,1,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (5,3 ; 2 ; 6,4): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2 ; 4,2,2 ; 6,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2,1 ; 6 ; 6,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3 ; 5,1,1 ; 6,2,1,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (4,1 ; 3,1 ; 4,4,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (1,1 ; 4,2,2 ; 4,3,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (4,1 ; 2,2 ; 6,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,3,2,1 ; 1 ; 3,3,3,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3 ; 3,2,1 ; 4,2,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (2,2 ; 2,1 ; 4,3): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,2 ; 3,2 ; 4,4,1,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (0 ; 4,2,2 ; 4,2,2): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (3,2,1,1 ; 2 ; 4,2,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS
  - (5 ; 2,1 ; 5,2,1): P(0..5) = [1, 1, 1, 1, 1, 1] -> PASS

- failures: 0 / 30
- phase runtime: 0.0 s
- verdict: PASS

## Validation 3: 30 random c=2 stretched checks (Ikenmeyer/Sherman: c=2 => P(n) = n+1)

Triples drawn (same seed) from the ground-truth-certified c=2 pool
(131 distinct triples). Each is checked to give c(n*nu; n*lam, n*mu)
= n + 1 for all n = 0..5.

  - (3,1 ; 2,1,1 ; 4,2,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1,1 ; 3,1 ; 5,2,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 2,1 ; 4,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 5,1 ; 6,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 4,3 ; 5,4,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 3,2 ; 4,3,2): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 3,2,1 ; 5,3,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 2,1,1 ; 3,2,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,2 ; 2,1,1 ; 4,3,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 6,1 ; 7,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (4,2 ; 3,1 ; 5,4,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (4,2,1 ; 2,1 ; 5,3,2): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (4,1 ; 3,2 ; 6,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,2,1 ; 4,1 ; 5,2,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1,1 ; 3,1 ; 4,3,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 2,1 ; 3,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,2,1 ; 2,1 ; 3,2,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1,1 ; 2,1 ; 4,2,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1 ; 3,2,1 ; 3,3,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1,1 ; 3,1,1 ; 5,2,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (2,1,1 ; 4,2 ; 5,3,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 2,2,1 ; 4,2,2,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,2 ; 4,1 ; 5,3,2): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 3,1 ; 4,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 4,1 ; 5,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (5,2 ; 2,1 ; 6,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (3,1 ; 4,2 ; 5,4,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (4,1,1 ; 3,1 ; 5,3,1,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (5,1 ; 3,1 ; 6,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS
  - (4,1 ; 4,1 ; 6,3,1): P(0..5) = [1, 2, 3, 4, 5, 6] -> PASS

- failures: 0 / 30
- phase runtime: 0.0 s (pool extension: 0.4 s)
- verdict: PASS

## Validation 4: CLI contract smoke (subprocess)

  - single call c((3,2,1);(2,1),(2,1)): got '2', expected '2' -> PASS
  - single call with cap=1: got 'CAP_EXCEEDED', expected 'CAP_EXCEEDED' -> PASS
  - empty triple (n=0 sample point): got '1', expected '1' -> PASS
  - batch mode 3 lines: got '2|1|CAP_EXCEEDED', expected '2|1|CAP_EXCEEDED' -> PASS

- verdict: PASS

## Overall verdict

ALL VALIDATIONS PASS

- Phase 1: 4929/4929 triples match brute-force Schur ground truth (100%).
- Phase 1c: 88/88 high-multiplicity triples match (max c = 4).
- Phase 2: 30/30 random c=1 triples give P(n) = 1 for n = 0..5.
- Phase 3: 30/30 random c=2 triples give P(n) = n+1 for n = 0..5.
- Phase 4: CLI contract (single, cap, empty, batch) exercised via
  subprocess -- all as specified.
