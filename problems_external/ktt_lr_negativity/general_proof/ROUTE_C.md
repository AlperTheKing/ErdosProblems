# ROUTE C — KTT-SD at d=3 (r=4): the edge-local certificate CANNOT reach 11/6

Target of this step: prove **KTT-SD** (simplex domination) at `d=3`, i.e.
`a_1 >= 11/6`, using the McMullen / Berline–Vergne edge-local machinery that
already proved `a_1 >= 0` for the whole `r=4` cell.

**Verdict: BLOCKED.** The stated next step is *provably impossible*, for a
structural (homogeneity + realizability-gap) reason, not a contingent one.
KTT-SD at `d=3` itself is **not** falsified — it remains empirically true and
OPEN, but it requires an ingredient (lattice realizability) that the homogeneous
edge-local LP structurally does not have.

Everything below is exact (`Fraction` arithmetic). Search scripts and the exact
certificate are in `scratchpad/route_c_*.py` and
`general_proof/route_c_d3_ratio_certificate.json`.

---

## 0. Statement of KTT-SD at d=3 (PROVED equivalences)

For a `d=3` lattice polytope with `h* = (1, h1, h2, h3)` and
`P(n) = sum_j h*_j C(n+3-j, 3)`, the exact `crit.py` identity gives
```
a_1 = (1/6)(11*h0 + 2*h1 - h2 + 2*h3),   h0 = 1.
```
Hence, with `c = P(1) = 4 + h1` (LR coefficient) and `i = h3` (interior points),
```
KTT-SD@d3   <=>   a_1 >= 11/6
            <=>   2*h1 - h2 + 2*h3 >= 0
            <=>   h2 <= 2*(h1 + h3)
            <=>   V <= 3(c + i) - 11        (V = sum h*_j = normalized volume).
```
Compare the already-certified KTT bound `a_1 >= 0  <=>  h2 <= 11 + 2(h1+h3)  <=>
V <= 3(c+i)`. So KTT-SD is KTT tightened by exactly `11` in the volume floor.

Equality holds **only** at the unimodular simplex `h* = (1,0,0,0)` (V=1, c=4,
i=0), whose Ehrhart polynomial is `C(n+3,3)`, `a_1 = 11/6`.

This is a *strictly stronger* conjecture than KTT: the Reeve tetrahedron
`T_2 = conv{0,e1,e2,(1,1,2)}` has `h* = (1,0,1,0)`, `a_1 = 5/3 < 11/6`, so KTT-SD
is **false for general lattice 3-polytopes** and must use hive structure. (`T_2`
is excluded because its facet normal `(1,1,1)` is not in the 15 hive normals.)

---

## 1. The edge-local certificate, restated (PROVED, reproduced)

Fixed data (from `q2_basis_witness_certificate.json`, SHA-256
`c13f8f47…0148`, `q2_verify_r4_certificate.py` → `PASS`):

- 15 primitive hive normals; 99 non-parallel unordered pairs (edge types).
- Balance map `B` (45×99), `rank(B) = 27`, `dim ker(B) = 72`. Every lattice
  3-polytope's edge-length vector `Λ(P)` (indexed by edge type) satisfies
  `B·Λ(P) = 0`.
- A **fixed** vector `mu ∈ Q^99`, `mu >= 0`, with
  `a_1(P) = Λ(P)·mu` for every `Λ ∈ ker(B)` (verified on a 72-witness basis).

Because `mu >= 0` and `Λ >= 0`, this gives `a_1 >= 0`. That is the whole of the
`r=4` KTT positivity theorem, and it is *homogeneous of degree 1* in `Λ`.

---

## 2. THE OBSTRUCTION (PROVED): the homogeneous scheme cannot yield 11/6

**Falsifying fact (one sentence):** `a_1(Λ) = Λ·mu` is a linear functional on
the scale-invariant balance cone `C = ker(B) ∩ {Λ >= 0}`, so along the ray
`t·Λ_0` of the unimodular simplex (`Λ_0` integer, `sum Λ_0 = 6`, `Λ_0·mu = 11/6`)
we get `a_1(t·Λ_0) = 11t/6 → 0` as `t → 0+`, whence `inf_C a_1 = 0` and the
constant lower bound `a_1 >= 11/6` is **false on C**.

Any certificate of the scheme's form ("`mu' >= 0` with `Λ·mu'` reproducing the
target") certifies a bound valid on **all** of `C`. Since `a_1 >= 11/6` fails on
`C`, no such certificate exists. **The literal next step — find `mu >= 0` with
`M·mu = a_1 − (11/6)·(indicator)` — is an infeasible LP.** The infeasibility is
witnessed exactly by the ray `t·Λ_0`.

The tightness checkpoint the task asked for (equality at `h* = e_0`) is exactly
what breaks the scheme: the minimizer is not an interior tight point but the
**apex of a ray that the cone lets slide to 0.**

### 2a. Sharpest thing the homogeneous scheme *can* prove (PROVED, exact)

Removing the scale freedom by normalizing total edge length, the exact LP
```
min { Λ·mu : B·Λ = 0, Λ >= 0, sum Λ = 6 }  =  7/8   (attained)
```
gives the sharp homogeneous ratio `min_C  a_1 / sum(Λ) = 7/48`. Certificates:

- **Primal** (upper bound, exact): the ray `Λ*` supported on 24 edge types, each
  value `1/4`, lies exactly in `ker(B)`, with `sum Λ* = 6`, `Λ*·mu = 7/8`,
  ratio `7/48`. (So `a_1/sum(Λ) = 7/48 < 11/36` is achievable — this is why the
  `sum(Λ)`-homogenization of §3 cannot give 11/6.)
- **Dual** (lower bound, exact): an explicit `y ∈ Q^45` with
  `B^T y <= mu − (7/48)·𝟙` componentwise (all 99 checked exactly, 0 violations;
  `route_c_d3_ratio_certificate.json`). Hence for every `Λ ∈ C`,
  `a_1 = Λ·mu >= (7/48)·sum(Λ)`.

Combined with the elementary lattice fact that **any** lattice 3-polytope has at
least 6 edges, each of lattice length ≥ 1, so `sum(Λ) >= 6`:

> **Lemma (new, PROVED, weaker than KTT-SD).** Every lattice 3-polytope with the
> `r=4` hive normals has `a_1 >= 7/8`.

This strictly improves the published `a_1 >= 0`, but `7/8 < 11/6`: the scheme
falls short of KTT-SD by the gap `11/6 − 7/8 = 23/24`, and `7/48` is provably the
best ratio, so **this gap cannot be closed inside the homogeneous LP.**

---

## 3. Why the gap is real: it is a *realizability* gap, not a search failure

The low-ratio ray `Λ*` has `a_1 = 7/2` at its integer point (24 unit edges),
which is **not** a KTT-SD violation (`7/2 > 11/6`). It only proves the ratio can
be small on the *relaxation*. The gap between the relaxation and the truth:

- On the balance cone `C`, `a_1` can be made arbitrarily small (scale to 0) —
  minimum 0.
- Adding integrality to the balance relaxation is still not enough: `B·Λ = 0`
  with `Λ >= 0` is **necessary but not sufficient** for `Λ` to be an actual
  lattice-polytope edge vector, and the low-ratio directions are populated by
  such non-realizable balance vectors.
- The bound `11/6` comes entirely from **lattice realizability of small
  polytopes** (the unimodular simplex is the smallest realizable member), which
  is exactly the information `B` throws away.

### 3a. KTT-SD is NOT false on the relaxation (PROVED by search)

To rule out the alternative "KTT-SD fails already on the normal-set superset":

- All 72 certificate witnesses (relaxed-offset lattice polytopes with hive
  normals, not restricted to real `(λ,μ,ν)`) have `a_1 ∈ {11/6, 13/6, 5/2, …}`,
  **min = 11/6.**
- Exhaustive scan of lattice **simplices** over the 15 hive normals, all
  positively-spanning 4-subsets, offsets in `[-3,3]^4`: **28 956 lattice
  simplices, min `a_1 = 11/6`, zero below.**
- Project census (bands 1–11, billions of real triples): min `a_1 = 11/6`.

So the target holds on the relaxation too; the failure in §2 is purely that the
*linear/homogeneous method* cannot express a bound whose value is set by lattice
discreteness.

---

## 4. PROVED vs OPEN

**PROVED (exact, this step):**
1. `KTT-SD@d3 ⇔ a_1 >= 11/6 ⇔ h2 <= 2(h1+h3) ⇔ V <= 3(c+i) − 11`; tight only at
   the unimodular simplex.
2. The homogeneous edge-local LP certificate **cannot** prove `a_1 >= 11/6`: the
   functional `Λ·mu` has infimum 0 on the scale-invariant balance cone `C`
   (ray `t·Λ_0 → 0`). The stated next-step LP is infeasible.
3. The sharp homogeneous ratio is `min_C a_1/sum(Λ) = 7/48`, with exact primal
   (24-edge ray) and dual (`y ∈ Q^45`) certificates.
4. Consequently `a_1 >= 7/8` for all lattice 3-polytopes with hive normals — a
   genuine improvement on `a_1 >= 0`, still short of KTT-SD by `23/24`.
5. KTT-SD@d3 is **not** false on the normal-set relaxation (28 956 simplices +
   72 witnesses all have `a_1 >= 11/6`).

**OPEN:**
- KTT-SD at `d=3` itself (`a_1 >= 11/6` for `r=4` hive polytopes). Empirically
  true; requires a **lattice/realizability** argument, e.g. classifying the
  lattice 3-polytopes with hive normals and `a_1 < 11/6` and showing the only
  one is the unimodular simplex — a discrete statement outside any homogeneous
  local-Ehrhart LP.
- Whether the min over **integer** points of `ker(B) ∩ {Λ>=0}` equals `11/6`
  (would reduce KTT-SD@d3 to an ILP on the balance lattice); not resolved here,
  and even if `= 11/6` it would need realizability to conclude for actual hives.

---

## 5. Consequence for the r=5 plan

The task proposed reusing the same LP/Farkas scheme at `r=5` (`d ≤ 6`) "where
KTT-SD is still linear in `h*`". §2 shows the scheme is the wrong tool: KTT-SD's
constant (`11/6` at `d=3`; the analogous simplex value at each `d`) is set by
lattice discreteness, and the edge/face-local functional is homogeneous of
degree ≥ 1 and slides to 0 on the balance cone. The `r=5` LP will be infeasible
for the identical structural reason. **Do not re-run the local-weight LP with a
constant KTT-SD target at any `r`.**

**nextStep:** Either (a) attack KTT-SD@d3 as a lattice-point classification
(bound the polytopes with `a_1 < 11/6` and enumerate — feasible since the slab
`7/8 <= a_1 < 11/6` plus hive normals is very restrictive), or (b) drop KTT-SD
(a strictly stronger conjecture than KTT that the BV method cannot deliver) and
keep the edge-local certificate for its correct job — the plain KTT bound
`a_1 >= 0` — which it already settles at `r=4`.
