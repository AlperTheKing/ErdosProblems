# R40 exact strong-probe census, N <= 12

## Verdict

PASS.  The exact connected triangle-free census found no failure of:

```text
at every global matching-defect-minimal complete-row tuple,
every ActiveOwner has
  sigma >= 2 valid common-blue
  OR a genuine complete-DB two-edge detour
  OR an explicit lower matching-defect row trade.
```

The third branch is necessarily absent at a global defect minimum.  Every
eligible graph had minimum coherent collision defect zero.

```text
generated graphs              1,246,466
eligible all-ell-five graphs    992,618
complete-row tuples          40,228,399
global defect minimizers     40,228,102
ActiveOwner checks           12,284,249
strong common-blue           10,448,966
genuine two-edge detour       1,835,283
failures                              0
```

The smallest exact witness field is therefore `null`.  A failure record, if
present, contains the graph, full complete row database, selected tuple,
exact coherent Hall defect/witness, every owner probe, singleton losses, and
the checked lower-defect trade search.

Payload:

```text
census_n5_n12.json
SHA-256 32031926763f5db50ce6ce8d18c9efd9d8bd2ea88bd58b62da1469cebc38dbdc
```

## Singleton sigma audit

The payload records singleton-loss histograms separately for active-neighbor
`X` and support-neighbor `Y` occurrences.  Every value is a nonnegative
integer.  There were no all-weak owners at a defect-minimal tuple, so the
one-class-zero reduction and its cut-tight detour/trade continuation are
vacuous in this N <= 12 universe.  Here "all weak" was checked on the entire
X-by-Y probe grid, including covered cells that could expose detours.

## R41 support audit

The general exact identity passed on all 7,600,710 checked genuine detours:

```text
supportDelta = genuinelyNewSupportEdges - uniqueOldSupportEdges.
```

The stronger R41 premise does not hold for the R37 owner probes.  Here `y` is
an old selected-support neighbor of owner `v`, so `vy` is already in support.
Every checked detour had exactly one genuinely new edge and none had both new
edges active/off-support.  The exact support-delta histogram is:

```text
-1 : 3,364,027
 0 : 3,066,915
+1 : 1,169,768
```

Thus support is not monotone for these attachment detours.  The conditional
`2-u` identity remains valid only for a different detour class satisfying the
extra two-new-active-edges premise; this census contains zero such instances.
It does verify that all four old-middle ordered pairs are freed in 3,364,027
fully unsaturated transitions.

The optional Fable endpoint-pair statistic was not inferred from this output:
the run did not retain `(m,a),(a,m),(m,b),(b,m)` target eligibility, and an
exact total would require another traversal of all 40,228,399 tuples.  No
universality claim about that proposed invariant is made here.

## Replay

```powershell
python tmp/fanout/r40_strong_probe_census/verify_result.py
```

The census command used exactly eight workers and integer matching logic:

```powershell
python tmp/fanout/r40_strong_probe_census/strong_probe_census.py `
  --n-min 5 --n-max 12 --workers 8 --chunk-size 16 `
  --output tmp/fanout/r40_strong_probe_census/census_n5_n12.json
```
