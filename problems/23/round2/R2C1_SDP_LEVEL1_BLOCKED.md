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

## Level 2 was then run, per the decision rule above. It also fails.

`claude_lasserre2_c5.py` implements the genuine level-2 moment relaxation on `C5`: moment vector
indexed by `|α| ≤ 4` (126 entries), moment matrix `M₂` of size 21×21, localizing matrices `M₁(xᵢ y)`
for each `xᵢ ≥ 0`, the simplex equalities `Σᵢ y_{α+eᵢ} = y_α` on every `|α| ≤ 3`, all moments
nonnegative, and a localizing matrix `M₁(q_S y) − t·M₁(y) ⪰ 0` per cut. `t` enters bilinearly so the
optimum is found by bisection (24 steps), each step a feasibility SDP.

| relaxation | bound on `max_x ψ(C5,x)` | ratio to the true `1/25` |
|---|---|---|
| truth | **0.040000** | 1.000× |
| level 1 (doubly nonnegative) | 0.055279 = (5 − √5)/50 | 1.382× |
| **level 2 (moment, 21×21)** | **0.053170** | **1.329×** |

**A bug I made and fixed, recorded because the fix matters.** My first level-2 run returned
`0.057409`, which is *larger* than the level-1 bound — impossible for a hierarchy, and therefore a
formulation error rather than a result. The cause: I had omitted the nonnegativity of the moments
themselves. Since `x ≥ 0` on the simplex, every monomial is nonnegative and hence every moment
`y_α ≥ 0`; without that the level-2 relaxation is genuinely weaker than the doubly-nonnegative
level-1 one, which does impose entrywise `Y ≥ 0`. With `y ≥ 0` added the hierarchy is monotone again
(`0.053170 < 0.055279`) and the numbers above are the corrected ones. **Anyone rebuilding this must
include the moment nonnegativity.**

**Verdict: the moment/SOS hierarchy is not a practical certificate route here.** Going from level 1
to level 2 closed `0.00211` of a `0.01528` gap — about 14 % of the remaining distance — while the
moment matrix grew from `n+1` to `1 + n + C(n+1,2)`. At that rate roughly fifteen levels would be
needed on `C5` alone, and the whole computation would then have to be redone, at far larger size,
for every pattern. Level 3 on `C5` already needs a 56×56 moment matrix and level 3 on Wagner a
165×165 one, for a bound that would still be far from `1/25`.

Blocking statement, verbatim:

> *on `C5`, whose true value is exactly `1/25`, the Lasserre relaxations give `(5 − √5)/50 ≈ 0.05528`
> at level 1 and `≈ 0.05317` at level 2, closing only about one seventh of the gap per level; the
> hierarchy therefore cannot certify the `1/25` ceiling at any computationally reachable level.*

## Correction: symmetry reduction CANNOT help, and I should not have suggested it

An earlier version of this note proposed a symmetry-reduced SDP for vertex-transitive patterns, on
the idea that `C5`'s rotational symmetry "could be tight where the generic one is not". **That is
false, and the one-line proof is worth recording so nobody spends time on it.**

If a convex program is invariant under a group `G` acting on its variables, then for any feasible
point `p` the average `(1/|G|) Σ_{g∈G} g·p` is again feasible (the feasible set is convex and
`G`-invariant) and has the same objective value (the objective is linear and `G`-invariant). Hence
the optimum is attained at a `G`-invariant point, and restricting the program to `G`-invariant
points returns **exactly the same optimal value**. Symmetry reduction (block-diagonalisation) is a
purely computational device: it makes the SDP smaller and faster, never tighter.

Since the level-1 and level-2 relaxations above are already invariant under `Aut(C5) = D₅`, their
symmetry-reduced versions would return `(5 − √5)/50` and `0.053170` unchanged. Route closed.

## What is actually left

A **structurally different certificate** is needed — one that uses the fact that `q_S` ranges over
*cuts* rather than over arbitrary quadratic forms. Generic relaxations of the max-min do not see
that, which is exactly why they stall at `0.053` on an object whose truth is `0.040`.

## Exact lower bounds via the blow-up identity (side result)

While testing this, the blow-up identity gives a way to compute **exact rational** lower bounds
instead of floating-point ones: `psi(H, a/q) = bip(H[a])/q²`, so
`u_q(H) := max over integer a with Σa = q of bip(H[a])/q²` is exact and increases to
`max_x psi(H,x)` (`claude_blowup_sup.cpp`).

Calibration on `C5` is perfect: `u_q` never exceeds `1/25` and attains it exactly at
`q = 5, 10, 15` — the multiples of five, i.e. the balanced blow-ups.

For Wagner `C8(1,4)`, `u_q` for `q = 8 … 26` climbs to `6/169 = 0.035503`, still well under `1/25`.
**But this does not settle Wagner**, and the honest reason is that the sequence has not converged:
the exact rational point found earlier by hill-climbing already gives
`max_x psi(Wagner) ≥ 15341/396900 = 0.038652`, which the integer-weight search only reaches at
denominators far beyond `q = 26`. So the current status of Wagner is

> `0.038652 ≤ max_x psi(Wagner) ≤ ?`, with no upper bound available by any method tried here.

Wagner remains the tightest open case and the right first target for any new certificate.

## Files

- `claude_psi_sdp.py` — level-1 doubly-nonnegative version.
- `claude_psi_sdp2.py` — level-1 lifted version with row-sum/moment constraints (identical optima).
