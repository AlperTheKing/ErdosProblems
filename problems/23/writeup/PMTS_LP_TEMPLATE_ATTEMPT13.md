# PMTS-LP Template (GPT-Pro attempt-13) — VERIFIED worked instance + enumeration spec

Status: worked calibration certificate VERIFIED EXACT by Claude (2026-07-02); general template
ready for the LP engine. This is the (A1) proper-mask atom.

## Verified worked instance — the SIB 7/30 calibration point

Seed SIB = I?`FAo]]? (build graph6 via 'I?'+chr(96)+'FAo]]?'), edge set
{04,06,15,16,17,19,26,29,37,39} ∪ {38,47,48,49,58,68}. Gamma-min cut c* = 0000111101
(sides: {4,5,6,7,9}=1). Bad edges M = {38,47,49}. Row Q* = (4,8,6,1,9) for bad edge 49.
Loads (exact, Claude-verified): s = (2, 34/15, 31/15, 12/5, 8/5); N=10, m=3, η=1, τ=3/2;
x_i = (1/2, 23/30, 17/30, 9/10, 1/10). Best proper mask A* = {0,1,2,3} (anchor i0=4, q4=9):
X_A* = 41/15 = (25/N + 7/30)η exactly ⟹ β_{A*} = 7/30, ρ_{A*} = 0.

Anchored prefix shadows (ALL VERIFIED: B-connected, anchor-9-excluded, σ = δB − δM = 0):
  S_[0]       = {4}:           δB={04,48},        δM={47,49}
  S_[0,1]     = {4,8}:         δB={04,58,68},     δM={38,47,49}
  S_[0,1,2]   = {0,4,6,8}:     δB={16,26,58},     δM={38,47,49}
  S_[0,1,2,3] = {0,1,4,5,6,8}: δB={17,19,26},     δM={38,47,49}
All four natural terminal shadows are NEUTRAL ⟹ the 7/30 coefficient is intrinsic to this local
family (α_J = 0 is the tight certificate; the slack cone's tight face).

Comparison row (cut 0001111000, Q=(1,6,8,4,9)): loads (2, 11/5, 34/15, 28/15, 2), best mask
A={0,1,2,4} (i0=3), X_A = 37/15 ⟹ X_A − (25/N+7/30)η = −4/15 (strictly slack, α=0).

## General PMTS shadow-family template (enumeration spec for the LP engine)

Input: shortest all-ℓ5 row Q=(q_0..q_4) in a gamma-min max cut; nonempty proper mask A ⊊ Z5.
For each anchor h ∈ A^c: cut the cycle at h, order h+1<h+2<h+3<h+4; decompose A into maximal
intervals in this order; enumerate ALL nonempty subintervals J ⊆ A → interval set I(A,h).

For each (h, J), shadows = subsets S of the positive-flow support satisfying SEVEN predicates:
  1. {q_j : j∈J} ⊆ S                          (contains the interval)
  2. q_h ∉ S                                   (excludes the anchor)
  3. G_B[S] connected                          (B-connected)
  4. row-convex: every shortest row P has P∩S empty or contiguous along P
  5. terminal for crossing bad edges: if bad g crosses S, every P∈cyc[g] has P∩S = initial or
     terminal segment of P
  6. noncrossing-safe: no shortest row leaves S and re-enters
  7. true-twin closed within the positive-flow support (same side + same open nbhd in support)
Take inclusion-minimal such sets per (h,J), or ALL such sets as LP columns (only strengthens).
Equivalent fixed-point construction: start S={q_j: j∈J}; iterate (i) B-connected row-segment
closure avoiding q_h, (ii) terminal-prefix closure from both bad-edge orientations, (iii)
noncrossing-safe completion, (iv) twin closure, (v) DISCARD the (h,J) candidate if q_h is forced in.

σ(S) = δ_B(S) − δ_M(S) ≥ 0 by max-cut.

LP per (row, proper mask A): find α_S ≥ 0 and β_A minimal with
  X_A − (25/N + β_A)η ≤ Σ_S α_S σ(S)     [residual ρ_A = RHS − LHS ≥ 0]
Target: max β_A over the battery ≤ 1/2 (⟹ pair-residual automatic for N ≥ 50; small N finite).
Calibration floor: β = 7/30 at the SIB point above (all local slacks vanish there).

## Downstream (dependency chain)
A1(pair/residual form) ⟹ AM §5 absorption (≥4-door disposal) ⟹ ODL all-N = seed certificates
(EQ seven-cut program + SIB S7). C5-RS = PROPER-MASK + ODL ⟹ net-DW′ (uniform width) ⟹ GERSH_{L=5}.
