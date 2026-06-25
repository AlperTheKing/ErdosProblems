# Step 2 (CF) — step-by-step closure plan (Codex-style: compute + NARROW GPT)

**User directive 2026-06-20:** Step 2 is too hard for a one-shot GPT proof. Advance **adım adım**
(step by step) like Codex: do the heavy computation ourselves, feed GPT small digestible sub-problems,
build CF up rung by rung. NEVER ask GPT "prove CF". Each rung = one narrow lemma, either **(C)** computed
+ audited by us, or **(G)** a focused GPT question, audited. CF stays UNPROVEN until every rung is closed
AND assembled into one verified chain.

## Reduced target (proved upstream)
CF ⟺ **sup over in-band (x=e/N²∈[0.1243,0.16]) triangle-free F of R(F)=τ_K(F)/RHS(F) ≤ 1**, where
RHS=(N²/5−e)/2. R is **blow-up-INVARIANT** (τ_K(F[k])=k²τ_K(F), RHS likewise). So CF reduces to a bound on
R over *irreducible* (non-blow-up) band graphs — still infinitely many, so we need a finite/inductive closure.

## Known data (this session)
- τ_K(F)=0 ⟺ F is Clebsch-homomorphic. χ(Clebsch)=4, so χ(F)≥5 ⟹ τ_K>0 (but χ=4 non-hom graphs also have τ_K>0).
- Worst R found so far: **M(M(C5)) (iterated Mycielskian, 23v, χ5, in-band) R=0.402**; M³(C5) R=0.360.
- 4-template coverage proof DEAD (Grötzsch=M(C5), Q12). Density-only bound τ_K≤e−4e²/N² too weak (R-cap ≫1).

## The ladder
- **Rung 1 (C) — exact extremal census.** Compute EXACT τ_K (CP-SAT / ILP, Codex-style — not just local
  search) on: M(C5), M(M(C5)), M³(C5), and an exhaustive sweep of small in-band triangle-free graphs
  (geng, N≤~13, band edge-counts). Output: validated max R = r* and the extremal family. STATUS: started.
- **Rung 2 (G, =Q13) — a LOCAL/INDUCTIVE upper bound on τ_K. ✅ DONE+AUDITED 2026-06-20.** GPT delivered
  (all VERIFIED, `verify_q13_audit.py`): Lemma 1 exact star-extension + Q(d) degree term; per-vertex recursion
  τ_K(G)≤τ_K(G−v)+Q(d_v); **Lemma 3 (every 2-centre ball is Clebsch-hom)** + Cor 4 two-centre deletion ⟹
  computable U(H)≥τ_K; local charging certificate; Mycielski recursion ⟹ iterated Mycielskians R→0. Extremal
  = edge-saturated, near upper density, K-deletion-distance Θ(N). See Q13_ANSWER_AND_AUDIT.
- **Rung 3 (C) — ✅ partially DONE** (Q13 lemmas verified). REMAINING: implement U(H) (eq 15) / a greedy
  2-centre-ball peel; compute U(H) vs exact τ_K (tightness) and vs RHS on the Rung-1 census + Mycielskians.
- **Rung 4 (C) — ✅ DONE 2026-06-20 (NEGATIVE result, redirects).** Tested the Q-based deletion bound (eq 25/11)
  and the combined vertex+2-centre-ball peel (eq 14): both **work on Mycielskians** (M(M(C5)) cost 7≤17.4 r=0.40)
  but are **too loose** — fail on small census extremals (N11/N12: cost 3 > RHS≈2.7 though τ_K=1) and give r=0.87
  on M³. Reason: Q(d)≈3d/4 charges ~3/4 per boundary edge; for a genuine extremal (deletion-distance Θ(N), §6)
  the bound is (3/4)tN=Θ(N²) — SAME ORDER as RHS but LOOSE CONSTANT ⟹ insufficient. `rung4_deletion_test.py`,
  `rung4_ball_peel.py`. **Tight object = local charging certificate (eq 17):** cost(φ)=(1/8)Σ_v(3d_v−Σ_i|s_{v,i}|
  +2ε_v m_v) at a 1-opt-stable φ EQUALS the local-search value (≈0.40·RHS, the truth).
- **Rung 5 (G, =Q14, narrow) — NEXT.** Prove the charging inequality `Σ_v(3d_v−Σ_i|s_{v,i}|+2ε_v m_v) ≤ 8·RHS
  = 4(N²/5−e)` at a 1-opt-stable labeling for band triangle-free graphs (the tight, correct-constant form of CF),
  OR a sharper boundary-refined deletion (eq 9) with the right constant. Use triangle-freeness (N(v) independent
  ⟹ neighbor-label structure constrained). FRESH GPT chat.
- **Rung 6 (C+G)** — finite closure: small N by census (Rung 1), large N by the Rung-5 inequality; assemble into
  one audited proof of sup R ≤ 1 ⟹ CF ⟹ Step 2. Only THEN write bridge_theorem.tex.

## Discipline
Audit every GPT suggestion against compute. Any in-band triangle-free F with R>1 found at ANY rung = a CF
COUNTEREXAMPLE — save + halt. Keep PROGRESS/ledger honest. Do not claim a rung closed without a verified check.
