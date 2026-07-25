# R5-K23 — CORRECTION to the Fourier identity (R5-K10), and what Round 6 confirmed of my chain

Root-agent entry, 2026-07-25. Round 6's audit found two errors in my Fourier write-up; I verified
both myself and state the corrected result.

## The two errors

**(1) The coefficients decay like `1/n`, not `1/n²`, so the series is NOT absolutely convergent.**

```
        ψ̂(n) = (−1)^n [ sin(πn/3)/(6πn) + (cos(πn/3) − 1)/(2π²n²) ]
```

The first term is `Θ(1/n)` whenever `3 ∤ n`. Verified: `n·ψ̂(n)` for `n = 10, 50, 100, 500, 1000` is
`−0.0535, +0.0444, −0.0467, +0.0458, −0.0460` — it oscillates and does not tend to `0`. The partial
sums `Σ_{n<N}|ψ̂(n)|` are `0.149, 0.220, 0.291` for `N = 10², 10³, 10⁴`, growing logarithmically.
R5-K10's claim "`ψ̂(n) = O(1/n²)`, so the sum converges absolutely for every measure, atomic or not"
is **WRONG**. The series must be read as a symmetric limit `lim_{N→∞} Σ_{|n| ≤ N}`.

**(2) There is an exact defect term when the measure has pairs at distance exactly `1/3`.**

`ψ(s) = |s − 1/2|` on `(1/3, 2/3)` and `0` outside jumps at `s = ±1/3`, and a Fourier series converges
at a jump to the midpoint. Adjacency is `d > 1/3` **strictly**, so a pair at distance exactly `1/3`
contributes `0` to `A` but `1/12` per unit mass to the series. Corrected identity:

```
        A  =  lim_{N→∞} Σ_{|n| ≤ N} ψ̂(n)|μ̂(n)|²  −  (1/12)·τ ,
        τ  =  mass of ordered pairs at circular distance exactly 1/3.
```

Verified exactly: three atoms at `0, 1/3, 2/3` (all pairs tied) have `A = 0`, series `= 0.055556`,
`τ = 2/3`, and `0.055556 − (2/3)/12 = 0` exactly; six atoms at `k/6` have `A = 0`, series `0.027778`,
`τ = 1/3`, difference `0` exactly; five equal atoms have `τ = 0` and series `= A = 0.04`.

**Consequence for R5-K10's reading.** The qualitative conclusion — that `A` can exceed `1/25` only
for measures with substantial low-frequency Fourier mass — survives, with `n = 3` (`+0.0113`) and
`n = 5` (`+0.0102`) still the two largest positive coefficients. But "only `n = 3, 5` are positive"
is false: there are 105 positive coefficients below `n = 200` (`2, 3, 5, 8, 9, 11, 14, 15, 17, 20,
21, 23, …`), and any argument that sums them needs the conditional convergence handled.

## What Round 6 CONFIRMED of my chain (re-derived independently by the auditor)

* the blow-up identity and the equivalence "conjecture ⟺ `max_x ψ ≤ 1/25` for all triangle-free `H`";
* `And(k) ≅ Γ_{3k−1}` for `k = 2..8`, including the multiplier map;
* the identity `∫m dμ = W − ∫g²dμ` **and** the pairing hazard (the arc must be attached to `b`
  through `N(b)`, the error I made and caught earlier);
* `bound_k` is a valid upper bound on `min_b m(b)` for every `k`, and `A` is exactly the half-arc
  position average;
* `ARCBOUND = ψ` on all 12 witnesses and on 379 exact random circle measures — so on the tested
  ground the arc family attains the true minimum, and the gap I worried about does not exist there.

## Ranges: what my own runs actually cover

Checked against the raw logs, not the summaries:

* `claude_arccut.exe` over all integer weightings with **`q ≤ 15` completed for `Γ_14, 16, 17, 19,
  20, 22, 23, 25`** and `q ≤ 16` for `Γ_5, 8, 10, 11, 13`; Wagner and Petersen to `q = 45`.
* `claude_blowup_zero.exe`: `q ≤ 24` for `And(4)`, Grötzsch, `C11(1,3)`; `q ≤ 20` for `C13(1,5)` and
  the extremal graphs at `N = 12, 13`; `q ≤ 19` for `And(5)` and the `N = 14` extremal.
* The **two-length** run (`--twolen`) printed `0` violations for `Γ_5 … Γ_23` but the loop hit its
  wall clock at `Γ_25`, so that claim is stated for `Γ_5 … Γ_23` only.
