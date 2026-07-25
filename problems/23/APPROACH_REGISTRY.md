# Erdős #23 — APPROACH REGISTRY

One entry per approach FAMILY, keyed by mathematical mechanism (not by wording). Maintained by the
root agent. Status values: LIVE / BLOCKED / DEAD. A route is BLOCKED when it terminates at a lemma
of strength ≥ the conjecture, or when an exact falsifier kills its mechanism; the blocking statement
is quoted verbatim.

Last updated 2026-07-26 (Rounds 3–6 of the CDC-template restart).

| # | family (mechanism) | status | decisive fact |
|---|---|---|---|
| A1 | **Arc-cut / structured weight-reading cut family** on circle graphs `Γ_m = And(k)` | **LIVE — primary** | proved `ARCBOUND ≤ W/3`, so only total adjacent mass `W ∈ (3/25, 1/4]` is open; zero violations in exhaustive integer sweeps on 13 circle graphs and in continuous optimisation over positions+weights |
| A2 | **Moment / SOS (Lasserre) ceiling certificates** | **LIVE** (was wrongly declared blocked in Round 2) | epigraph form at level 3 returns `0.0400000003` on `C5` vs truth `0.04`; levels 1–2 give `0.0553`, `0.052`. Needs an exact rational dual to become a proof |
| A3 | **Structure-theorem route on the degree band** (Chen–Jin–Koh / Brandt–Thomassé: `δ > n/3` ⟹ hom to an Andrásfai or Vega graph) | **LIVE** | reduces the whole `δ > N/3` range to `max_x ψ = 1/25` on two explicit families; the Andrásfai half is A1, the Vega half is open |
| A4 | **Counterexample hunt in weighted-pattern form** | **LIVE** | complete for maximal triangle-free patterns on `≤ 11` vertices with all weightings `q ≤ 20` (0 violations) and for a validated max-min optimiser (0 hits); `n = 12, 13` running |
| A5 | **Covering / packing (odd-cycle edge transversal) duality** | BLOCKED | fractional packing is not tight on a known extremal object: `bip = 7` but `ν* = τ* = 32/5` on the `N = 14` extremal graph, integrality gap `35/32` |
| A6 | **Fixed averaging certificates** (one distribution over cuts, independent of `x`) | **DEAD** | for every `λ`, value `≥ bip(H)/(4|E(H)|)`, exactly `1/20` on every `C5[n]` against the truth `1/25` |
| A7 | **Independent-set / neighbourhood covering** (`bip ≤ min_I e(G−I)`) | **DEAD** | `min_I e(G−I) = 3 > 64/25` already on the Wagner graph; `15 > 256/25` on Clebsch |
| A8 | **Local switching families** (switch-star, σ-inequalities, sets below a fixed fraction of `N`) | **DEAD** | `P4`-blow-up `W_b` has a cut with `25|M| > N²` stable under every switching set of size `< 0.27N` while `bip = 0` |
| A9 | **Deletion induction on the low-degree side** (single vertex, independent set, greedy re-insertion) | **DEAD at 4/25** | `C5[7t,2t,7t,7t,2t]` is maximal triangle-free with `δ = 4N/25` exactly and the step fails at every vertex by exactly `1/25` |
| A10 | **Spectral / eigenvalue certificates** | DEAD | cap `0.0429 N²`; tight on all four triangle-free strongly regular graphs, so no slack |
| A11 | **Threshold / "N sufficiently large" arguments** | DEAD (vacuous) | `a(tN) ≥ t²a(N)` makes "for all `N ≥ N₀`" equivalent to "for all `N`" |
| A12 | **Exact reduction of `a(N)` to blow-up optimisation** | DEAD | `a(12) = 5` while the best `C5` blow-up on 12 vertices gives 4 |
| A13 | **Box branch-and-bound on `ψ`** | DEAD | bound ignores `Σx = 1`; stalls past 3·10⁶ nodes at `n = 8, 10` |
| A14 | **Flag algebras** (Balogh–Clemen–Lidický) | LIVE but external | published `n²/23.5`; exactness would need stability/spectrum machinery not yet applied to this problem |
| A15 | **Motzkin–Straus-style support reduction** | DEAD | `ψ` is *concave* along transfer lines (a min of affine functions), so the optimum sits at interior kinks; no endpoint argument exists |
| A17 | **Any functional of the neighbourhood-cut values `{m(b)}` together with `A = W−2T`** | **DEAD** | far-regular Wagner configuration `Γ_14`, support `{0,1,2,5,6,7,10,11}` uniform: `m(b) = 3/64` at every support point so every mean/variance/hierarchy collapses to one number, and `A = 9/224 > 1/25`, while the true `ARCBOUND = 1/32`. Refuted twice independently — the same machinery also fails on the Vega side |
| A18 | Degree-2-multiplier SOS certificate (the shape verified for `C5`) applied to `And(3)` | **DEAD at that degree** | parity-blocked SDP over 20 arc cuts is infeasible under a strict margin; the coefficient-wise LP form is infeasible even for `C5` |
| A16 | **Inherited soft-collision / Hall / bank-certificate machinery (R52–R58)** | BLOCKED | terminal lemma `canonicalSoftCollisionFeasibleTuple_exists` has strength ≥ the conjecture |

## Diversity check (LOOP rule 5: at least three incompatible routes alive)

Alive and mutually incompatible in mechanism: **A1** (combinatorial weight-reading cut family),
**A2** (algebraic SOS certificate), **A3** (structural/homomorphism reduction), **A4** (search for a
falsifier). That satisfies the rule with margin; A14 is tracked but is external work.

## Underexplored families to open in later rounds

* entropy / counting arguments on the cut structure;
* discharging on the maximum-cut local structure (σ-values) *combined with* a global potential —
  the local part alone is A8 and is dead, but no discharging with a global term has been tried;
* transport / flow formulations of `bip` as a minimum-cost object rather than a transversal;
* stability: quantitative "close to `C5[n]` or strictly below `1/25`" statements, which is what
  every flag-algebra exactness proof in the literature needs.
