# Band 8 — r = 4 Reeve-dimension census, weight band W = |nu| in [61, 90]

Hunter 8 of 12 of the r = 4 sweep for a counterexample to the
**King–Tollu–Toumazet positivity conjecture** (2004): a triple of partitions
(λ, μ, ν) with |λ|+|μ| = |ν| whose stretched Littlewood–Richardson polynomial
P(n) = c(nν; nλ, nμ) has a strictly **negative** coefficient.

## Why r = 4 and why a1 is the only live coefficient

Knutson–Tao: c(ν; λ, μ) = #(Q(λ,μ,ν) ∩ Z^D) where Q is the hive polytope on the
D = (r−1)(r−2)/2 interior vertices of a side-r triangular array. For r = 4,
D = 3 — the **Reeve dimension**, the smallest dimension in which an Ehrhart
polynomial can have a negative coefficient. Stretching dilates Q, so P is the
Ehrhart counting function of Q and deg P = dim Q ≤ 3.

Writing P(n) = a3 n³ + a2 n² + a1 n + a0 and h* = (1, h1, h2, h3):

```
a0 = 1                                   (always)
a3 = V/6,  V = normalized volume > 0     (when dim Q = 3)
a2 = 1 + (h1 − h3)/2                     (≥ 0 in everything observed)
6 a1 = 11 + 2 h1 − h2 + 2 h3             ← the ONLY coefficient that can be < 0
V   = 1 + h1 + h2 + h3
```

so a **KTT counterexample in this cell is exactly `h2 > 11 + 2 h1 + 2 h3`**.
In terms of the raw stretched counts (L(n) = P(n), L(0) = 1):

```
6 a1 = −11 + 18 L(1) − 9 L(2) + 2 L(3)
V    =        L(3) − 3 L(2) + 3 L(1) − 1
```

The classical Reeve tetrahedron T_q sits at h* = (1, 0, q−1, 0), i.e. c = L(1) = 4
lattice points and V = q, giving a1 = 2 − q/6 < 0 for q ≥ 13. So the sharpest
single statistic to watch is **max V at h1 = 0 (c = 4)**: a Reeve-type
counterexample needs it to reach 13.

## Files

| file | what |
|---|---|
| `bandscan.cpp` / `bandscan.exe` / `bandscan2.exe` | exact 64-bit-integer band scanner; rhombus rows and fibre counting taken verbatim from the validated `../../r4_reeve/gapscan.cpp` |
| `validate_band8.py` / `validation_band8.json` | cross-validation of `bandscan.exe` against the exact-`Fraction` reference engine `../../hive4.py` on random band triples |
| `drive_band8.py` | two-stage driver (nu steering, then exhaustive splits) |
| `nutop_<W>.log` | stage 1: for every ν of weight W, hill-climb over splits to maximise V |
| `nu_<n1>_<n2>_<n3>_<n4>.log` | stage 2: **exhaustive** over all ordered splits (λ, μ) of that ν |
| `wexh_<W>.log` | **exhaustive** over every triple of weight W |
| `randband*.log`, `climbv*.log` | uniform random band census / large max-V climb |
| `band_size.json` | exact count of ordered triples in the band |
| `manifest.json` | assembled result record |

## Rigor contract

* All arithmetic is exact integer arithmetic. No floating point decides
  anything (the only `double` in the source is a hill-climb heuristic score).
* Splits with λ₁ > ν₁ or μ₁ > ν₁ are skipped: then λ ⊄ ν (resp. μ ⊄ ν), so
  c(nν; nλ, nμ) = 0 for **every** n ≥ 1, P ≡ 0, and there is no coefficient to
  be negative. This is an exact criterion, not a heuristic prune.
* A negative coefficient would be re-verified with the two independent LR
  counters `engine/lr_hive.exe` (A) and `engine/engineB_lrrule.py` (B) at
  n = 0..5 before being reported.
* **Absence of a negative coefficient proves nothing about the KTT conjecture
  and is not evidence for it.** It closes the enumerated window and nothing
  more. The band as a whole is *not* exhausted (it holds 1.878 × 10^12 ordered
  triples); the sub-levels declared exhaustive in `manifest.json` are.
