Completed the exact parametric double-star search.

Main result: the global-minimizer scoped Hall theorem is falsified by the replayable 89-vertex family member `(a,b,e)=(4,5,0)`. Its singleton row database makes the unique tuple a global minimizer, while the hub shore has demand `528`, reach `526`, and Hall deficit `2`.

Artifacts:

- [RESULT.md](E:/Projects/ErdosProblems/tmp/fanout/adversarial_search_double_star/RESULT.md) — SHA-256 `a35eb33ecc4002977368a866b9dfc8a2e16d75b665f4d36f971ea68b486bad68`
- [search.py](E:/Projects/ErdosProblems/tmp/fanout/adversarial_search_double_star/search.py) — SHA-256 `cb52baaad8395864c6efabac1e147c0d6f596359082a76663bba43070a393ee7`
- [search_results.json](E:/Projects/ErdosProblems/tmp/fanout/adversarial_search_double_star/search_results.json) — SHA-256 `304767bd4c2f06dfd0589eef204894c0d0de55ab2cb3cfdef776abdb9e657d37`

Tested 22,032 exact parameter cases over `2 ≤ a ≤ b ≤ 18`, `0 ≤ extra locks ≤ 8`, and alias/coupling parameters `1..4`; 9,584 had positive hub Hall gap. The full independent graph/max-flow fixture replay passed every check.