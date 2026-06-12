# Erdos #23: deletion escape profiles for `a(30)=36`

Date: 2026-06-11

Local tool:

`E:\Projects\ErdosProblems\search23\deletion_escape_profiles.cpp`

This is not a graph search.  It is an arithmetic audit of the deletion routes
from a hypothetical 30-vertex triangle-free graph with `beta >= 37`.

## Root-min-degree correction

The first version allowed impossible tail degrees such as `0` after deleting a
minimum-degree root.  The corrected version uses the elementary invariant:

if the original graph has minimum degree at least `r`, then after `t` vertex
deletions every remaining vertex has current degree at least `r-t`.

The output therefore records only rooted profiles consistent with this lower
bound.

## Five deletions to `a(25)=25`

To invoke the verified result `a(25)=25`, one needs cumulative loss

`sum floor(d_i/2) <= 11`.

The corrected rooted arithmetic still has many escape profiles.  The most
frequent include:

- `7,6,6,4,6` with loss `14`, witness `(r,e)=(7,139)`;
- `6,6,4,4,6` with loss `13`, witness `(r,e)=(6,139)`;
- `7,6,6,4,4` with loss `13`, witness `(r,e)=(7,139)`;
- `6,6,4,4,4` with loss `12`, witness `(r,e)=(6,139)`;
- `8,7,6,6,4` with loss `15`, witness `(r,e)=(8,139)`.

Conclusion: even after using the root-min-degree lower bound, average-degree
arithmetic cannot force a five-vertex deletion loss `<=11`.

## Seven deletions to McKay `a(23)=20`

The stronger catalogue route would close if after seven deletions either:

- loss `L <= 16`, or
- loss `L <= 17` and the remaining edge count is at most `99`, because all
  McKay `n=23`, `beta=20` extremals have at least `100` edges.

The corrected rooted arithmetic still has broad escape families.  The most
frequent include:

- `8,7,6,6,4,4,2`, loss `18`, witness `(r,e,e23)=(8,139,102)`;
- `7,6,6,6,6,6,6`, loss `21`, witness `(r,e,e23)=(7,126,83)`;
- `7,6,6,4,6,6,6`, loss `20`, witness `(r,e,e23)=(7,126,85)`;
- `8,8,6,6,4,4,6`, loss `21`, witness `(r,e,e23)=(8,139,97)`;
- `6,6,4,4,2,6,8`, loss `18`, witness `(r,e,e23)=(6,139,103)`.

Conclusion: the seven-deletion McKay route is not closed by degree arithmetic.
It needs a lemma that uses the high `beta` condition itself, not only
triangle-free + edge count + minimum-degree evolution.

## Structural target extracted

A useful next lemma would be one of:

1. **Low-loss deletion lemma.**  
   Every triangle-free 30-vertex graph with `109 <= e <= 139` and `beta >= 37`
   has a five-vertex deletion sequence with loss `<=11`, or a seven-vertex
   deletion sequence satisfying the McKay condition above.

2. **Profile exclusion lemma.**  
   Under `beta >= 37`, none of the high-frequency escape profiles above can be
   the greedy minimum-degree evolution of a rooted counterexample.

3. **Stability lemma.**  
   A triangle-free 30-vertex graph in the hard medium-density window with
   `beta >= 37` must be close enough to a `C5`-blow-up or another structured
   family that the integer part sizes force `beta <= 36`.

The profile data suggests that (1) cannot be proved by soft degree arithmetic
alone.  A proof must exploit max-cut structure, e.g. bad-cut certificates,
local improvement inequalities, or a medium-density stability theorem.
