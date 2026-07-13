# R42/R44 graph-specific exclusion replay

Run from `E:\Projects\ErdosProblems` with Python 3.12, NetworkX 3.6.1, and
`tools/nauty2_8_9/geng.exe`.

## Primary census

```powershell
python tmp/fanout/r42_graph_specific_exclusion/enumerate_t4_support_graphs.py `
  --workers 8 `
  --output tmp/fanout/r42_graph_specific_exclusion/t4_support_graph_census.json
```

Expected:

```text
graphs=153978
graphsWithOwnerEmbedding=34
ownerEmbeddings=34
canonical_sha256=40f16a84559ace4827e366f152026f2b7868bdaed31ff9afb36184a29b48046d
```

```powershell
python tmp/fanout/r42_graph_specific_exclusion/enumerate_t4_atom_circuits.py `
  --input tmp/fanout/r42_graph_specific_exclusion/t4_support_graph_census.json `
  --workers 8 `
  --output tmp/fanout/r42_graph_specific_exclusion/t4_atom_circuit_census.json
```

Expected decisive counts:

```text
extraChoices=74920
trianglePass=2299
unionMultiplicityPass=862
circuitPass=576
canonical_sha256=302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652
```

```powershell
python tmp/fanout/r42_graph_specific_exclusion/enumerate_t4_profile_transitions.py `
  --input tmp/fanout/r42_graph_specific_exclusion/t4_atom_circuit_census.json `
  --workers 8 `
  --output tmp/fanout/r42_graph_specific_exclusion/t4_profile_transition_census.json
```

Expected:

```text
rowTuples=16288
forcedThroughBelowEight=0
circuits_with_transition=0
central_circuits=0
circuitsWithRawMiddleTransition=0
canonical_sha256=b464682b4142a9db2396dc39ac9a0ffd8ff638aba1b9270734667c8f0a543114
```

## Independent replay

```powershell
python tmp/fanout/r42_graph_specific_exclusion/verify_t4_support_census.py
python tmp/fanout/r42_graph_specific_exclusion/verify_t4_atom_census.py
python tmp/fanout/r42_graph_specific_exclusion/verify_t4_profile_exclusion.py
```

Expected verdicts:

```text
PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS
PASS_INDEPENDENT_NETWORKX_ATOM_CENSUS
PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION
```

The production-facing graph-only replay is:

```powershell
python tmp/fanout/r42_graph_specific_exclusion/verify_t4_cross_outer_exclusion.py
```

Expected:

```text
supportOwnerTypeCount=4
circuitCount=576
totalLiveCrossOuterCandidates=0
verdict=PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY
canonical_sha256=79db75b95e8401064f1b6159bb980ee0149f0fb3a602a607306a7f0e501a5d49
```

The corresponding kernel lemma builds with:

```powershell
$env:ELAN_TOOLCHAIN='leanprover/lean4:v4.27.0'
$env:LEAN_PATH='E:/Projects/ErdosProblems/tmp/codex_r35_graph_adapter_verify/deps'
cd E:/Projects/ErdosProblems/formal-conjectures
lake env lean --root=E:/Projects/ErdosProblems `
  E:/Projects/ErdosProblems/tmp/fanout/r42_graph_specific_exclusion/LiveMiddleSwapCrossOuter.lean
```

Expected axiom report: `[propext, Quot.sound]`.

## Rooted t=5 falsifier search

```powershell
python tmp/fanout/r42_graph_specific_exclusion/rooted_t5_support_cp_sat.py `
  --left 10 --right 8 --workers 8 --max-supports 3 `
  --support-time 30 --circuit-time 15 `
  --output tmp/fanout/r42_graph_specific_exclusion/t5_rooted_smoke_l10_r8.json

python tmp/fanout/r42_graph_specific_exclusion/verify_t5_rooted_hit.py `
  tmp/fanout/r42_graph_specific_exclusion/t5_rooted_smoke_l10_r8.json
```

Expected hit and independent verdict:

```text
HIT_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT
PASS_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT
source canonical SHA a8eeca69b1b674deeff88bf2e6b70cf5750e0781d626f7c2fd56e0685a7719c7
verification SHA     65bc9f52a2bff779184068136d64996c7abdfa78a03c1aa6135cf73bedff1586
```

CP-SAT uses at most eight workers.  The independent verifier uses only exact
graph operations and integer bipartite matching.  This artifact is a
support/row countermodel, not a maximum-cut production cage.

The exact ambient-extension rejection for this hit is:

```powershell
python tmp/fanout/r42_graph_specific_exclusion/extend_t5_hit_maxcut.py `
  tmp/fanout/r42_graph_specific_exclusion/t5_rooted_smoke_l10_r8.json `
  --workers 8 --iterations 500 --solve-time 20 --allow-existing-extra `
  --output tmp/fanout/r42_graph_specific_exclusion/t5_rooted_maxcut_extension_full.json

python tmp/fanout/r42_graph_specific_exclusion/verify_t5_maxcut_extension_unsat.py `
  tmp/fanout/r42_graph_specific_exclusion/t5_rooted_smoke_l10_r8.json `
  tmp/fanout/r42_graph_specific_exclusion/t5_rooted_maxcut_extension_full.json
```

Expected:

```text
all eight split statuses = INFEASIBLE
PASS_ALL_EIGHT_SPLITS_UNSAT
master canonical SHA       7896ae9480673fa850f86a35b433cd04dc5826b618f665e13a1f4b021c212795
SAT replay canonical SHA   ada85054d6a4d5b2848b5c92d9965d6e07d02d3b937daa810a6309c2ba9d969a
```

The master allows all missing cross-shore blue edges and omits connectivity,
so its UNSAT result covers every connected 25-vertex extension of this fixed
support/atom hit with exactly 25 bad edges and unchanged complete rows.

The final exact contradiction is:

```text
Live rotor requirement: some complete family contains rows differing only by middle v<->m.
Exhaustive complete-row result: zero such row pairs in all 576 circuits.
Secondary: every row choice also has r(v)>=8 and r(m)>=8.
```

The primary and independent implementations use different graph6 decoders,
shortest-path engines, and SDR matchers.  Neither acceptance path uses floating
point arithmetic.
