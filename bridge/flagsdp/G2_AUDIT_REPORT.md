# G2 Audit Report — dual_cert_n9.pkl underpinning "a(5n)=n^2 for n<=36" (Erdos #23 Step-1)

## (1) Overall verdict

**G2 PASS-WITH-RESIDUALS**

All six dimensions audited PASS (D2 logged "CONCERN" only because it correctly hands the
graphon-PSD soundness to a separate gate), and every adversarial re-verify returned
`CONFIRMED_PASS` with `refuted: false`. The exact-arithmetic core of the certificate is sound.
The single load-bearing item NOT closed by this G2 round is the graphon-level moment-PSD gate
(G1): `v^T P^sigma(W) v >= 0` for all band graphons W. It must be discharged by the Step-2
agent before submission.

## (2) Per-dimension status

- **D1 (gr_exact deficit regenerator)** — PASS / CONFIRMED_PASS. Two fully independent
  reimplementations match `fx.gr_exact` with max abs discrepancy **exactly 0** (Fraction) over
  all triangle-free states n=4..9 x 8 atoms; soundness `g_r(H) >= d_mono(H)-2/25` had **0
  violations, min gap exactly 0** over 4366 states (n=5..9, plus partial n=10 clean). Confirmed
  the bound is an AVERAGING property (per-R cm can dip to -0.0625), exactly as designed.

- **D2 (moment_cut_exact / Psigma_exact + SOS structure)** — PASS (logged CONCERN) /
  CONFIRMED_PASS. P^sigma matches an independent first-principles enumeration (max|diff| **0**),
  quadratic form matches (diff **0**), Razborov sum identity holds; all 114 active gamma >= 0
  so Q is PSD. Independent graphon Monte-Carlo gives worst min-eig -5.9e-17, worst atom
  v^T M v = +4.3e-7 > 0 — strong positive evidence for G1, but NOT an exact proof.

- **D3 (exact dual-feasibility end-to-end)** — PASS / CONFIRMED_PASS. sum(lam)=1 exactly,
  8 nonzero lam, 114 nonzero gam, mu=nu=0, no negative multipliers. Independent regeneration of
  all atoms over the 1897 order-9 flags reproduces max_H Phi **identical** to saved maxPhi
  (difference exactly 0). Fresh `certify_dual.py 9` rerun reproduced byte-identical multipliers.
  Per-flag moment minima are negative (down to -5.45e-3) = documented graphon-SOS, not a defect.

- **D4 (soundness chain (b)-(e))** — PASS / CONFIRMED_PASS. Chain re-derived from scratch:
  (b) `sum_lam g(H) >= d_mono(H)-2/25` had 0 violations over 1897 states; (e) order-<=9
  flag-density averaging identity verified exact over 400 random n=10,11 cases; blow-up identity
  `beta(G[t])=t^2 beta(G)` 0 violations. Clarified chain-(c): moment terms are NEGATIVE
  pointwise and pull Phi down — so G1 must be read as GRAPHON-level nonnegativity, not pointwise.

- **D5 (brute-force in-band ground truth)** — PASS / CONFIRMED_PASS. Independent numpy XOR
  max-cut (validated on C5=4, Petersen=12) and explicit triangle-free verifier; in-band max
  d_mono = 0.0494/0.0400/0.0496/0.0556 (n=9..12), margins >= 0.0245 below bound 0.0800607; the
  d_mono=0.08 extremal sits OUTSIDE the band (d_edge=0.4444). Blow-up identity exact on every
  N<=13 case.

- **D6 (band-coverage + integrality arithmetic)** — PASS / CONFIRMED_PASS. Re-derived with exact
  Fractions AND raw integer cross-multiplication: `25*36^2*PN < 2*PD` holds, `25*37^2*PN > 2*PD`
  fails -> first failing n is exactly 37, so n<=36 holds. delta<1/450 confirmed
  (450*PN < PD). N=30 band edges align gap-free (112..143 in-band; 111/144 in tails).

### Independently re-verified key numbers (this synthesis run)
- delta = 12045893274065266971721 / 198450000000000000000000000 = 6.069989052187083e-05
- sum(lam) = 1 (exact); nz_lam = 8; nz_gam = 114; neg multipliers = 0; mu = nu = 0
- (25/2)*36^2*delta = 0.9833382 < 1 ; (25/2)*37^2*delta = 1.0387269 >= 1
- delta < 1/450 : True

## (3) Unresolved concerns / required follow-ups

1. **G1 (graphon moment-PSD) is STILL REQUIRED before submission — almost certainly the gate.**
   D2/D3/D4 all converge on the same point: the moment atoms are negative per-flag, and the only
   reason the certified inequality is a valid bound on d_mono(W) is that
   `v^T P^sigma(W) v >= 0` holds for all band graphons W (Razborov moment-matrix PSD). This G2
   round gives only numerical/Monte-Carlo evidence (worst atom +4.3e-7, worst min-eig -5.9e-17).
   The Step-2 agent's exact flag-PSD eigenvalue check on M^sigma(W) over the band MUST pass; this
   is the project's historical false-closure failure mode (the -7.2e-4 localizer bug), so do not
   treat numerical positivity as sufficient.

2. **Finite-n disjointness correction must be invoked explicitly.** P_sigma counts DISJOINT
   ordered s-subset pairs, so the finite-n matrix is an O(1/n) perturbation of the true graphon
   Gram matrix. The writeup must cite the Razborov theorem and state that the disjointness
   correction vanishes in the limit (or bound it), rather than leaving it implicit.

3. **Tails rely on cited Balogh-Clemen-Lidicky Thm 1.3 (not verified here).** Density <= 0.2486
   and >= 0.3197 are out of certificate scope; the closure depends on that citation covering the
   complement of the band gap-free. D6 confirmed only the arithmetic alignment of band edges.

4. **Completeness-of-sampling residual (minor).** Exhaustive soundness is full for n<=9 and the
   blow-up identity makes n=9 the binding case; n>=10 was only partially enumerated. Trend is
   unambiguous (0 violations, min gap exactly 0). Not a correctness gap.

## (4) Bottom line

The exact-arithmetic spine of dual_cert_n9.pkl is trustworthy for a computer-assisted
publication: two-or-more independent reimplementations reproduce every regenerator
(deficit and moment) to **exactly zero** Fraction discrepancy, the saved LP combination
re-derives max_H Phi = delta byte-identically with all multipliers nonnegative and sum(lam)=1,
the integrality arithmetic ((25/2)n^2 delta < 1 iff n<=36) holds under both Fraction and raw-integer
checks, and independent brute-force ground truth confirms no real in-band triangle-free graph or
blow-up approaches the certified bound. This is exactly the kind of exact-rational cross-check that
caught all three prior false closures, and it is clean here. The single biggest remaining risk is
**the G1 graphon moment-PSD gate**: the entire bound's validity on graphons rests on
`v^T P^sigma(W) v >= 0` for band W, which this round supports only numerically — it must be closed
by the Step-2 agent's exact flag-SDP eigenvalue check, with the Razborov finite-n disjointness
correction invoked explicitly, before the arXiv claim is sound.
