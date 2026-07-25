# Directed-C4 obstruction to loss-accounting tournament completion

Status: **canonical obstruction**.

This hand audit is independent of the earlier certifying-completion
obstruction. It concerns only the weaker loss-accounting frontier lemma in
`APPROACH_REGISTRY.md`.

## Oriented graph

Let `D` be the directed four-cycle on vertices `0,1,2,3`:

```text
0: [1]
1: [2]
2: [3]
3: [0]
```

Thus, with indices modulo four,

```text
N_D+(f)  = {f+1},
N_D++(f) = {f+2}.
```

The only missing unordered pairs are `{0,2}` and `{1,3}`, so there are
exactly four tournament completions.

## Exhaustion of median-order feeds

For a tournament `T` and a proposed last vertex `f`, the largest possible
number of forward arcs in an order ending at `f` is

```text
F_T(f) = d_T-(f) + m(T-f),
```

where `m(T-f)` is 3 if the remaining three-vertex tournament is transitive
and 2 if it is a directed triangle. Therefore the maximum of the four
displayed values gives all possible feeds of median orders. When the maximum
is 5 in the table below, the first three vertices must occur in the unique
transitive order, so the displayed median order is also unique.

| `0-2` | `1-3` | `(F(0),F(1),F(2),F(3))` | unique median order | feed |
|:---|:---|:---|:---|---:|
| `0->2` | `1->3` | `(4,3,4,5)` | `(0,1,2,3)` | 3 |
| `0->2` | `3->1` | `(3,4,5,4)` | `(3,0,1,2)` | 2 |
| `2->0` | `1->3` | `(5,4,3,4)` | `(1,2,3,0)` | 0 |
| `2->0` | `3->1` | `(4,5,4,3)` | `(2,3,0,1)` | 1 |

Each displayed order has five forward arcs. Every other possible final
vertex has strictly smaller `F_T(f)`, so the table exhausts every
completion/median-feed pair without invoking a search.

## Exact loss ledger

Use the registered definitions

```text
A_f = N_T+(f)  setminus N_D+(f),
L_f = N_T++(f) setminus N_D++(f),
M_f = N_D++(f) setminus N_T++(f).
```

| completion diagonals | feed `f` | `N_T+(f)` | `N_T++(f)` | `A_f` | `L_f` | `M_f` |
|:---|---:|:---|:---|:---|:---|:---|
| `0->2, 1->3` | 3 | `{0}` | `{1,2}` | `{}` | `{2}` | `{}` |
| `0->2, 3->1` | 2 | `{3}` | `{0,1}` | `{}` | `{1}` | `{}` |
| `2->0, 1->3` | 0 | `{1}` | `{2,3}` | `{}` | `{3}` | `{}` |
| `2->0, 3->1` | 1 | `{2}` | `{0,3}` | `{}` | `{0}` | `{}` |

In every row,

```text
|L_f| = 1 > 0 = |A_f|+|M_f|.
```

Hence no tournament completion of `D` and no median-order feed of that
completion satisfies the frontier inequality.

For completeness, the accounting identity itself remains exact. At every
listed feed,

```text
|N_D++(f)|-|N_D+(f)| = 1-1 = 0,
|N_T++(f)|-|N_T+(f)| = 2-1 = 1,
|A_f|+|M_f|-|L_f|    = 0+0-1 = -1.
```

Thus the identity reads `0=1-1`; the failed inequality is strictly stronger
than the SNP already witnessed by every vertex of the directed cycle.

## Verdict

The registered loss-accounting frontier lemma is false. The directed
four-cycle is a canonical obstruction, and no larger sparse orientation is
needed to kill this route. This does not disprove SSNC.
