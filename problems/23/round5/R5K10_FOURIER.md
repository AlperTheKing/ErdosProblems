# R5-K10 — the half-arc quantity is a positive-definite Fourier form; only 3-fold and 5-fold structure is dangerous

Root-agent result, 2026-07-25. A new mechanism for this campaign: Fourier analysis /
positive-definiteness on the circle. It converts one of the two terms of the moment criterion
(R5-K9) into an exact spectral sum and identifies precisely which measures can make it large.

## The identity (proved, and machine-checked)

For a probability measure `μ` on `R/Z` with adjacency `d(x,y) > 1/3`, the half-arc average is

```
        A := W − 2T = ∫∫_{d(x,y) > 1/3} ( 1/2 − d(x,y) ) dμ(x) dμ(y) .
```

The integrand depends only on `s = x − y`, so with `ψ(s) = |s − 1/2|` on `(1/3, 2/3)` and `0`
elsewhere, Parseval gives

```
        A  =  Σ_{n ∈ Z}  ψ̂(n) · |μ̂(n)|²      =  1/36  +  2 Σ_{n ≥ 1} ψ̂(n) |μ̂(n)|² ,

        ψ̂(0) = 1/36 ,
        ψ̂(n) = (−1)^n [ sin(πn/3)/(6πn) + (cos(πn/3) − 1)/(2π²n²) ]   for n ≠ 0 .
```

`|μ̂(n)|² ≥ 0` always and `ψ̂(n) = O(1/n²)`, so the sum converges absolutely for every measure,
atomic or not. Verified numerically against the direct double integral on five measures (C5, `C7`,
the three-atom near-path, uniform, a random six-atom measure) — agreement to `10⁻⁵`, the truncation
error of the series.

## What the spectrum says

| `n` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ψ̂(n)` | −0.0206 | **+0.0040** | **+0.0113** | −0.0162 | **+0.0102** | 0 | −0.0060 | **+0.0046** | **+0.0013** | −0.0054 | **+0.0044** | 0 |

* The **uniform** measure has `μ̂(n) = 0` for `n ≠ 0`, so `A = 1/36 = 0.02778` exactly — comfortably
  below `1/25`, which is why the half-arc family handles it.
* `A > 1/25` requires `2 Σ_{n≥1} ψ̂(n)|μ̂(n)|² > 1/25 − 1/36 = 0.01222`, and the only positive
  coefficients of any size are `n = 3` (`+0.0113`) and `n = 5` (`+0.0102`). So **the half-arc term
  can fail only for measures with substantial 3-fold or 5-fold periodic structure**, and multiples
  of 6 contribute exactly nothing.
* That is exactly the observed dichotomy:
  * **5-fold** — the `C5` extremal, where `A = 1/25` precisely (the equality case);
  * **3-fold** — three clusters at mutual distance `≈1/3`, where `A = 0.0696 ≫ 1/25` but the
    *other* term of the criterion collapses: for the three-cluster measure `∫g²dμ = W`, so
    `B = W − ∫g² = 0`.

## Why this matters for the proof

The moment criterion of R5-K9 is `min(B − Var/(max−B), A) ≤ 1/25`. R5-K10 turns the `A`-side into a
spectral statement, so the remaining work has a concrete shape:

> Show that `2 Σ_{n≥1} ψ̂(n)|μ̂(n)|² > 0.01222` — i.e. large 3-fold or 5-fold Fourier mass — forces
> `B − Var_μ(m)/(max m − B) ≤ 1/25`.

The two extremes are already understood: pure 5-fold structure *is* the extremal `C5` (equality on
both sides), and pure 3-fold structure kills `B` outright. What is needed is the interpolation.

Note also `Σ_{n≥1, ψ̂(n)>0} 2ψ̂(n) = 0.2277`, so the crude bound `|μ̂(n)| ≤ 1` gives only
`A ≤ 0.2555`; the spectral route is useful only in combination with `B`, not on its own.

## Files

`(inline gate this session)` — direct double integral vs the truncated spectral sum, five measures.
