# Claims manifest — section "No balanced rotor on nine-atom circuits (t=3)"

File: `sections/claude_t3_no_balanced_rotor.tex` (drafted 2026-07-17 by Claude / Fable 5).
Every numbered claim in the section is listed with statement summary, verification
status, and exact sources. SHA-256 values are of the files as they exist today
(recomputed 2026-07-17 with `Get-FileHash`); provenance discrepancies are noted
explicitly.

Cross-section label dependencies (must exist at assembly): `sec:rotor8`,
`def:rotor8-selection` (claude_eight_vertex_rotor.tex); `cor:graph`
(support_circuits.tex); `def:switchloss`, `cor:badendpoint` (star_lemma.tex).
Bibliography key: `Ferudun26supports` (companion paper), as in support_circuits.tex.

## Definitions (no mathematical claims, but sourced)

### Definition `def:t3-profile` (rotating owner profile; covered star)
- Content: (P1) d_B=d_M=3 with monochromatic star consisting of atoms; (P2) exactly one
  unselected crossing star edge (active edge); (P3) both remaining star pairs covered by
  owner-avoiding selected geodesics.
- Source: WALL_ATTACK_R42_GPTPRO56.md secs. 9-10 (owner condition "(22): dB=dM=3,
  deg_I=1, r=3, P1 pressure 1, star fully covered"); WALL_ATTACK_R48_GPTPRO56.md
  secs. 1-4 (the four-condition local profile, here simplified: row-count and matching
  conditions dropped); WALL_ATTACK_R41_GPTPRO56.md sec. 7 (window incidence target,
  including owner-avoiding coverage). The section's Remark `rem:t3-profile-scope`
  states explicitly that the paper profile is a weakening of the engine profile, so
  excluding it is sufficient.

### Definition `def:t3-rotor` (balanced rotor, k in {2,3})
- Content: k distinct owners, profile at each state, consecutive states related by a
  one-atom middle-swap detour move.
- Source: WALL_ATTACK_R42_GPTPRO56.md secs. 1, 9-10 (row swap Q=C∪{m} -> Q'=C∪{v};
  balanced-rotor constraint list); WALL_ATTACK_R43_GPTPRO56.md secs. 5-6 (k in [2,3]
  after the four-owner exclusion); Lean inductive `T3BalancedDeficiencyRotor`
  (two/three cases) in R43SupportIncidence.lean. The ledger ("balanced") is named in
  Remark `rem:t3-profile-scope` but deliberately not formalized in the definition,
  matching the Lean scope.

## Claims

### Remark `rem:t3-fourowners` (four-owner configurations force |M| >= 12 > 9)
- Status: proved (proof sketch included in the remark) + Lean finite core.
- Scope as stated: the engine's four-owner configuration (four cut-tight corners of a
  crossing four-cycle, each with >= 4 crossing neighbours), NOT arbitrary
  four-owner families. Uses maximum-cut (via d_M >= d_B - 1 at cut-tight vertices,
  cross-referenced to the star-lemma section). Explicitly flagged as the only
  max-cut-dependent statement of the section.
- Sources: archive REPORT.md ("Lemma (four-star bad-incidence bound)"), path
  problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/REPORT.md;
  WALL_ATTACK_R42_GPTPRO56.md.
- Lean: `Erdos23Delta0.Gamma.CutTightActiveRotorIncidence`
  (`FourBadStars.twelve_le_ambient_card`, `FourBadStars.not_ambient_card_nine`,
  `three_le_badDegree_of_four_le_blueDegree_of_cutTight`).
  Production file SHA-256 0814A665869737B86A93B44B7E42C55690B81058E221891C36B26FC168B688F1.
  Audited archive copy (REPORT.md: rc=0, axioms exactly propext/Classical.choice/
  Quot.sound, no sorryAx/native_decide) has SHA-256 3D7C194B...; it is a superset of
  the production file (it additionally contains a `FourDisjointBadStars` slack section
  absent from production). All declarations cited in the paper are present in the
  production file (verified by direct read 2026-07-17).

### Lemma `lem:t3-ownerdeg` (profile owner has deg_F >= 3; all three star edges in F)
- Status: proved — full proof in the section (selected star edges are support edges;
  the active edge enters F via the covered-pair middle-replacement detour, which is a
  geodesic of the covering atom by d_B = 4 and completeness of supports).
- Sources: WALL_ATTACK_R43_GPTPRO56.md secs. 1-2 ("coverage => detour rows containing
  vx, vy0, vy1 => deg_F*(v) >= 3"); REPORT.md, section "Shape-independent t=3 closure"
  ("all three distinct owner-star edges lie in F*; hence its F*-degree is at least
  three"); WALL_ATTACK_R41_GPTPRO56.md sec. 2-3 (positions-differ-2 detour validity).
- Lean (finite core only): `fullyCoveredLiveStar_fullSupportDegree_ge_three` in
  `Erdos23Delta0.Gamma.R43SupportIncidence` — abstract three-witness carrier; the
  graph argument above is the paper-level adapter (division stated honestly in
  Remark `rem:t3-lean`(i)).

### Lemma `lem:t3-disjoint` (owners on one shore; pairwise nonadjacent; disjoint incident F-edge sets for k <= 3)
- Status: proved — full proof in the section (middle position parity; common crossing
  neighbour + triangle-freeness kills a monochromatic edge between owners; every owner
  pair is consecutive when k <= 3).
- Sources: WALL_ATTACK_R43_GPTPRO56.md secs. 1-2 ("v,m same side + common blue nbr =>
  vm not in B (same side) and vm not in M (else triangle) => incident support-edge sets
  disjoint") and 5-6 ("same side by transitivity around the cycle"); REPORT.md,
  "Shape-independent t=3 closure".
- Lean: disjointness enters the R43SupportIncidence carriers as hypotheses
  (`disjointVM`, `disjoint01`, ...); graph derivation is paper-level.

### Theorem `thm:t3-counting` (first closure: no balanced rotor on nine-atom circuits, by support-edge counting)
- Status: proved — full proof in the section. k=3: three disjoint incident triples give
  9 > 8 = |E(F)|. k=2: 3+3 incident edges plus a three-edge external family via the
  two-case argument (some v-b_i geodesic avoids m: its last three edges are external;
  otherwise m is forced to the middle position of every such geodesic and the three
  final edges q_i b_i are distinct and external). |E(F)| = 8 from the circuit identity
  (cross-ref cor:graph(a)); geodesics of atoms lie in F (cor:graph(c)).
  Does NOT use maximality of the cut; shape-independent (no classification input).
- Sources: WALL_ATTACK_R43_GPTPRO56.md (gate header + secs. 1-2, 5-6: the exact
  two-case argument, "|E(F*)| >= 3+3+3 = 9 > 8"; verified-by-inspection gate note);
  REPORT.md, "Shape-independent t=3 closure" (the same argument in prose, including
  the case split and the position-2 forcing of m).
- Lean (finite counting core, kernel-checked): module
  `Erdos23Delta0.Gamma.R43SupportIncidence`, file
  problems/23/lean/Erdos23Delta0/Gamma/R43SupportIncidence.lean,
  SHA-256 6664967000F45660BD82C9EA9304942257248FBCA5BB88482C45F6397D184CEA — byte-identical
  to the copy audited in REPORT.md (rc=0; axioms exactly propext, Classical.choice,
  Quot.sound; forbidden-token scan empty). Declarations:
  `fullyCoveredLiveStar_fullSupportDegree_ge_three`,
  `TwoRotatingOwners.twoRotatingOwners_force_nine_supportEdges`,
  `ThreeRotatingOwners.threeRotatingOwners_force_nine_supportEdges`,
  `no_t3_balancedDeficiencyRotor`. The modules are also listed as accepted/axiom-clean
  in problems/23/writeup/ASSEMBLY_PLAN_v1.md. The Lean theorem consumes abstract
  incidence data (witness triples, disjointness, |support| = 8); the paper supplies the
  graph-level reduction — this division is stated verbatim in Remark `rem:t3-lean`(i).

### Theorem `thm:t3-emptystar` (row exclusion at a closed star)
- Status: proved — full proof in the section (positions 1,3 by shore parity; endpoint
  cases give a selected star edge or a length-2 shortcut contradicting d_B = 4;
  monochromatic-neighbour cases give triangles). Does NOT require |A| = 9 and does not
  use maximality of the cut.
- Sources: REPORT.md, section "Bad-star vertex-cover freeness" (row-local statement and
  proof: "Both neighbours must occupy the two opposite-shore positions 1 and 3...");
  the production adapter description ibid. ("K3,3 production adapter ... pairCount = 0").
- Lean (graph-level, kernel-checked):
  - `bad_star_cover_row_impossible` in `Erdos23Delta0.Gamma.BadStarCoverFreeness`,
    file problems/23/lean/Erdos23Delta0/Gamma/BadStarCoverFreeness.lean, SHA-256
    AFD944EA407A6FB29A9E005C4827B7E8AF9E12EDC7DCC532A9BD523E083AE253 — byte-identical to
    the audited copy (REPORT.md: axioms exactly the standard triple).
  - `pairCount_eq_zero_of_closedBadStar` in
    `Erdos23Delta0.Gamma.K33BadStarPairCountZero`, file
    problems/23/lean/Erdos23Delta0/Gamma/K33BadStarPairCountZero.lean, SHA-256
    354565234093E4E25B7A4F296B985A43A1809B438F0633C7C97F7FE422E33233. PROVENANCE NOTE:
    the copy audited in REPORT.md has SHA-256 8A8E5C9C...; diff against the production
    file shows the ONLY difference is the import header line (archive tmp path
    `import tmp.fanout...BadStarCoverFreeness` vs production
    `import Erdos23Delta0.Gamma.BadStarCoverFreeness`) plus a trailing blank line
    (verified by Compare-Object 2026-07-17). ASSEMBLY_PLAN_v1.md lists the production
    module as accepted/axiom-clean.
  - Supporting inducedness lemma `checkedRow_blue_cooccur_implies_pathEdge` in
    `Erdos23Delta0.Gamma.SaturatedRotorSupportPersistence` (named in the remark;
    used by the Lean endpoint cases).
- Note: the Lean proof of the endpoint cases goes through checked-row inducedness; the
  paper proof uses the equivalent shortcut argument (d_B(a,b)=4). Both are stated.

### Corollary `cor:t3-second` (second closure: no rotating owner profile, hence no balanced rotor, on nine-atom circuits)
- Status: proved CONDITIONAL on the companion's footprint classification, which is
  computer-assisted (exact enumeration, two independently written verifiers) — this
  dependence is stated explicitly in the corollary proof and in Remark
  `rem:t3-independent`. The K3,3 closed-star verification itself (all six endpoints on
  one shore; every atom incident to a monochromatic neighbour of any fixed endpoint) is
  a two-line proof included in the section.
- Sources: REPORT.md ("This completely excludes the canonical K3,3 double-star
  realization: every active/support star pair is free, so a fully covered star does not
  exist", plus the scope caveat "closes the canonical cage, not every abstract 9/8
  shape" — resolved in the paper by invoking the classification); companion paper
  shortest_support_obstructions/main.tex, Theorem "Exact classification of the first
  footprints" (unique nine-atom footprint = double star with atom set K3,3, graph6
  H???FaM) — cited as \cite{Ferudun26supports}.

### Remark `rem:t3-independent` (independence of the two closures)
- Status: meta-statement about the section's own logical structure; each half restates
  the verification status of the theorems above (counting: classification-free;
  emptiness: classification-dependent, but excludes even one profiled vertex).
- Sources: REPORT.md scope caveat (as above); WALL_ATTACK_R43_GPTPRO56.md.

### Remark `rem:t3-lean` (formalization)
- Status: factual description of the Lean artifacts; module names, declaration names,
  axiom sets, and SHA-256 prefixes as recorded above. Axiom claims (exactly propext,
  Classical.choice, Quot.sound; no sorry/native_decide) come from the REPORT.md audits
  of the (byte-identical or import-line-only-different) copies and the
  ASSEMBLY_PLAN_v1.md acceptance list.

### Remark `rem:t3-scope` (t >= 4 open; no bearing on the Erdos conjecture)
- Status: proved arithmetic observation + honest scope statement.
- Sources: WALL_ATTACK_R43_GPTPRO56.md sec. 7 ("At t >= 4 (N=20, |M|=16, |F*| = t^2-1
  = 15): 2t incident + t externals = 3t = 12 <= 15 — the direct obstruction fails");
  REPORT.md ("This closes only the t=3/N=15/|M|=9 balanced-rotor window. It does not
  prove the full live-wall theorem for t>=4."). The no-bearing sentence mirrors the
  companion paper's honest frame.

## Claims EXCLUDED from the section (and why)

1. R43's "reservation-starvation FALSE" verdict (WALL_ATTACK_R43 sec. 4) — engine
   bookkeeping about payer keys, out of this section's mathematical scope.
2. All probability estimates ("P(falsifier) ~ 8%") — not mathematics.
3. Any claim that the K3,3 coverage-emptiness route alone covers every abstract
   nine-atom shape — the archives explicitly caveat this; in the paper the gap is
   closed only via the (computer-assisted) classification, and the dependence is
   stated.
4. Any unconditional "the t=3 window is closed in Lean" claim — the Lean closure of
   Theorem `thm:t3-counting` is the finite incidence core; the graph adapter is
   paper-level. The division is stated explicitly rather than claimed away.
5. The t=4 reductions and exclusions (R44/R45 material, K_{2,3} core, exhaustive t=4
   census) — belong to other sections of this paper.
6. The R42 "exact transport identity" and ledger machinery — referenced only as the
   origin of the name "balanced"; no ledger claim is made or needed.
7. WALL_ATTACK_R48's frozen t=5 lemma and classifier — used only as background for the
   simplified profile definition; its own (unproven/refuted-variant) claims are not
   reproduced.
