# R35 referee: canonical coverage-or-trade

## Verdict

Endpoint anchoring does **not** prove canonical coverage-or-trade at the
abstract adapter interface.  The anchored `3 x 3` singleton-family model is a
counterexample: its unique tuple is automatically canonical, its central
shore has demand 72 and only 62 sources, all 62 sources can be saturated, and
there is no nonidentity row change.  Thus it has defect 10, no coherent
augmentation, and no checked row trade.

This abstract witness is not real-graph realizable under the full attachment
hypotheses.  Exhausting the local endpoint-anchored path positions leaves no
sterile branch:

```text
pair free       -> two unreserved common-blue halves (max-cut sigma >= 0)
pair covered,
  separation 4  -> blue path x-v-y shortens endpoint distance 4 to 2
  separation 2  -> replace the row middle by v, giving a distinct shortest row
```

There are four same-shore position pairs in a five-vertex row.  The checker
tests both free/covered states for all four: 4 common-blue branches, 3 detour
branches, 1 shortcut contradiction, and 0 surviving sterile branches.

## Exact abstract witness

Rows are

```text
(l_i,cL,h,cR,r_j),  0 <= i,j < 3.
```

All nine rows and all nine endpoint pairs are distinct.  Every row family is
a singleton, so there is one tuple and its mixed-radix rank is zero.  With
`N=29` and two unavailable P1 half-zero orientations:

```text
D_h = 2(5*9-9) = 72
P1  = 2(29-9)-2 = 38
P3  = 2(3*2+3*2) = 24
reach = 62, defect = 10.
```

Taking the relation to be complete from the central obligations to these 62
keys gives an explicit coherent matching of size 62 and proves maximality by
source cardinality.  It saturates every source, hence there is no augmenting
key.  Singleton families prohibit a nonidentity row change.  This falsifies
any theorem whose graph input consists only of endpoint anchoring, distinct
endpoint pairs/rows, and the abstract source tables.

## Minimal real graph fact

The blocker is the following local disjunction.

> **Active-owner free-pair-or-detour.** Let `x,y` be same-shore blue
> neighbors of a scoped owner `v`.  If `pairCount(x,y)=0`, both common-blue
> halves are available.  Otherwise a least selected row covering `x,y` has
> position separation two and replacing its middle by `v` is a distinct
> shortest row.  Separation four contradicts the anchored endpoint distance.

Its exact inputs are max-cut switch nonnegativity, endpoint-anchored shortest
rows, the triangle-free row-intersection fact that `v` is outside the covering
row, and completeness of the shortest-row database.  Dropping any branch
input recreates the abstract sterile construction: omit max-cut eligibility to
kill common-blue, omit shortestness to allow separation four, or omit
row-intersection/completeness to suppress the detour row.

This is local only.  It blocks endpoint-anchored real/abstract embeddings of
the R35 sterile core, but it does not by itself prove the current global sink
neutral attachment SCC lemma.

## Reproduction

From the workspace root:

```powershell
python tmp/fanout/r35_referee/canonical_coverage_or_trade_referee.py `
  --output tmp/fanout/r35_referee/result.json
python tmp/fanout/r35_endpoint_diversity/check_real_endpoint_floor_obstruction.py
```
