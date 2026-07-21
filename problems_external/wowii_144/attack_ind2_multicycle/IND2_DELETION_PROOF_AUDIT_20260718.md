# W144-IND2 multicyclic deletion: proof audit

Date: 2026-07-18.

## 1. Exact frontier

For a finite connected cyclic graph `X`, put

```text
eta(X) = max_x d_X(x,C(X)),
phi(X) = girth(X)+eta(X),
beta(X) = |E(X)|-|V(X)|+1.
```

The required multicyclic induction lemma is

```text
beta(G)>=2 and girth(G)>=5
  ==> exists v, G-v is connected and cyclic and phi(G-v)>=phi(G).     (IND2)
```

This note does **not** prove (IND2).  It records the exact finite evidence,
the structural part that is proved, and three direct selection rules that
are false.  The sole remaining unsupported implication is identified in
Section 6.

## 2. Finite evidence

The registered exhaustive certificate covers every connected
girth-at-least-five multicyclic graph through order 13.  At orders 12 and 13
there are 44,258 such graphs; every graph has an (IND2) deletion and the
minimum best slack is zero.

The stronger assertion

```text
exists v, G-v connected cyclic and eta(G-v)>=eta(G)                  (S)
```

was independently recomputed through order 12 with `geng -ctf`; no failure
occurred.  This is stronger finite evidence, not a proof and not the
registered frontier.  The deterministic/random large-order audit in
`IND2_LARGE_AUDIT_20260718.md` checked another 16,590 graphs of orders 14--40,
again without an (IND2) failure.

The scripts in this directory recompute centers and all deletion invariants
from the graph itself.  In particular:

```text
analyze_tight_deletions.py
test_low_degree_deletion.py
random_ind2_search.py
```

The seeded subdivided-core search checked 1,000 additional graphs, found no
failure, and found 87 equality cases.

## 3. A proved structural lemma

**Lemma 3.1 (girth-preserving exterior deletion).**  Let `K` be a shortest
cycle of a connected simple graph `G` with `beta(G)>=2`.  There is a vertex
`v` outside `K` such that `G-v` is connected, contains `K`, and therefore is
cyclic with `girth(G-v)=girth(G)`.

**Proof.**  The shortest cycle `K` is induced.  If every vertex lay on `K`,
inducedness and simplicity would give `G=K`, contrary to `beta(G)>=2`.
Hence an exterior vertex exists.  Delete one edge of `K`, extend the resulting
tree on `V(K)` to a spanning tree `T` of `G`, and root `T` in `V(K)`.  Choose
an exterior vertex `v` of maximum rooted depth.  It has no exterior child by
maximality and no child in `K`, since `T[V(K)]` is already connected.  Thus
`v` is a leaf of `T`; `T-v` proves that `G-v` is connected.  The cycle `K`
survives, and vertex deletion creates no shorter cycle.  QED.

This lemma proves admissibility and exact girth preservation.  It does not
control the new center, and the required metric conclusion for this `v` is
false in general (Section 5.1).

## 4. What deletion does control metrically

Let `H=G-v` be connected.  For every surviving vertex `u`,

```text
ecc_H(u) >= ecc_G(u)-1.                                           (4.1)
```

Indeed, if an eccentric vertex `x` for `u` survives, then
`d_H(u,x)>=d_G(u,x)=ecc_G(u)`.  Otherwise `v` is eccentric for `u`; the
penultimate vertex `w` on a shortest `u`--`v` path survives and satisfies
`d_H(u,w)>=d_G(u,w)=ecc_G(u)-1`.  Taking minima gives

```text
rad(H) >= rad(G)-1.                                                (4.2)
```

Equations (4.1)--(4.2) do **not** bound `eta(H)` from below.  The exact graph

```text
J?AA@agU?M?
```

has order 11, girth 6, radius 3, center `{7}`, and `eta=3`.  Deleting vertex
`2` leaves a connected cyclic graph of girth 6 in which every surviving
vertex has eccentricity 4.  Its radius rises to 4, its center expands to all
ten vertices, and `eta` falls from 3 to 0.  Thus the load-bearing difficulty
is center-set expansion, not a missing pointwise eccentricity estimate.

## 5. Exact dead selection rules

### 5.1 Exterior-only deletion is false

For

```text
G = K??CA?_sDOEg
```

we have `n=12`, `beta=2`, `girth=5`, `C(G)={2,10}`, and `eta(G)=3`.  Its
unique shortest cycle is `(1,7,11,3,9)`.  Every admissible deletion outside
that cycle is one of `4,5,6,8`; each preserves girth 5 but lowers `eta` to 2,
so each lowers `phi` by one.  Good deletions exist, but they lie on the
shortest cycle: for example, deleting `3` gives `(girth,eta)=(7,3)`, and
deleting `7` gives `(6,3)`.

Consequently Lemma 3.1 cannot be completed by asserting that its exterior
vertex is metric-good.

### 5.2 Shortest-cycle-only eta preservation is false

For

```text
G = J?AAD?oTEO?
```

we have `n=11`, `beta=2`, `girth=5`, and `eta=2`.  The girth-cycle vertices
are `{0,1,5,9,10}`.  The only admissible deletion among them is `5`, and it
lowers `eta` to 1.  Eta-nondecreasing deletions exist only off that cycle.

### 5.3 Shortest-cycle-only phi preservation is also false

For

```text
G = J?AAD?WsAQ?
```

we have `n=11`, `beta=2`, `girth=5`, and `eta=2`.  Its girth-cycle vertices
are `{0,1,7,9,10}`, but deleting any of them fails to leave a connected
cyclic graph.  Phi-preserving deletions exist on the exterior long ear
(`v=3` or `v=4`) and at the leaf `v=6`.

Thus neither side of a shortest-cycle/exterior split supplies a universal
location for the desired vertex.  The two sides must be compared through
the actual center change; replacing that comparison by a location rule is
not valid.

### 5.4 Degree-two ear deletion is false

The graph

```text
I?`acgwg_
```

has order 10, girth 5, `beta=5`, and `eta=2`.  Its only degree-two vertices
are bad; every eta-preserving deletion has degree three.  Therefore a proof
cannot select only an internal vertex of a terminal degree-two ear.

## 6. The unsupported implication

The direct proof now reduces to the following exact assertion and no weaker
surrogate:

```text
max { girth(G-v)-girth(G) + eta(G-v)-eta(G) :
      G-v connected and cyclic } >= 0.                           (6.1)
```

Lemma 3.1 proves that the set in (6.1) is nonempty and contains a deletion
with zero girth change.  Section 4 supplies the only general pointwise
eccentricity estimate presently proved.  It does not imply (6.1), because a
one-unit increase of the old central eccentricity can make many formerly
noncentral vertices tie for the new radius and collapse `eta` by several
units.  None of the current arguments compares that center expansion with
the girth gain of a different admissible deletion.

This comparison is the first unsupported step.  Asserting it would simply
assert the load-bearing multicyclic theorem, so it is not inserted as a
lemma with an omitted proof.

## 7. Lean-friendly lemma tree

The proved and required formal pieces separate as follows.

1. `shortestCycle_isInduced` (proved in the existing order-cover work).
2. `exists_exterior_vertex_delete_connected` (Lemma 3.1, spanning-tree leaf).
3. `girth_delete_eq_of_cycle_survives` (the last sentence of Lemma 3.1).
4. `eccent_delete_lower` (4.1), then `radius_delete_lower` (4.2).
5. `multicyclic_delete_phi_nonneg` (exact statement (6.1), **open**).
6. `ind2_multicyclic_step`: apply item 5 and preserve an induced tree from
   `G-v` inside `G`.
7. `wowii144_induction`: iterate item 6 until the proved unicyclic base in
   `attack_ind2_unicyclic/UNICYCLIC_W144_THEOREM_20260718.md`.

Items 1--4 are elementary and Lean-suitable.  Item 5 is the sole global
center-change theorem still missing; no warning-free formal proof of W144 can
be claimed without it.

