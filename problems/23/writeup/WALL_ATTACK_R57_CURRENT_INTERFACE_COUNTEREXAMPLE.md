# R57 current-interface counterexample

Source: independent GPT-5.6 Pro audit, 2026-07-12. Attached checker SHA-256 reported by the source: `7aae03d129191646a42c3d228456455a04295bc8b2f070e6a579ceca5170b868`.

## Verdict

The current `CheckedSameAtomExclusiveFork` fields, triangle-freeness, maximum-cut optimality, connected blue graph, checked Row5 semantics, and Gamma-minimality do not imply an R56 negative opposite-corner pair. Therefore R57's seven-row-shape to six-menu/15-pair normalizer is not derivable from the current interface.

## Graph

Core vertices are `s,t,a1,a2,a3,b1,b2,b3`. Add one private leaf `u'` for each core vertex `u`.

Blue edges are the two length-four paths

```
s-a1-a2-a3-t
s-b1-b2-b3-t
```

and the eight pendant edges `u-u'`. The sole bad edge is `s-t`.

Use the cut with core shore `{s,t,a2,b2}` versus `{a1,a3,b1,b3}`, placing every leaf opposite its parent. All 16 blue edges cross and `s-t` is bad.

## Production hypotheses

- The graph is triangle-free: its core is two 5-cycles sharing only `s-t`; pendants create no cycles.
- The blue graph is connected.
- The cut is maximum. Each 5-cycle has at most four crossing edges; adding their cut values double-counts `s-t`, so the core contributes at most 8. Pendants contribute at most 8. The displayed cut attains 16.
- It is Gamma-minimal. Every maximum cut leaves one of 17 edges bad. For a connected-blue maximum cut, the bad endpoints have even blue distance; triangle-freeness excludes distance 2, hence ell >= 5 and Gamma >= 25. The displayed cut has `d_B(s,t)=4`, hence Gamma=25.
- The complete shortest-row family for `s-t` is exactly the two displayed rows.

The fork has first divergence at position 1 and aligned internal-sharing mask `(0,0,0)`, one of the seven real Row5 shapes.

## Failure of every mask pair

For any vertex sets `X,Y`, let

```
loss(S) = |B intersect delta(S)| - |M intersect delta(S)|
mu(A,C) = |B intersect E(A,C)| - |M intersect E(A,C)|.
```

The exact four-corner identity gives

```
loss(X)+loss(Y)-2*mu(X\Y,Y\X)
  = loss(X intersect Y)+loss(X union Y).
```

Maximum-cut optimality makes every loss nonnegative. Thus no pair `X,Y` in the entire graph can satisfy

```
loss(X)+loss(Y) < 2*mu(X\Y,Y\X).
```

In particular, no six-menu extraction or 15-pair catalogue map can produce the required negative pair.

## Missing field

Private blue leaves raise row-mask losses without changing the opposite-corner term. Attaching `k` private blue leaves to every row vertex adds `k*(|X|+|Y|)` to the four-corner margin while preserving the literal rows, fork fields, triangle-freeness, maximum-cut optimality, connectedness, and Gamma-minimality.

R57 therefore needs explicit additional data from the positive-defect/saturated rotor context: a checked branch-window embedding plus a full-graph boundary-protection inequality. That data is not reconstructible from the current fork record or the seven row-intersection shapes.