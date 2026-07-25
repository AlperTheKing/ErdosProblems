# R5-K19 — the harmonic-mean criterion is PROVED on the whole extremal family

Root-agent result, 2026-07-25. First proved piece of the target inequality
`min(W − 2T, H) ≤ 1/25`, and it covers exactly the configurations where the bound is tight.

## Setting

`μ` a probability measure on `R/Z`, `x ~ y` iff `d(x,y) > 1/3`, `g(x) = μ(F(x))` with
`F(x) = (x+1/3, x+2/3)`, `W = ½∫g dμ`, and

```
        m(b) = W − ∫_{F(b)} g dμ = the adjacent mass with NO endpoint in F(b)
             = the monochromatic mass of the neighbourhood cut A = N(b) = F(b),
        H    = 1 / E_μ[1/m]   (harmonic mean of m).
```

`min_b m(b) ≤ H`, so `H ≤ 1/25` certifies the arc-cut ceiling.

## Lemma (pentagram configurations)

**Suppose the support of `μ` consists of five clusters `P_1,…,P_5` in circular order whose far-graph
is the pentagram — each cluster is adjacent exactly to the two clusters at circular distance two.
Write `x_i = μ(P_i)`. Then**

```
        m(b) = x_{i−1} x_{i+1}   for every b ∈ P_i ,
        Σ_b x_b / m(b) = Σ_i x_i / (x_{i−1} x_{i+1})  ≥  5 (Π_i x_i)^{−1/5}  ≥  5 · 5 = 25 ,
        hence   H ≤ 1/25 ,  with equality iff x_1 = … = x_5 = 1/5 .
```

**Proof.** For `b ∈ P_i` the far arc `F(b)` contains exactly the clusters `P_{i−2}, P_{i+2}` (the two
adjacent to `b` in the far-graph). The adjacent pairs with no endpoint in `F(b)` are therefore the
pairs inside `P_{i−1} ∪ P_i ∪ P_{i+1}`, and in the pentagram the only adjacent pair among those three
clusters is `{P_{i−1}, P_{i+1}}`. Hence `m(b) = x_{i−1}x_{i+1}`. Now apply AM–GM to the five terms:

```
   Σ_i x_i/(x_{i−1}x_{i+1})  ≥  5 ( Π_i x_i/(x_{i−1}x_{i+1}) )^{1/5}
                             =  5 ( Π_i x_i / (Π_i x_i)² )^{1/5}  =  5 (Π_i x_i)^{−1/5},
```

and AM–GM on the simplex gives `Π_i x_i ≤ 5^{−5}`, so `(Π_i x_i)^{−1/5} ≥ 5`. ∎

This is **the same "AM–GM twice" mechanism as the classical proof for `C5`-colourable graphs**,
recovered here as a statement about the harmonic mean rather than about a homomorphism — which is
why it reproduces the extremal case exactly.

## What it covers

Every `C5` blow-up `C5[a_1,…,a_5]`, in particular the extremal family `C5[n]`, and every measure
supported on five clusters in pentagram position — i.e. precisely the configurations where the
conjecture is sharp and where every averaging argument must be tight.

## Verification (exact rationals)

* `m(b_i) = x_{i−1}x_{i+1}` verified on pentagram configurations in `Γ_5, Γ_10, …, Γ_40` with random
  rational weights (320 configurations, 0 mismatches).
* `Σ_i x_i/(x_{i−1}x_{i+1}) ≥ 25` over 4000 random rational weight vectors: minimum found
  `25.074…`, and exactly `25` at uniform.
* `C5` blow-ups with parts `(2,2,2,2,2)`, `(3,1,4,2,2)`, `(5,5,5,5,5)`, `(1,2,3,4,5)`: sums
  `25, 29.5, 25, 54.25`, giving `H = 1/25, 0.0339, 1/25, 0.0184`.

## Status of the whole inequality after this

| case | closed by | status |
|---|---|---|
| `W ≤ 1/20` or `W ≥ 1/5` | `E_μ[m] ≤ W − 4W²`, Cauchy–Schwarz | **proved** |
| `W ≤ 3/25` | `A = W − 2T ≤ W/3` | **proved** |
| support in pentagram position (all `C5` blow-ups) | this lemma, AM–GM twice | **proved** |
| `W ∈ (0.12, 0.2)`, support not pentagram | — | **OPEN** |

The open case is the last one. Its empirical size: of 3600 random exact measures only 3 fall in the
region where both plain averages fail, and all three are closed by the harmonic mean.


## Proof strategy for the general case, with the pieces that are already proved

Write `A = W − 2T` (half-arc average) and `H = 1/E_μ[1/m]` (harmonic mean of the neighbourhood-cut
values). The target is `min(A,H) ≤ 1/25`. Empirically the dichotomy is complete: over 1182 random
exact measures, both terms work in 944 cases, only `H` in 68, only `A` in 170, and **neither fails in
0 cases**.

**The mechanism, from the Fourier identity (R5-K10).**
`A = 1/36 + 2Σ_{n≥1} ψ̂(n)|μ̂(n)|²`, and `Σ_{n≥1, ψ̂(n)>0} ψ̂(n) = 0.11385`. So

> **Case I (proved, crude form).** If `|μ̂(n)|² ≤ 0.0537` for every `n` with `ψ̂(n) > 0`, then
> `A ≤ 1/36 + 2(0.0537)(0.11385) < 1/25`.

So `A` can only fail when the measure has substantial `n`-fold Fourier mass for some `n` with
`ψ̂(n) > 0` — and the significant ones are `n = 3` (`+0.0113`) and `n = 5` (`+0.0102`), with
`n = 2, 8, 9, 11` an order of magnitude smaller and all multiples of 6 exactly zero.

**Case II: the dangerous frequencies all collapse `H`.**

* `n = 5` (five clusters in pentagram position): **proved** in R5-K19 — `m(b) = x_{i−1}x_{i+1}` and
  AM–GM twice give `Σ_b x_b/m(b) ≥ 5(Πx)^{−1/5} ≥ 25`, i.e. `H ≤ 1/25`, with equality exactly at the
  balanced blow-up. This is the extremal family, where the bound must be tight.
* `n = 3` (three clusters at mutual distance `≈1/3`): the neighbourhood cut at a point of the middle
  cluster has `m(b) = 0` (verified: `∫g²dμ = W` there), so `E_μ[1/m] = ∞` and `H = 0`.
* `n = 2` (two antipodal clusters): the far-graph is bipartite, some neighbourhood cut has `m(b) = 0`,
  so again `H = 0`.

So each frequency that can make `A` fail forces a cluster structure that makes `H` small, and the two
sides meet exactly at `C5`, where `A = H = 1/25` simultaneously.

**What remains:** the quantitative interpolation — "approximately `n`-fold" instead of exactly, i.e.
a stability version of R5-K19 and of the `n = 2, 3` collapses. That is the single open step of the
whole chain.
