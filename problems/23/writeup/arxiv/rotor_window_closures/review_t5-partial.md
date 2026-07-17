# Adversarial referee review — `sections/t5_partial.tex` (+ `t5_partial_claims.md`)

Reviewer: independent referee session, 2026-07-17.
Scope: every numbered claim of the manifest checked against the named sources
(WALL_ATTACK_R48/R49/R50 archives, LOOP_STATE TICK-108/109/110, PROGRESS.md
2994/2998/3001-3005, the archived engine/verifier scripts under
`problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/`
and its `REPORT.md`); all by-hand proofs re-derived line by line; all
reader-checkable finite facts re-verified by fresh scripts written for this
review (not copied from the drafter's); the nine+three CP-SAT infeasibility
verdicts re-run from scratch; Proposition `prop:hits` independently
reconstructed with a new CP-SAT encoding written from the paper's own
definitions.

Verification artifacts of this review (session scratchpad `referee/`):
`referee_check_t5.py` (graph6 facts, f1/f2, switch crossings),
`referee_hits_existence.py` (independent existence search for prop:hits),
`replay_l{p}_r{q}.json` x15 (CP-SAT split replays), `tex_audit.py`.

## Replay results (fresh runs, this session)

- CP-SAT support relaxation, all 12 claimed-infeasible splits re-run with the
  archived `rooted_t5_support_cp_sat.py` (defaults; no shared-s, no
  live-transition constraints in the support stage):
  n=15 (7,8),(8,7),(9,6),(10,5); n=16 (7,9),(8,8),(9,7),(10,6),(11,5);
  n=17 (7,10),(8,9),(12,5) — **all INFEASIBLE with supportsSolved=0**
  (completed proofs, no time-outs). The three claimed-feasible n=17 splits
  (9,8),(10,7),(11,6) re-run **support-feasible** (supportsSolved=1 each).
- I read the support-stage model in the archived script and confirm it encodes
  **exactly** (R1)-(R7) plus WLOG rooting (v,m,a,b,x,y labelled) plus
  degree-sorting of the non-distinguished vertices only (left indices >= 4,
  right indices >= 2). No extra constraint is imposed at the support stage
  when `--require-live-transition-profile` is absent (it is incompatible with
  `--local-classifier`, which the recorded runs used). Distance-four is
  encoded exactly (two-step in the shore square AND no common neighbour).
  Direction of soundness is correct: script-INFEASIBLE => (R1)-(R7)
  infeasible => no balanced rotor at that order/split.
- Independent reconstruction of `prop:hits`: my own encoding (25 atoms from
  the supply, multiplicity >= 2, atom-graph triangle-free, all 25
  deletion-SDRs, deg_A(owner)=5, selection satisfying Def. owner (i)-(iv))
  returns **OPTIMAL (witness found) for #298 at (0,17) and #264 at (0,9)**.
  In both witnesses the only latent edge is the active edge and the owner
  tail is the singleton {x0} — dead, consistent with `prop:dead`.
- All printed graph6 facts re-verified exactly (see per-claim list).
- The drafter's cited session scripts (`check_hits.py`, `verify_circuits.py`,
  shared scratchpad) rerun: outputs agree with the section.

## Per-claim verdicts (manifest numbering)

| # | Claim | Verdict |
|---|-------|---------|
| D | Definitions t5circuit/selection/owner/live/rotor | **CONFIRMED** — faithful renderings of R48 secs 1-4, R50 secs 1-3, R49 sec 6 and the engine's circuit axioms (24 edges / 25 atoms / d4 same-class / multiplicity>=2 / deletion-SDRs / tri-free); the deletion-SDR <=> proper-subfamily-SDR equivalence and the Hall-defect-one gloss are correct. The "full rotor object contains this data, exclusions apply a fortiori" direction is the sound one. |
| 1 | `lem:tight` | **CONFIRMED** — proof complete; matches R48 gate item (1) (Forced=Inc sharpness; >= t+1 when violated). |
| 2 | `lem:positions` | **CONFIRMED** — proof complete (q1/q3 parity, (ii) and adjacency kill both); matches R50 "no incident row contains x0". |
| 3 | `lem:steps` | **CONFIRMED** — proof complete; surjectivity + pigeonhole gives (2,1,...,1); matches R48 item (2). |
| 4 | `lem:parity` | **CONFIRMED** — full parity proof correct (three N(v)-members at 0,2,4 make the atom endpoints distance <= 2). Matches R48 item (3). |
| 5 | `cor:coverage` | **CONFIRMED** — four distinct covering atoms (parity), common row-neighbour q_i != v, private edges vy_i give independence, rank >= 4, \|V\| <= 21. Complete. |
| 6 | `lem:trichotomy` | **CONFIRMED** — proof complete; merging R49's Types 0/2 into case II loses nothing used later (endpoint counts preserved). |
| 7 | `thm:order15` | **CONFIRMED** — \|K\|=11 correct; >= 3 externals correct in both branches; case 1 (4 distinct atoms on C(3,2)=3 pairs) and case 2 (Mantel equality 16+9=25 forces K_{4,4}, max degree 4 < deg_A(v)=5) both check out. Window 15..21 follows. |
| 8 | `thm:selected` | **CONFIRMED** — the three edge families are pairwise disjoint (class bookkeeping and d(v,b_j)=4 both verified), none contains x0, the coverage row adds a genuinely new edge at x0; \|S\|>=3t-1, \|L\|<=t(t-3). Complete for all t>=3. |
| 9 | `cor:latent` | **CONFIRMED** — 14/10/9 arithmetic correct (tail excludes vx0 since v is deleted). |
| 10 | `rem:t3` | **CONFIRMED** — t=3 impossibility is immediate from thm 8 + (ii); the double-star consistency fact re-checked computationally (9-atom double star: no vertex has support- and atom-degree both 3); budgets 0/4/10 match R50 sec 9. |
| 11 | realizability remark | **CONFIRMED** — both directions verified by hand; the converse construction (coverage matching rows + step matching rows + arbitrary v-avoiding rows) does realize (i)-(iv); coverage atoms are automatically off v. |
| 12 | `lem:shores` | **CONFIRMED** — d(v,m)=2 via x, partners at distance 4, so 7 distinct; N_F(v) gives 5. Matches the driver's root validation (`left >= 7 and right >= 5`). |
| 13 | `prop:orders1516` | **CONFIRMED + REPLAYED** — all 9 splits re-run INFEASIBLE from scratch this session; support model verified to be exactly (R1)-(R7)+WLOG (see above); SHA prefixes match PROGRESS 3001/3003/3004 and TICK-109/110 with per-split order preserved; single-solver status honestly flagged in the text. Caveat: the original JSON artifacts no longer exist in the repo (see Issues). |
| 14 | printed graph6 facts | **CONFIRMED** — re-verified independently: both graphs 18 vertices / 24 edges / classes 0-8, 9-17 / connected / bipartite; deg(0)=deg(1)=5; d(2,3)=4; rotor core rows (2,9,0,y,3),(2,9,1,y,3) present as geodesics of {2,3} (y in {10,13} resp. {10,12,13}); supply 32 (#298) and 30 (#264). |
| 15 | `prop:hits` | **CONFIRMED (independently reconstructed)** — existence re-derived with a fresh CP-SAT encoding; witnesses found at exactly the recorded pairs, atom graph triangle-free (nontrivially: the full supplies contain 12 resp. 10 atom triangles), all deletion-SDRs valid. Bookkeeping mismatch in the artifact citation, see Issues (I3). |
| 16 | `prop:dead` | **CONFIRMED** — the by-hand proof is complete given finite facts, and every finite input was re-verified this session: #298 deg(17)=2, N(17)={0,1}, N(0)=N(1)={9,10,11,13,17} (so the 0<->1 transposition is an automorphism); #264 N(9)={0,1,2}, N(0)={9,10,12,13,15}, (f1) witness counts 3/3/3/1 with every witness through edge {1,9}, (f2) unique row (15,2,9,1,17), a row of the pair {15,17}, using {2,9}. Note the proof is atom-set-independent (f1/f2 quantify over all same-class d4 pairs), which is stronger than the fixed-circuit certificates. |
| 17 | all-row dead-owner certificates | **CONFIRMED AS CITED** — statements and prefixes match R49 gate header (f5c0cbca, a8a160d5, 1680 vars/5239 clauses), archive REPORT.md and PROGRESS 2998 (c7fbcc70); the "no atom has both endpoints in the owner's latent component" rendering is equivalent to the engine's two-commodity flow encoding; verifier confirmed to be CaDiCaL via PySAT. Two caveats: (i) the #264 CP-SAT prefix (79471ef0, in the archive REPORT) is uncited although the text says "twice per circuit"; (ii) artifacts deleted — not re-runnable (Issues I1). |
| 18 | `prop:extension` | **CONFIRMED AS CITED** — the model scope in the .tex (<= 25 vertices, classes extended, all crossing edges free, unused vertices isolated, row preservation, maximum cut) faithfully renders the archive REPORT's #264 extension section (which is the authoritative source; the manifest's pointer to REPLAY.md actually describes the earlier l10r8 smoke hit, same model shape). Switch S={4,5,6,7,8,11,14,16}: **2 support crossings re-verified this session** ((2,14),(3,11)); capacities 21,19,...,7 and the joint kill 42>28 match REPORT verbatim; 23 atom crossings is artifact-dependent (supply crossings = 24, consistent). Replay coverage of the #264 extension is documented (TICK-106 "6/6 PASS ... #264 8-split extension", PROGRESS 2998). No output SHAs recorded — honestly stated. |
| 19 | `rem:298maxcut` | **CONFIRMED AS CITED** — R49 "min switch sigma -20" (also: exhaustive full-supply min sigma on #298 recomputed this session is -20, consistent); the #298 eight-assignment record reduces to PROGRESS 2994's phrase "both hits die at (ii)+(iii)" — thin, which is precisely why the demotion to a remark (not a proposition) is the right call. |
| 20 | `prop:order17` | **CONFIRMED + REPLAYED** — the 3/3 infeasible/feasible pattern re-run from scratch and confirmed; bounded no-hit runs correctly framed as non-probative. MINOR: the parenthetical juxtaposition of the three splits with the three prefixes 4d450ca0/f76b9d64/325012ec reads as an ordered mapping that no source asserts (PROGRESS 3005 lists them unmapped); suggest "in some order" or per-split records. |
| 21 | order-18, 350 supports | **CONFIRMED** — matches R49 gate header; explicitly non-probative in the text. |
| 22 | open question | **GAP (minor, framing)** — "Is every support circuit at twenty-five atoms scope-vacuous? *Equivalently*, is there no balanced rotor at t=5?" is NOT an equivalence on the section's definitions. Scope-vacuity of all circuits => no balanced rotor (a balanced rotor's live owner witnesses non-vacuity). The converse fails structurally: a live covered rotating owner at some (v,x0) need not sit in any rotor core (no second middle m with deg_F=deg_A=5 is implied), so a non-scope-vacuous circuit does not produce a balanced rotor. "Equivalently" should be "in particular" (or the vacuity question restricted to rotor-core middles). The subsequent sentence ("a negative answer ... would refute the rotor route") survives because such a falsifier refutes the *strategy*, but the displayed equivalence is unproved and presumably false. |
| 23 | closing honesty statement | **CONFIRMED** — no bound on bip(G) claimed; scope of the results correctly limited to one local strategy; no Lean status claimed anywhere (grep-verified). |

Manifest exclusion list: verified against the .tex — none of the excluded
claims (n<=20 live bound, per-owner exhaustiveness, clustering pattern claim,
#298 extension as proposition, separators/k=3/t=6/probabilities, Lean) appear
in the section.

## Issues, ranked

**I1 (verification infrastructure, most consequential operationally).** Every
JSON artifact cited by SHA-256 prefix in the section (nine+three split
certificates, both hit payloads, both scope UNSATs, the tail blanket, the
extension master/replay) has been deleted from the repository (`tmp/` was
cleaned; a full-tree search finds none). Only the ledger lines, the gate
headers, and the archived scripts remain. The scripts are intact — I confirmed
`verify_t5_local_classifier_hit.py` hashes to 017d1e44 today, matching the
R49 gate header — and the cheap verdicts replay from scratch (done this
session), but the specific hashed payloads (in particular the recorded
25-atom sets A for #298/#264 and the extension certificates of claims 17/18)
are no longer reproducible as cited. Before arXiv submission the artifact set
should be regenerated and archived next to the scripts, or the SHA prefixes
dropped in favour of "replayed from source, this paper's ancillary files".

**I2 (mathematical, most serious in-text).** Claim 22's "Equivalently" — see
table. One-word fix.

**I3 (bookkeeping).** Artifact attribution for `prop:hits`/#298 is garbled:
48ce1638 is the *verification* (replay) artifact, the *primary* hit artifact
is c1d474d7 (uncited), and 017d1e44 is the SHA of the verifier *script*, not
a replay output. The .tex/table present 48ce1638 as the primary and 017d1e44
as "replay". Same pattern for #264: d9e73413 is the verification artifact
(primary 6595501f uncited). Also, the text says the all-row check ran "twice
per circuit" but cites only one prefix for #264 (CP-SAT prefix 79471ef0
exists in the archive REPORT). All easily fixed from
`archive/.../REPORT.md`.

**I4 (unmanifested prose claim).** "the graphs G_t themselves are not support
circuits for t>=4: their violation has defect far exceeding one, and their
minimal subsystems are always the nine-atom circuit" — companion-paper claim,
not in the manifest, no \ref, and "always" is strong. Cite the companion
result or soften.

**I5 (LaTeX, minor).** Static audit passes: all environments balanced, all
\ref targets defined in-file, no duplicate labels, braces/math delimiters
balanced (the apparent \[ surplus is the \\[2pt] row separator), underscores
properly escaped in all \texttt{} literals. But the header comment lists only
"amsthm environments ..., booktabs, enumitem" as assumed preamble; the section
also uses \operatorname/\tfrac/\Bigl (amsmath) and \texorpdfstring
(hyperref). Both are surely in the companion preamble, but the comment should
say so. No compiler available on this machine; verified by static audit plus
the drafter's wrapper preamble, which covers every control sequence used.

## Verdict

All mathematics presented as proved is proved (items 1-12, 14, 16 checked
line-by-line; several finite inputs re-verified computationally). All
computer-assisted claims match their sources exactly, are honestly labelled
(single-solver vs dual-verified, bounded vs exact), and the two cheap
certificate families were replayed from scratch successfully; prop:hits was
re-derived with an independent encoding. The one mathematical defect is the
overclaimed equivalence in the open question (I2); the one systemic defect is
the deleted artifact set behind the cited SHAs (I1).
