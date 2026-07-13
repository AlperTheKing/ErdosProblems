# Typed Door-source audit

The complete graph-realizable restriction-exit Door-key universe for the
canonical all-anchor core has **56** keys.  They are precisely the normalized
blue edges outside selected support with one endpoint in the 2,803-vertex
core.  The other 4,186 off-support edges are not restriction exits: 4,074 are
internal and 112 are external.

Each of the 56 ports has singleton-core load `1/2`, hence total port load is
`56/2 = 28`.  No port is incident with a hub-owner vertex in `{0,1,2}`.  The
certificate lists every key and its unique inside/outside endpoints.

Source-key injectivity is exact: ports are indexed by distinct normalized
graph edges and `portEdge` is the identity.  Under
`OwnEdgeDoorSourceData.Checked`, compiled theorem `doorOf_injective` then
forces distinct token indices.  With the required raw cap `>=25`, each token
has Hall cap `>=1`; assigning its sole port load `1/2` proves no double spend.

That conclusion is conditional.  The compiled repository has no concrete R29
`OwnEdgeDoorSourceData.Checked` plus `DoorWallAdapter` instantiation.
`FullBankPortSinks.lean` explicitly leaves legal edge-to-token incidence
absent.  Thus exact *available* realized Door capacity is `0`, not the
conditional `>=56`, and no 28-unit Door absorber is justified.  Although 28
typed unit-capacity keys would be the smallest capacity absorber, routing the
actual boundary layer uses all 56 half-loaded ports and does not repair the
owner-shore FreeHalf defect.

Exact Hall/dual certificate for the complete justified Door universe: take
all 56 restriction-exit ports, each of demand `1/2`, and their realized typed
token neighborhood, which is empty.  Demand is `28`, neighbor capacity is
`0`, and defect is `28`.  Equivalently use dual weights `y_p=1` for all ports;
there are no realized neighbor-token constraints to charge.

Replay:

```powershell
python audit_doors.py
```
