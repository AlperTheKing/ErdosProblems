# Erdős #944 / Dirac k=4: 6-Regular Subproblem Notes

Status: draft. This is a secondary-result package, not a full resolution of
Erdos #944.

## Target

Let a `(4,1)` graph mean a finite simple graph `G` such that:

- `chi(G) = 4`;
- `chi(G - v) = 3` for every vertex `v`;
- `chi(G - e) = 4` for every edge `e`.

Skottova-Steiner 2025 ask explicitly whether a 6-regular `(4,1)` graph exists
(Problem 5.2). The present verified package proves:

1. no 6-regular `(4,1)` graph exists on at most 14 vertices;
2. every hypothetical 6-regular `(4,1)` graph satisfies several additional
   rigidity conditions.

## Computational Theorem

There is no 6-regular `(4,1)` graph on `n <= 14` vertices.

The exhaustive checker summaries are below. The counts are SMS stream entries;
when the SMS minimality cutoff is reached the stream may contain isomorphic
duplicates, but this cannot create a false negative for the `TARGET=0` claim.

```text
n=11: total=266 threecol=3 notVC=263 vcWithCritEdge=0 TARGET=0
n=12: total=7849 threecol=50 notVC=7799 vcWithCritEdge=0 TARGET=0
n=13: total=367860 threecol=849 notVC=367010 vcWithCritEdge=1 TARGET=0
n=14: total=21609301 threecol=42667 notVC=21566634 vcWithCritEdge=0 TARGET=0 badline=0
```

At `n=13` the stream contains one 6-regular 4-vertex-critical entry, and it has
critical edges. Facts about this unique graph
(`experiments/sixreg/unique_6reg_4vc_n13.txt`, 39 edges):

- its 13 critical edges form a Hamilton cycle;
- across all 13 vertex-deletions it admits exactly 78 proper 3-colourings and
  NONE splits any neighbourhood `2+2+2`: every colouring leaves a singleton
  colour class in `N(v)`, so Lemma 1 predicts critical edges at every vertex;
  the 156 singleton predictions hit exactly the 13 critical edges — 0 false
  positives, 13/13 covered (`experiments/sixreg/verify_lemma21_n13.py`).

So the smallest 6-regular 4-vertex-critical graph fails the target conditions
"everywhere locally", not marginally.

The n=14 slice was checked twice by different native chunk partitions:
`experiments/sixreg/n14_chunks` (110 residue classes) and
`experiments/sixreg/n14_chunks_v2` (73 residue classes). Both aggregate to the
same totals above with `badline=0`. Hence any 6-regular `(4,1)` graph, if one
exists, has at least 15 vertices.

Artifacts:

- `experiments/sixreg/check_stream2.cpp`: independent C++ stream checker;
- `experiments/sixreg/sixreg_n11.out`, `sixreg_n12.out`, `sixreg_n13.out`:
  SMS enumeration outputs;
- `experiments/sixreg/check_n11_summary2.out`;
- `experiments/sixreg/check_n12_summary2.out`;
- `experiments/sixreg/check_n13_summary2.out`;
- `experiments/sixreg/n14_chunks`, `n14_chunks_v2`;
- `experiments/sixreg/unique_6reg_4vc_n13.txt`.

## Rigidity Lemmas

### Lemma 1: Local multiplicity

Let `G` be a `(4,1)` graph. For any vertex `v` and any proper colouring
`phi : V(G-v) -> {1,2,3}`, each colour appears in `N(v)`, and no colour appears
exactly once in `N(v)`.

Proof. If some colour is absent from `N(v)`, then colour `v` with that colour
and obtain a 3-colouring of `G`, contradiction. If some colour appears exactly
once in `N(v)`, say only at `u`, then deleting `uv` lets us colour `v` with that
singleton colour, giving a 3-colouring of `G-uv`, contradiction to the absence
of critical edges.

In particular, in a 6-regular `(4,1)` graph the colour multiplicities in every
neighbourhood under every such colouring are exactly `(2,2,2)`.

Corollary (quantitative): any 4-vertex-critical `G` has at least
`(1/2) * Sum_v max(0, 6 - d(v))` critical edges (each vertex of degree `d < 6`
forces at least `6-d` singleton classes in its chosen colouring; each critical
edge is counted at most twice).

### Lemma 2: Triangle bound

In a 6-regular `(4,1)` graph every edge lies in at most four triangles.

Proof. If an edge `uv` had five common neighbours, then all neighbours of `u`
other than `v` would also be adjacent to `v`. In a 3-colouring of `G-u`, the
colour of `v` cannot appear on any of those five common neighbours. Hence the
colour of `v` appears exactly once in `N(u)`, contradicting Lemma 1.

### Lemma 3: Exact 6-cut conflict count

Let `F` be a 6-edge cut from a nontrivial vertex partition `V(G)=X disjoint Y`,
with both shores proper. Fix 3-colourings of both induced shores. For every
permutation of the colours on one shore, the resulting gluing has exactly two
monochromatic cut edges.

Proof. Each shore is 3-colourable: if `y in Y`, then `G[X] subset G-y`, and
`G-y` is 3-colourable; similarly for `G[Y]`. Now zero monochromatic cut edges
would 3-colour `G`. One monochromatic cut edge would make that edge critical.
Therefore every permutation has at least two conflicts. For each cut edge,
exactly two of the six colour permutations make its endpoints equal in colour,
so the total number of conflicts over all six permutations is `2|F| = 12`.
Thus all six permutations have exactly two conflicts.

### Theorem 3b: Five-type classification of 6-cut matrices

Write the cut matrix `m_ij = #{ab in F : alpha(a)=i, beta(b)=j}` and
`D_pi = Sum_i m_{i,pi(i)}`. If all six `D_pi = 2` (Lemma 3), then every `2x2`
submatrix is additively balanced (compare two permutations differing by a
transposition and cancel the common entry), giving `m_ij = (R_i + C_j - 2)/3`
where `R, C` are the row/column sums. Hence all row sums are congruent mod 3
(likewise columns), the row-sum vector is `(6,0,0)`, `(3,3,0)`, `(4,1,1)` or
`(2,2,2)` up to permutation, and exactly 21 matrices survive, forming five
types up to row/column permutation (rows):

```text
(I) 222/000/000  (II) 111/111/000  (III) 001/001/112  (IV) 200/200/200  (V) 110/110/110
```

Orbit count `3+3+9+3+3 = 21`, machine-verified (Python exhaustive over all
3x3 sum-6 matrices) and Lean-checked (`cut_matrix_classification`,
`matrix_mem_classification`). Consequently any 6-cut side boundary
colour-vector is `(6,0,0)`, `(3,3,0)`, `(4,1,1)` or `(2,2,2)`; boundary
vectors like `(5,1,0)`, `(4,2,0)`, `(3,2,1)` force a critical edge.

### Lemma 4: Kempe tether

In the setting of Lemma 3, let the two conflict edges be `{e,f}`. If
`e = xy` has conflict colour `a`, then for every colour `b != a`, the endpoints
`x` and `y` lie in the same `(a,b)`-Kempe component of `G - {e,f}`.

Proof. Otherwise swap colours `a,b` in the component containing `x`. This keeps
all edges of `G-{e,f}` properly coloured and removes the conflict on `e`, while
`f` remains deleted. The result is a 3-colouring of `G-f`, contradiction.

This is a global tether in `G-{e,f}`, not a purely internal-shore statement.
Any later argument that needs a shore-internal path must add a separate
first-cut-crossing or equivalent localization argument.

### Lemma 4b: Vertex-form Kempe tether

Let `G` be a `(4,1)` graph, `d(v) = 6`, `phi` a 3-colouring of `G-v`, so `N(v)`
splits into three same-colour pairs (Lemma 1). For `x in N(v)` with
`phi(x) = a`, mate `x'`, and any colour `b != a`: the component of `x'` in
`(G-v)[phi^{-1}({a,b})]` must contain a colour-`b` neighbour of `v`.

Proof. Otherwise swap colours `a,b` on that component: `x'` leaves colour `a`;
`x` is unaffected (or also leaves colour `a` if it lies in the component); no
colour-`b` neighbour of `v` enters colour `a` (none is in the component); the
third-colour neighbours are untouched. Then in `G - vx` the vertex `v` has no
colour-`a` neighbour; colouring `v` with `a` 3-colours `G - vx`, making `vx`
critical, contradiction.

Corollary: in each bicoloured pair-graph the four boundary vertices lie in
mixed components only — boundary pattern `(2,2)` in one component or
`(1,1)+(1,1)` across two. A single-colour boundary component forces a critical
edge at `v`. [Mechanism stress-tested: 19,389 tether-failure implications on
random 4-chromatic graphs, 0 counterexamples;
`experiments/sixreg/test_lemma21_random.py`.]

### Lemma 5: Small 6-cut shores

No 6-edge cut in a 6-regular `(4,1)` graph has a shore of size `2..8`.

Proof. If `|delta(S)| = 6` and `G` is 6-regular, then
`6|S| = 2e(G[S]) + 6`, so `e(G[S]) = 3|S|-3`. Since `S` is a proper induced
subgraph, choose `v notin S`. Then `G-v` is 3-colourable and
`G[S] subset G-v`, so `G[S]` is 3-colourable by monotonicity. Hence
`e(G[S]) <= floor(|S|^2/3)`. This excludes `2 <= |S| <= 7`.

For `|S| = 8`, equality in the 3-colourable Turan bound forces
`G[S] = K_{3,3,2}`. The two vertices in the part of size 2 have internal degree
6, hence no external neighbours. They are non-adjacent twins in `G`, impossible
in a vertex-critical graph: deleting one twin and colouring the other lets us
colour the deleted vertex with the same colour.

Corollary 5a: every nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has both
shores of size `>= 9`; in particular for `n <= 17` every such graph is
super-6-edge-connected (its only 6-edge-cuts are vertex stars). The same holds
for general `(4,1)` graphs with `delta >= 6` since the shore-degree equality in
the proof forces degree exactly 6 on the shore.

### Lemma 6: No 9-shores in the 6-regular case

No nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has a shore of size 9.

This is a finite, machine-assisted lemma. If `A` is such a shore, then
`e(G[A]) = 24`, `Delta(G[A]) <= 6`, and with
`b(v) = 6 - deg_{G[A]}(v)` we have `sum_v b(v)=6`. The 6-cut matrix theorem
forces every proper 3-colouring of `G[A]` to have boundary-deficiency vector,
up to permutation, in

```text
(6,0,0), (4,1,1), (3,3,0), (2,2,2).
```

Running

```powershell
geng -c -D6 9 24:24 | enum_9shore.exe
```

checks 729 connected candidates. The classification is:

```text
total=729 badDeficiency=0 not3col=711 badBoundaryVec=9 comparableNonNbr=8 SURVIVORS=1
```

The unique survivor is graph6 `HEzftz{`, with `b=011101110`. An independent
Python recount (`verify_9shore_survivor.py`) gives the same classification and
prints the survivor edge list.

Finally, the survivor has internal vertices `0,4,8` where `b(v)=0`, so
`N_G(v)=N_{G[A]}(v)`. For each of these vertices, the independent kill script
enumerates all 6 proper 3-colourings of `G[A]-v` and finds that none has all
three colours appearing at least twice on `N(v)`:

```text
v=0: colourings of H-v: 6, with all counts>=2 on N(v): 0
v=4: colourings of H-v: 6, with all counts>=2 on N(v): 0
v=8: colourings of H-v: 6, with all counts>=2 on N(v): 0
```

This contradicts Lemma 1 applied to a 3-colouring of `G-v`, restricted to
`G[A]-v`. Therefore the survivor cannot occur as a shore.

Corollary 6a: every nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has both
shores of size `>= 10`; in particular for `n <= 19` every such graph is
super-6-edge-connected. This corollary uses 6-regularity and is not being
claimed for general `delta >= 6` graphs.

### Lemma 7: No 10-shores in the 6-regular case

No nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has a shore of size 10.

Again this is finite and machine-assisted. A 10-shore `A` is connected
(otherwise one component has boundary at most 5), has `e(G[A])=27`,
`Delta(G[A]) <= 6`, and deficiency sum `sum_v (6-deg_{G[A]}(v))=6`.

Running

```powershell
geng -c -D6 10 27:27 | enum_10shore.exe
```

checks 18,655 connected candidates and gives:

```text
total=18655 badDeficiency=0 not3col=18345 badBoundaryVec=197 comparableNonNbr=86 localMultiplicityKill=27 SURVIVORS=0
```

The independent Python recount (`verify_10shore.py`) gives the same
classification:

```text
python recount: {'badvec': 197, 'badcomp': 86, 'not3col': 18345, 'badlocal': 27}
survivors: []
```

The filters are the same verified necessary conditions as in Lemma 6:
the 6-cut boundary-vector condition for every proper 3-colouring, the
comparable-non-neighbour obstruction at `b=0` vertices, and the local
multiplicity test at `b=0` vertices.

Corollary 7a: every nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has both
shores of size `>= 11`; in particular for `n <= 21` every such graph is
super-6-edge-connected. This strengthened corollary also uses 6-regularity.

### Lemma 8: No 11-, 12-, 13-, or 14-shores in the 6-regular case

No nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has a shore of size
`11..14`.

For these sizes we use the generalized shore filter
`experiments/sixreg/enum_shore.cpp`. For a shore `A` of size `a`, the filter
uses the same necessary conditions as above plus the generalized local
multiplicity test: for every vertex `v in A`, there must be a proper
3-colouring of `G[A]-v` for which

```text
sum_i max(0, 2 - |N_A(v) cap colour_i|) <= b(v),
```

where `b(v)=6-deg_A(v)`. This is necessary because in any 3-colouring of
`G-v`, Lemma 1 requires every colour to appear at least twice in `N_G(v)`, and
the missing appearances can only be supplied by the `b(v)` cut-neighbours of
`v`.

The complete native C++ chunk results are:

```text
a=11: total=696208 not3col=687377 badBoundaryVec=6013 comparableNonNbr=1300 localKill=1518 SURVIVORS=0
a=12: total=32833744 not3col=32484081 badBoundaryVec=241863 comparableNonNbr=27322 localKill=80478 SURVIVORS=0
a=13: total=1839349287 not3col=1822133664 badBoundaryVec=11944366 comparableNonNbr=788481 localKill=4482776 SURVIVORS=0
a=14: total=154941621 not3col=115063872 badBoundaryVec=32712357 comparableNonNbr=1752943 localKill=5412449 SURVIVORS=0
```

For `a=12,13,14` the runs use 110 `geng` residue chunks; all 110 summaries are
present and well-formed for each size. The `a=11` run also has an independent
full Python recount matching the C++ result. For larger sizes, independent
Python spot checks agree on an `a=13` residue sample and an `a=14` 5000-line
graph6 sample.

Corollary 8a: every nontrivial 6-edge-cut in a 6-regular `(4,1)` graph has both
shores of size `>= 15`; in particular for `n <= 29` every such graph is
super-6-edge-connected. This corollary is specific to the 6-regular subproblem.

## Lean / Formal Cores

`E:\Projects\ErdosProblems\formal-conjectures\erdos944_cores.lean` compiles
clean (Lean 4.27 / Mathlib, exit 0) with no `sorry` or `native_decide`.
Axiom report (`#print axioms`, 2026-06-10):

- `singleton_edge_critical` (Lemma 1 recolouring core): depends on NO axioms;
- `cut_matrix_classification` (Theorem 3b count = 21, via the 3003 weak
  compositions `comps 9 6` with completeness lemma `mem_comps`): `[propext]`;
- `mem_comps`, `matrix_mem_classification` (genuine matrix form with
  `Equiv.Perm` diagonal bounds), `turan_count_shore` (Lemma 5 numeric core):
  `[propext, Classical.choice, Quot.sound]`.

## Remaining Verification Work

- cold GPT-5.5 Pro red-team of Lemmas 1-5: completed; passed with wording
  corrections recorded in `../gpt_redteam_2026-06-10.md`;
- SECOND, wider cold red-team (full package incl. quantitative corollary,
  five-type classification, K_{3,3,2} analysis, dichotomy, literature +
  counterexample hunts): IN FLIGHT, thread "Cold Review Request"
  (chatgpt.com/c/6a29bd3c-31fc-83ed-b9ae-be902de6b95a); fold in verdicts
  before publication;
- final novelty sweep against Skottova-Steiner, Martinsson-Steiner, Jensen,
  Brown, Lattanzio, problem-page history, and citation graph;
- fold the n=14 closure and 9-shore exclusion into the public artifact branch
  and PR wording after final review;
- decide whether to add Lean coverage for Lemmas 2, 4, 4b and the non-adjacent
  twins endpoint of Lemma 5;
- write final PR language only if the novelty gate remains clean.
