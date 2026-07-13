# Lead structural reduction

## Exact claim

Fix the blue graph, bad pairs, and two row tuples `omega` and `eta`.
Assume:

1. every vertex selected by `eta` is selected by `omega`;
2. every support edge selected by `omega` is selected by `eta`;
3. at every `eta`-active owner, its selected-row multiplicity under
   `eta` is at most that under `omega`;
4. at every `eta`-active owner, its raw collision-half demand under
   `eta` is at most that under `omega`.

Then the active-scoped score of `eta` is at most that of `omega`.

## Proof

Conditions 1-2 make the new active graph a subgraph of the old active graph.
Thus every new active component lies in an old active component, every new
active owner was old-active, and each new active degree is at most its old
degree.  Condition 4 bounds collision demand ownerwise.  HitNeed at owner
`v` is
`max(0, activeDegree(v) + 5 * rowMultiplicity(v) - N)`; conditions 3 and
the degree bound therefore make it non-increasing ownerwise.  Summing over
the subset of surviving active owners proves the claim.

If `omega` has positive score and `eta` has no active owner, the decrease
is strict because the new score is exactly zero.  Consequently a Hall-failing
global minimizer must evade every full-deactivating tuple and, more generally,
every safe support-expansion tuple satisfying 1-4.

## R29 use and gap

The R29 archive does not contain the claimed construction script or JSON
certificate, only its 39-line summary.  Therefore the 676-by-680 selector
menus cannot yet be reconstructed independently.  The exact remaining gate
is to decide whether a joint selector trade can enlarge support without
introducing new selected vertices/collisions or row load at surviving hubs.
The invariant is sufficient, not necessary; failure of one hypothesis is not
a counterexample to global descent.

## Exact census

The checker exhaustively evaluated:

- `N=5..8`: 100 systems, 290 tuples, 304 safe trades, 0 violations.
- `N=9`: 632 systems, 2,784 tuples, 3,084 safe trades, 0 violations.
- `N=10`: 5,686 systems below the 256-tuple cap, 42,134 tuples,
  53,903 safe trades, 57 full deactivations, 0 violations.  Three systems
  exceeded the cap.

First strict full-deactivation witness:

- graph6 ``I?`fBO]]?``;
- old rows `(0,4,7,1,6)`, `(5,2,9,3,8)`,
  `(6,2,9,3,8)`, score 19;
- new rows differ only in the last row,
  `(6,2,9,4,8)`, score 0.

This witness is not a falsifier of Hamming-one locality; it is a replayable
example of the support-expansion mechanism that a global proof may use.
