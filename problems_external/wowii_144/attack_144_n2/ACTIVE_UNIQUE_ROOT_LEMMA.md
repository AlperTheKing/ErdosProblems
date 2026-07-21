# Active-component surplus with one usable cycle root

This note proves a load-bearing subcase of the Extended Reserved
Rooted-Capacity Lemma.  It is not a proof of Conjecture 144: the
multiattachment active component and the wrapped case with no active
coverage remain.

## Lemma

Use the residual notation of `APPROACH_REGISTRY.md`.  In particular,
`g>=5`, `K` is a shortest cycle, `x` is an `e`-realizer of maximum height
`h=d(x,K)>=1`, `m` is a nearest anchor, `delta=e-h`, and `z` is a neighbor
of `m` on `K`.  Let `H_x` be the component of `G-K` containing `x`, put

    Q=E_{H_x} intersect W,   q=|Q|,
    c=max(0,2 delta-g),

and suppose

    A(H_x) subset {m,z}                                      (1)

and `q>0`.  Then

    q+c <= 2(mu_z(H_x)-h).                                  (2)

Here attachments at `z` are ignored in the definition of `mu_z`, so (1)
says that `m` is the only usable cycle root of `H_x`.

## Proof

Choose `sigma in Q` minimizing

    a=d_K(m,sigma),

and choose `y in H_x` with `d(sigma,y)>=r+1`.  The vertices `m,x,y` are
distinct.  Indeed `h>=1` gives `m notin H_x`, while

    d(sigma,x) <= a+h <= delta-1+h=e-1<=r-1,

so `y!=x`.

The induced graph

    B=G[H_x union {m}]

is connected and triangle-free.  The three-in-a-tree theorem for connected
triangle-free graphs therefore supplies an induced tree `T` in `B` containing
`m,x,y`.  (Equivalently, this follows by taking a vertex-minimal connected
induced subgraph containing the three vertices: a cycle has length at least
four, whereas its necessary terminal branches can account for at most three
cycle vertices.)

Distances in `T` dominate ambient distances.  The reserved geodesic gives
`d_B(m,x)=h`, and the triangle inequality gives

    d_B(m,y) >= d_G(m,y) >= r+1-a,
    d_B(x,y) >= d_G(x,y) >= r+1-h-a.                         (3)

In a tree, the sum of the three pairwise distances of three vertices is twice
the number of edges in their minimal spanning subtree.  Hence (3) implies

    |T|-1 >= (h+(r+1-a)+(r+1-h-a))/2 = r+1-a.               (4)

Delete `m` from `T`.  By (1), every component that remains sends exactly one
edge into `K-{z}`: its unique such edge is its tree edge to `m`; any edge into
`z` is ignored.  Thus `T-{m}` is a legal local forest, and (4) gives

    mu_z(H_x) >= r+1-a.

Since `e=h+delta<=r`,

    mu_z(H_x)-h >= delta+1-a.                               (5)

It remains only to count `Q`.  By minimality of `a`, `Q` avoids the cycle ball
of radius `a-1` about `m`, which is contained in `W`.  If the window is
unwrapped, `|W|=2delta-1`, and therefore

    q <= (2delta-1)-(2a-1)=2(delta-a).

If the window is wrapped, `|W|=g` and `c=2delta-g`, so

    q+c <= (g-(2a-1))+(2delta-g)
         = 2delta-2a+1.

The case `a=0` follows directly from `q<=|W|` and the same two displayed
window sizes.  In both regimes,

    q+c <= 2(delta+1-a) <= 2(mu_z(H_x)-h)

by (5), proving (2).  QED.

## Exact remaining boundary

The argument does not cover either of the following:

1. `H_x` has a usable attachment in `K-{m,z}`.  A three-terminal tree in
   `G[H_x union {m}]` may then acquire extra apex edges in `J_z(H_x)`, so
   deleting `m` need not be locally legal.
2. The window is wrapped, `q=0`, and the positive correction
   `2delta-g` must be obtained from other components or from active branching.

These are the precise active-capacity obligations still open.
