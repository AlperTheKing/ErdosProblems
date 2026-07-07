# GAP-#1 ROUTE-B PAIR-DOOR PROOF (GPT-Pro MAIN, 2026-07-07, via Chrome MCP) — the residual-lemma proof

Reply length 17993 chars, harvested verbatim from MAIN thread 6a4c8b1a. GPT-Pro **self-corrected the 49-bound**:
"No L=5 forcing is needed. No 24 exact drop is needed. The strict drop Gamma(B)-Gamma(B^U) >= 4L+4 > 0 is enough."
This matches Claude's gate (global drop = (L+2)^2 - L^2 = 4L+4 = 24 for L=5; the born pair is TWO length-L edges).

## VERDICT
Route B closes the switch side if the CAP package supplies ONE L-uniform pair-door theta gate. The old one-door
gate is FALSE for the stretched model; the correct local object is:
  old bads:   f0 = oldLo length L,  f1 = oldHi length L+2
  born bads:  b0 = born0, b1 = born1, both length <= L
  drop:       >= (L+2)^2 - L^2 = 4L+4 > 0
Exact identity Gamma(B)-Gamma(B^U) = 4L+4 needs ell_{B^U}(born0)=L, ell_{B^U}(born1)=L + stable-edge metric equality.
For the Gamma-minimality contradiction, exact equality is NOT necessary; the inequality >= 4L+4 > 0 suffices.

The genuine residual (if not already in S1/S2) is **CAP_PairDoorTheta_LUniform**, and inside it the only delicate part
is **PairDoorMetricStability / PairDoorConvexity**: the two-door terminal-shadow exchange does not lengthen any
stable bad edge's cut-geodesic.

## 1. Born edges become bad with cut-length <= L  (stretched core, U={s,u,a1})
After switching U: born0,born1 become bad; oldLo,oldHi become cut edges. Post-switch paths:
  born0 = (s,a0):   s - t - b0 - chain_last - ... - chain0 - a0     cut-length L-1
  born1 = (a1,chain0): a1 - s - t - b1 - chain_last - ... - chain0   cut-length L-1
Hence ell_{B^U}(born0) <= L, ell_{B^U}(born1) <= L. In gated stretched examples both are exactly L.

## 2. NO-CROSS is AUTOMATIC from maximum-cutness  (§9.2, FULLY GENERAL — no CAP geometry)
Assume pair-door CAP gate gives: deltaB(U) = {born0,born1}; oldLo,oldHi in M and in deltaG(U); oldLo != oldHi.
Because B is a maximum cut, every switch set satisfies the switch inequality  |deltaB(U)| >= |deltaM(U)|.
Here |deltaB(U)| = 2. oldLo,oldHi are two distinct bad edges crossing U, so |deltaM(U)| >= 2. Therefore
|deltaM(U)| = 2 and deltaM(U) = {oldLo,oldHi}. So "no other old bad edge is killed" needs NO extra CAP geometry once
the pair-door boundary and the two crossing core edges are given.

## 3. Pair-door metric stability (the crux; two-door convexity, NOT automatic)
Unlike one-door, a shortest path between same-side vertices can cross the boundary twice (enter one door, return the
other). So we need a two-door convexity lemma.

### 3.1 Abstract pair-door convexity lemma
Let W = V\U. In a cut graph H suppose deltaH(U) = {d0,d1}, d0=u0--w0, d1=u1--w1 (u_i in U, w_i in W). Define
H_U = H[U], H_W = H[W]. Say the pair-door cut is CONVEX if:
  dist_{H_U}(u0,u1) <= 2 + dist_{H_W}(w0,w1)
  dist_{H_W}(w0,w1) <= 2 + dist_{H_U}(u0,u1)
Then every shortest path in H between two same-side vertices can be chosen to avoid the two boundary doors.
Proof: a simple same-side path crosses the boundary 0 or exactly 2 times; a 2-crossing path uses both doors and its
detour cost is bounded by the convexity inequalities, so the same-side (door-free) route is no longer. QED.

### 3.2 Apply before and after the switch
Before: H=B, deltaB(U)={born0,born1}. After: H'=B^U, delta_{B^U}(U)={oldLo,oldHi}. If both pair-door cuts are
convex — PairDoorConvex(B,U,born0,born1) and PairDoorConvex(B^U,U,oldLo,oldHi) — then for any stable old bad edge
e=xy NOT crossing U, its endpoints lie on the same side. KEY: the induced cut graphs on each side are UNCHANGED by
switching, because switching changes only crossing edges:
  B[U] = B^U[U]      and      B[V\U] = B^U[V\U].
Therefore d_B(x,y) = d_{B^U}(x,y) and hence ell_B(e) = ell_{B^U}(e). This proves metric stability.

## 4. Does S1/S2 prove pair-door convexity?  For the explicit stretched model, YES (direct distance witnesses).
Before: old-door U-endpoints internal distance 1, W-endpoints external distance 1.
After:  new-door U-endpoints internal distance 2, W-endpoints external distance 2.
These are L-UNIFORM; the long annulus length L lives in the corridor to the right, not in the cap door distances.
So the exact CAP residual (if not already proven) is **CAP_PairDoorConvexity_LUniform**: for every nested type-B
L/(L+2) deficient CAP core with its canonical pair-door terminal-shadow U, PairDoorConvex(B,U,born0,born1) and
PairDoorConvex(B^U,U,oldLo,oldHi). WEAKER than L=5 forcing; gateable on stretched L=5,7,9,11.
(For long annuli the precise blocker is NoSideDoorForLongAnnulus.)

## 5. Born-edge lengths: for strict decrease only ell_{B^U}(born_i) <= L is needed (from completed recut). Exact
ell=L is a checked/gated strengthening, not required.

## 6. Pair-door TS-CTI strict drop  (§9.4)
Assume weak pair-door gate (L odd >=5; deltaB(U)={born0,born1}; oldLo,oldHi distinct bad crossing; ell_B(oldLo)=L,
ell_B(oldHi)=L+2; ell_{B^U}(born_i)<=L; PairDoorConvex before+after). Then deltaM(U)={oldLo,oldHi} (max-cutness),
all stable bad edges keep ell (metric stability), so
  Gamma(B)-Gamma(B^U) = ell_B(oldLo)^2 + ell_B(oldHi)^2 - ell_{B^U}(born0)^2 - ell_{B^U}(born1)^2
                     >= L^2 + (L+2)^2 - L^2 - L^2  =  (L+2)^2 - L^2  =  4L+4 > 0.
Thus Gamma(B^U) < Gamma(B), contradicting Gamma-minimality. (Exact born lengths => equality 4L+4.)

## 7. Connectivity  (§9.5)
B^U = B - {born0,born1} + {oldLo,oldHi}. After deleting born0,born1 the two induced sides U and V\U remain
connected (assumption). oldLo,oldHi cross U so at least one connects the two sides => B^U connected (one crossing
added edge suffices). CAP-side theorem: **CAP_PairDoorSidesConnected_LUniform**: for the canonical pair-door U of a
nested type-B core, both B[U] and B[V\U] are connected after deleting the two B-doors. Stretched: U={s,u,a1}
connected by s-a1-u; complement connected through the annulus and t-x-v. Separate connectivity residual.

## 8. Core existence for route B  — R2 restated WITHOUT 5/7:
**ActiveTypeB_LCore_exists**: every minimal-positive-debt sigma-zero deficient terminal cage contains >=1 active
nested type-B L-core (some odd L>=5). (Claude gate: |Active|>=1 uniform on 42800.)

## 9. Lean proof-contract signatures (GPT-Pro's names; use real project types)
- 9.1 `structure PairTypeBThetaGate { U:VertexSet, oldLo oldHi born0 born1:Edge, L coreId:Nat }` +
      `checkPairTypeBThetaGate_sound (G B gate) (hTri hMax) (hCheck) : Odd L /\ 5<=L /\ born0!=born1 /\ oldLo!=oldHi
       /\ deltaB G B U = pairSet born0 born1 /\ oldLo,oldHi in badEdges /\ oldLo,oldHi in edgeBoundary U
       /\ ell G B oldLo = L /\ ell G B oldHi = L+2 /\ ell G (switchCut G B U) born0 <= L /\ ...born1 <= L`
- 9.2 `pairDoor_deltaM_exact_of_maxcut (...hMax, hBorn:deltaB=pairSet born0 born1, hOld*Bad, hOld*Cross, hOldNe)
       : deltaM G B U = pairSet oldLo oldHi`  — PROOF: |deltaM(U)| <= |deltaB(U)| = 2; oldLo,oldHi two distinct
       members => equality. (FULLY GENERAL.)
- 9.3 `pairDoor_metric_stability (...hDoorB, hDoorBU, hConvB, hConvBU) : ell stable`  — induced cut graphs on U and
       V\U unchanged by switching => endpoint distances, hence ell, equal.
- 9.4 `pairTypeBTheta_gammaDrop_pos (...hCheck) : GammaOfCut G (switchCut G B gate.U) < GammaOfCut G B` (inequality
       version recommended). Exact version `... = (((L+2)^2 - L^2 : Nat):Rat)` when born lengths exact.
- 9.5 `pairTypeBTheta_switch_connected (...hConn hTri hMax hCheck) : BConnected G (switchCut G B gate.U)`.
- 9.6 `activePairTypeB_exists_of_minPositiveDeficient (G B C hTri hMax hConn hMin...) : exists gate ...`.
- 9.7 `no_minPositive_sigma0_deficient_cage_routeB (...hGammaMin hMin hSigma0 hDef) : False`  — obtain gate from 9.6;
       gate+no-cross => sigma(U)=0 (|deltaB|=|deltaM|=2, switch preserves max cut size); 9.5 => connected; 9.4 =>
       Gamma strictly decreases; contradiction to Gamma-minimality.
- 9.8 `reserveResidual_nonneg_core_routeB (...) : reserveResidual >= 0`  + required token-bank decomposition:
       `negative_reserve_yields_minPositive_sigma0_deficient_cage (G B rowDB) (hRows:RowDBFactsGeneral) (hNeg:
       reserveResidual G B rowDB < 0) : exists C, MinimalPositiveDebtCage /\ sigma=0 /\ DeficientTerminalCage`.

## 10. FINAL CLOSURE CONDITION for gap #1 (Route B) — closes iff these 5 are proved OR supplied as checked gates:
1. **CAP_PairDoorTheta_LUniform**  — pair-door TypeBThetaGate facts for arbitrary odd L >= 5.
2. **PairDoorConvexity_LUniform**  — before AND after the switch (=> metric stability). [THE crux residual]
3. **PairDoorSidesConnected_LUniform**  — switched B-connectivity.
4. **ActivePairTypeB_exists_of_minPositiveDeficient**  — >=1 active pair-door core in every deficient min-pos-debt
   sigma-0 terminal cage. [= my R2; gate |A|>=1 on 42800]
5. **negative_reserve_yields_minPositive_sigma0_deficient_cage**  — token-bank residual decomposition. [the ONE
   piece that is bank-accounting, not switch-geometry; still fully open]

## CLAUDE EXACT-GATE PLAN (this session, solo)
Checkable NOW on stretched L=5,7,9,11 (+ glue families): (a) §9.2 exact deltaM(U)={f0,f1} & |deltaB|=|deltaM|=2;
(b) PairDoorConvex(B,U,born0,born1) & PairDoorConvex(B^U,U,oldLo,oldHi) — the 2 convexity inequalities each;
(c) induced invariance B[U]=B^U[U], B[V\U]=B^U[V\U]; (d) PairDoorSidesConnected (B[U],B[V\U] connected);
(e) metric stability ell_B(e)=ell_{B^U}(e) for stable e (already 0-fail/36000). Gate = _claude_pairdoor_convexity_gate.py.
NOT gateable solo (GPT-Pro/proof): the GENERAL CAP_PairDoorConvexity proof (all cages), and §9.8 token-bank
decomposition. STATUS: gap #1 switch-geometry side reduced to gateable structural claims + 2 genuinely-open CAP/bank
lemmas. P(Lean gap#1) unchanged pending #2 general proof + #5 bank decomposition.
