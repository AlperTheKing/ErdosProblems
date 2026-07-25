# EXP-MATH-ERDOS20-SUNFLOWER-002 — Cross-w Report

**Date:** 2026-04-17
**Problem:** Erdős #20 (Sunflower Conjecture)
**Framework:** Prima Materia Framework, Layer 2 — Arithmetic Phase (Boolean lattice gas)
**Scope:** Partition function + max family size for sunflower-free families of w-subsets of [n], for w ∈ {2, 3, 4} at k=3
**Status:** OPEN (problem), measured (experiment). No progress on the conjecture; A-axis stays A0.
**Safe verbs:** formalize, encode, compute, measure, observe, recover. **Do not** say prove / solve / advance / improve.

## Why this run

The conjecture's substance is *w-independence* of the base c_k: it claims the extremal sunflower-free family has size ≤ c_k^w for some constant c_k that does not grow with w. Experiment 001 only covered w=3. A w-independence claim cannot be probed with a single w. This run adds w=2 and w=4.

## Headline numbers

| w | n range | M(largest n, w, k=3) | Saturated? | c_3 lower bound = M^(1/w) | Conjectured 2^w |
|---|---|---|---|---|---|
| 2 | 3..10 | 6 at n=6..10 | yes, at n=6 | 2.449 | 4 |
| 3 | 4..8  | 12 at n=7,8 | tentative (two points agree) | 2.289 | 8 |
| 4 | 5..7  | 15 at n=7 | no (n=8 aborted at 5 min) | 1.968 | 16 |

## What these numbers mean

M(n, w, k) is the size of the largest sunflower-free family of w-subsets of [n]. As n grows, M is non-decreasing (more room for sets). Once M stops growing with n, it has hit the extremal value M(∞, w, k). The Erdős conjecture asserts M(∞, w, k) ≤ c_k^w with c_k an absolute constant.

Each row above gives a lower bound on M(∞, w, 3), hence a lower bound on c_3. Only the w=2 row is a strict bound — M has been observed at 6 for five consecutive n (6 through 10), which is a strong saturation signal. The w=3 row has two agreeing data points (n=7, 8), not enough to call it saturated. The w=4 row is just one measurement.

The single hard fact this run extracts:

**c_3 ≥ √6 ≈ 2.449** (from w=2 saturation).

This rules out the textbook-naive guess c_3 = 2, since 2^2 = 4 < 6. It does not rule out c_3 being an absolute constant — it just sets that constant above 2.

## The w=2 case has a clean combinatorial identity

For w=2, "sunflower-free family of 2-sets (edges) with k=3" translates to: the graph has no 3-matching (three pairwise disjoint edges, core ∅) and no 3-claw (three edges through a common vertex with disjoint other endpoints, core a single vertex). Equivalently: matching number ≤ 2 and max degree ≤ 2. Any such graph has at most 6 edges, with equality attained uniquely by two vertex-disjoint triangles on 6 vertices (degree sequence 2,2,2,2,2,2; matching number 2; |E|=6).

The enumeration in this run recovers this exact value (M=6 on n=6) and keeps observing it at n=7, 8, 9, 10 — consistent with the known combinatorial argument. That is a sanity check, not a new result.

## The w=3 case is still tentative

Two data points agreeing (M(7,3)=M(8,3)=12) is suggestive but not sufficient. A known upper bound from the literature would pin this down; I have not checked what the current best-known M(∞, 3, 3) is. It may already be settled at 12 or it may be higher. Before claiming anything about w=3, this gap needs a literature check.

## The w=4 case is incomplete

n=7 gives M=15, but n=7 has only 35 four-subsets of [7] available, and the relevant sunflower structures only start admitting s=2 cores at n=8. Our value of 15 is a lower bound that may be loose. The n=8 run was aborted at ~5 minutes of runtime without output (the exhaustive backtracking for C(8,4)=70 subsets does not finish in session budget). A canonical-order transfer matrix would make this feasible; the current code does not implement one.

## Lattice-gas reading

For all three w, the growth rate g_n(m) = #extensions / #families at family size m decays monotonically from a high value (35 at w=3, n=7; 35 at w=4, n=7; 15 at w=4, n=6) to zero at the jamming transition. The jamming m* (first m where g < 1) for the n=7 data points:

| w | n | C(n,w) | m* (jamming) | m*/C(n,w) |
|---|---|---|---|---|
| 3 | 7 | 35 | 6 | 0.171 |
| 4 | 7 | 35 | 9 | 0.257 |

Same ambient state space (35 subsets) but m* is higher for w=4. This is because with larger subset size, fewer triples of subsets can form a sunflower (needs ≥ 12 − 2s elements, larger for bigger w), so the constraint is less restrictive per family size. The gas is "cooler" at higher w in this sense.

## Does the w-dependence signal support or oppose the conjecture?

Neither, definitively. What the data shows:

- The c_3 lower-bound sequence (2.449, 2.289, 1.968) is monotone *decreasing* — but this is a weakness of the measurement, not of the conjecture. c_3 from w=2 is a real lower bound (saturated). c_3 from w=3 is a lower bound on a lower bound (M might be larger at n ≥ 9). c_3 from w=4 is a lower bound on a lower bound (M almost certainly larger at n=8, 9, ...). The right way to read this: **c_3 ≥ 2.449 is the only firm number**; the other two entries could rise as n grows.

- Nothing in this data requires c_3 to grow with w. That is consistent with the conjecture but does not prove it.

- Nothing in this data forces c_3 to be bounded either. It is just too small an n range.

## What this adds to the PMF story

The lattice-gas picture is now verified at three w values. For each, the partition function Z_n, the density of states c_n(m), and (for most) the growth rates g_n(m) are well-defined, finite, and computable. The jamming transition is visible at every w. The PMF-amenability tier ("Tier 2 — modified state space needed") listed in Math/CLAUDE.md is concretely consistent with execution: the state space varies cleanly with w, and the constraint (incremental 3-sunflower check) is identical across w.

What remains unexecuted: the Leg 4 morphism experiment (comparing measured extremal density to Mendoza's Limit M_L prediction for the core-closure channel). This run produces the mathematical-side quantities needed to feed that comparison; it does not compute the physics side.

## Honest limits (stronger than in 001)

1. **n=8 w=4 is missing.** The strongest cross-w comparison would be M(n=∞, w, 3) read off saturation for all three w. We only have that for w=2.
2. **k is fixed at 3.** The conjecture's k-dependence is untested here.
3. **Enumeration algorithm is the bottleneck.** The file is called `sunflower_transfer_matrix.cpp` but what it implements is exhaustive backtracking. A real transfer matrix over canonical-ordered states would lift the ceiling.
4. **Literature check not done.** The known M(∞, 3, 3) and M(∞, 4, 3) extremal values may already be in the literature. If they are, the c_3 lower bound here may already be known to be tight or loose; I did not cross-check.
5. **No Leg 4.** The morphism experiment is designed, not executed.

## Recommended next step (single call-to-action)

**Literature check c_3 and the known extremal M(∞, w, 3) for w=3, 4.** If the w=3 extremal is known to be 12, the conjecture's c_3 lower bound from this measurement is 2.289 (already weaker than the w=2 bound of 2.449). If the w=3 extremal is >12, our saturation claim is wrong and we need larger n. Either outcome is valuable; doing anything else (Leg 4, transfer matrix rewrite, Zenodo) without this check risks building on an unverified extremal claim.

## Artifacts

- `EXP-MATH-ERDOS20-SUNFLOWER-002_RESULTS.json` — cross-w structured data
- `EXP-MATH-ERDOS20-SUNFLOWER-002_REPORT.md` — this file
- `EXP-MATH-ERDOS20-SUNFLOWER-002_RESULTS.sha256` — checksum
- `results_w2.json`, `results_w4.json`, `run_w2.log`, `run_w4.log` — raw per-w outputs
- Parent: `EXP-MATH-ERDOS20-SUNFLOWER-001_*` (w=3 data)
