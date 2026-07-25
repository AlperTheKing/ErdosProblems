# TIER-0 REPORT — King–Tollu–Toumazet positivity, hive-polytope route

Target: a counterexample to KTT positivity (literature item LR(iv); open — Gao
arXiv:2101.00984, De Loera–McAllister Conj. 4.7): partitions (λ,μ,ν) with
|λ|+|μ|=|ν| whose stretched Littlewood–Richardson polynomial
P(n) = c(nν; nλ, nμ) has a strictly **negative** monomial coefficient.

All arithmetic below is exact. Floating point never decided anything. A null
result proves nothing about the conjecture and is not stated as support for it
(see §8).

---

## 1. The exact tier-0 criterion and why it is the cheapest possible target

P(n) is the Ehrhart polynomial of the Knutson–Tao hive polytope Q(λ,μ,ν):
Q is rational (not in general a lattice polytope), its constraint matrix depends
only on r = #parts(ν), its right-hand side is linear and homogeneous in (λ,μ,ν),
so Q(nλ,nμ,nν) = nQ, and P has Ehrhart period 1 (Derksen–Weyman). Write
d = deg P = dim Q and let h* = (h*_0,…,h*_d) be the h*-vector of P.

Fixed identities (period 1):
- h*_0 = 1
- **h*_1 = c − (d+1)**, where c = P(1) = #(lattice points of Q)
- **h*_d = #(relative-interior lattice points of Q)** (Ehrhart–Macdonald reciprocity)

Negativity of the top sub-leading coefficients, with u_j := 2j − (d+1) and ⟨·⟩
the h*-weighted average:
- [n^{d−1}]P < 0  ⟺  ⟨u⟩ > 0
- [n^{d−2}]P < 0  ⟺  ⟨u²⟩ < (d+1)/3

Under **only** Stanley nonnegativity (h*_j ≥ 0 — the one inequality that holds for
every period-1 rational polytope), the minimum-volume configuration that makes
[n^{d−2}]P < 0 is

    Σ h* = 3,   h* = (1, 0, …, 0, 2)   at any d ≥ 4.

The campaign-wide volume thresholds that previously ruled this out
(Σ h* ≥ 13 at d=3, 27 at d=4, 19 at d=5, 37 at d=6, 25 at d=7) rest entirely on
inequalities valid **only for lattice polytopes** — Stanley monotonicity, Hibi,
and h*_d ≤ h*_1. Hive polytopes are provably not lattice polytopes in general
(the refuter below has half-integral vertices), so those thresholds are not
theorems here.

The (1,0,…,0,2) shape forces **h*_d > h*_1**, i.e. a polytope with exactly d+1
lattice points at least one of which is interior. For a lattice polytope this is
impossible (its ≥ d+1 vertices are boundary lattice points, so any interior
lattice point forces c > d+1). For a rational polytope with non-lattice vertices
it is not excluded. Hence the hunt:

- **TIER0**  ⟺  c = d+1 (h*_1 = 0)  **and**  h*_d > 0 (≥ 1 interior lattice point).
  This makes Σ h* = 3, h* = (1,0,…,0,2 when d≥4), and [n^{d−2}]P < 0 outright.
- **JACKPOT** ⟺ any triple with **h*_d > h*_1** (escapes the lattice-polytope
  inequalities; proves the campaign thresholds do not bind).

This is the cheapest target because it is the smallest normalized volume
(Σ h* = 3) at which Stanley nonnegativity alone permits a negative coefficient;
the earlier campaign only ever flagged the different, stronger condition
h*_1 < 0 (c ≤ deg P). Search is confined to d ≥ 4, i.e. r ≥ 5. (r=4/d=3 is closed
separately: at d=3, h*_1=0 forces h* = (1,0,q−1,0) by White, and an r=4
empty-simplex hive polytope has volume ≤ 4 < 13.)

### Exact geometric reformulation used throughout
With B := #(lattice points on the **relative boundary** of Q),

    h*_d − h*_1 = (d+1) − B.

Therefore **JACKPOT ⟺ B ≤ d**, and **TIER0 ⟺ c = d+1 with ≥1 interior point
(B = d exactly)**. Verified with 0 violations on 175,859 exactly-screened records.
This replaces the h*-vector hunt with one integer quantity B.

---

## 2. Was h*_d > h*_1 (JACKPOT) achieved?

**No.** Across the entire dedicated tier-0 hunt (seven families, > 13.4 million
records/triples examined; see §6), the prior 581,713-record LP-free baseline, and
the 616,485-record corpus re-mine:

- 0 JACKPOT, 0 TIER0, 0 negative monomial coefficient, 0 negative h*_j.
- **Global record minimum of h*_1 − h*_d = 0. It was never negative.**

### The record-minimum attainer
h*_1 − h*_d = 0 is attained by the base refuter itself

    λ=(2,2,1), μ=(4,3,2,1), ν=(5,4,3,2,1)
    r=5, d=4, c=5=d+1, h*=(1,0,1,0,0), h*_1=0, h*_d=0
    P(n) = (n+1)(n+2)(n²+3n+6)/12  (live engine-A profile P(0..3)=1,5,16,40; confirmed §7)

Via the identity above, B = d+1 = 5: this polytope has exactly one relative-boundary
lattice point **too many** for a jackpot, and no interior lattice point at all. It
is a margin-0 near-miss, one interior lattice point short of TIER0, not a hit.

Margin 0 is attained two ways: trivially at d=1 (a segment, where h*_1 = h*_d
identically and a jackpot is structurally impossible), and non-trivially by
c = d+1 polytopes at d ≥ 2 with h*_d = 0 (h*_1 = 0 exactly). Representatives of the
second, informative kind, all with h*_1 − h*_d = 0:

| triple | r | d | c | h* | note |
|---|---|---|---|---|---|
| λ=(2,2,1), μ=(4,3,2,1), ν=(5,4,3,2,1) | 5 | 4 | 5 | (1,0,1,0,0) | base refuter, canonical attainer |
| λ=(3,1), μ=(5,3,2,2,1), ν=(6,3,3,2,2,1) | 6 | 2 | 3 | (1,0,0) | c=d+1, no interior point |
| λ=(5,4,1), μ=(5,4,3,2,2,1), ν=(7,6,5,4,3,2) | 6 | 6 | 7 | (1,0,0,0,0,0,0) | deepest d with h*_1=0 |

In every one of these, c = d+1 (h*_1 = 0) is reached but h*_d = 0: exactly the
c=d+1 half of TIER0 with the interior-point half absent.

---

## 3. The one non-null result: a rigorous obstruction for the full-dimensional case

**Theorem 1.** Let Q = Q(λ,μ,ν) have no implicit equalities, i.e.
dim Q = D := (r−1)(r−2)/2 (Q full-dimensional in the interior-site space). If Q has
a lattice point in its interior, then B ≥ 2d, hence h*_1 − h*_d ≥ d − 1 ≥ 0. **No
JACKPOT and no TIER0 exists in the full-dimensional case, at any r.**

*Proof.* Every rhombus inequality has coefficient vector in {−1,0,+1}^D, so a unit
step ±e_v changes each slack by at most 1. Slacks at integer hives are integers,
so an interior point p has every slack ≥ 1 ⟹ p ± e_v ∈ Q for all D sites. Walking
p + k·e_v, each decreasing slack drops by exactly 1, so the last feasible step lands
on ∂Q. The 2D endpoints differ from p in one coordinate with a fixed sign, hence are
pairwise distinct boundary lattice points. ∎

Machine-verified on λ=μ=(11,8,5,2), ν=(15,13,10,7,4): D=d=6, no implicit
equalities, 2 interior lattice points, 22 distinct boundary lattice points recovered
(≥ 2d = 12).

**Consequence and scope (honest).** The entire tier-0 population is confined to the
**non-full-dimensional** hive polytopes (d < D). The known refuter has D=6 but d=4,
i.e. d < D — precisely the regime Theorem 1 does not cover. General polytope theory
cannot close this regime either: the period-1 rational triangle with vertices
(1,−3/2),(2,−2),(0,1) realizes the TIER-0 shape abstractly (P(n)=n²+n+1, c=3=d+1,
h*=(1,0,1), interior point (1,−1), B=2=d). What breaks that abstract example inside a
hive polytope is integrality of slacks — the ingredient powering Theorem 1 — which
holds only in the full-dimensional case. **The non-full-dimensional case remains open
by proof; it has only been sampled by exact search.**

Supporting exact structure (verified, used by the screen): if Q has an interior
lattice point then the rhombi tight at every lattice point equal the implicit
equalities (Lemma A — the enumeration screen computes the interior/boundary split
exactly, no false negatives); and q(x,y) = −(x²+xy+y²) is an integral hive with all
slacks 1 (Lemma B), so in the full-dimensional case h*_d is itself an LR coefficient
of the shift λ_i+(2i−1), μ_i+(2i−1−r), ν_i+(2i−1), forcing all three partitions to
have consecutive gaps ≥ 2 as a necessary condition for an interior lattice point. The
c=1 route is closed by Fulton's conjecture (Knutson–Tao–Woodward): c=1 ⟹ P≡1 ⟹ d=0.

---

## 4. Non-lattice hive polytopes: measured rate, and co-occurrence with interior points

Non-lattice polytopes (at least one non-integer vertex) identified in the families
that tracked latticeness:

| family | records | non-lattice found |
|---|---|---|
| refuter cell (§6.1) | 595,672 | 1,416 |
| r=6 full census (§6.3) | 697,963 | 203 |
| FAM4 asymmetric-weight (§6.4) | 413,751 | 73 |
| fam5 short-vs-long (§6.5) | 7,020 | 5,913 |
| fam6 minimal-lattice-point (§6.6) | 480,178 exact screens | 715 |
| **total (tracked families)** | | **≥ 8,320** |

Non-latticeness is common and shape-dependent: the short-vs-long family fam5 is
~84% non-lattice, the exhaustive symmetric-neighborhood families far sparser. (The
r=5 full census recorded 0 in its non-lattice field; that field must be reading a
narrower quantity or was not populated, because the verified half-integral refuter
lies inside that census — so it is not evidence that r=5 non-lattice polytopes are
absent. Non-latticeness of hive polytopes is established by the refuter itself.)

**Did non-latticeness ever come with an interior lattice point (h*_d > 0)?**

- In the exhaustive families that tracked both (refuter cell, r=6 census), the
  non-lattice polytopes (1,416 and 203) had **no** interior lattice point for any
  d ≥ 2: h*_d ≡ 0 there.
- Interior lattice points at d ≥ 2 **do** occur, but only in the targeted
  asymmetric/interior-hunt families, and were **always** accompanied by strictly
  more surplus boundary lattice points, i.e. h*_1 ≥ h*_d (never h*_d > h*_1):
  FAM4 max h*_d = 11 at d=2 with h*_1 = 23; fam5 max h*_d = 6 at d=2 with h*_1 = 15;
  fam7 (interior-point hunt) max engine-audited h*_d = 126 at d=6 with h*_1 = 2193.

So non-latticeness by itself never produced h*_d > h*_1, and every interior lattice
point found was outnumbered by boundary lattice points. No non-lattice polytope
combined c = d+1 with an interior point.

---

## 5. (moved into §6)

---

## 6. Families searched — exact counts and which were exhaustive

Every screen used the mandated LP-free instrument (exact profile via engine A,
exact interpolation, two held-out points, exact h*, exact interior/boundary split).
No LP dimension oracle and no simplex filter were used at any decision point.

### 6.1 Refuter cell — EXHAUSTIVE (≤4-box perturbation shells)
λ=(2,2,1), μ=(k,3,2,1), ν=(k+1,4,3,2,1), k=4..60, exhaustive ≤2-box and ≤4-box
perturbation shells. 595,672 records (97,120 with d ≥ 2 in the mandated cell).
max h*_d over the mandated cell = 0 (no interior lattice point on any d ≥ 2 member);
h*_d = 5 appears only in a thickened sub-family (t=4) outside the cell, always with
h*_1 ≫ h*_d. min h*_1 − h*_d = 0 (74,283 records at d ≥ 2; 8,353 at d ≥ 4).
Non-lattice: 1,416. Verdict: dead for tier-0.

### 6.2 r=5 full census — EXHAUSTIVE (|ν| ≤ 27)
ALL triples (λ,μ,ν) with |λ|+|μ|=|ν|, r = #parts(ν) = 5, |ν| ≤ 27. 9,315,870 records.
356,099 with d ≥ 3, and max h*_d over the entire census restricted to d ≥ 3 is 0 (not
one interior lattice point). Global max h*_d = 2, only at d=1 (forced margin 0).
min h*_1 − h*_d = 0. Verdict: exhausted, dead for tier-0.

### 6.3 r=6 full census — EXHAUSTIVE (|ν| ≤ 22)
ALL non-empty r=6 triples, |ν| ≤ 22. 697,963 records (the 84 engine-A node-cap skips
all resolved via engine B; zero unresolved). For every d ≥ 2, h*_d = 0; global max
h*_d = 1, only at d=1. min h*_1 − h*_d = 0 (230,617 records at margin 0). Non-lattice:
203. Verdict: exhausted, dead for tier-0.

### 6.4 FAM4 asymmetric-weight — sweep (not exhaustive)
|μ| ≥ 2|λ|, r ∈ {5,6,7}. 413,751 records. Per-dimension max h*_d: d=1→4, d=2→11,
d=3→8, d=4→1, d=5→6, d=6→2, d≥7→0. min h*_1 − h*_d = 0 (121,188 records; 0 at every
d in 1..8). Non-lattice: 73. Never negative.

### 6.5 fam5 short-vs-long — sweep (not exhaustive)
λ with 2–3 parts vs μ with 4–7 parts, ν with 5–7 parts. 7,020 records. max h*_d = 6
at d=2 (h*_1 = 15). min h*_1 − h*_d = 0 (2,556 records; deepest at d=6, c=7=d+1,
h*=(1,0,0,0,0,0,0)). Non-lattice: 5,913.

### 6.6 fam6 minimal-lattice-point hunt — targeted (not exhaustive)
Stage-1 exact c = P(1) filter, then exact screen. 1,481,329 generated triples,
480,178 exact screens. h*_d = 0 for every d ≥ 2 record; global max h*_d = 1 at d=1.
min h*_1 − h*_d = 0. Non-lattice: 715. Not exhausted; carriers structurally pinned
(tier-0 requires h*-degree s = d, not met at d ≥ 2 here).

### 6.7 fam7 interior-point hunt — targeted (not exhaustive)
Screen for h*_d > 0 first, then audit. 929,162 records. Engine-audited max h*_d = 126
at λ=μ=(16,12,8,4), ν=(24,20,16,12,8), d=6, c=2200, h*_1 = 2193 (margin 2067). (The
run's ray-extrapolated 15,631 is a dilation-budget artifact — h*_d is unbounded along
any dilation ray — not a structural record.) Large interior-point counts occur; every
one carried far larger h*_1.

Additional exact section-4 hunt in hive space (engine-A prefilter for nonempty
2 ≤ c ≤ 200, exact enumeration, exact interior/boundary split): r=5 34,404 nonempty
triples → 1,130 with a relative-interior lattice point; r=6 36,995 → 219; r=7 23,289
nonempty triples (interior-candidate pass incomplete). 651 targeted candidates screened
exactly. Result: 0 JACKPOT, 0 TIER0.

---

## 7. Instrument provenance and live cross-check

Instrument: `problems_external/ktt_lr_negativity/purged_region/lpfree_screen.py`
(LP-free; the earlier campaign screen that used an LP dimension oracle / simplex
filter systematically purged exactly this population and was discarded).
Cross-checkers: engine A `engine/lr_hive.exe`, engine B `engine/engineB_lrrule.py`
(partitions comma-separated: `"2,2,1" "4,3,2,1" "5,4,3,2,1"`).

Live cross-check performed for this report (engine A):
P(1)=5, P(2)=16, P(3)=40 for the base refuter — identical to the recorded profile and
to (n+1)(n+2)(n²+3n+6)/12. The detector is proven to fire when a hit exists
(VALIDATION_TIER0.txt V3): synthetic rational triangle conv{(−1/2,−1/2),(0,1),(1,0)}
→ c=3, d=2, h*=(1,0,1), INTERIOR=1, TIER0=True, JACKPOT=True; and
conv{(−2,−2),(−3/2,3/2),(3,1)} → c=10, h*=(1,7,8), JACKPOT=True. The engine matches
independent SSYT ground truth on all 4,993 triples with |ν| ≤ 8 and on 300 stretched
c=1/c=2 checks. So the campaign-wide null is a genuine absence in the searched region,
not detector blindness.

---

## 8. What remains untested, and the standing disclaimer

Untested / open:
1. **The non-full-dimensional regime (d < D) by proof.** Theorem 1 closes only the
   full-dimensional case (d = D), at every r. The entire tier-0 population lives in
   d < D, and no theorem forces hive polytopes to obey the lattice-polytope
   inequalities there — it has only been sampled, never excluded.
2. **r = 7 interior pass incomplete** (23,289 nonempty triples generated; interior
   candidate pass still running) and **r ≥ 8 not hunted** for tier-0.
3. **|ν| above the exhaustive bounds**: r=5 exhaustive only to |ν| ≤ 27, r=6 only to
   |ν| ≤ 22. Larger sizes are untested exhaustively.
4. **Shape families beyond those sampled** (higher weight ratios, other asymmetries)
   in the non-full-dimensional regime.

**A null census is not evidence for the KTT positivity conjecture and is not to be
described as such.** No theorem in this report forces the searched hive polytopes to
be positivity-obeying in the untested regime; the record min h*_1 − h*_d = 0 means the
target was approached to within one interior lattice point but never reached, and the
only proved statement (Theorem 1) leaves the tier-0 population's home regime open.
