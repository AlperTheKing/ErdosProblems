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
