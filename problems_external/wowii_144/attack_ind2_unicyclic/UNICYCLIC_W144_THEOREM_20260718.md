# W144-IND2: the unicyclic base case

Date: 2026-07-18.

## Result

Let `G` be a finite simple connected unicyclic graph.  Let `K` be its
unique cycle, let `g=|K|=girth(G)`, let `C=C(G)` be its ordinary center, and
put

    e = max_x d_G(x,C).

Then

    largestInducedTreeSize(G) >= g-1+e.                       (U)

The proof works for every `g>=3`, so it includes the `g>=5` base required by
W144-IND2.  This closes the unicyclic class only; it does not prove the
paired-deletion lemma for multicyclic graphs.

The only imported metric result is the already proved total-cover order
lemma

    e <= |V(G)|-girth(G)                                     (OC)

for finite connected cyclic simple graphs.  Its complete proof and exact
audit are in `attack_global/ORDER_COVER_LEMMA_20260718.md`.

## 1. Branch partition at the unique cycle

The graph `G-V(K)` is a forest.  Every one of its connected components has
exactly one edge to `K`: it has at least one by connectedness, while two
attachment edges, together with the path between their outside endpoints
and a suitable arc of `K`, would produce a cycle different from `K`.

For `a in V(K)`, let `B_a` be the union of all components of `G-V(K)` whose
unique attachment edge ends at `a`, and define

    n_a=|B_a|,       q=sum_(a in K) n_a=|V(G)|-g,
    m=min_(a in K) n_a,       N=max_(a in K) n_a.

Several outside components may have the same root `a`; no later argument
assumes otherwise.  A vertex in a component contained in `B_a` is at
distance at most `n_a` from `a`, since a simple root-to-vertex path uses at
most all vertices of that component.

## 2. Exact Lemma-M capacity

For this unique cycle,

    M(K)=q-m.                                                 (1)

To prove the lower bound, choose `z in K` with `n_z=m` and take

    F=(V(G)-V(K))-B_z.

The induced graph `G[F]` is a forest.  Each of its components is an entire
outside component rooted at some `a!=z`, and hence sends exactly one edge
to `K-{z}`.  Thus `(F,z)` is a valid Lemma-M witness and `|F|=q-m`.

Conversely, let `(F,z)` be any valid Lemma-M witness.  If `F` met `B_z`, the
component of `G[F]` containing such a vertex would lie in an outside
component whose only cycle attachment is at `z`.  It would therefore send
zero edges to `K-{z}`, contrary to validity.  Hence

    F subseteq (V(G)-V(K))-B_z,
    |F| <= q-n_z <= q-m.

This proves (1), including the empty-forest case.

The lower-bound witness also gives the induced tree directly.  The graph
induced by

    (K-{z}) union F

is an induced path on `g-1` cycle vertices with forest components attached
to it by exactly one edge each.  It is a tree of order

    g-1+q-m.                                                  (2)

Thus no optimization or unstated choice is hidden in the use of Lemma M.

## 3. Center bound `e<=q-m`

We split according to whether the lightest cycle root is empty.

### Case 1: `m=0`

Here (OC) gives

    e <= |V(G)|-g = q = q-m.                                 (3)

This also covers the bare cycle: then `q=m=e=0`.

### Case 2: `m>=1`

Put `s=floor(g/2)` and choose `z in K` with `n_z=m`.  For a cycle vertex
`x`, the shorter cycle arc gives `d_G(z,x)<=s`.  If `x in B_a`, first take
the shorter `z`--`a` arc and then a path inside the outside component of
`x`; Section 1 gives

    d_G(z,x) <= s+n_a <= s+N.

Consequently

    rad(G) <= ecc_G(z) <= s+N.                                (4)

There are `g-1` branch weights other than one attaining `N`, and every one
is at least `m`.  Hence

    N+(g-1)m <= q.                                            (5)

Since `g>=3`,

    s=floor(g/2) <= g-2 <= (g-2)m.                            (6)

For every vertex `x` and every center vertex `c`,
`d_G(x,C)<=d_G(x,c)<=rad(G)`, so `e<=rad(G)`.  Combining (4)--(6) gives

    e <= rad(G)
      <= s+N
      <= (g-2)m + q-(g-1)m
       = q-m.                                                 (7)

Together, (3) and (7) prove `e<=M(K)=q-m`.  The induced tree in (2) now has
at least `g-1+e` vertices, proving (U).

## 4. Referee audit

1. **No path-branch assumption.**  The proof uses only that each outside
   component is a tree with one attachment and that root distance is at most
   its order.  Branching and several components at one cycle root are allowed.
2. **No center-location assumption.**  In the all-positive case the center
   may lie on or off `K`; only `e<=rad(G)<=ecc_G(z)` is used.
3. **Why the cases differ.**  If `m=0`, the estimate
   `ecc_G(z)<=floor(g/2)+N` does not imply the target; (OC) supplies exactly
   the missing `e<=q`.  If `m>=1`, the other `g-1` nonempty branch bundles
   pay the cycle term in (6).
4. **Natural-number subtraction.**  Equation (5) implies
   `(g-1)m<=q`, so every displayed subtraction is defined; equivalently the
   arithmetic may be carried out in the integers and returned to naturals.
5. **Scope.**  The one-attachment assertion is false for general
   multicyclic graphs.  Nothing here is used to claim the global W144 theorem.

## 5. Lean-friendly lemma tree

The paper proof separates into the following finite lemmas.

1. `unicyclic_outside_isForest`:
   `G` unicyclic and `K` its unique cycle implies `G[V-K]` is a forest.
2. `unicyclic_component_unique_attachment`:
   every component of `G[V-K]` has exactly one edge to `K`.
3. `unicyclic_branch_partition_card`:
   the fibers `B_a` partition `V-K` and `sum a, |B_a|=|V|-|K|`.
4. `unicyclic_M_eq_total_sub_minBranch`:
   the two inclusions in Section 2 prove `M(K)=q-m`.
5. `unicyclic_minBranch_inducedTree`:
   the explicit vertex set `(K-{z}) union ((V-K)-B_z)` induces a tree of
   cardinality `g-1+q-m`.
6. `unicyclic_allBranches_pos_radius_le`:
   if every `n_a>=m>=1`, then
   `rad(G)<=g/2+max_a n_a<=q-m`.
7. `unicyclic_centerEcc_le_M`:
   split on `m=0`; use (OC) in the zero case and Lemma 6 plus `e<=rad` in
   the positive case.
8. `unicyclic_wowii144`:
   compose Lemmas 5 and 7.

For formalization, define the branch root as the unique cycle endpoint of
the unique attachment edge of an outside component.  This avoids choosing
paths or quotienting vertices.  The only prerequisite not local to the
unicyclic file is the formal version of (OC).

## 6. Exact computation

The independent script `test_unicyclic_formula.py` enumerates with `geng`
every connected unlabeled graph with `n` vertices and `n` edges through
`n=15`; these are exactly the unicyclic graphs.  It recomputes the unique
cycle, branch partition, ordinary center, `e`, and `q-m`.  Through `n=10`
it also enumerates every subset outside `K` and checks the defining maximum
`M(K)` rather than using (1).

The deterministic run

    python test_unicyclic_formula.py --max-n 15 --exact-m-n 10

returned

    unicyclic graphs checked:       171512
    exact M(K) subsets checked on:     1040 graphs
    failures of M(K)=q-m:                  0
    failures of e<=q-m:                    0
    minimum slack (q-m)-e:                 0

Order counts were `1,2,5,13,33,89,240,657,1806,5026,13999,39260,110381`
for `n=3,...,15`, providing a reproducible enumeration checksum.
