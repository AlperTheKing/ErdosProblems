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
