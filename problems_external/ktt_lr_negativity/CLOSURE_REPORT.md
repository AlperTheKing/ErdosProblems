# CLOSURE REPORT — KTT stretched-LR negativity campaign

Date: 2026-07-21. Status: **CLOSED, NO HIT.**
Target: one triple of partitions (λ, μ, ν) with |λ|+|μ| = |ν| such that the stretched
Littlewood–Richardson polynomial P(n) = c(nν; nλ, nμ) has at least one **strictly negative**
monomial coefficient — a counterexample to the King–Tollu–Toumazet (2004) positivity conjecture
(quoted in the literature as LR(iv)); also a FrontierMath open problem.

Outcome of 4 waves: **0 candidate counterexamples, 0 degree anomalies surviving resolution,
0 held-out interpolation failures.** Approximately 4.05 × 10⁸ triples screened.

A no-hit sweep is not evidence for the conjecture. §5 states this without qualification.

Artifacts: `engine/` (two independent exact counters + interpolator + LP oracle), `runs/` (58
populated family directories with `manifest.json` each), `r4_reeve/` (post-wave-4 direct r=4
engine), `NEXT_WAVES.md` (completeness critique, audited 2026-07-21), `APPROACH_REGISTRY.md`.

---

## 1. What was searched

### 1.1 Accounting

Three independent counts of the same campaign, all recorded, all reported here because they
differ:

| accounting | value | source |
|---|---|---|
| campaign headline (screens at n = 1) | ≈ 4.05 × 10⁸ | wave-4 close-out |
| independent streaming re-scan of `runs/` | ≈ 3.93 × 10⁸ exact n = 1 screens | `NEXT_WAVES.md` §0 |
| sum over 58 manifests of the largest screen-valued field per family | 415,753,374 | this pass, upper bound (double-counts nested per-phase totals in some families) |

Three families account for 379,799,664 screens = 93.8 % of the headline:
`wave3_maxr-minweight-corner` (335,148,806), `wave2_c456-census-midshell-r5` (29,712,059),
`wave4_c-eq-dim-plus-1-heavy-r5` (14,938,799).

Exactly interpolated stretched polynomials campaign-wide: **≈ 3.34 × 10⁶** (353,350 in the
streaming scan of files ≤ 90 MB, plus 2,990,538 in the mid-shell census whose 878 MB
`results.jsonl` was read from its manifest).

Engine calibration held throughout: engine A `lr_hive.exe`
(sha256 `95d1fea3716756ff…`) and engine B `engineB_lrrule.py` (sha256 `c7677d041ed18491…`)
agreed on every cross-check performed, including the c = 1 ⟹ P ≡ 1 and c = 2 ⟹ P = n+1 theorem
validators re-run as a gate in every family. Recorded dual-engine mismatches campaign-wide: **0**.

### 1.2 By r (records carrying an explicit ν; 980,641 scanned)

| r | records | exact interpolations | max deg P observed | ambient D = (r−1)(r−2)/2 |
|---|---|---|---|---|
| 4 | 179 | 64 | 3 | 3 |
| 5 | 505,261 | 326,818 | 6 | 6 |
| 6 | 445,908 | 25,713 | 10 (67 records) | 10 |
| 7 | 26,228 | 755 | 9 (2 records) | 15 |
| 8 | 2,854 | 0 with a `deg` field | — | 21 |
| 9 | 211 | 0 with a `deg` field | — | 28 |
| 3, ≥10 | 0 | 0 | — | — |

Degree histogram r = 6: {0:13, 1:115, 2:6065, 3:4399, 4:3046, 5:4839, 6:4412, 7:1308, 8:568,
9:881, 10:67}. Degree histogram r = 7: {0:1, 2:62, 3:80, 4:121, 5:164, 6:151, 7:140, 8:34, 9:2}.

### 1.3 By c (records carrying an explicit ν; the c = 1 and c = 2 validator records excluded)

| r | c = 3–12 | c = 13–24 | c = 25–100 | c > 100 |
|---|---|---|---|---|
| 5 | 463,751 | 12,014 | 11,713 | 7,774 |
| 6 | 246,368 | 88,455 | 17,156 | 10,932 |
| 7 | 17,611 | 2,759 | 885 | 2,604 |
| 8 | 2,854 | 0 | 0 | 0 |
| 9 | 211 | 0 | 0 | 0 |

Exact profiles (not LP screens) above c = 24 exist only in
`wave4_oddc-hstar2-parity-break-heavy-r5` (r = 5, c up to 1,521) and
`wave4_heavy-unbiased-statistic-control-w4` (c up to 40,952 measured, 1,225 profiles, all gated
to certified dim ≤ 6). At r = 6 the exact-profile counts are c ≤ 12 → 15,105, c ∈ [13,24] → 526,
c > 24 → 69. Of the 755 exact r = 7 polynomials, 733 have c ≤ 12.

### 1.4 By weight |ν|

- r = 5: |ν| ∈ [10,49] → 464,806; [50,119] → 39,695; ≥ 120 → 760.
- r = 6: [10,49] → 245,251; [50,119] → 199,427; ≥ 120 → 1,230.
- r = 7: [10,49] → 13,621; [50,119] → 12,603; ≥ 120 → 4.
- r = 8: [10,39] → 2,854 only. r = 9: [20,49] → 211 only.
- Campaign-wide records with |ν| ≥ 120: **2,026** (760 at r = 5, 1,230 at r = 6, 4 at r = 7,
  32 at r = 4), essentially evolver drift; no designed heavy-weight family above |ν| = 64 except
  the r = 5 staircase.

### 1.5 Exhaustive (not sampled) censuses completed

| family | census slice | triples |
|---|---|---|
| `wave2_c456-census-midshell-r5` | r = 5, depth ≥ 4 mid-shell, W = 22..34, all admissible | **29,712,059** screened / 2,990,538 profiled |
| `wave4_c-eq-dim-plus-1-heavy-r5` | r = 5, entire generator pool, 10,153 λ/μ pairs × 3,450 δ-vectors | **14,938,799** |
| `wave3_lowc-highdim-exhaustive-smallnu` | r ∈ {6,7,8} × W = 18..24, c ≤ 6, every cell complete | 9,288,190 screened / 11,712 oracle analyses |
| `wave1_c3-total-sweep-r5` | c = 3, r = 5, W = 18..30, all splits | 780,000 screened / 21,382 profiled |
| `wave2_selfconj-nu-involution-r6` | all 32 self-conjugate 6-part ν, complete stratum | 120,590 orbit classes / 7,213 profiled |
| `wave1_stair5-interleave-core` | staircase pool ±4 band, complete | 71,592 |
| `wave1_degenerate-multiplicity-bait-r5` | all 990 repeated-part pairs × 42,343 ν | 42,343 universe / 3,157 c-band profiles |
| `wave3_selfconj-involution-r6r7` | complete r = 6 self-conjugate census | 6,295 |
| `wave1_conjugation-symmetric-r5` | conjugate pairs + full self-conjugate census | 4,146 |
| `wave4_s3-cyclic-symmetric-hive` | S₃-fixed locus, N ∈ [8,20], complete | 4,463 LP censused |

**The two large exhaustive censuses in detail.**

**(a) `wave2_c456-census-midshell-r5` — 29,712,059 triples, c ∈ {4,5,6} mid-shell, W = 22..34.**
Slice: r = 5, ambient D = 6; |λ| ≤ |μ|, both weights in [8, W−8], ≤ 5 parts, parts ≤ 10;
Stembridge prefilter (no single row/column, no rect × rect, no rect × ≤2-distinct-part-sizes);
ν exactly 5 parts at box-transport depth ≥ 4 below the dominance top T = λ+μ; exact necessary
positivity prefilters (containment, dominance, union bound). Exhaustiveness is **proved, not
asserted**: `count_admissible.py` re-enumerates the slice with no engine calls and returns
29,712,059, equal to the screens performed, which also proves the three resume passes were
disjoint. Per-W admissible triples run from 96,660 (W = 22) to 7,406,604 (W = 34); every W is
flagged exhausted. Screen cap 20,000: **0 CAP_EXCEEDED, 0 errors.**
Results: 2,990,538 profiles (n = 0..8, held-out P(7) and P(8) verified by direct count against
the n = 0..6 interpolant for **every** profile), 0 degree anomalies, 0 h*-anomalies, 0 engine
mismatches, 0 negative-coefficient candidates. The whole census produced exactly **16 distinct
polynomials** (3 at c = 4, 6 at c = 5, 7 at c = 6); the rarest are c = 5, deg 4,
h* = (1,0,1,0,0) with 15 members, and c = 5, deg 1, P = 1+4n with 98 members. All 1,670,223
c = 3 triples were probed at n = 2 and every one returned P(2) ∈ {5,6}, i.e. wave-1's
two-polynomial c = 3 law held with 0 exceptions. `make_inventory_r2.py` re-audited every profile
from scratch (re-evaluating each stored interpolant over Fractions at n = 0..8 and recomputing
h*): 0 audit failures. Engine-B spot checks: 56 triples × 9 samples = 504 values (R2) and
61 × 9 = 549 values (R1), 1,053/1,053 exact matches.

**(b) `wave4_c-eq-dim-plus-1-heavy-r5` — 14,938,799 triples, c = 7 / c = 9 (and 8, 10, 11, 12)
sweep at r = 5.** Pool: λ, μ with 4–5 strictly decreasing parts, gaps ≥ 3, λ₁ ∈ [12,30],
|λ| ∈ [22,45]; ν obtained from T = λ+μ by transporting 1..8 boxes down with T₁−ν₁ ≤ 6; the entire
pool of 10,153 pairs was consumed. Screen cap 25 gave 8,008,734 fat skips (c > 25) and
1,690,682 kept at c ∈ [7,12]. The decisive result is an **exact full-dimensionality sweep**
(exact rational interior-point certification):

- c = 7: 0 of 250,459 triples are full-dimensional (dim Q = 6).
- c = 9: 0 of 123,631 triples are full-dimensional.
- c = 11: 0 of 150,338 triples are full-dimensional.

i.e. the odd-c, dim-6 cell — the r = 5 Reeve cell where h*₁ = c − 7 would be 0 or 2 — is
**empty** in this pool. Of the 2,121 dim-6 triples profiled (c ∈ {8,10,12}), the h* vector was
**universally (1, c−7, 0, 0, 0, 0, 0)**, max Σh* = 6, max h*₂ = 0, 0 held-out mismatches,
0 negative coefficients, 0 negative h* entries. Best Σh* anywhere in the family: 17, at dim 5.
Max vertex denominator over a 9,360-triple certified sample: 2 (one triple).

### 1.6 Post-wave-4 addendum: the r = 4 (dim 3) cell

The 4-wave campaign never entered r = 4. A dedicated direct engine (`r4_reeve/hive4.py`, exact
integers/Fractions only, no stretched-LR counting inside) was built afterwards and gated:
400/400 cross-engine agreement at L(1); 210/210 stretched-dilation checks at n = 2,3,4;
1000/1000 on a 250-triple dim-3-only pool; and — decisively for detector validity — the Reeve
tetrahedron unit test T_q, q = 1..20, reproduced h* = (1,0,q−1,0) and fired NEG for exactly
q ≥ 13 and no smaller q. **The negativity detector demonstrably fires on the textbook case.**

Censuses run in that cell (every triple, ν with exactly 4 positive parts, λ, μ with ≤ 4 parts):

| census | window | triples | dim-3 polytopes | non-lattice Q | negatives |
|---|---|---|---|---|---|
| `census_r4.py` | 4 ≤ N ≤ 22 | 1,363,713 | 4,202 | 0 | 0 |
| `q2_criterion.py` | N ≤ 30 | 20,676,729 | 160,143 | 0 | 0 |
| `_dim3_min.py` | 4 ≤ |ν| ≤ 20 | 610,125 | 1,320 | 0 | 0 |
| `hunt_reeve.py` (local search) | parts to ~44 | 200,383 evals | — | 0 | 0 |

Exact reduction for dim Q = 3: a₃ = V/6, a₂ = 1 + (h*₁−h*₃)/2, a₁ = (11 + 2h*₁ − h*₂ + 2h*₃)/6,
a₀ = 1. So negativity in this cell requires **h*₂ > 11 + 2h*₁ + 2h*₃**. All 59,168 c = 4 dim-3
polytopes at N ≤ 30 have normalized volume V = 1 (`c4_with_V_ge_2` is empty); min 6a₁ = 11 in
every window searched, attained at the unimodular simplex λ = μ = (3,2,1), ν = (5,4,2,1);
record h*₂ = 291 reached at λ=(37,19,7,3), μ=(33,20,5), ν=(44,38,28,14), h* = (1,138,291,38),
where 11 + 2·138 + 2·38 = 363 > 291 so a₁ = 12 > 0. Saturation audit: 13,905 nonempty Q out of
120,000 random triples, every one with L(1) ≥ 1, 0 violations.

---

## 2. Two theorems that invalidated the original search design

Both are standard Ehrhart theory. Both were established or re-derived *during* the campaign,
after families had already been allocated against them. Each one voids a specific block of work.

### 2.1 h*₁ = c − d − 1 ≥ 0, hence deg P ≤ c − 1 always ⟹ the "c ≤ deg P" regime is empty

For a lattice polytope Q of dimension d with c = #(Q ∩ Z^D) lattice points, h*₁ = c − d − 1, and
Stanley's non-negativity gives h*₁ ≥ 0, i.e. **d ≤ c − 1** — always. Since deg P = dim Q = d,
the inequality **deg P ≤ c − 1** is a theorem, not an observation.

Several early families were designed to hunt the complementary regime c ≤ deg P (labelled
"Track B", "the non-integrality jackpot flag", "h*₁ < 0"): `wave3_thinhigh-c-le-dim-r6r7`,
`wave2_r7-trackb-lift`, `wave2_r6-interior-capfilter-trackb`, and the Track-B lanes of
`wave1_stair6-interleave-r6` and `wave1_collapse-scan-lowc-r5`. **That regime is empty for
lattice polytopes.** The campaign duly observed `c_le_dimlo_count = 0`,
`c_le_dimlo_certificates = 0`, and min gap c − dim = +1 across ≈ 3.34 × 10⁶ exact polynomials —
which is the theorem, restated as a measurement.

The observation retains content only for **non-lattice** hive polytopes, where Stanley's
inequality does not apply and h*₁ is not the count c − d − 1. No family was ever steered on that
distinction: the Track-B families gated on c and dim, not on certified non-integrality. Their
null results are therefore uninformative about their own stated hypothesis.

### 2.2 Stanley h*_i ≥ 0 ⟹ wave-1's h*-forensics confirmed a known theorem

For any lattice polytope, h*_i ≥ 0 for all i (Stanley, 1980). The wave-1 h*-atlas (118,639
triples) and its wave-2 remine (`wave2_hstar-forensics-remine-w1`) recorded "no h*_j < 0 was ever
observed" as a campaign finding. Every polytope in those atlases was a lattice polytope (max
vertex denominator 1). **The finding is Stanley's theorem.** It is not evidence about KTT, and it
is not evidence that the search was looking in the right place.

The corollary that *was* actionable — and that was acted on late — is that h* ≥ 0 does not imply
monomial-coefficient positivity: the transfer P(n) = Σ h*_i C(n+d−i, d) can produce a negative
a_k when the h* mass sits at high i. The exact thresholds derived from that transfer matrix are
in §3.

---

## 3. Structural findings that survived adversarial checking

Each item carries its status. "SURVIVED" means an adversarial agent tried to break it and
failed. "REFUTED" and "GAP" verdicts are reproduced verbatim below, unsoftened.

### 3.1 SURVIVED — exact negativity thresholds from the h* → monomial transfer

Computed exactly from the transfer matrix; independent of any search.

- d = 3: negativity requires h*₂ > 11 + 2h*₁ + 2h*₃ (equivalently, with h*₁ = 0, normalized
  volume V ≥ 13 — the Reeve tetrahedron threshold, reproduced by the engine).
- d = 6: negative a₁ requires Σh* ≥ 37.
- d = 9: h*₂ ≥ 204. d = 10: h*₂ ≥ 264.
- Lattice-simplex requirement with h*₁ = 0: V ≥ 13 (d=3), ≥ 27 (d=4), ≥ 19 (d=5), ≥ 37 (d=6),
  ≥ 25 (d=7).

Best Σh* attained inside the mandated cells: 4 (`wave4_hstar1-le2-dim9-10-prime-cell-r6`),
20 (`wave3_maxr-minweight-corner`), 478 at c = 24 (`wave3_stair6-interleave-dimgated-r6`, where
a₁ = 1501/420 > 0 and ~201 further units of h*₂ were required). The single place where the
threshold was numerically exceeded is `wave4_maxden-highc-dim9-r6` — see §4.1.

### 3.2 SURVIVED — all certified h*₁ = 0 hive simplices found were unimodular

`wave4_hive-simplex-determinant-mine`: 7,171 triples screened, 2,171 CERTIFIED_SIMPLEX with
complete h*, 5,000 NOT_SIMPLEX. Joint (h*₁, V) distribution: 1,886 at (0,1), 187 at (1,2),
22 at (2,3), 27 at (3,4), 29 at (6,8), 5 at (7,9), 9 at (15,32), 5 at (16,27), 1 at (50,243).
`h1_zero_V_values` = {1: 1886}: **every h*₁ = 0 certified simplex had V = 1**, against the d = 3
requirement V ≥ 13. Max normalized volume anywhere in the family: 243, at h*₁ = 50.
Fractional-vertex polytopes: 927 (maxden 2: 918, maxden 3: 9); certified fractional *simplices*: 0.

### 3.3 REFUTED — structural claim C1 (h*₁ = 0 ⟹ Q is a unimodular simplex and P(n) = C(n+d,d))

Adversarial verdict, verbatim:

> ```
> {"verdict":"REFUTED",
>  "counterexample":"lam = (2,2,1), mu = (4,3,2,1), nu = (5,4,3,2,1)   [|lam|+|mu| = 5+10 = 15 = |nu|; r = 5, ambient hive dimension (r-1)(r-2)/2 = 6]
>
> CERTIFIED DATA (all exact, integers/Fractions only):
>   dim Q                    = 4   (complete exact vertex enumeration; independently = deg P)
>   exact lattice points c   = 5   = dim Q + 1  ==>  h*_1 = 0   (exactly C1's hypothesis)
>   vertices of Q            = 7   (NOT a simplex), two of them HALF-INTEGRAL (NOT a lattice polytope)
>   normalized volume Sum h* = 2   (NOT 1)
>   h*                       = (1, 0, 1, 0, 0)
>   P(n) for n = 0..8        = 1, 5, 16, 40, 85, 161, 280, 456, 705      (engine A == engine B, byte-identical)
>   P(n)                     = (n+1)(n+2)(n^2+3n+6)/12 = n^4/12 + n^3/2 + 17n^2/12 + 2n + 1
>   unimodular-simplex claim C(n+4,4) = 1, 5, 15, 35, 70, 126, 210, 330, 495  --  P(2) = 16 != 15
>
> The 7 exact vertices (complete enumeration over all C(27,6) = 296,010 six-subsets of the 27 distinct
> facet normals, each candidate solved over Fractions and checked exactly feasible):
>   (7,8,9,10,11,13) (7,8,9,11,12,13) (7,8,9,11,12,14) (7,9,9,11,12,13) (7,9,9,11,12,14)
>   (7,17/2,9,21/2,12,27/2)   (7,17/2,9,11,23/2,27/2)
> The 5 exact lattice points: (7,8,9,10,11,13) (7,8,9,11,12,13) (7,8,9,11,12,14) (7,9,9,11,12,13) (7,9,9,11,12,14)
>
> All three assertions of C1 fail simultaneously: Q is not a simplex, not unimodular (V = 2), and
> P(n) != C(n+d,d).
>
> INFINITE FAMILY (dual-engine verified k = 4..9): lam = (2,2,1), mu = (k,3,2,1), nu = (k+1,4,3,2,1)
> for every k >= 4 gives the identical P, h* = (1,0,1,0,0), V = 2, dim 4, c = 5.
>
> Note: this triple's own monomial coefficients (1/12, 1/2, 17/12, 2, 1) are all positive, so it is a
> counterexample to C1, not to KTT positivity.",
>
>  "details":"VERIFICATION CHAIN (every step exact; no float decided anything)
>
> 1. Lattice-point count c = 5 by THREE independent methods: engine A (lr_hive.exe, hive DFS),
>    engine B (engineB_lrrule.py, LR-rule tableau counter, independent of the hive model), and my own
>    direct box enumeration of Z^6 ∩ Q from the rhombus system. All agree.
> 2. Stretched profile P(0..8) computed by engines A and B separately: identical.
>    Direct geometric lattice-point counts of the dilates nQ for n = 1,2,3 give 5, 16, 40 — a third,
>    purely polyhedral confirmation of the Ehrhart link.
> 3. Degree-4 Newton interpolation from n = 0..4 reproduces n = 5, 6, 7, 8 exactly (FOUR held-out
>    points, not the mandated two). deg P = 4 = dim Q, as Ehrhart theory requires.
> 4. dim Q = 4 from the COMPLETE vertex set (all C(27,6) six-subsets of the reduced normal system;
>    every vertex of {x : Ax <= b} is the unique solution of d linearly independent tight rows, so the
>    enumeration is exhaustive, not sampled). maxden = 2 is a rigorous non-integrality certificate.
> 5. h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i) with d = 4 gives (1,0,1,0,0); Sum h* = 2 matches
>    4! * (leading coefficient 1/12) = 2. Self-consisten
> ```
> *[adversarial transcript truncated at this point in the record]*

Consequences carried forward: (i) the h*₁ = 0 cell contains non-lattice, non-simplex polytopes —
so §3.2's "all unimodular" statement is a property of the *sampled* certified simplices, not of
the h*₁ = 0 cell; (ii) an explicit infinite family of non-lattice hive polytopes at r = 5 with
h*₁ = 0 and V = 2 now exists and was never used as a search seed; (iii) the wave-2 mid-shell
census independently contains this shape — the c = 5, deg 4, h* = (1,0,1,0,0) class with
15 members — and did not flag it as non-lattice, because non-integrality was never measured
there.

### 3.4 GAP — structural claim C2 (bounded vertex denominators at r = 5 constrain coefficient signs)

Adversarial audit, verbatim:

> ```
> {"status":"GAP","isCompleteProof":false,
>  "gapDescription":"TWO gaps, one fatal.
>
> FATAL (logical, unfixable by more computation of the same kind): a bound on vertex denominators is not a bound on Ehrhart coefficients, and C2 supplies NO bridge between them. The bridge does not exist: Ehrhart negativity is a LATTICE-polytope phenomenon. I verified exactly that the Reeve tetrahedron T_13 = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,13)} has all vertex denominators = 1 (q=1, strictly stronger than "q<=2"), h* = (1,0,12,0) >= 0, and P(n) = 1 - (1/6)n + n^2 + (13/6)n^3 — a strictly negative monomial coefficient, held-out-verified at n=4,5,6. So even a fully-proved "every r=5 hive polytope has q=1" would leave the KTT conjecture at r=5 completely untouched. C2 therefore cannot become a proof of anything about coefficient signs by any amount of further denominator/determinant work. (This also undercuts the campaign's own steering statistic: it hunted non-lattice polytopes while the classical negativity mechanism it cites lives in lattice polytopes.)
>
> SECONDARY (rigor/coverage, fixable): the sub-claim "max q = 2 over all r=5 triples" is itself not proved by the artifacts.
>  (a) The "no simple vertex" verdict (tpos=0 for all 5682 bases) is read off a FLOATING-POINT scipy/HiGHS LP with threshold res.x[NP] > 1e-9. hive_poly.py's own rigor contract says "no mathematical verdict may rest on it"; here one does. Needs exact rational LP / Farkas certificates.
>  (b) The gcd collapse step is executed for only 1981 of the 5682 bases. synth3.log FINAL reads trip_fail=3701, and synth3.py does `if pint is None: stat["trip_fail"]+=1; continue` BEFORE the gcd block. So 65% of the high-determinant bases received no denominator check at all, contradicting manifest.json's "Every basis with |det| >= 3 (all 5682 of them) ... collapses".
>  (c) Where the gcd IS computed, it is computed at the WRONG point. p* is a basic optimal solution (an extreme point) of the LP, so its tight set is MAXIMAL, hence gcd over 6-subsets is minimal — g=1 is nearly forced by construction and carries almost no information. The supremum of the denominator over the feasibility cone C_B is attained at RELATIVE-INTERIOR points, where the tight set is minimal and the gcd largest.
>  (d) Per-triple maxden in the corpus comes from analyze_ext with K=45 random objectives — sampled vertices, not all vertices — so "max_q_attained: 2" over 6610 triples is only a lower bound on the true maximum.
>
> WHAT A COMPLETE PROOF WOULD NEED, and whether it is finitely checkable: the correct use of the (true) structural fact is not vertex denominators but PARAMETRIC LATTICE-POINT COUNTING. Since A is fixed and b = C p with C an integer 30x15 matrix, c(p) = #{h in Z^6 : A h <= C p} is a piecewise quasi-polynomial on the chamber complex of the parametric polytope (Sturmfels, "On vector partition functions"; Clauss–Loechner; computable with barvinok). Chambers are polyhedral CONES, so the ray {n p} never leaves th
> ```
> *[adversarial transcript truncated at this point in the record]*

This audit invalidates the campaign's principal steering statistic. Maximizing the vertex
denominator q was the organizing heuristic of Route N (`wave3_fracvertex-denominator-ladder-r6`,
`wave4_maxden-ladder-fulldim-r5`, `wave4_maxden-highc-dim9-r6`,
`wave4_nonsimple-vertex-excess-r6-r7lift`, `wave4_asymmetric-weight-ratio-corner`). The
Reeve tetrahedron — the only object anyone can point to with a negative Ehrhart coefficient — has
q = 1. Those families' CPU time was spent moving away from the one known mechanism.

### 3.5 SURVIVED (as a restriction) — certified fractional vertices with q = 4 and q = 5 exist at r = 7

Three families closed directions on a "vertex denominator ceiling q = 3". Those are r ≤ 6
statements. `runs/wave4_nonsimple-vertex-excess-r6-r7lift/CERT_fractional_q4_q5_r7.json` carries
two independently verified r = 7 vertices:

- λ=(13,8,7,5,2,1), μ=(7,6,4,3,2,1), ν=(15,13,11,7,5,5,3): c = 790, certified dim 14, **q = 5**,
  tight rank 15, tight-basis |det| 5.
- λ=(10,8,6,2,1), μ=(11,6,4,3,1,1), ν=(18,11,9,5,5,3,2): c = 644, certified dim 12, **q = 4**,
  tight rank 15, tight-basis |det| 4.

Neither has ever been profiled. Per §3.4 this is a *weakened* finding, not a lead: q is not
known to bear on coefficient signs.

### 3.6 SURVIVED — the dimension oracle `hive_poly.analyze` is not a certificate

`runs/wave4_rho-uncapped-margin-evolver/anomalies.json` (type `ORACLE_FALSIFICATION`) plus the
wave-4 control's resolution summary establish that the `dim_lo == dim_hi` agreement test is not
rigorous. Root cause recorded: HiGHS returns the same optimal vertex for many random objectives,
so the "tight at every sampled vertex" set is too large and `dim_hi` collapses onto `dim_lo`.
Measured failure rates: 3 of the first 24 wave-4 triples (12.5 %) and 41 of 1,225 unbiased
profiles (3.3 %), dimension under-estimated by 1 or 2 in every case.

**24 apparent negative coefficients were produced as under-degree fitting artifacts and vanished
at the true degree.** Worked example on record: λ=(13,5,4,1,1), μ=(6,5,2,2,1), ν=(16,10,6,5,2,1);
`analyze` returned dim 6, true dim 8; the deg-6 interpolant has coefficients
1, −43/10, 4123/180, −161/12, 637/72, −77/60, 89/360 and misses both held-out points; at dim 8
every coefficient is positive and both held-out points match. This is precisely why the mandatory
held-out check at n = D+1, D+2 was a non-negotiable — it caught all 24.

A validated remedy exists and was used in exactly one family:
`runs/wave4_rho-uncapped-margin-evolver/dimoracle.py` (implicit-equality method: constraint i is
an implicit equality iff max_{x∈Q}(b_i − A_i x) = 0; dim Q = d − rank of the implicit set, rank
taken exactly). Every campaign closure that rests on an *upper* bound for dim Q is therefore
unproven; the affected families are listed in §4.4.

### 3.7 SURVIVED — weight scaling is inert

At fixed absolute perturbation the stretched polynomial is bit-identical for every base weight
t ≥ 2 (checked to t = 32; 205 of 213 ladders already identical at t = 1 vs t = 2). Recorded
caveat: the measurement was made at fixed *absolute* perturbation, not at fixed near-wall
geometry, so it does not settle the near-Horn-wall heavy-weight families.

### 3.8 SURVIVED — three logged anomalies were tooling artifacts, not mathematics

`wave2_stair5-heavy-interleave-w2/anomalies/anom_00{0,1,2}.json` were logged as DEGREE_ANOMALY
with `deg: null`. Re-running `engine/interp.py` on their stored sample tables returns exit 0 for
all three: deg 5 (1, 41/15, 3, 41/24, 1/2, 7/120), deg 5 (1, 161/60, 65/24, 31/24, 7/24, 1/40),
deg 3 (1, 13/6, 3/2, 1/3); held-out points match in each case; all coefficients positive. Same
failure mode as `wave2_random-thin-control-w2/degree_anomaly_A1_resolution.json`: a transient
non-zero exit of the `interp.py` subprocess.

### 3.9 KNOWN — novelty gate

Adversarial novelty verdict, verbatim:

> ```
> {"known":true,
>  "details":"VERDICT (short): Neither S1 nor S2 is a published theorem, but neither is new as a *question*. S1's low-dimensional instances are literally the published King–Tollu–Toumazet (KTT) small-coefficient statements — d=1 is a proved theorem (Ikenmeyer; Sherman), d=2 is an explicitly stated OPEN KTT conjecture. So S1 in general implies an open published conjecture and therefore cannot be already proved; but it is not a novel formulation either. S2 is a special case (5 parts) of the open KTT positivity conjecture LR(iv), which is stated in the literature and still open with no known counterexample. The ~4x10^8-triple negative search re-covers ground that is only qualitatively described in the literature ("computer experiments", "a significant amount of data"); I found no published *quantified* exhaustive verified range on the LR side, so the campaign's range is probably new as data, though a null result.
>
> === S2: KTT positivity for stretched LR polynomials ===
> 1. The conjecture is KTT 2004 (CRM Proc. Lecture Notes 34). It is quoted verbatim in the modern literature as item LR(iv): "All coefficients of the polynomial c^{t·lambda}_{t·mu,t·nu} are non-negative", together with LR(v) (the same for the associated F(w)); see Gao, "Stretched Newell-Littlewood coefficients", arXiv:2101.00984, Conjecture 1.1 and its LR analogues, where LR(i) (saturation, Knutson–Tao), LR(ii) (Fulton, Knutson–Tao–Woodward) and LR(iii) (polynomiality, Derksen–Weyman / Rassart) are listed as THEOREMS and LR(iv), LR(v) as OPEN. The same conjecture appears as Conjecture 4.7 of De Loera–McAllister for stretched Clebsch–Gordan coefficients.
> 2. Status as of now: still open, no counterexample. Per Alexandersson's maintained reference page (symmetricfunctions.com, "Littlewood–Richardson coefficients"): computer experiments suggest the Ehrhart polynomial has non-negative coefficients and "This conjecture is still open." Nothing in 2024–2026 arXiv changes this.
> 3. Publis
> ```
> *[adversarial transcript truncated at this point in the record]*

---

## 4. What remains unmeasured

This section states measurement-blindness, not open questions in general. Each item names the
artifact that establishes the blindness.

### 4.1 The high-c non-lattice corner at certified dim 9–10, r = 6 — the campaign is blind here

`wave4_maxden-highc-dim9-r6` (8,000 screened, 5,061 dimension analyses, 1,332 certified dim 9 and
1,371 certified dim 10) reached the only stratum in the whole campaign where the Route-A
arithmetic threshold of §3.1 was numerically exceeded, and could not finish the measurement.

Record triple: λ = (23,17,7,6,4), μ = (17,17,6,5,4,1), ν = (39,32,13,11,10,2); c = 52, certified
dim 9, vertex denominator q = 3.

- h* settled through j = 8: **(1, 42, 388, 892, 534, 60, 0, 0, 0)**, Σ prefix = 1917.
  h*₂ = 388 against the d = 9 threshold h*₂ ≥ 204 — exceeded by 184.
- P(8) = 4,627,524, obtained only after raising the cap to 4 × 10⁷ (184 s).
- **P(9): `CAP_EXCEEDED` at cap 4 × 10⁷ after 318 s ⟹ P(9) > 4 × 10⁷.** (The campaign's standard
  profile cap was 4 × 10⁶; the raise to 4 × 10⁷ did not suffice.)
- Consequence recorded verbatim in the manifest: "h*_9 (the only remaining entry of this dim-9
  h*-vector) is UNREACHABLE with engine A; the h*-vector is settled nonnegative only through j=8."

**h*_9 is unknown for every triple in this stratum**, and h*_9 is exactly the entry whose weight
in the transfer to a₁ is largest. The family's own verdict: "Not exhausted." Adjacent
unfinished mass: 18 certified q = 3 dim-9 hive polytopes (first ever at r = 6), all with
CAP_EXCEEDED h* tails; and `wave3_dim10-lowc-frontier-r6`, whose minimum c at certified dim 10 is
28 unbiased / 16 after beam steering, against a lattice lower bound of 11 — gap 5, never closed.

### 4.2 The r = 7, dim ≥ 10 held-out verification wall — arithmetically impossible with the current engine

A polytope of dimension 10 forces P(D+2) ≥ C(D+2+10, 10). At r = 6 (D = 10) that is
P(12) ≥ C(22,10) = 646,646, which is reachable. At r = 7 (D = 15) the mandated held-out point is
n = 17 and

**P(17) ≥ C(27,10) = 8,436,285 > 4 × 10⁶ (the profile cap).**

Hence **every r = 7 family mandated to certify held-out points at dim ≥ 10 was arithmetically
incapable of finishing before it started** (`wave3_r7-thin-highdim-probe`, which located
34 dim ≥ 10 r = 7 triples and could verify none of them). Max degree ever attained at r = 7 in
the campaign: 9, on 2 records. **Degrees 10 through 15 at r = 7 are empty of exact data.** That is
6 of the 16 possible degrees at r = 7, entirely unmeasured.

### 4.3 Eight triples whose exact P is unknown after an observed mismatch

`runs/wave4_heavy-unbiased-statistic-control-w4/ares*.jsonl` records 41 DEGREE_ANOMALY
resolutions: 33 `ok`, **8 `CAP_EXCEEDED`**. For those 8 the true degree of P is still unknown and
the low-degree fit demonstrably missed the held-out points. Engine B agreed with engine A on
every sample it could complete.

| idx | r | λ | μ | ν | c | oracle d | D |
|---|---|---|---|---|---|---|---|
| 3962 | 7 | 8,8,4,3,3,2,1 | 11,11,6,5,3,3,1 | 17,16,11,8,8,7,2 | 9 | 4 | 15 |
| 1907 | 7 | 21,8,8,4,3,3,1 | 11,9,5,3,2,1 | 30,11,10,10,6,6,6 | 28 | 6 | 15 |
| 1919 | 7 | 8,8,5,2,2,2 | 7,7,3,2,2,1 | 12,9,8,8,6,3,3 | 14 | 6 | 15 |
| 1769 | 7 | 13,7,3,2,2,1,1 | 13,13,11,5,1,1,1 | 19,14,13,11,8,6,3 | 18 | 5 | 15 |
| 3997 | 7 | 7,7,3,3,3,1 | 8,4,3,2,2,1 | 14,9,7,6,4,2,2 | 11 | 6 | 15 |
| 4494 | 7 | 14,8,8,8,2,2 | 9,8,7,3,2,2,1 | 18,16,15,9,7,6,3 | 8 | 5 | 15 |
| 5167 | 7 | 22,11,6,6,3,3,2 | 13,5,2,1,1,1 | 27,18,12,7,4,4,4 | 53 | 6 | 15 |
| 142 | 6 | 19,16,6,3,3 | 18,8,4,4,2,1 | 30,19,18,7,5,5 | 56 | 6 | 10 |

These are the only triples in the campaign whose exact P is unknown after a mismatch was observed.

### 4.4 Closures that rest on an unsound dimension upper bound (§3.6)

Unproven as stated, pending re-certification with `dimoracle.py`:
`wave3_oddc-fulldeg-parity-r6` ("0 of 6,776 odd-c triples attained dim 10"),
`wave4_hstar1-le2-dim9-10-prime-cell-r6` (699 at dim ≥ 9, `dim_10_certified = 0` over 8,536
analyses), `wave3_stair6-interleave-dimgated-r6` (10,782 analyses),
`wave4_maxden-highc-dim9-r6` (5,061 analyses), `wave3_dim10-lp-census-r6`,
`wave3_selfconj-involution-r6r7` (1,191 analyses).

### 4.5 Strata with zero or near-zero coverage

- **r = 3: 0 records** (d = 1, P linear; positivity is a theorem there).
- **r = 4: 0 records in waves 1–4.** Covered only by the post-campaign addendum of §1.6, and only
  for |ν| ≤ 30 exhaustively plus ~200k local-search states; that cell is bounded, not closed.
- **r = 8, r = 9: 3,065 records total, all from one minimal-weight family**
  (`wave3_maxr-minweight-corner`, screen cap 12, c ∈ [3,12], |ν| ≲ 35). Their "simplex-like"
  verdict is a statement about minimal weight only. r = 8/9 at |ν| ∈ [40,80] or c > 12:
  **zero records.** r ≥ 10: **zero records.**
- **r = 6, dim ∈ {9,10}, c ∈ [25,80]: measurement-blind** (§4.1).
- **c ∈ [13,24] at r = 7: 2,759 records but 16 exact profiles**, all of degree ≤ 6.
  c > 24 at r = 7: 6 exact profiles.
- **c > 24 at r = 6: 69 exact profiles out of 28,088 records.** Every degree-10 r = 6 polynomial
  in the campaign — all 67 — comes from one family and sits at c ∈ {16, 20, 24}.
- **`wave2_c11-shell-mapper-r6`: 14,146 distinct c ∈ {11,12} primaries found, 348 profiled
  (2.5 %).** That shell is explicitly not exhausted; c = 11 at dim 10 is the exact r = 6 Reeve
  cell (h*₁ = 0 at d = 10) and was never found.
- **Non-lattice polytopes were never given a full h*.** Banked but unprofiled: 11,861 analyses in
  `wave3_fracvertex-denominator-ladder-r6`, 267 certified in
  `wave4_near-disconnected-skew-degenerate-content` (24 of them at dim 10, that leg explicitly
  reported NOT dead), 492 q = 3 in `wave4_s3-cyclic-symmetric-hive`, 1,499 q = 2 + 2 q = 3 in
  `wave3_oddc-fulldeg-parity-r6`. Only h*-prefixes were ever measured on these, and Stanley's
  theorem gives no non-negativity guarantee there.
- **Eight of 22 wave-2 hunter slots produced no data whatsoever**:
  `wave2_allodd-parity-r6` (script only), `wave2_nearwall-r5-heavy` (driver only),
  `wave2_hook-vs-fat-r6` (3 probe batches), `wave2_r7-trackb-lift` (script only),
  `wave2_raisedcap-fulldeg-shelf-r6` (preflight only), `wave2_r6-interior-capfilter-trackb`
  (calibration probe only), `wave2_beam-evolver-r6-lowk` (none), `wave2_smallw-census-r6` (none).
- **Move budgets**: 2- and 3-box coupled moves only at r = 5; 5/8/13-box walks only at r = 6,
  c ∈ [9,12]; **≥ 4-box coordinated moves at r ≥ 7: never run.** Corner peels were capped at
  6 boxes and 334/3,306 pairs (~10 %) in `wave1_corner-peel-offwall-r5`, whose own manifest
  states it is not exhausted.

### 4.6 The methodological blind spot

**No Barvinok / LattE-style direct Ehrhart computation was ever used.** The entire campaign
inferred P by exact sampling plus exact interpolation, so its reach was set by the cost of
counting hives by depth-first search, not by mathematics. Both walls in §4.1 and §4.2 are
artifacts of that choice. The parametric-lattice-point route named in the C2 audit (fixed A,
b = Cp, chamber complex of the parametric polytope; Sturmfels, Clauss–Loechner, barvinok) was
never implemented, and neither was the finite chamber enumeration that would decide the r = 4
cell outright (`r4_reeve/BUILD_HIVE4.md`, "Route to a decisive r=4 verdict — not attempted here").

---

## 5. No result in this campaign is evidence for the KTT conjecture

Stated plainly and without hedge:

1. **A null search bounds only where the generators plus the caps looked.** Zero hits in
   ~4.05 × 10⁸ triples is a statement about the enumerated window, the screen caps, the node
   caps, and the family biases — not about the conjecture. The conjecture quantifies over all
   triples; the campaign covered a set of measure zero within that, concentrated at r ∈ {5,6},
   c ≤ 12, |ν| ≤ 60.
2. **Two of the campaign's headline "findings" are theorems it re-measured, not data.**
   `deg P ≤ c − 1` (never once violated in 3.34 × 10⁶ polynomials) is h*₁ ≥ 0; "no h*_j < 0 ever
   observed" is Stanley's theorem. Neither carries information about KTT (§2).
3. **The organizing steering statistic was shown to be unconnected to the target.** The Reeve
   tetrahedron, the only known negative-coefficient mechanism, has vertex denominator q = 1;
   the campaign's Route N maximized q. Per the C2 audit: even a fully proved "every r = 5 hive
   polytope has q = 1" would leave KTT at r = 5 completely untouched (§3.4).
4. **The detector is known to work and the search still found nothing** — the Reeve unit test
   fires NEG for exactly q ≥ 13 (§1.6) — which removes "the tooling was broken" as an
   explanation, but adds nothing on the side of the conjecture.
5. **The regions where negativity is arithmetically least excluded are exactly the regions the
   campaign could not measure**: r = 6 dim 9–10 at c ∈ [25,80] where h*₂ = 388 already exceeds the
   d = 9 threshold of 204 and h*_9 is unknown (§4.1); r = 7 at degrees 10–15, empty of data
   because P(17) ≥ 8,436,285 exceeds the cap (§4.2); and every non-lattice polytope banked
   without a full h*, where Stanley gives no protection at all (§4.5).
6. **Two dozen "negative coefficients" were produced and every one was an artifact** of an
   under-estimated dimension (§3.6). The mandated held-out checks caught all 24. This is a
   statement about the verification protocol's soundness, and simultaneously a warning that any
   future hit must be certified against a rigorously proved dim Q, not an LP oracle's agreement
   test.
7. **The conjecture's published status is unchanged.** KTT (2004), quoted as LR(iv) in the modern
   literature, remains open with no known counterexample; the campaign contributes a quantified
   null range where the literature had only qualitative "computer experiments" (§3.9). That is
   the entire contribution.

The correct one-line summary of the campaign is: **a large null, a refuted internal structural
claim (C1), a fatally gapped internal structural claim (C2), an unsound dimension oracle now
documented, and a precisely located measurement frontier.** Nothing more.
