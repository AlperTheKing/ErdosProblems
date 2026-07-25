# R5-K7 — partial proof of the arc-cut conjecture: three cases closed in closed form, one thin sliver left

Root-agent result, 2026-07-25. Target (R3-C11): for every probability measure `μ` on the circle
`R/Z` with adjacency `d(x,y) > 1/3`, some ARC cut has monochromatic mass `≤ 1/25`. Proving it gives
`max_x ψ(And(k),x) = 1/25` for every `k` (Heinig's Conjecture 6) and hence Erdős #23 for every
triangle-free graph with `δ > N/3`.

## 0. Notation

`g(x) = μ(F(x))` where `F(x) = (x+1/3, x+2/3)` is the far arc — the weighted degree;
`W = ½∫g dμ` the total adjacent mass; `T = ∫ t dW(t)` the mass-weighted mean pair distance,
so `T/W ∈ (1/3, 1/2]`.

## 1. Only two arc lengths are needed (exhaustively verified)

Arcs of length `≈ m/3` and `≈ m/2` alone give the same bound as the full two-parameter family:
zero violations of `25·mono ≤ q²` over **all** integer weightings with `q ≤ 15` on
`Γ_5,7,8,10,11,13,14,16,17,19,20,22,23`. Neither length alone suffices, and they fail on **disjoint**
witnesses (`claude_witness_regression.py`): half-arcs fail on the `(1,1,2,2,1)` weighting
(`2/49 > 1/25`), third-arcs fail on the uniform measure (`5/108`, `21/400`).

The `1/3`-arcs have an exact identification: **the `1/3`-arc cut at `b` is the neighbourhood cut
`A = N(b)`**, which is independent because the graph is triangle-free, and its monochromatic mass is

```
        m(b) = W − ∫_{N(b)} g dμ ,
```

the adjacent mass entirely outside `N(b)`. The half-arc cut at `a` has monochromatic mass
`cov(a) = ` the adjacent mass whose short arc misses both `a` and `a+1/2`.

## 2. Two closed-form bounds (both proved)

**(i) Neighbourhood cuts, `μ`-weighted position average.**

```
        min_b m(b)  ≤  ∫ m(b) dμ(b)  =  W − ∫ g² dμ  ≤  W − 4W² ,
```

the last step by Cauchy–Schwarz (`∫g dμ = 2W`). This holds for **every triangle-free weighted
graph**, not only circle graphs, since every neighbourhood is independent; the uniform-weight case
is the already-gated chain `bip ≤ |E| − (1/N)Σd(v)²`.

**(ii) Half-arc cuts, uniform position average.**

```
        min_a cov(a)  ≤  ∫ cov(a) da  =  W − 2T ,
```

because a pair at distance `t` fails to be separated by the antipodal cut `{a, a+1/2}` for exactly
an `a`-measure of `1 − 2t`.

## 3. The case analysis

`4W² − W + 1/25 ≥ 0` has the rational roots `1/20` and `1/5`. Hence the arc-cut conjecture is
**PROVED** in each of these cases:

| case | closed by | range |
|---|---|---|
| `W ≤ 1/20` | (i) via `W − 4W²` | sparse |
| `W ≥ 1/5` | (i) via `W − 4W²` | dense — **contains the extremal `C5` at `W = 1/5` exactly, with equality `1/25`** |
| `∫g² dμ ≥ W − 1/25` | (i), `μ`-weighted | non-regular far-degree |
| `2T ≥ W − 1/25` | (ii) | pairs not concentrated at distance `1/3` |

Since `T ≥ W/3`, case (ii) alone already covers `W ≤ 3/25 = 0.12`. So the residual is

```
        W ∈ (0.12, 0.2),   ∫g² dμ < W − 1/25,   and   2T < W − 1/25,
```

a thin sliver: `T/W ∈ (1/3, (1 − 0.04/W)/2)`, which at `W = 0.15` is `(0.3333, 0.3667)` and at
`W = 0.2` is `(0.3333, 0.4)`.

**Coverage in practice:** all 9 regression witnesses are closed by the case analysis, and of 2200
random exact measures over 11 circle graphs exactly **one** falls in the residual sliver.

## 4. The residual case, exactly

`Γ_11`, `x = (1/17, 3/17, 3/34, 0, 3/17, 3/17, 0, 0, 5/34, 5/34, 1/34)`:

```
        W = 111/578 = 0.192042 ,   T/W = 0.391892
        W − ∫g² = 825/19652 = 0.041980 > 1/25       (case (i) average fails, barely)
        W − 2T  = 12/289   = 0.041522 > 1/25       (case (ii) average fails, barely)
        BUT     min over 1/3-arcs = min over half-arcs = min over all arcs = 15/578 = 0.025952
```

so the true minimum beats its own average by a factor `1.62`. **The residual case is therefore not a
gap in the mechanism but a gap in the averaging step**: what is missing is a second-moment
(variance) argument showing that in this regime `m(b)` deviates enough from its mean for the minimum
to fall below `1/25`.

## 5. What remains, stated as one sentence

> For every probability measure on the circle with `W ∈ (0.12, 0.2)`, `∫g² dμ < W − 1/25` and
> `2T < W − 1/25`, either `min_b m(b) ≤ 1/25` or `min_a cov(a) ≤ 1/25`.

Anything proving that — a variance bound on `m`, a structural description of the measures in the
sliver, or a third explicit cut family — closes the arc-cut conjecture and with it the `δ > N/3`
range of Erdős #23, modulo the Vega half of the Brandt–Thomassé structure theorem.

*Every claim in §2 and §3 is a complete proof; §1 and the coverage figures in §3 are exhaustive or
sampled computations, labelled as such.*
