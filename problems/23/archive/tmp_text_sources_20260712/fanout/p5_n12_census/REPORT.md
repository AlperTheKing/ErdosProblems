# Exact Pattern-5 N<=12 census

## Scope and verdict

This is a falsifier/coverage gate, not a theorem claim.  It checks the exact
relation-level FreeHalf semantics; it does not supply the still-missing
terminal-to-token reservation-ledger adapter.

The gate generated every connected triangle-free graph of orders 5 through
12, selected the existing exact connected Gamma-minimum maximum cut, retained
the all-ell=5 systems, and enumerated every coherent shortest-row tuple.
Arithmetic is integer-only.  Maximum worker count was 12.

Two relations and two demand scales are reported:

- Claude checksum: P1 sameFirst + P3 rowCompanion, before/after adding P5.
- Full relation-level union: P1 + corrected common-blue P2 + P3 + strict P4
  + P5.
- One-copy demand: collision + HitNeed.
- Production MicroDemand: collision + 25*HitNeed.

## Input audit

P5 is computable on the N12 fixtures without guessed fields.  From graph6,
the canonical cut, and the explicit row choice, the gate derives pair counts,
selected support, active scope, quiescent components of `B[V\A]`, active
boundaries, selected-component equality, half-zero reservations, and exact
switch loss.

The pinned `K??E@cyjFgWk`, choice `[0,4,5,7]` fixture reproduced every raw
field.  One cached-name caveat was found: its `activeComponents` JSON field
contains all selected off-support components; the true active subset must be
filtered by bad-pair containment.  No cached component label is consumed.

That fixture has P5 keys 32, no negative switch and no reserved candidate.
Its micro deficient shore `{10,11}` changes from reach/demand `59/72` to
`87/72`, so P5 repairs that particular defect-13 tuple.

## Coverage

| Orders | Eligible systems | Row tuples | Positive demand |
|---|---:|---:|---:|
| 5-10 | 6,421 | 50,104 | 922 |
| 11 | 64,287 | 1,035,476 | 20,943 |
| 12 | 921,910 | 39,142,819 | 1,627,854 |
| **5-12** | **992,618** | **40,228,399** | **1,649,719** |

The N12 preflight exactly revalidated 1,144,061 generated graphs, 899,619
light / 21,841 medium / 450 heavy eligible systems, and 20,181,461 /
14,160,291 / 4,801,067 tuples in those bands.

For every eligible graph, the gate also records the lexicographically first
global minimum of `collision + 25*HitNeed`.  All 992,618 representatives have
exact minimum zero and therefore pass vacuously; no heuristic selection or
sampling is used.

## Counts

- P5 was nonempty on 1,462,332 tuples.
- P5 emitted 42,424,232 distinct-key occurrences and 94,951,980 owner arcs.
- Of those, 27,565,896 keys and 75,166,260 owner arcs were new versus P1-P4.
- 21,212,116 P5 switch sets were checked: negative loss 0, reserved sources 0.
- Claude P1/P3 one-copy failures: 8,929 before P5, 677 after; repaired 8,252.
- Full P1-P5 one-copy failures: 0 on all 40,228,399 tuples.
- Full relation micro failures: 63,422 before P5, 25,112 after; repaired 38,310.
- Remaining micro failures by order: N10 886, N11 3,162, N12 21,064.

Thus P5 is a large exact repair, but it is not a universal completion at the
25-microcopy scale.  The full one-copy relation has no census falsifier.

## First falsifiers

Literal Claude P1/P3/P5 one-copy relation: graph6 `I?rFf_{N?`, family sizes
`[8,8,8,8]`, tuple index 7, choice `[0,0,0,7]`.  Demand is 36; P1/P3 reach is
22 and P5 raises it to 30, leaving defect 6.  Adding current P2/P4 raises full
P1-P5 reach to 46, so this is not a full-union falsifier.

Full P1-P5 production MicroDemand: graph6 ``I?`fBO]]?``, family sizes
`[4,6,6]`, tuple index 43, choice `[1,1,1]`, rows:

```text
[0,4,7,1,6]
[5,2,9,3,8]
[6,2,9,3,8]
```

The independent replay checks connectedness, triangle-freeness, maximum cut
14, minimum Gamma 75, and three length-five bad edges.  Active owners 8 and 9
have micro demands 33 and 58.  P1-P4 provides 33 keys; P5 adds exactly 8 keys,
for full-shore reach/demand `41/91`, defect 50.  At one-copy scale the same
tuple has demand 19 and minimum margin 14, hence passes.

## Replay

```powershell
python tmp/fanout/p5_n12_census/audit_inputs.py
python tmp/fanout/p5_n12_census/p5_census.py --n-min 5 --n-max 10 --mode all --workers 10 --output tmp/fanout/p5_n12_census/census_all_n5_n10.json
python tmp/fanout/p5_n12_census/p5_census.py --n-min 11 --n-max 11 --mode all --workers 11 --output tmp/fanout/p5_n12_census/census_all_n11.json
python tmp/fanout/p5_n12_census/p5_census.py --n-min 12 --n-max 12 --mode all --workers 12 --output tmp/fanout/p5_n12_census/census_all_n12.json
python tmp/fanout/p5_n12_census/aggregate_results.py
python tmp/fanout/p5_n12_census/replay_first_falsifier.py
python tmp/fanout/p5_n12_census/find_first_claude_falsifier.py
python tmp/fanout/p5_n12_census/verify_results.py
```

## Pinned hashes

- Aggregate canonical payload: `229dbf56afd9ce078a28a80a992d3a7e6fb6de63c4bb5f90cc5c016f04252ce9`.
- Aggregate JSON file: `37d80d492ac607f6dd7b4ecc471a9ad5f7a45e216bdc05cee4549b20e88340dc`.
- N12 canonical payload: `d628a42235b36c6543e6f3a3047830c436c5b4a32987025bea4c450cc7ec7705`.
- N12 JSON file: `378515734f097c7b1c10cfa8aa900c3d5a56a9458dacb4497ce174a67bf067e1`.
- Input-audit canonical payload: `241988945df779b15e611121b620de377b3ea12a174a06e288cdbfae82cadf46`.
- P5 core: `64c8aca68f6ccb548a65c1df439fb562cc9a8f54e64249e8346489ad97b4796a`.
- Census driver: `a819e5ff59fe92081016cdffdcaa8b978aca51fba7006ddc69f1c6b2841874cb`.
- First micro replay canonical payload: `23d36a5ded1e22e1a42bf77b7718e88d165c34cc3001db1d76a202993f3c399d`.
- First micro replay JSON: `47e86b826b753051d30553f3d9c8e71441f9bc9d33421c51a605095a80e154f0`.
- First Claude-relation falsifier JSON: `fe3c7a18acf73ed53d160844a53da6070e62c53028b3dd38546a10bd7bfdaf48`.

`MANIFEST.sha256` pins every delivered artifact in this directory.
