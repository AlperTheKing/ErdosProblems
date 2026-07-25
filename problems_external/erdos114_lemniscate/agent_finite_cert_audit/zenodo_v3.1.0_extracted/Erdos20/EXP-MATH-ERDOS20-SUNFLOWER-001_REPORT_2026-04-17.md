# EXP-MATH-ERDOS20-SUNFLOWER-001 — Report

**Date:** 2026-04-17
**Problem:** Erdős #20 (Sunflower Conjecture)
**Framework:** Prima Materia Framework, Layer 2 — Arithmetic Phase (Boolean lattice gas)
**Scope:** Partition function and growth rates for sunflower-free families of 3-subsets of [n], n=4..8, k=3 petals
**Status:** OPEN (problem), measured (experiment)
**Safe verbs at current A-axis=A0:** formalize, encode, compute, measure, observe. Do not say "prove", "solve", "advance", or "improve" when citing this run.

## What was done

Enumerated, for each n∈{4,5,6,7,8}, every family F ⊆ {3-subsets of [n]} that contains no 3-sunflower (three sets with identical pairwise intersection and pairwise disjoint petals). For each family size m, counted how many SF-free families of size m exist (the "density of states" c_n(m)) and — for n≤7 — how many extensions of an SF-free family of size m to size m+1 are themselves SF-free (the "growth rate" g_n(m)). n=8 growth rates were not tractable in budget and are omitted; the n=8 partition function and density-of-states alone are sufficient to read the jamming transition.

Computation is exhaustive backtracking with the standard incremental 3-sunflower check (every new element S is tested against all existing pairs). No sampling, no stochastic estimation, no axiomatic shortcuts.

## Results

| n | C(n,3) | Z_n (total SF-free families) | log₂ Z_n | Max family size M(n) | Max density M(n)/C(n,3) | Erdős–Ko 1960 bound (k-1)^w |
|---|---|---|---|---|---|---|
| 4 | 4  | 16           | 4.00   | 4  | 1.000 | 8 |
| 5 | 10 | 388          | 8.60   | 6  | 0.600 | 8 |
| 6 | 20 | 33,652       | 15.04  | 10 | 0.500 | 8 |
| 7 | 35 | 2,485,795    | 21.25  | 12 | 0.343 | 8 |
| 8 | 56 | 148,790,380  | 27.15  | 12 | 0.214 | 8 |

## Phase-transition reading (lattice-gas interpretation)

In the PMF picture, an SF-free family is a configuration of a lattice gas on the C(n,3) "sites" (the 3-subsets of [n]). The constraint "no 3-sunflower" is a local exclusion rule. The growth rate g_n(m) = #extensions / #families at size m is the mean branching factor — the analogue of an inverse compressibility.

The jamming transition (first family size at which extensions become impossible on average, g_n(m) < 1):

| n | m* (g crosses 1 from above) | Corresponding density m*/C(n,3) |
|---|---|---|
| 4 | 2 | 0.500 |
| 5 | 3 | 0.300 |
| 6 | 5 | 0.250 |
| 7 | 6 | 0.171 |

m* grows, but the jamming density m*/C(n,3) shrinks — the lattice gas becomes harder to fill relative to the ambient space as n grows. This is the signature the PMF predicts: the extremal quantity is a close-packing density that decreases as the ambient configuration space inflates super-linearly.

Max family size M(n) saturates at 12 between n=7 and n=8. Two consecutive data points is not a pattern — it is a hint. Running n=9 is needed before this observation is worth anything; at n=9 with C(9,3)=84, the partition function is likely ≥10¹⁰ and needs a different algorithm (symmetry reduction, state merging, or the actual transfer matrix in the sense of canonical order rather than exhaustive backtracking).

## What this does and does not support

**Supports (modestly):**
- The PMF-amenability claim for Erdős #20 listed in Math/CLAUDE.md (Tier 2 — "modified state space needed"). The state space (all w-subsets) and constraint (local triple check) are in fact implementable, the partition function is finite and computable for n≤8, and the density-of-states is well-behaved.
- The lattice-gas reading of the sunflower problem — growth rates decay monotonically, the system exhibits a jamming transition, and the max-family-size sequence plausibly saturates.
- Morphism epistemology Leg 4 groundwork: there is now a measured quantity (M(n), jamming m*, growth-rate profile) that can be compared against a physical prediction once Mendoza's Limit M_L is evaluated for the sunflower core closure channel.

**Does not support:**
- Any claim about the conjecture itself. The Erdős Sunflower Conjecture asserts c_k = C(k) (w-independent). This run does not vary w and therefore cannot test that.
- Any claim of improved bounds. The 1960 Erdős–Ko bound (k-1)^w · w! = 48 at w=3, k=3 is not approached by M(n) in this range (max 12), which is expected — the extremal families at small n are just small.
- Any "proof", "advance", or "improvement". A-axis score remains A0.

## Gaps and honest caveats

1. **w=3 only.** To test the conjecture's core claim (bound is w-independent), the partition function must be computed for at least w=2,3,4 at matching n. Not done here.
2. **k=3 only.** The code's `creates_sunflower` fast path is hardcoded to k=3. General k needs the general pair/triple enumeration path, which is commented as "not implemented efficiently".
3. **Saturation of M(n) is unestablished.** Two equal data points (M(7)=M(8)=12) is not evidence of saturation at 12. It could break at n=9.
4. **Growth rates are not computed for n=8.** The O(families · subsets · m) cost is prohibitive. A canonical-order transfer matrix (state = "last L subsets in lexicographic order") would reduce this to polynomial per layer, but the existing code enumerates rather than transferring. The file is named `sunflower_transfer_matrix.cpp` aspirationally; what it actually implements is exhaustive enumeration. This mismatch should be addressed before the next round.
5. **No formal morphism experiment (Leg 4).** The Mendoza's Limit M_L prediction for the sunflower core closure channel is not computed here. That is the actual PMF-morphism test and is the next step.

## Morphism context

Math/CLAUDE.md lists "sunflower core closure cost (Erdős #20) vs. displacement current energy (Maxwell #4)" as the canonical Leg 4 example. This run produces the mathematical-side quantity (the extremal close-packing density and its scaling). The physics-side quantity (displacement current energy per core closure, under Mendoza's Limit) is still to be computed. A proper Leg 4 experiment compares the two as n grows and asks whether the PMF-amenability tier ruling ("Tier 2 — modified state space needed") survives — i.e., whether the lattice gas obeys the thermodynamic floor M_L = I·k_B·T·ln2/c² in the regime where geometry is exhausted.

Per GEOMETRIC_SHIELDING_PRINCIPLE.md, the first diagnostic for any apparent M_L binding is "has geometry been exhausted here?". The current data shows growth-rate decay that is smooth and geometric-looking (not Landauer-flat), which is consistent with geometry *not* yet being exhausted at n≤8. Small-n sunflower is a geometry-dominated regime; M_L binding should only appear as n→∞ along a specifically geometry-exhausting sequence, if at all.

## Artifacts

- `EXP-MATH-ERDOS20-SUNFLOWER-001_RESULTS.json` — structured data (n, Z_n, DoS, growth_rates)
- `EXP-MATH-ERDOS20-SUNFLOWER-001_REPORT.md` — this file
- `EXP-MATH-ERDOS20-SUNFLOWER-001_RESULTS.sha256` — reproducibility checksum
- `sunflower_transfer_matrix.cpp` — source
- `run_n8_v2.log` — full stdout of the run

## Recommended next steps (priority order)

1. **Swap enumeration for canonical-order transfer matrix.** State = last L subsets in lex order. Growth rates become computable at n=8, potentially n=9. This is what the file name promises and what the PMF framework actually wants.
2. **Sweep w ∈ {2,3,4} at matched n.** Without this, the w-independence conjecture is untested. This is the minimum viable morphism experiment for the actual conjecture.
3. **Compute Leg 4 morphism prediction.** Evaluate M_L for the sunflower core-closure channel; compare against the measured extremal density. Per morphism epistemology, this is the only route from "interesting lattice gas" to a power morphism.
4. **Update ERDOS_MASTER_SCORECARD.xlsx** with the run date (2026-04-17) and a note that the PMF amenability tier is experimentally consistent but unproven. No score change — A-axis remains A0.
5. **Deposit Sunflower_MDL.lean to Zenodo** (separate action, flagged by the scorecard as the DOI gap). This run does not replace that step.
