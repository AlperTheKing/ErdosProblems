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
| A5 | **Covering / packing (odd-cycle edge transversal) duality** — general form | **BLOCKED** | blocking lemma verbatim: *"for every triangle-free `H` and every `x ≥ 0`, `τ_{w(x)}(H) = τ*_{w(x)}(H)`, where `w(x)_uv = x_u x_v"* (product-weight integrality, PWI). PWI + Theorem A (`Λ ≤ 1/25`) gives `ψ ≤ 1/25` for every triangle-free `H` — the whole conjecture — so PWI is at least as strong as the conjecture. **And PWI is outright FALSE**, re-derived independently by me (`claude_gate_find_n14_gap.py`): of the 1274 maximal triangle-free 14-vertex patterns, **exactly one** attains `τ = 7 = ⌊196/25⌋`, namely graph6 `M?AE@bH{AYN_LgBs?` (32 edges), and on it `τ = 7` (exact integer minimum over all 8192 bipartitions) while an exact rational cover of cost `32/5` is feasible against all 10204 odd cycles — gap `35/32`, matching A5's original figure exactly. Uniform weights are a product weight, so this kills PWI at the extremal object itself. Note it is **not** a `C5` blow-up: `C5[3,3,3,3,2]` gives only `τ = 6` |
| A5b | **The `And(k)` restriction of A5** (`ψ = Λ` on Andrásfai graphs only) | **LIVE** | not blocked: it delivers only the Andrásfai half of the `δ > N/3` reduction, not the conjecture. Guenin's sufficient condition is **provably unavailable from `And(4)` on** — `Γ_11` carries a genuine odd-`K5` minor (signed conditions verified exactly; explicit finite gap weight with `τ_w = 4 > 10/3 ≥ τ*_w`), while `Γ_8` has **none** over all 2646 canonical branch tuples. Integrality nevertheless holds on `And(4)`: exact rational packing certificates give `Λ = ψ` in 31 of 32 weightings against the complete 596-cycle list. Needs a non-Guenin certificate |
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
| A19 | **Discharging with local cut hypotheses** (`σ(S) ≥ 0` for `\|S\| < 0.244N`, plus any global graph functional) | **DEAD** | `C5[7,7,12,7,12]`: `N=45`, `bip=49 ≤ 81`, yet the class cut `{c0,c2}` has `25\|M\| = 2100 > 2025 = N²` with every `σ(v) ≥ 0` and the smallest negative switching set of size `0.2444N`. A witness *inside* the extremal family |
| A20 | **Unions-of-neighbourhood cuts** (closure of the neighbourhood family) | **DEAD** | Grötzsch: family value 5 vs `bip = 4`, `25·5 = 125 > 121`; and `C6` kills the plain family, `bip = 0` but `min_v e(C6−N(v)) = 2`, `50 > 36` |
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
