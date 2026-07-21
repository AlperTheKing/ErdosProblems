# W144 ordinary rooted-triameter reduction

Date: 2026-07-18.

This note does **not** prove Conjecture 144, the registered WN2 frontier, or
the ordinary-component inequality below.  It isolates one exact metric lemma
which would prove the ordinary inequality for `g>=7`, gives independently
reproducible exhaustive evidence, and records counterexamples to three simpler
surrogates.  Bounded computations are not used as proofs.

## 1. Registered setting and the ordinary target

Use the W144-R residual notation.  Thus `K` is a shortest cycle of order `g`,
`r` is the radius, `C` is the center, `e=ecc(C)`, and

    D <= e+floor(g/2)-1,        e <= r.

Choose an `e`-realizer `x` of maximum height `h=d(x,K)<e`, an anchor `m`, put
`delta=e-h`, and let

    W={sigma in K : d_K(m,sigma)<=delta-1}.

The reserved vertex `z` is a neighbor of `m` on `K`, selected so that no
component attached only at `z` covers a point of `W`.  For a component `H` of
`G-K`, put

    E_H={sigma in W : some y in H has d_G(sigma,y)>=r+1},
    q_H=|E_H|,
    lambda=2r+1-g.

For an ordinary component (`H` does not contain `x`) with `q_H>0` and an
attachment outside `z`, the tested target is

    q_H+lambda <= 2 mu_z(H).                                  (O)

Here `mu_z(H)` is the maximum order of an induced forest in `H` every component
of which has exactly one edge to `K-{z}`.  Several selected components inside
the same `H` are allowed.

## 2. Exact apex model and rooted triameter

Let `J=J_z(H)` be obtained from `G[H]` by adding an apex `rho` adjacent to every
vertex of `H` incident with `K-{z}`.  Then

    mu_z(H)+1 = maximum order of an induced tree of J containing rho.   (1)

For `y in H`, put `p(y)=d_J(rho,y)`, and define the rooted triameter

    P_z(H)=max_{u,v in H} [p(u)+p(v)+d_J(u,v)].                (2)

The exact metric-window lemma suggested by all current data is

    q_H+lambda <= P_z(H).                                     (MW)

This statement retains the registered window, the maximum-height realizer,
the residual hypotheses, the adjacent reserved root, and the ordinary-component
condition.  None may presently be dropped.

For `g>=7`, (MW) implies (O) rigorously.  The auxiliary graph `J` is
triangle-free: an apex triangle would expand to an ear of length three between
two cycle roots, forcing `g<=floor(g/2)+3`.  Choose `u,v` attaining (2).  The
three-in-a-tree theorem supplies an induced tree of `J` through `rho,u,v`.
Its minimal terminal subtree has at least

    ceil((p(u)+p(v)+d_J(u,v))/2)=ceil(P_z(H)/2)

edges.  Deleting `rho` gives a `z`-admissible forest of the same order, so

    2 mu_z(H) >= P_z(H) >= q_H+lambda.

The existence input is Theorem 1.2 of Derhy, Picouleau and Trotignon,
*The four-in-a-tree problem in triangle-free graphs*, arXiv:1309.0978.

Thus the only missing step in the `g>=7` ordinary branch is a proof of (MW).

## 2.1 Proven one-legal-root subcase

The full ordinary inequality (O) is proved, in every girth `g>=5`, whenever
`A(H)-{z}` consists of one cycle vertex `a`.  If `R=max_y d_J(rho,y)`, every
witness satisfies

    d_K(sigma,a) >= r+1-R.

The exact cycle layer count gives `q_H+lambda<=2R`, while a deepest rooted
geodesic deletes to a `z`-admissible tree of order `R`.  Hence
`q_H+lambda<=2R<=2mu_z(H)`.  The referee-ready proof is in
`ORDINARY_ONE_ROOT_LEMMA.md`.  Consequently (MW) is needed only for components
with at least two distinct legal roots.
## 3. Exact tests of (MW)

`verify_ordinary_triameter_n14.py` generated every connected triangle-free and
square-free graph of orders 5 through 14 using nauty `geng -c -t -f`.  It then
enumerated every residual shortest-cycle choice, every maximum-height realizer
and anchor, every safe adjacent `z`, and every ordinary component with nonempty
cover.  It computed all distances in `J` and (2) exactly.

Results:

* `g>=7`: 14,072 tests, minimum `(P-q-lambda)` equal to zero;
* `g=5,6`: 38,400 tests, minimum `(P-q-lambda)` equal to zero;
* failures: zero.

The result file is `ordinary_triameter_n5_14.json`, with SHA-256

    EA66CE0AFD3DFB8EF062B665609854EC62633FEDDD4F6FD1E39B580E14AFA913.

A separate mutation search, `search_ordinary_triameter_targeted.py`, checked
22,320 girth-safe cycle/ear mutations of order at most 28.  Of these, 3,811
entered the registered ordinary frontier.  Its minimum metric slack was zero
and it found no failure.  This is additional falsification evidence only.

## 4. Simpler metric routes are false

### 4.1 Rooted depth is insufficient, even for `g>=7`

Writing `R=max_y p(y)`, the replacement

    q_H+lambda <= 2R

is false.  The smallest exhaustive `g>=7` failure occurs at order 13 on graph6

    L???C@_UCg@W@g

with `g=7`, `r=e=3`, `D=5`,

    K={0,5,6,7,10,11,12},  x=m=0,  h=0,  delta=3,
    W={0,5,7,10,11},       z=7,
    H={1,2,3,4,8,9},       A(H)={10,11,12}.

Here `q_H=5`, `lambda=0`, and `R=2`, so `5>4`; nevertheless
`P_z(H)=6` and `mu_z(H)=5`.  The exhaustive depth audit through order 14 had
14,072 `g>=7` tests with minimum slack `-2`, and 38,400 `g=5,6` tests with
minimum slack `-3`.  Its result SHA-256 is

    4000A7A0EC543E8F5B53737B72A1451E780A07CA022C52CEB27CFE0119B8DD42.

### 4.2 Two extreme window witnesses are insufficient

Even when `W` is unwrapped, the witnesses at the two extreme covered positions
need not attain enough rooted perimeter.  The smallest `g>=7` exhaustive
failure found is graph6

    M???C@?g?oAoX??Y?

of order 14, with `g=8`, `r=e=4`, `D=6`, `h=1`, `delta=3`,

    K={1,3,5,8,10,11,12,13},  m=11, z=3,
    W={3,5,10,11,12},         H={0,2,7,9},
    A(H)={12,13},              E_H={3,5,10,11}.

The component is the path `7-0-9-2`, with its endpoints attached to 13 and 12.
The two extreme-position witnesses have rooted perimeter four, below
`q+lambda=5`.  Interior/depth pairs have perimeter five, so (MW) is exact.
The endpoint audit result has SHA-256

    A82B3EBD73AC091D462EF35584CA5148B3D3396F42AF8C5D6CAF2E5B09CC8CB3.

This certificate shows that a proof of (MW) must use the global maximum in (2),
not only two extreme cover witnesses.

### 4.3 The unrestricted/full-cycle extension is false

The natural statement formed by replacing `E_H subset W` with all of `K` is
false outside the registered setup.  On graph6 `I?ABAaoq?`, of order 10,

    g=6, r=3, D=4, e=1,
    K={1,2,3,6,7,8}, H={0,4,5,9}, z=2,

one has `q_full=4`, `lambda=1`, and `mu_z(H)=2`, so `5>4`.  Hence the residual
window must not be erased from (O) or (MW).  The corresponding diagnostic file
has SHA-256

    C6D47E83155EDF326FE0BDC5F8B8D3BA6D9907A1EF01E2FC54BF872C193F7B6E.

## 5. The short-girth conversion is a separate obligation

For `g=5,6`, apex triangles may occur, and the implication

    2 mu_z(H) >= P_z(H)

is false in both girths.

At `g=5`, graph6 `H?BD@hY` has a registered ordinary component with
`q=3`, `lambda=0`, `P=5`, and `mu=2`.  Thus `2mu-P=-1`, although (O) still
has slack one.

At `g=6`, graph6 `J?AA@AOw?V?` has a registered ordinary component with
`q=2`, `lambda=1`, `P=7`, and `mu=2`.  Thus `2mu-P=-3`, while (O) again has
slack one.

These examples show that `g=5,6` require a tailored apex-triangle structural
argument; proving (MW) alone does not close them.  The exact local arithmetic
needed is equivalent to

    g=5:  mu_z(H) >= r-1 + floor((q_H-1)/2),
    g=6:  mu_z(H) >= r-2 + floor(q_H/2).

No proof of these two bounds is supplied here.

## 6. Active component and the full global bridge

The local active inequality with the wrap correction included is false when
`q_X=0`.  On the independently checked 32-vertex graph supplied by the GPT Pro
consultation,

    g=9, r=e=6, D=9, K=(6,8,21,22,16,13,12,9,7),
    x=25, h=1, m=9, delta=5,

one has `q_X=0`, `c=max(0,2delta-g)=1`, and `mu_z(H_X)=1` for both adjacent
choices `z=7,12`.  Thus `q_X+c>2(mu_z(H_X)-h)` by one.

This does **not** refute WN2.  The full graph has

    S=9, M_z(K)=22,
    2(M_z(K)-h)-S-c=32.

Its large ordinary component has `q=9`, `lambda=4`, and `mu=15`, so (O) pays
the correction with slack 17.  This is exactly the already registered split:
when `q_X=0`, choose one positive ordinary component, use (O) there and
`q_H<=2mu_z(H)` on the others.  Since

    c=2delta-g <= 2r-g=lambda-1,

that ordinary component pays `c`; the active local correction is not needed.
The remaining active obligation is only the multiattachment case `q_X>0`.

An exact order-14 distribution audit found 40,390 safe active records.  Of
these, 25,120 had `q_X>0`; all 25,120 were multiattachment cases and none was
wrapped (`delta>floor(g/2)`).  Their girth counts were

    g=5: 11876,  g=6: 12290,  g=7: 920,  g=8: 32,  g=9: 2.

The result SHA-256 is

    1D6577E6B7B76F27130FD2720E041018258CEEC125815B582A48B5FBC73AF5E0.

The absence of wrapped positive active covers is finite evidence, not a
structural proof.

## 7. Remaining direct obligations

The current direct route has three load-bearing statements and no auxiliary
hierarchy:

1. prove (MW) for ordinary components with at least two distinct legal roots;
2. for `g=5,6`, prove the displayed tailored capacity bounds despite apex
   triangles; and
3. prove the unwrapped active multiattachment surplus for `q_X>0`.

For `g>=7`, item 1 plus the proved triangle-free apex conversion closes every
ordinary component.  For `q_X=0`, item 1 also closes the global wrap correction
without the false active-local inequality.  No claim beyond these conditional
bridges is made.