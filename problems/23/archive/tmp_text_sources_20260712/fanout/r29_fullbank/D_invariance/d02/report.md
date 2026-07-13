# R29 ActiveScoped hub-shore demand is selector-invariant

## Result

For the canonical R29 graph at `N=2943`, and for every independent choice of one of the 680 shortest rows in each of the 676 selector families, the ActiveScoped demand on the hub shore `W={0,1,2}` is

`CollisionHalf(W) + HitNeed(W) = 19950 + 3 = 19953`.

Equivalently, every hub contributes `6650+1=6651`.  Thus the claimed value `19953` is correct.  The term called “collision” by `scoped_state` is already measured in half-slots: its definition has an outer factor 2.  There is no further division by two.  The unambiguous decomposition is therefore **19950 CollisionHalf units and 3 HitNeed units**.

## Reconstructed definitions

The production-style Python state in `tmp/fanout/r29_gate/lead/r29_lead_gate.py` forms, for selected rows `R`,

* `m(x,y) = |{r in R : x in r and y in r}|` (including `x=y`);
* `rowCount(x)=m(x,x)`;
* `CollisionHalf(x)=2 sum_y max(m(x,y)-1,0)`;
* row support `S` from consecutive pairs in selected rows;
* active blue edges: both endpoints selected and edge not in `S`;
* demanded active edges: active edges in an active component (a component containing both endpoints of a selected bad atom);
* `HitNeed(x)=max(0, deg_demanded(x)-max(0,N-5 rowCount(x)))`.

These are exactly the operations in `scoped_state`; the demand used by the owner-Hall replay is `CollisionHalf+HitNeed`.

## Row-support proof

Each of the 676 fixed traffic rows has shape

`(left, 1, 0, 2, right)`, with `left` ranging over 26 vertices and `right` over 26 vertices.

Fix a hub `h in {0,1,2}`.  The pair multiplicities involving `h` are therefore:

* `m(h,h)=676`;
* for each of the other two hubs, `m(h,h')=676`;
* for each of 52 leaves, `m(h,leaf)=26`;
* all other pair multiplicities with `h` are at most one (in fact zero in the fixed rows relevant here).

Consequently

`sum_y max(m(h,y)-1,0) = 3(676-1)+52(26-1) = 2025+1300 = 3325`,

where the factor 3 consists of `y=h` and the other two hubs.  Hence

`CollisionHalf(h)=2*3325=6650`.

Every selector-family row avoids all three hubs.  Structurally, selector rows use only arm/selector vertices in `3..2761`: the 676 anchor alternatives may contain vertex 55 and the four local alternatives do not, but neither kind contains `0,1,2`.  Therefore an arbitrary change in any or all 676 selectors changes neither `rowCount(h)` nor any `m(h,y)`.  This proves collision invariance without enumerating the `680^676` choices.

For HitNeed, `rowCount(h)=676`, so

`max(0,2943-5*676)=max(0,-437)=0`.

All ordinary blue edges incident to a hub are consecutive pairs in traffic rows and hence excluded from the active-edge set.  Each hub has exactly one additional cable edge: `(0,55)`, `(1,2929)`, `(2,2930)`.  Its endpoints are selected by fixed rows, it is not row-support, and its component is activated by a fixed seed bad atom.  Thus its demanded active degree is exactly one, independently of selectors, and `HitNeed(h)=1`.

Summing over three hubs gives

`3 * [2*(3*675+52*25)+1] = 3*(6650+1) = 19950+3 = 19953`.

## Scope and proof obligations

The conclusion is for the canonical R29 row bank and ActiveScoped definition above.  Its only non-arithmetic graph hypotheses are the source-artifact identities: selector rows avoid hubs; fixed non-traffic rows avoid hubs; the three listed cable edges have fixed selected endpoints, are absent from row support, and lie in components activated by fixed seed atoms.  Selector rows can change other active components and global score, but none of those changes can alter hub incidence or the fixed activation witness.

## Reproduction

From this directory run:

`python derive.py > output.txt`

The script uses integer arithmetic only and generates no selector tuples.  It writes `result.json`; `output.txt` records the exact run.  `SHA256SUMS.txt` contains hashes for the delivered artifacts and the principal read-only source artifacts used to reconstruct the definitions.
