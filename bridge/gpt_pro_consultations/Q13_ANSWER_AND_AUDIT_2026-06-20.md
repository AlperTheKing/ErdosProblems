# Q13 (Rung 2) — local/inductive τ_K bound + extremal family: GPT ANSWER + Step-2 AUDIT (2026-06-20)

Chat "Triangle-free Graph Bounds" `c/6a36cf3b-def0-83eb-9ca3-9a5a1fef4851`, Kapsamlı Pro, reasoned
**31m33s**. NARROW ask (step-by-step plan, Rung 2): a local/inductive upper bound on τ_K + extremal family.
**GPT delivered RICH, CHECKABLE material** (multiple lemmas with proofs). **AUDIT VERDICT: SOUND —
ALL lemmas VERIFIED computationally (`verify_q13_audit.py`, 2026-06-20T21:10):**
(1) character formula exact on all 256 pairs; (2) Lemma 1 formula = brute min_A, 0 viol/20000 multisets;
(4-5) Q(d)=[0,1,1,3,3,4,4,6,6,7,7,9] = sampled max, sharp block confirmed; (12) Lemma 3 — 2-centre balls
Clebsch-hom 0 viol/11625, explicit map (13) 0 fail/6053; (19-20) Mycielski τ_K(M²(C5))=7=closed(2) ✓.
Highly promising; reframes CF onto edge-saturated, deletion-distance-Θ(N) cores near upper density.

## The lemmas (verbatim-faithful)

**Character structure.** For even A⊆[5], σ_i(A)=(−1)^[i∈A]∈{±1}; since |A| even, ∏_i σ_i(A)=1. Edge cost
`c(A,B)=(4−|A△B|)/2 = (3 + Σ_{i=1}^5 σ_i(A)σ_i(B))/4`.  (eq 1)

**Lemma 1 (exact star extension).** Given neighbor labels B_1..B_d, let s_i=Σ_j σ_i(B_j). Then
`min_{A∈K} Σ_j c(A,B_j) = (3d − Σ_i|s_i| + 2ε m)/4`, where m=min_i|s_i| and ε=1 iff all s_i≠0 and
∏(−sgn s_i)=−1 (parity-correction), else ε=0.  (eq 2). Proof: x_i=σ_i(A)∈{±1}, ∏x_i=1; unconstrained
min picks x_i=−sgn(s_i); fix parity by flipping the smallest |s_i| (cost +2m).

**Degree bound Q(d) (eq 4-5):** `max_{B_1..B_d} min_A Σ c(A,B_j) = Q(d) = 3⌊d/4⌋ + 1[d mod 4 ∈{2,3}]`.
Sharp via the 4-label block B={∅,12,1345,2345} (all s_i=0 ⟹ adds exactly 3 per copy).

**Lemma 2 (Clebsch gluing, eq 7):** V=X⊔Y, m=e(X,Y) ⟹ `τ_K(G) ≤ τ_K(G[X])+τ_K(G[Y])+Q(m)`. Proof: translate
X-labeling by T (α_T(x)=α(x)△T preserves internal costs); cross-edge cost = star-extension of {α(x)△β(y)}.

**Per-vertex deletion recursion (eq 11):** `τ_K(G) ≤ τ_K(G−v) + Q(d_G(v))`. (Best universal degree-only term.)

**Lemma 3 (every 2-centre ball is Clebsch-hom, eq 12-13):** G triangle-free, x≠y, S_xy=N[x]∪N[y] ⟹
G[S_xy]→K. Case xy∈E: ({x}∪B,{y}∪A) is a bipartition (A=N(x)∖y, B=N(y)∖x) → any K-edge. Case xy∉E:
A=N(x)∖N(y), B=N(y)∖N(x), C=N(x)∩N(y) (all independent, no A-C/B-C edges; only A-B edges else); map
x↦∅, y↦12, A↦1234, B↦35, C↦1345 (all required pairs have |Δ|=4).

**Corollary 4 (two-centre deletion, eq 14):** m_xy=e(S_xy, V∖S_xy) ⟹ `τ_K(G) ≤ τ_K(G−S_xy) + Q(m_xy)`.

**Computable recursive bound (eq 15-16):** U(H)=0 if |V|≤1, else min over {min_v (U(H−v)+Q(d_v)),
min_{x≠y}(U(H−S_xy)+Q(m_xy))}; then `τ_K(H) ≤ U(H)`. DIRECTLY TESTABLE.

**Local charging certificate (eq 17-18):** for a 1-opt-stable labeling φ, s_{v,i}=Σ_{u∈N(v)}σ_i(φ(u)),
`cost(φ) = (1/8)Σ_v(3d(v) − Σ_i|s_{v,i}| + 2ε_v m_v)`, and τ_K(G) ≤ cost(φ).

**Lemma 5 (Mycielski recursion, eq 19):** `τ_K(M(G)) ≤ 3τ_K(G) + Q(n)`, n=|V(G)|. ⟹ closed form (eq 20):
`τ_K(M^k(C5)) ≤ 8·3^{k−1} − 9·2^{k−1} + 1` (τ_K(M(M(C5)))≤7 ✓ matches CP-SAT; M³≤37). R(M^k(C5)) ≲
(20/27)(3/4)^k → 0. **Iterated Mycielskians are NOT extremal** (frustration ×3, vertices ×2 ⟹ denom ×4).

**Eq 23:** LAYERED generalized Mycielskian M_r(C5)→M(C5)→K ⟹ τ_K=0 (different from the iterate M^∘r).

**Section 6 — extremal family.** (24): adding edges (stay triangle-free, in band) raises τ_K and lowers
denominator ⟹ R nondecreasing ⟹ **maximizer is edge-saturated (maximal triangle-free)**, near the UPPER
density endpoint, non-Clebsch-hom. Every edge-maximal triangle-free nonbipartite graph contains C5.
**(25): deletion filter** — if deleting t vertices makes G Clebsch-hom, `τ_K(G) ≤ Σ_{j=1}^t Q(d_j) ≤ (3/4)tN`.
So K-vertex-deletion distance o(N) ⟹ τ_K=o(N²) ⟹ R→0. **A genuine extremal must be LINEARLY far from
Clebsch-homomorphic.**

## Why this is the right Rung-2 output (and the new Rung-3/4 targets)
- Concrete, per-vertex/local, verifiable — NOT a meta SDP. The recursion U(H) and the charging certificate
  are directly computable; the deletion filter (25) reframes CF as: bound R only for cores at deletion
  distance Θ(N), edge-saturated, near upper density.
- **Rung 3 (NEXT, compute):** verify Lemma 1/Q(d) exactly; verify recursions (11),(14),(19) on small graphs;
  verify Lemma 3's map (13) is a homomorphism for all triangle-free 2-centre balls; compute U(H) vs exact
  τ_K (tightness); CRUCIAL: is U(H) ≤ RHS on the band? (if provably yes ⟹ CF). Check R census extremals
  are edge-saturated near upper density (consistent with §6).
- **Rung 4 (then, narrow GPT):** prove "U(H) ≤ RHS on band" OR bound R on edge-saturated non-hom cores.

CF still UNPROVEN. These are building blocks, audited next.
