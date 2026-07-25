# Track A Results Synthesis — 2026-04-19

**Pre-registration:** `TRACK_A_PREREGISTRATION.json` (FROZEN)
**Artifacts:** `exp8_v2_results.json` + `EXP8_V2_REPORT.md`; `exp9_v2_results.json` + `EXP9_V2_REPORT.md`

## Headline

Track A ran two pre-registered Leg-4 tests against GSP scoped-bucket candidates and both came back FAIL: exp8_v2 returned **LEG4_FAIL** on the Huang-signed hypercube (all three criteria failed), exp9_v2 returned **CHIRAL_CLASS_REJECTED** on the bipartite Gaussian chiral operator (C2 failed at 3 of 5 Ws, C1 failed globally, C3 passed). Scope of these verdicts: Leg-4 decides **power-morphism / scoped-bucket candidacy only**. A Leg-4 FAIL does *not* retract legs 1–3 of the underlying morphism — the morphism remains a putative atlas entry based on its legs-1–3 evidence. What the FAILs do rule out is the stronger claim that these items are scoped (M_L-binding / geometry-exhausted) power morphisms. The principle-level consequence is that GSP's Leg-4 falsification track produced unambiguous rejections instead of murky partial passes, and two candidates for the scoped bucket have been honestly declined.

## exp8_v2 summary — hypercube

Tested: Δ(ε)/√n on the Huang-signed hypercube vs three geometry-killed nulls (ER_Gnp with matched average degree, sign-randomized cube, configuration-model degree shuffle). 20 realizations per n, n ∈ {10,11,12,13}, ε grid 0.1–1.0 step 0.005, knot fixed at ε = M_L = 0.4804530. Wall time 2164.3 s.

Verdict: **LEG4_FAIL**. All three criteria failed:

- **C1 strength-ratio** — required cube/null ratio ≥ 3 at n ≥ 11 on each null. Observed: every pair below 1. At n=13 the ratios were 0.34 (ER_Gnp), 0.19 (sign_randomized_cube), 0.36 (degree_shuffle). The nulls had *larger* Δslope at the M_L knot than the cube. The cube Δslope at n=13 was 0.1062 vs 0.5700 for the sign-randomized cube. This is the cleanest failure of the three.
- **C2 scaling** — required cube strictly increasing in n (pass: cube went 0.101, 0.1028, 0.1035, 0.1062), nulls flat (|Spearman ρ| ≤ 0.3). All three nulls violated flatness: ER_Gnp ρ=−1, degree_shuffle ρ=−1, sign_randomized_cube ρ=+0.8. Nulls are drifting with n in a structured way, not acting as flat baselines.
- **C3 model-selection** — cube ΔBIC=485.1 passed the ≥10 threshold on its own. But "at least one null ΔBIC ≤ 2" was required to establish the BIC is discriminating, and all three nulls came in high (445.8 / 496.6 / 447.0). The cube's large ΔBIC is not distinguishing; the piecewise-linear-with-fixed-knot model beats single-slope on all four systems.

What this means for the hypercube: it is **not promoted to the GSP scoped-exhausted roster**. Legs 1–3 of the Huang-hypercube morphism are untouched — the λ_max = √n bound remains a real RMT-class structural result, and the hypercube stays a putative RMT-class atlas morphism on that basis. What Leg-4 rules out is the stronger, narrower claim that M_L has a distinguishing kink on this system vs geometry-killed controls. No public claim may cite the hypercube as a scoped-bucket M_L example until a future pre-registered Leg-4 passes; the atlas-level RMT-class framing is unaffected.

## exp9_v2 summary — chiral / neutrino slot

Tested: bipartite Gaussian random operator (M=2W, N=W, entries N(0, 1/√W)), σ_min via SVD, 100 realizations per W, W ∈ {20, 40, 80, 160, 320}. Primary operator used per pre-reg rule; no implementation blocker, no fallback needed. Zero realizations filtered by the 1e-10 σ_min floor at any W. Wall time 1.9 s.

Verdict: **CHIRAL_CLASS_REJECTED** (rule: C2 fails → REJECTED, regardless of C1/C3).

- **C1 microscopic universality** — required max KS distance between consecutive-W CDFs of σ_min·W ≤ 0.10. Observed KS = 1.0000 at every pair (20,40), (40,80), (80,160), (160,320). No convergence at all in the tested W range.
- **C2 soft/bulk kink ratio** — required ≥ 1.0 at *every* W. Observed: 0.681 (W=20), 0.720 (W=40), 0.899 (W=80), 1.156 (W=160), 1.401 (W=320). Fails at W=20, 40, 80. **But note the trend: the ratio is rising monotonically with W, from 0.68 to 1.40.** This is the same criterion that cleanly rejected the Ulam-Galerkin doubling-map operator in exp9_v1; it remains the real discriminator.
- **C3 flavor-oscillation range** — required β ≥ −0.10 at 2σ. Observed β=0.3352, SE=0.0158, lower-2σ=0.3036. Passes cleanly. Range grows with W rather than shrinks.

Structural reading: the bipartite Gaussian operator is clearly in *some* universality class (C3 passes strongly, C2 trends toward passing), but it is not in chiral-RMT universality at the W range tested. C1's KS=1 is the stark signal — no microscopic convergence whatsoever. That the soft/bulk ratio is climbing suggests the class signature may emerge at W > 320, but we did not pre-register that extension and are not retrofitting it now.

Consequence per pre-reg, scoped to Leg-4 only: the neutrino slot is **not confirmed** as a scoped-bucket power morphism for this operator at the tested W range. Legs 1–3 of the neutrino-morphism candidacy are untouched — the chiral-RMT framing remains a legitimate atlas-level candidate on legs-1–3 evidence. The rising soft/bulk ratio (0.68 → 1.40 across W = 20 → 320) is consistent with the class signature emerging above W = 320, but we did not pre-register that extension and are not retrofitting it. The preregistration's deletion rule ("if no chiral operator in the atlas produces CONFIRMED, the scoped slot is formally deleted") applies only to scoped-bucket candidacy, not to atlas membership.

## What this means for GSP

The principle is strengthened, not weakened. GSP made a falsifiable claim about its scoped bucket ("these slots are where geometry is exhausted and M_L binds"), a frozen protocol was written to test two candidates for that claim, the protocol ran, and neither was promoted. The scoped-bucket roster shrinks to empirically-confirmed members. That is what correct science looks like — **the scoped-bucket roster** should contain only empirically-confirmed members, not hopeful candidates. Note the scope: this is about the scoped-bucket roster (power-morphism-level claims), not about atlas membership (legs-1–3 putative morphisms), which is a weaker standing that neither Leg-4 FAIL retracts. The remaining scoped candidates (PHYS-LD-001 Landauer, #20 sunflower, Shannon-capacity, Bernstein-flat) retain their candidacy only because they have not yet been tested, and each should go through a similar Leg-4 protocol before being cited publicly as a scoped-bucket GSP example.

The generic class (geometry dominates) continues to hold: exp1 Gauss map, exp4 universality sweep, exp5 Huang (as an RMT artifact, not as an M_L scoped example), exp7 tent map, MOR-DISS-001. The backprop over those 20 artifacts is unchanged — slope evidence still places them in the generic bucket with slopes near −1/2.

## What this means for Track B

The Track B gate stays closed pending user review. Two points to carry forward when it opens.

First, the Leg-4 methodology itself survived contact with reality. The three methodological upgrades (geometry-killed nulls instead of different geometric systems, pre-registered thresholds with no post-hoc tuning, model-selection via fixed-knot BIC instead of peak-finding) produced unambiguous verdicts. Compare to exp8 v1 and exp9 v1, which produced "partial" or "near-pass" verdicts that required post-hoc interpretation. The v2 template produces PASS or FAIL and nothing in between. That template is now validated for reuse.

Second, Track B pilots (QC ↔ #30 Sidon generic control, QC ↔ #20 sunflower scoped positive control) should inherit that template verbatim. The QC ↔ #20 pilot is particularly load-bearing because #20 is one of the four remaining scoped-bucket candidates — it needs to pass a Leg-4 test on its own terms before it can anchor the GSP roster.

## Next actions (priority order, no timelines)

1. **User review of both verdicts.** Confirm the readings above, confirm the GSP doc edits, confirm the CLAUDE.md table edit.
2. **Decide on the neutrino scoped-bucket slot.** Two options per the preregistration, both scoped to power-morphism / scoped-bucket standing (legs 1–3 candidacy is unaffected either way): (a) formally delete the scoped-bucket slot now, accepting that one rejected operator is a strong signal given the other three scoped entries are also untested; (b) reserve the slot for a future amended preregistration testing a different chiral operator or extending W beyond 320 to chase the rising soft/bulk ratio. The preregistration allows either; the decision is a strategic call about how aggressive to be in shrinking the scoped-bucket roster.
3. **Launch Track B pilot** (QC ↔ #30 Sidon as generic control, QC ↔ #20 sunflower as scoped positive control) using the validated Leg-4 v2 template. Freeze a new preregistration before running.
4. **Apply the same Leg-4 treatment to the remaining scoped-bucket candidates.** PHYS-LD-001 (Landauer), #20 sunflower (done by #3 above), Shannon-capacity at rate ceiling, Bernstein-flat throughput. Each needs a pre-registered Leg-4 with geometry-killed nulls before it can be cited as a scoped-bucket GSP example. Without this, the scoped-bucket roster is asymmetrically supported — hypercube and neutrino were declined at Leg-4 cleanly, the other four have never been tested at the same standard. This applies to scoped-bucket standing only; atlas-level (legs 1–3) status is independent.
