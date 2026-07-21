# ENGINE A — lr_hive.exe build + validation log

Date: 2026-07-21. Builder: Fable-5 subagent (workflow ktt-lr-negativity-hunt).

## Artifact

- `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe`
- Source: `lr_hive.cpp` (single file). Validator: `gt_lr.py`.
- Build: `clang++ -O3 -march=native -std=c++17 -static -o lr_hive.exe lr_hive.cpp`
  - clang 22.1.4, target x86_64-w64-windows-gnu (MSYS2/MinGW, native Windows, NO WSL). Zero warnings.

## Method

Knutson–Tao hive model. Side n = #parts(nu) triangle, coordinates (x,y), x,y>=0, x+y<=n.
Boundary: bottom-left corner 0; left edge partial sums of lam (bottom-left -> top);
right edge |lam| + partial sums of mu (top -> bottom-right = |lam|+|mu|); bottom edge
partial sums of nu (0 -> |nu|). c(nu;lam,mu) = # integer labelings of the
(n-1)(n-2)/2 interior vertices satisfying the three rhombus-orientation inequalities
(obtuse-corner sum >= acute-corner sum):

- (A) h(x+1,y)+h(x,y+1) >= h(x,y)+h(x+1,y+1)     x,y>=0, x+y<=n-2
- (B) h(x,y)+h(x+1,y)   >= h(x,y+1)+h(x+1,y-1)   y>=1, x+y<=n-1
- (C) h(x,y)+h(x,y+1)   >= h(x+1,y)+h(x-1,y+1)   x>=1, x+y<=n-1

Counting: DFS over interior vertices in bottom-up row-major order; every inequality is
imposed as an exact +/-1-coefficient bound on its last-assigned vertex (interval
propagation). Each interior vertex (x,y) always has an earlier-only UB from rhombus (A)
at (x-1,y-1) and an earlier-only LB from rhombus (C) at (x,y-1), so DFS intervals are
finite. At the final vertex the interval length is added in one step. All-boundary
rhombi (n<=2 and edge cases) are checked explicitly. All arithmetic int64/uint64 exact;
no floating point anywhere.

Input normalization: strip zero parts; require weakly decreasing; `|lam|+|mu| != |nu|`
or #parts(lam or mu) > #parts(nu) => 0; all-empty => 1.

## CLI contract (verified)

- `lr_hive.exe "lam" "mu" "nu" [cap]` -> one line: exact count | `CAP_EXCEEDED` | `ERROR`.
- `lr_hive.exe --batch <file>`, lines `lam;mu;nu;cap` (cap optional, `#` comments ok,
  CRLF ok) -> one output line per input line.
- cap: count > cap => `CAP_EXCEEDED` (default cap 1e12). A node-visit safety cap
  (default 2e8 DFS nodes, env `LR_HIVE_NODE_CAP`) also yields `CAP_EXCEEDED`, so a
  too-fat triple aborts in seconds; CAP_EXCEEDED is always "skip", never a math verdict.

## Validation (gt_lr.py — ALL PASSED, exit 0)

Ground truth is fully independent of the hive model: Schur polynomials by exact SSYT
monomial expansion in m=8 variables (pure-Python big ints), products decomposed in the
Schur basis by repeated subtraction at the lex-greatest (dominant) monomial. No LR rule
used anywhere in the validator.

- PHASE 1 — exhaustive: EVERY triple with |nu| = |lam|+|mu| <= 8 over ALL partitions
  lam, mu, nu with <= 8 parts (301 (lam,mu) pairs, **4993 triples**, r up to 8 — strictly
  stronger than the mandated r<=4 sweep): **4993/4993 exact matches, 0 mismatches**
  (1197 nonzero, 3796 zero, max c = 2 in this range). Any wrong hive orientation or
  boundary convention would fail here.
- PHASE 2 — stretched theorems: pools harvested from |nu| = 9..12 by the same SSYT
  ground truth (|c1 pool|=1176, |c2 pool|=60), seed 20260721. 30 random c=1 triples:
  stretched counts identically 1 for n=1..5 (Knutson–Tao–Woodward). 30 random c=2
  triples: stretched counts exactly n+1 for n=1..5 (Ikenmeyer/Sherman).
  **300/300 exact matches, 0 mismatches.**
- PHASE 3 — edge cases: c=2 with cap=1 -> `CAP_EXCEEDED`; cap=2 -> `2`;
  #parts(lam) > #parts(nu) -> `0`; sum mismatch -> `0`; empty triple -> `1`;
  fat r=7 triple (8,6,4,2)^2 -> nu=(9,8,7,6,5,3,2) -> `44` (no error). **PASS.**

## Performance spot checks (hunt regime)

- c((4,3,2,2,1);(3,2,1),(3,2,1)) = 4; stretched by n=12: count 455 in 0.05 s.
- Deliberately fat r=10 stretched triple: `CAP_EXCEEDED` (node cap) in 1.8 s.

## Status: OK — all mandated validations passed.
