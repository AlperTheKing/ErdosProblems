Audit complete.

Result: no graph-derived prune token is available for canonical R29 `N=2943`, all-anchor shore `{0,1,2}`.

- Prune token count: `0`
- Hall capacity: `0`
- `capQ`: `0`
- Source IDs: `[]`
- Remaining defect: `19953 − 19925 = 28`
- Selector rewrites cannot count as prune: they do not create a strict vertex-set descendant or ledger split, and all-anchor already achieves the certified global minimum `23115`.

The precise missing provider is a graph-to-FullBank constructor supplying a proper descendant and complement, ledger identity/remainder, typed source ID, exact capacity and incidence, uniqueness safeguards, and the cage-balance-to-port-Hall semantic bridge.

Artifacts:

- [report.md](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d5_prune/report.md)
- [result.json](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d5_prune/result.json)
- [replay.py](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d5_prune/replay.py)

Replay and stored exact fields/hashes agree.