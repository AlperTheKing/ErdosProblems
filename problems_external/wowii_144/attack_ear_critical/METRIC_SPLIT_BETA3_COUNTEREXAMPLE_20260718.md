# W144-MET3 exact counterexample and surviving route

Date: 2026-07-18.

## Result

The corrected metric split restricted to cycle rank at least three is false.
The exact graph6 record

```text
NhCGGE@?O?_@O@G???g
```

is a simple 2-connected graph with

```text
n=15, m=17, beta=3, girth=6,
diameter=5, Delta=3, radius=4,
C(G)={0,1}, eta(G)=4.
```

Therefore

```text
max{Delta,diameter-floor(girth/2)}=max{3,5-3}=3<4=eta.
```

This graph is not a counterexample to W144.  Its exact maximum induced-tree
order is 13, whereas the W144 target is only `6-1+4=9`.

## Construction and hand audit

The edge set is the union of the 9-cycle

```text
0-1-2-3-4-5-6-7-8-0,
```

the ear `1-12-11-10-9-7`, and the ear `2-13-14-11`.  Adding two open ears
to a cycle proves 2-connectivity and gives cycle rank three.  The seven simple
cycles have lengths

```text
6, 8, 9, 10, 11, 11, 13,
```

so the girth is six.  Direct all-pairs distances give eccentricity four for
vertices 0 and 1 and eccentricity five for every other vertex.  Hence the
center is exactly `{0,1}`.  Vertex 5 is the unique vertex at distance four
from this center, so `eta=4`; all vertex pairs are at distance at most five.

Deleting vertices 8 and 11 leaves the 13-vertex set

```text
{0,1,2,3,4,5,6,7,9,10,12,13,14},
```

whose induced graph is a tree.  Conversely every one-vertex deletion remains
connected and cyclic, so no induced tree has order 14.  Thus `tree(G)=13`.

## What survives

The eta-nondecreasing deletion route survives strongly.  The exact set of
vertices `v` with connected cyclic `G-v` and `eta(G-v)>=eta(G)` is

```text
{2,4,6,7,10,11}.
```

In particular, deleting vertex 2 produces a connected unicyclic graph with

```text
girth(G-2)=8, radius(G-2)=5, eta(G-2)=4.
```

Thus `girth+eta` rises from 10 to 12, and the already proved unicyclic theorem
closes W144 for this graph.  The larger parameter-nondecreasing deletion set
for `girth+eta` is `{1,2,4,6,7,10,11,13,14}`.  Hence this counterexample kills
W144-MET3 but supplies no obstruction to W144-IND2 or W144-2DEL.

## Reproduction

Run

```text
python problems_external/wowii_144/attack_ear_critical/verify_metric_split_beta3_counterexample.py
```

The verifier reconstructs the graph from graph6, checks the adjacency list,
all invariants, exhaustively computes the induced-tree number, and checks
every one-vertex deletion.
