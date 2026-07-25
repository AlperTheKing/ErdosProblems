# Directed C4 obstruction to the certifying tournament-completion lemma

## Scope

This note refutes only the frontier lemma registered under `DIRECT ROUTE -
CERTIFYING TOURNAMENT COMPLETION`. It is not a counterexample to Seymour's
Second Neighborhood Conjecture: every vertex of the directed 4-cycle has one
out-neighbor and one new second out-neighbor.

A median order of a tournament is an ordering maximizing the number of forward
arcs, and its last vertex is a feed vertex. The tournament feed-vertex theorem
then supplies the second-neighborhood inequality in the completed tournament.
These conventions agree with Ghazal, arXiv:1509.03282.

## Canonical oriented graph

Let `D` have vertex set `{0,1,2,3}` and adjacency list

```text
0: 1
1: 2
2: 3
3: 0
```

Thus `D` is the directed cycle `0 -> 1 -> 2 -> 3 -> 0`; its only missing
unordered pairs are `{0,2}` and `{1,3}`.

The proposed frontier lemma asks for a tournament completion `T` and a feed
vertex `f` such that:

1. every `T`-out-neighbor of `f` is already a `D`-out-neighbor; and
2. every new second out-neighbor of `f` in `T` has a two-edge witness using
   only arcs of `D`.

## Forced completion for a candidate vertex

Take `f=0`. Condition 1 forces the missing edge incident with `0` to be
`2 -> 0`, because the sole `D`-out-neighbor of `0` is `1`.

If the other missing edge were `1 -> 3`, then `0 -> 1 -> 3` would make `3` a
new second out-neighbor in `T`. But the sole two-edge walk from `0` in `D` is
`0 -> 1 -> 2`, so `3` has no original witness. Condition 2 therefore forces
`3 -> 1`.

Hence the only completion compatible with candidate `f=0` is

```text
0: 1
1: 2
2: 0, 3
3: 0, 1
```

The same argument rotates modulo 4: for candidate `f`, the two missing chords
are forced as `f+2 -> f` and `f-1 -> f+1`.

## Candidate 0 is not a feed vertex

In the forced tournament `T0`, the vertices `{1,2,3}` induce the directed
3-cycle `1 -> 2 -> 3 -> 1`. Therefore an ordering ending in `0` has at most two
forward arcs inside `{1,2,3}`. Exactly two arcs from those vertices enter `0`,
namely `2 -> 0` and `3 -> 0`. Thus every ordering ending in `0` has at most
`2+2=4` forward arcs.

The ordering

```text
(2,3,0,1)
```

has five forward arcs: `2->3`, `2->0`, `3->0`, `3->1`, and `0->1`. Since `T0`
contains a directed triangle, it has no ordering with all six arcs forward, so
five is the tournament maximum. Consequently no median order of `T0` ends in
`0`; candidate `0` is not a feed vertex.

Indeed, the maximum forward-arc totals conditional on the terminal vertex are

```text
terminal 0: 4
terminal 1: 5
terminal 2: 4
terminal 3: 3
```

so the compatible completion for candidate `0` has feed vertex `1`. At that
feed vertex, `N_T^+(1)={2}` and `N_T^{++}(1)={0,3}`, whereas
`N_D^{++}(1)={3}`: target `0` is created by the added chord `2 -> 0`, exactly
violating condition 2.

Rotating gives the four pairs

```text
(candidate, forced-completion feed) = (0,1), (1,2), (2,3), (3,0).
```

Thus no vertex of `D` can be the required feed vertex in a compatible
tournament completion.

## Vertex minimality

For an oriented graph on at most three vertices, if there is a sink `f`, orient
all missing edges incident with `f` toward `f` and complete the other pairs
arbitrarily. The resulting tournament has sink `f`; moving `f` to the end
strictly increases the number of forward arcs in any ordering not already
ending there. Hence `f` is a feed vertex and both compatibility conditions are
vacuous.

If an oriented graph on at most three vertices has no sink, the only possible
case is a three-vertex directed tournament in which every outdegree is one,
namely the directed triangle. It is already complete, so `T=D` and both
conditions hold for every feed vertex. Therefore the directed 4-cycle is a
vertex-minimal obstruction.

## Conclusion

The certifying tournament-completion frontier lemma is false. The route exits
with

```text
DEAD: directed C4 forces the compatible candidate away from every feed vertex
```

This obstruction does not decide SSNC.

Reference: https://arxiv.org/abs/1509.03282

## Definitions and bridge audit

For a vertex `f`, the new second out-neighborhood is
`N_T^{++}(f)={y notin {f} union N_T^+(f): there exists x with f->x->y}`.
The Havet-Thomasse theorem states that the last vertex `f` of every median
order of a tournament satisfies `|N_T^{++}(f)| >= |N_T^+(f)|`.

The proposed compatibility conditions have the exact required bridge.
Completion gives `N_D^+(f) subseteq N_T^+(f)`, while condition 1 gives the
reverse inclusion, so the two first neighborhoods are equal. If `y` lies in
`N_T^{++}(f)`, condition 2 supplies a two-arc witness in `D`; because `y` is
not in `N_T^+(f)`, it is not in `N_D^+(f)`. Hence
`N_T^{++}(f) subseteq N_D^{++}(f)`.
