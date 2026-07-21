# W144-MET exact counterexample

Date: 2026-07-18.

## Disposition

The proposed 2-connected metric split

```text
eta(G) <= max{Delta(G), diam(G)-floor(girth(G)/2)}
```

is false.  A 15-vertex counterexample is `Theta(1,7,8)`.  Its graph6 record
in the labeling below is

```text
NpCGIE??G?_@?@??g?G
```

This does not contradict the completed exact audit through order 13.

## Construction

Let `A=0`, `B=1`, and take three internally disjoint `A`--`B` paths

```text
0-1,
0-2-3-4-5-6-7-1,
0-8-9-10-11-12-13-14-1.
```

Their lengths are `1,7,8`.  Since only one branch has length one, this theta
graph is simple; three internally disjoint branches make it 2-connected.

## Hand verification

Every cycle is the union of two of the three branches, so the cycle lengths
are `8,9,15`; hence the girth is `g=8`.  Only `A` and `B` have degree three,
and all other vertices have degree two, so `Delta=3`.

Write `p_i` and `q_i` for the vertices at position `i` on the length-seven
and length-eight branches.  Direct distance calculation gives
`ecc(A)=ecc(B)=4`, while every internal branch vertex has eccentricity at
least five.  Thus

```text
C(G)={A,B},  rad(G)=4.
```

For a branch of length `L`, the vertex at position `i` has distance
`min{i,L-i}` from `{A,B}`.  The unique midpoint `q_4=11` of the length-eight
branch is therefore distance four from the center and

```text
eta(G)=4.
```

For vertices at positions `i` and `j` on the two nontrivial branches, the
routes through `A` and `B` have lengths `i+j` and `15-i-j`; one is at most
seven.  Pairs on one branch are also at distance at most seven.  The vertices
`4` and `11` have distance seven, so `diam(G)=7`.

Consequently

```text
max{Delta,diam-floor(g/2)} = max{3,7-4} = 3 < 4 = eta.
```

Thus the implication `eta>Delta => diam>=eta+floor(g/2)` fails as well:
here `4>3`, but `7<4+4`.

## Independent reproduction

From the repository root run

```text
python problems_external/wowii_144/attack_ear_critical/verify_metric_split_counterexample.py
```

The verifier constructs the graph from the three paths, checks simplicity,
2-connectivity, the graph6 record, and all displayed invariants independently.
The counterexample kills only W144-MET; it is not a counterexample to W144.