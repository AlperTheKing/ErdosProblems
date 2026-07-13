# C08: scale-dependent fixed-slope affine blocks

For a word of licensed affine maps `f_d(x)=d x-1`, write `F(x)=M x-C`. If the outermost multiplier is `d`, then `(M/d,C0)` maps to `(M,d C0+1)`. With `C(1)={0}`, this gives an exact dynamic enumeration of every intercept for every slope `M` whose ordered factors lie in the actual closure `G`.

The hoped-for near-cover was `|C(M)|=M-O(1)`, because `M-1` distinct maps of common slope `M` would have reciprocal-slope mass `1-1/M`; choosing growing `M` could evade every fixed-automaton obstruction.

Exact search through `M<=10000` finds no such block beyond the trivial slope 2. The largest coverage ratios `|C(M)|/(M-1)` are:

- M=3: 1/2;
- M=6: 2/5;
- M=12: 3/11;
- M=30: 6/29;
- M=60: 12/59;
- M=180: 35/179;
- M=540: 100/539;
- M=3240: 576/3239;
- M=6480: 1132/6479.

Thus the concrete near-complete same-slope mechanism has no finite seed through 10000; this is a bounded falsifier, not an asymptotic theorem. The exact recurrence includes all ordered factorizations over all `d in G`, not only `{2,3,5}`.

Artifacts:

- `compute/wave3/C08_intercepts/search_intercepts.py`
- `compute/wave3/C08_intercepts/result_1e4.json`

Reproduce:

```powershell
python problems\424\compute\wave3\C08_intercepts\search_intercepts.py --limit 10000 --top 30 --output problems\424\compute\wave3\C08_intercepts\result_1e4.json
```
