Implemented and verified the exact FullBank max-flow gate:

- [gate.py](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py)
- [input.json](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d6_flow/input.json)
- [output.json](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d6_flow/output.json)
- [report.md](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d6_flow/report.md)

The gate uses denominator-scaled integer Dinic flow, verifies canonical artifact hashes, and enforces token uniqueness, global token capacity, component confinement, and global no-double-spend. Demand coverage is computed, never accepted as an assumed field.

Current exact all-anchor probe result: `INFEASIBLE`, with max flow `0` and demand `5`, because the canonical payloads contain no instantiated FullBank sinks. Only typed own-door capacity `25` is presently constructively instantiable from the compiled API; other provider capacities must be explicitly marked assumed.