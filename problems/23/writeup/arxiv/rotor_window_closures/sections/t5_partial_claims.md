# Claims manifest — section `t5_partial.tex`

Section: "Partial results at twenty-five atoms, and two certified near-misses"
(rotor_window_closures). Every numbered claim of the section is listed with
its verification status and exact sources. Statuses used: **proved** (full
proof included in the section), **computer-assisted** (verifier script +
artifact SHA-256 prefix; dual verification noted where present). No claim in
this section is Lean-verified; none is presented as such.

Source archive files (all under `E:\Projects\ErdosProblems`):

- `problems/23/writeup/WALL_ATTACK_R47_GPTPRO56.md` (R47)
- `problems/23/writeup/WALL_ATTACK_R48_GPTPRO56.md` (R48)
- `problems/23/writeup/WALL_ATTACK_R49_GPTPRO56.md` (R49)
- `problems/23/writeup/WALL_ATTACK_R50_GPTPRO56.md` (R50)
- `LOOP_STATE.md` (TICK-108/109/110)
- `PROGRESS.md` (ledger lines of 2026-07-12, esp. the GATE-T5BATCH replay
  line 2998, ENGINE reconciliation line 2994, SOLO-SWEEP lines 3001-3005)
- engine/verifier scripts archived under
  `problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/`
  (`rooted_t5_support_cp_sat.py`, `verify_t5_local_classifier_hit.py`,
  `verify_t5_active_scope_unsat.py`, `verify_t5_tail_blanket_unsat.py`,
  `extend_t5_hit_maxcut.py`, `verify_t5_maxcut_extension_unsat.py`,
  `REPLAY.md`)

Additionally, the graph-level facts printed about the two graph6 strings
(order/size/classes/degrees/core/d(2,3)=4/distance-4 supply 32 and 30, the
neighbourhoods N(17)={0,1} in #298, N(9)={0,1,2} in #264, N(0)=N(1) in #298,
and the #264 coverage-row facts (f1)/(f2) with witness counts 3/3/3/1) were
re-verified for this draft by fresh exact scripts (session scratchpad
`check_hits.py`, `verify_circuits.py`; NetworkX, integer arithmetic only).

---

## Definitions (no verification burden)

- Def. `def:t5circuit` (support circuit at parameter t) — restates the
  engine's circuit axioms ("24 edges, 25 atoms, tri-free, union,
  deletion-SDRs", R50 sec. 7-8 / R48 sec. 7) in the companion paper's
  footprint language; equivalence with inclusion-minimal Hall violations is
  Hall's theorem (one line, given in text).
- Def. `def:selection`, `def:owner`, `def:live`, `def:rotor` — clean-language
  renderings of: selection/selected/latent (R50 sec. 1-2), the
  T5LocalOwnerProfile conditions (R48 sec. 1-4), active-scope capture
  (R49 sec. 6, R50 sec. 3), and the live middle-swap rotor core
  (`rooted_t5_support_cp_sat.py` docstring + model). The section states
  explicitly that the programme's full rotor object carries more structure
  and that all exclusions apply to the weaker package.

## Numbered claims

1. **Lemma `lem:tight` (tightness/sharpness, r=5 iff Forced=Inc)** —
   status: **proved** (proof in section; elementary).
   Source: R48 sec. 1-4 ("forced-through sharpness", gate header item (1)).

2. **Lemma `lem:positions` (rows of atoms at v avoid x0; selected rows
   through x0 avoid v)** — status: **proved** (proof in section; geodesic
   position argument). Source: R50 sec. 1-2 ("no incident row contains x0
   [co-occurrence]").

3. **Lemma `lem:steps` (step surjection, multiplicities (2,1,1,1))** —
   status: **proved** (proof in section; pigeonhole).
   Source: R48 sec. 1-4 (gate header item (2), "multiplicities forced
   (2,1,1,1)").

4. **Lemma `lem:parity` (one owner-avoiding row covers at most one star
   pair)** — status: **proved** (full parity proof in section).
   Source: R48 gate header item (3) (parity argument reproduced).

5. **Corollary `cor:coverage` (four distinct covering atoms; four
   independent 4-cycles; cycle rank >= 4; |V(F)| <= 21)** — status:
   **proved** (proof in section). Source: R48 sec. 5-6 ("cycle rank exactly
   4 ... |V| <= 21").

6. **Lemma `lem:trichotomy` (endpoint trichotomy for covering rows)** —
   status: **proved** (proof in section). Source: R49 sec. 1-2 (Type 0/1/2
   trichotomy; the section merges Types 0 and 2 into case II since only
   endpoint counts are needed).

7. **Theorem `thm:order15` (order >= 15; window 15..21)** — status:
   **proved** (full proof in section: base-11 count, trichotomy case
   analysis, Mantel with extremal uniqueness). Source: R49 sec. 3
   ("ORDER-14 CLOSED (range 15-21)"; endorsed in the R49 gate header as a
   ledger-quality lemma).

8. **Theorem `thm:selected` (|S_omega| >= 3t-1; |L_omega| <= t(t-3))** —
   status: **proved** (full proof in section). Source: R50 sec. 1-2
   ("PROVABLE: |S_omega| >= 3t-1 ... coverage adds >= 1 at x0").

9. **Corollary `cor:latent` (t=5: >=14 selected, <=10 latent, tail <= 9
   edges)** — status: **proved** (immediate). Source: R50 sec. 1-2.

10. **Remark `rem:t3` (no covered rotating owner at t=3; budgets 0/4/10 at
    t=3/4/5; mechanism weakens quadratically)** — status: **proved**
    (immediate from Theorem 8) + honesty note sourced from R50 sec. 9
    ("0/4/10/18/28 at t=3..7 — the scope mechanism WEAKENS quadratically").

11. **Remark (four-part realizability test / classifier equivalence)** —
    status: **proved** (both directions argued in section text; this is the
    paper-level rendering of R48's "profile iff four-number classifier
    (0,0,0,0)", gate-verified by inspection in R48's header).

12. **Lemma `lem:shores` (owner class >= 7, opposite class >= 5)** —
    status: **proved** (proof in section). Source:
    `rooted_t5_support_cp_sat.py` (root validation "left >= 7 and
    right >= 5") + TICK-109 note; the proof is independent and elementary.

13. **Proposition `prop:orders1516` (orders 15 and 16: all shore splits of
    the rotor support relaxation (R1)-(R7) infeasible; rotor support order
    >= 17)** — status: **computer-assisted, single verifier** (flagged in
    text). Verifier: `rooted_t5_support_cp_sat.py` (OR-Tools CP-SAT, exact
    Boolean model; INFEASIBLE = completed proof). Artifacts (canonical
    SHA-256 prefixes, from PROGRESS.md lines 3001-3004 and LOOP_STATE
    TICK-109/110): order 15 splits (7,8)/(8,7)/(9,6)/(10,5) =
    14ac9d93 / 8d194613 / 66e0813c / 5721cbc5; order 16 splits
    (7,9)/(8,8)/(9,7)/(10,6)/(11,5) = 8dff49ea / bd0c0320 / cc5462d6 /
    b5037e11 / 9f9401d0. No independent replay exists for these nine; the
    section says so.

14. **Printed graph6 facts for #298 and #264 (18 vertices, 24 edges, 9+9
    classes, deg(v)=deg(m)=5, rotor core, d(a,b)=4, distance-4 supply
    32/30)** — status: **proved/reader-checkable** (finite facts about the
    printed strings; re-verified this session with fresh exact scripts).
    Sources: R49 gate header (#298 graph6), R50 gate header (#264 graph6).

15. **Proposition `prop:hits` (existence of the two 25-atom triangle-free
    circuits with covered rotating owners; #298 at (v,x0)=(0,17), #264 at
    (0,9) with active edge = core edge vx)** — status: **computer-assisted,
    dual-verified** (primary CP-SAT construction + independent exact
    NetworkX/matching replay `verify_t5_local_classifier_hit.py`).
    Artifacts: #298 hit 48ce1638, replay 017d1e44 (R49 gate header);
    #264 hit d9e73413 (PROGRESS.md line 2998 replay batch; R50 gate
    header). Near-miss framing (falsifies the purely-local closure route,
    i.e. the former conjecture "profile forces a bad triangle") sourced to
    R49 gate header (falsification event) — stated in the section as a
    negative structural datum, not as a live lemma.

16. **Proposition `prop:dead` (every realization of the recorded profile in
    either circuit leaves the owner dead)** — status: **proved** in the
    section, MODULO two finite row-database facts for #264 ((f1): every
    star-pair covering row avoiding v uses edge {1,9}, witness counts
    3/3/3/1; (f2): unique covering row (15,2,9,1,17) for {9,15}, using
    {2,9}). For #298 the proof needs only deg(17)=2, read off the printed
    string. Facts (f1)/(f2): **computer-assisted, dual-verified** —
    engine per-edge UNSATs + SAT replay `verify_t5_tail_blanket_unsat.py`
    artifact 3720a8c2 (R50 gate header, PROGRESS.md 2998), independently
    re-verified this session by exhaustive geodesic enumeration
    (scratchpad `verify_circuits.py`). The #298 owner-swap symmetry
    N(0)=N(1) is a printed-string fact.

17. **All-row dead-owner certificates (monolithic "no atom has both
    endpoints in the owner's latent component" over all admissible
    selections)** — status: **computer-assisted, dual-verified** (CP-SAT
    infeasibility + independent CaDiCaL replay via PySAT,
    `verify_t5_active_scope_unsat.py`). Artifacts: #298 f5c0cbca (CP-SAT) +
    a8a160d5 (CaDiCaL; 1680 variables / 5239 clauses) — R49 gate header;
    #264 c7fbcc70 — PROGRESS.md line 2998. The section states explicitly
    that these are *intrinsic* certificates (fixed circuit row database),
    per the R50 gate header scope qualifier.

18. **Proposition `prop:extension` (#264 ambient exclusion: no triangle-free
    row-preserving maximum-cut extension on <= 25 vertices; all eight
    class-assignments infeasible; explicit switch obstruction
    S={4,5,6,7,8,11,14,16}, 23 atom crossings vs 2 support crossings,
    demand 21 vs capacities 21,19,...,7, joint kill 42 > 28)** — status:
    **computer-assisted, dual-verified** (primary
    `extend_t5_hit_maxcut.py` with exact lazy switch separation +
    independent SAT replay `verify_t5_maxcut_extension_unsat.py`;
    replayed PASS in the PROGRESS.md line 2998 batch; switch data from the
    R50 gate header; the model scope — "all missing cross-shore blue edges,
    connectivity omitted, hence every <= 25-vertex extension" — from
    REPLAY.md in the script archive). The 2 support crossings of S were
    re-verified this session; the 23 atom crossings depend on the selected
    atom set and carry artifact status. No SHA prefix for the two extension
    artifacts is recorded in the named sources; the section cites the
    scripts and the replay verdict instead.

19. **Proposition `prop:298extension` (#298 ambient exclusion, 8
    assignments; PROMOTED 2026-07-17 from the former remark
    `rem:298maxcut`)** — status: **computer-assisted, dual-verified**.
    The #298 circuit was rebuilt on the pinned printed graph at (v,x0) =
    (0,17) (`rebuild_t5_local_classifier_hit.py`, canonical ff1c1209...,
    independent verifier PASS); the primary extension run
    (`extend_t5_hit_maxcut.py`, canonical 2bf166b7...) returned all eight
    splits INFEASIBLE (completed proofs), and the independent CaDiCaL
    replay (`verify_t5_maxcut_extension_unsat.py`, canonical d176ce66...)
    returned PASS_ALL_EIGHT_SPLITS_UNSAT. Chain shipped in
    `anc/t5_artifacts/298_extension/`. The explicit switch
    S={4,5,6,7,8,12,14,15,16} is crossed by 24/25 atoms vs 4 support
    edges (sigma = -20, matching the historical R49 record); unlike #264
    the demand alone kills no assignment (infeasibility joint with the
    row-preservation clauses and, at k in {0,1}, a second switch).
    Caveat: the certified 25-atom set is the regenerated witness on the
    pinned graph (the original c1d474d7 payload was deleted);
    `prop:dead`'s #298 argument is atom-set-independent and unaffected.

20. **Proposition `prop:order17` (order 17: splits (7,10),(8,9),(12,5)
    infeasible; (9,8),(10,7),(11,6) feasible)** — status:
    **computer-assisted, single verifier** (same model as claim 13).
    Artifacts: 4d450ca0 / f76b9d64 / 325012ec (infeasible splits; PROGRESS
    line 3005 lists the three SHAs for the three splits without an explicit
    per-split mapping, and the section does not assert one); feasible-split
    staged no-hit runs 95dbc901 / d612c59e / 31d82c62 (3000 supports each)
    — presented in the section as *bounded searches, not proofs*.
    Source: LOOP_STATE TICK-110 + PROGRESS line 3005.

21. **Bounded order-18 statement ("first 350 supports at split (9,9)
    rejected at the live-owner gate")** — status: bounded search, explicitly
    non-probative in the text. Source: R49 gate header ("first 350
    no-shared 9+9 supports ALL rejected at active scope (bounded)").

22. **Open question (scope-vacuity of all 25-atom circuits / nonexistence of
    balanced rotors at t=5)** — status: **open, stated as a question**, with
    both possible outcomes described and the honest caveat that a positive
    answer is one more finite base case (R50 sec. 9). This is the archives'
    live lemma `t5_triangleFree_localProfile_is_scopeVacuous`
    (R49/R50 gate headers), which is UNPROVEN — the section never asserts
    it.

23. **Closing honesty statement** — the section's results constrain one
    local proof strategy and produce no bound on bip(G); nothing resolves
    the Erdos n^2/25 conjecture. (Frame mandated by the task; consistent
    with all sources.)

## Claims EXCLUDED from the section (and why)

- The improved order bound "n <= 20 for live owners (capture => rank >= t
  => n <= t^2-t)" (PROGRESS line 3018, fiber agent) — outside the named
  source set for this section; excluded.
- Any per-owner exhaustiveness claim for the intrinsic certificates beyond
  the recorded (owner, active) pairs — the archived UNSATs fix the recorded
  pair; #298's mirror profile is covered in-text only via the proved
  N(0)=N(1) automorphism.
- The R49 sec. 4 claim that "clustering + Mantel cannot close 15-21"
  (abstract endpoint pattern) — not individually endorsed by the gate
  header; only a soft methodological sentence retained, no mathematical
  claim.
- The #298 eight-assignment extension UNSAT as a *proposition* — recorded
  (PROGRESS 2994) but not independently replayed; demoted to a remark with
  the caveat spelled out (claim 19).
- "Two-owner doubling adds nothing", relaxation-ladder material, k=3
  variants, t=6 window claims, separator-certificate machinery
  (T5ForcedTailSeparator), and all probability estimates from R47-R51 —
  either not needed, engine-internal, or not gate-endorsed as theorems;
  excluded.
- The R46 18-vertex "near-candidate" (30 atom triangles, scope-vacuous) —
  superseded by the two genuine hits; excluded to keep the section tight.
