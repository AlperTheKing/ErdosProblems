# Q14 BRIEF (Rung 5) — the local charging inequality (correct-constant form of CF)

**READY TO SEND (fresh GPT-Pro chat).** Narrow, well-posed; builds directly on the AUDITED Q13 toolkit.
Step-by-step plan (STEP2_QUERY_PLAN.md): do NOT ask for all of CF; ask for the specific closing argument.

## Context (all proved/audited upstream)
K = Clebsch graph (16 even subsets of [5], A~B iff |A△B|=4). τ_K(G)=min over φ:V→V(K) of
Σ_{uv∈E}(4−|φ(u)△φ(v)|)/2. CF (open): triangle-free G, e edges, N vtx, band x=e/N²∈[0.1243,0.16] ⟹
τ_K(G) ≤ RHS=(N²/5−e)/2. Character form (eq 1, VERIFIED): c(A,B)=(3+Σ_i σ_i(A)σ_i(B))/4, σ_i(A)=(−1)^[i∈A],
∏_i σ_i(A)=1 for even A.

From Q13 (all VERIFIED, `verify_q13_audit.py` + `verify_charging_eq17.py`):
- **Charging identity (eq 17, VERIFIED 0/300):** for a 1-opt-stable labeling φ (stable under changing any
  single vertex), with s_{v,i}=Σ_{u∈N(v)}σ_i(φ(u)), ε_v∈{0,1} the Lemma-1 parity indicator, m_v=min_i|s_{v,i}|:
      8·cost(φ) = Σ_v ( 3 d_v − Σ_i |s_{v,i}| + 2 ε_v m_v ).
  Since τ_K ≤ cost(φ) for ANY stable φ, CF follows if SOME stable φ has cost(φ) ≤ RHS. Equivalently (using
  Σ_v 3 d_v = 6e), CF reduces to the **CHARGING INEQUALITY**:
      ┌────────────────────────────────────────────────────────────────────────┐
      │  Σ_v Σ_i |s_{v,i}|  −  2 Σ_v ε_v m_v   ≥   10 e − (4/5) N²   (★)         │
      └────────────────────────────────────────────────────────────────────────┘
  at a/the cost-minimizing 1-opt-stable labeling φ, for every triangle-free band graph.
  (Verified with slack: M(M(C5)) LHS=370 ≥ 287; M³(C5) 1120 ≥ 593.)

## Why this is hard and what's actually needed
- The per-vertex term (3d_v−Σ_i|s_{v,i}|+2ε_v m_v) can be **0** (if all neighbors of v share one K-label,
  Σ_i|s_{v,i}|=5d_v, ε_v=1, m_v=d_v ⟹ term 0). So (★) is NOT closable vertex-by-vertex in isolation — it is
  an **irreducibly GLOBAL** inequality: a vertex's label must simultaneously serve all neighbors, and
  **triangle-freeness (N(v) independent)** plus band density is what forces global label conflicts.
- This is exactly the correct-constant form (it EQUALS the true τ_K at optimum, ≈0.40·RHS), unlike the
  Q-deletion bounds (Rung 4) which charge ~3/4 per boundary edge and are too loose for the extremal regime
  (deletion-distance Θ(N), GPT Q13 §6).

## Concrete narrow questions (building blocks — NOT "prove CF")
1. **A second-moment / spectral handle.** Σ_i s_{v,i}² = Σ_{u,w∈N(v)}(4c(φ(u),φ(w))−3) (from eq 1). Is there
   a clean lower bound Σ_i|s_{v,i}| ≥ F(s_{v,·}) (e.g. via ‖·‖₁ ≥ ‖·‖₂²/‖·‖_∞ or a fixed convexity) that,
   SUMMED over v with the global edge constraints, yields (★)? What global quantity does Σ_v Σ_i s_{v,i}²
   equal, and does triangle-freeness make it tractable?
2. **The right potential/discharging.** Is there a vertex (or edge) potential whose global sum is exactly
   RHS and that dominates the local charging term — i.e., a discharging proof of (★) using independence of
   N(v)?
3. **Reduction to a bounded certificate.** Does (★) reduce to a finite inequality over the local profile
   (the multiset of K-labels on N(v) up to K-automorphism, |Aut(K)|=1920), checkable by a finite computation
   — i.e., a per-vertex-type LP whose feasibility implies (★) given the global degree/edge identities?
4. **Falsification.** Construct a triangle-free band graph + 1-opt-stable φ where (★) is tight or violated,
   to locate the extremal (we expect edge-saturated, near upper density, per Q13 §6).

Deliverable: a route to (★) — a global discharging/second-moment argument, OR a finite per-type LP that
implies it, OR a falsifying configuration. Audit-grade; I will verify any lemma on small graphs. Small N is
handled separately by a finite census (N≤12 done: max R≤0.40), so focus on the asymptotic/extremal regime.
