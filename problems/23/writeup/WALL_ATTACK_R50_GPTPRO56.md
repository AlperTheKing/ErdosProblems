# WALL ATTACK — R50: LATENT-MATCHING FALSE (even theta); |S_ω| ≥ 3t−1 ⟹ LATENT ≤ t(t−3) (t=5: tail ≤ 9);
# SEPARATOR CERTIFICATES (per-tuple + tuple-independent T5ForcedTailSeparator); 56-SPLIT KERNEL-REPLAY
# ENUMERATION SPEC; FULL t=5 CLOSURE CHAIN; MECHANISM WEAKENS WITH t; P ~3%
# (GPT-5.6 Pro, 2026-07-12, "worked 17m2s"; harvested ~13.4k ch)

**[CLAUDE GATE HEADER + ENGINE OVERLAY: (1) SECOND zero-vector falsification — hit #264 at the ACTUAL live
x=9 (graph6 Q??????wE_Bws?s?DCD??@?@???; live middle swaps present on atom (2,3)) kills even the
live-active-specific triangle lemma; fallback holds AGAIN exactly (all-row intrinsic scope-vacuity CP-SAT +
CaDiCaL; tail blanket {19,29} forced-selected by per-edge UNSATs AND by a DIRECT ROW-FAMILY CERTIFICATE:
every coverage witness for the star pairs uses edge 9-1, and y=15's unique witness (15,2,9,1,17) also uses
9-2 — the fiber-intersection form of R50's ProfileForced, found in the wild). (2) ⚠ SCOPE QUALIFIER
(Codex, correct, adopted): the engine's UNSATs fix F* — they prove INTRINSIC scope-vacuity only; production
activeGraph may use row-safe ambient blue edges outside F* ⟹ R50's scope lemma must carry the
no-extra-active-edge hypothesis or incorporate H_safe/CheapGeometry. (3) The live-x hit is EXCLUDED at the
R47 gate anyway: all 8 ambient splits UNSAT; finite obstruction = fixed switch S={4,5,6,7,8,11,14,16}
(badCross 23 / fixedBlue 2 ⟹ demand 21) with row-safe capacities 21,19,17,15,13,11,9,7 by k=newLeft killing
k=1..7, and k=0 dying by JOINT capacity of two switches (28 < 42). First violated production invariant =
CheapGeometry, not ActiveOwner. (4) Cheap live filter: positive-scope candidates need d_B(x) ≥ 3 (degree-2
active endpoints give component {v,x} vacuous). Every event = fixed-countermodel exclusion; exhaustion
pending. The per-candidate certificate BUNDLE is crystallizing: classifier + tail-blanket/separator +
8-split extension UNSAT.]**

## 1-2. Latent matching false; the sharp selected-support bound
Latent matching killed by an even theta (two disjoint 4-paths; select one; the other = 4 consecutive latent
edges) — the circuit axioms bound COMPLETE multiplicity (μ(e) ≥ 2) but NOT selected multiplicity s_ω(e); the
complete-vs-selected gap again. **PROVABLE: |S_ω| ≥ 3t−1** (t incident rows v−y−p−q−b give (t−1) star +
(t−1) first-middle + t terminal pairwise-distinct edges [terminal=first-middle would triangle v−y−b]; no
incident row contains x₀ [co-occurrence]; coverage adds ≥ 1 at x₀) ⟹ **|L_ω| ≤ t(t−3)**; t=5: ≥14 selected,
≤10 latent, tail beyond v ≤ 9 edges. Shells: profile_selectedSupport_card_ge + corollary.

## 3-5. Tail criterion + separator certificates
v active ⟺ tail K_ω(v,x₀) (component of x₀ in L_ω − v) has incident capture (I-path ≥ 3) or remote capture
(≥ 4); tail ≤ 9 edges ⟹ tiny rooted problem. **Per-tuple cut certificate**: region C ∋ x₀, v ∉ C, no bad
nbrs of v, no complete bad edge inside, ALL boundary edges selected ⟹ scope-vacuous
(profileTail_scopeVacuous_of_selectedBoundary). **Tuple-independent**: ProfileForced(e) decidable from the
row DB ⟹ T5ForcedTailSeparator + forcedTailSeparator_scopeVacuous — kernel-checkable per circuit, covering
ALL realizations. Missing lemma: t5_profile_has_forcedTailSeparator (may fail even when vacuity holds —
disjunctive path-hitting fallback). ⚠ ALL of this is INTRINSIC-F*; production needs the extension overlay.

## 7-8. THE ENUMERATION CLOSURE (kernel-theorem spec) + t=5 chain
56 rooted shore splits (n=15..21, p=6..n−5). Per split report (G,C,P,A); lemma ⟺ A=0 everywhere. Kernel
shape: T5SupportCircuitCert (24 edges, 25 atoms, tri-free, union, deletion-SDRs) + per-zero-vector-profile
certificate (T5ForcedTailSeparator OR LRAT/DRAT UNSAT via checkedProfileCaptureUnsat_scopeVacuous) +
rootedT5Catalogue_complete ⟹ census becomes a KERNEL THEOREM. Closure chain: classifier iff → order-14
lemma → cycle-rank caps → per-circuit scope certificates → no active covered owner → no_t5_balancedDeficiencyRotor.
(PLUS the production overlay: CheapGeometry gate per surviving candidate — the R47 bridge.)

## 9. Honest scale verdict
|L_ω| ≤ t(t−3): 0/4/10/18/28 at t=3..7 — the scope mechanism WEAKENS quadratically; the fixed-separator form
is t-uniform but existence unclear at larger t. t=5 closure = another finite base case, not the all-t
theorem. **P ≈ 3%.**
