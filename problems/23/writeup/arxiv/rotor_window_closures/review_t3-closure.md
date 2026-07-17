# Adversarial referee review — section "No balanced rotor on nine-atom circuits (t=3)"

Reviewed: `sections/claude_t3_no_balanced_rotor.tex` + `sections/claude_t3_no_balanced_rotor_claims.md` (manifest)
Date: 2026-07-17. Reviewer: independent referee pass (Claude, adversarial).

Method: every numbered claim checked against (a) the four cited Lean production
modules on disk and their audited archive copies, (b) the archives
`WALL_ATTACK_R41/R42/R43/R48_GPTPRO56.md` and
`problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/REPORT.md`,
(c) the sibling sections defining the cross-referenced labels, (d) the companion
paper `shortest_support_obstructions/main.tex`; every proof in the .tex
re-derived line by line; both companion classification enumerators rerun for
m<=9; the section compiled with a companion-style preamble (TinyTeX pdflatex,
two passes, exit 0).

## Source-integrity anchor (all recomputed with Get-FileHash, 2026-07-17)

Production `problems/23/lean/Erdos23Delta0/Gamma/`:
- `R43SupportIncidence.lean` = `6664967000F45660BD82C9EA9304942257248FBCA5BB88482C45F6397D184CEA`
  — matches manifest, byte-identical to the REPORT.md-audited archive copy.
- `BadStarCoverFreeness.lean` = `AFD944EA407A6FB29A9E005C4827B7E8AF9E12EDC7DCC532A9BD523E083AE253`
  — matches manifest, byte-identical to the audited archive copy.
- `K33BadStarPairCountZero.lean` = `354565234093E4E25B7A4F296B985A43A1809B438F0633C7C97F7FE422E33233`;
  audited archive copy = `8A8E5C9C...`. Compare-Object re-run by this reviewer:
  the ONLY differences are the third import line
  (`tmp.fanout...BadStarCoverFreeness` -> `Erdos23Delta0.Gamma.BadStarCoverFreeness`)
  and one trailing blank line (158 vs 159 lines). The other two imports are
  identical in both copies. Provenance note in the manifest is accurate.
  Moreover PROGRESS.md:2979 (2026-07-11T21:37:27Z, GATE-T3CLOSURE) records a
  rebuild of the PRODUCTION copies after exactly this import-path fix: 4x rc=0,
  axiom probes = exactly the allowed triple — so the production K33 file itself
  has a build record, not only the archive copy.
- `CutTightActiveRotorIncidence.lean` = `0814A665869737B86A93B44B7E42C55690B81058E221891C36B26FC168B688F1`;
  audited archive copy = `3D7C194B...`. Reviewer diff: zero production-only
  lines; the archive copy is production plus the 83-line `FourDisjointBadStars`
  slack section (and its two extra `#print axioms`). All three declarations
  cited by the paper are present in the production file. Manifest accurate.
  Independent build record: PROGRESS.md:2969 (2026-07-11T20:44:26Z, rc=0).
- Forbidden-token grep (`sorry|native_decide|axiom `) over all five involved
  production modules (incl. `SaturatedRotorSupportPersistence.lean`): empty.
- `ASSEMBLY_PLAN_v1.md` lines 14-17 list all four modules under
  "What EXISTS (accepted, axiom-clean)" — as the manifest states.

## Verifier reruns (the section's only computational dependence)

`cor:t3-second` consumes the companion's m=9 footprint classification. Both
ancillary enumerators were rerun (GENG=tools/nauty2_8_9/geng.exe):
- `local_obstruction_recheck.py 9` (independent implementation):
  m=6,7,8 -> 0 candidates/0 footprints/0 atom-sets; m=9 -> 1/1/1, witness
  graph6 `H???FaM`, edges {1,2,3}-7, 7-0, 0-8, 8-{4,5,6}, atom set
  {1,2,3}x{4,5,6}. This is EXACTLY the double star + K3,3 atom set displayed
  in the corollary. PASS.
- `local_obstruction_scan.py scan 6 9 16` (primary branch-and-bound):
  m=6/7/8 -> 0 witnesses; m=9 -> 1 witness `H???FaM`, same nine atoms,
  aborted=0. PASS.
Both agree with Table 1 and Theorem `thm:classification` (m<=9 rows) of the
companion paper. (The m=10 row is not consumed by this section and was not
rerun.)

## LaTeX check

Compiled `support_circuits.tex` + `star_lemma.tex` + `claude_eight_vertex_rotor.tex`
+ `claude_t3_no_balanced_rotor.tex` under a preamble copied from the companion
`shortest_support_obstructions/main.tex` (amsthm envs numbered by section,
`\supp`, `\bip`, `\mc`, booktabs, hyperref). Two pdflatex passes, both exit 0;
no errors, no undefined references, no undefined citations, no multiply-defined
labels; PDF produced. All five cross-section labels used by this section
(`sec:rotor8`, `def:rotor8-selection`, `cor:graph`, `def:switchloss`,
`cor:badendpoint`) exist in the sibling files and resolve. Environments
balanced (every `\begin` matched). Macro inventory of the section:
only `\supp`, `\bip` beyond standard LaTeX/amsmath/hyperref — matches the
header's preamble assumption; `\texorpdfstring` requires hyperref, which the
companion preamble loads.

Two harness caveats (not section defects): (i) real `enumitem` is not in the
local TinyTeX, so a shim accepting/ignoring the optional argument was used;
the `label=\textup{(P\arabic*)}`-style keys are syntactically identical to the
companion paper's own (arXiv-compiled) usage. (ii) the companion's
`blue!55!black` hyperref colors need xcolor (loaded via tikz in the companion);
the test used `hidelinks`. At assembly the companion preamble loads tikz, so
this is moot.

## Per-claim verdicts

### 1. Definition `def:t3-profile` — CONFIRMED
(P1)-(P3) are a faithful weakening of the engine owner condition
R42 (22) ("dB=dM=3, deg_I=1, r=3, P1 pressure 1, star fully covered") and the
R48 four-condition profile: row-count (r=3) and the two matching conditions
are dropped, exactly as the manifest says. Weakening direction is the sound
one (excluding the weaker object excludes the stronger), and
`rem:t3-profile-scope` states this explicitly. The "atoms at the owner" part
of (P1) matches the R41 sec 6-7 window, where the nine bad edges ARE the nine
circuit atoms.

### 2. Remark `rem:t3-profile-scope` — CONFIRMED
The owner-avoidance-is-free argument is complete and correct: vx in B forces
opposite parity of the positions of v and x on a selected geodesic; adjacent
positions make vx selected (contradicts (P2)); positions {0,3}/{1,4} give a
length-two B-path between the atom endpoints via the chord vx (contradicts
d_B=4). Re-derived without gaps. (Bookkeeping note: the manifest folds this
remark into the `def:t3-profile` entry rather than listing it as its own
claim; the argument is nonetheless real mathematics and was verified.)

### 3. Definition `def:t3-rotor` — CONFIRMED
Middle-swap move (R2) matches R42's row swap Q=C∪{m} -> Q'=C∪{v} (owner v_i
inserted, next owner v_{i+1} removed), and the k in {2,3} split matches R43
secs 5-6 and the Lean inductive `T3BalancedDeficiencyRotor`
(R43SupportIncidence.lean:178-181, two/three cases, support_card = 8).

### 4. Remark `rem:t3-fourowners` — CONFIRMED (motivational; scope honestly stated)
Matches REPORT.md "Lemma (four-star bad-incidence bound)" step for step:
adjacent corners blue, opposite corners same-shore with common blue
neighbours (triangle-freeness kills an edge), disjoint stars, d_M >= d_B-1 >= 3
via cut-tightness, |M| >= 12 > 9. Lean core verified in the production file:
`FourBadStars.twelve_le_ambient_card`, `FourBadStars.not_ambient_card_nine`,
`three_le_badDegree_of_four_le_blueDegree_of_cutTight` — statements match
exactly (4 <= d_B and d_B - d_M <= 1 imply 3 <= d_M; four disjoint >=3 stars
imply 12; contradiction with card 9). The remark correctly flags itself as the
section's only use of cut maximality. Minor observation (not a defect): the
remark takes "at least four crossing neighbours" as part of the engine
configuration, whereas REPORT.md derives d_B >= 4 from the ActiveOwner
opposite-state argument; since the remark only describes the engine
configuration and is explicitly motivational, this is an acceptable
presentation choice.

### 5. Lemma `lem:t3-ownerdeg` — CONFIRMED
Full proof, re-derived: vy_1, vy_2 in S_omega ⊆ E(F) by (P2); for vx, the
(P3) covering geodesic puts x, y_1 at distance two (odd positions if the atom
endpoints are on v's shore; even positions excluding {w_0,w_4} by the
triangle v-x-y_1 otherwise), middle-vertex replacement by v gives a
length-four B-path = geodesic (d_B(a,b)=4), whose edges lie in
supp_B(ab) ⊆ E(F). Distinctness from x,y_1,y_2 distinct. Matches R43 secs 1-2
and REPORT.md "Shape-independent t=3 closure". Lean finite core
(`fullyCoveredLiveStar_fullSupportDegree_ge_three`, three-witness carrier)
matches; the paper/Lean division is stated in `rem:t3-lean`(i) exactly as the
manifest describes.

### 6. Lemma `lem:t3-disjoint` — CONFIRMED
Full proof, re-derived: middle position of a five-vertex alternating path
with same-shore endpoints lies on the endpoint shore; transitivity around the
move cycle puts all owners on one shore; v_i v_{i+1} not in B (same shore) and
not in M (else triangle with the common blue neighbour x from the two
displayed geodesics); every owner pair is consecutive for k <= 3 (checked:
for k=3 the pair (v_1,v_3) is consecutive via the wrap move). Matches R43
secs 1-2, 5-6. Disjointness enters the Lean carriers as hypotheses
(`disjointVM`, `disjoint01/02/12`) — division stated.

### 7. Theorem `thm:t3-counting` (first closure) — CONFIRMED
Full proof. |E(F)| = 8 from `cor:graph`(a) (verified in
support_circuits.tex; circuit identity proof there is complete). k=3:
3 disjoint triples, 9 > 8. k=2: 6 incident + 3 external. External-triple
two-case argument re-derived: b_i are distinct, same-shore, != m
(vm not in E(G) but vb_i in M); d_F(v,b_i) = 4 by `cor:graph`(c) (vb_i are
atoms by (P1)); case "some geodesic avoids m" gives its last three edges
(distinct, avoid v at position 0 and m entirely); case "all geodesics contain
m" forces m to position 2 (even position, not 0 = v, not 4 = b_i), and the
final edges q_i b_i are external and pairwise distinct (unique same-shore
endpoint b_i distinct). Exhaustive case split. Matches the R43 gate header and
REPORT.md prose exactly (including the position-2 forcing). Lean core:
all four cited declarations present in the production file; carriers require
explicit ThreeMembers witnesses, pairwise disjointness, support card 8, and
derive 9 <= 8; SHA byte-identical to the audited copy; REPORT.md records
axioms exactly propext/Classical.choice/Quot.sound with empty forbidden-token
scan; independent rebuild record PROGRESS.md:2979. No strengthening: the
paper does NOT claim the graph adapter is formalized.

### 8. Theorem `thm:t3-emptystar` (row exclusion) — CONFIRMED
Full proof, re-derived: shore parity forces {x,s} = {q_1,q_3}; endpoint cases
give a selected star edge (z=a, x=q_1) or a length-two B-shortcut
(z=a, x=q_3) contradicting d_B(a,b)=4; monochromatic-neighbour cases give
triangles z,a,q_1 / z,b,q_3. The four cases exhaust the hypothesis
"one endpoint in {z} ∪ N_M(z)". Statement correctly does not require
|A| = 9 and does not use cut maximality. Lean: `bad_star_cover_row_impossible`
hypothesis list matches (same-shore endpoints, cover disjunction
v=u ∨ v=w ∨ badb(v,u) ∨ badb(v,w), blue v-x/v-s, x != s, vx off the row
support); its endpoint cases invoke
`SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge`
(verified present, statement matches the remark's description); the
selection-level `pairCount_eq_zero_of_closedBadStar` matches the REPORT.md
display verbatim (CompleteShortestRowDB + ClosedBadStarDB + TriangleFree +
blue pair + off-support => pairCount = 0). The manifest's note that Lean uses
checked-row inducedness where the paper uses the d_B=4 shortcut is accurate
and is disclosed in `rem:t3-lean`(ii).

### 9. Corollary `cor:t3-second` (second closure) — CONFIRMED (conditional as stated)
The classification dependence is stated in the proof AND in
`rem:t3-independent`. The corollary's displayed footprint equals the
companion's Theorem (thm:classification, display (4)): unique m=9 class,
atom set forced, graph6 `H???FaM` — and this reviewer reran BOTH companion
enumerators for m<=9 and reproduced exactly that unique footprint/atom set
(see Verifier reruns). The two-line closed-star verification for K3,3
(all six endpoint vertices one shore via connectivity of the atom graph;
every atom has an endpoint in N_M(z) since l_i r_b is itself an atom) is
correct and complete; the application of `thm:t3-emptystar` with (x, y_1)
contradicts (P3) — in fact (P3) requires an owner-avoiding covering geodesic,
and the theorem excludes even non-avoiding ones, so the step is safe.
The archives' scope caveat (K3,3 adapter closes the canonical cage, not every
abstract 9/8 shape) is resolved exactly as the manifest says: by invoking the
classification, with the dependence stated.

### 10. Remark `rem:t3-independent` — CONFIRMED
Accurate meta-statement: Theorem 1 uses no classification (checked — its
proof consumes only cor:graph(a),(c) and the two lemmas); the corollary
counts nothing; "two independent exact verifiers" matches the companion's
reproducibility section (two enumerators, rerun here); the "stronger in one
respect" claim (excludes even one profiled vertex) is exactly what
`cor:t3-second` proves.

### 11. Remark `rem:t3-lean` — CONFIRMED
All four SHA-256 prefixes match recomputed hashes. All cited declaration
names exist in the production files with the described statements (verified
by direct read): `fullyCoveredLiveStar_fullSupportDegree_ge_three`,
`twoRotatingOwners_force_nine_supportEdges` (namespace TwoRotatingOwners),
`threeRotatingOwners_force_nine_supportEdges` (namespace ThreeRotatingOwners),
`no_t3_balancedDeficiencyRotor`, `bad_star_cover_row_impossible`,
`checkedRow_blue_cooccur_implies_pathEdge`,
`pairCount_eq_zero_of_closedBadStar`, `twelve_le_ambient_card`,
`not_ambient_card_nine`. Axiom set / no-sorry / no-native_decide claims are
backed by the REPORT.md audits (byte-identical or import-line-only-different
copies), the reviewer's forbidden-token grep, and the independent
GATE-T3CLOSURE / GATE-LEAN2 rebuild records in PROGRESS.md (rc=0, axiom
probes exactly the allowed triple, on the PRODUCTION import paths). The
division of labour ((i) counting core formal, graph adapter on paper;
(ii) graph-level; (iii) finite core) is stated accurately — no
overclaim of an unconditional Lean t=3 closure anywhere in the section.

### 12. Remark `rem:t3-scope` — CONFIRMED
3t = 12 <= 15 at t=4 matches R43 sec 7 verbatim; the two-owner degree-t plus
size-t external family accounting is the correct generalization of the
theorem's 3+3+3 count. The no-bound-on-bip(G) / no-bearing sentence matches
the companion's honest frame and REPORT.md's closing scope paragraph.

## Issues found (ranked)

1. (Most serious; disclosed, not a soundness error) The k in {2,3} cap in
   `def:t3-rotor` is definitional. The only four-owner exclusion in the
   section (`rem:t3-fourowners`) covers the ENGINE's four-owner geometry
   (cut-tight corners of a crossing four-cycle with d_B >= 4), not arbitrary
   four-owner cyclic detour families; nothing in the section excludes a
   hypothetical k >= 4 balanced rotation outside that geometry. The intro
   sentence "the terminal objects such a strategy must exclude are cyclic
   families of detour moves ... We call these balanced rotors and define them
   precisely below" could lead a fast reader to assume the definition captures
   all such families. The remark and the manifest state the true scope, so
   this is a presentation risk, not a gap; a one-clause hedge in the intro
   ("with at most three owners, the engine-relevant range — see
   Remark 4") would remove it.
2. (Minor, manifest bookkeeping) `rem:t3-profile-scope` contains a genuine
   proof (owner-avoidance WLOG) but has no dedicated manifest entry; it is
   subsumed under `def:t3-profile`. Verified sound regardless.
3. (Minor, attribution precision) The manifest credits R41 sec 7 with
   "including owner-avoiding coverage"; the explicit owner-avoidance (v not
   in Q) appears in R48's coverage relation R_cov, R41 saying only "selected
   rows cover {x,s0},{x,s1}". Immaterial because the section proves avoidance
   costs nothing.
4. (Minor, presentation) `rem:t3-fourowners` assumes d_B >= 4 as part of the
   engine configuration where the source derives it (see verdict 4).

No MISMATCH and no GAP verdicts. All twelve claims CONFIRMED; the two
closure proofs are complete at the stated level; all four Lean citations are
exact; the classification dependence was independently re-verified by
rerunning both enumerators; the assembled LaTeX compiles cleanly.
