# Structural-induction report: rooted support order

Date: 2026-07-12

## Verdict

There is a valid structural compression, but no support-only induction step.

1. A fully quantified degree-partition lemma gives

   ```text
   2t^2 - 2t - 1 <= |R| (|L| - 3).
   ```

   For the two-owner `t=6` rooted support this raises the lower support order
   from 17 to 19.

2. For `t=5`, the order-15 count and corrected order-16 counts prove

   ```text
   |V(F*)| >= 17.
   ```

   After `left>=9`, `right>=6`, and the existing upper order 21, the rooted
   split catalogue is therefore the 25 bins

   ```text
   n=17,...,21,   left=9,...,n-6.
   ```

   This replaces the 28-bin range left after the two shore bounds and removes
   all order-15/16 LRAT obligations once the structural projection is connected
   to production.

3. The natural induction measure is explicit below. Its universal support-only
   descent lemma is false: the exact connected `(9,8)` order-17 positive control
   is a minimum-order rooted support object. Any valid descent must use more
   than rooted support and distance-four counts.

4. This does not construct the remaining production/rooting provider. The
   current kernel deliberately asks for order-15/16 pair projections; it does
   not yet derive them from `RootedT5Circuit`.

## Definitions

Let `H=(L,R;E)` be a finite simple bipartite graph. For a vertex `z`, write
`N(z)` for its neighborhood and `d(z)=|N(z)|`. Let `D4_L(H)` and `D4_R(H)` be
the unordered same-shore vertex pairs at support distance exactly four.

The rooted data used below are distinct vertices `v,m,a,b in L` and a set
`W subset L \ {v,m,a,b}`. In the production application:

- `v,m` are the two displayed owners;
- `a-x-v-y-b` is the rooted bad-atom row;
- `W` consists of `t` distinct bad neighbors of `v`;
- `|E|=t^2-1`, `d(v)=d(m)=t`;
- triangle-freeness gives `N(v) cap N(w)=empty` for `w in W` and
  `N(a) cap N(b)=empty`.

## Fully quantified reduction lemma

Assume `t>=1`.

**Lemma (rooted support quadratic bound).** For every natural number `t`, every
finite simple bipartite graph `H=(L,R;E)`, every four distinct vertices
`v,m,a,b in L`, and every `W subset L \ {v,m,a,b}`, if

```text
|W| = t,
d(v) = d(m) = t,
forall w in W, N(w) cap N(v) = empty,
N(a) cap N(b) = empty,
|E| = t^2 - 1,
```

then, writing `l=|L|` and `r=|R|`,

```text
2t^2 - 2t - 1 <= r(l-3).                         (1)
```

All arithmetic may be read in `Int`; the hypotheses imply `l>=t+4`, so no
truncated-subtraction issue occurs.

### Proof

Partition the left shore as

```text
{v,m} disjoint_union W disjoint_union {a,b} disjoint_union X,
|X| = l-t-4.
```

Because `|N(v)|=t` and every `N(w)` avoids `N(v)`,

```text
sum_(w in W) d(w) <= t(r-t).
```

The disjointness of `N(a),N(b)` gives `d(a)+d(b)<=r`, while every vertex of
`X` has degree at most `r`. Summing degrees on `L`,

```text
t^2-1 = |E|
        <= 2t + t(r-t) + r + (l-t-4)r
         = lr - 3r - t^2 + 2t.
```

Rearrangement is (1). This proof uses no circuit deletion, matching, Hall,
Schur, switch, or maximum-cut inequality.

A split-free consequence is

```text
(|L|+|R|-3)^2 >= 4(2t^2-2t-1),                  (2)
```

because `4r(l-3) <= (r+l-3)^2`.

For `t=5`, (1) has left side 39 and excludes `(l,r)=(9,6)`, since
`6(9-3)=36`. For `t=6`, its left side is 59. Every allowed split of order at
most 18 has `r(l-3)<=56`, so the two-owner `t=6` support order is at least 19.

## The two order-16 t=5 splits

Distinctness of database atom keys means that 25 atoms require at least 25
same-shore distance-four endpoint pairs. Thus it suffices to prove

```text
|D4_L(H)| + |D4_R(H)| <= 24.                    (3)
```

### Split `(left,right)=(10,6)`

Let `U` be the six left vertices outside `{v,m,a,b}`. The sets `V4,M4 subset
U` of distance-four neighbors of `v,m` each have size at least five. Since
`R\N(v)` and `R\N(m)` are singletons and `|V4 cap M4|>=4`, those singletons
are the same `{r}`. Put `U0=V4 union M4`, `k=|U0| in {5,6}`. Every vertex of
`U0` is a leaf with neighborhood `{r}`. Put

```text
Q = L \ ({v,m} union U0),   q=|Q|=8-k.
```

At least one vertex of `Q` is a bridge adjacent to `r` and to
`S=N(v)=N(m)=R\{r}`; otherwise a leaf in `U0` has no length-four path to an
owner.

If `k=6`, then `q=2` and

```text
|D4_L| <= 2k + k(q-1) + C(q,2) = 19,
|D4_R| <= 4,
```

so the total is at most 23. (The degree sum also gives the quicker
`d(a)+d(b)=8>6` contradiction.)

If `k=5`, then `V4=M4=U0`; the exceptional `c in U` is not distance four from
either owner, and `Q={a,b,c}`. Let `h` be the number of nonbridge vertices
`z in Q` with `r notin N(z)` whose `S`-neighborhood meets the `S`-neighborhood
of a bridge. Exactly these vertices can be distance four from a leaf. Hence

```text
|D4_L| <= 10 + 5h + (3-h) = 13+4h,
|D4_R| <= 4.
```

If `h<=1`, the total is at most 21. If `h=2`, there is one bridge. When
`|D4_R|<=3`, the total is at most 24. Equality `|D4_R|=4` forces the bridge to
have a singleton `S`-neighborhood `{s}`; both nonbridges then contain `s`, so
all three pairs inside `Q` have distance two. Consequently
`|D4_L|<=10+10=20`, and the total is again at most 24. This proves (3).

An exact finite gate over the reduced labeled neighborhood cases found 900
valid supports in the `k=5` branch and maximum pair count 23; the proof above
uses the conservative bound 24.

### Split `(left,right)=(9,7)`: corrected proof

There are exactly five non-root left vertices `W`. The mandatory rooted edges
make `m,a,b` distance two from `v`, and `v,a,b` distance two from `m`; hence
all five vertices of `W` are distance four from both owners. Put

```text
C_v=R\N(v),  C_m=R\N(m),  |C_v|=|C_m|=2.
```

Every `w in W` has a nonempty neighborhood contained in `C_v cap C_m`. If the
intersection is a singleton, then `sum_W d(w)=5`, and the edge count gives
`d(a)+d(b)=9>7`, contradicting `N(a) cap N(b)=empty`. Therefore
`C_v=C_m=C={r,s}` and `N(v)=N(m)=S=R\C`.

Write the five `W` neighborhoods as

```text
p copies of {r}, q copies of {s}, h copies of {r,s},
p+q+h=5.
```

The edge count gives `d(a)+d(b)=9-h<=7`, so `h>=2` and `p+q<=3`.

Let `A_C=N(a) cap C`, `B_C=N(b) cap C`, and similarly define `A_S,B_S`.
The endpoint neighborhoods are disjoint. Set

```text
P = |A_C||A_S| + |B_C||B_S|.
```

Among right-shore pairs, all pairs in `S` have distance two through an owner,
and `{r,s}` has distance two through any doubleton `W` vertex. Each of the `P`
endpoint products is also a distance-two `C-S` pair. Therefore

```text
|D4_R| <= 10-P.                                  (4)
```

On the left, the ten owner-`W` pairs and `ab` account for 11 possible
distance-four pairs. A `W-W` distance-four pair must be an `r`-singleton
paired with an `s`-singleton, so there are at most `pq`. Classifying the
middle left vertex of a four-path shows that a `W`-endpoint pair is distance
four only when the `W` vertex is a singleton and the endpoint contains the
opposite member of `C`; let their number be `X`. Thus

```text
|D4_L| <= 11+pq+X.                                (5)
```

It remains to show `pq+X<=P`.

At least one endpoint is incident with `C`: a length-four owner-`W` path has
the form `owner-S-endpoint-C-W`, since owners have no `C` neighbor and `W`
vertices have no `S` neighbor. Thus the following cases are exhaustive.

- If only one member of `C` occurs at the endpoints, no singleton at the
  other member can have distance four from an owner. Thus `pq=X=0`.
- If both members of `C` occur at one endpoint, then `X=0`, `P>=2`, and
  `pq<=2` because `p+q<=3`.
- If the two members of `C` occur at different endpoints, then `X=p+q=5-h`.
  The edge count gives
  `P=|A_S|+|B_S|=7-h=X+2`, while again `pq<=2`.

In every case `pq+X<=P`. Adding (4) and (5) gives the stronger bound

```text
|D4_L|+|D4_R| <= 21.
```

An exact finite gate over the `3^5` possible `W` types and disjoint endpoint
neighborhoods found 5,308 valid reduced labeled supports; the maximum was 21.

## Exact falsifier to one proposed subclaim

The assertion "no `w in W` can be distance four from `a`" is false and must
not be used in the `(9,7)` proof. Here is an exact 24-edge connected support.
Label the left shore `v=0,m=1,a=2,b=3,w0=4,...,w4=8` and the right shore
`0,...,6`, with neighborhoods

```text
N(v)=N(m)={0,1,2,3,4}
N(a)={0,2,3,4,5}
N(b)={1,6}
N(w0)=N(w1)={5}
N(w2)={6}
N(w3)=N(w4)={5,6}.
```

All five `W` vertices are distance four from both owners, `d(a,b)=4`, and the
rooted edge count is 24. Nevertheless

```text
w2 - 6 - w3 - 5 - a
```

is a length-four shortest path. Direct exact distance enumeration gives

```text
|D4_L|=16, |D4_R|=5, total=21.
```

Thus this graph falsifies only that intermediate subclaim, not the corrected
order-16 closure.

## Explicit induction measure and its obstruction

For fixed `t`, use the well-founded natural-number measure

```text
mu_t(H) = |L(H)|+|R(H)|-(2t+5).
```

The rooted shore bounds make this a natural number. For `t=5`, the arguments
above close `mu=0` (order 15) and `mu=1` (order 16).

The support-only induction step

```text
forall H in S_5,
  mu_5(H)>=2 -> exists H' in S_5, mu_5(H')<mu_5(H)              (6)
```

is false, where `S_5` is the class of connected bipartite 24-edge rooted
supports with the six mandatory root edges, both owner degrees five, at least
five distance-four neighbors at each owner, rooted pair `d(a,b)=4`, and at
least 25 same-shore distance-four pairs.

The exact falsifier is
`tmp/fanout/r51_independent_t5_verifier/n17_l9_r8_connected_control.json`,
canonical SHA256
`17f91f2a2ee764cd58adf713ad1287f450c4942ba8c75f97d1927a96318911ce`.
Its neighborhoods are

```text
N(v)=N(m)={0,1,2,3,5}
N(a)={0,6}
N(b)={1,3,4}
N(u4)={4,7}
N(u5)={4,6}
N(u6)={6}
N(u7)=N(u8)={6,7}.
```

It is connected, has 24 edges, owner degrees `(5,5)`, owner distance-four
counts `(5,5)`, and 26 same-shore distance-four pairs. Thus `mu_5=2`. Any
smaller member of `S_5` would have order 15 or 16 after the shore bounds, but
both orders were just excluded. Hence no `H'` in (6) exists.

This is only a support-level falsifier. It does not carry a triangle-free
25-atom minimal transversal circuit, a live profile, or a production maximum-
cut extension. A descent theorem using one of those additional structures is
not refuted. What is refuted is an induction step based only on rooted support
order and distance-four counts.

## Exact use of graph hypotheses

**Triangle-freeness.** The degree and pair counts are purely bipartite once
the no-common-neighbor statements and atom pair cover are supplied.
Triangle-freeness is used in the production lift at exactly these points:

1. if a selected bad pair `xy` shared a blue/support neighbor `z`, then
   `xyz` would be a triangle; hence `N(x) cap N(y)=empty`;
2. together with a checked five-vertex blue row, this places each distinct bad
   atom endpoint pair in the support distance-four pair cover.

This supplies the disjointness for `v-W` and `a-b` and the lower bound of 25
distinct covered pairs. No Mantel bound and no triangle-freeness of an
auxiliary distance-four graph is used.

**Maximum-cut.** It is not used. Support bipartiteness follows from the two cut
shores and the fact that support edges are blue; maximality of the cut plays no
role in (1), in either order-16 count, or in the induction falsifier. Maximum-
cut is needed later for ambient extension/switch exclusion, not for this range
reduction.

## Production-provider boundary

The reduction does not yet remove the real-provider theorem. The current APIs
leave the following exact gaps:

1. `RootedT5Circuit` has a 24-edge `support`, but does not state that it equals
   `BalancedRotor.completeRowSupport bads`, nor that every atom has a complete
   four-edge row contained in this support.
2. `RootedT5Circuit` does not carry `TriangleFree graph`; triangle-freeness is
   present on `CheckedBalancedDeficiencyRotor` and must be transported by the
   rooting adapter.
3. `RootedT5OwnerShoreData` exposes one owner's five distance-four neighbors.
   The order-16 proofs also need the displayed partner's degree five and five
   distance-four neighbors in the same fixed support.
4. The root data must expose that `endpointA,endpointB` are the endpoints of a
   database bad atom, not only that they share the displayed blue row geometry.
5. The current `RootedT5Order15PairProjection` and
   `RootedT5Order16PairProjection` are therefore honest conditional endpoints:
   their `cover_card_le` fields are not constructed by the kernel.

A sufficient provider output is: equality with complete row support,
triangle-freeness, the second-owner neighborhood projection, the rooted `ab`
atom, and the finite pair cover consisting of all same-shore support-distance-
four pairs. With those fields, the arguments above construct the order-15/16
projections and remove those catalogue bins without LRAT.

## Upper support-order bridge

Let `F` be a finite connected simple graph with 24 edges, let `v` have degree
five, and let its five distinct neighbors be `x0,...,x4`. Assume that, for
each `i=1,...,4`, there is an `x0`-to-`xi` path in `F-v`. Then

```text
|V(F)| <= 21.                                             (7)
```

Indeed, every component of `F-v` contains a neighbor of `v`: take a path in
`F` from a vertex of the component to `v` and inspect its last edge. The four
supplied paths put all five neighbors in one component, so `F-v` is connected.
It has `|V(F)|-1` vertices and `24-5=19` edges. A connected graph on
`|V(F)|-1` vertices has at least `|V(F)|-2` edges, hence
`|V(F)|-2<=19` and (7) follows.

The minimal data-facing signature can avoid an ordered five-tuple. For a
24-edge support `support` and owner `v`, it is enough to expose

```text
ownerNeighbors : Finset Nat
ownerNeighbors_card : ownerNeighbors.card = 5
ownerNeighbors_exact :
  z in ownerNeighbors <-> normEdge v z in support
anchor : Nat
anchor_mem : anchor in ownerNeighbors
neighbor_path_avoiding_owner :
  forall z in ownerNeighbors,
    exists path,
      SupportPath support anchor z path and v notin path
```

together with the existing support connectivity and `support.card=24`. The
corresponding conclusion should be

```text
supportOrder_le_twentyOne :
  (supportVertices support).card <= 21.
```

It should not conclude `graph.n<=21` unless the rooting adapter separately
proves that every ambient graph vertex lies in `supportVertices support`.

### Why the current API does not compile this theorem directly

The required projection is absent, and the M3/M6 support notions do not yet
coincide.

1. M3's active edge `owner-activeNbr` is absent from the current
   `selectedSupport omega`, but `OwnerSupportTriple.edge0_mem` places it in
   `BalancedRotor.completeRowSupport bads`. Thus the graph `F` in (7) must be
   the complete 24-edge row support, not the current selected support.
2. M3 supplies only three explicit owner-incident complete-support edges.
   `blue_degree=5` and `every_other_blue_edge_supported` do not package the
   five-neighbor Finset or identify its incident edges with one fixed `F`.
3. `every_active_support_pair_covered` gives only
   `0<pairCount omega activeNbr z`. This produces a selected row containing
   both vertices, but neither `pairCount` nor `checkRow5` says that the row
   avoids the owner. `checkRow5` checks five distinct vertices and four blue
   consecutive steps; it does not ban nonconsecutive blue chords. Therefore
   `active_edge_off_support` alone cannot prove owner avoidance.
4. M3 has no connectedness field for `completeRowSupport bads`. M6 has
   connectedness for `RootedT5Circuit.support`, but its `activeNbr` edge is
   explicitly off that support and it carries no four coverage paths.
5. M6's support order is `(supportVertices support).card`; equality with
   `circuit.graph.n` is not a field.

Therefore the minimal missing production bridge is a projection from one
fully covered profile to the fixed complete support carrying: equality with
the rooted 24-edge support, connectedness, the exact five-neighbor Finset, and
four explicit owner-avoiding support paths from the active neighbor. Once that
projection exists, (7) is graph-theoretic and uses neither triangle-freeness
nor maximum-cut.

Combining (7) with `left>=9`, `right>=6` gives the rigorous pre-exclusion
range `15<=supportOrder<=21`, hence 28 splits. The order-15/16 arguments above
then leave exactly the 25 splits of orders 17 through 21.
