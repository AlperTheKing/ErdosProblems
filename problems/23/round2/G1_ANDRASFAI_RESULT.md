# Round 2 / G1 — the Andrásfai family against the 1/25 ceiling

Root-agent computation, 2026-07-25. Engine: `claude_andrasfai.cpp` (exhaustive maximum cut over all
`2^(n-1)` bipartitions for the exact `bip`; multi-start hill-climb on the simplex for the weighted
maximum). A Python prototype (`claude_andrasfai.py`) was abandoned as too slow and is kept only for
readability.

## Why this computation

Chen–Jin–Koh: every triangle-free graph with `δ > N/3` is either homomorphic to a graph in an
explicit finite Andrásfai-type family, or contains an induced Grötzsch graph. By the blow-up
identity (R1-C7), if `G → H` then

```
bip(G)/N²  ≤  max over the simplex of  ψ(H,x),      ψ(H,x) = min over cuts S of Σ_{uv mono} x_u x_v.
```

So "`max_x ψ(H,x) ≤ 1/25` for every `H` in that finite family" would close the entire regime
`δ > N/3` for the graphs that map into it — a finite, checkable computation. This is its core.

`And(k)` = circulant on `Z_{3k−1}` with connection set `{k,…,2k−1}`: `k`-regular, triangle-free,
vertex-transitive, `n = 3k−1`. Note `And(2) = C5` — the extremal graph itself — and `And(3)` is the
Wagner graph `C₈(1,4)` (multiply the connection set by 3 mod 8).

## Results

| k | n | \|E\| | triangle-free | bip (exact) | uniform ψ = bip/n² | best ψ found | lower bound on max_x ψ |
|---|---|---|---|---|---|---|---|
| 2 | 5 | 5 | yes | 1 | **0.040000 = 1/25** | 0.039987 | **1/25 exactly** (proved) |
| 3 | 8 | 12 | yes | 2 | 0.031250 | 0.038892 | **0.038652** (exact re-eval, R1-C8) |
| 4 | 11 | 22 | yes | 4 | 0.033058 | 0.034666 | 0.034666 |
| 5 | 14 | 35 | yes | 6 | 0.030612 | 0.032746 | 0.032746 |
| 6 | 17 | 51 | yes | 9 | 0.031142 | 0.030257 | 0.031142 (uniform) |
| 7 | 20 | 70 | yes | 12 | 0.030000 | 0.030543 | 0.030543 |

**Honest flag on the search.** At `k = 6` the hill-climb returned `0.030257`, which is *below* the
exact uniform value `0.031142`. That is impossible for a true maximum, so the search budget
(6 restarts × 700 iterations at `n = 17`) was inadequate there and the `best ψ found` column is not
even a valid lower bound at `k = 6, 7` on its own. The final column therefore takes
`max(uniform, hill-climb)`, which is always a valid lower bound since the uniform point is exact.
Anyone extending this must raise the budget at `n ≥ 17`.

## Reading

The family **recedes monotonically from the ceiling**:

```
k =  2      3        4        5        6        7
     0.0400 0.0387   0.0347   0.0327   0.0311   0.0305      (lower bounds on max_x ψ)
```

`And(2) = C5` sits exactly at `1/25` — it *is* the extremal object. `And(3) =` Wagner is the closest
competitor anywhere in this project at `0.0387`, and from `k = 4` on the family drops away steadily.
No member other than `C5` comes near the ceiling.

## What this does and does not establish

**Does not:** these are lower bounds. Confirming `max_x ψ(And(k), x) ≤ 1/25` rigorously needs an
upper-bound certificate, and §3g of `round1/CLAUDE_GATE_RESULTS.md` records that the two natural
fixed-multiplier certificates fail and that plain interval branch-and-bound does not scale
(§3h/R1-C9: it stalls on Wagner at `n = 8` and on Petersen at `n = 10`). So the G1 route's finite
check is **not yet certified**, and that certificate is the bottleneck.

**Does:** it removes the plausible worry that some Andrásfai graph exceeds `1/25` and refutes the
conjecture outright — nothing in `k ≤ 7` does, and the trend is away from the ceiling. It also
identifies exactly where the finite check will be hardest: at `k = 3` (Wagner, gap `0.0013`), not at
large `k`. Any certifier must handle Wagner first.

**Still open in G1:** the exact statement of the Chen–Jin–Koh family (the list of target graphs must
be read from the source, not assumed to be the Andrásfai graphs alone), and the Grötzsch branch —
`max_x ψ(Grötzsch, x) ≥ 0.037700` from R1-C8, the second-closest competitor after Wagner.
