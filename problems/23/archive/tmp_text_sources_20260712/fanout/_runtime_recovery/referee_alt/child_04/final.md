FALSIFY result:

- Without the explicit global-descent premise, the wrapper-level hypotheses admit an exact Hall-failing global minimizer:
  - choices: `w0,w1`
  - scores: `(1,1)`
  - canonical choice: `w0`
  - Hall incidence at `w0`: `[0]`, giving exact witness `1 > 0`
  - incidence at `w1`: `[1]`

- With `HallFailureHasScopedScoreGlobalDescent`, the system is infeasible. Exact Farkas certificate:
  - `s0 - s1 ≤ 0`
  - `-s0 + s1 ≤ -1`
  - multipliers `(1,1)` yield `0 ≤ -1`.

Thus the compiled wrapper is logically sound but tautological at the abstract level. The unresolved proof gap is precisely `RealHallFailureHasScopedScoreGlobalDescent`; the R29 2,943-vertex local minimum does not resolve global minimality.

Artifacts:

- [REPORT.md](E:/Projects/ErdosProblems/tmp/fanout/referee_alt/child_04/REPORT.md)
- [finite_wrapper_farkas.py](E:/Projects/ErdosProblems/tmp/fanout/referee_alt/child_04/finite_wrapper_farkas.py)

Command:

```powershell
python tmp/fanout/referee_alt/child_04/finite_wrapper_farkas.py
```

SHA256:

```text
575E5BFBD98E44AD1B4D245007A331F3BEAF3845F2D41A9AEC449EF4C21A4604  finite_wrapper_farkas.py
9E392C0953F0A35B1FC7EB788D3B518D824FF4BC030BB0E081594EDA6930DC9B  REPORT.md
```

Certificate payload SHA256: `f170807b1d3fd4d080ae9125ae3dbe25ae62508edcbb9f5c6faea642a630a702`.