# R5-K9 — the arc-cut conjecture reduced to ONE explicit moment inequality

Root-agent result, 2026-07-25. This supersedes the case analysis of R5-K7: the residual sliver is
closed by a second-moment step, and what remains is a single inequality among explicit moments of the
measure, with every reduction step to it proved.

## The two proved bounds

Let `μ` be a probability measure on `R/Z`, adjacency `d(x,y) > 1/3`, `g(x) = μ(F(x))` the far-mass,
`W = ½∫g dμ` the adjacent mass, `T = ∫t dW` the mass-weighted mean pair distance. For `b` on the
circle let `m(b)` be the monochromatic mass of the **neighbourhood cut** `A = N(b)` — an arc of
length `1/3`, independent because the graph is triangle-free — so

```
        m(b) = W − ∫_{N(b)} g dμ ,        E := ∫ m dμ = W − ∫ g² dμ    (identity, machine-checked)
```

**(1) Neighbourhood cuts with a second moment.** `m` is a bounded random variable under `μ`, so
`Var_μ(m) ≤ (max − E)(E − min)` and therefore

```
        min_b m(b)  ≤  E − Var_μ(m) / (max_{b ∈ supp μ} m(b) − E) .
```

**(2) Half-arc cuts, uniform position average.**

```
        min_a cov(a)  ≤  W − 2T ,
```

since a pair at distance `t` survives the antipodal cut `{a, a+1/2}` for an `a`-measure of `1 − 2t`.

Both are rigorous for every measure. Hence

```
   ARCBOUND(μ)  ≤  CRIT(μ) := min(  E − Var_μ(m)/(max m − E) ,   W − 2T  ) .
```

## The one remaining statement

> **CONJECTURE (moment inequality).** `CRIT(μ) ≤ 1/25` for every probability measure `μ` on the
> circle.

Proving it proves the arc-cut conjecture, hence `max_x ψ(And(k),x) = 1/25` for every `k` (Heinig's
Conjecture 6), hence Erdős #23 for every triangle-free graph with `δ > N/3` — modulo the Vega half
of Brandt–Thomassé.

## Why this is the right form

* **It is exactly tight at the extremal object and for the right reason.** On the five equal atoms
  `m ≡ 1/25` identically, so `Var = 0`, `max = E`, and `CRIT = E = W − ∫g² = 1/5 − 4/25 = 1/25`
  exactly. The rigidity of `C5[n]` appears as *`m` being constant*, not as a coincidence of numbers.
* **Each of the two terms handles what the other cannot.** The uniform measure has `Var = 0` and
  `E = 1/18 > 1/25`, and is closed by the half-arc term (`W − 2T = 1/36`). The
  `(1,1,2,2,1)` witness kills the half-arc term (`2/49`) and is closed by the neighbourhood term.
* **It closes the residual sliver of R5-K7.** The one case in 2200 that survived both plain averages
  — `Γ_11`, `x = (1/17,3/17,3/34,0,3/17,3/17,0,0,5/34,5/34,1/34)`, with `E = 0.041980` and
  `W − 2T = 0.041522`, both above `1/25` — has `Var_μ(m) = 0.00013290` and `max_supp m = 0.062284`,
  giving `CRIT = 0.035435 ≤ 1/25`.

## Verification (all exact rational arithmetic)

| test | measures | violations of `CRIT ≤ 1/25` |
|---|---|---|
| the 9-witness regression set (`claude_witness_regression.py`) | 9 | **0** |
| random exact measures over `Γ_5,7,8,10,11,13,14,16,17,20,22,23` | 2400 | **0** |
| perturbations of the extremal five-atom configuration on fine circles `Γ_30…Γ_60`, positions **and** weights perturbed — the zone where `CRIT` is tight | 840 | **0** |

The identity `∫m dμ = W − ∫g² dμ` is asserted at runtime in every evaluation, so a pairing error
(the arc must be attached to `b` through `N(b)`, not by its starting index — I made exactly that
error first, and it produced a spurious failure) is caught automatically.

## What a proof of the moment inequality needs

The two terms are `E − Var/(max−E)` and `W − 2T`. In the regime where both plain averages fail one
has, from R5-K7, `W ∈ (0.12, 0.2)`, `∫g² < W − 1/25` (so `g` is close to the constant `2W`) and
`T/W < (1 − (1/25)/W)/2` (so the adjacent pairs concentrate near distance `1/3`). The task is to show
that those two conditions force `Var_μ(m)` to be large enough — intuitively, mass concentrated at
distance exactly `1/3` makes `g` jump, and a jumping `g` makes `m` spread out. Making that
quantitative closes the whole `δ > N/3` range.


## 7. The g^k hierarchy (replaces the ad-hoc variance term)

Averaging the neighbourhood-cut value `m(b)` over `b` with weight `g(b)^k dμ(b)` gives, for each
`k ≥ 0`, a closed-form upper bound on `min_b m(b)`:

```
        bound_k  =  ( Σ_b x_b g(b)^k m(b) ) / ( Σ_b x_b g(b)^k ) ,      m(b) = W − Σ_{u ∈ N(b)} x_u g(u).
```

`k = 0` is `W − ∫g²dμ`; `k = 1` is `W − Q/(2W)` with `Q = ∫∫_{far} g(x)g(y)dμdμ`. Behaviour:

| case | `k=0` | `k=1` | `k=2` | `k=3` | `k=4` | `k=5` | true `min_b m(b)` |
|---|---|---|---|---|---|---|---|
| **C5 extremal** | **0.0400** | **0.0400** | **0.0400** | **0.0400** | **0.0400** | **0.0400** | **0.0400** |
| residual `Γ_11` | 0.0420 | 0.0408 | **0.0397** | 0.0387 | 0.0379 | 0.0373 | 0.0260 |
| `W1` `(1,1,2,2,1)` | 0.0379 | 0.0363 | 0.0343 | 0.0321 | 0.0300 | 0.0281 | 0.0204 |
| three-atom near-path | 0.0370 | **0.0000** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| seven-atom (g constant) | 0.0612 | 0.0612 | 0.0612 | 0.0612 | 0.0612 | 0.0612 | 0.0612 |

Two structural facts make this the right object:

* **At `C5` every level equals `1/25` exactly**, because `g` is constant there, so the weighting does
  nothing. The hierarchy cannot overshoot the extremal case at any level — the tightness is
  automatic, not tuned.
* **The hierarchy is stuck exactly when `g` is constant** (last row). And a constant `g` is precisely
  the case the half-arc bound `A = W − 2T` handles: by R5-K10 the Fourier mass that makes `A` large
  is 3-fold or 5-fold structure, and `1̂_far(n) = (−1)ⁿ sin(πn/3)/(πn)` kills the 3-fold component of
  `g`, so a `g`-flat measure has no room left.

So the proof splits along "is `g` constant?", with the hierarchy on one side and the Fourier bound on
the other — and the two sides meet exactly at `C5`, where both give `1/25`.


## 8. FINAL FORM of the reduction (this session)

Every ingredient below is an explicit moment of `μ`, and each is a *proved* upper bound on
`ARCBOUND(μ)`:

```
   m(b) = W − Σ_{u ∈ N(b)} x_u g(u)          (value of the neighbourhood cut at b)

   bound_k = ( Σ_b x_b g(b)^k m(b) ) / ( Σ_b x_b g(b)^k )      for k = 0, 1, 2, …   [weighted average]
   A       = W − 2T                                                                 [half-arc average]

   CRIT(μ) := min( A , bound_0 , bound_1 , bound_2 , … )   ≥   ARCBOUND(μ)   ≥  ψ(μ) .
```

> **CONJECTURE (final form).** `CRIT(μ) ≤ 1/25` for every probability measure on the circle.

Proving it proves the arc-cut conjecture, hence `max_x ψ(And(k),x) = 1/25` for all `k`, hence
Erdős #23 for every triangle-free graph with `δ > N/3` (modulo the Vega half).

**Verification record, all exact rational arithmetic, zero violations everywhere:**

| test | measures | violations |
|---|---|---|
| 9-witness regression set | 9 | 0 |
| random exact measures over 11–12 circle graphs | 2127 + 2134 | 0 |
| near-extremal perturbations, `Γ_25…Γ_60`, positions and weights perturbed | 1362 | 0 |
| the two cases that killed weaker rules (`Γ_11` residual, `Γ_40` danger-zone) | 2 | 0 |

**Why no single term suffices — each of these was tried and refuted:**

* the plain averages `A` and `bound_0` alone: 2 violations in 2127 (the `Γ_11` residual);
* `bound_∞`, i.e. "cut at the neighbourhood of the point of maximum far-mass `g`": fails on the
  `Γ_40` configuration with support `{1,7,16,21,32}` and weights `(8,11,12,12,11)`, where it gives
  `0.041495` and `A` gives `0.041238` — but `bound_0 = 0.039679` closes it;
* the `Γ_11` residual goes the other way: `bound_0 = 0.041980` and `A = 0.041522` both fail, and
  `bound_2 = 0.0397` closes it.

So the hierarchy is genuinely needed in both directions, and **at `C5` every term equals exactly
`1/25`** — `g` is constant there, so all `bound_k` coincide, and `A = W − 2T = 1/5 − 4/25 = 1/25`.


## 9. The remaining gap, localised exactly

Writing `Var_μ(g) = ∫g²dμ − 4W²`, the two plain bounds fail simultaneously only when

```
        2T < W − 1/25          (half-arc bound fails)
        4W² + Var_μ(g) < W − 1/25   (k = 0 neighbourhood bound fails)
```

Over 3600 random exact measures on nine circle graphs, **exactly 3** measures satisfy both, and they
are tightly clustered:

| `W` | `T/W` | `Var_μ(g)` | `m` |
|---|---|---|---|
| 0.1763 | 0.3701 | 0.010564 | 17 |
| 0.1748 | 0.3838 | 0.010966 | 17 |
| 0.1724 | 0.3837 | 0.005741 | 20 |

so the gap sits at `W ≈ 0.172–0.177`, mean adjacent-pair distance `T/W ≈ 0.370–0.384`, and small but
nonzero `Var_μ(g) ≈ 0.006–0.011`. In every such case a higher level `k ≥ 1` of the hierarchy closes
the bound (the full criterion has zero violations across all 5632 exact tests).

**The whole arc-cut conjecture is therefore reduced to this statement:**

> For every probability measure on the circle with `W ∈ (0.12, 0.2)`, `2T < W − 1/25` and
> `4W² + Var_μ(g) < W − 1/25`, some level `bound_k` of the `g^k`-weighted hierarchy is at most `1/25`.

That is the single unproved step. It is not a reformulation of the conjecture — it is a statement
about three explicit moments of a measure on the circle, in a region of parameter space that is
about 0.1 % of the sampled space, with the extremal `C5` sitting exactly on its boundary at
`W = 1/5`, `T/W = 2/5`, `Var_μ(g) = 0`.
