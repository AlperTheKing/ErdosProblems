# Reproducibility audit: Erdős #23 obstruction-paper candidates

Generated: `2026-07-12T11:31:10.366163Z`  
Workspace: `E:\Projects\ErdosProblems`  
Python: `3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)]`  
Platform: `Windows-11-10.0.26200-SP0`  
Detected logical CPUs: `128`

## Verdict

**PASS**: all nine declared replays returned their expected exit codes.

The C5[3] two-row exchange gate intentionally returns exit code `1`: its exact
negative verdict is `NO_TWO_ROW_EXCHANGE`. The R57 nine-copy object is an
interface countermodel, not a graph counterexample: it violates
`CompleteShortestRowDB.badKeys_nodup`, absent from the proposed bridge.

## Summary

| Replay | Exit | Status | Seconds | Input SHA-256 |
|---|---:|---|---:|---|
| `localobs_m6_m10` | 0 | PASS | 0.390 | `F5FC925962D21B1EACB557BF732718257A7C44EC897FC3B3B924A4F72E90112C` |
| `census_n5_n10` | 0 | PASS | 5.765 | `A0CC90035F562D2C5E562EAC06E5AC197C13415F488BD027F79F3A1F873066DB` |
| `counterexample_24vtx` | 0 | PASS | 2.889 | `038B2C575CC3620A38D9EAFAFF86677DFF93058CB9C11CC07CF9528A4D65AF96` |
| `rotor_8vtx` | 0 | PASS | 0.031 | `6D74BCBD1BAB12948C5E1A498F62A7185B03743A2B701EC5AEBA6F54B01B2AEB` |
| `r57_interface_counterexample_16vtx` | 0 | PASS | 0.535 | `699624663CEA009669BFDCC25B6D329953CFC69617B32F4DD016BF1591EDB617` |
| `r57_positive_defect_interface_countermodel` | 0 | PASS | 1.178 | `C8D0E07B3187DFDF401E1828343DAD1D9FC0165C571FD830E65337EC1612E768` |
| `c5_3_two_row_exchange` | 1 | PASS | 3.481 | `B0326057FBB5C07EB1FDAB7A4515CDBB312CE795190D0A13FFABDDF4E6CC415C` |
| `c5_3_global_collision_minimum` | 0 | PASS | 30.375 | `262CE5CC5FB4293BCD6575B156B01E7C18840AA68C4A5211B0F8F47F06311982` |
| `hoffman_singleton_exact` | 0 | PASS | 5.971 | `1BE533264252422A1AE9005165B3F5B2501B6624C10318FC6850E6E514552723` |

## Main exact outcomes

- Local footprints: none for `m=6,7,8`; one footprint/one atom set for `m=9`;
  three footprints/56 atom sets for `m=10`.
- Census `n=5..10`: 11,563 connected triangle-free graphs and 23,449 maximum
  cuts; zero Hall violations and zero endpoint-position anomalies.
- The 24-vertex graph has a unique maximum cut and a genuine `9>8` support-Hall
  obstruction. The 8-vertex rotor is genuine but has scoped defect zero.
- The 16-vertex R57 graph has no negative four-corner pair among 65,536 pairs.
- The nine-copy R57 interface model has lex face `(179,50)` with 420 states,
  residual unit core `293=292+1`, and P1 demand/capacity `318>142`.
- On balanced `C5[3]`, no Hamming-distance-at-most-two defect descent exists
  from the center, although a distant global collision minimizer has defect zero.
- Exact Hoffman-Singleton identities and `2^22` image-cut enumeration certify
  `beta=50` and maximum cut 125.

## Exactness boundary

All combinatorial evaluations use integers (and integral Dinic flow). Graph
censuses use exhaustive `nauty geng`; the 24-vertex gate exhausts `2^23`
normalized cuts. The C5[3] global minimum is an integer CP-SAT replay followed
by exact flow evaluation, not a standalone SAT proof certificate.

## Commands and outputs

### localobs_m6_m10

Claim: Independent exact footprint enumeration for m=6,...,10.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\problems\23\writeup\_claude_v3_localobs_recheck.py 10
```

Exit code: `0` (expected: 0); runtime: `0.389953 s`.

Input SHA-256: `F5FC925962D21B1EACB557BF732718257A7C44EC897FC3B3B924A4F72E90112C`  
stdout SHA-256: `EAED3743354C6D9884A2E936ADF723BCADBC733448FA908175D37A4FF879C4E9`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
m=6: candidate graphs (>= m dist-4 pairs) = 0, footprints with witness = 0, atom-sets = 0
m=7: candidate graphs (>= m dist-4 pairs) = 0, footprints with witness = 0, atom-sets = 0
m=8: candidate graphs (>= m dist-4 pairs) = 0, footprints with witness = 0, atom-sets = 0
m=9: candidate graphs (>= m dist-4 pairs) = 1, footprints with witness = 1, atom-sets = 1
m=10: candidate graphs (>= m dist-4 pairs) = 9, footprints with witness = 3, atom-sets = 56
```

### census_n5_n10

Claim: Independent exact census of connected triangle-free graphs and maximum cuts for n=5,...,10.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\problems\23\writeup\_claude_v3_census_recheck.py 5 10
```

Exit code: `0` (expected: 0); runtime: `5.765032 s`.

Input SHA-256: `A0CC90035F562D2C5E562EAC06E5AC197C13415F488BD027F79F3A1F873066DB`  
stdout SHA-256: `9F397E04E61A0522A301C620E151C54487F80A8EAB68291A6A4E0F0E5CC25B3B`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
n=5 done graphs_cum=6 maxcuts_cum=10
n=6 done graphs_cum=25 maxcuts_cum=35
n=7 done graphs_cum=84 maxcuts_cum=132
n=8 done graphs_cum=351 maxcuts_cum=594
n=9 done graphs_cum=1731 maxcuts_cum=3243
n=10 done graphs_cum=11563 maxcuts_cum=23449
=== SUMMARY ===
graphs: 11563 maxcuts: 23449
hall violations: 0  at gamma-min: 0
position anomalies: 0
```

### counterexample_24vtx

Claim: Exact 24-vertex counterexample to bare shortest-support expansion.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\problems\23\writeup\_claude_verify_24vtx_ce.py
```

Exit code: `0` (expected: 0); runtime: `2.888867 s`.

Input SHA-256: `038B2C575CC3620A38D9EAFAFF86677DFF93058CB9C11CC07CF9528A4D65AF96`  
stdout SHA-256: `A17DC9F05A3089CAC9E2D84906915EC32434A3A9874E0C29A7CE0E922BC04ED7`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
VERDICT: CONFIRMED -- bare SSE is FALSE at a genuine UNIQUE (Gamma-min) max cut of a real 24-vtx triangle-free graph; banked form is the ONLY viable target
```

### rotor_8vtx

Claim: Exact 8-vertex neutral rotor verification.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\problems\23\writeup\_claude_r39_8vtx_rotor_gate.py
```

Exit code: `0` (expected: 0); runtime: `0.031154 s`.

Input SHA-256: `6D74BCBD1BAB12948C5E1A498F62A7185B03743A2B701EC5AEBA6F54B01B2AEB`  
stdout SHA-256: `FFD0BD66668B155FDC5BC2E1CDB7BDF8F45952A52BC377DADFA2353E163C587F`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
CLAUDE-GATE=PASS (exhaustive)
VERDICT: rotor construction GENUINE; bare rotor NOT a falsifier (vacuous scope); graft question OPEN
```

### r57_interface_counterexample_16vtx

Claim: Exact 16-vertex R57 current-interface counterexample.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\tmp\fanout\r57_current_interface_counterexample\verify.py
```

Exit code: `0` (expected: 0); runtime: `0.535009 s`.

Input SHA-256: `699624663CEA009669BFDCC25B6D329953CFC69617B32F4DD016BF1591EDB617`  
stdout SHA-256: `1C1E5DCFFD503D8D329404ED67A1292804C0581F7E67C9BD504957B7E5E7CCEC`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
PASS_R57_CURRENT_INTERFACE_COUNTEREXAMPLE
```

### r57_positive_defect_interface_countermodel

Claim: Exact nine-copy positive-defect countermodel to the compiled R55/R57 interface.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\tmp\paper_replay_audit\r57_positive_defect_interface_countermodel_v2.py
```

Exit code: `0` (expected: 0); runtime: `1.178237 s`.

Input SHA-256: `C8D0E07B3187DFDF401E1828343DAD1D9FC0165C571FD830E65337EC1612E768`  
stdout SHA-256: `B3888121C979C048C2DE86953D08F532072B95DDAF64C627AD48A48ADD4E1C11`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
{"arithmetic":"Python integers; exact integral grouped max flow","collisionMinimum":179,"defectMinimumOnCollisionFace":50,"displayedChoice":[0,0,0,0,1,1,1,1,1],"displayedDemand":358,"displayedGlobalDefect":50,"displayedMaximumFlow":308,"internalActive":0,"lexMinimalStates":420,"lexStatesSaturatingBothForkHalves":420,"orderTimesOwnerCardinality":112,"ownerSet":["s","t","a1","a2","a3","b1","b2"],"p1GroupedCapacity":142,"p1GroupedDemand":318,"rowTuplesExhausted":512,"schema":"R57_POSITIVE_DEFECT_INTERFACE_COUNTERMODEL_REPLAY_V1","scope":"compiled interface only; nine copies violate CompleteShortestRowDB.badKeys_nodup","shoreCollision":159,"shoreSelectedLoad":200,"shoreZero":71,"unitCore":{"activeReachedGroupCounts":{},"bothHalvesMatched":true,"directReachedCapacity":292,"forkKeysReached":true,"globalDefect":50,"leastUnmatchedRoot":[4,3,1,0],"noSimultaneous":true,"obligationCount":293,"positiveUnitDefect":true,"rawReachedSourceKeys":292,"residualSinkUnreachable":true,"sourceCapacity":292,"successorObligations":[[2,3,2,0],[2,3,2,1]],"successorSinkClosed":true,"successorsInUnitCore":true},"verdict":"PASS_R57_POSITIVE_DEFECT_COMPILED_INTERFACE_COUNTERMODEL"}
```

### c5_3_two_row_exchange

Claim: Exhaustive Hamming-distance-at-most-two exchange obstruction on balanced C5[3].

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\tmp\fanout\cdc_wave1\exchange\c5_3_exchange_gate.py --workers 61
```

Exit code: `1` (expected: 1); runtime: `3.481264 s`.

Input SHA-256: `B0326057FBB5C07EB1FDAB7A4515CDBB312CE795190D0A13FFABDDF4E6CC415C`  
stdout SHA-256: `F61241DC420D97D3385478642A3FB5892642BD1CE3E0448CA12FD993C1EC32AA`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
{"arithmetic":"Python integers only; exact integral Dinic max flow","bestDecomposition":null,"bestDescent":null,"center":{"collisionUnits":42,"flowDefect":12,"maximumFlow":72,"state":[12,16,11,1,5,6,26,18,22]},"defectHistogram":{"8":27,"10":54,"12":550,"14":1638,"16":4644,"18":6858,"20":7290,"22":3150,"24":360},"descentCount":0,"descentDistanceHistogram":{},"distanceHistogram":{"0":1,"1":234,"2":24336},"graphCheck":{"badEdges":9,"familySize":27,"minimumBadEdges":9,"triangleFree":true},"schema":"CDC_WAVE1_C5_3_CORRECTED_EXCHANGE_V1","statesExhausted":24571,"verdict":"NO_TWO_ROW_EXCHANGE","zeroDescentCount":0}
```

### c5_3_global_collision_minimum

Claim: Exact global collision-face optimization on balanced C5[3].

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\tmp\fanout\cdc_wave1\exchange\c5_3_global_min_gate.py --workers 64
```

Exit code: `0` (expected: 0); runtime: `30.374884 s`.

Input SHA-256: `262CE5CC5FB4293BCD6575B156B01E7C18840AA68C4A5211B0F8F47F06311982`  
stdout SHA-256: `19D101EB64441E33B640685106E846EA4D50804CE28BA6E247050827A28E8338`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
{"arithmetic":"integer CP-SAT plus exact integral Dinic max flow","capacityObstructionOnEntireOptimalFace":{"activeEdges":0,"actualFlowDefect":0,"branches":9739,"choice":[2,16,21,6,14,19,4,9,26],"collisionUnits":42,"conflicts":640,"globalCollisionHalfDemand":84,"groupedCapacityUpperBound":84,"maximumFlow":84,"minimumUnselectedPlusActive":0,"predictedDefectLowerBound":0,"status":"OPTIMAL","unselectedVertices":0},"globalMinimum":{"branches":0,"choice":[2,25,12,24,14,1,13,0,26],"collisionUnits":42,"conflicts":0,"flowDefect":12,"hammingFromWitness":9,"maximumFlow":72,"status":"OPTIMAL"},"graphCheck":{"badEdges":9,"familySize":27,"minimumBadEdges":9,"triangleFree":true},"nearestGlobalMinimum":{"branches":464,"choice":[12,16,11,1,5,6,26,18,22],"collisionUnits":42,"conflicts":0,"flowDefect":12,"hammingFromWitness":0,"maximumFlow":72,"status":"OPTIMAL"},"nearestStrictCollisionDescent":{"branches":43954,"collisionUpperBound":41,"conflicts":3489,"meaning":"the witness is globally collision-minimal","status":"INFEASIBLE"},"schema":"CDC_WAVE1_C5_3_GLOBAL_COLLISION_MIN_V1","selectorVerdict":"PASS_EXPLICIT_GLOBAL_MINIMUM","witness":{"choice":[12,16,11,1,5,6,26,18,22],"collisionUnits":42,"flowDefect":12,"maximumFlow":72}}
```

### hoffman_singleton_exact

Claim: Exact Hoffman-Singleton construction, spectral lower bound, and matching explicit cut.

```text
C:\Users\a\AppData\Local\Programs\Python\Python312\python.exe -B E:\Projects\ErdosProblems\tmp\agent_reform\audit_1\b_hosi.py
```

Exit code: `0` (expected: 0); runtime: `5.971103 s`.

Input SHA-256: `1BE533264252422A1AE9005165B3F5B2501B6624C10318FC6850E6E514552723`  
stdout SHA-256: `DE6A5FA212EF01725C5BBF5DFDC79969030D618A8BA9364EA34CF7DD239182EF`  
stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

Key output:

```text
PASS  HoSi constructed: n=50 e=175 7-regular, A^2+A-6I-J=0 exactly (=> triangle-free, girth 5)
PASS  (A-2I)(A+3I) = J exactly => lambda_min = -3 => maxcut <= 50*(7+3)/4 = 125 => beta >= 175-125 = 50 (EXACT rational)
PASS  HoSi fam = 50 with exact sandwich 50 <= fam; report claim fam=50 <= 100 = n^2/25 CONFIRMED (fam = beta = 50, family achieves the spectral optimum)
```

