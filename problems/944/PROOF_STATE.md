# (appended 2026-06-10 ~14:20) Consult-1 digest (chat "Erdos Dirac Graph Conjecture" c/6a294081)
PENDING claims to verify:
- [P1] Cut Lemma: 4-vertex-critical G, vertex partition with cut size ≤5 ⟹ some cut edge critical.
  (Random S3-permutation of one side's 3-coloring: E[mono]=cut/3<2; 0 impossible ⟹ some π gives exactly 1
  ⟹ that edge critical.) RE-DERIVED, looks sound ⟹ near-T1; NOVELTY CHECK vs SkSt25 needed (they ask the
  6-regular question explicitly ⟹ δ≥6 corollary likely known there — verify before any claim).
- [P2] Corollaries: any (4,1)-target is 6-edge-connected; δ≥6; star of any degree-≤5 vertex contains a
  critical edge (explains SA floor at small n); n ≥ 11 (with Δ ≤ n−5 claim — verify that step); n=11 ⟹
  6-regular, 33 edges (SkSt25's explicit open subquestion).
- [P3] Jensen anatomy: circulant construction; k≥5 needed for nonempty long-distance intervals (+ forced
  periodicity wrap argument); k=4 specialization degenerates. (Citation-level; verify from SkSt25/Jensen.)
- [P4] Candidate: Schrijver SG(2q+2,q) (n=(q+1)²=25,36,49; 4-chromatic vertex-critical) as H-seeds +
  dihedral-orbit extra edges S (δ≥6, kill edge-criticality); α(G−e)≤⌈n/3⌉−1 certificate for non-3-col.
  Edge-transitive families of degree ≤5 ruled out by P1.
Next iterations: (1) verify P1/P2 + check stuck-graph δ in data; (2) build SG(10,4)+orbit-S search;
(3) SMS exhaustive n=11 6-regular (lower-bound product); (4) fetch SkSt25 full text (lemma novelty + their
exact open subquestions). Budgets: iter 5/40, consults 1/12.

# (2026-06-10 ~22:00) Deep-math consult result: RIGIDITY PACKAGE (Direction B)
- [VERIFIED T1] Lemma 1.1 (singleton color class in N(v) under any 3-coloring of G-v => that edge critical;
  re-derived independently). Corollary: targets need every color class >=2 in every neighborhood => delta>=6
  (local form of SkSt25 Prop 5.1, cited honestly).
- [VERIFIED T1] Corollary 1.3 (NEW-looking): c(G) >= (1/2) sum_v max(0, 6-d(v)) critical edges.
- [VERIFIED T1] Lemma 3.1 cut-matrix form; D_pi >= 2 for all pi in targets; |F| >= 6.
- [VERIFIED T0/T1 ★] Theorem 4.3 (NEW-looking): exact 6-cut obstruction — cut matrix must be one of FIVE
  types (row sums (6,0,0),(3,3,0),(4,1,1),(2,2,2)); MACHINE-VERIFIED: exhaustive over all 3x3 sum-6
  matrices: exactly 21 satisfy all-diagonals>=2, exactly 5 canonical types, matching GPT statement 1:1.
- [PENDING] Property A (every edge of 6-regular target in <=4 triangles); Property B (Kempe tethers);
  Property C consequences (no 6-cut shore of size 2..7; size-8 shore forced = K_{3,3,2}; 6-regular target
  super-6-edge-connected or atoms >= K_{3,3,2}). Verify next (incl. test against unique n=13 graph).
- Unique n=13 6-regular 4-vertex-critical graph: critical edges form a HAMILTON CYCLE (13 edges, verified).
- NEXT: (1) read weakest-steps; (2) machine-verify A/B/C on n=13 unique graph; (3) novelty sweep on the
  rigidity package; (4) decision: publishable SECONDARY package (rigidity theorems + n<=13 exhaustion +
  unique graph) vs continue to n=14 with theoretical pruning.

# (2026-06-10 ~22:30) Lean cores repaired and compiled
- `E:\Projects\ErdosProblems\formal-conjectures\erdos944_cores.lean` now compiles with
  `lake env lean erdos944_cores.lean` (clean log: `lean_compile_clean.log`).
- No `sorry`/`admit`/`axiom`/`unsafe` tokens in the file.
- T2 cores currently covered:
  (1) `singleton_edge_critical`, the recolouring core of Lemma 1.1;
  (2) cut-matrix count/membership support (`cut_matrix_classification`,
      `matrix_mem_classification`) for the 6-cut obstruction, with canonical five-type
      reduction still recorded as external exhaustive Python/C++ certificate;
  (3) `turan_count_shore`, the numeric shore bound for sizes 2..7.
- Axiom check sample:
  `singleton_edge_critical` does not depend on any axioms;
  `turan_count_shore` depends only on `[propext, Classical.choice, Quot.sound]`.
  Need rerun/record full axiom print for cut-matrix names after module import path is packaged or by
  temporary in-file `#print` if desired.

# (2026-06-10 ~23:00) GPT-5.5 Pro Property-B answer received and independently re-derived
- GPT correction: the earlier "small shore size 8 may be a K_{3,3,2} atom" endpoint is too weak.
  In a 6-regular 4-vertex-critical graph such a shore is actually impossible, because the two vertices
  in the size-2 part of `K_{3,3,2}` have internal degree 6, no external neighbours, and are non-adjacent
  twins. Non-adjacent twins contradict vertex-criticality.
- [VERIFIED T1] Local multiplicity lemma restated cleanly:
  In any 3-colouring of `G-v`, each colour appears at least once in `N(v)`; if a colour appears exactly
  once, say only at `u`, then `G-uv` is 3-colourable by colouring `v` with that singleton colour.
  Hence every target has no singleton colour class in any `N(v)` under any 3-colouring of `G-v`;
  in the 6-regular case the three colour multiplicities are exactly `(2,2,2)`.
- [VERIFIED T1] Property A / triangle bound:
  In a 6-regular target, no edge `uv` can satisfy `N(u) \ {v} subset N(v)`. In particular every edge
  lies in at most four triangles. If `uv` had five common neighbours, then in any 3-colouring of `G-u`
  the colour of `v` appears exactly once in `N(u)`, forcing `uv` critical by the local multiplicity
  lemma.
- [VERIFIED T1] Exact 6-cut conflict count:
  For a nontrivial partition with both shores proper, a cut `F` of size 6, and fixed 3-colourings of both
  shores, every permutation of the colours on one shore has exactly two monochromatic cut edges.
  Each shore is 3-colourable by deleting a vertex on the other shore and restricting. Then zero conflicts
  would 3-colour `G`, one conflict would make that one edge critical, and the sum over the six colour
  permutations is `2|F| = 12`.
- [VERIFIED T1] Property B / corrected Kempe tether:
  Let a 6-cut gluing permutation have exactly two conflict edges `{e,f}`. If `e = xy` has conflict
  colour `a`, then for every `b != a`, the endpoints `x,y` lie in the same `(a,b)`-Kempe component of
  `G - {e,f}`. Otherwise swapping colours `a,b` in the component of `x` removes the conflict on `e`
  while `f` is deleted, giving a 3-colouring of `G-f`, contradiction.
  Important scope: this is a global tether through `G-{e,f}`, not a purely internal-shore connectivity
  statement. Any later shore-local use must pass through a separate first-cut-crossing argument.
- [VERIFIED T1] Small 6-cut shore exclusion:
  If `G` is 6-regular and `|delta(S)| = 6`, then `e(G[S]) = 3|S|-3`. Since `S` is a proper induced
  subgraph, choose `v notin S`; `G-v` is 3-colourable and `G[S] subset G-v`, so `G[S]` is 3-colourable.
  Thus `e(G[S]) <= floor(|S|^2/3)`.
  This excludes `2 <= |S| <= 7`. For `|S|=8`, equality forces `G[S] = K_{3,3,2}`, and the size-2
  part gives non-adjacent twins of full degree 6, contradicting vertex-criticality. Therefore no
  6-edge-cut shore has size `2..8`.
- [GPT RED-TEAM PASSED WITH WORDING CORRECTIONS] Cold adversarial audit on 2026-06-10 found no mathematical
  counterexample to claims 1-5, but required: fixed 3-colour palette wording; nontrivial/proper shores for the
  cut lemma; Kempe tether only in global `G-{e,f}`; monotonicity proof for `G[S]` 3-colourability.
  Digest: `problems/944/gpt_redteam_2026-06-10.md`.
- [PENDING before publication] Put the corrected package into final write-up, run final novelty sweep, and decide
  which pieces should be Lean-formalized beyond the existing cores.

# (2026-06-10 late) Session continuation: Lean cores + Property A/B/C verification COMPLETE
- LEAN CORES COMPILED CLEAN (erdos944_cores.lean, exit 0, axioms verified):
  * singleton_edge_critical (Lemma 1.1 core): NO axioms at all (fully constructive).
  * cut_matrix_classification (Thm 4.3 count=21 via comps 9 6 enumeration, 3003 weak compositions
    + mem_comps completeness lemma): [propext] only. 7^9 decide replaced by composition encoding.
  * matrix_mem_classification (matrix-form bridge, Equiv.Perm instantiation at 6 explicit perms),
    mem_comps, turan_count_shore: [propext, Classical.choice, Quot.sound]. No sorry, no native_decide.
- PROPERTY B (Kempe tethers) = Lemma 2.1 + Cor 2.2 of GPT Direction-B reply: READ IN FULL, VERIFIED
  line-by-line (swap on mate-component, x' leaves colour 1, no new colour-1 boundary by assumption,
  v gets colour 1 in G-vx => vx critical; boundary patterns (2,2) or (1,1)+(1,1)). T1.
- PROPERTY A VERIFIED: 2+2+2 split (Cor 1.2 + 6-regular) => same-colour pairs are complement edges
  => perfect matching in complement of G[N(v)] => every edge in <=4 triangles. T1.
- PROPERTY C VERIFIED: Thm 5.1 (shores 2..7 impossible) + Thm 5.2 (8-shore => K_{3,3,2}, double
  equality: e(G[A])=21=Turan bound, all degrees exactly 6, part-2 no cut edge, part-3 one each) +
  Thm 5.3 (double-rainbow: unique K_{3,3,2}-colouring => boundary (3,3,0) => only type II) +
  dichotomy (super-6-edge-connected OR atoms >=8 with smallest exactly K_{3,3,2}). T1.
- Lemma 4.1/4.2 alt derivation VERIFIED: D_pi=2 forall pi => 2x2 additive condition => m_ij=(R_i+C_j-2)/3
  => row/col sums congruent mod 3 => row sums in {(6,0,0),(3,3,0),(4,1,1),(2,2,2)} => five types
  I..V with orbit sizes 3+3+9+3+3 = 21 = Lean count. Analytic + machine agreement.
- MACHINE TESTS (new):
  * verify_lemma21_n13.py: unique n=13 graph: 78 vertex-deleted colourings, ZERO of type 2+2+2
    (graph is everywhere-singleton!); 156 Lemma-1.1 predictions, 0 false positives, 13/13 critical
    edges covered. Kempe mechanism vacuous on n=13 (no 2+2+2 colourings) - notable rigidity datapoint.
  * test_lemma21_random.py: Lemma 2.1 as standalone implication stress-tested on random 4-chromatic
    graphs: 19389 tether-failure implications across 451 graphs, 0 counterexamples.
- PRs: deepmind #4218 all CI green (Build+CLA), no human review yet; teorth #313 open, no comments.
- NEXT: cold-context red-team (new GPT thread) -> writeup -> publish (teorth problems.yaml #944
  comment PR + optional formal-conjectures 944.lean).

# (2026-06-11 ~00:10) Verified n=14 closure and 9-shore exclusion
- [VERIFIED NUMERICALLY, DOUBLE CHUNK CHECK] The 6-regular n=14 enumeration is closed:
  two independent native chunk partitions give the same totals.
  * `experiments/sixreg/n14_chunks` (110 residue classes):
    `total=21609301 threecol=42667 notVC=21566634 vcWithCritEdge=0 TARGET=0 badline=0`.
  * `experiments/sixreg/n14_chunks_v2` (73 residue classes):
    `total=21609301 threecol=42667 notVC=21566634 vcWithCritEdge=0 TARGET=0 badline=0`.
  Thus there is no 6-regular 4-vertex-critical graph on 14 vertices at all, hence no
  6-regular `(4,1)` target on `n <= 14`. The redundant live stream rerun
  (`smsg`/`check_stream_mt`) was stopped after this verification.
- [VERIFIED NUMERICALLY + T1 local argument] No 9-vertex shore of a nontrivial
  6-edge-cut can occur in a 6-regular `(4,1)` target.
  * Candidate setup: a 9-shore `A` has `e(G[A]) = 24`, `Delta(G[A]) <= 6`, and
    deficiency vector `b(v) = 6 - deg_A(v)` with total 6.
  * Exhaustive nauty/C++ filter:
    `geng -c -D6 9 24:24 | enum_9shore.exe` classifies 729 connected candidates:
    `711` not 3-colourable, `9` violate the 6-cut boundary-vector condition, `8`
    have a comparable non-neighbour at a `b=0` vertex, and exactly one survives:
    graph6 `HEzftz{`, `b=011101110`, `ncol=6`.
  * Independent Python recount (`verify_9shore_survivor.py`) reproduces the same
    `711/9/8/1` classification and prints the survivor edge list.
  * Kill test (`kill_9shore_survivor.py`): the survivor has internal vertices
    `{0,4,8}`. For each such vertex `v`, all 6 proper 3-colourings of `H-v`
    leave some colour appearing at most once on `N_H(v) = N_G(v)`, contradicting
    the local multiplicity lemma. Hence the survivor cannot embed as a 9-shore.
  Conclusion: in a 6-regular `(4,1)` target every nontrivial 6-edge-cut shore has
  size at least 10, and therefore any such graph on `n <= 19` is
  super-6-edge-connected (only vertex-star 6-cuts).
- Scope warning: the 9-shore exclusion uses 6-regularity (`b(v)=6-deg_A(v)` and
  internal vertices with `N_G(v)=N_A(v)`). Do not state it for general
  `delta >= 6` targets without a separate argument.

# (2026-06-11 ~00:25) 10-shore exclusion COMPLETE
- [VERIFIED NUMERICALLY, independent C++ + Python] No 10-vertex shore of a
  nontrivial 6-edge-cut can occur in a 6-regular `(4,1)` target.
  * Candidate setup: a 10-shore `A` is connected (otherwise some component has
    boundary at most 5, contradicting the known cut lower bound), has
    `e(G[A]) = 27`, `Delta(G[A]) <= 6`, and deficiency
    `b(v) = 6 - deg_A(v)` with total 6.
  * C++ filter:
    `geng -c -D6 10 27:27 | enum_10shore.exe` classifies 18,655 connected
    candidates:
    `total=18655 badDeficiency=0 not3col=18345 badBoundaryVec=197
    comparableNonNbr=86 localMultiplicityKill=27 SURVIVORS=0`.
  * Independent Python recount (`verify_10shore.py`) on the same nauty stream
    reproduces the classification:
    `{'badvec': 197, 'badcomp': 86, 'not3col': 18345, 'badlocal': 27}` and
    `survivors: []`.
  * Filters are the same verified necessary conditions as the 9-shore run:
    6-cut row-sum boundary vectors for every proper 3-colouring, comparable
    non-neighbour obstruction at `b=0` vertices, and local multiplicity kill
    at `b=0` vertices.
  Conclusion: in a 6-regular `(4,1)` target every nontrivial 6-edge-cut shore
  has size at least 11; therefore any such graph on `n <= 21` is
  super-6-edge-connected.
- Scope warning remains: the 9/10-shore finite exclusions use 6-regularity and
  the fixed deficiency formula `b(v)=6-deg_A(v)`.

# (2026-06-11 ~00:20) SHORE-EXCLUSION MACHINE: 9,10,11,12 ALL EXCLUDED (a=13 running)
- Native pipeline (user directive: no WSL): geng.exe (nauty 2.8.9, clang-built, validated
  vs SMS chain exactly) + enum_shore.cpp filter battery, all NECESSARY conditions:
  [B] b(v)=6-deg in [0,5]; [C] 3-colourable + EVERY colouring's deficiency-weighted
  boundary vector in {(6,0,0),(3,3,0),(4,1,1),(2,2,2)} (T4.3 row sums, beta-independent);
  [T] folklore comparable-nonneighbours at b=0 vertices; [K] GENERALIZED local kill:
  for every v, exists proper colouring of H-v with sum_i max(0,2-cnt_{N_A(v)}(i)) <= b(v)
  (necessity: chi(G-v)=3 colouring needs every colour >=2 on N_G(v) by Lemma 1.1+target,
  cut neighbours supply at most b(v)).
- G[A] connected forced (any component would use all 6 cut edges; a second component
  disconnects G). e(G[A]) = 3a-3 exact (6-regular).
- RESULTS (native C++; a=9,10 also independently verified in Python):
  a=9:  729 cands: 711 not3col, 9 badvec, 8 twins, 1 localKill (H=K333-rainbow-matching,
        g6 HEzftz{, killed: all 6 colourings of H-v leave a colour <=1 on N(v), v in
        {0,4,8}; ALSO 3^8 brute-force confirmed) => 0 SURVIVORS.
  a=10: 18,655: 18,345/197/86/27 => 0 SURVIVORS.
  a=11: 696,208: 687,377/6,013/1,300/1,518 => 0 SURVIVORS.
  a=12: 32,833,744 (110 chunks): 32,484,081/241,863/27,322/80,478 => 0 SURVIVORS.
- THEOREM (current): every nontrivial 6-edge-cut shore in a 6-regular (4,1)-graph has
  >= 13 vertices => every 6-regular target on n <= 25 is super-6-edge-connected.
  (a=13, e=36, ~1.5e9 cands estimated, 110 chunks RUNNING -> would give shores>=14, n<=27.)
- n=14 SLICE CLOSED DOUBLE-VERIFIED (mod-110 + mod-73 identical): 21,609,301 graphs
  (= published count), 0 six-regular 4-VC at n=14 => Problem 5.2 needs n >= 15.

# (2026-06-11 ~00:50) Shore-exclusion audit: 9..14 ALL EXCLUDED
- [VERIFIED NUMERICALLY] The generalized shore filter has complete 110-chunk
  coverage for `a = 12, 13, 14`; each chunk has a well-formed summary, no
  missing `.out`/`.err` files, and no nonempty `.err` files.
- Aggregate results:
  * `a=9`: `total=729 badDeficiency=0 not3col=711 badBoundaryVec=9 comparableNonNbr=8 localKill=1 SURVIVORS=0`
    (`shore9_certs.txt`; independently checked by the earlier Python recount/kill scripts).
  * `a=10`: `total=18655 badDeficiency=0 not3col=18345 badBoundaryVec=197 comparableNonNbr=86 localKill=27 SURVIVORS=0`
    (`shore10_certs.txt`; independently checked by `verify_10shore.py`).
  * `a=11`: `total=696208 badDeficiency=0 not3col=687377 badBoundaryVec=6013 comparableNonNbr=1300 localKill=1518 SURVIVORS=0`
    (`shore11.out`; independent Python full recount `shore11_py.out` matches).
  * `a=12`: `total=32833744 not3col=32484081 badBoundaryVec=241863 comparableNonNbr=27322 localKill=80478 SURVIVORS=0`
    (`shore12_chunks`, 110/110 chunks).
  * `a=13`: `total=1839349287 not3col=1822133664 badBoundaryVec=11944366 comparableNonNbr=788481 localKill=4482776 SURVIVORS=0`
    (`shore13_chunks`, 110/110 chunks).
  * `a=14`: `total=154941621 not3col=115063872 badBoundaryVec=32712357 comparableNonNbr=1752943 localKill=5412449 SURVIVORS=0`
    (`shore14_chunks`, 110/110 chunks).
- [INDEPENDENT SAMPLE CHECKS] `verify_shore_indep.py` is an independent Python
  implementation of the full filter battery. Full Python recount is complete for
  `a=11`. For larger `a`, residue/sample comparisons were run:
  * `a=13`, residue `0/100000`: C++ and Python both give
    `total=13350 not3col=13313 badvec=20 badtwin=0 localKill=17 SURVIVORS=0`.
  * `a=14`, first 5000 graph6 lines: C++ and Python both give
    `total=5000 not3col=936 badvec=3589 badtwin=430 localKill=45 SURVIVORS=0`.
- Current theorem: in a 6-regular `(4,1)` target, every nontrivial 6-edge-cut
  shore has at least 15 vertices. Therefore every 6-regular target on
  `n <= 29` is super-6-edge-connected.
- Scope warning: this theorem depends on 6-regularity and on the generalized
  local-kill necessary condition using boundary deficiency `b(v)=6-deg_A(v)`.

# (2026-06-11) Strategy reset: no early PR; push toward full 6-regular resolution
- User instruction: do not rush another PR update. Treat the existing #944
  package as partial evidence, but keep publication secondary until either the
  6-regular Skottova-Steiner subproblem is completely resolved or a stronger
  frontier-moving result is fully verified.
- Current gap: finite exclusions (`n <= 14`, 6-cut shores `<= 14`) do not by
  themselves imply a general-n contradiction. A full proof needs a global
  structural lemma for a hypothetical 6-regular `(4,1)` target.
- Active GPT-5.5 Pro consult submitted in a fresh ChatGPT thread:
  ask for a rigorous route to prove nonexistence of 6-regular targets from the
  verified local multiplicity, triangle bound, 6-cut matrix/Kempe package, and
  no-small-shore theorem. Explicit candidate lemmas requested:
  (A) every target has a 6-edge-cut shore of size `<= 14`;
  (B) some vertex-deleted colouring must violate the forced `(2,2,2)` local
      multiplicity;
  (C) every minimal target contains a bounded reducible configuration.
- Verification policy for the answer: decompose any proposed proof into atomic
  claims; do not promote anything to VERIFIED until independently re-derived
  and, when checkable, tested by exact computation or Lean.

# (2026-06-11) Prover/Verifier agent triage + Kempe-balance diagnostic
- Subagent verifier warning: the present theorem does not force the existence
  of a nontrivial 6-cut. The unique 6-regular 4-vertex-critical graph on 13
  vertices has edge-connectivity 6 but no nontrivial 6-cuts, so any broad lemma
  "6-regular 4-critical + triangle bound => nontrivial 6-cut" is false.
- Subagent prover candidate direction: every `(4,1)` target is forced to be
  perfectly Kempe-balanced at every deleted vertex. More explicitly, for every
  vertex `v`, every 3-colouring of `G-v`, and every two-colour Kempe component
  in the `(a,b)` subgraph, the number of boundary neighbours of `v` coloured
  `a` should equal the number coloured `b`; otherwise swapping the component
  changes the `(2,2,2)` boundary counts and creates a critical edge.
- New verifier: `experiments/sixreg/kempe_balance.cpp`.
  It exactly measures edge-connectivity, nontrivial 6-cuts, triangle histogram,
  vertex-deleted 3-colouring neighbourhood patterns, and two-colour Kempe
  boundary component patterns.
- Run on `unique_6reg_4vc_n13.txt`:
  `experiments/sixreg/kempe_balance_n13.out`.
  Output:
  `edge_connectivity=6`, `nontrivial_6cuts=0`,
  `max_triangle_count=2`, `triangle_hist 0:13 1:13 2:13`,
  `deleted_colourings=78`, `local_222_colourings=0`,
  `colourings_with_singleton_neighbour_colour=78`,
  `edge_split_predictors=0`, `edge_split_false_positives=0`,
  `neighbour_size_patterns [1,1,4]=78`.
- Interpretation: the `n=13` graph fails the target condition purely locally
  (singleton neighbour colours in every deleted colouring), and is a guard
  against overclaiming small-cut existence. The next scalable proof target is
  not "force a 6-cut" in this broad class, but "perfect Kempe-balance is
  impossible in a 6-regular 4-vertex-critical no-critical-edge graph" or a
  bounded reducible configuration derived from that balance.
- [VERIFIED T1 candidate] Perfect Kempe-balance is necessary for any target:
  Fix `v` and a 3-colouring `phi` of `G-v`. Let `C` be a connected component of
  the `(a,b)`-coloured subgraph of `G-v`. Let `p` be the number of neighbours
  of `v` in `C` coloured `a`, and `q` the number coloured `b`. Swapping colours
  `a,b` on `C` gives another 3-colouring of `G-v`, changing the neighbour
  colour counts from `(2,2)` on `(a,b)` to `(2-p+q, 2-q+p)`. If `p != q`,
  the new colouring violates the local multiplicity lemma: one of the two
  counts is not 2, hence is either 0/1 or 3/4. Count 0 would colour `G`;
  count 1 would make the unique incident edge critical. Both are forbidden.
  Therefore every `(a,b)`-Kempe component has balanced boundary counts
  `p=q`. In the 6-regular case, each positive boundary component for a colour
  pair is therefore only of type `(1,1)` or `(2,2)`.
- [VERIFIED T1 candidate] Nonincident edge/Kempe split obstruction:
  Fix `v` and a 3-colouring `phi` of `G-v` with the forced `(2,2,2)`
  neighbourhood split. Let `e=xy` be an edge of `G-v` whose endpoints have
  colours `a,b`. In the `(a,b)`-subgraph of `(G-v)-e`, suppose some connected
  component contains both `a`-coloured neighbours of `v` and no `b`-coloured
  neighbour of `v` (or symmetrically both `b` and no `a`). Swapping colours
  `a,b` on that component gives a proper 3-colouring of `G-v-e` in which colour
  `a` is absent from `N(v)`. Colouring `v` with `a` yields a 3-colouring of
  `G-e`, so `e` is critical. Therefore a target forbids such a split for every
  `v`, every deleted-vertex colouring, and every nonincident edge `e`.
  This is stronger than perfect Kempe-balance because it constrains how
  balanced `(2,2)` Kempe components may break after deleting one edge.
  Scope caution: a weaker unbalance such as `(2,1)` after deleting `e` does
  not by itself prove that `e` is critical; the direct edge-critical conclusion
  currently only uses the `(2,0)`/`(0,2)` absence case.

# (2026-06-11) GPT Pro structural answer: K6 route, not A/B directly
- GPT Pro does not see a complete proof of A/B/C from current hypotheses. It
  rejects B as a useful intermediate: under vertex-criticality, "some
  vertex-deleted colouring violates `(2,2,2)`" is essentially the target
  contradiction translated into colouring language.
- [VERIFIED T1] Kempe component accounting lemma:
  Fix `v` and a 3-colouring of `G-v` with colour classes `A,B,C`, where each
  colour has exactly two neighbours of `v`. Let `K` range over the `(A,B)`
  Kempe components in `G-v`, and let `delta_G(K)` count edges from `K` to its
  complement in `G` (including edges to `v`). Since
  `e(A,B)+e(A,C)=6|A|-2`, `e(A,B)+e(B,C)=6|B|-2`, and
  `e(A,C)+e(B,C)=6|C|-2`, we get
  `e(A,B)=3(|A|+|B|-|C|)-1`. Also
  `6|K|=2e(K)+|delta_G(K)|`. Summing over `(A,B)` components gives
  `sum_K |delta_G(K)|/2 = 3|C|+1`, equivalently
  `sum_K |delta_G(K)| = 6|C|+2`.
  The same cyclic identities hold for `(A,C)` and `(B,C)`.
- [PENDING target lemma K6] Pro's recommended next lemma:
  in every 6-regular target, for some `v`, some 3-colouring of `G-v`, and some
  colour pair, there is a touched non-singleton two-colour Kempe component
  `K` with `|delta_G(K)| = 6`. This would force a nontrivial 6-edge cut, after
  which the existing shore exclusions become relevant. It is weaker than A and
  currently the smallest useful global target.
- [PENDING / weak step] Triple-Kempe pressure:
  assuming every touched non-singleton Kempe component has boundary at least 8
  should force, using all three colour-pair decompositions simultaneously, one
  of: a 6-cut, a comparable same-colour non-neighbour pair, or a bounded
  reducible atom. Pro explicitly marks this inference as the weak point; a
  single giant touched component can defeat one-pair averaging, so all three
  pair decompositions must be used.
- Verifier update: `experiments/sixreg/kempe_balance.cpp` now records
  `kempe_accounting_failures`, touched component boundary histograms, and
  `touched_non_singleton_delta6` counts. On the unique `n=13` graph:
  `kempe_accounting_failures=0`, `touched_kempe_components=0`,
  `touched_non_singleton_delta6=0`; the K6 test is vacuous there because
  `local_222_colourings=0`.
- [DERIVED inequality under not-K6, pending usefulness]
  For a fixed deleted vertex colouring and a colour pair `(A,B)`, let `m_AB`
  be the number of `(A,B)` Kempe components and let `t_AB` be the number of
  touched non-singleton `(A,B)` components. Edge-connectivity gives
  `|delta(K)| >= 6` for every nonempty proper component `K`; if K6 fails for
  this colouring then every touched non-singleton component has
  `|delta(K)| >= 8`. Combining with the accounting identity gives
  `3*m_AB + t_AB <= 3*|C| + 1`. Since balance forces the two `A`-neighbours
  and two `B`-neighbours of `v` to lie in either one `(2,2)` touched component
  or two `(1,1)` touched components, `t_AB` is `1` or `2`. Hence one pair
  alone only gives `m_AB <= |C|` (or `m_AB <= |C|-1` in the split case);
  no contradiction follows without combining all three colour pairs.

# (2026-06-11) K6 follow-up: accounting alone is insufficient
- Prover subagent conclusion: K6 is not derivable from Kempe accounting plus
  boundary balance alone. A local counter-model shape is consistent with these
  constraints: take a large 3-partite `H=G-v`, attach `v` to two vertices in
  each colour class, make touched vertices degree 5 in `H` and all others
  degree 6, and arrange all three two-colour graphs connected. Then every
  touched Kempe component is balanced `(2,2)` but has boundary
  `6*|opposite colour|+2`, far above 6.
- Sharp deficiency identity for a fixed colouring:
  for colour pair `ij` with opposite class size `n_k`, let `r_ij` be the
  number of `(i,j)` Kempe components. Then
  `sum_K (|delta(K)| - 6) = 6*(n_k - r_ij) + 2`.
- If K6 fails for this fixed colouring and pair, and `s_ij in {1,2}` is the
  number of touched components for that pair, then touched components
  contribute at least `2*s_ij` to the excess, so
  `2*s_ij <= 6*(n_k-r_ij)+2`. In particular, if `s_ij=2` then
  `r_ij <= n_k-1`; if `r_ij=n_k` then K6 failure forces the sharp case
  `s_ij=1`, the unique touched component has boundary 8, and all untouched
  components have boundary 6.
- Summing over all three pairs, if `p` is the number of split-touched colour
  pairs (`s_ij=2`) and `R=r_AB+r_AC+r_BC`, then K6 failure implies
  `R <= |V(G)| - 1 - p`.
- New proof target: find an extra ingredient from full vertex-criticality/no
  critical edges that forces either `R > |V(G)|-1-p` for some deleted colouring,
  or localizes a large touched Kempe component into a smaller 6-cut. Pure
  component accounting is exhausted.

# (2026-06-11) Local countermodel to K6-by-accounting
- Verifier subagent proposed, and C++ independently confirmed, a 10-vertex
  6-regular graph satisfying the local deleted-vertex/Kempe-balance picture
  at one vertex but with no touched `delta=6` Kempe component:
  take `H=K_{3,3,3}` with colour classes `A={a1,a2,a3}`,
  `B={b1,b2,b3}`, `C={c1,c2,c3}`, delete the rainbow matching
  `a1b1, a2c1, b2c2`, then add a vertex `v` adjacent to
  `a1,a2,b1,b2,c1,c2`.
- Artifact:
  `experiments/sixreg/local_model_k333_minus_matching.txt`;
  verifier output:
  `experiments/sixreg/kempe_balance_local_model.out`.
- C++ result:
  `n=10 m=30`, all degrees 6, `three_colourable=0`,
  `critical_edges=0`, `edge_connectivity=6`, `nontrivial_6cuts=0`,
  `k4_count=2`, `vertex_deletions_leaving_k4=9 1 2 3 4 5 6 7 8 9`,
  `deleted_colourings=6`, `local_222_colourings=6`,
  `unbalanced_kempe_boundary_components=0`,
  `kempe_accounting_failures=0`,
  `touched_non_singleton_components=18`,
  `touched_non_singleton_delta6=0`,
  `kempe_boundary_patterns [01:(2,2)]=6 [02:(2,2)]=6 [12:(2,2)]=6`,
  `touched_delta_hist [20]=18`.
- What fails: vertex-criticality. The graph is 4-chromatic and has no critical
  edge, but `vertex_deleted_not_three_colourable=9`; deleting any vertex other
  than `v` leaves a `K4`. Therefore K6 cannot be proved from 6-regularity,
  no critical edges, one local `(2,2,2)` colouring, Kempe balance, and
  accounting alone. Any full proof must use the all-vertices condition
  `chi(G-x)=3` essentially, or turn this local model into a construction seed
  by vertex-criticalizing it.
- Small n=10 seed census:
  `experiments/sixreg/classify_no_crit.cpp` classifies graph6 streams by
  4-chromaticity, no-critical-edge property, and vertex-critical failures.
  Running
  `geng.exe -q -c -d6 -D6 10 | classify_no_crit.exe 10` gives
  `total=21 threecol=1 fourchrom=20 noCriticalEdge=19 vcNoCrit=0`.
  Failure histogram among no-critical-edge graphs:
  `[9]=1 [10]=18`. Thus the local `K_{3,3,3}`-minus-matching seed appears to
  be the unique n=10 connected 6-regular no-critical-edge graph with even one
  vertex deletion 3-colourable; the other 18 no-critical-edge graphs fail
  vertex-criticality at every vertex.
- n=11/n=12 seed census:
  `n=11`: `total=266 threecol=3 fourchrom=263 noCriticalEdge=247 vcNoCrit=0`,
  histogram `[10]=4 [11]=243`.
  `n=12`: `total=7849 threecol=50 fourchrom=7799 noCriticalEdge=7398 vcNoCrit=0`,
  histogram `[8]=1 [10]=11 [11]=204 [12]=7182`.
- The unique best n=12 seed has graph6 `K?rDtr{~BmMw`;
  saved as `experiments/sixreg/n12_best_no_crit_seed.g6` and analysed in
  `kempe_balance_n12_best_seed.out`. It is 6-regular, 4-chromatic, has
  `critical_edges=0`, `vertex_deleted_not_three_colourable=8`, no K4s
  (`k4_count=0`), no nontrivial 6-cuts, all 24 deleted-vertex colourings have
  `(2,2,2)` neighbourhoods and balanced Kempe components, but
  `touched_non_singleton_delta6=0` with `touched_delta_hist [20]=24 [26]=48`.
  This is a stronger construction seed than the n=10 K4-based model: K6 still
  fails locally, and the remaining obstruction is genuinely vertex-criticality,
  not leftover K4s.

# (2026-06-11) n=12 seed obstruction cores
- Added `experiments/sixreg/seed_structure.cpp`, compiled to
  `seed_structure.exe`, with output saved as
  `experiments/sixreg/seed_structure_n12_best.out`.
- For the best n=12 no-critical-edge seed `K?rDtr{~BmMw`, exactly four vertex
  deletions are 3-colourable: deleting vertices `0,1,4,5`. The other eight
  deletions are not 3-colourable.
- Each failed deletion contains minimum non-3-colourable induced cores of size
  7, all with 13 edges, degree sequence `3,3,4,4,4,4,4`, and vertex-critical
  as induced subgraphs. There are no K4 cores (`k4_count=0`), so this seed is
  obstructed by repeated 7-vertex 4-critical atoms rather than by cliques.
- A full connected 7-vertex enumeration (`classify_4critical.cpp` with
  `geng -q -c 7`) finds seven 4-critical graphs. The n=12 seed cores are in
  the `m=13, deg=3,3,4,4,4,4,4` family, and a direct permutation check
  (`iso_g6.cpp`) identifies their isomorphism type as `FUxuo` (not `FQzuo`).
- Structural pattern: every minimum core listed contains the fixed 4-set
  `{0,1,4,5}` plus one choice from each of two pairs among
  `{6,7}`, `{8,9}`, `{10,11}`. Thus the four globally 3-colourable deletions
  are exactly the fixed 4-set, and the eight bad deletions are the paired
  extension vertices.
- Updated proof target: a genuine target cannot contain this local
  no-critical-edge/Kempe-expanding seed pattern, because every vertex deletion
  must be 3-colourable. The next useful lemma should explain how full
  vertex-criticality prevents these repeated 7-vertex cores, or else how to
  modify such a seed into a larger genuine target/counterexample.

# (2026-06-11) Reducibility census: comparable non-neighbours are useful but not enough
- [VERIFIED T1] Comparable-nonneighbour reducibility:
  in a 4-vertex-critical graph there are no distinct nonadjacent vertices
  `x,y` with `N(x) subseteq N(y)` or `N(y) subseteq N(x)`. Indeed, if
  `N(y) subseteq N(x)` and `G-y` has a 3-colouring, then colouring `y` with
  the colour of `x` extends the colouring to all of `G`, contradiction.
  True nonadjacent twins are the equality case.
- Added `experiments/sixreg/no_crit_core_census.cpp`:
  reads `classify_no_crit` outputs and, for every failed vertex deletion in
  a no-critical-edge seed, finds minimum induced non-3-colourable cores.
  Outputs:
  `core_census_n10.out`, `core_census_n11.out`, `core_census_n12.out`.
- Core census:
  `n=10`: 19 no-critical-edge seeds, 189 failed deletions; minimum core sizes
  `[4]=185 [6]=4`. Thus the unique one-good-deletion local model is explained
  by small proper 4-critical subgraphs, usually K4.
  `n=11`: 247 seeds, 2713 failed deletions; minimum sizes
  `[4]=2529 [6]=160 [7]=24`.
  `n=12`: 7398 seeds, 88546 failed deletions; minimum sizes
  `[4]=78511 [6]=8064 [7]=1946 [8]=1 [9]=24`.
  All minimum cores found are vertex-critical as induced subgraphs. This is
  computational evidence for the meta-lemma: local no-critical-edge models
  fail vertex-criticality through proper 4-critical induced atoms.
- Added `experiments/sixreg/reducibility_census.cpp`:
  counts nonadjacent comparable-neighbourhood pairs and true twin pairs in
  the no-critical-edge seeds. Clean summaries:
  `n=10`: comparable/twin graphs by failures `[10]=5`; the best `[9]=1`
  seed has no comparable pair and is instead K4-obstructed.
  `n=11`: comparable/twin graphs `[10]=4 [11]=34`.
  `n=12`: comparable/twin graphs `[8]=1 [10]=10 [11]=74 [12]=604`.
  The unique best n=12 seed `K?rDtr{~BmMw` has four true twin pairs
  `(2,3),(6,7),(8,9),(10,11)`, exactly matching its eight failed deletions.
- Important negative lesson: the naive lemma
  `K6 failure => comparable non-neighbour pair` is not supported even in
  small no-critical-edge seeds; many n=12 seeds with K6-style local behaviour
  have no comparable pair. A plausible theorem must allow the alternative
  "proper 4-critical induced atom" obstruction, not just comparable vertices.

# (2026-06-11) GPT Pro K6 consult: trichotomy is circular; new blocker target
- GPT Pro did not find a complete proof of K6 or of the proposed
  triple-pressure lemma.
- Key correction:
  in a genuine 4-vertex-critical graph, "proper induced 4-critical atom" is
  impossible by definition, and comparable non-neighbours are impossible by
  the extension lemma. Therefore any trichotomy of the form
  `proper atom OR comparable pair OR K6` is essentially equivalent to K6 on
  genuine targets. It is not a smaller lemma.
- Reconfirmed usable facts:
  (1) local `(2,2,2)` multiplicity in every deleted-vertex colouring of a
  6-regular target;
  (2) perfect Kempe balance for every two-colour Kempe component;
  (3) component accounting
  `sum_{K in K_AB} |delta_G(K)| = 6|C| + 2`, cyclically;
  (4) local accounting alone cannot prove K6, as the n=10 and n=12 seeds show.
- New PENDING target from GPT Pro: terminal list-critical blockers.
  Fix a target `G`, vertex `v`, 3-colouring `phi` of `H = G-v`, and a colour
  `A` whose neighbours at `v` are `a,a'`. For the non-critical incident edge
  `va`, define a list assignment `L_a` on `H` by
  `L_a(a)={A,B,C}`, `L_a(x)={B,C}` for
  `x in N(v)\{a}`, and `L_a(x)={A,B,C}` otherwise.
  Then `H` is not `L_a`-colourable, while `H-a` is `L_a`-colourable; hence an
  inclusion-minimal induced `L_a`-uncolourable blocker `Q_a` exists and must
  contain both terminals `a,a'`.
- Verification status:
  the existence of `Q_a` is a clean T1-level argument once the target
  hypotheses are fixed; the actual desired implication
  `terminal blocker => boundary-6 touched Kempe component` is OPEN/PENDING.
- Next concrete attack:
  write an exact C++ list-colouring/blocker extractor and run it on the known
  n=10/n=12 no-critical-edge seeds to classify terminal blocker shapes before
  asking GPT Pro a sharper follow-up. Avoid restarting the abandoned large
  `a=14` shore enumeration unless the blocker route produces a reason.

# (2026-06-11) Terminal blocker extraction on local seeds
- Added C++ exact tool:
  `experiments/sixreg/terminal_blockers.cpp`.
  It enumerates every 3-colourable deletion `G-v`, deduplicates the
  two-neighbour colour pairs, constructs the terminal list assignment `L_a`,
  and exhaustively finds minimum induced `L_a`-uncolourable blockers.
- n=10 local model
  (`experiments/sixreg/terminal_blockers_local_model.out`):
  `deletion_colourable_vertices=1`, `cases=6`, `H_not_L=6`,
  `H_minus_terminal_L=0`, `min_blocker_size_hist [3]=6`.
  The blockers are triangles (`g6=Bw`), ordinary 3-colourable as graphs but
  list-uncolourable; they contain the mate terminal but not the freed terminal.
  This matches the fact that the n=10 seed is not vertex-critical and therefore
  does not satisfy the target-side `H-a` list-colourability condition.
- n=12 best seed
  (`experiments/sixreg/terminal_blockers_n12_best.out`):
  `deletion_colourable_vertices=4`, `cases=24`, `H_not_L=24`,
  `H_minus_terminal_L=8`, `min_blocker_size_hist [6]=24`.
  In the 8 target-like cases with `H-a` list-colourable, every minimum blocker
  has size 6, contains both terminal vertices, is ordinary 3-colourable
  (`ordinary3=1`), is inclusion-minimal as a list blocker, has 9 internal
  edges, boundary 18 in the full seed, degree sequence `2,3,3,3,3,4`, and
  induced graph6 `E\xO`.
- Interpretation:
  terminal blockers are not just the old proper induced 4-critical cores.
  The promising object is a 6-vertex ordinary-3-colourable but
  list-critical terminal blocker. The next proof question is whether such a
  blocker can exist inside a genuine 6-regular target while all touched Kempe
  components have boundary at least 8. This is now sharper than the previous
  circular trichotomy.
- Added abstract TB6 shape classifier:
  `experiments/sixreg/tb6_shape_patterns.cpp`, output
  `tb6_shape_patterns.out`.
  For the labelled shape with edges `pr,ps,pt,qr,qt,qu,rs,rt,su`, there are
  68 minimal list-uncolourable terminal/restricted-set patterns:
  36 with three restricted vertices and 32 with four restricted vertices.
  Therefore the six-vertex list-critical shape is locally consistent; it
  cannot be ruled out without using its embedding in the 6-regular target
  (external neighbours, the full neighbourhood of `v`, and/or Kempe expansion).

# (2026-06-11) GPT Pro answer: terminal blockers are global in a target
- GPT Pro completed the terminal-blocker follow-up.
- [VERIFIED T1] Global terminal blocker lemma:
  Let `G` be 4-vertex-critical. Fix `v`, put `H=G-v`, and fix
  `a in N(v)`. Define `L_a` on `H` by
  `L_a(a)={A,B,C}`, `L_a(x)={B,C}` for `x in N(v)\{a}`, and
  `L_a(x)={A,B,C}` otherwise. Then every proper induced subgraph of `H` is
  `L_a`-colourable.
- Independent proof check:
  if `S` is a proper subset of `V(H)` and `H[S]` is not `L_a`-colourable,
  then `W=G[S union {v}]` is not 3-colourable; otherwise rename a
  3-colouring of `W` so that `v` has colour `A`, and restrict to `S` to get
  an `L_a`-colouring. Since `S` is proper in `H`, choose
  `y in V(H)\S`; then `W` is an induced subgraph of `G-y`, which is
  3-colourable by vertex-criticality, contradiction.
- Consequence:
  if `va` is not critical, so `G-va` is not 3-colourable, then `H` is not
  `L_a`-colourable and is itself inclusion-minimal `L_a`-uncolourable.
  Therefore in a genuine target there are no proper induced terminal
  list-blockers at all.
- This explains the n=12 seed:
  each extracted 6-vertex terminal blocker `Q` becomes an ordinary proper
  induced 4-chromatic witness after adding back the deleted vertex `v`.
  Thus those blockers certify non-vertex-criticality, not a possible local
  obstruction inside a target.
- Corrected live target:
  abandon small terminal-blocker classification as a route to K6. The useful
  lemma is now global:
  in a 6-regular target, the whole `H=G-v` is terminal-list-critical for each
  non-critical incident edge `va`; combine this whole-H minimality with Kempe
  balance/accounting to force a touched boundary-6 Kempe component.

# (2026-06-11) GPT Pro Kempe-expansion answer: no proof of A/B/C yet
- GPT Pro did not provide a complete proof of the proposed A/B/C route.
  Treat the answer as a route correction, not as a result.
- Main correction:
  the proposed lemma B is essentially equivalent to the no-critical-edge
  hypothesis once vertex-criticality is assumed. A deleted-vertex colouring
  with a colour appearing exactly once in `N(v)` makes the corresponding
  incident edge critical, and conversely a critical incident edge yields such
  a colouring. Therefore B is not a smaller intermediate target.
- Reconfirmed [VERIFIED T1] Kempe facts:
  in every deleted-vertex 3-colouring of a target, all touched two-colour
  Kempe components are balanced with respect to the two neighbours of each
  colour, and
  `sum_{K in K_AB} |delta_G(K)| = 6|C| + 2`, cyclically.
- Correct next target:
  prove K6 / no Kempe-expansion:
  some non-singleton two-colour Kempe component touching `N(v)` has
  `|delta_G(K)| = 6`.
- Weak point:
  one colour-pair accounting cannot force K6, because a large touched
  component can absorb the boundary budget. Any proof must use all three
  colour-pair decompositions simultaneously, likely together with the
  whole-`H` terminal-list-criticality lemma.
- Candidate pressure formulation [OPEN]:
  if every touched two-colour Kempe component has boundary at least 8, then
  either there is already a nontrivial 6-edge-cut, or a comparable same-colour
  non-neighbour, or a bounded reducible atom around `v`.
  In a genuine target, the latter two alternatives should be impossible by
  vertex-criticality and the comparable-nonedge extension lemma.
- Saved digest:
  `problems/944/gpt_kempe_expansion_answer_digest_2026-06-11.md`.

# (2026-06-11) Pending invariant idea while GPT Pro is thinking
- Setup:
  fix a deleted colouring `phi` of `H=G-v` with A-terminals `a,a'`.
  For terminal list assignment `L_a`, `phi` has exactly one forbidden terminal:
  `a'` is coloured `A`, while `a` is allowed to keep colour `A` and the other
  four neighbours of `v` are not coloured `A`.
- Observation [PENDING]:
  in `H`, any single two-colour Kempe swap preserves the number of
  `A`-coloured neighbours of `v`, by Kempe balance. Therefore elementary
  Kempe swaps can move the `L_a` violation among terminals but cannot reduce
  the count of A-terminals from two to one.
- Global terminal-list-criticality says that for every `y in V(H)`, `H-y`
  has an `L_a`-colouring, so after deleting any vertex the A-terminal count
  can drop to one.
- Potential bridge [OPEN]:
  deletion of every `y` must break some Kempe lock or permit a non-Kempe
  recolouring that eliminates `a'`. If this can be localized, it may force a
  touched two-colour component with small boundary. This needs a theorem about
  3-colouring reconfiguration/list-criticality; it is not yet verified.

# (2026-06-11) Terminal unlock diagnostics
- Added C++ exact diagnostic:
  `experiments/sixreg/terminal_unlock.cpp`.
  Outputs:
  `terminal_unlock_local_model.out`,
  `terminal_unlock_n12_best.out`.
- What it measures:
  for each deleted-vertex colouring `phi` of `H=G-v` and each terminal list
  assignment `L_a`, it checks whether `H` is `L_a`-colourable, how many
  one-vertex deletions `H-y` are `L_a`-colourable, and whether each unlocker
  `y` lies in the original two Kempe components through the mate terminal
  `a'`.
- n=10 local model:
  every terminal assignment is locked on `H`, but only `1/9` one-vertex
  deletions unlock it. The mate-terminal `(A,B)` and `(A,C)` components both
  have boundary 20.
- n=12 best no-critical-edge seed:
  every terminal assignment is locked on `H`, but only `3/11` or `4/11`
  one-vertex deletions unlock it. Mate-terminal Kempe component boundary pairs
  are only `(20,26)`, `(26,20)`, or `(26,26)`, never 6.
- Interpretation [T0 computational]:
  local no-critical-edge seeds can satisfy the no-critical-edge terminal lock
  while being far from global `L_a`-criticality. A genuine target requires
  `H-y` to unlock for every `y in V(H)`, not merely for the few vertices in
  a local blocker. The next useful lemma should be:
  if a deleted colouring is Kempe-expanding and all six terminal list
  assignments are globally one-deletion-unlocked, then some touched
  two-colour Kempe component has boundary 6 or a forbidden reducible pair.

# (2026-06-11) GPT Pro answer: boundary-support obstruction, not K6
- GPT Pro completed the global-list-criticality vs Kempe-expansion follow-up.
- Status:
  no contradiction and no proof of K6. Current ingredients do not logically
  force a boundary-6 component.
- [VERIFIED T1] Boundary-support obstruction lemma:
  Fix a target `G`, a deleted colouring `phi` of `H=G-v`, A-terminals
  `a,a'`, and the terminal list assignment `L_a`. Let `K` be the
  `(A,B)`-Kempe component containing `a'`. Let `R_C(K)` be the vertices of
  `K` with at least one neighbour outside `K` coloured `C`. If `M_{a,K}` is
  `L_a` restricted to `K` with colour `C` additionally forbidden on
  `R_C(K)`, then `K` is not `M_{a,K}`-colourable.
- Independent proof:
  an `M_{a,K}`-colouring of `K` could be pasted into the original colouring
  on `H-K`. Cross-edge conflicts are avoided because all edges from an
  `(A,B)`-Kempe component to `H-K` hit `C`-coloured vertices, and support
  vertices are forbidden to receive `C`. The only original `L_a` violation is
  at `a'`, inside `K`; the pasted colouring satisfies `L_a` everywhere,
  contradicting `H` not being `L_a`-colourable.
- Equivalent form:
  every `L_a`-colouring of `K` must use colour `C` somewhere on the
  third-colour boundary support `R_C(K)`.
- Computational sanity:
  `terminal_unlock.cpp` now checks this `M`-colourability condition. On the
  n=12 best no-critical-edge seed, every mate component has
  `M_colourable=0`, but its boundary is 20 or 26. This confirms the lemma is
  a support obstruction, not a multiplicity bound.
- GPT Pro's quotient-level countermodel [CONCEPTUAL, not an actual graph]:
  colour classes of size 4; for each colour pair two touched `(1,1)` terminal
  edge components of boundary 8 and one untouched component of boundary 10.
  The accounting `8+8+10=26=6*4+2` holds cyclically. This satisfies the
  fixed-colouring Kempe/accounting/support constraints without a boundary-6
  component, so more structure is needed.
- New missing lemma [OPEN]:
  support-to-multiplicity. In a genuine 6-regular target, a touched Kempe
  component that is boundary-support-critical cannot have too many edges to
  the third colour:
  type `(1,1)` should force `e_H(K,C) <= 4`;
  type `(2,2)` should force `e_H(K,C) <= 2`.
  Together with the 6-edge-connectivity lower bound, this would yield K6.
- Saved digest:
  `problems/944/gpt_kempe_pressure_answer_digest_2026-06-11.md`.

# (2026-06-11) Agent prover/verifier stress test of support-to-multiplicity
- Boole prover note:
  `problems/944/agent_notes_boole_support_to_multiplicity.md`.
- Verdict from both Boole and Feynman:
  support-to-multiplicity does not follow from the current verified local
  ingredients. The obstruction is exactly that boundary support is boolean,
  while `e_H(K,C)` is a multiplicity.
- Boole's local models:
  type `(1,1)` can be a single terminal edge `a'--b` with both endpoints
  having several `C`-neighbours. The support-forbid-C lists collapse both
  endpoints to `{B}`, so boundary-support-criticality holds, while
  `e_H(K,C)` can exceed 4.
  Type `(2,2)` can be `K_{2,2}` on terminals `a,a',b,b'`; with all four
  vertices in the third-colour support, the lists are
  `a:{A,B}` and `a',b,b':{B}`, uncolourable, while already one C-edge per
  vertex gives `e_H(K,C)=4>2`.
- Feynman's finite near-countermodel:
  the n=10 local model with `v=0` has a type `(2,2)` mate component
  `K={1,2,3,4,5,6}` with `|delta_G(K)|=20` and `e_H(K,C)=16`, while
  boundary-support obstruction holds. It satisfies many local constraints
  (6-regularity, no critical edge, local `(2,2,2)`, Kempe balance/accounting,
  terminal locks) but fails exactly global vertex-criticality:
  `H-y` unlocks for only `1/9` deletions, not every `y`.
- Refined missing lemma [OPEN]:
  global one-deletion unlock localization. If `H` is globally `L_a`-critical,
  then the `L_a`-colourings of `H-y` for all `y` must force some colouring
  that is local enough around the mate Kempe component to control
  third-colour boundary multiplicity. Without such a localization or
  reconfiguration theorem, multiplicity can hide behind the same support set.

# (2026-06-11) One-swap unlock diagnostics
- Extended `experiments/sixreg/terminal_unlock.cpp` again:
  for each `H-y` that is `L_a`-colourable, it now checks whether the original
  restricted colouring `phi|_{H-y}` already satisfies `L_a`, or whether a
  single Kempe-component swap from `phi|_{H-y}` gives an `L_a`-colouring.
- n=10 local model:
  every terminal assignment has exactly `1/9` unlock; that unlock is already
  `phiOK` and hence also counted as one-swap/local.
- n=12 best seed:
  unlock profiles are:
  `3/11 phiOK=1 oneSwap=1` (4 cases),
  `3/11 phiOK=1 oneSwap=3` (4 cases),
  `4/11 phiOK=1 oneSwap=2` (8 cases),
  `4/11 phiOK=1 oneSwap=3` (8 cases).
- Interpretation [T0 computational]:
  some one-deletion unlocks are local Kempe phenomena, but not all even in the
  small seed. Therefore the likely missing theorem cannot simply assert that
  every `H-y` list-colouring is one Kempe swap from `phi|_{H-y}`. A weaker
  but plausible target is to prove that sufficiently many globally required
  unlocks can be localized to force one small-boundary component.

# (2026-06-11) Current #944 blocker status
- The GPT Pro answer reducing A/B/C to K6/Triple-Kempe pressure is already
  incorporated above. It is not a proof of nonexistence.
- The active narrow blocker is still:
  `support-to-multiplicity / global one-deletion unlock localization`.
  Concretely, boundary-support-criticality controls only which vertices of a
  touched Kempe component see the third colour; it does not control the number
  of third-colour boundary edges.
- Browser status after the latest user-pasted GPT text:
  the later support-to-multiplicity question is still generating in ChatGPT
  Pro Extended. Await that answer before spending more compute on this route.
- Decision rule:
  if GPT Pro does not supply either a genuine localization lemma or a
  target-level obstruction, then #944 should be parked as `HARD/PARKED` and
  the autonomous loop should move back to the next active candidate (#23 or a
  fresh SELECT), because the current local Kempe package has reached a real
  mathematical bottleneck rather than a compute bottleneck.

# (2026-06-11) GPT Pro answer to support-to-multiplicity
- GPT Pro did not prove support-to-multiplicity.
- Main verified reduction:
  for an `(A,B)`-Kempe component `K` with
  `t=|K cap N(v)|`,
  6-regularity gives
  `e_H(K,C) = 6|K| - t - 2e(K)`.
  For terminal type `(1,1)`, the desired `e_H(K,C) <= 4`, and for terminal
  type `(2,2)`, the desired `e_H(K,C) <= 2`, are both equivalent to
  `e(K) >= 3|K| - 3`.
  Thus support-to-multiplicity is really a strong internal-density claim
  about the mate Kempe component.
- GPT Pro supplied an actual 9-vertex coloured obstruction showing that
  boundary-support-criticality plus one-deletion criticality for the two
  naturally associated terminal assignments does not imply the type `(1,1)`
  multiplicity bound.
- Independent C++ verifier added:
  `experiments/sixreg/verify_gpt_obstruction.cpp`.
  It confirms:
  the component `K={a',alpha,b,beta}` has terminal type `(1,1)`,
  `e_H(K,C)=7>4`,
  is support-critical for `L_a` and `L_b'`,
  and `H` is one-deletion-list-critical for `L_a` and `L_b'`.
- The obstruction is not a target:
  it is not 6-regular after adding the deleted vertex,
  it has the comparable same-colour nonedge `N(c') subset N(gamma)`,
  and it is not critical for all six terminal assignments.
- New smaller proposed lemma [OPEN]:
  high third-colour multiplicity in a dual-terminal or four-terminal
  support-critical Kempe component forces either a same-colour comparable
  nonedge or a failure of one of the required one-deletion list-colourings.
- Route assessment:
  Kempe accounting + boundary support + one/two terminal list criticalities
  are insufficient. Any full #944 proof must use all six terminal assignments
  and comparable-nonedge exclusion in a genuinely new domination/synchronising
  lemma.
- Digest:
  `problems/944/gpt_support_to_multiplicity_answer_digest_2026-06-11.md`.

# (2026-06-11) Domination/synchronisation follow-up
- Sent follow-up prompt:
  `problems/944/gpt_followup_domination_2026-06-11.md`.
- The prompt asks GPT Pro to prove or refute the reduced domination lemma:
  in a genuine target-level local setting, high third-colour multiplicity on a
  support-critical mate Kempe component should force either a comparable
  same-colour nonedge or failure of one of the required terminal
  one-deletion list-colourabilities.
- Browser status after send: GPT Pro thinking.
- Decision:
  this is the last narrow #944 Kempe consult before parking. If the answer
  does not provide a verifiable proof or a target-level obstruction, the
  Kempe route should be marked STUCK/HARD and the global loop should move on.

# (2026-06-11) Domination local random search
- Added experiment:
  `experiments/sixreg/domination_search.cpp`.
- Purpose:
  search for local target-level countermodels to the proposed
  dual/four-terminal domination lemma.
- Model:
  tripartite `H` with fixed deleted-colouring, two terminals per colour,
  terminals of H-degree `5`, nonterminals of H-degree `6`, all six terminal
  list assignments required to be globally one-deletion critical, and
  no same-colour comparable open-neighbourhood pair in `G=H+v`.
- Search target:
  a type `(1,1)` support-critical mate Kempe component with
  `e_H(K,C)>=5`, or type `(2,2)` with `e_H(K,C)>=3`.
- Run:
  `domination_search.exe 4 60 96`.
- Result [T0]:
  `generated=104623827 allSixCritical=0 noComparable=0 hits=0`.
- Interpretation:
  no obstruction found in the smallest equal-colour-size degree-normalized
  random class. Since no all-six-critical model was found, this is evidence
  that all-six criticality is very restrictive, not a proof of domination.

# (2026-06-11) GPT Pro domination answer: no proof
- GPT Pro completed the domination/synchronisation follow-up.
- It did not prove the domination lemma and did not provide a genuine
  target-level obstruction satisfying all required one-deletion
  list-colourabilities.
- Verified reduction:
  for `m=e_H(K,C)` and `t=|K cap N(v)|`,
  `6|K| = 2e(K) + m + t`, hence `m+t` is even.
  Therefore the bad thresholds are:
  type `(1,1)`: `m >= 6`;
  type `(2,2)`: `m >= 4`.
- Proposed remaining bridge [OPEN]:
  a trace-domination theorem. For `W=H-K`, deletion `z`, and an exterior
  `L`-colouring `theta` of `W-z`, define the trace lists
  `T_{theta,z}(u) = L(u) \ {theta(w) : w in N_H(u) cap (W-z)}`.
  The missing theorem would show that high third-colour multiplicity forces
  some `z` and relevant terminal list `L` such that every exterior trace leaves
  `K` uncolourable, contradicting target-level one-deletion list-criticality.
- GPT also supplied a 22-vertex graph6 diagnostic. Independent verifier:
  `experiments/sixreg/verify_gpt_21_obstruction.cpp`.
  Verified from graph6:
  the graph is 6-regular, not 3-colourable, `G-v` is 3-colourable, no edge
  deletion is 3-colourable, and only deletion of `v` is 3-colourable.
  But GPT's detailed labelled claims failed under the claimed vertex order:
  `H` is not tripartite in the displayed partition, `L_a` is colourable, and
  the claimed small `(A,B)` component is not recovered.
- Status:
  no new theorem. The Kempe route now depends on proving the trace-domination
  theorem from scratch; current GPT/local evidence does not supply it.
- Digest:
  `problems/944/gpt_domination_answer_digest_2026-06-11.md`.

# (2026-06-11 ~14:00) BRIDGE-LEMMA frontier: consult round + decisive small-n experiment
- GPT bridge verdict (audited): bridge NOT yet a theorem; "[C] => global freezing" route
  FALSE — explicit H0 (prism 2-blow-up minus vertical matching on 0-copies, a=12) is
  [C]-compliant with totally local mechanism. H0 MACHINE-VERIFIED by us: [C] 12/12
  colourings OK, [T] OK, BUT [K] fails at ALL 12 vertices => dies (consistent with
  exhaustive a=12 = 0 survivors). GPT's real gap statement: [C] constrains colourings
  of H; [K] lives on colourings of H-v (incl. NON-EXTENDABLE ones) — counterexamples
  would live in that gap.
- GPT's proposed kernel experiment (Sec 7): does a connected 6-regular 3-colourable R
  exist with EVERY vertex deletion-unfrozen (R-v has a colouring with N(v) counts
  (2,2,2) — necessarily non-extendable)? EXECUTED n=12,13 (all 50+849 3-col 6-regular
  graphs): fullyUnfrozen=0, MAX unfrozen vertices = 2 (!!) of 12/13. The bridge's
  counterexample ingredient is nowhere near existing at small n.
- SHARPENED CONJECTURE (new, supported n<=13): a 6-regular 3-colourable graph has at
  most 2 deletion-unfrozen vertices. If "not all vertices unfrozen" is provable for
  all n, the attachment route to refute the bridge dies entirely.
- Two [C]-gadget families (triangle-support, K222-support) both empirically dead at
  [K] (a=15..21, ~1000 realized candidates, 0 valid).
- NEXT: (1) n=14 unfrozen scan (42,667 3-col graphs) AFTER shore scan frees workers;
  (2) feed max-2-unfrozen finding to GPT: prove bound or characterize the unfrozen
  pairs; (3) a=14 shore scan continues (13.4k/55k, 0 survivors).

# (2026-06-11 ~16:00) Unfrozen-bound kernel: REFUTED by verified construction; kernel reduced
- GPT round: "unfrozen <= C" is FALSE. Explicit B (15 vertices, 6-regular, 3-colourable,
  45 edges) with exactly ONE unfrozen vertex (v=10), no bridges/2-cuts (lambda>=4);
  colour-compatible 2-edge-sum chain B^(m) (ports (0,1),(2,9), colours preserved under
  both kappa and the witness psi) has >= m unfrozen vertices. WE MACHINE-VERIFIED ALL OF
  IT: B 6-regular/kappa/psi/(2,2,2)/port colours/connectivity ✓; B^(3) 6-regular,
  connected, 3-colourable, all three 10_j unfrozen ✓; B census: unfrozen = {10} only.
- Mechanism of refutation: 2-edge cuts between blocks defeat any cut-charge bound;
  cut-charge needs edge-connectivity >= 6 hypothesis.
- LIVE KERNEL (reduced): "every connected 6-regular 3-colourable graph has at least one
  deletion-frozen vertex" — unrefuted (all 899 graphs n<=13 + B have >= 13/15 frozen);
  the 6-edge-connected restricted version is the cut-charge-compatible target and the
  one relevant to the super-6-ec shore endgame.
- NEXT EXPERIMENTS (GPT-agreed): (1) n=14 unfrozen census (42,667 3-col 6-regular) when
  workers free; (2) n=15 enumeration can feed BOTH Theorem-A extension and the census;
  (3) attempt proof: reduce along 2/4-cuts, irreducible 6-ec case via Kempe cut-charge.
- a=14 shore scan: 18,099/55,000 done, 0 survivors, chains healthy.
