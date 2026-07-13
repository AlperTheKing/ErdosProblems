# R36 audit: active-owner free-pair-or-detour

## Verdict

The R37 production conclusion is false. Its geometric free-pair conclusion is
valid, but it does not imply the production `CommonBlueOwner` predicate.

`CommonBlueExtendedMatching.CommonBlueOwner` unfolds through
`CheckedC5BaseTransfer.TerminalData.Valid` to

```text
blue(x,v) and blue(y,v) and dM({x,y}) + 2 <= dB({x,y}).
```

Thus it requires `2 <= sigma({x,y})`. Maximum-cut minimality supplies only
`0 <= sigma({x,y})`. The two extra units pay for reserving the terminal edges
`x-v` and `y-v`; the fact that the source half `(x,y,h)` is not
`ScopedReserved` does not pay those units.

## Exact real-graph counterexample

There are 20 vertices and four edge-disjoint displayed 5-cycles, with rows

```text
f0: (0,2,3,4,1), bad edge 0-1
f1: (5,7,8,9,6), bad edge 5-6
f2: (10,12,13,14,11), bad edge 10-11
f3: (15,17,18,19,16), bad edge 15-16.
```

Add the blue path `(0,7,10,15,1)`. The complete row family of `f0` consists
of the displayed row and this added path; the other three families are
singletons. Select the four displayed rows.

The cut shores are

```text
true  = {0,1,3,5,6,8,10,11,13,17,19}
false = {2,4,7,9,12,14,15,16,18}.
```

The graph is triangle-free. The displayed cut has 20 blue edges out of 24.
Each of the four edge-disjoint 5-cycles forces one uncut edge, so no cut has
more than 20 blue edges; the verifier also exhausts all `2^20` cuts.

The selected support contains all displayed-row path edges. Its active graph
is exactly the added path `(0,7,10,15,1)`, whose component contains both
endpoints of `f0`; hence `v=7` is an `ActiveOwner`. Vertex `x=0` is an active
off-support blue neighbour of `v`, and `y=5` is a selected-support blue
neighbour. They lie on the same shore and

```text
pairCount(0,5) = 0
dB({0,5}) = 3
dM({0,5}) = 2
sigma({0,5}) = 1.
```

Both `FreeHalf(0,5,h)` values exist and neither is `ScopedReserved`, because
`0-5` is not blue. Nevertheless `CommonBlueOwner 7` is false because
`2 + dM = 4 > 3 = dB`.

Replay:

```powershell
python tmp/fanout/r36_freepair_proof/verify_counterexample.py
```

## Exact theorem that is valid

The production-API local theorem must expose the attachment roles and return
only the weaker free branch unless it assumes the missing two-unit surplus.

```lean
inductive ActiveAttachmentProbeResult
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (omega : RowChoice bads) (v x y : Fin G.n) : Type
  | free
      (s0 s1 : FreeHalf G omega)
      (hkey0 : sourceKey s0 = (x,y,0))
      (hkey1 : sourceKey s1 = (x,y,1))
      (hunreserved0 : not ScopedReserved G c omega s0)
      (hunreserved1 : not ScopedReserved G c omega s1)
      (hsigma : 0 <= sigma G c [x.1,y.1])
  | detour
      (i : Fin bads.length)
      (old replacement : Fin (bads.get i).rows.length)
      (hold : old = omega i)
      (hcover : x.1 ∈ (bads.get i).rows.get old |>.verts /\
                y.1 ∈ (bads.get i).rows.get old |>.verts)
      (hsep : rowSeparation ((bads.get i).rows.get old) x y = 2)
      (hreplaced : replaceMiddle ((bads.get i).rows.get old) x y v =
                   (bads.get i).rows.get replacement |>.verts)
      (hdistinct : replacement != old)
```

Assumptions:

```lean
checkGraph G = true
TriangleFree G
IsMaxCut G c
CompleteShortestRowDB G c bads
ActiveOwner G c omega v
(activeGraph G c omega).Adj v x
normEdge v.1 y.1 ∈ selectedSupport omega
blueb G c v.1 y.1 = true
```

The `ActiveOwner` hypothesis records scope but is not used by the local case
split after the active edge is supplied. The active edge is load-bearing: it
puts `v-x` outside selected support and, with triangle-freeness, proves that
`v` is outside every selected row covering `x,y`. The support-edge hypothesis
gives `x != y` and the same-shore relation. `pairCount=0` constructs the two
free halves. Otherwise the least filtered selected-row occurrence covers the
pair. Checked length five, parity, and nodup leave separations 2 or 4.
Separation 4 makes `x,y` the bad endpoints, while `x-v-y` is a triangle,
contradicting `TriangleFree`. At separation 2, replacing the middle by `v`
passes `checkRow5`; `CompleteShortestRowDB.covers_row` supplies the database
member and `rowVerts_nodup` makes it distinct.

To conclude the production common-blue branch, add exactly

```lean
2 <= sigma G c [x.1,y.1]
```

or equivalently `dM G c [x.1,y.1] + 2 <= dB G c [x.1,y.1]`. This condition
does not follow from the stated R37 hypotheses.

## Consequence for the sink-neutral SCC lemma

R37's proposed `attachmentStep_total` cannot use the free branch to create or
follow an edge in the production six-relation matching: the two unreserved
`FreeHalf`s need not realize a common-blue relation edge. Therefore the
claimed elimination of `deadEnd` and the reduction to
`realSinkNeutralAttachmentClass_hasAugment` are not established.

There is also no production `CheckedSinkNeutralAttachmentClass` or neutral
attachment graph in the current Lean tree. The live graph adapter remains
`NoCommonBlueSourceRelations`, while `CommonBlueExtendedMatching` is a
separate demand/matching API and has not been bridged into
`CollisionDefectGraphAdapter.defectData`.

The valid next wall must retain a fourth local outcome:

```text
free pair with 0 <= sigma < 2 (no production terminal)
```

or prove a new global statement showing that every such outcome in a
positive-defect sink class is matched by another source/detour mechanism.
Without that additional argument, focusing directly on sink-class saturation
would assume the missing local transition.
