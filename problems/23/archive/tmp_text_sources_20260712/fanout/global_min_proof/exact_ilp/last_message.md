Completed the `exact_ilp` route.

Key outcome: exact finite MILP/SAT reduction established, but the uniform theorem remains open. The mandatory 2943 gate could not run because no constructor or data artifact exists in the workspace.

Artifacts:

- [RESULT.md](E:/Projects/ErdosProblems/tmp/fanout/global_min_proof/exact_ilp/RESULT.md)
- [FORMULATION.md](E:/Projects/ErdosProblems/tmp/fanout/global_min_proof/exact_ilp/FORMULATION.md)
- [GATES.jsonl](E:/Projects/ErdosProblems/tmp/fanout/global_min_proof/exact_ilp/GATES.jsonl)
- [SHA256SUMS.txt](E:/Projects/ErdosProblems/tmp/fanout/global_min_proof/exact_ilp/SHA256SUMS.txt)

Also identified a concrete defect: the existing C5 CP-SAT Hall encoding omits the required `sigma ≥ 0` condition for `RowCompanion`.