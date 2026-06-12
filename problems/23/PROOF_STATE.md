# Erdos #23 proof state

## Verified lemmas

### V1. Vertex deletion inequality

For any graph `G` and vertex `v`,

`beta(G) <= beta(G-v) + floor(d_G(v)/2)`.

Equivalently,

`beta(G-v) >= beta(G) - floor(d_G(v)/2)`.

Proof: take an optimal bipartition of `G-v`, then put `v` on the side that
creates at most half of its incident edges as monochromatic edges.

Tier: T1.

### V2. McKay 23-vertex extremal edge check

The full McKay file `minbip23_20x.g6` contains six 23-vertex triangle-free
graphs with `beta=20`, and their edge counts are `100,101,102,103,104,105`.

Local verifier:

`E:\Projects\ErdosProblems\search23\verify_mckay23.cpp`

Tier: T1 relative to McKay catalogue completeness; computational exact check
of listed graphs.

### V3. Finite exact value `a(25)=25`

Proof memo:

`E:\Projects\ErdosProblems\docs_newmath\erdos23_a25_proof.md`

Tier: T1, relying on BCL high-density theorem and McKay catalogue completeness.

### V4. Edge lower bound for a beta-threshold search

Every graph has `maxcut(G) >= e(G)/2`, by averaging over all bipartitions.
Therefore `beta(G)=e(G)-maxcut(G) <= e(G)/2`. In particular, a graph with
`beta(G) >= T` must have `e(G) >= 2T`.

For the L29 search (`T=33`), only edge counts `e >= 66` matter.

Tier: T1.

### V5. Rooted `a(30)` branches `r=0,1,2,3` are impossible

Assume a 30-vertex triangle-free counterexample `G` to `a(30)=36`, so
`beta(G) >= 37`. BCL high-density gives `e(G) <= 139`, hence `G` has a
minimum-degree vertex `v` of degree `r <= 9`. If `r <= 3`, delete `v`. By V1,

`beta(G-v) >= 37 - floor(r/2) >= 36`.

But `G-v` has 29 vertices, and the BCL global bound for triangle-free graphs
gives

`beta(G-v) <= floor(29^2 / 23.5) = 35`.

Contradiction. Therefore only rooted branches `r=4,5,6,7,8,9` need a finite
certificate.

Tier: T1, relative to the cited BCL global theorem.

### V6. Arithmetic BCL/deletion pruning for `a(30)`

Using only BCL low/high density, BCL global `n^2/23.5`, known `a(23)=20`,
the project result `a(25)=25`, and the vertex deletion inequality:

- A 30-vertex counterexample with `beta >= 37` and `e <= 108` is impossible
  by BCL low density (`0.2486 * binom(30,2) = 108.141...`).
- Therefore the hard edge window is `109 <= e <= 139`.
- After deleting a root minimum-degree vertex, pure arithmetic prunes only part
  of the rooted campaign; it does not close `a(30)`.

Local checker:

`E:\Projects\ErdosProblems\search23\deletion_bound_dp.cpp`

Output summary:

`n=30 beta>=37 e=74..139 arithmetic_impossible=35 arithmetic_open=31`.

Root branch open counts:

`r=4,5,6,7` each leave `29` edge slices open;
`r=8` leaves `20`;
`r=9` leaves `5`.

Tier: T1 for the arithmetic implications; the checker is only an audit aid.

### V7. Five-deletion route needs structure

To invoke the verified `a(25)=25` result from a hypothetical 30-vertex
counterexample with `beta >= 37`, one would need to delete five vertices with
cumulative loss

`sum floor(d_current(v_i)/2) <= 11`.

Using only the average-degree guarantee for a minimum-degree vertex, this is
not forced anywhere in the hard medium-density window `109 <= e <= 139`.

Local checker:

`E:\Projects\ErdosProblems\search23\five_delete_loss_dp.cpp`

Output:

the guaranteed worst five-deletion loss ranges from `15` at `e=109..119` to
`20` at `e=136..139`; no rooted `r=4..9` slice is certified by this arithmetic
alone.

Tier: T1 for the negative arithmetic conclusion.

### V8. Seven-deletion route to McKay `a(23)` also needs structure

A more flexible route is to delete seven vertices and invoke McKay's exact
`a(23)=20` catalogue. If the cumulative deletion loss is `L` and the deleted
current degrees sum to `R`, then the remaining graph has

`beta >= 37-L` and `e' = e-R`.

Using the verified catalogue fact that all `n=23`, `beta=20` extremals have
at least `100` edges, a contradiction would follow from:

- `L <= 16`, or
- `L <= 17` and `e' <= 99`.

Local checker:

`E:\Projects\ErdosProblems\search23\seven_delete_to_a23_dp.cpp`

Output:

for every hard edge count `109 <= e <= 139`, and for every rooted branch
`r=4..9`, average-degree/minimum-degree arithmetic alone still leaves escape
sequences. The worst escape losses are `20..26` depending on `e,r`.

Conclusion:

the McKay `n=23` route is not dead, but it also requires a genuine structural
lemma. Pure greedy deletion arithmetic cannot close `a(30)=36`.

Tier: T1 for the negative arithmetic conclusion.

### V9. Corrected deletion escape profiles

Local profile extractor:

`E:\Projects\ErdosProblems\search23\deletion_escape_profiles.cpp`

Digest:

`E:\Projects\ErdosProblems\problems\23\deletion_escape_profiles_digest_2026-06-11.md`

This audit refines V7/V8 by using the elementary rooted lower bound:

if the original graph has minimum degree at least `r`, then after `t` vertex
deletions every remaining vertex has current degree at least `r-t`.

Even with this correction, many rooted escape profiles remain for both routes.
For example:

- five-deletion escapes include `7,6,6,4,6`, `6,6,4,4,6`,
  `8,7,6,6,4`;
- seven-deletion escapes include `8,7,6,6,4,4,2`,
  `7,6,6,6,6,6,6`, `8,8,6,6,4,4,6`.

Conclusion:

the missing ingredient is not a sharper average-degree bookkeeping lemma. It
must use the `beta >= 37` max-cut condition, likely through local cut
improvement, discharging with bad cuts, or a medium-density stability theorem.

Tier: T1 for the arithmetic/profile extraction.

### V10. Low-codegree root reduction

Any 30-vertex triangle-free counterexample with `beta >= 37` can be
maximalized without decreasing `beta`: adding one triangle-free edge increases
`e` by one and `maxcut` by at most one.

The BCL high-density consequence then forces the maximalized graph to still
have `e <= 139`; otherwise `beta <= floor(30^2/25)=36`.

In a maximal triangle-free graph every nonedge has at least one common
neighbour.  By Wang--Yang--Zhao, arXiv:2408.05547, every triangle-free graph
with minimum common degree greater than `floor(n/8)` is homomorphic to `C5`.
For `n=30`, this says `delta_2 >= 4` implies `G -> C5`.

If `G -> C5`, deleting the least-populated consecutive class-link makes the
graph bipartite, so `beta(G) <= e(G)/5 <= 139/5 < 37`.  Contradiction.

Therefore every maximalized counterexample has a nonedge `xy` with

`1 <= |N(x) cap N(y)| <= 3`.

Digest:

`E:\Projects\ErdosProblems\problems\23\gpt_lowcodegree_strategy_digest_2026-06-11.md`

Tier: T1 relative to Wang--Yang--Zhao and BCL.

### V11. Low-codegree root cut formulae verified

For a low-codegree root `xy`, let

- `C=N(x) cap N(y)`, `t=|C| in {1,2,3}`;
- `A=N(x)\C`;
- `B=N(y)\C`;
- `R=V(G)\({x,y} union A union B union C)`.

The GPT Pro strategy defines two rooted cut families, `Psi(s)` and `Phi(s)`,
over assignments `s:R -> {0,1}`.  These count, respectively:

- the best opposite-root cut with `x,B,R_0` opposite `y,A,R_1`;
- the best same-root cut with `x,y,R_0` opposite `A,B,R_1`;

after optimizing the side of each vertex in `C`.

Local verifier:

`E:\Projects\ErdosProblems\search23\verify_lowcodegree_root.cpp`

Self-test:

`verify_lowcodegree_root.exe 1000 13`

Output:

`OK trials=1000 max_n=13 roots_checked=20361`

This randomly generated small maximal triangle-free graphs, selected every
nonedge with common-neighbour count `1..3`, and checked `Psi/Phi` against
direct cut enumeration for every spin assignment on `R`.

Tier: T1 for the formula accounting.

### V12. Direct low-codegree SAT and raw `R` enumeration are insufficient

Added direct low-codegree rooted SAT worker:

`E:\Projects\ErdosProblems\search23\sat_lowcodegree_30.cpp`

It fixes a nonedge `0,1` with exact common-neighbour count
`t in {1,2,3}`, enforces triangle-free/maximality, edge bounds,
minimum-degree lower bounds, and then lazily adds exact full-cut constraints
for `beta >= 37`.

Smoke/calibration:

- `t=1`, `min_degree >= 8`, `e=109`, maximality on:
  `UNKNOWN` on the first SAT call after `1,000,000` conflicts.
- Same slice with maximality off:
  `UNKNOWN` on the first SAT call after `200,000` conflicts.

Conclusion:

direct 30-vertex SAT remains too blunt even after the low-codegree root.

Raw `R`-core enumeration was also tested with nauty:

- `geng -t -u 13`: `20,797,002` triangle-free unlabeled graphs in `7.15s`;
- `geng -t -u 15`: `14,232,552,452` triangle-free unlabeled graphs in
  about `58min`.

Conclusion:

the compressed low-codegree certificate cannot simply enumerate all
triangle-free `R` graphs up to `q=15`.  Additional pruning is needed before
graph generation, or a different exact certificate formulation must avoid raw
`q=15` enumeration.

Status: VERIFIED computational calibration.

### V13. The `q=15` low-codegree boundary branch needs further pruning

For minimum degree branch `r0=8`, the only way the low-codegree partition can
have `q=|R|=15` is

`t=3`, `|A|=|B|=5`, `|C|=3`, `|R|=15`.

The active SAT worker now has an optional `q15_shape` mode that fixes the
labelled representative

- `x=0`, `y=1`;
- `C={2,3,4}`;
- `A={5,6,7,8,9}`;
- `B={10,11,12,13,14}`;
- `R={15,...,29}`.

It also adds certificate-safe local consequences of maximal triangle-freeness:

- every `A` vertex has a neighbour in `B`;
- every `B` vertex has a neighbour in `A`;
- every `R` vertex has a neighbour in `A union C` and in `B union C`;
- if `a in A` and `b in B` are nonadjacent, then their common neighbour is
  forced to lie in `R`.

The first calibration accidentally used `e=109`, but in the `min_degree >= 8`
branch this edge count is arithmetically impossible:

`2e >= 30*8`, hence `e >= 120`.

The worker now catches this before SAT:

`sat_lowcodegree_30.exe dummy 10 search23/q15_shape_arith_e109 3 8 109 109 4 100000 1 1`

returned `UNSAT_ARITHMETIC`.

Calibration on the first meaningful boundary slice:

`sat_lowcodegree_30.exe dummy 10 search23/q15_shape_calib_e120 3 8 120 120 4 200000 0 1`

found models quickly and added `36` bad cut constraints over `10` rounds,
ending `INCONCLUSIVE`.

A longer calibration:

`sat_lowcodegree_30.exe dummy 80 search23/q15_shape_calib_e120_r80 3 8 120 120 8 500000 0 1`

added `632` bad cut constraints over `80` rounds and still ended
`INCONCLUSIVE`.

Conclusion:

the meaningful `q=15`, `e>=120` boundary branch is not closed by simply adding
bad cuts one model at a time.  The next certificate must either analytically
eliminate `q=15`, compress by neighbourhood types before solving, or add a
stronger rooted cut/deletion pruning lemma.

Status: VERIFIED computational calibration.

### V14. Minimum-codegree q=15 pure `(R,U_i)` filter

GPT Pro proposed the key strengthening:

root the low-codegree nonedge `xy` at minimum nonedge-codegree
`t=delta_2(G)`.  In the `q=15` branch this forces

`t=3`, `|A|=|B|=5`, `|C|=3`, `|R|=15`, and `delta_2(G)=3`.

For `C={c_1,c_2,c_3}` and `U_i=N_R(c_i)`, the following certificate-safe
constraints are hand-checked:

- `|U_i| >= 6`;
- `U_i` is independent;
- every `r in R \ U_i` has at least three neighbours in `U_i`;
- `U_i cap U_j` is nonempty for `i != j`.

Added pure filter:

`E:\Projects\ErdosProblems\search23\sat_q15_ru_filter.cpp`

It solves only for the triangle-free graph `R` and the three sets `U_i`, then
checks the scalar q=15 feasibility and paired rooted-cut inequalities from
GPT Pro's answer for all `W subset R`.

Calibration:

`sat_q15_ru_filter.exe 100 search23/q15_ru_smoke_100 200000`

rejected all `100` sampled SAT models by scalar/paired rooted-cut feasibility;
no survivor.

Calibration:

`sat_q15_ru_filter.exe 10000 search23/q15_ru_calib_10k 200000`

rejected all `10,000` sampled SAT models by scalar/paired rooted-cut
feasibility; no survivor.

Calibration:

`sat_q15_ru_filter.exe 100000 search23/q15_ru_calib_100k 200000`

rejected all `100,000` sampled SAT models by scalar/paired rooted-cut
feasibility in about `45s`; no survivor.

Status:

strong computational evidence that the pure `(R,U_i)` layer may already kill
the q=15 branch, but not yet a complete certificate.  The current worker blocks
complete assignments one-by-one.  To promote this to a proof certificate, the
violated scalar/paired inequalities must be encoded as reusable lazy
constraints or replaced by a smaller dual/Hall certificate.

## Pending / active claims

### P1. `a(30)=36`

Current direct finite target:

For each `r=4,5,6,7,8,9`, prove UNSAT for the rooted 30-vertex branch:

- `G` is triangle-free and maximal triangle-free;
- vertex `0` has degree `r` and fixed neighborhood `{1,...,r}`;
- `e(G) <= 139`;
- every vertex has degree at least `r` (root chosen minimum-degree);
- every cut of `G` has at least 37 monochromatic edges, equivalently for
  `H=G-0` and every cut `sigma` of `H`,
  `mono_H(sigma) + min(|{a in A : sigma(a)=0}|, |{a in A : sigma(a)=1}|) >= 37`.

This rooted target supersedes the blunt L29 target.

Current computational route:

- `search23/sat_rooted_30.cpp`: rooted lazy-cut worker with exact rooted cut
  scan and optional CaDiCaL conflict limit.
- `search23/campaign_rooted_30.cpp`: progress-reporting campaign wrapper
  (`PROGRESS.txt`, active branch list, elapsed/rate/ETA/counters).
- Smoke: `r=0,e=74..75` closes UNSAT immediately, consistent with V5.
- Calibration: `r=8,e=130..131` and `r=9,e=135..136` are INCONCLUSIVE under
  20 rounds and 20k conflicts per SAT call; no counterexample found.
- Arithmetic pruning now restricts the meaningful edge window to
  `109 <= e <= 139`; the older `e<109` campaign slices need not be run.

Status: PENDING.

## Failed or insufficient approaches

- Direct generalization of the `a(25)` two-deletion proof to all `m`: fails
  already at `m=6`. Two deletions give only `beta >= 29` on 28 vertices, below
  the balanced `C5` lower threshold 30.
- Any proof using only the BCL high-density edge cap and greedy deletion appears
  asymptotically insufficient: beta loss per deletion is about `0.79925m`, while
  the balanced `C5` target drops about `0.4m` per deletion.
- The five-deletion route to `a(25)=25` cannot be closed from average-degree
  arithmetic alone; it requires a structural/stability lemma forcing a much
  smaller deletion loss set than the min-degree bound guarantees.
- The seven-deletion route to McKay's `a(23)=20` catalogue also cannot be
  closed from average-degree arithmetic alone, even using the catalogue fact
  that all `beta=20` extremals have at least 100 edges.
- Corrected rooted deletion-profile extraction shows the obstruction persists
  even after using the lower bound `delta(G-S) >= r-|S|`; the needed lemma must
  exploit the `beta >= 37` cut condition itself.
- Standalone L29 CEGAR route abandoned after 13.34h: 253/740 `(e,d0)` slices
  completed, with 39 UNSAT, 214 INCONCLUSIVE, and no counterexample. It is too
  blunt because it includes 29-vertex graphs that need not extend to a
  30-vertex counterexample.

## Open subgoals

1. Prove rooted branches `r=4..9`, preferably by degree-sequence/stability
   reductions before further computation.
2. If `a(30)` certificate succeeds, write and verify a second finite exact
   value.
3. If it fails or stalls, extract structural information from hard candidates
   and formulate the missing medium-density stability theorem.
4. For the low-codegree route, find pruning that eliminates raw `q=15`
   enumeration or reduces it to a smaller exact certificate.  GPT Pro has been
   asked specifically for this pruning after the `q=13/q=15` counts.
