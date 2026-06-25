# Q16 BRIEF — the 2-color switching flag-SDP plateaus at β/N²=1/20; how to reach 1/25?

Follow-up to Q15 (you recommended: direct β + max-cut 2-coloring + macroscopic switching flag-SDP). I BUILT it
from scratch (Python+cvxpy, validated: reproduces Mantel edge-density=1/2 exactly). It WORKS and gives a real
decreasing bound — but **plateaus at β/N² ≤ 1/20, not the target 1/25**, robustly. I need your judgment on
whether 1/20 is a fundamental limit of this relaxation, and the precise next refinement.

## Setup (as you specified)
Prove `β=e−MaxCut ≤ N²/25` for triangle-free G on N vertices in the band `x=e/N²∈[0.1243,0.16]`. Asymptotic
certificate suffices (audited blow-up transfer). 2-color the vertices by a fixed MAXIMUM cut (A/B). Objective:
`d_mono` = monochromatic-edge density; `β/N² → d_mono/2`, so target `d_mono ≤ 2/25 = 0.08`.
PRIMAL flag SDP: `max d_mono` over 2-colored triangle-free graphons s.t. moment matrices `M^σ(x)⪰0` (colored
types σ up to k=2 roots, flags up to order 4), edge-band, and SWITCHING constraints. Switching = the limit
functionals of your SW: for `p` a function of (color, adjacency to k bounded roots),
`Σ_{edges uv} χ(uv)(p_u+p_v−2p_up_v) ≤ 0` (χ=+1 mono, −1 cut); I include p∈{0,½,1}, k=0,1,2,3 via a separation
oracle. SW1 (your 1-root switch) verified ≤0 on max cuts.

## RESULT — robust plateau (all machine-checked)
`max d_mono` vs switching root depth (separation oracle, converges):
- band only: 0.320  (nothing forces a good cut)
- +0-root (p=½ gives d_mono≤d_cut): 0.160
- +1-root: 0.118
- +2-root: 0.101
- +3-root (coordinate-ascent p-opt): 0.1005  ← **converged plateau**, β/N² ≤ **0.0502 ≈ 1/20**
**Flag order does NOT help:** k≤1 bound is 0.118 IDENTICAL at N=5, N=6, N=7 (order-3 and order-4 flags).
So neither higher flag order (≤7) nor deeper switching (≤3 roots) breaks past β/N² ≈ 1/20. Target is 1/25.

## The pseudo-graphon (primal x* the SDP cannot beat)
A diffuse fractional mixture at the band TOP (`d_edge*≈0.316`, i.e. x≈0.158), aggregate mono-edge fraction
≈ 0.30 (top-weight pieces are sparse 5-vertex colored graphs, mostly all-cut, with a tail carrying the mono
mass). For comparison the true extremal C5[n] (x=0.2, OUTSIDE the band) has mono-fraction = 1/5 = 0.20 and
β/N²=1/25. So the SDP's fake sits in-band with TOO MUCH mono density (0.30 vs ~0.20) that bounded-order
switching can't suppress.

## QUESTIONS (concrete)
1. **Is β/N² = 1/20 a fundamental limit** of the single-maximum-cut + bounded-order-switching relaxation, or
   can it reach 1/25 with the right refinement? (Did you expect ≈1/20 from this exact relaxation?)
2. **Color refinement by max-cut margin** `h(v)=d_C(v)−d_M(v) ≥ 0`: you suggested this when the direct calc
   stalls. But h(v) is SEMI-GLOBAL (depends on v's whole neighborhood coloring), not flag-local. Precisely how
   do I encode it as a vertex color in the flag algebra — as an extra attribute with which consistency
   constraints linking the margin-color to the local cut/mono degrees? Give the exact construction (the new
   color set, the constraints, and which switches/flags to add).
3. **Or: do I need MORE THAN ONE CUT?** The Clebsch/τ_K route used 5 coordinate cuts precisely because one cut
   loses information; β≤(e+2τ_K)/5 needed all 5. Is the single-max-cut relaxation inherently ≈1/20, and should
   I instead run a flag-SDP over the 5-cut / Clebsch-colored structure (16 colors) with switching — or some
   intermediate (2 or 3 cuts)? If so, the exact colored-flag setup.
4. **Any additional valid inequality** specific to triangle-free max cuts (a second-order switching, a local
   C5-block identity, an entropy/degree inequality) that provably suppresses the 0.30→0.20 mono-fraction gap?

Deliverable: tell me whether to (a) push color refinement (exact scheme), (b) switch to multi-cut/Clebsch flags
(exact scheme), or (c) accept ~1/20 as the relaxation's limit and pursue a different proof. I will machine-check
any concrete construction immediately. Audit-grade; be honest if 1/20 is the wall.
