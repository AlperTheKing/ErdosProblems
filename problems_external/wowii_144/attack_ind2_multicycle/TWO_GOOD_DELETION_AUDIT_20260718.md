# W144 two-good-deletion audit

Date: 2026-07-18.

## 1. Exact statement and status

For a connected graph `X`, write

```text
C(X)   = {u : ecc_X(u)=rad(X)},
eta(X) = max_x d_X(x,C(X)),
beta(X)= |E(X)|-|V(X)|+1.
```

The proposed strengthening of the W144 deletion step is

```text
beta(G)>=2 and girth(G)>=5
 ==> at least two distinct v satisfy
     G-v connected and cyclic, and eta(G-v)>=eta(G).       (2DEL)
```

This note does **not** claim a proof of `(2DEL)`.  It proves the exact
radius/unique-eccentric consequences available for a bad deletion, closes
the 2-connected cycle-rank-two base with two distinct deletions, and gives
the first exact obstruction to completing the proof from those local
consequences alone.

The direct bridge to W144 is valid.  Given a prescribed vertex `x`, one of
the two deletions avoids `x`.  Iterating would give an induced connected
unicyclic subgraph containing `x`, with nondecreasing `eta` and nondecreasing
girth.  The proved unicyclic theorem would then give W144.

## 2. A radius drop is automatically eta-good

**Lemma 2.1.**  Let `H=G-v` be connected.  If

```text
rad(H)<rad(G),
```

then `eta(H)>=eta(G)`.

**Proof.**  Put `r'=rad(H)` and `r=rad(G)`.  For `c in C(H)`, every vertex of
`H` is within `r'` of `c`.  If `z` is a neighbor of `v`, then

```text
d_G(c,v) <= d_H(c,z)+1 <= r'+1.
```

Thus `ecc_G(c)<=r'+1`, so `r<=r'+1`.  The strict radius inequality gives
`r=r'+1`.  It also gives `C(H) subset C(G)`: each `c in C(H)` has
`ecc_G(c)<=r`, hence is central in `G`.

If an `eta(G)`-realizer `x` survives, then

```text
d_H(x,C(H)) >= d_G(x,C(H)) >= d_G(x,C(G))=eta(G),
```

and the result follows.  It remains to consider the case in which `v` is
the unique realizer.  Assume first `r>=2`.  For any `c in C(H)`, all vertices
of `H` are within `r-1` of `c`, while `ecc_G(c)=r`; hence
`d_G(c,v)=r`.  If `p` is the neighbor of `c` on a `c`--`v` geodesic, then

```text
d_G(p,y)<=1+d_H(c,y)<=r       for y in H,
d_G(p,v)=r-1.
```

Therefore `p in C(G)` and `d_G(v,C(G))<=r-1`.  On the other hand every
neighbor `z` of `v` satisfies, for every `c in C(H)`,

```text
r-1 <= d_G(c,z) <= d_H(c,z) <= r-1.
```

Consequently `d_H(z,C(H))=r-1`, and

```text
eta(H)>=r-1>=d_G(v,C(G))=eta(G).
```

If `r=1`, then `r'=0`, `H` is a single vertex, and the assertion is checked
directly.  QED.

This lemma is also implicit in the earlier bad-deletion center lemma: a bad
deletion with nonincreasing radius must in fact preserve the radius.

## 3. The exact local unique-eccentric obstruction

**Lemma 3.1.**  Let `H=G-v` be connected, let

```text
r=rad(G),  e=eta(G),  R={x:d_G(x,C(G))=e},
```

and suppose `rad(H)<=r` and `eta(H)<e`.  Then `rad(H)=r`.  Moreover, for
every `x in R-{v}` there is a vertex `u in C(H)-C(G)` such that

```text
d_H(x,u)<=e-1,
d_G(u,v)=r+1,
v is the unique eccentric vertex of u in G.                (3.1)
```

In particular,

```text
d_G(x,v)>=r-e+2                                             (3.2)
```

for every surviving realizer `x`.

**Proof.**  Lemma 2.1 excludes `rad(H)<r`, so `rad(H)=r`.  Since
`eta(H)<=e-1`, choose `u in C(H)` with `d_H(x,u)<=e-1`.  This `u` is not in
`C(G)`, since otherwise `d_G(x,C(G))<=e-1`.  Every surviving vertex is at
distance at most `r` from `u`, because `u` is central in `H`.  Since `u` is
not central in `G`, the deleted vertex is therefore its unique eccentric
vertex and is at distance `r+1`.  Finally,

```text
r+1=d_G(u,v)<=d_G(u,x)+d_G(x,v)<=e-1+d_G(x,v),
```

which is (3.2).  QED.

Thus any admissible deletion with a radius drop is good, and any admissible
radius-preserving vertex within distance `r-e+1` of a surviving realizer is
good.  These are genuine sufficient conditions, not a characterization.

For two distinct bad radius-preserving deletions `v,w`, the new-center sets
in (3.1) are disjoint: one vertex cannot have both `v` and `w` as its unique
eccentric vertex.  This recovers the strongest presently justified UEP
counting datum.

## 4. The 2-connected cycle-rank-two base has two deletions

The proved theta theorem identifies every 2-connected graph with `beta=2`
as `Theta(a,b,c)`, where `1<=a<=b<=c` and the girth condition is
`a+b>=5`.  In particular `b>=3`.  Write the middle path as

```text
A=v_0,v_1,...,v_b=B.
```

The theta theorem proves that deleting `v_1` leaves a connected unicyclic
tadpole and does not decrease `eta`.  Apply the identical theorem after
interchanging `A` and `B`.  It proves the same assertion for `v_(b-1)`.
The two vertices are distinct because `b>=3`.  Hence `(2DEL)` is proved for
the 2-connected `beta=2` base.

This does not prove the cut-vertex case or the `beta>=3` step.

## 5. Exact obstruction to the local completion

The graph

```text
J??CBBOi?{?
```

has

```text
n=11, m=13, beta=3, girth=5,
rad(G)=3, C(G)={0,8,9}, eta(G)=3, R={5}.
```

It has five eta-good admissible deletions,

```text
v in {3,4,6,8,9},
```

but **none** is certified by Lemmas 2.1 and 3.1: no admissible deletion has a
radius drop, and every radius-preserving candidate is farther than

```text
r-e+1=1
```

from the sole realizer `5`.  For example, deletions `3,4,6` preserve both
radius and eta, although all three vertices are at distance two from `5`.

This is not a counterexample to `(2DEL)`.  It is an exact counterexample to
the proposed structural completion

```text
at least two good deletions are forced by a radius drop or by (3.2).
```

The independent verifier recomputes every distance, center, deletion
radius, deletion eta, new-center set, and unique eccentric vertex:

```text
python problems_external/wowii_144/attack_ind2_multicycle/verify_two_good_deletion_audit.py
```

It writes the full record to `two_good_deletion_obstruction.json`.

## 6. Finite evidence and the first unsupported implication

The existing exact verifier

```text
test_two_good_deletions.py --max-n 13
```

checks all 45,593 connected multicyclic girth-at-least-five graphs through
order 13.  The minimum number of eta-good admissible deletions is two.  A
separate exact run over all 201,727 2-connected graphs through order nine,
without a girth restriction, also found minimum two.  These computations are
falsification evidence, not proofs.

After the theta base and Lemmas 2.1--3.1, the first unsupported implication
is now precise:

> In a `beta>=3` graph, prove that the radius-increasing bad deletions and
> the mutually disjoint unique-eccentric fibers of the radius-preserving bad
> deletions cannot cover all but at most one admissible vertex.

No proved metric or block/ear theorem currently implies this.  The graph in
Section 5 shows that even the existence of the required good vertices may be
invisible to all the local consequences (3.1)--(3.2).  Radius-increasing bad
deletions carry no unique-eccentric witness at all.  Therefore asserting the
quoted incompatibility would assert the load-bearing global center-change
theorem rather than prove it.  The two-deletion route remains open at this
point.
