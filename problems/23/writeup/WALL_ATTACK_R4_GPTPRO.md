# WALL ATTACK — R4: concrete grounding of root-locality (2026-07-09/10, RELAYED VERBATIM BY USER)

*Answer to the grounding retask (concrete defs + prove-or-break real-cage root-locality + census spec).*

**[CLAUDE GATE HEADER:**
- HEADLINE: "I cannot prove real-cage root-locality from the ten facts + W1 as currently stated." The EXACT
  missing fact is named: **`forcedEscapeStep_commonBankSink`** — every forced ℓ=5 escape step's newly exposed
  off-support port shares ≥1 legal bank sink with an old exposed port. Forced steps are SUPPORT-geometric;
  legal roots are BANK-INCIDENCE-geometric; the ten facts never mention LegalSinkPort.
- Weaker sufficient form: `forcedEscapeClosure_preservesLegalRoot` (implied by common-sink via closure
  induction); weakest: per-cage checked `PositiveRootBlockClosedExtraction` (already compiled abstractly in
  ClosedShoreExtraction.lean — §4's proof plan feeds it).
- §3 gives a real-graph CROSSING CANDIDATE (two ℓ=5 rows sharing support edge (a2,b3); doors (a0,dA) vs
  (c4,dC) with disjoint legal neighborhoods) — explicitly a SANITY TEST for census code, NOT a wall falsifier
  (displayed cut not certified maximum; shared-support odd cycles usually resolvable by making the shared
  edge bad).
- §6 = the COMPLETE OPERATIONAL CENSUS ALGORITHM (my implementation spec — next action). Key implementation
  warnings: (a) closure one-step operator may be NONMONOTONE ("every geodesic crosses sepF U" is not monotone
  in U) ⟹ use closure-by-enumeration (least closed superset) for the gate; (b) QComp = VERTEX-level blue
  components of B \ F on the cage vertex set (NOT K2ComponentData); (c) roots = connected components of the
  bipartite port-sink legal-incidence graph (overlapping neighborhoods auto-merge).
- DECISION TREE: census says common-sink holds ⟹ W2 is graph-real, restricted-Farkas route LIVES (prove
  common-sink from cage-legality = the new concrete W2 gate). Census finds a crossing in a GENUINE cage ⟹
  root-locality false for real cages ⟹ fallback = per-cage checked PositiveRootBlockClosedExtraction
  certificates (still no η, still banked-only).**]

---

## VERBATIM (§§1-8; python/lean blocks preserved exactly)

I cannot prove real-cage root-locality from the ten facts + W1 as currently stated. Grounding the objects
against the concrete cage surface exposes the exact missing fact: `forcedEscapeStep_commonBankSink`.
A forced ell=5 closure step is support-geometric; legal root components are bank-incidence-geometric. Unless
the bank checker proves that every forced escape step creates new exposed off-support load sharing at least
one legal bank sink with the old exposed load that forced it, closure can cross legal root blocks.

# 1. Concrete instantiation

## 1.1 QComp: blue components of B \ F, not K2ComponentData
Vertex-level blue component relation (M6BlueConnectivity style) after deleting the cage's short support
edges. K2ComponentData is provider dispatch — wrong object here.

```lean
def Fshort (G cut rows) (C : ConcreteCage G cut rows) : Finset (Sym2 G.Vertex) :=
  Ell5SupportFinset.Eshort G cut rows C.atomSet
def BlueMinusF (G cut rows C) (e) : Prop := IsBlueEdge G cut e ∧ e ∉ Fshort G cut rows C
def CageVertex (G cut rows C) : Finset G.Vertex := ConcreteCage.Restrict.vertexSet G cut rows C
def BminusFConnected (G cut rows C) (u v) : Prop :=
  u ∈ CageVertex ∧ v ∈ CageVertex ∧ Relation.ReflTransGen (step via BlueMinusF edges inside CageVertex) u v
structure QCompData where
  compCount : Nat
  compOfVertex : {v // v ∈ CageVertex} → Fin compCount
  sound : ∀ u v, compOfVertex u = compOfVertex v ↔ BminusFConnected u.1 v.1
-- QShore := Finset (Fin compCount); shoreVerts U := CageVertex.filter (compOfVertex · ∈ U)
-- (implementation: store compOfVertex? : Vertex → Option (Fin compCount) to avoid dependent pain)
```

## 1.2 Boundary
```text
dB(U)   = blue edges splitting shoreVerts U
sepF(U) = dB(U) ∩ Fshort      (in-support short boundary)
off(U)  = dB(U) \ Fshort      (off-support blue load to be bank-routed)
```

## 1.3 Concrete forced ℓ=5 escape step
Defined from ACTUAL ℓ=5 geodesics (universal over geodesics — union support is not enough).
`ell5BlueGeodesics a` = all length-4 blue geodesics realizing the atom (endpoints of the bad edge, 4 blue
edges, distinct vertices, shortestness certified by RowDB facts). `pathEdges p` = consecutive Sym2 pairs.
`atomTouchesQComp a` = components touched by geodesicSupport a.

```lean
def AtomForcedAcross (U) (a) (e) : Prop :=
  e ∈ sepF U ∧ ConcreteCage.Basic.atomSupportedOn G cut rows C a e
  ∧ ∀ p ∈ ell5BlueGeodesics G cut rows a, ∃ f ∈ pathEdges p, f ∈ sepF U
def ForcedEll5EscapeStep (U W) (a) (e) : Prop :=
  AtomForcedAcross U a e ∧ W = U ∪ atomTouchesQComp G cut rows C a
```

**WARNING: monotonicity of AtomForcedAcross in U is NOT automatic** ("every geodesic crosses sepF U" can
change nonmonotonically). For the executable closure define closedness directly and take the least closed
superset:

```lean
def IsFullEscapeClosed (U) : Prop := ∀ a e, AtomForcedAcross U a e → atomTouchesQComp a ⊆ U
def fullEscapeClosure (U) := sInter {W | U ⊆ W ∧ IsFullEscapeClosed W}   -- laws by construction
```

## 1.4 Concrete exposed ports + bank
Port = one off-support blue boundary edge (structure: edge, isBlue, offSupport). BankSink inductive:
door (Sym2 V) | vertexSlack (V) | c5Base (C5BaseId) | prune (PruneId).

```lean
def LegalSinkPort (p) (s) : Prop := match s with
  | door g        => p.edge = g ∧ Bank.hasDoorTerm C g
  | vertexSlack v => v ∈ p.edge ∧ Bank.hasVertexSlackTerm C v
  | c5Base k      => Bank.c5BaseCoversPort C k p.edge
  | prune k       => Bank.pruneCoversPort C k p.edge
-- caps: doorCapQ (=25 standard), vertexSlackCapQ (certified from deltaM_card_le_deltaB_card; the bank term
-- for max(0, N−T(v)), NOT an eta), c5BaseCapQ, pruneCapQ.
def NoUnbankableExposedPortsConcrete : Prop :=
  ∀ U, fullEscapeClosure U = U → ∀ p ∈ exposedPorts U, ∃ s, LegalSinkPort p s   -- W1 grounded
```

# 2. Can a real forced step cross legal root blocks?
**Yes, unless the bank checker proves the additional one-step fact:**

```lean
def forcedEscapeStep_commonBankSink : Prop :=
  ∀ U W a e, ForcedEll5EscapeStep U W a e →
    ∀ pNew ∈ exposedPorts W, pNew ∉ exposedPorts U →
      ∃ pOld ∈ exposedPorts U, ∃ s, LegalSinkPort pOld s ∧ LegalSinkPort pNew s
-- weaker: forcedEscapeClosure_preservesLegalRoot (common-sink ⟹ it, by closure induction)
```

Why underivable: the forcing edge e is IN-support (sepF U); exposed ports are OFF-support (dB \ F). The
common-sink intuition is valid only if the bank checker proves, per forced step, one of: door overlap /
vertex overlap (share v, both legal to VertexSlack v) / same c5Base term / same prune term. The ten facts
are support-hypergraph statements — they do not constrain bank-sink incidence.

# 3. Local real-graph crossing candidate (SANITY TEST, not falsifier)
A = {a0,a2,a4,c0,c4}, B = {b1,b3,b5,dA,dC}; bad (a0,a4),(c0,c4); blue a0b1,b1a2,a2b3,b3a4, c0b3,a2b5,b5c4,
a0dA, c4dC. Rows: a0-b1-a2-b3-a4 and c0-b3-a2-b5-c4 share support edge (a2,b3). Exposed door ports (a0,dA)
and (c4,dC) have DISJOINT legal neighborhoods. Triangle-free; displayed cut locally stable but NOT certified
maximum (shared-support odd cycles usually resolvable by making the shared edge bad). The machine-checkable
failure pattern to hunt in GENUINE cages:

```text
ForcedEll5EscapeStep U W a e;  pNew ∈ exposedPorts(W) \ exposedPorts(U);
∀ pOld ∈ exposedPorts(U): legalNbr({pOld}) ∩ legalNbr({pNew}) = ∅.
```

# 4. If root-locality holds ⟹ PositiveRootBlockClosedExtraction
`positiveRootBlockClosedExtraction_of_commonBankSink (hCommon) (hW1)`: pick the positive-deficiency root r
(PortHallUncrossing additivity); V0 = U-components incident to ports of r; Vr = fullEscapeClosure V0 ⊆ U;
induct over closure steps with invariant exposedPorts(current) ⊆ D.ports r (hCommon keeps new ports in the
same legal component); exposedPorts Vr = D.ports r; properness from a second root. Defect-one/support-size/
no-private/footprint-connected NOT used here — they are candidates only for proving common-sink itself.

# 5. Concrete W2 gate
`forcedEscapeStep_commonBankSink_of_cageLegality : CageLegality → commonBankSink` via the four overlap
clauses (door/vertexSlack/c5Base/prune). If it fails in the census, the route needs per-cage checked
PositiveRootBlockClosedExtraction certificates instead of a derived theorem.

# 6. OPERATIONAL CENSUS FALSIFIER SEARCH (my implementation spec)
Per census item (G, cut, rows, C, Bank):
6.1 F = Eshort(atomSet); V_cage = Restrict.vertexSet; B_edges (blue, inside V_cage); BminusF_edges;
QComp = connected_components(V_cage, BminusF_edges); flag support-edge endpoints outside V_cage.
6.2 atom_qsupport(atom) = components touched by geodesicSupport endpoints.
6.3 shore_vertices / splits / dB / sepF / off / exposed_ports (raw off-support blue boundary).
6.4 all_sinks from Bank terms; legal(p,s) per §1.4; legal_neighbors(p); W1 check per closed shore.
6.5 ell5_geodesics(atom) = brute length-4 blue paths (distinct vertices) between bad-edge endpoints (RowDB
certifies shortestness); atom_forced_across(U,atom) = witnesses e ∈ sepF(U) ∩ support(atom) with EVERY
geodesic crossing sepF(U); one_step_expansions(U) = (atom, e, W = U ∪ qsupport(atom)) with W ≠ U.
CLOSURE FOR THE GATE = closure_by_enumeration (least closed superset; is_closed(U) = all expansions ⊆ U);
iterative closure only as a fast path when monotone.
6.6 closed shores: full enumeration of subsets for small QComp; else closures of seeds (singletons,
atom_qsupports, F-edge endpoint pairs) + random seed unions as fuzzing.
6.7 root_decomposition(P) = connected components of the bipartite port-sink legal-incidence graph
(ports P vs sinks N(P)); a root neighborhood = one component (overlaps auto-merge).
6.8 crossing detection: for each closed U with ≥2 roots, for each root block (P_r, S_r): V0 =
qcomps_incident_to_ports(P_r, U); step the closure inside U; for each new port pNew ∉ P_r: crossing; if NO
old port in P_r shares a legal sink with pNew ⟹ **emit root-locality FAILURE** with full report (graph/cage/
cut/rows ids, U, root, before/after shores, atom, forcing edge, new port + sinks, old sinks) + support-outlet
flags (private_short_edge = supportMultiplicity(e)==1; support_size_5; pair_union_lt_5;
proper_full_closure_hall_violator).

# 7. Checker gates to add
checkNoUnbankableExposedPortsConcrete (W1) / checkForcedEscapeStepCommonBankSink (strong) /
checkPositiveRootBlockClosedExtraction (weak). Strong+W1 ⟹ weak
(positiveRootBlockClosedExtraction_of_checkCommonBankSink, closure induction + PortHallUncrossing). If strong
fails but weak passes, the wall route STILL SURVIVES (W2 stays the weaker checked extraction theorem).

# 8. Bottom line
Do not assume "support closure crossing ⟹ legal root neighborhoods merge". Check/prove
forcedEscapeStep_commonBankSink, or directly PositiveRootBlockClosedExtraction. The concrete danger: the
forcing edge is in-support but the new exposure is an off-support door/vertex/base/prune port whose legal
sinks need not overlap the old root's. The real-cage question is now a FINITE, EXECUTABLE gate: for every
forced closure step V → W inside a closed shore U, does every newly exposed port share a legal bank sink
with the old root block that generated the step? If yes — W2 is graph-real and the restricted-Farkas route
lives. If no — fallback is NOT eta or bare expansion; it is per-cage checked
PositiveRootBlockClosedExtraction or a stronger closed-cut exchange certificate.
