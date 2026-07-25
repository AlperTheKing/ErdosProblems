# Bridge lemma: "unimodular vertex cones ==> a_1 >= 0 at dimension 3"

**Verdict: FALSE.  The lemma is refuted, not proved.**

Smoothness (every vertex cone unimodular, i.e. Delzant) does **not** imply
`a_1 >= 0` for lattice 3-polytopes.  An explicit, exactly verified
counterexample is given in Section 2, together with an infinite family.
Consequently no version of routes (a)-(d) of the task brief can work, and the
reason each of them fails is identified in Section 3.

Two further facts established here, both of which matter for the r=4 program:

* **The hypothesis of this task is itself false.**  Statement (E5) — "every
  simple vertex cone of an r=4 hive polytope is unimodular" — is disproved by
  an explicit hive: `lam = mu = (12,8,4,0)`, `nu = (18,14,10,6)` has the simple
  integral vertex `(26,32,38)` whose tangent cone has multiplicity 2
  (Section 4).  The earlier `vcheck.cpp` scan missed it because it tested
  simplicity by counting *tight rows*, not *edges*.
* **The route that does survive** is the fixed-normal-set edge-balancing
  certificate already in this directory
  (`q2_basis_witness_certificate.json`).  It never uses smoothness.  Section 5
  reports an independent, adversarial validation of it that it passed.

Everything below is exact (integers / `Fraction`).  No floating point was used
to decide anything.

---

## 1. The statement under test

> Let `Q` be a 3-dimensional lattice polytope such that at every vertex the
> tangent cone is unimodular (equivalently: `Q` is simple and the primitive
> edge directions at each vertex form a `Z`-basis of `Z^3`).  Then the linear
> Ehrhart coefficient `a_1(Q)` is nonnegative, i.e. `V <= 3(c+i)` in the
> notation of (E2).

This is exactly the Ehrhart-positivity question for smooth polytopes asked by
De Loera, Haws and Koeppe.  It is false in dimension 3.

## 2. The counterexample

For an integer `N >= 2` put

```
Q_N = { (x,y,z) in R^3 :  0 <= z <= 1,
                          x >= 0,
                          y >= 0,
                          x + (N-1) z <= N,
                          y - (N-1) z <= 1 }.
```

Equivalently `Q_N = conv(P_0 x {0}, P_1 x {1})` is the Cayley polytope of the
two rectangles `P_0 = [0,N] x [0,1]` and `P_1 = [0,1] x [0,N]`, which have the
same normal fan.

**Theorem A.**  For every `N >= 2`, `Q_N` is a 3-dimensional lattice polytope
with 8 vertices, 12 edges and 6 facets, and **every** vertex cone of `Q_N` is
unimodular.  Its Ehrhart polynomial is

```
L_{Q_N}(t) = 1 + a_1 t + a_2 t^2 + a_3 t^3,
     a_1 = -(N-1)^2/6 + N + 2 = -(N^2 - 8N - 11)/6,
     a_2 = 2N + 1,
     a_3 = (N^2 + 4N + 1)/6.
```

In particular `a_1 < 0` for every `N >= 10`, and

```
N = 10 :  L(t) = 1 - (3/2) t + 21 t^2 + (47/2) t^3,
          a_1 = -3/2,  V = 6 a_3 = 141,  c = 44,  i = 0,  3(c+i) - V = -9 = 6 a_1.
```

*Proof.*

(i) *Vertices and smoothness.*  The recession cone of `Q_N` is `{0}`
(`0 <= z <= 1` forces `d_z = 0`, then `x >= 0, x + (N-1)z <= N` forces
`d_x = 0`, likewise `d_y = 0`), so `Q_N` is a polytope.  Enumerating all
`C(6,3)` triples of the six inequalities and keeping the feasible solutions
gives exactly the 8 points

```
(0,0,0) (N,0,0) (N,1,0) (0,1,0) (0,0,1) (1,0,1) (1,N,1) (0,N,1),
```

all integral, each of them tight on exactly 3 of the 6 inequalities, and each
of those three triples of primitive outward normals has determinant `+-1`.
Being tight on exactly three facets means exactly three edges meet there, so
`Q_N` is simple; unimodularity of the triple of facet normals is equivalent to
unimodularity of the tangent cone.  Hence every vertex cone is unimodular.
(Machine-verified in exact arithmetic for `N = 1..14`;
`bridge_lemma/smooth3_counterexample.py`.)

(ii) *Ehrhart polynomial.*  The slice of `t Q_N` at height `z = k`
(`0 <= k <= t`, integer) is the axis-parallel rectangle

```
[0, Nt - (N-1)k] x [0, t + (N-1)k],
```

so

```
L(t) = sum_{k=0}^{t} (Nt - (N-1)k + 1) (t + (N-1)k + 1).
```

Faulhaber summation of this quadratic-in-`k` expression gives

```
L(t) = (t+1) ( (N^2 + 4N + 1) t^2 + (-N^2 + 8N + 5) t + 6 ) / 6,
```

whose expansion is the displayed cubic.  The linear coefficient is
`(-N^2 + 8N + 5 + 6)/6 = -(N^2 - 8N - 11)/6`, negative exactly when
`N^2 - 8N - 11 > 0`, i.e. `N >= 10`.  ∎

**Independent verification performed.**

* Two disjoint counting paths — the slice formula, and a brute-force triple
  loop over the H-representation — agree on `L(0..5) = 1, 44, 270, 820, 1835,
  3456` for `N = 10`.
* The cubic through `L(0..3)` reproduces `L(4)` and `L(5)`.
* Ehrhart reciprocity holds: `L(-1) = 0 = -#interior(Q_10)`,
  `L(-2) = -100 = -#interior(2 Q_10)`.
* The identity of (E2), `6 a_1 = 3(c+i) - V`, holds for every `N` tested.
* Symbolic re-derivation of the closed form with `sympy`.

Sign pattern for the family (exact):

```
N :  1     2      3     4     5     6     7    8     9    10     11     12
6a1: 18    23     26    27    26    23    18   11    2    -9    -22    -37
V :   6    13     22    33    46    61    78   97   118  141    166    193
c :   8    12     16    20    24    28    32   36    40   44     48     52
```

`a_2 = 2N+1 > 0` and `a_3 > 0` throughout, so `a_1` is indeed the only
coefficient that turns negative — consistent with (E2).

**Attribution.**  The existence of smooth lattice polytopes with negative
Ehrhart coefficients in dimension 3 is a published theorem of Castillo, Liu,
Nill and Paffenholz, *Smooth polytopes with negative Ehrhart coefficients*,
J. Combin. Theory Ser. A **160** (2018) 316-331, arXiv:1704.05532 ("examples of
smooth lattice polytopes in dimensions 3 and higher where each coefficient of
their Ehrhart polynomials that can potentially be negative is indeed
negative").  The family `Q_N` above was found and verified here independently;
it is offered as a self-contained witness, not as a new result.

**No conflict with the r=4 data.**  The facet normals of `Q_N` are
`(0,0,+-1), (-1,0,0), (0,-1,0), (1,0,N-1), (0,1,-(N-1))`.  For `N >= 3` the
last two do not belong to the 15-element r=4 hive normal set, so `Q_N` is not
an r=4 hive polytope and (E3) is untouched.

## 3. Why routes (a)-(d) cannot be repaired

**(a) "a clean lattice-length sum".**  The hoped-for shape was
`a_1 = sum_e ell(e) * w(cone(e))` with `w` depending only on the lattice
isomorphism class of the transverse/normal cone of the edge `e`.  For a smooth
3-polytope **all** edge normal cones are lattice-equivalent: if `n_1,n_2,n_3`
are the facet normals at a vertex of the edge `e = F_1 ∩ F_2`, smoothness makes
them a `Z`-basis of `Z^3`, and `Z^3 ∩ e^perp = Z n_1 + Z n_2`, so the pair
(lattice, normal cone) is isomorphic to `(Z^3, cone(e_1,e_2))` for every edge
of every smooth 3-polytope.  Such a formula would therefore force
`a_1 = w * sum_e ell(e) >= 0` — and it is false already for two of the smallest
smooth polytopes:

```
unit cube            : a_1 = 3,    sum_e ell(e) = 12,  ratio 1/4
unimodular triangular
  prism Delta_1 x [0,1]: a_1 = 5/2, sum_e ell(e) = 9,   ratio 5/18
```

So no `GL(3,Z)`-invariant edge weight exists.  (This is the standard caveat on
the McMullen / Berline-Vergne local formulas: the weight `alpha(F,P)` depends
on the normal cone as an actual cone in Euclidean `R^d` together with the
lattice; it is invariant under lattice-preserving *orthogonal* maps only, not
under all of `GL(d,Z)`.  Route (a) implicitly assumed the stronger
invariance.)

**(b) Riemann-Roch / nefness.**  For the smooth projective toric 3-fold `X` of
the normal fan with ample divisor `D`, Hirzebruch-Riemann-Roch gives

```
a_1 = (1/12) ( D . c_1(X)^2 + D . c_2(X) ),   c_2(X) = sum over invariant curves,
    = (1/12) ( D . (-K)^2 + sum_e ell(e) ).
```

Nefness of `D` is available, but the 1-cycle class `(-K)^2` is **not** nef in
general, and that is precisely what the counterexample exploits: for `Q_10`,
`12 a_1 = -18` and `sum_e ell(e) = 48`, so `D . (-K)^2 = -66`.  There is no
positivity statement about `(-K)^2` to lean on.  (Consistency check of the
formula on the unit cube: `D.(-K)^2 = 24`, `sum_e ell(e) = 12`,
`(24+12)/12 = 3 = a_1`.)

**(c) Literature.**  What is *proved* about Ehrhart positivity for smooth
polytopes in dimension 3 is the negative result cited above.  The De Loera-Haws-
Koeppe expectation is false; there is no theorem to import.

**(d) Face-lattice combinatorics.**  `Q_10` is combinatorially a cube: `f =
(8,12,6)`, identical to the unit cube, which has `a_1 = 3`.  Since `a_1` takes
both signs on one combinatorial type, no bound of the form `V <= 3(c+i)`
derived from the face lattice (plus smoothness) can exist.

## 4. The hypothesis of Proof Task 1 is false as well

The prior run's statement (E5) — every simple vertex cone of an r=4 hive
polytope is unimodular — is **refuted** by a genuine hive:

```
lam = mu = (12,8,4,0),  nu = (18,14,10,6),   |lam| + |mu| = |nu| = 48.
c(nu; lam, mu) = 50   (engine A and engine B agree; = L_Q(1) from hive4.py)
Q has 11 vertices, all integral, dim 3, V = 144, P(t) = 1 + 7t + 18t^2 + 24t^3.
```

At the vertex `v = (26,32,38)` six of the rhombus rows are tight, but only
three of them are facet-defining for the tangent cone; the tangent cone has
exactly **three** extreme rays

```
(0,1,1), (1,0,1), (1,1,0),        det = 2,
```

so `v` is a *simple* vertex with a *non-unimodular* cone of multiplicity 2.
The three edges are confirmed by the vertex list itself: `v + 2(0,1,1) =
(26,34,40)`, `v + 2(1,0,1) = (28,32,40)` and `v + 2(1,1,0) = (28,34,38)` are
all vertices of the same polytope.  The three facet normals of that cone are
exactly the three "odd" rows `(-1,-1,1), (-1,1,-1), (1,-1,-1)` — i.e. the
unique `|det| = 4` triple of the atlas is realised, and its ray determinant is
2.

Why the earlier scan reported the opposite: `vcheck.cpp` classifies a vertex as
simple when it has "exactly three distinct tight row directions" (see its own
comment on line 4 and the test on line 101).  A vertex with redundant tight
rows — which is what `v` is — is silently filed as non-simple and skipped, so
the scan's "every simple vertex cone is unimodular, 854,321,098 vertices"
is a statement about a proper subclass and carries no information about
vertices like `v`.  Vertex *integrality* (`max denominator 1`) is unaffected by
this bug.

Replay: `python bridge_lemma/hive_vertex_cones.py`.

## 5. What actually survives, and an adversarial check of it

The surviving route is the one that never mentions smoothness: fix the
15-element r=4 normal set, and use that for a **fixed** set of normals the
Berline-Vergne weight of an edge depends only on its unordered pair of facet
normals (the normal cone is then a literal fixed cone `cone(n_i,n_j)` in
`R^3` — this is legitimate exactly because the weight is *not* required to be
a `GL(3,Z)` invariant, cf. Section 3(a)).  Then `a_1` is a fixed linear
functional of the 99-vector `Lambda(P)` of edge lattice lengths, facet-boundary
closure confines `Lambda(P)` to `ker B` (dim 72), and a nonnegative `mu`
agreeing with the weight vector on `ker B` yields `a_1 = Lambda . mu >= 0`.

That is the content of `R4_EDGE_POSITIVITY_CERTIFICATE.md` /
`q2_basis_witness_certificate.json`.  It was stress-tested here with code
written independently of it:

1. `bridge_lemma/fixed_normal_linearity.py` — 250 lattice 3-polytopes
   `{x : n_i.x <= b_i}` with random `b in [0,5]^15` over the r=4 normals; own
   vertex enumeration, own facet/edge extraction, own brute-force lattice-point
   counting, own exact interpolation (each cubic re-validated at `t = 4`).
   Result: `rank(M) = 72`, `rank([M | a]) = 72`.  The second equality is a
   falsifiable prediction of the certificate's central claim (that `a_1` *is* a
   linear functional of `Lambda`) and it held on all 250 samples; all 99 edge
   types occurred.
2. `bridge_lemma/mu_crosscheck.py` — the certificate's own `mu` (all 99
   entries `>= 0`, minimum 0) evaluated on 200 further independently generated
   polytopes it had never seen: `Lambda(P) . mu = a_1(P)` **exactly, 200/200,
   zero mismatches**; observed minimum `6 a_1 = 11`, matching (E3).
3. `python q2_verify_r4_certificate.py` re-run from the repository root:
   `PASS`, `certificate_sha256=c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148`,
   `witnesses=72 witness_rank=72 balance_rank=27 kernel_dimension=72 min_mu=0`.
4. Of the 2829 random right-hand sides that produced a 3-dimensional polytope,
   1444 gave **non-integral** vertices.  So integrality of the vertices is a
   genuine extra hypothesis of the certificate, not a consequence of the normal
   set; for hives it must come from Buch's `n <= 4` integrality statement, and
   that import is where the remaining risk in the r=4 theorem sits.

## 6. Net effect on the r=4 program

* The bridge lemma requested by this task **does not exist**; the r=4 result
  cannot be obtained from unimodularity of vertex cones.
* The premise of Proof Task 1 is false in any case (Section 4), so nothing is
  lost.
* The r=4 claim now rests entirely on: (i) hive rule + saturation, (ii) Buch's
  integrality of hive-polytope vertices for `n <= 4`, (iii) existence of a
  local (McMullen/Berline-Vergne) formula whose edge weight depends only on the
  edge's normal cone, and (iv) the exact 72-witness / `mu >= 0` certificate.
  Items (i)-(iii) are literature imports; (iv) is machine-checked here twice
  independently.
* Note that (E5) being false does **not** endanger (iv): the certificate
  requires only that `Q` be a *lattice* polytope with normals in the fixed set.

## 7. Artifacts

```
bridge_lemma/smooth3_counterexample.py   Theorem A: exact vertices, unimodularity,
                                         two counting paths, reciprocity, N = 1..14
bridge_lemma/hive_vertex_cones.py        Section 4: tangent-cone extreme rays and
                                         multiplicities of a real r=4 hive polytope
bridge_lemma/fixed_normal_linearity.py   Section 5.1: rank(M) = rank([M|a]) = 72
bridge_lemma/mu_crosscheck.py            Section 5.2: certificate mu on unseen polytopes
```

All four run in exact arithmetic and print their own verdicts.
