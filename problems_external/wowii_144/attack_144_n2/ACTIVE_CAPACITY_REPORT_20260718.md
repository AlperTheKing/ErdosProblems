# W144 active rooted-capacity attack

Date: 2026-07-18.

This note does **not** claim a proof of Conjecture 144.  It records an exact
local decomposition, one closed active-component regime, a sharper ordinary
component target, and independently reproducible finite tests.  The remaining
statement is displayed in the last section; no bounded test is used as a
proof.

## 1. Data and the exact local capacity

Work in the registered residual case with `g>=5`.  Thus `K` is a shortest
cycle, `r` is the radius, `C` is the center, `e=ecc(C)`, and

    D <= e+floor(g/2)-1,       e <= r.

Choose an `e`-realizer `x` of maximum height `h=d(x,K)<e`, a nearest cycle
vertex `m`, and put `delta=e-h`.  Let

    W={sigma in K : d_K(m,sigma)<=delta-1}.

For a component `H` of `G-K`, put

    E_H={sigma in W : some y in H has d(sigma,y)>=r+1},
    q_H=|E_H|.

Fix `z in K`.  Define `mu_z(H)` to be the maximum order of a set `F subset H`
such that `G[F]` is a forest and every component of `G[F]` sends exactly one
edge into `K-{z}`.  Edges into `z` are unrestricted.  This definition permits
several selected tree components inside the same component `H`; replacing it
by one rooted path or one connected tree is false in general.

Let `M_z(K)` be the corresponding maximum over all of `G-K`.  Components of
`G-K` are pairwise anticomplete, so restriction and union give the exact
identity

    M_z(K)=sum_H mu_z(H).                                      (1)

For later use, form `J_z(H)` from `G[H]` by adding one apex `rho` adjacent to
every vertex of `H` incident with an edge into `K-{z}`.  A vertex outside `K`
has at most one neighbor on `K` because `g>=5`.  Consequently

    mu_z(H)+1 = maximum order of an induced tree in J_z(H)
                that contains rho.                            (2)

Indeed, deleting `rho` from such a tree leaves a forest whose components each
have one `rho`-edge, and adjoining `rho` to any admissible forest reverses the
construction.

There is also a useful girth transfer.  A cycle of `J_z(H)` avoiding `rho` is
a cycle of `G` and has length at least `g`.  A cycle through `rho`, after
removing `rho`, is an `H`-path between two boundary vertices.  If their cycle
attachments are `a,b`, adjoining a shortest `a-b` arc of `K` gives a cycle of
`G`.  Hence

    girth(J_z(H)) >= ceil(g/2).                                (3)

In particular `J_z(H)` is triangle-free for `g>=7`.  Apex triangles, and thus
the exceptional local geometry, can occur only at `g=5,6`.

## 2. The exact global inequality and a sharper local reduction

Write

    S=sum_H q_H,       c=max(0,2delta-g),
    lambda=2r+1-g >= 0.

The registered frontier is

    S+c <= 2(M_z(K)-h).                                       (WN2)

The following sharper ordinary-component inequality survived every exact test
reported below:

    q_H+lambda <= 2 mu_z(H)                                   (O)

whenever `q_H>0` and `H` has an attachment outside `z`.  The plain consequence
`q_H<=2mu_z(H)` is enough in the unwrapped case.  The `lambda` term is exactly
what is needed when the active component contributes no cover, because

    c=2delta-g <= 2r-g=lambda-1.                               (4)

Since `W` is covered, if the active component has `q=0`, some ordinary
component has positive `q_H`; (O) pays `c` by (4).  The same observation handles
`h=0`, when `x=m` lies on `K` and there is no active outside component.

Thus, after (O), it remains only to prove the active inequality

    q_X+c <= 2(mu_z(H_X)-h)                                   (X)

when `h>=1` and `q_X>0`, where `H_X` contains `x`.

## 3. Closed active regime: no usable attachment except m

Assume `h>=1`, `q_X>0`, and every attachment of `H_X` lies in `{m,z}`.  Choose
`sigma in E_{H_X}` minimizing

    a=d_K(m,sigma),

and choose `y in H_X` with `d(sigma,y)>=r+1`.  The vertex `y` is different from
`x`, since

    d(sigma,x)<=a+h<=delta-1+h=e-1<r+1.

The graph `B=G[H_X union {m}]` is connected and triangle-free.  The standard
three-in-a-tree theorem for triangle-free graphs therefore supplies an induced
tree `T subset B` containing the three distinct vertices `m,x,y`.  In any tree,
the number of edges in the minimal subtree spanning three vertices is half the
sum of their three pairwise tree distances.  Distances in `T` dominate graph
distances, while

    d(m,x)=h,
    d(m,y)>=d(sigma,y)-d_K(m,sigma)>=r+1-a,
    d(x,y)>=d(sigma,y)-d(sigma,x)>=r+1-h-a.

The sum is at least `2(r+1-a)`.  After replacing `T` by its minimal subtree on
`{m,x,y}`, it follows that

    |V(T)-{m}| >= r+1-a.                                      (5)

Put `F=V(T)-{m}`.  Removing `m` from a tree gives a forest, and every resulting
component has exactly one edge to `m`.  All other cycle edges from `F` go to
`z`, by the attachment hypothesis, and are unrestricted.  Therefore `F` is
`z`-admissible and

    mu_z(H_X)-h >= r+1-a-h >= delta+1-a.                       (6)

It remains only to count cycle layers.  If `W` is unwrapped, at most
`2(delta-a)` vertices of `W` have distance at least `a` from `m` (the harmless
case `a=0` is even smaller than the bound used below).  If `W` wraps, then
`W=K` and, for `a>=1`, at most `g-2a+1` cycle vertices have distance at least
`a`; adding `c=2delta-g` gives at most `2delta-2a+1`.  In both cases

    q_X+c <= 2(delta+1-a) <= 2(mu_z(H_X)-h),

by (6).  This proves (X) in the stated attachment regime.  If `q_X=0` and
`c=0`, (X) is immediate.

The existence theorem used here is Theorem 1.2 quoted in N. Derhy,
C. Picouleau and N. Trotignon, *The four-in-a-tree problem in triangle-free
graphs*, arXiv:1309.0978: every three distinct vertices of a connected
triangle-free graph lie in an induced tree.

## 4. Exact computations

`verify_component_capacity.py` generated every connected triangle-free and
square-free graph of orders 5 through 14 with nauty `geng -c -t -f`.  These are
exactly the connected graphs in this range that can have girth at least five.
It enumerated every shortest cycle, every maximum-height realizer and anchor,
and every retained-attachment component.  It enumerated `mu_z(H)` over all
vertex subsets, allowing multiple selected components.

The result file is

    component_capacity_n5_14_results.json

with SHA-256

    54F8EE540219EA6B42D156CEE473F6EB65E09FFF598679C6BE4A753603B8C2E3.

Counts and minimum slacks are:

* ordinary `q_H<=2mu_z(H)`: 279,517 tests, minimum slack 0;
* sharpened (O), with `q_H>0`: 175,733 tests, minimum slack 0;
* safe adjacent-root WN2: 46,070 tests, minimum slack 0;
* active (X): 40,390 tests, minimum slack 0.

For `A(H_X) subset {m,z}`, the exact split contained 7,576 cases, all with
`q_X=0` and `c=0`; no positive-`q_X` or wrapped example occurred.  A tight
record is graph6 `I??CBbGH_`, with `g=7`, `r=e=3`, `D=5`, `x=4`, `h=1`,
`m=8`, `z=0`, `A(H_X)={8}`, `E_{H_X}=empty`, and `mu_z(H_X)=1`.

Sharp ordinary equality already occurs on graph6 ``F?q`o``: for
`K={0,2,4,5,6}`, `x=m=5`, `W={0,2,5}`, `z=0`, the singleton component
`H={1}` has attachment `{4}`, `E_H={2,5}`, and `mu_z(H)=1`, attained by
`F={1}`.  The other singleton component has the symmetric equality.  Thus the
factor two in (O) cannot be improved.

`search_n2_targeted.py` also tested 7,809 exact `n-g<=18` rooted-cycle
mutations (1,457 residual graphs) with the wrap correction included.  It found
no WN2 failure; minimum slack was zero.  This is evidence only.

## 5. Falsified shortcuts

1. Rooted depth cannot replace active induced-tree capacity.  The exact
   29-vertex certificate in `depth_only_counterexample.md` has
   `q_X=13>12=2(R_z(H_X)-h)` while `mu_z(H_X)=11`.
2. Even a maximum admissible forest need not itself contain far witnesses for
   all of `E_H`.  On graph6 `I??E@qcT?`, one ordinary component has
   `E_H={2,3,7}` and `mu_z(H)=2`; its three maximum forests cover the three
   two-element subsets of `E_H`, but no maximum forest covers all three.
3. The tempting universal two-terminal bound

       mu_z(H_X) >= h+d(x,y)-1

   is false on graph6 `J??ED?WD_Y?`: `h=2`, `d(x,y)=4`, and `mu=4<5`.
4. The residual three-terminal candidate is not a general graph lemma.  On
   graph6 ``H?`DBRO``, outside the residual regime,

       ceil((h+d(m,y)+d(x,y))/2)-1=3 > mu_z(H)=2.

   A second nonresidual example with an `e`-realizer and `h<e` is
   `J?AA@BOLDO?`.  Thus any proof must use the residual diameter/center
   hypotheses; triangle-freeness alone is insufficient.

## 6. Remaining exact obligation

The direct route has now been reduced without a hierarchy to two local
statements:

1. prove (O) for every nonempty ordinary cover component with an attachment
   outside `z`; and
2. prove (X) when `H_X` has an attachment outside `{m,z}`.

For `g>=7`, (3) makes the auxiliary rooted graph `J_z(H)` triangle-free, so a
three-in-a-tree exchange is available.  The cases `g=5,6` are exactly the cases
where apex triangles may occur and must be treated separately.  No proof of
these two remaining statements is supplied here, and the finite certificates
above must not be cited as one.
