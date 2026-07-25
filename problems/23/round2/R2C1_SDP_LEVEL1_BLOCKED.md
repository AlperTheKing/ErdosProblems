# R2-C1 — the level-1 SDP certificate route is BLOCKED (obstruction, measured)

Root-agent result, 2026-07-25. This **corrects a recommendation I made myself** in
`round1/CLAUDE_GATE_RESULTS.md` §3g.

## What was recommended, and why it is wrong

§3g recorded the certificate bottleneck: `max_x psi(H,x) <= 1/25` needs a rigorous upper bound;
hill-climbing gives only lower bounds; the two natural **fixed-multiplier** certificates were proved
too weak (uniform over all cuts → `1/8`; the five `C5` rotation cuts → `1/20`, failing on `C5`
itself); and §3h showed exact interval branch-and-bound does not scale (stalls on Wagner at `n = 8`
and Petersen at `n = 10`). The recorded conclusion was that a valid certificate needs an
**x-dependent multiplier, i.e. an SDP/Lasserre dual**. That direction is now measured, and **level 1
does not work.**

## The relaxation

With `q_S(x) = sum_{uv mono under S} x_u x_v = (1/2) <A_S, x x^T>`, lift `Y = x x^T`:

```
maximise t
s.t.   (1/2) <A_S, Y> >= t                for every cut S
       [[1, x^T],[x, Y]] psd,  Y >= 0 entrywise,  x >= 0,  sum(x) = 1
       sum_v Y[u,v] = x[u]  for every u,   Y[u,u] <= x[u]
```

`Y = x x^T` is feasible for every `x` in the simplex, so the optimum is a valid **upper** bound on
`max_x psi(H,x)`. Solved with CVXPY 1.9.1 / Clarabel.

## Results

| pattern | n | cuts | true value | level-1 SDP bound | ratio | verdict |
|---|---|---|---|---|---|---|
| **C5** | 5 | 16 | **exactly 1/25 = 0.040000** | **0.055279** | **1.382×** | **too weak** |
| C7 | 7 | 64 | 1/49 = 0.020408 | 0.037575 | 0.939× | certifies |
| Wagner C8(1,4) | 8 | 128 | ≈ 0.038652 | 0.056635 | 1.416× | too weak |
| Petersen | 10 | 512 | ≈ 0.030879 | 0.060000 | 1.500× | too weak |
| Grötzsch | 11 | 1024 | ≈ 0.037700 | 0.058328 | 1.458× | too weak |
| C11(1,3) | 11 | 1024 | ≈ 0.036426 | 0.065647 | 1.641× | too weak |
| C13(1,5) | 13 | 4096 | ≈ 0.035170 | 0.069393 | 1.735× | too weak |

**The decisive line is `C5`.** Its true value is exactly `1/25`, and the relaxation returns

```
        0.05527864045…  =  (5 − √5)/50        (matched to ten digits)
```

a **38.2 % gap on the extremal object itself**. Since `C5` is the graph the conjecture is tight on,
a relaxation that cannot see `1/25` there cannot certify `1/25` anywhere.

**The row-sum constraints change nothing.** A first version without
`sum_v Y[u,v] = x[u]` and `Y[u,u] <= x[u]` returned *identical* optima to six decimals on every
pattern, so those moment constraints are inactive at the optimum and the weakness is intrinsic to
level 1, not an oversight in the formulation.

The appearance of `√5` is not a coincidence: `(5 − √5)/50` is a theta-function-flavoured value, and
the Lovász theta number of `C5` is `√5`. The level-1 lift is essentially seeing the theta body of
`C5` rather than its true cut structure.

## Consequence for the campaign

**BLOCKED**, with the blocking statement verbatim:

> *the level-1 (Shor / doubly-nonnegative, with or without the moment row-sum constraints)
> SDP relaxation of `max_x psi(H,x)` has value `(5 − √5)/50 > 1/25` on `C5`, so no aggregation of
> level-1 SDP duals can certify the `1/25` ceiling for any pattern.*

Reopen only with a **level ≥ 2 Lasserre relaxation**, whose moment matrix is indexed by monomials of
degree ≤ 2 and therefore has size `1 + n + C(n,2)`: 16 for `C5`, 37 for Wagner, 56 for Petersen,
92 for `C13(1,5)`. Those sizes are computationally feasible; the work is in generating the localizing
matrices for the simplex constraints and the `2^(n-1)` cut inequalities, then rationalising the dual.
**Calibrate any such attempt on `C5` first** — if level 2 does not return exactly `1/25` there, it is
equally useless, and that single computation decides the whole route cheaply.

## Files

- `claude_psi_sdp.py` — level-1 doubly-nonnegative version.
- `claude_psi_sdp2.py` — level-1 lifted version with row-sum/moment constraints (identical optima).
