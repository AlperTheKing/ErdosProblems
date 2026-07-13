# R42 source-swap matching audit

## Verdict

`NoPositiveDefectSourceSwapRotor` is **not proved or refuted** by exact
physical-key turnover plus `BaseKeyComponentCoherent`.  Those two facts do not
imply an augmentation or a strict defect trade.  The checker in this directory
gives an exact two-state positive-defect matching countermodel to that proposed
inference.  It is not a real triangle-free maximum-cut cage, so it does not
refute the graph theorem itself.

## 1. Exact physical-key turnover

Consider a support-constant genuine detour

```text
Q  = (..., x, m, y, ...)
Q' = (..., x, v, y, ...).
```

Before the move, `xv` and `vy` are active and absent from every selected row.
Inducedness of a shortest four-edge row implies

```text
pairCount(v,x)=pairCount(x,v)=pairCount(v,y)=pairCount(y,v)=0.
```

After the move, support constancy makes `xm` and `my` disappear.  Hence the
target has the four new free ordered bases

```text
(m,x), (x,m), (m,y), (y,m),
```

and loses the four old free ordered bases with `v` in place of `m`.  Each base
has two physical keys, one for each half.  Thus the raw turnover is exactly
eight keys out and eight keys in.

In the source-swap SCC, each relevant active path lies in an active component,
so every endpoint of its two active edges is an `ActiveOwner`.  The production
definition

```text
ScopedReserved(s) := s.half=0 and activeGraph.Adj(s.x,s.y)
                     and ActiveOwner(s.x)
```

therefore reserves half zero in **both orientations** of both active edges.
The usable turnover is exactly

```text
four half-one v-endpoint keys out,
four half-one m-endpoint keys in.                         (T)
```

There is no diagonal `(m,m)` key because `FreeHalf.distinct` excludes it.

## 2. Why coherence supplies no surplus

`BaseKeyComponentCoherent` says that two assigned keys with the same ordered
base must serve obligations in the same component.  After the half-zero
reservation, every base in (T) has only one usable physical key.  Injectivity
of the matching prevents that key from being assigned twice.  Consequently
base-key coherence is vacuous on every gained and lost turnover base.

It also has no cross-state content: the definition is applied separately to
the source matching and the target matching.  It neither identifies an
obligation across states nor transports a source assignment around the SCC.

## 3. Optimal-matching countermodel

The exact checker constructs two states.  Each state has five obligations in
one component and four usable half-one keys, namely the four orientations at
its active middle.  Every obligation is eligible for every usable key.

There are exactly `5P4 = 120` coherent optimal matchings per state.  Every one
has size four and defect one.  A transition loses all four old usable keys and
gains all four target keys.  Every gained key is consumed by every optimal
target matching.  The inverse transition swaps them back.  Therefore:

```text
constant positive defect + exact turnover + optimality + coherence
does not produce an augmenting path or a strict trade.
```

Replay:

```powershell
python tmp/fanout/r42_source_swap_proof/check_countermodel.py
```

All checks use finite sets and exhaustive enumeration of the 120 matchings in
each state.

## 4. Status of the real graph theorem

The available exact real inputs do not decide the theorem.  The four fixtures
and all 992,618 available canonical states through order 12 have defect zero,
so their positive-defect SCC domain is empty.  The genuine eight-vertex rotor
has defect zero because its active edge component contains no bad-edge endpoint
pair.  No positive-defect active graft has been certified.

Thus an exact real cage has not been built, and the theorem remains open.  A
proof needs graph-derived information absent from turnover and coherence, such
as a source surviving the swap, a target obligation-to-source eligibility
transport that creates Hall surplus, or a strict decrease outside the SCC.
Per-state optimality alone cannot provide any of these.
