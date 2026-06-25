# Erdős #23 Step-2: a clean reduction to the Connected-B Gamma Lemma (consolidated, audited)

Goal: every triangle-free graph G on N vertices has β(G) = e(G) − MaxCut(G) ≤ N²/25.
After a long multi-route investigation (flag-SDP, congestion/QFC25, geodesic, PCF25, signature lemma (16),
all dead/refuted), the surviving and cleanest formulation is the **cosystole / Gamma** route, which is
Guenin/Lehman-FREE and Lean-formalizable. Below: what is PROVED, and the single precisely-stated OPEN core.

## Setup
Fix a MAXIMUM cut V = X ⊔ Y. B = bipartite graph of cut edges; M = monochromatic "bad" edges; β = |M|.
For uv ∈ M, ℓ(uv) := d_B(u,v) + 1. Cut-domination (CD): ∀W, e_M(W,~W) ≤ e_B(W,~W).
Invariant: **Γ := Σ_{uv∈M} ℓ(uv)².**

## PROVED / rigorously-audited modules (all my-own-code verified)
1. **Structural facts (3b).** Every bad edge uv has u,v in the SAME B-component, d_B(u,v) EVEN and ≥4
   (triangle-free kills d_B=2; cross-component ⟹ improving flip). So ℓ(uv) ∈ {5,7,9,…}, ℓ²≥25, **Γ ≥ 25β**.
   Hence **Γ ≤ N² ⟹ β ≤ N²/25** = Step-2. [verified]
2. **Γ ≤ N² holds numerically** over ALL 119702 triangle-free graphs N≤11 (verify_cosystole.py), 0 violations;
   tight on C_{2k+1} (m=1, B=path, ℓ=N) and on C5[q] (m=q², all ℓ=5, N=5q). [my code]
3. **Per-B-component reduction (3a) [NEW, my-code-verified 0/2461 N≤9].** For B-components on W_1,…,W_p
   (n_j=|W_j|, Σn_j ≤ N): every bad edge lies in one W_j with d_B computed inside it; the induced cut
   (X∩W_j, Y∩W_j) is a MAXIMUM cut of G[W_j]; hence Γ = Σ_j Γ_j, and IF the connected-B case gives Γ_j ≤ n_j²,
   then Γ = Σ_j Γ_j ≤ Σ_j n_j² ≤ (Σ_j n_j)² ≤ N². **Reduces Step-2 to the connected-B case.**
4. **Single-block AM-GM base case (3c) [proved, sharp].** If M is one complete-bipartite block with five
   pairwise-disjoint B-distance shells of sizes a_0..a_4 (Σa_i ≤ N), CD gives a_i a_{i+1} ≥ q (i mod 5);
   (a_0a_1a_2a_3a_4)² ≥ q⁵ and AM-GM ⟹ 25q ≤ N², i.e. β=q ≤ N²/25. **Sharp constant 25 = 5²**, tight at
   a_i = N/5 (= C5[N/5]). [min slack exactly 0.0]
5. **ν*(G) ≤ N²/25 unconditional** (Cauchy + cycle-degree inequality Σ_{v∈C}d(v) ≤ N(|C|−1)/2), tight at C5[n].
   [my code] — makes any eventual packing step non-circular.
6. **Block-cut / square-gluing reduction** (τ, ν* additive over blocks; N²≥Σn_j² ⟹ gluing): proved by hand
   (Cauchy-Schwarz + N²−Σn_j² = 1+2Σ_{i<j}M_iM_j−k ≥ (k−1)² ≥ 0, M_i=n_i−1≥1).

## THE SOLE OPEN CORE — the Connected-B Gamma Lemma (a genuine research barrier)
   **Conjecture.** Let G be triangle-free with a maximum cut whose cut-edge graph B is CONNECTED on all N
   vertices. Then Γ = Σ_{uv∈M} (d_B(u,v)+1)² ≤ N².
Status: numerically TRUE (0 violations, B-connected, N≤10), tight only at C_{2k+1} and C5[q]. The single-block
case is module 4 above (proved, sharp). The OPEN difficulty is the **block → connected-B transfer in the
THETA REGIME** (a bad edge whose B-endpoints are joined by paths of different even lengths, e.g. 4 and 6 —
the minimal witness `c5paths20`), where there is NO global 5-shell layering to assemble the per-block
pair-products, so the AM-GM constant 25 is asserted-to-transfer, never derived.
Why it is hard (audited dead ends):
 - The block contradiction bound 25|F| ≤ n_A² binds (ratio=1) ONLY at the full graph (= the theorem itself):
   no intermediate local regime has slack to drive an induction (probe_sync_circular.py).
 - Any SINGLE scalar potential / coarea caps at the LINEAR bound 4|M| ≤ |B|, far from quadratic 25.
 - The signature-based dual (lemma (16)) has the "signature rotation" pathology (optimal signature depends on
   the toll; K23: single-sig 4/3 vs mixed 6/5) — defeated a deep GPT-Pro LP-dual attempt and a 6-angle
   Workflow. Γ AVOIDS this (signature-free) but then needs the quadratic transfer.
 - Closing it requires a genuinely QUADRATIC / electrical-flow (multicommodity-congestion) dual whose
   sublevel sets feed CD without exceeding per-level capacity and hit equality at BOTH tight families
   (C_{2k+1} and C5[q]). No such certificate currently exists.

## All certificate routes hit the SAME tight/circular wall (audited)
Independently of the proof attempt, the bound Γ ≤ N² is "self-tight": every relaxation/certificate equals Γ
at its optimum, so it re-expresses Γ ≤ N² rather than proving it. Confirmed for:
 - flag-SDP (order-9 η frozen +2.3e-5, moment hierarchy saturates);
 - the signature lemma (16) LP-dual (signature-rotation; κ* = 6/5 at K23 by mixing, no canonical measure);
 - GPT's QUADRATIC CUT-PAIR / QCD certificate (verify_QCD.py): the convex QP min_{a≥0} Σ_{S,T} a_S a_T
   min{b(S),b(T)} s.t. coverage h_a(e)=ℓ_e equals Γ EXACTLY on every instance (C5 25=25, C5[2] 100=100,
   Petersen 75=75, K23-N13 100=100). So QCD gives only Γ ≤ Γ; "∃a: Σ a a min{b,b} ≤ N²" ⟺ Γ ≤ N² (the
   theorem). Any non-circular proof must come from a STRUCTURAL budget argument (GPT's common-energy-profile
   z + theta-cut multipliers α with Σ α_S Z_{b(S)} ≤ N), constructed without reference to Γ — which no
   attempt has produced. [GPT consulted on whether the energy-profile genuinely escapes the tightness.]

## Honest verdict
NOT a closure (all-or-nothing requires a complete sorry-free Lean proof). The deliverable is a clean,
Lean-formalizable REDUCTION of Erdős #23 Step-2 to the single Connected-B Gamma Lemma, with the per-component
reduction and the sharp single-block base case proved. The connected-B theta-transfer is the genuine open
core, and it is "self-tight" (every certificate route equals Γ at the optimum) — a genuine research barrier.
