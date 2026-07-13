Read the required onboarding, newest R29 handoff, and R29 wall. I ran a read-only exact search, but could not write lane artifacts because the Windows sandbox wrapper rejected `apply_patch` before filesystem access.

Exact results:

- Tested 11 nonuniform `C5` blow-up orders, \(N=5\ldots9\).
- Menu sizes: 1, 2, 3, 4, 6, 8, 9, and 12.
- All global optima passed scoped Hall.
- The broader companion-relaxation was UNSAT at every global optimum, which soundly excludes true Hall failure.
- Only nonzero optimum:
  - Input order `(2,2,2,2,1)`, rotated `(1,2,2,2,2)`
  - \(N=9\), 2 bad edges
  - 8 rows per bad edge, 16 choice variables
  - Exact global score: 12
  - Exact replay: demand 12, matched 12, 2 active edges, 4 reserved hits
- The other ten instances had exact optimum 0.

Tested input orders and menu sizes:

```text
(1,1,1,1,1): 1
(2,1,1,1,1): 2
(2,2,1,1,1): 4
(3,1,1,1,1): 3
(2,2,2,1,1): 8
(3,2,1,1,1): 6
(4,1,1,1,1): 4
(2,2,2,2,1): 8 × 2 bad edges
(3,3,1,1,1): 9
(4,2,1,1,1): 8
(3,2,2,1,1): 12
```

No concrete global-minimum Hall falsifier was found. This is not broad-family closure: cage/cable/selector hybrids and larger orders remain untested because a lane-local driver/report could not be created. The repository also still lacks an executable 2943 constructor.

Relevant SHA-256 hashes:

```text
CODEX_ONBOARDING.md
e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0

CLAUDE_TO_CODEX.md
b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126

WALL_ATTACK_R29_GPTPRO56.md
fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04

_codex_r20_c5_nonuniform_global_cpsat.py
25707f776cfca057ef17aab5f54303f1c9d5a1ee796583fdddb03bfffc63cf68

_codex_r19_global_base_census.py
b49e9a2add265052605ac412449b9fb12b1b879cc67e254b68189db7b831a737

_codex_r20_two_row_exchange_gate.py
73697b12b1e22a30e320fb970415e79fa90d88d1a6db27f42022cf9ffd9c6d83
```

No files were modified.