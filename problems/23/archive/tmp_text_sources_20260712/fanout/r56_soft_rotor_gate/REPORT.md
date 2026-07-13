# R56 global-softcap saturated rotor necessary-condition gate

## Scope and verdict

This is a finite **necessary-condition superset gate**, not a universal theorem.
Sinkhood is computed only inside each finite tested saturated-transition graph;
therefore boundary truncation can create false-positive sinks but cannot justify a
general rotor-exclusion claim.

Exact verdict: `NO_CANDIDATE_IN_TESTED_FINITE_SCOPES`.

## Exact model

- `C` is one half of global CollisionHalf demand.
- `D` is the defect after explicitly unioning all six R53 families.
- Every state carries one explicit exact integral maximum-flow assignment.
- A forced-key test fixes total flow at the true optimum and gives lower bound 2
  to the exact ordered `(u,w)` pool, so both literal keys `(u,w,0/1)` are used.
- Neutral transitions change one row at one internal slot and preserve `(C,D)`.
- Saturated transitions additionally have `pairCount(u,w)=0` and pass that forced-key test.

The exact D=1 population is zero. In this executable R53 relation every
owner demand is even, every ordered-base pool contributes two literal halves,
and every active-edge group has capacity two, so all tested grouped defects
are even. Thus the requested D=1 filter is vacuous on these scopes; this gate
does not by itself exclude an R55 unit-core whose local deficiency is one.

## Exact counts

- Rotor states: 4
- R35 displayed Hamming<=2 states: 19630
- R35 one-row-minimum Hamming<=2 states: 19630
- R35 neighborhood intersection: 7650
- R35 unique union states: 31610
- Total explicit assigned flow units: 9553052
- Total neutral directed transitions: 84744
- Total saturated directed transitions: 76876
- Candidate rotor flags: 0
- Unique states with D=1: 0

### Per-fixture transition counts

| Fixture | Raw same-slot | Neutral `(C,D)` | Free | Saturated |
|---|---:|---:|---:|---:|
| rotor8 | 8 | 8 | 0 | 0 |
| r35n24 | 356850 | 84736 | 84736 | 76876 |

### Scope classification

| Fixture / scope | States | C min | C-min states | C-min has D=0 | Flags |
|---|---:|---:|---:|---:|---:|
| rotor8 / complete-four-state-rotor | 4 | 4 | 4 | true | 0 |
| r35n24 / displayed-center-hamming-le-two | 19630 | 128 | 216 | true | 0 |
| r35n24 / one-row-minimum-center-hamming-le-two | 19630 | 136 | 72 | true | 0 |
| r35n24 / union-of-both-hamming-le-two-neighborhoods | 31610 | 128 | 216 | true | 0 |

## Replay

From `E:\Projects\ErdosProblems`:

```powershell
python tmp/fanout/r56_soft_rotor_gate/gate.py --workers 32 --output tmp/fanout/r56_soft_rotor_gate/results.json
python tmp/fanout/r56_soft_rotor_gate/verify.py --workers 32 --input tmp/fanout/r56_soft_rotor_gate/results.json
```

## SHA-256

```text
gate.py       22589BC49EAA387C22653AA7735CA208924B9F6E12CABF4CFFB42AEEB2664E41
verify.py     364B198D965A9710AA44EA7142CD180D86C01C04BB29FFC8ED345365F766E0F4
results.json  48714FFF012574F63D7034BBE64099584BED4B9BB8B93E9580BFF88254D88544
global_softcap.py 32C7F9BC0C4D2921D3B1FA5D8557ADA0088EEE8A024FDB90330023060101AC13
rotor input   6D74BCBD1BAB12948C5E1A498F62A7185B03743A2B701EC5AEBA6F54B01B2AEB
R35 input     38F068167D3FB8BB7E8F05BF23A4B3C0C180589A7012B2DFD25DBD455D61EE52
```
