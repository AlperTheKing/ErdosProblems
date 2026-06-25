# Q7 — radius-2 extension: GPT Pro ANSWER + Step-2 AUDIT (2026-06-20)

Driven directly via Chrome (chat c/6a35ec9b "Triangle-Free Graph Bounds", model
Kapsamlı Pro / Pro Extended; GPT reasoned 29m55s). Question: refine the radius-2
MaxCut method to prove β(G) ≤ N²/25 for all triangle-free G.

## GPT VERDICT (honest): the radius-2 method is CORRECT and exactly tight at C5[n],
## but does NOT prove 1/25. It reduces the conjecture to an equivalent inequality;
## tractable relaxations give only 1/16–1/17.2 (WEAKER than BCL's 1/23.5).

## What GPT established (Step-2 audited; bound (2) independently VERIFIED)
Notation per root v: X=N(v), Y=L2(v), F_v=G[Y], d_v=|X|, t_v=e(F_v)=e2(v),
A_v=e(X,Y)=S_v−d_v, Δ_v := MaxCut(H_v)−S_v = t_v−β(H_v) ≥ 0. Q=Σd(x)², T=Σt_v, D=ΣΔ_v.
- **(1) Exact refined per-vertex bound:** β(G) ≤ e/2 − (S_v − t_v + 2Δ_v)/2.
- **(2) Averaged bound:** `β(G) ≤ e/2 − (Q−T)/(2N) − D/N`.
  **Step-2 INDEPENDENT VERIFICATION: 0 violations over ALL triangle-free graphs
  N=8,9,10 (17196 graphs); EXACTLY TIGHT at C5[2] (β=4=RHS) and C5[3] (β=9=RHS),
  with D=0.** So (2) is correct and the reduction below is sound.
- **(a) REFUTED (my proposed refinement):** no inequality MaxCut(H_v) ≥ S_v + λ·e2(v)
  holds for any universal λ>0. On C5[n], H_v=G (diameter 2), S_v=4n², e2(v)=n²,
  MaxCut(H_v)=4n²=S_v, and β(H_v)=t_v=n² — so estimating the local ball IS the global
  problem. The refinement is CIRCULAR on triangle-free diameter-2 graphs (incl. C5[n]).
- **Noncircular correction (4):** Φ_v := max_{U⊆Y}[ e_{F_v}(U,Y∖U) − Σ_{y∈U} a_y ],
  a_y=|N(y)∩X|; then Δ_v ≥ Φ_v. Exact at C5[n] (Φ_v=0) and Petersen (Φ_v=3 ⟹ MaxCut=12).
  Random-p closed form (5): Φ_v ≥ (2t_v−A_v)²/(8t_v) when A_v<2t_v, else 0. "Far too
  weak for 1/25."
- **Exact T/C5 accounting (6,7):** T = Σ_{xy∈E}Σ_v 1{c(v,x)>0}1{c(v,y)>0} (support);
  5·C5(G) = Σ_{xy}Σ_v c(v,x)c(v,y) (with multiplicity); T ≤ 5C5. On C5[n], T=5n³,
  C5=n⁵, so 5C5=n²·T — raw C5-counts cannot bound T sharply.
- **Scalar relaxations:** support-count + degree-squares alone ⟹ **β ≤ N²/16** (eq 10,
  optimum at e/N²=1/8); with the Bernoulli/Φ_v correction, sharp constant
  **c_*=1/17.2039…** (eq 17). Both weaker than 1/23.5 (BCL) and 1/25 (target).
- **★ EXACT REDUCTION (the real output):** β(G) ≤ N²/25 (for all triangle-free G)
  ⟺ **`Q − T + 2Σ_v Δ_v ≥ Ne − 2N³/25`**. This is the conjecture restated; on
  diameter-2 graphs it reduces to the original 1/25 assertion. The simpler noncircular
  Φ_v correction is OBSTRUCTED by the Clebsch graph at 11/256 > 1/23.5.

## Step-2 AUDIT verdict
- Bound (2): re-derived (probabilistic extension of an optimal cut of H_v) and
  COMPUTATIONALLY VERIFIED (0 viol, tight at C5[2],C5[3]). SOUND.
- The reduction `Q−T+2D ≥ Ne−2N³/25` ⟺ `β ≤ N²/25` is exact algebra from (2)
  (multiply `e/2−(Q−T)/2N−D/N ≤ N²/25` by 2N). SOUND.
- Refinement-(a) circularity: correct — on diameter-2 graphs H_v=G, verified D=0 and
  RHS=β on C5[n]. SOUND.
- Constants 1/16, 1/17.2: the scalar envelope optimisation is internally consistent;
  both exceed 1/25 so they do NOT prove the conjecture. (Some intermediate algebra
  chunks eq 8–9, 11–15 were harness-blocked on read; the load-bearing (2) + reduction
  + tightness are verified, which is what matters.)
- No fabrication, no overclaim: GPT explicitly states it does NOT prove 1/25.

## Net for the bridge
- NEW VERIFIED ASSET: bound (2) and the **exact reduction** of Erdős #23 to
  `Q−T+2D ≥ Ne−2N³/25` (a clean equivalent reformulation via local MaxCut surpluses,
  tight at C5[n]); the C5-free specialisation (T=D=0) recovers a_7 ≤ N²/32.
- HONEST OUTCOME: the radius-2 line does NOT close the conjecture. The essential term
  is D=ΣΔ_v (local MaxCut surplus = cut-REALIGNMENT), which is exactly the recurring
  wall — circular on dense/extremal graphs, and the noncircular Φ_v relaxation is
  Clebsch-obstructed. Consistent with all other routes: only realignment, never static
  accounting, reaches the constant.
- DO NOT pursue further radius-2 SCALAR relaxations (capped at ~1/17). Any progress must
  bound D structurally — the same open core.
