# Native D2C search runbook

## Toolchain and build

Compiler:

```text
g++.exe (Rev5, Built by MSYS2 project) 16.1.0
```

Build commands, from `E:\Projects\ErdosProblems`:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -Wpedantic -pthread problems_external\erdos_742\native\d2c_search.cpp -o problems_external\erdos_742\native\d2c_search.exe
g++ -O3 -std=c++20 -Wall -Wextra -Wpedantic -pthread problems_external\erdos_742\native\d2c_prune.cpp -o problems_external\erdos_742\native\d2c_prune.exe
g++ -O3 -std=c++20 -Wall -Wextra -Wpedantic problems_external\erdos_742\native\audit_c5_blowup.cpp -o problems_external\erdos_742\native\audit_c5_blowup.exe
```

## Calibration

```powershell
problems_external\erdos_742\native\d2c_prune.exe --calibrate
```

The gate accepts `K12,13`, `C5`, and the 25-vertex star; rejects `K25`,
`K12,13` plus one internal edge, and `K12,13` minus one cross edge; compares
the local witness test with a definition-level BFS implementation on all
32,768 labelled graphs of order six; and audits 200 random flip/rollback
steps at order 25.

Final output:

```json
{"calibration_complete":true}
```

## Bounded calibration searches

Fixed-size swap calibration:

```powershell
problems_external\erdos_742\native\d2c_search.exe --search --threads 1 --seconds 10 --target-edges 157 --seed 74201
```

Result: 3,823,581 proposed swaps; zero uncovered nonedges; best 27
noncritical edges; no hit.

Direct edge-minimalization calibration:

```powershell
problems_external\erdos_742\native\d2c_prune.exe --search --threads 1 --seconds 5 --seed 74202
```

Result: 678 restarts; best D2C graph has 156 edges and the engine's explicit
bipartition replay reports `is_K12_13=true`.

A 16-thread, 60-second throughput check with seed `7422026072303` completed
120,843 restarts and again reached 156 edges.  Its winning lane 10 is
deterministically replayed as a single lane by

```powershell
problems_external\erdos_742\native\d2c_prune.exe --search --threads 1 --seconds 3 --seed 3536711900714205965
```

At restart 105 this replay reports

```json
{"edges":156,"uncovered":0,"noncritical":0,"d2c":true,"is_K12_13":true}
```

Thus the recorded 156-edge optimum was the balanced complete bipartite graph,
not a second isomorphism type.

## Recommended bounded production configuration

Only after the calibration command returns success:

```powershell
problems_external\erdos_742\native\d2c_prune.exe --search --threads 64 --seconds 3600 --seed 7422026072401
```

The observed per-thread throughput predicts roughly 29 million independent
minimalization restarts in one hour.  Stop at the first raw graph with at
least 157 edges.  Replay its raw adjacency through a separately implemented
verifier before treating it as a certificate.  `NO_HIT` from this run is only
a bounded search result and is neither a proof nor a disproof.

## SHA-256

```text
F6F3E105D0221C88B52A12657A45459511E450000ADA74B431E1BEECD582A25F  d2c_search.cpp
1714E60D094F1440B4F627AF900FD28EC3A756F0D92C11E773ACDA1009F384AC  d2c_search.exe
41D2808EE1701FCF23050C0853ABAD0668E8AE59EE055F1B5F8E57F24C219865  d2c_prune.cpp
9DEAD7848B5C98E5DEDB39CA7E2A37D9CD03E1D696DF451581196C6B7B8FB2AC  d2c_prune.exe
36A9E98B743986A9E443E466B2151E3E5DFE612CBEFE79F452F68F89A76ED407  audit_c5_blowup.cpp
6CF6FEA58DCCF2712DE1C53B61A3247BC7C859A5F3B64D7CEF19FD17F11E5330  audit_c5_blowup.exe
35E006934F9FA44B5C1154A4637DD6E08C38D5B64275940A467EF3F158F56EFE  STRUCTURAL_FAMILY_AUDIT.md
```
