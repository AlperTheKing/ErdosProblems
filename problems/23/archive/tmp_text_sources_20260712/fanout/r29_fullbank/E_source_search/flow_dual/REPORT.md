# Exact capacitated-flow audit: all-anchor R29 hub shore

## Verdict

The flow over the **currently proved, concretely instantiated FullBank universe** is infeasible.  The exact residual after the certified FreeHalf allocation is 28 Hall units, all at owner 2.  The current APIs instantiate no concrete R29 FullBank token or legal incidence arc, so max flow and min-cut capacity are both 0.

This is not a proof that semantic Door, vertexSlack, or c5Base arcs are absent.  Those three kinds are explicitly recorded as `unknown_not_absent`.  It is an exact certificate that the present API/data boundary does not yet supply an absorber.

## Exact certificate

- Owner demands: `(6651,6651,6651)`.
- Certified FreeHalf allocation: `(6651,6651,6623)`.
- Residual demand: `(0,0,28)`.
- Proved FullBank tokens/arcs: `0/0`.
- Hall set: `{owner:2:residual}`.
- Neighbor capacity: `0`.
- Defect: `28`.
- Farkas multiplier: 1 on the residual owner-2 constraint, 0 elsewhere.

The min cut has source side `{source, owner:2:residual}`, sink side `{sink}`, and capacity 0.  Thus `0 < 28` is the exact Hall obstruction.

## Semantic boundary

| Kind | Audited status | Missing current provider |
|---|---|---|
| Door | unknown, not absent | concrete R29 port/extractor-edge adapter, capQ, own-edge incidence |
| vertexSlack | unknown, not absent | concrete capQ and legal port-to-vertex incidence |
| c5Base | unknown, not absent | checked-terminal enumeration and terminal-to-token/incidence adapter |
| prune | proved absent in this scoped tuple | a strict descendant/ledger split; all-anchor is already the certified scoped minimum |

FreeHalf triples are not FullBank tokens and are not duplicated as c5Base capacity.

## Replay

```powershell
python check_certificate.py
```

The checker uses `fractions.Fraction`, verifies the owner-Hall artifact SHA-256, recomputes the residual from its allocation, validates token uniqueness and arc references, and replays the exact Hall/min-cut/Farkas inequality.
