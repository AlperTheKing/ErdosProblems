# R35 endpoint-diversity lane: exact obstruction

## Verdict

The proposed anchored endpoint-diversity source-floor theorem is **false**.
Endpoint anchoring and distinct bad-edge endpoint pairs do not force enough
P1/P3/strict-P4/P5 sources to eliminate a positive coherent collision defect.

There are two levels of obstruction.

1. The R35 abstract `3 x 3` double-star already has an anchored sterile
   matching rotation with 72 honest collision halves and only 62 P1/P3 source
   halves.  Its shortfall is 10.
2. More strongly, the checker in this directory constructs a **real
   24-vertex triangle-free Gamma-minimal maximum-cut cage** satisfying the
   graph-side endpoint/path hypotheses.  At a concrete selected tuple its
   central owner has 72 honest collision halves and only 48 sources under the
   no-common-blue P1/P3/strict-P4/P5 union.  Thus its central Hall shore has
   shortfall 24.

The real cage is not claimed to be a counterexample to the final canonical
existence theorem: it has alternative shortest rows, and one explicit one-row
change lowers the central demand from 72 to 62.  What it refutes is the static
claim that endpoint diversity, even together with triangle-freeness, maximum
cut, Gamma-minimality, connected blue graph, complete shortest rows, and an
active owner, supplies the required source floor at an arbitrary state.

## Exact endpoint calculation

Consider the anchored `a x b` double-star rows

```text
(l_i, c_L, h, c_R, r_j),       1 <= i <= a, 1 <= j <= b.
```

At the middle owner `h`, the selected pair multiplicities are

```text
n(h,h) = n(h,c_L) = n(h,c_R) = ab,
n(h,l_i) = b,
n(h,r_j) = a.
```

Therefore the exact number of `CollisionHalf` obligations owned by `h` is

```text
D_h
 = 2 [3(ab-1) + a(b-1) + b(a-1)]
 = 2(5ab-a-b-3).
```

The endpoint-diversity P3 pool contains only ordered same-shore endpoint
pairs.  Every cross pair `(l_i,r_j)` is occupied by its own selected row, so it
is not a `FreeHalf` base.  Consequently

```text
S_P3 = 2[a(a-1) + b(b-1)],
D_h - S_P3 = 2(5ab-a^2-b^2-3).
```

On the diagonal `a=b=t`, the residual is `6(t^2-1)`, so it grows
quadratically.  Distinct anchored endpoints do not close the source count;
the rows themselves consume the cross-endpoint quadratic pool.

For `a=b=3`, `D_h=72`, `S_P3=24`, and the residual before P1/P4/P5 is 48.
The R35 abstract model has 38 unreserved P1 halves and hence shortfall 10.

## Real 24-vertex cage

The exact checker constructs the following graph.

- Core vertices: `L={0,1,2}`, `R={3,4,5}`, `c_L=6`, `h=7`, `c_R=8`.
- Main bad edges: all nine `L x R` pairs.
- Main selected rows: `(l,c_L,h,c_R,r)`.
- Anchor-web layers:
  `A_L={9,10,11}`, `Z_L={12,13,14}`, `M={15,16,17}`,
  `Z_R={18,19,20}`, `A_R={21,22,23}`, with complete blue links between
  consecutive layers and from `L`/to `R`.
- Three additional bad edges `(A_L[i],A_R[i])`, with selected private rows
  `(A_L[i],Z_L[i],M[i],Z_R[i],A_R[i])`.  These rows make the selected-row
  union equal to all 24 vertices.
- Extra blue cut edges `h-A_L`, `h-M`, and
  `c_R-Z_L[0], c_R-Z_L[1]` make `h` active and keep the displayed cut
  maximum.

The checker establishes, with integer arithmetic only:

```text
vertices=24 edges=82 triangles=0
intended_cut=70 exact_maxcut=70 maxcuts_vertex0_fixed=17
bad_edges=12 gamma=300 row_family_hist={10: 9, 45: 3}
selected_rows=12 distinct_anchored=12 selected_union=24
active_vertices=23 quiescent=[6] owner_active=True
owner_obligations=72 P1=24 P3=24 strictP4=0 P5=0 reachable=48 defect=24
explicit_one_row_alternative_owner_obligations=62
VERDICT=ENDPOINT_DIVERSITY_SOURCE_FLOOR_FALSE_AT_REAL_GAMMA_MIN_CAGE
script_sha256=905831548C44208C87ED088F451DC2F4DF1C23E32F6A0AD84D6A41F9011B17E9
```

The exact maximum-cut enumeration visits all `2^23` cuts with vertex 0 fixed
by a Gray-code update.  No floating point or `native_decide` is used.

The displayed cut is Gamma-minimal: every maximum cut has 12 bad edges;
triangle-freeness gives length at least 5 for each bad edge in a connected
blue cut, while this connected cut has blue distance exactly 4 for every bad
edge and hence `Gamma=12*25=300`.

Complete shortest-row data exists literally: the nine main bad edges each
have 10 shortest rows and the three private bad edges each have 45.  The 12
selected rows are members of those families, endpoint-anchored, simple, and
pairwise distinct.

## Honest copies, halves, and coherence

For owner `h=7`, the checker explicitly enumerates obligations as

```text
(other, copy, half),
copy in Fin(pairCount(h,other)-1),
half in Fin 2.
```

The three multiplicity-nine coordinates `h,c_L,c_R` contribute 16 halves
each.  The six multiplicity-three leaf coordinates contribute 4 halves each.
This is exactly `3*16 + 6*4 = 72`; no occurrence or half is collapsed.

The P1 pool consists of the two halves of the 15 bases `(h,x)` outside the
main row core, minus six half-zero reservations on active edges `h-A_L` and
`h-M`, giving 24.  P3 consists of the 12 ordered distinct same-shore leaf
bases, with two halves each, giving 24.  The two pools are disjoint.

Strict P4 is empty because its source coordinates must lie outside the
selected-row union, while here that union is all of `V`.  P5 is empty because
only `c_L=6` is quiescent, while a `FreeHalf` needs two distinct endpoints.

All 72 obligations have the same real active-component label.  Hence the
base-component coherence condition imposes no additional loss within this
shore.  Every central obligation sees the same 48 P1/P3 keys, so the maximum
coherent matched cardinality on the shore is 48 and every global coherent
partial matching leaves at least 24 of these obligations unmatched.

## Precise missing lemma

The R34 suggestion cannot be repaired by a larger endpoint count.  The
load-bearing statement must use **canonical row selection / an explicit row
trade**, not anchoring alone.  A minimal viable replacement is:

```text
CANONICAL COVERAGE-OR-TRADE.
Let omega be lex-minimal for (collisionDefect,rowCode).  If an active owner h
supports an anchored double-star closed trace and its P1/P3/strict-P4/P5 Hall
shore is deficient, then there exists either

  (i) an explicit coherent augmentation, or
  (ii) an explicit CheckedCollisionDefectTrade / CheckedCollisionLexTrade.
```

Equivalently, in the completely covered case exposed here (`U=V`, at most one
quiescent vertex), positive residual

```text
2(5ab-a^2-b^2-3) - |unreserved P1 halves|
```

must force a checked simultaneous row change.  It cannot be paid by a static
endpoint-diversity source floor.

The example identifies why the selector/trade clause is essential: the row
`(0,6,7,8,3)` has the genuine alternative shortest row `(0,9,12,8,3)`, and
that one change lowers the central obligation count from 72 to 62.  Proving
that a canonical deficient trace always exposes such a coherent trade (or a
missing real source family) is the remaining geometric content.

This result does **not** test or refute the frozen relation with common-blue;
it is a falsifier to the assigned no-common-blue endpoint-floor route.

## Reproduction

From the workspace root:

```powershell
python tmp/fanout/r35_endpoint_diversity/check_real_endpoint_floor_obstruction.py
```

