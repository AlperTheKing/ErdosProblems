Audit complete. Verdict:

- `sameFirst`: 17,325 available half-keys, capacity `17325/(2K)`.
- `commonBad`: 0 keys and zero capacity because hubs have no bad neighbours.
- Base-only defect: `19953 − 17325 = 2628`.
- Auxiliary `ActiveScoped` adds 2,600 `rowCompanion` keys, yielding 19,925 and defect 28.
- Raw base key sets are selector-invariant; active status, HitNeed, and `ScopedReserved` can vary with selectors.

Artifacts:

- [REPORT.md](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank_referee/root_audit/REPORT.md)
- [audit_r29_hub_base.py](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank_referee/root_audit/audit_r29_hub_base.py)

Script SHA256: `71E1D1B84458D391A3A174D6B596FD3F47940EA702B0812A003D13F90B5134AE`  
Report SHA256: `D3725682A87E1922B922044A358300504637F9DDD6AC36286AB263D536D95268`

The script ran successfully using integer/Fraction arithmetic. No forbidden Lead B, R29 gate, FullBank audit, global-minimum script, or JSON artifact was read or imported.