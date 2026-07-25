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

### V15. q=15 scalar/paired split obstruction isolated

Added scalar-window split worker:

`E:\Projects\ErdosProblems\search23\sat_q15_ru_scalar_exhaust.cpp`

This splits the pure q=15 `(R,U_i)` certificate by exact scalar parameters
`(p,e_R,U)`, where `p=e(A,B)`, `e_R=e(R)`, and
`U=sum_i |U_i|`.

Findings:

- A scalar-only full split immediately found a survivor at
  `p=25`, `e_R=41`, `U=33`, so scalar inequalities alone do not eliminate q=15.
- Adding a label-independent fixed-cut consequence of paired `Psi` is valid,
  but the direct CNF encoding is too slow:
  `40/100` jobs completed in `1731s`, with no summary result.
- The practical paired/type blocker was instrumented with a per-job limit.
  First hard branch:

  `p=25`, `e_R=34`, `U=35`, scalar cap `29`.

  Diagnostic output:

  `E:\Projects\ErdosProblems\search23\q15_ru_first_hardjob_500\HARD_JOB.txt`

  It blocked `100000` concrete `(R,U_i)` assignments in this single branch
  without closing the branch.

Status:

verified computational obstruction.  The remaining q=15 work should focus on
the hard scalar region around large `p`, medium/high `e_R`, and `U≈35`, rather
than broad scalar splitting.  Current full-assignment blocking is not a proof
certificate.

### V16. q=15 same-type shape cuts

For q=15 label-count profiles write `S_i` for singleton labels, `D_i` for
doubleton labels missing colour `i`, and `T` for triple labels.

Exact support enumeration:

`E:\Projects\ErdosProblems\search23\q15_shape_cut_audit.cpp`

Output:

- `(n1,n2,n3)=(3,9,3)`: only the three colour permutations
  `S_i^3 D_i^9 T^3`; two rooted cuts force
  `M=e(A union B,R) >= 62`, while the edge budget gives `M <= 56`.
- `(4,7,4)`: only `S_i^4 D_i^7 T^4`; the cuts force `M >= 60`,
  budget gives `M <= 56`.
- `(5,7,3)`: only `S_i^5 D_i^7 T^3`; the cuts force `M >= 62`,
  budget gives `M <= 58`.
- `(6,7,2)`: non-same-type support profiles have `e_R <= 30`; hence
  `e_R >= 31` forces `S_i^6 D_i^7 T^2`, whose cuts force `M >= 64`,
  budget gives `M <= 60`.
- `(6,8,1)`: non-same-type support profiles have `e_R <= 33`, matching
  the earlier `e_R >= 34` one-triple cut.

The two rooted cuts used for `S_i^a D_i^b T^c` put `S_i` on one side and
`D_i,T` on the other, then swap the roles.  Each cut has exactly `3` forced
root monochromatic edges and at most `min(a,c)` forced `C-R` monochromatic
edges, so beta `>=37` forces the corresponding complementary A/B-R edge
package to have size at least `37-3-min(a,c)`.  Summing the two cuts gives
`M >= 2*(37-3-min(a,c))`.  The q=15 decomposition gives
`e(G)=16+U+p+e_R+M`, and since `e(G)<=139` and `p+e_R>=37`,
`M <= 139-16-U-37`.

Implemented cuts:

- whole-profile cuts for `(3,9,3)`, `(4,7,4)`, `(5,7,3)`;
- whole-profile high-edge cut for `(6,7,2)` when `e_R>=31`;
- whole-profile mixed max-edge cut for `(6,7,2)` when `e_R=30` and `p>=10`;
- exact same-type CNF cuts forbidding `S_i^6 D_i^7 T^2` and
  `S_i^7 D_i^6 T^2`.

Status: VERIFIED by exact enumeration plus rigorous cut accounting.

### V17. q=15 mixed `(6,7,2)` max-edge cut

For `(n1,n2,n3)=(6,7,2)`, exact support enumeration shows every mixed
profile has `e_R<=30`.  At `e_R=30`, up to colour permutation, the only
mixed shapes are

- `s=(0,3,3)`, `d=(0,3,4)`, `t=2`; or
- `s=(0,3,3)`, `d=(0,4,3)`, `t=2`.

Because `e_R=30` equals the disjoint-label upper bound, all allowed R-edge
cells are complete.  In the first shape these cells are
`S1-S2` with 9 edges, `S1-D1` with 9 edges, and `S2-D2` with 12 edges.

Use the usual rooted cut with `x` opposite `y`, `A` on the `y` side, and
`B` on the `x` side.  Put `S2 union D1` on the `A` side and
`S1 union D2 union T` on the `B` side.  The complete R-cells all cross this
cut, so they contribute no monochromatic R-edge.  Choosing the sides of
`c0,c1,c2` independently minimizes the C-R monochromatic contribution to
`3+0+2=5`, while the root contributes exactly 3 monochromatic edges.  Hence
the A/B-R package selected by this cut has size at least
`37-3-5=29`.  The complementary R cut gives the complementary A/B-R package
also at least 29.  Summing gives `M=e(A union B,R)>=58`.

The second mixed shape is identical with `D1,D2` interchanged; the two
complete-cell cuts are `S1 union D2` versus `S2 union D1 union T` and its
complement, again giving `M>=58`.

In the q=15 scalar branch under attack, `p>=15`.  With `U=26` and `e_R=30`,
the edge budget gives

`M <= 139 - 16 - U - p - e_R = 67-p <= 52`,

contradicting `M>=58`.  More generally, this mixed max-edge cut rules out
the profile whenever `p>=10`.

Local audits:

- `E:\Projects\ErdosProblems\search23\q15_mixed672_audit.cpp`
  prints the six mixed max-shapes and their complete edge cells;
- `E:\Projects\ErdosProblems\search23\q15_mixed672_cut_cover.cpp` and
  `q15_mixed672_cut_sat.cpp` were exploratory attempts; the useful final
  certificate is the two-cut argument above.

Status: VERIFIED by exact enumeration plus explicit rooted-cut accounting.

### V18. q=15 `(8,6,1)` low-cap shape-family cut

After the generalized complementary pair-cut filter, the low-cap
`(n1,n2,n3)=(8,6,1)` profile has only two surviving support-shape orbits in
the scalar band `cap<=50`, `p=15..20`, `e_R>=50-p`:

- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`, up to colour permutation;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`, up to colour permutation.

The generic shape-family SAT verifier

`E:\Projects\ErdosProblems\search23\sat_q15_shape_family.cpp`

keeps the R-edges variable but fixes the label multiset, and imposes the
same AB incidence, missing-edge, triangle-free, degree, colour-admissibility,
and common-neighbour constraints used by the witness verifiers.  It proves
UNSAT for all 15 surviving orbit/job pairs:

- first orbit, `(p,e_R,M)=(15,35,50),(16,34,50),(17,33,50),`
  `(18,32,50),(19,31,50),(20,30,50)`;
- second orbit, `(15,35,50),(15,36,49),(16,34,50),(16,35,49),`
  `(17,33,50),(17,34,49),(18,32,50),(19,31,50),(20,30,50)`.

All runs returned `SHAPE_FAMILY_STATUS 20`.  This is encoded as the profile
cut

`n1=8, n2=6, n3=1, cap<=50, p>=15, e_R>=50-p`.

Status: VERIFIED computational certificate for this scalar band.

### V19. q=15 `(9,6,0)` low-cap shape-family cut

After fixing the pair-cut shape audit so that individual support shapes with
`e_R` above their own R-edge upper bound are killed, the low-cap
`(n1,n2,n3)=(9,6,0)` profile leaves only two support-shape orbits in the
band `cap<=50`, `p=15..20`, `e_R>=52-p`:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`, up to colour permutation;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

The generic verifier

`E:\Projects\ErdosProblems\search23\sat_q15_shape_family.cpp`

returned `SHAPE_FAMILY_STATUS 20` for all 36 orbit/job pairs:

`p=15..20`, with `e_R=52-p, 53-p, 54-p` and
`cap=102-p-e_R` respectively, for each of the two orbits.

This is encoded as the profile cut

`n1=9, n2=6, n3=0, cap<=50, p>=15, e_R>=52-p`.

Status: VERIFIED computational certificate for this scalar band.

### V20. q=15 `(10,5,0)` cap-50 shape-family cut

After pair-cut shape pruning, the cap-50 `(n1,n2,n3)=(10,5,0)` band leaves
three support-shape orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`;

all up to colour permutation.  The generic shape-family SAT verifier returned
`SHAPE_FAMILY_STATUS 20` for all 9 cases with

`(p,e_R,M)=(15,38,50),(16,37,50),(17,36,50)`.

This is encoded as the profile cut

`n1=10, n2=5, n3=0, cap<=50, p>=15, e_R>=53-p`.

Status: VERIFIED computational certificate for this scalar band.

### V21. q=15 cap-51 extensions for the `(8,6,1)` and `(9,6,0)` bands

After V20 the first scalar jobs were dominated by cap-51 profiles.  I used the
generic shape-family SAT verifier, which fixes the exact label multiset but
leaves all admissible R-edges variable, including the support, degree,
triangle-free, A/B-incidence, and common-neighbour constraints.

For `(n1,n2,n3)=(8,6,1)`, the only surviving cap-51 shapes up to colour
permutation were

- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For `(p,e_R,M)=(15,34,51),(16,33,51),(17,32,51),(18,31,51),(19,30,51),(20,29,51)`,
all 12 cases returned `SHAPE_FAMILY_STATUS 20`.

This widens the profile cut to

`n1=8, n2=6, n3=1, cap<=51, p>=15, e_R>=49-p`.

For `(n1,n2,n3)=(9,6,0)`, the only surviving cap-51 shapes up to colour
permutation were

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For `(p,e_R,M)=(15,36,51),(16,35,51),(17,34,51),(18,33,51),(19,32,51),(20,31,51)`,
all 12 cases returned `SHAPE_FAMILY_STATUS 20`.

This widens the profile cut to

`n1=9, n2=6, n3=0, cap<=51, p>=15, e_R>=51-p`.

Status: VERIFIED computational certificate for these two scalar bands.

### V22. q=15 cap-51 extension for the `(10,5,0)` band

The remaining cap-51 `(10,5,0)` scalar jobs have `U=20` and
`e_R=52-p`.  After support and complementary-pair-cut filtering, the only
surviving shapes up to colour permutation are

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

The generic shape-family SAT verifier returned `SHAPE_FAMILY_STATUS 20` for
all 18 cases

`p=15..20`, `e_R=52-p`, `M<=51`.

This widens the profile cut to

`n1=10, n2=5, n3=0, cap<=51, p>=15, e_R>=52-p`.

Status: VERIFIED computational certificate for this scalar band.

### V23. q=15 cap-51 extension for the `(9,5,1)` band

After V22 the only remaining cap-51 scalar head was `(n1,n2,n3)=(9,5,1)`.
For this profile `U=22` and the cap-51 equality is `e_R=50-p`.

After support and complementary-pair-cut filtering, the surviving shapes up to
colour permutation are

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

The generic shape-family SAT verifier returned `SHAPE_FAMILY_STATUS 20` for
all 60 cases

`p=15..20`, `e_R=50-p`, `M<=51`.

This adds the profile cut

`n1=9, n2=5, n3=1, cap<=51, p>=15, e_R>=50-p`.

Status: VERIFIED computational certificate for this scalar band.

### V24. q=15 cap-52 extension for the `(9,6,0)` band

The cap-52 `(9,6,0)` scalar jobs have `U=21` and `e_R=50-p`.
After support and complementary-pair-cut filtering, the only surviving shapes
up to colour permutation are again

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

The generic shape-family SAT verifier returned `SHAPE_FAMILY_STATUS 20` for
all 12 cases

`p=15..20`, `e_R=50-p`, `M<=52`.

This widens the profile cut to

`n1=9, n2=6, n3=0, cap<=52, p>=15, e_R>=50-p`.

Status: VERIFIED computational certificate for this scalar band.

### V25. q=15 cap-52 extension for the `(11,4,0)` band

For `(n1,n2,n3)=(11,4,0)`, the cap-52 scalar jobs have `U=19` and
`e_R=52-p`.  After support and complementary-pair-cut filtering, the only
surviving shapes up to colour permutation are

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

The generic shape-family SAT verifier returned `SHAPE_FAMILY_STATUS 20` for
all 12 cases

`p=15..20`, `e_R=52-p`, `M<=52`.

This adds the profile cut

`n1=11, n2=4, n3=0, cap<=52, p>=15, e_R>=52-p`.

Status: VERIFIED computational certificate for this scalar band.

### V26. q=15 cap-52 extension for the `(10,5,0)` band

For `(n1,n2,n3)=(10,5,0)`, the cap-52 scalar jobs have `U=20` and
`e_R=51-p`.  The same three support orbits as in V22 survive the support and
complementary-pair-cut filters:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

The generic shape-family SAT verifier returned `SHAPE_FAMILY_STATUS 20` for
all 18 cases

`p=15..20`, `e_R=51-p`, `M<=52`.

This widens the profile cut to

`n1=10, n2=5, n3=0, cap<=52, p>=15, e_R>=51-p`.

Status: VERIFIED computational certificate for this scalar band.

### O1. Alive obstruction in the q=15 cap-52 `(7,6,2)` band

Attempted to extend the shape-family SAT certificate to `(n1,n2,n3)=(7,6,2)`
at cap 52.  The leading scalar case has `U=25`, `p=15`, and `e_R=31`.
After support and complementary-pair-cut filtering there are four shape orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

The first orbit

`s=(0,0,7)`, `d=(0,0,6)`, `t=2`, `p=15`, `e_R>=31`, `M<=52`

did not close under the generic shape-family SAT verifier: it timed out in the
unlimited run and returned `SHAPE_FAMILY_STATUS 0` with a 1,000,000 conflict
limit.  Therefore no `(7,6,2)` cap-52 cut has been recorded.

Status: ALIVE obstruction; needs a sharper lemma or a different certificate.

### O2. q=15 cap-52 bounded classification: hard orbits collapse to one-sided shapes

I ran the generic shape-family SAT verifier with a 100,000-conflict limit on
the remaining cap-52 profiles after V26.  This is not a proof for the unknown
cases, but it gives a verified classification of which cases closed quickly and
which cases remain alive under the current certificate.

Results:

- `(7,6,2)`, `M<=52`: first orbit
  `s=(0,0,7)`, `d=(0,0,6)`, `t=2`, `p=15`, `e_R>=31`
  is UNKNOWN at 1,000,000 conflicts; no full bounded sweep recorded.
- `(8,5,2)`, `M<=52`: 25/30 cases UNSAT at 100,000 conflicts; the unknown
  cases are exactly
  `s=(0,0,8)`, `d=(0,0,5)`, `t=2`, for `p=16..20`.
- `(8,6,1)`, `M<=52`: 42/48 cases UNSAT at 100,000 conflicts; the unknown
  cases are exactly
  `s=(0,0,8)`, `d=(0,0,6)`, `t=1`, for `p=15..20`.
- `(9,5,1)`, `M<=52`: 55/60 cases UNSAT at 100,000 conflicts; the unknown
  cases are exactly
  `s=(0,0,9)`, `d=(0,0,5)`, `t=1`, for `p=16..20`.

Common obstruction pattern:

`s=(0,0,a)`, `d=(0,0,b)`, `t=c`.

Equivalently, all singleton-labelled R-vertices carry the same colour, all
doubleton-labelled R-vertices carry the same missing colour, and the remaining
vertices are triples.  In this shape all admissible R-edges lie between the
singletons and the doubletons; triples are isolated in R.  The next useful
lemma should target this one-sided label collapse directly rather than trying
to close each SAT instance independently.

Status: ALIVE obstruction; bounded computation isolates the next lemma target.

### V27. q=15 cap-52 profile cuts from bounded shape sweeps plus prior cover cuts

After O2 I completed the `(7,6,2)` cap-52 bounded shape sweep and used the
existing one-sided cover cuts to convert three formerly hard profile families
into scalar cuts in the main q=15 runner.

Verified inputs:

- `(7,6,2)`, `M<=52`, `p=15..20`, `e_R >= 46-p`:
  18 non-one-sided shape cases are UNSAT at 100,000 conflicts.  The remaining
  one-sided cases `s=(0,0,7)`, `d=(0,0,6)`, `t=2` are handled by the existing
  same-type `(6,7,2)`/`(7,6,2)` two-triple shape cut.  Added scalar cut:
  `n1=7, n2=6, n3=2, cap<=52, p>=15, e_R>=46-p`.
- `(8,6,1)`, `M<=52`, `p=15..20`, `e_R >= 48-p`:
  42 non-one-sided shape cases are UNSAT at 100,000 conflicts.  The remaining
  one-sided cases `s=(0,0,8)`, `d=(0,0,6)`, `t=1` are handled by the existing
  `n3=1` all-doubletons-same cover cut.  Added scalar cut:
  `n1=8, n2=6, n3=1, cap<=52, p>=15, e_R>=48-p`.
- `(9,5,1)`, `M<=52`, `p=15..20`, `e_R >= 49-p`:
  55 non-one-sided shape cases and the one-sided `p=15` case are UNSAT at
  100,000 conflicts.  The remaining one-sided cases `p=16..20` are handled by
  the existing `n3=1` all-doubletons-same cover cut.  Added scalar cut:
  `n1=9, n2=5, n3=1, cap<=52, p>=15, e_R>=49-p`.

Implementation:

- `search23/sat_q15_ru_scalar_exhaust.cpp`
- `search23/q15_profile_audit.cpp`

Status: VERIFIED computational certificate plus previously recorded hand
cover cuts for these scalar bands.

### V28. q=15 `(8,5,2)` one-sided residual: triple vertices are side-pure

Consider the remaining one-sided support shape
`s=(0,0,8)`, `d=(0,0,5)`, `t=2`, after permuting colours.  Thus the
eight singleton-labelled vertices have label `{3}`, the five doubletons have
label `{1,2}`, and the two triples have label `{1,2,3}`.  Let `F` be the
missing-edge graph between the two 5-sets `A` and `B`.

In the AB-incidence checker every row and column of `F` has degree at most 2,
and if an R-vertex `r` is joined to side sets `X_r subset A` and `Y_r subset B`
then `X_r x Y_r` is contained in `F`.  For a triple-labelled vertex `t`, the
minimum side-incidence constraint gives

`|X_t| + |Y_t| >= 5`.

If both `X_t` and `Y_t` are nonempty, then `X_t x Y_t subset F`.  Since every
row and every column of `F` has degree at most 2, this forces
`|X_t| <= 2` and `|Y_t| <= 2`, hence `|X_t|+|Y_t| <= 4`, a contradiction.
Therefore every triple-labelled vertex in this residual is side-pure:

- either `X_t=A` and `Y_t=empty`;
- or `X_t=empty` and `Y_t=B`.

Status: VERIFIED hand lemma.  The remaining residual can be split into three
cases according to whether 0, 1, or 2 triples choose the A-side.

### V29. q=15 cap-52 `(8,5,2)` one-sided residual is impossible

This closes the remaining one-sided support shape from O2:

`s=(0,0,8)`, `d=(0,0,5)`, `t=2`, with `M<=52`.

By V28 each triple-labelled vertex is side-pure, so each triple contributes
exactly 5 incidences to `A union B`.  Independently, every singleton-labelled
vertex has `|X_s|>=2` and `|Y_s|>=2`, while every doubleton-labelled vertex has
`|X_d|>=1` and `|Y_d|>=1`.  Hence

`M >= 8*(2+2) + 5*(1+1) + 2*5 = 52`.

Since the scalar band has `M<=52`, equality holds throughout.  Therefore:

- each singleton has `|X_s|=|Y_s|=2`;
- each doubleton has `|X_d|=|Y_d|=1`;
- each triple is exactly one of `X_t=A,Y_t=empty` or `X_t=empty,Y_t=B`.

If both triples choose the same side, then the opposite side needs two
colour-1/2 hits from doubletons at each of its five vertices.  But there are
only five doubletons and each contributes exactly one hit on that side, for
only five total hits.  Thus the two triples must choose opposite sides.

Now every vertex of `A` and every vertex of `B` needs exactly one colour-1/2
hit from the five doubletons.  Since each doubleton contributes one `A` hit and
one `B` hit, the five doubletons define a perfect matching `P` inside the
missing-edge graph `F`.

Take any singleton-labelled vertex `s`.  It chooses two `A` vertices
`X_s` and two `B` vertices `Y_s`, and `X_s x Y_s subset F`.  A doubleton `d`
with matching edge `(a_d,b_d)` can be adjacent to `s` in `R` only if
`a_d notin X_s` and `b_d notin Y_s`, because R-adjacent vertices must have
disjoint `A`- and `B`-incidence sets.  In a perfect matching on five pairs,
at most three matching edges avoid a fixed 2-set on the `A` side and a fixed
2-set on the `B` side.  Therefore every singleton has R-degree at most 3.

Consequently `e_R <= 8*3 = 24`.  But the scalar jobs in this one-sided band
have `e_R >= 47-p`, and throughout the q=15 frontier `15 <= p <= 20`, so
`e_R >= 27`, contradiction.

Status: VERIFIED hand lemma.  Add scalar cut
`n1=8,n2=5,n3=2,cap<=52,p>=15,e_R>=47-p`.

### V30. q=15 cap-53 `(7,5,3)` scalar band is impossible

The first remaining cap-53 frontier after V29 has count profile
`(n1,n2,n3)=(7,5,3)`, with scalar threshold `e_R >= 44-p`.
Support-shape filtering leaves exactly two orbits:

- one-sided: `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- mixed: `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

The mixed orbit was checked by the generic shape-family AB/F SAT verifier for
`p=15..20`, `e_R>=44-p`, and `M<=53`; all six cases returned UNSAT.

For the one-sided orbit, V28 again makes every triple side-pure.  The minimum
side-incidence count is now

`M >= 7*(2+2) + 5*(1+1) + 3*5 = 53`.

Since `M<=53`, equality holds.  Thus each singleton has `|X_s|=|Y_s|=2`,
each doubleton has `|X_d|=|Y_d|=1`, and each triple is side-pure.

If all three triples choose the same side, the other side needs ten
colour-1/2 doubleton hits but only five are available.  Therefore at least one
side has exactly one triple and hence every vertex on that side needs exactly
one doubleton hit.  Since the five doubletons each contribute one hit on that
side, their chosen endpoints cover that side exactly once.

For any singleton `s`, any R-adjacent doubleton must avoid the two side
vertices in `X_s` (or symmetrically `Y_s`) on the side covered exactly once by
the doubletons.  Hence `s` has at most three doubleton neighbours in R.  With
seven singleton vertices this gives `e_R <= 7*3 = 21`, contradicting
`e_R >= 44-p >= 24` for `15 <= p <= 20`.

Status: VERIFIED hand lemma plus computational mixed-orbit certificate.  Add
scalar cut `n1=7,n2=5,n3=3,cap<=53,p>=15,e_R>=44-p`.

### V31. q=15 cap-53 `(7,6,2)` band closed by paired rooted cuts

After V30, the first remaining frontier profile is `(n1,n2,n3)=(7,6,2)`,
`cap=53`, with scalar threshold `e_R >= 45-p`.  Support-shape filtering leaves
four orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

The last three mixed orbits are UNSAT in the generic shape-family AB/F verifier
for all `p=15..20` at `e_R>=45-p`, `M<=53`.

The one-sided orbit is not killed by the AB/F verifier alone: the case
`p=17`, `e_R>=28`, `M<=53`, `s=(0,0,7)`, `d=(0,0,6)`, `t=2` returned SAT.
The dumped witness violates paired rooted-cut inequality 1 on
`W={0,1,2,3,4,5}`, with `2*boundary(W)=48` and right-hand side `47`.

Adding the fixed-label paired rooted-cut inequalities before SAT solving closes
the one-sided orbit for every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=53`.  The static verifier results are stored in
`search23/q15_762_cap53_onesided_static_batch`, and all six cases returned
UNSAT.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=6,n3=2,cap<=53,p>=15,e_R>=45-p`, relying on paired rooted cuts for the
one-sided support orbit.

### V32. q=15 cap-53 `(8,5,2)` band closed by paired rooted cuts

After V31, the next frontier profile is `(n1,n2,n3)=(8,5,2)`, `cap=53`, with
scalar threshold `e_R >= 46-p`.  Support-shape filtering leaves five orbits for
each `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 30-case certificate is stored in
`search23/q15_852_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=8,n2=5,n3=2,cap<=53,p>=15,e_R>=46-p`.

### V33. q=15 cap-53 `(8,6,1)` band closed by paired rooted cuts

After V32, the next frontier profile is `(n1,n2,n3)=(8,6,1)`, `cap=53`, with
scalar threshold `e_R >= 47-p`.  Support-shape filtering leaves eight orbits
for each `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 48-case certificate is stored in
`search23/q15_861_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=8,n2=6,n3=1,cap<=53,p>=15,e_R>=47-p`.

### V34. q=15 cap-53 `(9,5,1)` band closed by paired rooted cuts

After V33, the next frontier profile is `(n1,n2,n3)=(9,5,1)`, `cap=53`, with
scalar threshold `e_R >= 48-p`.  Support-shape filtering leaves ten orbits for
each `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=48-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 60-case certificate is stored in
`search23/q15_951_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=9,n2=5,n3=1,cap<=53,p>=15,e_R>=48-p`.

### V35. q=15 cap-53 `(9,6,0)` band closed by paired rooted cuts

After V34, the next frontier profile is `(n1,n2,n3)=(9,6,0)`, `cap=53`, with
scalar threshold `e_R >= 49-p`.  Support-shape filtering leaves two orbits for
each `p=15..20`:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=49-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 12-case certificate is stored in
`search23/q15_960_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=9,n2=6,n3=0,cap<=53,p>=15,e_R>=49-p`.

### V36. q=15 cap-53 `(10,5,0)` band closed by paired rooted cuts

After V35, the next frontier profile is `(n1,n2,n3)=(10,5,0)`, `cap=53`, with
scalar threshold `e_R >= 50-p`.  Support-shape filtering leaves three orbits
for each `p=15..20`:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=50-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 18-case certificate is stored in
`search23/q15_1050_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=10,n2=5,n3=0,cap<=53,p>=15,e_R>=50-p`.

### V37. q=15 cap-53 `(11,4,0)` band closed by paired rooted cuts

After V36, the next frontier profile is `(n1,n2,n3)=(11,4,0)`, `cap=53`, with
scalar threshold `e_R >= 51-p`.  Support-shape filtering leaves two orbits for
each `p=15..20`:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=51-p`, `M<=53`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 12-case certificate is stored in
`search23/q15_1140_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=11,n2=4,n3=0,cap<=53,p>=15,e_R>=51-p`.

### V38. q=15 cap-53 residual `(10,4,1)` band closed by paired rooted cuts

After V37, the only cap-53 residual frontier profile is `(n1,n2,n3)=(10,4,1)`,
with exact scalar cases `(p,e_R)=(15,34),(16,33),(17,32)`.  Support-shape
filtering leaves eleven orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For every orbit and every residual exact scalar case, the fixed-label SAT
verifier with all paired rooted-cut inequalities added before solving returns
UNSAT.  The 33-case certificate is stored in
`search23/q15_1041_cap53_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=10,n2=4,n3=1,cap<=53,p>=15,e_R>=49-p`.

### V39. q=15 cap-54 `(7,5,3)` band closed by paired rooted cuts

After V38 closes the cap-53 layer, the next frontier profile is
`(n1,n2,n3)=(7,5,3)`, `cap=54`, with scalar threshold `e_R >= 43-p`.
Support-shape filtering leaves two orbits for each `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`, `M<=54`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns UNSAT.  The 12-case certificate is stored in
`search23/q15_753_cap54_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=5,n3=3,cap<=54,p>=15,e_R>=43-p`.

### V40. q=15 cap-54 `(7,6,2)` band closed by paired rooted cuts

After V39, the next frontier profile is `(n1,n2,n3)=(7,6,2)`, `cap=54`,
with scalar threshold `e_R >= 44-p`.  Support-shape filtering leaves four
orbits for each `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_762_cap54_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=6,n3=2,cap<=54,p>=15,e_R>=44-p`.

### V41. q=15, cap54 first-frontier pair `(7,7,1)` / `(8,5,2)` UNSAT

After V40, the first open q=15 frontier row is `M=54`, `p=20`,
`e_R=25`, with profiles `(7,7,1)` and `(8,5,2)`.  The corresponding
paired scalar band is `p=15..20`, `e_R=45-p`, `M<=54`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits
for every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits
for every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 60-case certificate
is stored in `search23/q15_cap54_771_852_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=54,p>=15,e_R>=45-p` and
`n1=8,n2=5,n3=2,cap<=54,p>=15,e_R>=45-p`.

### V42. q=15, cap54 second-frontier pair `(8,6,1)` / `(9,4,2)` UNSAT

After V41, the first open q=15 frontier row is `M=54`, `p=20`,
`e_R=26`, with profiles `(8,6,1)` and `(9,4,2)`.  The corresponding
paired scalar band is `p=15..20`, `e_R=46-p`, `M<=54`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits
for every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits
for every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 102-case certificate
is stored in `search23/q15_cap54_861_942_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=54,p>=15,e_R>=46-p` and
`n1=9,n2=4,n3=2,cap<=54,p>=15,e_R>=46-p`.

### V43. q=15, cap54 profile `(9,5,1)` UNSAT

After V42, the first open q=15 frontier row is `M=54`, `p=20`,
`e_R=27`, with profile `(9,5,1)`.  The corresponding scalar band is
`p=15..20`, `e_R=47-p`, `M<=54`.

The support-shape frontier has 10 canonical orbits for every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 60-case certificate
is stored in `search23/q15_cap54_951_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=9,n2=5,n3=1,cap<=54,p>=15,e_R>=47-p`.

### V44. q=15, cap54 third-frontier pair `(9,6,0)` / `(10,4,1)` UNSAT

After V43, the first open q=15 frontier row is `M=54`, `p=20`,
`e_R=28`, with profiles `(9,6,0)` and `(10,4,1)`.  The corresponding
paired scalar band is `p=15..20`, `e_R=48-p`, `M<=54`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits
for every `p=15..20`:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits
for every `p=15..20`:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=48-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 78-case certificate
is stored in `search23/q15_cap54_960_1041_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=54,p>=15,e_R>=48-p` and
`n1=10,n2=4,n3=1,cap<=54,p>=15,e_R>=48-p`.

### V45. q=15, cap54 profile `(10,5,0)` UNSAT

After V44, the first open q=15 frontier row is `M=54`, `p=20`,
`e_R=29`, with profile `(10,5,0)`.  The corresponding scalar band is
`p=15..20`, `e_R=49-p`, `M<=54`.

The support-shape frontier has 3 canonical orbits for every `p=15..20`:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=49-p`,
`M<=54`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 18-case certificate
is stored in `search23/q15_cap54_1050_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=10,n2=5,n3=0,cap<=54,p>=15,e_R>=49-p`.

### V46. q=15, remaining cap54 zero-triple profiles UNSAT

After V45, the remaining q=15 cap54 frontier consists of profile
`(11,4,0)` in the band `p=15..20`, `e_R=50-p`, and profile `(12,3,0)`
in the band `p=15..17`, `e_R=51-p`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For every listed orbit and exact scalar case in the bands above, `M<=54`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns CaDiCaL status code 20.  The 15-case certificate is
stored in `search23/q15_cap54_1140_1230_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=54,p>=15,e_R>=50-p` and
`n1=12,n2=3,n3=0,cap<=54,15<=p<=17,e_R>=51-p`.

### V47. q=15, cap55 profile `(7,5,3)` UNSAT

After V46 closed cap54, the first open q=15 frontier row is `M=55`,
`p=20`, `e_R=22`, with profile `(7,5,3)`.  The corresponding scalar band is
`p=15..20`, `e_R=42-p`, `M<=55`.

The support-shape frontier has 2 canonical orbits for every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap55_753_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=5,n3=3,cap<=55,p>=15,e_R>=42-p`.

### V48. q=15, cap55 pair `(7,6,2)` / `(8,4,3)` UNSAT

After V47, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=23`, with profiles `(7,6,2)` and `(8,4,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=43-p`, `M<=55`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 48-case certificate
is stored in `search23/q15_cap55_762_843_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=6,n3=2,cap<=55,p>=15,e_R>=43-p` and
`n1=8,n2=4,n3=3,cap<=55,p>=15,e_R>=43-p`.

### V49. q=15, cap55 pair `(7,7,1)` / `(8,5,2)` UNSAT

After V48, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=24`, with profiles `(7,7,1)` and `(8,5,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=44-p`, `M<=55`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits for
every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 60-case certificate
is stored in `search23/q15_cap55_771_852_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=55,p>=15,e_R>=44-p` and
`n1=8,n2=5,n3=2,cap<=55,p>=15,e_R>=44-p`.

### V50. q=15, cap55 pair `(8,6,1)` / `(9,4,2)` UNSAT

After V49, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=25`, with profiles `(8,6,1)` and `(9,4,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=45-p`, `M<=55`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits for
every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 102-case certificate
is stored in `search23/q15_cap55_861_942_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=55,p>=15,e_R>=45-p` and
`n1=9,n2=4,n3=2,cap<=55,p>=15,e_R>=45-p`.

### V51. q=15, cap55 profile `(9,5,1)` UNSAT

After V50, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=26`, with profile `(9,5,1)`.  The corresponding scalar band is
`p=15..20`, `e_R=46-p`, `M<=55`.

The support-shape frontier has 10 canonical orbits for every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 60-case certificate
is stored in `search23/q15_cap55_951_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=9,n2=5,n3=1,cap<=55,p>=15,e_R>=46-p`.

### V52. q=15, cap55 pair `(9,6,0)` / `(10,4,1)` UNSAT

After V51, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=27`, with profiles `(9,6,0)` and `(10,4,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=47-p`, `M<=55`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits for
every `p=15..20`:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits
for every `p=15..20`:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 78-case certificate
is stored in `search23/q15_cap55_960_1041_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=55,p>=15,e_R>=47-p` and
`n1=10,n2=4,n3=1,cap<=55,p>=15,e_R>=47-p`.

### V53. q=15, cap55 profile `(10,5,0)` UNSAT

After V52, the first open q=15 frontier row is `M=55`, `p=20`,
`e_R=28`, with profile `(10,5,0)`.  The corresponding scalar band is
`p=15..20`, `e_R=48-p`, `M<=55`.

The support-shape frontier has 3 canonical orbits for every `p=15..20`:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=48-p`,
`M<=55`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 18-case certificate
is stored in `search23/q15_cap55_1050_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=10,n2=5,n3=0,cap<=55,p>=15,e_R>=48-p`.

### V54. q=15, remaining cap55 profiles UNSAT

After V53, the remaining q=15 cap55 frontier consists of:

- profile `(11,4,0)` in the band `p=15..20`, `e_R=49-p`;
- profile `(12,3,0)` in the band `p=15..20`, `e_R=50-p`;
- profile `(11,3,1)` in the band `p=15..17`, `e_R=48-p`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For every listed orbit and exact scalar case in the bands above, `M<=55`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns CaDiCaL status code 20.  The 45-case certificate is
stored in `search23/q15_cap55_remaining_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=55,p>=15,e_R>=49-p`,
`n1=12,n2=3,n3=0,cap<=55,p>=15,e_R>=50-p`, and
`n1=11,n2=3,n3=1,cap<=55,15<=p<=17,e_R>=48-p`.

### V55. q=15, cap56 pair `(6,6,3)` / `(7,4,4)` UNSAT

After V54 closed cap55, the first open q=15 frontier row is `M=56`,
`p=20`, `e_R=20`, with profiles `(6,6,3)` and `(7,4,4)`.  The corresponding
scalar band is `p=15..20`, `e_R=40-p`, `M<=56`.

For profile `(6,6,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,6)`, `t=3`;
- `s=(0,3,3)`, `d=(0,3,3)`, `t=3`.

For profile `(7,4,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,4)`, `t=4`;
- `s=(1,3,3)`, `d=(0,2,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_cap56_663_744_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=6,n3=3,cap<=56,p>=15,e_R>=40-p` and
`n1=7,n2=4,n3=4,cap<=56,p>=15,e_R>=40-p`.

### V56. q=15, cap56 profile `(7,5,3)` UNSAT

After V55, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=21`, with profile `(7,5,3)`.  The corresponding scalar band is
`p=15..20`, `e_R=41-p`, `M<=56`.

The support-shape frontier has 2 canonical orbits for every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap56_753_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=5,n3=3,cap<=56,p>=15,e_R>=41-p`.

### V57. q=15, cap56 pair `(7,6,2)` / `(8,4,3)` UNSAT

After V56, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=22`, with profiles `(7,6,2)` and `(8,4,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=42-p`, `M<=56`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 48-case certificate
is stored in `search23/q15_cap56_762_843_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=6,n3=2,cap<=56,p>=15,e_R>=42-p` and
`n1=8,n2=4,n3=3,cap<=56,p>=15,e_R>=42-p`.

### V58. q=15, cap56 pair `(7,7,1)` / `(8,5,2)` UNSAT

After V57, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=23`, with profiles `(7,7,1)` and `(8,5,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=43-p`, `M<=56`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits for
every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCAL status code 20.  The 60-case certificate
is stored in `search23/q15_cap56_771_852_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=56,p>=15,e_R>=43-p` and
`n1=8,n2=5,n3=2,cap<=56,p>=15,e_R>=43-p`.

### V59. q=15, cap56 pair `(8,6,1)` / `(9,4,2)` UNSAT

After V58, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=24`, with profiles `(8,6,1)` and `(9,4,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=44-p`, `M<=56`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits for
every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 102-case certificate
is stored in `search23/q15_cap56_861_942_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=56,p>=15,e_R>=44-p` and
`n1=9,n2=4,n3=2,cap<=56,p>=15,e_R>=44-p`.

### V60. q=15, cap56 pair `(9,5,1)` / `(10,3,2)` UNSAT

After V59, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=25`, with profiles `(9,5,1)` and `(10,3,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=45-p`, `M<=56`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits for
every `p=15..20`:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits for
every `p=15..20`:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap56_951_1032_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=56,p>=15,e_R>=45-p` and
`n1=10,n2=3,n3=2,cap<=56,p>=15,e_R>=45-p`.

### V61. q=15, cap56 pair `(9,6,0)` / `(10,4,1)` UNSAT

After V60, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=26`, with profiles `(9,6,0)` and `(10,4,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=46-p`, `M<=56`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits for
every `p=15..20`:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits for
every `p=15..20`:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 78-case certificate
is stored in `search23/q15_cap56_960_1041_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=56,p>=15,e_R>=46-p` and
`n1=10,n2=4,n3=1,cap<=56,p>=15,e_R>=46-p`.

### V62. q=15, cap56 pair `(10,5,0)` / `(11,3,1)` UNSAT

After V61, the first open q=15 frontier row is `M=56`, `p=20`,
`e_R=27`, with profiles `(10,5,0)` and `(11,3,1)`.  The corresponding
scalar band is `p=15..20`, `e_R=47-p`, `M<=56`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits for
every `p=15..20`:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits for
every `p=15..20`:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`,
`M<=56`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 72-case certificate
is stored in `search23/q15_cap56_1050_1131_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=56,p>=15,e_R>=47-p` and
`n1=11,n2=3,n3=1,cap<=56,p>=15,e_R>=47-p`.

### V63. q=15, remaining cap56 profiles UNSAT

After V62, the remaining q=15 cap56 frontier consists of:

- profile `(11,4,0)` in the band `p=15..20`, `e_R=48-p`;
- profile `(12,3,0)` in the band `p=15..20`, `e_R=49-p`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For every listed orbit and exact scalar case in the bands above, `M<=56`,
the fixed-label SAT verifier with all paired rooted-cut inequalities added
before solving returns CaDiCaL status code 20.  The 18-case certificate is
stored in `search23/q15_cap56_remaining_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=56,p>=15,e_R>=48-p` and
`n1=12,n2=3,n3=0,cap<=56,p>=15,e_R>=49-p`.

### V64. q=15, cap57 pair `(6,6,3)` / `(7,4,4)` UNSAT

After V63 closed cap56, the first open q=15 frontier row is `M=57`,
`p=20`, `e_R=19`, with profiles `(6,6,3)` and `(7,4,4)`.  The corresponding
scalar band is `p=15..20`, `e_R=39-p`, `M<=57`.

For profile `(6,6,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,6)`, `t=3`;
- `s=(0,3,3)`, `d=(0,3,3)`, `t=3`.

For profile `(7,4,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,4)`, `t=4`;
- `s=(1,3,3)`, `d=(0,2,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_cap57_663_744_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=6,n3=3,cap<=57,p>=15,e_R>=39-p` and
`n1=7,n2=4,n3=4,cap<=57,p>=15,e_R>=39-p`.

### V65. q=15, cap57 profile `(7,5,3)` UNSAT

After V64, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=20`, with profile `(7,5,3)`.  The corresponding scalar band is
`p=15..20`, `e_R=40-p`, `M<=57`.

The support-shape frontier has 2 canonical orbits for every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap57_753_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=7,n2=5,n3=3,cap<=57,p>=15,e_R>=40-p`.

### V66. q=15, cap57 pair `(7,6,2)` / `(8,4,3)` UNSAT

After V65, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=21`, with profiles `(7,6,2)` and `(8,4,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=41-p`, `M<=57`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits for
every `p=15..20`:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 48-case certificate
is stored in `search23/q15_cap57_762_843_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=6,n3=2,cap<=57,p>=15,e_R>=41-p` and
`n1=8,n2=4,n3=3,cap<=57,p>=15,e_R>=41-p`.

### V67. q=15, cap57 triple `(7,7,1)` / `(8,5,2)` / `(9,3,3)` UNSAT

After V66, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=22`, with profiles `(7,7,1)`, `(8,5,2)`, and `(9,3,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=42-p`, `M<=57`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap57_771_852_933_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=57,p>=15,e_R>=42-p`,
`n1=8,n2=5,n3=2,cap<=57,p>=15,e_R>=42-p`, and
`n1=9,n2=3,n3=3,cap<=57,p>=15,e_R>=42-p`.

### V68. q=15, cap57 pair `(8,6,1)` / `(9,4,2)` UNSAT

After V67, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=23`, with profiles `(8,6,1)` and `(9,4,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=43-p`, `M<=57`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 102-case certificate
is stored in `search23/q15_cap57_861_942_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=57,p>=15,e_R>=43-p` and
`n1=9,n2=4,n3=2,cap<=57,p>=15,e_R>=43-p`.

### V69. q=15, cap57 pair `(9,5,1)` / `(10,3,2)` UNSAT

After V68, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=24`, with profiles `(9,5,1)` and `(10,3,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=44-p`, `M<=57`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap57_951_1032_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=57,p>=15,e_R>=44-p` and
`n1=10,n2=3,n3=2,cap<=57,p>=15,e_R>=44-p`.

### V70. q=15, cap57 pair `(9,6,0)` / `(10,4,1)` UNSAT

After V69, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=25`, with profiles `(9,6,0)` and `(10,4,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=45-p`, `M<=57`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 78-case certificate
is stored in `search23/q15_cap57_960_1041_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=57,p>=15,e_R>=45-p` and
`n1=10,n2=4,n3=1,cap<=57,p>=15,e_R>=45-p`.

### V71. q=15, cap57 pair `(10,5,0)` / `(11,3,1)` UNSAT

After V70, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=26`, with profiles `(10,5,0)` and `(11,3,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=46-p`, `M<=57`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 72-case certificate
is stored in `search23/q15_cap57_1050_1131_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=57,p>=15,e_R>=46-p` and
`n1=11,n2=3,n3=1,cap<=57,p>=15,e_R>=46-p`.

### V72. q=15, cap57 profile `(11,4,0)` UNSAT

After V71, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=27`, with profile `(11,4,0)`.  The corresponding scalar band is
`p=15..20`, `e_R=47-p`, `M<=57`.

The support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap57_1140_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=11,n2=4,n3=0,cap<=57,p>=15,e_R>=47-p`.

### V73. q=15, cap57 profile `(12,3,0)` UNSAT

After V72, the first open q=15 frontier row is `M=57`, `p=20`,
`e_R=28`, with profile `(12,3,0)`.  The corresponding scalar band is
`p=15..20`, `e_R=48-p`, `M<=57`.

The support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For every exact scalar case `p=15..20`, `e_R=48-p`, `M<=57`, the
fixed-label SAT verifier with all paired rooted-cut inequalities added before
solving returns CaDiCaL status code 20.  The 6-case certificate is stored in
`search23/q15_cap57_1230_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=12,n2=3,n3=0,cap<=57,p>=15,e_R>=48-p`.

### V74. q=15, cap57 profile `(12,2,1)` UNSAT

After V73, the only remaining cap57 frontier rows are `p=15..17`,
`e_R=47-p`, with profile `(12,2,1)`.  The verifier was run on the full
scalar band `p=15..20`, `e_R=47-p`, `M<=57`.

The support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=47-p`,
`M<=57`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_cap57_1221_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=12,n2=2,n3=1,cap<=57,p>=15,e_R>=47-p`.

### V75. q=15, cap58 pair `(6,6,3)` / `(7,4,4)` UNSAT

After V74, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=18`, with profiles `(6,6,3)` and `(7,4,4)`.  The corresponding scalar
band is `p=15..20`, `e_R=38-p`, `M<=58`.

For profile `(6,6,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,6)`, `t=3`;
- `s=(0,3,3)`, `d=(0,3,3)`, `t=3`.

For profile `(7,4,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,4)`, `t=4`;
- `s=(1,3,3)`, `d=(0,2,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_cap58_663_744_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=6,n3=3,cap<=58,p>=15,e_R>=38-p` and
`n1=7,n2=4,n3=4,cap<=58,p>=15,e_R>=38-p`.

### V76. q=15, cap58 triple `(6,7,2)` / `(7,5,3)` / `(8,3,4)` UNSAT

After V75, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=19`, with profiles `(6,7,2)`, `(7,5,3)`, and `(8,3,4)`.  The
corresponding scalar band is `p=15..20`, `e_R=39-p`, `M<=58`.

For profile `(6,7,2)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,7)`, `t=2`;
- `s=(0,3,3)`, `d=(0,3,4)`, `t=2`.

For profile `(7,5,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For profile `(8,3,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,3)`, `t=4`;
- `s=(2,3,3)`, `d=(0,1,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap58_672_753_834_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=7,n3=2,cap<=58,p>=15,e_R>=39-p`,
`n1=7,n2=5,n3=3,cap<=58,p>=15,e_R>=39-p`, and
`n1=8,n2=3,n3=4,cap<=58,p>=15,e_R>=39-p`.

### V77. q=15, cap58 triple `(6,8,1)` / `(7,6,2)` / `(8,4,3)` UNSAT

After V76, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=20`, with profiles `(6,8,1)`, `(7,6,2)`, and `(8,4,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=40-p`, `M<=58`.

For profile `(6,8,1)`, the support-shape frontier has 3 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,8)`, `t=1`;
- `s=(0,3,3)`, `d=(0,3,5)`, `t=1`;
- `s=(0,3,3)`, `d=(0,4,4)`, `t=1`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 66-case certificate
is stored in `search23/q15_cap58_681_762_843_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=8,n3=1,cap<=58,p>=15,e_R>=40-p`,
`n1=7,n2=6,n3=2,cap<=58,p>=15,e_R>=40-p`, and
`n1=8,n2=4,n3=3,cap<=58,p>=15,e_R>=40-p`.

### V78. q=15, cap58 triple `(7,7,1)` / `(8,5,2)` / `(9,3,3)` UNSAT

After V77, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=21`, with profiles `(7,7,1)`, `(8,5,2)`, and `(9,3,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=41-p`, `M<=58`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap58_771_852_933_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=58,p>=15,e_R>=41-p`,
`n1=8,n2=5,n3=2,cap<=58,p>=15,e_R>=41-p`, and
`n1=9,n2=3,n3=3,cap<=58,p>=15,e_R>=41-p`.

### V79. q=15, cap58 pair `(8,6,1)` / `(9,4,2)` UNSAT

After V78, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=22`, with profiles `(8,6,1)` and `(9,4,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=42-p`, `M<=58`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 102-case certificate
is stored in `search23/q15_cap58_861_942_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=58,p>=15,e_R>=42-p` and
`n1=9,n2=4,n3=2,cap<=58,p>=15,e_R>=42-p`.

### V80. q=15, cap58 pair `(9,5,1)` / `(10,3,2)` UNSAT

After V79, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=23`, with profiles `(9,5,1)` and `(10,3,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=43-p`, `M<=58`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap58_951_1032_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=58,p>=15,e_R>=43-p` and
`n1=10,n2=3,n3=2,cap<=58,p>=15,e_R>=43-p`.

### V81. q=15, cap58 triple `(9,6,0)` / `(10,4,1)` / `(11,2,2)` UNSAT

After V80, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=24`, with profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.  The
corresponding scalar band is `p=15..20`, `e_R=44-p`, `M<=58`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 126-case certificate
is stored in `search23/q15_cap58_960_1041_1122_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=58,p>=15,e_R>=44-p`,
`n1=10,n2=4,n3=1,cap<=58,p>=15,e_R>=44-p`, and
`n1=11,n2=2,n3=2,cap<=58,p>=15,e_R>=44-p`.

### V82. q=15, cap58 pair `(10,5,0)` / `(11,3,1)` UNSAT

After V81, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=25`, with profiles `(10,5,0)` and `(11,3,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=45-p`, `M<=58`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 72-case certificate
is stored in `search23/q15_cap58_1050_1131_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=58,p>=15,e_R>=45-p` and
`n1=11,n2=3,n3=1,cap<=58,p>=15,e_R>=45-p`.

### V83. q=15, cap58 pair `(11,4,0)` / `(12,2,1)` UNSAT

After V82, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=26`, with profiles `(11,4,0)` and `(12,2,1)`.  The corresponding scalar
band is `p=15..20`, `e_R=46-p`, `M<=58`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,2,1)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=58`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap58_1140_1221_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=58,p>=15,e_R>=46-p` and
`n1=12,n2=2,n3=1,cap<=58,p>=15,e_R>=46-p`.

### V84. q=15, cap58 profile `(12,3,0)` UNSAT

After V83, the first open q=15 frontier row is `M=58`, `p=20`,
`e_R=27`, with profile `(12,3,0)`.  The corresponding scalar band is
`p=15..20`, `e_R=47-p`, `M<=58`.

The support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For every exact scalar case `p=15..20`, `e_R=47-p`, `M<=58`, the
fixed-label SAT verifier with all paired rooted-cut inequalities added before
solving returns CaDiCaL status code 20.  The 6-case certificate is stored in
`search23/q15_cap58_1230_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cut
`n1=12,n2=3,n3=0,cap<=58,p>=15,e_R>=47-p`.

### V85. q=15, cap59 pair `(6,6,3)` / `(7,4,4)` UNSAT

After V84, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=17`, with profiles `(6,6,3)` and `(7,4,4)`.  The corresponding scalar
band is `p=15..20`, `e_R=37-p`, `M<=59`.

For profile `(6,6,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,6)`, `t=3`;
- `s=(0,3,3)`, `d=(0,3,3)`, `t=3`.

For profile `(7,4,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,4)`, `t=4`;
- `s=(1,3,3)`, `d=(0,2,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=37-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 24-case certificate
is stored in `search23/q15_cap59_663_744_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=6,n3=3,cap<=59,p>=15,e_R>=37-p` and
`n1=7,n2=4,n3=4,cap<=59,p>=15,e_R>=37-p`.

### V86. q=15, cap59 triple `(6,7,2)` / `(7,5,3)` / `(8,3,4)` UNSAT

After V85, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=18`, with profiles `(6,7,2)`, `(7,5,3)`, and `(8,3,4)`.  The
corresponding scalar band is `p=15..20`, `e_R=38-p`, `M<=59`.

For profile `(6,7,2)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,7)`, `t=2`;
- `s=(0,3,3)`, `d=(0,3,4)`, `t=2`.

For profile `(7,5,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For profile `(8,3,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,3)`, `t=4`;
- `s=(2,3,3)`, `d=(0,1,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap59_672_753_834_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=7,n3=2,cap<=59,p>=15,e_R>=38-p`,
`n1=7,n2=5,n3=3,cap<=59,p>=15,e_R>=38-p`, and
`n1=8,n2=3,n3=4,cap<=59,p>=15,e_R>=38-p`.

### V87. q=15, cap59 triple `(6,8,1)` / `(7,6,2)` / `(8,4,3)` UNSAT

After V86, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=19`, with profiles `(6,8,1)`, `(7,6,2)`, and `(8,4,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=39-p`, `M<=59`.

For profile `(6,8,1)`, the support-shape frontier has 3 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,8)`, `t=1`;
- `s=(0,3,3)`, `d=(0,3,5)`, `t=1`;
- `s=(0,3,3)`, `d=(0,4,4)`, `t=1`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 66-case certificate
is stored in `search23/q15_cap59_681_762_843_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=8,n3=1,cap<=59,p>=15,e_R>=39-p`,
`n1=7,n2=6,n3=2,cap<=59,p>=15,e_R>=39-p`, and
`n1=8,n2=4,n3=3,cap<=59,p>=15,e_R>=39-p`.

### V88. q=15, cap59 triple `(7,7,1)` / `(8,5,2)` / `(9,3,3)` UNSAT

After V87, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=20`, with profiles `(7,7,1)`, `(8,5,2)`, and `(9,3,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=40-p`, `M<=59`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap59_771_852_933_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=59,p>=15,e_R>=40-p`,
`n1=8,n2=5,n3=2,cap<=59,p>=15,e_R>=40-p`, and
`n1=9,n2=3,n3=3,cap<=59,p>=15,e_R>=40-p`.

### V89. q=15, cap59 triple `(8,6,1)` / `(9,4,2)` / `(10,2,3)` UNSAT

After V88, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=21`, with profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=41-p`, `M<=59`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For profile `(10,2,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,1)`, `t=3`;
- `s=(2,4,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,0,2)`, `t=3`;
- `s=(3,3,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,2,0)`, `t=3`;
- `s=(3,3,4)`, `d=(1,1,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 138-case certificate
is stored in `search23/q15_cap59_861_942_1023_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=59,p>=15,e_R>=41-p`,
`n1=9,n2=4,n3=2,cap<=59,p>=15,e_R>=41-p`, and
`n1=10,n2=2,n3=3,cap<=59,p>=15,e_R>=41-p`.

### V90. q=15, cap59 pair `(9,5,1)` / `(10,3,2)` UNSAT

After V89, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=22`, with profiles `(9,5,1)` and `(10,3,2)`.  The corresponding
scalar band is `p=15..20`, `e_R=42-p`, `M<=59`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap59_951_1032_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=59,p>=15,e_R>=42-p` and
`n1=10,n2=3,n3=2,cap<=59,p>=15,e_R>=42-p`.

### V91. q=15, cap59 triple `(9,6,0)` / `(10,4,1)` / `(11,2,2)` UNSAT

After V90, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=23`, with profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.  The
corresponding scalar band is `p=15..20`, `e_R=43-p`, `M<=59`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 126-case certificate
is stored in `search23/q15_cap59_960_1041_1122_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=59,p>=15,e_R>=43-p`,
`n1=10,n2=4,n3=1,cap<=59,p>=15,e_R>=43-p`, and
`n1=11,n2=2,n3=2,cap<=59,p>=15,e_R>=43-p`.

### V92. q=15, cap59 pair `(10,5,0)` / `(11,3,1)` UNSAT

After V91, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=24`, with profiles `(10,5,0)` and `(11,3,1)`.  The corresponding
scalar band is `p=15..20`, `e_R=44-p`, `M<=59`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 72-case certificate
is stored in `search23/q15_cap59_1050_1131_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=59,p>=15,e_R>=44-p` and
`n1=11,n2=3,n3=1,cap<=59,p>=15,e_R>=44-p`.

### V93. q=15, cap59 pair `(11,4,0)` / `(12,2,1)` UNSAT

After V92, the first open q=15 frontier row is `M=59`, `p=20`,
`e_R=25`, with profiles `(11,4,0)` and `(12,2,1)`.  The corresponding
scalar band is `p=15..20`, `e_R=45-p`, `M<=59`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,2,1)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap59_1140_1221_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=59,p>=15,e_R>=45-p` and
`n1=12,n2=2,n3=1,cap<=59,p>=15,e_R>=45-p`.

### V94. q=15, final cap59 pair `(12,3,0)` / `(13,1,1)` UNSAT

After V93, the only remaining cap59 q=15 frontier rows are the scalar band
`p=15..20`, `e_R=46-p`, with profile `(12,3,0)` and, for the lower rows,
profile `(13,1,1)`.  We verified both profiles uniformly over `p=15..20`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For profile `(13,1,1)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,5)`, `d=(0,0,1)`, `t=1`.

For both orbits and every exact scalar case `p=15..20`, `e_R=46-p`,
`M<=59`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap59_1230_1311_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=12,n2=3,n3=0,cap<=59,p>=15,e_R>=46-p` and
`n1=13,n2=1,n3=1,cap<=59,p>=15,e_R>=46-p`.

Post-V94 frontier audit: `search23/q15_frontier_after_V94/AUDIT.out` has no
remaining `M=59` row.  The first open row is `M=60`, `p=20`, `e_R=17`, with
profiles `(6,7,2)`, `(7,5,3)`, and `(8,3,4)`.  The list-only run reports 270
remaining q=15 scalar jobs.

### V95. q=15, cap60 triple `(6,7,2)` / `(7,5,3)` / `(8,3,4)` UNSAT

The first cap60 frontier row after closing cap59 is `M=60`, `p=20`,
`e_R=17`, with profiles `(6,7,2)`, `(7,5,3)`, and `(8,3,4)`.  The
corresponding scalar band is `p=15..20`, `e_R=37-p`, `M<=60`.

For profile `(6,7,2)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,7)`, `t=2`;
- `s=(0,3,3)`, `d=(0,3,4)`, `t=2`.

For profile `(7,5,3)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,5)`, `t=3`;
- `s=(1,3,3)`, `d=(0,2,3)`, `t=3`.

For profile `(8,3,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,3)`, `t=4`;
- `s=(2,3,3)`, `d=(0,1,2)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=37-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap60_672_753_834_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=7,n3=2,cap<=60,p>=15,e_R>=37-p`,
`n1=7,n2=5,n3=3,cap<=60,p>=15,e_R>=37-p`, and
`n1=8,n2=3,n3=4,cap<=60,p>=15,e_R>=37-p`.

### V96. q=15, cap60 quartet `(6,8,1)` / `(7,6,2)` / `(8,4,3)` / `(9,2,4)` UNSAT

After V95, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=18`, with profiles `(6,8,1)`, `(7,6,2)`, `(8,4,3)`, and `(9,2,4)`.
The corresponding scalar band is `p=15..20`, `e_R=38-p`, `M<=60`.

For profile `(6,8,1)`, the support-shape frontier has 3 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,8)`, `t=1`;
- `s=(0,3,3)`, `d=(0,3,5)`, `t=1`;
- `s=(0,3,3)`, `d=(0,4,4)`, `t=1`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For profile `(9,2,4)`, the support-shape frontier has 3 canonical orbits:

- `s=(2,3,4)`, `d=(0,1,1)`, `t=4`;
- `s=(3,3,3)`, `d=(0,0,2)`, `t=4`;
- `s=(3,3,3)`, `d=(0,1,1)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 84-case certificate
is stored in `search23/q15_cap60_681_762_843_924_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=8,n3=1,cap<=60,p>=15,e_R>=38-p`,
`n1=7,n2=6,n3=2,cap<=60,p>=15,e_R>=38-p`,
`n1=8,n2=4,n3=3,cap<=60,p>=15,e_R>=38-p`, and
`n1=9,n2=2,n3=4,cap<=60,p>=15,e_R>=38-p`.

### V97. q=15, cap60 triple `(7,7,1)` / `(8,5,2)` / `(9,3,3)` UNSAT

After V96, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=19`, with profiles `(7,7,1)`, `(8,5,2)`, and `(9,3,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=39-p`, `M<=60`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap60_771_852_933_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=60,p>=15,e_R>=39-p`,
`n1=8,n2=5,n3=2,cap<=60,p>=15,e_R>=39-p`, and
`n1=9,n2=3,n3=3,cap<=60,p>=15,e_R>=39-p`.

### V98. q=15, cap60 triple `(8,6,1)` / `(9,4,2)` / `(10,2,3)` UNSAT

After V97, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=20`, with profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The
corresponding scalar band is `p=15..20`, `e_R=40-p`, `M<=60`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For profile `(10,2,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,1)`, `t=3`;
- `s=(2,4,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,0,2)`, `t=3`;
- `s=(3,3,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,2,0)`, `t=3`;
- `s=(3,3,4)`, `d=(1,1,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 138-case certificate
is stored in `search23/q15_cap60_861_942_1023_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=60,p>=15,e_R>=40-p`,
`n1=9,n2=4,n3=2,cap<=60,p>=15,e_R>=40-p`, and
`n1=10,n2=2,n3=3,cap<=60,p>=15,e_R>=40-p`.

### V99. q=15, cap60 pair `(9,5,1)` / `(10,3,2)` UNSAT

After V98, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=21`, with profiles `(9,5,1)` and `(10,3,2)`.  The corresponding
scalar band is `p=15..20`, `e_R=41-p`, `M<=60`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap60_951_1032_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=60,p>=15,e_R>=41-p` and
`n1=10,n2=3,n3=2,cap<=60,p>=15,e_R>=41-p`.

### V100. q=15, cap60 triple `(9,6,0)` / `(10,4,1)` / `(11,2,2)` UNSAT

After V99, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=22`, with profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.  The
corresponding scalar band is `p=15..20`, `e_R=42-p`, `M<=60`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 126-case certificate
is stored in `search23/q15_cap60_960_1041_1122_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=60,p>=15,e_R>=42-p`,
`n1=10,n2=4,n3=1,cap<=60,p>=15,e_R>=42-p`, and
`n1=11,n2=2,n3=2,cap<=60,p>=15,e_R>=42-p`.

### V101. q=15, cap60 triple `(10,5,0)` / `(11,3,1)` / `(12,1,2)` UNSAT

After V100, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=23`, with profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.  The
corresponding scalar band is `p=15..20`, `e_R=43-p`, `M<=60`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For profile `(12,1,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,1,0)`, `t=2`;
- `s=(4,4,4)`, `d=(0,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap60_1050_1131_1212_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=60,p>=15,e_R>=43-p`,
`n1=11,n2=3,n3=1,cap<=60,p>=15,e_R>=43-p`, and
`n1=12,n2=1,n3=2,cap<=60,p>=15,e_R>=43-p`.

### V102. q=15, cap60 pair `(11,4,0)` / `(12,2,1)` UNSAT

After V101, the first open cap60 q=15 frontier row is `M=60`, `p=20`,
`e_R=24`, with profiles `(11,4,0)` and `(12,2,1)`.  The corresponding
scalar band is `p=15..20`, `e_R=44-p`, `M<=60`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,2,1)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap60_1140_1221_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=60,p>=15,e_R>=44-p` and
`n1=12,n2=2,n3=1,cap<=60,p>=15,e_R>=44-p`.

### V103. q=15, final cap60 pair `(12,3,0)` / `(13,1,1)` UNSAT

After V102, the only remaining cap60 q=15 frontier rows are the scalar band
`p=15..20`, `e_R=45-p`, with profiles `(12,3,0)` and `(13,1,1)`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For profile `(13,1,1)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,5)`, `d=(0,0,1)`, `t=1`.

For both orbits and every exact scalar case `p=15..20`, `e_R=45-p`,
`M<=60`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap60_1230_1311_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=12,n2=3,n3=0,cap<=60,p>=15,e_R>=45-p` and
`n1=13,n2=1,n3=1,cap<=60,p>=15,e_R>=45-p`.

Post-V103 frontier audit: `search23/q15_frontier_after_V103/AUDIT.out` has no
remaining `M=60` row.  The first open row is `M=61`, `p=20`, `e_R=17`, with
profiles `(6,8,1)`, `(7,6,2)`, `(8,4,3)`, and `(9,2,4)`.  The list-only run
reports 216 remaining q=15 scalar jobs.

### V104. q=15, cap61 quartet `(6,8,1)` / `(7,6,2)` / `(8,4,3)` / `(9,2,4)` UNSAT

The first cap61 frontier row after closing cap60 is `M=61`, `p=20`,
`e_R=17`, with profiles `(6,8,1)`, `(7,6,2)`, `(8,4,3)`, and `(9,2,4)`.
The corresponding scalar band is `p=15..20`, `e_R=37-p`, `M<=61`.

For profile `(6,8,1)`, the support-shape frontier has 3 canonical orbits:

- `s=(0,0,6)`, `d=(0,0,8)`, `t=1`;
- `s=(0,3,3)`, `d=(0,3,5)`, `t=1`;
- `s=(0,3,3)`, `d=(0,4,4)`, `t=1`.

For profile `(7,6,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,6)`, `t=2`;
- `s=(0,3,4)`, `d=(0,3,3)`, `t=2`;
- `s=(1,3,3)`, `d=(0,2,4)`, `t=2`;
- `s=(1,3,3)`, `d=(0,3,3)`, `t=2`.

For profile `(8,4,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,4)`, `t=3`;
- `s=(1,3,4)`, `d=(0,2,2)`, `t=3`;
- `s=(2,3,3)`, `d=(0,1,3)`, `t=3`;
- `s=(2,3,3)`, `d=(0,2,2)`, `t=3`.

For profile `(9,2,4)`, the support-shape frontier has 3 canonical orbits:

- `s=(2,3,4)`, `d=(0,1,1)`, `t=4`;
- `s=(3,3,3)`, `d=(0,0,2)`, `t=4`;
- `s=(3,3,3)`, `d=(0,1,1)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=37-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 84-case certificate
is stored in `search23/q15_cap61_681_762_843_924_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=6,n2=8,n3=1,cap<=61,p>=15,e_R>=37-p`,
`n1=7,n2=6,n3=2,cap<=61,p>=15,e_R>=37-p`,
`n1=8,n2=4,n3=3,cap<=61,p>=15,e_R>=37-p`, and
`n1=9,n2=2,n3=4,cap<=61,p>=15,e_R>=37-p`.

### V105. q=15, cap61 triple `(7,7,1)` / `(8,5,2)` / `(9,3,3)` UNSAT

The first open cap61 row after V104 is `M=61`, `p=20`, `e_R=18`, with
profiles `(7,7,1)`, `(8,5,2)`, and `(9,3,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=38-p`, `M<=61`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap61_771_852_933_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=61,p>=15,e_R>=38-p`,
`n1=8,n2=5,n3=2,cap<=61,p>=15,e_R>=38-p`, and
`n1=9,n2=3,n3=3,cap<=61,p>=15,e_R>=38-p`.

Post-V105 frontier audit: `search23/q15_frontier_after_V105/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=18` row.  The first open row is `M=61`,
`p=20`, `e_R=19`, with profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.
The list-only run reports 204 remaining q=15 scalar jobs.

### V106. q=15, cap61 triple `(8,6,1)` / `(9,4,2)` / `(10,2,3)` UNSAT

The first open cap61 row after V105 is `M=61`, `p=20`, `e_R=19`, with
profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=39-p`, `M<=61`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For profile `(10,2,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,1)`, `t=3`;
- `s=(2,4,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,0,2)`, `t=3`;
- `s=(3,3,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,2,0)`, `t=3`;
- `s=(3,3,4)`, `d=(1,1,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 138-case certificate
is stored in `search23/q15_cap61_861_942_1023_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=61,p>=15,e_R>=39-p`,
`n1=9,n2=4,n3=2,cap<=61,p>=15,e_R>=39-p`, and
`n1=10,n2=2,n3=3,cap<=61,p>=15,e_R>=39-p`.

Post-V106 frontier audit: `search23/q15_frontier_after_V106/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=19` row.  The first open row is `M=61`,
`p=20`, `e_R=20`, with profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.
The list-only run reports 198 remaining q=15 scalar jobs.

### V107. q=15, cap61 triple `(9,5,1)` / `(10,3,2)` / `(11,1,3)` UNSAT

The first open cap61 row after V106 is `M=61`, `p=20`, `e_R=20`, with
profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=40-p`, `M<=61`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For profile `(11,1,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,5)`, `d=(0,0,1)`, `t=3`;
- `s=(3,3,5)`, `d=(0,1,0)`, `t=3`;
- `s=(3,4,4)`, `d=(0,0,1)`, `t=3`;
- `s=(3,4,4)`, `d=(1,0,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 132-case certificate
is stored in `search23/q15_cap61_951_1032_1113_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=61,p>=15,e_R>=40-p`,
`n1=10,n2=3,n3=2,cap<=61,p>=15,e_R>=40-p`, and
`n1=11,n2=1,n3=3,cap<=61,p>=15,e_R>=40-p`.

Post-V107 frontier audit: `search23/q15_frontier_after_V107/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=20` row.  The first open row is `M=61`,
`p=20`, `e_R=21`, with profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.
The list-only run reports 192 remaining q=15 scalar jobs.

### V108. q=15, cap61 triple `(9,6,0)` / `(10,4,1)` / `(11,2,2)` UNSAT

The first open cap61 row after V107 is `M=61`, `p=20`, `e_R=21`, with
profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=41-p`, `M<=61`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 126-case certificate
is stored in `search23/q15_cap61_960_1041_1122_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=61,p>=15,e_R>=41-p`,
`n1=10,n2=4,n3=1,cap<=61,p>=15,e_R>=41-p`, and
`n1=11,n2=2,n3=2,cap<=61,p>=15,e_R>=41-p`.

Post-V108 frontier audit: `search23/q15_frontier_after_V108/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=21` row.  The first open row is `M=61`,
`p=20`, `e_R=22`, with profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.
The list-only run reports 186 remaining q=15 scalar jobs.

### V109. q=15, cap61 triple `(10,5,0)` / `(11,3,1)` / `(12,1,2)` UNSAT

The first open cap61 row after V108 is `M=61`, `p=20`, `e_R=22`, with
profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=42-p`, `M<=61`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For profile `(12,1,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,1,0)`, `t=2`;
- `s=(4,4,4)`, `d=(0,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap61_1050_1131_1212_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=61,p>=15,e_R>=42-p`,
`n1=11,n2=3,n3=1,cap<=61,p>=15,e_R>=42-p`, and
`n1=12,n2=1,n3=2,cap<=61,p>=15,e_R>=42-p`.

Post-V109 frontier audit: `search23/q15_frontier_after_V109/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=22` row.  The first open row is `M=61`,
`p=20`, `e_R=23`, with profiles `(11,4,0)` and `(12,2,1)`.
The list-only run reports 180 remaining q=15 scalar jobs.

### V110. q=15, cap61 pair `(11,4,0)` / `(12,2,1)` UNSAT

The first open cap61 row after V109 is `M=61`, `p=20`, `e_R=23`, with
profiles `(11,4,0)` and `(12,2,1)`.  The corresponding scalar band is
`p=15..20`, `e_R=43-p`, `M<=61`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,2,1)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 36-case certificate
is stored in `search23/q15_cap61_1140_1221_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=61,p>=15,e_R>=43-p` and
`n1=12,n2=2,n3=1,cap<=61,p>=15,e_R>=43-p`.

Post-V110 frontier audit: `search23/q15_frontier_after_V110/AUDIT.out` has no
remaining `M=61`, `p=20`, `e_R=23` row.  The first open row is `M=61`,
`p=20`, `e_R=24`, with profiles `(12,3,0)` and `(13,1,1)`.
The list-only run reports 174 remaining q=15 scalar jobs.

### V111. q=15, final cap61 pair `(12,3,0)` / `(13,1,1)` UNSAT

The first open cap61 row after V110 is `M=61`, `p=20`, `e_R=24`, with
profiles `(12,3,0)` and `(13,1,1)`.  The corresponding scalar band is
`p=15..20`, `e_R=44-p`, `M<=61`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For profile `(13,1,1)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,5)`, `d=(0,0,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=44-p`,
`M<=61`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap61_1230_1311_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=12,n2=3,n3=0,cap<=61,p>=15,e_R>=44-p` and
`n1=13,n2=1,n3=1,cap<=61,p>=15,e_R>=44-p`.

Post-V111 frontier audit: `search23/q15_frontier_after_V111/AUDIT.out` has no
remaining `M=61` row.  The first open row is `M=62`, `p=20`, `e_R=17`, with
profiles `(7,7,1)`, `(8,5,2)`, `(9,3,3)`, and `(10,1,4)`.  The list-only
run reports 168 remaining q=15 scalar jobs.

### V112. q=15, cap62 quartet `(7,7,1)` / `(8,5,2)` / `(9,3,3)` / `(10,1,4)` UNSAT

The first open cap62 row after V111 is `M=62`, `p=20`, `e_R=17`, with
profiles `(7,7,1)`, `(8,5,2)`, `(9,3,3)`, and `(10,1,4)`.  The corresponding
scalar band is `p=15..20`, `e_R=37-p`, `M<=62`.

For profile `(7,7,1)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,7)`, `d=(0,0,7)`, `t=1`;
- `s=(0,3,4)`, `d=(0,3,4)`, `t=1`;
- `s=(0,3,4)`, `d=(0,4,3)`, `t=1`;
- `s=(1,3,3)`, `d=(0,2,5)`, `t=1`;
- `s=(1,3,3)`, `d=(0,3,4)`, `t=1`.

For profile `(8,5,2)`, the support-shape frontier has 5 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,5)`, `t=2`;
- `s=(1,3,4)`, `d=(0,2,3)`, `t=2`;
- `s=(1,3,4)`, `d=(0,3,2)`, `t=2`;
- `s=(2,3,3)`, `d=(0,1,4)`, `t=2`;
- `s=(2,3,3)`, `d=(0,2,3)`, `t=2`.

For profile `(9,3,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,3)`, `t=3`;
- `s=(2,3,4)`, `d=(0,1,2)`, `t=3`;
- `s=(2,3,4)`, `d=(0,2,1)`, `t=3`;
- `s=(3,3,3)`, `d=(0,0,3)`, `t=3`;
- `s=(3,3,3)`, `d=(0,1,2)`, `t=3`;
- `s=(3,3,3)`, `d=(1,1,1)`, `t=3`.

For profile `(10,1,4)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,4)`, `d=(0,0,1)`, `t=4`;
- `s=(3,3,4)`, `d=(0,1,0)`, `t=4`.

For every orbit and every exact scalar case `p=15..20`, `e_R=37-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 108-case certificate
is stored in `search23/q15_cap62_771_852_933_1014_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=7,n2=7,n3=1,cap<=62,p>=15,e_R>=37-p`,
`n1=8,n2=5,n3=2,cap<=62,p>=15,e_R>=37-p`,
`n1=9,n2=3,n3=3,cap<=62,p>=15,e_R>=37-p`, and
`n1=10,n2=1,n3=4,cap<=62,p>=15,e_R>=37-p`.

Post-V112 frontier audit: `search23/q15_frontier_after_V112/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=17` row.  The first open row is `M=62`,
`p=20`, `e_R=18`, with profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.
The list-only run reports 162 remaining q=15 scalar jobs.

### V113. q=15, cap62 triple `(8,6,1)` / `(9,4,2)` / `(10,2,3)` UNSAT

The first open cap62 row after V112 is `M=62`, `p=20`, `e_R=18`, with
profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=38-p`, `M<=62`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For profile `(10,2,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,1)`, `t=3`;
- `s=(2,4,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,0,2)`, `t=3`;
- `s=(3,3,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,2,0)`, `t=3`;
- `s=(3,3,4)`, `d=(1,1,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 138-case certificate
is stored in `search23/q15_cap62_861_942_1023_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=62,p>=15,e_R>=38-p`,
`n1=9,n2=4,n3=2,cap<=62,p>=15,e_R>=38-p`, and
`n1=10,n2=2,n3=3,cap<=62,p>=15,e_R>=38-p`.

Post-V113 frontier audit: `search23/q15_frontier_after_V113/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=18` row.  The first open row is `M=62`,
`p=20`, `e_R=19`, with profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.
The list-only run reports 156 remaining q=15 scalar jobs.

### V114. q=15, cap62 triple `(9,5,1)` / `(10,3,2)` / `(11,1,3)` UNSAT

The first open cap62 row after V113 is `M=62`, `p=20`, `e_R=19`, with
profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=39-p`, `M<=62`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For profile `(11,1,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,5)`, `d=(0,0,1)`, `t=3`;
- `s=(3,3,5)`, `d=(0,1,0)`, `t=3`;
- `s=(3,4,4)`, `d=(0,0,1)`, `t=3`;
- `s=(3,4,4)`, `d=(1,0,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 132-case certificate
is stored in `search23/q15_cap62_951_1032_1113_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=62,p>=15,e_R>=39-p`,
`n1=10,n2=3,n3=2,cap<=62,p>=15,e_R>=39-p`, and
`n1=11,n2=1,n3=3,cap<=62,p>=15,e_R>=39-p`.

Post-V114 frontier audit: `search23/q15_frontier_after_V114/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=19` row.  The first open row is `M=62`,
`p=20`, `e_R=20`, with profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.
The list-only run reports 150 remaining q=15 scalar jobs.

### V115. q=15, cap62 triple `(9,6,0)` / `(10,4,1)` / `(11,2,2)` UNSAT

The first open cap62 row after V114 is `M=62`, `p=20`, `e_R=20`, with
profiles `(9,6,0)`, `(10,4,1)`, and `(11,2,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=40-p`, `M<=62`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 126-case certificate
is stored in `search23/q15_cap62_960_1041_1122_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=62,p>=15,e_R>=40-p`,
`n1=10,n2=4,n3=1,cap<=62,p>=15,e_R>=40-p`, and
`n1=11,n2=2,n3=2,cap<=62,p>=15,e_R>=40-p`.

Post-V115 frontier audit: `search23/q15_frontier_after_V115/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=20` row.  The first open row is `M=62`,
`p=20`, `e_R=21`, with profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.
The list-only run reports 144 remaining q=15 scalar jobs.

### V116. q=15, cap62 triple `(10,5,0)` / `(11,3,1)` / `(12,1,2)` UNSAT

The first open cap62 row after V115 is `M=62`, `p=20`, `e_R=21`, with
profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=41-p`, `M<=62`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For profile `(12,1,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,1,0)`, `t=2`;
- `s=(4,4,4)`, `d=(0,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=41-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap62_1050_1131_1212_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=62,p>=15,e_R>=41-p`,
`n1=11,n2=3,n3=1,cap<=62,p>=15,e_R>=41-p`, and
`n1=12,n2=1,n3=2,cap<=62,p>=15,e_R>=41-p`.

Post-V116 frontier audit: `search23/q15_frontier_after_V116/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=21` row.  The first open row is `M=62`,
`p=20`, `e_R=22`, with profiles `(11,4,0)`, `(12,2,1)`, and `(13,0,2)`.
The list-only run reports 138 remaining q=15 scalar jobs.

### V117. q=15, cap62 triple `(11,4,0)` / `(12,2,1)` / `(13,0,2)` UNSAT

The first open cap62 row after V116 is `M=62`, `p=20`, `e_R=22`, with
profiles `(11,4,0)`, `(12,2,1)`, and `(13,0,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=42-p`, `M<=62`.

For profile `(11,4,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,5)`, `d=(1,1,2)`, `t=0`;
- `s=(3,4,4)`, `d=(1,1,2)`, `t=0`.

For profile `(12,2,1)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,0,2)`, `t=1`;
- `s=(3,4,5)`, `d=(0,1,1)`, `t=1`;
- `s=(4,4,4)`, `d=(0,1,1)`, `t=1`.

For profile `(13,0,2)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,5)`, `d=(0,0,0)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=42-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 42-case certificate
is stored in `search23/q15_cap62_1140_1221_1302_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=11,n2=4,n3=0,cap<=62,p>=15,e_R>=42-p`,
`n1=12,n2=2,n3=1,cap<=62,p>=15,e_R>=42-p`, and
`n1=13,n2=0,n3=2,cap<=62,p>=15,e_R>=42-p`.

Post-V117 frontier audit: `search23/q15_frontier_after_V117/AUDIT.out` has no
remaining `M=62`, `p=20`, `e_R=22` row.  The first open row is `M=62`,
`p=20`, `e_R=23`, with profiles `(12,3,0)` and `(13,1,1)`.  The list-only
run reports 132 remaining q=15 scalar jobs.

### V118. q=15, final cap62 pair `(12,3,0)` / `(13,1,1)` UNSAT

The first open cap62 row after V117 is `M=62`, `p=20`, `e_R=23`, with
profiles `(12,3,0)` and `(13,1,1)`.  The corresponding scalar band is
`p=15..20`, `e_R=43-p`, `M<=62`.

For profile `(12,3,0)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,4)`, `d=(1,1,1)`, `t=0`.

For profile `(13,1,1)`, the support-shape frontier has 1 canonical orbit:

- `s=(4,4,5)`, `d=(0,0,1)`, `t=1`.

For every orbit and every exact scalar case `p=15..20`, `e_R=43-p`,
`M<=62`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 12-case certificate
is stored in `search23/q15_cap62_1230_1311_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=12,n2=3,n3=0,cap<=62,p>=15,e_R>=43-p` and
`n1=13,n2=1,n3=1,cap<=62,p>=15,e_R>=43-p`.

Post-V118 frontier audit: `search23/q15_frontier_after_V118/AUDIT.out` has no
remaining `M=62` row.  The first open row is `M=63`, `p=20`, `e_R=17`, with
profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The list-only run reports
126 remaining q=15 scalar jobs.

### V119. q=15, cap63 triple `(8,6,1)` / `(9,4,2)` / `(10,2,3)` UNSAT

The first open cap63 row after V118 is `M=63`, `p=20`, `e_R=17`, with
profiles `(8,6,1)`, `(9,4,2)`, and `(10,2,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=37-p`, `M<=63`.

For profile `(8,6,1)`, the support-shape frontier has 8 canonical orbits:

- `s=(0,0,8)`, `d=(0,0,6)`, `t=1`;
- `s=(0,3,5)`, `d=(0,3,3)`, `t=1`;
- `s=(0,4,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,2,4)`, `t=1`;
- `s=(1,3,4)`, `d=(0,3,3)`, `t=1`;
- `s=(1,3,4)`, `d=(0,4,2)`, `t=1`;
- `s=(2,3,3)`, `d=(0,2,4)`, `t=1`;
- `s=(2,3,3)`, `d=(0,3,3)`, `t=1`.

For profile `(9,4,2)`, the support-shape frontier has 9 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,4)`, `t=2`;
- `s=(1,3,5)`, `d=(0,2,2)`, `t=2`;
- `s=(1,4,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,1,3)`, `t=2`;
- `s=(2,3,4)`, `d=(0,2,2)`, `t=2`;
- `s=(2,3,4)`, `d=(0,3,1)`, `t=2`;
- `s=(3,3,3)`, `d=(0,1,3)`, `t=2`;
- `s=(3,3,3)`, `d=(0,2,2)`, `t=2`;
- `s=(3,3,3)`, `d=(1,1,2)`, `t=2`.

For profile `(10,2,3)`, the support-shape frontier has 6 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,1)`, `t=3`;
- `s=(2,4,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,0,2)`, `t=3`;
- `s=(3,3,4)`, `d=(0,1,1)`, `t=3`;
- `s=(3,3,4)`, `d=(0,2,0)`, `t=3`;
- `s=(3,3,4)`, `d=(1,1,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=37-p`,
`M<=63`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 138-case certificate
is stored in `search23/q15_cap63_861_942_1023_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=8,n2=6,n3=1,cap<=63,p>=15,e_R>=37-p`,
`n1=9,n2=4,n3=2,cap<=63,p>=15,e_R>=37-p`, and
`n1=10,n2=2,n3=3,cap<=63,p>=15,e_R>=37-p`.

Post-V119 frontier audit: `search23/q15_frontier_after_V119/AUDIT.out` has no
remaining `M=63`, `p=20`, `e_R=17` row.  The first open row is `M=63`,
`p=20`, `e_R=18`, with profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.
The list-only run reports 120 remaining q=15 scalar jobs.

### V120. q=15, cap63 triple `(9,5,1)` / `(10,3,2)` / `(11,1,3)` UNSAT

The first open cap63 row after V119 is `M=63`, `p=20`, `e_R=18`, with
profiles `(9,5,1)`, `(10,3,2)`, and `(11,1,3)`.  The corresponding scalar
band is `p=15..20`, `e_R=38-p`, `M<=63`.

For profile `(9,5,1)`, the support-shape frontier has 10 canonical orbits:

- `s=(0,0,9)`, `d=(0,0,5)`, `t=1`;
- `s=(1,3,5)`, `d=(0,2,3)`, `t=1`;
- `s=(1,3,5)`, `d=(0,3,2)`, `t=1`;
- `s=(1,4,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,1,4)`, `t=1`;
- `s=(2,3,4)`, `d=(0,2,3)`, `t=1`;
- `s=(2,3,4)`, `d=(0,3,2)`, `t=1`;
- `s=(3,3,3)`, `d=(0,2,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,1,3)`, `t=1`;
- `s=(3,3,3)`, `d=(1,2,2)`, `t=1`.

For profile `(10,3,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,5)`, `d=(0,1,2)`, `t=2`;
- `s=(2,3,5)`, `d=(0,2,1)`, `t=2`;
- `s=(2,4,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,0,3)`, `t=2`;
- `s=(3,3,4)`, `d=(0,1,2)`, `t=2`;
- `s=(3,3,4)`, `d=(0,2,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,1,1)`, `t=2`;
- `s=(3,3,4)`, `d=(1,2,0)`, `t=2`.

For profile `(11,1,3)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,5)`, `d=(0,0,1)`, `t=3`;
- `s=(3,3,5)`, `d=(0,1,0)`, `t=3`;
- `s=(3,4,4)`, `d=(0,0,1)`, `t=3`;
- `s=(3,4,4)`, `d=(1,0,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=38-p`,
`M<=63`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 132-case certificate
is stored in `search23/q15_cap63_951_1032_1113_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=5,n3=1,cap<=63,p>=15,e_R>=38-p`,
`n1=10,n2=3,n3=2,cap<=63,p>=15,e_R>=38-p`, and
`n1=11,n2=1,n3=3,cap<=63,p>=15,e_R>=38-p`.

Post-V120 frontier audit: `search23/q15_frontier_after_V120/AUDIT.out` has no
remaining `M=63`, `p=20`, `e_R=18` row.  The first open row is `M=63`,
`p=20`, `e_R=19`, with profiles `(9,6,0)`, `(10,4,1)`, `(11,2,2)`, and
`(12,0,3)`.  The list-only run reports 114 remaining q=15 scalar jobs.

### V121. q=15, cap63 quartet `(9,6,0)` / `(10,4,1)` / `(11,2,2)` / `(12,0,3)` UNSAT

The first open cap63 row after V120 is `M=63`, `p=20`, `e_R=19`, with
profiles `(9,6,0)`, `(10,4,1)`, `(11,2,2)`, and `(12,0,3)`.  The corresponding
scalar band is `p=15..20`, `e_R=39-p`, `M<=63`.

For profile `(9,6,0)`, the support-shape frontier has 2 canonical orbits:

- `s=(3,3,3)`, `d=(1,2,3)`, `t=0`;
- `s=(3,3,3)`, `d=(2,2,2)`, `t=0`.

For profile `(10,4,1)`, the support-shape frontier has 11 canonical orbits:

- `s=(1,3,6)`, `d=(0,2,2)`, `t=1`;
- `s=(1,4,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,3,5)`, `d=(0,1,3)`, `t=1`;
- `s=(2,3,5)`, `d=(0,2,2)`, `t=1`;
- `s=(2,4,4)`, `d=(0,1,3)`, `t=1`;
- `s=(2,4,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(0,1,3)`, `t=1`;
- `s=(3,3,4)`, `d=(0,2,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,1,2)`, `t=1`;
- `s=(3,3,4)`, `d=(1,2,1)`, `t=1`;
- `s=(3,3,4)`, `d=(2,2,0)`, `t=1`.

For profile `(11,2,2)`, the support-shape frontier has 8 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,1)`, `t=2`;
- `s=(2,4,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(0,0,2)`, `t=2`;
- `s=(3,3,5)`, `d=(0,1,1)`, `t=2`;
- `s=(3,3,5)`, `d=(1,1,0)`, `t=2`;
- `s=(3,4,4)`, `d=(0,0,2)`, `t=2`;
- `s=(3,4,4)`, `d=(0,1,1)`, `t=2`;
- `s=(3,4,4)`, `d=(1,0,1)`, `t=2`.

For profile `(12,0,3)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,0)`, `t=3`;
- `s=(3,4,5)`, `d=(0,0,0)`, `t=3`;
- `s=(4,4,4)`, `d=(0,0,0)`, `t=3`.

For every orbit and every exact scalar case `p=15..20`, `e_R=39-p`,
`M<=63`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 144-case certificate
is stored in `search23/q15_cap63_960_1041_1122_1203_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=9,n2=6,n3=0,cap<=63,p>=15,e_R>=39-p`,
`n1=10,n2=4,n3=1,cap<=63,p>=15,e_R>=39-p`,
`n1=11,n2=2,n3=2,cap<=63,p>=15,e_R>=39-p`, and
`n1=12,n2=0,n3=3,cap<=63,p>=15,e_R>=39-p`.

Post-V121 frontier audit: `search23/q15_frontier_after_V121/AUDIT.out` has no
remaining `M=63`, `p=20`, `e_R=19` row.  The first open row is `M=63`,
`p=20`, `e_R=20`, with profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.
The list-only run reports 108 remaining q=15 scalar jobs.

### V122. q=15, cap63 triple `(10,5,0)` / `(11,3,1)` / `(12,1,2)` UNSAT

The first open cap63 row after V121 is `M=63`, `p=20`, `e_R=20`, with
profiles `(10,5,0)`, `(11,3,1)`, and `(12,1,2)`.  The corresponding scalar
band is `p=15..20`, `e_R=40-p`, `M<=63`.

For profile `(10,5,0)`, the support-shape frontier has 3 canonical orbits:

- `s=(3,3,4)`, `d=(1,1,3)`, `t=0`;
- `s=(3,3,4)`, `d=(1,2,2)`, `t=0`;
- `s=(3,3,4)`, `d=(2,2,1)`, `t=0`.

For profile `(11,3,1)`, the support-shape frontier has 9 canonical orbits:

- `s=(2,3,6)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,1,2)`, `t=1`;
- `s=(2,4,5)`, `d=(0,2,1)`, `t=1`;
- `s=(3,3,5)`, `d=(0,0,3)`, `t=1`;
- `s=(3,3,5)`, `d=(0,1,2)`, `t=1`;
- `s=(3,3,5)`, `d=(1,1,1)`, `t=1`;
- `s=(3,4,4)`, `d=(0,1,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,0,2)`, `t=1`;
- `s=(3,4,4)`, `d=(1,1,1)`, `t=1`.

For profile `(12,1,2)`, the support-shape frontier has 4 canonical orbits:

- `s=(3,3,6)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,0,1)`, `t=2`;
- `s=(3,4,5)`, `d=(0,1,0)`, `t=2`;
- `s=(4,4,4)`, `d=(0,0,1)`, `t=2`.

For every orbit and every exact scalar case `p=15..20`, `e_R=40-p`,
`M<=63`, the fixed-label SAT verifier with all paired rooted-cut inequalities
added before solving returns CaDiCaL status code 20.  The 96-case certificate
is stored in `search23/q15_cap63_1050_1131_1212_static_batch`.

Status: VERIFIED computational certificate.  Add scalar cuts
`n1=10,n2=5,n3=0,cap<=63,p>=15,e_R>=40-p`,
`n1=11,n2=3,n3=1,cap<=63,p>=15,e_R>=40-p`, and
`n1=12,n2=1,n3=2,cap<=63,p>=15,e_R>=40-p`.

Post-V122 frontier audit: `search23/q15_frontier_after_V122/AUDIT.out` has no
remaining `M=63`, `p=20`, `e_R=20` row.  The first open row is `M=63`,
`p=20`, `e_R=21`, with profiles `(11,4,0)`, `(12,2,1)`, and `(13,0,2)`.
The list-only run reports 102 remaining q=15 scalar jobs.

### V123. q=15 shadow-count lemma closes the scalar universe

In the q=15 branch, with the minimum-codegree root `xy`, let
`C={c_1,c_2,c_3}` and `U_i=N_R(c_i)`.  The local condition already used by the
static verifier is:

for every `r in R \ U_i`, vertex `r` has at least three neighbours in `U_i`.

This condition is encoded in `search23/sat_q15_shape_family.cpp`: for each
R-vertex label and each missing colour `i`, the verifier requires at least
three R-edge variables from that vertex to vertices whose label contains `i`.

Write singleton labels as `S_i={i}` and doubleton labels as
`D_i={1,2,3}\{i}`.  R-edges are allowed only between disjoint labels, hence
only between `S_i,S_j` for `i!=j` or between `S_i,D_i`.

Doubletons: a vertex in `D_i` is missing colour `i`, and its only possible
neighbours in `U_i` have label `S_i`; therefore the `S_i-D_i` channels contain
at least `3 d_i` edges.  Summing gives `e_R >= 3 n2`.

Singletons: a vertex in `S_i` is missing the two other colours.  Its two local
requirements demand at least six incidences to R-neighbours.  Any R-edge
contributes to at most two such singleton requirements, so `2 e_R >= 6 n1`,
or `e_R >= 3 n1`.

Therefore every realizable q=15 count profile satisfies

`e_R >= 3 * max(n1,n2)`.

This hand lemma has been added to
`search23/sat_q15_ru_scalar_exhaust.cpp`,
`search23/q15_profile_audit.cpp`, and `search23/q15_shape_frontier.cpp`.
After recompilation, the list-only scalar audit
`search23/q15_frontier_after_shadow/AUDIT.out` reports `active=0`, and
`search23/q15_frontier_after_shadow/JOBS.tsv` has size `0`.

Status: VERIFIED hand lemma plus exact scalar audit.  The q=15 scalar branch is
closed relative to the V14 minimum-codegree local setup and the previously
verified cap certificates.

### V124. q=14/t=2 low-cap fixed-label certificates

For the next low-codegree branch `t=2`, `|C|=2`, `|A|=|B|=6`,
`|R|=14`, labels are masks in `{0,1,2,3}` relative to
`U_i=N_R(c_i)`.  The q=15 paired-root derivation specializes to:

- `2 bd_R(W) <= e_R + 53 - U - p + 2 m(W)`;
- `2 bd_R(W) <= p + e_R + 49 - U + g(W)+g(R\W)`.

The constant `53` is `123 + 2t - 74` with `t=2`; the second constant remains
`49`.  A fixed-label verifier was added:

`E:\Projects\ErdosProblems\search23\sat_q14_t2_shape_family.cpp`

This verifier includes the q=14 thresholds from minimum nonedge-codegree `2`,
allows zero labels, forbids `R`-triangles, and applies all fixed paired-rooted
cuts for exact `R`-edge profiles.  The scalar frontier generator:

`E:\Projects\ErdosProblems\search23\q14_t2_scalar_audit.cpp`

also includes the safe `W=D` paired-cut/Mantel pruning: for the double-labelled
class `D`, non-`D` edges are bounded by
`floor(z^2/4)+z(s_1+s_2)+s_1s_2`, giving a lower bound on `bd(D)` that must
fit the paired `Psi` upper bound.

Verified batches:

- `search23/q14_t2_cap24_28_batch`: `117/117` exact cases UNSAT.
- `search23/q14_t2_cap29_30_batch`: `264/264` exact cases UNSAT, including
  reruns for the two status-race omissions.

Status: VERIFIED computational certificate for the q=14/t=2 scalar frontier
with `cap <= 30`.  The q=14/t=2 branch is not yet closed; the regenerated
frontier still has `48798` scalar rows before these new batch cuts.

### V125. q=14/t=2 strengthened scalar audit and cap <= 34 certificates

GPT Pro's q=14/t=2 response was digested in:

`E:\Projects\ErdosProblems\problems\23\gpt_q14_t2_digest_2026-06-12.md`

The following claims from that response were independently checked by local
degree/counting algebra and added to the q14 scalar audit:

- zero labels are not excluded in the stated q14 setup;
- local lower bound
  `e_R >= 2*max(s1,s2) + h(d)*z`, where `h(0)=4`, `h(1)=3`, and `h(d)=2`
  for `d>=2`;
- global degree/budget constraints `p <= 11+e_R`, hence `e_R >= 13`,
  and `p >= U+e_R-39`;
- cap lower bounds from R-degree, A/B-degree, and local A/B-R incidence
  requirements;
- Mantel `floor(z^2/4)` bound for the zero-label subgraph.

After these cuts, the scalar frontier is:

`search23/q14_t2_scalar_audit_full.tsv`

with `39780` rows.

The fixed-label verifier now also includes direct R-vertex degree constraints
and an optional lazy exact-rooted-cut CEGAR mode for the two verified rooted
families `Psi` and `Phi`.

Verified batches:

- `search23/q14_t2_cap31_32_batch`: `449/449` exact cases UNSAT.
- `search23/q14_t2_cap33_34_batch`: `626/626` exact cases UNSAT.
- `search23/q14_t2_cap35_36_batch`: `808/808` exact cases UNSAT.

Together with V124, this closes the q=14/t=2 scalar frontier for `cap <= 36`.

Canary obstruction:

- No-zero canary `z=0,d=0,s1=s2=7,p=23,e_R=14,cap=72` returned
  `SHAPE_FAMILY_STATUS 0` under `500000` conflicts even with lazy exact-rooted
  cuts.
- Zero-heavy canary `z=8,d=6,s1=s2=0,p=21,e_R=16,cap=74` did not finish within
  the local wall-clock probe and was stopped.

Status: VERIFIED computational certificate for `cap <= 36`; q14/t=2 remains
open.  The hard obstruction is now specifically high-cap A/B-R incidence,
not the scalar label shadow or paired rooted cuts alone.

### V126. q=14/t=2 cap <= 38 closed by combined A/B-R incidence

The batch

`search23/q14_t2_cap37_38_batch`

verified `1017/1025` cap `37..38` fixed-label cases UNSAT before it was
stopped at the long tail.  The eight remaining rows all had

`z=8, d=6, s1=s2=0, U=12, cap=38, p=29..36`.

These rows are killed by a direct A/B-R incidence lower bound.  For a
zero-labelled R-vertex, the nonedges to the two root vertices force at least
two A-neighbours and at least two B-neighbours, so zero labels contribute
`4z` incidences.  For the A/B vertices, the local C-hit requirement forces
incidences into the singleton or double-labelled part.  The safe scalar form
added to `search23/q14_t2_scalar_audit.cpp` is:

`cap >= 4z + max(2*(s1+s2), d==0 ? 24 : 12)`.

After recompilation, `search23/q14_t2_scalar_audit_full.tsv` has `39660`
frontier rows.  The above eight long-tail cap38 profiles no longer occur, and
the cap distribution begins:

`26:4, 27:9, 28:72, 29:85, 30:154, 31:170, 32:256, 33:275, 34:340, 35:361, 36:441, 37:468, 38:549`.

Together with V124 and V125, this closes the q=14/t=2 scalar frontier for
`cap <= 38`.  The remaining q=14/t=2 frontier has `cap=39..74`.

### V127. q=14/t=2 cap 39 fixed-label certificate

The batch

`search23/q14_t2_cap39_39_batch`

ran the exact fixed-label verifier on all `577` cap39 rows from
`search23/q14_t2_scalar_audit_full.tsv`.

Result:

- `577/577` jobs returned `SHAPE_FAMILY_STATUS 20`;
- no SAT rows;
- no unknown rows;
- runner `PROGRESS.txt` reports `elapsedSec=511`.

Together with V124--V126, this closes the q=14/t=2 scalar frontier for
`cap <= 39`.  The remaining q=14/t=2 frontier has `cap=40..74`.

### V128. q=14/t=2 cap 40 fixed-label certificate

The batch

`search23/q14_t2_cap40_40_batch`

ran the exact fixed-label verifier on all `665` cap40 rows from
`search23/q14_t2_scalar_audit_full.tsv`.

Result:

- `665/665` jobs returned `SHAPE_FAMILY_STATUS 20`;
- no SAT rows;
- no unknown rows;
- runner `PROGRESS.txt` reports `elapsedSec=611`.

Together with V124--V127, this closes the q=14/t=2 scalar frontier for
`cap <= 40`.  Of the `39660` current scalar rows, `4426` are now closed by
low-cap exact certificates plus scalar cuts; `35234` rows remain with
`cap=41..74`.

### V129. q=14/t=2 cap 41 fixed-label certificate

The batch

`search23/q14_t2_cap41_41_batch`

ran the exact fixed-label verifier on all `696` cap41 rows from
`search23/q14_t2_scalar_audit_full.tsv`.

Result:

- `696/696` jobs returned `SHAPE_FAMILY_STATUS 20`;
- no SAT rows;
- no unknown rows;
- runner `PROGRESS.txt` reports `elapsedSec=843`.

Together with V124--V128, this closes the q=14/t=2 scalar frontier for
`cap <= 41`.  Of the `39660` current scalar rows, `5122` are now closed by
low-cap exact certificates plus scalar cuts; `34538` rows remain with
`cap=42..74`.

### V130. q=14/t=2 cap 42 fixed-label certificate

The batch

`search23/q14_t2_cap42_42_batch`

ran the exact fixed-label verifier on all `788` cap42 rows from
`search23/q14_t2_scalar_audit_full.tsv`.

Result:

- `788/788` jobs returned `SHAPE_FAMILY_STATUS 20`;
- no SAT rows;
- no unknown rows;
- runner `PROGRESS.txt` reports `elapsedSec=1196`.

Together with V124--V129, this closes the q=14/t=2 scalar frontier for
`cap <= 42`.  Of the `39660` current scalar rows, `5910` are now closed by
low-cap exact certificates plus scalar cuts; `33750` rows remain with
`cap=43..74`.

### V131. q=14/t=2 clean-shadow / C-tight dichotomy

GPT Pro suggested a high-cap split in

`problems/23/gpt_q14_highcap_answer_2026-06-12.md`.

The following part has been checked by direct counting.

Call the q14/t=2 label profile **clean** if for both `i=1,2` and every
`r in R \ U_i`, one has

`d_R(r,U_i) >= 3`.

Otherwise there is a `C`-tight vertex: some `r in R \ U_i` with
`d_R(r,U_i)=2`.  For such a vertex, the nonedge `c_i r` has exactly two
common neighbours in `R`, so rerooting at `c_i r` gives a new t=2 root with
residual

`q' = 28 - |U_i| - deg(r) <= 14`,

and `q' < 14` unless `|U_i|=6` and `deg(r)=8`.  Thus a q-minimal version of
the branch reduces C-tight vertices to the extremal case
`|U_i|=6, deg(r)=8`.

On the clean side, write `z,s1,s2,d` as above.  Then

`e_R >= 3*max(s1,s2) + eta(d)*z`,

where `eta(d)=6` for `d=0`, `5` for `d=1`, `4` for `d=2`, and `3` for
`d>=3`.

Reason: clean `S1` vertices need three neighbours in `U2`, and allowed
labels force these into `S2`, so `e(S1,S2)>=3s1`; symmetrically
`e(S1,S2)>=3s2`.  Each zero-labelled vertex needs three neighbours in `U1`
and three in `U2`; a `Z-D` edge can serve both requirements, with at most
`min(d,3)` such shared neighbours, giving at least
`6-min(d,3)=eta(d)` distinct R-edges incident from that zero vertex into
`U1 union U2`.  These zero-to-nonzero edges are disjoint from `S1-S2`.

Scalar effect on the current frontier:

- clean-shadow possible rows: `30777/39660`;
- cap74 clean-shadow possible rows: exactly six:
  `(z,d,s1,s2,p,e_R) = (5,3,3,3,13,24), (6,4,2,2,13,24),
  (8,6,0,0,13,24), (5,3,3,3,12,25), (6,4,2,2,12,25),
  (8,6,0,0,12,25)`.

The verifier `search23/sat_q14_t2_shape_family.cpp` now has an optional
`clean_shadow` argument which raises the local `R \ U_i` threshold from `2`
to `3`, without changing the default mode.

Exact clean cap74 probe:

- `(5,3,3,3,13,24)`: UNSAT;
- `(6,4,2,2,13,24)`: UNSAT;
- `(5,3,3,3,12,25)`: UNSAT;
- `(6,4,2,2,12,25)`: UNSAT;
- `(8,6,0,0,13,24)`: SAT without exact rooted CEGAR; with exact rooted CEGAR
  it reached `SHAPE_FAMILY_STATUS 0` after `16` rooted cuts at the 500k
  conflict limit;
- `(8,6,0,0,12,25)`: SAT without exact rooted CEGAR; exact rooted CEGAR was
  stopped after the local wall-clock probe.

Status: VERIFIED clean-shadow counting lemma and cap74 clean reduction, but
q14/t=2 is not closed.  The remaining high-cap obstruction is the clean
zero/doubleton-heavy family `z=8,d=6,s1=s2=0` plus the C-tight reroot side.

### V132. q=14/t=2 clean `z=8,d=6` witness rooted-cut obstruction

The file

`search23/q14_t2_clean_cap74_probe/z8d6_p13_e24_no_rooted.out`

contains a SAT model for the clean-shadow verifier with exact rooted cuts
disabled, for

`z=8, d=6, s1=s2=0, p=13, e_R=24, cap=74`.

This is not a valid full q14/t=2 witness: the analyzer

`search23/q14_witness_analyzer.cpp`

checks all exact rooted cuts and reports

`badCuts=241`.

The worst violations are:

- `Phi=25` on the D-only mask `{8,12,13}`;
- `Phi=27` on the D-only mask `{8,11,12,13}`;
- `Phi=28` on D-only masks `{8,12}` and `{8,13}`;
- `Psi=29` on mask `{0,1,2,3,4,5,6,7,9}`, containing all 8 zero vertices
  and one doubleton;
- `Psi=29` on mask `{8,9,11,12,13}`, containing five doubletons.

Thus the clean zero/doubleton-heavy obstruction is not just a scalar
label-count obstruction.  The missing ingredient is an exact rooted-cut
forcing argument, apparently already visible on small D-only cuts.

### V133. q=14/t=2 cap 43 fixed-label certificate

The batch

`search23/q14_t2_cap43_43_batch`

ran the exact fixed-label verifier on all `821` cap43 rows from
`search23/q14_t2_scalar_audit_full.tsv`.

Result:

- `821/821` jobs returned `SHAPE_FAMILY_STATUS 20`;
- no SAT rows;
- no unknown rows;
- runner `PROGRESS.txt` reports `elapsedSec=1637`.

Together with V124--V130, this closes the q=14/t=2 scalar frontier for
`cap <= 43`.  Of the `39660` current scalar rows, `6731` are now closed by
low-cap exact certificates plus scalar cuts; `32929` rows remain with
`cap=44..74`.

### V134. q=14/t=2 z8d6 follow-up: D-only cuts are not enough

GPT Pro's focused response is saved as

`problems/23/gpt_q14_z8d6_followup_answer_2026-06-12.md`.

The key checked conclusion is negative but useful: D-only `Phi` cuts alone do
not give a scalar hand contradiction for the clean `z=8,d=6` cap74 family.
The missing finite compatibility is the A/B rectangle two-cover condition.

For each `a in A`, `b in B`, define

`rho(a,b) = |{ r in R : a-r and b-r are both edges }|`.

Triangle-freeness gives `rho(a,b)=0` whenever `ab` is an edge.  If `ab` is a
nonedge, the minimum nonedge-codegree condition gives `rho(a,b)>=2`.  Hence
the exact condition is

`rho(a,b) != 1` for all 36 A/B cells,

and

`p = |{(a,b) : rho(a,b)=0}|`.

Equivalently, the R-incidence rectangles

`N_A(r) x N_B(r)`

must cover exactly `36-p` cells at least twice and leave exactly `p` cells
uncovered, with no cell covered exactly once.  This condition is already
present in the full fixed-label verifier through guarded A/B nonedge codegree,
but isolating it gives the next targeted finite experiment for the clean
`z=8,d=6` obstruction: enumerate only the R graph and A/B incidence
rectangles, derive `E(A,B)` from `rho=0`, and then check the remaining
A-A, B-B, A-R, and B-R nonedge-codegree constraints.

### V135. q=14/t=2 clean z8d6 p13/e24 R-graph quotient audit

For the clean `z=8,d=6,s1=s2=0`, `(p,e_R)=(13,24)` cap74 row, clean shadow
forces no zero-zero `R` edges, exactly `24` zero-doubleton `R` edges, and
every zero-label vertex to have exactly `3` neighbours in the six doubleton
vertices.

The audit

`search23/q14_z8d6_rgraph_audit.cpp`

enumerates the resulting `8 x 6` row-sum-3 matrices up to zero-row and
doubleton-column symmetry.  The 64-worker run in

`search23/q14_t2_z8d6_rgraph_audit/audit_mt.err`

reports:

- `multisets=2220075`;
- `canonical=3888`;
- `paired_ok=3888`;
- `margin_hist: 4 -> 3888`.

Thus the fixed paired cut inequalities do not eliminate any `R`-graph in this
core row; all `3888` quotient representatives pass with minimum margin `4`.
The remaining obstruction is genuinely in the A/B rectangle-incidence plus
exact rooted-cut layer.

The fixed-R incidence solver

`search23/sat_q14_z8d6_fixedR.cpp`

then fixes one such `R` graph and solves only for A/B incidence rectangles,
with `rho(a,b) != 1`, exactly `p=13` zero-rho cells, the A-A/B-B/A-R/B-R
nonedge-codegree constraints, and lazy exact rooted cuts.

Calibration:

- `search23/q14_t2_z8d6_fixedR/smoke5.err`: `5` cases, `1` UNSAT, `4`
  UNKNOWN at `20k` conflicts;
- `search23/q14_t2_z8d6_fixedR/calib200.err`: `200` cases, `36` UNSAT,
  `164` UNKNOWN, no SAT at `20k` conflicts;
- `search23/q14_t2_z8d6_fixedR/calib50_c200k.err`: `50` cases, `11` UNSAT,
  `39` UNKNOWN, no SAT at `200k` conflicts.

This is not a certificate, but it is a verified obstruction refinement:
quotienting `R` gives a small finite layer (`3888` cases), while the current
incidence encoding still needs a stronger mathematical or symmetry-breaking
lemma before it can close the row.

### V136. q=14/t=2 clean z8d6 `(p,e_R)=(13,24)` core closed

Adding a sound A-side lexicographic symmetry break to

`search23/sat_q14_z8d6_fixedR.cpp`

closes the fixed-R incidence layer for the clean `z=8,d=6`,
`(p,e_R)=(13,24)` row.

Soundness of the symmetry break: all constraints in the fixed-R incidence
problem are invariant under permutations of the six `A` vertices.  Hence any
satisfying assignment can be relabelled so that the six `A`-vertex signatures

`(missing[a,*], xa[*,a])`

are lexicographically nondecreasing.  The added clauses only impose this
canonical representative condition.

The full run

`search23/q14_t2_z8d6_fixedR/full_p13_e24_lex.err`

reports:

`FINAL done=3888 unsat=3888 sat=0 unknown=0 cutsum=6`.

Thus every zero/D-isomorphism class of the `p=13,e_R=24` clean z8d6
rectangle-incidence problem is UNSAT after the A-side symmetry break and lazy
exact rooted cuts.  This closes the first of the two clean cap74 z8d6 core
rows.  The remaining analogous clean core row is `(p,e_R)=(12,25)`.

### V137. q=14/t=2 clean z8d6 `(p,e_R)=(12,25)` no-ZZ branch closed

For the clean `z=8,d=6`, `(p,e_R)=(12,25)` row, one R-graph branch has no
zero-zero edge and `25` zero-doubleton edges.  Clean shadow then forces the
zero-D incidence matrix to have seven rows of size `3` and one row of size
`4`.

The quotient audit

`search23/q14_t2_z8d6_rgraph_audit/audit_p12_nozz.err`

reports:

- `multisets=9867000`;
- `canonical=15680`;
- `paired_ok=15680`;
- `margin_hist: 4 -> 15680`.

So fixed paired cuts again do not reduce the R quotient layer.

The fixed-R incidence solver was extended to this mode and strengthened with
the hand cuts suggested by the rectangle analysis:

- for every zero vertex, `|X_z|+|Y_z| <= 6`;
- in the `p=12` branch, each A-row and B-column of `E(A,B)` has exactly two
  present edges.

The first full run at `200k` conflicts left three UNKNOWN cases:

`search23/q14_t2_z8d6_fixedR/full_p12_e25_nozz_lex_pgen.err`

reported `15677` UNSAT, `0` SAT, `3` UNKNOWN.

The rerun at `1M` conflicts

`search23/q14_t2_z8d6_fixedR/full_p12_e25_nozz_lex_pgen_1m.err`

reports:

`FINAL done=15680 unsat=15680 sat=0 unknown=0 cutsum=744`.

Thus the no-ZZ branch of the clean `(p,e_R)=(12,25)` z8d6 core is closed.
The remaining branch has one zero-zero R edge and `24` zero-doubleton edges.

### V138. q=14/t=2 clean z8d6 `(p,e_R)=(12,25)` one-ZZ branch closed

The remaining clean `(p,e_R)=(12,25)` z8d6 branch has one zero-zero `R` edge
and `24` zero-doubleton `R` edges.  Clean shadow forces all eight zero-D rows
to have size `3`; triangle-freeness forces the two zero endpoints of the
zero-zero edge to have disjoint doubleton-neighbour sets.

The fixed-R solver mode `121` canonicalizes this branch by moving the
zero-zero edge endpoints to zero vertices `0` and `1`, sorting the remaining
zero rows, and quotienting by doubleton-column permutations.

Calibration:

`search23/q14_t2_z8d6_fixedR/p12_onezz_calib50.err`

reports `generated_graphs=2972` and `50/50` UNSAT.

The full run

`search23/q14_t2_z8d6_fixedR/full_p12_e25_onezz.err`

reports:

`FINAL done=2972 unsat=2972 sat=0 unknown=0 cutsum=36`.

Combining V136, V137, and V138 closes both clean z8d6 cap74 core rows:

- `(p,e_R)=(13,24)`;
- `(p,e_R)=(12,25)`.

Together with V131's four non-z8d6 clean cap74 probes, the clean-shadow cap74
survivor list is now exhausted.  The next task is to push these exact closures
back into the q14/t2 scalar frontier and identify the new first obstruction.

### V139. q=14/t=2 scalar frontier after clean z8d6 core cuts

The scalar audit

`search23/q14_t2_scalar_audit.cpp`

now includes the exact fixed-R incidence closures from V136--V138 as scalar
exclusions for

- `z=8,s1=s2=0,d=6,p=13,e_R=24`;
- `z=8,s1=s2=0,d=6,p=12,e_R=25`.

After recompilation, the regenerated frontier

`search23/q14_t2_scalar_audit_full.tsv`

reports `rows=39658`.  The maximum cap is still `74`, with `51` cap74 scalar
rows.  All cap74 rows have `U=12` and `p+e_R=37`.  They fall into six
label-count groups:

- `(z,s1,s2,d)=(2,6,6,0)`: `6` rows;
- `(3,5,5,1)`: `7` rows;
- `(4,4,4,2)`: `10` rows;
- `(5,3,3,3)`: `10` rows;
- `(6,2,2,4)`: `10` rows;
- `(8,0,0,6)`: `8` rows, now only `p=14..21`, `e_R=23..16`.

Conclusion: closing the clean z8d6 cap74 core was necessary but does not lower
the scalar maximum.  The remaining cap74 obstruction is the `U=12`,
`p+e_R=37` extremal band, likely corresponding to the C-tight/reroot side
rather than the clean-shadow core.

### V140. q=14/t=2 cap74 p12 category-band triage

For the cap74 row

`(z,s1,s2,d,p,e_R,U)=(3,5,5,1,12,25,12)`,

the shape verifier was extended with optional exact category counts for the
five R-edge classes:

`ZZ, ZS1, ZS2, ZD, S1S2`.

The runner

`search23/run_q14_t2_cap74_p12_cat_batch.ps1`

enumerates the `3500` category profiles with total `e_R=25`.

Triage results:

- `search23/q14_t2_cap74_p12_cat_10k/PROGRESS.txt`:
  `done=3500/3500`, `unsat=3376`, `sat=0`, `unknown=124`,
  `elapsedSec=760`.
- `search23/q14_t2_cap74_p12_cat_100k/PROGRESS.txt`:
  reran the `124` unknown profiles at `100000` conflicts:
  `unsat=0`, `sat=0`, `unknown=124`, `elapsedSec=273`.
- A no-conflict-limit run on the most extreme unknown profile
  `ZZ=0,ZS1=3,ZS2=3,ZD=3,S1S2=16` was stopped after `600s` without a
  solver result.

The remaining unknown band is concentrated at high `S1S2`:

`S1S2=10:43`, `11:33`, `12:23`, `13:14`, `14:7`, `15:3`, `16:1`.

By `(ZZ,ZD)` the unknown counts are:

`(0,3):28`, `(0,2):21`, `(0,1):15`, `(1,2):15`, `(0,0):10`,
`(1,1):10`, `(2,2):10`, `(1,0):6`, `(2,1):6`, `(2,0):3`.

Each of the `124` unknown category profiles satisfies

`S1S2 >= 10`, `ZS1+ZD >= 6`, and `ZS2+ZD >= 6`,

which are the aggregate consequences of the per-vertex label-local domination
constraints for `S1`, `S2`, and the three zero-labelled vertices.

These three aggregate local constraints leave `180` category profiles.  The
`56` profiles among these which the 10k SAT triage closed immediately are
explained by the aggregate triangle-free cut on `Z union D`:

- `ZZ=3` is impossible because the three zero-labelled vertices would form a
  triangle in `R`;
- `ZD=3` and `ZZ>=1` is impossible because the double-labelled vertex is then
  adjacent to both ends of some zero-zero edge, again forming a triangle.

Removing exactly these triangle-forced profiles from the `180` locally
admissible profiles leaves the same `124` category profiles as the UNKNOWN
band.  Thus the remaining obstruction is not visible from aggregate
label-local domination plus the `Z union D` triangle cut alone.

This was independently checked by the R-only category verifier

`search23/sat_q14_t2_r_category.cpp`.

It encodes only the R-edge category counts, disjoint-label rule,
triangle-freeness, and per-vertex q14/t2 label-local domination.  Its output

`search23/q14_t2_cap74_p12_r_category/run.err`

is:

`FINAL total=3500 sat=124 unsat=3376 unknown=0`.

The SAT category profiles from this R-only verifier match the `124` UNKNOWN
profiles from `search23/q14_t2_cap74_p12_cat_10k/status.tsv` exactly
(`r_not_unknown=0`, `unknown_not_r=0`).  Therefore the remaining frontier is
not R-category feasibility; it is the A/B incidence plus exact rooted-cut
extension problem over these R-feasible categories.

For soundness audit, `search23/sat_q14_t2_shape_family.cpp` now supports a
compile-time `LEX_MODE` macro.  The default `LEX_MODE=3` preserves the previous
simultaneous A/B lex ordering.  An A-only binary

`search23/sat_q14_t2_shape_family_cat_aonly.exe`

was compiled with `-DLEX_MODE=1` and run on the `124` profiles:

`search23/q14_t2_cap74_p12_cat_aonly_10k/PROGRESS.txt`

reports `done=124/124`, `unsat=0`, `sat=0`, `unknown=124`,
`elapsedSec=53`.  This confirms that the current hard band does not disappear
under the weaker sound A-only symmetry break; it also means the earlier
`3376` UNSAT count remains a T0 triage count until either simultaneous A/B lex
is justified or those rows are rerun under a sound symmetry scheme.

For the most extreme R-feasible category

`ZZ=0,ZS1=3,ZS2=3,ZD=3,S1S2=16`,

the R-only checker was extended with bounded model output.  It emitted 20
distinct labelled R models:

`search23/q14_t2_cap74_p12_r_category/models_0_3_3_3_16_20.tsv`.

The full q14 verifier was also extended with an optional fixed-R edge-list
input.  Using the sound A-only binary

`search23/sat_q14_t2_shape_family_fixedR_aonly.exe`,

all 20 fixed-R models closed quickly:

`search23/q14_t2_cap74_p12_fixedR20/status.tsv`

has `unsat=20`, `sat=0`, `unknown=0` at `200000` conflicts, elapsed `4s`.
This is sample evidence only, but it shows the A/B extension problem is easy
once R is fixed; the hard part is quotienting or certifying the R-model family.

A larger sample of the same extreme category is in

`search23/q14_t2_cap74_p12_fixedR500/status.tsv`.

It has `unsat=500`, `sat=0`, `unknown=0` at `200000` conflicts, elapsed `59s`.

GPT Pro's answer was saved at

`problems/23/gpt_q14_p12_extremal_band_answer_2026-06-13.md`.

Verified / currently accepted points from that answer:

- Since `p=12`, the A-B graph `P` is 2-regular on `6+6` vertices.
- For every `r`, `m_r=|X_r|+|Y_r|<=6`; this is the rectangle bound already
  encoded as `m_r<=floor(p/2)`.
- Since `M=sum_r m_r=74`, at least four R-vertices have `m_r=6`.
- If `P` were a single `C12`, then the only maximum independent sets are `A`
  and `B`; non-doubleton-labelled vertices require both A- and B-neighbours,
  so at most the single doubleton vertex could have `m_r=6`, contradicting the
  previous bullet.  Thus `P` is disconnected and only the templates
  `C8+C4`, `C6+C6`, and `3C4` need be considered in a state verifier.

Conditional terminal cut from GPT Pro:

If a q<14 reroot branch has already been closed/delegated, then any terminal
q14 R-graph may additionally satisfy

`d_R(r,U_i)=2 -> d_R(r)<=4`

for every `r` missing colour `i`.  This cut was added as an optional
`terminal` mode to `search23/sat_q14_t2_r_category.cpp`.  The R-only category
run

`search23/q14_t2_cap74_p12_r_category_terminal/run.err`

reports `FINAL total=3500 sat=41 unsat=3459 unknown=0`.  Thus the conditional
terminal q14 category frontier is only `41` profiles, almost all with `ZZ=0`.

State-table scaffold:

`search23/q14_p12_state_table.cpp`

generates the independent-set state tables for the three disconnected A-B
2-factor templates.  Its output

`search23/q14_p12_state_table/summary.tsv`

is:

- `C8+C4`: `states=329`, states with `|X|,|Y|>=2`: `46`,
  states with `|X|,|Y|>=1`: `202`, `m=6` states: `4`.
- `C6+C6`: `states=324`, states with `|X|,|Y|>=2`: `41`,
  states with `|X|,|Y|>=1`: `197`, `m=6` states: `4`.
- `3C4`: `states=343`, states with `|X|,|Y|>=2`: `60`,
  states with `|X|,|Y|>=1`: `216`, `m=6` states: `8`.

This verifies GPT Pro's claim that the exact A/B incidence problem can be
recast as a small state assignment problem over roughly `330` states per
template.

Status: this is T0 triage, not yet a proof certificate.  The current general
shape verifier uses simultaneous A/B lex ordering, which must either be
justified or replaced by a sound A-only / canonical rerun before these UNSAT
counts can be promoted to verified cuts.  The mathematical frontier is now a
structural lemma eliminating the `124` high-`S1S2` category profiles.

GPT Pro prompt:

`problems/23/gpt_q14_p12_extremal_band_prompt_2026-06-13.md`

### V141. q=14/t=2 cap74 p12 extreme R category fixed-R quotient closed

For the extreme category from V140

`ZZ=0,ZS1=3,ZS2=3,ZD=3,S1S2=16`,

the labelled R-family is too large to enumerate directly.  A canonical
quotient counter / emitter was added:

`search23/q14_extreme_r_quotient.cpp`.

It quotients the three zero-vertex attachments under the `S_3` zero symmetry
and the `S_5 x S_5` row/column symmetry of the singleton classes.  There are
10 zero-attachment quotient types.  Over these, the 5x5 `S1-S2` complement
families give:

- raw candidate complements: `1148128`;
- canonical fixed-R quotient models: `18418`;
- canonical terminal-cut quotient models, for the optional conditional cut:
  `15658`.

The emitted all-model manifest is

`search23/q14_extreme_r_quotient/fixedR_all/models.tsv`

with `18418` fixed-R edge-list files.

The fixed-R verifier was recompiled with the sound A-only lex mode:

`search23/sat_q14_t2_shape_family_fixedR_aonly.exe`

from `search23/sat_q14_t2_shape_family.cpp` with `LEX_MODE=1`.  The campaign
runner

`search23/run_q14_extreme_fixedR_batch.ps1`

was run at `200000` CaDiCaL conflicts and `64` workers.  Final output:

`search23/q14_extreme_fixedR_all_200k/PROGRESS.txt`

reports

`done=18418/18418`, `unsat=18418`, `sat=0`, `unknown=0`, `na=0`,
`elapsedSec=5321`.

Status: VERIFIED computational certificate, relative to the quotient emitter,
that this one extreme category has no A/B extension.  This does not close the
whole q14/t=2 cap74 p12 band; the remaining R-feasible categories from V140
still need quotient/fixed-R closure or a structural lemma.

### V142. q=14/t=2 cap74 p12 small-quotient R categories closed

Starting from the 124 R-feasible cap74/p12 categories isolated in V140, the
general quotient counter/emitter

`search23/q14_p12_r_quotient_general.cpp`

was validated against the already-closed V141 category:

`search23/q14_p12_r_quotient_general_idx207/summary.tsv`

reports `quotient=18418`, matching the V141 fixed-R quotient count.

The all-category quotient run

`search23/q14_p12_r_quotient_all/summary.tsv`

reports 124 categories with total quotient count `732715`; the subfamily with
`quotient <= 1000` consists of 76 categories and 11706 quotient representatives.
These representatives were emitted to

`search23/q14_p12_emit_q1000/manifest.tsv`

and checked with the fixed-R A-only verifier

`search23/sat_q14_t2_shape_family_fixedR_aonly.exe`

using 64 workers and a 200000-conflict CaDiCaL limit.  The campaign output

`search23/q14_p12_fixedR_q1000_200k/PROGRESS.txt`

reports

`done=11706/11706`, `unsat=11706`, `sat=0`, `unknown=0`, `na=0`,
`elapsedSec=3339`.

Status: VERIFIED computational certificate, relative to the quotient emitter
and fixed-R verifier, that all 76 small-quotient R categories have no A/B
extension.  The remaining cap74/p12 frontier from V140 has 48 categories and
721009 quotient representatives; these need either larger fixed-R batches or a
structural lemma targeting the heavy R categories.

### V143. q=14/t=2 `S1-S2` reconstruction lemma

GPT Pro was asked for a structural attack on the 48 heavy cap74/p12 categories.
The prompt and answer are saved at

`problems/23/gpt_q14_p12_heavy48_prompt_2026-06-13.md`

and

`problems/23/gpt_q14_p12_heavy48_answer_2026-06-13.md`.

The following local lemma from that answer has been checked and is now accepted
as a T1 structural reduction for the q14/t=2 state model.

Let `u in S1` and `v in S2`.  For each `r in R`, write

`X_r = N_A(r)` and `Y_r = N_B(r)`.

Let

`Z(u,v) = |{z in Z : zu in E_R and zv in E_R}|`.

In the q14/t=2 low-codegree branch, every nonedge has at least two common
neighbours, while triangle-freeness gives that adjacent vertices have no common
neighbour.  Therefore for any pair `a,b`,

- `kappa(a,b)=0` forces `ab` to be an edge;
- `kappa(a,b)=1` is impossible;
- `kappa(a,b)>=2` forces `ab` to be a nonedge.

For `u in S1`, `v in S2`, their common neighbours cannot lie in the root
vertices, in the colour core, in `D`, or in `S1 union S2`: same-label or
intersecting-label R edges are forbidden.  The only possible common neighbours
are A-vertices hit by both, B-vertices hit by both, and zero-labelled vertices
adjacent to both.  Hence

`kappa(u,v) = |X_u cap X_v| + |Y_u cap Y_v| + Z(u,v)`.

Consequently

`uv in E_R`

if and only if

`Z(u,v) + |X_u cap X_v| + |Y_u cap Y_v| = 0`;

the value `1` is forbidden; and value at least `2` forces `uv` to be a nonedge.

Status: VERIFIED T1 local lemma, relative to the q14/t=2 setup and its
minimum nonedge-codegree-2 hypothesis.  This does not close the 48 heavy
categories by itself.  It changes the next certificate target: instead of
enumerating all `S1-S2` R-edge graphs, enumerate zero-skeleton orbits and
A/B-state assignments over the three disconnected p=12 templates
`C8+C4`, `C6+C6`, and `3C4`, then reconstruct `S1-S2` edges by the formula
above and check the remaining state constraints.

### V144. q=14/t=2 cap74 p12 category `idx=275` closed by reconstruction-state verifier

Implemented the reconstruction-state verifier

`search23/q14_p12_reconstruct_state.cpp`

using the V143 `S1-S2` reconstruction lemma.  For a fixed cap74/p12 R
category it enumerates zero-skeleton orbits and the three p=12 A--B
templates, assigns A/B incidence states to the 14 R-vertices, reconstructs
all `S1-S2` R-edges by V143, and checks:

- the exact `S1-S2` count for the category;
- the cap74 A/B incidence bound;
- R-edge triangle-free incidence disjointness;
- local domination for singleton-labelled R vertices;
- R-degree and A/B degree lower bounds;
- colour-hit constraints for every A/B vertex;
- missing A--B and same-side A/A, B/B nonedge-codegrees;
- A--R, B--R, and fixed R--R nonedge-codegrees.

The largest category tested so far is

`idx=275`, category `(zz,zs1,zs2,zd,s12) = (0,4,4,3,14)`.

It has `62` zero-skeleton representatives and hence `186` reconstruction
jobs after the three A--B templates.  The main 16-worker run

`search23/recon_idx275_rr_w16.out`

reported `unsat=185`, `sat=0`, `unknown=1` at `500000` CaDiCaL conflicts.
The remaining job

`zi=58`, template `3C4`

was rerun separately at `5000000` conflicts:

`search23/recon_idx275_zi58_3c4_rr_5m.out`

and returned `RECON_STATE_STATUS 20`.

Status: VERIFIED computational certificate, relative to the V143
reconstruction-state verifier, that category `idx=275` has no A/B extension.
The full 48-category cap74/p12 frontier is not yet closed.

### V145. Additional q=14/t=2 cap74 p12 reconstruction categories closed

Using the same V143 reconstruction-state verifier

`search23/q14_p12_reconstruct_state.cpp`

and the cap32 run directory

`search23/q14_p12_reconstruct_heavy_rr`,

the following heavy categories are now closed with final status `20`
(UNSAT/no A--B extension):

- `idx=279`, category `(0,4,5,3,13)`: main run left six UNKNOWN
  jobs; all six hard reruns at `5000000` conflicts returned status `20`.
- `idx=339`, category `(0,5,4,3,13)`: main run left five UNKNOWN
  jobs; all five hard reruns at `5000000` conflicts returned status `20`.
- `idx=211`, category `(0,3,4,3,15)`: main run returned status `20`.
- `idx=271`, category `(0,4,3,3,15)`: main run returned status `20`.
- `idx=215`, category `(0,3,5,3,14)`: main run left one UNKNOWN
  job; the hard rerun `zi=22`, template `C8+C4`, at `5000000`
  conflicts returned status `20`.
- `idx=335`, category `(0,5,3,3,14)`: main run left one UNKNOWN
  job; the hard rerun `zi=18`, template `C8+C4`, at `5000000`
  conflicts returned status `20`.
- `idx=278`, category `(0,4,5,2,14)`: main run returned status `20`.
- `idx=338`, category `(0,5,4,2,14)`: main run returned status `20`.
- `idx=207`, category `(0,3,3,3,16)`: main run closed 27 of
  30 jobs; hard reruns closed `C6+C6` and `C8+C4`, and the remaining
  `zi=9`, template `3C4`, closed at `50000000` conflicts.

Status: VERIFIED computational certificates for the listed final-20
categories, relative to the V143 reconstruction-state verifier.  The full
48-category cap74/p12 frontier remains active.

### V146. Additional q=14/t=2 cap74 p12 reconstruction closures under cap128 run

Continuing the same V143 reconstruction-state verifier

`search23/q14_p12_reconstruct_state.cpp`

in the run directory

`search23/q14_p12_reconstruct_heavy_rr`,

the following additional heavy categories are now closed with final status
`20` (UNSAT/no A--B extension):

- `idx=1198`, category `(1,4,4,2,14)`: main run returned status `20`.
- `idx=1202`, category `(1,4,5,2,13)`: main run returned status `20`.
- `idx=1262`, category `(1,5,4,2,13)`: main run returned status `20`.
- `idx=274`, category `(0,4,4,2,15)`: main run closed 77 of
  78 jobs; the remaining hard rerun `zi=18`, template `3C4`, at
  `5000000` conflicts returned status `20`.

Status: VERIFIED computational certificates for the listed final-20
categories, relative to the V143 reconstruction-state verifier.  Including
V144--V146, 14 of the 48 heavy cap74/p12 categories are now closed; the
remaining categories are active or still queued.

### V147. q=14/t=2 neighbour-union capacity lemma

In the q=14/t=2 cap74/p12 state model, for each `r in R` write

`X_r = N_A(r)`, `Y_r = N_B(r)`, and `m_r = |X_r| + |Y_r|`.

Let

`A_R(r) = union_{u in N_R(r)} X_u`

and

`B_R(r) = union_{u in N_R(r)} Y_u`.

Then every valid state assignment satisfies

`m_r + |A_R(r)| + |B_R(r)| <= 12`.

Proof.  If `ru` is an R-edge, then triangle-freeness gives
`X_r cap X_u = empty` and `Y_r cap Y_u = empty`; otherwise any shared
`A`- or `B`-neighbour would form a triangle with `r,u`.  Hence `X_r` is
disjoint from `A_R(r)` and `Y_r` is disjoint from `B_R(r)`.  Since
`|A|=|B|=6`, the claim follows from

`|X_r| + |A_R(r)| <= 6`

and

`|Y_r| + |B_R(r)| <= 6`.

Combining this with the local lower bound

`m_r >= max(2 * (2 - |label(r)|), 8 - |label(r)| - d_R(r))`

gives the derived capacity cut

`|A_R(r)| + |B_R(r)| <= 12 - max(2 * (2 - |label(r)|), 8 - |label(r)| - d_R(r))`.

Status: VERIFIED T1 structural lemma, relative to the q14/t=2 state model.
It is implemented experimentally in
`search23/q14_p12_reconstruct_state.cpp` behind the `--union-cap` flag,
and a cheaper fixed-neighbour fragment is available behind
`--static-union-cap`.  Initial smoke testing shows the full direct CNF
encoding is too heavy for default campaign runs, so the active 128-worker
campaign continues with the V143 reconstruction verifier while the static
fragment remains available for targeted hard cases.

### V148. q=14/t=2 cap74 p12 reconstruction category `idx=1206` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=1206`, category `(1,4,6,2,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=1206 cat=1,4,6,2,12 zreps=60 jobs=180 done=180 unsat=180 sat=0 unknown=0 conflicts=500000 workers=7 light=0 only_zi=-1 only_template=*`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V148,
15 of the 48 heavy cap74/p12 categories are now closed; 33 remain active,
queued, or awaiting hard reruns.

### V149. q=14/t=2 cap74 p12 reconstruction category `idx=399` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=399`, category `(0,6,3,3,13)`,

had five main-run unknown leaves after

`RECON_STATE_STATUS 0 idx=399 cat=0,6,3,3,13 zreps=87 jobs=261 done=261 unsat=256 sat=0 unknown=5 conflicts=500000 workers=16 light=0 only_zi=-1 only_template=*`.

All five leaves are now closed by hard reruns:

- `zi=17`, `template=C6+C6`;
- `zi=51`, `template=C6+C6`;
- `zi=51`, `template=C8+C4`;
- `zi=86`, `template=3C4`;
- `zi=86`, `template=C6+C6`.

Each hard rerun reports `RECON_STATE_STATUS 20 ... jobs=1 done=1 unsat=1
sat=0 unknown=0 conflicts=5000000`, and
`idx_399.status` ends with

`STATUS idx=399 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V149,
16 of the 48 heavy cap74/p12 categories are now closed; 32 remain active,
queued, or awaiting hard reruns.

### V150. Singleton Phi rooted-cut lemma for q=14/t=2 cap74 p12

In the q=14/t=2, cap74, p=12 equality layer, let an R-vertex `r` have
C-label `ell(r)` and A/B-incidence state `(X_r,Y_r)`, with

`m_r = |X_r| + |Y_r|`.

Then every valid state assignment satisfies

`d_R(r) <= m_r + |ell(r)|`.

Proof.  The exact Phi rooted-cut inequality for `W subset R` is, in this
cap74 equality layer where `p+e_R=37`,

`M(W) + F_Phi(W) >= partial_R(W)`,

where `M(W)=sum_{r in W} m_r` and

`F_Phi(W)=sum_i min(|U_i cap W|, 8 - |U_i cap W|)`.

Taking `W={r}` gives `partial_R(W)=d_R(r)`,
`M(W)=m_r`, and exactly one unit in `F_Phi(W)` for each colour present in
`ell(r)`.  Hence `F_Phi({r})=|ell(r)|`, proving the claim.

Status: VERIFIED T1 structural lemma, relative to the q14/t=2 rooted-cut
model.  It is implemented experimentally in
`search23/q14_p12_reconstruct_state.cpp` behind the `--singleton-phi` flag.
Targeted `--singleton-phi --static-union-cap` hard reruns are active for the
remaining open leaves of `idx=341` and `idx=219`.

### V151. q=14/t=2 cap74 p12 reconstruction category `idx=1326` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=1326`, category `(1,6,4,2,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=1326 cat=1,6,4,2,12 zreps=60 jobs=180 done=180 unsat=180 sat=0 unknown=0 conflicts=500000 workers=3 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=1326 final=20 source=main`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V151,
17 of the 48 heavy cap74/p12 categories are now closed; 31 remain active,
queued, or awaiting hard reruns.

### V152. Small exact rooted-cut family for q=14/t=2 cap74 p12

In the q=14/t=2, cap74, p=12 equality layer, the exact rooted-cut
inequalities may be imposed for every subset `W subset R`.  The full
`2^14` family is correct but too large as a direct CNF block.  The restricted
family

`|W| <= 2`

is a cheap verified consequence and is now implemented as an experimental
cut family.

For each such `W`, the verifier adds both rooted orientations:

- Psi orientation:
  same-side R-edges inside/outside the cut, plus A-incidences from `W`,
  plus B-incidences from `R \\ W`, plus the fixed C-label contribution, must
  total at least `37`;
- Phi orientation:
  `p=12`, same-side R-edges inside/outside the cut, plus all A/B incidences
  from `W`, plus the fixed C-label contribution, must total at least `37`.

This is the same exact rooted-cut formula used by the earlier fixed-R
q14/t=2 verifier, restricted to the masks with at most two R-vertices.

Status: VERIFIED T1 structural cut family, relative to the q14/t=2
rooted-cut model.  It is implemented experimentally in
`search23/q14_p12_reconstruct_state.cpp` behind `--pair-rooted-cuts`.
Targeted v5 hard reruns using
`--pair-rooted-cuts --singleton-phi --static-union-cap` are active for
the currently open leaves of `idx=341` and `idx=219`.

### V153. q=14/t=2 cap74 p12 reconstruction category `idx=341` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=341`, category `(0,5,5,1,14)`,

had two main-run unknown leaves after

`RECON_STATE_STATUS 0 idx=341 cat=0,5,5,1,14 zreps=53 jobs=159 done=159 unsat=157 sat=0 unknown=2 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

Both leaves are now closed:

- `zi=16`, `template=C6+C6`, by the static-union hard rerun;
- `zi=16`, `template=3C4`, by the hard rerun.

The corresponding status file records

`STATUS idx=341 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V153,
18 of the 48 heavy cap74/p12 categories are now closed; 30 remain active,
queued, or awaiting hard reruns.

### V154. q=14/t=2 cap74 p12 reconstruction category `idx=463` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=463`, category `(0,7,3,3,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=463 cat=0,7,3,3,12 zreps=116 jobs=348 done=348 unsat=348 sat=0 unknown=0 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=463 final=20 source=main`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V154,
19 of the 48 heavy cap74/p12 categories are now closed; 29 remain active,
queued, or awaiting hard reruns.

### V155. q=14/t=2 cap74 p12 reconstruction category `idx=2096` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=2096`, category `(2,4,5,2,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=2096 cat=2,4,5,2,12 zreps=8 jobs=24 done=24 unsat=24 sat=0 unknown=0 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=2096 final=20 source=main`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.

### V156. q=14/t=2 cap74 p12 reconstruction category `idx=2156` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=2156`, category `(2,5,4,2,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=2156 cat=2,5,4,2,12 zreps=8 jobs=24 done=24 unsat=24 sat=0 unknown=0 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=2156 final=20 source=main`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V156,
21 of the 48 heavy cap74/p12 categories are now closed; 27 remain active,
queued, or awaiting hard reruns.

### V157. q=14/t=2 cap74 p12 reconstruction category `idx=223` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=223`, category `(0,3,7,3,12)`,

is now closed by the main run:

`RECON_STATE_STATUS 20 idx=223 cat=0,3,7,3,12 zreps=116 jobs=348 done=348 unsat=348 sat=0 unknown=0 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=223 final=20 source=main`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V157,
22 of the 48 heavy cap74/p12 categories are now closed; 26 remain active,
queued, or awaiting hard reruns.

### V158. q=14/t=2 cap74 p12 reconstruction category `idx=1265` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=1265`, category `(1,5,5,1,13)`,

is now closed by the `fastretry2` run:

`RECON_STATE_STATUS 20 idx=1265 cat=1,5,5,1,13 zreps=30 jobs=90 done=90 unsat=90 sat=0 unknown=0 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=1265 final=20 source=idx_1265_fastretry2.out`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V158,
23 of the 48 heavy cap74/p12 categories are now closed; 25 remain active,
queued, or awaiting hard reruns.

### V159. q=14/t=2 cap74 p12 reconstruction category `idx=219` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=219`, category `(0,3,6,3,13)`,

is now closed by hard leaf reruns.  The main run was:

`RECON_STATE_STATUS 0 idx=219 cat=0,3,6,3,13 zreps=87 jobs=261 done=261 unsat=256 sat=0 unknown=5 conflicts=500000 workers=2 light=0 only_zi=-1 only_template=*`.

The remaining five leaves are recorded in `idx_219.status` as UNSAT hard or
static-hard certificates, including the final hard leaf

`RECON_STATE_STATUS 20 idx=219 cat=0,3,6,3,13 zreps=87 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 union_cap=0 static_union_cap=1 only_zi=86 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=219 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V159,
24 of the 48 heavy cap74/p12 categories are now closed; 24 remain active,
queued, or awaiting hard reruns.

### V160. q=14/t=2 cap74 p12 reconstruction category `idx=2092` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=2092`, category `(2,4,4,2,13)`,

is now closed by one hard leaf rerun.  The full-category boost run was:

`RECON_STATE_STATUS 0 idx=2092 cat=2,4,4,2,13 zreps=4 jobs=12 done=12 unsat=11 sat=0 unknown=1 conflicts=500000 workers=8 light=0 only_zi=-1 only_template=*`.

The remaining leaf was `zi=3`, template `C6+C6`, and the hard rerun returned:

`RECON_STATE_STATUS 20 idx=2092 cat=2,4,4,2,13 zreps=4 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=3 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=2092 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V160,
25 of the 48 heavy cap74/p12 categories are now closed; 23 remain active,
queued, or awaiting hard reruns.

### V161. q=14/t=2 cap74 p12 reconstruction category `idx=2159` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=2159`, category `(2,5,5,1,12)`,

is now closed by one hard leaf rerun.  The full-category boost run was:

`RECON_STATE_STATUS 0 idx=2159 cat=2,5,5,1,12 zreps=13 jobs=39 done=39 unsat=38 sat=0 unknown=1 conflicts=500000 workers=5 light=0 only_zi=-1 only_template=*`.

The remaining leaf was `zi=10`, template `C6+C6`, and the hard rerun returned:

`RECON_STATE_STATUS 20 idx=2159 cat=2,5,5,1,12 zreps=13 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=10 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=2159 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V161,
26 of the 48 heavy cap74/p12 categories are now closed; 22 remain active,
queued, or awaiting hard reruns.

### V162. q=14/t=2 cap74 p12 reconstruction category `idx=1329` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=1329`, category `(1,6,5,1,12)`,

is now closed by the `boost128` run:

`RECON_STATE_STATUS 20 idx=1329 cat=1,6,5,1,12 zreps=84 jobs=252 done=252 unsat=252 sat=0 unknown=0 conflicts=500000 workers=4 light=0 only_zi=-1 only_template=*`.

The corresponding status file records

`STATUS idx=1329 final=20 source=idx_1329_boost128_20260613T201315Z.out`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier.  Including V144--V162,
27 of the 48 heavy cap74/p12 categories are now closed; 21 remain active,
queued, or awaiting hard reruns.

### V163. q=14/t=2 cap74 p12 reconstruction category `idx=405` closed

Continuing the same V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the heavy category

- `idx=405`, category `(0,6,5,1,13)`,

is now closed by the main run plus two hard leaf reruns.  The full-category
main run was:

`RECON_STATE_STATUS 0 idx=405 cat=0,6,5,1,13 zreps=166 jobs=498 done=498 unsat=496 sat=0 unknown=2 conflicts=500000 workers=3 light=0 only_zi=-1 only_template=*`.

The remaining leaves were both `C6+C6` leaves.  The pair-rooted,
singleton-phi, static-union hard reruns returned:

`RECON_STATE_STATUS 20 idx=405 cat=0,6,5,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=57 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=405 cat=0,6,5,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=163 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=405 final=20 source=hard`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V163, 28 of the 48 heavy
cap74/p12 categories are now closed; 20 remain active, queued, or awaiting
hard reruns.

### V164. q=14/t=2 cap74 p12 reconstruction category `idx=345` closed

Continuing the V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the category

`idx=345`, `(zz,zs1,zs2,zd,s12)=(0,5,6,1,13)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main/retry/boost runs and the remaining targeted hard-leaf reruns.  A fresh
leaf-set audit gives

`idx=345 jobs=498 doneUnique=498 missing=0`.

The six targeted hard leaves that completed the union were:

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=145 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=149 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=164 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=164 only_template=3C4`.

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=165 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=345 cat=0,5,6,1,13 zreps=166 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=165 only_template=3C4`.

The corresponding status file records

`STATUS idx=345 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V164, 29 of the 48 heavy
cap74/p12 categories are now closed; 19 remain active, queued, or awaiting
hard reruns.

### V165. q=14/t=2 cap74 p12 reconstruction category `idx=282` closed

Continuing the V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the category

`idx=282`, `(zz,zs1,zs2,zd,s12)=(0,4,6,2,13)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main/retry/boost runs and targeted hard-leaf reruns.  A fresh leaf-set audit
gives

`idx=282 jobs=564 doneUnique=564 missing=0`.

The last missing leaf was closed by

`RECON_STATE_STATUS 20 idx=282 cat=0,4,6,2,13 zreps=188 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=179 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=282 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V165, 30 of the 48 heavy
cap74/p12 categories are now closed; 18 remain active, queued, or awaiting
hard reruns.

### V166. q=14/t=2 cap74 p12 reconstruction category `idx=1270` closed

Continuing the V143 reconstruction-state verifier in

`search23/q14_p12_reconstruct_heavy_rr`,

the category

`idx=1270`, `(zz,zs1,zs2,zd,s12)=(1,5,6,2,11)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main/boost runs and targeted hard-leaf reruns.  A fresh leaf-set audit gives

`idx=1270 jobs=660 doneUnique=660 missing=0`.

The last two missing leaves were closed by

`RECON_STATE_STATUS 20 idx=1270 cat=1,5,6,2,11 zreps=220 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=210 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=1270 cat=1,5,6,2,11 zreps=220 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=219 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=1270 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V166, 31 of the 48 heavy
cap74/p12 categories are now closed; 17 remain active, queued, or awaiting
hard reruns.

### V167. q=14/t=2 cap74 p12 reconstruction category `idx=1269` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=1269`, `(zz,zs1,zs2,zd,s12)=(1,5,6,1,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=1269 jobs=252 doneUnique=252 missing=0`.

The last three missing leaves were closed by

`RECON_STATE_STATUS 20 idx=1269 cat=1,5,6,1,12 zreps=84 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=78 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=1269 cat=1,5,6,1,12 zreps=84 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=81 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=1269 cat=1,5,6,1,12 zreps=84 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=83 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=1269 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V167, 32 of the 48 heavy
cap74/p12 categories are now closed; 16 remain active, queued, or awaiting
hard reruns.

### V168. q=14/t=2 cap74 p12 reconstruction category `idx=1266` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=1266`, `(zz,zs1,zs2,zd,s12)=(1,5,5,2,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=1266 jobs=363 doneUnique=363 missing=0`.

The final missing leaf was closed by multiple absolute-cats hard reruns; one
certificate line is

`RECON_STATE_STATUS 20 idx=1266 cat=1,5,5,2,12 zreps=121 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=59 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=1266 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V168, 33 of the 48 heavy
cap74/p12 categories are now closed; 15 remain active, queued, or awaiting
hard reruns.

### V169. q=14/t=2 cap74 p12 reconstruction category `idx=1330` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=1330`, `(zz,zs1,zs2,zd,s12)=(1,6,5,2,11)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=1330 jobs=660 doneUnique=660 missing=0`.

The final missing leaves were closed by

`RECON_STATE_STATUS 20 idx=1330 cat=1,6,5,2,11 zreps=220 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=194 only_template=C6+C6`.

`RECON_STATE_STATUS 20 idx=1330 cat=1,6,5,2,11 zreps=220 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=194 only_template=C8+C4`.

The corresponding status file records

`STATUS idx=1330 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V169, 34 of the 48 heavy
cap74/p12 categories are now closed; 14 remain active, queued, or awaiting
hard reruns.

### V170. q=14/t=2 cap74 p12 reconstruction category `idx=402` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=402`, `(zz,zs1,zs2,zd,s12)=(0,6,4,2,13)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=402 jobs=564 doneUnique=564 missing=0`.

The final missing leaf was closed by

`RECON_STATE_STATUS 20 idx=402 cat=0,6,4,2,13 zreps=188 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=153 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=402 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V170, 35 of the 48 heavy
cap74/p12 categories are now closed; 13 remain active, queued, or awaiting
hard reruns.

### V171. q=14/t=2 cap74 p12 reconstruction category `idx=283` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=283`, `(zz,zs1,zs2,zd,s12)=(0,4,6,3,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=283 jobs=816 doneUnique=816 missing=0`.

The final missing leaf was closed independently by normal-executable reruns,
including

`RECON_STATE_STATUS 20 idx=283 cat=0,4,6,3,12 zreps=272 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=263 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=283 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V171, 36 of the 48 heavy
cap74/p12 categories are now closed; 12 remain active, queued, or awaiting
hard reruns.

### V172. q=14/t=2 cap74 p12 reconstruction category `idx=466` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=466`, `(zz,zs1,zs2,zd,s12)=(0,7,4,2,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=466 jobs=855 doneUnique=855 missing=0`.

The final missing leaf was closed by

`RECON_STATE_STATUS 20 idx=466 cat=0,7,4,2,12 zreps=285 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=279 only_template=3C4`.

The corresponding status file records

`STATUS idx=466 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V172, 37 of the 48 heavy
cap74/p12 categories are now closed; 11 remain active, queued, or awaiting
hard reruns.

### V173. q=14/t=2 cap74 p12 reconstruction category `idx=403` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=403`, `(zz,zs1,zs2,zd,s12)=(0,6,4,3,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=403 jobs=816 doneUnique=816 missing=0`.

The final missing leaf was closed by

`RECON_STATE_STATUS 20 idx=403 cat=0,6,4,3,12 zreps=272 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=223 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=403 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V173, 38 of the 48 heavy
cap74/p12 categories are now closed; 10 remain active, queued, or awaiting
hard reruns.

### V174. q=14/t=2 cap74 p12 reconstruction category `idx=286` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=286`, `(zz,zs1,zs2,zd,s12)=(0,4,7,2,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=286 jobs=855 doneUnique=855 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=286 cat=0,4,7,2,12 zreps=285 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=280 only_template=3C4`.

The corresponding status file records

`STATUS idx=286 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V174, 39 of the 48 heavy
cap74/p12 categories are now closed; 9 remain active, queued, or awaiting
hard reruns.

### V175. q=14/t=2 cap74 p12 reconstruction category `idx=342` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=342`, `(zz,zs1,zs2,zd,s12)=(0,5,5,2,13)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=342 jobs=888 doneUnique=888 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=342 cat=0,5,5,2,13 zreps=296 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=294 only_template=C8+C4`.

The corresponding status file records

`STATUS idx=342 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V175, 40 of the 48 heavy
cap74/p12 categories are now closed; 8 remain active, queued, or awaiting
hard reruns.

### V176. q=14/t=2 cap74 p12 reconstruction category `idx=346` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=346`, `(zz,zs1,zs2,zd,s12)=(0,5,6,2,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=346 jobs=2076 doneUnique=2076 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=346 cat=0,5,6,2,12 zreps=692 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=689 only_template=3C4`.

The corresponding status file records

`STATUS idx=346 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V176, 41 of the 48 heavy
cap74/p12 categories are now closed; 7 remain active, queued, or awaiting
hard reruns.

### V177. q=14/t=2 cap74 p12 reconstruction category `idx=467` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=467`, `(zz,zs1,zs2,zd,s12)=(0,7,4,3,11)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=467 jobs=1110 doneUnique=1110 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=467 cat=0,7,4,3,11 zreps=370 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=369 only_template=C8+C4`.

The corresponding status file records

`STATUS idx=467 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V177, 42 of the 48 heavy
cap74/p12 categories are now closed; 6 remain active, queued, or awaiting
hard reruns.

### V178. q=14/t=2 cap74 p12 reconstruction category `idx=409` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=409`, `(zz,zs1,zs2,zd,s12)=(0,6,6,1,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=409 jobs=1707 doneUnique=1707 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=409 cat=0,6,6,1,12 zreps=569 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=534 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=409 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V178, 43 of the 48 heavy
cap74/p12 categories are now closed; 5 remain active, queued, or awaiting
hard reruns.

### V179. q=14/t=2 cap74 p12 reconstruction category `idx=343` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=343`, `(zz,zs1,zs2,zd,s12)=(0,5,5,3,12)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=343 jobs=1134 doneUnique=1134 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=343 cat=0,5,5,3,12 zreps=378 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=377 only_template=3C4`.

The corresponding status file records

`STATUS idx=343 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V179, 44 of the 48 heavy
cap74/p12 categories are now closed; 4 remain active, queued, or awaiting
hard reruns.

### V180. q=14/t=2 cap74 p12 reconstruction category `idx=287` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=287`, `(zz,zs1,zs2,zd,s12)=(0,4,7,3,11)`,

has been closed by taking the union of exact UNSAT leaf certificates from the
main run and targeted hard-leaf reruns.  The independent recount over all
`zrep/template` leaves gives

`idx=287 jobs=1110 doneUnique=1110 missing=0`.

Representative final-tail leaf evidence:

`RECON_STATE_STATUS 20 idx=287 cat=0,4,7,3,11 zreps=370 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=363 only_template=C6+C6`.

The corresponding status file records

`STATUS idx=287 final=20 source=manual-hard-union`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V180, 45 of the 48 heavy
cap74/p12 categories are now closed; 3 remain active, queued, or awaiting
hard reruns.

### V181. q=14/t=2 cap74 p12 reconstruction category `idx=407` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=407`, `(zz,zs1,zs2,zd,s12)=(0,6,5,3,11)`,

has now been exhausted under the paired-rooted-cuts, singleton-phi, and
static-union-cap hard-leaf flags.  The manual union recount over the
main/target reruns gives:

`idx=407 jobs=2025 doneUnique=2025 missing=0 SAT=0 UNKNOWN=0`.

Recorded certificate:

`search23/q14_p12_reconstruct_heavy_rr/idx_407.status`.

Representative final-leaf evidence includes `zi=660, template=3C4`,
`zi=672, template=C8+C4`, and `zi=659, template=C6+C6`, each with
`RECON_STATE_STATUS 20`, `done=1`, `unsat=1`, `sat=0`, `unknown=0`,
`conflicts=5000000`, `workers=1`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V181, 46 of the 48 heavy
cap74/p12 categories are now closed; 2 remain active, queued, or awaiting
hard reruns.

### V182. q=14/t=2 cap74 p12 reconstruction category `idx=406` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=406`, `(zz,zs1,zs2,zd,s12)=(0,6,5,2,12)`,

has now been exhausted under the paired-rooted-cuts, singleton-phi, and
static-union-cap hard-leaf flags.  The manual union recount over the
main/target reruns gives:

`idx=406 jobs=2076 doneUnique=2076 missing=0 SAT=0 UNKNOWN=0`.

Recorded certificate:

`search23/q14_p12_reconstruct_heavy_rr/idx_406.status`.

Representative final-leaf evidence includes `zi=677, template=3C4`,
`zi=681, template=C6+C6`, and `zi=689, template=C6+C6`, each with
`RECON_STATE_STATUS 20`, `done=1`, `unsat=1`, `sat=0`, `unknown=0`,
`conflicts=5000000`, `workers=1`.

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V182, 47 of the 48 heavy
cap74/p12 categories are now closed; 1 remains active, queued, or awaiting
hard reruns.

### V183. q=14/t=2 cap74 p12 reconstruction category `idx=347` closed

For the q=14/t=2 cap74/p12 reconstruction-state verifier V143, category

`idx=347`, `(zz,zs1,zs2,zd,s12)=(0,5,6,3,11)`,

the hard rerun union is final-20:

`search23/q14_p12_reconstruct_heavy_rr/idx_347.status`

Manual recount over the main and target1--target27 hard rerun logs gives

`jobs=2025`, `doneUnique=2025`, `missing=0`, `SAT=0`, `UNKNOWN=0`.

Representative final leaves:

- `zi=629`, `template=C6+C6`: `RECON_STATE_STATUS 20 idx=347 cat=0,5,6,3,11 zreps=675 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=629 only_template=C6+C6`
- `zi=642`, `template=C6+C6`: `RECON_STATE_STATUS 20 idx=347 cat=0,5,6,3,11 zreps=675 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=642 only_template=C6+C6`
- `zi=642`, `template=C8+C4`: `RECON_STATE_STATUS 20 idx=347 cat=0,5,6,3,11 zreps=675 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=642 only_template=C8+C4`
- `zi=648`, `template=C8+C4`: `RECON_STATE_STATUS 20 idx=347 cat=0,5,6,3,11 zreps=675 jobs=1 done=1 unsat=1 sat=0 unknown=0 conflicts=5000000 workers=1 light=0 only_zi=648 only_template=C8+C4`

Status: VERIFIED computational certificate for this final-20 category,
relative to the V143 reconstruction-state verifier and the V150/V152/V147
strengthened hard-leaf flags.  Including V144--V183, all 48 of the 48 heavy
cap74/p12 categories are now closed.

### V184. q=14/t=2 scalar frontier after V183

The scalar audit

`search23/q14_t2_scalar_audit.cpp`

was updated with the exact V141--V183 exclusion for

`z=3`, `s1=s2=5`, `d=1`, `p=12`, `e_R=25`.

After recompilation, the regenerated frontier

`search23/q14_t2_scalar_audit_post_v183.tsv`

reports `rows=39657`.  The maximum cap remains `74`, now with `50` cap74
scalar rows.  They group as follows:

- `(z,s1,s2,d)=(2,6,6,0)`: `6` rows, `p=12..17`, `e_R=25..20`;
- `(3,5,5,1)`: `6` rows, `p=13..18`, `e_R=24..19`;
- `(4,4,4,2)`: `10` rows, `p=12..21`, `e_R=25..16`;
- `(5,3,3,3)`: `10` rows, `p=12..21`, `e_R=25..16`;
- `(6,2,2,4)`: `10` rows, `p=12..21`, `e_R=25..16`;
- `(8,0,0,6)`: `8` rows, `p=14..21`, `e_R=23..16`.

Status: VERIFIED scalar audit.  V183 closes the full hard reconstruction
frontier for the single `z=3,s1=s2=5,d=1,p=12,e_R=25` scalar row, but q14/t=2
is not yet closed.  The next frontier is the remaining cap74 scalar rows,
especially the still-minimal p=12 rows at `(2,6,6,0)`, `(4,4,4,2)`,
`(5,3,3,3)`, and `(6,2,2,4)`.

### V185. Generic A-only triage for two remaining cap74/p12 rows

The generic q=14/t=2 cap74 row category runner

`search23/run_q14_t2_cap74_row_cat_batch.ps1`

was corrected to parse `SHAPE_FAMILY_STATUS` anywhere in a job output, since
SAT outputs print the status line before the witness model rather than as the
last line.

For the row

`(z,s1,s2,d,p,e_R,cap)=(2,6,6,0,12,25,74)`,

the generic A-only category triage gave:

- `search23/q14_t2_cap74_p12_z2_cat_aonly_10k/status.tsv`:
  `338/338`, `UNSAT=311`, `SAT=0`, `UNKNOWN=27`;
- `search23/q14_t2_cap74_p12_z2_cat_aonly_100k/status.tsv`:
  rerunning the 27 unknown categories gave `UNSAT=6`, `SAT=0`,
  `UNKNOWN=21`.

For the row

`(z,s1,s2,d,p,e_R,cap)=(4,4,4,2,12,25,74)`,

the generic A-only category triage gave:

- `search23/q14_t2_cap74_p12_z4_cat_aonly_10k/status.tsv`:
  `10836/10836`, `UNSAT=10453`, `SAT=0`, `UNKNOWN=383`;
- `search23/q14_t2_cap74_p12_z4_cat_aonly_100k/status_corrected.tsv`:
  rerunning the 383 unknown categories gave `UNSAT=21`, `SAT=5`,
  `UNKNOWN=357`.

The five generic-model SAT rows are:

- `idx=676`, `(zz,zs1,zs2,zd,s12)=(0,5,8,4,8)`;
- `idx=786`, `(0,6,5,4,10)`;
- `idx=794`, `(0,6,6,3,10)`;
- `idx=812`, `(0,6,8,3,8)`;
- `idx=1060`, `(0,8,6,3,8)`.

Status: VERIFIED computational triage only.  This does not close either scalar
row.  The z4 SAT rows are witnesses for the relaxed generic A-only model, not
verified counterexamples to the q=14/t=2 branch.  They show that the generic
A-only necessary model is too weak for z4 and that the next useful step is
either a generalized reconstruction-state verifier or a structural lemma
excluding these relaxed SAT patterns.

### V186. z4 relaxed SAT rows are C-tight reroot obstructions

The five relaxed SAT rows from V185 were retested under the V131 clean-shadow
condition using

`search23/q14_t2_cap74_p12_z4_sat5_clean_shadow/status.tsv`.

Result: all five returned `SHAPE_FAMILY_STATUS 20` at `200000` conflicts
(`UNSAT=5`, `SAT=0`, `UNKNOWN=0`, elapsed `22s`).  Thus the relaxed z4 SAT
models do not lie in the clean side of the V131 dichotomy.

Direct extraction from the original relaxed SAT witnesses is recorded in

`search23/q14_t2_cap74_p12_z4_sat5_c_tight_witnesses.txt`

and

`search23/q14_t2_cap74_p12_z4_sat5_c_tight_degrees.txt`.

In every one of the five relaxed witnesses there are C-tight vertices
`d_R(r,U_i)=2`, and every listed C-tight certificate has total degree at least
`9`, giving a reroot residual `q' <= 13` for the nonedge `c_i r` when
`|U_i|=6`.

An optional conditional terminal-degree cut was added to

`search23/sat_q14_t2_shape_family.cpp`

behind the compile-time flag `TERMINAL_DEGREE_CUTS`.  The test binary

`search23/sat_q14_t2_shape_family_terminal_degree_aonly.exe`

forbids a C-tight vertex whose total degree would reroot to `q'<14`.  On the
five relaxed z4 SAT categories it produced no SAT rows but did not close them:

- `search23/q14_t2_cap74_p12_z4_sat5_terminal_degree_200k/status.tsv`:
  `UNSAT=0`, `SAT=0`, `UNKNOWN=5`;
- `search23/q14_t2_cap74_p12_z4_sat5_terminal_degree_5m/status.tsv`:
  `UNSAT=0`, `SAT=0`, `UNKNOWN=5`, elapsed `507s`.

Status: VERIFIED computational obstruction.  The z4 relaxed SAT patterns are
not clean; they are C-tight/reroot patterns, and the available terminal-degree
cut is not sufficient to certify them UNSAT.  The mathematical frontier is now
to establish the q<14 reroot closure or a stronger C-tight extremal lemma,
rather than continuing broad cap74 SAT sweeps.

### V187. q-minimal root normalization gives the terminal C-tight degree cut

In the t=2 branch, choose the root nonedge `xy` among all nonedges of
codegree `2` so that the corresponding residual value `q=|R|` is minimal.
Then a terminal q=14/t=2 branch may assume the following:

For every colour `i` and every `r notin U_i`, if

`d_R(r,U_i)=2`,

then

`deg(r) <= 14 - |U_i|`.

Proof.  Since `r notin U_i`, the pair `c_i r` is a nonedge.  The vertex
`c_i` has no neighbours in `A`, `B`, or the other root common-neighbour class:
otherwise triangle-freeness is violated through `x` or `y`.  Also vertices of
`R` are nonadjacent to `x` and `y` by definition.  Hence the common neighbours
of `c_i` and `r` are exactly `N_R(r) cap U_i`.  If `d_R(r,U_i)=2`, the pair
`c_i r` is therefore another t=2 nonedge.

Rerooting at `c_i r`, the new residual size is

`q' = 30 - deg(c_i) - deg(r) = 28 - |U_i| - deg(r)`,

because `deg(c_i)=|U_i|+2`.  By q-minimality of the original root, `q' >= 14`;
therefore `deg(r) <= 14-|U_i|`.

In the z4 row `(z,s1,s2,d)=(4,4,4,2)`, one has `|U_1|=|U_2|=6`, so every
C-tight vertex satisfies `deg(r)<=8`.  The branch degree lower bound gives
`deg(r)>=8`, hence every C-tight vertex is 8-regular in this terminal row.
Combining this with the singleton Phi cut in the cap74 equality layer
`p+e_R=37` gives the further terminal implication

`d_R(r,U_i)=2 -> d_R(r) <= 4`

for the z4 row: the singleton Phi cut says `m_r+|label(r)| >= d_R(r)`,
while `deg(r)=m_r+|label(r)|+d_R(r)=8`.

Status: rigorous-informal proof, pending final write-up integration.  This
justifies the `TERMINAL_DEGREE_CUTS` condition in the normalized q=14/t=2
terminal branch; it is not by itself a SAT certificate for the remaining z4
categories.

### V188. z4 cap74/p12 terminal-degree batch reduction

Using the V187 q-minimal terminal-degree cut, the corrected generic A-only
z4/p12 non-UNSAT frontier was rerun with

`search23/sat_q14_t2_shape_family_terminal_degree_aonly.exe`

on the `362` categories not already UNSAT in

`search23/q14_t2_cap74_p12_z4_cat_aonly_100k/status_corrected.tsv`.

The batch

`search23/q14_t2_cap74_p12_z4_terminal_degree_100k/status.tsv`

reports:

- `total=362`;
- `UNSAT=113`;
- `SAT=0`;
- `UNKNOWN=249`;
- `elapsedSec=409`;
- `throttle=128`, `conflicts=100000`.

Status: VERIFIED computational reduction under the V187 q-minimal terminal
normalization.  The z4 row is still not closed, but the terminal-degree cut
eliminates all relaxed SAT outputs seen in V185 and closes an additional 113
categories at 100k conflicts.

### V189. z4 terminal-degree 500k tail calibration

The `249` unknown categories from V188 were rerun with the same terminal-degree
binary at a higher conflict limit:

`search23/q14_t2_cap74_p12_z4_terminal_degree_500k/status.tsv`.

The run reports:

- `total=249`;
- `UNSAT=16`;
- `SAT=0`;
- `UNKNOWN=233`;
- `elapsedSec=842`;
- `throttle=128`, `conflicts=500000`.

Status: VERIFIED calibration.  Raising the terminal-degree run from 100k to
500k closes only 16 additional categories and produces no SAT rows.  The
remaining z4 obstruction is therefore not an efficient target for more of the
same conflict-limit escalation; it needs an additional structural cut or a
more exact state/reconstruction quotient.

### V190. z4 terminal R-degree cut calibration

The singleton-Phi consequence of V187 was added to

`search23/sat_q14_t2_shape_family.cpp`

behind the compile-time flag `TERMINAL_RDEG_CUTS`.  The test binary

`search23/sat_q14_t2_shape_family_terminal_dr_aonly.exe`

uses both `TERMINAL_DEGREE_CUTS=1` and `TERMINAL_RDEG_CUTS=1`.

The `233` unknown categories from V189 were rerun at `100000` conflicts:

`search23/q14_t2_cap74_p12_z4_terminal_dr_100k/status.tsv`.

The result is:

- `total=233`;
- `UNSAT=1`;
- `SAT=0`;
- `UNKNOWN=232`;
- `elapsedSec=273`;
- `throttle=128`.

Status: VERIFIED calibration.  The terminal R-degree cut is mathematically
justified by V187 plus singleton Phi, but by itself it barely reduces the
remaining z4 SAT frontier.  The next useful step must exploit more of the
p=12 2-factor structure or add a stronger rooted-cut/state quotient.

### V191. z4 p12 fixed A-B 2-factor template reduction

The generic q14 shape verifier

`search23/sat_q14_t2_shape_family.cpp`

was extended with an optional compile-time `P_TEMPLATE_ID` fixing the p=12
A-B graph to one of the three disconnected 2-factor templates from the p=12
lemma:

- `P_TEMPLATE_ID=0`: `C8+C4`;
- `P_TEMPLATE_ID=1`: `C6+C6`;
- `P_TEMPLATE_ID=2`: `3C4`.

The test binaries also include the V187 terminal-degree cut and the singleton
Phi terminal R-degree cut:

- `search23/sat_q14_t2_shape_family_terminal_dr_p0_aonly.exe`;
- `search23/sat_q14_t2_shape_family_terminal_dr_p1_aonly.exe`;
- `search23/sat_q14_t2_shape_family_terminal_dr_p2_aonly.exe`.

They were run on the `232` z4 categories left UNKNOWN by V190.

Template `C8+C4`:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p0_100k/status.tsv`

reports `UNSAT=232`, `SAT=0`, `UNKNOWN=0`, elapsed `5s`.

Template `C6+C6`:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p1_100k/status.tsv`

reports `UNSAT=232`, `SAT=0`, `UNKNOWN=0`, elapsed `5s`.

Template `3C4`:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p2_100k/status.tsv`

reports `UNSAT=28`, `SAT=0`, `UNKNOWN=204`, elapsed `190s`.

Rerunning the 204 unknown `3C4` categories at `500000` conflicts:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p2_500k/status.tsv`

reports `UNSAT=82`, `SAT=0`, `UNKNOWN=122`, elapsed `406s`.

Status: VERIFIED computational reduction under the p=12 2-factor lemma and
V187 terminal normalization.  For the z4 cap74/p12 scalar row, the `C8+C4`
and `C6+C6` A-B templates are fully excluded in the current category frontier.
The only remaining z4 obstruction is the `3C4` template, with 122 category
profiles still UNKNOWN.

### V192. z4 `3C4` template 2M tail reduction

The `122` `3C4` categories left UNKNOWN by V191 were rerun at a higher
conflict limit:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p2_2m/status.tsv`.

The result is:

- `total=122`;
- `UNSAT=68`;
- `SAT=0`;
- `UNKNOWN=54`;
- `elapsedSec=656`;
- `throttle=128`, `conflicts=2000000`.

Status: VERIFIED computational reduction.  The z4 cap74/p12 row is now reduced
to 54 still-unknown category profiles, all in the `3C4` A-B template.

### V193. z4 `3C4` template 10M core reduction

The `54` categories left UNKNOWN by V192 were rerun at a higher conflict limit:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p2_10m/status.tsv`.

The result is:

- `total=54`;
- `UNSAT=43`;
- `SAT=0`;
- `UNKNOWN=11`;
- `elapsedSec=1439`;
- `throttle=128`, `conflicts=10000000`.

The remaining 11 profiles are:

`(zz,zs1,zs2,zd,s12)` equal to

`(0,5,5,4,11)`, `(0,5,6,4,10)`, `(0,5,7,4,9)`,
`(0,6,5,4,10)`, `(0,6,6,4,9)`, `(0,7,5,4,9)`,
`(0,5,5,5,10)`, `(0,5,6,5,9)`, `(0,6,4,5,10)`,
`(0,6,5,5,9)`, and `(1,5,5,4,10)`.

Status: VERIFIED computational reduction.  The z4 cap74/p12 row is now reduced
to 11 category profiles, all in the `3C4` A-B template.

### V194. z4 cap74/p12 row closed by `3C4` RR-codegree tail

The generic q14 shape verifier was strengthened, behind the compile-time flag
`R_R_CODEGREE`, with the missing necessary condition that every R-R nonedge has
at least two common neighbours, counted from C-label overlap, R common
neighbours, and A/B incidence overlap.

The `3C4` test binary

`search23/sat_q14_t2_shape_family_terminal_dr_p2_rr_aonly.exe`

uses all of:

- `P_TEMPLATE_ID=2` (`3C4`);
- `TERMINAL_DEGREE_CUTS=1`;
- `TERMINAL_RDEG_CUTS=1`;
- `R_R_CODEGREE=1`;
- A-only lex mode.

The 11 profiles left UNKNOWN by V193 were rerun:

`search23/q14_t2_cap74_p12_z4_terminal_dr_p2_rr_20m/status.tsv`.

The result is:

- `total=11`;
- `UNSAT=11`;
- `SAT=0`;
- `UNKNOWN=0`;
- `elapsedSec=1110`;
- `throttle=11`, `conflicts=20000000`.

Combining V191--V194:

- `C8+C4` template: all 232 residual profiles UNSAT;
- `C6+C6` template: all 232 residual profiles UNSAT;
- `3C4` template: all residual profiles UNSAT after the RR-codegree tail.

Together with V185--V190, this closes the full scalar row

`(z,s1,s2,d,p,e_R,cap)=(4,4,4,2,12,25,74)`.

Status: VERIFIED computational certificate under the p=12 2-factor lemma, the
V187 q-minimal terminal normalization, and the R-R nonedge codegree condition.

### V195. q=14/t=2 scalar frontier after V194

The scalar audit was rerun after excluding the newly closed V194 row:

`search23/q14_t2_scalar_audit_post_v194.tsv`.

The first-line summary is:

- `rows=39656`;
- maximum remaining cap is `74`;
- remaining `cap=74` rows: `49`.

The remaining cap74 groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: `6` rows, `p=12..17`,
  `e_R=25..20`;
- `(z,s1,s2,d)=(3,5,5,1)`: `6` rows, `p=13..18`,
  `e_R=24..19`;
- `(z,s1,s2,d)=(4,4,4,2)`: `9` rows, `p=13..21`,
  `e_R=24..16`;
- `(z,s1,s2,d)=(5,3,3,3)`: `10` rows, `p=12..21`,
  `e_R=25..16`;
- `(z,s1,s2,d)=(6,2,2,4)`: `10` rows, `p=12..21`,
  `e_R=25..16`;
- `(z,s1,s2,d)=(8,0,0,6)`: `8` rows, `p=14..21`,
  `e_R=23..16`.

Status: q=14/t=2 remains active.  V194 closes one cap74 scalar row; the
frontier is now the 49 cap74 rows listed above.

### V196. z2 cap74/p12 row closed by p-template RR-codegree tail

The scalar row

`(z,s1,s2,d,p,e_R,cap)=(2,6,6,0,12,25,74)`

was rerun on the 21 categories left UNKNOWN by the older 100k generic A-only
run:

`search23/q14_t2_cap74_p12_z2_cat_aonly_100k/status.tsv`.

Using the RR-codegree p-template binaries with the V187 terminal normalization:

- `p0=C8+C4`:
  `search23/q14_t2_cap74_p12_z2_terminal_dr_p0_rr_100k/status.tsv`,
  `21/21` UNSAT;
- `p1=C6+C6`:
  `search23/q14_t2_cap74_p12_z2_terminal_dr_p1_rr_100k/status.tsv`,
  `21/21` UNSAT;
- `p2=3C4`:
  `search23/q14_t2_cap74_p12_z2_terminal_dr_p2_rr_100k/status.tsv`,
  `16` UNSAT and `5` UNKNOWN;
- `p2=3C4` 5M tail:
  `search23/q14_t2_cap74_p12_z2_terminal_dr_p2_rr_5m/status.tsv`,
  `3` UNSAT and `2` UNKNOWN;
- `p2=3C4` 20M tail:
  `search23/q14_t2_cap74_p12_z2_terminal_dr_p2_rr_20m/status.tsv`,
  `2/2` UNSAT, `elapsedSec=6104`.

The final hard profile in the p2 tail was

`(zz,zs1,zs2,zd,s12)=(0,4,4,0,17)`.

Status: VERIFIED computational certificate under the p=12 2-factor lemma,
the V187 q-minimal terminal normalization, and the R-R nonedge codegree
condition.  This closes the full scalar row
`(2,6,6,0,12,25,74)`.

### V197. z5 cap74/p12 p-template RR-codegree reduction

The scalar row

`(z,s1,s2,d,p,e_R,cap)=(5,3,3,3,12,25,74)`

was started with the same RR-codegree p-template split.

The easy templates closed at 10k:

- `p0=C8+C4`:
  `search23/q14_t2_cap74_p12_z5_terminal_dr_p0_rr_10k/status.tsv`,
  `14740/14740` UNSAT, `elapsedSec=299`;
- `p1=C6+C6`:
  `search23/q14_t2_cap74_p12_z5_terminal_dr_p1_rr_10k/status.tsv`,
  `14740/14740` UNSAT, `elapsedSec=304`.

For `p2=3C4`, the original 126-worker run was stopped after the user capped
future runs at 100 workers.  Its valid partial results were merged with a
100-worker continuation:

`search23/q14_t2_cap74_p12_z5_terminal_dr_p2_rr_10k/status_merged_10k.tsv`.

The merged p2 10k result is:

- `total=14740`;
- `UNSAT=14532`;
- `SAT=0`;
- `UNKNOWN=208`.

The p2 UNKNOWN tail then reduced further:

- 100k tail:
  `search23/q14_t2_cap74_p12_z5_terminal_dr_p2_rr_100k_tail/status.tsv`,
  `88` UNSAT, `120` UNKNOWN, `SAT=0`;
- 1M tail:
  `search23/q14_t2_cap74_p12_z5_terminal_dr_p2_rr_1m_tail/status.tsv`,
  `107` UNSAT, `13` UNKNOWN, `SAT=0`.

The remaining 13 profiles passed to the 10M tail are:

`(0,3,5,10,7)`, `(0,3,6,9,7)`, `(0,4,4,10,7)`,
`(0,4,5,9,7)`, `(0,5,3,10,7)`, `(0,5,4,9,7)`,
`(0,6,3,9,7)`, `(1,3,6,8,7)`, `(1,4,5,8,7)`,
`(1,5,3,9,7)`, `(1,5,4,8,7)`, `(1,6,3,8,7)`,
and `(2,5,3,8,7)`.

A focused GPT Pro prompt for this terminal `3C4` obstruction was written to

`problems/23/gpt_q14_p12_3c4_terminal_obstruction_prompt_2026-06-15.md`.

Status: VERIFIED computational reduction, not a closure.  The z5 row remains
active pending the 13-profile 10M tail and/or a structural lemma for the
terminal `3C4` band.

### V198. z5 cap74/p12 row closed by `3C4` 10M tail

The 13 profiles left by V197 were rerun at 10M conflicts:

`search23/q14_t2_cap74_p12_z5_terminal_dr_p2_rr_10m_tail/status.tsv`.

The result is:

- `total=13`;
- `UNSAT=13`;
- `SAT=0`;
- `UNKNOWN=0`;
- `elapsedSec=915`;
- `throttle=13`;
- `conflicts=10000000`.

Combining V197 and this tail:

- `p0=C8+C4`: `14740/14740` UNSAT;
- `p1=C6+C6`: `14740/14740` UNSAT;
- `p2=3C4`: `14532` UNSAT at 10k, then `88` UNSAT at 100k,
  `107` UNSAT at 1M, and final `13` UNSAT at 10M.

Therefore the full scalar row

`(z,s1,s2,d,p,e_R,cap)=(5,3,3,3,12,25,74)`

is closed.

Status: VERIFIED computational certificate under the p=12 2-factor lemma,
the V187 q-minimal terminal normalization, and the R-R nonedge codegree
condition.

### V199. z6 cap74/p12 easy p-template reduction

The next scalar row

`(z,s1,s2,d,p,e_R,cap)=(6,2,2,4,12,25,74)`

was started with the same RR-codegree p-template split.

The first two templates closed at 10k:

- `p0=C8+C4`:
  `search23/q14_t2_cap74_p12_z6_terminal_dr_p0_rr_10k/status.tsv`,
  `9499/9499` UNSAT, `elapsedSec=411`;
- `p1=C6+C6`:
  `search23/q14_t2_cap74_p12_z6_terminal_dr_p1_rr_10k/status.tsv`,
  `9499/9499` UNSAT, `elapsedSec=413`.

Status: VERIFIED computational reduction, not a closure.  The row remains
active until the `p2=3C4` template is closed.

### V200. z6 cap74/p12 row closed by `3C4` tail

The `p2=3C4` template for the row

`(z,s1,s2,d,p,e_R,cap)=(6,2,2,4,12,25,74)`

was completed after the V199 easy-template reductions.

The p2 run and tails are:

- 10k:
  `search23/q14_t2_cap74_p12_z6_terminal_dr_p2_rr_10k/status.tsv`,
  `9459` UNSAT, `40` UNKNOWN, `SAT=0`, `elapsedSec=1715`;
- 100k tail:
  `search23/q14_t2_cap74_p12_z6_terminal_dr_p2_rr_100k_tail/status.tsv`,
  `22` UNSAT, `18` UNKNOWN, `SAT=0`, `elapsedSec=63`;
- 1M tail:
  `search23/q14_t2_cap74_p12_z6_terminal_dr_p2_rr_1m_tail/status.tsv`,
  `18` UNSAT, `0` UNKNOWN, `SAT=0`, `elapsedSec=77`.

Combining V199 and this tail:

- `p0=C8+C4`: `9499/9499` UNSAT;
- `p1=C6+C6`: `9499/9499` UNSAT;
- `p2=3C4`: `9499/9499` UNSAT after the two tails.

Therefore the full scalar row

`(z,s1,s2,d,p,e_R,cap)=(6,2,2,4,12,25,74)`

is closed.

Status: VERIFIED computational certificate under the p=12 2-factor lemma,
the V187 q-minimal terminal normalization, and the R-R nonedge codegree
condition.

### V201. q=14/t=2 scalar frontier after V200

The scalar audit was rerun after excluding the V196, V198, and V200 closed
rows:

`search23/q14_t2_scalar_audit_post_v200.tsv`.

The first-line summary is:

- `rows=39653`;
- maximum remaining cap is `74`;
- remaining `cap=74` rows: `46`;
- no `cap=74` row with `p=12,e_R=25` remains.

The remaining cap74 groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: `5` rows, `p=13..17`,
  `e_R=24..20`;
- `(z,s1,s2,d)=(3,5,5,1)`: `6` rows, `p=13..18`,
  `e_R=24..19`;
- `(z,s1,s2,d)=(4,4,4,2)`: `9` rows, `p=13..21`,
  `e_R=24..16`;
- `(z,s1,s2,d)=(5,3,3,3)`: `9` rows, `p=13..21`,
  `e_R=24..16`;
- `(z,s1,s2,d)=(6,2,2,4)`: `9` rows, `p=13..21`,
  `e_R=24..16`;
- `(z,s1,s2,d)=(8,0,0,6)`: `8` rows, `p=14..21`,
  `e_R=23..16`.

Status: q=14/t=2 remains active.  The cap74/p12/eR25 layer is closed; the
frontier has moved to p>=13/e_R<=24 (or the z8 p>=14 group).

### V202. z8 cap74 p14/eR23 generic RR calibration

The small z8 frontier row

`(z,s1,s2,d,p,e_R,cap)=(8,0,0,6,14,23,74)`

has only 24 category profiles.  It was tested with the generic RR-codegree
solver

`search23/sat_q14_t2_shape_family_terminal_dr_rr_aonly.exe`

using the V187 terminal normalization and R-R nonedge codegree condition.

The runs were:

- 10k:
  `search23/q14_t2_cap74_p14_z8_terminal_dr_rr_10k/status.tsv`,
  `16` UNSAT, `8` UNKNOWN, `SAT=0`, `elapsedSec=82`;
- 100k tail:
  `search23/q14_t2_cap74_p14_z8_terminal_dr_rr_100k_tail/status.tsv`,
  `0` additional UNSAT, `8` UNKNOWN, `SAT=0`, `elapsedSec=454`.

Status: VERIFIED calibration, not a closure.  This row appears to need a
stronger z8-specific structural cut rather than merely increasing the generic
RR-codegree conflict limit.

### V203. z2 cap74 p13/eR24 generic RR calibration

The first p>=13 frontier row

`(z,s1,s2,d,p,e_R,cap)=(2,6,6,0,13,24,74)`

was tested with the generic RR-codegree solver.

The runs were:

- 10k:
  `search23/q14_t2_cap74_p13_z2_terminal_dr_rr_10k/status.tsv`,
  `333` UNSAT, `4` UNKNOWN, `SAT=0`, `elapsedSec=52`;
- 100k tail:
  `search23/q14_t2_cap74_p13_z2_terminal_dr_rr_100k_tail/status.tsv`,
  `1` UNSAT, `3` UNKNOWN, `SAT=0`, `elapsedSec=38`;
- 1M tail:
  `search23/q14_t2_cap74_p13_z2_terminal_dr_rr_1m_tail/status.tsv`,
  `0` additional UNSAT, `3` UNKNOWN, `SAT=0`, `elapsedSec=155`;
- exact-M 1M tail:
  `search23/q14_t2_cap74_p13_z2_terminal_dr_rr_exactm_1m_tail/status.tsv`,
  `0` additional UNSAT, `3` UNKNOWN, `SAT=0`, `elapsedSec=149`.

The remaining 3 profiles are

`(zz,zs1,zs2,zd,s12)=(0,4,4,0,16)`,
`(0,5,5,0,14)`, and `(0,6,6,0,12)`.

Status: VERIFIED calibration, not a closure.  This z2 p13 row appears to have
the same central-orientation obstruction as the z2 p12 row and likely needs a
special structural cut rather than merely raising the generic RR-codegree
limit.

### V204. z3 cap74 p13/eR24 generic RR calibration

The next p>=13 frontier row

`(z,s1,s2,d,p,e_R,cap)=(3,5,5,1,13,24,74)`

was tested with the generic RR-codegree solver.

The runs were:

- 10k:
  `search23/q14_t2_cap74_p13_z3_terminal_dr_rr_10k/status.tsv`,
  `3321` UNSAT, `35` UNKNOWN, `SAT=0`, `elapsedSec=785`;
- 100k tail:
  `search23/q14_t2_cap74_p13_z3_terminal_dr_rr_100k_tail/status.tsv`,
  `2` UNSAT, `33` UNKNOWN, `SAT=0`, `elapsedSec=60`;
- 1M tail:
  `search23/q14_t2_cap74_p13_z3_terminal_dr_rr_1m_tail/status.tsv`,
  `0` additional UNSAT, `33` UNKNOWN, `SAT=0`, `elapsedSec=257`.
- exact-M 1M tail:
  `search23/q14_t2_cap74_p13_z3_terminal_dr_rr_exactm_1m_tail/status.tsv`,
  `0` additional UNSAT, `33` UNKNOWN, `SAT=0`, `elapsedSec=246`.

The 33 remaining profiles all have `zz=0` and lie in the high `Z-S` /
high `S1-S2` terminal band.  A focused GPT Pro prompt for the p13 obstruction
was written to

`problems/23/gpt_q14_p13_terminal_obstruction_prompt_2026-06-15.md`.

Status: VERIFIED calibration, not a closure.  As with V203, the generic
RR-codegree conflict limit is no longer the main lever; the row appears to
need a p13 structural cut.

### V205. z4 cap74 p13/eR24 generic RR calibration

The next p>=13 frontier row

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,13,24,74)`

was run with the generic terminal-degree + terminal-R-degree + full R/R
codegree worker:

- 10k triage:
  `search23/q14_t2_cap74_p13_z4_terminal_dr_rr_10k/status.tsv`,
  `9914` UNSAT, `208` UNKNOWN, `SAT=0`.
- 100k tail on those 208 UNKNOWN profiles:
  `search23/q14_t2_cap74_p13_z4_terminal_dr_rr_100k_tail_r2/status.tsv`,
  `11` additional UNSAT, `197` UNKNOWN, `SAT=0`, `elapsedSec=374`.

The 197 remaining profiles concentrate in the high-`ZD` / low-`S12` band:
by `zz`, counts are `0:148`, `1:44`, `2:5`; by `zd`, counts are
`0:1, 1:2, 2:7, 3:14, 4:25, 5:37, 6:43, 7:33, 8:35`; by `s12`, counts are
`8:57, 9:51, 10:39, 11:27, 12:18, 13:4, 14:1`.

Status: VERIFIED calibration, not a closure.  The row now matches V203--V204
in requiring a p13 structural cut rather than merely higher generic conflict
limits.

### V206. z4 cap74 p13/eR24 exact-M calibration

The 197 UNKNOWN profiles from V205 were rerun with the exact A/B-incidence
total equality (`EXACT_M`) at 1M conflicts:

- `search23/q14_t2_cap74_p13_z4_terminal_dr_rr_exactm_1m_tail/status.tsv`,
  `23` UNSAT, `174` UNKNOWN, `SAT=0`, `elapsedSec=1379`.

The 174 remaining profiles have distribution:

- by `zz`: `0:128`, `1:41`, `2:5`;
- by `zd`: `1:2, 2:6, 3:14, 4:24, 5:34, 6:37, 7:29, 8:28`;
- by `s12`: `8:48, 9:50, 10:39, 11:27, 12:9, 13:1`.

Exact-M removes only a small part of the z4 p13 row.  The surviving band is
still concentrated in high-`ZD` / low-to-medium-`S12` profiles, so the next
useful step is a p13 structural obstruction or a smaller proof-checkable
orientation/deletion certificate targeted at that band.

### V207. z2 cap74 p13/eR24 defect reduction

In the row

`(z,s1,s2,d,p,e_R,cap) = (2,6,6,0,13,24,74)`,

the three V203 hard profiles reduce to one.  The profiles

`(zz,zs1,zs2,zd,s12) = (0,5,5,0,14)` and `(0,6,6,0,12)`

are impossible under the terminal hypotheses; only `(0,4,4,0,16)` remains.

Proof.

Let `P = G[A,B]`.  Since `p=13`, `|A|=|B|=6`, every row and column of `P`
has degree at least `2`, and the total number of `P`-edges is `13`, the row
and column degree sequences are both `(3,2,2,2,2,2)`.

For `r in R`, put `X_r=N_A(r)`, `Y_r=N_B(r)`, and
`m_r=|X_r|+|Y_r|`.  Triangle-freeness gives
`X_r x Y_r` disjoint from `E(P)`.  Counting `P`-edges from `X_r` to
`B\Y_r` gives

`2|X_r| <= e_P(X_r,B\Y_r) <= 2(6-|Y_r|)+1`,

because each `a in X_r` has `P`-degree at least `2`, while `B\Y_r` contains
at most one degree-`3` vertex and all other vertices have degree at most `2`.
Thus `m_r <= 6`.  Define `delta_r = 6-m_r >= 0`.  Since `cap=74`,

`sum_r delta_r = 14*6 - 74 = 10`.                         (D)

If `r notin U_i` is terminal C-tight, so `d_R(r,U_i)=2`, the terminal
normalization gives `deg(r)=8`.  Hence

`delta_r = d_R(r) + |label(r)| - 2`.                       (T)

For a singleton `s in S_1`, write `h(s)=d_R(s,S_2)` and
`z(s)=d_R(s,Z)`.  Since `d=0`, `s` is C-tight exactly when `h(s)=2`, and
then (T) gives

`delta_s = 1 + z(s)`.                                     (S)

Let `k=ZS_1=ZS_2`, so the three V203 profiles have `k=4,5,6` and
`S12=24-2k`.  On one singleton side, let
`T_i={s : d_R(s,S_{3-i})=2}` and `t_i=|T_i|`.  Since every singleton has at
least two opposite-singleton neighbours and non-tight singletons have at
least three,

`t_i >= 18-S12`.

The non-tight vertices on that side can absorb at most `2(6-t_i)` of the
`k` zero-singleton incidences.  Therefore tight singleton defect on side `i`
is at least

`t_i + max(0, k - 2(6-t_i))`.                              (side)

For `k=6`, `S12=12`, so `t_1=t_2=6`.  All singletons are tight, and

`sum_{s in S_1} delta_s = 6 + ZS_1 = 12`,

with the same bound on `S_2`.  Singleton defect alone is at least `24`,
contradicting (D).

For `k=5`, `S12=14`, so `t_1,t_2 >= 4`.  The side bound is minimized at
`t_i=4` and gives at least `5` defect on each singleton side, hence at least
`10` singleton defect.  The two zero vertices have total `5` incidences to
each singleton colour, while each zero must have at least two neighbours in
each singleton colour.  Thus their colour-count pairs are either `(2,2)` and
`(3,3)`, or `(2,3)` and `(3,2)`.  In every case at least one zero vertex is
C-tight and contributes at least `2` defect by (T).  Total defect is therefore
at least `12`, contradicting (D).

For `k=4`, both zero vertices have exactly two neighbours in each singleton
colour, hence both are C-tight and contribute `4` total defect.  The same
argument gives only the residual necessary condition

`sum_{s in T_1 union T_2} (1+z(s)) <= 6`,

which is compatible with (D).  Therefore the only surviving z2 profile is
`(0,4,4,0,16)`.

The arithmetic lower bound is independently reproduced by

`search23/verify_z2_p13_defect.cpp`

with output `k=4 ... total_min=8 ... SURVIVES`,
`k=5 ... total_min=12 ... IMPOSSIBLE`, and
`k=6 ... total_min=24 ... IMPOSSIBLE`.

Tier: rigorous-informal plus checked finite arithmetic.  This lemma explains
two of the three V203 UNKNOWN profiles; it is not yet a closure of the z2 row.

### V208. z2 cap74 p13/eR24 row closed

The remaining V207 profile

`(zz,zs1,zs2,zd,s12) = (0,4,4,0,16)`

was split by the p=13 `A-B` template classification.  The C++ enumerator

`search23/enumerate_p13_templates.cpp`

shows that every `6 x 6` bipartite graph with row and column degree sequence
`(3,2,2,2,2,2)` is, up to `S_6 x S_6`, one of 14 templates:

`search23/p13_templates.tsv`.

The residual profile was checked with the exact-M, terminal-degree,
terminal-R-degree, full R/R-codegree worker, the V207 residual tight-defect
cut, and fixed `P_TEMPLATE_ID = 100..113`.  The run

`search23/q14_t2_cap74_p13_z2_k4_p13templates_1m/status.tsv`

has `14` UNSAT, `SAT=0`, `UNKNOWN=0`.

Together with V207, this closes the row

`(z,s1,s2,d,p,e_R,cap) = (2,6,6,0,13,24,74)`.

Status: VERIFIED finite closure of this row.

### V209. q=14/t=2 scalar frontier after V208

The scalar audit was rerun after excluding the V208 z2 p13/eR24 row:

`search23/q14_t2_scalar_audit_post_v208.tsv`

It reports `39652` surviving scalar rows and `45` cap74 rows.  The cap74
groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: 4 rows, `p=14..17`, `e_R=23..20`;
- `(3,5,5,1)`: 6 rows, `p=13..18`, `e_R=24..19`;
- `(4,4,4,2)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(5,3,3,3)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(6,2,2,4)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Next target: apply the p=13 template split from V208 to the z3 and z4 p13
hard cores before designing a broader p13 certificate.

### V210. z3 cap74 p13/eR24 p=13 template split

The 33 UNKNOWN profiles from V204 were split over the 14 p=13 `A-B`
templates from V208 and run at 1M conflicts:

`search23/q14_t2_cap74_p13_z3_p13templates_1m/status.tsv`

Result: `444` UNSAT, `18` UNKNOWN, `SAT=0`, `elapsedSec=1552`.

The 18 remaining template leaves are:

`(profile_idx,template,zz,zs1,zs2,zd,s12)` =
`(219,6,0,3,6,3,12)`,
`(283,6,0,4,6,3,11)`,
`(335,12,0,5,3,3,13)`,
`(339,6,0,5,4,3,12)`,
`(343,6,0,5,5,3,11)`,
`(345,6,0,5,6,1,12)`,
`(347,7,0,5,6,3,10)`,
`(399,6,0,6,3,3,12)`,
`(403,6,0,6,4,3,11)`,
`(406,6,0,6,5,2,11)`,
`(407,7,0,6,5,3,10)`,
`(407,10,0,6,5,3,10)`,
`(408,7,0,6,6,0,12)`,
`(408,12,0,6,6,0,12)`,
`(408,13,0,6,6,0,12)`,
`(410,6,0,6,6,2,10)`,
`(410,10,0,6,6,2,10)`,
`(467,13,0,7,4,3,10)`.

Status: VERIFIED reduction, not a row closure.  The remaining z3 p13 hard
core is now 18 fixed-template leaves.

### V211. z3 cap74 p13/eR24 row closed

The 18 UNKNOWN fixed-template leaves from V210 were rerun at 10M conflicts:

`search23/q14_t2_cap74_p13_z3_p13templates_10m_tail/status.tsv`

Result: `18` UNSAT, `SAT=0`, `UNKNOWN=0`, `elapsedSec=271`.

Together with V210, this closes the row

`(z,s1,s2,d,p,e_R,cap) = (3,5,5,1,13,24,74)`.

Status: VERIFIED finite closure of this row.

### V212. q=14/t=2 scalar frontier after V211

The scalar audit was rerun after excluding the V211 z3 p13/eR24 row:

`search23/q14_t2_scalar_audit_post_v211.tsv`

It reports `39651` surviving scalar rows and `44` cap74 rows.  The cap74
groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: 4 rows, `p=14..17`, `e_R=23..20`;
- `(3,5,5,1)`: 5 rows, `p=14..18`, `e_R=23..19`;
- `(4,4,4,2)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(5,3,3,3)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(6,2,2,4)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Next finite target: apply the p=13 template machinery to the z4 p13/eR24 row,
or derive a high-`ZD` structural cut for V206's z4 hard core.

### V213. z4 cap74 p13/eR24 row closed by p=13 template split

The z4 row

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,13,24,74)`

was split over the 14 p=13 A-B templates.  The 1M run

`search23/q14_t2_cap74_p13_z4_p13templates_1m/status.tsv`

returned `2403` UNSAT, `33` UNKNOWN, `SAT=0`, `elapsedSec=3168`.

The remaining 33 profile/template leaves were rerun at 10M conflicts.  The
tail directory

`search23/q14_t2_cap74_p13_z4_p13templates_10m_tail/status.tsv`

returned `462` UNSAT, `SAT=0`, `UNKNOWN=0`, `elapsedSec=11`.  The tail script
reran all 14 templates for the 33 hard profiles, which is stronger than only
rerunning the previously unknown leaves.

Together these runs close the row

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,13,24,74)`.

Status: VERIFIED finite closure of this row.

### V214. q=14/t=2 scalar frontier after V213

The scalar audit was rerun after excluding the V213 z4 p13/eR24 row:

`search23/q14_t2_scalar_audit_post_v213.tsv`

It reports `39650` surviving scalar rows and `43` cap74 rows.  The cap74
groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: 4 rows, `p=14..17`, `e_R=23..20`;
- `(3,5,5,1)`: 5 rows, `p=14..18`, `e_R=23..19`;
- `(4,4,4,2)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(5,3,3,3)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(6,2,2,4)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Next finite target: apply the p=13 template machinery to z5 and z6 p13/eR24,
then reassess whether a broader p>=14 structural cut is needed.

### V215. z5 p13/eR24 matching cut and finite closure

For the z5 row

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,13,24,74)`,

write the category parameters as

`(ZZ,ZS1,ZS2,ZD,S12) = (a,b,c,f,x)`.

GPT Pro supplied, and I checked against the local hypotheses, the following
rigorous category cut. Since every singleton has at least two neighbours in
the opposite singleton side and each singleton side has size `3`, the missing
`S1-S2` pairs form a matching of size `M = 9 - S12`. If a zero vertex `z` has
neighbour sets `P_z` in `S1` and `Q_z` in `S2`, then triangle-freeness forces
`P_z x Q_z` to lie in that missing matching. Hence every zero has at least one
`D`-neighbour, and the defect budget implies

- `S12=6 -> ZD>=9`;
- `S12=7 -> ZD>=8`;
- `S12=8 -> ZD>=8`;
- `S12=9 -> ZD>=10`.

On the 10k generic category triage, this cut eliminates `38` of the `244`
UNKNOWN category profiles:

`search23/q14_t2_cap74_p13_z5_terminal_dr_rr_exactm_10k/status.tsv`

The finite closure was then obtained as follows.

1. Generic exact-M terminal triage at 10k conflicts over all category profiles:

   `search23/q14_t2_cap74_p13_z5_terminal_dr_rr_exactm_10k/status.tsv`

   Result: `13585` category profiles, `13341` UNSAT, `SAT=0`, `244` UNKNOWN,
   `elapsedSec=7174`.

2. Split the `244` UNKNOWN profiles over the 14 canonical p=13 `A-B`
   templates at 1M conflicts:

   `search23/q14_t2_cap74_p13_z5_p13templates_1m/`

   The run was interrupted/ended before consolidation, but produced `3255`
   UNSAT leaves, `5` UNKNOWN leaves, `48` NA leaves, and `108` missing leaves.

3. The non-closed leaves in (2) involved only `25` category profiles. These
   were written to

   `search23/q14_t2_cap74_p13_z5_hard25_from_1m.tsv`

   and all 14 templates for those 25 profiles were rerun at 10M conflicts:

   `search23/q14_t2_cap74_p13_z5_p13templates_10m_tail25/status.tsv`

   Result: `350` UNSAT, `SAT=0`, `UNKNOWN=0`, `NA=0`, `elapsedSec=1274`.

4. A coverage audit checked every one of the `244*14=3416` template leaves:
   each leaf is UNSAT either in the 1M split or in the 10M tail, with
   `missing=0` and `bad=0`.

Therefore the row

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,13,24,74)`

is closed by finite certificate.

Status: VERIFIED finite closure of this row.

### V216. q=14/t=2 scalar frontier after V215

The scalar audit was rerun after excluding the V215 z5 p13/eR24 row:

`search23/q14_t2_scalar_audit_post_v215.tsv`

It reports `39649` surviving scalar rows and `42` cap74 rows.  The cap74
groups are:

- `(z,s1,s2,d)=(2,6,6,0)`: 4 rows, `p=14..17`, `e_R=23..20`;
- `(3,5,5,1)`: 5 rows, `p=14..18`, `e_R=23..19`;
- `(4,4,4,2)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(5,3,3,3)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(6,2,2,4)`: 9 rows, `p=13..21`, `e_R=24..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Next finite target: apply the p=13 template machinery to the remaining z6
p13/eR24 row, then reassess whether a broader p>=14 structural cut is needed.

### V217. z6 cap74 p13/eR24 row closed by p=13 template split

For the z6 row

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,13,24,74)`,

the closure was obtained as follows.

1. Generic exact-M terminal triage at 10k conflicts over all category profiles:

   `search23/q14_t2_cap74_p13_z6_terminal_dr_rr_exactm_10k/status.tsv`

   Result: `8850` category profiles, `8756` UNSAT, `SAT=0`, `94` UNKNOWN,
   `elapsedSec=1629`.

2. Split the `94` UNKNOWN profiles over the 14 canonical p=13 `A-B`
   templates at 1M conflicts:

   `search23/q14_t2_cap74_p13_z6_p13templates_1m/status.tsv`

   Result: `1315` UNSAT, `SAT=0`, `1` UNKNOWN, `elapsedSec=1498`.

3. The one remaining UNKNOWN was profile `1780`, category
   `(ZZ,ZS1,ZS2,ZD,S12)=(2,2,3,13,4)`, template `9`.  To avoid relying on
   just the one leaf, all 14 templates for that profile were rerun at 10M:

   `search23/q14_t2_cap74_p13_z6_p13templates_10m_tail1/status.tsv`

   Result: `14` UNSAT, `SAT=0`, `UNKNOWN=0`, `NA=0`, `elapsedSec=210`.

4. A coverage audit checked every one of the `94*14=1316` template leaves:
   each leaf is UNSAT either in the 1M split or in the 10M tail, with
   `missing=0` and `bad=0`.

Therefore the row

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,13,24,74)`

is closed by finite certificate.

Status: VERIFIED finite closure of this row.

### V218. q=14/t=2 scalar frontier after V217

The scalar audit was rerun after excluding the V217 z6 p13/eR24 row:

`search23/q14_t2_scalar_audit_post_v217.tsv`

It reports `39648` surviving scalar rows and `41` cap74 rows.  The cap74
frontier now has no p13/eR24 rows.  All remaining cap74 rows satisfy `p>=14`:

- `(z,s1,s2,d)=(2,6,6,0)`: 4 rows, `p=14..17`, `e_R=23..20`;
- `(3,5,5,1)`: 5 rows, `p=14..18`, `e_R=23..19`;
- `(4,4,4,2)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(5,3,3,3)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(6,2,2,4)`: 8 rows, `p=14..21`, `e_R=23..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Next finite target: find a structural cut for `p>=14`, or close the first
remaining p14/eR23 layer by a broader template/certificate split.

### V219. First p>=14 obstruction snapshot

After V218, the first p>=14 layer was probed computationally.

For the z8 row

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,14,23,74)`,

generic exact-M terminal triage at 10k conflicts over all category profiles:

`search23/q14_t2_cap74_p14_z8_terminal_dr_rr_exactm_10k/status.tsv`

returned `16` UNSAT, `SAT=0`, `8` UNKNOWN, `elapsedSec=77`.
The eight UNKNOWN categories are the pure `Z-D` band

`(ZZ,ZS1,ZS2,ZD,S12) = (a,0,0,23-a,0)` for `0 <= a <= 7`.

They were rerun at 1M in

`search23/q14_t2_cap74_p14_z8_terminal_dr_rr_exactm_1m_tail/`.

At the time of this snapshot, the first finished leaves remained UNKNOWN,
so this row appears to need a structural `Z-D` reduction or a better finite
certificate rather than only higher conflict limits.

For the z6 row

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,14,23,74)`,

generic exact-M terminal triage at 10k conflicts:

`search23/q14_t2_cap74_p14_z6_terminal_dr_rr_exactm_10k/status.tsv`

returned `8170` category profiles, `8084` UNSAT, `SAT=0`, `86` UNKNOWN,
`elapsedSec=1661`.

The `86` UNKNOWN categories were rerun at 1M:

`search23/q14_t2_cap74_p14_z6_terminal_dr_rr_exactm_1m_tail/status.tsv`

which returned `21` UNSAT, `SAT=0`, `65` UNKNOWN, `elapsedSec=766`.
All remaining z6 p14 UNKNOWN categories have `S12=4`, i.e. the `S1-S2`
channel is complete, and the obstruction again concentrates in high `ZD`.

Status: VERIFIED obstruction data, not a closure.

### V220. First p>=14 row closure: z8, p21/e_R16

GPT Pro's p>=14 reduction answer was saved at

`problems/23/gpt_pge14_reduction_answer_2026-06-15.md`.

The first finite-certificate target suggested there was

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,21,16,74)`.

For this row, local domination forces each of the eight zero-labelled
vertices to have at least two neighbours in `D`.  Since there are no singleton
vertices and no `D-D` edges are allowed, `e_R=16` forces the unique category

`(ZZ,ZS1,ZS2,ZD,S12) = (0,0,0,16,0)`,

and each zero vertex has exactly two `D`-neighbours.  Under terminal
normalization, every zero has `m_z=6`, so the whole remaining cap defect is
carried by the six double-labelled vertices.

The p=21 A-B template enumeration produced `10951` canonical templates:

`search23/p21_templates.tsv`

with individual fixed-P files in

`search23/p21_templates/`.

The fixed-P batch

`search23/z8_p21_e16_zd16_p21templates_all_10k/`

checked all `10951` templates at `10000` CaDiCaL conflicts each, using the
exact-M terminal-degree/R-degree/RR-codegree solver with `fixed_p_path`.
It returned:

`done=10951/10951`, `unsat=10951`, `sat=0`, `unknown=0`, `na=0`,
`elapsedSec=417`.

The scalar audit was updated to remove this row:

`search23/q14_t2_scalar_audit_post_v220.tsv`.

The cap74 frontier is now `40` rows, all still with `p>=14`.

Status: VERIFIED finite row closure.

### V221. Second p>=14 row closure: z8, p20/e_R17

The next zero/doubleton row was

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,20,17,74)`.

Again local domination forces `ZD >= 16`; because there are no singleton
vertices and no `D-D` edges, the only two possible R categories are

`(ZZ,ZS1,ZS2,ZD,S12) = (0,0,0,17,0)` and `(1,0,0,16,0)`.

The p=20 A-B template enumeration produced `11278` canonical templates:

`search23/p20_templates.tsv`

Both category splits were checked with the exact-M terminal-degree/R-degree/
RR-codegree fixed-P solver at `10000` CaDiCaL conflicts per template:

- `search23/z8_p20_e17_zz0_zd17_p20templates_all_10k/`:
  `done=11278/11278`, `unsat=11278`, `sat=0`, `unknown=0`, `elapsedSec=434`.
- `search23/z8_p20_e17_zz1_zd16_p20templates_all_10k/`:
  `done=11278/11278`, `unsat=11278`, `sat=0`, `unknown=0`, `elapsedSec=463`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v221.tsv`.

The cap74 frontier is now `39` rows, all still with `p>=14`.

Status: VERIFIED finite row closure.

### V222. Third p>=14 row closure: z4, p21/e_R16

GPT Pro's next-row recommendation was saved at

`problems/23/gpt_next_after_v220_answer_2026-06-15.md`.

The recommended finite target was

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,21,16,74)`.

For this row, local domination forces the category

`(ZZ,ZS1,ZS2,ZD,S12) = (0,0,0,8,8)`.

The four zero vertices must each be adjacent to both double-labelled vertices,
and the `S1-S2` graph is 2-regular on `4+4` vertices.  Hence there are only
two R-skeletons up to symmetry:

- `C8`: `search23/z4_p21_R_C8.txt`
- `C4+C4`: `search23/z4_p21_R_C4C4.txt`

Both fixed-R skeletons were checked against all `10951` p=21 canonical A-B
templates with the exact-M terminal-degree/R-degree/RR-codegree fixed-P solver
at `10000` CaDiCaL conflicts per template:

- `search23/z4_p21_e16_C8_p21templates_all_10k/`:
  `done=10951/10951`, `unsat=10951`, `sat=0`, `unknown=0`, `elapsedSec=384`.
- `search23/z4_p21_e16_C4C4_p21templates_all_10k/`:
  `done=10951/10951`, `unsat=10951`, `sat=0`, `unknown=0`, `elapsedSec=389`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v222.tsv`.

The cap74 frontier is now `38` rows, all still with `p>=14`.

Status: VERIFIED finite row closure.

### V223. Fourth p>=14 row closure: z6, p21/e_R16

The next GPT-suggested row after V222 was

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,21,16,74)`.

Local domination forces the category

`(ZZ,ZS1,ZS2,ZD,S12) = (0,0,0,12,4)`.

Reason: each zero needs at least two neighbours in the double-labelled class,
so `ZD >= 12`; each singleton has only two opposite singleton vertices
available, so `S12=4`; with `e_R=16`, all other R-edge categories vanish.

Unlike V222, the category closed directly without fixing the Z-D skeleton or
the A-B template.  The exact-M terminal-degree/R-degree/RR-codegree solver ran

`search23/sat_q14_t2_shape_family_terminal_dr_rr_exactm_aonly.exe 6 2 2 4 21 16 74 100000 1 1 0 0 0 0 0 0 0 12 4`

and returned:

`SHAPE_FAMILY_STATUS 20`, `sat=0`, `unknown=0` for the forced category.

Output:

`search23/z6_p21_e16_forcedcat_100k.out`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v223.tsv`.

The cap74 frontier is now `37` rows, all still with `p>=14`.

Status: VERIFIED finite row closure.

### V224. Fifth p>=14 row closure: z5, p21/e_R16

The remaining p=21 cap74 row was

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,21,16,74)`.

Unlike V222 and V223, the R-category is not forced by scalar counting alone,
so all category profiles were triaged with the exact-M terminal-degree/
R-degree/RR-codegree solver.

The initial category run was interrupted by the tool timeout after `1273/4506`
profiles had produced status files.  These partial statuses were consolidated:

`search23/z5_p21_e16_cat_10k/status.partial.tsv`.

It contained `1272` UNSAT, `SAT=0`, `UNKNOWN=1`.

The remaining `3233` missing profiles plus the one unknown profile were rerun
as

`search23/z5_p21_e16_cat_tail_10k/`,

which returned `done=3234/3234`, `unsat=3233`, `sat=0`, `unknown=1`,
`elapsedSec=1999`.

Merging the partial and tail results gave:

`total=4506`, `unsat=4505`, `sat=0`, `unknown=1`.

The sole remaining category was

`(ZZ,ZS1,ZS2,ZD,S12) = (0,0,0,10,6)`.

That category was rerun directly at `1000000` CaDiCaL conflicts:

`search23/z5_p21_e16_cat_zz0_zd10_s12_6_1m.out`,

and returned `SHAPE_FAMILY_STATUS 20`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v224.tsv`.

The cap74 frontier is now `36` rows, all with `14 <= p <= 20`.

Status: VERIFIED finite row closure.

### V225. Sixth p>=14 row closure: z6, p20/e_R17

The next p20 row tested was

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,20,17,74)`.

A no-category exact-M terminal/RR solver probe at `100000` conflicts returned
`UNKNOWN`, so a category split was run:

`search23/z6_p20_e17_cat_10k/`.

This checked `4020` category profiles at `10000` conflicts with `100` workers
and returned:

`unsat=4016`, `sat=0`, `unknown=4`, `na=0`.

The four unknown categories were:

- `(0,0,0,13,4)`
- `(0,0,1,12,4)`
- `(0,1,0,12,4)`
- `(1,0,0,12,4)`

They were rerun at `1000000` conflicts in

`search23/z6_p20_e17_cat_tail4_1m/`,

and all four returned `SHAPE_FAMILY_STATUS 20`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v225.tsv`.

The cap74 frontier is now `35` rows.

Status: VERIFIED finite row closure.

### V226. Seventh p>=14 row closure: z4, p20/e_R17

The next p20 row tested was

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,20,17,74)`.

A no-category exact-M terminal/RR solver probe at `100000` conflicts returned
`UNKNOWN`, so a full category split was run.

The initial category run was interrupted by the tool timeout after `1474/4491`
profiles had produced status files.  These partial statuses were consolidated:

`search23/z4_p20_e17_cat_10k/status.partial.tsv`.

It contained `1470` UNSAT, `SAT=0`, `UNKNOWN=4`.

The remaining missing profiles plus the four unknown profiles were rerun as

`search23/z4_p20_e17_cat_tail_10k/`,

which returned `done=3021/3021`, `unsat=3017`, `sat=0`, `unknown=4`,
`elapsedSec=1463`.

Merging the partial and tail results gave:

`total=4491`, `unsat=4487`, `sat=0`, `unknown=4`.

The four remaining categories were:

- `(0,0,0,8,9)`
- `(0,0,1,8,8)`
- `(0,1,0,8,8)`
- `(0,1,1,7,8)`

They were rerun at `1000000` conflicts in

`search23/z4_p20_e17_cat_tail4_1m/`,

and all four returned `SHAPE_FAMILY_STATUS 20`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v226.tsv`.

The cap74 frontier is now `34` rows.

Status: VERIFIED finite row closure.

### V227. Eighth p>=14 row closure: z5, p20/e_R17

The remaining p20 row was

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,20,17,74)`.

A no-category exact-M terminal/RR solver probe at `100000` conflicts returned
`UNKNOWN`, so a full category split was run:

`search23/z5_p20_e17_cat_10k/`.

This checked `5430` category profiles at `10000` conflicts with up to `100`
workers and returned:

`unsat=5425`, `sat=0`, `unknown=5`, `na=0`, `elapsedSec=3448`.

The five unknown categories were:

- `(0,0,0,10,7)`
- `(0,0,0,11,6)`
- `(0,0,1,10,6)`
- `(0,1,0,10,6)`
- `(0,1,1,9,6)`

They were rerun at `1000000` conflicts in

`search23/z5_p20_e17_cat_tail5_1m/`,

and all five returned `SHAPE_FAMILY_STATUS 20`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v227.tsv`.

The cap74 frontier is now `33` rows, all with `14 <= p <= 19`.

Status: VERIFIED finite row closure.

### V228. Ninth p>=14 row closure: z8, p19/e_R18

The first p19 row tested was

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,19,18,74)`.

A no-category exact-M terminal/RR solver probe at `100000` conflicts produced
no status output after `244` seconds and was stopped, so the row was split into
its three locally forced categories:

- `(ZZ,ZD)=(0,18)`
- `(ZZ,ZD)=(1,17)`
- `(ZZ,ZD)=(2,16)`

The category-only run at `10000` conflicts returned `UNKNOWN` for all three
categories, so canonical `p=19` A-B templates were generated:

`search23/p19_templates.tsv`.

This contains `9596` canonical templates.  First-100 fixed-P samples for each
of the three categories all returned UNSAT.  The full fixed-P runs were then
performed at `10000` conflicts with up to `100` workers:

- `search23/z8_p19_e18_zz0_zd18_p19templates_all_10k/`:
  `done=9596/9596`, `unsat=9596`, `sat=0`, `unknown=0`,
  `elapsedSec=338`.
- `search23/z8_p19_e18_zz1_zd17_p19templates_all_10k/`:
  `done=9596/9596`, `unsat=9596`, `sat=0`, `unknown=0`,
  `elapsedSec=348`.
- `search23/z8_p19_e18_zz2_zd16_p19templates_all_10k/`:
  `done=9596/9596`, `unsat=9596`, `sat=0`, `unknown=0`,
  `elapsedSec=351`.

The scalar audit was updated:

`search23/q14_t2_scalar_audit_post_v228.tsv`.

The cap74 frontier is now `32` rows:

- `p=19,e_R=18`: `z=4,5,6`;
- `p=18,e_R=19`: `z=3,4,5,6,8`;
- `p=17,e_R=20`: `z=2,3,4,5,6,8`;
- `p=16,e_R=21`: `z=2,3,4,5,6,8`;
- `p=15,e_R=22`: `z=2,3,4,5,6,8`;
- `p=14,e_R=23`: `z=2,3,4,5,6,8`.

Status: VERIFIED finite row closure.

### V229. Terminal degree-sum scalar cut for two tight rows

GPT Pro suggested that two non-p19 rows in the V228 frontier should be removed
by a direct terminal degree-sum contradiction.  The argument was checked
independently and encoded into the scalar audit.

For the row

`(z,s1,s2,d,p,e_R,cap) = (2,6,6,0,17,20,74)`,

the local R-edge lower bound is tight:

- the two zero vertices have exactly two neighbours in `S1` and exactly two
  neighbours in `S2`;
- every singleton vertex has exactly two neighbours in the opposite singleton
  class;
- no extra `R`-edges are available.

Thus every one of the `14` R-vertices is C-tight.  Terminal normalization gives
degree `8` for each, so the R-degree sum would be `14*8=112`.  But the exact
degree sum from labels, A/B incidence, and R-edges is

`U + cap + 2e_R = 12 + 74 + 40 = 126`,

a contradiction.

For the row

`(z,s1,s2,d,p,e_R,cap) = (3,5,5,1,18,19,74)`,

the same tightness gives:

- every singleton vertex has exactly two neighbours in the opposite singleton
  class and is C-tight;
- every zero vertex has exactly one D-neighbour, one `S1`-neighbour, and one
  `S2`-neighbour, hence is C-tight to both colours;
- no extra zero-zero or singleton/zero slack is available.

The `13` non-D R-vertices therefore all have terminal degree `8`, contributing
`104` to the R-degree sum.  The exact total is

`U + cap + 2e_R = 12 + 74 + 38 = 124`,

so the unique D-vertex would need degree `20`.  However the D-vertex has at
most `2` C-neighbours, `3` zero-neighbours, and `12` A/B-neighbours, so its
degree is at most `17`.  Contradiction.

The scalar audit now includes this cut:

`search23/q14_t2_scalar_audit_post_v229.tsv`.

It reports `rows=39637` and cap74 frontier size `30`.

Status: VERIFIED scalar proof cut.

### V230. z6, p19/e_R18 slack-2 category certificate

The next p19 row tested was

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,19,18,74)`.

For this row, local domination and the p19 slack calculation give

`S12 = 4`

and

`ZZ + ZS1 + ZS2 + (ZD - 12) = 2`.

The restricted category manifest

`search23/z6_p19_e18_slack2_input.tsv`

contains `672` categories satisfying these equations.

The first triage run used the terminal/RR/exact-M solver at `10000`
conflicts with up to `100` workers:

`search23/z6_p19_e18_slack2_cat_10k/`.

It returned

`done=672/672`, `unsat=662`, `sat=0`, `unknown=10`, `na=0`,
`elapsedSec=518`.

The ten unknown categories were:

- `(0,0,0,14,4)`
- `(0,0,1,13,4)`
- `(0,0,2,12,4)`
- `(0,1,0,13,4)`
- `(0,1,1,12,4)`
- `(0,2,0,12,4)`
- `(1,0,0,13,4)`
- `(1,0,1,12,4)`
- `(1,1,0,12,4)`
- `(2,0,0,12,4)`

They were rerun at `1000000` conflicts in

`search23/z6_p19_e18_slack2_tail10_1m/`,

and all ten returned `SHAPE_FAMILY_STATUS 20`:

`done=10/10`, `unsat=10`, `sat=0`, `unknown=0`, `elapsedSec=77`.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v230.tsv`.

It reports `rows=39636` and cap74 frontier size `29`.

Status: VERIFIED finite row closure.

### V231. z4, p19/e_R18 slack-2 category/template certificate

The next p19 row tested was

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,19,18,74)`.

For this row, local domination gives `E_Z=ZS1+ZS2+ZD >= 8` and `S12 >= 8`.
Together with `e_R=18`, this leaves `306` slack-2 categories in

`search23/z4_p19_e18_slack2_input.tsv`.

The first triage run used the terminal/RR/exact-M solver at `10000`
conflicts with up to `100` workers:

`search23/z4_p19_e18_slack2_cat_10k/`.

It returned

`done=306/306`, `unsat=296`, `sat=0`, `unknown=10`, `na=0`,
`elapsedSec=121`.

The ten unknown categories were:

- `(0,0,0,8,10)`
- `(0,0,1,8,9)`
- `(0,0,2,8,8)`
- `(0,1,0,8,9)`
- `(0,1,1,7,9)`
- `(0,1,1,8,8)`
- `(0,1,2,7,8)`
- `(0,2,0,8,8)`
- `(0,2,1,7,8)`
- `(0,2,2,6,8)`

They were rerun at `1000000` conflicts in

`search23/z4_p19_e18_slack2_tail10_1m/`,

which returned

`done=10/10`, `unsat=9`, `sat=0`, `unknown=1`, `elapsedSec=374`.

The remaining category was

`(ZZ,ZS1,ZS2,ZD,S12) = (0,1,1,8,8)`.

It was split across all `9596` canonical p19 A-B templates:

`search23/z4_p19_e18_cat01188_p19templates_all_10k/`.

At `10000` conflicts and up to `100` workers, this returned

`done=9596/9596`, `unsat=9596`, `sat=0`, `unknown=0`,
`elapsedSec=334`.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v231.tsv`.

It reports `rows=39635` and cap74 frontier size `28`.

Status: VERIFIED finite row closure.

### V232. z5, p19/e_R18 slack-2 category/template certificate

The final p19 row tested was

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,19,18,74)`.

For this row, local domination gives `E_Z=ZS1+ZS2+ZD >= 10` and `S12 >= 6`.
Together with `e_R=18`, this leaves `445` slack-2 categories in

`search23/z5_p19_e18_slack2_input.tsv`.

The first triage run used the terminal/RR/exact-M solver at `10000`
conflicts with up to `100` workers:

`search23/z5_p19_e18_slack2_cat_10k/`.

It returned

`done=445/445`, `unsat=430`, `sat=0`, `unknown=15`, `na=0`,
`elapsedSec=347`.

The fifteen unknown categories were rerun at `1000000` conflicts in

`search23/z5_p19_e18_slack2_tail15_1m/`,

which returned

`done=15/15`, `unsat=7`, `sat=0`, `unknown=8`, `elapsedSec=256`.

The eight remaining categories were:

- `(0,0,1,10,7)`
- `(0,1,0,10,7)`
- `(0,1,1,9,7)`
- `(0,1,1,10,6)`
- `(0,1,2,9,6)`
- `(0,2,1,9,6)`
- `(0,2,2,8,6)`
- `(1,1,1,9,6)`

Each of these was split across all `9596` canonical p19 A-B templates, using
`10000` conflicts per template and `12` workers per category, i.e. `96`
workers total.  The output directories were:

- `search23/z5_p19_e18_cat001107_p19templates_10k/`
- `search23/z5_p19_e18_cat010107_p19templates_10k/`
- `search23/z5_p19_e18_cat01197_p19templates_10k/`
- `search23/z5_p19_e18_cat011106_p19templates_10k/`
- `search23/z5_p19_e18_cat01296_p19templates_10k/`
- `search23/z5_p19_e18_cat02196_p19templates_10k/`
- `search23/z5_p19_e18_cat02286_p19templates_10k/`
- `search23/z5_p19_e18_cat11196_p19templates_10k/`

Every directory returned

`done=9596/9596`, `unsat=9596`, `sat=0`, `unknown=0`.

The slowest wall time was `3980` seconds.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v232.tsv`.

It reports `rows=39634` and cap74 frontier size `27`.  There are no remaining
p19 rows.

Status: VERIFIED finite row closure.

### V233. z8, p18/e_R19 fixed-P template certificate

The first p18 row tested was

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,18,19,74)`.

The canonical p18 A-B templates were generated by

`search23/enumerate_p_templates.exe 18`.

This produced

`search23/p18_templates.tsv`

with `6973` canonical templates.

For the z8 row, local domination gives `ZD >= 16`; since `e_R=19`, the only
four categories are:

- `(ZZ,ZD)=(0,19)`
- `(ZZ,ZD)=(1,18)`
- `(ZZ,ZD)=(2,17)`
- `(ZZ,ZD)=(3,16)`

The category-only run

`search23/z8_p18_e19_cat4_10k/`

returned `UNKNOWN` for all four categories at `10000` conflicts.

Each category was then split across all `6973` canonical p18 A-B templates:

- `search23/z8_p18_e19_zz0_zd19_p18templates_10k/`
- `search23/z8_p18_e19_zz1_zd18_p18templates_10k/`
- `search23/z8_p18_e19_zz2_zd17_p18templates_10k/`
- `search23/z8_p18_e19_zz3_zd16_p18templates_10k/`

Every directory returned

`done=6973/6973`, `unsat=6973`, `sat=0`, `unknown=0`.

The slowest wall time was `1435` seconds.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v233.tsv`.

It reports `rows=39633` and cap74 frontier size `26`.

Status: VERIFIED finite row closure.

### V234. z2, p16/e_R21 scalar terminal-degree cut

The row

`(z,s1,s2,d,p,e_R,cap) = (2,6,6,0,16,21,74)`

is removed by a scalar terminal-degree contradiction.

Here `D` is empty.  Write

- `a = ZZ`,
- `b = ZS1`,
- `c = ZS2`,
- `x = S12`.

Local domination gives `b >= 4`, `c >= 4`, and `x >= 12`: each zero
needs at least two neighbours in each singleton class, and every singleton
needs at least two neighbours on the opposite singleton side.

Since `e_R = a + b + c + x = 21`, the slack equation is

`a + (b + c - 8) + (x - 12) = 1`.

There are three cases.

1. `a = 1`, `b + c = 8`, `x = 12`.

   All local lower bounds are tight.  Both zero vertices are C-tight to both
   colours, and every singleton is C-tight.  Thus all 14 vertices of `R` are
   terminal C-tight, hence have degree 8.  The R-degree sum would be `112`,
   but the exact sum is `U + cap + 2e_R = 12 + 74 + 42 = 128`.

2. `a = 0`, `b + c = 9`, `x = 12`.

   The 12 singleton vertices are C-tight.  Each zero still has at least two
   neighbours in each singleton colour and the total zero-singleton incidence
   count is 9, so each zero is tight to at least one colour.  Again all 14
   vertices of `R` are terminal C-tight, giving `112 < 128`.

3. `a = 0`, `b + c = 8`, `x = 13`.

   Both zero vertices are C-tight and contribute degree `8`.  On the
   `S1-S2` bipartite graph, 13 edges with minimum opposite degree at least 2
   force degree sequence `(3,2,2,2,2,2)` on each side.  Hence exactly ten
   singleton vertices are C-tight.  These ten singletons and the two zeros
   contribute `12 * 8 = 96` to the R-degree sum.

   The two remaining singletons have opposite-singleton degree `3`, at most
   two zero neighbours, label size `1`, and universal A/B state size at most
   `8`, so each has degree at most `1 + 3 + 2 + 8 = 14`.  Thus the total
   R-degree sum is at most `96 + 2 * 14 = 124`, again below the exact `128`.

This row is therefore impossible.

The scalar audit cut was added to
`search23/q14_t2_scalar_audit.cpp`; after recompilation,
`search23/q14_t2_scalar_audit_post_v234.tsv` reports `rows=39632` and
cap74 frontier size `25`.

Status: VERIFIED scalar row closure.

### V235. z6, p18/e_R19 fixed-P template certificate

The row

`(z,s1,s2,d,p,e_R,cap) = (6,2,2,4,18,19,74)`

is closed by the same terminal/RR/exact-M solver stack, followed by a split
over all canonical `p=18` A-B templates for the remaining tail categories.

For this row every singleton sees both vertices on the opposite singleton
side, so `S12=4`.  Also the p18 slack equation is

`ZZ + ZS1 + ZS2 + (ZD - 12) = 3`.

The restricted category manifest is

`search23/z6_p18_e19_slack3_input.tsv`.

It contains `796` categories.  The category run

`search23/z6_p18_e19_slack3_cat_10k/`

closed `776` categories at `10000` conflicts and left `20` UNKNOWN.

The tail rerun

`search23/z6_p18_e19_slack3_tail20_1m/`

closed `12` of those `20` categories at `1000000` conflicts and left `8`
UNKNOWN:

- `(0,0,2,13,4)`
- `(0,0,3,12,4)`
- `(0,1,2,12,4)`
- `(0,2,0,13,4)`
- `(0,2,1,12,4)`
- `(0,3,0,12,4)`
- `(1,0,2,12,4)`
- `(1,2,0,12,4)`

Each remaining category was then split over all `6973` canonical `p=18`
A-B templates:

- `search23/z6_p18_e19_cat002134_p18templates_10k/`
- `search23/z6_p18_e19_cat003124_p18templates_10k/`
- `search23/z6_p18_e19_cat012124_p18templates_10k/`
- `search23/z6_p18_e19_cat020134_p18templates_10k/`
- `search23/z6_p18_e19_cat021124_p18templates_10k/`
- `search23/z6_p18_e19_cat030124_p18templates_10k/`
- `search23/z6_p18_e19_cat102124_p18templates_10k/`
- `search23/z6_p18_e19_cat120124_p18templates_10k/`

Every directory returned

`done=6973/6973`, `unsat=6973`, `sat=0`, `unknown=0`.

The slowest wall time was `2948` seconds.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v235.tsv`.

It reports `rows=39631` and cap74 frontier size `24`.

Status: VERIFIED finite row closure.

### V236. z4, p18/e_R19 S12=8 degree-cover cut

For the row

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,18,19,74)`

the category solver left 16 tail categories after the `1M` rerun.  GPT Pro
suggested a degree-cover variable

`x(r) = 8 - m(r)`, where `m(r)` is the A/B-neighbourhood size of `r`.

Since `sum_R m(r)=cap=74`, the global identity is

`sum_R x(r) = 14*8 - 74 = 38`.

If `S12=8`, the `S1-S2` graph has `4+4` vertices, 8 edges, and minimum
opposite degree at least 2, so it is 2-regular.  Hence all eight singleton
vertices are C-tight.  For such a singleton `s`,

`x(s) = 1 + d_R(s) = 3 + d_Z(s)`.

Summing over the singleton vertices gives

`sum_{S1 union S2} x = 24 + ZS1 + ZS2`.

Thus the zero/doubleton block has remaining budget

`14 - ZS1 - ZS2`.

For the `S12=8` tail categories, this budget is exceeded by a small exact
zero/D minimization:

- zero vertices `z` have degrees `delta_z=d_D(z)`, `alpha_z=d_{S1}(z)`,
  `beta_z=d_{S2}(z)`;
- local domination imposes `delta_z + alpha_z >= 2` and
  `delta_z + beta_z >= 2`;
- if either inequality is tight, terminal normalization fixes
  `x(z)=d_R(z)=delta_z+alpha_z+beta_z`;
- every Z-D edge imposes the A/B edge-cover inequality `x(z)+x(d) >= 4`;
- non-tight zero vertices are allowed to choose any integral `x(z)>=0`.

The independent verifier

`search23/verify_z4_p18_s12_8_degree_cover.cpp`

enumerates all four-zero/two-D skeleton degree distributions and optimizes the
integer `x` variables.  Its output

`search23/verify_z4_p18_s12_8_degree_cover.tsv`

is:

```text
zs1	zs2	zd	s12	budget	min_zd_x	closed
0	3	8	8	11	15	yes
1	2	8	8	11	12	yes
1	3	7	8	10	15	yes
2	1	8	8	11	12	yes
2	2	7	8	10	12	yes
2	3	6	8	9	15	yes
3	0	8	8	11	15	yes
3	1	7	8	10	15	yes
3	2	6	8	9	15	yes
3	3	5	8	8	15	yes
```

Therefore all ten `S12=8` categories in the `z4,p18,e_R19` tail are closed
without A-B template enumeration.  The only remaining categories in this row
are the six `S12=9` categories:

- `(0,0,2,8,9)`
- `(0,1,1,8,9)`
- `(0,1,2,7,9)`
- `(0,2,0,8,9)`
- `(0,2,1,7,9)`
- `(0,2,2,6,9)`

Status: VERIFIED partial row cut.

### V237. z4, p18/e_R19 row closure

The row

`(z,s1,s2,d,p,e_R,cap) = (4,4,4,2,18,19,74)`

is now closed.

The p18 slack equation for this row is

`ZZ + (ZS1+ZS2+ZD - 8) + (S12 - 8) = 3`.

The restricted category manifest

`search23/z4_p18_e19_slack3_input.tsv`

contains `540` categories.  The category run

`search23/z4_p18_e19_slack3_cat_10k/`

returned

`done=540/540`, `unsat=519`, `sat=0`, `unknown=21`.

The tail rerun

`search23/z4_p18_e19_slack3_tail21_1m/`

returned

`done=21/21`, `unsat=5`, `sat=0`, `unknown=16`.

The verified degree-cover cut V236 closes the ten `S12=8` categories among
these 16 UNKNOWN categories.

The remaining six `S12=9` categories were split across all `6973` canonical
`p=18` A-B templates:

- `search23/z4_p18_e19_cat00289_s12_9_p18templates_t16_10k/`
- `search23/z4_p18_e19_cat01189_s12_9_p18templates_t16_10k/`
- `search23/z4_p18_e19_cat01279_s12_9_p18templates_t16_10k/`
- `search23/z4_p18_e19_cat02089_s12_9_p18templates_t16_10k/`
- `search23/z4_p18_e19_cat02179_s12_9_p18templates_t16_10k/`
- `search23/z4_p18_e19_cat02269_s12_9_p18templates_t16_10k/`

Every directory returned

`done=6973/6973`, `unsat=6973`, `sat=0`, `unknown=0`.

The slowest wall time was `2244` seconds.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v237.tsv`.

It reports `rows=39630` and cap74 frontier size `23`.

Status: VERIFIED finite row closure.

### V238. z5, p18/e_R19 raw category reduction and zero-defect cut

For

`(z,s1,s2,d,p,e_R,cap) = (5,3,3,3,18,19,74)`,

the p18 slack equation is

`ZZ + (ZS1+ZS2+ZD - 10) + (S12 - 6) = 3`.

The trusted raw category manifest

`search23/z5_p18_e19_slack3_input_raw.tsv`

contains `785` categories.  The raw category run

`search23/z5_p18_e19_slack3_raw785_cat_10k/`

returned

`done=785/785`, `unsat=750`, `sat=0`, `unknown=35`.

The tail rerun

`search23/z5_p18_e19_slack3_raw_tail35_1m/`

returned

`done=35/35`, `unsat=10`, `sat=0`, `unknown=25`.

The independent zero-defect skeleton verifier

`search23/verify_z5_p18_zero_defect_cut.cpp`

produced

`search23/verify_z5_p18_zero_defect_cut.tsv`

and closed 9 of these 25 remaining categories:

- `(0,1,3,9,6)`
- `(0,2,3,8,6)`
- `(0,3,1,9,6)`
- `(0,3,2,8,6)`
- `(0,3,3,7,6)`
- `(1,1,1,10,6)`
- `(1,1,2,9,6)`
- `(1,2,1,9,6)`
- `(1,2,2,8,6)`

The verifier uses only skeleton-local lower bounds for

`x(r) = 8 - |N_{A \cup B}(r)|`,

the R-edge inequality `x(u)+x(v) >= 4`, C-tight equalities, and exact
zero/singleton incidence enumeration.  It does not rely on the earlier
filtered p13-style z5 manifest.

Status: VERIFIED partial row cut; 16 categories remained for fixed-P splitting.

### V239. z5, p18/e_R19 row closure

The 16 categories not closed by V238 were split across all `6973` canonical
`p=18` A-B templates:

- `search23/z5_p18_e19_raw_cat001108_p18templates_t7_10k/`
- `search23/z5_p18_e19_raw_cat001117_p18templates_t7_10k/`
- `search23/z5_p18_e19_raw_cat002107_p18templates_t7_10k/`
- `search23/z5_p18_e19_raw_cat010108_p18templates_t7_10k/`
- `search23/z5_p18_e19_raw_cat010117_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat01198_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat011107_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat011116_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat01297_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat012106_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat020107_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat02197_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat021106_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat02287_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat02296_p18templates_t6_10k/`
- `search23/z5_p18_e19_raw_cat11197_p18templates_t6_10k/`

Every directory returned

`done=6973/6973`, `unsat=6973`, `sat=0`, `unknown=0`.

The combined fixed-P split therefore checked

`16 * 6973 = 111568`

template instances, all UNSAT.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v239.tsv`.

It reports `rows=39629`.  The cap74 frontier size is now `22`; the p18 layer is
fully closed.

Status: VERIFIED finite row closure.

### V240. z3, p17/e_R20 row closure

GPT Pro suggested a p17/e_R20 z3 reduction.  The independent verifier

`search23/verify_p17_z3_reduction.cpp`

checks the scalar/category part and the residual R-skeleton reduction.

For `(z,s_1,s_2,d,p,e_R,cap)=(3,5,5,1,17,20,74)`, local domination and
`ZD <= 3` leave exactly five scalar categories:

- `(0,3,3,3,11)`
- `(0,3,4,3,10)`
- `(0,4,3,3,10)`
- `(0,4,4,2,10)`
- `(1,3,3,3,10)`

The last four are eliminated by the C-tight x-budget
`sum_{r in R} (8-m_r)=38`.

The only scalar survivor is `(0,3,3,3,11)`.  The verifier found:

`core_labeled=432`, `core_orbits=2`,
`residual_labeled=241920`,
`pressure_survivors_labeled=8208`, and
`pressure_survivor_orbits=28`.

The GPT answer predicted 38 pressure survivor skeletons; the independent
canonical count is 28 under the label-preserving zero/low-singleton
permutation action used here.

The 28 survivor R-skeletons were emitted to

`search23/p17_z3_pressure_skeletons/`

and checked by

`search23/verify_p17_z3_pfree_ilp.py`.

The first CP-SAT pass, without non-tight R-degree lower bounds, closed 19 of
28 skeletons at 20s and 7 more at 180s; 2 remained unknown.  After adding the
valid lower bound

`m_r >= 8 - |label(r)| - d_R(r)`

for every R-vertex, the verifier returned:

`SUMMARY total=28 sat=0 unknown=0`

with all 28 skeletons `INFEASIBLE`.

The scalar audit now includes this row closure:

`search23/q14_t2_scalar_audit_post_v240.tsv`.

It reports `rows=39628`.  The cap74 frontier size is now `21`; the p17/e_R20
frontier has been reduced to `z in {4,5,6,8}`.

Status: VERIFIED finite row closure.

### V241. z8, p17/e_R20 P-free zero/D shortcut is insufficient

GPT Pro suggested a zero/D skeleton plus P-free exact-M cover certificate for
the remaining z8 row of the p17/e_R20 layer.  I implemented the category-level
necessary CP-SAT model in

`search23/verify_p17_z8_pfree_cpsat.py`.

The model uses only the R-skeleton variables, twelve independent A/B
neighbourhood rows, total `M=74`, degree lower bounds, terminal zero equalities
when `d_R(z,D)=2`, R-edge codegree zero, R-nonedge codegree at least two, and
D-visibility for every A/B row.  It deliberately omits the p17 A-B template,
rectangle two-cover, A/A, B/B, A/R, and B/R constraints, so infeasibility would
have closed the row before fixed-P enumeration.

The 60s / 4-worker run

`search23/verify_p17_z8_pfree_cpsat_60s.out`

returned SAT for all five z8 categories:

`(ZZ,ZD)=(0,20),(1,19),(2,18),(3,17),(4,16)`.

Thus the P-free zero/D shortcut alone is too weak for z8 p17/e_R20.  The active
fixed-P template certificates remain necessary for this row.

Status: VERIFIED negative shortcut result.

### V242. z6, p17/e_R20 category-level P-free shortcut is insufficient

I also tested the analogous category-level P-free CP-SAT model for the z6 row
of the p17/e_R20 layer, implemented in

`search23/verify_p17_z6_pfree_cpsat.py`.

The model hard-codes `S12=4`, i.e. `S_1-S_2=K_{2,2}`, uses only allowed
R-edge variables of types `ZZ`, `ZS1`, `ZS2`, and `ZD`, enforces local zero
domination, terminal equalities for the four forced C-tight singleton vertices
and for tight zeros, R-edge/R-nonedge codegree constraints, and twelve
independent A/B-neighbourhood rows with total `M=74`.

The streaming run

`search23/verify_p17_z6_pfree_cpsat_stream.out`

found SAT P-free models for several categories, e.g.
`(ZZ,ZS1,ZS2,ZD,S12)=(0,0,0,16,4)`, and UNKNOWNs for some harder categories.
It also proved a few categories infeasible, but the presence of SAT P-free
models means this shortcut cannot close the row by itself.  The z6 row still
requires the stronger RR/exact-M tail or a more P-aware certificate.

Status: VERIFIED partial/negative shortcut result.

### V243. z8, p17/e_R20 fixed-P template certificate

For the z8 row of the p17/e_R20 layer, local domination leaves exactly five
categories:

- `(ZZ,ZD)=(0,20)`
- `(ZZ,ZD)=(1,19)`
- `(ZZ,ZD)=(2,18)`
- `(ZZ,ZD)=(3,17)`
- `(ZZ,ZD)=(4,16)`

Each category was checked across the `3908` canonical p17 A-B templates with
the terminal/RR/exact-M solver:

- `search23/p17_e20_z8_cat000020_fixedp_10k/`: `3908/3908` UNSAT, SAT `0`,
  UNKNOWN `0`.
- `search23/p17_e20_z8_cat100019_fixedp_10k/`: `3908/3908` UNSAT, SAT `0`,
  UNKNOWN `0`.
- `search23/p17_e20_z8_cat200018_fixedp_10k/`: `3908/3908` UNSAT, SAT `0`,
  UNKNOWN `0`.
- `search23/p17_e20_z8_cat300017_fixedp_10k/`: `3908/3908` UNSAT, SAT `0`,
  UNKNOWN `0`.
- `search23/p17_e20_z8_cat400016_fixedp_10k/`: `3908/3908` UNSAT, SAT `0`,
  UNKNOWN `0`.

The scalar audit now includes this closure:

`search23/q14_t2_scalar_audit_post_v243.tsv`.

It reports `openRows=39627`, with cap74 frontier size `20`.  The p17/e_R20
frontier is now reduced to

`z in {4,5,6}`.

Status: VERIFIED finite row closure.

### V244. z6, p17/e_R20 category `(0,3,0,13,4)` fixed-P closure

The z6 row of the p17/e_R20 layer has tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(0,3,0,13,4)`.

The first fixed-P run

`search23/p17_e20_z6_cat030134_fixedp_10k/status.tsv`

closed `3716` of the `3908` canonical p17 A-B templates, all UNSAT.  The
remaining `192` template indices were rerun in

`search23/p17_e20_z6_cat030134_fixedp_missing872_1063_10k/status.tsv`.

An independent union check over the two status files gave

`unique=3908 dups=0 missing=0 bad=0`.

Therefore this category is closed: `3908/3908` UNSAT, SAT `0`, UNKNOWN `0`.

Status: VERIFIED finite category closure.

### V245. z6, p17/e_R20 category `(0,0,4,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(0,0,4,12,4)`

was checked across all `3908` canonical p17 A-B templates by the
terminal/RR/exact-M solver:

`search23/p17_e20_z6_cat004124_fixedp_10k_clean/status.tsv`.

The run finished with

`done=3908/3908 unsat=3908 sat=0 unknown=0 na=0`.

Status: VERIFIED finite category closure.

### V246. z6, p17/e_R20 categories `(0,1,2,13,4)` and `(0,1,3,12,4)`

Two further z6 p17/e_R20 tail categories were checked across all `3908`
canonical p17 A-B templates:

- `(ZZ,ZS1,ZS2,ZD,S12)=(0,1,2,13,4)` via
  `search23/p17_e20_z6_cat012134_fixedp_10k/status.tsv`.
- `(ZZ,ZS1,ZS2,ZD,S12)=(0,1,3,12,4)` via
  `search23/p17_e20_z6_cat013124_fixedp_10k/status.tsv`.

For both status files, the verification count is

`lines=3908 uniqueTemplates=3908 missing=0 codes=20:3908`.

Thus both categories are closed: SAT `0`, UNKNOWN `0`, NA `0`.

Status: VERIFIED finite category closure.

### V247. z6, p17/e_R20 category `(0,4,0,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(0,4,0,12,4)`

was first checked in

`search23/p17_e20_z6_cat040124_fixedp_10k/status.tsv`,

which closed `3426` of `3908` p17 templates.  The missing contiguous template
block `340..821` was rerun with `pwsh` in

`search23/p17_e20_z6_cat040124_fixedp_missing340_821_10k_pwsh/status.tsv`,

closing the remaining `482` templates.

The union check over the two status files gave

`unique=3908 dups=0 missing=0 bad=0`.

Therefore this category is closed: `3908/3908` UNSAT, SAT `0`, UNKNOWN `0`.

Status: VERIFIED finite category closure.

### V248. z6, p17/e_R20 category `(1,0,2,13,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(1,0,2,13,4)`

was checked across all `3908` canonical p17 A-B templates:

`search23/p17_e20_z6_cat102134_fixedp_10k/status.tsv`.

The independent status audit gave

`lines=3908 uniqueTemplates=3908 missing=0 codes=20:3908`.

Thus the category is closed: SAT `0`, UNKNOWN `0`, NA `0`.

Status: VERIFIED finite category closure.

### V249. z6, p17/e_R20 category `(1,0,3,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(1,0,3,12,4)`

was checked across all `3908` canonical p17 A-B templates:

`search23/p17_e20_z6_cat103124_fixedp_10k/status.tsv`.

The status audit gave

`lines=3908 uniqueTemplates=3908 missing=0 codes=20:3908`.

Thus the category is closed: SAT `0`, UNKNOWN `0`, NA `0`.

Status: VERIFIED finite category closure.

### V250. z6, p17/e_R20 category `(1,1,2,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(1,1,2,12,4)`

was checked across all `3908` canonical p17 A-B templates:

`search23/p17_e20_z6_cat112124_fixedp_10k/status.tsv`.

The run finished with

`done=3908/3908 unsat=3908 sat=0 unknown=0 na=0`.

Status: VERIFIED finite category closure.

### V251. z6, p17/e_R20 category `(1,2,0,13,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(1,2,0,13,4)`

was checked across all `3908` canonical p17 A-B templates:

`search23/p17_e20_z6_cat120134_fixedp_10k/status.tsv`.

The run finished with

`done=3908/3908 unsat=3908 sat=0 unknown=0 na=0`.

Status: VERIFIED finite category closure.

### V252. z6, p17/e_R20 categories `(1,2,1,12,4)` and `(1,3,0,12,4)`

Two further z6 p17/e_R20 tail categories were checked across all `3908`
canonical p17 A-B templates:

- `(ZZ,ZS1,ZS2,ZD,S12)=(1,2,1,12,4)` via
  `search23/p17_e20_z6_cat121124_fixedp_10k/status.tsv`.
- `(ZZ,ZS1,ZS2,ZD,S12)=(1,3,0,12,4)` via
  `search23/p17_e20_z6_cat130124_fixedp_10k/status.tsv`.

Both completed with

`done=3908/3908 unsat=3908 sat=0 unknown=0 na=0`.

Status: VERIFIED finite category closure.

### V252. z6, p17/e_R20 categories `(1,2,1,12,4)` and `(1,3,0,12,4)`

Two further z6 p17/e_R20 tail categories were checked across all `3908`
canonical p17 A-B templates:

- `(ZZ,ZS1,ZS2,ZD,S12)=(1,2,1,12,4)`:
  `search23/p17_e20_z6_cat121124_fixedp_10k/status.tsv`.
- `(ZZ,ZS1,ZS2,ZD,S12)=(1,3,0,12,4)`:
  `search23/p17_e20_z6_cat130124_fixedp_10k/status.tsv`.

Both runs finished with

`done=3908/3908 unsat=3908 sat=0 unknown=0 na=0`.

Status: VERIFIED finite category closures.

### V253. z6, p17/e_R20 category `(2,0,2,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(2,0,2,12,4)`

was checked by combining the initial partial run

`search23/p17_e20_z6_cat202124_fixedp_10k/`

with the non-overlapping tail run

`search23/p17_e20_z6_cat202124_fixedp_tail2666_3907_10k/`.

The union over all `status_*.txt` files gave

`unique=3908 dups=0 missing=0 bad=0`.

Therefore this category is closed: `3908/3908` UNSAT, SAT `0`, UNKNOWN `0`.

Status: VERIFIED finite category closure.

### V254. z6, p17/e_R20 category `(0,3,1,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(0,3,1,12,4)`

was closed by combining three runs:

- `search23/p17_e20_z6_cat031124_fixedp_clean_10k/`,
- `search23/p17_e20_z6_cat031124_fixedp_tail1941_3907_10k/`,
- `search23/p17_e20_z6_cat031124_fixedp_gap1881_1886_10k/`.

The original run had six killed/NA templates, `1881..1886`; the gap run
checked exactly those six and returned UNSAT for all of them.  The final union
check gave

`covered=3908 dups=1242 missing=0 noUnsat=0`.

Thus every canonical p17 A-B template has at least one UNSAT certificate for
this category.  SAT `0`, uncovered templates `0`.

Status: VERIFIED finite category closure.

### V255. z6, p17/e_R20 category `(2,2,0,12,4)` fixed-P closure

The z6 p17/e_R20 tail category

`(ZZ,ZS1,ZS2,ZD,S12)=(2,2,0,12,4)`

was closed by combining three runs:

- `search23/p17_e20_z6_cat220124_fixedp_clean_10k/`,
- `search23/p17_e20_z6_cat220124_fixedp_tail1130_3907_10k/`,
- `search23/p17_e20_z6_cat220124_fixedp_gap1090_1094_10k/`.

The original clean run had five killed/NA templates, `1090..1094`; the gap run
checked those five and returned UNSAT for all of them.  The final union check
gave

`covered=3908 dups=1356 missing=0 noUnsat=0`.

Thus every canonical p17 A-B template has at least one UNSAT certificate for
this category.  SAT `0`, uncovered templates `0`.

Status: VERIFIED finite category closure.

### V256. z6, p17/e_R20 row closed and scalar frontier after V255

The initial z6 p17/e_R20 RR tail left exactly 19 UNKNOWN categories:

`search23/p17_e20_z6_rr_tail35_1m/status.tsv`.

The category-closure audit compared those 19 categories with the closures
recorded in V244--V255 and returned

`unknownCount=19 closedCount=19 missingClosures=0 extraClosures=0`.

The scalar audit now includes the z6 p17/e_R20 row closure:

`search23/q14_t2_scalar_audit_post_v255.tsv`.

It reports

`rows=39626 cap74=19`.

The remaining cap74 frontier by `(p,e_R)` is:

- `(14,23)`: 6 rows,
- `(15,22)`: 6 rows,
- `(16,21)`: 5 rows,
- `(17,20)`: 2 rows.

The remaining p17/e_R20 rows are only

- `z=4,s1=4,s2=4,d=2`,
- `z=5,s1=3,s2=3,d=3`.

Status: VERIFIED finite row closure.

### V257. z4 and z5 close the p17/e_R20 cap74 frontier

After V256 the only remaining `p=17,e_R=20,cap=74` scalar rows were

- `z=4,s1=4,s2=4,d=2`,
- `z=5,s1=3,s2=3,d=3`.

GPT Pro suggested additional row-specific category cuts.  I checked the safe
category cuts independently in C++:

- `search23/verify_p17_z4_z5_category_cuts.cpp`,
- output `search23/p17_z4_z5_category_cuts_audit.tsv`.

The audit confirms:

- in the z4 `S12=8` slice, 25 of the 35 category literals are eliminated by
  the hand boundary cut, leaving the listed 10 residual literals;
- in the z5 row, the matching/`S12=6` boundary cuts eliminate the listed 12
  category literals.

The remaining category tails were then checked by the robust terminal/RR/
exact-M category solver:

- `search23/p17_e20_z4_rr_cat_tail_filtered_v257_robust45_10k`:
  `3010/3010` status files, all `20=UNSAT`, with `sat=0`, `unknown=0`,
  `na=0`;
- `search23/p17_e20_z5_rr_cat_tail_filtered_v257_robust50_10k`:
  `5284/5284` status files, all `20=UNSAT`, with `sat=0`, `unknown=0`,
  `na=0`.

An independent status audit over both directories found no missing or duplicate
status files and no non-UNSAT status.  Therefore the full `p=17,e_R=20`
cap74 layer is closed.

The scalar audit was updated accordingly and rerun:

- `search23/q14_t2_scalar_audit_post_v257.tsv`.

The remaining cap74 frontier is now 17 rows:

- `(p,e_R)=(16,21)`: 5 rows,
- `(p,e_R)=(15,22)`: 6 rows,
- `(p,e_R)=(14,23)`: 6 rows.

All remaining cap74 rows have `U=12`; the p17/e_R20 layer is gone.

Status: VERIFIED finite row closure.

### V258. z8 p16/e_R21 dirty `(ZZ,ZD)=(1,20)` complementary endpoint branch closed

For the active p16/e_R21 z8 row, the dirty one-ZZ category
`(ZZ,ZD)=(1,20)` was attacked by the P-free dirty projection verifier

`search23/dirty_z8_projection_audit.py`.

The branch fixed the dirty ZZ endpoints to the complementary degree-3 rows

`4:{8,9,10}` and `5:{11,12,13}`.

This is the broad complementary `(3,3)` endpoint skeleton that had previously
returned `UNKNOWN` without touching-footprint branching.

The touched-footprint split is now fully closed:

- size 6: `search23/p16_z8_1_20_dirty_fixed_size4_masks.out` plus protocol
  log records the size-6 test as `INFEASIBLE sec=0.432`;
- size 5: `search23/p16_z8_1_20_dirty_fixed_size5_masks.out`, all `6/6`
  masks `INFEASIBLE`;
- size 4: `search23/p16_z8_1_20_dirty_fixed_size4_masks.out`,
  `search23/p16_z8_1_20_dirty_fixed_size4_remaining.out`, and
  `PROGRESS_CODEX.md`, all `15/15` masks `INFEASIBLE`;
- size 3: `search23/p16_z8_1_20_dirty_fixed_size3_masks.out`, all `20/20`
  masks `INFEASIBLE`;
- size 2: `search23/p16_z8_1_20_dirty_fixed_size2_masks.out`, all `15/15`
  masks `INFEASIBLE`;
- size 1: `search23/p16_z8_1_20_dirty_fixed_size1_masks.out`, all `6/6`
  masks `INFEASIBLE`.

Thus this complementary degree-3 dirty endpoint branch of `(ZZ,ZD)=(1,20)`
is closed by the P-free projection certificate, using the dirty touched-column
equalities, dirty footprint capacity cut, zero/D local codegree, and the
total-pair reroot cap.  This is not yet the full `(ZZ,ZD)=(1,20)` category:
the remaining dirty endpoint row types still have to be split and certified.

Status: VERIFIED branch closure.

### V259. z8 p16/e_R21 exact `u3_422` residual capacity cut

GPT Pro identified a short P-free contradiction for the exact `u3_422`
residual in the already closed `(ZZ,ZD)=(0,21)` category.  The branch has

- tight rows `{8,10}^2` and `{9,10}^2`;
- non-tight rows `{8,9,12}`, `{8,9,12,13}`, and `{11,12,13}^2`;
- pair excesses `E_{8,10}=E_{9,10}=0`.

In this branch the saturated columns `8,9,10` each have exactly two A/B
vertices.  The two `{11,12,13}` zero rows force the `S_8` and `S_9` vertices
to have singleton D-state and five R-neighbours, just as the existing
saturated-column cuts force for `S_10`.  The six vertices in
`S_8 union S_9 union S_10` contribute exactly `30` A/B-to-R incidences, while
every remaining A/B vertex contributes at most `7`, hence `M <= 72`,
contradicting the cap74 equality `M=74`.

I checked the branch by running the main verifier with exact row counts,
`--pair-excesses 8:10=0,9:10=0`, `--u3-422-e00-cuts`, `--h4-misses 11`,
and the branch-local cut `--ab-rdeg-max 72`:

`cat=(0,21) INFEASIBLE status=3 sec=1.733`.

Status: VERIFIED branch cut.

### V260. z8 p16/e_R21 dirty `(ZZ,ZD)=(1,20)` endpoint pair `(2,2)` closed

Continuing V258, the next dirty endpoint type in zero-D degree profile
`(4,4,0,0)` has the unique zero-zero edge joining two degree-2 zeros.  By
symmetry this is represented by

`0:{8,9}` and `1:{10,11}`.

The broad projection audit timed out, so the branch was split by touched
footprint.  The size-6 footprint and the two size-5 footprints are directly
closed in

`search23/p16_z8_1_20_zdeg4400_zzpair22_footprints.out`:

- `{8,9,10,11,12,13}`: `INFEASIBLE sec=0.426`;
- `{8,9,10,11,12}`: `INFEASIBLE sec=166.068`;
- `{8,9,10,11,13}`: `INFEASIBLE sec=176.690`.

The remaining footprint is `{8,9,10,11}`.  There the two non-dirty degree-2
rows were split by row2 multiset.  All row2 multisets except the symmetric
hard multiset closed directly in

`search23/p16_z8_1_20_zdeg4400_pair22_row2splits.out`.

The only hard multiset is

`{8,9}^2, {10,11}^2`,

encoded as

`--row2-counts-all 2,0,0,0,0,0,0,0,0,2,0,0,0,0,0`.

GPT Pro suggested a P-free zero-skeleton projection certificate, saved at

`problems/23/gpt_answer_p16_z8_zzpair22_projection_2026-06-17.md`.

I added `--min-m` support to

`search23/dirty_z8_projection_audit.py`

and wrote the parallel leaf driver

`search23/run_pair22_row3_cert.py`.

For the hard row2 multiset, the row3 skeleton search has `1082` possible
multisets after the touched-column load filter.  The 100-way driver

`python search23/run_pair22_row3_cert.py --workers 100 --timeout 60 --out search23/p16_z8_1_20_pair22_row3_cert.tsv`

reports

`FINAL done=1082 bad=0 elapsed=132.5s`.

Each leaf imposes `Mproj >= 67` in the P-free `N[S,U]` projection and returns
`INFEASIBLE`; hence every hard-row2 skeleton has `Mproj <= 66`, contradicting
the cap74 requirement `M=74`.  Therefore the `(2,2)` dirty endpoint branch of
`(ZZ,ZD)=(1,20)`, degree profile `(4,4,0,0)`, is closed.

Status: VERIFIED branch closure.

### V261. p16/e_R21 z8 `(ZZ,ZD)=(1,20)`, degree profile `(4,4,0,0)`: dirty endpoint pair `(2,3)` branch closed

Target branch:

- `(ZZ,ZD)=(1,20)`;
- zero-D degree profile `(4,4,0,0)`;
- the unique `ZZ` edge joins a degree-2 zero and a degree-3 zero.

By column symmetry fix the dirty endpoint rows as

`0:{8,9}` and `4:{10,11,12}`.

I added the deterministic footprint driver

`search23/run_pair23_footprint_cert.py`.

It runs the P-free projection audit

`search23/dirty_z8_projection_audit.py`

over all 16 tight-footprint masks containing `{8,9}`.  If projection returns a
SAT/OPTIMAL zero skeleton, the driver extracts the row-count vectors and lifts
that leaf to

`search23/verify_p16_z8_pfree_exact_ab_cpsat.py`

with `--zz-degree-pair 2:3`.

The run

`python search23/run_pair23_footprint_cert.py --workers 100 --projection-timeout 180 --main-timeout 180 --out search23/p16_z8_1_20_pair23_footprint_cert.tsv`

reports

`FINAL done=16 bad=0 elapsed=1851.7s`.

The only projection SAT footprints were `{8,9}` and `{8,9,13}`; both lift to
main-verifier `SUMMARY total=6 sat=0 unknown=0`.  The other 14 footprints are
projection-level `INFEASIBLE`.  Therefore the `(2,3)` dirty endpoint branch of
`(ZZ,ZD)=(1,20)`, degree profile `(4,4,0,0)`, is closed.

Status: VERIFIED branch closure.

### V262. p16/e_R21 z8 `(ZZ,ZD)=(1,20)`, degree profile `(4,4,0,0)` closed

For `(ZZ,ZD)=(1,20)` with zero-D degree profile `(4,4,0,0)`, the unique
zero-zero edge can have endpoint degree pair `(2,2)`, `(2,3)`, or `(3,3)`.

The three branches are closed as follows:

- `(3,3)`: V258;
- `(2,2)`: V260;
- `(2,3)`: V261.

These cases exhaust the profile.  Therefore the full `(4,4,0,0)` degree profile
inside the p16/e_R21 z8 dirty `(ZZ,ZD)=(1,20)` category is closed.

Status: VERIFIED profile closure.

### V263. p16/e_R21 z8 `(ZZ,ZD)=(1,20)`, degree profile `(6,0,2,0)` closed

For `(ZZ,ZD)=(1,20)` with zero-D degree profile `(6,0,2,0)`, the unique
zero-zero edge can only join disjoint endpoint rows of degrees `(2,2)` or
`(2,4)`.

Both endpoint branches close directly in the P-free dirty projection verifier:

- `(2,4)`, represented by `0:{8,9}` and `6:{10,11,12,13}`:
  `search23/p16_z8_1_20_zdeg6020_pair24_broad.out` reports
  `status INFEASIBLE sec 39.674`;
- `(2,2)`, represented by `0:{8,9}` and `1:{10,11}`:
  `search23/p16_z8_1_20_zdeg6020_pair22_broad.out` reports
  `status INFEASIBLE sec 7.491`.

These cases exhaust the profile.  Therefore the full `(6,0,2,0)` degree profile
inside the p16/e_R21 z8 dirty `(ZZ,ZD)=(1,20)` category is closed.

Status: VERIFIED profile closure.

### V264. p16/e_R21 z8 `(ZZ,ZD)=(1,20)`, degree profile `(6,1,0,1)` closed

For `(ZZ,ZD)=(1,20)` with zero-D degree profile `(6,1,0,1)`, the unique
zero-zero edge can only join disjoint endpoint rows of degrees `(2,2)` or
`(2,3)`.  A degree-5 zero cannot be incident to the zero-zero edge because its
D-row cannot be disjoint from another row of size at least 2.

Both endpoint branches close directly in the P-free dirty projection verifier:

- `(2,3)`, represented by `0:{8,9}` and `6:{10,11,12}`:
  `search23/p16_z8_1_20_zdeg6101_pair23_broad.out` reports
  `status INFEASIBLE sec 13.969`;
- `(2,2)`, represented by `0:{8,9}` and `1:{10,11}`:
  `search23/p16_z8_1_20_zdeg6101_pair22_broad.out` reports
  `status INFEASIBLE sec 0.794`.

These cases exhaust the profile.  Therefore the full `(6,1,0,1)` degree profile
inside the p16/e_R21 z8 dirty `(ZZ,ZD)=(1,20)` category is closed.

Status: VERIFIED profile closure.

### V265. p16/e_R21 z8 `(ZZ,ZD)=(1,20)`, degree profile `(5,2,1,0)` closed

For `(ZZ,ZD)=(1,20)` with zero-D degree profile `(5,2,1,0)`, the unique
zero-zero edge can only join disjoint endpoint rows of degrees `(2,2)`,
`(2,3)`, `(2,4)`, or `(3,3)`.

All four endpoint branches close directly in the P-free dirty projection
verifier:

- `(2,4)`, represented by `0:{8,9}` and `7:{10,11,12,13}`:
  `search23/p16_z8_1_20_zdeg5210_pair24_broad.out` reports
  `status INFEASIBLE sec 272.886`;
- `(3,3)`, represented by `5:{8,9,10}` and `6:{11,12,13}`:
  `search23/p16_z8_1_20_zdeg5210_pair33_broad.out` reports
  `status INFEASIBLE sec 82.942`;
- `(2,3)`, represented by `0:{8,9}` and `5:{10,11,12}`:
  `search23/p16_z8_1_20_zdeg5210_pair23_broad.out` reports
  `status INFEASIBLE sec 212.470`;
- `(2,2)`, represented by `0:{8,9}` and `1:{10,11}`:
  `search23/p16_z8_1_20_zdeg5210_pair22_broad.out` reports
  `status INFEASIBLE sec 99.082`.

These cases exhaust the profile.  Therefore the full `(5,2,1,0)` degree profile
inside the p16/e_R21 z8 dirty `(ZZ,ZD)=(1,20)` category is closed.

Status: VERIFIED profile closure.

### V266. p16/e_R21 z8 dirty `(ZZ,ZD)=(1,20)` category closed

For the p16/e_R21 z8 dirty category `(ZZ,ZD)=(1,20)`, zero-D degrees sum to
`20`, every zero has degree at least `2`, and the no-all-D-neighbour rule
excludes degree `6`.  Therefore the possible zero-D degree profiles are exactly

- `(4,4,0,0)`,
- `(5,2,1,0)`,
- `(6,0,2,0)`,
- `(6,1,0,1)`,

where the tuple counts degree-2, degree-3, degree-4, and degree-5 zeros.

These profiles are closed as follows:

- `(4,4,0,0)`: V262;
- `(6,0,2,0)`: V263;
- `(6,1,0,1)`: V264;
- `(5,2,1,0)`: V265.

Thus the full `(ZZ,ZD)=(1,20)` category in the p16/e_R21 z8 cap74 row is
closed.

Status: VERIFIED category closure.

### V267. p16/e_R21 z8 `(ZZ,ZD)=(2,19)`, degree profile `(7,0,0,1)` closed

For `(ZZ,ZD)=(2,19)` with zero-D degree profile `(7,0,0,1)`, the two zero-zero
edges can only use degree-2 zeros.  Up to graph isomorphism there are two
two-edge zero-zero skeletons: two disjoint edges and a path of length two.

I added multi-edge skeleton fixing to the P-free dirty projection verifier:

`search23/dirty_z8_projection_audit.py --fix-zz-edges`.

Both skeleton types close directly:

- disjoint edges `0:1|2:3`:
  `search23/p16_z8_2_19_zdeg7001_disjointZZ_broad.out` reports
  `status INFEASIBLE sec 76.363`;
- path `0:1|0:2`:
  `search23/p16_z8_2_19_zdeg7001_pathZZ_broad.out` reports
  `status INFEASIBLE sec 105.460`.

These cases exhaust the profile.  Therefore the full `(7,0,0,1)` degree profile
inside the p16/e_R21 z8 category `(ZZ,ZD)=(2,19)` is closed.

Status: VERIFIED profile closure.

### V268. p16/e_R21 z8 `(ZZ,ZD)=(2,19)`, degree profile `(6,1,1,0)` closed

For `(ZZ,ZD)=(2,19)` with zero-D degree profile `(6,1,1,0)`, a broad
projection run timed out, so the two zero-zero edges were split by endpoint
degree skeleton and then by incident zero-D rows.

The all-`(2,2)` endpoint skeletons were split first:

- the two fixed-edge broad skeleton probes
  `search23/p16_z8_2_19_zdeg6110_22_22_disjoint.out` and
  `search23/p16_z8_2_19_zdeg6110_22_22_path.out` both returned
  `status UNKNOWN` at 120s;
- after fixing incident rows, the driver
  `search23/run_cat219_zdeg6110_22_splits.py` checked `66` leaves and reports
  `FINAL done=66 bad=0 elapsed=29.7s`.

The remaining mixed endpoint skeletons were then split by incident rows:

- `22+23` disjoint skeleton:
  `search23/run_cat219_zdeg6110_2223_disjoint_rows.py` checks `60` leaves and
  reports `FINAL done=60 bad=0 elapsed=12.8s`;
- the other mixed skeletons:
  `search23/run_cat219_zdeg6110_remaining_row_splits.py` checks `71` leaves and
  reports `FINAL done=71 bad=0 elapsed=49.3s`.

Every leaf is projection-level `INFEASIBLE`.  The skeleton list covers
`22+22`, `22+23`, `22+24`, `23+23`, `24+24`, and `23+24`, with both disjoint
and path forms where possible.  Therefore the full `(6,1,1,0)` degree profile
inside the p16/e_R21 z8 category `(ZZ,ZD)=(2,19)` is closed.

Status: VERIFIED profile closure.

### V269. p16/e_R21 z8 `(ZZ,ZD)=(2,19)`, degree profile `(5,3,0,0)` closed

For `(ZZ,ZD)=(2,19)` with zero-D degree profile `(5,3,0,0)`, a broad
projection run timed out, so the two zero-zero edges were split by endpoint
degree skeleton and incident zero-D rows.

The all-`(2,2)` endpoint skeletons close by the parameterized row-split driver

`python search23/run_cat219_zdeg6110_22_splits.py --zdeg-counts 5,3,0,0 --workers 100 --timeout 90 --out search23/p16_z8_2_19_zdeg5300_22_splits.tsv`,

which reports

`FINAL done=66 bad=0 elapsed=64.5s`.

The `22+23` disjoint skeleton closes by

`python search23/run_cat219_zdeg6110_2223_disjoint_rows.py --zdeg-counts 5,3,0,0 --workers 100 --timeout 90 --out search23/p16_z8_2_19_zdeg5300_2223_disjoint_rows.tsv`,

which reports

`FINAL done=60 bad=0 elapsed=14.4s`.

The remaining skeletons were checked by

`python search23/run_cat219_zdeg5300_remaining_row_splits.py --workers 100 --timeout 90 --out search23/p16_z8_2_19_zdeg5300_remaining_row_splits.tsv`.

This projection-level split checked `790` leaves.  It closed `765` directly and
left `25` projection-UNKNOWN leaves, all in the symmetric `23+23 path` and
`33+33 path` families.  These 25 leaves lift to the stronger exact A/B-state
main verifier via

`python search23/run_cat219_zdeg5300_bad_lifts.py --workers 25 --timeout 180 --out search23/p16_z8_2_19_zdeg5300_bad_lifts.tsv`,

which reports

`FINAL done=25 bad=0 elapsed=2.2s`.

Therefore every row-split leaf is infeasible, either at projection level or at
the main verifier level.  This closes the full `(5,3,0,0)` degree profile inside
the p16/e_R21 z8 category `(ZZ,ZD)=(2,19)`.

Status: VERIFIED profile closure.

### V270. p16/e_R21 z8 `(ZZ,ZD)=(2,19)` category closed

For the p16/e_R21 z8 category `(ZZ,ZD)=(2,19)`, zero-D degrees sum to `19`,
every zero has degree at least `2`, and the no-all-D-neighbour rule excludes
degree `6`.  Therefore the possible zero-D degree profiles are exactly

- `(7,0,0,1)`,
- `(6,1,1,0)`,
- `(5,3,0,0)`.

These are closed in V267, V268, and V269 respectively.  Thus the full
`(ZZ,ZD)=(2,19)` category in the p16/e_R21 z8 cap74 row is closed.

Status: VERIFIED category closure.

### V271. p16/e_R21 z8 `(ZZ,ZD)=(3,18)` category closed

For the p16/e_R21 z8 category `(ZZ,ZD)=(3,18)`, zero-D degrees sum to `18`,
every zero has degree at least `2`, and the no-all-D-neighbour rule excludes
degree `6`.  Therefore the possible zero-D degree profiles are exactly

- `(7,0,1,0)`,
- `(6,2,0,0)`.

A graph-type split over the three zero-zero edges gives 12 colour-respecting
zero-graph orbits for `(7,0,1,0)` and 25 such orbits for `(6,2,0,0)`.
After fixing the unique high row by D-symmetry (`z7={10,11,12,13}` in
`(7,0,1,0)`, and `z6={8,9,10}` in `(6,2,0,0)`), the dirty projection verifier
closed 17 of these 37 graph-type leaves:

- `search23/p16_z8_3_18_graph_types_canonhigh.tsv`.

The remaining 20 graph-type leaves were lifted to the exact P-free A/B verifier.
This closed 15 leaves:

- `search23/p16_z8_3_18_exact_bad_lifts.tsv`.

The last 5 leaves all belonged to the `(6,2,0,0)` profile.  In those leaves, the
second degree-3 zero row was split by its intersection size with the fixed row
`{8,9,10}`.  The four representatives are
`{11,12,13}`, `{8,11,12}`, `{8,9,11}`, and `{8,9,10}`.  The exact P-free A/B
verifier closed all 20 resulting leaves:

- `search23/p16_z8_3_18_z7row_lifts.tsv`, `FINAL done=20 bad=0`.

Thus the full `(ZZ,ZD)=(3,18)` category in the p16/e_R21 z8 cap74 row is closed.

Status: VERIFIED category closure.

### V272. p16/e_R21 z8 `(ZZ,ZD)=(4,17)` category closed

For the p16/e_R21 z8 category `(ZZ,ZD)=(4,17)`, zero-D degrees sum to `17`.
Since every zero has D-degree at least `2`, the only possible zero-D degree
profile is `(7,1,0,0)`.

The unique degree-3 zero row was fixed by D-symmetry as `{8,9,10}`.  A
colour-respecting graph-type split over the four zero-zero edges gives 30
triangle-free zero-graph orbits.  The dirty projection verifier closed every
one of these leaves:

- `search23/p16_z8_4_17_graph_types.tsv`, `FINAL done=30 bad=0`.

Thus the full `(ZZ,ZD)=(4,17)` category in the p16/e_R21 z8 cap74 row is closed.

Status: VERIFIED category closure.

### V273. p16/e_R21 z8 `(ZZ,ZD)=(5,16)` category closed

For the p16/e_R21 z8 category `(ZZ,ZD)=(5,16)`, zero-D degrees sum to `16`.
Since every zero has D-degree at least `2`, the only possible zero-D degree
profile is `(8,0,0,0)`.

All zeros have D-degree `2`.  A colour-respecting graph-type split over the
five zero-zero edges gives 17 triangle-free zero-graph orbits.  For each orbit,
one zero-zero edge was fixed by zero symmetry, and its two endpoint D-rows were
fixed by D-symmetry as `{8,9}` and `{10,11}`.  The dirty projection verifier
closed every resulting leaf:

- `search23/p16_z8_5_16_graph_types.tsv`, `FINAL done=17 bad=0`.

Thus the full `(ZZ,ZD)=(5,16)` category in the p16/e_R21 z8 cap74 row is closed.

Status: VERIFIED category closure.

### V274. p16/e_R21 z8 row closed

In the p16/e_R21 z8 cap74 row, the possible category values are

- `(ZZ,ZD)=(0,21)`,
- `(ZZ,ZD)=(1,20)`,
- `(ZZ,ZD)=(2,19)`,
- `(ZZ,ZD)=(3,18)`,
- `(ZZ,ZD)=(4,17)`,
- `(ZZ,ZD)=(5,16)`.

The clean `(0,21)` category was previously closed by the z8 p16 clean-row
certificate.  The dirty categories are closed as follows:

- `(1,20)`: V266,
- `(2,19)`: V270,
- `(3,18)`: V271,
- `(4,17)`: V272,
- `(5,16)`: V273.

Therefore the p16/e_R21 z8 cap74 row is closed.

Status: VERIFIED row closure.

### V275. p16/e_R21 z3 induced A/B verifier closes six live categories

For the p16/e_R21 z3 cap74 row, the category manifest
`search23/p16_e21_z3_category_manifest.tsv` contains 15 categories.  The old
R/R rooted-cut run `search23/p16_e21_z3_cat_rr_10k/status.tsv` closed the five
categories with `ZZ>0` at solver status `20`.

For the remaining ten `ZZ=0` categories, I added the induced A/B state verifier
`search23/verify_p16_z3_induced_ab_cpsat.py`.  This verifier uses the exact
P-free A/B law: an A/B pair is an edge iff the two A/B vertices have disjoint
R-neighbourhoods, forbids common R-count `1`, imposes exactly `p=16` A/B
edges, and checks local R/R, A/R, B/R, A/A, B/B codegrees plus all cap74
rooted Phi/Psi cuts.

The run

`python search23/verify_p16_z3_induced_ab_cpsat.py --timeout 300 --workers-per-cat 10 --parallel-cats 10`

wrote `search23/p16_z3_induced_10x300.out` and closed six categories:

- `(0,3,5,3,10)`,
- `(0,4,4,3,10)`,
- `(0,4,5,2,10)`,
- `(0,5,3,3,10)`,
- `(0,5,4,2,10)`,
- `(0,5,5,1,10)`.

The same run left four categories UNKNOWN, with no SAT witness:

- `(0,3,3,3,12)`,
- `(0,3,4,3,11)`,
- `(0,4,3,3,11)`,
- `(0,4,4,2,11)`.

Status: VERIFIED finite closure for six categories; four residual categories
passed to V276.

### V276. Terminal-touch closure closes the four p16/e_R21 z3 residuals

Terminal-touch lemma used: if a vertex is terminal C-tight to colour `i`, then
each of its two R-neighbours inside the corresponding `U_i` reroots onto the
same cap74 equality layer and therefore has original degree exactly `8`.  This
is the same terminal-reroot closure principle used earlier for touched
doubleton columns in the z8 row.

In verifier form this adds the following conditional degree-8 equalities:

- if a zero `z` satisfies `d_D(z)+d_S1(z)=2`, then every adjacent vertex in
  `D union S1` has `m+rdeg+|label|=8`;
- if `d_D(z)+d_S2(z)=2`, then every adjacent vertex in `D union S2` has
  `m+rdeg+|label|=8`;
- if a singleton has opposite-singleton R-degree `2`, then each opposite
  singleton adjacent to it has `m+rdeg+1=8`.

After adding these constraints to
`search23/verify_p16_z3_induced_ab_cpsat.py`, the residual run

`python search23/verify_p16_z3_induced_ab_cpsat.py --timeout 180 --workers-per-cat 25 --parallel-cats 4 --only "0:3:3:3:12,0:3:4:3:11,0:4:3:3:11,0:4:4:2:11"`

wrote `search23/p16_z3_induced_touch_rem4_4x25.out` and reports all four
residual categories INFEASIBLE:

- `(0,3,3,3,12)`: `sec=146.136`;
- `(0,3,4,3,11)`: `sec=82.284`;
- `(0,4,3,3,11)`: `sec=65.323`;
- `(0,4,4,2,11)`: `sec=70.548`.

Status: VERIFIED finite closure for the four residual categories.

### V277. p16/e_R21 z3 row closed

The p16/e_R21 z3 cap74 row has 15 category literals:

- five `ZZ>0` categories closed by
  `search23/p16_e21_z3_cat_rr_10k/status.tsv`;
- six `ZZ=0`, `S12=10` categories closed in V275;
- four residual `ZZ=0`, `S12=11,12` categories closed in V276.

Therefore the full p16/e_R21 z3 cap74 row is closed.

Status: VERIFIED row closure.

### V278. p16/e_R21 z6 induced A/B verifier closes 44 categories

For the p16/e_R21 z6 cap74 row, `S12=4` is forced, so the two singleton
classes form `K_{2,2}`.  I adapted the z3 induced-A/B verifier to
`search23/verify_p16_z6_induced_ab_cpsat.py`.  The verifier uses:

- the exact induced A/B edge law;
- full R/R, A/R, B/R, A/A, B/B local codegree constraints;
- terminal-touch closure;
- root-to-R side visibility and explicit D-visibility for every A/B state;
- cap74 rooted Phi/Psi cuts;
- aggregate R-edge capacity `m_u+m_v <= 12`;
- the touched-D visibility cap for tight-zero-touched D columns.

The runs

`python search23/verify_p16_z6_induced_ab_cpsat.py --timeout 120 --workers-per-cat 10 --parallel-cats 10`

`python search23/verify_p16_z6_induced_ab_cpsat.py --timeout 300 --workers-per-cat 10 --parallel-cats 10 --only <27 residual categories>`

and

`python search23/verify_p16_z6_induced_ab_cpsat.py --timeout 180 --workers-per-cat 10 --parallel-cats 10 --only <14 residual categories>`

wrote:

- `search23/p16_z6_induced_touch_54x120.out`: `27 INFEASIBLE`, `27 UNKNOWN`;
- `search23/p16_z6_induced_touch_res27_10x300.out`: `13 INFEASIBLE`, `14 UNKNOWN`;
- `search23/p16_z6_induced_capacity_res14_10x180.out`: `4 INFEASIBLE`, `10 UNKNOWN`.

Together these induced-A/B checks close `44` of the `54` z6 categories, with
no SAT category found.

Status: VERIFIED finite closure for 44 categories.

### V279. p16/e_R21 z6 skeleton+m certificate closes the final 10 categories

The final z6 categories after V278 were:

- `(0,2,1,14,4)`;
- `(0,1,3,13,4)`;
- `(0,2,3,12,4)`;
- `(0,2,2,13,4)`;
- `(1,1,1,14,4)`;
- `(0,3,1,13,4)`;
- `(0,1,2,14,4)`;
- `(1,1,2,13,4)`;
- `(1,2,1,13,4)`;
- `(1,2,2,12,4)`.

These close without fixed A/B templates.  The checker
`search23/verify_p16_z6_skeleton_m_cpsat.py` uses only the R-skeleton and
the A/B incidence counts `m_r`, with:

- R triangle-freeness and the category counts;
- zero domination `d_D(z)+d_S1(z)>=2`, `d_D(z)+d_S2(z)>=2`;
- degree lower bounds `m_r+|label(r)|+d_R(r)>=8`;
- singleton exactness, since `S1-S2=K_{2,2}`;
- terminal-touch degree-8 equalities;
- R-edge capacity `m_u+m_v<=12`;
- the touched-D visibility cap;
- the cap equation `sum_r m_r=74`.

The run

`python search23/verify_p16_z6_skeleton_m_cpsat.py --timeout 20 --workers-per-cat 4 --parallel-cats 10`

wrote `search23/p16_z6_skeleton_m_res10.out` and reports:

`SUMMARY total=10 sat=0 unknown=0`.

All ten categories are INFEASIBLE in this P-free skeleton+m model.

Status: VERIFIED P-free finite closure for the final ten categories.

### V280. p16/e_R21 z6 row closed

The p16/e_R21 z6 cap74 row has `54` category literals.  V278 closes `44`,
and V279 closes the remaining `10`.  Therefore the full p16/e_R21 z6 cap74
row is closed.

Status: VERIFIED row closure.

### V281. p16/e_R21 z4 skeleton+m certificate closes 63 tail categories

For the p16/e_R21 z4 cap74 row, the old R/R rooted-cut tail file
`search23/p16_e21_z4_tail_unknown_status_input.tsv` contains `65` categories.

The P-free skeleton+m checker
`search23/verify_p16_z4_skeleton_m_cpsat.py` uses only the R-skeleton and
the A/B incidence counts `m_r`, with:

- R triangle-freeness and category counts;
- zero domination `d_D(z)+d_S1(z)>=2`, `d_D(z)+d_S2(z)>=2`;
- singleton opposite-degree lower bound at least `2`;
- degree lower bounds `m_r+|label(r)|+d_R(r)>=8`;
- terminal-touch degree-8 equalities for tight zeros and tight singletons;
- R-edge capacity `m_u+m_v<=12`;
- the touched-D visibility cap;
- the cap equation `sum_r m_r=74`.

The run

`python search23/verify_p16_z4_skeleton_m_cpsat.py --timeout 20 --workers-per-cat 4 --parallel-cats 10`

wrote `search23/p16_z4_skeleton_m_tail65.out` and reports:

`SUMMARY total=65 sat=2 unknown=0`.

The only two skeleton-feasible categories are:

- `(0,0,1,8,12)`;
- `(0,1,0,8,12)`.

Thus the skeleton+m certificate closes the other `63` z4 tail categories.

Status: VERIFIED P-free finite closure for 63 categories.

### V282. p16/e_R21 z4 induced A/B verifier closes the two residuals

The z4 induced-A/B verifier
`search23/verify_p16_z4_induced_ab_cpsat.py` extends the z4 skeleton+m cuts
with:

- independent A/B states in R;
- root-colour visibility through `U1=S1 union D` and `U2=S2 union D`;
- root-to-R side visibility;
- exact induced A/B edge law, with common R-neighbour count `1` forbidden;
- total `p=16`;
- full R/R, A/R, B/R, A/A, B/B local codegree constraints;
- cap74 rooted Phi/Psi cuts.

The run

`python search23/verify_p16_z4_induced_ab_cpsat.py --timeout 300 --workers-per-cat 20 --parallel-cats 2 --only "0:0:1:8:12,0:1:0:8:12"`

wrote `search23/p16_z4_induced_two_2x20_300.out` and reports:

- `(0,1,0,8,12)`: INFEASIBLE in `sec=59.868`;
- `(0,0,1,8,12)`: INFEASIBLE in `sec=66.794`.

Status: VERIFIED finite closure for the two residual categories.

### V283. p16/e_R21 z4 row closed

The p16/e_R21 z4 cap74 row tail has `65` categories after the old R/R
rooted-cut pass.  V281 closes `63`, and V282 closes the remaining `2`.
Therefore the full p16/e_R21 z4 cap74 row is closed.

Status: VERIFIED row closure.

### V284. p16/e_R21 z5 skeleton+m certificate closes 108 tail categories

For the p16/e_R21 z5 cap74 row, the old R/R rooted-cut tail file
`search23/p16_e21_z5_tail_unknown_status_input.tsv` contains `113` categories.

The P-free skeleton+m checker
`search23/verify_p16_z5_skeleton_m_cpsat.py` uses the same R-skeleton and
`m_r` capacity constraints as V281, with z5 blocks
`|Z|=5`, `|S1|=|S2|=3`, `|D|=3`.

The run

`python search23/verify_p16_z5_skeleton_m_cpsat.py --timeout 20 --workers-per-cat 4 --parallel-cats 10`

wrote `search23/p16_z5_skeleton_m_tail123.out` and reports:

`SUMMARY total=113 sat=5 unknown=0`.

The five skeleton-feasible categories are:

- `(0,0,0,15,6)`;
- `(0,0,2,10,9)`;
- `(0,1,1,10,9)`;
- `(0,1,1,13,6)`;
- `(0,2,0,10,9)`.

Thus the skeleton+m certificate closes the other `108` z5 tail categories.

Status: VERIFIED P-free finite closure for 108 categories.

### V285. p16/e_R21 z5 induced A/B verifier closes the five residuals

The z5 induced-A/B verifier
`search23/verify_p16_z5_induced_ab_cpsat.py` extends the z5 skeleton+m cuts
with exact induced A/B states, the total `p=16` edge law, local codegrees, and
cap74 rooted Phi/Psi cuts.

The run

`python search23/verify_p16_z5_induced_ab_cpsat.py --timeout 300 --workers-per-cat 20 --parallel-cats 5 --only "0:0:0:15:6,0:0:2:10:9,0:1:1:10:9,0:1:1:13:6,0:2:0:10:9"`

wrote `search23/p16_z5_induced_five_5x20_300.out` and reports:

- `(0,2,0,10,9)`: INFEASIBLE in `sec=46.981`;
- `(0,0,2,10,9)`: INFEASIBLE in `sec=50.633`;
- `(0,1,1,10,9)`: INFEASIBLE in `sec=53.745`;
- `(0,1,1,13,6)`: INFEASIBLE in `sec=61.440`;
- `(0,0,0,15,6)`: INFEASIBLE in `sec=170.161`.

Status: VERIFIED finite closure for the five residual categories.

### V286. p16/e_R21 layer closed

The p16/e_R21 cap74 layer consists of the z8, z3, z6, z4, and z5 rows.
These are closed by:

- z8: V274;
- z3: V277;
- z6: V280;
- z4: V283;
- z5: V285.

Therefore the full `(p,e_R)=(16,21)` cap74 layer is closed.

Status: VERIFIED layer closure.

### V287. p15/e_R22 z8 final two-ZZ residual closed

The final z8 residual in the p15/e_R22 cap74 layer was
`(ZZ,ZD)=(2,20)` with zero D-degree profile `4,4,0,0`.

The optimized two-ZZ skeleton enumerator
`search23/p15_z8_enum_twozz_4_4_fast.cpp` was compiled and run as:

`search23/p15_z8_enum_twozz_4_4_fast.exe search23/p15_z8_skeleton_twozz_n4_4_fast`

It generated:

- star ZZ orbit `0:1|0:2`: `4166` canonical skeleton keys;
- matching ZZ orbit `0:1|2:3`: `2951` canonical skeleton keys.

The P-free skeleton count verifier
`search23/verify_p15_z8_skeleton_count.py` then reported:

- `search23/p15_z8_twozz_n4_4_fast_star_count.out`:
  `SUMMARY infeasible=4161 sat=5 unknown=0 max_states=522`;
- `search23/p15_z8_twozz_n4_4_fast_matching_count.out`:
  `SUMMARY infeasible=2950 sat=1 unknown=0 max_states=506`.

The six skeleton survivors are recorded in
`search23/p15_z8_twozz_n4_4_fast_survivors.tsv`.

Each survivor was checked by
`search23/verify_p15_z8_pfree_exact_ab_cpsat.py` with fixed zero rows and
fixed ZZ edges.  The exact verifier wrote
`search23/p15_z8_twozz_n4_4_fast_exact/` and reported `INFEASIBLE` with
`unknown=0` for all six survivors:

- `star_107228272816600.out`;
- `star_125099563561180.out`;
- `star_147090215547100.out`;
- `star_147433819484380.out`;
- `star_151831865995484.out`;
- `matching_75950293574734.out`.

Status: VERIFIED finite closure for the final p15/e_R22 z8 residual.

### V288. p15/e_R22 layer closed

The p15/e_R22 cap74 layer consists of the z8, z2, z3, z4, z5, and z6 rows.
The earlier z2, z3, z4, z5, and z6 closures were already part of the p15
frontier reduction.  The remaining z8 row is closed by V287.

Therefore the full `(p,e_R)=(15,22)` cap74 layer is closed.

Status: VERIFIED layer closure.

### V289. p14/e_R23 z2 row closed

The p14/e_R23 z2 row has parameters
`z=2`, `s1=s2=6`, `d=0`, `U=12`, `M=74`, and `e_R=23`.

The terminal-touch exact-M solver
`search23/sat_q14_t2_shape_family_terminal_touch_dr_rr_exactm_aonly.exe`
was run on the generated manifest
`search23/p14_e23_z2_manifest.tsv`.

The run wrote `search23/q14_t2_cap74_p14_z2_touch_exactm_1m/` and reports:

`END ... done=16/16 unsat=14 sat=0 unknown=2 na=0`.

The two 1M-conflict UNKNOWN categories are:

- `(ZZ,ZS1,ZS2,ZD,S12)=(0,4,4,0,15)`;
- `(ZZ,ZS1,ZS2,ZD,S12)=(0,5,5,0,13)`.

They are closed by the following excess argument.  For every `r in R`, define

`eps(r) = m_r + d_R(r) + |label(r)| - 8 >= 0`.

Since `|R|=14`, `U=12`, `M=74`, and `e_R=23`,

`sum_R eps(r) = M + 2e_R + U - 8|R| = 74 + 46 + 12 - 112 = 20`.

Every C-tight or terminal-touched vertex has `eps=0`.

For `(0,4,4,0,15)`, each zero has exactly two neighbours in each singleton
class, hence both zeros are C-tight on both colours and have `eps=0`.
Any singleton with positive excess must have opposite-singleton degree at
least `3` and no zero neighbour.  On each singleton side the degree sum is
`15` with minimum degree `2`, so the total opposite degree over high
vertices on one side is at most `9`.  Therefore the total possible singleton
excess is at most `18`, and the zeros add no excess.  This contradicts the
required total excess `20`.

For `(0,5,5,0,13)`, the singleton-side degree sequence is
`(3,2,2,2,2,2)` on each side.  Degree-2 singletons are C-tight.  The unique
degree-3 singleton on either side has at least two degree-2 neighbours on
the opposite side, so it is terminal-touched and has `eps=0`.  Thus all
singletons have `eps=0`.  The two zero degrees into each singleton side are
`{2,3}`; hence at most one zero can be non-C-tight, and such a zero has
`d_R=6`, so `eps <= m_z+6-8 <= 5` because `m_z <= 7` in the p14 layer.
This again contradicts the required total excess `20`.

Status: VERIFIED hybrid finite/scalar closure for the p14/e_R23 z2 row.

### V290. p14/e_R23 z3 row closed by terminal-touch excess plus zero-rectangle

The p14/e_R23 z3 row has 68 category literals in
`search23/p14_e23_z3_manifest.tsv`.  The terminal-touch SAT worker
`search23/sat_q14_t2_shape_family_terminal_touch_dr_rr_exactm_aonly.exe`
proved all `ZZ>=1` literals UNSAT within the 1M-conflict category run
`search23/q14_t2_cap74_p14_z3_touch_exactm_1m/`: summary
`done=68/68, unsat=42, sat=0, unknown=26`.

The 26 UNKNOWN literals are exactly the `ZZ=0` categories.  For these,
`search23/p14_z3_excess_bound.py` maximizes the safe upper bound for
`sum eps`, where `eps(r)=m_r+d_R(r)+|label(r)|-8`.  It includes:

- local domination;
- terminal-touch exactness (`eps=0` for C-tight or terminal-touched
  vertices);
- singleton C-tightness;
- the zero-rectangle triangle-free cut
  `zs1(z,s)+zs2(z,t)+s12(s,t) <= 2`.

The rerun
`search23/p14_z3_excess_bound_triangle_dump.out` proves every `ZZ=0`
category has excess bound `< 20`; the formerly sharp symmetric residuals
`(0,3,4,3,13)` and `(0,4,3,3,13)` drop to bound `17`.  Since the p14/e_R23
layer requires `sum eps = 20`, all `ZZ=0` categories are impossible.

The human-readable reason for the last two residuals is as follows.  In
`(0,3,4,3,13)`, every zero is adjacent to the unique D-vertex; every zero is
C-tight on the singleton side with three zero edges, and the two light zeros
are also C-tight on the side with four zero edges.  Hence all zeros, D, and
all terminal-touched singleton neighbours have `eps=0`.  A positive-excess
singleton must therefore have opposite-singleton degree 3 and all its
opposite neighbours must also be degree-3 vertices; on the thin side it has
no zero neighbour, and on the thick side it can only use the heavy zero.  Thus
if `P` singleton vertices have positive excess, their total excess is at most
`3P+2`.  If `P=6`, the high singletons induce `K_{3,3}` and the two low
vertices on each side induce `K_{2,2}`.  A light zero must meet one low vertex
on each side, creating a forbidden R-triangle through that `K_{2,2}` edge.
So `P<=5`, hence `sum eps <= 17`, contradicting `sum eps=20`.  The
`(0,4,3,3,13)` row is symmetric.

Status: VERIFIED hybrid finite/scalar closure for the p14/e_R23 z3 row.

### V291. p14/e_R23 z8 high-ZZ categories closed by skeleton excess

For z8 in the p14/e_R23 cap74 layer, the manifest has exactly eight category
literals `(ZZ,ZD)=(0,23),(1,22),...,(7,16)`.

The skeleton-only excess checker
`search23/p14_z8_excess_bound.py` uses:

- local zero domination `d_D(z)>=2`;
- triangle-freeness of the zero graph;
- `ZZ` endpoints have disjoint D-neighbourhoods;
- terminal-touch exactness for D-columns touched by degree-2 zeros;
- the p14 upper bound `m_r<=7`;
- the global excess target `sum eps=20`.

The run `search23/p14_z8_excess_bound.out` proves:

- `(ZZ,ZD)=(5,18)` has upper bound `19`;
- `(ZZ,ZD)=(6,17)` has upper bound `15`;
- `(ZZ,ZD)=(7,16)` has upper bound `2`.

Hence these three z8 categories are impossible.  The remaining z8 residual is
`(ZZ,ZD)=(0,23),(1,22),(2,21),(3,20),(4,19)`.

Status: VERIFIED partial z8 category closure.

### V292. p14/e_R23 z8 `(ZZ,ZD)=(4,19)` closed by P-free exact A/B verifier

The p14/e_R23 z8 residual after V291 included `(ZZ,ZD)=(4,19)`.
The P-free exact A/B verifier
`search23/verify_p15_z8_pfree_exact_ab_cpsat.py` was run with `--p 14 --eR 23
--only 4:19 --timeout 300 --workers 20 --rooted-mode full`.

Output file:

- `search23/p14_z8_pfree_exact_4_19_300s.out`: `INFEASIBLE` in `54.6s`.

This verifier uses the z8 R-skeleton, exact A/B state law, full local codegree
constraints, exact cap `M=74`, rooted cuts, and no fixed A/B template
enumeration.

Thus z8 is reduced to:

`(ZZ,ZD)=(0,23),(1,22),(2,21),(3,20)`.

Status: VERIFIED finite closure for the `(4,19)` z8 category.

### V293. p14/e_R23 z6 row closed

The p14/e_R23 z6 row has parameters

`(z,s1,s2,d,p,e_R,cap)=(6,2,2,4,14,23,74)`.

Here `S12=4` is forced, so the singleton core is `K_{2,2}`.  The skeleton
excess checker

`search23/p14_z6_excess_bound.py`

uses:

- zero local domination;
- `K_{2,2}` zero-rectangle exclusion, so zeros cannot touch both singleton
  sides;
- triangle-free R-skeleton constraints;
- terminal-touch exactness;
- the p14 bound `m_r <= 7`;
- exact cap `sum m_r=74`.

The corrected run

- `search23/p14_z6_excess_bound_fixed.out`

reports `closed=194, open=10` over the 204 category literals.

The terminal-touch exact-M SAT worker

- `search23/q14_t2_cap74_p14_z6_touch_exactm_1m/`

closed all skeleton-open categories except the two symmetric residuals

- `(ZZ,ZS1,ZS2,ZD,S12)=(0,1,2,16,4)`;
- `(ZZ,ZS1,ZS2,ZD,S12)=(0,2,1,16,4)`.

The exact induced A/B verifier

`search23/verify_p16_z6_induced_ab_cpsat.py`

was parameterized by `--p` and `--eR` and run on these two residual categories:

`python search23/verify_p16_z6_induced_ab_cpsat.py --p 14 --eR 23 --timeout 600 --workers-per-cat 20 --parallel-cats 2 --only "0:1:2:16:4,0:2:1:16:4"`

Output:

- `search23/p14_z6_induced_res2_2x20_600.out`: both categories
  `INFEASIBLE` (`309.9s`, `310.1s`), `sat=0`, `unknown=0`.

Therefore the full p14/e_R23 z6 cap74 row is closed.

Status: VERIFIED hybrid finite/scalar closure for the p14/e_R23 z6 row.

### V294. p14/e_R23 z4 row closed

The p14/e_R23 z4 row has parameters

`(z,s1,s2,d,p,e_R,cap)=(4,4,4,2,14,23,74)`.

The z4 skeleton+m verifier

`search23/verify_p16_z4_skeleton_m_cpsat.py`

was parameterized by `--manifest` and `--max-m`.  The run

`python search23/verify_p16_z4_skeleton_m_cpsat.py --manifest search23/p14_e23_z4_manifest.tsv --timeout 20 --workers-per-cat 4 --parallel-cats 25`

wrote `search23/p14_z4_skeleton_m_all_25x4_20.out` and reports:

- `total=329`;
- `sat=8`;
- `unknown=1`;
- all other categories `INFEASIBLE`.

The exact induced A/B verifier

`search23/verify_p16_z4_induced_ab_cpsat.py`

was parameterized by `--p`, `--eR`, `--manifest`, and `--max-m`.  The run

`python search23/verify_p16_z4_induced_ab_cpsat.py --p 14 --eR 23 --timeout 600 --workers-per-cat 10 --parallel-cats 9 --only "...nine residual categories..."`

wrote `search23/p14_z4_induced_res9_9x10_600.out` and closes eight of the
nine residuals as `INFEASIBLE`.

The remaining category

`(ZZ,ZS1,ZS2,ZD,S12)=(0,3,3,6,11)`

was rerun in the skeleton verifier:

`python search23/verify_p16_z4_skeleton_m_cpsat.py --timeout 300 --workers-per-cat 100 --parallel-cats 1 --only 0:3:3:6:11`

Output:

- `search23/p14_z4_skeleton_res1_1x100_300.out`: `INFEASIBLE`.

Therefore the full p14/e_R23 z4 cap74 row is closed.

Status: VERIFIED hybrid finite/scalar closure for the p14/e_R23 z4 row.

### V295. p14/e_R23 z5 row closed

The p14/e_R23 z5 row has parameters

`(z,s1,s2,d,p,e_R,cap)=(5,3,3,3,14,23,74)`.

The z5 skeleton+m verifier

`search23/verify_p16_z5_skeleton_m_cpsat.py`

was parameterized by `--manifest` and `--max-m`.  The run

`python search23/verify_p16_z5_skeleton_m_cpsat.py --manifest search23/p14_e23_z5_manifest.tsv --timeout 20 --workers-per-cat 4 --parallel-cats 25`

wrote `search23/p14_z5_skeleton_m_all_25x4_20.out` and reports:

- `total=485`;
- `sat=18`;
- `unknown=0`;
- all other categories `INFEASIBLE`.

The exact induced A/B verifier

`search23/verify_p16_z5_induced_ab_cpsat.py`

was parameterized by `--p`, `--eR`, `--manifest`, and `--max-m`, and includes a
canonical `S12=6` representative for the unique `K_{3,3}` minus perfect
matching singleton core.  The run

`python search23/verify_p16_z5_induced_ab_cpsat.py --p 14 --eR 23 --timeout 600 --workers-per-cat 10 --parallel-cats 10 --only "...eighteen residual categories..."`

wrote `search23/p14_z5_induced_res18_10x10_600.out` and closes seventeen of
the eighteen residuals as `INFEASIBLE`.

The sole remaining category is

`(ZZ,ZS1,ZS2,ZD,S12)=(0,2,2,13,6)`.

It is impossible by the following P-free argument.

Because `S12=6` and every singleton has opposite degree at least `2`, every
singleton has opposite degree exactly `2`; hence every singleton is C-tight.
For each singleton `s`,

`m_s + d_R(s) + 1 = 8`.

Since `d_R(s)=2+d_Z(s)` and `ZS1+ZS2=4`,

`sum_{s in S1 union S2} m_s = 6*5 - 4 = 26`.

Thus the zero/D part must contribute

`M_ZD = 74 - 26 = 48`.                                      (1)

The D-degree deficit of the five zeros is `15-ZD=2`, so the zero D-degree
profile is either `(1,3,3,3,3)` or `(2,2,3,3,3)`.

If a zero has D-degree `1`, local domination and the matching-complement
singleton core force it to have exactly one neighbour on each singleton side,
so it is C-tight on both sides and has `m_z=5`.  Its unique D-neighbour is then
terminal-touched and has zero-degree `5`, so `m_d=1`.  If `q` is the largest
`m` among the four full-D zeros, then the other two D-columns are adjacent to
all four of those zeros, giving `m_d'<=12-q` and `m_d''<=12-q`.  Since
`q<=7`,

`M_ZD <= 5+1+4q+2(12-q) <= 44`,

contradicting (1).

So the profile is `(2,2,3,3,3)`.  If one D-degree-2 zero is C-tight, its two
D-neighbours are terminal-touched.  Each is adjacent to that zero and to the
three full-D zeros, so each has zero-degree at least `4` and hence `m_d<=2`.
The C-tight zero has `m_z<=6`; the other D-degree-2 zero has `m<=7`; the three
full-D zeros have total `m<=21`; and the remaining D-column has `m<=7`.  Hence

`M_ZD <= 6+7+21+2+2+7 = 45`,

again contradicting (1).

Therefore no zero is C-tight.  The structure is forced: two D-degree-2 zeros
each touch exactly one missing singleton pair, and three zeros touch all three
D-columns.

Now classify an arbitrary A/B state `I` by `r=|I cap D|`.

- If `r=0`, root visibility forces exactly one missing singleton pair, so
  `|I|<=7`; states of size at least `6` are zero-large.
- If `r=3`, no zero can lie in `I`, and `|I|<=6`; equality is a D-large state
  consisting of all three D-columns plus all three singletons on one side.
- If `r=2`, no zero can lie in `I`, so `|I|<=5`.
- If `r=1`, no full-D zero can lie in `I`, at most the two mixed zeros can lie
  in `I`, and the remaining singleton part has size at most `2`, so `|I|<=5`.

Since the twelve A/B states have total size `M=74`, at least seven states have
size at least `6`.  Both the A-side and B-side contain a large state.

A zero-large state and an opposite-side D-large state intersect in exactly one
singleton, contradicting the exact A/B law (`|X_i cap Y_j|=1` is forbidden).
Thus all large states have the same type.  They cannot all be D-large, because
D-large states have size at most `6`, giving total size at most `72`.  Hence all
large states are zero-large.

Let `L` be the number of large states.  Zero-large states contain no D-column,
so the five D-columns of `M_ZD=48` can only be carried by the `12-L` small
states:

`M_D <= 3(12-L)`.

Thus

`M_Z = 48-M_D >= 12+3L`.

But each of the five zeros has `m_z<=7`, so `12+3L<=35`, hence `L<=7`.  Since
also `L>=7`, we have `L=7`, and equality in

`74 <= 7L + 5(12-L)`

forces seven size-7 zero-large states and five size-5 small states.  Every
size-7 zero-large state contains all five zeros, so all zeros already have
`m_z=7` and no small state contains a zero.  Therefore `M_D=13`.

A size-5 small state with no zero has either:

- all three D-columns plus two singletons; or
- two D-columns plus all three singletons on one side.

If `n_3` is the number of small states with all three D-columns, then

`3 n_3 + 2(5-n_3) = 13`,

so `n_3=3`.  Thus two small states contain all three singletons on one side.
The opposite side contains a zero-large state, since seven large states cannot
all lie on one side.  Such a small state and that zero-large state intersect in
exactly one singleton, again forbidden by the exact A/B law.

Contradiction.  Hence `(0,2,2,13,6)` is impossible, and the full p14/e_R23 z5
row is closed.

Status: VERIFIED rigorous-informal closure for the p14/e_R23 z5 row.

## V296. p14/e_R23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 2 branch

Status: VERIFIED finite closure of the touched-count 2 subbranch.

Target subbranch:

- q14/t=2 cap74, `(p,e_R)=(14,23)`;
- z8 row, category `(ZZ,ZD)=(3,20)`;
- zero D-degree profile `(2^4,3^4)`, encoded as zdeg counts `(4,4,0,0)`;
- exactly two D-columns touched by degree-2 tight zeros.

Certificate structure:

1. Enumerated canonical touched-count 2 zero/D skeleton representatives with
   touched columns fixed as `8,9`.  The four degree-2 zeros use `{8,9}`; the
   four degree-3 zeros use triples among the other four D-columns; `ZZ=3`.
   This gives 117 canonical skeleton representatives:

   `search23/p14_z8_touch2_orbits.tsv`.

2. Projection-filtered all 117 representatives by the P-free z8 projection
   audit, using the D-column cover constraints from
   `search23/verify_p15_z8_pfree_exact_ab_cpsat.py`.  Result:

   - 116 representatives INFEASIBLE;
   - 1 representative SAT at projection level.

   Results:

   `search23/p14_z8_touch2_projection_filter.tsv`.

3. The sole projection survivor is representative `idx=3`, with rows

   `0:8,9|1:8,9|2:8,9|3:8,9|4:10,12,13|5:10,12,13|6:10,12,13|7:10,12,13`

   and `ZZ` star edges

   `0:4|1:4|2:4`.

   Running the full exact P-free A/B verifier on this fixed skeleton gives
   INFEASIBLE:

   `search23/p14_z8_touch2_projection_idx3_full.out`

   with summary `cat=(3,20) INFEASIBLE status=3 sec=63.056`.

Conclusion:

The `(3,20)`, zdeg `(4,4,0,0)`, touched-count 2 branch has no model.  The
remaining z8 frontier still includes touched-count 3 and 4 subbranches of the
same zdeg profile, plus the other z8 categories until separately closed.

Independent P-free proof:

In the touched-count 2 branch the four tight zeros all use the same D-pair
`F={a,b}`.  The two touched columns are saturated, so

`c_a=c_b=4` and `m_a=m_b=2`.

Let `H` be the four non-tight degree-3 zeros and let `U=D\F`.  Every zero in
`H` avoids `a,b` and chooses a 3-subset of `U`.  No two tight zeros are
ZZ-adjacent, and no two non-tight zeros are ZZ-adjacent, so all three ZZ-edges
go between the tight zeros and `H`.

For the four tight zeros,

`sum_T m_t = 4*6 - 3 = 21`.

Hence

`sum_H m_h + sum_{d in U} m_d = 74 - 21 - m_a - m_b = 49`.       (1)

If the 4-by-4 bipartite graph between `H` and `U` had a perfect matching, the
edge inequalities `m_h+m_d<=12` along the matching would give the left side of
(1) at most `48`.  Thus Hall fails.  Four 3-subsets of a 4-set fail Hall only
when they are all equal, so all non-tight zeros use the same triple
`S=U\{f}`.

Choose a tight zero `t` incident to a ZZ-edge, and choose a non-tight zero
`h` not ZZ-adjacent to `t`.  The rows `F` and `S` are disjoint and miss only
`f`, and the nonedge `th` has no common R-neighbour.  Its two required common
A/B neighbours must therefore all contain `f`.

For any A/B state `I`, write `tau=|I cap T|`, `eta=|I cap H|`,
`phi=|I cap {a,b}|`, `sigma=|I cap S|`, and let `f_I`, `h_I`, and
`q_I=1[{t,h,f} subset I]` be the corresponding indicators.  Since any state
containing a vertex of `H` cannot contain a column of `S`,

`eta + sigma <= 3 + h_I - q_I`.

Therefore

`|I| <= 3 + tau + phi + h_I + f_I - q_I`.

Summing over the twelve A/B states gives

`M <= 36 + sum_T m_t + m_a + m_b + m_h + m_f - sum q_I`.

Using `sum_T m_t=21`, `m_a+m_b=4`, the p14 bound `m_h,m_f<=7`, and at least
two common A/B neighbours of the nonedge `th` containing `{t,h,f}`, we get

`M <= 36 + 21 + 4 + 7 + 7 - 2 = 73`,

contradicting `M=74`.

## V297. p14/e_R23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 3, type 431

Status: VERIFIED finite closure of the touched-count 3 tight-footprint type
`431`.

In touched-count 3, the four tight zero D-pairs have one of three D-column
tight-degree multisets: `431`, `422`, or `332`.  For type `431`, fix a
representative

`(8,9)^3, (8,10)`.

The touched-column equality gives `c_d<=4` for touched columns.  With this
filter, the possible degree-3 non-tight zero row multisets reduce to 110
cases.  I checked these cases by the P-free projection audit

`search23/dirty_z8_projection_audit.py`

with `--zz 3 --zd 20 --zdeg-counts 4,4,0,0` and the fixed row2 profile above.
The two batch outputs are:

- `search23/p14_z8_touch3_431_row3_batch0_10.tsv`: 10/10 INFEASIBLE;
- `search23/p14_z8_touch3_431_row3_batch10_110.tsv`: 100/100 INFEASIBLE.

Thus the full touched-count 3, type `431` branch has no projection-level model.

## V298. p14/e_R23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 3, type 422

Status: VERIFIED closure of the touched-count 3 tight-footprint type `422`.

Fix a representative of the type `422` tight rows:

`(8,9)^2, (8,10)^2`.

Let `a=8` be the common touched column, and let `b=9`, `c=10` be the two
non-central touched columns.  The common column has `c_a=4`, hence all
non-tight degree-3 zeros avoid `a`.

P-free leaf-incidence cut:

Let

`s = sum_{h non-tight} (1_{h~b} + 1_{h~c})`.

Then any feasible type `422` model must have `s=0`.

Proof sketch.  All ZZ-edges run between tight and non-tight zeros.  The tight
zeros contribute `21` to `M`, and the touched D-columns contribute

`m_a+m_b+m_c = 2 + (4-beta) + (4-gamma) = 10-s`.

Between the four non-tight zeros and the three untouched columns there are
`12-s` incidences.  If this bipartite graph has matching number `nu`, the
matching edge bounds give

`sum_H m_h + sum_U m_u <= 49 - 2 nu`.

Thus `M=74` forces `s+2nu<=6`.  But for `s=1,2,3`, the 4-by-3 graph has
`11,10,9` edges and hence `nu=3`; for `s=4`, it has `8` edges and hence
`nu>=2`.  These all contradict `s+2nu<=6`.  Therefore `s=0`.

This cut was added to the exact verifier as `--u3-422-leaf-cut`.

The difficult first row3 branch with non-tight rows

`(9,10,11)^2, (11,12,13)^2`

has `s=4`; with the cut it closes immediately:

`search23/p14_z8_touch3_422_leafcut_idx0_smoke.out`

reports `cat=(3,20) INFEASIBLE status=3 sec=1.011`.

The only possible residual has all four non-tight zeros using the untouched
triple:

`(11,12,13)^4`.

This residual has 9 canonical ZZ skeleton representatives:

`search23/p14_z8_touch3_422_s0_orbits.tsv`.

The P-free projection audit closes all 9:

`search23/p14_z8_touch3_422_s0_projection_reps.tsv`

reports 9/9 INFEASIBLE and 0 survivors.

Conclusion:

The full touched-count 3, type `422` branch is closed.

### V299. p14/eR23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 3, type `332`

The first 10 row3 projection branches for row2 counts

`2,1,0,0,0,1,0,0,0,0,0,0,0,0,0`

gave 7 direct INFEASIBLE and 3 UNKNOWN:

`search23/p14_z8_touch3_332_row3_batch0_10.tsv`.

The 3 UNKNOWN branches were split into 84 canonical ZZ orbit reps, all
projection-infeasible:

`search23/p14_z8_touch3_332_unknown_orbit_summary.tsv`.

The remaining 289 row3 branches were run in parallel at a 100-worker cap:

`search23/p14_z8_touch3_332_row3_parallel10_rest.tsv`

reports 286 direct INFEASIBLE and 3 UNKNOWN.  These 3 UNKNOWN branches
generate 87 canonical ZZ orbit reps:

`search23/p14_z8_touch3_332_row3_idx289_orbits.tsv`

`search23/p14_z8_touch3_332_row3_idx293_orbits.tsv`

`search23/p14_z8_touch3_332_row3_idx296_orbits.tsv`

and the orbit projection audit closes all 87:

`search23/p14_z8_touch3_332_unknown_rest_orbit_projection.tsv`.

Conclusion:

The full touched-count 3, type `332` branch is closed.

### V300. p14/eR23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 4, type `4211`

The canonical tight-row count vector

`0,0,0,0,0,0,0,0,0,0,0,1,0,1,2`

has 215 admissible non-tight row3 branches under the touched-column
capacity cut.  The P-free projection batch

`search23/p14_z8_touch4_4211_row3_projection.tsv`

reports 206 direct INFEASIBLE and 9 UNKNOWN, with no SAT.

The 9 UNKNOWN row3 branches generate 149 canonical ZZ orbit reps:

`search23/p14_z8_touch4_4211_row3_idx4_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx13_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx25_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx32_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx121_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx131_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx139_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx181_orbits.tsv`

`search23/p14_z8_touch4_4211_row3_idx183_orbits.tsv`

The orbit projection audit

`search23/p14_z8_touch4_4211_unknown_orbit_projection.tsv`

reports 149/149 INFEASIBLE and 0 survivors.

Conclusion:

The full touched-count 4, type `4211` branch is closed.

### V301. p14/eR23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 4, type `3311`

There are two canonical tight-row count vectors for type `3311`.

First vector:

`0,0,0,0,0,0,0,0,0,0,0,1,1,0,2`

The row3 projection audit

`search23/p14_z8_touch4_3311a_row3_projection.tsv`

reports 452 direct INFEASIBLE and 1 UNKNOWN, with no SAT.  The single
UNKNOWN branch is `idx=10` with row3 counts

`2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0`.

It generates 31 canonical ZZ orbit reps:

`search23/p14_z8_touch4_3311a_row3_idx10_orbits.tsv`,

and the orbit projection audit

`search23/p14_z8_touch4_3311a_idx10_orbit_projection.tsv`

reports 31/31 INFEASIBLE and 0 survivors.

Second vector:

`0,0,0,0,0,0,0,0,0,0,0,1,3,0,0`

The row3 projection audit

`search23/p14_z8_touch4_3311b_row3_projection.tsv`

reports 453/453 INFEASIBLE and 0 UNKNOWN/SAT.

Conclusion:

The full touched-count 4, type `3311` branch is closed.

### V302. p14/eR23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 4, type `3221`

There are two canonical tight-row count vectors for type `3221`.

First vector:

`0,0,0,0,0,0,0,0,0,0,0,1,1,1,1`

The row3 projection audit

`search23/p14_z8_touch4_3221a_row3_projection.tsv`

reports 668 direct INFEASIBLE and 9 UNKNOWN, with no SAT.  The nine
UNKNOWN branches generate 245 canonical ZZ orbit reps in

`search23/p14_z8_touch4_3221a_row3_idx*_orbits.tsv`,

and the orbit projection audit

`search23/p14_z8_touch4_3221a_unknown_orbit_projection.tsv`

reports 245/245 INFEASIBLE and 0 survivors.

Second vector:

`0,0,0,0,0,0,0,0,0,0,0,1,2,0,1`

The row3 projection audit was run in two pieces and merged by branch index:

`search23/p14_z8_touch4_3221b_row3_projection_merged.tsv`

It reports 668 direct INFEASIBLE and 9 UNKNOWN, with no SAT.  The nine
UNKNOWN branches generate 242 canonical ZZ orbit reps in

`search23/p14_z8_touch4_3221b_row3_idx*_orbits.tsv`,

and the orbit projection audit

`search23/p14_z8_touch4_3221b_unknown_orbit_projection.tsv`

reports 242/242 INFEASIBLE and 0 survivors.

Conclusion:

The full touched-count 4, type `3221` branch is closed.

### V303. p14/eR23 z8 `(3,20)`, zdeg `(4,4,0,0)`, touched-count 4, type `2222`

There are two canonical tight-row count vectors for type `2222`.

First vector:

`0,0,0,0,0,0,0,0,0,0,0,2,2,0,0`

The row3 projection audit

`search23/p14_z8_touch4_2222a_row3_projection.tsv`

reports 1036 direct INFEASIBLE and 46 UNKNOWN, with no SAT.  The 46
UNKNOWN branches generate 738 canonical ZZ orbit reps in

`search23/p14_z8_touch4_2222a_row3_idx*_orbits.tsv`,

and the orbit projection audit

`search23/p14_z8_touch4_2222a_unknown_orbit_projection.tsv`

reports 738/738 INFEASIBLE and 0 survivors.

Second vector:

`0,0,0,0,0,0,0,0,0,0,1,1,1,1,0`

The row3 projection audit

`search23/p14_z8_touch4_2222b_row3_projection.tsv`

reports 957 direct INFEASIBLE and 125 UNKNOWN, with no SAT.  The 125
UNKNOWN branches generate 3165 canonical ZZ orbit reps, summarized in

`search23/p14_z8_touch4_2222b_orbit_generation_summary.tsv`,

and the orbit projection audit

`search23/p14_z8_touch4_2222b_unknown_orbit_projection.tsv`

reports 3165/3165 INFEASIBLE and 0 survivors.

Conclusion:

The full touched-count 4, type `2222` branch is closed.  Together with
V300--V302, all touched-count 4 types for this z8 residual are closed.

### V304. p14/eR23 z8 `(ZZ,ZD)=(3,20)` closed

The possible zero D-degree count profiles for `(ZZ,ZD)=(3,20)` are exactly

`(4,4,0,0)`, `(5,2,1,0)`, `(6,0,2,0)`, and `(6,1,0,1)`.

The first profile `(4,4,0,0)` is closed by V296--V303: touched-count 2,
touched-count 3 types `431`, `422`, `332`, and touched-count 4 types `4211`,
`3311`, `3221`, `2222`.

The remaining three profiles were checked by the full P-free exact A/B verifier
with `--p 14 --eR 23 --only 3:20 --rooted-mode full --timeout 300 --workers 20`:

- `search23/p14_z8_3_20_zdeg5210_pfree_300.out`:
  `cat=(3,20) INFEASIBLE status=3 sec=53.066`;
- `search23/p14_z8_3_20_zdeg6020_pfree_300.out`:
  `cat=(3,20) INFEASIBLE status=3 sec=22.254`;
- `search23/p14_z8_3_20_zdeg6101_pfree_300.out`:
  `cat=(3,20) INFEASIBLE status=3 sec=47.516`.

Thus the full z8 category `(ZZ,ZD)=(3,20)` is closed.  The remaining z8
frontier after V292 and V304 is `(ZZ,ZD)=(0,23),(1,22),(2,21)`.

### V305. p14/eR23 z8 `(0,23)`, zdeg `(1,7,0,0)`, touched-count 2 closed

In the `(ZZ,ZD)=(0,23)` category with zero D-degree profile `(1,7,0,0)`,
the unique tight degree-2 zero may be fixed by D-symmetry to row `{8,9}`.
The row3-count orbit generation
`search23/p14_z8_0_23_zdeg1700_row2_89_row3_orbits.tsv` produced 3505
row3-count representatives.  A smoke projection on the first 200
representatives left 27 non-infeasible rows:

`search23/p14_z8_0_23_zdeg1700_row2_89_row3_smoke200.tsv`
reported 173 `INFEASIBLE`, 14 projection-SAT, and 13 `UNKNOWN`.

The full P-free verifier then closed 21 of these 27 rows:

`search23/p14_z8_0_23_zdeg1700_row2_89_smoke_survivors_full.tsv`
has 21 rows whose verifier output begins
`cat=(0,23) INFEASIBLE status=3`; six rows remained `UNKNOWN` at the
600s limit.

For the remaining six row3-count patterns, the P-free state-count certificate
`search23/verify_z8_zdeg1700_six_state_ilp.py` verifies the following:

- pattern 1: 344 raw independent D-visible state types; direct slack identity
  gives `M <= 71`;
- pattern 2: 443 raw state types, 116 retained by the one-unit slack budget;
- pattern 3: 355 raw state types; direct slack identity gives `M <= 72`;
- pattern 4: 533 raw state types, 471 retained by the three-unit slack budget;
- pattern 5: 481 raw state types, 379 retained by the two-unit slack budget;
- pattern 6: 391 raw state types, 27 retained by the exact zero-slack budget.

The checker output
`search23/z8_zdeg1700_six_state_ilp.out` is:

```text
pattern=1 raw_states=344 retained_states=344 status=INFEASIBLE
pattern=2 raw_states=443 retained_states=116 status=INFEASIBLE
pattern=3 raw_states=355 retained_states=355 status=INFEASIBLE
pattern=4 raw_states=533 retained_states=471 status=INFEASIBLE
pattern=5 raw_states=481 retained_states=379 status=INFEASIBLE
pattern=6 raw_states=391 retained_states=27 status=INFEASIBLE
```

Thus the full touched-count 2 subbranch of `(ZZ,ZD)=(0,23)`,
zdeg `(1,7,0,0)` is closed.

### V306. p14/eR23 z8 complementary-row touched-count 2 closures

Two touched-count 2 branches in the remaining z8 frontier close by the
complementary-row skeleton lemma.

If two zero D-rows are complementary, then the two zeros must be adjacent by a
ZZ edge.  Otherwise they have no common D-neighbour; any common A/B-neighbour
would have to avoid all six D-columns, contradicting D-visibility; and a common
zero-neighbour would also need a D-row disjoint from all six D-columns,
contradicting the lower bound `d_D >= 2`.

In a touched-count 2 branch, all tight degree-2 zeros have the same two-column
footprint `F`.  Therefore:

- In `(ZZ,ZD)=(1,22)`, zdeg `(4,2,2,0)`, touched-count 2, the four tight
  zeros have row `F`, and the two degree-4 zeros have row `D\F`.  This forces
  `4*2=8` complementary ZZ edges, contradicting `ZZ=1`.
- In `(ZZ,ZD)=(2,21)`, zdeg `(4,3,1,0)`, touched-count 2, the four tight
  zeros have row `F`, and the unique degree-4 zero has row `D\F`.  This forces
  `4` complementary ZZ edges, contradicting `ZZ=2`.

The verifier now includes these branch no-goods in
`search23/verify_p15_z8_pfree_exact_ab_cpsat.py`.  Direct checks:

```text
search23/p14_z8_1_22_zdeg4220_touch2_comprow.out:
cat=(1,22) INFEASIBLE status=3 sec=0.000

search23/p14_z8_2_21_zdeg4310_touch2_comprow.out:
cat=(2,21) INFEASIBLE status=3 sec=0.000
```

Thus those two touched-count 2 branches are closed.

### V307. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 2 closed

In the `(ZZ,ZD)=(2,21)` z8 branch with zdeg `(3,5,0,0)` and touched-count 2,
the three degree-2 zeros have the same touched pair.  By D-symmetry this pair
may be fixed as `{8,9}`.

The row3-count orbit generator
`search23/generate_z8_row3_count_orbits.py` gives 56 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_row2x3_89_row3_orbits.tsv
row3_orbits=56 raw=1336 d_auts=48
```

A broad row3-count run left the first four orbits UNKNOWN at 300s, so the
verifier was strengthened operationally by fixing canonical zero D-rows for
each row3-count orbit.  The runner
`search23/run_z8_row3_fixed_rows_parallel.py` turns each row3-count vector into
an explicit `--fix-rows` instance for
`search23/verify_p15_z8_pfree_exact_ab_cpsat.py`.

For orbit `idx=0`, all five degree-3 rows are `{11,12,13}`.  The only possible
ZZ edges lie between the three `{8,9}` zeros and the five `{11,12,13}` zeros,
and there are three ZZ-edge orbits: a matching, a tight-zero 2-star, and a
degree-3-zero 2-star.  The durable checks are:

```text
search23/p14_z8_2_21_zdeg3500_idx0_zz_matching.out:
cat=(2,21) INFEASIBLE status=3

search23/p14_z8_2_21_zdeg3500_idx0_zz_tstar.out:
cat=(2,21) INFEASIBLE status=3

search23/p14_z8_2_21_zdeg3500_idx0_zz_hstar.out:
cat=(2,21) INFEASIBLE status=3
```

For row3-count orbits `idx=1,2,3`, fixed rows alone suffice:

```text
search23/p14_z8_2_21_zdeg3500_idx1_fixed.out:
cat=(2,21) INFEASIBLE status=3

search23/p14_z8_2_21_zdeg3500_idx2_fixed.out:
cat=(2,21) INFEASIBLE status=3

search23/p14_z8_2_21_zdeg3500_idx3_fixed.out:
cat=(2,21) INFEASIBLE status=3
```

The remaining 52 row3-count orbits, `idx=4..55`, are all closed by the
fixed-row runner:

```text
search23/p14_z8_2_21_zdeg3500_touch2_row3_fixed.tsv:
INFEASIBLE 52
```

The corresponding runner stdout ends with:

```text
52/52 idx=53 INFEASIBLE 31.7s cat=(2,21) INFEASIBLE status=3 sec=17.763
done selected=52 elapsed=654.9s out=search23/p14_z8_2_21_zdeg3500_touch2_row3_fixed.tsv
```

Thus the full touched-count 2 subbranch of `(ZZ,ZD)=(2,21)`, zdeg
`(3,5,0,0)`, is closed.

### V308. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 3 row2b orbit closed

In the same `(ZZ,ZD)=(2,21)` z8 branch with zdeg `(3,5,0,0)`, the
touched-count 3 degree-2-row layer has two row2-count orbits.  The second
orbit has row2-count vector

```text
0,0,0,0,0,0,0,0,0,0,0,0,1,1,1
```

over the lexicographic D-pairs.  For this row2 orbit the row3-count generator
produced 143 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch3_row2b_row3_orbits.tsv
```

As a smoke check, the first 20 row3-count orbits were run through the fixed-row
runner and all closed:

```text
search23/p14_z8_2_21_zdeg3500_touch3_row2b_smoke20_fixed.tsv:
INFEASIBLE 20
```

The full fixed-row run then closed all 143 row3-count orbits using 20 parallel
jobs with 5 CP-SAT workers per job:

```text
search23/p14_z8_2_21_zdeg3500_touch3_row2b_full_fixed.tsv:
INFEASIBLE 143
```

The corresponding runner stdout ends with:

```text
143/143 idx=142 INFEASIBLE 62.8s cat=(2,21) INFEASIBLE status=3 sec=47.271
done selected=143 elapsed=345.3s out=search23/p14_z8_2_21_zdeg3500_touch3_row2b_full_fixed.tsv
```

Thus this touched-count 3 row2 orbit is closed.  The other touched-count 3
row2 orbit remains active unless closed separately.

### V309. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 3 closed

The other touched-count 3 degree-2-row orbit has row2-count vector

```text
0,0,0,0,0,0,0,0,0,0,0,0,0,1,2
```

over the lexicographic D-pairs.  For this row2 orbit the row3-count generator
produced 399 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch3_row2a_row3_orbits.tsv
```

Running the same fixed-row verifier with 20 parallel jobs and 5 CP-SAT workers
per job closed all 399 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch3_row2a_full_fixed.tsv:
INFEASIBLE 399
```

The corresponding runner stdout ends with:

```text
399/399 idx=395 INFEASIBLE 78.9s cat=(2,21) INFEASIBLE status=3 sec=61.968
done selected=399 elapsed=991.6s out=search23/p14_z8_2_21_zdeg3500_touch3_row2a_full_fixed.tsv
```

Together with V308, this closes the full touched-count 3 subbranch of
`(ZZ,ZD)=(2,21)`, zdeg `(3,5,0,0)`.

### V310. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 4 row2c orbit closed

For touched-count 4, the first degree-2-row orbit considered has row2-count
vector

```text
0,0,0,0,0,0,0,0,0,0,0,1,0,1,1
```

over the lexicographic D-pairs.  The row3-count generator produced 253
row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2c_row3_orbits.tsv
row3_orbits=253 raw=2341 d_auts=12
```

The fixed-row verifier closed all 253 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2c_full_fixed.tsv:
INFEASIBLE 253
```

The corresponding runner stdout ends with:

```text
253/253 idx=251 INFEASIBLE 60.6s cat=(2,21) INFEASIBLE status=3 sec=44.749
done selected=253 elapsed=551.0s out=search23/p14_z8_2_21_zdeg3500_touch4_row2c_full_fixed.tsv
```

Thus this touched-count 4 row2 orbit is closed.  The other touched-count 4
row2 orbits remain active unless closed separately.

### V311. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 4 row2e orbit closed

Another touched-count 4 degree-2-row orbit has row2-count vector

```text
0,0,0,0,0,0,0,0,0,0,0,1,2,0,0
```

over the lexicographic D-pairs.  The row3-count generator produced 565
row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2e_row3_orbits.tsv
row3_orbits=565 raw=3600 d_auts=8
```

The fixed-row verifier closed all 565 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2e_full_fixed.tsv:
INFEASIBLE 565
```

The corresponding runner stdout ends with:

```text
562/565 idx=557 INFEASIBLE 61.9s cat=(2,21) INFEASIBLE status=3 sec=46.412
563/565 idx=555 INFEASIBLE 62.5s cat=(2,21) INFEASIBLE status=3 sec=46.311
564/565 idx=556 INFEASIBLE 69.1s cat=(2,21) INFEASIBLE status=3 sec=53.485
565/565 idx=564 INFEASIBLE 53.6s cat=(2,21) INFEASIBLE status=3 sec=38.180
done selected=565 elapsed=1142.8s out=search23/p14_z8_2_21_zdeg3500_touch4_row2e_full_fixed.tsv
```

Thus this touched-count 4 row2 orbit is closed.  The other touched-count 4
row2 orbits remain active unless closed separately.

### V312. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 4 row2d orbit closed

Another touched-count 4 degree-2-row orbit has row2-count vector

```text
0,0,0,0,0,0,0,0,0,0,0,1,1,0,1
```

over the lexicographic D-pairs.  The row3-count generator produced 971
row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2d_row3_orbits.tsv
row3_orbits=971 raw=3600 d_auts=4
```

The fixed-row verifier closed all 971 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch4_row2d_full_fixed.tsv:
INFEASIBLE 971
```

The corresponding runner stdout ends with:

```text
967/971 idx=962 INFEASIBLE 62.7s cat=(2,21) INFEASIBLE status=3 sec=46.575
968/971 idx=968 INFEASIBLE 50.2s cat=(2,21) INFEASIBLE status=3 sec=35.423
969/971 idx=967 INFEASIBLE 58.3s cat=(2,21) INFEASIBLE status=3 sec=42.125
970/971 idx=970 INFEASIBLE 54.0s cat=(2,21) INFEASIBLE status=3 sec=38.302
971/971 idx=969 INFEASIBLE 55.3s cat=(2,21) INFEASIBLE status=3 sec=39.201
done selected=971 elapsed=1970.1s out=search23\p14_z8_2_21_zdeg3500_touch4_row2d_full_fixed.tsv
```

Together with V310 and V311, this closes the full touched-count 4 subbranch of
`(ZZ,ZD)=(2,21)`, zdeg `(3,5,0,0)`.

### V313. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 5 closed

The unique touched-count 5 degree-2-row orbit has row2-count vector

```text
0,0,0,0,0,0,0,0,1,0,0,1,1,0,0
```

over the lexicographic D-pairs.  The row3-count generator produced 1255
row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch5_row2f_row3_orbits.tsv
row3_orbits=1255 raw=4450 d_auts=4
```

The fixed-row verifier closed all 1255 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch5_row2f_full_fixed.tsv:
INFEASIBLE 1255
```

The corresponding runner stdout ends with:

```text
1251/1255 idx=1244 INFEASIBLE 45.1s cat=(2,21) INFEASIBLE status=3 sec=30.031
1252/1255 idx=1246 INFEASIBLE 45.5s cat=(2,21) INFEASIBLE status=3 sec=30.527
1253/1255 idx=1247 INFEASIBLE 50.1s cat=(2,21) INFEASIBLE status=3 sec=34.798
1254/1255 idx=1253 INFEASIBLE 43.2s cat=(2,21) INFEASIBLE status=3 sec=29.349
1255/1255 idx=1254 INFEASIBLE 50.4s cat=(2,21) INFEASIBLE status=3 sec=35.199
done selected=1255 elapsed=1574.8s out=search23\p14_z8_2_21_zdeg3500_touch5_row2f_full_fixed.tsv
```

Thus the touched-count 5 subbranch of `(ZZ,ZD)=(2,21)`, zdeg `(3,5,0,0)`,
is closed.

### V314. p14/eR23 z8 `(2,21)`, zdeg `(3,5,0,0)`, touched-count 6 closed

The unique touched-count 6 degree-2-row orbit has row2-count vector

```text
0,0,0,0,1,0,0,1,0,1,0,0,0,0,0
```

over the lexicographic D-pairs.  The row3-count generator produced 153
row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch6_row2g_row3_orbits.tsv
row3_orbits=153 raw=5612 d_auts=48
```

The fixed-row verifier closed all 153 row3-count orbits:

```text
search23/p14_z8_2_21_zdeg3500_touch6_row2g_full_fixed.tsv:
INFEASIBLE 153
```

The corresponding runner stdout ends with:

```text
149/153 idx=150 INFEASIBLE 18.1s cat=(2,21) INFEASIBLE status=3 sec=2.572
150/153 idx=148 INFEASIBLE 18.3s cat=(2,21) INFEASIBLE status=3 sec=2.610
151/153 idx=149 INFEASIBLE 18.3s cat=(2,21) INFEASIBLE status=3 sec=2.575
152/153 idx=152 INFEASIBLE 18.1s cat=(2,21) INFEASIBLE status=3 sec=2.539
153/153 idx=151 INFEASIBLE 18.5s cat=(2,21) INFEASIBLE status=3 sec=2.559
done selected=153 elapsed=145.5s out=search23\p14_z8_2_21_zdeg3500_touch6_row2g_full_fixed.tsv
```

Together with V307--V313, this closes the full zdeg `(3,5,0,0)` subbranch of
`(ZZ,ZD)=(2,21)`.

### V315. p14/eR23 z8 `(1,22)`, zdeg `(4,2,2,0)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(4,2,2,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg4220_row2_orbits.tsv
row2_orbits=21 raw=3060
```

The touched-count 2 branch is closed by the complementary-row check from V306:

```text
search23/p14_z8_1_22_zdeg4220_touch2_comprow.out:
cat=(1,22) INFEASIBLE status=3 sec=0.000
```

The touched-count 3 branch consists of row2 orbit indices `1,2,3`.  For these
three row2 orbits, the row3-count manifests contain `10`, `11`, and `21`
row3-count orbits respectively:

```text
search23/p14_z8_1_22_zdeg4220_touch3_row2idx1_row3_orbits.tsv
search23/p14_z8_1_22_zdeg4220_touch3_row2idx2_row3_orbits.tsv
search23/p14_z8_1_22_zdeg4220_touch3_row2idx3_row3_orbits.tsv
```

The fixed-row verifier leaves the two degree-4 zero rows free and closes all
three manifests:

```text
search23/p14_z8_1_22_zdeg4220_touch3_row2idx1_full_fixed.tsv: 10 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch3_row2idx2_full_fixed.tsv: 11 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch3_row2idx3_full_fixed.tsv: 21 INFEASIBLE
```

Thus touched-count 3 contributes `42/42` INFEASIBLE leaves.

The touched-count 4 branch consists of row2 orbit indices `4..10`.  The
row3-count manifests contain `22`, `38`, `56`, `92`, `28`, `29`, and `29`
row3-count orbits.  The fixed-row verifier closes all of them:

```text
search23/p14_z8_1_22_zdeg4220_touch4_row2idx4_full_fixed.tsv: 22 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx5_full_fixed.tsv: 38 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx6_full_fixed.tsv: 56 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx7_full_fixed.tsv: 92 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx8_full_fixed.tsv: 28 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx9_full_fixed.tsv: 29 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch4_row2idx10_full_fixed.tsv: 29 INFEASIBLE
```

Thus touched-count 4 contributes `294/294` INFEASIBLE leaves.

The touched-count 5 branch is closed directly by the P-free exact A/B verifier:

```text
search23/p14_z8_cat1_22_zdeg4220_touch5_pfree_300.out:
cat=(1,22) INFEASIBLE status=3 sec=18.163
```

The touched-count 6 branch consists of row2 orbit indices `17..20`.  The
row3-count manifests contain `26`, `42`, `70`, and `29` row3-count orbits,
and the fixed-row verifier closes all of them:

```text
search23/p14_z8_1_22_zdeg4220_touch6_row2idx17_full_fixed.tsv: 26 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch6_row2idx18_full_fixed.tsv: 42 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch6_row2idx19_full_fixed.tsv: 70 INFEASIBLE
search23/p14_z8_1_22_zdeg4220_touch6_row2idx20_full_fixed.tsv: 29 INFEASIBLE
```

Thus touched-count 6 contributes `167/167` INFEASIBLE leaves.

Since the row2 manifest has touched counts only `2,3,4,5,6`, these checks close
the full zdeg `(4,2,2,0)` subbranch of `(ZZ,ZD)=(1,22)`.

### V316. p14/eR23 z8 `(2,21)`, zdeg `(4,3,1,0)` closed

For the `(ZZ,ZD)=(2,21)` z8 branch with zero-D degree profile `(4,3,1,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_2_21_zdeg4310_row2_orbits.tsv
row2_orbits=21 raw=3060
```

The touched-count 2 branch is closed by the complementary-row check from V306:

```text
search23/p14_z8_2_21_zdeg4310_touch2_comprow.out:
cat=(2,21) INFEASIBLE status=3 sec=0.000
```

The touched-count 3 branch consists of row2 orbit indices `1,2,3`.  The
row3-count manifests contain `21`, `19`, and `38` row3-count orbits, and the
fixed-row verifier closes all of them:

```text
search23/p14_z8_2_21_zdeg4310_touch3_row2idx1_full_fixed.tsv: 21 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch3_row2idx2_full_fixed.tsv: 19 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch3_row2idx3_full_fixed.tsv: 38 INFEASIBLE
```

Thus touched-count 3 contributes `78/78` INFEASIBLE leaves.

The touched-count 4 branch consists of row2 orbit indices `4..10`.  The
row3-count manifests contain `54`, `97`, `162`, `279`, `68`, `75`, and `75`
row3-count orbits.  The fixed-row verifier closes all of them:

```text
search23/p14_z8_2_21_zdeg4310_touch4_row2idx4_full_fixed.tsv: 54 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx5_full_fixed.tsv: 97 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx6_full_fixed.tsv: 162 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx7_full_fixed.tsv: 279 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx8_full_fixed.tsv: 68 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx9_full_fixed.tsv: 75 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch4_row2idx10_full_fixed.tsv: 75 INFEASIBLE
```

Thus touched-count 4 contributes `810/810` INFEASIBLE leaves.

The touched-count 5 branch is closed directly by the P-free exact A/B verifier:

```text
search23/p14_z8_cat2_21_zdeg4310_touch5_pfree_300.out:
cat=(2,21) INFEASIBLE status=3 sec=18.150
```

The touched-count 6 branch consists of row2 orbit indices `17..20`.  The
row3-count manifests contain `100`, `171`, `319`, and `104` row3-count orbits,
and the fixed-row verifier closes all of them:

```text
search23/p14_z8_2_21_zdeg4310_touch6_row2idx17_full_fixed.tsv: 100 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch6_row2idx18_full_fixed.tsv: 171 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch6_row2idx19_full_fixed.tsv: 319 INFEASIBLE
search23/p14_z8_2_21_zdeg4310_touch6_row2idx20_full_fixed.tsv: 104 INFEASIBLE
```

Thus touched-count 6 contributes `694/694` INFEASIBLE leaves.

Since the row2 manifest has touched counts only `2,3,4,5,6`, these checks close
the full zdeg `(4,3,1,0)` subbranch of `(ZZ,ZD)=(2,21)`.

### V317. p14/eR23 z8 `(2,21)`, zdeg `(5,1,2,0)` closed

For the `(ZZ,ZD)=(2,21)` z8 branch with zero-D degree profile `(5,1,2,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_2_21_zdeg5120_row2_orbits.tsv
row2_orbits=45 raw=10887
```

The row2 manifest has touched counts only `3,4,5,6`.  The fixed-row verifier
leaves the remaining high-degree zero rows free and closes each touched layer:

```text
touch-count 3: row2 idx 0..1,   5/5 INFEASIBLE
touch-count 4: row2 idx 2..12, 70/70 INFEASIBLE
touch-count 5: row2 idx 13..28, 172/172 INFEASIBLE
touch-count 6: row2 idx 29..44, 128/128 INFEASIBLE
```

The corresponding certificate files are:

```text
search23/p14_z8_2_21_zdeg5120_touch3_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5120_touch4_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5120_touch5_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5120_touch6_row2idx*_full_fixed.tsv
```

Thus all `375/375` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(5,1,2,0)` subbranch of `(ZZ,ZD)=(2,21)`.

### V318. p14/eR23 z8 `(2,21)`, zdeg `(5,2,0,1)` closed

For the `(ZZ,ZD)=(2,21)` z8 branch with zero-D degree profile `(5,2,0,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_2_21_zdeg5201_row2_orbits.tsv
row2_orbits=45 raw=10887
```

All row3-count manifests were generated for the 45 row2 orbits and checked by
the fixed-row verifier with the remaining high-degree zero rows left free.  The
layer totals are:

```text
touch-count 3: 9/9 INFEASIBLE
touch-count 4: 256/256 INFEASIBLE
touch-count 5: 964/964 INFEASIBLE
touch-count 6: 830/830 INFEASIBLE
```

The corresponding certificate files are:

```text
search23/p14_z8_2_21_zdeg5201_touch3_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5201_touch4_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5201_touch5_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg5201_touch6_row2idx*_full_fixed.tsv
```

Thus all `2059/2059` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(5,2,0,1)` subbranch of `(ZZ,ZD)=(2,21)`.

### V319. p14/eR23 z8 `(2,21)`, zdeg `(6,0,1,1)` closed; category `(2,21)` closed

For the `(ZZ,ZD)=(2,21)` z8 branch with zero-D degree profile `(6,0,1,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_2_21_zdeg6011_row2_orbits.tsv
row2_orbits=98 raw=30405
```

Each row2 orbit has a single row3-count orbit.  The fixed-row verifier closes
all row2 orbits:

```text
touch-count 3: 1/1 INFEASIBLE
touch-count 4: 13/13 INFEASIBLE
touch-count 5: 34/34 INFEASIBLE
touch-count 6: 50/50 INFEASIBLE
```

The corresponding certificate files are:

```text
search23/p14_z8_2_21_zdeg6011_touch3_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg6011_touch4_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg6011_touch5_row2idx*_full_fixed.tsv
search23/p14_z8_2_21_zdeg6011_touch6_row2idx*_full_fixed.tsv
```

Thus all `98/98` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(6,0,1,1)` subbranch of `(ZZ,ZD)=(2,21)`.

The possible zero D-degree profiles for `(ZZ,ZD)=(2,21)` are exactly
`(3,5,0,0)`, `(4,3,1,0)`, `(5,1,2,0)`, `(5,2,0,1)`, and `(6,0,1,1)`.
They are closed respectively by V307--V314, V316, V317, V318, and this item.
Therefore the full z8 category `(ZZ,ZD)=(2,21)` is closed.

### V320. p14/eR23 z8 `(0,23)`, zdeg `(2,5,1,0)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(2,5,1,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg2510_row2_orbits.tsv
row2_orbits=3 raw=120
```

The row3 manifests contain `2404` fixed-row leaves:

```text
search23/p14_z8_0_23_zdeg2510_touch2_row2idx0_row3_orbits.tsv: 282 rows
search23/p14_z8_0_23_zdeg2510_touch3_row2idx1_row3_orbits.tsv: 1106 rows
search23/p14_z8_0_23_zdeg2510_touch4_row2idx2_row3_orbits.tsv: 1016 rows
```

The first fixed-row pass closed `2396` leaves and left `8` CP-SAT timeout
UNKNOWNs.  Rerunning exactly those eight rows with `1200s` timeout and `12`
CP-SAT workers per row closed all eight:

```text
search23/p14_z8_0_23_zdeg2510_touch2_idx24_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch2_idx158_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch2_idx200_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch2_idx203_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch3_idx43_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch3_idx647_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch4_idx958_rerun1200.tsv: INFEASIBLE
search23/p14_z8_0_23_zdeg2510_touch4_idx1009_rerun1200.tsv: INFEASIBLE
```

Thus all `2404/2404` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(2,5,1,0)` subbranch of `(ZZ,ZD)=(0,23)`.

### V321. p14/eR23 z8 `(1,22)`, zdeg `(2,6,0,0)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(2,6,0,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg2600_row2_orbits.tsv
row2_orbits=3 raw=120
```

The row3 manifests contain `3340` fixed-row leaves:

```text
search23/p14_z8_1_22_zdeg2600_touch2_row2idx0_row3_orbits.tsv: 532 rows
search23/p14_z8_1_22_zdeg2600_touch3_row2idx1_row3_orbits.tsv: 1634 rows
search23/p14_z8_1_22_zdeg2600_touch4_row2idx2_row3_orbits.tsv: 1174 rows
```

The first fixed-row pass closed `3328` leaves and left `12` CP-SAT timeout
UNKNOWNs.  Rerunning exactly those twelve rows with `1200s` timeout and `8`
CP-SAT workers per row closed all twelve:

```text
search23/p14_z8_1_22_zdeg2600_touch2_idx24_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch2_idx292_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch2_idx301_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch3_idx17_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch3_idx399_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch3_idx1175_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx676_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx705_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx967_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx1073_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx1137_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg2600_touch4_idx1157_rerun1200.tsv: INFEASIBLE
```

Thus all `3340/3340` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(2,6,0,0)` subbranch of `(ZZ,ZD)=(1,22)`.

### V322. p14/eR23 z8 `(0,23)`, zdeg `(3,3,2,0)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(3,3,2,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg3320_row2_orbits.tsv
row2_orbits=8 raw=600
```

The row3 manifests contain `1294` fixed-row leaves:

```text
search23/p14_z8_0_23_zdeg3320_touch2_row2idx0_row3_orbits.tsv: 18 rows
search23/p14_z8_0_23_zdeg3320_touch3_row2idx1_row3_orbits.tsv: 139 rows
search23/p14_z8_0_23_zdeg3320_touch3_row2idx2_row3_orbits.tsv: 55 rows
search23/p14_z8_0_23_zdeg3320_touch4_row2idx3_row3_orbits.tsv: 100 rows
search23/p14_z8_0_23_zdeg3320_touch4_row2idx4_row3_orbits.tsv: 319 rows
search23/p14_z8_0_23_zdeg3320_touch4_row2idx5_row3_orbits.tsv: 201 rows
search23/p14_z8_0_23_zdeg3320_touch5_row2idx6_row3_orbits.tsv: 408 rows
search23/p14_z8_0_23_zdeg3320_touch6_row2idx7_row3_orbits.tsv: 54 rows
```

The fixed-row verifier closes every leaf:

```text
search23/p14_z8_0_23_zdeg3320_touch2_row2idx0_full_fixed.tsv: 18 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch3_row2idx1_full_fixed.tsv: 139 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch3_row2idx2_full_fixed.tsv: 55 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch4_row2idx3_full_fixed.tsv: 100 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch4_row2idx4_full_fixed.tsv: 319 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch4_row2idx5_full_fixed.tsv: 201 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch5_row2idx6_full_fixed.tsv: 408 INFEASIBLE
search23/p14_z8_0_23_zdeg3320_touch6_row2idx7_full_fixed.tsv: 54 INFEASIBLE
```

Thus all `1294/1294` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(3,3,2,0)` subbranch of `(ZZ,ZD)=(0,23)`.

### V323. p14/eR23 z8 `(0,23)`, zdeg `(3,4,0,1)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(3,4,0,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg3401_row2_orbits.tsv
row2_orbits=8 raw=680
```

The row3 manifests contain `3198` fixed-row leaves:

```text
search23/p14_z8_0_23_zdeg3401_touch2_row2idx0_row3_orbits.tsv: 35 rows
search23/p14_z8_0_23_zdeg3401_touch3_row2idx1_row3_orbits.tsv: 287 rows
search23/p14_z8_0_23_zdeg3401_touch3_row2idx2_row3_orbits.tsv: 110 rows
search23/p14_z8_0_23_zdeg3401_touch4_row2idx3_row3_orbits.tsv: 218 rows
search23/p14_z8_0_23_zdeg3401_touch4_row2idx4_row3_orbits.tsv: 805 rows
search23/p14_z8_0_23_zdeg3401_touch4_row2idx5_row3_orbits.tsv: 477 rows
search23/p14_z8_0_23_zdeg3401_touch5_row2idx6_row3_orbits.tsv: 1115 rows
search23/p14_z8_0_23_zdeg3401_touch6_row2idx7_row3_orbits.tsv: 151 rows
```

The corrected fixed-row verifier run used `--only 0:23` and closes every leaf:

```text
search23/p14_z8_0_23_zdeg3401_touch2_row2idx0_full_fixed.tsv: 35 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch3_row2idx1_full_fixed.tsv: 287 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch3_row2idx2_full_fixed.tsv: 110 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch4_row2idx3_full_fixed.tsv: 218 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch4_row2idx4_full_fixed.tsv: 805 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch4_row2idx5_full_fixed.tsv: 477 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch5_row2idx6_full_fixed.tsv: 1115 INFEASIBLE
search23/p14_z8_0_23_zdeg3401_touch6_row2idx7_full_fixed.tsv: 151 INFEASIBLE
```

Thus all `3198/3198` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(3,4,0,1)` subbranch of `(ZZ,ZD)=(0,23)`.

### V324. p14/eR23 z8 `(1,22)`, zdeg `(3,4,1,0)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(3,4,1,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg3410_row2_orbits.tsv
row2_orbits=8 raw=680
```

The row3 manifests contain `3198` fixed-row leaves:

```text
search23/p14_z8_1_22_zdeg3410_touch2_row2idx0_row3_orbits.tsv: 35 rows
search23/p14_z8_1_22_zdeg3410_touch3_row2idx1_row3_orbits.tsv: 287 rows
search23/p14_z8_1_22_zdeg3410_touch3_row2idx2_row3_orbits.tsv: 110 rows
search23/p14_z8_1_22_zdeg3410_touch4_row2idx3_row3_orbits.tsv: 218 rows
search23/p14_z8_1_22_zdeg3410_touch4_row2idx4_row3_orbits.tsv: 805 rows
search23/p14_z8_1_22_zdeg3410_touch4_row2idx5_row3_orbits.tsv: 477 rows
search23/p14_z8_1_22_zdeg3410_touch5_row2idx6_row3_orbits.tsv: 1115 rows
search23/p14_z8_1_22_zdeg3410_touch6_row2idx7_row3_orbits.tsv: 151 rows
```

The first fixed-row pass closed `3189` leaves and left `9` CP-SAT timeout
UNKNOWNs.  The UNKNOWN rows are listed in:

```text
search23/p14_z8_1_22_zdeg3410_unknowns.csv
```

Rerunning exactly those nine rows with `1200s` timeout and `11` CP-SAT workers
per row closed all nine:

```text
search23/p14_z8_1_22_zdeg3410_touch3_idx265_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch3_idx67_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch3_idx88_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch3_idx101_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch3_idx105_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch4_idx217_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch4_idx341_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch4_idx727_rerun1200.tsv: INFEASIBLE
search23/p14_z8_1_22_zdeg3410_touch4_idx801_rerun1200.tsv: INFEASIBLE
```

Thus all `3198/3198` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(3,4,1,0)` subbranch of `(ZZ,ZD)=(1,22)`.

### V325. p14/eR23 z8 `(0,23)`, zdeg `(4,1,3,0)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(4,1,3,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg4130_row2_orbits.tsv
row2_orbits=21 raw=3060
```

The row3 manifests contain `147` fixed-row leaves.  The fixed-row verifier
closes every leaf:

```text
touch2 row2idx0: 1 INFEASIBLE
touch3 row2idx1..3: 13 INFEASIBLE
touch4 row2idx4..10: 52 INFEASIBLE
touch5 row2idx11..16: 58 INFEASIBLE
touch6 row2idx17..20: 23 INFEASIBLE
```

The certificate files are:

```text
search23/p14_z8_0_23_zdeg4130_touch*_row2idx*_full_fixed.tsv
```

Thus all `147/147` fixed-row leaves are INFEASIBLE, closing the full zdeg
`(4,1,3,0)` subbranch of `(ZZ,ZD)=(0,23)`.

### V326. p14/eR23 z8 `(0,23)`, zdeg `(4,2,1,1)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(4,2,1,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg4211_row2_orbits.tsv
row2_orbits=21
```

The row3 manifests contain `925` fixed-row leaves across the 21 row2 branches.
The fixed-row verifier closed every leaf.  The combined certificate is:

```text
search23/p14_z8_0_23_zdeg4211_full_fixed_combined.tsv
```

The combined audit gives `925/925` rows with status INFEASIBLE and no missing
or duplicate row3 indices.  This closes the full zdeg `(4,2,1,1)` subbranch of
`(ZZ,ZD)=(0,23)`.

### V327. p14/eR23 z8 `(0,23)`, zdeg `(5,0,2,1)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(5,0,2,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg5021_row2_orbits.tsv
row2_orbits=45 raw=10887
```

The row3 manifests contain `45` fixed-row leaves, one for each row2 branch.
The fixed-row verifier closed every leaf.  The combined certificate is:

```text
search23/p14_z8_0_23_zdeg5021_full_fixed_combined.tsv
```

The combined audit gives `45/45` rows with status INFEASIBLE.  This closes the
full zdeg `(5,0,2,1)` subbranch of `(ZZ,ZD)=(0,23)`.

### V328. p14/eR23 z8 `(0,23)`, zdeg `(5,1,0,2)` closed

For the `(ZZ,ZD)=(0,23)` z8 branch with zero-D degree profile `(5,1,0,2)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_0_23_zdeg5102_row2_orbits.tsv
row2_orbits=45 raw=10887
```

The row3 manifests contain `375` fixed-row leaves.  The fixed-row verifier
closed every leaf.  The combined certificate is:

```text
search23/p14_z8_0_23_zdeg5102_full_fixed_combined.tsv
```

The combined audit gives `375/375` rows with status INFEASIBLE.  Together with
V305, V320, V322, V323, V325, V326, and V327, this closes all possible zdeg
subbranches of the full `(ZZ,ZD)=(0,23)` category.

### V329. p14/eR23 z8 `(1,22)`, zdeg `(4,3,0,1)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(4,3,0,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg4301_row2_orbits.tsv
row2_orbits=21 raw=3060
```

The row3 manifests contain `3209` fixed-row leaves.  The fixed-row verifier
closed every leaf, using two tail relaunches to keep process-level parallelism
near the 100-worker cap.  The combined certificate is:

```text
search23/p14_z8_1_22_zdeg4301_full_fixed_combined.tsv
```

The combined audit gives `3209/3209` rows with status INFEASIBLE and no missing
row2/row3 counts.  This closes the full zdeg `(4,3,0,1)` subbranch of
`(ZZ,ZD)=(1,22)`.

### V330. p14/eR23 z8 `(1,22)`, zdeg `(5,0,3,0)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(5,0,3,0)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg5030_row2_orbits.tsv
row2_orbits=45 raw=10887
```

The row3 manifests contain `45` fixed-row leaves, one for each row2 branch.
The fixed-row verifier closed every leaf.  The combined certificate is:

```text
search23/p14_z8_1_22_zdeg5030_full_fixed_combined.tsv
```

The combined audit gives `45/45` rows with status INFEASIBLE.  This closes the
full zdeg `(5,0,3,0)` subbranch of `(ZZ,ZD)=(1,22)`.

### V331. p14/eR23 z8 `(1,22)`, zdeg `(5,1,1,1)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(5,1,1,1)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg5111_row2_orbits.tsv
row2_orbits=45 raw=10887
```

The row3 manifests contain `375` fixed-row leaves.  The fixed-row verifier
closed every leaf.  The combined certificate is:

```text
search23/p14_z8_1_22_zdeg5111_full_fixed_combined.tsv
```

The combined audit gives `375/375` rows with status INFEASIBLE.  This closes
the full zdeg `(5,1,1,1)` subbranch of `(ZZ,ZD)=(1,22)`.

### V332. p14/eR23 z8 `(1,22)`, zdeg `(6,0,0,2)` closed

For the `(ZZ,ZD)=(1,22)` z8 branch with zero-D degree profile `(6,0,0,2)`,
the row2-count orbit manifest is:

```text
search23/p14_z8_1_22_zdeg6002_row2_orbits.tsv
row2_orbits=98 raw=30405
```

The row3 manifests contain `98` fixed-row leaves, one for each row2 branch.
The fixed-row verifier closed every leaf.  The combined certificate is:

```text
search23/p14_z8_1_22_zdeg6002_full_fixed_combined.tsv
```

The combined audit gives `98/98` rows with status INFEASIBLE.  Together with
V315, V321, V324, V329, V330, and V331, this closes all possible zdeg
subbranches of the full `(ZZ,ZD)=(1,22)` category.

### V333. q14/t2 cap74 scalar frontier empty after V332

The scalar audit source

```text
search23/q14_t2_scalar_audit.cpp
```

was updated with the verified cap74 layer closures:

- p16/e_R21: V274, V277, V280, V283, V285, and V286;
- p15/e_R22: V287 and V288;
- p14/e_R23: V289--V332.

After recompiling and rerunning the C++ audit, filtering the output to
`cap=74` gives:

```text
search23/q14_t2_scalar_audit_cap74_latest.tsv
cap74_rows=0
```

Thus, relative to the scalar necessary-condition audit and the recorded
certificates V123 and V202--V332, the q14/t2 cap74 frontier has no remaining
scalar rows.

### V334. High-q low-codegree frontier after q15 and q14/t2 closures

Added the C++ coarse-shape audit

```text
search23/lowcodegree_highq_remaining_audit.cpp
```

which enumerates all low-codegree root shapes with `r0 in {8,9}`,
`t in {1,2,3}`, minimum-degree lower bounds `a,b >= r0-t`, and `q >= 14`.
The compiled audit writes

```text
search23/lowcodegree_highq_remaining_audit.tsv
search23/lowcodegree_highq_remaining_audit.summary.txt
```

and reports:

```text
total_q_ge_14=4
closed_q15=1
closed_q14_t2=1
remaining_q14_t3=2
other_open_or_unaudited=0
```

The four high-q coarse shapes are:

```text
r0  t  a  b  q   status
8   2  6  6  14  CLOSED_Q14_T2_V333
8   3  5  5  15  CLOSED_Q15_V123
8   3  5  6  14  REMAINING_Q14_T3
8   3  6  5  14  REMAINING_Q14_T3
```

Thus V123 and V333 close only two of the four `q >= 14` low-codegree
coarse shapes.  The remaining high-q branch is the asymmetric
`q=14,t=3` case with `(a,b)=(5,6)` or `(6,5)`.  All `r0=9` branches
have `q <= 13` by the same count.

### V335. q14/t3 conservative scalar prefilter is insufficient

Added a conservative scalar prefilter for the remaining asymmetric high-q
branch

```text
t=3, |A|=5, |B|=6, |R|=14
```

at

```text
search23/q14_t3_scalar_prefilter.cpp
```

The prefilter enumerates label-count vectors over all `8` subsets of the
three root common-neighbour colours, including zero labels.  It applies only
safe necessary conditions:

- `|U_i| >= 6` for each `c_i`;
- potential local domination `d_R(r,U_i) >= 3` for every missing colour;
- `p=e(A,B) >= 18`, from the minimum nonedge-codegree condition on `ay`
  and `xb`;
- root-to-R visibility lower bounds on the `A/B-R` incidence count;
- R-degree-sum lower bound `M >= 112-U-2e_R`;
- edge budget `M <= 122-p-U-e_R`;
- label-disjoint capacity upper bound for `e_R`;
- demand lower bounds for `e_R`.

After compiling and running, it reports:

```text
profiles_total=116280
profiles_survive=653
rows_survive=92060
```

with outputs:

```text
search23/q14_t3_scalar_prefilter.tsv
search23/q14_t3_scalar_prefilter.summary.txt
```

Thus the q14/t3 branch is not closed by these scalar conditions alone.  The
next useful certificate should add exact `A/B` state structure, rooted
Phi/Psi cuts, or an R-skeleton/label-edge realization layer, rather than
continuing broad direct rooted SAT.

### V336. q14/t3 exact-state CP-SAT prototype closes first 20 profiles

Added a P-free exact-state CP-SAT verifier:

```text
search23/verify_q14_t3_profile_cpsat.py
```

For a fixed q14/t3 label-count profile, the model chooses:

- the R-edge skeleton subject to label-disjointness, R triangle-freeness, and
  local domination `d_R(r,U_i) >= 3`;
- the five A-states and six B-states as independent subsets of R;
- the induced A-B edge indicators, with the exact law
  `|X_a cap Y_b|=0` iff `ab` is an A-B edge, and
  `|X_a cap Y_b| >= 3` otherwise;
- full R/R edge and nonedge codegree constraints with threshold `3`;
- A/B and R degree lower bounds;
- the global edge budget;
- all rooted Phi/Psi cut inequalities for the q14/t3 branch.

The verifier uses OR-Tools CP-SAT's C++ backend with
`num_search_workers=100`.  The first smoke profile

```text
profile_idx=1894, cnt=0,0,0,3,3,0,0,8
```

closed in `6.069s`.  A first batch over ordinals `0..19` in the surviving
profile list was run with `timeout=30` and `workers=100`, writing

```text
search23/q14_t3_profile_cpsat_first20.tsv
```

All `20/20` tested profiles returned `INFEASIBLE`.

Status: verified computational progress on q14/t3, but not a complete branch
closure.  The remaining profile ordinals `20..652` still need to be checked
or reduced by a stronger profile-level lemma.

### V337. q14/t3 exact-state CP-SAT closes all 653 surviving profiles

The q14/t3 profile-level CP-SAT verifier from V336 was extended across the
full surviving profile frontier from

```text
search23/q14_t3_scalar_prefilter.tsv
```

The frontier contains `653` distinct label-count profiles.  They were checked
in the following batches:

```text
search23/q14_t3_profile_cpsat_first20.tsv
search23/q14_t3_profile_cpsat_20_39.tsv
search23/q14_t3_profile_cpsat_40_79.tsv
search23/q14_t3_profile_cpsat_80_632.tsv
search23/q14_t3_profile_cpsat_563_632_parallel.tsv
search23/q14_t3_profile_cpsat_633_652.tsv
```

The long serial run over `80..632` was stopped after ordinal `562` and resumed
with

```text
search23/run_q14_t3_profile_parallel.py
```

on ordinals `563..632`, using `10` parallel solver processes and
`10` OR-Tools CP-SAT workers per process, for a hard cap of `100` workers.

A profile-index coverage audit against `q14_t3_scalar_prefilter.tsv` found:

```text
profiles=653
results=653
statuses=INFEASIBLE=653
missing_count=0
```

Conclusion: subject to the exact-state model described in V336, the remaining
q14/t3 high-q asymmetric low-codegree branch is closed at the profile level.
Together with V123 for q15 and V333 for q14/t2, the current high-q
low-codegree frontier `q >= 14` has no surviving scalar/profile branch.

Status: VERIFIED COMPUTATIONALLY.  This is not yet a complete `a(30)=36`
proof: the proof assembly still has to audit the reductions into the high-q
frontier and close or bypass the q<=13 low-codegree/direct rooted branches.

### V338. First q<=13 low-codegree branch: r0=9, t=3, q=13 closed

After V337 closed the high-q frontier `q >= 14`, a new coarse manifest was
added:

```text
search23/lowcodegree_qle13_manifest.cpp
search23/lowcodegree_qle13_manifest.tsv
search23/lowcodegree_qle13_manifest.summary.txt
```

For `r0 in {8,9}` and `q <= 13`, the conservative edge/degree audit reports:

```text
total_qle13_shapes=631
edge_survivors=420
```

The highest-q `r0=9` survivor is a single coarse shape:

```text
r0=9, t=3, |A|=6, |B|=6, q=13
```

with conservative lower bounds

```text
min_p=0, min_abR=60, min_cR=21, min_edges=99.
```

A dedicated scalar profile prefilter was added:

```text
search23/q13_t3_r9_scalar_prefilter.cpp
search23/q13_t3_r9_scalar_prefilter.tsv
search23/q13_t3_r9_scalar_prefilter.summary.txt
```

It found:

```text
profiles_total=77520
profiles_survive=94
rows_survive=6169
```

The exact-state CP-SAT verifier

```text
search23/verify_q13_t3_r9_profile_cpsat.py
search23/run_q13_t3_r9_profile_parallel.py
```

uses the q14/t3 model from V336 with the constants adjusted to
`Q=13`, `|A|=|B|=6`, `r0=9`, `t=3`.  It includes:

- R skeleton realization with label-disjointness and R triangle-freeness;
- local domination `d_R(r,U_i) >= 3` for missing colours;
- exact A/B law: intersection `0` iff A-B edge, otherwise intersection at
  least `3`;
- R/R edge and nonedge codegree threshold `3`;
- R vertex degree at least `9`;
- A/B degree constraints `deg_B(a) >= 3`, `deg_A(b) >= 3`, and
  `deg_B(a)+|N_R(a)| >= 8`, `deg_A(b)+|N_R(b)| >= 8`;
- A-C and B-C nonedge codegree cuts
  `|N_R(a) cap U_i| >= 2`, `|N_R(b) cap U_i| >= 2`;
- all rooted Phi/Psi cuts;
- safe symmetry breaking within identical R-label blocks and within the A/B
  sides.

Batch output:

```text
search23/q13_t3_r9_profile_cpsat_0_93.tsv
```

closed `93/94` profiles as `INFEASIBLE` with a `30s` timeout.  The only hard
profile

```text
profile_idx=74088, cnt=6,0,0,0,0,0,0,7
```

was rerun with the A-C/B-C and symmetry cuts:

```text
search23/q13_t3_r9_profile_74088_rerun_sym.txt
```

and returned:

```text
status=INFEASIBLE, sec=245.955
```

Conclusion: the single `r0=9,t=3,q=13,|A|=|B|=6` low-codegree branch is
closed at the same exact-state profile level.

Status: VERIFIED COMPUTATIONALLY.  This narrows q<=13 but does not close it:
the remaining q<=13 manifest still contains lower-q `r0=8,9` coarse shapes.

### V339. q12/r0=9/t=3 asymmetric branch closed

The next highest-q `r0=9` low-codegree branch after V338 has `q=12`.  Among
the q12 survivors, the `t=3` asymmetric pair

```text
|A|=6, |B|=7
```

and its side-swap `|A|=7, |B|=6` were targeted first.

A scalar profile prefilter was added:

```text
search23/q12_t3_r9_a6b7_scalar_prefilter.cpp
search23/q12_t3_r9_a6b7_scalar_prefilter.tsv
search23/q12_t3_r9_a6b7_scalar_prefilter.summary.txt
```

It reports:

```text
profiles_total=50388
profiles_survive=45
rows_survive=1980
```

The exact-state verifier is a thin wrapper around the V338 CP-SAT model with
constants set to `Q=12`, `|A|=6`, `|B|=7`, `r0=9`, `t=3`:

```text
search23/verify_q12_t3_r9_a6b7_profile_cpsat.py
search23/run_q12_t3_r9_a6b7_profile_parallel.py
```

The batch output

```text
search23/q12_t3_r9_a6b7_profile_cpsat_0_44.tsv
```

closed all surviving profiles:

```text
45/45 INFEASIBLE
```

using `10` parallel solver processes and `10` OR-Tools CP-SAT workers per
process.

Conclusion: the q12 `r0=9,t=3` asymmetric branches `(6,7)` and `(7,6)` are
closed at the exact-state profile level.

Status: VERIFIED COMPUTATIONALLY.  The q12 `r0=9,t=2,|A|=|B|=7` branch and
lower-q manifest entries remain open.

### V340. q12/r0=9/t=2 branch: 14 profiles closed, 21 hard profiles isolated

The remaining q12 `r0=9` branch has

```text
t=2, |A|=|B|=7, |R|=12.
```

A scalar prefilter was added:

```text
search23/q12_t2_r9_a7b7_scalar_prefilter.cpp
search23/q12_t2_r9_a7b7_scalar_prefilter.tsv
search23/q12_t2_r9_a7b7_scalar_prefilter.summary.txt
```

It reports:

```text
profiles_total=455
profiles_survive=35
rows_survive=2865
```

The exact-state verifier is again a wrapper around the V338 model, now with
constants `Q=12`, `K=2`, `|A|=|B|=7`, `r0=9`, `t=2`:

```text
search23/verify_q12_t2_r9_a7b7_profile_cpsat.py
search23/run_q12_t2_r9_a7b7_profile_parallel.py
```

A first `30s` batch

```text
search23/q12_t2_r9_a7b7_profile_cpsat_0_34.tsv
```

returned:

```text
14 INFEASIBLE
21 UNKNOWN
```

The `21` unknown profiles were extracted to

```text
search23/q12_t2_r9_a7b7_hard_profiles.tsv
```

and rerun with `timeout=300`, `10` parallel solver processes, and `10`
workers per process:

```text
search23/q12_t2_r9_a7b7_hard_cpsat_0_20.tsv
```

All `21/21` remained `UNKNOWN`.

Conclusion: the current exact-state CP-SAT model closes 14 of the 35 surviving
profiles, but the remaining 21-profile core is a genuine obstruction for this
verifier.  Raising timeout did not produce a new closure; the next step should
add a structural cut for the hard profiles rather than merely increasing
solver time.

Status: PARTIAL VERIFIED COMPUTATION.  Active obstruction: q12/r0=9/t=2,
`|A|=|B|=7`, hard profile set in
`search23/q12_t2_r9_a7b7_hard_profiles.tsv`.

### V341. q12/r0=9/t=2 no-zero scalar obstruction isolated

Date: 2026-06-19.

After V340, the exact-state verifier was strengthened with the missing local
nonedge-codegree constraints:

- same-side `A/A` and `B/B` nonedge codegrees;
- missing `A/R` and `B/R` nonedge codegrees;
- extra safe symmetry breaking for identical `R` labels and A/B state rows;
- complete no-zero propagation cuts for `e_R` at the full S1-S2 capacity:
  all allowed `R`-edges forced, every A/B state sees a D-vertex, and when
  `M` equals the vertex degree lower-bound sum, each `R` vertex load is forced
  to equality.

The first 200 scalar rows from

```text
search23/q12_t2_r9_a7b7_hard_scalar_rows.tsv
```

were rerun with the strengthened verifier (`10` parallel solver processes,
`10` CP-SAT workers each, total `100` workers):

```text
search23/q12_t2_r9_a7b7_scalar_rows_0_199_localcodeg.tsv
```

Result:

```text
165 INFEASIBLE
35 UNKNOWN
0 SAT
```

A representative no-zero complete-skeleton scalar row remained UNKNOWN even
after a longer run:

```text
ordinal=29, idx=40, cnt=(0,3,4,5), p=25, eR=12, M=67
timeout=300s, workers=100 -> UNKNOWN
```

and again after the complete no-zero propagation cuts:

```text
timeout=60s, workers=100 -> UNKNOWN
```

Thus this is not merely a short-timeout artefact.

A C++ skeleton census was added:

```text
search23/q12_t2_nozero_unknown_skeleton_census.cpp
search23/q12_t2_nozero_unknown_skeleton_census.tsv
```

It enumerates the S1-S2 bipartite `R`-skeletons underlying the 35 no-zero
UNKNOWN scalar rows.  Result:

```text
rows=35
total_skeletons=63821
no_tight_skeletons=3929
single_skeleton_rows=9
```

The 9 single-skeleton rows include complete bipartite `K_{3,4}`, `K_{3,5}`,
and `K_{4,4}` S1-S2 skeletons, where there is no degree-2 singleton.  Hence a
pure C-tight singleton / terminal-neighbour equality argument cannot close the
whole no-zero band.

The corrected GPT-Pro consult prompt for this obstruction is:

```text
problems/23/gpt_q12_t2_nozero_unknown_prompt_2026-06-19.md
```

The earlier prompt

```text
problems/23/gpt_q12_t2_r9_hard_profiles_prompt_2026-06-19.md
```

is marked superseded because it incorrectly claimed that each hard profile had
a forced scalar row.

Status: PARTIAL VERIFIED COMPUTATION.  The active obstruction is the
q12/t=2 no-zero scalar band.  The next viable step is a structural lemma or a
P-free state-family certificate for the complete / no-tight S1-S2 skeletons,
not a further blind timeout increase.

### V342. K3,4 no-zero equality row fixed-R audit

Date: 2026-06-19.

The smallest no-tight scalar row from V341 was isolated:

```text
ordinal=29, idx=40, cnt=(0,3,4,5), U=17, p=25, eR=12, M=67.
```

Here the `R`-skeleton is forced to be complete bipartite `K_{3,4}` between
the singleton labels, with 5 isolated doubletons.  The `M=67` value equals the
sum of the individual degree lower bounds:

```text
S1 vertices: m=4 each
S2 vertices: m=5 each
D vertices:  m=7 each
```

Additional safe complete-skeleton propagation was added to the generic
verifier:

- all allowed `S1-S2` R-edges are forced when `fixed_eR` reaches capacity;
- every A/B state sees a D-vertex;
- every complete-skeleton A/B state has no mixed S1/S2 support;
- when `M` equals the vertex lower-bound sum, every R-vertex load is forced
  to equality.

The row nevertheless remained:

```text
timeout=60s, workers=100 -> UNKNOWN
```

A specialized fixed-R CP-SAT verifier was added:

```text
search23/verify_q12_t2_k34_fixed.py
```

It removes R-edge variables and encodes the fixed `K_{3,4}+5D` skeleton
directly.  Results:

```text
with rooted Phi/Psi cuts: timeout=120s, workers=100 -> UNKNOWN
without rooted Phi/Psi cuts: timeout=120s, workers=100 -> UNKNOWN
```

Thus the obstruction is already in the local exact-state constraints, not only
in rooted cut separation.

The fixed-R verifier was then branched on total A-side R-load
`sum_r alpha_r`.  The only possible totals are `31..36`.  Six parallel
branches were run with `16` workers each, total `96` workers:

```text
alpha_sum=31 -> UNKNOWN at 120s
alpha_sum=32 -> UNKNOWN at 120s
alpha_sum=33 -> UNKNOWN at 120s
alpha_sum=34 -> UNKNOWN at 120s
alpha_sum=35 -> UNKNOWN at 120s
alpha_sum=36 -> UNKNOWN at 120s
```

Two exploratory state-family attempts were also made and abandoned as too
coarse:

```text
search23/q12_t2_nozero_k34_state_loads.cpp
  raw side-load multiset enumeration; timeout>120s and killed.

search23/q12_t2_k34_dsubset_dp.cpp
  D-subset DP; A_multisets=10295472, timeout>120s and killed.
```

A smaller D-subset CP-SAT optimization found that D-neighbourhoods alone do
not obstruct `p=25`: it produced a feasible D-level pattern with 49 possible
D-disjoint A-B pairs at 120s.  Hence the missing obstruction must use the
interaction of singleton supports, exact A/B law, and local codegree
constraints.

Status: PARTIAL VERIFIED COMPUTATION.  The next concrete experiment should be
a finer state-family certificate for the fixed `K_{3,4}+5D` row, probably
branching by the actual A-state multiset or by the D-subset pattern together
with singleton-side support, rather than by alpha total alone.

### V343. K3,4 fixed row: A/R-B/R constraints isolated as critical

Date: 2026-06-19.

The specialized fixed-R verifier

```text
search23/verify_q12_t2_k34_fixed.py
```

was extended with switches for three local constraint families:

- R/R codegrees;
- same-side `A/A` and `B/B` codegrees;
- missing `A/R` and `B/R` codegrees.

With rooted Phi/Psi cuts disabled, a relaxation matrix was run with timeout
`60s` and up to `84` total workers.  Results:

```text
noRR+noSame+noARBR -> OPTIMAL in 0.437s
noSame+noARBR      -> OPTIMAL in 0.516s
noRR+noARBR        -> OPTIMAL in 0.694s
noARBR             -> OPTIMAL in 0.758s
noRR+noSame        -> UNKNOWN at 60s
noRR               -> UNKNOWN at 60s
noSame             -> UNKNOWN at 60s
```

Thus the first relaxation that becomes immediately feasible is precisely the
one dropping the missing `A/R` and `B/R` codegree constraints.  The obstruction
is concentrated in A/R-B/R, not in R/R or same-side codegree alone.

The `noARBR` witness was dumped to

```text
search23/q12_t2_k34_noarbr_witness.txt
```

It satisfies the fixed `K_{3,4}+5D` skeleton, exact A/B law, R/R codegree,
same-side codegree, degree/load equalities, and `p=25`, but violates:

```text
8 A/R nonedge-codegree constraints
11 B/R nonedge-codegree constraints
```

An aggregate A/R-B/R coverage cut was added to the fixed verifier.  It is
implied by the individual A/R-B/R constraints:

For every `r in R`,

```text
sum_{a,b} [ab][r in Y_b] + sum_{a,s~r} [s in X_a] >= 2*(7-alpha_r)
sum_{a,b} [ab][r in X_a] + sum_{b,s~r} [s in Y_b] >= 2*(7-beta_r)
```

After adding this aggregate cut, the fixed model still remained:

```text
timeout=120s, workers=100 -> UNKNOWN
alpha_sum=31..36 branches, timeout=120s, total workers=96 -> 6/6 UNKNOWN
```

Status: PARTIAL VERIFIED COMPUTATION.  The next concrete experiment is an
A/R-B/R violation-cover certificate for the `K_{3,4}+5D` row: branch on the
state-family data that determines which missing A/R and B/R incidences can
receive two common neighbours, rather than on alpha total.

### V344. K3,4 no-zero equality row closed by D-alpha branching

Date: 2026-06-19.

The `K_{3,4}+5D` scalar row from V342/V343 is now closed:

```text
ordinal=29, idx=40, cnt=(0,3,4,5), U=17, p=25, eR=12, M=67.
```

The fixed-R verifier

```text
search23/verify_q12_t2_k34_fixed.py
```

was strengthened with:

- equivalent linear forms of the A/R and B/R nonedge-codegree constraints,
  `common >= 2*(1-incidence)`;
- aggregate A/R-B/R coverage cuts;
- a D-alpha branch option, fixing the sorted vector
  `(alpha_d : d in D)`.

For this row each D-vertex has total load `alpha_d+beta_d=7`, so the sorted
D-alpha vector is a 5-tuple with entries in `0..7`.  There are exactly `792`
nonincreasing vectors.

First pass:

```text
search23/q12_t2_k34_dalpha_all.tsv
timeout=30s, jobs=20, workers/job=5, total workers=100
757 INFEASIBLE
35 UNKNOWN
0 SAT
```

Second pass on the 35 hard vectors:

```text
search23/q12_t2_k34_dalpha_hard_180.tsv
timeout=180s, jobs=10, workers/job=10, total workers=100
35 INFEASIBLE
0 UNKNOWN
0 SAT
```

Therefore all `792/792` D-alpha branches are infeasible, proving the fixed
`K_{3,4}+5D` row impossible under the exact local-state constraints.

Status: VERIFIED COMPUTATION for this scalar row.  The next step is to
parameterize this D-alpha branch certificate for the other single-skeleton
no-zero rows, especially `K_{3,5}` and `K_{4,4}` rows in the V341 census.

### V345. K3,5 no-zero row `p=22, M=68` closed

Date: 2026-06-19.

The D-alpha branch certificate from V344 was parameterized as

```text
search23/verify_q12_t2_complete_nozero_fixed.py
```

and first validated against the closed `K_{3,4}+5D` row.

It was then applied to the first `K_{3,5}+4D` single-skeleton row:

```text
cnt=(0,3,5,4), U=16, eR=15, p=22, M=68.
```

There are `330` sorted D-alpha vectors for the four D-vertices.

First pass:

```text
search23/q12_t2_k35_p22_m68_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
324 INFEASIBLE
6 UNKNOWN
0 SAT
```

Second pass on the 6 hard vectors:

```text
search23/q12_t2_k35_p22_m68_dalpha_hard_300.tsv
timeout=300s, jobs=6, workers/job=16, total workers=96
6 INFEASIBLE
0 UNKNOWN
0 SAT
```

Therefore all `330/330` D-alpha branches are infeasible.

Status: VERIFIED COMPUTATION for this scalar row.

### V346. All K3,5 no-zero single-skeleton rows closed

Date: 2026-06-19.

The parameterized complete no-zero fixed verifier

```text
search23/verify_q12_t2_complete_nozero_fixed.py
```

was applied to all `K_{3,5}+4D` single-skeleton rows from the V341 census:

```text
cnt=(0,3,5,4), U=16, eR=15.
```

Rows closed:

```text
p=22, M=68
p=23, M=66..67
p=24, M=64..66
p=25, M=62..65
```

The `p=22, M=68` row was closed in V345.  The remaining rows were run as:

```text
search23/q12_t2_k35_p23_m66_67_dalpha.tsv
search23/q12_t2_k35_p24_m64_66_dalpha.tsv
search23/q12_t2_k35_p25_m62_65_dalpha.tsv
timeout=90s, jobs=20, workers/job=5, total workers=100
```

First pass results:

```text
p=23: 327 INFEASIBLE, 3 UNKNOWN, 0 SAT
p=24: 326 INFEASIBLE, 4 UNKNOWN, 0 SAT
p=25: 326 INFEASIBLE, 4 UNKNOWN, 0 SAT
```

The 11 hard branches were rerun:

```text
search23/q12_t2_k35_p23_25_hard_300.tsv
timeout=300s, jobs=11, workers/job=9, total workers=99
11 INFEASIBLE
0 UNKNOWN
0 SAT
```

Therefore all D-alpha branches for all four `K_{3,5}+4D` single-skeleton
rows are infeasible.

Status: VERIFIED COMPUTATION for these four scalar rows.

### V347. All K4,4 no-zero single-skeleton rows closed

Date: 2026-06-19.

The same parameterized complete no-zero fixed verifier was applied to all
`K_{4,4}+4D` single-skeleton rows from the V341 census:

```text
cnt=(0,4,4,4), U=16, eR=16.
```

Rows closed:

```text
p=23, M=66
p=24, M=64..65
p=25, M=62..64
```

Runs:

```text
search23/q12_t2_k44_p23_m66_dalpha.tsv
search23/q12_t2_k44_p24_m64_65_dalpha.tsv
search23/q12_t2_k44_p25_m62_64_dalpha.tsv
timeout=90s, jobs=20, workers/job=5, total workers=100
```

Each row has `330` sorted D-alpha branches.  Results:

```text
p=23: 330 INFEASIBLE, 0 UNKNOWN, 0 SAT
p=24: 330 INFEASIBLE, 0 UNKNOWN, 0 SAT
p=25: 330 INFEASIBLE, 0 UNKNOWN, 0 SAT
```

Status: VERIFIED COMPUTATION for these three scalar rows.

### V348. The symmetric K4,3 no-zero single-skeleton row is closed

Date: 2026-06-19.

The parameterized complete no-zero fixed verifier was also applied to the
`K_{4,3}+5D` single-skeleton row, the colour-side symmetric counterpart of
V344:

```text
cnt=(0,4,3,5), U=17, eR=12, p=25, M=67.
```

The first pass over all `792` sorted D-alpha branches used:

```text
search23/q12_t2_k43_p25_m67_dalpha.tsv
timeout=30s, jobs=20, workers/job=5, total workers=100
737 INFEASIBLE
55 UNKNOWN
0 SAT
```

The 55 unknown branches were rerun with:

```text
search23/q12_t2_k43_p25_m67_dalpha_hard_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
55 INFEASIBLE
0 UNKNOWN
0 SAT
```

Therefore all D-alpha branches for this `K_{4,3}+5D` row are infeasible.
Together with V344, V346, and V347, all nine single-skeleton no-zero rows in
the V341 census are now closed.

Status: VERIFIED COMPUTATION for this scalar row.

### V349. The K3,5-minus-one-edge no-zero block is closed

Date: 2026-06-19.

The first multi-skeleton no-zero block from the V341 census has
`cnt=(0,3,5,4)`, `U=16`, and an S1-S2 skeleton equal to `K_{3,5}` with one
edge removed.  The census lists 15 labelled skeletons, all equivalent under
the side-preserving symmetry; the representative used was the row-major mask
`011111111111111`.

The new mask-based verifier:

```text
search23/verify_q12_t2_nozero_skeleton_fixed.py
```

was smoke-tested against the complete `K_{3,5}` verifier on a branch where
both returned `INFEASIBLE`.

Rows closed:

```text
eR=14
p=23, M=66..68
p=24, M=64..67
p=25, M=64..66
p=26, M=64..65
```

Runs:

```text
search23/q12_t2_k35_minus1_p23_m66_68_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
328 INFEASIBLE
2 UNKNOWN

search23/q12_t2_k35_minus1_p23_hard_300.tsv
timeout=300s, jobs=2, workers/job=10, total workers=20
2 INFEASIBLE

search23/q12_t2_k35_minus1_p24_26_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
972 INFEASIBLE
18 UNKNOWN

search23/q12_t2_k35_minus1_p24_26_hard_300.tsv
timeout=300s, jobs=9, workers/job=11, total workers=99
18 INFEASIBLE
```

Therefore all `4 * 330 = 1320` D-alpha branches for these four rows are
infeasible.

Status: VERIFIED COMPUTATION for these four scalar rows.

### V350. The K4,4-minus-one-edge no-zero block is closed

Date: 2026-06-19.

The next multi-skeleton no-zero block from the V341 census has
`cnt=(0,4,4,4)`, `U=16`, and an S1-S2 skeleton equal to `K_{4,4}` with one
edge removed.  The census lists 16 labelled skeletons, all equivalent under
the side-preserving symmetry; the representative used was the row-major mask
`0111111111111111`.

Rows closed:

```text
eR=15
p=22, M=68
p=23, M=66..67
p=24, M=64..66
p=25, M=62..65
p=26, M=62..64
```

Runs:

```text
search23/q12_t2_k44_minus1_p22_26_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
1644 INFEASIBLE
6 UNKNOWN

search23/q12_t2_k44_minus1_p22_26_hard_300.tsv
timeout=300s, jobs=6, workers/job=11, total workers=66
6 INFEASIBLE
```

Therefore all `5 * 330 = 1650` D-alpha branches for these five rows are
infeasible.

Status: VERIFIED COMPUTATION for these five scalar rows.

### V351. The K3,5-minus-two-edge no-zero block is closed

Date: 2026-06-19.

The next no-zero block has `cnt=(0,3,5,4)`, `U=16`, `eR=13`, and S1-S2
skeletons equal to `K_{3,5}` with two edges removed.  There are two
side-preserving orbits:

```text
same_row: missing two edges incident with the same S1 vertex
mask 001111111111111

disjoint: missing two edges with distinct S1 and S2 endpoints
mask 011111011111111
```

Rows closed:

```text
p=24, M=66..68
p=25, M=66..67
p=26, M=66
```

First pass:

```text
search23/q12_t2_k35_minus2_p24_26_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
1891 INFEASIBLE
85 UNKNOWN
4 OPTIMAL
```

The four feasible local branches were rerun with rooted cuts:

```text
search23/q12_t2_k35_minus2_optimal_with_cuts.tsv
timeout=300s, jobs=4, workers/job=25, total workers=100
4 INFEASIBLE
```

The 85 unknown branches were rerun with rooted cuts:

```text
search23/q12_t2_k35_minus2_unknown_with_cuts_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
85 INFEASIBLE
```

Therefore all `2 * 3 * 330 = 1980` D-alpha branches for these rows are
infeasible.  This block also shows that the mask-based local verifier needs
the rooted-cut layer for some multi-skeleton branches.

Status: VERIFIED COMPUTATION for these three scalar rows.

### V352. The K4,4-minus-two-edge no-zero block is closed

Date: 2026-06-19.

The next no-zero block has `cnt=(0,4,4,4)`, `U=16`, `eR=14`, and S1-S2
skeletons equal to `K_{4,4}` with two edges removed.  There are three
side-preserving orbits:

```text
same_s1: both missing edges incident with one S1 vertex
mask 0011111111111111

same_s2: both missing edges incident with one S2 vertex
mask 0111011111111111

disjoint: missing edges have distinct S1 and S2 endpoints
mask 0111101111111111
```

Rows closed:

```text
p=23, M=66..68
p=24, M=64..67
p=25, M=64..66
p=26, M=64..65
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k44_minus2_p23_26_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
3946 INFEASIBLE
14 UNKNOWN
0 SAT/OPTIMAL
```

The 14 unknown branches were rerun:

```text
search23/q12_t2_k44_minus2_hard_cuts_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
14 INFEASIBLE
```

Therefore all `3 * 4 * 330 = 3960` D-alpha branches for these rows are
infeasible.

Status: VERIFIED COMPUTATION for these four scalar rows.

### V353. The K3,5-minus-three-edge no-zero row is closed

Date: 2026-06-19.

The remaining `cnt=(0,3,5,4)` no-zero block in the V341 census has `U=16`,
`eR=12`, and S1-S2 skeletons equal to `K_{3,5}` with three edges removed.
There are three side-preserving orbits, represented by:

```text
three_same_s1: mask 000111111111111
two_one_s1:    mask 001111101111111
one_each_s1:   mask 011111011111011
```

The single scalar row is:

```text
p=25, M=68
```

Run:

```text
search23/q12_t2_k35_minus3_p25_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
990 INFEASIBLE
0 UNKNOWN
0 SAT/OPTIMAL
```

Therefore all `3 * 330 = 990` D-alpha branches for this row are infeasible.

Status: VERIFIED COMPUTATION for this scalar row.

### V354. The K4,4-minus-three-edge no-zero block is closed

Date: 2026-06-19.

The next no-zero block has `cnt=(0,4,4,4)`, `U=16`, `eR=13`, and S1-S2
skeletons equal to `K_{4,4}` with three edges removed.  After excluding the
two orbits with a singleton of opposite degree 1, the four valid
side-preserving orbits are:

```text
hook:        mask 0011011111111111
two_same_s1: mask 0011110111111111
two_same_s2: mask 0111011110111111
matching3:   mask 0111101111011111
```

Rows closed:

```text
p=24, M=66..68
p=25, M=66..67
p=26, M=66
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k44_minus3_p24_26_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
3945 INFEASIBLE
15 UNKNOWN
0 SAT/OPTIMAL
```

The 15 unknown branches were rerun:

```text
search23/q12_t2_k44_minus3_hard_cuts_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
15 INFEASIBLE
```

Therefore all `4 * 3 * 330 = 3960` D-alpha branches for these rows are
infeasible.

Status: VERIFIED COMPUTATION for these three scalar rows.

### V355. The K4,4-minus-four-edge no-zero row is closed

Date: 2026-06-19.

The final `cnt=(0,4,4,4)` no-zero block in the V341 census has `U=16`,
`eR=12`, and S1-S2 skeletons equal to `K_{4,4}` with four edges removed.
After enforcing minimum opposite singleton degree at least 2, there are ten
side-preserving orbits, represented by:

```text
o1:  0011001111111111
o2:  0011010111111111
o3:  0011011110111111
o4:  0011011111011111
o5:  0011110011111111
o6:  0011110111011111
o7:  0011110111101111
o8:  0111011110111011
o9:  0111011110111101
o10: 0111101111011110
```

The single scalar row is:

```text
p=25, M=68
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k44_minus4_p25_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
3295 INFEASIBLE
5 UNKNOWN
0 SAT/OPTIMAL
```

The 5 unknown branches were rerun:

```text
search23/q12_t2_k44_minus4_hard_cuts_300.tsv
timeout=300s, jobs=5, workers/job=10, total workers=50
5 INFEASIBLE
```

Therefore all `10 * 330 = 3300` D-alpha branches for this row are
infeasible.  Together with V347, V350, V352, and V354, all no-zero rows with
`cnt=(0,4,4,4)` are closed.

Status: VERIFIED COMPUTATION for this scalar row.

### V356. The K4,5-minus-four-edge eR=16 no-zero block is closed

Date: 2026-06-19.

The first `cnt=(0,4,5,3)` no-zero block has `U=15`, `eR=16`, and S1-S2
skeletons equal to `K_{4,5}` with four edges removed.  After enforcing
minimum opposite singleton degree at least 2, there are twelve side-preserving
orbits.

Rows closed:

```text
p=22, M=68
p=23, M=66..67
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k45_minus4_e16_p22_23_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
2879 INFEASIBLE
1 UNKNOWN
0 SAT/OPTIMAL
```

The single unknown branch was rerun:

```text
search23/q12_t2_k45_minus4_e16_hard_cuts_300.tsv
timeout=300s, workers=25
1 INFEASIBLE
```

Therefore all `12 * 2 * 120 = 2880` D-alpha branches for these rows are
infeasible.

Status: VERIFIED COMPUTATION for these two scalar rows.

### V357. The K4,5-minus-five-edge eR=15 no-zero block is closed

Date: 2026-06-19.

The next `cnt=(0,4,5,3)` no-zero block has `U=15`, `eR=15`, and S1-S2
skeletons equal to `K_{4,5}` with five edges removed.  After enforcing
minimum opposite singleton degree at least 2, there are seventeen
side-preserving orbits.

Rows closed:

```text
p=22, M=68..69
p=23, M=66..68
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k45_minus5_e15_p22_23_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
4043 INFEASIBLE
37 UNKNOWN
0 SAT/OPTIMAL
```

The 37 unknown branches were rerun:

```text
search23/q12_t2_k45_minus5_e15_hard_cuts_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
37 INFEASIBLE
```

Therefore all `17 * 2 * 120 = 4080` D-alpha branches for these rows are
infeasible.

Status: VERIFIED COMPUTATION for these two scalar rows.

### V358. The final K4,5-minus-six-edge no-zero row is closed

Date: 2026-06-19.

The final `cnt=(0,4,5,3)` no-zero block in the V341 census has `U=15`,
`eR=14`, and S1-S2 skeletons equal to `K_{4,5}` with six edges removed.
After enforcing minimum opposite singleton degree at least 2, there are
twenty-nine side-preserving orbits.

The single scalar row is:

```text
p=23, M=66..69
```

First pass with rooted cuts enabled:

```text
search23/q12_t2_k45_minus6_e14_p23_cuts_dalpha.tsv
timeout=60s, jobs=20, workers/job=5, total workers=100
3422 INFEASIBLE
58 UNKNOWN
0 SAT/OPTIMAL
```

The 58 unknown branches were rerun:

```text
search23/q12_t2_k45_minus6_e14_hard_cuts_300.tsv
timeout=300s, jobs=10, workers/job=10, total workers=100
57 INFEASIBLE
1 UNKNOWN
```

The last branch was:

```text
orbit=o5, dalpha=4,4,3
```

and was rerun as:

```text
search23/q12_t2_k45_minus6_e14_single_hard_cuts_900.tsv
timeout=900s, workers=100
INFEASIBLE 134.378s
```

Therefore all `29 * 120 = 3480` D-alpha branches for this row are infeasible.

Together with V344--V358, every no-zero row in the V341 q12/t2 census is
closed by the mask-based finite verifier plus rooted cuts.

Status: VERIFIED COMPUTATION for this scalar row and for the full no-zero
q12/t2 census.

### V359. q13/r0=8/t=3 high-q branches closed

The q13 exact-state verifier was parameterized to cover the r0=8, t=3
survivor triples:

```text
search23/q13_t3_r9_scalar_prefilter.cpp
search23/verify_q13_t3_r9_profile_cpsat.py
search23/run_q13_t3_r9_profile_parallel.py
```

The three scalar prefilters produced the following survivor counts:

```text
r0=8,t=3,A=5,B=7: 257 profiles
r0=8,t=3,A=6,B=6: 256 profiles
r0=8,t=3,A=7,B=5: 256 profiles
```

Exact-state CP-SAT verification results, using at most 100 total workers:

```text
search23/q13_t3_r8_a5b7_profile_cpsat_0_256.tsv
257/257 INFEASIBLE, SAT=0, UNKNOWN=0

search23/q13_t3_r8_a6b6_profile_cpsat_0_255.tsv
249/256 INFEASIBLE, SAT=0, UNKNOWN=7

search23/q13_t3_r8_a6b6_profile_hard_300.tsv
7/7 hard rerun INFEASIBLE, SAT=0, UNKNOWN=0

search23/q13_t3_r8_a7b5_profile_cpsat_0_255.tsv
256/256 INFEASIBLE, SAT=0, UNKNOWN=0
```

Therefore the q13/r0=8/t=3 branches `(A,B)=(5,7),(6,6),(7,5)` are closed
by finite exact-state verification.

Status: VERIFIED COMPUTATION for q13/r0=8/t=3.

### V360. q13/r0=8/t=2 anti-tightness cut and exact-row audit

Active branch:

```text
q=13, r0=8, t=2, A=6, B=7.
```

The scalar prefilter leaves `1427` label-count profiles.  The exact-state
profile verifier

```text
search23/verify_q13_t3_r9_profile_cpsat.py
```

was extended with a safe conditional anti-tightness flag from the q14 reroot
audit:

```text
for r notin U_i:
D(r) + |U_i| + d_R(r,U_i) >= 17,
D(r)=alpha_r+beta_r+d_R(r)+|L(r)|.
```

This is conditional on the already recorded q14/t=2 frontier closure and
deliberately does not impose the rejected experimental terminal equalities.

Important audit: GPT Pro rejected the stronger terminal-reroot closure

```text
d_R(r,U_i)=2 ==> D(r)=8
terminal touched s ==> D(s)=8
```

as mathematically unsupported from the stated q13 assumptions.  Results using
`--terminal-closure` are therefore diagnostic only and are not counted as a
proof certificate.

Safe anti-tightness-only measurements:

```text
search23/q13_t2_r8_a6b7_anti_tightness_hard40_60.tsv
40 UNKNOWN, 0 SAT
```

An exact p/e_R/M row rerunner was added:

```text
search23/run_q13_exact_rows_parallel.py
```

Rerunning the `257` diagnostic hard rows from
`search23/q13_t2_r8_a6b7_row_split_unknown257.tsv`, with terminal equalities
disabled and only `--anti-tightness` enabled, gives:

```text
search23/q13_t2_r8_a6b7_exact_unknown257_anti_30.tsv
5 INFEASIBLE, 252 UNKNOWN, 0 SAT
```

The five safely closed p/e_R/M rows are:

```text
ordinal profile e_R p  M       cnt
60      5212    14  25 55..60  0,0,2,3,4,3,0,1
60      5212    14  24 55..61  0,0,2,3,4,3,0,1
61      5222    14  23 56..63  0,0,2,3,5,2,0,1
61      5222    14  24 56..62  0,0,2,3,5,2,0,1
88      6191    12  27 57..58  0,0,3,2,3,2,0,3
```

To separate scalar effects from A/B-state effects, a five-label R-skeleton
M-lower optimizer was added:

```text
search23/q13_fivelabel_mlower.py
```

It uses only the five-label support, exact `e_R`, local domination, degree
lower bounds, root-side visibility, and the H14 anti-tightness inequality.  On
the same 257 exact rows it reports:

```text
search23/q13_t2_r8_a6b7_exact_unknown257_mlower.tsv
257 OPTIMAL
4 rows closed by M_lower > M_max
253 rows not closed by this scalar lower bound
```

The four scalar M-lower closures are the first four rows above:

```text
profile 5212, e_R=14, p=25, M=55..60, M_lower=62
profile 5212, e_R=14, p=24, M=55..61, M_lower=62
profile 5222, e_R=14, p=23, M=56..63, M_lower=65
profile 5222, e_R=14, p=24, M=56..62, M_lower=65
```

The fifth safe CP-SAT closure

```text
profile 6191, e_R=12, p=27, M=57..58, cnt=0,0,3,2,3,2,0,3
```

has scalar `M_lower=57`, so it is not explained by the R-skeleton lower bound;
it uses the rooted-cut constraints in the exact verifier.

A direct cut-family ablation on this exact row gives:

```text
local constraints only, no anti-tightness: UNKNOWN at 60s
local constraints plus anti-tightness: UNKNOWN at 60s
Phi cuts only, no anti-tightness: UNKNOWN at 60s
Psi cuts only, no anti-tightness: INFEASIBLE in 16.8s
Phi/Psi cuts, no anti-tightness: INFEASIBLE in 18.4s
Phi/Psi cuts plus anti-tightness: INFEASIBLE in 18.3s
```

Thus the fifth safe closure is specifically a `Psi` rooted-cut phenomenon,
not a terminal-reroot or anti-tightness phenomenon.

Class-uniform `Psi` finite certificate:

The verifier was extended with a safe `--class-cuts` option.  This restricts
rooted cut masks to those which are constant on equal-label classes in `R`.
For the five-label rows this is at most `2^5 = 32` `Psi` inequalities, rather
than all `2^13` masks.  This is a subset of the already valid rooted-cut
system, so it introduces no new mathematical assumption.

On the `252` rows left UNKNOWN by the anti-tightness exact-row rerun,

```text
search23/q13_t2_r8_a6b7_classpsi_full252.tsv
```

reports:

```text
8 INFEASIBLE, 244 UNKNOWN, 0 SAT
```

The eight additional class-Psi closures are:

```text
profile e_R p  M       cnt
4965    11  26 55..56  0,0,2,2,2,2,0,5
4999    11  27 57..57  0,0,2,2,3,2,0,4
5222    15  23 54..62  0,0,2,3,5,2,0,1
5222    15  22 54..63  0,0,2,3,5,2,0,1
5344    15  23 54..62  0,0,2,4,4,3,0,0
5344    15  22 54..63  0,0,2,4,4,3,0,0
6165    11  27 57..57  0,0,3,2,2,2,0,4
5350    15  22 55..64  0,0,2,4,5,2,0,0
```

The old `6191, e_R=12, p=27, M=57..58` row also closes with these same
`32` class-uniform `Psi` cuts in `13.9s`.  Thus the useful rooted-cut pressure
is already visible at label-class level, though it is still too weak to close
the whole q13/t=2 core.

Isolated-support finite certificate:

The verifier was extended with a safe `--isolated-support` option.  In this
five-label branch every `T={1,2,3}` vertex is R-isolated.  For an isolated
vertex `t` and any other R-vertex `r`, the added projected constraints are:

```text
if B_r \ B_t is nonempty, then |A_t \ A_r| >= 2,
if A_r \ A_t is nonempty, then |B_t \ B_r| >= 2.
```

Proof: if `b in B_r \ B_t`, then the nonedge `(b,t)` needs two common
neighbours.  Since `t` is R-isolated, these common neighbours cannot be roots,
`C`, `B`, or R-vertices; they must be A-vertices adjacent to both `b` and `t`.
If such an A-vertex also lay in `A_r`, then the exact A/B law would make the
corresponding `ab` pair a nonedge through the common R-neighbour `r`.  Hence
the two witnesses lie in `A_t \ A_r`.  The other side is symmetric.  This is a
projection of the existing A/R and B/R nonedge-codegree constraints plus the
exact A/B law; it adds no terminal-reroot assumption.

On the `244` rows left UNKNOWN by class-uniform `Psi`,

```text
search23/q13_t2_r8_a6b7_iso_classpsi_full244.tsv
```

reports:

```text
2 INFEASIBLE, 242 UNKNOWN, 0 SAT
```

The two additional isolated-support closures are:

```text
profile e_R p  M       cnt
6170    11  27 58..58  0,0,3,2,2,3,0,3
6165    11  26 57..58  0,0,3,2,2,2,0,4
```

Full-`Psi` and mixed-codegree projection audit:

The verifier was extended with two further safe flags:

```text
--mixed-codegree-aggregate
--mixed-codegree-projection[-scope isolated|all]
```

The aggregate mixed-codegree cut is:

```text
B_r \ B_t nonempty => |A_t \ A_r| + |N_R(t) \ N_R(r)| >= T,
A_r \ A_t nonempty => |B_t \ B_r| + |N_R(t) \ N_R(r)| >= T.
```

It is the skeleton-level projection of the same missing B/R and A/R
codegree constraints used for isolated-support.  It does not use any
terminal-reroot equality.  The witness-resolved all-vertex variant was also
implemented, but on the `6191` smoke row it slowed the solver enough to return
UNKNOWN at a 30s timeout; it is not currently useful as a batch setting.

Measurements:

```text
search23/q13_t2_r8_a6b7_iso_fullpsi_full242.tsv
2 INFEASIBLE, 240 UNKNOWN, 0 SAT

search23/q13_t2_r8_a6b7_aggregate_classpsi_full244.tsv
2 INFEASIBLE, 242 UNKNOWN, 0 SAT

search23/q13_t2_r8_a6b7_aggregate_fullpsi_full242.tsv
1 INFEASIBLE, 241 UNKNOWN, 0 SAT
```

The full-`Psi` plus isolated-support closures are:

```text
profile e_R p  M       cnt
4999    12  26 55..57  0,0,2,2,3,2,0,4
6165    12  26 55..57  0,0,3,2,2,2,0,4
```

The aggregate mixed-codegree class-`Psi` closures are:

```text
profile e_R p  M       cnt
5190    11  27 58..58  0,0,2,3,3,2,0,3
5212    14  23 55..62  0,0,2,3,4,3,0,1
```

Combining aggregate mixed-codegree with full `Psi` masks, without
isolated-support, only recovers:

```text
profile e_R p  M       cnt
4999    12  26 55..57  0,0,2,2,3,2,0,4
```

This row was already closed by full-`Psi` plus isolated-support.  Thus the
aggregate and full-`Psi` effects do not combine into a substantially stronger
batch certificate at the current 60s row timeout.

Thus the three post-class-`Psi` experiments close six distinct additional
exact rows, but they do not break the q13/t=2 core:

```text
4999  eR=12 p=26 M=55..57
5190  eR=11 p=27 M=58..58
5212  eR=14 p=23 M=55..62
6165  eR=11 p=26 M=57..58
6165  eR=12 p=26 M=55..57
6170  eR=11 p=27 M=58..58
```

Current conclusion: anti-tightness is valid and nonempty, but it is too weak
to close the q13/t=2 core.  Isolated-support, full-`Psi`, and aggregate
mixed-codegree projection are all safe and nonempty, but still insufficient.
The remaining hard rows are still concentrated in the five-label support
`c0=c1=c6=0`, i.e. labels `{2},{1,2},{3},{1,3},{1,2,3}`, with R-edges only in
the blocks `S2-D13`, `D12-S3`, and `S2-S3`.  A stronger P-free skeleton/state
cut is still needed.

Status: VERIFIED COMPUTATION for the five safe row closures; q13/r0=8/t=2
remains OPEN.

### V361. q13/r0=8/t=2 post-cut remainder and top-family skeleton audit

After taking the union of the safe post-class-`Psi` closures from isolated
support, full-`Psi`, and aggregate mixed-codegree projection, the remaining
exact rows are:

```text
search23/q13_t2_r8_a6b7_postcuts_remaining.tsv
238 UNKNOWN rows
25 distinct cnt families
```

The family summary is recorded in:

```text
search23/q13_t2_r8_a6b7_postcuts_family_summary.txt
```

The largest remaining family is:

```text
cnt = 0,0,3,2,3,3,0,2
profile = 6195
20 exact rows
e_R = 12..21, p = 16..26, M_min = 49..59, M_max = 60..61
```

A direct test of the full witness-resolved mixed-codegree projection on this
largest family was diagnostic but did not close rows:

```text
search23/q13_t2_r8_a6b7_topfamily_6195_witness_full_45.tsv
0 INFEASIBLE, 20 UNKNOWN, 0 SAT
timeout=45s, total workers <=100
```

Thus the all-vertex witness projection is currently too expensive for batch
closure and should not be treated as the next proof engine.

To inspect whether the remaining difficulty is the R-skeleton or the A/B
state layer, a small C++ R-skeleton counter was added:

```text
search23/count_q13_fivelabel_skeletons.cpp
```

For the largest family it reports:

```text
search23/q13_t2_family_6195_skeleton_counts.txt
allowed_edges = 24
all_skeletons = 16777216
local_skeletons = 17408

e_R count
12  6
13  72
14  387
15  1234
16  2601
17  3816
18  3990
19  2988
20  1584
21  576
22  135
23  18
24  1
```

This is a verified finite count of local R-skeletons for the top family, not
a proof of infeasibility.  It indicates that the hard part of the remaining
top family is no longer R-skeleton generation; the next useful finite
certificate should fix or enumerate these small skeleton sets and attack the
A/B state and rooted-cut layer directly.

Follow-up fixed-skeleton audit:

The exact verifier was extended with a diagnostic `--fixed-r-mask` option,
which fixes the allowed R-edge variables to one enumerated skeleton.  For the
six local `e_R=12` skeletons in the largest family, the two corresponding
exact rows are:

```text
p=25, M=58..61
p=26, M=58..60
```

Running all `6 x 2 = 12` fixed-skeleton cases gives:

```text
search23/q13_t2_family_6195_er12_fixedmask_verify.tsv
0 INFEASIBLE, 12 UNKNOWN, 0 SAT
timeout=60s per fixed skeleton, workers=100
```

So merely fixing the R-skeleton is not enough to produce a small certificate
with the current A/B-state verifier.  The next cut must strengthen the state
or rooted-cut layer for a fixed skeleton, not just reduce the R-skeleton
search.

GPT Pro then suggested fixed-`P`-free A/B nonedge-rectangle projection cuts:

```text
Q_r = A_r x B_r,  q_r = |Q_r| = alpha_r beta_r,
o_rs = |Q_r cap Q_s|.

Wedge: if rs,rt in E(R), then q_r + q_s + q_t - o_st <= 36-p.

Complete block: if a forced complete R-block P x Q occurs, then
sum_{v in P union Q} q_v
  - sum_{u<v in P} o_uv
  - sum_{u<v in Q} o_uv
<= 36-p.

Global moment:
sum_r q_r >= 2(36-p),
sum_{r<s} o_rs >= sum_r q_r - (36-p).
```

These were added to the verifier as safe diagnostic flags:

```text
--rectangle-wedge-cuts
--rectangle-complete-block-cuts
--rectangle-global-cuts
```

They are projections of the exact A/B state law and triangle-freeness, not
new terminal-reroot assumptions.

High-`p` audit on the `49` remaining rows with `p >= 25`:

```text
search23/q13_t2_r8_a6b7_pge25_rect_wedge_30.tsv
0 INFEASIBLE, 49 UNKNOWN, 0 SAT

search23/q13_t2_r8_a6b7_pge25_rect_complete_global_30.tsv
0 INFEASIBLE, 49 UNKNOWN, 0 SAT

search23/q13_t2_r8_a6b7_pge25_rect_all_30.tsv
0 INFEASIBLE, 49 UNKNOWN, 0 SAT
```

Thus the rectangle projections are mathematically safe and implemented, but
at the current 30s row timeout they do not close the high-`p` remainder.  The
q13/t=2 core needs a sharper state separator or a more specialized
fixed-skeleton certificate.

Additional structural lemma for the top family, `e_R=12`:

For

```text
cnt = 0,0,3,2,3,3,0,2
labels: |S2|=3, |D12|=2, |S3|=3, |D13|=3, |T|=2
e_R = 12
```

local domination alone forces the R-skeleton up to relabeling:

```text
R[D12,S3] = K_{2,3}
R[S2,D13] = K_{3,3} minus a perfect matching
R[S2,S3] = empty
T isolated
```

Proof: because `|D12|=2`, every `S3` vertex needs two `D12` neighbours, so
`R[D12,S3]=K_{2,3}` and contributes `6` edges.  The total `e_R` is `12`, so
only `6` edges remain for the `S2-D13` and `S2-S3` blocks.  Local domination
requires every `S2` vertex to have at least two `D13` neighbours and every
`D13` vertex to have at least two `S2` neighbours, already forcing at least
`6` edges in `S2-D13`.  Hence there are exactly these `6` edges, no optional
`S2-S3` edge, and the bipartite `S2-D13` graph has all degrees exactly `2`,
so it is `K_{3,3}` minus a perfect matching.

The six local `e_R=12` masks in
`search23/q13_t2_family_6195_er12_masks.txt` are exactly the six choices of
that missing perfect matching.

Status: RIGOROUS-INFORMAL structural lemma, verified against the enumerated
masks.

### V362. q13/r0=8/t=2 state-separator capacity audit

GPT Pro response saved at:

```text
problems/23/gpt_pro/q13_t2_state_separator_response_20260619.md
```

It identified the next safe projection as state-separator capacity, targeting
the A/B edge side of the exact state law rather than only the A/B nonedge
rectangles.  The verifier now has:

```text
--state-separator-capacity
--state-separator-minimal-fixed-r
```

The first flag adds the static five-label separators:

```text
D13 union T, when |D12|=2 or |S3|=2
D12 union T, when |S2|=2 or |D13|=2
```

For a separator `K`, the added per-state cuts are:

```text
d_P(a) <= sum_{r in K \ X_a} beta_r
|X_a| + sum_{r in K \ X_a} beta_r >= 7

d_P(b) <= sum_{r in K \ Y_b} alpha_r
|Y_b| + sum_{r in K \ Y_b} alpha_r >= 7
```

These are projections of the existing exact A/B edge law and the usual
`r0=8` A/B vertex degree inequality; they do not use the invalid
terminal-degree reroot equality.

Pass A on all `238` postcut rows:

```text
search23/q13_t2_postcuts_state_separator_45.tsv
timeout=45s, jobs=20, workers/job=5, total workers <=100
4 INFEASIBLE, 234 UNKNOWN, 0 SAT
```

Newly closed rows:

```text
profile 4971: cnt=0,0,2,2,2,3,0,4, e_R=12, p=26, M=54..56
profile 5164: cnt=0,0,2,3,2,2,0,4, e_R=12, p=26, M=54..56
profile 5190: cnt=0,0,2,3,3,2,0,3, e_R=11, p=26, M=58..59
profile 6198: cnt=0,0,3,2,3,4,0,1, e_R=14, p=23, M=55..62
```

For the top family `6195`, the `--state-separator-minimal-fixed-r` mode
computes inclusion-minimal legal-state transversals directly from a fixed
R-mask.  For canonical mask `0xfd8a30` it reports:

```text
state_separators=8
```

This independently verifies the GPT Pro "eight separator" classification for
the canonical `e_R=12` skeleton.

Canonical `6195/e_R=12` exact-case run:

```text
search23/q13_t2_family_6195_er12_canonical_minsep_7cases_120.tsv
fixed_r_mask=0xfd8a30
timeout=120s, jobs=7, workers/job=14, total workers <=98
4 INFEASIBLE, 3 UNKNOWN, 0 SAT
```

Closed exact cases:

```text
p=25, M=58
p=25, M=59
p=26, M=58
p=26, M=59
```

Remaining canonical `e_R=12` high-M cases:

```text
p=25, M=60
p=25, M=61
p=26, M=60
```

Thus state-separator capacity is a real safe strengthening, but it does not
yet close the high-M top-family residual.  The next proof-grade step should be
the canonical fixed-skeleton state-table SAT/certificate architecture proposed
by GPT Pro if these high-M cases remain UNKNOWN under longer runs.

Status: VERIFIED COMPUTATION for the remainder audit, top-family skeleton
count, and state-separator capacity audit; q13/r0=8/t=2 remains OPEN.

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
- 100-worker pilot:
  `search23/campaign_rooted_r4_9_e109_139_w100_c20k_20260618_233808`
  ran `r=4..9`, `e=109..139` with 20 rounds and a 20k conflict limit.  It
  completed all `149` slices in about 79 seconds with `149/149` INCONCLUSIVE,
  no UNSAT certificate, and no SAT counterexample.
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
- Rooted 30-vertex lazy-cut pilot with 100 workers and settings
  `r=4..9`, `e=109..139`, 20 rounds, 20k conflicts returned `149/149`
  INCONCLUSIVE.  This setting is useful as a diagnostic but is not a viable
  proof engine without stronger structural cuts or a sharper branch split.

## Open subgoals

1. Prove rooted branches `r=4..9`, preferably by degree-sequence/stability
   reductions before further computation.
2. If `a(30)` certificate succeeds, write and verify a second finite exact
   value.
3. If it fails or stalls, extract structural information from hard candidates
   and formulate the missing medium-density stability theorem.
4. For the low-codegree route, q=15 is closed by V123, q14/t=2 by V333, and
   q14/t=3 by V337.  Remaining work is proof assembly/audit of the reductions
   feeding into the high-q frontier, plus q<=13 or the direct rooted branches;
   it is not yet a standalone final theorem statement.

## V363. q13/r0=8/t=2 canonical high-M count-state audit

Date: 2026-06-19.

Context: canonical profile `6195`, `eR=12`, fixed mask `0xfd8a30`, after
V362 state-separator capacity cuts.  The already closed exact cases are
`(p,M)=(25,58),(25,59),(26,58),(26,59)`.  The remaining high-M cases are
`(25,60)`, `(25,61)`, and `(26,60)`.

Implemented `search23/state_count_6195_cpsat.py`, a count/multiset CP-SAT
prototype over the `648` legal fixed-R state types.  The model uses integer
A/B state multiplicities, exact `M`, exact `p` through typewise disjoint
products, intersection-one forbiddance, per-state A/B degree constraints,
same-side A/A and B/B projected codegrees, A/R and B/R projected codegrees,
R/R codegrees, anti-tightness, and all `8192` Psi masks.

Runs with `100` workers and `600s` timeout:

- `p=25, M=60`: `UNKNOWN`, `sec=636`, `states=648`.
- `p=25, M=61`: `UNKNOWN`, `sec=632`, `states=648`.
- `p=26, M=60`: `UNKNOWN`, `sec=640`, `states=648`.

GPT Pro was consulted in the in-app browser.  Response saved at
`problems/23/gpt_pro/q13_t2_state_count_quotient_response_20260619.md`.
Its verdict: the state-count quotient is a sound row-permutation quotient if
typewise products and all active same-shore type-pair constraints are exact;
no 6-by-6 matching variable is needed.  The recommended next strengthening is
weighted quotient cut separation over state types, plus small column-excess
branches.  For the canonical skeleton the column degree floors sum to `58`,
so the high-M cases have total excess `2` for `M=60` and `3` for `M=61`,
giving `91` raw excess-two and `455` raw excess-three branches before
automorphism quotienting.

Status: VERIFIED COMPUTATION for the count-state audit; no high-M case closed.
Next frontier: implement weighted quotient cut separation and excess-profile
branching, then rerun the three high-M cases before fixed A/B template
enumeration.

## V364. q13/r0=8/t=2 high-M excess-branch audit

Date: 2026-06-19.

Implemented two further state-count improvements for the canonical profile
`6195`, `eR=12`, fixed mask `0xfd8a30`:

- `search23/state_count_6195_cpsat.py`: compressed exact `p` counting from
  all disjoint state-pair products to one product per A-state, added optional
  `--excess-vector`, and added a lazy weighted quotient-cut separator hook.
- `search23/run_state_count_6195_excess_parallel.py`: parallel excess-vector
  runner with total worker control.

Verification:

- Refactored full `p=25, M=60` count-state run with `100` workers and `600s`
  still returned `UNKNOWN` (`sec=649`, `states=648`, `floors=58`).
- Exhaustive excess-two branching for `p=25, M=60` was run over all `91`
  raw excess vectors using `10 x 10` workers and `300s` per branch:
  `10 INFEASIBLE`, `81 UNKNOWN`.
  Outputs:
  `search23/q13_t2_6195_p25_m60_excess2_qcut_limit20_300.tsv` and
  `search23/q13_t2_6195_p25_m60_excess2_qcut_offset20_300.tsv`.

Closed excess vectors:

- `0,0,0,0,0,0,0,0,0,0,2,0,0`
- `0,0,0,0,0,0,0,0,0,2,0,0,0`
- `0,0,0,0,0,0,0,0,2,0,0,0,0`
- `0,0,1,0,0,0,0,0,1,0,0,0,0`
- `0,0,1,0,0,0,0,0,0,1,0,0,0`
- `0,1,0,0,0,0,0,0,0,0,1,0,0`
- `0,1,0,0,0,0,0,0,1,0,0,0,0`
- `0,2,0,0,0,0,0,0,0,0,0,0,0`
- `1,0,0,0,0,0,0,0,0,1,0,0,0`
- `2,0,0,0,0,0,0,0,0,0,0,0,0`

The lazy weighted quotient separator did not add cuts in these branch runs
because branch masters generally timed out before producing a candidate
(`quotient_cuts=0` in completed rows).  Thus the next frontier is not the
validity of quotient cuts but search strategy: find count candidates faster or
encode a static quotient-cut/outer-pattern family rather than waiting for lazy
FEASIBLE candidates.

Automorphism audit of the fixed R-skeleton:

- The automorphism group preserving labels and the fixed mask has size `144`.
- The `91` raw excess-two vectors form `21` orbits.
- The `10` raw closed vectors cover `3` full orbits, i.e. `12` raw vectors by
  symmetry.
- Remaining: `18` excess-two orbits, `79` raw vectors.

Status: VERIFIED COMPUTATION.  New fact: three excess-two orbits are closed;
`18` excess-two orbits for `p=25, M=60` remain unresolved.

## V365. q13/r0=8/t=2 quotient-separator implementation audit

Date: 2026-06-19.

Attempted the `18` unresolved excess-two orbit representatives for
`p=25, M=60` with `6 x 16` workers and `900s` per representative using
`--quotient-cut-rounds 2`.

The run was aborted manually after the first wave exceeded the expected
CP-SAT wall-time without output.  Process inspection showed the child
`state_count_6195_cpsat.py` jobs were still live after likely producing
candidate count solutions.  The bottleneck is the pure-Python lazy weighted
quotient separator: it enumerates too many quotient side assignments after a
candidate and can dominate the CP-SAT timeout.

All Python processes were killed cleanly.  No proof result is claimed from this
aborted run.  The mathematical quotient-cut family remains valid; the current
implementation is not yet a practical proof engine.

Next required implementation step: replace or guard the separator with a
bounded/optimized version, preferably the min-cut/flow formulation from GPT
Pro, before rerunning the unresolved orbit representatives.

## V366. q13/r0=8/t=2 guarded quotient-separator rerun

Date: 2026-06-19.

Patched `search23/state_count_6195_cpsat.py` so the lazy weighted quotient
separator:

- returns immediately when it finds any valid violating quotient cut
  (`mono < 37`);
- has a per-separation wall-time guard via
  `--quotient-separator-timeout`;
- reports `quotient_timeouts` and `quotient_checked_outer`.

Also patched `search23/run_state_count_6195_excess_parallel.py` to forward the
separator timeout to child solvers.

Verification:

- `python -m py_compile search23\state_count_6195_cpsat.py`
- `python -m py_compile search23\run_state_count_6195_excess_parallel.py`
- smoke run:
  `python search23\state_count_6195_cpsat.py --p 25 --m 60 --timeout 5 --workers 10 --quotient-cut-rounds 1 --quotient-separator-timeout 1`
  returned `UNKNOWN`, `quotient_cuts=0`, `quotient_timeouts=0`.
- runner smoke over two unresolved orbit representatives wrote
  `search23/tmp_smoke_excess_runner.tsv`, both `UNKNOWN`.

Then reran the `18` unresolved excess-two orbit representatives for
`p=25, M=60`:

```
python search23\run_state_count_6195_excess_parallel.py \
  --p 25 --m 60 --timeout 600 \
  --jobs 6 --workers-per-job 16 \
  --quotient-cut-rounds 2 --quotient-separator-timeout 20 \
  --vectors-file search23\q13_t2_6195_p25_m60_excess2_unresolved_orbit_reps.txt \
  --out search23\q13_t2_6195_p25_m60_excess2_orbit_reps_guarded_600.tsv
```

Result:

- `18/18 UNKNOWN`;
- every completed row reports `quotient_cuts=0`, `quotient_timeouts=0`,
  `quotient_checked_outer=0`;
- no `SAT` count candidate was produced;
- no child process remained after the run.

Interpretation: the previous runaway separator failure is fixed, but these
orbit representatives do not reach a candidate count solution under the
current typewise count model within `600s`.  The active obstruction is now the
strength of the master model, not lazy quotient separation.  Continuing this
same run shape with more blind timeout is unlikely to produce a verified new
fact; the next concrete move should be either:

1. implement a static/projected quotient-cut encoding (preferably the small
   min-cut/flow formulation) inside the master rather than waiting for lazy
   candidates; or
2. ask GPT Pro for a structural cut targeted specifically at the `18` remaining
   excess-two orbit representatives.

Status: VERIFIED COMPUTATION.  New fact: the guarded separator no longer
hangs, and all `18` remaining excess-two orbit representatives are still
`UNKNOWN` at `600s` with the current count master.

## V367. q13/r0=8/t=2 C6 projection bound for 6195 high-M orbits

Date: 2026-06-19.

GPT Pro proposed a smaller projection certificate for the fixed `6195`
(`mask=0xfd8a30`) skeleton.  Let

```
X = S2 = {0,1,2}
H = D13 = {8,9,10}.
```

The induced `R[X,H]` graph is `K_{3,3}` minus a perfect matching, hence a
6-cycle in the complement sense relevant to independent projected states.
Project each `A/B` state to its intersection with `X union H`.  There are
exactly `18` legal projected states: all subsets of `X`, all subsets of `H`,
with the empty set identified, plus the three missing-pair states.  For each
missing pair `Omega_i`, the `R/R` nonedge codegree constraint gives

```
a_{Omega_i} + b_{Omega_i} >= 2.
```

The projected `A-B` edge count

```
p_XH = sum_{S cap T = empty} a_S b_T
```

is an upper bound for the true `p`, since full disjointness implies projected
disjointness.

Implemented an independent C++ verifier:

```
search23/verify_c6_projection_6195.cpp
```

It derives the `R`-skeleton from the given mask, derives the `X,H` sets from
the labels, derives the missing matching, enumerates all `6`-multisets of the
`18` projected states on each shore (`100947` per shore), groups them by the
six projected column sums, and maximizes `p_XH` subject to the projected column
sums and the three `Omega_i` coverage constraints.

Verification command:

```
g++ -O3 -std=c++20 search23\verify_c6_projection_6195.cpp -o search23\verify_c6_projection_6195.exe
.\search23\verify_c6_projection_6195.exe
```

Default-mask output summary:

```
local_vertices=0,1,2,8,9,10
projection_types=18
omega_indices=9,11,14
shore_multisets=100947
listed_worst=21
universal_targets=84
universal_infeasible=66
universal_worst=21
universal_arg_target=5,5,5,4,4,4
RESULT PASS pXH<=21
```

The checker also writes audit tables:

- `search23/verify_c6_projection_6195_types.tsv`
- `search23/verify_c6_projection_6195_listed.tsv`
- `search23/verify_c6_projection_6195_universal.tsv`

The same checker was then run over all six `e_R=12` masks for profile `6195`:

```
0xfd8a30
0xfd8c28
0xfe8630
0xfe8c18
0xff0628
0xff0a18
```

Each run returned:

```
projection_types=18
listed_worst=21
universal_worst=21
RESULT PASS pXH<=21
```

Per-mask outputs were saved as
`search23/verify_c6_projection_6195_0x*.txt`.

The `18` listed unresolved excess-two orbit representatives all satisfy
`max p_XH <= 21` under the projection constraints.  More strongly, all
projected target vectors with total excess at most `3` over the base
`(5,5,5,4,4,4)` satisfy `max p_XH <= 21`; `66/84` projected targets are
already infeasible.

Consequence: for every `e_R=12` mask in this `6195` skeleton family, any row requiring
`p >= 25` (in particular the active high-M rows `(p,M)=(25,60)`, `(26,60)`,
and `(25,61)` under this projected excess regime) is impossible before fixed
`A-B` template enumeration.

Status: VERIFIED COMPUTATION / PENDING PROOF PACKAGING.  The next step is to
turn this projection enumerator into a proof-grade finite certificate or a
small standalone lemma with a reproducible checked table.

## V368. q13/r0=8/t=2 profile 6195 eR=12 high-M row closed

Date: 2026-06-19.

V363 recorded seven canonical high-M exact cases for profile `6195`, `e_R=12`:

```
(p,M)=(25,58),(25,59),(25,60),(25,61),
      (26,58),(26,59),(26,60).
```

The four low-M cases `(25,58)`, `(25,59)`, `(26,58)`, `(26,59)` were already
closed by the V363 count-state audit.  V367 closes the three remaining cases
`(25,60)`, `(25,61)`, and `(26,60)`: for every `e_R=12` mask in the `6195`
family, the `C6` projection gives `p <= p_XH <= 21`, contradicting `p >= 25`.

Closure manifest:

```
search23/q13_t2_family_6195_er12_closure_v367.tsv
```

Additional generalized checker audit:

```
g++ -O3 -std=c++20 search23\verify_projection_6195_row.cpp -o search23\verify_projection_6195_row.exe
```

Running this generalized projection checker on the same six `e_R=12` masks
with `p_threshold=25` and `max_total_excess=3` reproduced the closure:

```
search23/verify_projection_6195_er12_general.tsv
```

Result: `6/6 CLOSE`, with `worst_p_proj=21` in every mask.

Status: VERIFIED COMPUTATION.  The profile `6195`, `e_R=12` high-M canonical
row is closed.  This does not close the whole `6195` support family; the
`e_R=13..21` rows remain separate frontier items unless covered by other
recorded lemmas.

## V369. q13/r0=8/t=2 profile 6195 eR=13 projection audit

Date: 2026-06-19.

Used the generalized projection checker

```
search23/verify_projection_6195_row.cpp
```

on all `72` profile-`6195` local skeleton masks with `e_R=13`, dumped by

```
search23/count_q13_fivelabel_skeletons.exe "0,0,3,2,3,3,0,2" 13
```

Rows tested:

```
p=24, max_total_excess=5
p=25, max_total_excess=5
```

Output:

```
search23/verify_projection_6195_er13.tsv
```

Summary:

```
p=24: 54 CLOSE, 18 OPEN
p=25: 54 CLOSE, 18 OPEN
```

The open masks are the same structural class in both rows.  Extracted table:

```
search23/verify_projection_6195_er13_open.tsv
```

For every open entry:

```
projection_types=17
need_pairs=2
worst_p_proj=28
```

Interpretation: the `C6`-style projection certificate closes three quarters
of the `e_R=13` mask cases for `p=24,25`, but it does not close the row.  The
remaining obstruction is a smaller projected class with only two forced
projected `R/R` pair-cover constraints and a projected upper bound as high as
`28`.  A stronger projection or an additional structural lemma is required
for these `18` masks.

Representative open mask inspection:

```
search23/inspect_6195_projection_mask_0xfd8a38.txt
search23/verify_projection_6195_0xfd8a38_witness.txt
```

For `mask=0xfd8a38`, the local edges between `X={0,1,2}` and `H={8,9,10}`
are:

```
0-8, 0-9, 0-10,
1-8, 1-10,
2-8, 2-9.
```

So only `(1,9)` and `(2,10)` are missing X-H pairs with projected codegree
need `2`.  The `p_proj=28` witness occurs already at the floor target
`(4,5,5,3,4,4)` and has projected multiplicities:

```
A: {0,2}^1, {0,1,2}^1, {2,10}^3, {8,10}^1
B: {0,1}^2, {1,9}^2, {8,9}^2
```

This witness is not a full model.  It is the obstruction showing exactly why
the current projection certificate is too weak: the two missing-pair cover
constraints alone allow too many projected disjoint A-B pairs.

Status: VERIFIED COMPUTATION / PARTIAL CLOSURE.  No full `e_R=13` row closure
is claimed.

## V370. q13/r0=8/t=2 profile 6195 eR=13 high-p row closed

Date: 2026-06-19.

Strengthened the generalized projection checker

```
search23/verify_projection_6195_row.cpp
```

by adding projected typewise necessary filters.  For a projected A-type `I`,
the number of projected-disjoint B-types is an upper bound for the true
number of B-neighbours of any lift of `I`; hence it must be at least `2`.
Similarly, for a local projected vertex `r notin I`, the quantity

```
|I cap N_R(r) in the projection|
  + #{projected-disjoint B-types containing r}
```

is an upper bound for the A/R codegree contribution visible through this
projection, so it must be at least `2` for a lift to exist.  The symmetric
conditions are imposed for B-types.  These are necessary conditions only, so
they safely strengthen the projected relaxation without enumerating a fixed
`A-B` template.

Audit on the representative open mask `0xfd8a38`:

```
search23/verify_projection_6195_0xfd8a38_typewise_witness.txt
```

The previous `p_proj=28` witness is eliminated.  The strengthened checker
returns:

```
worst_p_proj=20
result=CLOSE
```

Then reran all `72` profile-`6195`, `e_R=13` masks for:

```
p=24, max_total_excess=5
p=25, max_total_excess=5
```

Output:

```
search23/verify_projection_6195_er13_typewise.tsv
```

Summary:

```
p=24: 72 CLOSE, 0 OPEN
p=25: 72 CLOSE, 0 OPEN
```

Closure manifest:

```
search23/q13_t2_family_6195_er13_closure_v370.tsv
```

This closes the profile `6195`, `e_R=13` high-p rows:

```
(e_R,p,M) = (13,24,56..61)
(e_R,p,M) = (13,25,56..60)
```

Status: VERIFIED COMPUTATION.  The profile `6195`, `e_R=13` high-p rows are
closed by a P-free projected typewise certificate.

## V371. q13/r0=8/t=2 profile 6195 eR=14 projection reduction

Date: 2026-06-19.

Built a parallel wrapper for the existing projected typewise checker:

```
search23/run_verify_projection_6195_batch.cpp
search23/run_verify_projection_6195_batch.exe
```

The wrapper ran the profile-`6195`, `e_R=14` masks using:

```
mask file: search23/q13_t2_family_6195_er14_masks.txt
p values: 23,24
max_total_excess: 7
labels: 2,5
workers: 100
```

Output:

```
search23/verify_projection_6195_er14_full_typewise.tsv
```

Summary:

```
p=23: 378 CLOSE, 9 OPEN
p=24: 378 CLOSE, 9 OPEN
```

The same nine masks remain open for both p-values:

```
0xfd8e38
0xfe8e38
0xff0e38
0xff8638
0xff8a38
0xff8c38
0xff8e18
0xff8e28
0xff8e30
```

For each open case the `labels=2,5` projection has `projection_types=16`,
`need_pairs=1`, and `worst_p_proj=34`, so the current P-free projected
typewise certificate is insufficient.  Alternative label pairs `2,4` and
`4,5` were tested on the nine masks but have `64` projected states, beyond
the lightweight checker's current enumeration cap:

```
search23/verify_projection_6195_er14_open9_labels24.tsv
search23/verify_projection_6195_er14_open9_labels45.tsv
```

Status: VERIFIED COMPUTATION / PARTIAL CLOSURE.  The profile `6195`,
`e_R=14` row is reduced to nine explicit masks; no full row closure is
claimed.

## V372. q13/r0=8/t=2 profile 6195 eR=14 root-side projection cut

Date: 2026-06-19.

GPT Pro audit saved at:

```
problems/23/gpt_pro/q13_t2_6195_er14_open9_answer_20260619.md
```

The audit identified that the six-column `labels=2,5` projection certificate
was missing the projected root-side inequalities

```
alpha_r >= 2 - |L(r)|, beta_r >= 2 - |L(r)|
```

for local projected vertices.  This is already present in the full
state-count quotient, but was absent from the lightweight projection checker.
The checker was updated:

```
search23/verify_projection_6195_row.cpp
search23/verify_projection_6195_general.cpp
search23/projection_cpsat_6195.py
```

Re-running the nine open masks with this root-side cut gives:

```
search23/verify_projection_6195_er14_open9_rootside.tsv
```

Summary:

```
p=23,24: 0 CLOSE, 18 OPEN
representative 0xfd8e38 worst_p_proj: 34 -> 29
representative infeasible local targets: 1669 / 1716
```

For the representative mask `0xfd8e38`, the previously highlighted local
target

```
(4,4,5,3,3,6)
```

now has projected upper bound `p_K=23`; hence it is closed for `p=24`.
The `p=23` equality case remains and requires either the hand equality
argument from the GPT audit or a full state-count certificate.

A full-state exact-excess certificate was started for this equality target
in the row `p=23, M=61`.  The vector file is:

```
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_vectors.txt
```

Using projected-PMC propagation cuts

```
--projection-cuts '2,5;2,4;4,5;2,7;5,7'
```

the first 70 exact excess vectors were closed:

```
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_first20.tsv
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_unknown6_300s.tsv
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_20_69.tsv
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_20_69_unknown_300s.tsv
```

The next batch `offset70 limit100` was stopped at `40/100` because it had
only `6 INFEASIBLE` and `34 UNKNOWN` at `120s` per vector:

```
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_70_169.tsv
```

Status: VERIFIED COMPUTATION / PARTIAL CLOSURE.  Root-side projection is a
valid missing cut for the lightweight certificate, but it does not close the
nine `e_R=14` masks.  The active frontier is the remaining exact-excess
vectors for representative target `(4,4,5,3,3,6)`, especially those with
excess on vertices `5,6,7`; GPT Pro recommends defect-block constraints
`D1-D3` for this frontier.

## V373. q13/r0=8/t=2 profile 6195 defect-block prototype

Date: 2026-06-19.

Implemented an optional defect-block layer in the full state-count master:

```
search23/state_count_6195_cpsat.py --defect-block-labels '2,5'
```

For `K = X union H` this adds:

```
a_{S,v}, b_{S,v} class-column aggregation variables for v outside K
cross K/outside R/R coverage constraints
p = sum_{S cap T empty} a_S b_T - sum defects
defect >= shared outside column count per column
sum outside shared counts >= 2 defect
```

The constraints are P-free and do not enumerate an A/B template.  They use
the full-state count variables, so they are a propagation/certificate layer
inside the quotient model.

Smoke test on a previously UNKNOWN vector:

```
mask: 0xfd8e38
p,M: 23,61
excess vector: 0,0,0,0,0,1,0,4,0,0,2,0,0
projection cuts: 2,5;2,4;4,5;2,7;5,7
defect block: 2,5
```

returned:

```
INFEASIBLE in 95.625s
```

Batch test on the `34` UNKNOWN vectors from the stopped `offset70` run:

```
search23/state_count_6195_0xfd8e38_p23_M61_target_445336_projcuts_70_169_unknown_defect.tsv
```

returned:

```
11 INFEASIBLE
23 UNKNOWN
```

The remaining UNKNOWN vectors have excess concentrated on vertices
`5,6,7,11,12`, with vertex `10` fixed at excess `2`.  This indicates that
the defect-block layer helps but does not yet close the hard equality target.

Status: VERIFIED COMPUTATION / PARTIAL CLOSURE.  Defect-block constraints are
a useful next certificate layer, but a sharper branch or additional block
invariant is still needed for the remaining exact-excess vectors.

## V374. q13/r0=8/t=2 profile 6195 eR=14 open9 closure

Date: 2026-06-19.

After adding projected root-side cuts and the defect-block layer, the nine
remaining `e_R=14` masks for profile `6195` were rerun over all relevant
`p,M` rows:

```
search23/run_state_count_6195_masks_batch.exe \
  search23/q13_t2_family_6195_er14_open9_masks.txt \
  search23/state_count_6195_er14_open9_defect24.tsv \
  23:54-61,24:54-60 120 20 5 0 0 \
  --projection-cuts '2,5;2,4;4,5;2,7;5,7' \
  --defect-block-labels 2,4
```

The run completed with:

```
tasks=135
INFEASIBLE=135
FEASIBLE=0
UNKNOWN=0
```

Output file:

```
search23/state_count_6195_er14_open9_defect24.tsv
```

Independent TSV check:

```
INFEASIBLE 135
```

Status: VERIFIED COMPUTATION.  The previously open `e_R=14` rows for profile
`6195` are closed by the state-count quotient with projected cuts and the
`2,4` defect-block certificate layer.  The proof-grade write-up still needs
the defect-block constraints stated as a finite certificate lemma and an
independent checker/audit.

## V375. q13/r0=8/t=2 profile 6195 eR=15 pilot

Date: 2026-06-19.

Generated the `e_R=15` local skeleton masks for profile `6195`:

```
search23/q13_t2_family_6195_er15_masks.txt
```

Mask count:

```
1234
```

Pilot run on the first `20` masks:

```
search23/run_state_count_6195_masks_batch.exe \
  search23/q13_t2_family_6195_er15_masks_first20.txt \
  search23/state_count_6195_er15_first20_defect24.tsv \
  22:52-61,23:52-60 60 20 5 0 0 \
  --projection-cuts '2,5;2,4;4,5;2,7;5,7' \
  --defect-block-labels 2,4
```

Result:

```
tasks=380
INFEASIBLE=380
FEASIBLE=0
UNKNOWN=0
elapsed_s=111
```

Status: VERIFIED COMPUTATION / PILOT ONLY.  This is not a full closure of
`e_R=15`; it indicates that the V374 certificate layer likely scales to the
next `6195` row.  A full `e_R=15` run would cover `1234 * 19 = 23446` tasks.

## V376. q13/r0=8/t=2 profile 6195 eR=15 full closure

Date: 2026-06-19.

The full `e_R=15` mask set for profile `6195` was rerun over all relevant
`p,M` rows:

```
search23/run_state_count_6195_masks_batch.exe \
  search23/q13_t2_family_6195_er15_masks.txt \
  search23/state_count_6195_er15_defect24.tsv \
  22:52-61,23:52-60 60 20 5 0 0 \
  --projection-cuts '2,5;2,4;4,5;2,7;5,7' \
  --defect-block-labels 2,4
```

The run completed with:

```
tasks=23446
jobs=20
workers_per_job=5
INFEASIBLE=23446
FEASIBLE=0
UNKNOWN=0
elapsed_s=6742
```

Output file:

```
search23/state_count_6195_er15_defect24.tsv
```

Independent TSV check:

```
INFEASIBLE 23446
total rows 23446
```

Status: VERIFIED COMPUTATION.  The full `e_R=15` layer for profile `6195` is
closed by the same state-count quotient, projected cuts, and `2,4`
defect-block certificate layer used in V374.  The proof-grade write-up still
needs the projected cuts and defect-block constraints stated as finite
certificate lemmas and checked independently.

## V377. q13/r0=8/t=2 profile 6195 eR=16 pilot

Date: 2026-06-19.

Generated the `e_R=16` local skeleton masks for profile `6195`:

```
search23/q13_t2_family_6195_er16_masks.txt
```

Mask count:

```
2601
```

Pilot run on the first `20` masks:

```
search23/run_state_count_6195_masks_batch.exe \
  search23/q13_t2_family_6195_er16_masks_first20.txt \
  search23/state_count_6195_er16_first20_defect24.tsv \
  21:50-61,22:50-60 60 20 5 0 0 \
  --projection-cuts '2,5;2,4;4,5;2,7;5,7' \
  --defect-block-labels 2,4
```

Result:

```
tasks=460
INFEASIBLE=460
FEASIBLE=0
UNKNOWN=0
elapsed_s=122
```

Independent TSV check:

```
INFEASIBLE 460
total rows 460
```

Status: VERIFIED COMPUTATION / PILOT ONLY.  This is not a full closure of
`e_R=16`; it indicates that the V374/V376 certificate layer likely continues
to scale.  A full `e_R=16` run would cover `2601 * 23 = 59823` tasks.

## Active. q13/r0=8/t=2 profile 6195 eR=16 full run

Date: 2026-06-19.

Target universe:

```
2601 masks * (21:50-61,22:50-60) = 59823 (mask,p,M) tasks
```

The initial `20 * 5 = 100` worker run was stopped after the thread budget was
reduced to `64` hardware threads.  Partial TSVs are preserved and only rows
with status `INFEASIBLE` are counted as closed.  Interrupted `NO_STATUS` rows
are not accepted and are rerun.

Current run style:

```
search23/run_state_count_6195_tasks_batch.exe ... 60 15 2 0 0 \
  --projection-cuts '2,5;2,4;4,5;2,7;5,7' \
  --defect-block-labels 2,4
```

Chunks `chunkA`, `chunkB`, `chunkC`, clean rerun chunk `chunkD2`, and
`chunkE2`, `chunkH`, `chunkI`, `chunkJ`, `chunkK`, `chunkL`, and `chunkM`
were run with `15 jobs * 2 solver workers`; each chunk had 2000 tasks, all
`INFEASIBLE`, with no `FEASIBLE` or `UNKNOWN` rows.  This setting is intended
to stay within the 64-thread Step-1 cap by conservative process-tree estimate.

Auto-launched chunks `chunkN` and `chunkO` were run with `25 jobs * 2 solver
workers`; each chunk had 2000 tasks, all `INFEASIBLE`, with no `FEASIBLE` or
`UNKNOWN` rows.

The final auto-launched chunk `chunkP` covered the remaining 2104 tasks with
`25 jobs * 2 solver workers`; all rows were `INFEASIBLE`, with no `FEASIBLE`
or `UNKNOWN` rows.

Union verifier added:

```
search23/verify_state_count_union.cpp
search23/verify_state_count_union.exe
```

Snapshot verifier command:

```
search23/verify_state_count_union.exe \
  search23/q13_t2_family_6195_er16_masks.txt \
  21:50-61,22:50-60 \
  search23/q13_t2_family_6195_er16_missing_snapshot.tsv \
  search23/q13_t2_family_6195_er16_bad_snapshot.tsv \
  search23/state_count_6195_er16_defect24.tsv \
  search23/state_count_6195_er16_remaining_defect24.tsv \
  search23/state_count_6195_er16_remaining32x2_defect24.tsv \
  search23/state_count_6195_er16_remaining3_defect24_clean.tsv \
  search23/state_count_6195_er16_remaining4_defect24.tsv \
  search23/state_count_6195_er16_remaining5_30x2_defect24_clean.tsv \
  search23/state_count_6195_er16_remaining6_15x2_defect24.tsv \
  search23/state_count_6195_er16_chunkA_defect24.tsv \
  search23/state_count_6195_er16_chunkB_defect24.tsv \
  search23/state_count_6195_er16_chunkC_defect24.tsv \
  search23/state_count_6195_er16_chunkD2_defect24.tsv \
  search23/state_count_6195_er16_chunkE2_defect24.tsv \
  search23/state_count_6195_er16_chunkH_defect24.tsv \
  search23/state_count_6195_er16_chunkI_defect24.tsv \
  search23/state_count_6195_er16_chunkJ_defect24.tsv \
  search23/state_count_6195_er16_chunkK_defect24.tsv \
  search23/state_count_6195_er16_chunkL_defect24.tsv \
  search23/state_count_6195_er16_chunkM_defect24.tsv \
  search23/state_count_6195_er16_chunkN_defect24.tsv \
  search23/state_count_6195_er16_chunkO_defect24.tsv \
  search23/state_count_6195_er16_chunkP_defect24.tsv
```

Latest snapshot:

```
expected=59823
closed=59823
missing=0
bad=0
duplicate_infeasible=238
malformed=0
outside_expected=0
```

The clean proof union uses `INFEASIBLE`-only filtered copies of the earlier
partial `remaining3` and `remaining5_30x2` files, leaving the raw interrupted
logs intact.  A separate clean union artifact also exists at
`search23/state_count_6195_er16_clean_infeasible_union.tsv`.  Status: the
`6195, e_R=16` task universe is closed by this state-count verifier layer; H1
still requires global Step-1 audit.

The abandoned `chunkD` output is not part of the trusted union because a
duplicate launch polluted it with `NO_STATUS`/blank status rows.

The stopped `chunkF` output is also not part of the trusted union because it
was launched with `20 jobs * 3 solver workers`, outside the conservative
Step-1 cap policy.

Update 2026-06-20T01:52+03:00:

`6195, e_R=16` is now closed by the clean union certificate.

Final accepted chunk:

```
search23/state_count_6195_er16_chunkP_defect24.tsv
tasks=2104
INFEASIBLE=2104
FEASIBLE=0
UNKNOWN=0
other=0
jobs=25
workers_per_job=2
```

Clean union artifact:

```
search23/state_count_6195_er16_clean_infeasible_union.tsv
```

Final clean union verifier output:

```
expected=59823
rows_read=63867
unique_infeasible=59823
missing=0
noninf_keys=0
duplicate_inf_rows=4044
malformed=0
```

Only rows with `status=INFEASIBLE` were copied into the clean union artifact.
Interrupted `NO_STATUS` and malformed rows from older partial runs are not used
in the final certificate.  Status: VERIFIED COMPUTATIONAL CLOSURE for
`6195, e_R=16`; next step is a global Step-1 proof-state audit before making
any claim about H1 as a whole.

Global audit note 2026-06-20T01:52+03:00:

The original q13/r0=8/t=2 post-cut remainder table

```
search23/q13_t2_r8_a6b7_postcuts_remaining.tsv
```

still has `238` rows.  The largest `20`-row family
`cnt=0,0,3,2,3,3,0,2` / profile `6195` is now closed by V368/V370/V374/V376
and the clean `e_R=16` union certificate above.  Therefore the old table still
leaves about `218` non-6195 rows requiring either individual closure or a
superseding q13/r0=8/t=2 certificate.

This audit also confirms that H1 is not yet a closed theorem: the Step-1
handoff still needs (i) closure of the remaining q13/r0=8/t=2 rows or a
stronger global certificate and (ii) a finite-n justification for the edge
window, because the BCL density reductions are asymptotic and do not alone
prove that n=30 cases outside `109 <= e <= 139` are covered.

Audit note 2026-06-20T02:05+03:00:

The experimental q13/r0=8/t=2 `terminal_closure` equalities are not accepted
as proof rules.  GPT Pro identified the terminal-touch equality as unjustified
from the current frontier assumptions, and a safe rerun without
`terminal_closure` confirmed that the smallest non-6195 four-row smoke set

```
search23/q13_t2_r8_a6b7_small4_non6195.tsv
```

remains open:

```
search23/q13_t2_r8_a6b7_small4_safe_anti_300.tsv
INFEASIBLE=0
UNKNOWN=4
FEASIBLE=0
```

An unsafe run with `terminal_closure` closed two `p=26` rows, but those
closures are not counted toward H1.  Future q13/r0=8/t=2 certificates must use
only validated cuts such as anti-tightness, class/rectangle/state-separator
cuts, fixed-skeleton certificates, or independently proved replacements.

Update 2026-06-20T02:35+03:00:

The smallest non-6195 q13/r0=8/t=2 smoke set is now closed by a safe
state-count defect-block certificate, without `terminal_closure`.

Closed rows:

```
row 43 / profile 4971 / cnt=0,0,2,2,2,3,0,4 / e_R=12
p=25, M=54..57
p=26, M=54..56

row 52 / profile 5164 / cnt=0,0,2,3,2,2,0,4 / e_R=12
p=25, M=54..57
p=26, M=54..56
```

Certificates:

```
search23/q13_t2_4971_eR12_state_count_defect34.tsv
rows=42
INFEASIBLE=42
FEASIBLE=0
UNKNOWN=0
other=0
cnt=0,0,2,2,2,3,0,4
defect_block_labels=3,4

search23/q13_t2_5164_eR12_state_count_defect25.tsv
rows=42
INFEASIBLE=42
FEASIBLE=0
UNKNOWN=0
other=0
cnt=0,0,2,3,2,2,0,4
defect_block_labels=2,5
```

For each family, `count_q13_fivelabel_skeletons.exe` reports exactly six
local `e_R=12` skeleton masks.  The 42 tasks per family are these six masks
times the seven exact `(p,M)` possibilities listed above.  The verifier used
the generalized state-count quotient

```
search23/state_count_6195_cpsat.py
```

with `--cnt`, `--na 6`, `--nb 7`, `--r0 8`, `--t 2`, and no
`terminal_closure`.

Defect-block soundness note: for any fixed local block `K`, every actual
A/B-state model satisfies

```
p = (# projected A/B pairs disjoint on K)
    - (# such pairs sharing at least one outside R-coordinate).
```

Since intersection-size-one A/B pairs are forbidden, each outside-defective
pair contributes at least two outside shared incidences.  The implemented
defect-block constraints are a necessary count-level relaxation of this exact
identity.  Therefore an `INFEASIBLE` result from the defect-block state-count
model safely excludes the corresponding fixed-R task.

Status impact: the old q13/r0=8/t=2 post-6195 remainder drops by four rows,
from about `218` non-6195 rows to about `214` rows, unless later superseded by
a broader q13 certificate.

## V378. q13/r0=8/t=2 `a6b7` vertex-count audit

Update 2026-06-20:

The q13/r0=8/t=2 `a6b7` family is not a valid `n=30` branch.  In the rooted
partition used by the q13 verifier, the total vertex count is

```
n = 2 + k + |A| + |B| + q.
```

For the `a6b7` runs this gives

```
2 + 3 + 6 + 7 + 13 = 31,
```

so all `search23/q13_t2_r8_a6b7_*` solver outputs are diagnostic only and are
not counted as H1 certificates.  This supersedes the previous estimates of
`218` and `214` remaining rows in that `a6b7` universe.

Code audit:

```
search23/verify_q13_t3_r9_profile_cpsat.py
search23/run_q13_exact_rows_parallel.py
```

both now validate the rooted partition and reject any invocation with
`2 + k + na + nb + q != n` (default `n=30`).  The invalid smoke command

```
python search23/run_q13_exact_rows_parallel.py --rows search23/q13_small4_exactM_input.tsv --out search23/tmp_invalid.tsv --q 13 --k 3 --na 6 --nb 7 --r0 8 --t 2 --limit 1
```

exits with

```
ValueError: invalid rooted partition: 2 + k + na + nb + q = 31, expected n=30
```

The GPT Pro audit that first flagged the mismatch is archived at

```
gpt_pro_consultations/q13_r0_8_t2_small4_safe_unknown_answer_2026-06-20.md
```

Status impact: H1 is still open.  The `a6b7` branch is dead by vertex count,
not by solver infeasibility.  The next q13 audit must identify whether any
valid `q=13,k=3` branches with `na+nb=12` remain, e.g. `a6b6` or `a5b7`.

## V379. Valid q13/k=3/t=3/r8 profile audit

Update 2026-06-20:

After removing the invalid `t=2/a6b7` branch, the visible valid `q=13,k=3`
profile artifacts with `na+nb=12` are the `t=3,r8` files:

```
search23/q13_t3_r8_a5b7_scalar_prefilter.summary.txt
profiles_survive=257
rows_survive=55827

search23/q13_t3_r8_a6b6_scalar_prefilter.summary.txt
profiles_survive=256
rows_survive=53333

search23/q13_t3_r8_a7b5_scalar_prefilter.summary.txt
profiles_survive=256
rows_survive=39208
```

Their profile CP-SAT closure artifacts are:

```
search23/q13_t3_r8_a5b7_profile_cpsat_0_256.tsv
rows=257
INFEASIBLE=257

search23/q13_t3_r8_a6b6_profile_cpsat_0_255.tsv
rows=256
INFEASIBLE=249
UNKNOWN=7

search23/q13_t3_r8_a6b6_profile_hard_300.tsv
rows=7
INFEASIBLE=7

search23/q13_t3_r8_a7b5_profile_cpsat_0_255.tsv
rows=256
INFEASIBLE=256
```

Thus the visible valid `q=13,k=3,t=3,r8` profile universes are closed at the
profile level by the recorded CP-SAT artifacts, including the seven hard
`a6b6` reruns.

The visible valid `q=13,k=3,t=3,r9,na=6,nb=6` branch was already recorded
earlier in this file: `q13_t3_r9_profile_cpsat_0_93.tsv` closes `93/94`
profiles, and `q13_t3_r9_profile_74088_rerun_sym.txt` closes the single hard
profile `74088` as `INFEASIBLE`.

This audit does not close H1 by itself; the global Step-1 handoff still needs
the finite-density replacement for asymptotic BCL usage and a complete
inventory proving that no other valid q13 branch remains.

## V380. Finite low-edge deletion closure for `e=74..98`

Update 2026-06-20:

The first part of the BCL low-density gap can be replaced by a finite deletion
argument using only V1, the exact value `a(23)=20`, and the McKay extremal edge
audit from V2.

If a 30-vertex graph has `beta(G)>=37`, delete seven vertices one at a time.
If the cumulative deletion loss is

```
L = sum floor(d_current(v_i)/2)
```

and the removed-edge count is

```
R = sum d_current(v_i),
```

then the remaining 23-vertex graph has

```
beta >= 37-L,  e' = e-R.
```

The McKay audit gives:

- if `e' >= 100`, contradiction follows from `L <= 16`, since then
  `beta >= 21 > a(23)`;
- if `e' <= 99`, contradiction follows from `L <= 17`, since then
  `beta >= 20`, while all 23-vertex `beta=20` extremals in the McKay file have
  at least `100` edges.

The audit checker

```
search23/seven_delete_low_edge_dp.cpp
search23/seven_delete_low_edge_dp.exe
search23/seven_delete_low_edge_dp.txt
```

enumerates all deletion sequences allowed by the conservative guarantee

```
delta(G_current) <= floor(2e_current/n_current)
```

and checks the two McKay contradiction conditions above.  It reports:

```
e=74..98:  forced YES
e=99..108: forced NO
summary forced=25 open=10
```

Therefore no triangle-free 30-vertex graph with `beta>=37` exists for

```
74 <= e(G) <= 98.
```

This uses no BCL density theorem and no unverified `a(25)` input.  The finite
low-edge gap is reduced to

```
99 <= e(G) <= 108.
```

Status: VERIFIED ARITHMETIC COMPUTATION.  H1 remains open because the low-edge
range `99..108`, the high-edge range `140..225`, the q13 inventory audit, and
the final search-space handoff are not yet complete.

## V381. Finite high-edge AES peeling tail for `e>=204`

Update 2026-06-20:

The top part of the BCL high-density gap can be replaced by a finite peeling
audit using the Andrasfai-Erdos-Sos theorem.

Fact used: if a triangle-free graph on `n` vertices has minimum degree
strictly larger than `2n/5`, then it is bipartite.  Therefore any non-bipartite
triangle-free graph has a vertex of degree at most `floor(2n/5)`.

The audit checker

```
search23/high_edge_aes_peeling_dp.cpp
search23/high_edge_aes_peeling_dp.exe
search23/high_edge_aes_peeling_dp.txt
```

computes a conservative recurrence over `(n,e)`: delete a guaranteed
low-degree vertex from any non-bipartite triangle-free graph, add
`floor(d/2)` to the bipartization budget, and stop with budget `0` once the
edge count alone forces the AES minimum-degree condition.

It reports:

```
summary forced=22 open=64 forced_tail_start=204
```

Hence the finite high-edge tail

```
204 <= e(G) <= 225
```

cannot contain a 30-vertex triangle-free graph with `beta>=37`.

Status: VERIFIED ARITHMETIC COMPUTATION.  H1 remains open because the low-edge
range `99..108`, the high-edge range `140..203`, the q13 inventory audit, and
the final search-space handoff are not yet complete.

## V382. BCL density ranges transfer to finite `n=30` by uniform blow-up

Update 2026-06-20:

The previous concern that the Balogh--Clemen--Lidicky density theorem is only
stated for sufficiently large `n` can be removed for the density ranges
themselves by a uniform blow-up argument.

Source checked: the BCL arXiv abstract states that the Erdős bipartization
conjecture is proved for triangle-free graphs of edge density at most `0.2486`
and at least `0.3197`, and the paper notes in its concluding remarks that the
large-`n` restriction is not an actual restriction for the conjecture because
of blow-ups.

Additional source audit: the downloaded arXiv TeX source
`tmp_bcl_src/Extendedabstract.tex` states Theorem 2 with
`|E(G)| >= 0.3197 \binom{n}{2}` and
`|E(G)| <= 0.2486 \binom{n}{2}`, so the finite transfer uses binomial edge
density, not `|E(G)|/n^2`.

Finite-transfer lemma:

Let `G[t]` be the uniform `t`-blow-up of `G`.  Then

```
e(G[t]) = t^2 e(G),
beta(G[t]) = t^2 beta(G).
```

The second identity follows because, in a cut of `G[t]`, if `a_i` of the `t`
copies of a vertex `v_i` lie on one side, the cut contribution of every blown-up
edge is affine in each `a_i`.  Moving each class wholly to one side never
decreases the cut.  Hence a maximum cut may be chosen class-uniformly and is
the blow-up of a maximum cut of `G`.

For a 30-vertex graph with `m` edges, the edge density of `G[t]` is

```
t^2 m / binom(30t,2) -> m/450.
```

Thus:

- if `m <= 111`, then `m/450 < 0.2486`, so for sufficiently large `t`, BCL
  gives `beta(G[t]) <= (30t)^2/25 = 36t^2`, contradicting
  `beta(G) >= 37`;
- if `m >= 144`, then `m/450 > 0.3197`, and the same blow-up contradiction
  applies.

Therefore the BCL density ranges are valid finite exclusions for `n=30`:

```
e(G) <= 111  or  e(G) >= 144  =>  beta(G) <= 36.
```

The only edge counts not covered by this finite density transfer are

```
112 <= e(G) <= 143.
```

Status: T1 ARITHMETIC/REDUCTION CHECK, conditional on accepting the published
BCL theorem.  It does not reverify BCL's flag-algebra computation.  H1 remains
open pending a finite closure of the full `112..143` window, q13 inventory
audit, and final handoff.

## V383. Rooted `e109..139` campaign is not a certificate; valid q13 T2 frontier

Update 2026-06-20:

The direct rooted campaign
`search23/campaign_rooted_r4_9_e109_139_w100_c20k_20260618_233808` was audited.
It is not a finite certificate.  Its `summary.tsv` has

```
INCONCLUSIVE 149
```

and its `DONE.txt` reports

```
jobs 149
unsat 0
sat_counterexample 0
inconclusive 149
errors 0
```

Therefore no part of the `112..139` medium-density window may be counted as
closed from this campaign.  Together with V382, the current BCL-transfer
frontier for H1 remains

```
112 <= e(G) <= 143.
```

Additional q13 audit:

- the old `q13/r0=8/t=2/a6b7` artifacts are invalid for H1 because their rooted
  partition has `2+3+6+7+13=31` vertices;
- the visible valid `q=13,k=3,t=3` artifacts with `na+nb=12` are closed at the
  profile level, including the seven hard `a6b6` rows and the `r9` hard profile
  `74088`;
- no trusted valid `q=13,k=3,t=2,na+nb=12` closure is visible.

Codex generated the valid `q=13,k=3,t=2,r0=8` scalar prefilters under total edge
cap `143`:

```
(na,nb)=(5,7): profiles_survive=1427, rows_survive=576607
(na,nb)=(6,6): profiles_survive=1427, rows_survive=556394
(na,nb)=(7,5): profiles_survive=1427, rows_survive=493254
```

These counts are too large for a naive row-by-row attack.  The next step is a
structural or quotient certificate for the valid `q13/K3/T2` frontier, with GPT
Pro consult prompt saved at
`gpt_pro_consultations/q13_k3_t2_valid_frontier_prompt_2026-06-20.md`.

Status: VERIFIED AUDIT.  H1 remains open.  This section also confirms the claim
boundary: H1 is only the finite theorem `a(30)<=36`; a full solution of Erdős
Problem #23 would additionally need an independently proved general-to-30
reduction.

## V383a. Valid q13/K3/T2 cap143 inventory summary and one top-profile row closure

Update 2026-06-20:

Codex added a read-only summarizer for the valid `q=13,k=3,t=2,r0=8`
cap-143 scalar frontier:

```
search23/summarize_q13_t2_frontier.cpp
search23/summarize_q13_t2_frontier.exe
```

Running it on

```
search23/q13_t2_r8_a5b7_cap143_scalar_prefilter.tsv
search23/q13_t2_r8_a6b6_cap143_scalar_prefilter.tsv
search23/q13_t2_r8_a7b5_cap143_scalar_prefilter.tsv
```

produced

```
search23/q13_t2_r8_cap143_profile_summary.tsv
search23/q13_t2_r8_cap143_bucket_summary.tsv
```

The audited totals are:

```
tag   profiles  rows
a5b7      1427  576607
a6b6      1427  556394
a7b5      1427  493254
```

The row mass is concentrated near `U=20`:

```
a5b7,U=20: 126774 rows over 261 profiles
a6b6,U=20: 122490 rows over 261 profiles
a7b5,U=20: 108330 rows over 261 profiles
```

The heaviest single valid profile in the summary is

```
tag=a6b6
idx=66649
cnt=4,0,0,3,3,0,0,3
U=18
eR=14..51
p=12..36
rows=810
```

Codex patched `search23/verify_q13_t3_r9_profile_cpsat.py` and
`search23/run_q13_profile_row_parallel.py` with an explicit `--edge-cap`
parameter, defaulting to the old value `139`, so cap-143 runs are not
accidentally checked under the narrower cap.

Smoke closure for the heaviest valid profile at `eR=14`:

```
profile idx 66649, cnt=4,0,0,3,3,0,0,3, (na,nb)=(6,6), eR=14
```

The row split

```
search23/q13_t2_valid_top_a6b6_66649_eR14_rows_60.tsv
```

has `23` `INFEASIBLE` rows and one `UNKNOWN` row:

```
p=23, M=58..70
```

The remaining row was rerun with the stronger state-separator-capacity cut and
saved as

```
search23/q13_t2_valid_top_a6b6_66649_eR14_p23_strong.tsv
```

with output

```
status=INFEASIBLE sec=40.703
```

Therefore the scalar row-family

```
tag=a6b6, idx=66649, cnt=4,0,0,3,3,0,0,3, eR=14
```

is closed at the current profile-level verifier layer.  This is only a sample
closure inside the valid T2 frontier; it does not materially close the whole
`q13/K3/T2` branch.  Its value is diagnostic: broad profile-level `p`-free
checks can return `UNKNOWN`, while row-level splits plus targeted state
separator cuts can close at least some heavy profiles.

Status: VERIFIED COMPUTATIONAL SUBCASE.  H1 remains open.

## V384. Cap-143 low-codegree delta collapses to six `k=1,q=8` scalar shapes

Update 2026-06-20:

After V382, the density-transfer frontier expanded the exact edge cap from
`139` to `143`.  Codex first generated the conservative q<=13 low-codegree
shape manifests

```
search23/lowcodegree_qle13_manifest_cap139.tsv
search23/lowcodegree_qle13_manifest_cap143.tsv
```

with summaries

```
cap139 survivors = 420
cap143 survivors = 481
```

so the new conservative shape delta had `61` rows, saved as

```
search23/lowcodegree_qle13_manifest_cap143_minus_cap139.tsv
```

Codex then added a generic scalar prefilter

```
search23/lowcodegree_scalar_prefilter.cpp
```

parameterized by `(q,k,a,b,r0,t,total_edge_cap)`.  A smoke check against the
existing q13/r9 scalar prefilter gave exactly the same row count:

```
old q13/r9 rows = 6169
generic q13/r9 rows = 6169
```

Applying the generic scalar prefilter to all `61` cap-143-minus-cap-139 shapes
gave

```
shapes checked     = 61
survivor shapes    = 6
survivor profiles  = 18
survivor rows      = 4986
```

The summary artifact is

```
search23/lowcodegree_scalar_cap143_minus_cap139_summary.tsv
```

The two largest conservative delta blocks are killed already at this scalar
profile level:

```
r0=8, t=2, q=5: 10/10 shapes, 0 profiles, 0 rows
r0=9, t=3, q=6:  8/8 shapes, 0 profiles, 0 rows
```

The only scalar-surviving new cap-143 shapes are

```
r0=8, k=t=1, q=8,
(a,b) = (7,12), (8,11), (9,10), (10,9), (11,8), (12,7).
```

Each has exactly `3` surviving label profiles and `831` scalar rows.  The
combined row artifact is

```
search23/lowcodegree_scalar_r8_t1_q8_cap143_survivor_rows.tsv
```

with summary

```
search23/lowcodegree_scalar_r8_t1_q8_cap143_survivor_summary.tsv
```

Status: VERIFIED SCALAR INVENTORY.  This does not close H1.  It reduces the
new `140..143` low-codegree delta to a small `k=1,q=8` frontier.  The older
`112..139` frontier and the valid `q13,k=3,t=2,na+nb=12` frontier remain open.

## V385. The remaining new `k=1,q=8` cap-143 R-skeleton universe has 60 orbits

Update 2026-06-20:

For the six scalar-surviving new cap-143 shapes isolated in V384, the R-label
structure has only one root common neighbour `c`.  Thus every R-vertex has
label `0` or `1` according as it is nonadjacent or adjacent to `c`.

The scalar survivors have only

```
(c0,c1) = (0,8), (1,7), (2,6).
```

Codex added the canonical R-skeleton manifest generator

```
search23/k1_q8_skeleton_manifest.cpp
```

and generated

```
search23/k1_q8_skeleton_manifest.tsv
search23/k1_q8_skeleton_manifest.summary.txt
```

The manifest uses counts `(n00,n10,n01,n11)` for the label-1 vertices'
neighbourhoods into the at-most-two label-0 vertices.  If the two label-0
vertices are adjacent, `n11=0` is imposed to avoid triangles.

The resulting canonical R-skeleton orbit counts are

```
c0=0:  1
c0=1:  7
c0=2: 52
total: 60
```

Status: VERIFIED FRONTIER INVENTORY.  The next exact certificate for the new
`140..143` delta can target these 60 R-skeleton orbits across the six
`(a,b)=(7,12)..(12,7)` shapes, with beta/maxcut constraints still required.

## V386. `k=1,q=8` state-count solver interface smoke

Update 2026-06-20:

Codex patched

```
search23/state_count_6195_cpsat.py
```

to accept an explicit `--k` parameter, defaulting to the prior `K=3`
behaviour.  This is needed for the new cap-143 delta isolated in V384/V385,
whose remaining rooted branch has only one root common neighbour (`k=1`).

The first smoke row was run on the unique `c0=0,c1=8` skeleton:

```
--k 1
--cnt 0,8
--na 7 --nb 12 --r0 8 --t 2
--fixed-r-mask 0
--p 19 --m 95
--timeout 60 --workers 8
--quotient-cut-rounds 1 --quotient-separator-timeout 2
```

The saved artifact is

```
search23/k1_q8_c0_0_a7b12_p19_M95_smoke.tsv
```

with stderr

```
search23/k1_q8_c0_0_a7b12_p19_M95_smoke.err
```

The result was

```
status=INFEASIBLE
sec=19.467
states=255
p=19
M=95
floors=56
quotient_cuts=0
```

and the stderr file is empty.

Status: VERIFIED COMPUTATIONAL SMOKE.  This does not close the `k=1,q=8`
frontier; it verifies that the state-count certificate interface now reaches
the new `k=1` branch and closes at least the first canonical row.

## V387. `k=1,q=8,c0=0,(a,b)=(7,12)` state-count closure

Update 2026-06-20:

Codex generated the `k=1,q=8` state-count task files with

```
search23/k1_q8_make_state_count_tasks.cpp
```

and then closed the full `c0=0,c1=8,(a,b)=(7,12)` task group using

```
search23/run_state_count_6195_tasks_batch.exe
```

with `4` parallel jobs and `16` CP-SAT workers per job.  The trusted result
artifacts are

```
search23/k1_q8_a7b12_c0_first40_w16.tsv
search23/k1_q8_a7b12_c0_remaining_w16.tsv
```

Their status counts are

```
first40:   40 INFEASIBLE
remaining: 380 INFEASIBLE
total:    420 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

Status: VERIFIED SUBFRONTIER CLOSURE.  This closes the unique `c0=0,c1=8`
R-skeleton orbit for the `(a,b)=(7,12)` side choice in the cap-143
`k=1,q=8` delta.  It does not close the other five `(a,b)` side choices or
the `c0=1,2` skeleton families.

## V388. `K=2,T=2` four-label reroot profile manifest

Update 2026-06-20:

GPT Pro suggested replacing the large valid `K=3,T=2` frontier by rerooting at
an attained exact-codegree-two nonedge.  This gives a `K=2` rooted model with
four R-labels

```
E, S1, S2, D
```

and profile counts `(c0,c1,c2,c3)` satisfying

```
c0+c1+c2+c3 = q
c1+c3 >= 6
c2+c3 >= 6
c1>0 => c2>=2
c2>0 => c1>=2
```

up to the colour swap `S1 <-> S2`.  Codex added and ran

```
search23/k2_four_label_profiles.cpp
```

which produced

```
search23/k2_four_label_profile_instances.tsv
search23/k2_four_label_profile_summary.tsv
```

The independently generated summary is

```
q  raw  orbits  side_choices  instances
6    1       1       5              5
7    2       2       4              8
8    4       4       4             16
9    9       8       3             24
10  19      15       3             45
11  36      26       2             52
12  62      42       2             84
13  98      63       1             63
14 145      90       1             90
TOTAL 376  251                    387
```

The q14 exclusion audit did not pass: the historical q14/t2 closure contains
terminal-touch/terminal-degree dependencies that are no longer accepted as
proof rules.  Therefore the safe K2 manifest includes `q=14`, and
anti-tightness must remain disabled until q14 is independently reclosed without
the rejected terminal equalities.

Status: VERIFIED MANIFEST.  This is a search-space compression, not yet a
closure certificate.  The next certificate target is a P-free K2 master with
the paired opposite-root and same-root cut families.

## V389. `K=2,T=2` P-free master smoke over the full four-label manifest

Update 2026-06-20:

Codex added

```
search23/verify_k2_pfree_master.py
search23/run_k2_pfree_master_batch.py
```

for a necessary P-free master over the K2 four-label manifest.  The master
uses R-edge variables, `alpha/beta` column sums, local domination, R
triangle-freeness, R-edge A/B capacity projections, R-nonedge codegree capacity
envelopes, the BCL edge window `112..143`, aggregate A/B degree constraints,
opposite-root lower bounds, and the paired opposite-root/same-root cut
families

```
M + U + 2eR - 2 boundary_R(W) >= 70
2p + U + M + 2eR - 2 boundary_R(W) >= 74
```

The batch command was run with `8` jobs and `8` CP-SAT workers per job:

```
python search23/run_k2_pfree_master_batch.py \
  --manifest search23/k2_four_label_profile_instances.tsv \
  --out search23/k2_pfree_master_results.tsv \
  --jobs 8 --workers 8 --timeout 20
```

The result was

```
387/387 OPTIMAL
```

so this P-free master is a validated necessary-condition layer, but it does
not close any K2 profile-side instance by itself.

Status: VERIFIED NEGATIVE FILTER RESULT.  The K2 compression remains the
preferred route, but the next layer must be the exact A/B state-count quotient
or weighted quotient-cut separator.

## V390. `K=2,T=2,q=6` all-doubleton support closure

Update 2026-06-20:

Codex applied the fixed-skeleton state-count quotient to the five `q=6`
profile-side instances with support `{D}`:

```
(c0,c1,c2,c3) = (0,0,0,6)
(a,b) in (6,14), (7,13), (8,12), (9,11), (10,10)
```

For this support all R-labels are doubletons, so the R-skeleton is forced
empty and the H14/anti-tightness rule is vacuous.  The rooted constants are

```
q = 6
U = 12
root_edges = 24
eR = 0
112 <= 24 + U + p + M <= 143
```

For each side choice Codex generated the complete `(p,M)` grid allowed by the
edge window and ran

```
search23/run_state_count_6195_tasks_batch.exe \
  <tasks.tsv> <results.tsv> 60 8 8 3 5 \
  --k 2 --cnt 0,0,0,6 --na <a> --nb <b> --r0 8 --t 2
```

The audited result files are

```
search23/k2_idx0_q6D_a6b14_state_results.tsv   912 INFEASIBLE
search23/k2_idx1_q6D_a7b13_state_results.tsv   976 INFEASIBLE
search23/k2_idx2_q6D_a8b12_state_results.tsv  1040 INFEASIBLE
search23/k2_idx3_q6D_a9b11_state_results.tsv  1104 INFEASIBLE
search23/k2_idx4_q6D_a10b10_state_results.tsv 1168 INFEASIBLE
```

Thus the complete q=6 all-doubleton family has

```
5200 / 5200 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

Status: VERIFIED SUBFRONTIER CLOSURE.  This closes the support family
`{D}` for `K=2,T=2,q=6`; it does not close the other `q>=7` K2 four-label
families.

## V391. `K=2,T=2,q=7` all-doubleton support closure

Update 2026-06-20:

Codex repeated the fixed-empty-R state-count quotient for the four `q=7`
profile-side instances with support `{D}`:

```
(c0,c1,c2,c3) = (0,0,0,7)
(a,b) in (6,13), (7,12), (8,11), (9,10)
```

Again all R-labels are doubletons, so the R-skeleton is forced empty and the
H14/anti-tightness rule is vacuous.  The rooted constants are

```
q = 7
U = 14
root_edges = 23
eR = 0
112 <= 23 + U + p + M <= 143
```

For each side choice Codex generated the complete `(p,M)` grid allowed by the
edge window and ran

```
search23/run_state_count_6195_tasks_batch.exe \
  <tasks.tsv> <results.tsv> 60 8 8 3 5 \
  --k 2 --cnt 0,0,0,7 --na <a> --nb <b> --r0 8 --t 2
```

The audited result files are

```
search23/k2_idx5_q7D_a6b13_state_results.tsv  752 INFEASIBLE
search23/k2_idx6_q7D_a7b12_state_results.tsv  816 INFEASIBLE
search23/k2_idx7_q7D_a8b11_state_results.tsv  880 INFEASIBLE
search23/k2_idx8_q7D_a9b10_state_results.tsv  944 INFEASIBLE
```

Thus the complete q=7 all-doubleton family has

```
3392 / 3392 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

Status: VERIFIED SUBFRONTIER CLOSURE.  Together with V390, this closes the
all-doubleton support family `{D}` for `q=6,7` in the safe K2 manifest.

## V392. `K=2,T=2,q=7` empty-plus-doubleton support closure

Update 2026-06-20:

Codex ran the exact state-count quotient for the four `q=7` profile-side
instances with support `{E,D}`:

```
(c0,c1,c2,c3) = (1,0,0,6)
(a,b) in (6,13), (7,12), (8,11), (9,10)
```

The R-skeleton has one empty-label vertex and six doubleton vertices.  Edge
legality permits only `E-D` edges, and local domination forces the empty
vertex to have at least two doubleton neighbours.  Thus the canonical skeleton
family is the empty vertex joined to `k=2,3,4,5,6` doubleton vertices.

Because the H14/anti-tightness dependency is not yet audited through the full
cap-143 `q=14,T=2` universe, these runs explicitly disabled anti-tightness:

```
search23/run_state_count_6195_tasks_batch.exe \
  <tasks.tsv> <results.tsv> 60 8 8 3 5 \
  --k 2 --cnt 1,0,0,6 --na <a> --nb <b> --r0 8 --t 2 \
  --disable-anti-tightness
```

The audited result files are

```
search23/k2_idx9_q7ED_a6b13_state_results.tsv   4400 INFEASIBLE
search23/k2_idx10_q7ED_a7b12_state_results.tsv  4720 INFEASIBLE
search23/k2_idx11_q7ED_a8b11_state_results.tsv  5040 INFEASIBLE
search23/k2_idx12_q7ED_a9b10_state_results.tsv  5360 INFEASIBLE
```

Thus the complete q=7 `{E,D}` family has

```
19520 / 19520 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

Status: VERIFIED SUBFRONTIER CLOSURE.  Together with V391, this closes the
two smallest `q=7` K2 support families `{D}` and `{E,D}` in the safe manifest.

## V393. `K=2,T=2,q=8` all-doubleton support status

Update 2026-06-20:

Codex started the next all-doubleton family

```
(c0,c1,c2,c3) = (0,0,0,8)
(a,b) in (6,12), (7,11), (8,10), (9,9)
```

All R-labels are doubletons, so the R-skeleton is forced empty and
anti-tightness is disabled/vacuous.

The first side choice closed after a short hard-row rerun:

```
search23/k2_idx13_q8D_a6b12_state_results.tsv       590 INFEASIBLE, 2 UNKNOWN
search23/k2_idx13_q8D_a6b12_state_results_hard.tsv    2 INFEASIBLE
union                                               592 / 592 INFEASIBLE
```

The second side choice did not close with the current generic state-count
settings.  A first `8 jobs * 8 workers` run produced early timeouts; a stronger
`2 jobs * 32 workers` rerun closed only the first hard band before stalling.
The trusted union currently has

```
search23/k2_idx14_q8D_a7b11_state_results.tsv
search23/k2_idx14_q8D_a7b11_state_results_2x32.tsv
union: 48 INFEASIBLE, 608 remaining, 0 FEASIBLE
```

The remaining rows begin with `(p,M)=(22,81),(22,82),(22,83)` and then the
low-`p` bands from `p=23` upward.  These rows are not closed and require either
a targeted rerun strategy or a new P-free/state-count cut.

Status: PARTIAL.  The side choice `(a,b)=(6,12)` is verified closed; the full
`q=8` all-doubleton support family is still open.

## V394. Minimal-`p` parity lemma for all-doubleton K2 branches

Update 2026-06-20:

Codex added the hand certificate

```
problems/23/k2_allD_minimal_p_parity_2026-06-20.md
```

for the exact K2 all-doubleton quotient.  In an all-doubleton branch the
R-skeleton is empty.  If `p=2|B|`, then every B-vertex has exactly two
A-neighbours.  For a used B-state `J`, the B/R codegree condition for every
`r in R\J` forces both of those A-neighbour states to contain all of `R\J` and,
because they are A-B neighbours of `J`, none of `J`.  Hence both A-neighbour
states are exactly `R\J`, so `A_{R\J}=2`.  Since every A-copy must have at least
two B-neighbours, all A-copies lie in such complement classes, each of
multiplicity two.  Thus `|A|` is even.  The symmetric statement holds with A
and B exchanged.

This uses only:

- triangle-free A-B state law;
- root-opposite nonedge-codegree;
- typewise A/R and B/R nonedge-codegree;
- the empty R-skeleton of the all-doubleton support.

It does not use H14 anti-tightness, terminal-touch equality, or terminal-degree
equality.

Application to V393:

```
q=8, all-D, (|A|,|B|)=(7,11), p=22=2|B|
```

is impossible because `|A|=7` is odd.  This closes the three remaining `p=22`
rows

```
(p,M)=(22,81),(22,82),(22,83)
```

from V393.  Codex also patched `search23/state_count_6195_cpsat.py` with the
same prefilter and produced the machine artifact

```
search23/k2_idx14_q8D_a7b11_p22_parity_results.tsv  3 / 3 INFEASIBLE
```

The current `q=8` all-D `(7,11)` frontier is therefore reduced from `608`
remaining rows to `605`, beginning with the `p=23` band.

## V395. One-excess parity extension for all-doubleton K2 branches

Update 2026-06-20:

Codex extended the local hand certificate

```
problems/23/k2_allD_minimal_p_parity_2026-06-20.md
```

from the minimal root-opposite value `p=2|B|` to the one-excess value
`p=2|B|+1`, with the symmetric A/B statement.  If `p=2|B|+1`, the total
B-side excess over the lower bound two is exactly one.  Hence exactly one
B-copy can have three A-neighbours; every other used B-state has exactly two
A-neighbours and forces a complement A-state of multiplicity two by the same
B/R codegree argument as in V394.  Any A-copy outside those forced complement
classes could be adjacent only to the single exceptional B-copy, contradicting
the root-opposite lower bound that every A-copy has at least two B-neighbours.
Therefore `|A|` is even.  The symmetric statement holds with A and B exchanged.

This again uses only the exact K2 all-doubleton state-count quotient:

- triangle-free A-B state law;
- root-opposite nonedge-codegree;
- typewise A/R and B/R nonedge-codegree;
- the empty R-skeleton of the all-doubleton support.

It does not use H14 anti-tightness, terminal-touch equality, or terminal-degree
equality.

Application to V393/V394:

```
q=8, all-D, (|A|,|B|)=(7,11), p=23=2|B|+1
```

is impossible because `|A|=7` is odd.  Codex patched
`search23/state_count_6195_cpsat.py` so the safe all-D low-`p` parity
prefilter covers both `p=2|B|` and `p=2|B|+1`, and produced the machine
artifact

```
search23/k2_idx14_q8D_a7b11_p23_parity_results.tsv  13 / 13 INFEASIBLE
```

These are precisely the previously open `p=23, M=70..82` rows.  Combining the
generic state-count runs with V394 and this artifact gives:

```
search23/k2_idx14_q8D_a7b11_state_tasks.tsv          656 total
trusted union through p23 parity                     64 INFEASIBLE
remaining                                           592
first remaining                                     (p,M)=(24,50)
```

Status: VERIFIED LOCAL REDUCTION.  The q8 all-D `(7,11)` side choice remains
open, but both low-`p` bands `p=22` and `p=23` are now closed without broad
solver time.

## V396. q8 all-D `(7,11)` p24 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=24, M=50..81
```

with anti-tightness disabled.  The first pass used the exact state-count
quotient at

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p24_results.tsv
24 INFEASIBLE, 8 UNKNOWN, 0 FEASIBLE
```

The eight UNKNOWN rows were exactly `M=74..81`.  Codex then rebuilt the C++
batch runner with the current 100-worker cap and reran only that hard tail at

```
5 jobs x 20 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p24_hard_results.tsv
8 / 8 INFEASIBLE
```

Thus the whole `p=24` band is closed:

```
p=24, M=50..81: 32 / 32 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now consists of:

```
search23/k2_idx14_q8D_a7b11_state_results.tsv
search23/k2_idx14_q8D_a7b11_state_results_2x32.tsv
search23/k2_idx14_q8D_a7b11_p22_parity_results.tsv
search23/k2_idx14_q8D_a7b11_p23_parity_results.tsv
search23/k2_idx14_q8D_a7b11_p24_results.tsv
search23/k2_idx14_q8D_a7b11_p24_hard_results.tsv
```

with

```
total rows       656
closed rows       96
remaining rows   560
first remaining  (p,M)=(25,49)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=24` band.

## V397. q8 all-D `(7,11)` p25 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=25, M=49..80
```

with anti-tightness disabled.  The first pass used

```
5 jobs x 20 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p25_results.tsv
25 INFEASIBLE, 7 UNKNOWN, 0 FEASIBLE
```

The seven UNKNOWN rows were `M=72,75,76,77,78,79,80`.  Codex reran exactly
those rows at

```
5 jobs x 20 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p25_hard_results.tsv
7 / 7 INFEASIBLE
```

Thus the whole `p=25` band is closed:

```
p=25, M=49..80: 32 / 32 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      128
remaining rows   528
first remaining  (p,M)=(26,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=25` band.

## V398. q8 all-D `(7,11)` p26 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=26, M=48..79
```

with anti-tightness disabled.  The first pass used

```
5 jobs x 20 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p26_results.tsv
25 INFEASIBLE, 7 UNKNOWN, 0 FEASIBLE
```

The seven UNKNOWN rows were `M=72,74,75,76,77,78,79`.  Codex reran exactly
those rows at

```
5 jobs x 20 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p26_hard_results.tsv
7 / 7 INFEASIBLE
```

Thus the whole `p=26` band is closed:

```
p=26, M=48..79: 32 / 32 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      160
remaining rows   496
first remaining  (p,M)=(27,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=26` band.

## V399. q8 all-D `(7,11)` p27 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=27, M=48..78
```

with anti-tightness disabled.  The first pass used

```
5 jobs x 20 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p27_results.tsv
26 INFEASIBLE, 5 UNKNOWN, 0 FEASIBLE
```

The five UNKNOWN rows were `M=74,75,76,77,78`.  Codex reran exactly those rows
at

```
5 jobs x 20 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p27_hard_results.tsv
5 / 5 INFEASIBLE
```

Thus the whole `p=27` band is closed:

```
p=27, M=48..78: 31 / 31 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      191
remaining rows   465
first remaining  (p,M)=(28,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=27` band.

## V400. q8 all-D `(7,11)` p28 band closure

Update 2026-06-20:

Codex restored the batch-runner compute cap to the current goal limit of
`64` total solver workers, then ran the next q8 all-D `(7,11)` band

```
p=28, M=48..77
```

with anti-tightness disabled.  The first pass used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p28_results.tsv
25 INFEASIBLE, 5 UNKNOWN, 0 FEASIBLE
```

The five UNKNOWN rows were `M=72,74,75,76,77`.  Codex reran exactly those rows
at

```
4 jobs x 16 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p28_hard_results.tsv
5 / 5 INFEASIBLE
```

Thus the whole `p=28` band is closed:

```
p=28, M=48..77: 30 / 30 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      221
remaining rows   435
first remaining  (p,M)=(29,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=28` band.

## V401. q8 all-D `(7,11)` p29 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=29, M=48..76
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p29_results.tsv
26 INFEASIBLE, 3 UNKNOWN, 0 FEASIBLE
```

The three UNKNOWN rows were `M=74,75,76`.  Codex reran exactly those rows at

```
3 jobs x 16 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p29_hard_results.tsv
3 / 3 INFEASIBLE
```

Thus the whole `p=29` band is closed:

```
p=29, M=48..76: 29 / 29 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      250
remaining rows   406
first remaining  (p,M)=(30,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=29` band.

## V402. q8 all-D `(7,11)` p30 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=30, M=48..75
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p30_results.tsv
27 INFEASIBLE, 1 UNKNOWN, 0 FEASIBLE
```

The single UNKNOWN row was `M=74`.  Codex reran exactly that row at

```
1 job x 16 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p30_hard_results.tsv
1 / 1 INFEASIBLE
```

Thus the whole `p=30` band is closed:

```
p=30, M=48..75: 28 / 28 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      278
remaining rows   378
first remaining  (p,M)=(31,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=30` band.

## V403. q8 all-D `(7,11)` p31 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=31, M=48..74
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx14_q8D_a7b11_p31_results.tsv
25 INFEASIBLE, 2 UNKNOWN, 0 FEASIBLE
```

The two UNKNOWN rows were `M=70,74`.  Codex reran exactly those rows at

```
2 jobs x 16 solver workers, 600s per row
```

producing

```
search23/k2_idx14_q8D_a7b11_p31_hard_results.tsv
2 / 2 INFEASIBLE
```

Thus the whole `p=31` band is closed:

```
p=31, M=48..74: 27 / 27 INFEASIBLE
```

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      305
remaining rows   351
first remaining  (p,M)=(32,48)
```

Status: VERIFIED BAND CLOSURE.  No `FEASIBLE`, `NO_STATUS`, or remaining
`UNKNOWN` row exists in the `p=31` band.

## V404. q8 all-D `(7,11)` p32 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=32, M=48..73
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p32_results.tsv
26 / 26 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=32`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      331
remaining rows   325
first remaining  (p,M)=(33,48)
```

Status: VERIFIED BAND CLOSURE.

## V495. `K=2,T=2,q=8` support `{S1,S2,D}` closure

Update 2026-06-21:

Codex closed the next four-label exact-codegree-two support family

```
(c0,c1,c2,c3) = (0,2,2,4)
support = {S1,S2,D}
q=8, U=12
```

Here local domination forces the unique fixed `R`-skeleton:

```
R[S1,S2] = K_{2,2},  D isolated,  e_R = 4.
```

The initial labelled verifier with one full monochromatic cut added per
iteration stalled on this family (`CUT_LIMIT` / `UNKNOWN`).  The closure below
uses the exact fixed-`R` state-count quotient instead, with anti-tightness
disabled:

```
search23/state_count_6195_cpsat.py
```

For each side choice, Codex generated the full `(p,M)` grid compatible with
the edge window `112 <= e(G) <= 143`, the fixed values `U=12`, `e_R=4`, and
the state-count floor `M >= 44`.  Each grid was run by

```
search23/run_state_count_6195_tasks_batch.exe
```

with parameters

```
16 jobs x 4 solver workers, 60s per row,
--k 2 --cnt 0,2,2,4 --r0 8 --t 2 --disable-anti-tightness
--quotient-cut-rounds 1 --quotient-separator-timeout 1
```

Artifacts:

```
search23/k2_idx17_q8S1S2D_state_tasks.tsv
search23/k2_idx17_q8S1S2D_state_results_w16x4_60.tsv
search23/k2_idx18_q8S1S2D_state_tasks.tsv
search23/k2_idx18_q8S1S2D_state_results_w16x4_60.tsv
search23/k2_idx19_q8S1S2D_state_tasks.tsv
search23/k2_idx19_q8S1S2D_state_results_w16x4_60.tsv
search23/k2_idx20_q8S1S2D_state_tasks.tsv
search23/k2_idx20_q8S1S2D_state_results_w16x4_60.tsv
```

Audit:

```
idx=17 task=720 result=720 missing=0 extra=0 statuses=INFEASIBLE=720
idx=18 task=784 result=784 missing=0 extra=0 statuses=INFEASIBLE=784
idx=19 task=848 result=848 missing=0 extra=0 statuses=INFEASIBLE=848
idx=20 task=912 result=912 missing=0 extra=0 statuses=INFEASIBLE=912
```

Thus all `3264` exact `(p,M)` rows for the `K=2,T=2,q=8` support
`{S1,S2,D}` are closed by the exact state-count quotient, without
anti-tightness and without terminal-touch equalities.

Status: VERIFIED SUPPORT CLOSURE.

## V496. `K=2,T=2,q=8` support `{E,D}` closure

Update 2026-06-21:

Codex closed the next four-label exact-codegree-two support family

```
(c0,c1,c2,c3) = (1,0,0,7)
support = {E,D}
q=8, U=14
```

For this support, the `R`-skeleton has one empty-label vertex and seven
doubleton vertices.  Edge legality allows only `E-D` edges.  Local domination
requires the empty-label vertex to have at least two doubleton neighbours, so
up to the `D`-vertex symmetry the canonical star masks are

```
0x3, 0x7, 0xF, 0x1F, 0x3F, 0x7F
```

corresponding to star degrees `k=2..7`.

For star degree `k`,

```
root_edges = 22
U = 14
e_R = k
M_floor = 50 - 2k
112 <= 22 + 14 + k + p + M <= 143
p >= 2 max(|A|,|B|)
```

Codex generated the full `(mask,p,M)` grids for the four side choices
idx21-24 and ran the exact fixed-`R` state-count quotient with anti-tightness
disabled:

```
search23/run_state_count_6195_tasks_batch.exe
16 jobs x 4 solver workers, 60s per row,
--k 2 --cnt 1,0,0,7 --r0 8 --t 2 --disable-anti-tightness
```

Artifacts:

```
search23/k2_idx21_q8ED_a6b12_state_tasks.tsv
search23/k2_idx21_q8ED_a6b12_state_results_w16x4_60.tsv
search23/k2_idx22_q8ED_a7b11_state_tasks.tsv
search23/k2_idx22_q8ED_a7b11_state_results_w16x4_60.tsv
search23/k2_idx23_q8ED_a8b10_state_tasks.tsv
search23/k2_idx23_q8ED_a8b10_state_results_w16x4_60.tsv
search23/k2_idx24_q8ED_a9b9_state_tasks.tsv
search23/k2_idx24_q8ED_a9b9_state_results_w16x4_60.tsv
```

Audit:

```
idx=21 task=4416 result=4416 missing=0 extra=0 statuses=INFEASIBLE=4416
idx=22 task=4800 result=4800 missing=0 extra=0 statuses=INFEASIBLE=4800
idx=23 task=5184 result=5184 missing=0 extra=0 statuses=INFEASIBLE=5184
idx=24 task=5568 result=5568 missing=0 extra=0 statuses=INFEASIBLE=5568
TOTAL task=19968 result=19968 missing=0 extra=0 INFEASIBLE=19968 UNKNOWN=0 FEASIBLE=0
```

Thus all `19968` exact `(mask,p,M)` rows for the `K=2,T=2,q=8` support
`{E,D}` are closed by the exact state-count quotient, without anti-tightness
and without terminal-touch equalities.

Status: VERIFIED SUPPORT CLOSURE.

## V480. `k=1,q=8,c0=1,c1=7,(a,b)=(7,12)` state-count closure

Update 2026-06-21:

Codex closed the first `k=1,q=8,c0=1,c1=7` side choice using the exact
state-count quotient with anti-tightness disabled:

```
cnt=(1,7), (a,b)=(7,12), r0=8, t=2
```

The run was split only to retune parallelism.  The first part used

```
search23/k1_q8_a7b12_c1_w16_300.tsv
```

and closed `1966` rows.  The remaining unique tasks were then run with
`32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a7b12_c1_w2x32_300_part2.tsv
19306 / 19306 INFEASIBLE
```

Manifest audit over the original task file

```
search23/k1_q8_state_count_tasks/a7_b12_c01_c17.tasks.tsv
```

gives

```
task rows        21609
unique keys       4809
missing unique       0
extra unique         0
result statuses  INFEASIBLE=21272
UNKNOWN=0, FEASIBLE=0, other=0
```

The duplicate manifest rows have identical `(mask,p,M)` keys, which are the
only task fields used by the runner.  Thus the whole `(7,12)` side is closed
at the exact state-count level.

Status: VERIFIED SIDE CLOSURE.

## V514. K2/T2 q=9 four-label support `{E,D}`, profile `(3,0,0,6)`, idx52 and full profile closed

Update 2026-06-21:

For the final side of the same `q=9` four-label profile

```
(c0,c1,c2,c3)=(3,0,0,6), support={E,D},
idx52: (|A|,|B|)=(8,9),
```

Codex reused the `300` canonical `R`-skeleton masks from V512 and generated
the state-count grid

```
search23/k2_idx52_q9ED3_a8b9_state_tasks.tsv  69087 tasks
```

The first hidden `64 x 1` pass exited early after one `NO_STATUS` row.  The
valid `INFEASIBLE` rows were retained, the original task grid was recovered,
and continuation runs closed the remaining original task keys.

Artifacts:

```
search23/k2_idx52_q9ED3_a8b9_state_results_w64x1_60.tsv
search23/k2_idx52_q9ED3_a8b9_remaining_after_1261_results_w32x2_60.tsv
search23/k2_idx52_q9ED3_a8b9_remaining_after_recovery_results_w48x1_60.tsv
search23/k2_idx52_q9ED3_a8b9_unknown10_tasks.tsv
search23/k2_idx52_q9ED3_a8b9_unknown10_results_w4x16_600.tsv
search23/k2_idx52_q9ED3_a8b9_missing755_tasks.tsv
search23/k2_idx52_q9ED3_a8b9_missing755_results_w16x4_600.tsv
```

Audit:

```
original task grid: 69087 tasks
covered original keys: 69087
missing original keys: 0
FEASIBLE/OPTIMAL among covered keys: 0
UNKNOWN after targeted rerun: 0
```

The final targeted rerun closed the ten remaining rows

```
mask=0x1860c0
(p,M) in {(31,70),(31,71),(31,72),(31,73),
          (32,70),(32,71),(32,72),(33,70),(33,71),(34,70)}
```

with

```
10 / 10 INFEASIBLE
```

using timeout `600`, `4` parallel jobs, and `16` solver workers per job.

A final recovery run closed the last `755` original task keys missed by the
earlier recovery audit:

```
755 / 755 INFEASIBLE
```

using timeout `600`, `16` parallel jobs, and `4` solver workers per job.

Combining V512, V513, and this run gives the full side table for the profile
`(3,0,0,6)`:

```
idx50 (|A|,|B|)=(6,11): 69087 / 69087 INFEASIBLE
idx51 (|A|,|B|)=(7,10): 69087 / 69087 INFEASIBLE
idx52 (|A|,|B|)=(8,9):  69087 / 69087 INFEASIBLE
total:                  207261 / 207261 INFEASIBLE
```

Therefore the `q=9` four-label support `{E,D}` profile

```
(c0,c1,c2,c3)=(3,0,0,6)
```

is closed.

Status: VERIFIED FAMILY CLOSURE.

## V515. K2/T2 q=10 all-doubleton support `{D}`, idx53-55 closed

Update 2026-06-21:

The next four-label manifest block is the `q=10` all-doubleton support

```
(c0,c1,c2,c3)=(0,0,0,10), support={D},
idx53-55, sides (6,10), (7,9), (8,8).
```

Here `R` has no legal edges, so `e_R=0`.  The fixed root and label edges are

```
root_edges + U = (30-q) + 2q = 20 + 20 = 40.
```

The finite edge upper bound gives

```
p + M <= 143 - 40 = 103.
```

The exact-two-root unpaired cut family gives, at `W=empty`,

```
p >= 37
M_A >= 35
M_B >= 35
```

and hence

```
p + M >= 37 + 70 = 107.
```

This contradicts `p+M<=103`, independently of the side choice.

Audit:

```
idx53: scalar contradiction
idx54: scalar contradiction
idx55: scalar contradiction
```

Status: VERIFIED FAMILY CLOSURE.

## V509. K2/T2 q=9 support `{E,D}`, profile `(2,0,0,7)`, idx47 closed

Update 2026-06-21:

The next `q=9` `{E,D}` block has two empty-label vertices and seven
doubleton vertices.  The generalized `E-D` skeleton generator gives 55
canonical masks for the profile `(c0,c1,c2,c3)=(2,0,0,7)`.

For side choice `(a,b)=(6,11)`, idx47, the state-count task grid contains
8029 original `(mask,p,M)` keys:

```
search23/k2_idx47_q9ED2_a6b11_state_tasks.tsv
```

Artifacts:

```
search23/k2_idx47_q9ED2_a6b11_state_results_w16x4_60.tsv
search23/k2_idx47_q9ED2_a6b11_unknown3_results_w3x20_600.tsv
```

Audit:

```
idx47: 8029 / 8029 INFEASIBLE
missing: 0
UNKNOWN after targeted rerun: 0
```

Status: VERIFIED ROW CLOSURE.

## V518. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,2,6)`, idx57 closed

Update 2026-06-21:

For side `(A,B)=(7,9)`, idx57, the fixed-R state-count grid has 45
`(p,M)` rows:

```
search23/k2_idx57_q10S1S2D_a7b9_state_tasks.tsv
```

The short count-quotient pass closed 12 rows and left 33 rows for the
labelled exact A/B verifier.  The labelled verifier uses the fixed
`K_{2,2}` R-core, exact `p`, exact `M`, sorted labelled A/B state rows,
full local codegree constraints, full Psi cuts, K2 unpaired cuts, and the
split-C static cuts for all `T subset D`.

Artifacts:

```
search23/verify_k2_q10_0226_labelled.py
search23/k2_idx57_q10S1S2D_a7b9_labelled_remaining33_results.tsv
search23/k2_idx57_q10S1S2D_a7b9_labelled_unknown12_splitC_results.tsv
search23/k2_idx57_q10S1S2D_p33m70_labelled_MAbranches_splitC_results.tsv
```

Audit:

```
initial labelled pass: 21 INFEASIBLE, 12 UNKNOWN
split-C rerun of UNKNOWN rows: 11 INFEASIBLE, 1 UNKNOWN
remaining (p,M)=(33,70) split by MA=31..39: 9 / 9 INFEASIBLE
idx57 total: 45 / 45 INFEASIBLE
missing: 0
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx57 after
the MA-branch split.

Status: VERIFIED ROW CLOSURE.

## V518. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,2,6)`, idx57 closed

Update 2026-06-21:

For side `(A,B)=(7,9)`, idx57, the fixed-R state-count grid has 45
`(p,M)` rows:

```
search23/k2_idx57_q10S1S2D_a7b9_state_tasks.tsv
```

The closure audit combines four independently recorded sources:

```
state-count short pass: 12 rows
labelled exact A/B verifier, timeout120: 21 rows
split-C labelled retry, timeout180: 11 rows
MA/MB branch family for (p,M)=(33,70): 1 row
```

The decisive files are:

```
search23/k2_idx57_q10S1S2D_a7b9_state_results_w16x4_60.tsv
search23/k2_idx57_q10S1S2D_a7b9_labelled_remaining33_results.tsv
search23/k2_idx57_q10S1S2D_a7b9_labelled_unknown12_splitC_results.tsv
search23/k2_idx57_q10S1S2D_p33m70_labelled_MAbranches.tsv
search23/k2_idx57_q10S1S2D_p33m70_labelled_MAinner_w64.tsv
```

For the last row `(p,M)=(33,70)`, all possible side-load branches
`MA+MB=70`, `31<=MA<=39`, are infeasible.

Audit:

```
idx57: 45 / 45 INFEASIBLE
missing: 0
```

Status: VERIFIED ROW CLOSURE.

## V510. K2/T2 q=9 support `{E,D}`, profile `(2,0,0,7)`, idx48 closed

Update 2026-06-21:

For the same profile `(2,0,0,7)`, side choice `(a,b)=(7,10)`, idx48,
the state-count task grid contains 8029 original `(mask,p,M)` keys:

```
search23/k2_idx48_q9ED2_a7b10_state_tasks.tsv
```

Artifacts:

```
search23/k2_idx48_q9ED2_a7b10_state_results_w16x4_60.tsv
search23/k2_idx48_q9ED2_a7b10_state_results_remaining_w16x4_60.tsv
search23/k2_idx48_q9ED2_a7b10_unknown3_results_w3x20_600.tsv
```

Audit:

```
idx48: 8029 / 8029 INFEASIBLE
missing: 0
UNKNOWN after targeted rerun: 0
```

Status: VERIFIED ROW CLOSURE.

## V511. K2/T2 q=9 support `{E,D}`, profile `(2,0,0,7)`, idx47-49 closed

Update 2026-06-21:

The full side family for profile `(2,0,0,7)` consists of idx47-49.
Idx47 and idx48 are V509-V510.  Idx49, side `(a,b)=(8,9)`, was closed
by the full/targeted result union:

```
search23/k2_idx49_q9ED2_a8b9_state_results_full_w16x4_60.tsv
search23/k2_idx49_q9ED2_a8b9_remaining5_results_w5x12_600.tsv
```

Audit:

```
idx47: 8029 / 8029 INFEASIBLE
idx48: 8029 / 8029 INFEASIBLE
idx49: 8029 / 8029 INFEASIBLE
total: 24087 / 24087 INFEASIBLE
missing: 0
UNKNOWN after targeted reruns: 0
```

Status: VERIFIED FAMILY CLOSURE.

## V512. K2/T2 q=9 support `{E,D}`, profile `(3,0,0,6)`, idx50 closed

Update 2026-06-21:

The next `{E,D}` profile is `(c0,c1,c2,c3)=(3,0,0,6)`.  The generalized
`E-D` skeleton generator gives 300 canonical masks, and each side grid has
69087 original `(mask,p,M)` keys.

For idx50, side `(a,b)=(6,11)`, the trusted result union is:

```
search23/k2_idx50_q9ED3_a6b11_state_results_clean_w16x4_60.tsv
search23/k2_idx50_q9ED3_a6b11_remaining2_results_w64x1_60.tsv
```

Audit:

```
idx50: 69087 / 69087 INFEASIBLE
missing: 0
UNKNOWN after recovery: 0
```

Status: VERIFIED ROW CLOSURE.

## V513. K2/T2 q=9 support `{E,D}`, profile `(3,0,0,6)`, idx51 closed

Update 2026-06-21:

For idx51, side `(a,b)=(7,10)`, the first pass produced 69077
`INFEASIBLE` rows and 10 `UNKNOWN` rows.  The targeted ten-row rerun closed
all ten.

Artifacts:

```
search23/k2_idx51_q9ED3_a7b10_state_results_w64x1_60.tsv
search23/k2_idx51_q9ED3_a7b10_unknown10_results_w4x16_600.tsv
```

Audit:

```
idx51: 69087 / 69087 INFEASIBLE
missing: 0
UNKNOWN after targeted rerun: 0
```

Status: VERIFIED ROW CLOSURE.

## V514. K2/T2 q=9 support `{E,D}`, profile `(3,0,0,6)`, idx50-52 closed

Update 2026-06-21:

Idx52, side `(a,b)=(8,9)`, initially had crash/recovery holes.  The hard
ten-row rerun closed the genuine `UNKNOWN` rows, and the final 755-key
recovery closed the remaining uncovered original task keys.

Trusted idx52 result union:

```
search23/k2_idx52_q9ED3_a8b9_state_results_w64x1_60.tsv
search23/k2_idx52_q9ED3_a8b9_remaining_after_recovery_results_w48x1_60.tsv
search23/k2_idx52_q9ED3_a8b9_unknown10_results_w4x16_600.tsv
search23/k2_idx52_q9ED3_a8b9_missing755_results_w16x4_600.tsv
```

Audit:

```
idx52: 69087 / 69087 INFEASIBLE
missing: 0
uncovered non-INFEASIBLE rows: 0

idx50-52 total: 207261 / 207261 INFEASIBLE
missing: 0
UNKNOWN after targeted/recovery reruns: 0
```

Status: VERIFIED FAMILY CLOSURE.

## V513. K2/T2 q=9 four-label support `{E,D}`, profile `(3,0,0,6)`, idx51 side closed

Update 2026-06-21:

For the same `q=9` four-label profile

```
(c0,c1,c2,c3)=(3,0,0,6), support={E,D},
idx51: (|A|,|B|)=(7,10),
```

Codex reused the `300` canonical `R`-skeleton masks from V512 and generated
the state-count grid

```
search23/k2_idx51_q9ED3_a7b10_state_tasks.tsv  69087 tasks
```

The grid used `U=12`, `root_edges=21`, exact per-mask `e_R`, exact
per-mask degree floors, the finite edge window, K2 unpaired cuts, exact
`p`, exact `M`, typewise state-count constraints, and the K2 anti-tightness
disabled.

Artifacts:

```
search23/k2_idx51_q9ED3_a7b10_state_results_w64x1_60.tsv
search23/k2_idx51_q9ED3_a7b10_unknown10_tasks.tsv
search23/k2_idx51_q9ED3_a7b10_unknown10_results_w10x6_600.tsv
```

Audit:

```
first pass:       69077 INFEASIBLE, 10 UNKNOWN, 0 FEASIBLE
targeted rerun:      10 / 10 INFEASIBLE
original task grid: 69087 tasks
covered original keys: 69087
missing original keys: 0
FEASIBLE/OPTIMAL among covered keys: 0
UNKNOWN after targeted rerun: 0
```

The ten first-pass `UNKNOWN` rows all had mask `0x1860c0` and were closed
by the targeted run with timeout `600`, `10` parallel jobs, and `6` solver
workers per job.

Thus the `idx51` side of the profile `(3,0,0,6)` is closed.

Status: VERIFIED SIDE CLOSURE.

## V511. K2/T2 q=9 four-label support `{E,D}`, profile `(2,0,0,7)`, idx47-49 closed

Update 2026-06-21:

For the `q=9` four-label profile

```
(c0,c1,c2,c3)=(2,0,0,7), support={E,D},
```

Codex generated 55 canonical triangle-free locally dominated `R`-skeleton
masks under the `S_2 x S_7` action.  For each of the three side choices
`(|A|,|B|)=(6,11),(7,10),(8,9)`, the state-count grid has 8029 tasks.

Side-instance artifacts:

```
idx47:
  search23/k2_idx47_q9ED2_a6b11_state_results_w16x4_60.tsv
  search23/k2_idx47_q9ED2_a6b11_unknown3_results_w3x20_600.tsv

idx48:
  search23/k2_idx48_q9ED2_a7b10_state_results_full_w16x4_60.tsv
  search23/k2_idx48_q9ED2_a7b10_state_results_remaining_w16x4_60.tsv
  search23/k2_idx48_q9ED2_a7b10_unknown3_results_w3x20_600.tsv

idx49:
  search23/k2_idx49_q9ED2_a8b9_state_results_full_w16x4_60.tsv
  search23/k2_idx49_q9ED2_a8b9_remaining5_tasks.tsv
  search23/k2_idx49_q9ED2_a8b9_remaining5_results_w5x12_600.tsv
```

Audit:

```
idx47: 8026 first-pass INFEASIBLE + 3 targeted INFEASIBLE = 8029 / 8029
idx48: 6251 partial INFEASIBLE + 1775 continuation INFEASIBLE
       + 3 targeted INFEASIBLE = 8029 / 8029
idx49: 8024 keyed first-pass INFEASIBLE + 5 targeted INFEASIBLE = 8029 / 8029
total: 24087 / 24087 INFEASIBLE
```

The idx49 first-pass output contained one malformed result row, so Codex
used the original task grid and the valid keyed `INFEASIBLE` rows to recover
the five remaining task keys before rerunning them.  The recovery file is

```
search23/k2_idx49_q9ED2_a8b9_remaining5_tasks.tsv
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx47-49
after the targeted reruns.

Status: VERIFIED FAMILY CLOSURE.

## V512. K2/T2 q=9 four-label support `{E,D}`, profile `(3,0,0,6)`, idx50 side closed

Update 2026-06-21:

The next `q=9` four-label manifest block is

```
(c0,c1,c2,c3)=(3,0,0,6), support={E,D},
idx50: (|A|,|B|)=(6,11).
```

Codex generated canonical `R`-skeletons for three empty-label vertices and
six doubleton vertices.  The generator represents the `E-D` layer as a
multiset of six columns over the three empty vertices, with optional
`E-E` edges, canonicalized under `S3 x S6`.  It enforces triangle-freeness
and local domination, namely each empty-label vertex has at least two
doubleton neighbours.

Artifacts:

```
search23/k2_ed_skeletons.cpp
search23/k2_ed_skeletons.exe
search23/k2_q9_ed3_skeletons.tsv
search23/k2_idx50_q9ED3_a6b11_state_tasks.tsv
```

The skeleton file contains `300` canonical masks.  The state-count task grid
contains `69087` tasks and uses `U=12`, `root_edges=21`, exact per-mask
`e_R`, exact per-mask degree floors, the finite edge window, K2 unpaired
cuts, exact `p`, exact `M`, typewise state-count constraints, and the K2
anti-tightness disabled.

Primary and recovery artifacts:

```
search23/k2_idx50_q9ED3_a6b11_smoke5_results.tsv
search23/k2_idx50_q9ED3_a6b11_state_results_w16x4_60.tsv.collision_20260621_140628
search23/k2_idx50_q9ED3_a6b11_remaining_results_w64x1_60.tsv
search23/k2_idx50_q9ED3_a6b11_remaining2_tasks.tsv
search23/k2_idx50_q9ED3_a6b11_remaining2_results_w64x1_60.tsv
```

Audit:

```
original task grid: 69087 tasks
covered original keys: 69087
missing original keys: 0
FEASIBLE/OPTIMAL among covered keys: 0
UNKNOWN among covered keys: 0
```

The final hidden `64 x 1` continuation run closed

```
67975 / 67975 INFEASIBLE
```

and the union of valid `INFEASIBLE` rows from the recovery artifacts covers
every original task key.  Extra stale keys from interrupted/collision runs
were ignored in the audit; only membership in the original task grid was
counted.

Thus the `idx50` side of the profile `(3,0,0,6)` is closed.

Status: VERIFIED SIDE CLOSURE.

## V513. K2/T2 q=9 four-label support `{E,D}`, profile `(3,0,0,6)`, idx51 side closed

Update 2026-06-21:

For the same `q=9` four-label profile

```
(c0,c1,c2,c3)=(3,0,0,6), support={E,D},
idx51: (|A|,|B|)=(7,10).
```

Codex reused the `300` canonical skeleton-mask grid from V512 and generated
the state-count task grid

```
search23/k2_idx51_q9ED3_a7b10_state_tasks.tsv  69087 tasks
```

The grid uses `U=12`, `root_edges=21`, exact per-mask `e_R`, exact per-mask
degree floors, the finite edge window, K2 unpaired cuts, exact `p`, exact `M`,
typewise state-count constraints, and the K2 anti-tightness disabled.

Artifacts:

```
search23/k2_idx51_q9ED3_a7b10_state_results_w64x1_60.tsv
search23/k2_idx51_q9ED3_a7b10_unknown10_tasks.tsv
search23/k2_idx51_q9ED3_a7b10_unknown10_results_w4x16_600.tsv
```

Audit:

```
original task grid: 69087 tasks
first pass: 69077 INFEASIBLE, 10 UNKNOWN, 0 FEASIBLE
targeted rerun: 10 / 10 INFEASIBLE
covered original keys: 69087
missing original keys: 0
FEASIBLE/OPTIMAL among covered keys: 0
UNKNOWN after targeted override: 0
```

Thus the `idx51` side of the profile `(3,0,0,6)` is closed.

Status: VERIFIED SIDE CLOSURE.

## V510. K2/T2 q=9 four-label support `{E,D}`, profile `(2,0,0,7)`, idx48 side closed

Update 2026-06-21:

For the same `q=9` four-label profile

```
(c0,c1,c2,c3)=(2,0,0,7), support={E,D},
idx48: (|A|,|B|)=(7,10),
```

Codex reused the 55 canonical `R`-skeleton masks from V509 and generated
the state-count grid

```
search23/k2_idx48_q9ED2_a7b10_state_tasks.tsv  8029 tasks
```

Artifacts:

```
search23/k2_idx48_q9ED2_a7b10_state_results_full_w16x4_60.tsv
search23/k2_idx48_q9ED2_a7b10_state_tasks_remaining_after_partial.tsv
search23/k2_idx48_q9ED2_a7b10_state_results_remaining_w16x4_60.tsv
search23/k2_idx48_q9ED2_a7b10_unknown3_tasks.tsv
search23/k2_idx48_q9ED2_a7b10_unknown3_results_w3x20_600.tsv
```

Audit:

```
partial first pass before interruption: 6251 INFEASIBLE
remaining-task continuation: 1775 INFEASIBLE, 3 UNKNOWN, 0 FEASIBLE
targeted rerun: 3 / 3 INFEASIBLE
combined: 8029 / 8029 INFEASIBLE
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx48
after the targeted rerun.  The sibling side instance idx49 remains to be
checked for this profile.

Status: VERIFIED SIDE CLOSURE.

## V483. `k=1,q=8,c0=1,c1=7,(a,b)=(11,8)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V482.  The two task manifests

```
search23/k1_q8_state_count_tasks/a8_b11_c01_c17.tasks.tsv
search23/k1_q8_state_count_tasks/a11_b8_c01_c17.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(8,11) unique keys   4809
(11,8) unique keys   4809
symmetric difference    0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V482 also closes the `(11,8)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V484. `k=1,q=8,c0=1,c1=7,(a,b)=(9,10)` state-count closure

Update 2026-06-21:

Codex closed the central `k=1,q=8,c0=1,c1=7` direct side choice using the
exact state-count quotient with anti-tightness disabled:

```
cnt=(1,7), (a,b)=(9,10), r0=8, t=2
```

The duplicate manifest rows were collapsed to the unique task file

```
search23/k1_q8_a9b10_c1_unique.tasks.tsv
```

and run with `32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a9b10_c1_unique_w2x32_300.tsv
4809 / 4809 INFEASIBLE
```

Audit against the full manifest

```
search23/k1_q8_state_count_tasks/a9_b10_c01_c17.tasks.tsv
```

gives

```
task rows        21609
unique keys       4809
result rows       4809
missing unique       0
extra unique         0
UNKNOWN=0, FEASIBLE=0, other=0
```

The whole `(9,10)` side is therefore closed at the exact state-count level.

Status: VERIFIED SIDE CLOSURE.

## V485. `k=1,q=8,c0=1,c1=7,(a,b)=(10,9)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V484.  The two task manifests

```
search23/k1_q8_state_count_tasks/a9_b10_c01_c17.tasks.tsv
search23/k1_q8_state_count_tasks/a10_b9_c01_c17.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(9,10) unique keys   4809
(10,9) unique keys   4809
symmetric difference    0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V484 also closes the `(10,9)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V486. `k=1,q=8,c0=1,c1=7` six-side closure

Update 2026-06-21:

The full `k=1,q=8,c0=1,c1=7` six-side family is now closed.

Direct state-count closures:

```
(a,b)=(7,12):  unique keys 4809 / 4809 INFEASIBLE  (V480)
(a,b)=(8,11):  unique keys 4809 / 4809 INFEASIBLE  (V482)
(a,b)=(9,10):  unique keys 4809 / 4809 INFEASIBLE  (V484)
```

A/B root-swap closures:

```
(a,b)=(12,7):  V481
(a,b)=(11,8):  V483
(a,b)=(10,9):  V485
```

Each direct closure used the exact state-count quotient with anti-tightness
disabled, timeout `300s`, and total worker count at most `64`.

Status: VERIFIED FAMILY CLOSURE.

## V509. K2/T2 q=9 four-label support `{E,D}`, profile `(2,0,0,7)`, idx47 side closed

Update 2026-06-21:

The next `q=9` four-label manifest block begins with

```
(c0,c1,c2,c3)=(2,0,0,7), support={E,D},
idx47: (|A|,|B|)=(6,11).
```

There are two empty-label vertices and seven doubleton vertices.  Allowed
`R`-edges are `E-E` and `E-D`; local domination forces each empty-label
vertex to have at least two `D`-neighbours.  Codex generated canonical
triangle-free skeletons under the `S_2 x S_7` action.

Artifacts:

```
search23/k2_q9_ed2_skeletons.tsv
search23/k2_idx47_q9ED2_a6b11_state_tasks.tsv
search23/k2_idx47_q9ED2_a6b11_state_results_w16x4_60.tsv
search23/k2_idx47_q9ED2_a6b11_unknown3_tasks.tsv
search23/k2_idx47_q9ED2_a6b11_unknown3_results_w3x20_600.tsv
```

Audit:

```
canonical skeleton masks: 55
idx47 task grid: 8029 tasks
first pass: 8026 / 8029 INFEASIBLE, 3 UNKNOWN, 0 FEASIBLE
targeted rerun: 3 / 3 INFEASIBLE
combined: 8029 / 8029 INFEASIBLE
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx47
after the targeted rerun.  The sibling side instances idx48 and idx49 remain
to be checked for this profile.

Status: VERIFIED SIDE CLOSURE.

## V505. `K=2,T=2,q=9` support `{S1,S2,D}`, profile `(0,3,3,3)` closure

Update 2026-06-21:

The final `q=9` `{S1,S2,D}` profile is

```
(c0,c1,c2,c3)=(0,3,3,3).
```

Here `R[S1,S2]` is a `3 x 3` bipartite graph with minimum degree at least
`2`.  Equivalently, its complement is a matching of size `m=0,1,2,3`.
Codex used the four canonical masks

```
m=0: mask=0x1ff, e_R=9, m_floor=42
m=1: mask=0x1fe, e_R=8, m_floor=44
m=2: mask=0x1ee, e_R=7, m_floor=46
m=3: mask=0xee,  e_R=6, m_floor=48
```

with `U=12`, all `D` vertices isolated, and the K2 unpaired empty-cut task
filters.  This produced `714` tasks for each side:

```
search23/k2_idx38_q9S1S2D_a6b11_state_tasks.tsv
search23/k2_idx39_q9S1S2D_a7b10_state_tasks.tsv
search23/k2_idx40_q9S1S2D_a8b9_state_tasks.tsv
```

First pass artifacts:

```
search23/k2_idx38_q9S1S2D_a6b11_state_results_w16x4_60.tsv
search23/k2_idx39_q9S1S2D_a7b10_state_results_w16x4_60.tsv
search23/k2_idx40_q9S1S2D_a8b9_state_results_w16x4_60.tsv
```

The idx40 first pass left two `OPTIMAL` count candidates with
`quotient_mono=36` and `quotient_mono=34`; rerunning those two rows with
`quotient_cut_rounds=10` closed both:

```
search23/k2_idx40_q9S1S2D_a8b9_optimal_tasks.tsv
search23/k2_idx40_q9S1S2D_a8b9_optimal_results_w2x16_q10_300.tsv
```

Audit:

```
idx38: 714 / 714 INFEASIBLE
idx39: 714 / 714 INFEASIBLE
idx40: 712 first-pass INFEASIBLE + 2 rerun INFEASIBLE = 714 / 714
total: 2142 / 2142 INFEASIBLE
```

Thus the profile `(c0,c1,c2,c3)=(0,3,3,3)` is closed.

Status: VERIFIED FAMILY CLOSURE.

## V506. Full `K=2,T=2,q=9` support `{S1,S2,D}` closure

Update 2026-06-21:

The four-label manifest contains exactly these `q=9` support `{S1,S2,D}`
profile-side blocks:

```
idx32-34: (c0,c1,c2,c3)=(0,2,2,5), closed by V503
idx35-37: (c0,c1,c2,c3)=(0,2,3,4), closed by V504
idx38-40: (c0,c1,c2,c3)=(0,3,3,3), closed by V505
```

Therefore the full `K=2,T=2,q=9` support `{S1,S2,D}` family is closed.

Status: VERIFIED SUPPORT CLOSURE.

## V504. `K=2,T=2,q=9` support `{S1,S2,D}`, profile `(0,2,3,4)` closure

Update 2026-06-21:

The next `q=9` four-label manifest block is

```
(c0,c1,c2,c3)=(0,2,3,4), support={S1,S2,D}.
```

Local domination forces every `S2` vertex to see both `S1` vertices, hence
`R[S1,S2]=K_{2,3}` and all `D` vertices are isolated.  In canonical label
order the fixed mask is

```
mask=0x3f, e_R=6, U=13.
```

Codex generated fixed-skeleton state-count grids using the K2 unpaired
empty-cut filters and the edge window:

```
search23/k2_idx35_q9S1S2D_a6b11_state_tasks.tsv  120 tasks
search23/k2_idx36_q9S1S2D_a7b10_state_tasks.tsv  120 tasks
search23/k2_idx37_q9S1S2D_a8b9_state_tasks.tsv   120 tasks
```

Artifacts:

```
search23/k2_idx35_q9S1S2D_a6b11_state_results_w16x4_60.tsv
search23/k2_idx36_q9S1S2D_a7b10_state_results_w16x4_60.tsv
search23/k2_idx37_q9S1S2D_a8b9_state_results_w16x4_60.tsv
```

Audit:

```
idx35: 120 / 120 INFEASIBLE
idx36: 120 / 120 INFEASIBLE
idx37: 120 / 120 INFEASIBLE
total: 360 / 360 INFEASIBLE
```

There is no `FEASIBLE`, `UNKNOWN`, or missing row for idx35-37.

Status: VERIFIED FAMILY CLOSURE.

## V503. `K=2,T=2,q=9` support `{S1,S2,D}`, profile `(0,2,2,5)` closure

Update 2026-06-21:

The next `q=9` four-label manifest block is

```
(c0,c1,c2,c3)=(0,2,2,5), support={S1,S2,D}.
```

Local domination forces `R[S1,S2]=K_{2,2}` and all `D` vertices are isolated.
In canonical label order the fixed `R` mask is

```
mask=0xf, e_R=4, U=14.
```

Codex generated exact state-count task grids using the K2 unpaired empty-cut
filters (`p+e_R>=37`, `M+2e_R>=70`) and the usual edge window, producing:

```
search23/k2_idx32_q9S1S2D_a6b11_state_tasks.tsv  55 tasks
search23/k2_idx33_q9S1S2D_a7b10_state_tasks.tsv  55 tasks
search23/k2_idx34_q9S1S2D_a8b9_state_tasks.tsv   55 tasks
```

First pass artifacts:

```
search23/k2_idx32_q9S1S2D_a6b11_state_results_w16x4_60.tsv
search23/k2_idx33_q9S1S2D_a7b10_state_results_w16x4_60.tsv
search23/k2_idx34_q9S1S2D_a8b9_state_results_w16x4_60.tsv
```

Targeted rerun artifacts for the first-pass `UNKNOWN` rows:

```
search23/k2_idx32_q9S1S2D_a6b11_unknown_results_w7x8_300.tsv
search23/k2_idx33_q9S1S2D_a7b10_unknown_results_w8x8_300.tsv
search23/k2_idx34_q9S1S2D_a8b9_unknown_results_w8x8_300.tsv
```

Audit:

```
idx32: first pass 48 INFEASIBLE + rerun 7 INFEASIBLE = 55 / 55
idx33: first pass 35 INFEASIBLE + rerun 20 INFEASIBLE = 55 / 55
idx34: first pass 34 INFEASIBLE + rerun 21 INFEASIBLE = 55 / 55
total: 165 / 165 INFEASIBLE
```

All rerun files have `rerunBad=0`; no `FEASIBLE`, `UNKNOWN`, or missing row
remains for idx32-34.

Status: VERIFIED FAMILY CLOSURE.

## V501. Full `K=2,T=2,q=8` four-label frontier closure

Update 2026-06-21:

Codex audited the four-label exact-two-root manifest

```
search23/k2_four_label_profile_instances.tsv
```

For `q=8`, the manifest contains exactly the following `16` profile-side
instances:

```
idx13-16: (c0,c1,c2,c3)=(0,0,0,8), support={D}
idx17-20: (c0,c1,c2,c3)=(0,2,2,4), support={S1,S2,D}
idx21-24: (c0,c1,c2,c3)=(1,0,0,7), support={E,D}
idx25-28: (c0,c1,c2,c3)=(2,0,0,6), support={E,D}
```

These instances are closed by the following verified records:

```
idx13-16: V476
idx17-20: V495
idx21-24: V496
idx25-28: V497, V498, V499, V500
```

Therefore every `K=2,T=2,q=8` four-label profile-side instance in the
manifest is closed.  The next unclosed exact-two-root manifest row begins at
`q=9`, `idx29`.

Status: VERIFIED Q8 FRONTIER CLOSURE.

## V502. `K=2,T=2,q=9` all-doubleton support closure

Update 2026-06-21:

Codex audited the four-label exact-two-root manifest

```
search23/k2_four_label_profile_instances.tsv
```

The `q=9` all-doubleton support consists exactly of:

```
idx29: (c0,c1,c2,c3)=(0,0,0,9), (|A|,|B|)=(6,11)
idx30: (c0,c1,c2,c3)=(0,0,0,9), (|A|,|B|)=(7,10)
idx31: (c0,c1,c2,c3)=(0,0,0,9), (|A|,|B|)=(8,9)
```

Here every `R`-vertex has label `D={1,2}`, so no `R`-edge is legal:

```
e_R=0, U=18, root_edges=30-q=21.
```

Thus every graph in this support has

```
e(G)=21+18+p+M=39+p+M.
```

The finite edge window gives `e(G)<=143`, hence

```
p+M<=104.              (1)
```

The unpaired exact-two-root cuts with `W=empty` give:

```
U1: 2 + gamma(R) + e_R >= 37,
U2: 2 + alpha(R) + e_R >= 37,
U3: p + e_R >= 37.
```

Adding `U1` and `U2` gives

```
M + 2e_R >= 70.
```

Since `e_R=0`, this yields

```
M>=70, p>=37.
```

Therefore `p+M>=107`, contradicting (1).  Hence idx29, idx30, and idx31
are all infeasible without any A/B state enumeration.

Implementation note: `search23/state_count_6195_cpsat.py` now includes the
K2 unpaired cut family and an early `reason=k2_unpaired_empty_cut` scalar
filter for the `W=empty` consequences above.

Status: VERIFIED FAMILY CLOSURE.

## V487. `k=1,q=8,c0=2,c1=6,(a,b)=(7,12)` state-count closure

Update 2026-06-21:

Codex closed the first `k=1,q=8,c0=2,c1=6` direct side choice using the
exact state-count quotient with anti-tightness disabled:

```
cnt=(2,6), (a,b)=(7,12), r0=8, t=2
```

The duplicate manifest rows were collapsed to the unique task file

```
search23/k1_q8_a7b12_c2_unique.tasks.tsv
```

and run with `32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a7b12_c2_unique_w2x32_300.tsv
47424 / 47424 INFEASIBLE
```

Audit against the full manifest

```
search23/k1_q8_state_count_tasks/a7_b12_c02_c16.tasks.tsv
```

gives

```
task rows        287248
unique keys       47424
result rows       47424
missing unique        0
extra unique          0
UNKNOWN=0, FEASIBLE=0, other=0
```

Status: VERIFIED SIDE CLOSURE.

## V488. `k=1,q=8,c0=2,c1=6,(a,b)=(12,7)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V487.  The two task manifests

```
search23/k1_q8_state_count_tasks/a7_b12_c02_c16.tasks.tsv
search23/k1_q8_state_count_tasks/a12_b7_c02_c16.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(7,12) unique keys    47424
(12,7) unique keys    47424
symmetric difference      0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V487 also closes the `(12,7)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V489. `k=1,q=8,c0=2,c1=6,(a,b)=(8,11)` state-count closure

Update 2026-06-21:

Codex closed the second `k=1,q=8,c0=2,c1=6` direct side choice using the
exact state-count quotient with anti-tightness disabled:

```
cnt=(2,6), (a,b)=(8,11), r0=8, t=2
```

The duplicate manifest rows were collapsed to the unique task file

```
search23/k1_q8_a8b11_c2_unique.tasks.tsv
```

and run with `32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a8b11_c2_unique_w2x32_300.tsv
48048 / 48048 INFEASIBLE
```

Audit against the full manifest

```
search23/k1_q8_state_count_tasks/a8_b11_c02_c16.tasks.tsv
```

gives

```
unique keys       48048
result rows       48048
missing unique        0
extra unique          0
UNKNOWN=0, FEASIBLE=0, other=0
```

Status: VERIFIED SIDE CLOSURE.

## V490. `k=1,q=8,c0=2,c1=6,(a,b)=(11,8)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V489.  The two task manifests

```
search23/k1_q8_state_count_tasks/a8_b11_c02_c16.tasks.tsv
search23/k1_q8_state_count_tasks/a11_b8_c02_c16.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(8,11) unique keys    48048
(11,8) unique keys    48048
symmetric difference      0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V489 also closes the `(11,8)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V491. `k=1,q=8,c0=2,c1=6,(a,b)=(9,10)` state-count closure

Update 2026-06-21:

Codex closed the central `k=1,q=8,c0=2,c1=6` direct side choice using the
exact state-count quotient with anti-tightness disabled:

```
cnt=(2,6), (a,b)=(9,10), r0=8, t=2
```

The duplicate manifest rows were collapsed to the unique task file

```
search23/k1_q8_a9b10_c2_unique.tasks.tsv
```

and run with `32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a9b10_c2_unique_w2x32_300.tsv
48048 / 48048 INFEASIBLE
```

Audit against the full manifest

```
search23/k1_q8_state_count_tasks/a9_b10_c02_c16.tasks.tsv
```

gives

```
unique keys       48048
result rows       48048
missing unique        0
extra unique          0
UNKNOWN=0, FEASIBLE=0, other=0
```

Status: VERIFIED SIDE CLOSURE.

## V492. `k=1,q=8,c0=2,c1=6,(a,b)=(10,9)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V491.  The two task manifests

```
search23/k1_q8_state_count_tasks/a9_b10_c02_c16.tasks.tsv
search23/k1_q8_state_count_tasks/a10_b9_c02_c16.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(9,10) unique keys    48048
(10,9) unique keys    48048
symmetric difference      0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V491 also closes the `(10,9)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V493. Full `k=1,q=8,c0=2,c1=6` six-side family closure

Update 2026-06-21:

The direct root-side representatives are now closed:

```
(a,b)=(7,12): V487, 47424 / 47424 INFEASIBLE
(a,b)=(8,11): V489, 48048 / 48048 INFEASIBLE
(a,b)=(9,10): V491, 48048 / 48048 INFEASIBLE
```

Their A/B root-swap mates are closed by identical unique task-key audits:

```
(a,b)=(12,7): V488
(a,b)=(11,8): V490
(a,b)=(10,9): V492
```

Together with the model-symmetry audit in V479, these six entries exhaust the
root-side choices for `k=1,q=8,c0=2,c1=6`.

Status: VERIFIED FAMILY CLOSURE.

## V494. Full `k=1,q=8` cap-143 delta frontier closure

Update 2026-06-21:

V384 isolated the entire new cap-143 low-codegree delta to the six
`k=1,q=8` root-side choices

```
(a,b)=(7,12), (8,11), (9,10), (10,9), (11,8), (12,7).
```

V385 showed that these choices have only three label-count families:

```
(c0,c1)=(0,8), (1,7), (2,6).
```

Those three families are now closed:

```
(c0,c1)=(0,8): V479
(c0,c1)=(1,7): V486
(c0,c1)=(2,6): V493
```

Each closure uses direct state-count infeasibility on `(7,12)`, `(8,11)`,
`(9,10)` and audited A/B root-swap equality for `(12,7)`, `(11,8)`,
`(10,9)`.  Therefore the new cap-143 `k=1,q=8` delta frontier isolated in
V384/V385 is exhausted.

Status: VERIFIED FRONTIER CLOSURE.

## V481. `k=1,q=8,c0=1,c1=7,(a,b)=(12,7)` root-swap closure

Update 2026-06-21:

Codex audited the A/B root-swap mate of V480.  The two task manifests

```
search23/k1_q8_state_count_tasks/a7_b12_c01_c17.tasks.tsv
search23/k1_q8_state_count_tasks/a12_b7_c01_c17.tasks.tsv
```

have identical unique `(mask,p,M)` key sets:

```
(7,12) unique keys   4809
(12,7) unique keys   4809
symmetric difference    0
```

The exact state-count model is invariant under interchanging the A and B
roots, as audited in V479.  Therefore V480 also closes the `(12,7)` side.

Status: VERIFIED ROOT-SWAP SIDE CLOSURE.

## V482. `k=1,q=8,c0=1,c1=7,(a,b)=(8,11)` state-count closure

Update 2026-06-21:

Codex closed the second `k=1,q=8,c0=1,c1=7` direct side choice using the
exact state-count quotient with anti-tightness disabled:

```
cnt=(1,7), (a,b)=(8,11), r0=8, t=2
```

The duplicate manifest rows were collapsed to the unique task file

```
search23/k1_q8_a8b11_c1_unique.tasks.tsv
```

and run with `32 jobs x 2 workers`, timeout `300s`, producing

```
search23/k1_q8_a8b11_c1_unique_w2x32_300.tsv
4809 / 4809 INFEASIBLE
```

Audit against the full manifest

```
search23/k1_q8_state_count_tasks/a8_b11_c01_c17.tasks.tsv
```

gives

```
task rows        21609
unique keys       4809
result rows       4809
missing unique       0
extra unique         0
UNKNOWN=0, FEASIBLE=0, other=0
```

The whole `(8,11)` side is therefore closed at the exact state-count level.

Status: VERIFIED SIDE CLOSURE.

## V417. q8 all-D `(8,10)` p24 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=24, M=50..81
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p24_results.tsv
20 / 32 INFEASIBLE, 12 UNKNOWN
```

The 12 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p24_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
8 / 12 INFEASIBLE, 4 UNKNOWN
```

The remaining four rows were rerun in a focused tail

```
search23/k2_idx15_q8D_a8b10_p24_hard2_results.tsv
2 jobs x 32 solver workers, 1200s per row
4 / 4 INFEASIBLE
```

The verified union over the three result files is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=24` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V418. q8 all-D `(8,10)` p25 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=25, M=49..80
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p25_results.tsv
21 / 32 INFEASIBLE, 11 UNKNOWN
```

The 11 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p25_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
8 / 11 INFEASIBLE, 3 UNKNOWN
```

The remaining three rows were rerun in a focused tail

```
search23/k2_idx15_q8D_a8b10_p25_hard2_results.tsv
2 jobs x 32 solver workers, 1200s per row
3 / 3 INFEASIBLE
```

The verified union over the three result files is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=25` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V419. q8 all-D `(8,10)` p26 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=26, M=48..79
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p26_results.tsv
22 / 32 INFEASIBLE, 10 UNKNOWN
```

The 10 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p26_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
8 / 10 INFEASIBLE, 2 UNKNOWN
```

The remaining two rows were rerun in a focused tail

```
search23/k2_idx15_q8D_a8b10_p26_hard2_results.tsv
2 jobs x 32 solver workers, 1200s per row
2 / 2 INFEASIBLE
```

The verified union over the three result files is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=26` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V420. q8 all-D `(8,10)` p27 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=27, M=48..78
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p27_results.tsv
22 / 31 INFEASIBLE, 9 UNKNOWN
```

The 9 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p27_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
8 / 9 INFEASIBLE, 1 UNKNOWN
```

The remaining row was rerun in a focused tail

```
search23/k2_idx15_q8D_a8b10_p27_hard2_results.tsv
1 job x 32 solver workers, 1200s per row
1 / 1 INFEASIBLE
```

The verified union over the three result files is

```
31 / 31 INFEASIBLE
missing rows: 0
```

Thus the whole `p=27` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V421. q8 all-D `(8,10)` p28 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=28, M=48..77
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p28_results.tsv
22 / 30 INFEASIBLE, 8 UNKNOWN
```

The 8 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p28_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
8 / 8 INFEASIBLE
```

The verified union over the two result files is

```
30 / 30 INFEASIBLE
missing rows: 0
```

Thus the whole `p=28` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V422. q8 all-D `(8,10)` p29 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=29, M=48..76
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p29_results.tsv
22 / 29 INFEASIBLE, 7 UNKNOWN
```

The 7 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p29_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
7 / 7 INFEASIBLE
```

The verified union over the two result files is

```
29 / 29 INFEASIBLE
missing rows: 0
```

Thus the whole `p=29` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V423. q8 all-D `(8,10)` p30 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=30, M=48..75
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p30_results.tsv
22 / 28 INFEASIBLE, 6 UNKNOWN
```

The 6 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p30_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
6 / 6 INFEASIBLE
```

The verified union over the two result files is

```
28 / 28 INFEASIBLE
missing rows: 0
```

Thus the whole `p=30` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V424. q8 all-D `(8,10)` p31 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=31, M=48..74
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p31_results.tsv
22 / 27 INFEASIBLE, 5 UNKNOWN
```

The 5 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p31_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
5 / 5 INFEASIBLE
```

The verified union over the two result files is

```
27 / 27 INFEASIBLE
missing rows: 0
```

Thus the whole `p=31` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V425. q8 all-D `(8,10)` p32 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=32, M=48..73
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p32_results.tsv
22 / 26 INFEASIBLE, 4 UNKNOWN
```

The 4 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p32_hard_results.tsv
4 jobs x 16 solver workers, 600s per row
4 / 4 INFEASIBLE
```

The verified union over the two result files is

```
26 / 26 INFEASIBLE
missing rows: 0
```

Thus the whole `p=32` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V426. q8 all-D `(8,10)` p33 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=33, M=48..72
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p33_results.tsv
22 / 25 INFEASIBLE, 3 UNKNOWN
```

The 3 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p33_hard_results.tsv
3 jobs x 16 solver workers, 600s per row
3 / 3 INFEASIBLE
```

The verified union over the two result files is

```
25 / 25 INFEASIBLE
missing rows: 0
```

Thus the whole `p=33` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V427. q8 all-D `(8,10)` p34 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=34, M=48..71
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p34_results.tsv
22 / 24 INFEASIBLE, 2 UNKNOWN
```

The 2 UNKNOWN rows were rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p34_hard_results.tsv
2 jobs x 16 solver workers, 600s per row
2 / 2 INFEASIBLE
```

The verified union over the two result files is

```
24 / 24 INFEASIBLE
missing rows: 0
```

Thus the whole `p=34` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V428. q8 all-D `(8,10)` p35 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=35, M=48..70
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p35_results.tsv
22 / 23 INFEASIBLE, 1 UNKNOWN
```

The remaining UNKNOWN row was rerun in a hard tail

```
search23/k2_idx15_q8D_a8b10_p35_hard_results.tsv
1 job x 32 solver workers, 600s per row
1 / 1 INFEASIBLE
```

The verified union over the two result files is

```
23 / 23 INFEASIBLE
missing rows: 0
```

Thus the whole `p=35` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V429. q8 all-D `(8,10)` p36 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=36, M=48..69
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p36_results.tsv
22 / 22 INFEASIBLE
```

The verified union against the task manifest is

```
22 / 22 INFEASIBLE
missing rows: 0
```

Thus the whole `p=36` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V430. q8 all-D `(8,10)` p37 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=37, M=48..68
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p37_results.tsv
21 / 21 INFEASIBLE
```

The verified union against the task manifest is

```
21 / 21 INFEASIBLE
missing rows: 0
```

Thus the whole `p=37` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V431. q8 all-D `(8,10)` p38 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=38, M=48..67
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p38_results.tsv
20 / 20 INFEASIBLE
```

The verified union against the task manifest is

```
20 / 20 INFEASIBLE
missing rows: 0
```

Thus the whole `p=38` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V432. q8 all-D `(8,10)` p39 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=39, M=48..66
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p39_results.tsv
19 / 19 INFEASIBLE
```

The verified union against the task manifest is

```
19 / 19 INFEASIBLE
missing rows: 0
```

Thus the whole `p=39` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V433. q8 all-D `(8,10)` p40 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=40, M=48..65
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p40_results.tsv
18 / 18 INFEASIBLE
```

The verified union against the task manifest is

```
18 / 18 INFEASIBLE
missing rows: 0
```

Thus the whole `p=40` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V434. q8 all-D `(8,10)` p41 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=41, M=48..64
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p41_results.tsv
17 / 17 INFEASIBLE
```

The verified union against the task manifest is

```
17 / 17 INFEASIBLE
missing rows: 0
```

Thus the whole `p=41` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V435. q8 all-D `(8,10)` p42 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=42, M=48..63
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p42_results.tsv
16 / 16 INFEASIBLE
```

The verified union against the task manifest is

```
16 / 16 INFEASIBLE
missing rows: 0
```

Thus the whole `p=42` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V436. q8 all-D `(8,10)` p43 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=43, M=48..62
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p43_results.tsv
15 / 15 INFEASIBLE
```

The verified union against the task manifest is

```
15 / 15 INFEASIBLE
missing rows: 0
```

Thus the whole `p=43` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V437. q8 all-D `(8,10)` p44 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=44, M=48..61
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p44_results.tsv
14 / 14 INFEASIBLE
```

The verified union against the task manifest is

```
14 / 14 INFEASIBLE
missing rows: 0
```

Thus the whole `p=44` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V438. q8 all-D `(8,10)` p45 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=45, M=48..60
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p45_results.tsv
13 / 13 INFEASIBLE
```

The verified union against the task manifest is

```
13 / 13 INFEASIBLE
missing rows: 0
```

Thus the whole `p=45` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V439. q8 all-D `(8,10)` p46 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=46, M=48..59
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p46_results.tsv
12 / 12 INFEASIBLE
```

The verified union against the task manifest is

```
12 / 12 INFEASIBLE
missing rows: 0
```

Thus the whole `p=46` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V440. q8 all-D `(8,10)` p47 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=47, M=48..58
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p47_results.tsv
11 / 11 INFEASIBLE
```

The verified union against the task manifest is

```
11 / 11 INFEASIBLE
missing rows: 0
```

Thus the whole `p=47` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V441. q8 all-D `(8,10)` p48 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=48, M=48..57
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p48_results.tsv
10 / 10 INFEASIBLE
```

The verified union against the task manifest is

```
10 / 10 INFEASIBLE
missing rows: 0
```

Thus the whole `p=48` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V442. q8 all-D `(8,10)` p49 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=49, M=48..56
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p49_results.tsv
9 / 9 INFEASIBLE
```

The verified union against the task manifest is

```
9 / 9 INFEASIBLE
missing rows: 0
```

Thus the whole `p=49` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V443. q8 all-D `(8,10)` p50 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=50, M=48..55
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p50_results.tsv
8 / 8 INFEASIBLE
```

The verified union against the task manifest is

```
8 / 8 INFEASIBLE
missing rows: 0
```

Thus the whole `p=50` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V444. q8 all-D `(8,10)` p51 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=51, M=48..54
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p51_results.tsv
7 / 7 INFEASIBLE
```

The verified union against the task manifest is

```
7 / 7 INFEASIBLE
missing rows: 0
```

Thus the whole `p=51` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V445. q8 all-D `(8,10)` p52 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=52, M=48..53
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p52_results.tsv
6 / 6 INFEASIBLE
```

The verified union against the task manifest is

```
6 / 6 INFEASIBLE
missing rows: 0
```

Thus the whole `p=52` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V446. q8 all-D `(8,10)` p53 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=53, M=48..52
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p53_results.tsv
5 / 5 INFEASIBLE
```

The verified union against the task manifest is

```
5 / 5 INFEASIBLE
missing rows: 0
```

Thus the whole `p=53` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V447. q8 all-D `(8,10)` p54 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=54, M=48..51
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p54_results.tsv
4 / 4 INFEASIBLE
```

The verified union against the task manifest is

```
4 / 4 INFEASIBLE
missing rows: 0
```

Thus the whole `p=54` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V448. q8 all-D `(8,10)` p55 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=55, M=48..50
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
3 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p55_results.tsv
3 / 3 INFEASIBLE
```

The verified union against the task manifest is

```
3 / 3 INFEASIBLE
missing rows: 0
```

Thus the whole `p=55` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V449. q8 all-D `(8,10)` p56 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(8,10)` band

```
p=56, M=48..49
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
2 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p56_results.tsv
2 / 2 INFEASIBLE
```

The verified union against the task manifest is

```
2 / 2 INFEASIBLE
missing rows: 0
```

Thus the whole `p=56` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` is closed.

Status: VERIFIED BAND CLOSURE.

## V450. q8 all-D `(8,10)` p57 final row and full side closure

Update 2026-06-20:

Codex closed the final q8 all-D `(8,10)` row

```
p=57, M=48
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
1 job x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx15_q8D_a8b10_p57_results.tsv
1 / 1 INFEASIBLE
```

The verified union against the `p=57` task manifest is

```
1 / 1 INFEASIBLE
missing rows: 0
```

Codex then union-audited the entire `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(8,10)` task manifest

```
search23/k2_idx15_q8D_a8b10_state_tasks.tsv
```

against the `p=20..57` result artifacts.  The verified full-side union is

```
720 / 720 INFEASIBLE
missing rows: 0
```

Thus the whole q8 all-D `(8,10)` side is closed.

Status: VERIFIED SIDE CLOSURE.

## V451. q8 all-D `(9,9)` p18 band closure

Update 2026-06-20:

Codex started the final q8 all-D side `(A,B)=(9,9)` and closed the first band

```
p=18, M=67..98
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p18_results.tsv
32 / 32 INFEASIBLE
```

The verified union against the task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=18` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V452. q8 all-D `(9,9)` p19 band closure

Update 2026-06-20:

Codex closed the next q8 all-D `(9,9)` band

```
p=19, M=66..97
```

with anti-tightness disabled and the current 64-worker cap.  The run used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p19_results.tsv
32 / 32 INFEASIBLE
```

The verified union against the task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=19` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V453. q8 all-D `(9,9)` p20 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=20, M=66..97
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p20_results.tsv
16 INFEASIBLE, 16 UNKNOWN
```

The hard tail on `M=70..85` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p20_hard_results.tsv
8 INFEASIBLE, 8 UNKNOWN
```

The focused tail on `M=77..84` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p20_hard2_results.tsv
8 / 8 INFEASIBLE
```

The verified union against the `p=20` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=20` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V454. q8 all-D `(9,9)` p21 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=21, M=66..97
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p21_results.tsv
17 INFEASIBLE, 15 UNKNOWN
```

The hard tail on `M=70..84` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p21_hard_results.tsv
8 INFEASIBLE, 7 UNKNOWN
```

The focused tail on `M=77..82,84` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p21_hard2_results.tsv
7 / 7 INFEASIBLE
```

The verified union against the `p=21` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=21` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V455. q8 all-D `(9,9)` p22 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=22, M=66..97
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p22_results.tsv
18 INFEASIBLE, 14 UNKNOWN
```

The hard tail on `M=70..83` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p22_hard_results.tsv
7 INFEASIBLE, 7 UNKNOWN
```

The focused tail on `M=77..83` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p22_hard2_results.tsv
7 / 7 INFEASIBLE
```

The verified union against the `p=22` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=22` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V456. q8 all-D `(9,9)` p23 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=23, M=51..82
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p23_results.tsv
19 INFEASIBLE, 13 UNKNOWN
```

The hard tail on `M=70..82` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p23_hard_results.tsv
7 INFEASIBLE, 6 UNKNOWN
```

The focused tail on `M=77..82` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p23_hard2_results.tsv
6 / 6 INFEASIBLE
```

The verified union against the `p=23` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=23` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V457. q8 all-D `(9,9)` p24 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=24, M=50..81
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p24_results.tsv
20 INFEASIBLE, 12 UNKNOWN
```

The hard tail on `M=70..81` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p24_hard_results.tsv
7 INFEASIBLE, 5 UNKNOWN
```

The focused tail on `M=77..81` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p24_hard2_results.tsv
5 / 5 INFEASIBLE
```

The verified union against the `p=24` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=24` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V458. q8 all-D `(9,9)` p25 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=25, M=49..80
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p25_results.tsv
21 INFEASIBLE, 11 UNKNOWN
```

The hard tail on `M=70..80` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p25_hard_results.tsv
7 INFEASIBLE, 4 UNKNOWN
```

The focused tail on `M=77..80` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p25_hard2_results.tsv
4 / 4 INFEASIBLE
```

The verified union against the `p=25` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=25` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V459. q8 all-D `(9,9)` p26 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=26, M=48..79
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p26_results.tsv
22 INFEASIBLE, 10 UNKNOWN
```

The hard tail on `M=70..79` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p26_hard_results.tsv
7 INFEASIBLE, 3 UNKNOWN
```

The focused tail on `M=77..79` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p26_hard2_results.tsv
3 / 3 INFEASIBLE
```

The verified union against the `p=26` task manifest is

```
32 / 32 INFEASIBLE
missing rows: 0
```

Thus the whole `p=26` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V460. q8 all-D `(9,9)` p27 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=27, M=48..78
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p27_results.tsv
22 INFEASIBLE, 9 UNKNOWN
```

The hard tail on `M=70..78` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p27_hard_results.tsv
7 INFEASIBLE, 2 UNKNOWN
```

The focused tail on `M=77..78` used

```
2 jobs x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p27_hard2_results.tsv
2 / 2 INFEASIBLE
```

The verified union against the `p=27` task manifest is

```
31 / 31 INFEASIBLE
missing rows: 0
```

Thus the whole `p=27` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V461. q8 all-D `(9,9)` p28 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=28, M=48..77
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p28_results.tsv
22 INFEASIBLE, 8 UNKNOWN
```

The hard tail on `M=70..77` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p28_hard_results.tsv
7 INFEASIBLE, 1 UNKNOWN
```

The focused tail on `M=77` used

```
1 job x 32 solver workers, 1800s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p28_hard2_results.tsv
1 / 1 INFEASIBLE
```

The verified union against the `p=28` task manifest is

```
30 / 30 INFEASIBLE
missing rows: 0
```

Thus the whole `p=28` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V462. q8 all-D `(9,9)` p29 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=29, M=48..76
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p29_results.tsv
22 INFEASIBLE, 7 UNKNOWN
```

The hard tail on `M=70..76` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p29_hard_results.tsv
7 / 7 INFEASIBLE
```

The verified union against the `p=29` task manifest is

```
29 / 29 INFEASIBLE
missing rows: 0
```

Thus the whole `p=29` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V463. q8 all-D `(9,9)` p30 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=30, M=48..75
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p30_results.tsv
22 INFEASIBLE, 6 UNKNOWN
```

The hard tail on `M=70..75` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p30_hard_results.tsv
6 / 6 INFEASIBLE
```

The verified union against the `p=30` task manifest is

```
28 / 28 INFEASIBLE
missing rows: 0
```

Thus the whole `p=30` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V464. q8 all-D `(9,9)` p31 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=31, M=48..74
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p31_results.tsv
22 INFEASIBLE, 5 UNKNOWN
```

The hard tail on `M=70..74` used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p31_hard_results.tsv
5 / 5 INFEASIBLE
```

The verified union against the `p=31` task manifest is

```
27 / 27 INFEASIBLE
missing rows: 0
```

Thus the whole `p=31` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V465. q8 all-D `(9,9)` p32 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=32, M=48..73
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p32_results.tsv
22 INFEASIBLE, 4 UNKNOWN
```

The hard tail on the four UNKNOWN rows used

```
4 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p32_hard_results.tsv
4 / 4 INFEASIBLE
```

The verified union against the `p=32` task manifest is

```
26 / 26 INFEASIBLE
missing rows: 0
```

Thus the whole `p=32` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V466. q8 all-D `(9,9)` p33 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=33, M=48..72
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p33_results.tsv
22 INFEASIBLE, 3 UNKNOWN
```

The hard tail on the three UNKNOWN rows used

```
3 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p33_hard_results.tsv
3 / 3 INFEASIBLE
```

The verified union against the `p=33` task manifest is

```
25 / 25 INFEASIBLE
missing rows: 0
```

Thus the whole `p=33` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V467. q8 all-D `(9,9)` p34 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=34, M=48..71
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p34_results.tsv
22 INFEASIBLE, 2 UNKNOWN
```

The hard tail on the two UNKNOWN rows used

```
2 jobs x 16 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p34_hard_results.tsv
2 / 2 INFEASIBLE
```

The verified union against the `p=34` task manifest is

```
24 / 24 INFEASIBLE
missing rows: 0
```

Thus the whole `p=34` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V468. q8 all-D `(9,9)` p35 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=35, M=48..70
```

with anti-tightness disabled and the current 64-worker cap.  The first pass
used

```
4 jobs x 16 solver workers, 120s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p35_results.tsv
22 INFEASIBLE, 1 UNKNOWN
```

The hard tail on the one UNKNOWN row used

```
1 job x 64 solver workers, 600s per row
```

and produced

```
search23/k2_idx16_q8D_a9b9_p35_hard_results.tsv
1 / 1 INFEASIBLE
```

The verified union against the `p=35` task manifest is

```
23 / 23 INFEASIBLE
missing rows: 0
```

Thus the whole `p=35` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V469. q8 all-D `(9,9)` p36 band closure

Update 2026-06-20:

Codex closed the q8 all-D `(9,9)` band

```
p=36, M=48..69
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx16_q8D_a9b9_p36_results.tsv
22 / 22 INFEASIBLE
```

The verified union against the `p=36` task manifest is

```
22 / 22 INFEASIBLE
missing rows: 0
```

Thus the whole `p=36` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V470. q8 all-D `(9,9)` p37 band closure

Update 2026-06-21:

Codex closed the q8 all-D `(9,9)` band

```
p=37, M=48..68
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx16_q8D_a9b9_p37_results.tsv
21 / 21 INFEASIBLE
```

The verified union against the `p=37` task manifest is

```
21 / 21 INFEASIBLE
missing rows: 0
```

Thus the whole `p=37` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V471. q8 all-D `(9,9)` p38 band closure

Update 2026-06-21:

Codex closed the q8 all-D `(9,9)` band

```
p=38, M=48..67
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx16_q8D_a9b9_p38_results.tsv
20 / 20 INFEASIBLE
```

The verified union against the `p=38` task manifest is

```
20 / 20 INFEASIBLE
missing rows: 0
```

Thus the whole `p=38` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V472. q8 all-D `(9,9)` p39 band closure

Update 2026-06-21:

Codex closed the q8 all-D `(9,9)` band

```
p=39, M=48..66
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx16_q8D_a9b9_p39_results.tsv
19 / 19 INFEASIBLE
```

The verified union against the `p=39` task manifest is

```
19 / 19 INFEASIBLE
missing rows: 0
```

Thus the whole `p=39` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V473. q8 all-D `(9,9)` p40 band closure

Update 2026-06-21:

Codex closed the q8 all-D `(9,9)` band

```
p=40, M=48..65
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx16_q8D_a9b9_p40_results.tsv
18 / 18 INFEASIBLE
```

The verified union against the `p=40` task manifest is

```
18 / 18 INFEASIBLE
missing rows: 0
```

Thus the whole `p=40` band for `K=2,T=2,q=8`, support `{D}`,
side `(A,B)=(9,9)` is closed.

Status: VERIFIED BAND CLOSURE.

## V474. q8 all-D `(9,9)` full side closure

Update 2026-06-21:

Codex closed all remaining rows for the final q8 all-D side

```
K=2, T=2, q=8, support {D}, (A,B)=(9,9)
```

with anti-tightness disabled and the current 64-worker cap.  After the
verified `p=18..40` band closures, the remaining manifest rows were

```
p=41..57
153 task rows
```

Codex ran them in one batch:

```
search23/k2_idx16_q8D_a9b9_remaining_after_p40_results.tsv
153 / 153 INFEASIBLE
```

The full side union audit over all `k2_idx16_q8D_a9b9*_results.tsv`
artifacts and the state-count task manifest is

```
784 / 784 INFEASIBLE
missing rows: 0
```

Thus the entire q8 all-D `(A,B)=(9,9)` side is closed.

Status: VERIFIED SIDE CLOSURE.

## V475. q8 all-D support closure

Update 2026-06-21:

Codex audited the three q8 all-D side manifests:

```
search23/k2_idx14_q8D_a7b11_state_tasks.tsv
656 / 656 INFEASIBLE
missing rows: 0

search23/k2_idx15_q8D_a8b10_state_tasks.tsv
720 / 720 INFEASIBLE
missing rows: 0

search23/k2_idx16_q8D_a9b9_state_tasks.tsv
784 / 784 INFEASIBLE
missing rows: 0
```

Thus all q8 all-D `K=2,T=2` side choices are closed under the exact
state-count quotient with anti-tightness disabled.

Status: VERIFIED SUPPORT CLOSURE.

## V476. q8 all-D four-side support closure

Update 2026-06-21:

Codex reran the two old UNKNOWN rows in the remaining q8 all-D side:

```
search23/k2_idx13_q8D_a6b12_missing2_results.tsv
2 / 2 INFEASIBLE
```

The corrected q8 all-D four-side audit is:

```
search23/k2_idx13_q8D_a6b12_state_tasks.tsv
592 / 592 INFEASIBLE
missing rows: 0

search23/k2_idx14_q8D_a7b11_state_tasks.tsv
656 / 656 INFEASIBLE
missing rows: 0

search23/k2_idx15_q8D_a8b10_state_tasks.tsv
720 / 720 INFEASIBLE
missing rows: 0

search23/k2_idx16_q8D_a9b9_state_tasks.tsv
784 / 784 INFEASIBLE
missing rows: 0
```

Thus all q8 all-D `K=2,T=2` side choices are closed under the exact
state-count quotient with anti-tightness disabled.

Status: VERIFIED SUPPORT CLOSURE.

## V477. `k=1,q=8,c0=0,(a,b)=(8,11)` state-count closure

Update 2026-06-21:

Codex closed the next `k=1,q=8,c0=0` task group using the exact state-count
quotient:

```
search23/k1_q8_state_count_tasks/a8_b11_c00_c18.tasks.tsv
```

The run used

```
4 jobs x 16 solver workers, 300s per row
```

and produced

```
search23/k1_q8_a8b11_c0_w16_300.tsv
420 / 420 INFEASIBLE
UNKNOWN rows: 0
FEASIBLE rows: 0
```

Thus the unique `c0=0,c1=8` R-skeleton orbit for the `(A,B)=(8,11)` side
choice in the cap-143 `k=1,q=8` delta is closed.

Status: VERIFIED SUBFRONTIER CLOSURE.

## V478. `k=1,q=8,c0=0,(a,b)=(9,10)` state-count closure

Update 2026-06-21:

Codex closed the central `k=1,q=8,c0=0` task group using the exact state-count
quotient:

```
search23/k1_q8_state_count_tasks/a9_b10_c00_c18.tasks.tsv
```

The run used

```
4 jobs x 16 solver workers, 300s per row
```

and produced

```
search23/k1_q8_a9b10_c0_w16_300.tsv
420 / 420 INFEASIBLE
UNKNOWN rows: 0
FEASIBLE rows: 0
```

Manifest audit:

```
tasks=420
results=420
missing=0
extra=0
statuses=INFEASIBLE=420
```

Thus the unique `c0=0,c1=8` R-skeleton orbit for the `(A,B)=(9,10)` side
choice in the cap-143 `k=1,q=8` delta is closed.

Status: VERIFIED SUBFRONTIER CLOSURE.

## V479. `k=1,q=8,c0=0,c1=8` six-side closure by A/B root swap

Update 2026-06-21:

Codex audited the remaining `k=1,q=8,c0=0,c1=8` side choices under the
root swap exchanging the two exclusive root-neighbour sets `A` and `B`.

For the three swapped side pairs, the task manifests have identical
`(R-mask,p,M)` sets:

```
(a,b)=(7,12)  <->  (12,7): 420 tasks, symmetric difference 0
(a,b)=(8,11)  <->  (11,8): 420 tasks, symmetric difference 0
(a,b)=(9,10)  <->  (10,9): 420 tasks, symmetric difference 0
```

The exact state-count quotient is invariant under this root swap:

* the `A`-state multiplicities `A_I` and `B`-state multiplicities `B_I`
  are interchanged;
* `NA` and `NB` are interchanged;
* `alpha_r` and `beta_r` are interchanged for every `r in R`;
* the exact `A/B` law, `p=sum_I A_I*d_B(I)`, is preserved because
  disjointness of states is symmetric;
* root-to-`R`, degree, `A/R` versus `B/R`, and `A/A` versus `B/B`
  codegree constraints are paired under the same interchange;
* `R/R` codegree constraints and the fixed `R` skeleton do not mention the
  choice of exclusive side.

Thus an admissible quotient solution for `(b,a)` would root-swap to an
admissible quotient solution for `(a,b)` with the same `(R-mask,p,M)`, and
conversely.  Hence an exact state-count closure for one side closes its
root-swapped side.

Direct certified closures:

```
(a,b)=(7,12): 420 / 420 INFEASIBLE  (prior V387 artifacts)
(a,b)=(8,11): 420 / 420 INFEASIBLE  (V477)
(a,b)=(9,10): 420 / 420 INFEASIBLE  (V478)
```

Root-swap consequences:

```
(a,b)=(12,7): closed by (7,12)
(a,b)=(11,8): closed by (8,11)
(a,b)=(10,9): closed by (9,10)
```

Therefore all six `k=1,q=8,c0=0,c1=8` side choices are closed in the
cap-143 delta.

Status: VERIFIED SYMMETRY CLOSURE.

## V416. q8 all-D `(8,10)` p23 band closure

Update 2026-06-20:

Codex ran the q8 all-D `(8,10)` band

```
p=23, M=51..82
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The first pass produced

```
search23/k2_idx15_q8D_a8b10_p23_results.tsv
19 INFEASIBLE
13 UNKNOWN
0 FEASIBLE
```

Codex then reran the unknown tail

```
M=70..82
```

with

```
4 jobs x 16 solver workers, 600s per row
```

This hard-tail run produced

```
search23/k2_idx15_q8D_a8b10_p23_hard_results.tsv
8 INFEASIBLE
5 UNKNOWN
0 FEASIBLE
```

The remaining unknown rows were exactly

```
M=78,79,80,81,82
```

Codex reran them with a focused configuration

```
2 jobs x 32 solver workers, 1200s per row
```

producing

```
search23/k2_idx15_q8D_a8b10_p23_hard2_results.tsv
5 / 5 INFEASIBLE
```

The trusted union for this band has

```
total rows       32
closed rows      32
missing rows     0
```

Thus the full q8 all-D `(8,10)` `p=23` band is closed.

Status: VERIFIED BAND CLOSURE.

## V415. q8 all-D `(8,10)` p22 band closure

Update 2026-06-20:

Codex ran the q8 all-D `(8,10)` band

```
p=22, M=52..83
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The first pass produced

```
search23/k2_idx15_q8D_a8b10_p22_results.tsv
18 INFEASIBLE
14 UNKNOWN
0 FEASIBLE
```

Codex then reran the unknown tail

```
M=70..83
```

with

```
4 jobs x 16 solver workers, 600s per row
```

This hard-tail run produced

```
search23/k2_idx15_q8D_a8b10_p22_hard_results.tsv
11 INFEASIBLE
3 UNKNOWN
0 FEASIBLE
```

The remaining unknown rows were exactly

```
M=79,80,81
```

Codex reran them with a focused configuration

```
2 jobs x 32 solver workers, 1200s per row
```

producing

```
search23/k2_idx15_q8D_a8b10_p22_hard2_results.tsv
3 / 3 INFEASIBLE
```

The trusted union for this band has

```
total rows       32
closed rows      32
missing rows     0
```

Thus the full q8 all-D `(8,10)` `p=22` band is closed.

Status: VERIFIED BAND CLOSURE.

## V414. q8 all-D `(8,10)` p21 band closure

Update 2026-06-20:

Codex ran the q8 all-D `(8,10)` band

```
p=21, M=53..84
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The first pass produced

```
search23/k2_idx15_q8D_a8b10_p21_results.tsv
18 INFEASIBLE
14 UNKNOWN
0 FEASIBLE
```

Codex then reran the unknown tail

```
M=70..84
```

with

```
4 jobs x 16 solver workers, 600s per row
```

The hard-tail run produced

```
search23/k2_idx15_q8D_a8b10_p21_hard_results.tsv
14 / 14 INFEASIBLE
```

The trusted union for this band has

```
total rows       32
closed rows      32
missing rows     0
```

Thus the full q8 all-D `(8,10)` `p=21` band is closed.

Status: VERIFIED BAND CLOSURE.

## V412. q8 all-D `(7,11)` full side closure

Update 2026-06-20:

Codex first ran the q8 all-D `(7,11)` band

```
p=40, M=48..65
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p40_results.tsv
18 / 18 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

Codex then generated the remaining task file after p40,

```
search23/k2_idx14_q8D_a7b11_remaining_after_p40_tasks.tsv
```

which contained every not-yet-closed row

```
p=41..57
153 rows
```

The remaining-batch run produced

```
search23/k2_idx14_q8D_a7b11_remaining_after_p40_results.tsv
153 / 153 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

The final trusted union for `q=8` all-D `(7,11)` has

```
total rows          656
unique closed rows  656
missing rows        0
superseded non-INF  52
```

The `52` non-INFEASIBLE rows occur only in earlier generic pass files and are
superseded by later hard-tail, p22-tail, and remaining-batch artifacts on the
same `(mask,p,M)` keys.  Thus the full `q=8` all-D `(7,11)` side is closed.

Status: VERIFIED SIDE CLOSURE.

## V413. q8 all-D `(8,10)` p20 band closure

Update 2026-06-20:

Codex started the next q8 all-D side

```
(|A|,|B|)=(8,10)
```

and ran the first band

```
p=20, M=54..85
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The first pass produced

```
search23/k2_idx15_q8D_a8b10_p20_results.tsv
16 INFEASIBLE
16 UNKNOWN
0 FEASIBLE
```

Codex then reran the unknown tail

```
M=70..85
```

with

```
4 jobs x 16 solver workers, 600s per row
```

The hard-tail run produced

```
search23/k2_idx15_q8D_a8b10_p20_hard_results.tsv
16 / 16 INFEASIBLE
```

The trusted union for this band has

```
total rows       32
closed rows      32
missing rows     0
```

Thus the full q8 all-D `(8,10)` `p=20` band is closed.

Status: VERIFIED BAND CLOSURE.

## V411. q8 all-D `(7,11)` p39 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=39, M=48..66
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p39_results.tsv
19 / 19 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=39`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      485
remaining rows   171
first remaining  (p,M)=(40,48)
```

Status: VERIFIED BAND CLOSURE.

## V410. q8 all-D `(7,11)` p38 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=38, M=48..67
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p38_results.tsv
20 / 20 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=38`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      466
remaining rows   190
first remaining  (p,M)=(39,48)
```

Status: VERIFIED BAND CLOSURE.

## V409. q8 all-D `(7,11)` p37 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=37, M=48..68
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p37_results.tsv
21 / 21 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=37`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      446
remaining rows   210
first remaining  (p,M)=(38,48)
```

Status: VERIFIED BAND CLOSURE.

## V408. q8 all-D `(7,11)` p22-tail audit and p36 band closure

Update 2026-06-20:

Codex audited the trusted union after V407 and found that the existing p22
machine artifact only contained the three parity rows

```
M=81..83
```

although the text summary had treated the entire p22 band as closed.  Codex
therefore ran the missing p22 tail

```
p=22, M=70..80
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The tail run produced

```
search23/k2_idx14_q8D_a7b11_p22_tail_results.tsv
11 / 11 INFEASIBLE
```

so the p22 band is now machine-backed by the parity artifact plus the tail
artifact.

Codex then ran the next q8 all-D `(7,11)` band

```
p=36, M=48..69
```

with the same settings.  The run produced

```
search23/k2_idx14_q8D_a7b11_p36_results.tsv
22 / 22 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      425
remaining rows   231
first remaining  (p,M)=(37,48)
```

Status: VERIFIED BAND CLOSURE.

## V405. q8 all-D `(7,11)` p33 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=33, M=48..72
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p33_results.tsv
25 / 25 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=33`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      356
remaining rows   300
first remaining  (p,M)=(34,48)
```

Status: VERIFIED BAND CLOSURE.

## V406. q8 all-D `(7,11)` p34 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=34, M=48..71
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p34_results.tsv
24 / 24 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=34`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      380
remaining rows   276
first remaining  (p,M)=(35,48)
```

Status: VERIFIED BAND CLOSURE.

## V407. q8 all-D `(7,11)` p35 band closure

Update 2026-06-20:

Codex ran the next q8 all-D `(7,11)` band

```
p=35, M=48..70
```

with anti-tightness disabled and the current 64-worker cap:

```
4 jobs x 16 solver workers, 120s per row
```

The run produced

```
search23/k2_idx14_q8D_a7b11_p35_results.tsv
23 / 23 INFEASIBLE
```

with no `UNKNOWN`, `NO_STATUS`, or `FEASIBLE` row.  Thus the whole `p=35`
band is closed.

The trusted union for `q=8` all-D `(7,11)` now has

```
total rows       656
closed rows      403
remaining rows   253
first remaining  (p,M)=(36,48)
```

Status: VERIFIED BAND CLOSURE.

## V497. `K=2,T=2,q=8` support `{E,D}` with two empty labels, first side closure

Update 2026-06-21:

Codex began the next two-empty support family

```
(c0,c1,c2,c3)=(2,0,0,6), support={E,D}, q=8, U=12.
```

Here `R` has two empty-label vertices and six doubletons.  The only allowed
`R`-edges are `E-E` and `E-D`; `D-D` is forbidden.  Local domination forces
each empty-label vertex to have at least two doubleton neighbours.

Codex added and used

```
search23/k2_q8_ed2_skeletons.cpp
```

to enumerate canonical triangle-free locally dominated masks under
`S2 x S6`.  The enumeration produced `36` canonical masks:

```
search23/k2_q8_ed2_skeletons.tsv
```

For each mask, the state-count grid used

```
root_edges = 22,
U = 12,
M_floor = sum_r max(0, 8 - |L(r)| - d_R(r)),
e_R = e_R(mask),
112 <= root_edges + U + e_R + p + M <= 143.
```

Anti-tightness was disabled and no terminal-touch degree equalities were
used.

The first side choice is

```
idx=25, (|A|,|B|)=(6,12).
```

Artifacts:

```
search23/k2_idx25_q8ED2_a6b12_state_tasks.tsv
search23/k2_idx25_q8ED2_a6b12_state_results_w16x4_60.tsv
```

Audit:

```
task=29536
result=29536
missing=0
extra=0
statuses=INFEASIBLE=29536
```

Thus the `idx25` side of the two-empty `{E,D}` support is closed.  The task
grids for `idx26`, `idx27`, and `idx28` have also been generated, but are not
claimed closed here.

Status: VERIFIED SIDE CLOSURE.

## V498. `K=2,T=2,q=8` support `{E,D}` with two empty labels, second side closure

Update 2026-06-21:

Codex ran the next side choice for the two-empty support family

```
(c0,c1,c2,c3)=(2,0,0,6), support={E,D}, q=8, U=12,
idx=26, (|A|,|B|)=(7,11).
```

The run used the same `36` canonical `S2 x S6` masks from V497, with
anti-tightness disabled and no terminal-touch degree equalities.

Artifacts:

```
search23/k2_idx26_q8ED2_a7b11_state_tasks.tsv
search23/k2_idx26_q8ED2_a7b11_state_results_w16x4_60.tsv
```

Audit:

```
task=31840
result=31840
missing=0
extra=0
statuses=INFEASIBLE=31840
```

Thus the `idx26` side of the two-empty `{E,D}` support is closed.

Status: VERIFIED SIDE CLOSURE.

## V499. `K=2,T=2,q=8` support `{E,D}` with two empty labels, third side closure

Update 2026-06-21:

Codex ran the next side choice for the two-empty support family

```
(c0,c1,c2,c3)=(2,0,0,6), support={E,D}, q=8, U=12,
idx=27, (|A|,|B|)=(8,10).
```

The run used the same `36` canonical `S2 x S6` masks from V497, with
anti-tightness disabled and no terminal-touch degree equalities.

Artifacts:

```
search23/k2_idx27_q8ED2_a8b10_state_tasks.tsv
search23/k2_idx27_q8ED2_a8b10_state_results_w16x4_60.tsv
```

Audit:

```
task=34144
result=34144
missing=0
extra=0
statuses=INFEASIBLE=34144
```

Thus the `idx27` side of the two-empty `{E,D}` support is closed.

Status: VERIFIED SIDE CLOSURE.

## V500. `K=2,T=2,q=8` support `{E,D}` with two empty labels, full side closure

Update 2026-06-21:

Codex ran the final side choice for the two-empty support family

```
(c0,c1,c2,c3)=(2,0,0,6), support={E,D}, q=8, U=12,
idx=28, (|A|,|B|)=(9,9).
```

The run used the same `36` canonical `S2 x S6` masks from V497, with
anti-tightness disabled and no terminal-touch degree equalities.

Artifacts:

```
search23/k2_idx28_q8ED2_a9b9_state_tasks.tsv
search23/k2_idx28_q8ED2_a9b9_state_results_w16x4_60.tsv
```

Audit:

```
task=36448
result=36448
missing=0
extra=0
statuses=INFEASIBLE=36448
```

Combining V497, V498, V499, and this run gives the full side table:

```
idx25 (|A|,|B|)=(6,12): 29536 / 29536 INFEASIBLE
idx26 (|A|,|B|)=(7,11): 31840 / 31840 INFEASIBLE
idx27 (|A|,|B|)=(8,10): 34144 / 34144 INFEASIBLE
idx28 (|A|,|B|)=(9,9):  36448 / 36448 INFEASIBLE
total:                 131968 / 131968 INFEASIBLE
```

All four sides have `missing=0`, `extra=0`, and no `UNKNOWN` or `FEASIBLE`
row.  Therefore the two-empty `{E,D}` support family

```
(c0,c1,c2,c3)=(2,0,0,6)
```

is closed.

Status: VERIFIED FAMILY CLOSURE.

## V507. `K=2,T=2,q=9` support `{E,D}`, one-empty star-family closure

Update 2026-06-21:

The next `q=9` four-label manifest block is

```
(c0,c1,c2,c3)=(1,0,0,8), support={E,D}.
```

There is one empty-label vertex and eight doubleton vertices.  Local
domination forces the empty vertex to have at least two `D` neighbours.
Since `D-D` edges are illegal and the only legal `R` edges are `E-D`, the
canonical skeletons are the star masks with

```
k=2,3,4,5,6,7,8
mask=(1<<k)-1
```

where `k=e_R`.  Codex generated state-count task grids for the three side
choices:

```
search23/k2_idx41_q9ED_a6b11_state_tasks.tsv  421 tasks
search23/k2_idx42_q9ED_a7b10_state_tasks.tsv  421 tasks
search23/k2_idx43_q9ED_a8b9_state_tasks.tsv   421 tasks
```

The grids used `U=16`, `root_edges=21`, the exact per-`k` degree floor, the
finite edge window, and the K2 unpaired empty-cut filters.

Artifacts:

```
search23/k2_idx41_q9ED_a6b11_state_results_w16x4_60.tsv
search23/k2_idx42_q9ED_a7b10_state_results_w16x4_60.tsv
search23/k2_idx43_q9ED_a8b9_state_results_w16x4_60.tsv
```

Audit:

```
idx41: 421 / 421 INFEASIBLE
idx42: 421 / 421 INFEASIBLE
idx43: 421 / 421 INFEASIBLE
total: 1263 / 1263 INFEASIBLE
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx41-43.

Status: VERIFIED FAMILY CLOSURE.

## V508. K2/T2 q=9 four-label support `{E,S1,S2,D}`, profile `(1,2,2,4)`, idx44-46 closed

Update 2026-06-21:

The next `q=9` four-label manifest block is

```
(c0,c1,c2,c3)=(1,2,2,4), support={E,S1,S2,D}.
```

There is one empty-label vertex, two `S1` vertices, two `S2` vertices,
and four doubleton vertices.  Local domination forces
`R[S1,S2]=K_{2,2}`.  Since an empty vertex adjacent to both an `S1` and
an `S2` vertex would create an `R`-triangle, the empty vertex may touch at
most one singleton side.  Up to the `S1 x S2 x D` symmetries, the
canonical empty-neighbour patterns are the 15 triples

```
(a,b,d) with a in 0..2, b in 0..2, d in 2..4,
not both a,b positive,
```

where `a=|E-S1|`, `b=|E-S2|`, and `d=|E-D|`.

Codex generated state-count task grids for the three side choices:

```
search23/k2_idx44_q9ES1S2D_a6b11_state_tasks.tsv  2947 tasks
search23/k2_idx45_q9ES1S2D_a7b10_state_tasks.tsv  2947 tasks
search23/k2_idx46_q9ES1S2D_a8b9_state_tasks.tsv   2947 tasks
```

The grids used `U=12`, `root_edges=21`, the exact per-mask `e_R` and
degree floor, the finite edge window, K2 unpaired cuts, exact `p`, exact
`M`, typewise state-count constraints, and the K2 anti-tightness disabled.

Artifacts:

```
search23/k2_idx44_q9ES1S2D_a6b11_state_results_w16x4_60.tsv
search23/k2_idx45_q9ES1S2D_a7b10_state_results_w16x4_60.tsv
search23/k2_idx46_q9ES1S2D_a8b9_state_results_w16x4_60.tsv
```

Audit:

```
idx44: 2947 / 2947 INFEASIBLE
idx45: 2947 / 2947 INFEASIBLE
idx46: 2947 / 2947 INFEASIBLE
total: 8841 / 8841 INFEASIBLE
```

There is no `FEASIBLE`, `OPTIMAL`, `UNKNOWN`, or missing row for idx44-46.

Status: VERIFIED FAMILY CLOSURE.
## V516. Full K2/T2 q=9 four-label frontier closed

Update 2026-06-21:

The manifest

```
search23/k2_four_label_profile_instances.tsv
```

has exactly idx29-52 for `K=2,T=2,q=9`.  The closures are:

```
idx29-31  (0,0,0,9)  all-D scalar closure             V502
idx32-34  (0,2,2,5)  S1+S2+D fixed K2,2 core          V503
idx35-37  (0,2,3,4)  S1+S2+D fixed K2,3 core          V504
idx38-40  (0,3,3,3)  S1+S2+D matching-complement core V505/V506
idx41-43  (1,0,0,8)  E+D one-empty star family        V507
idx44-46  (1,2,2,4)  E+S1+S2+D family                 V508
idx47-49  (2,0,0,7)  E+D two-empty family             V511
idx50-52  (3,0,0,6)  E+D three-empty family           V514
```

Therefore every `K=2,T=2,q=9` four-label profile-side instance in the
manifest is closed.  No q9 manifest row remains open.

Status: VERIFIED Q CLOSURE.

## V517. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,2,6)`, idx56 closed

Update 2026-06-21:

The next `q=10` support after the all-doubleton scalar closure is

```
(c0,c1,c2,c3)=(0,2,2,6), support={S1,S2,D}.
```

For this profile, local domination fixes the `R`-skeleton:

```
R[S1,S2]=K_{2,2}, D isolated, mask=0xf, e_R=4, U=16.
```

For side `(A,B)=(6,10)`, idx56, the fixed-R state-count grid has 45
`(p,M)` rows:

```
search23/k2_idx56_q10S1S2D_a6b10_state_tasks.tsv
```

A short count-quotient pass closed 30 rows.  The side-sum scalar prefilter

```
alpha(R) >= max(37-2-e_R, 7|A|-p)
beta(R)  >= max(37-2-e_R, 7|B|-p)
```

closed 3 more rows.  The remaining 12 extremal rows were closed by the
labelled exact A/B verifier with sorted A/B state rows:

```
search23/verify_k2_q10_0226_labelled.py
search23/k2_idx56_q10S1S2D_a6b10_labelled_remaining12_results.tsv
```

Audit:

```
idx56: 45 / 45 INFEASIBLE
missing: 0
```

Status: VERIFIED ROW CLOSURE.

## V519. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,2,6)`, idx58 closed

Update 2026-06-21:

For side `(A,B)=(8,8)`, idx58, the fixed-R state-count grid has 45
`(p,M)` rows:

```
search23/k2_idx58_q10S1S2D_a8b8_state_tasks.tsv
```

The first labelled passes closed 35 rows:

```
search23/k2_idx58_q10S1S2D_a8b8_labelled45_w8x8_180.tsv
search23/k2_idx58_q10S1S2D_a8b8_labelled_splitC_results.tsv
```

A safe state bound was then added to the labelled verifier:

```
1 <= |state cap D| <= 5
```

The upper bound is forced because every opposite state must contain a `D`
vertex, so a state containing all six `D` vertices has opposite-root degree
zero.

The remaining 10 `(p,M)` rows were closed by symmetric `MA/MB` branching and
64-worker deep reruns:

```
search23/k2_idx58_q10S1S2D_hard10_MAbranches_sym_Dbounds_w8x8_180.tsv
search23/k2_idx58_q10S1S2D_p33m67_MA33MB34_deep_w64_600.tsv
search23/k2_idx58_q10S1S2D_deep18_w64_600.tsv
```

Audit:

```
idx58: 45 / 45 INFEASIBLE
missing: 0
```

Status: VERIFIED ROW CLOSURE.

## V520. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,2,6)` closed

Update 2026-06-21:

The profile `(c0,c1,c2,c3)=(0,2,2,6)` has exactly three side instances in
`search23/k2_four_label_profile_instances.tsv`:

```
idx56  (A,B)=(6,10)  closed by V517
idx57  (A,B)=(7,9)   closed by V518
idx58  (A,B)=(8,8)   closed by V519
```

Therefore the full q10 support `{S1,S2,D}` profile `(0,2,2,6)` is closed.

Status: VERIFIED PROFILE CLOSURE.

## V535. K2/T2 q=10 support `{E,D}`, profile `(3,0,0,7)`, idx93 closed

Update 2026-06-22:

The next q10 `{E,D}` side instance is

```
(c0,c1,c2,c3)=(3,0,0,7), support={E,D}, idx93, (A,B)=(7,9).
```

It uses the same compact skeleton file and 186349-task state-count grid:

```
search23/k2_q10_ED307_skeletons.tsv
search23/k2_idx93_q10ED3_a7b9_state_tasks.tsv
```

The side instance is closed by a state-count batch with K2 parameters
`--k 2 --cnt 3,0,0,7 --na 7 --nb 9 --r0 8 --t 2`,
projection cuts `0;3`, defect-block label `0`, and anti-tightness disabled:

```
search23/k2_idx93_q10ED3_a7b9_state_results_proj03_db0_w60x1_180.tsv
```

Audit:

```
idx93: 186349 / 186349 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED SIDE CLOSURE.

## V534. K2/T2 q=10 support `{E,D}`, profile `(3,0,0,7)`, idx92 closed

Update 2026-06-22:

The next q10 `{E,D}` side instance is

```
(c0,c1,c2,c3)=(3,0,0,7), support={E,D}, idx92, (A,B)=(6,10).
```

The compact `{E,D}` skeleton generator gives 664 canonical masks:

```
search23/k2_q10_ED307_skeletons.tsv
```

The idx92 state-count p/M task grid has 186349 rows:

```
search23/k2_idx92_q10ED3_a6b10_state_tasks.tsv
```

It was closed by two state-count batches with K2 parameters
`--k 2 --cnt 3,0,0,7 --na 6 --nb 10 --r0 8 --t 2`,
projection cuts `0;3`, defect-block label `0`, and anti-tightness disabled:

```
search23/k2_idx92_q10ED3_a6b10_state_results_proj03_db0_w64x1_180_bg.tsv
search23/k2_idx92_q10ED3_a6b10_remaining_after_bg36706_results_w60x1_180.tsv
```

Audit:

```
first batch:     36706 / 36706 INFEASIBLE
remaining batch: 149643 / 149643 INFEASIBLE
total:           186349 / 186349 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED SIDE CLOSURE.

## V533. K2/T2 q=10 support `{E,S1,S2,D}`, profile `(2,2,2,4)` closed

Update 2026-06-22:

The next q10 support profile is

```
(c0,c1,c2,c3)=(2,2,2,4), support={E,S1,S2,D}.
```

The generic `{E,S1,S2,D}` skeleton generator was generalized to accept an
explicit empty-label count `c0`.  Regression on `(1,3,3,3)` reproduced the
49 canonical masks from V532, and the new profile gives 123 canonical
R-skeleton masks:

```
search23/k2_q10_ES1S2D2224_skeletons.tsv
```

The three side instances are closed by state-count p/M grids with K2
parameters `--k 2 --cnt 2,2,2,4 --r0 8 --t 2`, projection cuts `0;3`,
defect-block label `0`, and anti-tightness disabled:

```
idx89  (A,B)=(6,10)  search23/k2_idx89_q10ES1S2D2224_a6b10_state_results_proj03_db0_w16x4_180.tsv  43276/43276 INFEASIBLE
idx90  (A,B)=(7,9)   search23/k2_idx90_q10ES1S2D2224_a7b9_state_results_proj03_db0_w16x4_180.tsv   43276/43276 INFEASIBLE
idx91  (A,B)=(8,8)   search23/k2_idx91_q10ES1S2D2224_a8b8_state_results_proj03_db0_w16x4_180.tsv   43276/43276 INFEASIBLE
```

Audit:

```
idx89: 43276 / 43276 INFEASIBLE
idx90: 43276 / 43276 INFEASIBLE
idx91: 43276 / 43276 INFEASIBLE
total: 129828 / 129828 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V532. K2/T2 q=10 support `{E,S1,S2,D}`, profile `(1,3,3,3)` closed

Update 2026-06-22:

The next q10 support profile is

```
(c0,c1,c2,c3)=(1,3,3,3), support={E,S1,S2,D}.
```

The generic `{E,S1,S2,D}` skeleton generator gives 49 canonical R-skeleton
masks:

```
search23/k2_q10_ES1S2D1333_skeletons.tsv
```

The three side instances are closed by state-count p/M grids with K2
parameters `--k 2 --cnt 1,3,3,3 --r0 8 --t 2`, projection cuts `0;3`,
defect-block label `0`, and anti-tightness disabled:

```
idx83  (A,B)=(6,10)  search23/k2_idx83_q10ES1S2D1333_a6b10_state_results_proj03_db0_w16x4_180.tsv  15449/15449 INFEASIBLE
idx84  (A,B)=(7,9)   search23/k2_idx84_q10ES1S2D1333_a7b9_state_results_proj03_db0_w16x4_180.tsv   15449/15449 INFEASIBLE
idx85  (A,B)=(8,8)   search23/k2_idx85_q10ES1S2D1333_a8b8_state_results_proj03_db0_w16x4_180.tsv   15449/15449 INFEASIBLE
```

Audit:

```
idx83: 15449 / 15449 INFEASIBLE
idx84: 15449 / 15449 INFEASIBLE
idx85: 15449 / 15449 INFEASIBLE
total: 46347 / 46347 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V531. K2/T2 q=10 support `{E,S1,S2,D}`, profile `(1,2,3,4)` closed

Update 2026-06-22:

The next q10 support profile is

```
(c0,c1,c2,c3)=(1,2,3,4), support={E,S1,S2,D}.
```

A generic q10 `{E,S1,S2,D}` skeleton generator gives 18 canonical skeleton
masks for this asymmetric profile:

```
search23/k2_q10_ES1S2D1234_skeletons.tsv
```

The three side instances are closed by state-count p/M grids with K2
parameters `--k 2 --cnt 1,2,3,4 --r0 8 --t 2`, projection cuts `0;3`,
defect-block label `0`, and anti-tightness disabled:

```
idx80  (A,B)=(6,10)  search23/k2_idx80_q10ES1S2D1234_a6b10_state_results_proj03_db0_w16x4_180.tsv  5253/5253 INFEASIBLE
idx81  (A,B)=(7,9)   search23/k2_idx81_q10ES1S2D1234_a7b9_state_results_proj03_db0_w16x4_180.tsv   5253/5253 INFEASIBLE
idx82  (A,B)=(8,8)   search23/k2_idx82_q10ES1S2D1234_a8b8_state_results_proj03_db0_w16x4_180.tsv    5253/5253 INFEASIBLE
```

Audit:

```
idx80: 5253 / 5253 INFEASIBLE
idx81: 5253 / 5253 INFEASIBLE
idx82: 5253 / 5253 INFEASIBLE
total: 15759 / 15759 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V530. K2/T2 q=10 support `{E,S1,S2,D}`, profile `(1,2,2,5)` closed

Update 2026-06-22:

The next q10 support profile is

```
(c0,c1,c2,c3)=(1,2,2,5), support={E,S1,S2,D}.
```

Local domination fixes the singleton core `R[S1,S2]=K2,2`.  The unique
empty-label vertex may touch no singleton shore or one singleton shore,
with one or two vertices on that shore, and it has two to five D-neighbours.
Up to the D-action and colour-swap symmetry this gives twelve canonical
skeleton masks:

```
search23/k2_q10_ES1S2D1225_skeletons.tsv
```

The three side instances are closed by state-count p/M grids with K2
parameters `--k 2 --cnt 1,2,2,5 --r0 8 --t 2`, anti-tightness disabled,
projection cuts `0;3`, and defect-block label `0`:

```
idx77  (A,B)=(6,10)  search23/k2_idx77_q10ES1S2D1225_a6b10_state_results_proj03_db0_w16x4_180.tsv   2466/2466 INFEASIBLE
idx78  (A,B)=(7,9)   search23/k2_idx78_q10ES1S2D1225_a7b9_state_results_proj03_db0_w16x4_180.tsv    2466/2466 INFEASIBLE
idx79  (A,B)=(8,8)   search23/k2_idx79_q10ES1S2D1225_a8b8_state_results_proj03_db0_w16x4_180.tsv    2466/2466 INFEASIBLE
```

Audit:

```
idx77: 2466 / 2466 INFEASIBLE
idx78: 2466 / 2466 INFEASIBLE
idx79: 2466 / 2466 INFEASIBLE
total: 7398 / 7398 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V527. K2/T2 q=10 support `{E,D}`, profile `(2,0,0,8)`, idx86 closed

Update 2026-06-22:

The next q10 `{E,D}` profile side instance is

```
(c0,c1,c2,c3)=(2,0,0,8), support={E,D}, idx86, (A,B)=(6,10).
```

The canonical R-skeleton manifest has 80 masks:

```
search23/k2_q10_ED208_skeletons.tsv
```

The full state-count grid with K2 parameters
`--k 2 --cnt 2,0,0,8 --na 6 --nb 10 --r0 8 --t 2
--projection-cuts 0;3 --disable-anti-tightness` has 13,805 `(mask,p,M)`
tasks:

```
search23/k2_idx86_q10ED2_a6b10_state_tasks.tsv
```

The first full pass used `jobs=16`, `workers_per_job=4`, timeout `180`,
and closed all but eight tasks:

```
search23/k2_idx86_q10ED2_a6b10_state_results_proj03_w16x4_180.tsv
13797 / 13805 INFEASIBLE
8 / 13805 UNKNOWN
0 FEASIBLE
```

The eight UNKNOWN rows were extracted to

```
search23/k2_idx86_q10ED2_a6b10_proj03_unknown8_tasks.tsv
```

and rerun with `jobs=4`, `workers_per_job=16`, timeout `900`,
same K2/profile/projection parameters:

```
search23/k2_idx86_q10ED2_a6b10_proj03_unknown8_results_w4x16_900.tsv
7 / 8 INFEASIBLE
1 / 8 UNKNOWN
```

The last UNKNOWN row was

```
mask=0x18180, p=33, M=70.
```

For this row the exact-two-root side bounds give

```
e_R=4,
alpha(R) >= max(37-2-e_R, 7|A|-p) = 31,
beta(R)  >= max(37-2-e_R, 7|B|-p) = 37,
M=alpha(R)+beta(R)=70,
```

so the only possible A-side totals are

```
MA=31,32,33.
```

All three MA branches are infeasible with `workers_per_job=21`, timeout
`900`, same K2/profile/projection parameters:

```
search23/k2_idx86_q10ED2_0x18180_p33_M70_MAbranches_w3x21_900.tsv
MA=31 MB=39 INFEASIBLE
MA=32 MB=38 INFEASIBLE
MA=33 MB=37 INFEASIBLE
```

Audit:

```
full grid:     13797 INFEASIBLE + 8 UNKNOWN + 0 FEASIBLE
targeted rerun: 7 INFEASIBLE + 1 UNKNOWN + 0 FEASIBLE
MA branch:       3 INFEASIBLE covering MA=31,32,33
covered: True
```

Therefore all `13,805` original idx86 task keys are covered by exact
infeasibility certificates or the exhaustive MA partition of the sole
targeted residual row.

Status: VERIFIED SIDE-INSTANCE CLOSURE.

## V529. K2/T2 q=10 support `{E,D}`, profile `(2,0,0,8)`, idx88 closed

Update 2026-06-22:

The final side instance of the q10 `{E,D}` profile

```
(c0,c1,c2,c3)=(2,0,0,8), support={E,D}
```

is

```
idx88, (A,B)=(8,8).
```

It uses the same 80-mask canonical R-skeleton manifest as V527 and V528:

```
search23/k2_q10_ED208_skeletons.tsv
```

The full state-count grid with K2 parameters
`--k 2 --cnt 2,0,0,8 --na 8 --nb 8 --r0 8 --t 2
--projection-cuts 0;3 --defect-block-labels 0 --disable-anti-tightness`
has 13,805 `(mask,p,M)` tasks:

```
search23/k2_idx88_q10ED2_a8b8_state_tasks.tsv
```

The first 100-task smoke test closed all sampled rows:

```
search23/k2_idx88_q10ED2_a8b8_first100_db0_results_w16x4_60.tsv
100 / 100 INFEASIBLE
0 UNKNOWN
0 FEASIBLE
```

The full run used `jobs=16`, `workers_per_job=4`, timeout `180`, quotient
rounds `4`, quotient separator timeout `30`, and the same K2/profile/projection
and defect-block parameters:

```
search23/k2_idx88_q10ED2_a8b8_state_results_proj03_db0_w16x4_180.tsv
13805 / 13805 INFEASIBLE
0 UNKNOWN
0 FEASIBLE
```

Audit:

```
result rows: 13805
INFEASIBLE: 13805
UNKNOWN: 0
FEASIBLE: 0
batch final stdout: tasks=13805 jobs=16 workers_per_job=4 infeasible=13805 feasible=0 unknown=0 other=0
stderr audit: no Traceback/Error/Exception/failed/FAIL match
```

Therefore idx88 is closed. Together with V527 and V528, all three side
instances of the q10 `{E,D}` profile `(2,0,0,8)` are closed:

```
idx86 (A,B)=(6,10)  13805 / 13805 covered
idx87 (A,B)=(7,9)   13805 / 13805 covered
idx88 (A,B)=(8,8)   13805 / 13805 INFEASIBLE
```

Status: VERIFIED PROFILE CLOSURE.

## V528. K2/T2 q=10 support `{E,D}`, profile `(2,0,0,8)`, idx87 closed

Update 2026-06-22:

The next q10 `{E,D}` profile side instance is

```
(c0,c1,c2,c3)=(2,0,0,8), support={E,D}, idx87, (A,B)=(7,9).
```

It uses the same 80-mask canonical R-skeleton manifest as V527:

```
search23/k2_q10_ED208_skeletons.tsv
```

The full state-count grid with K2 parameters
`--k 2 --cnt 2,0,0,8 --na 7 --nb 9 --r0 8 --t 2
--projection-cuts 0;3 --disable-anti-tightness` has 13,805 `(mask,p,M)`
tasks:

```
search23/k2_idx87_q10ED2_a7b9_state_tasks.tsv
```

The first full pass used `jobs=16`, `workers_per_job=4`, timeout `180`,
and closed all but 17 tasks:

```
search23/k2_idx87_q10ED2_a7b9_state_results_proj03_w16x4_180.tsv
13788 / 13805 INFEASIBLE
17 / 13805 UNKNOWN
0 FEASIBLE
```

The 17 UNKNOWN rows were extracted to

```
search23/k2_idx87_q10ED2_a7b9_proj03_unknown17_tasks.tsv
```

and rerun with `jobs=4`, `workers_per_job=16`, timeout `900`,
same K2/profile/projection parameters:

```
search23/k2_idx87_q10ED2_a7b9_proj03_unknown17_results_w4x16_900.tsv
11 / 17 INFEASIBLE
6 / 17 UNKNOWN
0 FEASIBLE
```

The six remaining `(mask,p,M)` cells were split by exact side totals
`MA=alpha(R)`, `MB=beta(R)`, producing 55 MA/MB branches:

```
search23/k2_idx87_q10ED2_a7b9_remaining6_MA55_tasks.tsv
search23/k2_idx87_q10ED2_a7b9_remaining6_MA55_results_w4x16_900.tsv
36 / 55 INFEASIBLE
19 / 55 UNKNOWN
0 FEASIBLE
```

The 19 remaining MA/MB branches were extracted to

```
search23/k2_idx87_q10ED2_a7b9_MA55_unknown19.tsv
```

and closed by adding the exact projected defect-block layer on the empty-label
block:

```
--defect-block-labels 0
```

with `jobs=4`, `workers_per_job=16`, timeout `600`, same K2/profile/projection
parameters:

```
search23/k2_idx87_q10ED2_a7b9_unknown19_db0_results_w4x16_600.tsv
19 / 19 INFEASIBLE
0 UNKNOWN
0 FEASIBLE
```

Audit:

```
full grid:       13788 INFEASIBLE + 17 UNKNOWN + 0 FEASIBLE
targeted rerun:     11 INFEASIBLE +  6 UNKNOWN + 0 FEASIBLE
MA/MB branch:       36 INFEASIBLE + 19 UNKNOWN + 0 FEASIBLE
defect-block:       19 INFEASIBLE +  0 UNKNOWN + 0 FEASIBLE
covered: True
```

Therefore all `13,805` original idx87 task keys are covered by exact
infeasibility certificates or the exhaustive MA/MB partition plus the
defect-block closure of the remaining partition leaves.

Status: VERIFIED SIDE-INSTANCE CLOSURE.

## V523. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,3,3,4)` closed

Update 2026-06-21:

The next q10 support profile is

```
(c0,c1,c2,c3)=(0,3,3,4), support={S1,S2,D}.
```

Local domination forces the complement of `R[S1,S2]` to be a matching of
size `0..3`.  The labelled verifier therefore checks four canonical masks:

```
miss=0: edge_mask=0x1ff
miss=1: edge_mask=0x1fe
miss=2: edge_mask=0x1ee
miss=3: edge_mask=0x0ee
```

No D-state bound is used here, because D-free A/B states supported on a
missing singleton pair can be legal.

The three side instances are closed by labelled p/M grids:

```
idx65  (A,B)=(6,10)  search23/k2_idx65_q10S1S2D334_a6b10_labelled_w8x8_180.tsv   260/260 INFEASIBLE
idx66  (A,B)=(7,9)   search23/k2_idx66_q10S1S2D334_a7b9_labelled_w8x8_180.tsv    260/260 INFEASIBLE
```

For idx67 `(A,B)=(8,8)`, the first labelled p/M pass closed `252/260`.
The remaining 8 p/M rows all had `miss=3`; splitting them by exact
`MA=sum alpha` and `MB=sum beta` gave 105 branches:

```
search23/k2_idx67_q10S1S2D334_a8b8_unknown8_MAbranches_w8x8_180.tsv
```

That branch pass closed `72/105`.  The remaining 33 MA/MB branches are closed
by a 100-worker deep rerun:

```
search23/k2_idx67_q10S1S2D334_a8b8_unknown33_MAbranches_w4x25_600.tsv  33/33 INFEASIBLE
```

Thus idx67 is closed by the MA/MB partition of its 8 initial p/M frontier rows.

Audit:

```
idx65: 260 / 260 INFEASIBLE
idx66: 260 / 260 INFEASIBLE
idx67: 260 / 260 covered by INFEASIBLE partitions
total: 780 / 780 covered
missing: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V521. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,3,5)` closed

Update 2026-06-21:

The next q10 support profile is

```
(c0,c1,c2,c3)=(0,2,3,5), support={S1,S2,D}.
```

Local domination fixes the R-skeleton:

```
R[S1,S2]=K_{2,3}, D isolated, mask=0x3f, e_R=6, U=15.
```

A parameterized labelled exact A/B verifier was added:

```
search23/verify_k2_s1s2d_labelled.py
search23/run_k2_s1s2d_labelled_tasks.py
```

It uses the exact A/B state law, all A/A, B/B, A/R, B/R, R/R codegrees,
root-opposite degree constraints, full R-mask Psi cuts, unpaired exact-two-root
cuts, split-C cuts, and the safe D-state bounds `1 <= |state cap D| <= c3-1`.

The three side instances are closed by labelled p/M grids:

```
idx59  (A,B)=(6,10)  search23/k2_idx59_q10S1S2D235_a6b10_labelled_w8x8_180.tsv   50/50 INFEASIBLE
idx60  (A,B)=(7,9)   search23/k2_idx60_q10S1S2D235_a7b9_labelled_w8x8_180.tsv    99/99 INFEASIBLE
idx61  (A,B)=(8,8)   search23/k2_idx61_q10S1S2D235_a8b8_labelled_w8x8_180.tsv   105/105 INFEASIBLE
```

Audit:

```
total: 254 / 254 INFEASIBLE
missing: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V522. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,2,4,4)` closed

Update 2026-06-21:

The next q10 support profile is

```
(c0,c1,c2,c3)=(0,2,4,4), support={S1,S2,D}.
```

Local domination fixes the R-skeleton:

```
R[S1,S2]=K_{2,4}, D isolated, e_R=8, U=14.
```

The parameterized labelled exact A/B verifier closes all three side instances:

```
idx62  (A,B)=(6,10)  search23/k2_idx62_q10S1S2D244_a6b10_labelled_w8x8_180.tsv   65/65 INFEASIBLE
idx63  (A,B)=(7,9)   search23/k2_idx63_q10S1S2D244_a7b9_labelled_w8x8_180.tsv   114/114 INFEASIBLE
idx64  (A,B)=(8,8)   search23/k2_idx64_q10S1S2D244_a8b8_labelled_w8x8_180.tsv   120/120 INFEASIBLE
```

Audit:

```
total: 299 / 299 INFEASIBLE
missing: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V524. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,3,4,3)` closed

Update 2026-06-21:

The next q10 support profile is

```
(c0,c1,c2,c3)=(0,3,4,3), support={S1,S2,D}.
```

The singleton core `R[S1,S2]` is a `3 x 4` bipartite graph with every
singleton vertex having opposite degree at least two.  Up to the
`S3 x S4` side action, this gives eight canonical core masks:

```
edge_mask=0x3cf  e_R=8
edge_mask=0x3de  e_R=8
edge_mask=0x3df  e_R=9
edge_mask=0x7bd  e_R=9
edge_mask=0x3ff  e_R=10
edge_mask=0x7bf  e_R=10
edge_mask=0x7ff  e_R=11
edge_mask=0xfff  e_R=12
```

No D-state bound is used for this profile: D-free A/B states supported on
nonadjacent singleton choices can be legal.

The three side instances are closed by labelled p/M grids:

```
idx68  (A,B)=(6,10)  search23/k2_idx68_q10S1S2D343_a6b10_labelled_w8x8_180.tsv   648/648 INFEASIBLE
idx69  (A,B)=(7,9)   search23/k2_idx69_q10S1S2D343_a7b9_labelled_w8x8_180.tsv   1039/1039 INFEASIBLE
idx70  (A,B)=(8,8)   search23/k2_idx70_q10S1S2D343_a8b8_labelled_w8x8_180.tsv   1080/1080 INFEASIBLE
```

Audit:

```
idx68: 648 / 648 INFEASIBLE
idx69: 1039 / 1039 INFEASIBLE
idx70: 1080 / 1080 INFEASIBLE
total: 2767 / 2767 INFEASIBLE
returncode: 0 for every task
stderr: empty for every task
missing: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V525. K2/T2 q=10 support `{S1,S2,D}`, profile `(0,4,4,2)` closed

Update 2026-06-21:

The next q10 support profile is

```
(c0,c1,c2,c3)=(0,4,4,2), support={S1,S2,D}.
```

The singleton core `R[S1,S2]` is a `4 x 4` bipartite graph with every
singleton vertex having opposite degree at least two.  Up to the
`S4 x S4` side action, this gives 42 canonical core masks.

No D-state bound is used for this profile: D-free A/B states supported on
nonadjacent singleton choices can be legal.

The three side instances are closed by labelled p/M grids:

```
idx71  (A,B)=(6,10)  search23/k2_idx71_q10S1S2D442_a6b10_labelled_w8x8_180.tsv   4113/4113 INFEASIBLE
idx72  (A,B)=(7,9)   search23/k2_idx72_q10S1S2D442_a7b9_labelled_w8x8_180.tsv   6038/6038 INFEASIBLE
idx73  (A,B)=(8,8)   search23/k2_idx73_q10S1S2D442_a8b8_labelled_w8x8_180.tsv   6170/6170 INFEASIBLE
```

Audit:

```
idx71: 4113 / 4113 INFEASIBLE
idx72: 6038 / 6038 INFEASIBLE
idx73: 6170 / 6170 INFEASIBLE
total: 16321 / 16321 INFEASIBLE
returncode: 0 for every task
stderr: empty for every task
missing: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V526. K2/T2 q=10 support `{E,D}`, profile `(1,0,0,9)` closed

Update 2026-06-22:

The next q10 support profile is

```
(c0,c1,c2,c3)=(1,0,0,9), support={E,D}.
```

The R-skeleton is a star from the unique empty-label vertex into the nine
doubleton vertices.  Up to the `S9` action on the doubletons, this gives
eight canonical masks with `e_R=2..9`:

```
search23/k2_q10_ED109_skeletons.tsv
```

The three side instances are closed by state-count p/M grids with K2
parameters `--k 2 --cnt 1,0,0,9 --r0 8 --t 2` and anti-tightness disabled:

```
idx74  (A,B)=(6,10)  search23/k2_idx74_q10ED_a6b10_state_results_w8x8_60.tsv    518/518 INFEASIBLE
idx75  (A,B)=(7,9)   search23/k2_idx75_q10ED_a7b9_state_results_w8x8_60.tsv     518/518 INFEASIBLE
idx76  (A,B)=(8,8)   search23/k2_idx76_q10ED_a8b8_state_results_w16x4_60.tsv    518/518 INFEASIBLE
```

Audit:

```
idx74: 518 / 518 INFEASIBLE
idx75: 518 / 518 INFEASIBLE
idx76: 518 / 518 INFEASIBLE
total: 1554 / 1554 INFEASIBLE
returncode: 0 for every batch
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V536. K2/T2 q=10 support `{E,D}`, profile `(3,0,0,7)` closed

Update 2026-06-22:

The q10 `{E,D}` profile

```
(c0,c1,c2,c3)=(3,0,0,7), support={E,D}.
```

uses the compact `{E,D}` skeleton generator:

```
search23/k2_q10_ED307_skeletons.tsv
```

The generator gives 664 canonical masks, and each side instance has a
186349-task state-count p/M grid.  The three side instances are closed with
K2 parameters `--k 2 --cnt 3,0,0,7 --r0 8 --t 2`, projection cuts `0;3`,
defect-block label `0`, and anti-tightness disabled:

```
idx92  (A,B)=(6,10)
  search23/k2_idx92_q10ED3_a6b10_state_results_proj03_db0_w64x1_180_bg.tsv
  search23/k2_idx92_q10ED3_a6b10_remaining_after_bg36706_results_w60x1_180.tsv

idx93  (A,B)=(7,9)
  search23/k2_idx93_q10ED3_a7b9_state_results_proj03_db0_w60x1_180.tsv

idx94  (A,B)=(8,8)
  search23/k2_idx94_q10ED3_a8b8_state_results_proj03_db0_w60x1_180.tsv
```

Audit:

```
idx92: 186349 / 186349 INFEASIBLE
idx93: 186349 / 186349 INFEASIBLE
idx94: 186349 / 186349 INFEASIBLE
total: 559047 / 559047 INFEASIBLE
UNKNOWN: 0
FEASIBLE: 0
```

Status: VERIFIED PROFILE CLOSURE.

## V537. K2/T2 all-doubleton support `{D}` closed for `q >= 11`

Update 2026-06-22:

In the exact-codegree-two K2 rooted model with all labels doubleton,

```
(c0,c1,c2,c3)=(0,0,0,q),
support={D}.
```

there are no legal R-edges, because every pair of doubleton labels intersects.
Thus `e_R=0`.  The same-root cut with both roots on one side and
`A,B,C` on the other gives the unpaired cut inequality

```
p + e_R >= 37.
```

So every all-doubleton candidate must have

```
p >= 37.
```

On the other hand, the fixed root and colour edges contribute

```
root_edges + U = (30-q) + 2q = 30+q.
```

Every R-vertex has label size 2 and no R-neighbours, so minimum degree
requires at least six A/B-neighbours at each R-vertex.  Hence

```
M >= 6q.
```

Using the finite edge window `e(G) <= 143`,

```
p <= 143 - (30+q) - 6q = 113 - 7q.
```

For `q >= 11`, this gives `p <= 36`, contradicting `p >= 37`.

Manifest audit:

```
search23/k2_four_label_profile_instances.tsv
```

contains exactly six all-doubleton profile-side instances with `q >= 11`:

```
idx98   q=11  (A,B)=(6,9)
idx99   q=11  (A,B)=(7,8)
idx150  q=12  (A,B)=(6,8)
idx151  q=12  (A,B)=(7,7)
idx234  q=13  (A,B)=(6,7)
idx297  q=14  (A,B)=(6,6)
```

All six are closed by the scalar cut above.  The generated q11 task grids

```
search23/k2_idx98_q11D_a6b9_state_tasks.tsv
search23/k2_idx99_q11D_a7b8_state_tasks.tsv
```

are retained as diagnostic artifacts only; no solver output is needed for
this closure.

Reproducibility audit:

```
python search23/audit_k2_scalar_closures_v537_v538.py
```

reports `V537 98,99,150,151,234,297` and `status=PASS`.

Status: VERIFIED SCALAR CLOSURE.

## V538. K2/T2 no-empty small `S1S2D` scalar closures

Update 2026-06-22:

Consider a K2/T2 four-label profile with no empty labels and with both
singleton shores present:

```
(c0,c1,c2,c3)=(0,c1,c2,c3),  c1,c2>0.
```

Then the only legal R-edges are between `S1` and `S2`; the `D` vertices are
R-isolated.  Write

```
e = e_R = e_R(S1,S2).
```

The same-root unpaired cut gives

```
p + e >= 37.                         (1)
```

For each doubleton vertex, minimum degree gives at least six A/B-neighbours.
For each singleton vertex `s`, since the listed profiles below have opposite
shore size at most five, `d_R(s) <= 5`, and minimum degree gives

```
m_s >= 7 - d_R(s).
```

Therefore

```
M >= 6c3 + 7(c1+c2) - 2e.             (2)
```

The fixed root and colour edges contribute

```
(30-q) + U = (30-q) + c1+c2+2c3 = 30+c3.
```

Using the edge cap `e(G) <= 143`, equations (2) and `q=c1+c2+c3` give

```
p <= 143 - (30+c3) - e - (6c3 + 7(c1+c2) - 2e)
  = 113 - 7q + e.                     (3)
```

Combining (1) and (3), any survivor must satisfy

```
37 - e <= 113 - 7q + e.
```

Equivalently,

```
2e >= 7q - 76.                        (4)
```

But `e <= c1*c2`.  Thus a profile is impossible whenever

```
2 c1 c2 < 7q - 76.
```

For `q=13`, this closes the two profile-side instances

```
idx235  q=13  (A,B)=(6,7)  (c0,c1,c2,c3)=(0,2,2,9)
idx236  q=13  (A,B)=(6,7)  (c0,c1,c2,c3)=(0,2,3,8)
```

For `q=14`, this closes the five profile-side instances

```
idx298  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,2,10)
idx299  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,3,9)
idx300  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,4,8)
idx301  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,5,7)
idx305  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,3,3,8)
```

Manifest audit:

```
search23/k2_four_label_profile_instances.tsv
```

contains exactly these profile-side rows with the displayed indices and
counts.  These seven instances are closed by the scalar inequalities above,
with no state-count solver output required.

Reproducibility audit:

```
python search23/audit_k2_scalar_closures_v537_v538.py
```

reports `V538 235,236,298,299,300,301,305` and `status=PASS`.

Status: VERIFIED SCALAR CLOSURE.

## V539. K2/T2 label-union aggregate MILP scalar closures

Update 2026-06-22:

Codex added a reproducible aggregate MILP checker:

```
search23/audit_k2_label_union_milp_v539.py
```

For each K2/T2 profile-side instance with `q>=11`, the checker forgets the
individual R-vertices and keeps only the four label classes

```
E, S1, S2, D.
```

The integer variables are:

```
eEE, eE1, eE2, eED, e12      R-edge counts by legal label block
p                            A-B edge count
alpha_E,alpha_S1,alpha_S2,alpha_D
gamma_E,gamma_S1,gamma_S2,gamma_D
```

Every actual rooted graph maps to such an integer point.  The checker imposes
only necessary constraints:

* legal block edge capacities;
* local domination in the two root colours;
* root-to-R side codegree lower bounds;
* aggregate minimum-degree lower bounds for each label class;
* aggregate A/B degree lower bounds;
* the finite edge window `112 <= e(G) <= 143`;
* the unpaired beta-cut inequalities for every `W` that is a union of label
  classes:

```
2 + L(W) + alpha(W) + gamma(R\\W) + e_R - boundary(W) >= 37,
2 + L(W) + gamma(W) + alpha(R\\W) + e_R - boundary(W) >= 37,
p + L(W) + alpha(W) + gamma(W) + e_R - boundary(W) >= 37.
```

Therefore MILP infeasibility is a sound certificate that no corresponding
profile-side instance can occur.

Running

```
python search23/audit_k2_label_union_milp_v539.py
```

returns

```
closed 98,99,120,121,150,151,182,183,234,235,236,255,271,297,298,299,300,301,302,303,304,305,324,325,326,345
new 120,121,182,183,255,271,302,303,304,324,325,326,345
open 263
status=PASS
```

The indices already closed by V537-V538 are ignored here.  The new V539
closures are:

```
idx120  q=11  (A,B)=(6,9)  (c0,c1,c2,c3)=(1,0,0,10)
idx121  q=11  (A,B)=(7,8)  (c0,c1,c2,c3)=(1,0,0,10)
idx182  q=12  (A,B)=(6,8)  (c0,c1,c2,c3)=(1,0,0,11)
idx183  q=12  (A,B)=(7,7)  (c0,c1,c2,c3)=(1,0,0,11)
idx255  q=13  (A,B)=(6,7)  (c0,c1,c2,c3)=(1,0,0,12)
idx271  q=13  (A,B)=(6,7)  (c0,c1,c2,c3)=(2,0,0,11)
idx302  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,6,6)
idx303  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,7,5)
idx304  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(0,2,8,4)
idx324  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(1,0,0,13)
idx325  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(1,2,2,9)
idx326  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(1,2,3,8)
idx345  q=14  (A,B)=(6,6)  (c0,c1,c2,c3)=(2,0,0,12)
```

Status: VERIFIED AGGREGATE MILP CLOSURE.

## V540: K2/T2 q10 `{E,D}` idx95 side-count closure

Update 2026-06-23:

Codex closed the first remaining q10 `{E,D}` profile-side instance

```
idx95  q=10  (A,B)=(6,10)  (c0,c1,c2,c3)=(4,0,0,6).
```

The original state-count grid has 1157595 rows.  The side-sum prefilter removes
558117 rows and leaves 599478 tasks.  The prefilter audit is

```
search23/k2_q10_ED406_sidesum_prefilter_audit.tsv
python search23/audit_k2_sidesum_prefilter.py
```

with `missing=0` and `extra=0` for idx95-97 filtered task sets.

The complete idx95 result certificate is

```
search23/k2_idx95_q10ED4_a6b10_state_results_sidesum_merged_complete.tsv
```

It is assembled from the split result files, a cleaned resume4 file, and the
single standalone retry-fix row

```
search23/k2_idx95_q10ED4_a6b10_state_results_sidesum_resume4_exception_fix.tsv
```

for key `(mask,p,M)=(0x3ce9c9d8,57,36)`, which reruns as INFEASIBLE.

The full closure audit command

```
python search23/audit_k2_filtered_result_closure.py \
  --skeletons search23/k2_q10_ED406_skeletons.tsv \
  --original search23/k2_idx95_q10ED4_a6b10_state_tasks.tsv \
  --filtered search23/k2_idx95_q10ED4_a6b10_state_tasks_sidesum.tsv \
  --results search23/k2_idx95_q10ED4_a6b10_state_results_sidesum_merged_complete.tsv \
  --a 6 --b 10
```

returns

```
original=1157595  killed=558117  filtered=599478
filter_missing=0 filter_extra=0 results=599478
result_missing=0 result_extra=0 bad_status=0
```

Status: VERIFIED STATE-COUNT CLOSURE.

## V541. K2/T2 no-doubleton root-pair transposition reduction

Update 2026-06-23:

Codex audited the GPT Pro suggestion that in a `K=2,T=2` rooted instance with
no doubleton labels (`c3=0`), the two original common neighbours can be used
as a second exact-codegree-two root pair.

The standalone proof note is

```
search23/k2_d0_root_transposition_note.md
```

The profile map is

```
(q,A,B; c0,c1,c2,0) -> (A+B+c0, c1, c2; c0,A,B,0),
```

followed by the same root-side and colour-swap canonicalization used by the
four-label manifest.

The manifest audit command

```
python search23/audit_k2_d0_transposition.py
```

returns

```
checked_d0_instances=8
failures=0
idx270->idx344
idx344->idx270
idx360->idx360
```

Therefore the residual `E+S1+S2` instance `idx344` is redundant with `idx270`,
and `idx360` is self-dual.  This is a reduction only: it does not close
`idx270` or `idx360`.

The post-V541 residual manifest is generated by

```
python search23/make_k2_residual_after_v541.py
```

which writes

```
search23/k2_q11_q14_residual_after_v541.tsv
search23/k2_q11_q14_residual_after_v541_dependencies.tsv
```

and reports

```
kept=262
removed=1
removed_idx=344
by_q=11:48,12:80,13:58,14:76
```

The independent residual-manifest audit

```
python search23/audit_k2_residual_after_v541.py
```

returns

```
v539=263
v541=262
dependencies=1
missing_kept=0
extra_kept=0
wrong_deps=0
bad_dep_fields=0
```

Status: VERIFIED MANIFEST REDUCTION.

## V542. K2/T2 q10 E+D idx96 closure and idx97 launch

Update 2026-06-23:

The q10 `E+D` profile-side instance

```
idx96: (q,A,B; c0,c1,c2,c3) = (10,7,9; 4,0,0,6)
```

is now closed by the complete state-count result

```
search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_complete.tsv
```

The finalizer command

```
python search23/finalize_k2_idx96.py \
  --extra-results search23/k2_idx96_q10ED4_a7b9_state_results_resume_no_status_retry_1x1.tsv
```

reported

```
inputs=4
rows=1010315
original=1157732
killed=147417
filtered=1010315
filter_missing=0
filter_extra=0
results=1010315
result_missing=0
result_extra=0
bad_status=0
```

The active resume had two `NO_STATUS` rows, both rerun as `INFEASIBLE` in

```
search23/k2_idx96_q10ED4_a7b9_state_results_resume_no_status_retry_1x1.tsv
```

for keys

```
(0x303b89c0,46,53)
(0x30b09bd8,35,53)
```

The audited Exact-E-ND open-neighbourhood cut has now been inserted into

```
search23/state_count_6195_cpsat.py
```

and `python -m py_compile search23/state_count_6195_cpsat.py` plus
`python search23/state_count_6195_cpsat.py --help` both succeeded.

The remaining q10 `E+D` instance

```
idx97: (q,A,B; c0,c1,c2,c3) = (10,8,8; 4,0,0,6)
```

has been launched with 64 workers using the strengthened verifier.  The live
output is

```
search23/k2_idx97_q10ED4_a8b8_state_results_sidesum_64x1.tsv
search23/k2_idx97_q10ED4_a8b8_state_results_sidesum_64x1.stderr.log
```

Initial poll: `3796` result rows, all `INFEASIBLE`.

Status: idx96 VERIFIED STATE-COUNT CLOSURE; idx97 ACTIVE.
