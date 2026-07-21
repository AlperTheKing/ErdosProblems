# Frozen irregular order-19 incidence seed: independent audit

Date: 2026-07-21 (Europe/Istanbul)

Status: **PASS AS A COARSE INCIDENCE/ORIENTATION SEED; FAIL AS AN SSNC COUNTEREXAMPLE**.

## Artifacts

- machine-readable seed: `IRREGULAR19_INCIDENCE_SEED.json`, 14,224 bytes, SHA-256 `B4BFB3000D9F14E7C763764DDF474FECD166DE12CC7F96B9D593F8801DF5EF69`;
- standard-library verifier: `audit_irregular19_incidence_seed.py`, 9,004 bytes, SHA-256 `02543C5ECA0D08FCB029EEEED672843AE63881A9B9AF47F73DF8A00A8C5AFAB4`.

The JSON freezes vertices `0,...,18`, the missing graph, all 19 target root blocks `R_u`, their transposed source fibres `W_v`, the full adjacency list, and a derived literal-reachability ledger. Lists are sorted and labels are fixed; no solver is needed to replay it.

## Independently replayed structural facts

The verifier reconstructs all data from raw JSON and checks:

- 19 missing edges with degree sequence `(4,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1)` and multiset `{4,3^8,1^10}`;
- 152 arcs, no loops, no digons, no arc on a missing edge, and exactly one orientation on each present unordered pair;
- outdegree 8 at every vertex;
- target root-block sizes `(7,5,5,5,5,5,5,5,5,1,1,1,1,1,1,1,1,1,1)`;
- no missing pair inside any root block;
- every target block is a regular tournament: internal outdegree 3 for the size-7 block, 2 for each size-5 block, and 0 for singleton blocks;
- 57 total root incidences and exactly three declared targets in each source fibre;
- exact agreement between the stored source fibres and the transpose of the 19 target blocks.

The audit returned exit 0 and summary status `PASS_COARSE_SEED_ONLY`. Four adversarial mutations were also rejected with exit 1: a changed missing edge, a loop, a source/target-fibre disagreement, and a falsified semantic ledger.

## Literal two-step ledger

The verifier does not trust the names `W_v` or `unreachable`. For each source it recomputes

\[
N^{++}(v)=\{x\ne v:x\notin N^+(v),\ \exists y\ (v\to y\to x)\}
\]

and the literal complement outside `{v} union N+(v) union N++(v)`.

For every one of the 19 vertices the result is the same:

```text
d+(v) = 8
|N++(v)| = 10
literal W_v = []
declared W_v has size 3
declared W_v != literal W_v
10 < 8 is false
```

The declared fibres are:

```text
v=00 [2,5,16]       v=01 [6,8,9]        v=02 [3,5,7]
v=03 [0,1,6]        v=04 [5,7,13]       v=05 [1,2,8]
v=06 [7,12,17]      v=07 [2,5,11]       v=08 [0,1,3]
v=09 [0,7,8]        v=10 [0,1,6]        v=11 [2,3,4]
v=12 [0,1,4]        v=13 [5,7,8]        v=14 [0,2,4]
v=15 [0,10,18]      v=16 [3,4,6]        v=17 [3,4,6]
v=18 [8,14,15]
```

Thus:

- declared incidence count: 57;
- literal unreachable incidence count: 0;
- declared-only false incidences: 57;
- rows satisfying the biconditional `declared W_v = literal W_v`: 0 of 19;
- rows satisfying the strict counterexample inequality: 0 of 19.

The orientation reaches every nondirect vertex in exactly two steps. It therefore satisfies Seymour's desired inequality at every vertex with `10 >= 8`; it is not a counterexample.

## Exact remaining lift condition

The coarse seed verifies that the irregular missing-degree, incidence-capacity, and regular-block constraints can coexist. The missing condition is load-bearing: after changing or completing the orientation, every one of the 57 declared incidences must become literally unreachable and every undeclared nondirect target must become two-step reachable. This is the full biconditional `W` semantics required by the registered direct route.

No strict SSNC conclusion follows from this seed or this audit.