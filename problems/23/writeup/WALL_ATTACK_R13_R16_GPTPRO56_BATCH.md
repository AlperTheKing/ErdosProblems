# WALL ATTACK — batch replies 2-5 (R13-R16), GPT-5.6 Pro, 2026-07-11, USER-RELAYED — GATES PENDING

## R13 — "Decision (B)": aggregate spendQ ledger CANNOT imply half-layer routing
- COUNTERMODEL (7-vtx wall data: x-a-b-c-y unique ℓ=5 row, exits xx',yy'; W_L={x},W_R={y} petals; TWO+PETAL
  hold; ledger = one door token cap 25, spend 0, ALL Checked fields pass; **Legal = ∅**): dual α=γ=γ=1/3,
  δ=0, all 32 D1 rows checked, D2 vacuous, StrictGap = 1/3 > 0, but HalfLayerRouted impossible (L_p = 1/2,
  no legal arcs). SEMANTIC INDISTINGUISHABILITY: adding Legal' = {(p_L,t),(p_R,t)} keeps every Checked field
  identical but makes routing exist ⟹ NO theorem from aggregate fields alone. Failure is INCIDENCE, not
  capacity (25 ≫ 1).
- REPAIR (adopted, Codex lane): **typed token sources** — sourceId : Nat → kind-indexed
  CapSource (door ⟹ ExitEdgeKey = index into extractor's exit-edge array; vertexSlack ⟹ VertexKey; baseLeaf/
  prune ⟹ keys); LedgerToken.source dependent; uniqueness on (comp,kind,source). checkOwnEdgeDoors (exact
  source-key equality + uniqueness count + 1 ≤ wallSinkCap) ⟹ doorOf map with legality (5) + injectivity (6)
  FROM TYPED EQUALITY (no supplied propositions). Full Lean proof sketch for
  halfLayerRouted_of_checkedEdgeDoorSources given (ρ = own-door routing; loads ≤ 1/2; petal-disjoint edge
  loads ≤ 1). Claimed checker SHA 9437d330…
## R14 — unannotated Horn-derivation implication FALSE
- 13-vtx COUNTERMODEL: bad f=xy; two even disjoint x-y paths P4 (support) + P6 (six zero-cap typed sinks);
  exits xx°,yy°,bb°; maxcut 13 unique-up-to-complement; ℓ=5; Γ=25 min. Dual α=1/13, γ=δ=1/13 on P6 edges;
  1024 D1 rows via path parity; StrictGap 1/13. Tight crossing X={x,r1,r2,u,b}, Y={y,r3,v,b} (I,J slack 0,
  four-corner applies). Horn rules make ∅/full the only closed shores; first collision Z; deficiency 1;
  NO split AND NO TwoCover (any two-cover forces ≥1 load onto zero-cap P6 sinks (8); X∩Y={b}≠∅). Individual
  rule labels (edge/inside/atom/corridor/wall-row/sink) all checkable yet carry no global coherence ⟹
  tri-free/shortest/Γ-min CANNOT supply it.
- REPAIR (adopted): **checked first-collision owner atlas** — deterministic ranks + first collision +
  canonical producer DAGs; owner(v) = first proof node containing v (root owner none); petal(n) := owner
  fibres ⟹ DISJOINTNESS IS A THEOREM (fibres of a function); checker verifies shore(wallKey n) = petal(n)
  (10) — the countermodel fails exactly here (b in both X and Y); endpoint-owner distinctness ⟹ exact TWO
  (11); boundary-complete Door check (internal off-support port edges REJECTED in this branch); algorithm
  checkHornSplitOrTwoCover (split search first at original load, else atlas) + soundness
  hornSplitOrTwoCover_of_checkedFirstCollisionAtlas (Lean skeleton given). Claimed checker SHA 30ab7739…
## R15 — NO-ACTIVE-COMPONENT FALSE (even with maxcut + Γ-min)
- 27-vtx canonical core: F = 26-cycle e_i + leaf e_*=wv0 (|F|=27); A = 26 cyclic atoms a_i = v_i v_{i+4}
  (unique shortest = 4 consecutive cycle edges) + 2 leaf atoms b± (w-v0-…) ⟹ |A|=28, defect one, EVERY
  proper subfamily Hall-satisfying (SDR certificates; (7): nonempty proper J gets |∪F| ≥ |J|+1 via e_{i+1});
  internal off-support path P_I = 12 blue step-9 edges v_{9k mod 26} joining v0…v4 ⟹ I-component ACTIVE
  (contains endpoints of a0 = v0v4). Lock extension: 5-vtx private length-6 blue path per atom ⟹ N=167,
  |B|=207, E=235; maxcut = 207 EXACT (per-gadget ≤ 6 (11)); Γ = 700 min. Tri-free (bipartite blue; step-4
  bad = two 13-cycles).
- CE satisfies the RIGHT branch of the corrected bridge with huge slack (max T = 35 at v0 ⟹ min slack 132).
- CORRECTED BRIDGE (adopted): componentwise disjunction (16): ∀ I-component H, Inactive(H) ∨ (∀ U ⊆ H,
  |I[U]| ≤ Σ_{v∈U} max(0, N−T(v))) — Lean target inactive_or_activeComponentEndpointHall. Claimed SHAs
  6aa6e9b8… / 43df696f…
- NOTE (mine): combined with R12 (IES false: T(v) can EXCEED N), the endpoint-Hall branch alone is ALSO
  insufficient in general ⟹ R16.
## R16 — THE NEXT THEOREM: C5-collision reserve ⟹ Full-Bank Hall (FBH) on every active component
- FBH: ∀ J ⊆ E(H): |J| ≤ Σ_{t ∈ N(J)} capQ(t) over the ACTUAL legal relation (door+vertexSlack+baseLeaf+
  prune, real token IDs) — exactly what compiled Ell5ActiveComponentHall consumes; boundary exits keep
  1/2-to-own-Door unchanged.
- Machinery: Ω = product of shortest-geodesic choices over ALL bad edges (not just A — essential for the
  3892-vtx overload); duplicate count q_v^ω = 5 r_v^ω − |A_v^ω| = Σ_z (|R_{v,z}|−1)_+ (SELF-fibers z=v
  retained as legitimate C5-bank witnesses); hit correction h_{H,v}^ω = |N_H(v) ∩ A_v^ω|; counting:
  |A_v|+deg_H−h ≤ N ⟹ E[q+h] ≥ T(v)+deg_H(v)−N ≥ deg_H(v)−s(v) (7); half of it (8) = required reserve.
- **THE ONE NEW REPOSITORY LEMMA** = exact c5Base/prune accounting: η(v,t) := (1/2|Ω|)·#witnesses mapped by
  the EXISTING constructors/prune chain to final term t; (10) kinds ∈ {baseLeaf,prune}; (11) legality at
  internal endpoint ports; **(12) Σ_v η(v,t) ≤ capQ(t)** by induction over the actual prune order (transfer
  exactly once; prune reserve identity; no-double-spend kills cross-branch double charge); (13) mass
  identity Σ_t η(v,t) = ½E[q+h]. Then (15): deg_H(v)/2 ≤ s(v) + Σ_t η(v,t) replaces the FALSE endpoint-only
  inequality. Routing: a_v = min(deg/2, s(v)) vertexSlack + scaled η ⟹ per-incidence exactly 1/2 ⟹ FBH.
- 3892-vtx example PAID: attachment (28,784,1,784,28) at v: q_v ≥ 5·784−1625 = 2295 ⟹ reserve ≥ 2295/2
  against demand 1/2; two attachments have disjoint graph-derived sources (12 prevents cross-use).
- Hypothesis usage: tri-free = raw witness validity (row+bad = induced C5); maxcut = c5Base capacity
  nonneg; Γ-min = prune termination (divergence/rejoin replacement shorter or smaller Γ-code).
- DECISIVE GATE: per active component, exact rational max-flow (source→e cap 1; e→t INF iff endpoint port
  legal; t→sink capQ); pass iff mincut = |E(H)|; failure exports J and the exact Hall gap. Exact expectation
  formulas for q̄_v, h̄_{H,v} WITHOUT enumerating Ω (product formulas) given. If flow passes but the
  witness-mass induction fails ⟹ theorem may hold but THIS mechanism is falsified.
- Lean skeleton canonicalEll5_activeComponent_fullBankHall with 4 named extractor lemmas:
  expected_duplicate_add_hit_ge_degree_sub_slack, c5BasePruneCollisionAssignment_legal/_cap/_mass.
## [CLAUDE STATUS: all four UNGATED — gate queue: (i) R13 7-vtx countermodel arithmetic (trivial) + adopt
typed-source SPEC-1 upgrade (Codex); (ii) R14 13-vtx countermodel (script: cuts/rows/Horn shores) + adopt
owner-atlas checker (Codex); (iii) R15 167-vtx CE (script: maxcut cert + supports + SDRs + active path);
(iv) R16 = THE LIVE THEOREM — verify the counting inequality algebra (done by inspection: (4)⟹(5)⟹(6)⟹(7)
✓ sound) + the 3892 numbers (2295 = 3920−1625 ✓) + implement the max-flow gate; the c5BasePrune accounting
(12) is the new load-bearing extractor lemma (Codex formalization lane after design ack).]
