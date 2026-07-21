# W144 rooted-capacity audit: exact restricted lemma and remaining obstruction

**Status (2026-07-18).** This is **not** a proof of Conjecture 144 or of WN2.
It proves one exact active-component subcase, proves a shortest-cycle exchange
fact that every full proof must use, and records reproducible finite tests.  The
only unresolved step is stated at the end without weakening or replacing the
registered W144-R frontier.

## 1. Setting

Use the notation of `STATUS.md`.  Thus `K` is a shortest cycle of length `g`,
`x` is an `e`-realizer, `h=d(x,K)<e`, `m` is an anchor of `x`,
`delta=e-h`,

    W={sigma in K : d_K(m,sigma)<=delta-1},
    c=max(0,2 delta-g),

and `H_x` is the component of `G-K` containing `x`.  For `z!=m`,
`mu_z(H_x)` is the largest `z`-admissible local forest order.  Put

    Q_x=E_{H_x} cap W,      q_x=|Q_x|.

The graph has girth at least five, so every outside vertex has at most one
neighbor on `K`.

## 2. Exact restricted active-component lemma

**Lemma A (two-root active component).**  Suppose `h>=1`, `q_x>0`, and the
attachment set of `H_x` is contained in `{m,z}`.  Then

    q_x + max(0,2 delta-g) <= 2(mu_z(H_x)-h).             (A)

**Proof.**  Choose `sigma in Q_x` minimizing

    a=d_K(m,sigma),

and choose `y in H_x` with `d(sigma,y)>=r+1`.  The vertex `y` is distinct from
`x`, because `d(sigma,x)<=h+a<=e-1<=r-1`.

The induced graph `B=G[H_x union {m}]` is connected and triangle-free.  The
three-in-a-tree theorem for connected triangle-free graphs therefore supplies
an induced tree `T` in `B` containing `m,x,y`.  Replace it by its minimal
subtree spanning these three vertices.  It remains induced.  In a tree, the
number of edges in that minimal subtree is half the sum of the three pairwise
distances.  Since distances in the induced subgraph and in `T` dominate graph
distances, while a shortest cycle is isometric,

    d_T(m,x) >= h,
    d_T(m,y) >= d(sigma,y)-d_K(m,sigma) >= r+1-a,
    d_T(x,y) >= d(sigma,y)-d(x,sigma) >= r+1-h-a.

Consequently

    |T|-1 >= (h+(r+1-a)+(r+1-h-a))/2 = r+1-a.            (1)

Delete `m` from `T`.  Each resulting component sends exactly one edge to `m`:
at least one by its definition as a component of `T-m`, and at most one because
`T` is a tree and is induced in `B`.  By hypothesis, every other edge from its
vertices to `K` goes to `z`.  Hence `T-m` is `z`-admissible, and (1) gives

    mu_z(H_x) >= r+1-a.

Since `r>=e=h+delta`,

    mu_z(H_x)-h >= delta+1-a.                             (2)

It remains only to count cycle positions.  If the window is unwrapped, the
vertices of `W` at distance at least `a` from `m` number at most
`2(delta-a)` when `a>=1`, while for `a=0` the whole window has `2delta-1`
vertices.  If the window is wrapped, `Q_x` avoids the cycle ball of radius
`a-1`; hence for `a>=1`,

    q_x <= g-(2a-1),

and adding `c=2delta-g` gives `q_x+c<=2delta-2a+1`.  For `a=0`,
`q_x+c<=g+(2delta-g)=2delta`.  In all cases

    q_x+c <= 2(delta+1-a) <= 2(mu_z(H_x)-h)

by (2).  This proves (A).  QED.

The three-in-a-tree input is Theorem 1.2 quoted in N. Derhy, C. Picouleau and
N. Trotignon, *The four-in-a-tree problem in triangle-free graphs*, Graphs and
Combinatorics 25 (2009), 489--502; open version:
https://arxiv.org/abs/1309.0978 .

## 3. Exact shortest-cycle exchange fact

The next lemma explains why true multiattachment examples have extra rooted
capacity in every bounded equality case.

**Lemma B (one-unit ear excess).**  Fix an `e`-realizer `x` and choose, among
all shortest cycles, `K` minimizing `h=d(x,K)`.  Suppose `h>=1`; let
`x=v_h,...,v_1,m` be an `x`--`K` geodesic.  If a vertex `u` in `H_x` is
adjacent to `a in K-{m}`, then

    d_{H_x}(v_1,u)+2+d_K(m,a) >= g+1.                    (B)

**Proof.**  A shortest `v_1`--`u` path in `H_x`, the edges `mv_1` and `ua`,
and a shortest `m`--`a` arc of `K` form a simple cycle.  Its length is the
left side of (B), so it is at least `g`.  Equality would give another shortest
cycle containing `v_1`; its distance from `x` would be at most `h-1`, contrary
to the choice of `K`.  Thus the integer length is at least `g+1`.  QED.

The extra `+1` is exactly the amount absent from the ordinary girth inequality
for an arbitrary shortest cycle.  Turning one such excess into one pruning
credit is straightforward for a single extra attachment.  What is not yet
proved is that credits can be assigned injectively when a minimal
three-terminal tree contains several extra attachment vertices.

## 4. Root triangles disappear for `g>=7`

**Lemma C (triangle-free auxiliary root).**  If `g>=7`, then every auxiliary
graph `J_z(H)` is triangle-free.

**Proof.**  A triangle wholly inside `H` would be a triangle of `G`.  Hence a
triangle would have the form `rho-u-v-rho`.  The vertices `u,v` are adjacent
and attach to roots `a,b in K-{z}`.  They cannot have the same root, since
`a-u-v-a` would be a triangle of `G`.  For distinct roots, the path
`a-u-v-b` and a shortest `a`--`b` arc of `K` form a cycle, so

    g <= d_K(a,b)+3 <= floor(g/2)+3,

which is impossible for `g>=7`.  QED.

**Corollary C.1 (quantitative rooted three-terminal tree).**  Let `x,y in H`,
let `m` be an anchor of `x`, let `z!=m`, and put `h=d(x,K)`.  If `g>=7`, then

    mu_z(H) >= ceil((h+d_J(rho,y)+d_J(x,y))/2).           (C1)

Indeed `d_J(rho,x)=h`: the legal `x`-tail gives the upper bound, while every
`rho`--`x` path expands to a path from `K` to `x` in `G`.  Lemma C and the
three-in-a-tree theorem give an induced tree of `J` through `rho,x,y`.  Its
minimal terminal subtree has at least half the sum of the three auxiliary
pair distances in edges; deleting `rho` is exactly a `z`-admissible forest.

This is the requested rigorous conversion of one active witness into
`mu_z(H)` in all girths at least seven.  It does not by itself sum several
witnesses: the apex collapses the cycle arc between their attachment roots,
so `d_J(rho,y)` need not retain the lower bound `d_G(m,y)>=r+1-a` used in
Lemma A.

## 4. Exact finite audit

`diagnose_root_capacity.py` enumerates local capacities by subsets.  On every
connected triangle-free and square-free graph of orders 8 through 12 it found

    residual graphs                         526
    (K,x,m,z) choices                    14,402
    retained-component q_H>2 mu_z(H)          0
    x-component q_x>2(mu_z(H_x)-h)            0
    graphs with negative best WN2 gap          0.

For `g>=7`, a separate exact check of (C1) on every active window position found 276 tests and zero cases where its right side was below `e-d_K(m,sigma)` (orders 8--12).

A separate exact active-ear audit found 4,538 active `H_x` choices.  In 4,229
the shortest `m`-to-third-root ear makes another cycle of length exactly `g`;
the remaining 309 have strict ear excess, with no rooted-surplus failure.
These are finite certificates only, not a proof.

The bounded random falsifiers add:

* 20,000 girth-safe multiattachment-tree trials: 619 residual graphs, all
  closed already by a tail of height at least `e`;
* 20,000 tight-cycle-seeded trials: 2,993 residual graphs, 2,708 genuine WN2
  frontier instances, minimum exact best slack zero and no failure.

## 5. Remaining exact obligation

Only the following case is open.  The active component `H_x` has an attachment
outside `{m,z}`.  A minimum induced tree through `m,x,y` then becomes a rooted
tree with extra apex chords when `m` is replaced by the auxiliary root `rho`.
One must prove that deleting/pruning the vertices needed to separate those
extra attachment edges costs no more than the strict ear excesses from Lemma B,
so that

    q_x + max(0,2 delta-g) <= 2(mu_z(H_x)-h).

The accounting must be simultaneous for all extra attachments and use one
global `z`.  No injective charging proof is presently known.  Iterating Lemma B
without that injection would be an unproved hierarchy and is not done here.



