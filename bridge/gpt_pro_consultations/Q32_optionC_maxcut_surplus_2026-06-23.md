# Q32 — Erdős #23 Step-2: reduced to ONE explicit constant (constant-fraction triangle-free MaxCut surplus)

## Status feeding this question
- Order-9 flag-SDP route is CONFIRMED structurally walled (P2 = max-cut/objective looseness; η frozen
  +2.81e-5 over 160 iters, localizers saturated to −7.8e-9; the fooling optimizer is a real-graph
  convex mixture, PSD at every moment order, so no moment hierarchy can exclude it).
- A 12-agent reconstruct→attack→adversarial-verify panel + a prior 15-agent panel independently
  converged: every route (flag-SDP, RAD2 D-term, CF/τ_K, RI* C5-master-bound, δ₂-dichotomy) bottoms
  out at the SAME wall.

## The reduction (the single load-bearing open lemma)
Band closure ⟺ an **explicit constant-fraction MaxCut surplus** for dense triangle-free graphs in the
BCL band: prove `MaxCut(G) ≥ e/2 + c0·N²` with an EXPLICIT c0>0 whenever d_edge(G) ∈ [0.2486,0.3197].
Equivalently a converse effective-stability constant κ>0 with `d_mono(W) ≤ 2/25 − κ` for triangle-free
graphons of band edge-density. (Alon's `MaxCut − e/2 = Θ(e^{4/5})` is sublinear → useless here; BCL is
asymptotic with no explicit n0.) The lemma is TRUE (brute-force in-band max d_mono = 0.049/0.040/0.050
vs 0.08, a 0.03 margin), so a finite/analytic certificate exists by compactness — the task is an
explicit, non-regularity, non-tower-type constant.

## The two precise questions (decide which to pursue first + name the single inequality)
(1) Is there a route to an EXPLICIT constant-fraction surplus for dense triangle-free graphs — e.g. via
    the deletion master-bound RI* `min_φ[|D_φ| + min-link]` combined with a second-moment / semidefinite
    LOCAL surplus that AVOIDS the Clebsch obstruction (11/256 > 1/23.5 kills scalar Φ_v relaxations)?
(2) Given an UNCONDITIONAL exact-rational upper bound `d_mono ≤ 2/25 + 2.8e-5` on the band (from an
    order-9 flag-SDP certificate), what is the WEAKEST stability lower bound that closes the band, and
    can the C5-blow-up self-envelope (d_mono(C5[·]) monotone increasing to 2/25 at d_edge=0.40) be
    leveraged so only a CRUDE constant (κ ~ 0.03, c ≥ 0.374) is needed rather than a tight one?

## Cleaner reformulation surfaced by the panel (envelope form, conf 0.62)
Replace cut-distance-to-C5 by a monotone EDGE-DENSITY ENVELOPE: find an explicit increasing f on
[0,2/5] with f(2/5)=2/25 such that every triangle-free graphon W has `d_mono(W) ≤ f(d_edge(W))`; then
f(0.3197) ≤ 2/25 − 0.03 closes the band directly — no cut-norm, no stability constant c. Is the
envelope form more tractable than the surplus-constant form?

## Known walls (any proposal must dodge these)
C7-blowup ({C3,C5}-free, β/N²≈1/49); Petersen[2]/Cay(Z20,1,4,9) (low-δ₂ yet τ_K=0); Grötzsch[3/5]+iso
(in-band, τ_K=0, cheap flag-roots fail CF); K_{16,64} (1-opt-stable, ΣF_v=0, charging ineq overshoots
0.8N²); Clebsch obstruction 11/256 > 1/23.5 kills scalar Φ_v.
