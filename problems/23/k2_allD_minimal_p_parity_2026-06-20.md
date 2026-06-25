# K2 all-D low-p parity lemma

Date: 2026-06-20.

This note is a local hand certificate for the `K=2,T=2` exact-two-root
state-count quotient in the all-doubleton support family.

## Setting

Assume:

- `R` has only doubleton labels `D={1,2}`;
- the `R`-skeleton is empty;
- all A/B states are subsets of `R`;
- `A_I` and `B_J` count A- and B-vertices with state `I,J`;
- an A-B edge occurs exactly when `I cap J = empty`;
- an intersection of size one is forbidden;
- every A-vertex has at least two B-neighbours and every B-vertex has at
  least two A-neighbours, by root-opposite nonedge-codegree;
- for every `r notin J`, a B-vertex of state `J` and the R-vertex `r` have at
  least two common neighbours in A.  Symmetrically for A/R.

No H14 anti-tightness, terminal-touch equality, or terminal-degree equality is
used.

## Minimal-p lemma

If `p=2|B|`, then `|A|` is even.

Symmetrically, if `p=2|A|`, then `|B|` is even.

## Proof

Assume `p=2|B|`.  Since every B-vertex has at least two A-neighbours, every
B-vertex has exactly two A-neighbours.  Hence for every used B-state `J`,

```
d_A(J) = sum_{I cap J = empty} A_I = 2.
```

Fix a used B-state `J`.  Let `r in R \ J`.  Since R has no edges and all labels
are doubletons, the only possible common neighbours of a B-vertex of state `J`
and the R-vertex `r` are A-vertices adjacent to that B-vertex whose states
contain `r`.  The B/R nonedge-codegree condition therefore says that, for each
`r notin J`, both of the two A-neighbours of this B-vertex contain `r`.

Each A-neighbour state is disjoint from `J`, because it is joined to `J` by an
A-B edge.  Thus the two A-neighbour states must contain all of `R \ J` and none
of `J`, so both states are exactly the complement `R \ J`.  Therefore

```
A_{R\J} = 2
```

for every used B-state `J`, and there are no other A-states adjacent to `J`.

Every A-vertex must have at least two B-neighbours.  Hence every A-copy must be
adjacent to some used B-state, and so every A-copy lies in one of the complement
classes `R\J` above.  These classes each have multiplicity exactly `2`, so
`|A|` is a sum of twos and is even.

The symmetric statement follows by exchanging A and B.

## One-excess lemma

If `p=2|B|+1`, then `|A|` is even.

Symmetrically, if `p=2|A|+1`, then `|B|` is even.

## Proof

Assume `p=2|B|+1`.  Since every B-vertex has at least two A-neighbours,
the total B-side excess

```
sum_J B_J (d_A(J)-2)
```

is exactly `1`.  Hence there is a unique used B-state `J*` with

```
B_{J*}=1, d_A(J*)=3,
```

and every other used B-state `J` satisfies `d_A(J)=2`.

For every used `J != J*`, the same B/R codegree argument as in the
minimal-p lemma gives

```
A_{R\J} = 2,
```

and no other A-state is adjacent to `J`.

Now take any A-copy not lying in one of these forced complement classes.
It cannot be adjacent to any used B-state `J != J*`, so its only possible
B-neighbours lie in the single exceptional B-copy of state `J*`.  Thus it
has at most one B-neighbour, contradicting the root-opposite lower bound
that every A-vertex has at least two B-neighbours.

Therefore every A-copy lies in one of the forced complement classes, all of
which have multiplicity exactly `2`.  Thus `|A|` is even.  The symmetric
statement follows by exchanging A and B.

## Application

In the `q=8` all-doubleton side choice

```
|A| = 7, |B| = 11
```

the root-opposite lower bound is `p >= 2|B| = 22`.  Therefore the whole `p=22`
slice is impossible by the minimal-p lemma, and the whole `p=23` slice is
impossible by the one-excess lemma, because either value would force `|A|` to
be even.  The first application closes the rows

```
(p,M) = (22,81), (22,82), (22,83)
```

that were not closed by the generic state-count runs.  The second application
closes all `p=23` rows in the same side choice.
