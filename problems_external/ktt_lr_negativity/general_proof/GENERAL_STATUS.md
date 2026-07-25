# GENERAL_STATUS — the FULL King–Tollu–Toumazet positivity conjecture

Date: 2026-07-22
Target: for EVERY Littlewood–Richardson triple in EVERY rank (no bound on the
number of parts), with `|lam|+|mu|=|nu|`, the stretched coefficient
`P(t)=c(t*nu; t*lam, t*mu)` — a genuine polynomial by Derksen–Weyman — has no
negative ordinary monomial coefficient.
Literature: LR(iv), OPEN. Gao arXiv:2101.00984; De Loera–McAllister Conj 4.7;
origin King–Tollu–Toumazet, CRM Proc. Lecture Notes 34 (2004). Proved special
cases in the literature: `c=1` (trivial, `P≡1`) and `c=2` (Ikenmeyer; Sherman).

All arithmetic in the supporting work is exact (`Fraction`); floating point
searched, never decided. Every polytope constructor used was validated to equal
the LR coefficient from BOTH engines (`engine/lr_hive.exe`,
`engine/engineB_lrrule.py`) on ≥300 varied triples.

---

## 1. BOTTOM LINE (no inflation)

**The full conjecture is OPEN. Nothing about the general (all-rank) statement is
proved in this project beyond what is dimension- or rank-bounded.** Specifically,
what is established:

- **Literature (all rank):** `c=1` and `c=2` only (Ikenmeyer; Sherman). These
  are the only unconditional all-rank cases known to anyone.
- **This project, bounded rank:** KTT for every triple with **at most four
  parts** (equivalently `V ≤ 3(c+i)` at `d=3`). Independent audit verdict:
  *a correct theorem with a valid, independently reproduced proof that is not yet
  self-contained* — it cites the published Berline–Vergne / McMullen local
  Ehrhart formula (never reproved or machine-checked here) and the certificate
  variant leans on Buch's one-line integrality remark; these are fixable gaps,
  not errors (`r4_reeve/AUDIT_VERDICT.md`, `r4_reeve/R4_STRUCTURAL_PROOF.md`).
- **This project, all rank but only the extreme coefficients:** for every rank
  and intrinsic dimension `D`, the coefficients of `n^D, n^{D-1}, n^{D-2},
  n^{D-3}` are positive (leading/volume `q=0`, second `q=1`, and rank-uniform
  exact BV positivity of every closed codim-2 and codim-3 hive normal cone), and
  the constant term is `P(0)=1`. Consequence: **KTT holds for every LR triple in
  any number of parts whose hive polytope has intrinsic dimension `≤ 4`.**
  (`UNIFORM_CODIM2_POSITIVITY.md`, `UNIFORM_CODIM3_BV_REPORT.md`,
  `GENERAL_KTT_PROOF_STATUS.md` §2.) Same BV-foundation caveat as above.
- **This project, full-dimensional side five (`d=6`) only:** coefficients of
  `n^6,n^5,n^4,n^3,n^2` positive; **only the linear coefficient `a_1` remains
  open** in that class (`R5_CODIM4_LOCAL_POSITIVITY_REPORT.md`).

No general-rank statement covering all coefficients exists. A ~405,000,000-triple
search and a 581,713-hive-polytope LP-free screen produced zero negative
coefficients, zero negative `h*_j`, and zero lattice-inequality violations; **no
theorem forces this**, and it is not evidence for the conjecture (see §4).

---

## 2. ROUTES — exact status, required lemma, referee findings

### Route A (Horn/KTT factorisation) — BLOCKED
- **Status.** Valid, positivity-preserving REDUCTION, not an induction on `r`.
  The KTT factorisation is now a theorem (King–Tollu–Toumazet, JCTA 116 (2009)
  314–333; geometrically Sherman arXiv:1505.06551): at a saturated ESSENTIAL
  (`c=1`) Horn wall, `P = P1·P2`, a product of two nonnegative-coefficient
  polynomials. Verified exactly here: `P=P1·P2` in 744/744 non-primitive triples;
  essential-Horn enumeration cross-validated against engine A both directions on
  600 triples, 0 contradictions.
- **Decisive obstruction.** Recursive factorisation stops on PRIMITIVE triples
  (every essential Horn inequality strict), which keep as many parts as
  themselves. Fraction of triples whose primitive leaves all have `≤4` parts:
  n=4 100%, n=5 36.9%, n=6 16.1%, n=7 7.4% — i.e. 63/84/93% of n=5/6/7 retain a
  primitive `≥5`-part leaf. Both known `r≥5` pathologies (F3) are themselves
  primitive.
- **Needed lemma.** *Primitive positivity lemma:* every primitive triple has no
  negative coefficient. By the factorisation theorem this is EQUIVALENT to full
  KTT; it does not reduce the number of parts, so it is exactly as hard as the
  original.
- **Deepened (`general_proof/ROUTE_A.md`).** Executed the primitive attack.
  Primitivity CONCENTRATES the danger rather than excluding it: primitive corpus
  reaches near-negativity ratio `maxR = 0.98710`; non-primitive caps at
  `0.90142`; every `R>0.90` triple is primitive. The only near-negative
  coefficient is the LINEAR one, and it grows with Horn slack (deep chamber
  interior / high volume), away from factorisation walls. Sharpened the whole
  full-dim side-five class to the scalar knife-edge
  `sup_{gcd-reduced primitive 5-part} R_1 ≤ 1`, explicit form
  `24 h*_2 + 12 h*_4 + 120 h*_6 ≤ 1764 + 120 h*_1 + 12 h*_3 + 24 h*_5`.
  Proved (P4) that NO `h*`-shape property closes it: order polytope
  `O_{P_{7,7}}` has palindromic + unimodal + centre-peaked `h*` yet
  `a_1 = -3041/1430 < 0` (recomputed exactly). Verdict BLOCKED: sharpens to a
  knife-edge and rules out shape lemmas; yields neither proof nor counterexample.

### Route B (import Ehrhart positivity from alcoved polytopes) — DEAD
- **Status.** Premise refuted. Hive polytopes are close to alcoved: of the 15
  primitive `r=4` normals, 12 are type-`A3` alcoved (`±e_i`, `±(e_i-e_j)`), only
  3 are "odd" `(±1,±1,±1)`-type (F4). But alcovedness does NOT imply Ehrhart
  positivity: order polytopes are alcoved (Lam–Postnikov math/0501246) and are
  NOT Ehrhart positive (Liu–Tsuchiya arXiv:1806.08403). All seven Table-1 linear
  coefficients reproduced exactly here (75/22, 61751/15015, -3041/1430,
  -1633/2145, -9905/286, -1285677/4862, -135276175/58786), plus Reeve controls
  `a_1 = 2 - q/6`.
- **Consequence.** The Berline–Vergne / McMullen local weights are NOT
  nonnegative on the family of cones with normals in `{±e_i, ±(e_i-e_j)}`
  (`a_1 = Σ_F relvol(F)·α(N(F))` with `relvol≥0`, and alcoved `a_1<0` exists).
  So there is nothing generic to import; positivity must be hive-specific.
- **Referee correction (MAJOR_REVISION G1), incorporated.** The earlier phrasing
  "the minimal dimension of a non-Ehrhart-positive ALCOVED polytope is EXACTLY
  14" is an overreach. Liu–Xin–Zhang (arXiv:2412.07164) prove only that ORDER
  polytopes of dimension `≤13` are Ehrhart positive; order polytopes are a
  PROPER subclass of alcoved polytopes. Correct statement: **14 is the minimal
  dimension of a non-Ehrhart-positive ORDER polytope, hence an UPPER bound (not
  necessarily the value) for non-positive alcoved polytopes.**
- **Retarget.** The `a_1<0` mechanism requires LARGE normalized volume (volume
  floors `V_floor(d,1)` = 11 at d=3, 147/10 at d=6, 7381/252 at d=10,
  ~696.83 at d=15, ~1531.05 at d=21), disjoint from the thin/low-volume Reeve
  regime the campaign had swept. This retarget feeds the disproof track (§4).

### Route C (edge-local certificate proves KTT-SD, `a_1 ≥ 11/6`, at `d=3`) — BLOCKED
- **Status (`general_proof/ROUTE_C.md`).** The homogeneous edge-local LP
  certificate that proves `a_1 ≥ 0` for all `r=4` hives CANNOT reach `a_1 ≥ 11/6`:
  `a_1(Λ)=Λ·mu` is homogeneous of degree 1 on the balance cone `C=ker(B)∩{Λ≥0}`
  and slides to 0 along the unimodular-simplex ray, so `inf_C a_1 = 0`; the
  literal next-step LP is infeasible. The sharpest the scheme proves is the new
  (exact primal 24-edge ray + dual `y∈Q^45`) lemma **`a_1 ≥ 7/8` for every
  lattice 3-polytope with hive normals** — a genuine improvement over the
  published `a_1 ≥ 0`, short of `11/6` by `23/24`, and `7/48` is provably the
  best ratio.
- **Why blocked, not disproved.** `11/6` is set by lattice REALIZABILITY (the
  smallest realizable member is the unimodular simplex), information the balance
  matrix `B` discards. KTT-SD@d3 is NOT false on the relaxation (28,956 lattice
  simplices over the 15 normals + 72 certificate witnesses + census bands 1–11
  all have `a_1 ≥ 11/6`).
- **Needed lemma / verdict.** KTT-SD is STRICTLY STRONGER than KTT (Reeve `T_2`:
  `a_1=5/3<11/6`) and is NOT required for the conjecture. Do not re-run the
  homogeneous local-weight LP with a constant KTT-SD target at any `r`
  (infeasible for the same structural reason). If pursued, KTT-SD@d3 must be a
  lattice-point classification, not an LP.

### GHTE program (the unifying rank-uniform frontier) — OPEN, one direction proved
- **Bridge (Theorem 1, `GHTE_REDUCTION_AND_ENDPOINTS.md`).** For each `q`, with
  the complete intrinsic hive normal fan, primitive quotient-lattice balance
  matrix `B_{H,q}`, and Berline–Vergne vector `a_{H,q}`, the GLOBAL-HIVE-TODD-
  EFFECTIVITY statement is `∃ y: a_{H,q} + B_{H,q}^T y ≥ 0` (GHTE). By exact
  rational Farkas duality this equals `⟨a_{H,q},w⟩≥0` for all `w≥0`, `Bw=0`.
  Paired with the nonnegative balanced face-volume weight, **GHTE in every `q`
  and every complete hive normal fan implies full KTT.** (`(HTE)` in
  `GENERAL_KTT_PROOF_STATUS.md` is the same statement.)
- **Proved endpoints (Proposition 3).** GHTE holds at `q=0` (`a_0=1`), `q=1`
  (all rays BV `1/2`), and `q=d` (constant term `=1`, connected max-cone
  adjacency). Frontier: `2 ≤ q ≤ d-1`.
- **Proved descent (Theorem, `GHTE_REFINEMENT_DESCENT_NOTE.md`).** GHTE descends
  from a refining fan to every coarsening via the invariant-cycle pushforward
  (`S_q t_q(Σ')=t_q(Σ)`, normal-cone additivity of the simple BV valuation).
  **This direction is one-way.**
- **Ascent is FALSE unconditionally.** The braid fan refines an effective
  simplex fan yet the permutohedral Todd class is non-effective for all `d≥24`
  (Castillo–Liu arXiv:1909.09127 Thm 1.3). So GHTE can hold coarse and fail after
  refinement; no rank-uniform wall-crossing proof may use a generic coarse-to-
  fine lift. The remaining obligation is a **hive-specific upward lift across
  every support-number wall**.
- **Dead sub-route.** Canonical local ear/strip deletion is dead: for
  `lam=mu=(3,2,1,0), nu=(5,4,2,1)` the closed edge cone has BV value `1/6` but
  the literal deletion correction is `-1/3` (`-1/12` even under fibre
  normalization), and the same boundary rhombus occurs in closed `r=4` cones
  with primitive quotient multiplicities 2 and 1, so a planar ear label does not
  determine the saturated lattice correction
  (`CLOSED_CONE_EAR_DELETION_OBSTRUCTION.md`).

### Referee findings (both), incorporated
- **Referee 1 (REJECT).** "REJECT strictly in the sense that the FULL conjecture
  is neither proved nor disproved here." Independent from-scratch re-derivation
  (own Yamanouchi LR counter agreeing with both engines) found **NO computational
  error and NO overclaim**; every route honestly labeled BLOCKED/DEAD/OPEN. This
  is not a rejection of any sub-result; it records that there is no proof of the
  target to accept and no near-complete proof to send back.
- **Referee 2 (MAJOR_REVISION).** Scope/honesty PASSES: nothing proved for
  bounded `r` is presented as proving the conjecture; empirical regularities are
  NOT cited as evidence for it; no false general claim exists. Every literature
  number and the F1 moment criterion re-verified symbolically. One real overreach
  found — the alcoved-vs-order dimension-14 claim (G1 above), now corrected.

---

## 3. SINGLE MOST TRACTABLE OPEN LEMMA (across all routes)

**Lemma L (full-dimensional side-five linear coefficient / GHTE degree `q=d-1=5`
for `r=5`, `d=6`).**

> For every full-dimensional 5-part LR triple `(lam,mu,nu)`, the linear Ehrhart
> coefficient of `P(n)=c(n*nu;n*lam,n*mu)` is nonnegative, i.e.
>
> ```
> a_1 ≥ 0   ⟺   24 h*_2 + 12 h*_4 + 120 h*_6  ≤  1764 + 120 h*_1 + 12 h*_3 + 24 h*_5
>           ⟺   sup over gcd-reduced primitive 5-part triples of  R_1 ≤ 1,
> ```
>
> where `R_1 = (negative-weight h*-mass)/(positive-weight h*-mass)` and
> `a_1 < 0 ⟺ R_1 > 1`.

Why this one: it is a single exact rational per triple; the other five
coefficients `n^6..n^2` of this entire class are already proved positive, so L is
literally all that stands between the current results and full KTT for
full-dimensional side five; the instruments (`general_proof/ehrhart.py`, exact
`h*` interpolation, `hstar_spread/crit.py`) are validated 320/320 and both-engine
cross-checked; and L is exactly GHTE at `q=5` restricted to `d=6` — the smallest
open case of the rank-uniform frontier. It is NOT closable by any `h*`-shape
argument (Route A P4), so a proof must use the hive-specific quantitative content
(`det ≤ 2` tangent-lattice data). Caution: L is a genuine knife-edge — the
validated `R_1` climb reaches `0.998087` without crossing `1`, so L is
simultaneously the most tractable lemma AND a live falsification lead.

A strictly-stronger alternative (KTT-SD@d3 as a lattice classification of hive-
normal 3-polytopes with `7/8 ≤ a_1 < 11/6`) is finite and feasible but proves
more than KTT needs; it is a lower-value target than L.

---

## 4. DISPROOF TRACK

- **Mechanism sought.** A negative LINEAR coefficient `a_1 < 0`. F1 rules out
  negativity of the top two coefficients except in the thin/low-volume Reeve
  regime (which the proved codim results and primitivity exclude), so the only
  live negativity mechanism is `a_1<0`, which the volume floor
  `V > H_d / max_j(-[n^1]C(n+d-j,d))` shows requires LARGE normalized volume
  (floors 11, 147/10, 7381/252, ~696.83, ~1531.05 at `d=3,6,10,15,21`).
- **How far it got.** Validated, both-engine `R_1` hill-climb (r=5, d=6) reached
  `R_1 = 0.998087` at normalized volume `M=696,860` with `a_1` strictly positive
  throughout and geometrically shrinking gains (extrapolated greedy plateau
  `≈0.9986 < 1`); no crossing of 1 anywhere. The ~405M-triple sweep (volume-
  limited) and the 581,713-polytope LP-free screen found zero negatives. No
  counterexample exists on any searched trajectory. The high-volume/deep-interior
  primitive cell (Route B retarget) is where any counterexample would live and is
  only partially explored.
- **Ferroni precedent — implication for the prior.** Ehrhart positivity is FALSE
  for general lattice polytopes (Reeve `T_q`, `a_1 = 2 - q/6 < 0` for `q≥13`), so
  any proof must use hive structure. More pointedly, the analogous Ehrhart-
  positivity conjecture for MATROID polytopes (De Loera–Haws–Köppe) — a natural,
  highly structured family that looked positive — was DISPROVED by Ferroni
  (~2021–2022); order polytopes (alcoved, structured) fail from dimension 14.
  These are precisely families where large "no counterexample" numerics preceded
  refutation. **Therefore the prior that KTT is FALSE is live and non-negligible;
  the 405M/581k null results carry the same (limited) evidential weight that was
  available for matroids before Ferroni.** The disproof track is a first-class
  objective, not a formality.

---

## 5. A PROOF FOR BOUNDED `r` IS NOT A PROOF OF THE CONJECTURE

The target is ALL partitions with no bound on the number of parts. As parts grow,
the hive polytope's intrinsic dimension `d = (r-1)(r-2)/2` grows without bound, so
new coefficients (and new cone types at every codimension) appear that no
fixed-`r` or fixed-dimension certificate covers. Concretely:

- The `r≤4` theorem, the "intrinsic dimension `≤4`" all-rank result, and the
  full-dim side-five result are each dimension- or rank-bounded and do NOT imply
  any triple outside their scope.
- Route A supplies NO induction on `r`: both known `r≥5` pathologies (F3: the
  half-integral-vertex `r=5` non-lattice example with `h*=(1,0,1,0,0)`, and the
  determinant-2 `r=4` tangent cone) are PRIMITIVE, hence already fully reduced.
- GHTE descent is ONE-WAY, and generic ascent is FALSE (Castillo–Liu, `d≥24`).
  A rank-uniform proof requires a hive-specific upward lift that does not yet
  exist.

**Any statement of the form "KTT is proved for `r ≤ N`" (any finite `N`), or "for
all triples of dimension `≤ D`", must never be described as proving the
conjecture. An overclaimed general theorem is a critical failure.**

---

## 6. RANKED NEXT ACTIONS (with expected cost)

1. **Falsification push at high volume / high `r`** (highest value given the
   Ferroni prior). Extend the validated `R_1`-climb into `r=6, d=10` with a
   raised node cap plus simulated-annealing restarts; treat any `R_1>1` as an
   exact KTT counterexample, recomputed on BOTH engines at two held-out
   dilations. *Cost: LOW implementation (instruments validated), MODERATE compute
   (engine-A/B runs, days).* This is the only search reaching the deep-interior
   high-volume primitives where §4 shows any counterexample must live.

2. **Direct `a_1` attack for full-dim side five (Lemma L / GHTE `q=5`).** Write
   `a_1 = Σ_edges len(edge)·α(5-dim normal cone)` and bound it using the
   `det ≤ 2` hive tangent-lattice data, not any `h*`-shape/moment inequality
   (Route A P4 shows shape cannot work). *Cost: HIGH analytic; MODERATE compute
   to build/validate the edge-cone census.* Success closes full-dim side five.

3. **GHTE hive-specific upward lift across one support-number wall.** Construct an
   explicit effective lift `t_q(Σ) → t_q(Σ')` for a single wall crossing that
   uses hive structure (the descent theorem gives the reverse for free). *Cost:
   HIGH, open-ended research.* This is the true rank-uniform frontier; a single
   worked wall would be the first genuinely general step.

4. **Bounded exact skew-Kostka negativity gate.** Using the proved homogeneous
   embedding `K_{nλ/nβ, nw} = c^{nR}_{nλ,nS}`
   (`KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md`), run one bounded census for a negative
   stretched skew-Kostka coefficient (a literal KTT counterexample). *Cost:
   MODERATE compute; MUST stop at its stated exit; a null result stays finite.*

5. **KTT-SD@d3 as a lattice classification** (Route C nextStep a). Enumerate
   lattice 3-polytopes with the 15 hive normals and `a_1 < 11/6` in the slab
   `7/8 ≤ a_1 < 11/6`; the slab-plus-normals constraint is very restrictive.
   *Cost: MODERATE finite ILP.* Lower value: proves a statement strictly stronger
   than KTT needs.

6. **Close the BV-foundation gap in the `r≤4` proof.** Reprove or machine-check
   the Berline–Vergne / McMullen local formula and remove the Buch integrality
   dependence, making the `r≤4` theorem self-contained (audit gap, not error).
   *Cost: HIGH formalization effort.* Needed for a submission-grade `r≤4` result;
   does NOT advance general KTT.

---

## Source map (this project)

- `GENERAL_KTT_PROOF_STATUS.md` — proved scope, `(HTE)` frontier, six audited
  rank-uniform obstructions.
- `general_proof/ROUTE_A.md` — primitive-case deepening, `R_1` knife-edge, P1–P5.
- `general_proof/ROUTE_C.md` — KTT-SD@d3 homogeneous-LP obstruction, `a_1≥7/8`.
- `GHTE_REDUCTION_AND_ENDPOINTS.md`, `GHTE_REFINEMENT_DESCENT_NOTE.md`,
  `GHTE_FOUNDATION_CONTRACT.md`, `APPROACH_REGISTRY_GENERAL_KTT_V3.md` — GHTE
  bridge, endpoints, one-way descent, false ascent.
- `r4_reeve/AUDIT_VERDICT.md`, `r4_reeve/R4_STRUCTURAL_PROOF.md` — `r≤4` theorem
  and independent audit.
- `R5_CODIM4_LOCAL_POSITIVITY_REPORT.md`, `UNIFORM_CODIM2_POSITIVITY.md`,
  `UNIFORM_CODIM3_BV_REPORT.md` — top-coefficient results.
