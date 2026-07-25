# R5-K21 — three more proved cases of the criterion, and exactly where the chain still leaks

Root-agent result, 2026-07-25, continuing R5-K19. Target: `min(A, H) ≤ 1/25` with
`A = W − 2T` and `H = 1/E_μ[1/m]`, `m(b)` the monochromatic mass of the neighbourhood cut at `b`.

## New structural facts (all proved)

Write, for a point `b` of the circle,

```
        L(b) = μ([b − 1/3, b)) ,   R(b) = μ((b, b + 1/3]) ,   g(b) = μ(F(b)) ,   c(b) = g(b) + μ({b}),
        so     L(b) + R(b) + c(b) = 1        (the four pieces partition the circle).
```

**(P1) `m(b) ≤ L(b)·R(b)`.** Every pair counted by `m(b)` has one endpoint in `[b−1/3,b)` and the
other in `(b, b+1/3]` — it *straddles* `b` — because a pair with both endpoints on the same side of
`b` within `1/3` is at distance `< 1/3` and so is not adjacent. Dropping the extra requirement
`s + t > 1/3` (with `s,t` the distances to `b`) gives the product. Verified: 0 failures in 1595
random exact measures. **Equality holds at `C5`**, where the two neighbouring atoms are at distance
`2/5 > 1/3`, so `m = L·R = (1/5)(1/5) = 1/25` exactly.

**(P2) closed-form bound.** `L·R ≤ ((L+R)/2)² = ((1−c)/2)²`, and `φ(t) = 4/(1−t)²` is convex with
`φ'' ≥ 24` on `[0,1)`, so Jensen with the strong-convexity remainder gives

```
        E_μ[1/m]  ≥  E_μ[φ(c)]  ≥  4/(1 − 2W − Q)²  +  12·Var_μ(c) ,        Q := Σ_a μ({a})² ,
```

using `E_μ[c] = 2W + Q`. Hence **`H ≤ (1 − 2W − Q)²/4`**, and therefore

> **`H ≤ 1/25` whenever `2W + Q ≥ 3/5`.**

At `C5`: `2W = 2/5`, `Q = 5·(1/5)² = 1/5`, so `2W + Q = 3/5` exactly and the bound gives exactly
`1/25` — **every step of the chain is simultaneously tight at the extremal measure**.

**(P3) the product form is sharper.** Keeping `L·R` instead of `((L+R)/2)²`, i.e. using
`E_μ[1/m] ≥ E_μ[1/(LR)]`, is strictly better: on the `(1,1,2,2,1)` witness it gives exactly `28`,
matching the true `E_μ[1/m]`, where the AM–GM version gives only `24.04`.

## Updated case list

| case | closed by | status |
|---|---|---|
| `W ≤ 1/20` or `W ≥ 1/5` | `H ≤ E_μ[m] ≤ W − 4W²` | **proved** |
| `W ≤ 3/25` | `A ≤ W/3` | **proved** |
| **`2W + Q ≥ 3/5`** | **(P2)** | **proved (new)** |
| support in pentagram position (every `C5` blow-up) | R5-K19, AM–GM twice | **proved** |
| `\|μ̂(n)\|² ≤ 0.0537` on every positive frequency | Fourier, R5-K10 | **proved** |
| remainder | — | **open** |

## Where the chain still leaks, measured

Violations of "`A ≤ 1/25` or the stated bound `≥ 25`", over the same 1595–1800 random exact measures:

| bound used in place of `E_μ[1/m]` | violations |
|---|---|
| `4/(1−2W−Q)²` (P2, AM–GM + Jensen) | 12 |
| `4/(1−2W−Q)² + 12 Var_μ(c)` (P2 with the strong-convexity term) | 12 |
| `E_μ[1/(LR)]` (P3, product kept) | **2** |
| exact `E_μ[1/m]` | **0** |

So the remaining leak is exactly the step `m ≤ L·R`: the two surviving measures are ones where the
straddle constraint `s + t > 1/3` removes a substantial part of `L·R`. The worst is on `Γ_17` with
support masses `(1/7, 1/42, 1/6, 1/6, 1/42, 1/7, 1/7, 4/21)`, where `A = 0.041450` and
`E[1/(LR)] = 21.47 < 25` while the exact `E[1/m] ≥ 25`.

**What remains is therefore a single quantitative statement about one relaxation step**, not about
the conjecture: bound `L·R − m(b)` — the mass of *non-adjacent* straddling pairs at `b` — well enough
that the product bound survives, or handle those measures by the `A` side.
