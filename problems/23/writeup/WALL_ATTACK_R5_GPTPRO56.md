# WALL ATTACK — R5 (GPT-5.6 Pro full-strength, 2026-07-10, RELAYED VERBATIM BY USER)

**[CLAUDE GATE HEADER:**
- VERDICT: `step_new_ports_legal_connected` does NOT follow from support overlap (§2: forcing edge ∈ Eshort;
  new exposed load ∈ δB\Eshort at a previously absent endpoint — door/vertex keys not shared).
- **REAL-GRAPH ROOT-CROSSING CANDIDATE (§3, must be exact-gated by me BEFORE any status change)**: 359-vtx
  triangle-free graph, genuine unique-up-to-complement max cut (lock-gadget argument, bad count exactly 9),
  nine ℓ=5 rows = the double-star footprint, concrete crossing step with disjoint door/vertexSlack sinks.
  TWO remaining gates before it kills root-locality: (1) do checked C5Base/prune Bank terms add a cross-root
  sink? (2) does the cage satisfy ReducedMinimalNegativeBalance? — candidate, NOT yet a wall falsifier.
- **§5: the UNIVERSAL-LOAD form of PositiveRootBlockClosedExtraction FAILS on this cage** (closed shores are
  only ∅/full since the support hypergraph is connected; adversarial rational load makes full minimal-closed-
  deficient with no proper closed extraction). Does NOT yet refute the form where loads = Z.L·R.gamma from a
  strict restricted dual.
- **NEW RESCUE LEMMA (the only plausibly derivable one, per 5.6)**: `RootCrossingPureLensSplit_exists` —
  root crossing ⟹ checked PureLensCageSplit into proper subcages with DISJOINT bank-token lists (no double
  count) ⟹ parent negative ⟹ some child negative ⟹ contradicts ReducedMinimalNegativeBalance. Builds on the
  compiled Proper/Restrict/PureSplit/PureLensSplit (T8) stack.
- Census spec refinements over R4: ACTIVE sinks only (cap>0) for roots; port source key = (shore key, global
  edgeId, inside endpoint); `internal_offSupport_boundary_empty` (every port is a restriction-exit edge —
  gate this in code); three gate kinds NO_COMMON_ACTIVE_SINK / ROOT_COMPONENT_CROSSING /
  ROOT_BLOCK_NOT_CLOSED_EXTRACTABLE + the exact positive-extraction LP test.
- MY NEXT ACTIONS: (1) build the 359-vtx candidate exactly and verify EVERY claim (triangle-free; max-cut
  uniqueness via the lock case analysis; ℓ=5 geodesic uniqueness by BFS; the ten footprint facts; the
  crossing step; sink disjointness); (2) implement the census gates; (3) verdict decides: crossing real ⟹
  retire root-locality, pivot to RootCrossingPureLensSplit_exists.**]

---

## §3 THE CANDIDATE (full construction — verbatim indices)

Core 9 vertices: L₀,L₁,L₂,C,R₀,R₁,R₂,U,V. Intended cut: side0 = {L₀,L₁,L₂,C,R₀,R₁,R₂}, side1 = {U,V}.
Support edges (8): Lᵢ—U (i=0,1,2), U—C, C—V, V—Rⱼ (j=0,1,2). Bad edges (9): Lᵢ—Rⱼ all i,j.
Rows: Lᵢ—U—C—V—Rⱼ; atom support {LᵢU, UC, CV, VRⱼ}. = the nine-row double-star-with-bridge footprint.

LOCK GADGETS: for each of 7 relations (L₀,C),(L₁,C),(L₂,C),(R₀,C),(R₁,C),(R₂,C),(U,V): TEN internally
vertex-disjoint paths of length SIX (5 fresh internal vertices each): a—P₁—P₂—P₃—P₄—P₅—b. Both endpoints
same side; internal vertices alternate so all six path edges cross. Totals: 9 + 7·10·5 = 359 vertices;
17 + 7·10·6 = 437 edges. Indexing: core 0=L₀,1=L₁,2=L₂,3=C,4=R₀,5=R₁,6=R₂,7=U,8=V;
internal(r,k,t) = 9 + 5·(10r+k) + (t−1), r∈[0,6], k∈[0,9], t∈[1,5]; relations r=0..6 in the order above.
side(P_t) = side(endpoints) xor Odd(t).

MAX-CUT PROOF (§3.3): displayed cut bad count = exactly 9 (the LᵢRⱼ); all support+lock edges cross. Any cut
violating one locked relation pays ≥10 bad on its ten disjoint length-6 paths (endpoints-opposite ⟹ ≥1 bad
per path) ⟹ can't beat 9. Hence every max cut satisfies L₀=L₁=L₂=C=R₀=R₁=R₂ and U=V; groups opposite ⟹
exactly 9 bad; same side ⟹ 17 bad. Max cuts = displayed + complement only (internal vertices forced
alternating) ⟹ displayed cut automatically Γ-minimal.

TRIANGLE-FREE (§3.4): bad edges form K₃,₃ on L/R; no support vertex completes a triangle; central path
U—C—V with no U—V edge; lock internals degree-2, distinct lock paths share only endpoints; length-6 paths
create cycles ≥8. Rows: Lᵢ—U—C—V—Rⱼ is blue length 4 and UNIQUE shortest (lock detours ≥6) ⟹ ell=5,
geodesicSupport = {LᵢU,UC,CV,VRⱼ}; blue graph connected ⟹ B-connected.

TEN FACTS (§3.5): |S|=9, |Eshort|=8; supports size 4; no private edge (LᵢU in 3 rows, VRⱼ in 3, UC/CV in 9);
pair-unions: same-L or same-R endpoint ⟹ 5, else 6; footprint connected (all share UC,CV). Minimality exact:
proper T with l left / r right indices: |Eshort(T)| = 2+l+r; (l,r)≠(3,3) ⟹ |T| ≤ l·r ≤ l+r+2; l=r=3 proper ⟹
|T| ≤ 8 = |Eshort(T)|; full: 9 > 8. No other bad edges ⟹ trivially escape-closed. UNRESOLVED:
ReducedMinimalNegativeBalance (many external door edges probably make this realization bank-positive).

## §4 THE CROSSING STEP (verbatim)
Cage restriction = the 9 core vertices (= union of geodesicSupport endpoints; lock internals outside).
Inside the restriction every blue edge is in F ⟹ restricted B\F has NO edges ⟹ every core vertex is its own
QComp. V₀ = {L₀,U,C,V,R₀} (support of row L₀R₀). Atom a = L₁R₀, unique geodesic L₁—U—C—V—R₀, exactly one
vertex (L₁) outside V₀, every (=the one) geodesic uses crossing support edge e = L₁U ⟹
ForcedEll5EscapeStep a e V₀ W, W = V₀ ∪ {L₁}. New exposed ports: L₁—P(L₁,C,k,1) for the ten lock paths.
Old exposed L₀ ports: L₀—P(L₀,C,k,1). Under door + endpoint(inside)-slack incidence:
N(L₀-port) = {Door(L₀—P₁), VertexSlack(L₀)}; N(L₁-port) = {Door(L₁—P₁), VertexSlack(L₁)} — DISJOINT.
⟹ ¬step_new_ports_legal_connected PROVIDED no checked C5Base/prune term is legally incident to both
endpoint families — a direct finite Bank-list gate:
∀ s, 0 < cap(s) → (∃ L₀-port legal to s) → ¬(∃ L₁-port legal to s).

## §5 UNIVERSAL-LOAD EXTRACTION FAILURE (verbatim logic)
Under forced-support closure the atom-support hypergraph is connected ⟹ only closed shores = ∅ and full.
If the full shore's ACTIVE legal-incidence graph has k ≥ 2 roots with capacities C₁..C_k: set load
L(p₁)=C₁+1 on one port of root 1, L(pᵢ)=Cᵢ on one port of each other root, else 0 ⟹ Def(full)=1, Def(∅)=0,
no proper nonempty closed shore ⟹ full is minimal closed deficient but NO root block is a proper closed
subshore ⟹ PositiveRootBlockClosedExtraction (arbitrary-nonneg-load version) FAILS. (Not yet refuted for
loads of the form Z.L·R.gamma from a strict restricted dual.)

## §6 NEW CHECKER FACTS (verbatim names)
6.1 `ForcedEscapeStepSharesActiveBankSink` (strong; NOT derivable from the ten support facts; relates
support-closure to Bank incidence; flag as new obstruction/cage-legality checker fact if chosen).
6.2 **`RootCrossingPureLensSplit_exists`** (more plausible, uses reduced minimality): if a forced escape
closure crosses between two ACTIVE legal roots, the concrete cage admits a checked PureLensCageSplit into
proper subcages with: disjoint child bank-token lists; no double-counted door/vertexSlack/C5Base/prune
capacity; atom/short charges assigned per the existing PureLensCageSplit contract; parent negative ⟹ some
child negative. Then ReducedMinimalNegativeBalance rules out root crossing. Does NOT claim roots share a
sink — uses that disjoint roots create a legitimate bank-separated pure split. THE new concrete research
lemma; the only one plausibly derivable from the compiled Proper/Restrict/PureSplit/PureLensSplit stack.

## §1 + §7 CONCRETE MODEL + CENSUS REFINEMENTS (deltas over R4 §6; all Rat, no float)
- QComp := blueComponent on filtered restricted GraphData (blue ∧ both endpoints ∈ R ∧ ∉ F); R := union of
  geodesicSupport endpoints (assert equal to Restrict's stored vertex set); compOf : Fin n → Option (Fin q).
- `internal_offSupport_boundary_empty`: an internal (both-endpoints-in-R) blue off-support edge can never
  cross X(U) (same B\F component) ⟹ EVERY port is a restriction-exit edge (inside ∈ R, outside ∉ R) — gate
  this; failure ⟹ component table / filtering bug.
- Geo4(a): enumerate length-4 blue paths between bad-edge endpoints with all edges ∈ geodesicSupport(a);
  ASSERT ⋃ pathEdges = geodesicSupport(a) (catches enumerator/support mismatch).
- AtomForcedAcross a U := qSupport(a)∩U ≠ ∅ ∧ qSupport(a) ⊄ U ∧ ∀ p ∈ Geo4(a), ∃ f ∈ pathEdges p ∩ F
  crossing X(U). ForcedEll5EscapeStep a e V W := e ∈ support(a) ∩ F ∧ crosses V ∧ AtomForcedAcross a V ∧
  W = V ∪ qSupport(a). NOT monotone ⟹ define IsFullEscapeClosed directly (∀ steps, W ⊆ U) and ENUMERATE
  closed shores (bitmask reference checker; DFS-pruned for large q).
- Port = (canonical shore key, global edgeId, inside, outside) — source key prevents identifying loads on
  the same edge from different cut atoms when C5Base/prune legality is cut-sensitive.
- Sinks = indices into the concrete Bank term LIST (do NOT aggregate same-kind terms — global source IDs
  stay distinct). Door: legal iff same global edge id, cap 25 (the 300-door anchor = twelve edge-labelled
  door terms). VertexSlack: legal iff vertex = p.inside, cap = max(0, N−T(v)) (certified via
  deltaM_card_le_deltaB_card; a bank term, not η). C5Base/prune: EXACTLY the proof-carrying incidence the
  Bank checker accepts (expose bankTermLegalPort : BankTerm → PortSourceKey → Bool if hidden — definitional
  only). ACTIVE sinks := cap > 0; run root decomposition with BOTH all/active and report both (zero-cap
  sinks must not create fictitious resource connections; removal preserves Hall values — short lemma).
- Root = connected component of the bipartite port/ACTIVE-sink legal-incidence graph.
- GATES per closed ambient U ⊇ transitions V→W: (7.7) NO_COMMON_ACTIVE_SINK — new port with
  activeNbr(pNew) ∩ activeNbr(pOld) = ∅ for ALL old ports (falsifies ForcedEscapeStepSharesActiveBankSink);
  (7.8) ROOT_COMPONENT_CROSSING — new port's root ∉ old ports' roots (the decisive weaker test);
  (7.9) ROOT_BLOCK_NOT_CLOSED_EXTRACTABLE — closed U with ≥2 roots where some root's port set ≠
  exposedPorts(V) for every closed V ⊂ U (exact structural falsifier for full RootBlockClosureSeparable);
  (7.10) exact positive-extraction LP: vars L_p ≥ 0; Def_U(L) ≥ 1; Def_V(L) ≤ 0 ∀ proper closed V ⊂ U —
  feasible exact rational solution = machine-checkable falsifier for universal-load
  PositiveRootBlockClosedExtraction (for the ∅/full case no solver needed: root-capacity+1 construction).

## §8 CONSEQUENCE (verbatim)
The route cannot take "forced support escape ⟹ shared active bank sink" as a graph theorem. Next exact gate:
run the census for ForcedEscapeStepSharesActiveBankSink / ROOT_COMPONENT_CROSSING /
ROOT_BLOCK_NOT_CLOSED_EXTRACTABLE. If the double-star lock candidate passes the actual Bank constructors and
exhibits the predicted crossing, retire root-locality permanently. The remaining viable reduced-minimality
route: root crossing ⟹ checked PureLensCageSplit with disjoint bank sources ⟹ a proper child has negative
balance ⟹ contradiction to reduced minimal negative balance = **RootCrossingPureLensSplit_exists**.
