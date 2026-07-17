# CLAIMS LEDGER — "Balanced deficiency rotors in shortest-support Hall systems of triangle-free maximum cuts"

Paper: `problems/23/writeup/arxiv/rotor_window_closures/main.tex` (assembled 2026-07-17).
Companion: `problems/23/writeup/arxiv/shortest_support_obstructions/main.tex` (cited as
`Ferudun26supports`); published certificate paper arXiv:2606.28041 (cited as `Ferudun26`).

This ledger aggregates the six per-section claims manifests
(`sections/*_claims.md`), the six adversarial referee reports
(`review_*.md`, all dated 2026-07-17), and the fixes applied at assembly.
Statuses: **proved** = complete proof in the paper; **Lean** = kernel-checked
Lean 4 declaration (axioms within {propext, Classical.choice, Quot.sound},
no sorry / native_decide, except where noted); **CA** = computer-assisted
(verifier + SHA-256); **CA-single** = computer-assisted, single solver, no
independent replay (flagged in the paper text).

Referee outcome summary: 6/6 sections reviewed adversarially; every proof
marked "proved" was verified complete; one MISMATCH (rotor verification
remark) and one GAP (t=5 open-question "Equivalently") were found, and both
are FIXED in the assembled version (see "Assembly fixes" below). No claim
required outright removal.

---

## Section 2 — Support circuits (`sections/support_circuits.tex`)

Review: `review_circuit-identity.md` — 13/13 manifest rows CONFIRMED, 4/4 exclusions CONFIRMED, no MISMATCH/GAP.

| Claim | Status | Verification |
|---|---|---|
| def:circuit (support circuit = inclusion-minimal deficient) | definitional | text equivalence, one line |
| thm:circuit (i) \|F*\| = m-1 | proved | paper only (NOT Lean; shell `minimalSupportDeficient_union_card` grep-verified absent from problems/23/lean) |
| thm:circuit (ii) deletion-unions = F* | proved | paper only |
| thm:circuit (iii) multiplicity >= 2 | proved | paper only |
| thm:circuit (iv) incidence connectivity | proved | paper only |
| thm:circuit (v) deletion-SDR bijections | proved | paper only (Hall's theorem now cited: Hall35) |
| rem:intrinsic (identity intrinsic to circuit) | proved | trivial from (i) |
| cor:sdr (circuit <=> no SDR, proper subfamilies have SDR) | proved | paper only |
| rem:matroid (transversal-matroid circuits) | proved | classical, cited EdmondsFulkerson65 |
| cor:graph (a)-(e) (graph form) | proved | paper; (a)-(d) recover companion's Minimal footprint lemma, (e)+connectivity+deletion-union new |
| cor:sizes (m >= 5; avg multiplicity > 4) | proved | paper only |

Sources: WALL_ATTACK_R44_GPTPRO56.md §1; companion main.tex lem:minimal.

## Section 3 — Star lemma at cut-tight vertices (`sections/star_lemma.tex`)

Review: `review_star-lemma.md` — 12/12 CONFIRMED, no MISMATCH/GAP. Lean source
hashes recomputed and matched to the 2026-07-11 gate-accepted builds.

| Claim | Status | Verification |
|---|---|---|
| lem:switchloss (switch identity; sigma >= 0 at max cut) | proved + Lean | `sigmaNonneg_of_badCount_min` (CertGraph.lean), `singleton_sigma_nonneg_of_isMaxCut` (SingletonPairSigma.lean, SHA e4060bcc...) |
| lem:nonedgeadd (additivity on a nonedge) | proved + Lean | `sigma_pair_eq_add_singletons_of_nonadjacent` + dB/dM halves (SingletonPairSigma.lean) |
| lem:starineq (star identity + inequality) | proved | paper only — explicitly NOT formalized (honesty flag verified both ways) |
| cor:badendpoint | proved | paper |
| cor:losstwoneighbour | proved | paper |
| prop:pairthreshold | proved + Lean | `nonadjacent_of_common_blue`, `two_le_sigma_pair_of_two_le_left`, `common_blue_pair_two_le_of_left_loss` |
| lem:starpigeon (abstract pigeonhole) | proved + Lean | `exists_other_with_two_le_loss_sum` (CutTightStarPigeonhole.lean, SHA dd6da23c...) |
| thm:starlemma (assembled star lemma) | proved | paper assembly; NOT a single Lean theorem (stated in rem:leanstar) |

No computer-assisted claims. Sources: WALL_ATTACK_R41_GPTPRO56.md §§1-3.

## Section 4 — Eight-vertex neutral square rotor (`sections/claude_eight_vertex_rotor.tex`)

Review: `review_rotor-construction.md` — all mathematics CONFIRMED (independent
machine re-verification C1-C5 all PASS); ONE MISMATCH in rem:rotor8-verification
(machine-verification overclaim + nonexistent ancillary archive) — **FIXED**.

| Claim | Status | Verification |
|---|---|---|
| def:rotor8 (graph R, cut, B, M) | construction | gate G1 |
| prop:rotor8-maxcut (tri-free, MaxCut=8, bip=2) | proved + CA | four-pentagon double count; gate G2 (all 2^8 cuts); NOTE: maximum cut NOT unique (11 max cuts exist; uniqueness never claimed) |
| lem:rotor8-geodesics (exactly two geodesics per bad edge; supp = B) | proved + CA | gate G3 (4-edge-path completeness half; d_B=4 is in-text) |
| def:rotor8-selection | definitional | n/a |
| thm:rotor8-states (4 states, 4-cycle, owners, \|S\|=7) | proved + CA | gates G4-G6 |
| prop:rotor8-neutral (order-4 shore-swapping automorphism) | proved + CA | in-text finite check + anc/verify_rotor8_automorphism.py (SHA 756cc65a..., PASS 2026-07-17: automorphism, order 4, shore swap, BFS d_B=4, states recomputed, transitive 4-cycle action) |
| rem:rotor8-scope (not a Hall violation; graft question open) | proved facts + open question | gate G5 |
| rem:rotor8-verification | meta | gate script SHA 6d74bcbd..., rerun PASS 2026-07-17 (also from the anc/ copy at assembly); now also cites verify_rotor8_automorphism.py (756cc65a...), "every numbered statement" phrasing restored 2026-07-17 |

Verifier: `anc/_claude_r39_8vtx_rotor_gate.py`
SHA-256 6d74bcbd1bab12948c5e1a498f62a7185b03743a2b701ec5aeba6f54b01b2aeb.
Source: WALL_ATTACK_R39_GPTPRO56.md §§4-5.

## Section 5 — No balanced rotor on nine-atom circuits, t=3 (`sections/claude_t3_no_balanced_rotor.tex`)

Review: `review_t3-closure.md` — 12/12 CONFIRMED, no MISMATCH/GAP; both
companion enumerators rerun for m<=9 (unique footprint H???FaM reproduced);
section compiled cleanly with companion preamble by the reviewer.

| Claim | Status | Verification |
|---|---|---|
| def:t3-profile, rem:t3-profile-scope (weakened owner profile; avoidance free) | definitional + proved | paper |
| def:t3-rotor (balanced rotor, k in {2,3}) | definitional | matches Lean inductive `T3BalancedDeficiencyRotor` |
| rem:t3-fourowners (engine 4-owner geometry forces \|M\|>=12>9) | proved + Lean | `twelve_le_ambient_card`, `not_ambient_card_nine` (CutTightActiveRotorIncidence.lean, SHA 0814a665...); only max-cut-dependent statement |
| lem:t3-ownerdeg (owner has deg_F >= 3) | proved + Lean core | `fullyCoveredLiveStar_fullSupportDegree_ge_three` (R43SupportIncidence.lean, SHA 66649670...) |
| lem:t3-disjoint (owners one shore, nonadjacent, disjoint edge sets) | proved | paper; enters Lean carriers as hypotheses |
| thm:t3-counting (FIRST CLOSURE, shape-independent) | proved + Lean core | `twoRotatingOwners_force_nine_supportEdges`, `threeRotatingOwners_force_nine_supportEdges`, `no_t3_balancedDeficiencyRotor`; graph adapter paper-level (division stated) |
| thm:t3-emptystar (row exclusion at a closed star) | proved + Lean | `bad_star_cover_row_impossible` (BadStarCoverFreeness.lean, SHA afd944ea...), `pairCount_eq_zero_of_closedBadStar` (K33BadStarPairCountZero.lean, SHA 35456523...), `checkedRow_blue_cooccur_implies_pathEdge` (SaturatedRotorSupportPersistence.lean) |
| cor:t3-second (SECOND CLOSURE) | proved, conditional on companion classification (CA, two independent verifiers, rerun by referee) | dependence stated in text |
| rem:t3-independent / rem:t3-lean / rem:t3-scope | meta / factual | SHAs recomputed 2026-07-17, all match |

Sources: WALL_ATTACK_R41/R42/R43/R48; archive REPORT.md
(r42_graph_specific_exclusion); PROGRESS.md:2979 GATE-T3CLOSURE rebuild record.

## Section 6 — The sixteen-atom closure, t=4 (`sections/sixteen_atom_closure.tex`)

Review: `review_t4-closure.md` — no MISMATCH/GAP; the ENTIRE census pipeline and
all five artifacts reproduced bit-exactly on 2026-07-17; four ranked wording/
provenance issues — **ALL FIXED** at assembly.

| Claim | Status | Verification |
|---|---|---|
| def:t4:circuit | definitional | matches companion + R44 deletion-SDR |
| lem:t4:transfer (minimal violations are circuits; incidence connected) | proved | paper |
| lem:t4:induced (rows induced) | proved | paper |
| def:t4:selection / def:t4:rotating | definitional | weakening of engine profile (sound direction) |
| thm:t4:crossover (i) \|E(F)\| >= kt+t; (ii) k=2 covered => >= 3t+2 | proved | paper (R44 "by inspection" steps written out in full) |
| cor:t4:table + tab:t4:crossover ((4,2) sole survivor, margin 1) | proved | arithmetic checked entry-by-entry |
| def:t4:window | definitional | matches census filter exactly |
| lem:t4:absorption (star absorption) | proved | paper |
| prop:t4:core (shared atom-partner; K_{2,3} core) | proved + Lean | `exists_common_tail_of_support_card_le_fifteen` (R44K2TailOverlap.lean, SHA 12dfb927...), axioms dual-attested |
| lem:t4:vertexrange (8 <= \|V\| <= 15; covered => <= 14) | proved | paper (unicyclic kill fully reconstructed) |
| thm:t4:census (153,978 graphs -> 34 embeddings -> 576 windows, all \|V\|=15; forced >= 8 histograms; zero middle swaps) | CA, dual acceptance paths | artifacts 40f16a84... / 302e04ef... / b464682b...; verifiers PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS / _ATOM_CENSUS / PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION; full bit-exact replay 2026-07-17 |
| cor:t4:closure (THE t=4 CLOSURE: no covered two-owner window) | proved given thm:t4:census | modus ponens (14 < 15) |
| prop:t4:swapgeometry (middle swap => cross-outer; row-free confirmation) | Lean + CA | `live_middle_swap_has_cross_outer` (LiveMiddleSwapCrossOuter.lean, SHA 3dff7897...; axiom audit DUAL: acceptance record + fresh rebuild-and-probe 2026-07-17, anc/lean_axiom_probe/, PASS_AXIOM_PROBE, axioms exactly propext, Quot.sound); artifact 79db75b9..., PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY |
| rem:t4:nearmiss (independent catalogue + 14-vertex near-miss) | CA-single, corroboration only | checker prefix 4644e5ab (not in repo); explicitly non-load-bearing |
| rem:t4:abstract (abstract 16/15 circuit; geometry load-bearing) | CA + independent recheck | artifact 5b386cd9... (regenerated at seed 0 step 0); wording now "have not been realized ... no census window realizes them" |
| rem:t4:scope | honest scope | (5,2)/(5,3) margins 7/4 open |

## Section 7 — Partial results at twenty-five atoms, t=5 (`sections/t5_partial.tex`)

Review: `review_t5-partial.md` — 22 CONFIRMED, 1 GAP (open-question
"Equivalently" — **FIXED** to "In particular"); 12 infeasible + 3 feasible
CP-SAT splits re-run from scratch; prop:hits independently reconstructed with a
fresh encoding; artifact attributions corrected at assembly from the archive
REPORT.md (issue I3).

| Claim | Status | Verification |
|---|---|---|
| def:t5circuit / def:selection / def:owner / def:live / def:rotor | definitional | faithful weakenings; a fortiori direction stated |
| lem:tight / lem:positions / lem:steps / lem:parity | proved | paper |
| cor:coverage (cycle rank >= 4; \|V\| <= 21) | proved | paper |
| lem:trichotomy | proved | paper |
| thm:order15 (order >= 15; window 15..21) | proved | paper (Mantel equality analysis) |
| thm:selected (\|S_omega\| >= 3t-1) + cor:latent + rem:t3 | proved | paper |
| realizability remark (four-part finite test) | proved | paper, both directions |
| lem:shores (owner class >= 7 / >= 5) | proved | paper |
| prop:orders1516 (orders 15,16 excluded, 9 splits) | CA-single | `rooted_t5_support_cp_sat.py`; artifact prefixes 14ac9d93 8d194613 66e0813c 5721cbc5 / 8dff49ea bd0c0320 cc5462d6 b5037e11 9f9401d0; referee replayed all 9 INFEASIBLE from scratch; regenerated BIT-EXACTLY 2026-07-17 and SHIPPED in anc/t5_artifacts/ |
| printed graph6 facts (#298, #264) | proved / reader-checkable | re-verified twice (drafting + review) |
| prop:hits (two 25-atom circuits with covered rotating owners) | CA, dual-verified | #298 primary c1d474d7, verification 48ce1638; #264 primary 6595501f, verification d9e73413; verifier script SHA prefix 017d1e44 (attribution FIXED at assembly); 2026-07-17: sweep trajectory solver-nondeterministic, both circuits REBUILT on the pinned printed graphs at recorded (v,x0) (#298 ff1c1209, #264 78db4d23), verifier PASS on both, SHIPPED in anc/t5_artifacts/; historical prefixes retained as session record |
| prop:dead (owners dead in both circuits) | proved modulo (f1)/(f2) | (f1)/(f2) CA dual-verified (3720a8c2) + independent re-verification |
| all-row dead-owner certificates | CA, dual-verified | #298 f5c0cbca + a8a160d5; #264 79471ef0 (CP-SAT, ADDED at assembly) + c7fbcc70 (CaDiCaL); regenerated 2026-07-17 on the pinned payloads, verdict-equal, CNF sizes exact (#298 1680/5239, #264 1645/5140), SHIPPED in anc/t5_artifacts/ |
| prop:extension (#264 ambient exclusion, 8 assignments) | CA, dual-verified | `extend_t5_hit_maxcut.py` + `verify_t5_maxcut_extension_unsat.py`; no output SHAs recorded (stated); regenerated 2026-07-17 (8/8 INFEASIBLE + PASS_ALL_EIGHT_SPLITS_UNSAT), SHIPPED in anc/t5_artifacts/ |
| prop:298extension (#298 ambient exclusion, 8 assignments; PROMOTED from rem:298maxcut 2026-07-17) | CA, dual-verified | same two verifiers as #264 on the rebuilt pinned circuit; source ff1c1209, extension 2bf166b7, replay d176ce66 (PASS_ALL_EIGHT_SPLITS_UNSAT); switch S={4,5,6,7,8,12,14,15,16} crossed by 24/25 atoms vs 4 support edges (sigma=-20) recomputed; chain SHIPPED in anc/t5_artifacts/298_extension/; caveat: atom set is the regenerated witness on the pinned printed graph, not guaranteed bit-identical to the deleted archived set (prop:dead unaffected) |
| prop:order17 (3 splits infeasible / 3 feasible) | CA-single | prefixes 4d450ca0 f76b9d64 325012ec; per-split mapping FIXED 2026-07-17 by bit-exact regeneration (4d450ca0=(7,10), f76b9d64=(8,9), 325012ec=(12,5)), stated in text; feasible splits re-certified at --max-supports 1; bounded searches 95dbc901 d612c59e 31d82c62 non-probative, not regenerated (nondeterministic enumeration) |
| order-18 350-support search | bounded, non-probative | stated |
| Open question (scope-vacuity at t=5) | OPEN | stated as question; "In particular" (not "Equivalently") |

## Master verification record

Ancillary archive `anc/` (created at assembly; extended 2026-07-17): 19
scripts + 9 Lean sources + the Lean axiom-probe record (`lean_axiom_probe/`)
+ the five t=4 census artifacts (`t4_artifacts/`) + the regenerated t=5
certificate artifacts (`t5_artifacts/`, incl. `298_extension/`) + README.md
+ SHA256SUMS (regenerated, recursive, 80 entries) + per-TODO notes files.
Full SHA-256 hashes in `anc/SHA256SUMS`; the Lean
production hashes were recomputed at assembly and match every value printed in
the paper:

- SingletonPairSigma.lean e4060bcc... ; CutTightStarPigeonhole.lean dd6da23c... ;
  R43SupportIncidence.lean 66649670... ; BadStarCoverFreeness.lean afd944ea... ;
  K33BadStarPairCountZero.lean 35456523... ; CutTightActiveRotorIncidence.lean 0814a665... ;
  SaturatedRotorSupportPersistence.lean b4438520... ; R44K2TailOverlap.lean 12dfb927... ;
  LiveMiddleSwapCrossOuter.lean 3dff7897...
- Rotor gate script 6d74bcbd... rerun at assembly: `CLAUDE-GATE=PASS (exhaustive)`, exit 0.
- Rotor automorphism checker 756cc65a... run 2026-07-17: `PASS_ROTOR8_AUTOMORPHISM`, exit 0.
- t=4 canonical artifacts (regenerated bit-exactly 2026-07-17 by the referee, now SHIPPED in anc/t4_artifacts/;
  embedded canonical hashes re-verified equal to the paper's values):
  40f16a84... / 302e04ef... / b464682b... / 79db75b9... / 5b386cd9...
- t=5 artifacts: SHIPPED in anc/t5_artifacts/ (12 splits bit-exact to the cited prefixes; circuit-level
  rebuilt on the pinned printed graphs, verdict-equal; historical prefixes retained in the paper as the
  session record; regeneration record anc/t5_artifacts/NOTES_t5_regeneration.md).
- LiveMiddleSwapCrossOuter axiom audit: dual-attested (acceptance record + fresh rebuild-and-probe
  2026-07-17, anc/lean_axiom_probe/, PASS_AXIOM_PROBE, axioms exactly propext, Quot.sound).

## Assembly fixes applied (2026-07-17)

1. **rotor MISMATCH (review_rotor-construction.md):** intro and
   rem:rotor8-verification no longer claim machine verification of the
   automorphism (prop:rotor8-neutral) — its finite check is in-text; the
   ancillary archive `anc/` now actually exists and contains the gate script;
   "cycles with period four" -> "never terminates" (walk may backtrack);
   geodesic-family machine check scoped to the 4-edge-path completeness half;
   "no canonical tie-break can halt" -> "no isomorphism-invariant tie-break
   distinguishes the states". (Automorphism sub-item superseded 2026-07-17:
   dedicated checker verify_rotor8_automorphism.py added and PASSED, "every
   numbered statement" phrasing restored — TODO 3.)
2. **t=5 GAP (review_t5-partial.md I2):** open question "Equivalently" ->
   "In particular" (scope-vacuity implies no balanced rotor; converse unproved).
3. **t=5 artifact attribution (I3):** #298 primary hit = c1d474d7 (48ce1638 is
   the verification artifact; 017d1e44 is the verifier script's own SHA);
   #264 primary = 6595501f (d9e73413 = verification artifact); #264 all-row
   CP-SAT prefix 79471ef0 added alongside CaDiCaL c7fbcc70. Corrected in prose
   and in tab:t5artifacts, per archive REPORT.md.
4. **t=5 I4:** "their minimal subsystems are always the nine-atom circuit"
   softened to "the nine-atom circuit arises among their minimal subsystems",
   with \cite{Ferudun26supports} added (matches what the companion proves).
5. **t=5 order-17 prefixes:** now stated as "recorded without an explicit
   per-split mapping".
6. **t=5 I1 caveat:** tab:t5artifacts caption now states that the hashed
   artifacts are session records not included in the ancillary files, and that
   the cheap verdicts were re-run from the archived scripts in the 2026-07-17
   review pass. (Superseded 2026-07-17: artifacts regenerated and shipped in
   anc/t5_artifacts/, caption rewritten accordingly — TODO 1.)
7. **t=4 issue 1:** LiveMiddleSwapCrossOuter axiom set softened to "its
   acceptance record lists axioms propext, Quot.sound" (single-source
   attestation; probe queued but never completed). (Superseded 2026-07-17:
   probe completed, dual-attestation wording restored — TODO 2.)
8. **t=4 issue 2:** "no shared code" -> "no shared code beyond the geng
   generator".
9. **t=4 issue 3:** abstract circuit "supports are not realized" -> "have not
   been realized ... and no census window realizes them".
10. **t=4 issue 4:** artifact-list header sentence now distinguishes the three
    census emissions from the two verification-path artifacts and the Lean
    sources.
11. **support-circuits notes N1-N4:** closing remark now credits the
    deletion-union clause of cor:graph(b) as statement-level new (N1); m >= 2
    justified when invoking thm:circuit in cor:graph (N2); "sharper counts are
    available" -> "are derived in later sections" (N3); Hall's theorem cited
    (Hall35) (N4).
12. **t=3 issue 1:** intro hedge added — cyclic families "with at most three
    owners, the engine-relevant range on nine atoms (Remark rem:t3-fourowners)".
13. **t=4 cite key:** \cite{SSO} unified to \cite{Ferudun26supports}.

## Dropped / demoted claims (none fabricated, none silently kept)

No referee verdict required deleting a mathematical claim outright. The
following remain deliberately EXCLUDED from the paper (carried over from the
section manifests, verified excluded by the referees):

- Rotor: Gamma_min=50; max-cut uniqueness (FALSE — 11 maximum cuts);
  cascade refutations; the grafted-rotor falsifier blueprint (except the
  one-sentence open question); pair-mass heuristics; uncompiled Lean shapes;
  "8 halves" bookkeeping.
- Star lemma: strongProbe-or-detour dichotomy (Lean shapes only);
  `noPositiveDefectFullyCoveredCutTightStar` (open); P1 pincer identity;
  anchored-mass bounds; the t=3 falsifier window; probability estimates.
- Circuits: R50 selected-support bound in the abstract section (moved to t=5);
  Lean status for the circuit identity (module absent from the development).
- t=3: reservation-starvation verdict; probability estimates; any unconditional
  "closed in Lean" claim; K3,3-only closure without the classification.
- t=4: full edge/atom lists of the 14-vertex near-miss (session-internal —
  only archived invariants printed); SHA prefix 83b1ee2f (unidentifiable
  artifact); R44OwnerStarDualHall.lean / A8D39A65 (no gate-accepted rebuild);
  profile-conditioned zero counts (once retracted); the reversed ambient
  restriction; GPT catalogue as load-bearing.
- t=5: n<=20 live-owner bound (outside source set); per-owner exhaustiveness
  beyond recorded pairs; the R49 "clustering+Mantel cannot close 15-21" claim;
  relaxation-ladder / k=3 / t=6 / separator machinery; probability estimates;
  the superseded R46 near-candidate. (The former exclusion "#298 extension
  UNSAT as a proposition" was lifted 2026-07-17: the chain was independently
  replayed and rem:298maxcut promoted to prop:298extension — TODO 6.)

## Open TODOs for the human author

1. ~~Regenerate the t=5 certificate artifacts~~ **DONE 2026-07-17.**
   Regenerated from the archived scripts and shipped in `anc/t5_artifacts/`:
   twelve split certificates BIT-EXACT to the cited prefixes (fixing the
   order-17 per-split mapping); the three feasible order-17 splits
   re-certified at `--max-supports 1`; both circuit hits rebuilt on the
   pinned printed graphs at the recorded (v,x0) (sweep trajectory is
   solver-nondeterministic, so byte-exact replay of the circuit-level
   artifacts is impossible — recorded in
   `anc/t5_artifacts/NOTES_t5_regeneration.md`); every downstream verdict
   reproduced, CNF sizes exact (1680/5239, 1645/5140). Caption of
   tab:t5artifacts and the Reproducibility section rewritten accordingly.
2. ~~Rebuild + axiom-probe `LiveMiddleSwapCrossOuter.lean`~~ **DONE
   2026-07-17.** Five-module chain rebuilt from source on the
   formal-conjectures Mathlib cache; kernel probe reports axioms exactly
   [propext, Quot.sound]; `PASS_AXIOM_PROBE`; record in
   `anc/lean_axiom_probe/`. Dual-attestation wording restored in main.tex
   and prop:t4:swapgeometry.
3. ~~Archive a sigma-automorphism checking script~~ **DONE 2026-07-17.**
   `anc/verify_rotor8_automorphism.py` (SHA 756cc65a...), all five checks
   PASS + three mutation controls fail as intended; "every numbered
   statement" phrasing restored in the rotor section.
4. **Companion citation:** `Ferudun26supports` is cited as "preprint, 2026" —
   insert its arXiv identifier once posted (v2 replacement), and cross-link
   the two papers' abstracts. (STILL OPEN — companion submit/7816436 was on
   hold in moderation at submission time)
5. ~~Compile check~~ **DONE 2026-07-17 (at submission).** arXiv AutoTeX
   compiled the submitted package with pdflatex (TeX Live 2025):
   `[SUCCEEDED]`, 31 pages, 458384 bytes, zero errors, no unresolved
   references (the nine `??` occurrences in extracted text are the two
   printed graph6 strings). Compiled PDF archived as
   `output/pdf/rotor_window_closures_arxiv_compiled.pdf` (SHA-256
   4C86BCF1B852F7BA31BBB0AE9FC56FEE8921DC936ACDC4D9E9EE23917D008483).
6. ~~Decide on the #298 ambient extension~~ **DONE 2026-07-17.** Replayed
   independently (rebuilt pinned hit ff1c1209, primary extension 2bf166b7
   8/8 INFEASIBLE, CaDiCaL replay d176ce66 PASS_ALL_EIGHT_SPLITS_UNSAT;
   chain in `anc/t5_artifacts/298_extension/`); rem:298maxcut PROMOTED to
   prop:298extension. Caveat: the certified 25-atom set is the regenerated
   witness on the pinned graph (original deleted), stated in the notes;
   prop:dead unaffected.
7. ~~Regenerate the five t=4 census artifacts into `anc/`~~ **DONE
   2026-07-17.** Shipped in `anc/t4_artifacts/` (1.9 MB total); embedded
   canonical hashes re-verified equal to the paper's printed values;
   verifiers re-exercised against the shipped copies (support census, atom
   census, profile exclusion, cross-outer exclusion — byte-identical
   regeneration — and abstract support circuit), all PASS.
8. ~~Packaging decision~~ **DONE 2026-07-17.** Kept: all NOTES files (they
   are the per-artifact regeneration records the paper's captions reference)
   and the clearly-labelled divergent fresh sweep (honest record). Dropped:
   the five byte-identical stdout/empty stderr captures under
   `298_extension/`. SHA256SUMS regenerated (75 entries, verified 0 fails).
   arXiv package: `main.tex` (+`\pdfoutput=1`) + `sections/*.tex` (leading
   provenance comment blocks stripped from the package copies only; repo
   copies unchanged) + `anc/` in full. Package zip SHA-256
   501C3D8E9CAE6EFEA4332AEBFB873BE0CC5CC8FEC38CDCBFB675BE51D64EDFB9,
   archived as `output/pdf/rotor_window_closures_arxiv.zip`.

## Submission record

**Submitted to arXiv 2026-07-17** as `submit/7837759` (user-authorized, via
the logged-in arXiv account): primary category math.CO, license CC BY 4.0,
MSC-class 05C35, comments "31 pages. Ancillary files contain all verifier
scripts, regenerated certificate artifacts, Lean 4 sources, and a SHA-256
manifest." Status at submission: **on hold** (moderation queue), same state
as the companion submit/7816436. Ledger closure note:
`problems/23/ERDOS23_LEDGER_CLOSED_20260717.md`.
