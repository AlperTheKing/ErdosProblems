# Generalizing the r=4 positivity certificate toward full KTT

Date: 2026-07-22
Scope: King--Tollu--Toumazet coefficient positivity (literature item LR(iv);
Gao arXiv:2101.00984; De Loera--McAllister Conjecture 4.7). For partitions with
`|lam|+|mu|=|nu|`, the polynomial `P(n)=c(n*nu; n*lam, n*mu)` (a polynomial by
Derksen--Weyman) has no negative coefficient. Proved cases in the literature:
`c=2` (Ikenmeyer; Sherman). No counterexample known; a ~405,000,000-triple
project search found none.

All arithmetic below is exact (`fractions.Fraction` / integer / exact rational
rank). Floating point never decided anything. Every numeric claim is a replayed
constant from a named script; the certificate SHA-256s are pinned.

--------------------------------------------------------------------------------

## 0. Bottom line: what is and is not proved

**Proved** (each subject only to the standard external inputs -- the hive rule
and saturation; Derksen--Weyman polynomiality of `P(n)`; the McMullen /
Berline--Vergne local Ehrhart formula; and the PIP scaling lemma of
`../R5_LOCAL_METHOD_GATE.md` that transfers the lattice-cone local formula to
rational period-one hive polytopes):

1. **All of KTT through side size four.** Every stretched LR polynomial with
   partitions of length `<= 4` has nonnegative coefficients; in the
   full-dimensional (`dim=3`) case all four coefficients are strictly positive.
   Files: `../r4_reeve/R4_KTT_THEOREM.md`, `../r4_reeve/R4_STRUCTURAL_PROOF.md`.
   Equivalent volume inequality `V <= 3(c+i)` for these polytopes.

2. **Rank-uniform top four coefficients.** For every full-dimensional side-`r`
   hive of intrinsic dimension `D`, the coefficients of `n^D, n^{D-1}, n^{D-2},
   n^{D-3}` are strictly positive, uniformly in `r`. The first two are volume
   and half boundary area; the last two are exact rank-uniform BV positivity of
   every closed codim-2 and codim-3 hive normal cone (`../UNIFORM_CODIM2_POSITIVITY.md`
   min weight `1/12`, sharpened to `1/9` at r=5; `../UNIFORM_CODIM3_BV_REPORT.md`
   min weight `1/264`).

3. **One further coefficient at full-dimensional side five.** For a
   full-dimensional side-5 hive (`D=6`), the coefficients of `n^6,n^5,n^4,n^3,n^2`
   are all positive. The new content over item 2 is `e_2` (codim-4), proved in
   `../R5_CODIM4_LOCAL_POSITIVITY_REPORT.md`. Only the linear coefficient `e_1`
   remains open in this class.

4. **Side-5 codim-2 (`e_4`) by an actual exact LP.** The `r5_certificate`
   machinery here re-derives `e_4 > 0` for every full-dimensional side-5 hive
   via a spanning witness set and a nonnegative certificate; `BUILD_R5.md`,
   `verify_r5_certificate.py -> PASS`, certificate SHA-256
   `752ea056085f587eb7399db5ce3c2a370b5f15e2f104982db0524d2c54783755`.

**Not proved:**

- The **full KTT conjecture, at any rank** (it is a single statement over all
  `r` at once; see Section 6).
- The **side-5 linear coefficient** `e_1` for full-dimensional hives. Its faces
  are edges, whose normal cones are 5-dimensional; the BV weight there is **not
  sign-definite**, and neither the codim-5 balancing matrix nor its BV weights
  nor the edge-type enumeration were built.
- **Non-full-dimensional side-5 hives**, for ALL coefficients beyond intrinsic
  dimension two (the rank-uniform top-four theorem is proved for
  full-dimensional hives only and does not apply here; intrinsic dimensions at
  most two are positive by the segment/Pick formulas, but for intrinsic
  dimensions three to five the facet normals are projections of the rank-5
  rows onto the affine hull, not the fixed atlas, so no certificate covers
  them). The dimension drop happens on Weyl-chamber walls, and Horn
  factorization does not reduce them: `lam=(4,3,3,1,0), mu=(4,2,1,1,0), nu=(6,5,4,2,2)` has hive
  dimension 3 while all 142 essential Horn inequalities are strict
  (`../R5_LOWERDIM_HORN_GAP.md`).
- **Anything for `r >= 6`** beyond the rank-uniform top-four coefficients.

--------------------------------------------------------------------------------

## 1. Why the r=4 proof does not extend verbatim

The r=4 theorem (`../r4_reeve/R4_KTT_THEOREM.md`) reduces KTT-for-length-<=4 to a
single functional on a single class of polytopes. Three facts, each verified in
this project, break that reduction at `r>=5`. One of them is not actually an
obstacle once the PIP scaling lemma is applied; the report states each honestly.

### (B1) Buch integrality is false at r=5 -- but is dissolved, not fatal

Buch's statement (used verbatim in the r=4 proof) that every hive polytope of
side `<= 4` is a lattice polytope is **false at side 5**. Verified
counterexample:

```
lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)
dim Q = 4, c = 5, 7 vertices, 2 of them half-integral, h* = (1,0,1,0,0),
normalized volume 2, P(n) = (n+1)(n+2)(n^2+3n+6)/12,
L(0..6) = 1,5,16,40,85,161,280.
```

Reproduced exactly by the `hive5` engine (`BUILD_R5.md` Section 2). So side-5
hive polytopes are **rational**, not lattice, polytopes, and the naive lattice
local formula and Stanley `h*>=0` do not apply as literally stated.

Exhaustive basis-set constants for `A_5` (not a sample):
`C(30,6)=593,775` subsets, `192,658` nonsingular; `|det|` histogram
`1:146656, 2:40320, 3:2892, 4:2502, 5:18, 6:252, 7:18`, **max |det| = 7**;
**max vertex denominator = 7** (Smith normal form, extremal witness rows
`[1,12,13,16,18,21]`, det 7, invariant factors `(1,1,1,1,1,7)`). Restricting the
right-hand side to the actual rank-14 hive rhs sublattice changes none of these.
The project's earlier "max denominator 3" was a sampling artifact.

**Why this is not fatal.** The **PIP scaling lemma** (`../R5_LOCAL_METHOD_GATE.md`,
proved there): for a rational period-one polytope `P`, pick `q` with `qP` a
lattice polytope; then `L_{qP}(n)=L_P(qn)`, so `e_k(qP)=q^k e_k(P)`; dilation
preserves the normal fan and every intrinsic normal cone and scales each
`k`-face volume by `q^k`; applying the lattice-cone local formula to `qP` and
dividing by `q^k` recovers the identical cone-only local formula for `P`.
Verified twice: for the two examples above, `a_k(qQ)=q^k a_k(Q)` holds for all
`k`. Consequently **no rational-polytope local Ehrhart theory and no bound on
the denominators is needed**; the same move also removes the Buch dependence
retroactively from the r=4 proof. B1 should be struck from the obstacle list.

### (B2) The one-coefficient reduction dies -- four negatable functionals

At r=4, `dim Q <= 3` and only the linear coefficient can be negative
(`a_3=V/6>0`, `a_2=` half boundary area `>0`, `a_0=1`). At r=5 the ambient
dimension is `D=6`, and only `e_0=1`, `e_6=vol>0`, `e_5=` half boundary area
`>0` are automatic. The four coefficients `e_1,e_2,e_3,e_4` can each be negative
in principle, and each needs its own certificate. There is no single-equation
analogue that closes all four at once. (Of these four, `e_4,e_3,e_2` are now
proved positive as in Section 0; `e_1` is open.)

### (B3) Type explosion

At r=4 an "edge type" (for the only nontrivial coefficient) is an unordered
pair of facet normals: `15` primitive normals, `99` nonparallel pairs = **99
edge types**. At r=5 the primitive-normal count is `27`. For codim-2 (`e_4`) a
type is still a normal pair -- `342` ridge types -- so `e_4` stays tractable.
But an actual **edge** (1-face, governing `e_1`) has a 5-dimensional normal
cone: there are `52,680` rank-5 normal subsets, `557` distinct primitive edge
directions, and the number of normals vanishing on a given direction ranges
`5..18`. So an edge normal cone is a 5-dimensional cone generated by up to 18 of
the 27 normals, and the edge-type count is `>= 557` and much larger. Types are
determined by **sets** of normals, not pairs.

--------------------------------------------------------------------------------

## 2. What the method reduces to for each fixed r: a finite LP

The single generalizing fact is that **`A_r` is fixed once `r` is fixed**
(entries in `{-1,0,+1}`; only the integral right-hand side varies, linearly and
homogeneously in `(lam,mu,nu)`). Hence the set of possible normal cones of
`k`-faces is finite, and the McMullen / Berline--Vergne local formula writes

```
e_k(P) = sum over k-faces F of  alpha(normal cone of F) * vol_Z(F),
```

with `alpha` depending only on the cone. The facet-Minkowski closure relations
(each 2-face's boundary edges close up, propagated to each facet) give a linear
balancing system `B * Lambda(P) = 0` on the face-volume vector `Lambda(P) >= 0`.

**Reduction.** For each fixed `(r,k)`, "is `e_k >= 0` for every hive polytope?"
reduces to the finite question

```
does the coset  alpha + rowspace(B)  contain a componentwise-nonnegative vector?
   (equivalently: exists mu >= 0 with  M mu = a  on a witness set whose
    face-volume rows span ker(B), where a = M alpha are the local coefficients)
```

If yes, `e_k >= 0` is **proved** for that `(r,k)`, on the whole realizable
`Lambda`-space, including rational hives (via the PIP scaling lemma). This is
the r=4 template, verbatim, transported to `R^D` with normals in `N_r`.

**Exact sizes measured.**

| r | k | face | normals | types (LP columns) | B shape | rank B | dim ker B | status |
|---|---|------|---------|--------------------|---------|--------|-----------|--------|
| 4 | 1 | edge (codim-2) | 15 | 99 | 99 -> 45 | 27 | 72 | proved (cert, 72 witnesses) |
| 5 | 4 | ridge (codim-2) | 27 | 342 | 405 x 342 | 120 | 222 | proved (this dir) |
| 5 | 3 | codim-3 | 27 | Gram-class 4320 | -- | -- | -- | proved (uniform, min 1/264) |
| 5 | 2 | codim-4 | 27 | 17550 4-tuples | -- | -- | -- | proved (realizability-filtered) |
| 5 | 1 | edge (codim-5) | 27 | >= 557 | not built | -- | -- | **OPEN** |

For the r=5 `e_4` row the balancing rank bound is tight: each facet block has
rank `<= 5`, and 27 blocks share 15 wedge-coordinate dependencies, giving
`rank(B) <= 27*5 - 15 = 120`, attained exactly (`balance5.py`,
`../r5_ridge_balance_gate.py`).

--------------------------------------------------------------------------------

## 3. Outcome of the r=5 LP that was run (coefficient e_4)

Run object: `run_r5_lp.py`, assembled certificate `e4_certificate.json`
(SHA-256 `752ea056...`), independent replay `verify_r5_certificate.py -> PASS`,
LP summary `R5_CERTIFICATE.json` (SHA-256 `0299438e...`).

**Verdict: FEASIBLE.** A constructive exact rational feasible point is `mu =
alpha` (every entry `>= 1/9 > 0`). Verified exactly:

- `rank(B)=120`, so `dim ker(B)=222`;
- witness face-volume rows have `rank(M)=222=dim ker(B)`, i.e. they span `ker(B)`
  (222 witnesses = 197 hive + 25 auxiliary lattice simplices);
- every witness `Lambda` lies in `ker(B)` (`B Lambda = 0` exact);
- the local identity `e_4 = alpha . Lambda` holds on all 222 witnesses, with the
  witness `e_4` values taken **independently** from lattice-count Ehrhart
  interpolation -- a genuine falsifiable check that `alpha` is the correct BV
  weight, cross-checked against both LR engines (`a4_A==a4_B==cert`);
- `mu >= 0`, `M mu = a`, and `mu - alpha` in `rowspace(B)`.

Proof chain for any hive `P`: `Lambda(P) in ker(B) = rowspan(M)` and
`Lambda(P) >= 0`; `mu >= 0` with `mu - alpha` perp `ker(B)` give
`mu . Lambda(P) = alpha . Lambda(P) = e_4(P) >= 0`.

**Honest reading of this outcome.** The `e_4` LP is **trivially feasible because
`alpha` itself is already componentwise `>= 1/9 > 0`**, so `mu - alpha = 0` and
the balancing rowspace is never exercised. `e_4` is exactly the case that
already worked at r=4 (there too every edge weight is `>= 1/9`, so the r=4
balancing certificate was likewise not the binding constraint). **This LP does
not test the failure mode.** The load-bearing, still-open case is `e_1` (edges,
5-dimensional normal cones), whose `alpha` is not sign-definite; its balancing
LP is where infeasibility with a Farkas dual could occur, and that machinery
does not exist.

--------------------------------------------------------------------------------

## 4. Farkas recipe status and how far the hunts got

**No Farkas certificate was produced**, because the only LP actually solved
(`e_4`) is feasible, and the genuinely decidable frontier LP (`e_1`) was never
built. `Farkas hunts: []`.

The nearest the project came to a "counterexample recipe" is at **codim-4
(`e_2`)**, and it is instructive that it did **not** yield one:

- The local Euler--Maclaurin recursion independently found **132 negative
  saturated four-normal cells**, minimum `alpha = -66821/2858240` at normal IDs
  `(0,7,23,25)`. A naive `alpha + rowspace(B)` LP over these cells would read
  **INFEASIBLE** and hand back a Farkas dual.
- But every such dual is **not** a KTT counterexample recipe. The negative cells
  **cannot be full normal cones of actual hive faces**: exact slack-closure
  identities (e.g. `s_3+s_4=s_10+s_14`, `s_15+s_3=s_10+s_12`) force additional
  tight rows, raising the normal rank to `>= 5` (excluding codim-4) in 54 of 192
  expanded cases, and embedding the rest in one of 513 pointed rank-preserving
  closed supersets, **all positive**, minimum `+739/86400`. A concrete realized
  instance: cell values `39/3200, -349/28800, 3587/120960` sum on the genuine
  closed face cone to `17977/604800 > 0`.

**Lesson for the failure-mode framing.** At codim `>= 4` the naive coset LP is
not the right object: a naive Farkas dual must be **filtered through
face-realizability** before it exhibits a shape a counterexample must have.
Termwise simplicial positivity is already false at r=5; the proofs survive
because negative cells are forced into positive closed cones. So "LP infeasible
=> counterexample recipe" holds only after the realizability filter, and at the
open coefficient `e_1` neither the LP nor the filter has been constructed.

--------------------------------------------------------------------------------

## 5. Assessment of a uniform-in-r route

A single statement suffices for full KTT (`../R5_LOCAL_METHOD_GATE.md`,
`../GENERAL_KTT_PROOF_STATUS.md`):

**Uniform Hive Todd Effectivity (UHTE) / Hive Todd Effectivity (HTE).** For
every rank `r`, every nonempty rank-`r` hive `H` of dimension `d`, and every
face `F` with `1 <= dim F <= d-2`, the BV/Todd weight `alpha(N_F(H)) >= 0`.
By the PIP scaling lemma this implies coefficientwise nonnegativity of every
stretched LR polynomial. Equivalently, by rational Farkas duality, for every
codimension `q` and every 2-connected primitive-interior closed flat-rhombus
coarsening `Sigma`, `<a_q, w> >= 0` for every nonnegative balanced realizable
face weight `w` (i.e. `a_q + partial_q^T y >= 0` for some `y`).

No proof of UHTE and no refuting negative realizable balanced weight is
currently available. Six rank-uniform shortcuts to UHTE were **exactly
obstructed** in this project (each with a replayable witness):

1. **Generic type-A Todd / cocircuit balancing.** The globally nonnegative
   `p=L^4` in the `A4` Dahmen--Micchelli space maps under the Todd operator to
   `N^4+4N^3+3N^2-2N-6/5` (negative linear and constant terms). So nonnegativity
   + generic type-A balancing cannot imply HTE. `../PLANAR_TODD_BRIDGE_AUDIT.md`.
2. **Network-flow / Lidskii positivity.** A simple side-4 hive tangent cone has
   determinant 2; ordinary network-flow cones are unimodular in their intrinsic
   flow lattice; the extra rhombus-capacity constraints block transfer.
   `../FLOW_BRIDGE_OBSTRUCTION.md`.
3. **Generic Hilbert-ring properties.** CM + rational singularities + negative
   `a`-invariant do not control monomial coefficients: the `Q_20` Hibi ring is
   standard/normal/CM/rational/Koszul/Gorenstein with `a<0` yet has Hilbert-
   polynomial linear coefficient `-168011/330`.
   `../HILBERT_HURWITZ_BRIDGE_REPORT.md`.
4. **Matroid / secondary-fan Todd effectivity.** A genuine side-4 hive face has
   a `U_{2,4}` tight-normal restriction, so the tight-row matroid is not graphic,
   cographic, or regular; generic permutohedral Todd effectivity and matroid
   Ehrhart positivity are themselves false. `../MATROID_TODD_BRIDGE_AUDIT.md`.
5. **Known positive tableau / representation recursions.** Marked-order-polytope
   Ehrhart positivity counts all SSYT, not a fixed-content LR fiber; the
   fermionic formula has an `n`-dependent configuration set (Kirillov's own
   stretch-coefficient positivity is a separate open conjecture); Racah--Speiser
   / Kostka reduction is signed with a `rho` shift; branching/Pieri require
   inversion (`s_{11}=s_1^2-s_2`). `../LR_POSITIVE_RECURSION_AUDIT.md` (+ erratum).
6. **Hurwitz stability.** Would imply KTT but is a strictly stronger unproved
   statement with no invariant-theoretic source; treating its Hurwitz
   determinants rank by rank is another unbounded hierarchy.

### What the King--Tollu--Toumazet factorisation actually gives

The relevant factorisation is the **Horn-facet product theorem** (King, Tollu,
Toumazet, *Factorisation of Littlewood--Richardson coefficients*, JCTA 116
(2009) 314--333; the earlier SLC 54A (2006) paper is the hive-model /
polynomiality source, not the factorisation). It states: when an **essential
Horn inequality is saturated** (equality), `c^nu_{lam,mu}` factors as a product
of smaller LR coefficients indexed by the two sides of that Horn facet.

Exactly what it yields for KTT:

- **It is a genuine positive rank reduction on the boundary.** Homogeneity
  preserves the Horn equality under stretching, so on a saturated essential Horn
  facet `P(n)` factors as a **product of lower-side stretching polynomials**. A
  product of monomial-nonnegative polynomials is monomial-nonnegative, so KTT on
  the boundary follows by induction from the side-4 base case.
- **It does not reach the interior.** A triple is *primitive* precisely when
  every essential Horn inequality is strict; there the factorisation gives no
  reduction. The obstruction appears already at the first rank beyond side 4:
  `lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)` has all 142 essential side-5 Horn
  inequalities strict (minimum integral slack 1) yet a degree-4 stretching
  polynomial `(n+1)(n+2)(n^2+3n+6)/12`. So Horn factorisation cannot reduce even
  this genuine side-5 case to side 4.
- **It also fails to remove the lower-dimensional caveat.** The dimension drop
  at `lam=(4,3,3,1,0), mu=(4,2,1,1,0), nu=(6,5,4,2,2)` occurs on Weyl-chamber
  walls with all Horn inequalities strict, so factorisation is not triggered
  there either (`../R5_LOWERDIM_HORN_GAP.md`).

Net: the factorisation reduces the **separating/boundary** coarsenings in the
UHTE Farkas dual, which is why the load-bearing UHTE case is stated as the
**2-connected primitive interior**. It supplies the induction's boundary step,
not its interior.

--------------------------------------------------------------------------------

## 6. Proving finitely many r never proves the conjecture

KTT is a single universally quantified statement over **all** ranks `r`
simultaneously. Each fixed `r` is an independent finite problem: the normal set
`N_r`, the balancing matrix, the face-type list, and the BV weights are all
`r`-specific and grow without bound (`15 -> 27 -> ...` normals; `99 -> 342 ->
...` codim-2 types; `>= 557` edge types already at r=5). A proof for `r <= r_0`,
however large `r_0`, says nothing about `r_0 + 1`. The fixed-codimension
cascade (prove `e_4`, then `e_3`, then `e_2`, then `e_1`, then repeat at r=6,
...) is likewise unbounded in **both** directions and is not a proof of the
conjecture. Only a **rank-uniform** theorem -- UHTE, or an equivalent
hive-specific positive decomposition valid for all `r` at once -- can close KTT.
The finite per-`r` LPs are diagnostic and produce partial theorems and targeted
counterexample geometry; they are not, and cannot be assembled into, a proof of
the full conjecture.

--------------------------------------------------------------------------------

## 7. Ranked next steps

1. **Build the `e_1` (codim-5, edge) machinery at r=5 and run its exact LP.**
   This is the only remaining coefficient for full-dimensional side 5 and the
   first place the balancing LP is load-bearing (BV weight not sign-definite).
   Deliverables: enumerate the `>= 557` edge types (5-dim normal cones generated
   by up to 18 of the 27 normals); compute exact BV weights for 5-dim cones;
   build the codim-5 balancing matrix `B_1` and its rank/kernel; assemble a
   witness set spanning `ker(B_1)`; solve `alpha + rowspace(B_1) >= 0` exactly.
   Either outcome is decisive: FEASIBLE proves full-dimensional side-5 KTT
   outright; INFEASIBLE yields the first genuine Farkas dual -- **which must then
   be run through the codim-4-style face-realizability filter** (Section 4)
   before it is treated as a counterexample recipe, and only a *realizable*
   negative balanced weight refutes UHTE at r=5.

2. **Close the non-full-dimensional side-5 gap.** Prove (or classify) an
   intrinsic-lattice contraction theorem for Weyl-chamber-wall hives, since Horn
   factorisation provably does not reach them (`../R5_LOWERDIM_HORN_GAP.md`).
   Without this, even a complete full-dimensional side-5 result leaves side 5
   itself open.

3. **Attack UHTE directly for the 2-connected primitive-interior coarsening.**
   This is the identified sufficient rank-uniform statement (Section 5). The six
   audited shortcuts are ruled out, so this needs a genuinely new generator
   theorem for the balanced-weight cone `W_q`, or a realizable negative balanced
   weight that refutes it. Pair item 1's data with this: a realizable Farkas
   dual at r=5 would be the sharpest available refutation target.

4. **Targeted counterexample hunt guided by the codim-4 negative cells.** The
   132 negative saturated cells (min `-66821/2858240`) and the realized
   `-349/28800` cell describe precisely which face types must carry volume for a
   coefficient to be pushed negative. Search partition triples whose hives
   realize a negative BV cell as close to a **full** face normal cone as the
   slack-closure identities permit -- the most concrete counterexample geometry
   the project has, even though every closure examined so far repaired to
   positive.

5. **Stress-test the shortcut obstructions for a hive-restricted survivor.**
   Several obstructions (planar Todd `p=L^4`, matroid `U_{2,4}`, Hibi
   `-168011/330`) kill only the *generic* statement; none is shown to be an
   actual hive chamber polynomial. Determining whether the negative witnesses lie
   in the much smaller cone of genuine hive volume-chamber polynomials would
   either revive one route or convert each obstruction into a sharper
   hive-specific separation.

--------------------------------------------------------------------------------

## Replay index

```
python hive5.py                              # fixed A_5, 27 normals, atlas sha 0e024bcd...
python validate_hive5.py 240 130 20260722    # GATE 1 vs both LR engines (670 triples, 0 mismatch)
python validate_stretch5.py                  # GATE 2 stretched profiles vs both engines
python balance5.py                           # B: 405x342, rank 120, ker 222
python verify_r5_certificate.py              # independent replay of e4 certificate -> PASS
python run_r5_lp.py                          # e_4 coset LP -> FEASIBLE (mu=alpha, min 1/9)
python ../r5_local_gate.py                   # A_5 det histogram, PIP scaling gate
python ../uniform_codim2_gate_canonical.py   # rank-uniform codim-2, bound 1/12, r5 min 1/9
python ../uniform_codim3_gram_lemma.py       # rank-uniform codim-3, min 1/264
python ../r5_codim4_bv_independent_v2.py     # codim-4 negative cells + realizability filter
python ../r5_lowerdim_horn_factorization_gap.py  # strict-Horn dim-drop example
```

Pinned artifacts: `e4_certificate.json` SHA-256
`752ea056085f587eb7399db5ce3c2a370b5f15e2f104982db0524d2c54783755`;
`R5_CERTIFICATE.json` SHA-256
`0299438e8aa4d856a83547d024d549e1b2d4cd1359ab7f2e478a9cd2383ce15a`;
r4 certificate SHA-256
`c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148`.
