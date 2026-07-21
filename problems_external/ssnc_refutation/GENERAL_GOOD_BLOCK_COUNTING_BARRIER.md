# Countermodel to the global good-block counting bridge

Status: **THE PROPOSED COUNTING BRIDGE IS FALSIFIED**.

This note performs the single permitted counting action after the good-block
overlap lemma.  It gives an explicit parameter/root-incidence model satisfying
all exact scalar sums, source lower bounds, target capacity bounds, zero
diagonal, and good-block disjointness.  It is not an oriented graph and is not
an SSNC counterexample.

## Parameters

Take

\[
 n=19,\qquad \delta=8,\qquad k=3,\qquad q=19,
\]

and set `e_v=0` for every vertex.  Use the missing-degree multiset

\[
 (\mu_0,\ldots,\mu_{18})=(4,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1).
                                                               \tag{1}
\]

It is graphical: a 9-cycle on `0,...,8`, two leaves at vertex 0, and one
leaf at each of vertices `1,...,8` has exactly this degree sequence.

The exact totals are

\[
 E=b=0,\qquad \sum_v\mu_v=38=2q,\qquad
 T=38,\qquad s=19.                                  \tag{2}
\]

The global necessary inequality is saturated:

\[
 kb+2q=38=n+s.                                       \tag{3}
\]

Every source has the exact lower-bound incidence degree three.  Every target
uses the exact capacity

\[
 r_u=2t_u-1=2\mu_u-1,
\]

so the target-degree sequence is

\[
 (r_0,\ldots,r_{18})=(7,5,5,5,5,5,5,5,5,1,1,1,1,1,1,1,1,1,1).
                                                               \tag{4}
\]

Its sum is 57, equal to `3n`.  No target has `t_u=2`, so there are no good
blocks and the accepted disjointness lemma is satisfied vacuously.

## Explicit root incidence

The following target fibres have the degrees in (4), avoid their own target,
and give every source incidence degree exactly three:

```text
R_0  = {1,13,14,15,16,17,18}
R_1  = {0,9,12,17,18}
R_2  = {9,10,12,16,18}
R_3  = {6,8,10,12,16}
R_4  = {6,8,10,11,15}
R_5  = {6,8,9,11,15}
R_6  = {2,3,4,5,14}
R_7  = {2,3,4,5,11}
R_8  = {2,3,4,5,13}
R_9  = {13}
R_10 = {7}
R_11 = {7}
R_12 = {7}
R_13 = {14}
R_14 = {1}
R_15 = {1}
R_16 = {17}
R_17 = {0}
R_18 = {0}
```

The transposed source fibres are

```text
W_0  = {1,17,18}
W_1  = {0,14,15}
W_2  = {6,7,8}
W_3  = {6,7,8}
W_4  = {6,7,8}
W_5  = {6,7,8}
W_6  = {3,4,5}
W_7  = {10,11,12}
W_8  = {3,4,5}
W_9  = {1,2,5}
W_10 = {2,3,4}
W_11 = {4,5,7}
W_12 = {1,2,3}
W_13 = {0,8,9}
W_14 = {0,6,13}
W_15 = {0,4,5}
W_16 = {0,2,3}
W_17 = {0,1,16}
W_18 = {0,1,2}
```

Direct checks give

```text
sum(mu) = 38
sum(r) = 57
all |W_v| = 3
all v notin R_v
good targets = 0
```

For each target, the numerical strengthened packing inequality is also
saturated because `e_v=0` and

\[
 {2t_u-1\choose2}=(2t_u-1)(t_u-1).                  \tag{5}
\]

## Exact conclusion

The exact sums, source lower bounds, target capacities, and pairwise
disjointness of good blocks do not imply a global contradiction.  Any closing
argument must add structural information not present in this counting system,
such as compatibility of the larger saturated root blocks with common
orientation rows.  Pursuing such an additional hierarchy is outside this
single action.

