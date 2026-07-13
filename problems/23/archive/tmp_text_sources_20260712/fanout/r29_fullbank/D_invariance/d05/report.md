# R29 N=2943 selector-invariance verification

## Verdict

PASS. For every one of the `680^676` selector tuples, the per-owner demand
vector, the exact set of reachable source triples with owner masks, and all
eight owner-shore `(demand, reach, gap)` triples are invariant. In particular,
the full shore has demand `19953`, reach `19925`, and gap `28`.

This is stronger than invariance of the two full-shore totals: it fixes each
owner's demand, the entire source-mask set, and every subshore count.

## Independence boundary

The script reuses only the labelled graph construction returned by
`r29_lead_gate.build()`, whose file SHA256 at the run was
`5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`.
This reuse is marked in the script and result. Shortest-row enumeration,
pair/load/support state, active components, collision, hit need, source masks,
and shore counts are independently implemented in `verify.py`.

## Exhaustive local classification

The verifier constructs every shortest row independently: exactly 680 rows
in each of 676 families, hence 459,680 checked options and zero selector
tuples enumerated. Every family has the identical profile:

- 676 anchor rows: contain vertex 55, contain no D-X vertex;
- 4 local rows: contain one D-X vertex, do not contain vertex 55.

Every one of these rows has five distinct vertices, four genuine blue support
edges, no fixed-row support edge, no owner vertex, no owner-companion vertex,
and no owner-incident support edge.

The union of support edges over all selector options has size 5,408. As a
worst-case firewall check, deleting this entire union from the blue graph and
using only fixed-row selected vertices still leaves owners 0, 1, and 2 active.
An actual tuple deletes only a subset. Thus selectors cannot change owner
activity, owner degree, owner load/pairs, companion sets, or reservations.

## Exact invariant values

Each owner has load `676`, `CollisionHalf = 6650`, `HitNeed = 1`, and demand
`6651`. The reachable source owner-mask histogram is
`{1:5775, 2:5775, 4:5775, 7:2600}`, totaling `19925` distinct source triples.
The complete eight-shore table is in `result.json`.

All arithmetic is integer arithmetic; the verifier contains no floating-point
operations.

## Replay and identities

Run from this directory:

```powershell
python verify.py *> run.out
```

- `verify.py` SHA256: `e74acb1fb4c3bb788dbe92e0a44cd4a6bd5d653a7290f272b43ea230ad939c38`
- `result.json` SHA256: `247534aec043f8e0bb12573deee6e510b479ed73eabd7f0f04e48d83182b1223`
- `run.out` SHA256: `247534aec043f8e0bb12573deee6e510b479ed73eabd7f0f04e48d83182b1223`

The process exits nonzero on any failed structural, classification, firewall,
or numerical assertion.
