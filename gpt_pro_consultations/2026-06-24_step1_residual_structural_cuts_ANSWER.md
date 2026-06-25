# GPT Pro Answer — Step-1 residual structural cuts (no brute force)

Source: ChatGPT Pro (Kapsamlı Pro), chat "Erdos Problem 23 Cuts" /c/6a3b562d. Prompt:
2026-06-24_step1_residual_structural_cuts_prompt.md. **NOT fully audited** — verify each cut
(false-closure history; the prior audit caught GPT dropping terms). Notation: a=|A|, b=|B|,
a+b=26-q; U=|S1|+|S2|+2|D|; e = 30-q + U + e_R + p + M.

## (a) BAND-TOP density separator (e=140..143) — via WEIGHTED blow-up into BCL high-density
**WBCL lemma (rigorous, claimed):** weights w_v with Σw=1, E_w(G)=Σ_{uv∈E} w_u w_v,
β_w(G)=min weighted mono mass. ρ = 0.3197/2 = 0.15985. Then **E_w(G) > ρ ⟹ β_w(G) ≤ 1/25**
(rational blow-up of v into class ∝ w_v; min cut doesn't split a class; BCL high-density applies
to the blow-up). Since every cut leaves ≥37 edges, β_w(G) ≥ Σ_{i=1}^{37} z_i (37 cheapest edge
products w_u w_v). Hence **Σ_{i=1}^{37} z_i > 1/25 ⟹ E_w(G) ≤ ρ** (37-WBCL): a 37-item knapsack.

- **Max-degree cut:** p_0=1/925, b_0=1/(5√37); one-heavy-vertex weighting ⟹
  e/925 + b_0(1-30 b_0) d(v) ≤ ρ. Gives Δ(G): e=140→Δ≤18, 141→16, 142→14, **143→Δ≤11**. [VERIFIED numerically consistent.]
- **Independent-set weighting** ⟹ band-top α(G),Δ(G) (eq5): e=143 ⟹ α≤12, Δ≤11; 142⟹≤12,≤12; 140,141⟹≤13,≤13.
- **Neighbourhood-sum sandwich (NS):** ⌈L_{d(v)}(e)⌉ ≤ Σ_{u∈N(v)} d(u) ≤ e-37, L_k(e)=(e h_k²-ρ)/(h_k²-p_0).
  Table (lower bounds) e=143: d=8→61,9→72,10→84,11→95,12→105,13→115.
- **★ Upper bound Σ_{u∈N(v)} d(u) ≤ e-37 is valid for EVERY vertex** (N(v) independent in tri-free G),
  not just empty-E R-vertices — "insert globally." [SOUND — same proof as the existing E-ND cut.]
  Rooted forms: S_x=4+U+a+p+M_A; S_y=4+U+b+p+M_B; S_{c1}=30-q+|S1|+2|D|+D_R(S1∪D)+M_S1+M_D; S_{c2} sym.
- **idx100 example (q=11,(0,2,2,7),e=143):** d(c1)=d(c2)=11, L_11(143)>94 ⟹ S_{c1},S_{c2}≥95 ⟹
  35+e_R+M_S1+M_D ≥95; with δ≥8 (M_S1,M_S2≥14-e_R) ⟹ **M+2e_R ≥ 74**; since M+e_R=106-p at e=143 ⟹ **e_R ≥ p-32**.
- **Class-weight separator (strongest):** ~10 class weights, edge-type multiplicities m_ij, take cheapest 37
  units Q_37; **Q_37 > 1/25 ⟹ W ≤ ρ** (eq18). Replaces stalled CP-SAT in e=140..143 cells (10 weights + 37-knapsack).

## (b) Exact skeleton reductions for big grids
1. Colored canonical augmentation (quotient by S_E×S_S1×S_S2×S_D + c1↔c2/S1↔S2 + x↔y/A↔B); generate canonically not mask-dedup.
2. **E+D (idx232/233):** core H=R[E] + UNORDERED MULTISET of independent-set attachments I_i∈I(H) for D.
   Labeled t^|D| → C(t+|D|-1,|D|) before Aut(H). e_R=e(H)+Σ n_I|I|, etc. Apply (15)-(17) to multiplicity vector.
3. **E+S1+S2 (idx270):** core H + S1-attach types I_s=N_E(s), S2-attach J_t=N_E(t), with st∈E_R ⟹ I_s∩J_t=∅;
   generate compatible blocks; run degree/column quotient on (n_I,n_J,z_IJ) BEFORE bipartite realization.
4. **pure S1+S2 (idx254):** enumerate Gale-Ryser degree partitions before matrices; codegree-demand cut
   Λ(H)=2(uv-e_R)+Z1+Z2 with Z1≥[C(u,2)-Σ C(c_j,2)]_+, Z2 sym — degree-seq-only lower bound on A/B common-nbr budget.
   (Ferrers/subset-domination NOT safe; use canonical augmentation + genuine twin classes.)

## (c) UNIFORM reduction for all 263 — state-free SECOND-SHADOW QUOTIENT
Retain α_r=e(r,A), γ_r=e(r,B); pair moments u^A_rs,u^B_rs (Fréchet 28; =0 if rs∈E_R; ≥[2-c_rs-ν_rs]_+ if nonedge, eq30).
Row-degree histograms n^A_jk (#A-vtx with j R-nbrs, k B-nbrs): Σ=a, Σj=M_A, Σk=p; n^A_jk=0 unless 8≤1+j+k≤Δ_e;
consistency v^A_rjk (33-35). Global 2nd-moment cuts: **Σ α_r γ_r ≥ 2(ab-p)** (36); **Σ C(α_r,2)+Σ n^B_jk C(k,2) ≥ C(a,2)** (37);
sym (38). Cheap aggregate Λ(R) ≤ F(M_A;a,K)+F(M_B;b,K) (39). Column-imbalance Σ|z_r+ε1ι1+ε2ι2| ≤ M+U+2e_R-70 (40).
"A projection of every genuine state solution ⟹ infeasibility is a rigorous closure certificate." O(q²) vars, no state masks.

## Recommended execution order (steps 1-4 RIGOROUS; only the reduction AMOUNT is heuristic)
1. Pre-skeleton: apply (5), root/c_i NS, side bounds 7a≤p+M_A≤(Δ_e-1)a, 7b≤p+M_B≤(Δ_e-1)b.
2. Generate skeletons canonically (core/attachment per support).
3. Second-shadow quotient (15-17, 28-40): O(q²), no masks.
4. e=140..143: class-weight 37-WBCL separator (18) per surviving scalar cell.
5. Only remaining canonical skeletons → exact state-count CP-SAT.
