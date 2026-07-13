# vertexSlack verdict

Literal replay: `python replay.py` (Python 3, integer/Fraction only).

The all-anchor tuple gives `|C|=2127`, `|F|=2797`, `|S|=1383`, and
`|O|=4242`, split into 1370 internal, 2760 boundary, and 112 edges disjoint
from `C`. `result.json` contains every exact set and every vertex row.

For every `v in C`, the replay computes `T(v)=5*r(v)`, candidate capacity
`max(0,2943-T(v))`, and literal endpoint load `deg_O(v)/2`. There are four
negative margins:

| v | T(v) | cap | deg_O/2 | margin |
|---:|---:|---:|---:|---:|
| 0 | 3380 | 0 | 1/2 | -1/2 |
| 1 | 3380 | 0 | 1/2 | -1/2 |
| 2 | 3380 | 0 | 1/2 | -1/2 |
| 55 | 3385 | 0 | 2 | -2 |

Thus the literal half-singleton vertexSlack constructor is numerically
infeasible. It does not absorb the claimed 28 residual, even conditionally on
legal incidence. Moreover, the 28 is a FreeHalf Hall-source deficit and is
not interchangeable with these FullBank rational load units.

Global source audit: 5500 distinct `(edge,core endpoint)` keys, exactly equal
to total `O`-incidence; no duplicate key; `F` and `O` are disjoint. Hence the
literal endpoint allocation has source uniqueness and no double-spend. This
does not repair the four negative capacities.

Licensing caveat: `certificate_of_singletonCore_vertexSlack` requires
`hinc : forall e in O, forall x in C, x in e -> inc e x`; it does not derive
that predicate from graph incidence. The internal-endpoint wrapper licenses
only internal off-support edges under its own abstract endpoint hypothesis;
boundary edges are routed to Doors. Therefore `max(0,N-T(v))` is only a
candidate numeric capacity here, not a graph-derived compiled license.

Smallest statement: **For the canonical N=2943 all-anchor selected rows, the
literal half-singleton vertexSlack inequalities fail exactly at vertices
0,1,2,55, with total negative margin 7/2 and minimum margin -2; consequently
vertexSlack alone supplies no FullBank certificate and does not eliminate the
purported 28 FreeHalf Hall residual.**

Exact identities are in `hashes.json`; full sets and margins are in
`result.json`.
