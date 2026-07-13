# Common-blue proof/dual synthesis

## Decisive falsifier

Universal all-row `MicroHallCondition` is false. The independent replay
`defect13_replay.py` constructs the real triangle-free graph6 fixture
`K??E@cyjFgWk` with maximum connected gamma-minimum cut mask 2016, complete
nodup shortest-row families of sizes `[6,5,8,10]`, and the literal choice
`[0,4,5,7]`.

Its micro-demand is 78 and exact maximum flow is 65. The full owner shore
`{10,11}` has demand 72, reach 59, and defect 13. Thus the requested universal
Hall theorem has a real finite countermodel; the earlier one-copy N=12 pass
was a scale artifact.

## Surviving reductions

`OwnerShoreReduction.lean` proves that micro-Hall is equivalent to checking
full owner fibers. It does not claim an inclusion-minimal demand shore is
already owner-complete.

`CanonicalMicroMinimumInterface.lean` defines:

- `microObligationScore = card MicroDemand`;
- the finite argmin `minMicroChoice` and `microCanonicalChoice`;
- `MinimumMicroCommonBlueHall`, the named unproved hypothesis that every
  global score minimizer satisfies literal micro-Hall;
- conditional canonical Hall and `MicroMatching` wrappers;
- `microMatching_of_score_zero`.

The exact N=12 medium/heavy gate reports all 22,291 graphs have global minimum
score zero, hence a vacuous MicroMatching. Coverage is 18,961,358 tuples;
result SHA-256 `83697A4F13618FADA85D70473FFBFE3A73A49CDC3F3AF3D8F28971F601658A53`.
This finite gate does not prove `MinimumMicroCommonBlueHall` universally.

## Adapter boundary

`MicroAdapter.lean` proves a supplied `MicroMatching` gives the exact raw
`ResidualSourceTokenization` embedding through explicit collision-debit and
free-cell `Fin 2` equivalences. `ComponentPreserving` remains explicit.

Common-blue terminals require a reservation ledger. The posted R29 repair is
net 27 after old-pool deduction, and the conservative exclusive full-pool gate
nets two. `TerminalData.Valid` does not prove reservation idempotence or net
capacity.

Pattern 5 is reservation-free but only static. Its positive switch loss does
not preserve rows or generate c5Base capacity. `StaticPattern5Adapter.lean`
therefore requires global literal-half injection, component preservation,
typed base keys, 25 micro-sources per HitNeed, and FullBank spend laws as
explicit supplied data. Only reservation avoidance is derived from
quiescence.

All scratch Lean modules compile with the allowed axiom triple and without
`sorry`, `admit`, or `native_decide`.
