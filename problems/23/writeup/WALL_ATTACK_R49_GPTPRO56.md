# WALL ATTACK — R49: ENDPOINT TRICHOTOMY; ORDER-14 CLOSED (range 15-21); CLUSTERING CANNOT CLOSE 15-21;
# TWO-OWNER DOUBLING ADDS NOTHING; EXACT ACTIVE-SCOPE CRITERION; DISJUNCTION SHELL; P ~3%
# (GPT-5.6 Pro, 2026-07-12, "worked 11m43s"; harvested ~14.5k ch)

**[CLAUDE GATE HEADER + ENGINE OVERLAY (same hour, supersedes the triangle branch): Codex FALSIFIED
t5_localProfile_forces_badTriangle EXACTLY — zero-vector triangle-free 25/24 circuit at 9+9 support #298
(graph6 Q??????wE_[?EGs?D_@A?C_B???; 297 prior infeasible; classifier (0,0,0,0); full profile constructed
and re-verified independently: r(v)=5, v-17 absent from support, all pairs covered, atom+support triangle
count 0; verifier SHA 017D1E44/artifact 48ce1638). THE FALLBACK SURVIVES: the hit's active component =
{0,17}, NO bad endpoints ⟹ ActiveOwner FALSE;**scope-vacuity is EXACT over ALL row choices** (CP-SAT
INFEASIBLE f5c0cbca + independent CaDiCaL UNSAT 1680 vars/5239 clauses a8a160d5); the displayed cut also
fails maxcut (min switch sigma -20). Staged sweep: first 350 no-shared 9+9 supports ALL rejected at active
scope (bounded). **LIVE LEMMA = t5_triangleFree_localProfile_is_scopeVacuous** (R49's disjunction shell with
the triangle branch dead as standalone). My replay queue: c1d474d7 hit + 48ce1638 + f5c0cbca + a8a160d5 +
f0cd4403. R49's own content below remains valid: order-14 exclusion is a LEDGER-quality lemma.]**

## 1-2. Endpoint trichotomy + clustering bound
Coverage row for {x₀,y_i} avoiding v: positions {0,2} (Type 0: row (x₀,q,y,s,c), atom x₀c; q,s ∉ N_M(v)
[triangle], c ∉ N_B(v); distinct Type-0 atoms have distinct c) / {1,3} (Type 1: (a,x₀,q,y,b), atom ab; ALL
THREE of a,q,b on v's shore OUTSIDE {v}∪N_M(v)) / {2,4} (Type 2: atom cy; c's shareable). Compile:
T5CoverageEndpointPattern + coverageRow_endpointTrichotomy. Bound: |V(F*)| ≥ 11 + ℓ_ext + r_ext
(ℓ_ext = 3 if c₁>0 else 2; r_ext = max(c₀, [c₂>0])).

## 3. ORDER-14 CLOSED (ledger lemma)
|V|=14 ⟹ 3 external vertices. c₁>0 ⟹ r_ext=0 ⟹ all four coverage atoms Type-1 on 3 external owner-shore
vertices ⟹ 4 distinct atoms in a 3-vertex graph (max 3) — CONTRADICTION (no atom-triangle-freeness needed).
c₁=0 ⟹ shores 8+6 ⟹ Mantel 16+9=25 forces equality ⟹ bad graph on 8-shore = K_{4,4}, max degree 4 < 5 =
dM(v) — CONTRADICTION. **t5_localProfile_supportOrder_ge_fifteen: range 15 ≤ |V| ≤ 21.**

## 4-5. Limits
Clustering + Mantel CANNOT close 15-21: explicit triangle-free abstract endpoint pattern (v+p₀..p₃ vs
b₀..b₄ bipartite-on-shore bads + 4 Type-0 coverage) satisfies all local counts — deletion-SDR/complete-
support geometry must carry the rest. TWO-OWNER DOUBLING ADDS NOTHING: coverage atoms shared via the two
middle orientations ((x₀,m,y,…) vs (x₀,v,y,…)) = exactly the bounce structure; committed atoms 10+4 = 14 ≤
25; k=3 floor 19 ≤ 25. The near-candidate realizes both owners' profiles simultaneously.

## 6. Exact active-scope criterion
deg_I(v)=1 ⟹ v's component = {v} ∪ K_ω(v,x₀) (tail). **v active ⟺ incident capture (∃b ∈ tail, vb bad;
needs I-path ≥ 3 from x₀ to b [length-1 would triangle]) ∨ remote capture (whole bad edge in tail; needs
I-path ≥ 4).** Compile: degreeOneProfile_active_iff_tailCapturesBad. The profile places NO condition on
extra internal edges leaving x₀ — vacuity not forced locally.

## 7-8. Sweep decision tree + the refined frontier
Zero-vector candidates: record coverage type-word ∈ {0,1,2}⁴, all matching combinations, tuples, tail
component, verdict ∈ {incidentCapture, remoteCapture, scopeVacuous}. Outcomes: no zero-vector ⟹ triangle
lemma by enumeration [NOW MOOT — falsified]; all scope-vacuous ⟹ fallback proved for the class [CURRENT
DATA]; active candidate ⟹ second owner + matching + ledger. **Refined sufficient shell:
t5_profileCircuit_triangle_or_scopeVacuous** (disjunction; near-candidate lands in both branches). FIRST
MISSING USE OF MINIMAL DEFECT ONE: the 16 non-profile atoms must complete the 25/24 transversal circuit —
prove completion forces triangle OR captureless tail. k=3: same treatment; closed instantly if the
disjunction is proved for one owner. **P ≈ 3%** (superseded by the engine events toward the scope branch).
