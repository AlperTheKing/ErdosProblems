# R53 typed edge-cap verification

## Verdict

The adaptive edge-cap counting implication is sound only when the flow domain
contains every global collision half and every sink is a proof-carrying free
half (or a certified partition of such free halves). Raw physical keys and the
active-scoped demand type are insufficient.

## Compiled positive result

`CheckedSoftCollisionTwoCover.lean` defines a rational edge-capped flow with
unit physical-key capacities and aggregate capacity two per active undirected
edge. It proves:

1. total flow is at most `2 * |ActiveEdge| + 2 * |DirectBase|`;
2. the same bound for the obligation cardinality;
3. under exact collision-cardinality and free-source-partition hypotheses,
   `collisionMass + |ActiveEdge| <= freeMass`;
4. consequently `0 <= |V|^2 - 25m` via the existing signed residual identity.

Build: Lean 4.27, exit code 0. Printed axioms for all four theorems are exactly
`propext`, `Classical.choice`, and `Quot.sound`.

Source SHA256:
`AB2452850FF7F0ED252B7BEAC03AA8BBCA54EC5DE09EADEB922821C3827D3245`.

Olean SHA256:
`4FAE98939C03B9511074B52F7A9ACE71CFEE0695931009B720331D41330617A8`.

## Compiled negative guardrail

`RawKeyCountermodel.lean` defines an exact multiplicity table on `Fin 4` with
total incidence 25, free mass 0, collision mass 9, and residual `16 - 25 = -9`.
There are nevertheless enough raw off-diagonal half keys to carry all 18
collision halves under unit key caps and one aggregate cap-two block. Thus a
raw-key adapter is unsound unless it proves that every sink key realizes an
actual free ordered-pair half.

Build: Lean 4.27, exit code 0. No `native_decide`; printed axioms are the
allowed triple only.

Source SHA256:
`3A5BC61D5437855D718449650ACC47CEA137886A86E78DBD5A999AA0F3C315C7`.

Olean SHA256:
`BE9B7DE9E76690283AAE8E7501BD51A82A3F824C2FE9DDAFE8151CE5BFB637C2`.

## Remaining provider

The only theorem-bearing frontier in this route is a graph-derived existence
theorem for a row tuple carrying a total global collision flow into an exact
partition of actual `FreeHalf` sources under the six production eligibility
relations and the grouped active-edge caps. The current
`canonicalSoftEdgeCapFeasibleTuple_exists` is only an interface proposition;
it is not proved.

The R53 adaptive object is locally weaker than fixed half-zero reservation on
an active-owner edge, but it is not globally comparable with the existing
active-scoped model because that model omits inactive collision mass and does
not reserve inactive-component edges.

## N=12 corrected global gate

`global_unreserved_n12_gate.py` exhausts all 2,400 row tuples of fixture
`K??E@cyjFgWk`. Demand is every global collision half; sinks are actual
off-diagonal free halves; no reservation is imposed. The relation uses only
P1, P3, and corrected common-blue, a subset of the six-relation union.

Exact result: 2,352 tuples pass and 48 fail this subrelation. All 27 tuples
minimizing collision units pass; their minimum collision mass is 12. The first
passing tuple is `(0,0,0,1)` with demand 92 and exact max-flow 92. The first
failure `(0,0,0,0)` has demand 110, max-flow 100, and a deficient owner shore
`{0,2,9}` of demand 78 and reach 68. Owner-shore enumeration and NetworkX
integer max-flow agree for every tuple.

Thus the corrected provider survives this stress fixture by existence even
without P4/P5. It is not true for every row tuple, so a row-choice theorem is
essential.

Script SHA256:
`30BF07BF9A88840EBF6CF130E92E7243FE886650C54F458FDA105F8109E4150F`.

Result SHA256:
`923470DFBBC82946C6AB8A5FDDDC95B5D9C0BA451F97986C8E25414AA3089B98`.
