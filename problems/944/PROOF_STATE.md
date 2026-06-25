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

# (2026-06-12 ~07:20) STRATEGY PIVOT + n=14 unfrozen census (NEW FACT)
- USER DECISION: n-by-n enumeration ladder cannot reach n=29 (each step ~70x graphs);
  n=16 scan STOPPED (resume-safe queue, 10 classes validated, 0 4-VC in 31.3M graphs).
  All CPU redirected to the structural (FK) frozen-kernel route.
- (FK) frontier lemma: H connected, 3-colourable, maxdeg<=6, total deficiency 6,
  |V|>=9 => H has a frozen full-degree vertex. Proves Theorem B for ALL shore sizes
  => every 6-edge-cut is a vertex star => star-cut endgame for Problem 5.2.
- GPT consult sent (thread c/6a29bd3c, gpt_frozen_kernel_consult_2026-06-12.md):
  Q1 prove (FK) / Q2 counterexample shape / Q3 finite certificate. Reply pending.
- n=14 UNFROZEN CENSUS (NEW, triple-anchored: total=21,609,301=geng>Z=known count;
  threecol=42,667=known): fullyUnfrozen=0 (kernel survives n<=14);
  maxUnfrozen=4 — REFUTES the "<=2 unfrozen" sharpening (n<=13 data was misleading).
  hist: 0:40237 1:2239 2:184 3:5 4:2. The 7 graphs with k>=3 in
  experiments/sixreg/census14/high_unfrozen_n14.txt (g6 + unfrozen bitmask).
  Tool: experiments/sixreg/unfrozen_census.cpp (validated exactly on n=12: 50/0/2,
  n=13: 849/0/2 vs known census).
- NEXT: (a) read GPT (FK) reply, feed it the n=14 data (esp. the k=4 graphs'
  structure); (b) analyze the 7 high-unfrozen graphs for the growth mechanism;
  (c) PR #4237 body updated to n<=15 / shores>=15 via REST PATCH (verified).

# (2026-06-12 ~08:15) (FK) GPT round AUDITED: charge identities VERIFIED; route fixed
- GPT reply (c/6a29bd3c): NO (FK) proof (honest); supplies (1) arithmetic signature
  + component charge identity sum kappa(C) = 6|X_k|+8-2B_k [VERIFIED: hand algebra +
  23/23 real unfrozen instances from n=14 census via deficiency-0 variant, 0 fails;
  verify_charge_identity{,_reg}.py], (2) NEW necessary filter: unfrozen v =>
  complement H[N(v)] has perfect matching [VERIFIED 23/23], (3) minimal-shore
  kappa(X)>=8 reduction [rigorous-informal ACCEPTED: smaller 6-cut contradicts
  minimality; 7 excluded by parity] — (FK) restricted to MINIMAL shores suffices
  for #944, (4) finite boundary-piece certificate architecture (programme).
- Killer constraint found: B_k>=4 => non-singleton bicolour component budget
  8-2B_k <= 0 under kappa>=8 — near-rigid witness structure. Squeeze next.
- Full digest: gpt_fk_answer_digest_2026-06-12.md. Verifiable new facts this
  cycle: n=14 census (fullyUnfrozen=0, maxUnfrozen=4) + verified identities ⇒ stall=0.
- NEXT: (a) filters-5/6 searcher at a=15..16 (does the counterexample SHAPE even
  exist? dies at 5/6 => local proof likely); (b) B_k>=4 budget case analysis;
  (c) boundary-piece state-table enumerator; (d) next GPT round with n=14 data.

# (2026-06-12 ~08:45) n=14 diagnostic CLOSED + (FK) round 2 sent + own squeeze derivation
- pm_stats n=14 EXHAUSTIVE (triple-anchored: total=21,609,301=gengZ; 3col=42,667;
  unfrozen=2,630 == census hist 2239+2*184+3*5+4*2): f5pass=596,942/597,338 (99.93%),
  I4viol=0, allF5graphs=42,448/42,667. CONFIRMED: binding constraint is GLOBAL
  extension rigidity (local matching filter almost never binds).
- Round 2 sent (c/6a29bd3c): Q1 zero-budget squeeze (B_k>=4), Q2 precise rigidity
  lemma, Q3 boundary-piece state-table formalism (codeable). Reply pending.
- OWN derivation (to cross-check GPT's Q1 answer), minimal-shore kappa>=8 setting,
  c=#components of H[X_i u X_j], T=#non-singletons, s=c-T singletons:
  (S1) 6c + 2T <= Sum kappa(C) = 6|X_k| + 8 - 2B_k  =>  T <= 3(|X_k|-c) + 4 - B_k.
  (S2) B_k=4 => c <= |X_k|; B_k=6 => c <= |X_k|-1 (T>=0).
  (S3) all-singleton (T=0 => e_ij=0) + identity e_ij=3(|X_i|+|X_j|-|X_k|)+B_k-4
       => 3 | (4-B_k) => B_k in {1,4}; B_k=4 => |X_i|+|X_j| = |X_k| = (n-1)/2
       (giant independent class, near-bipartite extreme). Status: rigorous-informal,
       cross-check + computational verify next.

# (2026-06-12 ~09:35) (FK) ROUND 2 AUDITED: zero-budget theorem PROVEN; certificate spec ready
- Q1 ZERO-BUDGET ACCOUNTING THEOREM (minimal-shore setting) — AUDIT COMPLETE, every
  step verified (kappa evenness, forest bound, q>=5 bipartite bound; equation form
  2r+zeta = 6h+8-2B_k refines my (S1); all-singleton case EXACTLY B=4, p=q, e_ij=0,
  bipartite near-6-regular structure, |V|>=11). Status: rigorous-informal THEOREM.
- Q2: DCRL(M) rigidity lemma formulated (conjectural target of the programme).
- Q3: boundary-piece certificate formalism FULLY SPECIFIED & codeable (pieces with
  stubs, Col/Unf bitset tables over <=3^8, FrozenFlag [soundness argument checked],
  composition lemmas [equality across deleted-v stubs], FK-simulation + replacement
  lemma, mu cut-profile, boundary 8 required). Digest:
  gpt_fk_round2_digest_2026-06-12.md
- NEXT (in order): (1) piece enumerator implementation; (2) FrozenFlag validation
  against census data; (3) FK-simulator hunt among small pieces; (4) Lean port of
  the zero-budget theorem (double counting; next PR increment candidate).

# (2026-06-12 ~12:30) (FK) BOUNDARY-PIECE PROGRAMME: implementation validated; FROZEN-PIECE THEOREMS (machine-verified)
- piece_state.cpp (Q3 spec: Piece/Col/Unf bitsets, FrozenFlag) VALIDATED against exhaustive
  census: n=12 full stock (7,849 graphs, 804,917 pieces, 258,931 certificate firings),
  n=13 full stock (367,860 graphs, 40.1M pieces, 3.96M firings), 7 high-unfrozen n=14
  graphs: VIOLATIONS = 0 in all runs (certified-frozen => truly frozen, every instance).
- piece_hunt.cpp: enumerated ALL kappa=8 b=0 pieces (connected, Delta<=6, e=3m-4, 3-col):
  m=8:3, m=9:62, m=10:1471, m=11:48525. RESULT (THEOREM, machine-verified +
  python double-check 27/27): EVERY such piece has FrozenFlag — an all-unfrozen
  6-regular graph contains NO kappa=8 cut piece on <=11 vertices at all.
- Col-state space tiny: only 355 distinct canonical tables over 50,061 pieces; 59 cross-
  size collisions exist BUT all pieces frozen => no robustly-unfrozen simulator exists
  => the REPLACEMENT/descent route is dead at small M; live route = M-boundedness.
- BIPARTITE chain (the zero-budget components are bipartite; family starts at m=11 and
  is tiny): m=11:1, 12:10, 13:27, 14:234, 15:1051, 16:33232, 17:302409 pieces; locked-
  vertex counts (python-verified 37/37 on m=12,13): min locked = 8 (m=12), >=10 (m13-16),
  >=12 (m=17). Lockedness is independent of b-designations elsewhere; total deficiency 6
  < 8 => EVERY kappa=8 bicolour component with <=17 vertices contains a locked FULL
  vertex under EVERY deficiency assignment and EVERY B_k regime.
- CONSEQUENCE for (FK): a minimal-shore all-unfrozen counterexample H has every
  kappa=8 component of H[X_i u X_j] of size >= 18. Derived structure of large kappa=8
  bipartite pieces: sides near-balanced (|a-b|<=1 from 6a >= e = 3(a+b)-4 at scale),
  near-6-regular dense bipartite.
- REMAINING GAPS (the (FK) frontier, for GPT round-3):
  (G1) kappa=8 components of size >= 18: M-unbounded; need theoretical locking argument
       for near-balanced near-6-regular bipartite pieces (or DCRL-type containment bound).
  (G2) configurations where NO kappa=8 component exists (all non-singletons kappa>=10,
       budget 2r+zeta=6h+8-2B allows it for large h); kappa=10 piece family unexplored
       (needs NSTUB=10 generalization, bipartite family starts ~m=10 incl. K_{5,5}).
  (G3) all-singleton extreme (B=4, e_ij=0): X_i u X_j AND X_k independent => H-v
       bipartite, near-6-regular, q>=5, |V|>=11 — own rigidity analysis pending.
  (G4) pair-choice freedom: zero-budget applies per (v,{i,j}); proof may choose best of
       3 pairs per unfrozen v + range over all v — squeeze unexploited.
- Tools: piece_state.cpp, piece_hunt.cpp (scan/match/locked/robust/exact modes),
  verify_piece_frozen.py, verify_locked.py; data: rec_m*.txt, locked_bip_m*.txt,
  piece_validate_n1{2,3}.out. Lean port of zero-budget L1/L2 delegated (in progress).
- (2026-06-12 ~13:30 update) F1 EXTENDED to m=12: general kappa=8 census 119.7M cands -> 2,055,237 3-col pieces, ALL FrozenFlag (min locked 4; locked<=6 only 280 pieces, relevant to adversarial deficiency placement only). Bipartite m=18 (18.66M) locked-census queued.
- (2026-06-12 ~13:45 CORRECTION + menu) kappa=10 family includes m=2 SINGLE EDGE (locked=0, NOT frozen — live structure); no m=3..9 members (bipartite density). Small-component menu in minimal-shore witness partitions: singleton (kappa=6), single edge (kappa=10, zeta=2), P3 (kappa=14), C4/stars (kappa>=16); everything else >=10 vtcs and locked-censused dead <=16/17. Budget consequence: non-singleton components are EDGES (cost 2r-share 2 + zeta 2 = 4) or BIG (>=17 vtcs).
- (2026-06-12 ~14:30) ZERO-BUDGET L1+L2 LEAN-VERIFIED: formal-conjectures/erdos944_zero_budget.lean (agent-built, independently recompiled EXIT=0, axioms clean, statements audited faithful: sIJ=2e_ij indicator form, L1 sIJ=6p-6q+2B_k-8, L2 charge identity, bonus evenness lemma). Candidate for PR #4237 increment together with the frozen-piece census.
- (2026-06-12 ~15:10) kappa=8 bipartite chain EXTENDED to m=18 (18.66M pieces, ALL >=10 locked; hist floor 10): every kappa=8 bicolour component <=18 vertices dead in every B_k regime => counterexample components >=19. m=19 (~1.2B) past brute-force frontier — large-piece theory (round-3 Q1) is the continuation.
- (2026-06-12 ~16:30) G3 (all-singleton extreme) FINITE SEARCH: candidate shape = connected balanced bipartite cross-graph (q,q), Delta<=6, 6q-6 edges (connectivity forced by minimal-shore kappa-sum), apex v->4+2 deficient vertices. Exhaustive q=5..8 (apexings 100/1695/83937/29084215): ZERO all-unfrozen survivors => no all-singleton counterexample with |V|<=17. Dominant kill = v itself frozen. Tool: allsingleton_search.cpp (MT; orientation-skip bug found+fixed in re-verify). kappa=12 m=17 census also closed (14.3M pieces, min locked 8).

# (2026-06-12 ~17:45) G3 (all-singleton) COMPREHENSIVELY DEAD COMPUTATIONALLY; freezing law identified
- (FK) all-singleton extreme attacked five ways, ZERO all-unfrozen candidates anywhere:
  (1) exhaustive q<=8 / |V|<=17 (all patterns+apexings; 29.2M at q=8);
  (2) random sparse 1^6-pattern q=10/12/15 x 5000 (g3_random.cpp; q=8 sanity matches exhaustive);
  (3) random GENERAL deficiency patterns q=12/15 x 100,000 (6 random edge deletions);
  (4) adversarial hill-climb minimizing #frozen: q=12 floor 6 (4.5M moves), q=15 floor 5
      (1.57M moves, never below 5; g3_hillclimb.cpp);
  (5) achievability probe (g3_counts.cpp): the FREEZING LAW — for full cross-vertices x,
      N(x) count-multisets with an absent colour are ~always achievable; {4,1,1} sometimes,
      {3,2,1} rare, {2,2,2} almost never (0/300 q=12, 1-2/300 q=15) while apex v achieves
      {2,2,2} ALWAYS (hand-proved: B monochromatic + 2/2 split on S_A).
- Interpretation: proper 3-colourings of all-singleton H are rigid near-2-colourings;
  minority-colour deviations cannot concentrate as (2,2,2) on a cross neighbourhood.
  CAVEAT: per-vertex {2,2,2} rate RISES with q (0% -> ~0.5% from q=12->15); the
  conjunction stays dead (floors 5-6) but the general-q proof must handle this.
- (FK) STATUS: survives all computational attack; the proof needs (G1) large-piece
  locking, (G2) kappa-level coverage via pair choice, (G3-theory) the near-2-colouring
  rigidity lemma for general q. ALL THREE are in gpt_fk_round3_draft_2026-06-12.md
  (final, ready to send; requires a browser session).
- Tools added: g3_random.cpp (matching + general modes), g3_counts.cpp, g3_hillclimb.cpp.
- (2026-06-12 ~18:50) 64-bit deep-sparse extension (g3_sparse64.cpp, cross-validated vs 32-bit at q=12/15): q=20 (10k) and q=25 (100k, both deficiency modes) ALL FROZEN, 0 candidates, caps negligible (33). q=30: 98% of searches hit the 5e8-node cap => INCONCLUSIVE (decided 1416 all frozen, 0 candidates) — honest gap; a CP/SAT-based witness solver would be needed beyond |V|~55. PR #4237 CI GREEN on 593085f (category-attribute fix).

# (2026-06-12 ~15:56, Claude/VSCode session) G4 PAIR-SUM SQUEEZE: PC1+PC2 derived and verified
- PC1 (three-pair impossibility): if every component of all THREE pair-graphs P_k has
  <=2 vertices then n<=4 (pure arithmetic over L1 + matching bound e(P_k)<=p_k/2;
  per-pair form 11q_k >= 5n-13+2b_k, summed with sum q=n-1, sum b=6).
  => at EVERY unfrozen v, EVERY witness has a >=3-vertex component in some pair.
- PC2 (linear mass): 11q_k + 5W_k >= 5n-13+2b_k+8R_k per k (W_k,R_k = vertices/count
  of >=3-vertex components of P_k; uses L2 + kappa>=8); summing:
  sum_k W_k >= (4n-16)/5 + (8/5) sum_k R_k — linear-in-n mass in >=3-vtx components.
- VERIFIED NUMERICALLY (pc_check.cpp, b=0 variant): full n=12 stock (7849 graphs,
  1572 witnesses) and full n=13 stock (367860 graphs, 71820 witnesses):
  0 PC1 instances, 0 PC2 violations, min slack 8/12.
- MENU GAP FLAGGED: F5's "EDGES or BIG" summary is too strong — kappa>=14 small/medium
  bipartite components (e<=3m-7: P3, C4, K_{1,3}, ..., K_{4,4} (kappa=16,m=8),
  K_{4,5} (kappa=14,m=9), and ALL m=10..17 e=3m-7 shapes) are UNCENSUSED LIVE shapes.
  PROPOSED CHEAP COMPUTE: locked-census kappa=14 (e=3m-7) and kappa=16 (e=3m-8)
  bipartite families m<=14 with the existing piece_hunt machinery (same threshold
  logic locked>=7 => dead). If they die, menu collapses to BIG-or-exceptions and
  PC1/PC2 force big components at every unfrozen vertex => strong structure for G1/G2.
- Files: g4_pairsum_note_2026-06-12.md (full derivation), pc_check.cpp.
  Round-3 draft: addendum appended to gpt_fk_round3_draft (Q2 strengthened).

# (2026-06-12 ~16:12, Claude/VSCode) HL LAW REFUTED — bridging decouples; correct mechanism is LOCAL SATURATION
- HL ("locked=0 => |C| <= kappa(C)/2", i.e. e<=2m) is an ARTIFACT of the bounded-kappa
  census window (kappa<=20). Machine-verified counterexamples (hl_check.cpp):
  (a) 2xK44 + 1 bridge: m=16, e=33=2m+1, kappa=30, locked=0;
  (b) 2xK44 + 2 bridges (2-CONNECTED — kills any per-block restatement): e=34, kappa=28, locked=0;
  (c) 3xK44 chain: m=24, e=50=2m+2, kappa=44, locked=0;
  (d) 2xK44 + 4 distinct-endpoint bridges: e=36, kappa=24, locked=0 (violation one step
      outside the censused window — the census boundary was exactly where the law stops);
  (e) 2xK44 + 8 saturating bridges (2-regular A1-A2): e=40, kappa=16, locked=8 = exactly
      the bridge endpoints.
- MECHANISM (hand analysis, machine-confirmed by (d) vs (e)): for v adjacent to a full
  K44-side B1, any witness colouring forces B1={1,1,2,2} and A1-v=colour 3 (B1 with 3
  colours kills A1-v). A cross-neighbour x of v stays colourable iff x has a free colour
  after its own block constraints; if v is x's ONLY cross-neighbour, deletion of v frees
  x => unlocked. Locking appears exactly when bridge multiplicity saturates (every
  cross-neighbour of v retains a colour-3 conflict after v's deletion).
- CONSEQUENCE for G1/G2 (large-piece theory): no global density bound characterizes free
  pieces; the usable invariant is the forced near-2-colouring rigidity around dense
  subblocks (same mechanism as the G3 freezing law). Round-3 Q1 must be restated:
  NOT "prove |C|<=kappa/2" but "quantify forced-{1,1,2,2} propagation in pieces with a
  K44-like core". Census facts remain valid as stated (per-kappa, m<=13/18 windows).
- Files: hl_check.cpp (+exe). PROGRESS.md 16:12 entries.

# (2026-06-12 ~16:50, Claude/VSCode) KAPPA=8 LAW DOES NOT EXTEND — free kappa=8 piece at m=62 (PG(2,5))
- Tick summary: TWO candidate laws refuted with machine-verified certificates, one new
  structural fact + budget-coupling consequence derived. Tool: kappa8_free_hunt.cpp.
- C1 ("every vertex of every 6-regular bipartite graph is locked") tested:
  TRUE on K66, C20/C24/C32(1,3,5) circulants, Q6 hypercube (m=64!), 9 random 6-reg
  (m=20/24/28, ALL vertices, exhaustive, NOCANON cross-validated, K44 positive control OK);
  m=40 randoms already show 6 unlockable vertices; and FALSE in the extreme:
- ** PG(2,5) incidence graph (m=62, 6-regular bipartite, girth 6): ALL 62 vertices
  unlockable ** (vertex-transitive via PGL(3,5)+self-duality; v=0 exhaustively witnessed).
  PG minus 4 spread edges = kappa=8 piece (e=182=3m-4), DIRECT all-62-vertex test:
  unlockable=62, locked=0 => FrozenFlag=0 => FREE kappa=8 piece at m=62.
  Witness colouring INDEPENDENTLY VERIFIED (verify_pg_witness.py: proper on G-0,
  trace exactly (2,2,2) on N(0)). So the m<=18 census law ("every kappa=8 piece is
  frozen") is a SMALL-m phenomenon; girth/local-tree-likeness restores colouring freedom.
  Open gap: minimal m of a free kappa=8 piece is in [19, 62].
- BUDGET COUPLING (rigorous-informal, via L2): if a pair-graph P_k consists of a SINGLE
  kappa=8 component then Sum kappa = 8 = 6q_k+8-2b_k => 6q_k = 2b_k <= 12 => q_k <= 2.
  So a big free kappa=8 piece cannot sit alone in a pair-graph unless the opposite
  colour class X_k has |X_k| <= 2 — large free pieces are throttled by the GLOBAL
  budget identity, not by intrinsic locking. G1/round-3 Q1 must be reframed as a
  joint death argument: budget identity + PC1/PC2 pair-sum squeeze + small-m censuses.
- Combined with the HL refutation (16:12 block): the entire "intrinsic large-piece
  death" hope is dead in BOTH directions (sparse: bridged-K44 free pieces with e>2m;
  dense kappa=8: PG(2,5)-4e free at m=62). The live assets are: small-m censuses
  (kappa<=20, m<=13/18), PC1/PC2 (Lean-grade arithmetic), budget identity L1/L2
  (Lean-verified), and the G3 rigidity computational evidence.
- Files: kappa8_free_hunt.cpp (modes: default battery / pg / pgdel), verify_pg_witness.py.

# (2026-06-12 ~17:18, Claude/VSCode) ** (FK) REFUTED ** — H* = PG(2,5) minus 3 disjoint edges
- (FK) ("every connected 3-colourable Delta<=6 deficiency-6 graph with >=9 vertices has a
  frozen full vertex") is FALSE. Counterexample H* = PG(2,5) incidence graph minus the
  3 vertex-disjoint edges (0,32),(7,41),(15,33) [labels: canonical F5^3 rep order]:
  connected, bipartite, |V|=62, e=183, degree profile {6:56, 5:6}, Sum b = 6.
  ALL 62 vertices (a fortiori all 56 full ones) are unfrozen: explicit witness
  colourings in fk_witnesses.txt, INDEPENDENTLY VERIFIED 62/62 by
  verify_fk_witnesses.py (proper on H*-v + trace <=2 per colour on N(v)).
  Minimal-shore side-condition kappa(X)>=8: holds empirically with slack (steepest-
  ascent hunt, 4000 restarts, all sizes 2..60: min kappa found = 10) — VERIFIED
  HEURISTICALLY; a rigorous super-6-ec proof for PG incidence graphs is a known-
  techniques exercise (girth-6 + edge-transitivity), deferred.
- CONSEQUENCE: the (FK) => "Theorem B for all shore sizes" => star-cut endgame route
  CANNOT close as designed. Theorems A+B as published (finite ranges) are UNAFFECTED.
- WHAT SURVIVES: per-vertex unfrozenness is only the ZERO-BUDGET simplification of
  shore survival. The genuine condition is ROBUST/Col-compatibility (round-2 digest,
  piece_hunt robust mode): the shore must offer, for EVERY outside boundary colouring
  gamma compatible with Col(H*) (<=3^6=729 classes here), witnesses at the relevant
  vertices matching gamma. NEW FRONTIER (next tick): formalize robust-(FK) exactly per
  round-2 and run it on H*. Outcomes: (i) H* dies robustly => correct conjecture is
  robust-(FK), route revivable; (ii) H* survives robustly => H* is a live candidate
  shore => counterexample-hunt direction (a second 4-VC-compatible structure) opens.
- GPT round-3 draft (gpt_fk_round3_draft_2026-06-12.md) is OBSOLETE in its main thrust
  (Q1/Q3 ask to prove sub-goals of a now-refuted conjecture). DO NOT SEND AS-IS.
  Banner added. Round-3 must be rewritten around the counterexample + robust-(FK).
- Artifacts: kappa8_free_hunt.cpp (mode fk), fk_witnesses.txt, verify_fk_witnesses.py.

# (2026-06-12 ~17:58, Claude/VSCode) ROBUST-(FK) ON H*: NOT ROBUST — the freezing mechanism survives at the gamma-interface
- Engine: robust_fk2.cpp (MRV + forward-checking, colour-orbit dedup: 122 canonical
  gammas, 64 threads); cross-validated by OR-Tools CP-SAT (verify_starved_cpsat.py):
  6/6 starved samples INFEASIBLE, 4/4 served controls FEASIBLE, all 26 engine-capped
  pairs decided (20 served, 6 starved). No gaps remain.
- RESULT: Col-compatibility is vacuous (all 729 gammas compatible) BUT H* is NOT
  robustly internally unfrozen: 864 starved canonical (gamma, v) pairs. Structure:
  * gamma-family A (5,11,15,32,34,38,42,46,48,86,88,92,96,100,102,113,115,119,123,
    127,129,140,142,146,150,154,156): starves the SAME 16 line-side vertices
    {31,34,35,36,39,40,43,45,48,49,53,54,55,58,59,60}.
  * gamma-family B (135..161): starves the same 15-16 point-side vertices
    {2,3,4,13,14,16,18,20,21,24,25,26,28,29,30} (+11 for 6 of them).
  * gammas 140,142,146,150,154,156 starve BOTH sides. Point/line duality visible.
- INTERPRETATION: per-vertex freezing fails (FK refuted) but its ROBUST version has
  teeth: death criterion for a completed cut (H, K, stub-matching pi) is
  EXISTS full v: Realizable(K) restricted via pi  SUBSET OF  Bad_H(v).
  Bad(v) sets are large and heavily shared across v => the mechanism is alive.
- NEXT EXPERIMENT (decisive either way): SELF-PAIRING — K = second copy of H*.
  Compute exact-trace tables Col(H*) and UnfTrace(v) = {tau in 3^6 : exists witness
  with anchor trace exactly tau}, then for each of the 720 stub-matchings check
  whether every full vertex of both copies is served by a compatible (tau_H, tau_K)
  pair. SURVIVES => candidate 124-vertex 6-regular graph with nontrivial 6-cut
  passing the freezing screen (counterexample hunt escalates: next screens =
  4-VC necessary conditions, G[N(v)] bipartite lemma, chi=4). DIES => strong
  evidence for robust-(FK) as the corrected keystone; formalize for round-3-prime.
- Files: robust_fk.cpp (v1), robust_fk2.cpp (v2 engine), verify_starved_cpsat.py.

# (2026-06-12 ~18:25, Claude/VSCode) SELF-PAIRING: ALL 720 MATCHINGS 3-COLOURABLE — the INTERFACE DICHOTOMY
- pair_tables.cpp (64 thr): exact-trace tables on H* built gapless (7686 canonical
  queries, 0 capped; orbit closure under S3). |Col(H*)| = 480/729.
  AnchorWit sizes 150/408/204/408/204/150 (point/line duality visible).
  Internal consistency vs robust_fk2 phase-B verdicts: PASS on sampled pairs.
- MATCHING SCAN (G(pi) = two copies of H* + 6 cut edges, all 720 stub-bijections):
  * 720/720 pairings give a 3-COLOURABLE G  => self-pairing can never be 4-chromatic,
    hence never 4-critical. The PG seed does NOT yield a counterexample by self-pairing.
  * Best pairing had unserved = 0: the freezing screen alone would NOT have killed it;
    the chi=4 requirement did. (Frozen-vertex and non-3-colourability are competing.)
- THE DICHOTOMY (new corrected keystone, replaces refuted (FK)):
  For a 4-critical G with nontrivial 6-cut (H, K, matching pi), criticality forces
  (a) NO avoiding pair: no tau in Col(H), gamma in Col(K) with tau_s != gamma_{pi(s)}
      for all s   [else G 3-colourable], and
  (b) every full vertex on both sides served w.r.t. the partner's realizable traces
      [else a frozen vertex kills criticality — the audited freezing argument].
  CONJECTURE (round-3-prime target): (b) for both sides implies NOT (a) — i.e. two
  robustly-served deficiency-6 shores always admit an avoiding Col pair under every
  matching => no 4-critical 6-regular graph has a nontrivial 6-cut => Theorem B for
  ALL shore sizes. Data point: H* x H* satisfies (b)-rich tables and fails (a) under
  all 720 matchings. Pigeonhole note: a single gamma blocks 665/729 traces (avoid-set
  = 2^6 = 64), so |Col| >= 666 would trivially force avoiding pairs; 480 < 666 means
  the conjecture needs structure (S3-closure + realizability), not just counting.
- NOVELTY GATE TODO before any writeup: Toft/Gallai-style decomposition of
  colour-critical graphs over small edge-cuts is classical — check whether the
  table-tension principle for 6-edge-cuts in 4-critical graphs is known; the NEW
  content here is the 6-regular zero-budget/(2,2,2) machinery + the PG refutation
  of intrinsic freezing + the explicit finite tables.
- Files: pair_tables.cpp. Next: round-3-prime GPT draft (dichotomy conjecture +
  Col(H*) data + starved structure); literature gate in parallel.

# (2026-06-12 ~18:45, Claude/VSCode) AVOID-COMPLETENESS: H* ABSOLUTELY EXCLUDED; CONJECTURE (D); ROUND-3-PRIME READY
- Avoid(Col(H*)) = [3]^6 exactly (729/729, machine-verified; label-invariant so it
  holds under every matching). Any shore of a 4-critical graph is 3-colourable =>
  partner Col nonempty => avoiding pair exists => pairing 3-colourable.
  PROVED (machine): H* is not a shore of ANY 4-critical 6-regular graph — excluded
  by table-completeness, not freezing.
- CONJECTURE (D) (corrected keystone, replaces (FK)): every minimal-shore H
  (>=15 vtcs) is EITHER branch-1 (some full vertex frozen against every
  partner-realizable trace) OR branch-2 (Avoid(Col(H)) full). (D) => Theorem B for
  all shore sizes. Evidence: all censused small pieces = branch 1; H* = branch 2.
  Proof route: classify deficient S3-closed tables (Avoid != full <=> Col subset
  Clash(gamma) for some gamma, |Clash| = 665) and show deficiency forces freezing.
- Literature gate: Gallai-Toft 1970 = separating sets of size <= k (k=3) with
  one-colour/rainbow structure; |F| = 6 = 2k regime uncovered; exactly SkSt25
  Problem 5.2 (arXiv:2508.08703). erdosproblems.com/944 still OPEN; no race signs.
- Round-3-prime draft READY: gpt_fk_round3prime_draft_2026-06-12.md (Q1 = (D),
  Q2 = Gallai-Toft extensions (k,2k], Q3 = PG-geometric Bad(v) invariant).
  Needs an interactive browser session to send (desktop lane).
- Files: pair_tables.cpp (now also prints Avoid coverage).

# (2026-06-12 ~20:22, Claude/VSCode) (D)-AS-STATED REFUTED (PG-star3); (D-prime) + (R3); n=15 CENSUS CLOSED
- STACKED SWEEP (dichotomy_sweep2.cpp, HH+MCMC generator, 40 graphs, profiles
  (2,2,2)P/(2,2,1,1)P/(3,1,1,1)P/(3,3)P/(2,2)(1,1)/(3)(3)/(2,1)(2,1) + crafted
  3x(b=2)+common-neighbour blockers): ALL branch 1. Avoid ceilings confirmed
  structural: profile with a b=3 anchor has avoid <= 567 = 729 - 162 (rainbow
  gammas at the 3 same-vertex stubs are unavoidable for EVERY graph); (3,3): 441.
- ** PG(2,5)-star3 (profile (3,1,1,1), m=62) = NEITHER ** : lockedFull=0 (witness
  survival from PG) and avoid = 567 < 729. So (D) AS STATED IS REFUTED. PG-P3+e
  (profile (2,1,1,1,1)) is still avoid-complete: the break is exactly b=3 stacking.
- CORRECTED KEYSTONE (D-prime), pairing-level: for every nontrivial 6-cut
  (H, K, pi) of a 4-critical 6-regular graph, some full vertex on some side is
  frozen OR an avoiding Col-pair exists. Salvage analysis for the PG-star3 hole:
  its unavoidable set = ONLY the 162 rainbow-at-y-stubs gammas; a partner K
  exploiting this needs Col(K) restricted to rainbow on 3 prescribed anchors =
  hyper-rigid. Supporting fact (classical): the obvious rainbow-forcer (y's three
  cut edges into a TRIANGLE of K) creates K4 <= G, and a 4-critical graph
  containing K4 equals K4 — so triangle partners are excluded outright; remaining
  rainbow-forcers are Hajos/diamond-chain gadgets. SUB-CONJECTURE (R3): a
  deficiency-6 shore whose every proper 3-colouring is rainbow on 3 prescribed
  stub-anchors has a frozen full vertex. ((R3) + spread/b<=2 avoid-completeness
  would give (D-prime) modulo the b=3 case analysis.)
- ** n=15 UNFROZEN CENSUS COMPLETE AND VALIDATED ** (n15c_q, 2750/2750 classes,
  geng-count == checker-total everywhere; runner ALL DONE 16:07, the 43 logged
  failures were transient validation races — all classes pass now):
  1,470,293,676 six-regular n=15 graphs; 2,552,562 three-colourable;
  fullyUnfrozen = 0 — NO everywhere-unfrozen 6-regular graph on 15 vertices;
  unfrozen-count histogram 0:2262609 1:252416 2:33084 3:4388 4:64 5:1.
  The unique maxUnfrozen=5 specimen lives in class 1776 (c_1776.out) — extract
  g6 later if wanted. Freezing is universal at n=15 (branch-1 world); PG world
  (m=62) is branch-2: the transition is the (D-prime) battleground.
- piece_enum: dead (process killer); NOT restarted — the FK-simulator/replacement
  route is moot after the (FK) refutation. n=16 brute force remains user-stopped.
- Files: dichotomy_sweep2.cpp (modes: default stacked sweep / pg).

# (2026-06-12 ~21:25) n=15 UNFROZEN CENSUS CLOSED (NEW FACT, triple-anchored)
- 2750/2750 classes (43 pipe-failures redone via two-stage file method, all
  gengZ==total); TOTAL = 1,470,293,676 == known n=15 6-regular count (exact).
- threecol = 2,552,562. **fullyUnfrozen = 0 — the reduced kernel ("every
  connected 6-regular 3-colourable graph has a deletion-frozen vertex") holds
  EXHAUSTIVELY through n <= 15.**
- maxUnfrozen = 5; hist: 0:2262609 1:252416 2:33084 3:4388 4:64 5:1.
  Growth: 2 (n<=13) -> 4 (n=14) -> 5 (n=15); unfrozen fraction stays ~1%.
  THE unique k=5 graph: g6 `N?r@`boN?^W]{EroFw?` set=28160 (extremal object,
  analyze its structure). All 4453 k>=3 graphs: census15_high_unfrozen.txt.
- Files: n15c_q/c_*.out (per-class, >Z-validated), queue_runner15c.ps1.

# (2026-06-12 ~22:02, Claude/VSCode) Q1b WORKFLOW VERDICT: REFUTED + SALVAGED LEMMA PROVED
- Workflow (3 independent attack agents, 2 adversarial referees each incl. a
  computational one, honest synthesis; 10 agents, all referee reports sound):
- Q1b AS STATED IS FALSE. H1 (18 vtcs): anchors form full K_{3,3} with rainbow
  bans per side. FOUR-LINE PROOF of unavoidability: cross-adjacency makes the two
  anchor colour-sets disjoint => one triple monochromatic => its rainbow ban is
  hit. Verified by 4 independent codebases with EXACT counts (0 colourings):
  q1b_counterexample.py, q1b_spread_counterexample.py, referee_q1b_check.py,
  referee2_q1b_independent.py. Second counterexample family: K33-PM anchors +
  common-neighbour blocker (the anchor system has exactly 2 solutions, both
  cyclic rainbow derangements; blocker uncolourable).
- SKELETON AUTOPSY: steps (1)-(2) correct and sharpened (parity: a_P = a_Q mod 6
  => splits 0+6 / 3+3 / 6+0); step (3) doubly false (matched edges fatal for
  EVERY nonempty matched set; the sigma=(2,0,2) hand repair had an arithmetic
  slip, sigma(2)=2=banned).
- ** SALVAGED LEMMA — PROVED ** (rigorous-informal + 650 instances x 3040
  verbatim recipe applications, 0 failures): under Q1b hypotheses the conclusion
  holds UNLESS (3+3 split) AND (both anchor triples rainbow-banned) AND (all six
  label-matching cross edges present). IN PARTICULAR: anchors pairwise
  non-adjacent => avoid-completeness ALWAYS. This explains all sweep data (random
  deficiency placement essentially never realizes the fatal pattern).
- ARCHITECTURE: the fatal pattern is HARMLESS at the pairing level — a K33-anchored
  H forces a monochromatic triple in EVERY colouring, so the partner can always
  realize a non-fatal gamma and an avoiding pair exists. Every escape route again
  funnels into partner hyper-rigidity => the (R3) family. (D-prime)-spread now =
  SALVAGED LEMMA (proved) + (R3) (open; 14/14 computational support).
- NEXT: (F-excl) check is MOOT for the pairing (above); remaining proof
  obligations: (R3)-family rigidity=>freezing, and the stacked b=2/b=3 salvage
  analogues. Round-3-prime draft updated.

# (2026-06-12 ~22:00) FK-sim stage 1: robust condition DEAD (0/878); corrected route
- fk_sim_check.cpp: all 878 cross-size groups' smallest members FAIL GPT's
  "robustly internally unfrozen" (typical: vertex with >=3 stubs + monochromatic
  outside beta => (2,2,2) impossible; also genuine deep failures). GPT itself
  flagged the condition as stronger than necessary — now PROVEN unusable on the
  entire q<=8 inventory. NEGATIVE FACT, logged.
- CORRECTED sufficient condition (my derivation from the audited composition
  lemma; sound, weaker): replacement P->Q preserves all-unfrozen if
  (a) Col(Q) = Col(P) (same canonical state — already grouped), and
  (b) for every internal q of Q there is p in P with Unf(P,p) SUBSET-OF Unf(Q,q)
      under the aligning stub bijection + colour permutation.
  Transfer argument: the host-side boundary data realizing p's witness in H is
  itself an element of Unf(P,p) subset Unf(Q,q), so it realizes q's witness in H'.
  Host vertices outside the piece keep their witnesses via Col equality.
- NEXT: fk_sim_check stage 2 = per-pair Unf-table subset test with explicit
  (sigma, pi) alignment search; run over the 878 groups. n=12 inventory 14/32
  classes done meanwhile (63.6M graphs, 840K pieces).

# (2026-06-12 ~23:50, subagent avenue-C) ** (R3') REFUTED ** — parity-compatible gadget pads
- (R3'/R3-prime) ("gadget-forced rainbow-rigid deficiency-6 shore has a frozen full
  vertex") is FALSE, including under the minimal-shore axiom kappa(X)>=8.
- COUNTEREXAMPLE K68 (canonical): PG(2,5) incidence minus 7 vertex-disjoint edges
  + diamond gadget {A,B,U,T} + path U-V-W + edge T-W, ALL six gadget vertices
  deficient (b=1 each, Sum b=6), 14 pads into the 14 capacity-1 slots under the
  SIDE-PARITY RULE (A,V pads -> line side; B,W pads -> point side; U,T anywhere),
  which guarantees the explicit colouring phi0 = bulk 2-colouring +
  (A,B,U,T,V,W)=(1,2,3,3,1,2). n=68, Delta<=6, connected, 3-colourable,
  z=(U,V,W) deficient non-triangle, rainbow-rigid (diamond forces psi(U)=psi(T);
  cadical153+glucose42 UNSAT on merge U=W), and ZERO of the 62 full vertices
  frozen — 62/62 explicit (2,2,2) witnesses, independently verified pure-Python.
  Shore axiom verified EXACTLY: min kappa over 2<=|X|<=n-2 is 8 (38k capped
  maxflows on K+; independent-side cases >=12/14 by stub bound).
- SECOND counterexample at scale: W(5)=GQ(5,5) incidence bulk (312 vtcs, girth 8):
  n=318, rainbow-rigid, 0/312 frozen, axiom EXACT (min kappa=8).
- THIRD: even F3's exact pad profile (17 pads, A,B,T full, 3 bulk stubs) with
  parity pads gives frozen counts 1/2/0 (seeds 1-3); seed 3 = full counterexample.
- MECHANISM AUTOPSY: the old 14/14 "freezing leak" (mass_sweep_r3.txt, 16-49
  frozen) was PARITY FRUSTRATION from random pad placement (every colouring forced
  colour-3 deep into the diameter-3 bulk), NOT a consequence of rainbow-rigidity.
  Lemma (proved): with parity-compatible pads, any full bulk vertex whose radius-2
  ball avoids pad-targets is unfrozen via an explicit <=15-vertex recolouring of
  phi0 (uses bulk girth>=6 only).
- CONSEQUENCE for (D-prime): the (R3)-family escape route is OPEN GROUND — a
  hyper-rigid rainbow partner CAN be everywhere-unfrozen, so the b=3-stacking hole
  cannot be closed by freezing alone; need avoid-completeness/Col-table arguments
  against these K's (note: K68's stub traces at U,V,W are PRESCRIBED-rainbow by
  construction — exactly the partner shape the PG-star3 hole requires).
- Files: experiments/sixreg/r3c/{r3c_build.py, r3c_verify.py, r3c_kappa.py,
  r3c_kappa_mp.py, inst_pg_s1.json, inst_gq_s1.json, inst_pg_s3_f3.json,
  inst_pg_s3.json, inst_pg_s4.json, kappa_pg_s1.log, kappa_gq_s1.log, gq_s1.log}.

# (2026-06-12 ~23:05) LANDMARK: LEMMA D verified n<=12 — THE problem is now ONE lemma
- ff_scan over the COMPLETE q<=8 piece inventory (2,504,198 connected 3-col
  Delta<=6 graphs with total deficit Sigma(6-d)<=8, 8<=n<=12; n=12 from 158.5M
  geng graphs, gengZ-validated): EVERY piece has a CERTIFIED-frozen vertex
  (empty Unf table => frozen in EVERY completion). 0 survivors in all 18 (n,q)
  cells. Tools: piece_enum.cpp + ff_scan.cpp (witness-existence early-exit).
- REDUCTION OF THE PROBLEM: a 6-cut shore is itself a q=6 piece. So
  LEMMA D(n) ("dense deficit<=8 + 3-col + Delta<=6 + n>=8 => certified-frozen
  vertex exists") for ALL n  ==>  (FK) for all shores  ==>  Theorem B for all
  sizes  ==>  every 6-edge-cut in a 6-regular target is a vertex star.
  D also feeds the zero-budget pincer: charge-forced kappa=8/10 components are
  q<=10 pieces; certified-frozen vertex inside any such component contradicts
  all-unfrozen hosts directly.
- Stage-1/2 today: GPT's robust condition DEAD (0/1160); Unf-subset transfer
  condition derived (sound); stage-2 found all 3371 larger same-state pieces
  host-impossible — superseded by the full sweep above.
- NEXT: GPT round 3 = prove D(n) for all n (suggest recursive charge identities
  with Sigma b = q general form); also extend inventory check to q<=10 (the
  kappa=10 case) and n=13 spot checks.

# (2026-06-12 ~23:12, Claude/VSCode) (R3-prime) REFUTED (K68, parity-pad rule); the freezing pillar collapses; criticality-locality is the real lever
- (R3-prime) workflow (3 attacks, 6 referees, synthesis; all load-bearing claims
  re-verified, incl. by my own rerun of r3c_verify.py): ** REFUTED **.
  K68 = PG(2,5) bulk minus 7 disjoint edges + diamond gadget {A,B,U,T,V,W} with
  PARITY-RULE pads (each gadget vertex's pads routed to the bulk side OPPOSITE its
  intended colour): all hypotheses hold INCLUDING minimal-shore kappa(X)>=8 with
  min kappa = 8 EXACTLY (kappa=cut maxflow reduction, proved + 2 codes + referee);
  rainbow-rigid on deficient non-triangle (U,V,W) (3-line hand proof + cadical153
  + glucose42 + CP-SAT + enumeration); ZERO of 62 full vertices frozen (explicit
  witnesses, 4+ independent verifications). Robustness: K318 (GQ(5,5)=W(5)
  incidence bulk, girth 8): 0/312 frozen. My earlier 14/14 was a RANDOM-pad
  parity-frustration artifact (even F3''s exact pad profile fails parity-routed).
- SALVAGE (proved by the workflow, kept): (R3-prime) TRUE for ALL n<=13
  (exhaustive 1.87e9-graph scan; >=2 frozen vertices in each of 10,467,772
  rainbow-rigid instances) => minimal counterexample size in [14,67] OPEN.
  Pairwise-certificate theory: forced-equal PAIRS never freeze (a pinned pair is
  a legal colour class) — only forced classes meeting N(v) THREE times do.
  Quotient characterization: rainbow-rigidity on non-adjacent pair <=>
  K/(z1=z2) non-3-colourable (core 4-critical + mandatory-leak lemma).
- ** THE COMBINATION INSIGHT **: pairing H = PG-star3 (every K-realizable gamma
  at y''s 3 stubs is unavoidable... precisely: K68 is rainbow-rigid on its stub
  triple) with K = K68, matching y''s 3 stubs to (U,V,W): every proper colouring
  of K68 puts rainbow on y''s outside endpoints => y uncolourable => G is a
  6-regular, 130-vertex graph with chi >= 4 and a NONTRIVIAL 6-CUT, passing the
  freezing screen on both sides. G is NOT 4-critical: deleting any vertex far
  from the forcing core leaves the chi>=4 certificate intact (chi(G-x)=4).
  => the (D-prime) frozen-or-avoid split is dead as components, BUT the lever is
  now visible: in a 4-CRITICAL graph the chi>=4 certificate must be destroyed by
  EVERY vertex deletion, so a cut-local certificate (interface tables blocking)
  contradicts criticality at far vertices. The correct death condition is the
  TABLE-LEVEL one (round-2 Unf framework): for every x, the post-deletion tables
  must admit a compatible (2,2,2)-pair — this is where the proof now lives.
- NEXT EXPERIMENTS: (i) workflow''s recommendation: constrained-stub variant (all
  six stubs on the z-triple, b=2 each) via r3c_build.py — decides if any frozen-
  vertex salvage remains; (ii) formalize the criticality-locality argument: a
  blocked interface + rigid core that survives deletion of any single far vertex
  CANNOT be 4-critical => quantify "certificate locality".
- Artifacts: r3c/ (inst_pg_s*.json, inst_gq_s1.json, builders, verifiers, referee/).

# (2026-06-12 ~23:55) Round 3 AUDITED + bipartite danger family FIRST DATA
- Q3 CLOSED: certified-frozen transfer lemma fully proven (permissive Unf table
  over-approximates every host witness; glue stubs AND ambient deficiency slots
  both safely free). Combined w/ 756-piece validation: RIGOROUS.
- Q1: general-deficit identities derived+audited: e_ij = 3(|Xi|+|Xj|-|Xk|) +
  (B_k-B_i-B_j+t_k-t_i-t_j)/2; full-v zero-budget: 2r+zeta = 6h+Q+2-2B_k
  (threshold B_k=(Q+2)/2; Q=6->4 consistent). HONEST: identities alone do NOT
  prove D — balanced witnesses (B=(2,2,2) etc.) evade the squeeze.
- RIGOROUS conditional theorem: host containing induced connected q<=8 piece of
  size 8..12 has a frozen vertex. Contrapositive: an all-unfrozen D-counterexample
  with n>12 is LOCALLY SPARSE: every induced connected P, 8<=|P|<=12, has
  e(P) <= 3|P|-5 (minimal shores: kappa(P)>=10 at sizes 8-12, beats kappa>=8).
- Q2 danger family: large 6-regular BIPARTITE (locally tree-like; witness <=>
  3-colouring of other side w/ N(v) balanced + all other N(a) non-rainbow;
  infinite 6-regular tree HAS local witnesses => finite quotients must be ruled out).
- FIRST DATA on the danger family (exhaustive, geng -b): n=14: 1 graph, n=16: 7,
  n=18: 157 — ALL vertices frozen in ALL of them (maxUnfrozen=0!). The family is
  maximally frozen at small n. n=20 (16 workers) running.
- NEXT: n=20 bipartite results; then high-girth large bipartite constructions
  (incidence graphs); GPT round 4 = prove "6-regular bipartite => some vertex
  frozen" (the hypergraph isolation property) as D's hardest case.

# (2026-06-13 ~00:22, Claude/VSCode) CONSTRAINED-STUB DECIDED: freezing route FULLY dead; TRACE-HYPO-RIGIDITY is the programme decisive object
- b2 experiment (all six stubs on U,V,W with b=2, parity-pads, 6 instances m=68):
  6/6 rainbow-rigid with |Col| = 6 (MAXIMALLY rigid interface — unique trace up
  to colour permutation) and lockedFull = 0/65. Combined with K68/K318: no
  freezing salvage remains in ANY stub profile on flexible parity-routed bulks.
- THE LEVER, formalized: a 4-critical G with nontrivial 6-cut needs, for EVERY
  vertex x, that G-x is 3-colourable; with a blocked interface this means every
  single deletion must UN-BLOCK the table compatibility. Bulk deletions in our
  specimens do not (rigidity is gadget-local). Hence the shore of a critical
  graph must be ** TRACE-HYPO-RIGID **: Col(K) blocking-rigid, yet Col(K - x)
  flexible (admits a compatibility-restoring trace) for every x in K. This is
  the exact shore-level analogue of 4-criticality, in the round-2 Unf/Col
  language, and it subsumes all of today''s refuted conjectures as necessary
  conditions. EXISTENCE QUESTION (decisive both ways): does a trace-hypo-rigid
  deficiency-6 Delta<=6 shore exist? NO => Theorem B for all shore sizes.
  YES => serious counterexample seed. Cheap per-vertex test: does K-x admit a
  non-rainbow trace on the z-triple?
- NEXT: (i) hypo-rigidity scanner (per-x rigidity test) — run on K-b2/K68 to
  quantify how far from hypo-rigid (expect: only gadget-adjacent x un-block);
  (ii) structure theory: rigidity core = 4-critical quotient M (workflow salvage
  lemma) — hypo-rigidity needs M to "move" under every deletion, i.e. cores
  covering all of K: tension with e(M) <= 3h-1 + Delta<=6 + deficiency budget;
  (iii) GPT round-3-prime draft is CURRENT through ADDENDUM 6; add ADDENDUM 7 =
  trace-hypo-rigidity formulation (the final form of the question).

# (2026-06-13 ~00:30) FALSIFICATION: Lemma D (general) is DEAD — PG(2,5) counterexample
- **THE INCIDENCE GRAPH OF PG(2,5) (31 points + 31 lines, 6-regular bipartite,
  girth 6, n=62) IS ALL-UNFROZEN.** Verified TWICE independently (pg25_test.cpp
  witness search; verify_pg25.py builds graph from scratch, finds witnesses for
  v=0 (point) and v=31 (line), verifies properness + (2,2,2) counts directly;
  point- and line-transitivity covers all 62 vertices).
- Consequences (honest):
  (1) Lemma D in its general form (q<=8 including q=0, all n) is FALSE.
  (2) The whole-graph kernel ("every connected 6-regular 3-col graph has a
      frozen vertex") is FALSE for n=62 — the n<=15 exhaustive truth was a
      small-size artifact. GPT's round-3 danger shape (locally tree-like
      bipartite) materialized exactly.
  (3) For full vertices, [K]-shortfall-0 == unfrozen, so the bare (FK)
      frozen-vertex route CANNOT exclude large shores by itself. Theorem B's
      a<=14 exhaustive exclusion stands, but its (FK)-style extension to ALL
      sizes is dead WITHOUT additional ambient constraints.
  (4) STILL ALIVE: the conditional locally-sparse theorem (PG(2,5) satisfies
      e(P)<=3|P|-5 — consistency check passed); the D<=12 inventory facts;
      Theorems A,B as published; the [C] boundary-vector filter and the AMBIENT
      4-VC/partner-shore constraints, which D never used — the corrected
      frontier must use them.
- NEW VERIFIED FACT for the note (writeup v4 candidate): explicit obstruction
  showing the boundary-shortfall method has a fundamental size barrier; the
  unique-intersection (girth-6) geometry defeats the (2,2,2) freeze mechanism.
- NEXT: GPT round 4 = report falsification; ask which ambient constraints
  (4-vertex-criticality of the whole target, [C] equality-case boundary vectors,
  partner-shore matching, parity) can exclude PG-type shores; test whether a
  deficit-6 PG(2,5) variant passes the FULL [B][C][T][K] battery as a shore
  candidate (enum_shore certs mode, 62 vertices — needs MAXN>32 port).

# (2026-06-13 ~00:55, Claude/VSCode) QUOTIENT-DESCENT: the cleanest formulation yet
- Workflow salvage lemma (proved): difference-rigidity on a non-adjacent pair
  z1,z2 <=> the quotient K/(z1=z2) is non-3-colourable, and a minimal such core
  M is 4-VERTEX-CRITICAL. Trace-hypo-rigidity then says: M is 4-critical AND its
  criticality must extend through ALL of K (every deletion un-blocks).
- DESCENT CORRESPONDENCE: a nontrivial 6-cut in a 4-critical 6-regular G yields
  shores whose rigidity cores are 4-critical graphs with degree profile
  "Delta<=6 except merged vertices" and size < |G|. Conversely, candidate shores
  arise from SPLITTING vertices of smaller 4-critical Delta<=6-ish graphs.
  Sanity check PASSED: the 12-vertex shore family (n13graph - v, six degree-5
  stubs at N(v)) is exactly the smallest split family, and it is already
  excluded by Theorem B (shores >= 15) — consistent with a=12 scans.
- PROOF SHAPE for Theorem B all sizes (minimal-counterexample descent): G a
  minimal 4-critical 6-regular graph with a nontrivial 6-cut; show the cut
  produces a 4-critical Delta<=6-ish quotient SMALLER than G with enough
  regularity to contradict minimality or the n<=14 classification (unique n13
  graph). This is the |F| = 2k = 6 analogue of the Gallai-Toft |F| <= k
  decomposition — exactly the literature gap identified at 18:44.
- The hypo-rigidity scanner (b2 scan mode) quantifies how far our specimens are
  from criticality-compatibility: expected result = only gadget-adjacent
  deletions unblock => deeply NOT hypo-rigid.

# (2026-06-13 ~01:18, Claude/VSCode) HYPO-SCAN CALIBRATED; DESCENT-CORE HUNT IS THE NEXT COMPUTE TARGET
- Scanner (b2 scan): 6/6 instances blocked = 62/65 — only deleting the gadget
  interior (A,B,T) breaks rigidity; the rigidity core is exactly the 6-vertex
  gadget. Cheap per-candidate criticality-compatibility test now exists.
- DESCENT-CORE TARGET: hypo-rigid shore <=> a 4-critical quotient core spanning
  ALL shore vertices <=> a 4-vertex-critical graph with profile "Delta<=6 plus
  one merged vertex of degree <= 8 (b=2 split) or <= 10 (b=1 split)" and a
  deficiency-2..4 budget, sizes 14..66. n=14 SIX-REGULAR is closed (Theorem A)
  but the near-regular profile is OPEN — adaptable to the existing geng +
  check_g6_v2 pipeline (degree-bounded geng + 4-VC check + neighbourhood-
  bipartite prefilter). NO such core <= n for growing n pushes the minimal
  hypo-rigid shore (hence any nontrivial 6-cut) upward; a found core = the seed
  for a genuine candidate cut. This unifies the day''s entire arc back onto the
  established enumeration machinery.
- GPT round-3-prime draft (through ADDENDUM 7) remains READY TO SEND.

# (2026-06-13 ~02:32) Descent-core hunt: blanket enumeration INFEASIBLE; apex-generator is the design
- geng -u on the blanket near-regular class (n=14, d5:D8, e=42:43) does not finish
  even mod-6400 chunks in 9-minute waves at 55-parallel: weeks-scale => dead as a
  brute-force target (vs 21.6M for the 6-regular class — the relaxation explodes).
- Correct design (morning task): exact target profiles only ({8,5,5,6^11},
  {8,4,6^12}, {10,5^4,6^9} e=42; from the split correspondence), generated by
  APEXING: enumerate 13-vertex degree-constrained bases with geng (much smaller),
  attach the excess vertex to the 8 (or 10) deficient base slots; prefilter with
  the proven 4-VC necessary conditions (all G[N(v)] bipartite; mindeg >= 3).
  GPT round-3-prime Q-B may further constrain the core structurally before any
  big run is committed.

# (2026-06-13 ~01:30) Round 4 audited + TEST A DECIDED: one-shore exclusion is DEAD
- Round-4 audited results (all checked): Lemma 1 (bipartite [C] classification:
  only 3+3-one-side or 3-each-side possible; subset-sum argument VERIFIED);
  Corollary (PG minus 3 ordinary edges ALWAYS violates [C]); the 3+3 LOOPHOLE
  ([C] automatic when support = two b=3 vertices); Lemma 3 ([C]-Kempe transfer
  table: (2,2,2) colourings force ALL Kempe components balanced, etc. — audited);
  strategy ranking: partner-shore matrix rigidity is now Rank 1.
- TEST A (PG-repair surgery: delete 3 edges at point p + 3 at line l, rematch
  the 6 unit deficits via non-incidences; b(p)=b(l)=3): TWO instances tested
  (p0/l10, p7/l22): all 60 full vertices have explicit [K] witnesses; the two
  b=3 vertices pass [K] by HAND PROOF (bipartite 2-colouring + recolour one
  neighbour to colour 3 => shortfall 3 <= 3, valid for every instance).
  [T] passes (checked). [C] automatic. [B] trivial.
  ==> **A 62-vertex shore candidate passes the ENTIRE one-sided battery
  [B]+[C]+[T]+[K]. One-shore exclusion cannot extend beyond bounded sizes.**
  (kappa>=8 minimality not yet machine-checked; PG connectivity makes it likely.)
- MY OBSERVATION for round 5 (Test B pre-empted): "two triples always rainbow"
  is REALIZABLE — e.g. each triple a triangle in the partner shore; moreover a
  triangle-pair partner with six b=1 units passes [C] automatically (each
  triangle rainbow => (1,1,1)+(1,1,1) = (2,2,2) every colouring). So boundary-
  state arguments alone do NOT close the 3+3 loophole; the remaining wall is
  GLOBAL: chi(G)=4 + vertex-criticality of the ASSEMBLED graph (and kappa
  minimality). Round 5 must target: can PG-repair + triangle-partner assemble
  into a 4-vertex-critical 6-regular graph? If yes => COUNTEREXAMPLE to Problem
  5.2 (!); if provably no => the criticality obstruction is the theorem.
- NOTE: pg_repair_test.cpp's "ALL 62 PASS" print is misleading (CAP-unresolved
  deficient vertices) — superseded by the hand proof above; fix print later.

# (2026-06-13 ~02:30) NEW THEOREM: Lemma E (pair-rigidity) — PG-repair EXCLUDED; 3+3 dichotomy
- **LEMMA E (proven, rigorous-informal; my derivation, audited against
  SHORE_MACHINE.md semantics).** G a 6-regular (4,1)-graph, 6-cut with A-side
  deficiency concentrated 3+3 at p != l (cut edges: p->T_p, l->T_l in B, |T|=3).
  (i) If A is PAIR-RICH (every (c_p,c_l) in [3]^2 realized by some proper
      3-colouring of G[A]), then chi(G)>=4 forces EVERY proper colouring of
      G[B] to make T_p or T_l rainbow ["rainbow-forcing"];
  (ii) rainbow-forcing makes every v in A\{p,l} non-critical (restrict a
      colouring of G-v to intact B; the rainbow triple blocks p or l).
  ==> A (4,1)-graph admits NO pair-rich 3+3 shore.
  Proof steps verified: composition of colourings across the 6 cut edges only
  meets p,l; restriction argument; both directions checked.
- **S3-ORBIT DICHOTOMY (corollary).** The realizable pair-set S of A is closed
  under simultaneous colour permutation; S3-orbits of [3]^2 are diag/offdiag.
  So every 3+3 shore of a (4,1)-graph is DIAGONAL (phi(p)=phi(l) in EVERY
  colouring) or ANTI-DIAGONAL (always different — "virtual adjacency").
  Bipartite A: the 2-colouring gives different colours => diagonal impossible
  => **bipartite 3+3 shores must enforce virtual adjacency p~l in every
  colouring.** Combined with round-4 Lemma 1 (bipartite [C] => 3+3 only):
  the ENTIRE bipartite shore case reduces to: can a colour-rich (locally
  tree-like) bipartite graph virtually-adjacent two deficient vertices?
  (Intuition: NO for girth-6/tree-like — contraction p*l should stay 3-col.)
- **COMPUTATION: PG-repair instance (p=0,l=10,seed944) is PAIR-RICH 9/9**
  (8 explicit colourings via pair_richness.py + (2,0) closed by colour
  symmetry from (0,1)). ==> PG-repair is NOT a valid (4,1)-shore. The
  one-shore battery gains the criticality filter **[P]: 3+3 shores must be
  pair-poor (diagonal or anti-diagonal)** — kills the whole pair-rich family.
- NEXT: round 5 to GPT = present Lemma E + dichotomy; request proof that
  locally tree-like bipartite graphs cannot enforce virtual adjacency
  (anti-diagonal rigidity) between two b=3 vertices => closes bipartite case
  entirely; then the non-bipartite spread case via Kempe rigidity (round-4
  Lemma 3). Also: bring kappa>=8 check for PG-repair (moot now but tidy).

# (2026-06-13 ~02:50) **THEOREM C (BIPARTITE EXCLUSION) — PROVED.** Half-page, elementary.
In a 6-regular (4,1)-graph, NO shore of a nontrivial 6-edge-cut is bipartite.
PROOF CHAIN (each step audited):
 1. Bipartite shore A must satisfy [C] => (round-4 Lemma 1, subset-sum argument)
    deficiency is concentrated as two b=3 vertices p,l.
 2. LEMMA E (this session, proved): pair-rich 3+3 shores are impossible
    (pair-rich + chi>=4 => partner rainbow-forcing => all v in A\{p,l}
    non-critical). Realizable-pair set S is S3-closed and nonempty =>
    S = diagonal orbit or off-diagonal orbit.
 3. p,l on DIFFERENT sides: the bipartition 2-colouring realizes an off-diagonal
    pair => S = off-diag => anti-diagonal rigidity <=> H/{p=l} not 3-colourable.
    But delete the merged vertex: H minus {p,l} is bipartite, 2-colour it, give
    the merged vertex the third colour => H/{p=l} IS 3-colourable. Contradiction.
 4. p,l on the SAME side: 2-colouring realizes a diagonal pair => S = diag <=>
    H + edge pl not 3-colourable. Delete p: bipartite, 2-colour, p gets colour 3
    => 3-colourable. Contradiction.
 QED. (Steps 3,4 are the one-vertex-deletion-leaves-bipartite trick.)
- STATUS: rigorous-informal, ready for write-up as Theorem C in the note (v4) +
  Lean-checkable core (Lemma E composition argument + the bipartite trick).
- Consequence: PG(2,5)-repair and ALL locally-tree-like bipartite candidates are
  permanently excluded. Remaining open: NON-bipartite colour-rich shores
  (odd cycles allowed) — round-5 Q2/Q3 (diagonal case via H+pl density? KY?)
  and the spread-deficiency Kempe rigidity.
- Verifiable new facts this cycle: Lemma E + S3 dichotomy + pair-richness
  computation (9/9) + THEOREM C. stall=0.

# (2026-06-13 ~05:46, Claude/VSCode overnight) n=14 SINGLE-MERGE DESCENT-CORE PROFILES: ALL EXCLUDED
- core_hunt.cpp (modes p1/p2/p2b/p3), apex-generator over geng degree-bounded
  bases, 55-parallel waves, every chunk >Z-validated (totals match exactly):
  * {8,5,5,6^11}: bases 41,386,386 (= independent -u count), 1.86e9 apexings,
    P1(bip-nbhd) 71.0M, chi>=4: 68,689,922, CRITICAL: 0
  * {8,4,6^12} via {4,5^8,6^4} bases: 669,086,840 profile bases, chi>=4 25.0M,
    CRITICAL: 0;  via {3,5^7,6^5} bases: 554,863,039, chi>=4 55.4M, CRITICAL: 0
  * {10,5^4,6^9}: 3.20e9 profile bases, 11.43e9 apexings, chi>=4 13,485,361,
    CRITICAL: 0
- THEOREM-GRADE (computational): no 4-vertex-critical graph on 14 vertices has
  any single-merge descent profile. Via the descent correspondence this excludes
  trace-hypo-rigid shores whose single-merge quotient has 14 vertices — the
  first rung of the descent ladder beyond Theorem A. (~30 billion candidates.)
- MORNING TASKS: (1) formalize the descent correspondence (which merge shapes
  cover ALL hypo-rigid shores of size 15; multi-merge / different split
  geometries); (2) send GPT round-3-prime (draft final through ADDENDUM 7);
  (3) extend hunts to 15-vertex quotients if the correspondence demands.
- Tools: core_hunt.cpp; data dirs core_hunt{1,2,2b,3}/ (chunk stats + gerr).

# (2026-06-13 ~03:20) ROUND 5 AUDITED — Theorem C proof CORRECTED & COMPLETED; frontier = diagonal case
- Lemma E: GPT audit VALID (+ |A|>=3 automatic: a=2 needs e=3, impossible).
- **MY THEOREM C PROOF HAD A GAP** (merge-trick fails when p,l ADJACENT: contraction
  creates a loop). FIXED by GPT's stronger ANTI-DIAGONAL KILL LEMMA, which I
  verified computationally: among the 21 cut matrices, row sums (3,3,0) admit
  ONLY 111/111/000 (both triples rainbow in EVERY partner colouring => Lemma
  E(ii) blocking) and (6,0,0) admits ONLY 222/000/000 (union balanced).
  [Python check vs the 21-matrix list: counts 6/3/9/3 by row type — exact.]
- **COMPLETED THEOREM C (corrected route):** bipartite shore => [C] => 3+3 (L1);
  p,l nonadjacent => pair-rich (explicit colourings, audited) => dead by Lemma E;
  p,l adjacent => anti-diagonal => dead by matrix-rainbow blocking. QED.
- **GENERAL 3+3 COROLLARY: every 3+3 shore must be DIAGONAL** (phi(p)=phi(l)
  in every colouring; equivalently H+pl is 4-chromatic, i.e. A is a
  "deleted-critical-edge equality gadget").
- Q2 honest: Kostochka-Yancey density CANNOT close the diagonal case (e=3n-2 is
  far ABOVE the 4-critical lower bound (5N-2)/3 — wrong direction; verified).
  Diagonal gadgets exist in general (J-xy for 4-critical J). The shore-specific
  structure (e=3a-3 exact + Delta<=6 + kappa>=8 + partner-balance) is the wall.
- DIAGONAL-CASE STRUCTURE (next frontier, Rank 1): A forces p=l; row vector
  always (6,0,0) => partner B must make T_p u T_l BALANCED (2,2,2) in EVERY
  colouring; criticality on A-side => for every v in A\{p,l} SOME B-colouring
  has union (2,2,2) with NEITHER triple rainbow. Finite boundary-state problem
  on 6 labelled stubs — enumerate B-side states (piece_state machinery applies).
- Spread case (non-3+3): [C]-Kempe transfer table (rigorous): weight-1/2 packets
  immobile, (2,2,2)-colourings fully balanced, transfers only 0/3/6. Missing:
  reducibility conclusion.
- Verifiable new facts this cycle: anti-diagonal kill (verified), Theorem C
  completed-corrected, matrix uniqueness checks. stall=0.

# (2026-06-13 ~04:15) DIAGONAL-CASE CASCADE (my derivations, from verified matrix facts)
Setting: A concentrated 3+3 shore (hence DIAGONAL by cor:diag). Cut matrix
M(alpha,beta), rows=A-classes, columns=B-classes, m_ij=(R_i+C_j-2)/3.
- (D1) A diagonal => row sums ALWAYS (6,0,0). Then integrality: R_i in {6,0},
  6=0 mod 3 => all C_j = 2 mod 3, sum 6 => **C = (2,2,2) FORCED in EVERY pair
  of colourings**: the partner B is "ALWAYS-BALANCED" (deficiency-weighted
  vector exactly (2,2,2) in every proper colouring of G[B]).
- (D2) => B has NO vertex with b >= 3 (a b>=3 vertex puts >=3 in one class).
  So when A is 3+3, B's deficiency profile has parts <= 2. COROLLARY: a 6-cut
  cannot have BOTH shores concentrated 3+3.
- (D3) Always-balanced B + round-5 Kempe table: every Kempe component of every
  B-colouring is deficiency-balanced (transfer 0 only).
- (D4) Criticality (round-5 Sec 5, audited): for every v in A\{p,l}, some
  B-colouring has union balanced but NEITHER triple T_p, T_l rainbow.
  My triangle observation: if T_p's three endpoints force rainbow in every
  colouring (e.g. a triangle), all A\{p,l} vertices are non-critical => dead.
  So B must be always-balanced IN TOTAL while EACH triple stays flexible —
  balance must be enforced ACROSS the triples, never within.
- FRONTIER QUESTION (round 6): does there exist a graph B (Delta<=6, e=3b-3,
  deficiency parts<=2 summing to 6) that is always-balanced with both triples
  flexible? Candidate obstruction: Kempe-balance (D3) + flexibility seem to
  pull in opposite directions. Note Theorem B forces |A|,|B| >= 15 anyway.

# (2026-06-13 ~05:05) Round 6 audited — diagonal frontier EXACTLY defined
- D1-D4 ALL VALIDATED. D1 simpler proof (GPT): diagonal A => cut matrix has one
  nonzero row r; D_pi = m_{r,pi(r)} = 2 for all pi => row = (2,2,2) directly.
- MY INCOMPATIBILITY INTUITION REFUTED: H9 = K_{3,3,3} minus rainbow 3-matching
  (the a=9 near-miss!) is ALWAYS-BALANCED with BOTH triples never-rainbow
  (colouring-rigid: classes = parts always; T_p={x0,x1,y0} ~ X,X,Y). So
  always-balanced + flexibility is satisfiable; diagonal case does NOT die at
  D1-D4. (H9 itself is no B-side: B must pass [K] as a shore — H9 fails it —
  and Theorem B forces |B|>=15.)
- AUTOMATICITY results (cheap consequences of always-balanced, both audited):
  (i) chi(G)>=4 free: common missing colour impossible (union count 2);
  (ii) MY NEW: cut-edge non-criticality at p/l-side edges free: c missing from
  T_p\{t} => count_c(union)=2 forces c in beta(T_l) (since [beta(t)=c]<=1).
- EXACT REMAINING SYSTEM for a diagonal 3+3 assembly (all sizes >= 15):
  (S-A) A: diagonal equality gadget passing shore filters; for every
        v in A\{p,l}: terminal-pair set R_A(v) nonempty matching (S-B2);
  (S-B1) B: shore passing [B][T][K] with [C] in always-balanced mode;
  (S-B2) for every w in B: B-w has a colouring creating a COMMON missing
        colour for the (possibly reduced) triples [B-side criticality];
  (S-K) every bicolour Kempe component of every B-colouring deficiency-balanced.
  Tension: (S-B2) unlock-on-vertex-deletion vs (S-K)+always-balanced rigidity.
- Spread-case structure theorem (audited): with parts<=2, transfers of 3 need
  multi-vertex Kempe packets; support pairs off through balanced Kempe chains
  in every colouring; always-balanced (2,2,2)-profile: the three weight-2
  vertices pairwise share bicolour Kempe components in EVERY colouring.
- STATUS: frontier exactly defined, finite-state, sizes >= 15. Next moves:
  (a) consolidation + RESEARCH_LOG; (b) Lean port of Theorem C / Lemma E core;
  (c) boundary-state enumeration design for (S-B1/B2) on abstract pieces.

# (2026-06-13 ~06:40) Diagonal-partner probe: always-balanced graphs are ABUNDANT
- always_balanced.cpp over shore-shaped graphs (conn, Delta<=6, e=3n-3, sum b=6,
  3-col): always-balanced count GROWS ~x35/step — n=9:4, n=10:22, n=11:795,
  n=12:30554. Profiles seen: 222, 1122, 11112, 111111 (all parts<=2, as D2 forces).
  The a=9 case includes HEzftz{ = K_{3,3,3}-minus-rainbow-matching (the published
  near-miss). VERIFIABLE NEW FACT (counts). stall=0.
- IMPLICATION: the all-sizes diagonal case CANNOT be closed by "always-balanced is
  rare" — the candidate space is large. All 30554 (n=12) are already killed by
  [T]/[K] in the published a<=14 exhaustion (0 survivors). So the all-sizes lever
  is the STRUCTURAL S-B2 (B-side criticality unlock on vertex deletion) vs S-K
  (every bicolour Kempe component deficiency-balanced) tension, NOT enumeration.
- NEXT EXPERIMENT (named): test whether always-balanced + S-K rigidity is even
  compatible with B-side criticality unlock at the assembly level — needs the
  cut-triple labelling (T_p,T_l partition of the 6 endpoints), so it is an
  assembly/boundary-state test (piece_state machinery), not a B-only test. Defer
  to a focused build; meanwhile Theorem C stands as the session's banked result
  (Lean core in PR #4237, note v4).

# (2026-06-13 ~06:55) STRONG LEVER: always-balanced => some B-vertex never unlocks (n<=11)
- diag_unlock.py: among ALL always-balanced shore-shaped B on n=9,10,11
  (821 graphs total), criticalityFeasible = 0. I.e. for NO always-balanced B and
  NO 3+3 split of the six cut units does EVERY vertex w in B "unlock"
  (= G-w 3-colourable, with diagonal A forcing p=l=c needing c absent from the
  cut-union after deleting w). VERIFIED NEW FACT. stall=0.
- LOGIC (rigorous-informal, audited): A diagonal => p=l in every colouring of A
  (intact in G-w) => G-w 3-col iff B-w has a colouring with some colour absent
  from T_p u T_l (minus w's units). Test ranges over ALL splits (most permissive),
  so feasible=0 => B excluded under EVERY assembly. Some w in B is non-critical
  => G not vertex-critical => not a (4,1)-graph.
- CANDIDATE THEOREM (the diagonal closer): "every always-balanced B (conn,
  Delta<=6, e=3|B|-3, sum b=6) has a vertex w such that every proper 3-colouring
  of B-w keeps all three colours present on the six cut units" => no 3+3 diagonal
  partner exists => (with Cor diag + Theorem C) NO concentrated 3+3 shore exists
  in a 6-regular (4,1)-graph, at any size.
- CAVEAT: n<=11 only (Python; n=12 needs C++ port — 30554 always-balanced graphs).
  All-sizes needs proof. Likely interior full vertices far from deficiency are the
  perennial non-unlockers (the (2,2,2) cut-weight is too rigid to break by one
  deletion). Sent to GPT for an all-sizes argument.
- NEXT: (a) C++ port of diag_unlock for n=12,13 confidence; (b) GPT consult on the
  candidate theorem; (c) if it holds, the concentrated case is fully closed and
  only the SPREAD case (parts<=2 but not 3+3) remains for the all-sizes program.

# (2026-06-13 ~06:25) diag_unlock SPLIT-INDEPENDENCE + C++ port
- KEY SIMPLIFICATION: the unlock condition is SPLIT-FREE. p=l=c needs c absent
  from colours(T_p) AND colours(T_l); since T_p u T_l = all 6 cut units, this is
  "c absent from all 6 units" — independent of the 3+3 split. So
  "feasible for some split" == "all w unlock" (unconditional). The candidate
  theorem is therefore split-free: every always-balanced B has a vertex w with
  no B-w colouring leaving a colour off the 6 units.
- C++ port diag_unlock.cpp matches Python EXACTLY on n=9/10/11 (4/22/795 always-
  balanced, 0 feasible). n=12 launched (32 workers, mod-32, 32.8M graphs, ~30554
  always-balanced expected) to extend confidence.

# (2026-06-13 ~06:27) diag_unlock n=12 CONFIRMED: criticalityFeasible = 0
- n=12: total=32,833,744 (=gengZ, validated), alwaysBalanced=30554 (matches
  always_balanced.cpp exactly), criticalityFeasible=0. Candidate theorem holds
  through n<=12: all 31,375 always-balanced graphs (4+22+795+30554) have a
  non-unlocking vertex => none is a diagonal partner. STRONG verified evidence.
  stall=0. (n=13 next if needed; ~1.8e9 graphs, chunked.)

# (2026-06-13 ~06:35) STRUCTURE of non-unlockers — unlocking is GENERIC-RARE
- nonunlock_type.py (n=9/10/11): the candidate theorem holds with HUGE margin.
  Per-graph non-unlocker COUNT is large: most always-balanced B have MOST vertices
  non-unlocking; several have ALL N (n=9: a 9/9 graph; n=11: 11/11 graphs).
  MIN non-unlockers per graph: n=9:6, n=10:3, n=11:4 — always >=3.
- Non-unlockers are BOTH full-interior (b=0, ~60%) and support (b=1, ~40%): not a
  single structural type. So "unlocking" (criticality) is the RARE event, not the
  failure. Reformulation: w unlocks <=> B-w has a colouring pushing some colour
  entirely off the 6 units; given always-balanced rigidity (every B-colouring is
  (2,2,2), all bicolour Kempe components deficiency-balanced), this needs a
  colouring of B-w NOT extending to B that also concentrates deficiency off one
  colour — a strong, rarely-met requirement.
- PROOF DIRECTION (for me + GPT round-7): don't hunt one special vertex; show the
  unlock set is a proper subset, e.g. |unlock set| <= |V|-3, via: Kempe-balanced
  components (round-6) + the fact that a single vertex deletion frees at most a
  bounded amount of the (2,2,2) rigidity. Candidate stronger claim: a full vertex
  whose deletion leaves B-w with the same colouring-projection on the support
  cannot unlock. VERIFIED NEW FACT (the counts). stall=0.

# (2026-06-13 ~06:33) d_u=9 PROFILE CLOSED — n=14 single-merge descent table COMPLETE
- run_du9_py.py (fork-safe Python ThreadPool->CreateProcess; replaces the xargs -P64
  bash driver that fork-bombed Git-bash at 0xC000026B / 2488 shards): 18,300/18,300
  shards VALID (read==>Z each), fails=0, read=17,663,716,608 graphs, apexings=
  13,829,527,706, P1pass=169,120,035, P2pass=157,283,764, **P3pass=0, SURVIVORS=0**.
- WITH the earlier profiles (d_u=6 = Theorem A closed; d_u=7 {7,5,6^12} P3=0;
  d_u=8 {8,5,5,6^11}+{8,4,6^12} P3=0; d_u=10 {10,5^4,6^9} P3=0), the n=14
  SINGLE-MERGE descent table is now FULLY CLOSED: ZERO 4-vertex-critical graphs in
  ANY single-merge descent profile at n=14, across ~30 billion candidates, every
  chunk >Z-validated.
- VERIFIABLE NEW FACT (computational). stall=0.
- INTERPRETATION (PENDING AUDIT, do NOT over-claim): via the descent correspondence
  this should exclude trace-hypo-rigid shores whose SINGLE-MERGE quotient has 14
  vertices. OPEN COVERAGE QUESTION (morning task #1): does single-merge n=14 closure
  exclude ALL size-15 hypo-rigid shores, or is there a multi-merge / size-15-quotient
  coverage gap? This determines whether the d_u closure is a real theorem-rung or a
  partial result. Adversarial coverage audit launched.

# (2026-06-13 ~07:00) ROUND 7 AUDITED — APEX EQUIVALENCE; diagonal case is HARD-FRONTIER
- GPT apex equivalence (VERIFIED exact + cross-checked): for always-balanced B,
  set F = B + apex z (z joined to support S). Then F not 3-col (z sees (2,2,2)),
  F-z=B 3-col, and F-w 3-col <=> B-w unlocks. So:
      B criticality-feasible  <=>  F is 4-vertex-critical.
  All-distinct (profile 111111, |S|=6): F is 6-REGULAR. Hence the candidate
  theorem (all-distinct) <=> "in every 6-regular 4-VC graph the critical edges
  cover every vertex (form an edge cover)" [via singleton lemma: z has no
  incident critical edge <=> N(z) splits (2,2,2) in every colouring].
- CROSS-CHECK (verify_apex_G13.py): the unique n=13 6-regular 4-VC graph G13 has
  critical edges = a Hamilton cycle = EDGE COVER (13/13 covered, 2-regular single
  cycle). So no apex z qualifies => diag_unlock feasible=0 at |B|=12 is FORCED by
  Theorem A. My diag_unlock computation was re-deriving Theorem A, not an
  independent lever.
- HONEST OBSTRUCTION (dead-end-protocol legitimate output): the diagonal 3+3 case
  does NOT have an elementary all-sizes closure. It is EQUIVALENT to a strong open
  statement about 6-regular 4-VC graphs (critical edges form an edge cover; for
  minimal kappa, additionally F-z internally super-6-edge-connected) — i.e. tied
  to Problem 5.2's own frontier. No short Kempe/parity proof exists. Extending it
  is the SAME as extending Theorem A to n>=16 (the exhaustive hunt the user
  deprioritized as infeasible to n=29).
- Q3 spread: one-apex model works only for always-balanced spread (same test).
  General spread [C] (vectors (6,0,0)/(4,1,1)/(3,3,0)/(2,2,2)) needs a boundary-
  constraint automaton (piece_state machinery), not one apex.
- NET SESSION POSITION: ELEMENTARY structural gains banked = Theorem C (no
  bipartite shore) + the reduction chain (pair-rich/anti-diagonal kills;
  diagonal => always-balanced => apex-criticality). Theorem C is the genuine new
  result (Lean core in PR #4237, note v4). The concentrated-diagonal and spread
  all-sizes closures are OPEN-HARD (= Problem 5.2 frontier). Track remains alive
  but the diagonal sub-route is correctly classified as hard, not a quick win.

# (2026-06-13 ~07:05) COVERAGE AUDIT VERDICT (multi-agent, high-confidence) — d_u closure is COMPUTATIONAL, not a rung
- VERIFIED-RIGOROUS (keep): P3pass=0 across ALL single-merge n=14 descent profiles
  d_u in {6,7,8,9,10}, ~30e9 candidates, every chunk >Z-validated. core_hunt.cpp
  testApex P1/P2/P3 logic confirmed; Theorem A is 6-regular-ONLY.
- OVER-CLAIM CORRECTED: the descent correspondence ("trace-hypo-rigid shore <=>
  minimal 4-VC Delta<=6 quotient of these single-merge profile shapes") is
  RIGOROUS-INFORMAL/SKETCH, NOT proven. Only the BASE salvage lemma is proved
  (difference-rigidity on a non-adjacent pair z1,z2 <=> K/(z1=z2) non-3-col,
  minimal core 4-VC). So the d_u closure does NOT yet exclude all size-15
  trace-hypo-rigid shores — that implication is conditional on the unproven
  correspondence and is LITERALLY the open GPT question (round-3-prime Q-B).
- DECISIVE GAP (high confidence): MULTI-MERGE. A size-15 shore whose partner forces
  a 3-vertex colour class contracts a TRIPLE (15->14->13), giving a 13-vertex
  NON-6-regular 4-critical quotient excluded by NEITHER the single-merge n=14 hunt
  NOR Theorem A (6-regular only). The profile descriptor admits 'merged vertices'
  (plural) but the hunt enumerates exactly ONE merged vertex. Other gaps: n=15
  quotients (size-16 shores); diagonal 3+3 closer = re-derivation of Thm A
  ('critical edges form an edge cover in every 6-reg 4-VC graph' = Prob-5.2
  frontier); spread case open.
- NEXT (proof-only blocker -> GPT-5.5 Pro): is the minimal 4-critical rigidity core
  of a size-15 trace-hypo-rigid shore ALWAYS a single pair-contraction (14-vertex
  quotient), or can it require a multi-merge/triple-contraction to a 13-vertex
  non-6-regular quotient? Question staged in gpt_descent_multimerge_q_2026-06-13.md.
- AUTONOMOUS COMPUTE MEANWHILE (this tick, 64 workers): build the two-merge
  (triple-contraction) n=13 quotient hunt (core_hunt2) as a strict re-use of the
  apex-generator + P1/P2/P3 battery. NOTE (honest): a P3pass=0 closes only the
  finite triple-contraction sub-case; interpretive value still gated on the
  correspondence proof. A SURVIVOR = first-ever counterexample seed in an unhunted,
  structurally-admitted class (asymmetric upside) -> the search is worthwhile.

# (2026-06-13 ~07:35) TRIPLE-MERGE (two-merge) n=13 QUOTIENT HUNT — near-regular slice CLOSED
- core_hunt2.cpp (apex over 12-vertex Delta<=6 bases; merged vertex deg 7..11; strict
  re-use of single-merge P1/P2/P3). run_triplemerge_py.py 64 workers, fork-safe.
- NEAR-REGULAR family (base e in {29,30,31,32}, residual base deficiency D'<=4):
  16,000/16,000 shards VALID (fails=0), read=1,941,877,414 bases, apexings=2,932,862,776,
  P1pass=195,330,452, P2pass=189,254,341, **P3pass=0, zero candidates**.
  => NO 4-vertex-critical 13-vertex triple-contraction quotient with D'<=4.
- DEFICIENCY ARITHMETIC (rigorous): for a triple-contraction of shore K (15 vtx, e=42,
  deficiency 6), the quotient M' (13 vtx, one merged vertex u) has base deficiency
  D' = 2*sum(deg z_i) - 12 - deg(u). For 3 b=2-stubs (deg 4): D'=12-d in [1,4] (covered).
  For 3 b=1-stubs (deg 5): D'=18-d in [6,13]. For interior (deg 6): D'=24-d in [12,17].
  So the D'<=4 slice covers exactly the b=2-stub triple-contractions; b=1-stub and
  interior triples (D' 5..17) are NOT yet covered.
- NEXT (this tick, 64 workers): extend to D'<=8 (e in {27,28,29,30}, D' in [5,8] via
  DMIN/DMAX) to cover b=1-stub triples and most of the feasible frontier. D'>8
  (e<=26, interior triples) = infeasible blanket => GPT-pinned correspondence required.

# (2026-06-13 ~07:56) TRIPLE-MERGE n=13: D'<=8 CLOSED; feasible descent finite hunts exhausted
- D'∈[5,8] band (core_hunt2 all 8 5; e∈{27,28,29,30}; run_triplemerge2_py.py 64 workers):
  16,000/16,000 shards VALID (fails=0), read=3,973,814,025 bases, apexings=68,932,140,044,
  P1pass=7,842,192,119, P2pass=7,466,539,973, **P3pass=0, zero candidates**.
- COMBINED with D'<=4: the triple-contraction (two-merge) n=13 quotient family is CLOSED
  for residual deficiency D'<=8 (~72e9 candidates total) -- covers all b=2-stub triples
  (D' 1..4) and b=1-stub triples (D' 6..8 partial). NO 4-vertex-critical triple-merge core.
- STATE OF THE DESCENT FINITE HUNTS (all P3pass=0):
  * single-merge n=14 (d_u 6..10, ~30e9): CLOSED
  * triple-merge n=13 (D'<=8, ~72e9): CLOSED
  Together ~100e9 candidates, ZERO descent cores in the feasible range.
- REMAINING (NOT autonomously feasible): D'>8 triple-merge (interior triples, e<=26 bases
  -> combinatorial blanket); quadruple-merge (12-vertex quotients, speculative); n=15
  single-merge quotients (14-vertex bases, ~10^11). a=15 shore brute force is OUT (user
  directive: no blanket shore enumeration).
- DECISIVE BLOCKER (proof-only, GPT-gated): bound the forced-equal-class size of a
  trace-hypo-rigid shore. SHARPENED: which cut-matrix types {(6,0,0),(3,3,0),(4,1,1),(2,2,2)}
  admit a forced colour class of size >=3 (=> triple+ merge)? Theorem-C/cor:diag forces a
  PAIR (p=l) in the 3+3 diagonal case; if forced-equal classes are provably <=2 (single
  pair-contraction only), the single-merge n=14 closure already excludes all size-15
  trace-hypo-rigid shores and the descent rung is COMPLETE. Question staged in
  gpt_descent_multimerge_q_2026-06-13.md.

# (2026-06-13 ~08:10) FEASIBLE NEAR-REGULAR DESCENT CENSUS COMPLETE (merge counts 2..7, all P3=0)
- core_hunt3.cpp (generalized base size; base=12 cross-checks core_hunt2 EXACTLY). Completion
  hunts (near-regular D'<=8) for quotient sizes 12,11,10,9 (= forced-equal-class / merge counts
  4,5,6,7), every geng class >Z-validated:
  * quotient 12 (base 11, e 24:29): read=92,982,080, apexings=901,760,271, P2=50,046,855, P3pass=0
  * quotient 11 (base 10, e 21:26): read=2,445,768, apexings=12,830,045, P2=268,741, P3pass=0
  * quotient 10 (base 9, e 19:23):  read=58,456, P2=905, P3pass=0
  * quotient 9  (base 8, e 16:20):  read=2,883, P2=0, P3pass=0
- WITH single-merge n=14 (k=2) and triple-merge n=13 (k=3, D'<=8): the NEAR-REGULAR (D'<=8)
  descent-core census is COMPLETE across forced-equal-class sizes 2..7 (quotient sizes 14..9):
  ZERO 4-vertex-critical descent core, ~100e9+ candidates total, all >Z-validated.
- SCOPE (honest): covers residual deficiency D'<=8 only; high-deficiency (interior-triple-type)
  profiles D'>8 remain an infeasible enumeration blanket. Interpretive value (excludes size-15
  trace-hypo-rigid shores) still gated on the forced-equal-class BOUND proof (workflow w4bupyw70
  in flight) and the all-sizes correspondence (GPT, staged).
