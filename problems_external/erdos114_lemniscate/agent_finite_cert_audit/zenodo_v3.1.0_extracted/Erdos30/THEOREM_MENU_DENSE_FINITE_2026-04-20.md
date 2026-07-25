# Theorem Menu for Erdős #30 — Dense Finite Rigidity

**Date:** 2026-04-20
**Scope:** Finite Sidon sets near the upper envelope
**Purpose:** Convert the current `#30` attack surface into a small set of lemma-level branches that match both the latest Sidon literature and the local formalization package.

**Status correction (later on 2026-04-20):** after checking Balasubramanian–Dutta, the current honest imported theorem interface is an ordered-element estimate at scale `O(n^{7/8}) + O(L^{1/2} n^{3/4})`. Candidate Lemma 1 below remains an aspirational local theorem target, not a theorem we are justified in importing at `sqrt(n)`-scale discrepancy.

## Why this branch

The old framing for `#30` was "search harder for better constructions" or "look for a new heuristic." That is no longer the highest-value reading of the problem.

The finite upper-bound frontier has moved in two directions:

1. The finite `n^{1/4}` coefficient has improved from the BFR `0.998` regime to `0.99703` (O'Bryant 2024) and then to `0.98183` (Carter–Hunter–O'Bryant 2025), with the strongest gain coming from computer-assisted combinatorics rather than a short new paper proof.
2. Dense finite Sidon sets appear to have much more internal rigidity than a naive "sparse random-looking object" model suggests. In particular, the `m`-th element and the sum of elements are both forced close to deterministic density-corrected templates.

That is exactly the geometry-constrained reading: the interesting objects are not arbitrary Sidon sets, but near-extremizers whose geometry is squeezed into a narrow corridor. This matches the physics intuition better than another unconstrained search.

## Local package alignment

The current local package in `Erdos30/` already gives a clean base for this program:

- `Erdos30_Sidon_Defs.lean` supplies the canonical `IsSidonSet` definition.
- `Erdos30_Lindstrom.lean` and `Erdos30_BFR.lean` formalize the classical finite upper-bound chain.
- `PROOF_RECIPES.md` now records the reusable counting and shifted-family patterns extracted from the latest BFR-support batch.

What is missing is not more elementary counting. What is missing is a stability layer: lemmas that say a Sidon set close to the upper envelope must look almost evenly distributed, almost linearly spaced, and almost mass-balanced.

## Candidate Lemma 1 — Prefix Discrepancy Stability

**Status:** Aspirational local theorem target. Not currently justified by an imported literature theorem at `sqrt(n)`-scale discrepancy.

**Working statement**

Let `A ⊆ [n]` be Sidon with `|A| = floor(sqrt(n)) - L`, where `L` is small on the natural `n^{1/4}` or slightly larger scale. Then every initial segment `[1,t]` of macroscopic length contains

`|A ∩ [1,t]| = (t/n) |A| + error(t, n, L)`

with an error term substantially smaller than the main term.

**What it would mean**

This says dense Sidon sets cannot front-load or starve long prefixes. If a set is close to extremal, then its cumulative distribution function is already rigid on coarse scales. In physics language: the geometry is constrained at the coarse-grained level before any finer statement about individual points can even be true.

**Why this matters**

This is the gateway lemma we actually need. Once prefix discrepancy is controlled, the `m`-th element and sum-of-elements statements become natural corollaries rather than separate miracles.

**Execution mode:** `Lean-first`

This is the most natural formal next step because it fits the current package and it is strictly weaker than all-interval control:

- finite counting,
- prefix counting,
- Cauchy-Schwarz / discrepancy style arguments,
- no brute-force search required to state the result.

**Likely proof ingredients**

- BFR-style sum counting,
- discrepancy over prefixes,
- reuse of the `distinctSums_subset_range` / `card_le_card` pattern,
- eventually a formal interface for a literature theorem if the sharp constant is imported rather than reproved.

## Candidate Lemma 2 — Ordered Element Rigidity

**Status:** External interface, Balasubramanian–Dutta 2025/2026. Perplexity gate passed on 2026-04-20. Current honest imported scale is `O(n^{7/8}) + O(L^{1/2} n^{3/4})`, not a sharper local discrepancy corollary.

**Working statement**

Let `A = {a_1 < ... < a_k} ⊆ [n]` be a dense Sidon set. Then the right linear
profile is

`a_m + 1 ≈ (m n) / k`

or, in division-free form,

`m n ≈ k (a_m + 1)`.

Since `k = sqrt(n) - L`, this is equivalent to

`m n ≈ (sqrt(n) - L) (a_m + 1)`.

**What it would mean**

This turns coarse occupancy into pointwise rigidity. A dense Sidon set is not merely "spread out"; its ordered elements lie near a deterministic linear profile with slope `n / |A|`. In the physics reading, this is the discrete analogue of a constrained ground-state profile: once the geometry is saturated, there is little freedom left in where the particles can sit.

**Why this matters**

This is the first theorem that starts to look classification-like. If true in a strong enough form, it says that any near-extremizer is trapped near an almost affine template with the correct density-adjusted slope. That sharply reduces the search space for construction experiments.

**Execution mode:** `Imported theorem interface first; Lean consequences after`

This is no longer the first local proof target. The honest state is that the ordered-element theorem is already available as an external theorem interface. The Lean work now is to extract local corollaries and connect it to the rest of the rigidity program.

**Likely proof ingredients**

- external ordered-element theorem interface,
- Candidate Lemma 1 if we still want a local discrepancy theorem,
- monotonicity from the ordered list of elements,
- a translation from interval count to inverse CDF / quantile control,
- careful separation between the true `n / |A|` slope and the naive `sqrt(n)` heuristic.

## Candidate Lemma 3 — Mass Balance / Sum-of-Elements Rigidity

**Working statement**

For a dense Sidon set `A ⊆ [n]`,

`sum_{a in A} a = (1/2) n^(3/2) + error(n, L)`.

**What it would mean**

This says that even the total mass of the configuration is almost forced. Once the set is close to maximal, it cannot only have the right density; it must place that density with nearly the right center of mass.

**Why this matters**

This is the cleanest bridge to a geometry-constrained physical picture. The set does not just satisfy a forbidden-sums rule. It pays a global placement cost. If the ordered elements are nearly linear and the total mass is nearly fixed, then the object behaves like a constrained low-energy configuration rather than a loose combinatorial gadget.

**Execution mode:** `Lean-first or computation-supported`

Once Lemma 2 exists, this becomes a sum of nearly linear positions. Without Lemma 2, it can still be tested computationally on exact dense Sidon sets and candidate near-extremizers.

**Likely proof ingredients**

- Candidate Lemma 2,
- summation of the ordered-element estimate,
- or direct prefix-discrepancy summation if that route is cleaner.

## Construction branch that depends on these lemmas

These lemmas do not directly solve `#30`. Their value is that they define a **restricted model class** for computation.

If the three rigidity statements are even approximately right, then construction search should stop ranging over all Sidon sets and instead range over:

- near-equispaced templates,
- perturbations of affine `(m n) / |A|` profiles,
- faithful algebraic constructions plus small structured perturbations.

That is the only construction branch that still looks worth serious compute. The old unconstrained branches already look weak:

- spectral greedy underperformed standard greedy in local experiments,
- toy Singer / toy Ruzsa proxies were not faithful enough to the actual algebraic mechanism,
- the morphism program currently classifies `#30` as a geometry-dominated generic control, not a scoped breakthrough case.

## Lean vs computation split

### Lean-first

- Candidate Lemma 1: prefix discrepancy stability
- consequences of the external ordered-element theorem at cutpoints and nearby prefixes
- Candidate Lemma 3: sum-of-elements rigidity

These are theorem statements about finite geometry and counting, which is where the current package already has traction.

### Computation-first

- exact dense-Sidon data generation,
- fitting the error term scales in Lemmas 1–3,
- searching only inside the rigid model class suggested by the lemmas,
- stress-testing whether extremizers really cluster near affine `(m n) / |A|` templates.

Computation should support conjecture sharpening, not replace the theorem program.

## Best next move

The shortest useful next step is:

1. Write exact local versions of Candidate Lemma 1–3 using the `A ⊆ Finset.range (n+1)` notation already used in the Lean files.
2. Decide which of the three is the cleanest first formal target.
3. Build a tiny computation harness on exact dense Sidon sets to estimate the correct error scale and keep the theorem statements honest.

My current recommendation is to treat **Candidate Lemma 2** as an imported external interface and use Lean to mine honest consequences from it. Candidate Lemma 1 remains important, but it is now clearly a harder aspirational local theorem rather than the obvious next thing to claim from the literature.

## References driving this menu

- Kevin O'Bryant, *On the size of finite Sidon sets* (2024): finite `n^{1/4}` coefficient improved to `0.99703`.
- Daniel Carter, Zach Hunter, Kevin O'Bryant, *On the diameter of finite Sidon sets* (2025): finite `n^{1/4}` coefficient improved to `0.98183`, with substantial computer assistance.
- R. Balasubramanian, Sayan Dutta, *The m-th element of a Sidon set* (Journal of Number Theory, 2026 issue / 2025 DOI): ordered-element and sum-of-elements rigidity for dense Sidon sets.

## Non-goals

This note does **not** claim:

- a new bound for `h(n)`,
- a route to the infinite problem by itself,
- any scoped Leg-4 upgrade in the morphism program.

It is a theorem menu for the finite rigidity branch only.
