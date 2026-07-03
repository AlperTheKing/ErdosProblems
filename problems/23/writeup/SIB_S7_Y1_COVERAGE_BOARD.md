# SIB S7 y=1 Coverage Board

Current date: 2026-07-02.

This file records the current executable state of the SIB S7 `y=1` branch. It is not a closure proof for S7.

## Audited Green Local Tree

Claude reproduced the full `problems/23/writeup/_codex_sib_s7_y1_manifest.py` run on 2026-07-02T15:10:55Z. Locally, the same manifest exits 0.

The manifest includes the following important local reductions:

- capacity fibers `s4..s7` reduce to `x=1`, `s2=0`, `s3=0`, `u=1`, or `x=q`;
- `x=q` has no interior minimum and reduces to endpoint blockers;
- observed `x=q` endpoint systems reduce to exact closed families;
- `x=q,s2=0` now reduces to the tracked `u1`, `s1`, or `s3` blockers via the descent trio;
- `x=q,s1=0` has paired capacity-sign identities recorded in `_codex_sib_s7_y1_xq_s1_pair_structure.py`;
- `x=q,s1=0` capacity faces have exact two-gap quadrant forms recorded in `_codex_sib_s7_y1_xq_s1_quadrant_parametrizations.py`;
- `x=q,s1=0,c=e` has the exact `b/d` paired ridge recorded in `_codex_sib_s7_y1_xq_s1_ridge_structure.py`;
- observed `u=1` capacity-critical systems reduce to exact closed families;
- all observed positive-dimensional support families are exactly positive or closed;
- one-step add-neighbors are closed subfaces or impossible;
- one-step drop-neighbors from the observed supports are closed;
- symbolic tangent witnesses exist for all six positive-dimensional observed families;
- univariate tangent-root counts are exact for the five one-parameter observed families;
- `XQ_A` simultaneous tangent criticality projects to exactly two `X>=0` algebraic candidates.

## Manifest Command

```text
PYTHONDONTWRITEBYTECODE=1 python problems/23/writeup/_codex_sib_s7_y1_manifest.py
```

Expected result: every listed script prints `PASS-MANIFEST`; the manifest then prints the open coverage obligations below.

## Remaining Proof Obligations

These are theorem-level coverage obligations, not missing local positivity gates.

1. Prove full `y=1` capacity critical-leaf exclusion beyond the observed survivor families.
2. Prove full `x=q` endpoint coverage after reductions to `v1/u1/s1/s3` blockers; `s2` is routed and `s1` has paired-sign structure.
3. Prove the restricted active-set survivor inventory covers every `y=1` capacity branch.
4. After `S7 y=1` coverage closes, handle the remaining refined endpoint faces outside `y=1`.

The first three items are parts of the same coverage theorem shape:

- any negative minimizer has an FJ/active support;
- if the support is one of the observed families, symbolic nonflatness plus the closed one-step neighborhood forces it to the closed boundary;
- if the support is not observed, a finite exact support enumeration/Groebner exclusion must rule it out.

## Non-Proof Guardrail

`problems/23/writeup/_codex_sib_s7_y1_observed_coverage.py` reruns the deterministic basin classifier and currently observes only classified/closed clusters. This is a regression guard only; it is not accepted as proof of the coverage theorem.

## Latest New Artifact

`problems/23/writeup/_codex_sib_s7_y1_symbolic_rank_certificates.py` verifies nonzero symbolic tangent derivative witnesses for:

- `ALL_TIGHT`
- `HIGH_A`
- `XQ_A`
- `XQ_B`
- `U1_S7_HIGH`
- `XQ_S5_HIGH`

This supports the observed-family part of the coverage proof but does not exclude unobserved supports.



## Latest Ridge Artifact

`problems/23/writeup/_codex_sib_s7_y1_xq_s1_ridge_structure.py` verifies that on `y=1,x=q,s1=0,c=e`, `s4=s5`, `s6=s7`, and `s6-s4=f(d-b)`. Hence active `s4/s5` faces force `d>=b`, active `s6/s7` faces force `b>=d`, and `b=d` makes all four capacity slacks equal.

## Latest Root Artifact

`problems/23/writeup/_codex_sib_s7_y1_tangent_root_inventory.py` verifies exact nonnegative root counts for the tangent witness polynomials on the five one-parameter observed families: `ALL_TIGHT=1`, `HIGH_A=1`, `XQ_B=1`, `U1_S7_HIGH=0`, `XQ_S5_HIGH=1`. The two-parameter `XQ_A` tangent-critical inventory remains separate.

## Latest Quadrant Artifact

`problems/23/writeup/_codex_sib_s7_y1_xq_s1_quadrant_parametrizations.py` verifies that with `r=c-e` and `h=s3-s2+1`, each active capacity face has the other capacity slacks equal to `aR`, `fH`, and `aR+fH` for nonnegative quadrant gaps `R,H`.

## Latest XQ_A Candidate Artifact

`problems/23/writeup/_codex_sib_s7_y1_xqa_bivariate_candidate_inventory.py` verifies by Groebner elimination that simultaneous tangent criticality on the two-parameter `XQ_A` family has an `X` eliminant whose degree-41 core has exactly two roots on `X>=0`; a nondegenerate linear Groebner row in `R` determines `R`. This narrows but does not yet exclude/domain-classify the two candidates.

## XQ_A Bivariate Coverage Role

The corrected `XQ_A` bivariate candidate gate is intended as a finite-criticality gate, not as a positivity gate. It proves that simultaneous vanishing of the two tangent derivatives on the two-parameter `XQ_A` family has only two `X>=0` algebraic candidates, with a nondegenerate linear Groebner row determining `R` at each candidate. Any candidate that lies in `0<=R<=1` is already covered by `_codex_sib_s7_y1_observed_supports_closed.py`, whose `XQ_A` Bernstein-in-`r` certificate proves positivity on the whole family rectangle. Thus the remaining theorem-level coverage burden is to exclude unobserved active supports and assemble the observed-family boundary/finite-criticality argument.

## Observed Coverage Counts

The deterministic regression scan `_codex_sib_s7_y1_observed_coverage.py` currently observes 12 branch/cap clusters and classifies all of them into exact closed families. The one-step support-neighborhood inventory has 101 one-step neighbors: 63 sample-compatible neighbors and 38 add-neighbors requiring witnesses. `_codex_sib_s7_y1_support_neighbor_reductions.py` closes those 38 add-neighbors as closed subfaces or impossible constraints. These are regression and local-neighborhood facts; the remaining proof obligation is an exact FJ/active-support enumeration showing that no unobserved support family can occur.

## Observed Rank-Basis Artifact

`problems/23/writeup/_codex_sib_s7_y1_observed_rank_bases.py` records exact Jacobian rank bases for the observed support families. In the seven-variable branch/cap charts, the observed families have rank bases of size at most seven: `XQ_A` has size 5; `ALL_ONES` has size 7; the other observed families have size 6. This is a coverage bookkeeping artifact: it identifies the basis-size scale for the exhaustive FJ active-support enumeration, but it does not by itself exclude unobserved supports.

## Raw Basis-Search Census

`problems/23/writeup/_codex_sib_s7_y1_basis_search_census.py` records the raw finite search universe for a rank-basis-style FJ enumeration. Across the 16 branch/cap charts, there are 184,432 active-label subsets of size at most seven: each `s2/s3/u1` chart has 9,908 such subsets, and each `xq` chart has 16,384. This is the unpruned finite universe; the next proof artifact must prune or close these supports by exact algebraic feasibility/KKT tests.

## Observed Cluster Rank Bases And Pruning

`problems/23/writeup/_codex_sib_s7_y1_observed_cluster_rank_bases.py` extends the rank-basis inventory to the full deterministic observed scan cluster list: all-tight clusters in `s2/s3/u1` charts, the `s2` and `s3` survivor families, and the cap-shifted `xq,s5` observed families. All observed scan clusters have rank bases of size at most seven.

`problems/23/writeup/_codex_sib_s7_y1_basis_pruning_census.py` then classifies the 184,432 raw rank-basis supports by proximity to these observed bases. The current counts are: 693 supports contain an observed basis, 99 are one-step from an observed basis, 1,051 are two-step, and 182,589 remain `unobserved_far`. Thus the remaining coverage theorem still requires algebraic exclusion/pruning of a large unobserved-support set; observed-neighborhood proximity alone is not enough.

## Exact Lower-Bound Far-Support Filter

`problems/23/writeup/_codex_sib_s7_y1_far_support_profile.py` records that the `182,589` unobserved-far supports are mostly size `5..7`, with size histogram `0:16, 1:228, 2:1494, 3:6162, 4:17167, 5:35849, 6:55300, 7:66373`. There is no small-size-only corner to close.

`problems/23/writeup/_codex_sib_s7_y1_far_support_linear_filter.py` applies exact deterministic propagation from active lower-bound labels and shifted one-sign/linear active equations. It eliminates or routes part of the far universe: `28,360` supports are contradictory, `3,577` deterministically close to an observed basis, and `150,652` remain still unobserved. The remaining theorem burden is therefore an algebraic/KKT exclusion for those `150,652` supports or a stronger structural replacement.

## Exact Monomial-Hit Branching Filter

`problems/23/writeup/_codex_sib_s7_y1_far_support_monomial_hit_filter.py` extends the lower-bound propagation filter by using one-sign shifted active equations with zero constant term. Each nonconstant monomial must vanish, so the script branches on the corresponding forced lower-bound labels and propagates recursively.

On the `150,652` post-linear still-unobserved starts, this closes `1,144` starts and leaves `149,508` starts with unobserved terminals. The terminal closures compress to `84,087` unique still-unobserved support states, with no branch explosions. This is not a closure theorem, but it gives a smaller normalized target for the next algebraic/KKT exclusion.

## Terminal Rank-Shape Samples

`problems/23/writeup/_codex_sib_s7_y1_terminal_rank_profile.py` profiles monomial-hit terminal states by exact generic active-equation rank. Full all-chart profiling is too slow without persisted terminal states, so the current evidence is chart-scoped.

For the completely unobserved charts:

- `xq,s7`: `6,924` unique terminal supports, rank histogram `2:1, 3:14, 4:92, 5:374, 6:1033, 7:1959, 8:2343, 9:1108`.
- `s3,s6`: `4,269` unique terminal supports, rank histogram `2:1, 3:13, 4:79, 5:294, 6:734, 7:1242, 8:1291, 9:615`.
- `s3,s7`: `4,221` unique terminal supports, rank histogram `2:1, 3:13, 4:79, 5:294, 6:732, 7:1232, 8:1271, 9:599`.

Thus a nontrivial isolated-system component exists, but the larger remaining mass is rank `7` and `8`; the next exclusion step needs positive-dimensional family/descent structure as well as Groebner handling of rank-9 terminals.

## Full Terminal Rank Distribution

Using chart-scoped runs of `problems/23/writeup/_codex_sib_s7_y1_terminal_rank_profile.py`, the `84,087` monomial-hit unique still-unobserved terminal states have aggregate exact generic active-equation rank histogram:

```text
rank 2:     16
rank 3:    220
rank 4:  1,386
rank 5:  5,431
rank 6: 13,882
rank 7: 24,804
rank 8: 26,724
rank 9: 11,624
```

The dominant obstruction is therefore rank `7/8` positive-dimensional (`51,528` states), with a substantial but secondary rank-9 isolated-system residue (`11,624` states). This supports prioritizing structural descent/family exclusion on the hard charts (`s3,s6`, `s3,s7`, and `xq` capacity charts), not only isolated Groebner cleanup.

## S3 Capacity Pair Structure

`problems/23/writeup/_codex_sib_s7_y1_s3_pair_structure.py` verifies exact paired capacity identities on the hard `s3=0` branch. With `R=c-e` and `H=b+c-d-e`:

```text
s4-s5 = s6-s7 = aR
s4-s6 = s5-s7 = fH
s4-s7 = aR+fH
s5-s6 = -aR+fH
```

Consequently, on the `s6=0` active face, feasibility of `s7>=0` forces `c<=e`; on the `s7=0` active face, feasibility of `s6>=0` forces `c>=e`. This gives the same kind of signed half-face split used earlier in the `x=q` pair-structure reductions and is the current structural target for the `s3,s6/s7` hard charts.

## S3 Ridge-Descent Stress

`problems/23/writeup/_codex_sib_s7_y1_s3_ridge_descent_stress.py` records an exact rational stress test for the ridge direction suggested by the `s3` pair structure. On `s3=0,s7=0`, with `R=c-e`, all deterministic feasible rational samples have `dPhi/dR>0`, supporting descent toward the `c=e` ridge. On the mirror `s3=0,s6=0` face, with `R=e-c`, the script gives an exact feasible rational witness with `dPhi/dR<0`. Thus the hard `s3,s6` chart cannot be closed by the naive mirror ridge descent; it needs another direction or a different structural argument.

## S3 Active-Face Normal Forms

`problems/23/writeup/_codex_sib_s7_y1_s3_active_faces.py` verifies exact two-gap parametrizations on the hard `y=1, s3=0` active capacity faces.

On `s7=0`, write `c=e+R` and `H=b+c-d-e`. Then `s6=aR`, `s5=fH`, and `s4=aR+fH`; feasibility reduces the remaining capacity slacks to `R>=0` and `H>=0`.

On `s6=0`, write `e=c+R` and keep `H=b+c-d-e`. Then `s7=aR`, `s4=fH`, and `s5=aR+fH`; again the remaining capacity slacks reduce to `R>=0` and `H>=0`.

This strengthens the earlier s3 sign split: the hard `s3,s6/s7` charts are now explicit two-gap ridge problems. The stress artifact still says only the `s3,s7` direct ridge is supported; `s3,s6` needs a different descent direction.

## S3S7 Split Coordinates

`problems/23/writeup/_codex_sib_s7_y1_s3_s7_split_coordinates.py` records a nonnegative split parametrization for the `s3=0,s7=0` hard face.

Write `d=1+D1+D2`, `b=1+D1+P`, `R=c-e=D2+Q`. Then `H=b+c-d-e=P+Q`, and the remaining capacity slacks are `s6=aR`, `s5=fH`, `s4=aR+fH`.

This removes the signed constraint `d-1 <= (b-1)+R` from the `s3,s7` feasibility region by replacing it with nonnegative split variables. Full derivative expansion in these variables was too large in the current session, but this is now the preferred coordinate system for the next `H`/`b`-descent certificate attempt.

## U1 Terminal Pruning Artifacts

`problems/23/writeup/_codex_sib_s7_y1_u1_terminal_shape_profile.py` profiles the `u1` branch of the monomial-hit terminal support universe. It records `20,152` unique still-unobserved `u1` terminal supports, with rank histogram:

```text
rank 2: 4
rank 3: 56
rank 4: 360
rank 5: 1,396
rank 6: 3,512
rank 7: 6,166
rank 8: 6,255
rank 9: 2,403
```

`problems/23/writeup/_codex_sib_s7_y1_u1_implied_slack_closure.py` adds any inactive slack label forced identically zero by the currently fixed lower-bound labels. This closes `208` terminal supports to observed bases and compresses the unresolved unique `u1` terminal supports to `16,572`.

`problems/23/writeup/_codex_sib_s7_y1_u1_inactive_ineq_closure.py` additionally uses deterministic inactive-slack inequality forcing: if an inactive slack, shifted by lower bounds, has all coefficients nonpositive and zero constant, then every linear negative term must vanish. This closes `2,712` of the `20,152` `u1` terminal supports to observed bases and compresses the unresolved unique count to `11,995`.

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_e_ray.py` certifies one newly exposed boundary ray from that pruning:

```text
y=1, u=1, s4=0,
a=b=c=d=f=x=v=1, e>=1.
```

After setting `e=1+E`, the cleared numerator of `Phi` is

```text
6E^4 + 361E^3 + 1530E^2 + 1450E + 125,
```

so the ray is strictly positive. This is a local family certificate, not a full `u1` coverage theorem.

## U1 ABDF Capacity Family

`problems/23/writeup/_codex_sib_s7_y1_u1_abdf_cap_family.py` certifies the broad lower-bound family

```text
y=1, u=1, a=b=d=f=1,
cap in {s4,s5,s6,s7}.
```

On this family, `s5=s6`, `s4-s5=c-e`, and `s7-s5=e-c`. Thus feasible `s5=0` or `s6=0` forces `c=e` and reduces to the common ridge. The full-dimensional faces are:

```text
s4=0: e>=c>=v>=1,
s7=0: c>=e>=v>=1.
```

Both are coefficientwise positive after nonnegative parametrization; the cleared numerator has `130` terms, no negative coefficients, and minimum coefficient `8` in each case.

`problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py` counts this custom family against the post-inactive `u1` terminals. It closes `282` terminal instances (`69,65,65,83` across `s4,s5,s6,s7`) and reduces the unresolved unique `u1` terminal support count from `11,995` to `11,730` after observed-family and custom-family closure.

## U1 ABD S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_abd_family.py` certifies the broader family

```text
y=1, u=1, s4=0, a=b=d=1.
```

With `s4=0`, solve

```text
c = (x(1+v)+v-f)/(1+f).
```

Feasibility gives `v>=f` and `e>=max(c,v)`. Since

```text
c-v = (1+v)(x-f)/(1+f),
```

the proof splits into two chambers: `x>=f` with `e=c+E`, and `f>=x` with `e=v+E`. In the `x>=f` chamber the cleared numerator has `1213` positive coefficients; in the `f>=x` chamber it has `1133` positive coefficients. The minimum coefficient is `2` in both chambers.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `487` terminal instances: `U1_ABDF_CAP=282` and `U1_ABD_S4=205`. The unresolved unique `u1` support count is now `11,617`.

## U1 AB S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_ab_family.py` certifies the broader family

```text
y=1, u=1, s4=0, a=b=1.
```

With `s4=0`, solve

```text
c = (x(1+v)+v-f)/(1+f).
```

Then

```text
c-x = (x+1)(v-f)/(1+f),
c-v = (1+v)(x-f)/(1+f).
```

The feasible region splits into chambers `x>=f` and `f>=x`. In the `x>=f` chamber the cleared numerator has `2662` positive coefficients; in the `f>=x` chamber it has `2609` positive coefficients. The minimum coefficient is `2` in both chambers.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `922` terminal instances: `U1_ABDF_CAP=282`, `U1_ABD_S4=205`, `U1_ABF_S4=190`, and `U1_AB_S4=245`. The unresolved unique `u1` support count is now `11,345`.

## U1 ACDF S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_acdf_family.py` certifies the family

```text
y=1, u=1, s4=0, a=c=d=f=1.
```

With `s4=0`, solve

```text
b = x(1+v)+v-2.
```

Writing `x=1+X`, `v=1+V`, and `e=b+E`, feasibility follows from

```text
b = 1 + VX + 2V + 2X,
b-x = VX + 2V + X,
e-v = E + VX + V + 2X.
```

The cleared numerator of `Phi` has `135` positive coefficients and minimum coefficient `2`.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `990` terminal instances: `U1_ABDF_CAP=282`, `U1_ABD_S4=205`, `U1_ABF_S4=190`, `U1_AB_S4=245`, and `U1_ACDF_S4=68`. The unresolved unique `u1` support count is now `11,277`.

A broader attempted `a=c=d=1, s4=0` family is not a raw coefficient cone. Monotonicity in `e` must be used with the true feasibility boundary `e=max(b,v)`, so the next proof surface splits into `b>=v, e=b` and `v>=b, e=v` chambers. The preliminary `e=b` core alone has negative coefficients, so this broader family should be handled by a compactified Bernstein/KKT certificate rather than another simple family cone.

## U1 ACD S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_acd_family.py` certifies the broader family

```text
y=1, u=1, s4=0, a=c=d=1.
```

Write `x=1+X`, `b=x+s`, and `f=1+t`. The equation `s4=0` determines

```text
v = (1 + f(b+1) - x)/(x+1).
```

Feasibility requires `s>=0`, `v>=1`, and `e>=max(b,v)`. The proof splits into four exact chambers:

```text
s>=X, b>=v:  t = R*U, 0<=R<=1, e=b+E,
s>=X, v>=b:  t = U+G, e=v+E,
X>=s, b>=v:  t = L+R*(U-L), 0<=R<=1, e=b+E,
X>=s, v>=b:  t = U+G, e=v+E.
```

In the two bounded `b>=v` chambers the cleared numerator is nonnegative in the Bernstein basis in `R`: chamber term totals are `1915` and `1514`, with minimum coefficient `0`. In the two unbounded `v>=b` chambers the cleared numerator is coefficientwise positive: `2115` terms and `2379` terms, both with minimum coefficient `2`.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1169` terminal instances: `U1_ABDF_CAP=282`, `U1_ABD_S4=205`, `U1_ABF_S4=190`, `U1_AB_S4=245`, and `U1_ACD_S4=247`. The unresolved unique `u1` support count is now `11,163`.

The next post-custom top residual example is

```text
cap=s4, support=a1,c1,f1,u1.
```

## U1 ACF S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_acf_family.py` certifies the family

```text
y=1, u=1, s4=0, a=c=f=1.
```

With `s4=0`, solve

```text
b = x(1+v)+v-2.
```

Writing `x=1+X`, `v=1+V`, this gives

```text
b = 1 + VX + 2V + 2X,
b-x = VX + 2V + X,
b-v = VX + V + 2X.
```

Set `d=1+D`, `e=1+E`. The remaining feasibility constraints reduce to

```text
E >= V,
D+E >= B0 := b-1 = VX + 2V + 2X.
```

The cleared numerator of `Phi` is coefficientwise increasing in both `D` and `E`: `dPhi/dD` has `132` positive coefficient terms with minimum coefficient `4`, and `dPhi/dE` has `396` positive coefficient terms with minimum coefficient `4`. Therefore the minimum is on the segment

```text
E = V + R*(B0-V),
D = B0-E,
0 <= R <= 1.
```

On that segment, the numerator has `3` Bernstein coefficients in `R`, with `140` total coefficient terms and minimum coefficient `4`; the denominator has `57` positive coefficient terms and minimum coefficient `1`.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1304` terminal instances: `U1_ABDF_CAP=282`, `U1_ABD_S4=205`, `U1_ABF_S4=190`, `U1_AB_S4=245`, `U1_ACD_S4=179`, and `U1_ACF_S4=203`. The unresolved unique `u1` support count is now `11,050`.

The next post-custom top residual example is

```text
cap=s4, support=a1,c1,u1.
```

## U1 AC S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_ac_family.py` certifies the broader family

```text
y=1, u=1, s4=0, a=c=1.
```

With

```text
m = x(1+v)+v,
```

`s4=0` gives

```text
1 + f(b+1) = m.
```

The proof uses

```text
b = x+s,
f = (m-1)/(b+1),
0 <= s <= xv+v-2.
```

Writing `x=1+X`, `v=1+V`, split by `X>=V` and `V>=X`.

In the `X>=V` side, `b>=x>=v`, and the feasible minimum is checked on:

```text
D = Q(b-v),   E = b-1-D      (segment)
D = b-v+G,    E = V          (ray)
```

where `d=1+D`, `e=1+E`.  The segment has `27` final Bernstein coefficients, `3488` total coefficient terms, and minimum coefficient `8`; the ray has `8` Bernstein coefficients, `2732` terms, and minimum coefficient `2`.

In the `V>=X` side, write `V=X+H`.  The low chamber `0<=s<=H` has `v>=b` and is checked on `E=V`; it has `7` Bernstein coefficients, `1457` terms, and minimum coefficient `2`.  The high chamber `H<=s<=xv+v-2` has `b>=v` and uses the same segment/ray split; the high segment has `24` coefficients, `3277` terms, and minimum coefficient `8`, while the high ray has `8` coefficients, `2732` terms, and minimum coefficient `2`.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1468` terminal instances:

```text
U1_ABDF_CAP=282
U1_ABD_S4=205
U1_ABF_S4=190
U1_AB_S4=245
U1_AC_S4=546
```

The unresolved unique `u1` support count is now `10,916`.  The next post-custom top residual example is

```text
cap=s4, support=a1,d1,f1,u1.
```

## U1 ADF S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_adf_family.py` certifies the family

```text
y=1, u=1, s4=0, a=d=f=1.
```

Here

```text
s4 = b + 2c - m,
m = x(1+v)+v.
```

Write `x=1+X`, `v=1+V`, and

```text
M3 = m-3 = XV + 2X + 2V,
c = 1 + R*M3/2,
b = 1 + (1-R)*M3,
0 <= R <= 1.
```

The remaining feasibility constraints reduce to

```text
e >= v,
e >= b+c-1.
```

The second lower bound dominates since

```text
b+c-1-v = (M3*(2-R)-2V)/2 >= (M3-2V)/2 = X(V+2)/2 >= 0.
```

So the proof checks the boundary

```text
e = b+c-1+E,
E >= 0.
```

The cleared numerator has `5` Bernstein coefficients in `R`, with `675` total coefficient terms and minimum coefficient `4`.

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1565` terminal instances:

```text
U1_ABDF_CAP=282
U1_ABD_S4=205
U1_ABF_S4=190
U1_AB_S4=245
U1_AC_S4=478
U1_ADF_S4=165
```

The unresolved unique `u1` support count is now `10,819`.  The next post-custom top residual example is

```text
cap=s4, support=a1,d1,u1.
```

## U1 AD S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_ad_family.py` certifies the broader family

```text
y=1, u=1, s4=0, a=d=1.
```

Set

```text
x = 1+X,
v = 1+V,
t = b+c-2,
q = c-1.
```

Then

```text
b = 1+t-q,
c = 1+q,
f = (m-c)/(b+c),
m = x(1+v)+v,
M3 = m-3 = XV+2X+2V.
```

The feasibility constraints are

```text
f >= 1       <=> t+q <= M3,
b,c >= 1    <=> 0 <= q <= t,
s3 >= 0     <=> t >= X,
e >= max(v,b+c-1).
```

Since `M3/2 >= X,V`, the proof covers the domain by four exact chambers:

```text
1. M3/2 <= t <= M3,        q <= M3-t,     e=1+t+E.
2. X<=V, X <= t <= V,      q <= t,        e=v+E.
3. X<=V, V <= t <= M3/2,   q <= t,        e=1+t+E.
4. X>=V, X <= t <= M3/2,   q <= t,        e=1+t+E.
```

The chamber Bernstein statistics are:

```text
high_all:       30 coeffs, 12450 terms, min 8
x_le_v_low:     32 coeffs,  9400 terms, min 2
x_le_v_mid:     36 coeffs, 17375 terms, min 8
x_ge_v_mid:     36 coeffs, 17375 terms, min 8
```

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1765` terminal instances:

```text
U1_ABDF_CAP=282
U1_ABD_S4=205
U1_ABF_S4=190
U1_AB_S4=245
U1_AC_S4=299
U1_AD_S4=544
```

The unresolved unique `u1` support count is now `10,698`.  The next post-custom top residual example is

```text
cap=s4, support=a1,f1,u1.
```

## U1 AF S4 Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_af_family.py` certifies the family

```text
y=1, u=1, s4=0, a=f=1.
```

With

```text
x = 1+X,
v = 1+V,
M3 = m-3 = XV+2X+2V,
q = c-1,
c = 1+q,
b = 1+M3-2q,
0 <= q <= M3/2.
```

The feasibility constraints reduce to

```text
e >= v,
e >= c,
d >= 1,
d+e >= b+c.
```

The proof splits into four Bernstein chambers:

```text
q <= V, e in [v, b+c-1], d=b+c-e+D: 18 coeffs, 2136 terms, min 2
q <= V, e >= b+c-1, d=1+D:       5 coeffs, 1480 terms, min 2
q >= V, e in [c, b+c-1], d=b+c-e+D: 15 coeffs, 1868 terms, min 4
q >= V, e >= b+c-1, d=1+D:       5 coeffs, 1480 terms, min 4
```

After adding this to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, custom closures become `1921` terminal instances:

```text
U1_ABDF_CAP=282
U1_ABD_S4=205
U1_ABF_S4=190
U1_AB_S4=245
U1_AC_S4=299
U1_AD_S4=544
U1_AF_S4=156
```

The unresolved unique `u1` support count is now `10,572`.  The next post-custom top residual example is

```text
cap=s4, support=a1,u1.
```

## U1 A S4 Low Chamber

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_a_low_chamber.py` certifies the first broad chamber of the next residual family

```text
y=1, u=1, s4=0, a=1.
```

Write

```text
x = 1+X,  v = 1+V,  V = X+H,
t = b+c-2 = X+R H,       0 <= R <= 1,
q = c-1 = S t,           0 <= S <= 1.
```

This is the low chamber `X <= t <= V`, with `q <= t`. The remaining variables are

```text
b = 1+t-q,
c = 1+q,
f = (x(1+v)+v-c)/(b+c),
e = 1+V+E,
d = 1+D.
```

The script verifies exact Bernstein positivity in `R,S` and monomial positivity in `X,H,D,E`:

```text
Phi: 32 Bernstein coefficients, 23416 shifted terms, minimum coefficient 2/35.
dPhi/dD: 28 Bernstein coefficients, 11020 shifted terms, minimum coefficient 1/5.
dPhi/dE: 32 Bernstein coefficients, 45136 shifted terms, minimum coefficient 4/35.
```

This is a chamber certificate for the broad `a=1` residual, not yet a full `U1_A_S4` family closure.

## U1 A S4 Middle Chamber: V >= X, q <= V <= t

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_a_vge_x_qle_v_mid_chamber.py` certifies the second chamber of the broad residual family

```text
y=1, u=1, s4=0, a=1.
```

Use

```text
x = 1+X,  v = 1+V,  V = X+H,
q = c-1 = S V,                 0 <= S <= 1,
t = b+c-2 = V + R*(M3-q-V),    0 <= R <= 1,
M3 = x(1+v)+v-3.
```

This is the chamber `V>=X` and `q<=V<=t`.  With `W=t-V`, the feasible `d/e` region splits into:

```text
segment: e=1+V+U*W, d=1+W-U*W+G, 0<=U<=1, G>=0,
ray:     e=1+t+E,   d=1+D.
```

The script uses the reduced `s4=0,a=1` identities

```text
Y=m,
f(b+c)=m-c,
Z=e*m+d*(m-c),
A=m+e+(d+e)*(b+c+f),
B=m+e*(1+b+c+f).
```

Exact checks:

```text
segment boundary: 116 Bernstein coefficients, 11128 terms, minimum coefficient 4/3.
segment d-slack derivative: 71 Bernstein coefficients, 11532 terms, minimum coefficient 1.
ray full hand-cleared numerator: 40 Bernstein coefficients, 30178 terms, minimum coefficient 1/10.
```

Therefore this whole `V>=X, q<=V<=t` chamber is Bernstein-positive.

## U1 A S4 Top Face: V >= X, q = t = M3/2

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_a_qtop_face.py` certifies a boundary face of the remaining broad residual family

```text
y=1, u=1, s4=0, a=1.
```

Use

```text
x = 1+X,  v = 1+V,  V = X+H,
M3 = x(1+v)+v-3,
q = c-1 = M3/2,
t = b+c-2 = q.
```

Since `e >= c = 1+q` already implies `d+e >= b+c = 2+t`, the remaining feasible region is

```text
e = 1+q+E,
d = 1+D.
```

The selected capacity equation `s4=0` gives `f=(m-c)/(b+c)`.  After clearing positive denominators, the numerator is coefficientwise nonnegative in `X,H,D,E`:

```text
terms = 855,
minimum coefficient = 1/8.
```

This certifies only the top face of the `V>=X, q>=V` chamber; the open interior still needs a secant/remainder certificate or a finer chamber split.

## U1 A S4 High Chamber: V >= X, V <= q <= t

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_a_vge_x_qge_v_chamber.py` certifies the remaining high chamber of the broad residual family

```text
y=1, u=1, s4=0, a=1.
```

Use

```text
x = 1+X,  v = 1+V,  V = X+H,
J = M3-2V = X(V+2),
q = c-1 = V + S*J/2,          0 <= S <= 1,
t = b+c-2 = q + R*(1-S)*J,    0 <= R <= 1.
```

The proof keeps `J` symbolic through the Bernstein conversion and then substitutes the true relation `J=X(X+H+2)` coefficientwise. With `W=t-q`, the feasible region splits into:

```text
segment: e=1+q+U*W, d=1+W-U*W+G, 0<=U<=1, G>=0,
ray:     e=1+t+E,   d=1+D.
```

Exact checks:

```text
segment boundary: 127 Bernstein coefficients, 13849 terms, minimum coefficient 1/105.
ray full numerator: 49 Bernstein coefficients, 40089 terms, minimum coefficient 1/80.
segment d-slack derivative G^0: 166 Bernstein coefficients, 22850 terms, minimum coefficient 1/210.
segment d-slack derivative G^1: 121 Bernstein coefficients, 13527 terms, minimum coefficient 1/35.
segment d-slack derivative G^2: 74 Bernstein coefficients, 6528 terms, minimum coefficient 1/15.
segment d-slack derivative G^3: 39 Bernstein coefficients, 2625 terms, minimum coefficient 1/20.
```

Together with the low chamber `X <= t <= V`, the middle chamber `q <= V <= t`, and the top face check, this completes the broad `U1_A_S4` chamber package used by the classifier.

After adding `U1_A_S4` to `problems/23/writeup/_codex_sib_s7_y1_u1_family_closure_count.py`, the exact count is:

```text
U1-FAMILY-CLOSURE closes_to_custom_family=2088 closes_to_observed_basis=2712 still_unobserved=15352
U1-FAMILY-CLOSURE-CUSTOM U1_ABDF_CAP=282 U1_ABD_S4=205 U1_ABF_S4=190 U1_AB_S4=245 U1_AC_S4=299 U1_AD_S4=544 U1_AF_S4=156 U1_A_S4=167
U1-FAMILY-CLOSURE-STILL-UNIQUE=10437
U1-FAMILY-CLOSURE-CAP cap=s4 contradiction=0 closes_to_observed_basis=629 closes_to_custom_family=1875 still_unobserved=2448
U1-FAMILY-CLOSURE-CAP cap=s5 contradiction=0 closes_to_observed_basis=728 closes_to_custom_family=65 still_unobserved=4262
U1-FAMILY-CLOSURE-CAP cap=s6 contradiction=0 closes_to_observed_basis=707 closes_to_custom_family=65 still_unobserved=4323
U1-FAMILY-CLOSURE-CAP cap=s7 contradiction=0 closes_to_observed_basis=648 closes_to_custom_family=83 still_unobserved=4319
```

The post-custom profiler now passes with

```text
U1-POST-CUSTOM-SHAPES unique_still=10437
```

## U1 C S4 Broad Family

`problems/23/writeup/_codex_sib_s7_y1_u1_s4_c_family.py` certifies the broad residual family

```text
y=1, u=1, s4=0, c=1.
```

With

```text
m = x(1+v)+v,
b = x+s,
a = 1+A,
A = Q*(s_max-s),
f = (m-1-A)/(b+1),
s_max = xv+v-2,
```

the equation `s4=0` is identically `a+f(b+1)=m`, and the built-in bounds give `a>=1`, `f>=1`, `b>=x`. The remaining feasibility constraints reduce to

```text
e >= v,
d+e >= b+1.
```

The script splits by `x>=v` and `v>=x`; in the `v>=x` side it further splits at `s=v-x`. Exact Bernstein checks:

```text
x>=v segment: 102 Bernstein coefficients, 14081 terms, minimum coefficient 2.
x>=v ray: 30 Bernstein coefficients, 10650 terms, minimum coefficient 2.
v>=x low: 32 Bernstein coefficients, 7416 terms, minimum coefficient 2.
v>=x high segment: 90 Bernstein coefficients, 13089 terms, minimum coefficient 2.
v>=x high ray: 30 Bernstein coefficients, 10655 terms, minimum coefficient 2.
```

After adding `U1_C_S4` to the classifier, the exact count is:

```text
U1-FAMILY-CLOSURE closes_to_custom_family=3123 closes_to_observed_basis=2712 still_unobserved=14317
U1-FAMILY-CLOSURE-CUSTOM U1_ABDF_CAP=282 U1_ABD_S4=205 U1_ABF_S4=190 U1_AB_S4=245 U1_AC_S4=299 U1_AD_S4=544 U1_AF_S4=156 U1_A_S4=167 U1_C_S4=1035
U1-FAMILY-CLOSURE-STILL-UNIQUE=9819
U1-FAMILY-CLOSURE-CAP cap=s4 contradiction=0 closes_to_observed_basis=629 closes_to_custom_family=2910 still_unobserved=1413
U1-FAMILY-CLOSURE-CAP cap=s5 contradiction=0 closes_to_observed_basis=728 closes_to_custom_family=65 still_unobserved=4262
U1-FAMILY-CLOSURE-CAP cap=s6 contradiction=0 closes_to_observed_basis=707 closes_to_custom_family=65 still_unobserved=4323
U1-FAMILY-CLOSURE-CAP cap=s7 contradiction=0 closes_to_observed_basis=648 closes_to_custom_family=83 still_unobserved=4319
```

The post-custom profiler now passes with

```text
U1-POST-CUSTOM-SHAPES unique_still=9819
```

The next top lower-pattern residuals are now `u1`, `b1,u1`, `d1,u1`, and `f1,u1`.
