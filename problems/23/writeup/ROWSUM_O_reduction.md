# Erdős #23, δ=0 (Γ ≤ N²) reduced to a single spectral inequality — ROWSUM-O

**Status (2026-06-27).** The whole remaining conjecture (every triangle-free graph G on N vertices has
β(G) = e(G) − MaxCut(G) ≤ N²/25) is reduced to ONE scalar inequality, **ROWSUM-O**, with every other step a
rigorously proven identity/standard fact. ROWSUM-O is verified 0-violation by exact rational arithmetic over the
full triangle-free census N ≤ 11 (65244 graphs at N=11), all C_{2k+1}[t] blow-ups to N=49, the N=22 graph that
falsified the earlier "sandwich" route, Grötzsch, iterated Mycielskians, and random triangle-free graphs to N=24.

## Setup
Fix a maximum cut of G; let B be the (bipartite, connected) set of cut edges and M the set of **bad edges**
(monochromatic, i.e. both endpoints on the same side). Triangle-free ⟹ every bad edge f=(a,b) closes an odd cycle
of length ℓ(f) = d_B(a,b)+1 ≥ 5 (d_B = distance in B). Set Γ := Σ_{f∈M} ℓ(f)².

For a bad edge f=(a,b), let p_f(v) be the fraction of shortest a–b B-geodesics passing through v (so p_f(v) ∈ [0,1]
and Σ_v p_f(v) = ℓ(f)). Let P be the V×M matrix P[v,f] = p_f(v), and define
- the load  T(v) := Σ_{g∈M} ℓ(g) p_g(v),
- the incidence field  S(v) := Σ_{g∈M} p_g(v),
- the geodesic-overlap Gram matrix  O := PᵀP, so O_{fg} = ⟨p_f,p_g⟩ = Σ_v p_f(v)p_g(v) ≥ 0,
- K := PPᵀ, K_{vw} = Σ_f p_f(v)p_f(w).

## The single open inequality
> **(ROWSUM-O).** For every bad edge f:  `Σ_g O_{fg} = (O·1)_f = Σ_v p_f(v) S(v) ≤ N.`

## The reduction (all steps below are PROVEN)

**Lemma 1 (load identity, P1).** Σ_v T(v) = Γ.
*Proof.* Σ_v T(v) = Σ_f ℓ(f) Σ_v p_f(v) = Σ_f ℓ(f)·ℓ(f) = Γ (each shortest geodesic has ℓ(f) vertices). ∎

**Lemma 2 (Gram identities).** (i) (O·1)_f = Σ_v p_f(v) S(v).  (ii) ℓᵀ O ℓ = Σ_v T(v)², where ℓ = (ℓ(f))_{f∈M}.
*Proof.* (i) (O·1)_f = Σ_g ⟨p_f,p_g⟩ = Σ_v p_f(v) Σ_g p_g(v) = Σ_v p_f(v)S(v).
(ii) ℓᵀOℓ = Σ_{f,g} ℓ(f)ℓ(g)⟨p_f,p_g⟩ = Σ_v (Σ_f ℓ(f)p_f(v))(Σ_g ℓ(g)p_g(v)) = Σ_v T(v)². ∎

**Lemma 3 (Perron–Frobenius row-sum bound).** Since O is symmetric and entrywise ≥ 0,
ρ(O) = λ_max(O) ≤ max_f Σ_g O_{fg} = max_f (O·1)_f.
*Proof.* Standard: for a nonnegative symmetric matrix, the spectral radius is at most the maximum row sum
(λ_max ≤ ‖O‖_∞ = max row sum). ∎

**Theorem (ROWSUM-O ⟹ #23).** If ROWSUM-O holds then Γ ≤ N², hence β ≤ N²/25.
*Proof.*
1. ROWSUM-O + Lemma 3 ⟹ ρ(O) ≤ N.
2. O is PSD (Gram), so ℓᵀOℓ ≤ ρ(O)·‖ℓ‖² ≤ N·‖ℓ‖². By Lemma 2(ii), ‖ℓ‖² = Σ_f ℓ(f)² = Γ, and ℓᵀOℓ = Σ_v T(v)².
   Hence Σ_v T(v)² ≤ N·Γ.
3. By Cauchy–Schwarz and Lemma 1, Σ_v T(v)² ≥ (Σ_v T(v))²/N = Γ²/N. Combining, Γ²/N ≤ NΓ ⟹ Γ ≤ N².
4. Triangle-free ⟹ ℓ(f) ≥ 5 for every bad edge, so β = |M| = Σ_f 1 ≤ Σ_f ℓ(f)²/25 = Γ/25 ≤ N²/25. ∎

(The factor 5 is the only place ℓ ≥ 5 / triangle-freeness is used in this final step; ROWSUM-O itself also requires
ℓ ≥ 5 — it is FALSE for general graphs.)

## Supporting proven facts (toward proving ROWSUM-O)
- **Diagonal bound.** O_{ff} = ‖p_f‖² = Σ_v p_f(v)² ≤ (max_v p_f(v))(Σ_v p_f(v)) ≤ 1·ℓ(f) = ℓ(f) ≤ N.
- **Betweenness factorization.** p_f(v) = σ_a(v)σ_b(v)/σ_ab, where σ_a(v)=#shortest B-paths a→v,
  σ_b(v)=#shortest v→b, σ_ab=#shortest a→b. (Brandes/centrality identity; verified 0-mismatch census N≤10.)
- **Layer-uniformity.** With interval layers I_i(f) = {v : d_B(a,v)=i, d_B(v,b)=ℓ(f)−1−i}, Σ_{v∈I_i(f)} p_f(v) = 1.
- **Incidence ≤ load/5.** S(v) ≤ T(v)/5 (since T = Σ_g ℓ(g)p_g ≥ 5 Σ_g p_g = 5S).
- **K row sums.** K·1 = T (row sums of K are the loads); B := diag(T) − K is a PSD zero-row-sum (Laplacian-type)
  matrix; ρ(O) = ρ(K). Equality ρ(O) = N holds EXACTLY when T ≡ N (uniform load ⟺ Γ = N² ⟺ the C_{2k+1}[t] extremal,
  where the constant vector is the Perron eigenvector of K).

## What does NOT prove ROWSUM-O (each refuted with an exact witness)
- CD endpoint-separation cut-metric ("Crofton" LP): refuted (separating-cut multiplicity m_f ≥ 2 inflates the bound;
  cuts cannot see the vertex-set overlap ⟨p_f,p_g⟩).
- Combinatorial charging / double-counting: the content is in the p_f-MEASURE weighting; every set/counting
  relaxation fails by large census margins.
- Geodesic flow / Menger / LP-dual on incidence: collapses to the layer-cover bound `rowsum_f ≤ Σ_i max_{I_i}S`
  (which overshoots N) or is circular.
- Overlap-packing LP (max Σ O_fg x_g, x_g ≤ 1, Σ sep_A(g)x_g ≤ δ_B(A)): CIRCULAR — its optimum equals (O·1)_f via
  the trivial dual μ_g = O_fg, λ = 0 (no cuts, CD never used).
- Simple norm bounds: ‖P‖² ≤ ‖P‖_1‖P‖_∞ = (max ℓ)(max S) ≈ 0.27N²; Cauchy–Schwarz splits give the trivial max-row-
  sum max_v T(v) > N. Both far too lossy.
- Per-cycle (Σ_{v∈C}S(v) ≤ N: false, up to 1.067N), per-layer, symmetric-pair, local Gershgorin-on-vertices.

## The live proof directions (a global spectral anti-concentration fact)
1. **Spectral comparison** K ⪯ M for an explicit odd-cycle/circulant model operator M with ρ(M) = N, from
   triangle-freeness + odd-girth ≥ 5.
2. **Non-circular SOS** N·I − K = L + R with L a graph Laplacian and R manifestly PSD via the betweenness
   factorization. (The exact split N·I − K = Σ_f [diag(N p_f/S) − p_f p_fᵀ] is circular: the f-th block is PSD ⟺
   ROWSUM-O(f).)
3. **Within-layer majorization** (Chebyshev sum): in each layer I_i the p_f-measure (= betweenness restricted to the
   layer) is anti-correlated with S, so the p_f-weighted average of S over the layer is controlled, recovering ≤ N
   only after summing layers (the per-layer max overshoots).

## Schur-complement M-matrix certificate for SPEC (ρ(K) ≤ N): condition (2) is FREE given (1)

The Schur route proves A = N·I − K ⪰ 0 (⟹ SPEC ⟹ Γ ≤ N²) from three conditions on the overloaded set
O = {v : T(v) > N}, Q = V\O: (1) A[Q,Q] = N·I − K_QQ is a nonsingular M-matrix (so M := (N·I−K_QQ)⁻¹ exists and is
entrywise ≥ 0); (2) the Schur complement E = A[O,O] − A[O,Q] M A[Q,O] has off-diagonal ≤ 0; (3) E has nonnegative
row sums. **Condition (2) is automatic given condition (1)** (no triangle-freeness or census needed):

**Lemma (2-free).** Assume (1). For distinct o, o′ ∈ O,
  E[o,o′] = A[o,o′] − A[o,Q] M A[Q,o′] = −K[o,o′] − K[o,Q] M K[Q,o′] ≤ 0.
*Proof.* For o ≠ o′ the diagonal N·I does not contribute, so A[o,o′] = −K[o,o′] and the off-diagonal blocks of
A = N·I − K are A[o,Q] = −K[o,Q], A[Q,o′] = −K[Q,o′]. Substituting, the two minus signs on the blocks cancel:
E[o,o′] = −K[o,o′] − K[o,Q] M K[Q,o′]. The first term is ≤ 0 since K = PPᵀ ≥ 0 entrywise. The second term
K[o,Q] M K[Q,o′] = Σ_{q,q′∈Q} K[o,q] M_{qq′} K[q′,o′] is a sum of products of three nonnegative factors (K ≥ 0
entrywise; M ≥ 0 entrywise by (1)), hence ≥ 0; with the leading minus it is ≤ 0. So E[o,o′] ≤ 0. ∎

(Edge cases: |O| = 1 ⟹ no off-diagonal, (2) vacuous; Q = ∅ ⟹ E = N·I − K_OO, off-diagonals = −K[o,o′] ≤ 0
trivially.) Thus the open conditions for the Schur certificate reduce to **(1) and (3) only**.

*Exact verification (Fraction) of the sign decomposition.* `_cond2_free.py` / `_cond2_census.py` confirm
0 violations of (a) M entrywise ≥ 0 [cond 1], (b) q := K[o,Q] M K[Q,o′] ≥ 0, (c) E[o,o′] ≤ 0, over the full
triangle-free connected census N = 7,8,9,10 (0 singular A[Q,Q], min q > 0, max E_offdiag < 0) and N = 11 (sampled,
28 cases with |O| ≥ 2), plus the N=22 sandwich-killer J???E?pNu\?[2] (|O|=6), overloaded blow-ups N=20,24
(I?BD@g]Qo[2], I?ABCc]}?[2], G?bF`w[3]). In every case relies_on_cond1 = False (no q ever went negative).

## Condition (1) reduces to a connectivity lemma; the finite-depth proof of (3) is FALSE at N=23

**Condition (1) (A_QQ nonsingular Stieltjes M-matrix) ⟸ NO-Q-ONLY connectivity.** Proven elementary facts:
K_QQ ≥ 0; for q∈Q, Σ_{q′∈Q}K[q,q′] ≤ (K·1)[q]=T[q] ≤ N, so ρ(K_QQ) ≤ N (Perron max-row-sum); A_QQ=N·I−K_QQ is a
symmetric Z-matrix, PSD, and *nonsingular iff ρ(K_QQ)<N strictly*. Decompose Q into K_QQ-components; within a
component C the row sum is s_q=T[q]−leak[q], leak[q]=Σ_{o∈O}K[q,o], and ρ on C equals N iff every q∈C has T[q]=N AND
leak[q]=0 ("critical" component). **Irreducibility-lever theorem (proven):** a critical component C is K-closed in V,
so the Perron vector of K|_C extended by 0 satisfies Kx=Nx, x≥0, x=0 on O — if K|_{T>0} is irreducible this contradicts
strict positivity of the global Perron vector; hence no critical component and ρ(K_QQ)<N. **Residual open lemma
NO-Q-ONLY:** K|_{T>0} is connected (no bad-edge K-component lies entirely in Q). Verified 0-exception exact over census
N≤11 + overloaded blow-ups N≤24 + random N≤15; same odd-girth anti-concentration difficulty class as ROWSUM-O.
(Files: `COND1_proof.md`, `_cond1_proof.py`, `_K_qonly.py`, `_load_connected.py`.)

**Boundary-deficit reformulations (audited; all = NO-Q-ONLY, no local proof).** Codex's BOUNDARY-DEFICIT candidate
(deficit(C) := N|C| − Σ_{v∈C}T[v] ≥ dB(C) = #B-edges leaving C, for every K-component C disjoint from O) is exact-true
(0 violations: full census N≤11, 2311 random triangle-free N≤16, Mycielskians N≤31, island gluings to N≤25; min slack
+4 on real proper components, +74 on adversarially-glued bad-carrying Q-only components) and boundary-deficit ⟹ cond(1)
is airtight. Two clean exact identities (a K-component is K-closed ⟹ its load mass comes only from internal bad edges):
**mass(C) = Γ_C := Σ_{f: supp(p_f)⊆C} ℓ(f)²**, and **deficit(C) = 1_Cᵀ(N·I−K)1_C** (the A=N·I−K Dirichlet energy at the
component indicator). So boundary-deficit ⟺ Γ_C + dB(C) ≤ N|C|. BUT it is **vacuous on every real graph**: no
bad-carrying Q-only K-component ever coexists with O≠∅ (only Q-only components are isolated T=0 singletons; on the
Mycielskians K spans V) — so its sole non-trivial content is excluding a hypothetical non-trivial critical component,
i.e. NO-Q-ONLY verbatim. **No local proof exists:** the candidate local bounds Γ_C ≤ |C|² (Codex's "LCB" self-cap) and
the per-vertex charge N−T(v) ≥ crossdeg_B(v) are both refuted exactly (Γ_C=50>36=|C|² at the O-empty graph I?AAD@wF_;
charge −2 at saturated vertex I??CABoNo v=9); underload must be *pooled* over C. ROWSUM-O is strictly stronger (⟹
ρ(K)≤N ⟹ cond(1)+cond(3) at once), co-tight at the same C5[t] extremizer. **Inductive angle (open):** a critical
component has T≡N ⟹ Γ_C=N|C|; since O≠∅ forces |C|<N, the island bound Γ_C ≤ |C|² would give N|C| ≤ |C|² ⟹ N ≤ |C|, a
contradiction ⟹ no critical component ⟹ cond(1). The gap is exactly LCB: whether the global max cut restricts to a
good-enough cut on the K-closed island that Γ_C ≤ |C|² (an induction-on-N hypothesis). (Audit: 4-agent workflow
wf_076d9c97, all numbers re-verified; files `_bdef.py`, `_bdef_identity.py`, `_bdef_all.py`, `_zmu.py`, `_lcb.py`,
`_bdef_construct.py`, `_bdef_theory.py`.)

**Best cond(1) lever = SAT-ZMU (Codex), and the traffic handshake.** Define cut-edge traffic μ(e)=Σ_f Σ_{geodesic
P∈cyc(f) using e} ℓ(f)/|cyc(f)|. *Full ZMU* (zero-μ cut edge ⟹ a T=0 endpoint) is FALSE (C5+Myc(C7) glued, N=20:
edge (0,5) is zero-μ with endpoints T=5, 15/2). *SAT-ZMU* (zero-μ cut edge ⟹ neither endpoint saturated, T≠N) holds
0-violation over census N≤11 (122 zero-μ edges; non-vacuous at N=11 — 3 graphs have a saturated vertex AND a zero-μ
edge, never coinciding), 32 glued constructions, and 224 unequal blow-ups (Codex). SAT-ZMU ⟹ cond(1): a critical
component (T≡N) has all boundary edges zero-μ and incident to saturated vertices ⟹ SAT-ZMU violated; B connected ⟹ a
proper critical component has a boundary edge ⟹ contradiction. **Traffic handshake (proven exact identity):**
Σ_{e∋v, e∈B} μ(e) = 2T(v) − D(v), D(v)=Σ_{f: v an endpoint} ℓ(f) (each geodesic through v uses 2 incident edges if
interior, 1 if endpoint). It gives the per-vertex budget (2N−D(v) at a saturated vertex) but is necessary-not-sufficient
for SAT-ZMU (a positive *sum* over incident edges does not force *each* >0); the residual is a per-edge geodesic-routing
non-degeneracy, needing a γ-min/flow argument. Files `_satzmu.py`, `_satzmu_refute.py`, `_handshake.py`.

**Resolution — SAT-ZMU-CONN (tie-invariant).** SAT-ZMU-CLASS is not invariant over all γ-min cuts (an N=12
leaf-extended graph has an equal-Γ cut with a saturated zero-μ endpoint and O≠∅), so it must be stated for the chosen
cut; the reduction allows this (β=|M| is cut-independent, all γ-min cuts share Γ, so Γ≤N² for one ⟹ the bound). The
clean tie-INVARIANT form is **SAT-ZMU-CONN**: for any γ-min connected-B max cut with O≠∅, a zero-μ B-edge with a
saturated endpoint u has u in a K-component that *meets O*. This directly gives cond(1) (a critical Q-only K-component
would put a saturated zero-μ-boundary endpoint in a K-component disjoint from O — contradiction) and needs no tie-break.
Verified 0-violation across **every** γ-min connected-B cut of the full census N≤10 (multi-cut enumeration), the
loads-cut gate, and all 11 γ-min cuts of the N=12 caveat (incl. the cut that breaks SAT-ZMU-CLASS — there the saturated
endpoint lies in the overload K-component). Proof target: a load-saturated endpoint of a geodesically-idle (zero-μ)
B-corridor is K-connected to O. File `_satzmu_conn.py`.

**⚠️ The finite-depth (k=2 Neumann) proxy of condition (3) is FALSE at N=23 (false-closure caught).** Condition (3) is
the TRUE full-depth Schur row sum E·1_O = r_O + K[O,Q]·(N·I−K_QQ)⁻¹·r_Q ≥ 0 (r=N−T). The k-step Neumann truncation
g_k=Σ_{t<k}(K_QQ/N)^t(r_Q/N) gives a monotone lower bound; the proposed "(k2): truncation at k=2 ≥ 0" proof was verified
0-violation over census N≤11 + blow-ups N≤24 but **fails on the iterated Mycielskian C5→Grötzsch(N=11)→Myc(Grötzsch)(N=23)**
(triangle-free, not a blow-up): at the overloaded high-incidence vertex o=22, (k2)·N² = −10842333408378828581/28344980104623000
< 0 (exact). The first nonnegative Neumann depth there is k=3, and the required depth grows with N — **no fixed finite
depth proves (3).** The certificate *condition* (3) itself still holds at N=23 (true full-depth row sum = +1062409533481/
161917129667 = +6.561 > 0; ROWSUM-O also holds, max row sum 19347/910 < 23), so the reduction is intact — only the
finite-truncation proof strategy is dead. (Files: `_k2_n23_indep.py`, `_h1h2_n23.py`, `_audit_k2fail.py`,
`_audit_myciel.py`.) **Standing stress requirement:** test every candidate inequality on iterated Mycielskians
(N=11, 23, 47), which break finite-depth proofs that the census + i.i.d. blow-ups miss.

**Surviving frontier (two routes to SPEC, both = the same global odd-girth ≥ 5 anti-concentration):**
(A) ROWSUM-O direct: Σ_v p_f(v)S(v) ≤ N per bad edge f (⟹ ρ(O) ≤ N by Perron). (B) Schur certificate:
condition (1) = NO-Q-ONLY connectivity, condition (3) = true full-depth Schur row sum ≥ 0; condition (2) is proven.
No fixed-coefficient per-edge/per-pair SOS suffices (exact witness: J???E?pNu? o=9 needs κ ≥ 2.93 but min-edge κ = 2.87);
the proof must use the joint correlation of edge weight p_f(o) with its load coupling — e.g. a spectral comparison
K ⪯ (odd-cycle model operator, ρ = N) derived from odd-girth ≥ 5 used globally.

## Verification files (problems/23/writeup/)
`_schur_spec.py` (exact Schur cert (1)(2)(3)), `_cond2_free.py`/`_cond2_census.py` (cond(2)-free sign decomposition),
`_rowsum_verify.py` (exact rational ROWSUM-O, census + blow-ups + N=22 witness), `_gram_spectral.py` (ρ(O)),
`_crofton_lp.py`/`_overlap_lp2.py`/`_dual_analysis.py` (refuted/circular cut & overlap LPs), `_pf_factor.py`
(betweenness factorization), `_strat2_chain.py`/`_waterfill_exact.py` (A⟹Γ≤N² chain, SOS identity), `_h.py` (helpers).
