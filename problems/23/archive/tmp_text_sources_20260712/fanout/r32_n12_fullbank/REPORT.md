# No-common collision Hall gate through N=12

## Headline

Common-blue is unnecessary at every exact defect-minimal tuple in the full
N<=12 census and on the requested fixture battery.  The tested relation is
exactly P1 sameFirst + P3 rowCompanion + strict P4 outsideAttachment + P5
quiescentAttachment.  Hall demand contains collision halves only; HitNeed is
excluded and recorded separately as bank-funded demand.

This does not prove the universal row-selection statement or Erdos #23.

## Exact census

Every connected triangle-free graph was decoded from the pinned graph6 stream.
The existing connected Gamma-minimum maximum cut was selected; systems were
retained when every bad edge had length five; every coherent shortest-row tuple
was enumerated.  Arithmetic is integer-only and the maximum worker count was
20.

| Orders | eligible graphs | row tuples | positive collision | failed tuples | graphs with a failed tuple | failed defect minima | all-tuples-fail graphs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5-8 | 100 | 290 | 0 | 0 | 0 | 0 | 0 |
| 9-10 | 6,321 | 49,814 | 922 | 32 | 1 | 0 | 0 |
| 11 | 64,287 | 1,035,476 | 20,943 | 120 | 3 | 0 | 0 |
| 12 | 921,910 | 39,142,819 | 1,627,854 | 145 | 25 | 0 | 0 |
| **5-12** | **992,618** | **40,228,399** | **1,649,719** | **297** | **29** | **0** | **0** |

All 992,618 exact graph-level defect minima have defect zero.  Of the
lexicographically first minimizers, 330 have positive collision demand, so the
minimum result is not wholly vacuous.  Strict P4 is nonempty on 190,256 tuples;
P5 is nonempty on 1,462,332 tuples.  Matching-level ordered-base component
coherence required the exact constrained search on 12,675 tuples.

The stronger all-tuple statement is false.  The first failure is graph6
`I?rFf_{N?`, choice `[0,0,0,7]`: owner shore `{4,6,8}` has collision
demand/reach `32/30`, defect 2.  Choice `[0,0,0,0]` on the same graph has
defect zero.  The replay is exported in `first_tuple_falsifier_n10.json`.

## Pinned N=12 fixture

For `K??E@cyjFgWk`, choice `[0,4,5,7]`, the gate reproduces collision profile
`{7:6, 10:14, 11:8}` and matches all 28 collision halves using P1/P3/P5.
Common-blue candidates and uses are both zero.  HitNeed is separately two at
owner 10 and maps to distinct Door keys `(0,10)` and `(2,10)`, each capacity
25.  Thus the diagnostic full-bank accounting is `28 + 50 = 78`, with the
reserved half-zero keys `(10,0,0)` and `(10,2,0)` excluded.

## Fixture battery

| fixture/scope | owners | collision demand | flow | minimum slack | HitNeed separate | verdict |
|---|---:|---:|---:|---:|---:|---|
| 2943 active | 17 | 23,108 | 23,108 | 3 | 7 | pass |
| 24 active | 0 | 0 | 0 | vacuous | 0 | pass |
| 24 legacy | 9 | 312 | 312 | 318 | 0 | pass |
| 167 active | 13 | 458 | 458 | 3,442 | 0 | pass |
| 175 active | 0 | 0 | 0 | vacuous | 0 | pass |
| 311 active | 13 | 1,062 | 1,062 | 3,730 | 2 | pass |
| 3892 active | 0 | 0 | 0 | vacuous | 0 | pass |
| 89 active | 0 | 0 | 0 | vacuous | 0 | pass |
| 89 legacy | 12 | 776 | 776 | 11,702 | 0 | pass |

On 2943, deleting HitNeed changes the hub shore from demand 19,953 to 19,950.
P1/P3/strict-P4 reaches 19,925; the checked 28 P5 keys raise reach to 19,953,
leaving exact slack 3.  Every owner record has `demand == collision`, contains
no P2 field, and uses no common-blue reservation.

## Interpretation

For the live existence/selection statement, the finite evidence supports
deleting common-blue and its exclusive-reservation adapter entirely.  The
remaining finite target is: choose a row tuple whose collision halves match
coherently into P1/P3/strict-P4/P5; typed Doors then handle HitNeed separately.
The 297 failed nonminimal tuples show why the quantifier must remain
existential or defect-minimal rather than universal over row tuples.

## Replay

```powershell
python tmp/fanout/r32_n12_fullbank/fixture_gate.py
python tmp/fanout/r32_n12_fullbank/fixture_battery.py --legacy-small
python tmp/fanout/r32_n12_fullbank/collision_census.py --n-min 12 --n-max 12 --workers 20 --chunk-size 16 --output tmp/fanout/r32_n12_fullbank/census_n12.json
python tmp/fanout/r32_n12_fullbank/aggregate.py
python tmp/fanout/r32_n12_fullbank/verify.py
```

`census_n5_n12_aggregate.json` is the aggregate machine record;
`verification.json` independently checks canonical payload hashes, all null
minimizer/all-tuple-graph falsifier fields, the first tuple replay, the pinned
78/78 fixture, and every fixture owner ledger.

