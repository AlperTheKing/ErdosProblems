Exact replay completed, but artifact creation was blocked by the Windows split-root sandbox: `apply_patch` could not prepare its filesystem wrapper. No required lane files could be written.

Findings:

- Exhaustive inventory: 11,563 generated connected triangle-free graphs for orders 5–10; 6,421 all-\(\ell=5\) graphs tested.
- Exactly nine base-only survivors were recovered.
- Under literal production `ActiveOwner`, all nine selected tuples have no active owners. Therefore:
  - collision demand = 0
  - HitNeed = 0
  - MicroDemand = 0
  - one-copy flow = 0/0
  - micro flow = 0/0
  - defect = 0
  - deficient shore = empty
  - added common-blue keys = 0

| graph6 | row choice | selected rows |
|---|---:|---|
| `G?q`qg` | `[0,0]` | `[4,0,5,2,6]`; `[5,0,4,1,7]` |
| `GCQb`o` | `[0,0]` | `[0,3,6,2,5]`; `[4,1,6,2,7]` |
| `H?BD@hY` | `[1,0]` | `[5,1,8,3,7]`; `[6,0,5,1,8]` |
| `H?bB@qQ` | `[0,0]` | `[4,0,8,3,7]`; `[6,1,5,0,8]` |
| `H?b@bPI` | `[0,0]` | `[0,4,8,1,5]`; `[6,2,7,1,8]` |
| `H?b@aTw` | `[0,0]` | `[0,4,8,1,5]`; `[6,2,8,1,7]` |
| `H?`acia` | `[1,1]` | `[5,2,8,0,7]`; `[6,3,7,0,8]` |
| `H?qa`pS` | `[2,0]` | `[4,1,6,3,7]`; `[5,0,4,1,8]` |
| `HCOf@pS` | `[1,1]` | `[1,6,0,3,8]`; `[2,6,0,3,7]` |

The exact inventory gap is semantic: `_codex_r19_global_base_census.py` generated collision and endpoint demands over the entire selected-row component. Production `MicroDemand` restricts collision halves to `ActiveOwner` and defines endpoint demand through `hitNeedUnits`. None of these nine tuples contains a selected bad edge whose endpoints lie in one off-support active component, so `ActiveOwner` is empty.

Thus these are genuine obstructions to the older global base-only census relation, but not nonzero instances of production `MicroMatching`.