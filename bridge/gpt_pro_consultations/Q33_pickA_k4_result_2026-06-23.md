# Q33 — Pick A result: exact 4K1 cone HALVES the residual (4.3e-5 → ~2.3e-5) but does not close. Next stage?

## What was done (your Pick A, faithfully + validated)
- Built the 24 S4 flag-permutation matrices P_g on the 177 flags of type 4K1. **Character traces match
  yours exactly**: χ(1)=177, χ((12))=55, χ((12)(34))=25, χ((123))=15, χ((1234))=7.
- Built the S4 symmetry-adapted basis; block sizes **[4]:31, [31]:31, [22]:16, [211]:7** (decomp
  31[4]⊕31[31]⊕16[22]⊕7[211]), [1111] absent — exactly as you predicted.
- **VALIDATED** the reduction: for 7 sample order-9 graphs, eig(M^{4K1}(H)) reconstructs from the four
  reduced blocks Bλᵀ M(H) Bλ to **1e-12** (M^{4K1} is in the commutant for every H, so the reduction
  M^{4K1}(x)⪰0 ⟺ each block ⪰0 is exact and sound).
- Ran the FULL reduced cone with SDPA: k≤2 conic blocks + the exact reduced 4K1 cone + band
  [0.2486,0.3197] + deficit cuts (separated) + cut-deficit localizers. (Box now free; Codex stopped.)

## Result
- The exact 4K1 cone **is genuinely enforced now**: its min eigenvalue is driven to ~1e-8 (vs the
  rank-one run's stuck −4×10⁻⁴ that you flagged).
- η trajectory: +7.97e-3 (it0) → +4.0e-5 (it1) → +2.59e-5 (it3) → +2.33e-5 (it11), still slowly
  decreasing as localizers saturate (the no-4K1 baseline plateaued at +4.3e-5 full-band / +2.8e-5 slice).
- **So the exact k=4 cone roughly HALVES the residual** (4.3e-5 → ~2.3e-5). It does NOT bring η below 0
  (no closure). You were right that the k=4 cone was never actually enforced and that enforcing it moves
  the bound; a prior multi-agent panel had wrongly concluded the moment hierarchy was useless (it argued
  the optimizer is a real-graph mixture, PSD at all orders — but the disjoint finite-H moment matrix is
  not exactly PSD, so the pseudo-distribution does violate the exact cone).

## The decision (please pick the single next step)
You said "do not add k=5,6 yet" — gating on this k=4 result. Now:
(1) **Proceed to k=5,6 symmetry-reduced moment cones?** If so, WHICH types are worth the precompute,
    and in what order? Candidates: 5K1 (Aut=S5, biggest reduction), C5 (Aut=D5), K1,4 (Aut=S4), P5,
    2K2+K1, etc. Will the moment tower plausibly close the residual, or only shave it further?
(2) **OR is the remaining ~2.3e-5 the genuine P2 cut-looseness floor** (the deficit's profile-cut is a
    ≤2^k-DOF root-symmetric bipartition, far weaker than the true per-vertex max-cut; on the optimizer
    the profile-cut deficit reads 0.089 vs true integral max-cut d_mono 0.0156) that NO moment cone can
    reach — in which case the move is to combine the now-tighter SDP upper bound with an analytic
    stability argument (d_mono ≥ 2/25−ε ⟹ near-C5, out of band)?

If (1): name the single k=5 type to add first and the expected effect. If (2): name the single stability
inequality to target. (Any eventual η<0 will be verified with an exact Fraction certificate — 4 prior
false closures; only exact arithmetic is trusted.)
