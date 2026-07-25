# Q1 Literature Gate — Sunflower Axis Disambiguation

**Date:** 2026-04-17
**Context:** Research Intelligence Briefing (2026-04-17) recommended comparing our PMF measurements c_3 ≥ √6 ≈ 2.449 against Mitchell 2026 values m(7,3) ≥ 30, m(8,3) ≥ 45 and Naslund–Sawin 2016 upper bound (1.889)^n. Before any public framing, resolve whether these quantities are on the same axis.

## Finding (headline)

**They are not.** Mitchell's m(n,3) and Naslund–Sawin's (1.889)^n both live on the Erdős–Szemerédi axis (sunflower-free families over the power set P([n]), growing in n). Our M(n, w, k) measurements live on the Erdős–Rado axis (sunflower-free w-uniform families at fixed k, with c_k^w the conjectured extremal base). The c_3 ≥ √6 observation does not belong in any note that also cites Mitchell or Naslund–Sawin as competing bounds.

## Evidence

### Mitchell (LinkedIn preprint, Jan 2026)

Web search returned exact values m(n,3) = 2, 4, 6, 9, 13, 20 for n = 1, ..., 6, described as "computed for a power-set formulation of the Erdős–Szemerédi sunflower problem." The cited formula (8/3)·(3/2)^(n−1) is a geometric fit to the floor of the exact values for n ≥ 2:

| n | (8/3)·(3/2)^(n−1) | floor | Mitchell reported |
|---|---|---|---|
| 1 | 2.667 | 2 | 2 |
| 2 | 4.000 | 4 | 4 |
| 3 | 6.000 | 6 | 6 |
| 4 | 9.000 | 9 | 9 |
| 5 | 13.500 | 13 | 13 |
| 6 | 20.250 | 20 | 20 |
| 7 | 30.375 | 30 | ≥ 30 (claimed) |
| 8 | 45.562 | 45 | ≥ 45 (claimed) |

At n=5 the formula value 13.5 exceeds C(5,3) = 10 — impossible for our w-uniform quantity — confirming that Mitchell's m(n,3) is counting arbitrary subsets, not 3-subsets.

### Naslund–Sawin 2016 (arXiv:1606.09575)

Web search snippet: "if A ⊆ P([n]) is sunflower-free, then |A| ≤ 3(n+1)C^n for C = 3/2^{2/3} ≤ 1.89". The domain is P([n]) — all subsets of [n]. This is the Erdős–Szemerédi bound, not the Erdős–Rado w-uniform bound. The (1.889)^n factor is indexed by n (ground set size), not by w (set size).

### Our measurements (EXP-MATH-ERDOS20-SUNFLOWER-001, -002)

| w | n range | M(∞, w, 3) | Saturated? | c_3 ≥ M^(1/w) |
|---|---|---|---|---|
| 2 | 3..10 | 6 | yes (n=6..10) | 2.449 |
| 3 | 4..8  | 12 (tentative) | two-point | 2.289 |
| 4 | 5..7  | 15 | no | 1.968 |

These are w-uniform measurements at fixed k=3 petals. The quantity c_3 here is the Erdős–Rado absolute constant (petal constant), for which the conjecture asserts a w-independent base.

## Axis comparison

| Axis | Erdős–Rado (our measurement) | Erdős–Szemerédi (Mitchell, Naslund–Sawin) |
|---|---|---|
| Ambient space | w-subsets of [n] | All subsets of [n], i.e., P([n]) |
| Ambient size | C(n, w) | 2^n |
| Extremal conjecture | max \|F\| ≤ c_k^w (w-independent base) | max \|A\| ≤ c^n for some c < 2 |
| Fixed parameter | w (set size) and k (petals) | k (petals) only; sets have arbitrary size |
| Varying parameter | n (to read saturation in w) | n |
| Current status | Wide open; bounds ALWZ 2019, Rao, Tao | Resolved upper bound ≤ (1.889)^n (Naslund–Sawin 2016); lower bound ≈ 1.5^n (Mitchell 2026 constructions) |
| Literature lower bound on base | Unknown in w; our w=2 saturation gives c_3 ≥ √6 ≈ 2.449 | ≈ 1.5 (Mitchell) |
| Literature upper bound on base | ALWZ: c_k = O(k log w) | Naslund–Sawin: ≤ 1.889 |

## Implications

1. **Our c_3 ≥ √6 measurement is on the Erdős–Rado axis and is NOT invalidated or subsumed by Mitchell or Naslund–Sawin.** Those are different quantities. The conflation in the briefing was an axis error, not a magnitude error.

2. **There is no published lower bound on the Erdős–Rado c_k at w=2 that we have yet seen.** The classical result that two disjoint triangles give M(∞, 2, 3) = 6 is well-known in graph theory, but whether it is explicitly stated in the sunflower literature as a lower bound c_3 ≥ √6 needs a targeted check before the observation note ships.

3. **The briefing's comparison recommendation should be retracted from the next observation note.** Any c_3 claim from our measurement must sit in the Erdős–Rado frame with its own literature context, not alongside Erdős–Szemerédi numbers.

4. **The w=4 case remains the highest-leverage publishable measurement.** Kupavskii–Noskov (Nov 2025, arXiv:2511.17142) covers core size 1 with k ≥ 5, leaving w = 3, 4 at k = 3 in the computational/asymptotic bucket. A clean exact value M(∞, 4, 3) via a real transfer matrix (not exhaustive backtracking) would be the strongest Erdős–Rado axis contribution within our reach.

## Published lower bound for c_3 (post-gate check)

**Abbott–Hansen–Sauer** (classical result surfaced by search): the best known lower bound on the Erdős–Rado sunflower constant at r = 3 petals is

f(w, 3) ≥ 10^(w/2 − O(log w)),   hence   c_3 ≥ √10 ≈ 3.162.

This is an explicit construction, asymptotic in w. Our extracted c_3 ≥ √6 ≈ 2.449 from w=2 saturation is strictly weaker than this bound. Our c_3 ≥ 12^(1/3) ≈ 2.289 from w=3 tentative saturation is also weaker. Our c_3 ≥ 15^(1/4) ≈ 1.968 from w=4 partial data is weaker still.

**Implication:** the extracted c_3 lower bounds from our PMF measurements are *not* new lower bounds on the Erdős–Rado constant. They are shadows of the true extremal at small n and small w, and they sit below the Abbott–Hansen–Sauer construction.

A simpler universal lower bound also follows from the search: for any w, f(w, 3) ≥ (ℓ−1)^w via the map construction X(f) = {(x, f(x)) : x ∈ [w]} with f : [w] → [ℓ−1], giving c_3 ≥ (ℓ−1) for the largest feasible ℓ. At w = 2 the relevant parameters give the 6 we recover.

## Implications for the observation note

The observation note's framing must change. Our measurements are **recoveries and extensions of small-n exact values**, not new lower bounds on c_3. Specifically:

1. M(∞, 2, 3) = 6 is classical. Our w=2 saturation is a sanity check, not a contribution.
2. M(∞, 3, 3) = 12 is the tentative two-point agreement from our w=3 data. The relevant literature question is whether 12 is the known exact value at w=3 k=3 in the Erdős–Rado setting. If yes, we recover. If no and 12 is above the literature lower bound but below an unknown truth, this is an incremental computational data point, not a bound improvement.
3. M(∞, 4, 3) ≥ 15 from our n=7 w=4 run is a strict lower bound only because we ran out of compute at n=8. It is unlikely to be the extremal at w=4; the Abbott–Hansen–Sauer construction at w=4 gives f(4, 3) ≥ 10^(2 − O(log 4)) ≈ 100 / (small factor), suggesting our 15 is far from the truth.

**The lattice-gas apparatus itself — density of states, growth-rate decay, jamming transition — is the method contribution and is IP-gated.** The numerical values we extracted are not novel contributions; they are the small-n sanity shadow of an asymptotic construction that dominates them.

## What still needs checking (deferred to post-filing session)

- Exact value of M(∞, 3, 3) and M(∞, 4, 3) in the sunflower literature — whether Abbott–Hansen–Sauer, Kostochka, or any post-ALWZ paper pins these down as exact at small w.
- Whether the PMF lattice-gas interpretation adds anything on top of Abbott–Hansen–Sauer-style combinatorial constructions — this is a Leg 4 / Mendoza's Limit question and is IP-gated.
- Whether the Duke–Erdős forbidden sunflower literature (Kupavskii–Noskov) has exact small-n values at k=3, w=3 that subsume our tentative 12.

## Revised next action

1. **No public observation note this week.** The measurements do not beat published lower bounds and do not add to the Erdős–Rado literature. Publishing a c_3 ≥ √6 claim would be embarrassing relative to Abbott–Hansen–Sauer c_3 ≥ √10. Publishing the PMF framework is IP-gated.
2. **Provisional filing becomes the unambiguous single rate limiter.** Without filing, there is no safe public surface on #20. With filing, Leg 4 (Mendoza's Limit vs. Abbott–Hansen–Sauer construction cost) becomes the high-leverage next experiment.
3. **Internal scorecard update** — A-axis stays A0; B-axis unchanged; note in NOTES column: "PMF lattice gas recovers known extremal at w=2; weaker than Abbott–Hansen–Sauer c_3 ≥ √10 at w=3, 4. No new numerical contribution. Method is IP-gated."
4. **Target for the next math session**: retire the "publishable observation" framing; aim directly at Leg 4 — compute Mendoza's Limit M_L for the sunflower core-closure channel and test whether the Abbott–Hansen–Sauer construction saturates or approaches the thermodynamic floor. This is the real Erdős #20 morphism experiment.

## Sources consulted

- Naslund–Sawin 2016, arXiv:1606.09575 — Upper bounds for sunflower-free sets (Erdős–Szemerédi)
- Mitchell LinkedIn preprint, Jan 2026 — computational m(n,3) values (Erdős–Szemerédi power-set formulation)
- Kupavskii–Noskov, arXiv:2511.17142 (Nov 2025) — Duke–Erdős forbidden sunflower, core size 1 for k ≥ 5
- Thomas Bloom, thomasbloom.org/notes/sunflowers.html — catalog of bounds
