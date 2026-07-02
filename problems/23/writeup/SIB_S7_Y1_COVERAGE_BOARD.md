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
