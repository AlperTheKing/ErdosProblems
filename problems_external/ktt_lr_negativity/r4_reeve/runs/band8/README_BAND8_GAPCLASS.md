# Band 8, second pass — the band W = |ν| ∈ [61, 90] made EXHAUSTIVE

The first pass (`README_BAND8.md`, `wexh_61..67.log`) enumerated raw triples and
got through W = 61…67 out of 61…90: 7 weights, 7.2 × 10^10 of the band's
1.878 × 10^12 ordered triples. The remaining 23 weights were out of reach by
raw enumeration (W = 90 alone holds 2.03 × 10^11 triples).

This pass closes the whole band by scanning the **gap moduli space** instead.

## The reduction

`c(nν; nλ, nμ)` is unchanged by

```
(λ, ν) → (λ + 1⁴, ν + 1⁴)          (μ, ν) → (μ + 1⁴, ν + 1⁴)
```

so every statistic depends on (λ, μ, ν) only through the nine gaps

```
a_i = λ_i − λ_{i+1},   b_i = μ_i − μ_{i+1},   c_i = ν_i − ν_{i+1}      (i = 1,2,3)
```

Write `Aw = a₁+2a₂+3a₃ = |λ| − 4λ₄`, and `Bw`, `Cw` likewise. A gap class is
realised by a triple of weight W iff

```
Cw ≤ W,   4 | (W − Cw),   Aw + Bw ≤ W,   4 | (W − Aw − Bw)
```

and then ν₄ = (W−Cw)/4 is forced while (λ₄, μ₄) ranges over the
`(W − Aw − Bw)/4 + 1` ordered splits. So the band region is

```
R = ⋃_{W=61..90} { (a,b,c) ≥ 0 : Cw ≤ W, Aw+Bw ≤ W, 4 | W−Cw, 4 | W−Aw−Bw }
```

`|R| = 176 528 678 464` gap classes.

## Why this is exhaustive and not a sample

Summing the multiplicity `(W−Aw−Bw)/4 + 1` over R, weight by weight, must
reproduce the exact number of ordered triples in the band. It does, to the
digit (`--count`, `count_region.log`):

```
Σ multiplicities = 1 877 911 502 602 = band_total of band_size.json
```

and per weight as well (e.g. W = 61: 6 108 384 018; W = 90: 202 880 443 392).
A region that were too small, too large, or mis-congruent could not match this
sum. The scan then enumerates every class of R, using only the exact symmetry
`c(ν; λ, μ) = c(ν; μ, λ)` to visit an unordered pair once with weight 2.

## Validation chain (all exact integers / `Fraction`, no floating point)

| gate | result |
|---|---|
| region multiplicity sum vs `band_size.json` | exact match, band and per-weight |
| gap scan of W = 61 vs the independent **raw-triple** exhaustive scan of the same weight (6.1 × 10⁹ triples, different code path) | identical `min 6a1 = 11`, `maxV = 326`, `maxV at h*₁=0 = 1`, `max h*₂ = 202`, `max V/(L₁+h*₃) = 324/126`, and every `maxV_at_c` |
| fast (regrouped) lattice count vs the reference routine | 750 101 random classes, 0 mismatches |
| gap scanner vs `hive4.py` exact-`Fraction` engine, on the ORIGINAL band triple (not the representative) | 300 triples, 0 mismatches (`validation_gapscan.json`) |
| polytope L(n) vs stretched LR coefficients from engine A (`lr_hive.exe`) and engine B (`engineB_lrrule.py`), n = 1,2,3 | 8 triples × 3 stretches × 2 engines, all equal (`xengine_band8.json`) |

## What is being looked for

With `P(n) = a₃n³ + a₂n² + a₁n + 1` and `h* = (1, h₁, h₂, h₃)`:

```
a₃ = V/6 > 0 ,   a₀ = 1 ,   2a₂ = 2 + h₁ − h₃ ,
6a₁ = −11 + 18L₁ − 9L₂ + 2L₃ = 11 + 2h₁ − h₂ + 2h₃ = 3(L₁ + h*₃) − V
```

so `a₁` is the only coefficient that can be negative, and

```
KTT counterexample in this cell  ⟺  V / (L₁ + h*₃) > 3  ⟺  h₂ > 11 + 2h₁ + 2h₃
```

The Reeve tetrahedron `T_q` (h* = (1,0,q−1,0), c = 4, V = q, a₁ = 2 − q/6) is the
classical dim-3 witness and needs q ≥ 13; its band-8 analogue is the statistic
**max V at h*₁ = 0**.

## Rigor note

Absence of a negative coefficient in this band closes the enumerated window and
is **not** evidence for the King–Tollu–Toumazet conjecture.
