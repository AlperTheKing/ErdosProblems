# Claims manifest — sections/sixteen_atom_closure.tex ("The sixteen-atom closure (t = 4)")

Drafted 2026-07-17. Every numbered claim in the section, with statement summary,
verification status (proved | Lean | computer-assisted), exact source file(s),
and verifier + SHA where applicable. Companion style/notation source:
`problems/23/writeup/arxiv/shortest_support_obstructions/main.tex`.

Source archives used (and nothing else):
- `problems/23/writeup/WALL_ATTACK_R44_GPTPRO56.md` (R44)
- `problems/23/writeup/WALL_ATTACK_R45_GPTPRO56.md` (R45)
- `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/REPORT.md` (REPORT)
- `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/REPLAY.md` (REPLAY)
- `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/verify_t4_profile_exclusion.py` (verifier, read in full)
- `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/verify_t4_support_census.py` (verifier, read in full)
- Session gate/replay ledger entries: `coordination/CLAUDE_TO_CODEX.md` (2026-07-11T21:37Z,
  21:59Z, 22:20Z entries), `LOOP_STATE.md` (t=4 closure block)

---

## Definition 1 (`def:t4:circuit`) — support circuit
- Statement: m-footprint obstruction + deletion SDRs (transversal-matroid circuit).
- Status: definition (matches R44 §1 "transversal circuit": deletion SDRs, multiplicity >= 2).
- Source: R44 §1; companion main.tex Definition 4.1.

## Lemma 2 (`lem:t4:transfer`) — minimal violations are support circuits; incidence connected
- Status: PROVED — full proof in section (Hall's theorem + component count).
- Source: R44 §1 + R44 gate header pillar (1) (|F*| = |A|-1, multiplicity >= 2,
  incidence connectivity); footprint part from companion Lemma 2.2 (cited as [SSO]).

## Lemma 3 (`lem:t4:induced`) — rows are induced paths
- Status: PROVED — full proof (standard geodesic fact; chord => length <= 3).
- Source: implicit in REPORT ("checked-row inducedness", Bad-star vertex-cover freeness
  section); proof self-contained.

## Definitions 4-5 (`def:t4:selection`, `def:t4:rotating`) — selection, active neighbour,
   covered star; rotating family of width t
- Status: definitions (terminology bridge). Covered star = clean form of the engine's
  "fully covered profile owner: one active star edge, remaining supported, all
  active/support pairs with positive pairCount".
- Source: REPORT (t=3 closure section, t=5 classifier section); R44 §3-5; R45 §4.

## Theorem 6 (`thm:t4:crossover`) — crossover bounds
- (i) k rotating owners of width t force |E(F)| >= kt + t.
- (ii) k = 2 with one covered star forces |E(F)| >= 3t + 2.
- Status: PROVED — full proofs in section. Reconstructed from R44 gate header pillars
  (2) and (3) (kt disjoint owner-incident + t distinct terminal edges of one owner;
  coverage row Q with v not in Q, <= 2 owner-incident edges, terminal-edge distinctness
  via the would-be common neighbour contradicting atom distance 4). Every step of the
  reconstruction is elementary and checked line-by-line here; the archive records the
  same skeleton as "verified by inspection".
- Source: R44 §3-5 + gate header; t=3 antecedent in REPORT ("Shape-independent t=3
  closure", kernel modules listed there).

## Corollary 7 (`cor:t4:table`) + Table `tab:t4:crossover` — crossover table
- k >= t-1 impossible; k=2 needs t >= 4; (4,2) sole survivor at t=4, margin exactly 1
  (14 <= 15). Table rows t=3..6, bounds 3t+2 / 4t vs budget t^2-1
  (11/12 vs 8; 14/16 vs 15; 17/20 vs 24; 20/24 vs 35).
- Status: PROVED (arithmetic from Theorem 6).
- Source: R44 gate header ("kt+t > t^2-1 iff k >= t-1; 3t+2 > t^2-1 iff t <= 3";
  "TABLE CONFIRMED") + R44 §3-5 table + R45 verdict (slacks 7 and 4 at t=5).

## Definition 8 (`def:t4:window`) — two-owner window; covered window
- Status: definition; matches the census filter exactly (REPORT step 2-3: two same-shore
  degree-four owners, >= 2 common blue neighbours, exactly four bad neighbours each).
- Source: REPORT ("Exhaustive path-realizable t=4 exclusion", steps 1-3); R44 §8.

## Lemma 9 (`lem:t4:absorption`) — star absorption (graph level)
- Covered owner with exactly four crossing neighbours has all four star edges in F.
- Status: PROVED — full proof in section (middle-replacement detour: q -> v swap gives a
  second geodesic row; complete supports absorb it).
- Source: R45 gate header ("covered-star detours => owner stars subset F*"); detour
  mechanism recorded in REPORT ("Replacing the intervening row vertex by u therefore
  gives another checked shortest row, and completeness includes it") and REPORT t=3
  closure ("all three distinct owner-star edges lie in F*").

## Proposition 10 (`prop:t4:core`) — shared atom-partner; the K_{2,3} core
- Status: PROVED (full proof in section: 8 + 4 + 4 = 16 > 15 forces tail overlap)
  + LEAN for the finite incidence core:
  `K2TailIncidence.exists_common_tail_of_support_card_le_fifteen`,
  module `R44K2TailOverlap.lean`, source SHA-256
  12DFB92724F36BEAC1F11EBA529023F0445893CA6E60376B09B2403C0E64066A,
  axioms exactly [propext, Classical.choice, Quot.sound]; gate-accepted rebuild
  recorded 2026-07-11T21:37Z (CLAUDE_TO_CODEX.md).
- Source: REPORT ("First t=4, k=2 reduction"); R44 gate header + §8 (K_{2,3} core).

## Lemma 11 (`lem:t4:vertexrange`) — 8 <= |V(F)| <= 15; covered => <= 14
- Mantel lower bound; tree kill at 16; unicyclic kill at 15 (three forced 4-cycles).
- Status: PROVED — full proofs in section. Tree/unicyclic kills are R45 §4's symbolic
  kills, recorded there as "verified by inspection"; the reconstruction here
  (three pairwise-distinct 4-cycles v-x0-q_i-y_i) is complete and self-contained.
- Source: R45 §4 + R45 gate header; Mantel bound from REPORT step 1.

## Theorem 12 (`thm:t4:census`) — the census (main computer-assisted theorem)
- 153,978 graphs (per-n 2/30/496/3675/15285/36337/52909/45244) -> 34 owner embeddings
  (one per graph) -> 74,920 atom completions -> 2,299 triangle-free -> 862
  coverage/multiplicity -> 576 two-owner windows, all |V(F)| = 15, four support
  isomorphism types; (ii) >= 8 atoms forced through each owner, histogram
  {8:255, 9:193, 10:101, 11:26, 12:1} identical for v and m; (iii) zero middle-swap
  row pairs over all complete families (16,288 row tuples in total).
- Status: COMPUTER-ASSISTED, dual verification.
  - Primary: `enumerate_t4_support_graphs.py`, `enumerate_t4_atom_circuits.py`,
    `enumerate_t4_profile_transitions.py` (archived in
    `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/`).
    Canonical artifact SHA-256:
    t4_support_graph_census.json  40f16a84559ace4827e366f152026f2b7868bdaed31ff9afb36184a29b48046d
    t4_atom_circuit_census.json   302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652
    t4_profile_transition_census  b464682b4142a9db2396dc39ac9a0ffd8ff638aba1b9270734667c8f0a543114
  - Independent: `verify_t4_support_census.py` (geng rerun + NetworkX;
    PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS), `verify_t4_atom_census.py`
    (NetworkX all_shortest_paths + bipartite matching;
    PASS_INDEPENDENT_NETWORKX_ATOM_CENSUS), `verify_t4_profile_exclusion.py`
    (own graph6 decoder + BFS; recomputes both canonical hashes; asserts 576 circuits,
    4 types, forced >= 8 both owners, rawMiddleSwaps == 0;
    PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION).
  - Session replay of the third verifier: PASS with matching histograms, recorded
    2026-07-11T21:59Z (CLAUDE_TO_CODEX.md item 2, "SHAs 302e04ef/83b1ee2f match").
  - Replayed for this write-up (2026-07-17): geng per-n counts re-generated with
    `tools/nauty2_8_9/geng.exe -u -c -b n 15:15`, n = 8..15; output
    2/30/496/3675/15285/36337/52909/45244 (sum 153,978) — exact match.
- Completeness of the reduction (that the census filter is necessary for every
  two-owner window): PROVED in section from Definition 8 + Proposition 10 + Lemma 11.
- Source: REPORT ("Exhaustive path-realizable t=4 exclusion" incl. stage-count table
  and audit note), REPLAY (expected counts/verdicts), verify_t4_profile_exclusion.py
  (read in full), verify_t4_support_census.py (read in full).

## Corollary 13 (`cor:t4:closure`) — the sixteen-atom closure
- No covered two-owner window; graph-level consequence via Lemmas 2 and 9;
  window (4,2) empty.
- Status: PROVED given Theorem 12 (so, overall, COMPUTER-ASSISTED): covered => |V| <= 14
  (Lemma 11) vs all windows at |V| = 15 (Theorem 12(i)).
- Source: R45 (closure verdict, three independent routes recorded);
  CLAUDE_TO_CODEX.md 2026-07-11T22:20Z ("T=4 CLOSED, LEDGER FACT"); LOOP_STATE.md.

## Proposition 14 (`prop:t4:swapgeometry`) — middle swap => cross-outer; row-free confirmation
- Status: LEAN for the row-local implication:
  `LiveMiddleSwapCrossOuter.live_middle_swap_has_cross_outer`,
  module `LiveMiddleSwapCrossOuter.lean`, source SHA-256
  3DFF7897F65112F4F8177B84AB28F631C85BC6F50F7F5D920ED06F033B7F9275,
  axioms exactly [propext, Quot.sound]; rebuilt green in the session gate
  (2026-07-11T22:20Z); axiom audit dual-attested 2026-07-17 by a fresh
  rebuild of the five-module import chain + kernel #print axioms probe
  (anc/lean_axiom_probe/, PASS_AXIOM_PROBE, axioms exactly
  [propext, Quot.sound]). COMPUTER-ASSISTED for the graph-level exhaustion:
  `verify_t4_cross_outer_exclusion.py`, four support/owner types with multiplicities
  180/190/190/16, zero live cross-outer candidates; artifact
  t4_cross_outer_exclusion.json, canonical SHA-256
  79db75b95e8401064f1b6159bb980ee0149f0fb3a602a607306a7f0e501a5d49,
  verdict PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY; session replay PASS recorded
  (CLAUDE_TO_CODEX.md 22:20Z, LOOP_STATE.md).
- Source: REPORT ("Production row invariant behind the t=4 exclusion"), REPLAY.

## Remark 15 (`rem:t4:nearmiss`) — independent catalogue + the tight 14-vertex near-miss
- Catalogue counts: |V|=10,11 no owner profile; |V|=12 max 10 same-part distance-4
  pairs; |V|=13: 280 graphs, 0 circuits; |V|=14: 455 graphs, 0 covered double stars.
  Near-miss invariants as archived: parts {0..6}/{7..13}; 15 edges; 16 atoms;
  owners 0,1; shared support neighbours {7,8}; shared atom-partners {3,5,6}; shared
  terminal edges {3,13},{5,13},{6,13}; remaining edges {2,11},{4,9}; 864 selections,
  none covering both stars; local failure mode as recorded. Checker SHA prefix 4644e5ab.
  Exact distance-4 criterion (Q_L)_{uv}=0<(Q_L^2)_{uv} from R45 §3.
- Status: COMPUTER-ASSISTED, SINGLE IMPLEMENTATION (GPT-side session enumeration);
  presented explicitly as corroboration only — NOT load-bearing for Corollary 13.
  Cross-consistency with the dual-verified census recorded in the R45 gate header.
- Source: R45 §§3, 5-6 + gate header.

## Remark 16 (`rem:t4:abstract`) — abstract support-only survivor
- A 16-atom/15-edge abstract transversal circuit satisfying all cardinality axioms
  (Hall on all 65,534 proper subsets) exists, so support-cardinality reasoning alone
  cannot close the window.
- Status: COMPUTER-ASSISTED with independent recheck (`verify_t4_support_circuit.py`
  recomputes the hash, edge degrees, shared-tail rows, and every proper-subset Hall
  inequality). Artifact t4_support_circuit_hit.json, canonical SHA-256
  5b386cd90b795bf1e6f8f174e21aa559e37c9f682e5dff373dae6bf74f3b9641.
- Source: REPORT ("Exact limit of support-incidence arguments at t=4").

## Verification-record paragraph
- All statements sourced from REPORT/REPLAY expected outputs and the two verifier
  scripts read in full; "no floating point on either acceptance path" from REPLAY.
- Formalization debt stated honestly: census not kernel-checked (R45 §7-8
  "Formalization debt: kernel-replay of the <=14 catalogue").

## Remark 17 (`rem:t4:scope`) — scope
- Does not resolve the Erdos n^2/25 conjecture; (5,2)/(5,3) open with margins 7/4;
  unrooted t=5 census infeasible (geng 24-edge n16 ~ 194.6M measured).
- Source: R45 verdict + gate header; LOOP_STATE.md.

---

## Claims EXCLUDED for verification reasons

1. **Full explicit edge/atom lists of the 14-vertex regression circuit.** R45 refers to
   them as its equations (13)/(14), but only the structural invariants were archived.
   The section exhibits exactly the archived invariants and says so; no list is
   fabricated or reconstructed.
2. **SHA prefix 83b1ee2f** (mentioned in the session replay ledger, CLAUDE_TO_CODEX.md
   21:59Z, "SHAs 302e04ef/83b1ee2f match"): the artifact it hashes is not identifiable
   from the archives, so it is cited only in this manifest, not in the paper.
3. **`t4_two_owner_stars_have_external_atom` (R44OwnerStarDualHall.lean, A8D39A65).**
   Recorded as "acknowledged, queued for rebuild" only — no gate-accepted rebuild found
   in the ledger. Excluded from the section.
4. **"Fully covered owner profiles = 0" as an independent census kill.** The archives'
   audit note records that profile-conditioned counts were retracted once (r=4 scope
   error) and replaced by the r-independent raw-middle-swap gate. The section therefore
   uses only: (a) the r-independent raw-swap count, (b) the forced r >= 8 histograms,
   and (c) the by-hand unicyclic kill — never the profile-conditioned zero.
5. **The R44 "ambient <= 4 / intrinsic maxcut" restriction.** Explicitly REVERSED by the
   accepted ambient correction (R45 gate header); not used anywhere in the section
   (the closure is support-internal, as the correction notes).
6. **GPT's |V| <= 14 catalogue as a load-bearing step.** Single implementation, code not
   archived; used only as corroboration (Remark 15), with the closure resting on the
   dual-verified census instead.
7. **All t=5 material** (rooted CP-SAT hit, max-cut extension UNSAT, classifier
   falsifiers): out of this section's scope; only the open-window sentence in
   Remark 17 remains.
