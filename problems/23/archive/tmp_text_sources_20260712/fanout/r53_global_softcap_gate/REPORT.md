# R53 corrected global FreeHalf soft-cap gate

## Verdict

The evaluator implements the corrected global model with coherence-free P4.
It routes every global `CollisionHalf` to an actual `FreeHalf` key, gives each
key capacity 1, and gives the four keys of each capped active undirected edge
aggregate capacity 2.

The named N12 common-blue tuple, N24 R1 tuple, N89 singleton database, N2943,
N3892, and all four N78 states pass.  All 2,400 N12 common-blue row tuples pass.
Every reconstructed graph system through order 12 has exact graph minimum 0.

The only corrected-model failures in this gate are the supplied R35 N24 tuple
and its tested Hamming-distance-one neighborhood.  The complete R35 row
product was not exhausted here, so these are fixed/local failures rather than
a negative graph-level verdict.

The former N89 defect-2 verdict used an extra selected-component equality in
P4.  That strict-P4 result is retained only as an archived model comparison.
The corrected P4 has no such coherence condition and routes N89 exactly
`776/776`.

## Exact model

- Demand contains every global `MinimumDemandCollisionHall.CollisionHalf`,
  including inactive owners.
- A sink is a triple `(x,y,h)` with `x != y`, `pairCount(x,y) = 0`, and
  `h in {0,1}`.  These are finite, proof-carrying `FreeHalf` realizations; raw
  physical keys that are not free are never admitted.
- The six relations are P1 same-first, P2 common-bad, P3 row-companion, P4
  outside attachment, P5 quiescent attachment, and common-blue.
- P4 is coherence-free: its boundary attachment does not require the source
  boundary vertex to share the owner's selected active component.
- Every literal key has capacity 1.  For every `activeEdges` entry, the four
  keys `(u,v,0/1),(v,u,0/1)` feed one capacity-2 node.
- Every capped active edge is checked to have all four actual FreeHalf keys.
- No fixed reservation is removed.
- The solver is integer Dinic flow.  Integrality of the capacitated network
  makes this the exact rational optimum; no floating point or tolerance is
  used.

Keys are compressed only when their complete owner masks agree.  Active-edge
orientations retain separate unit pools before entering their shared cap-2
node, so compression preserves both unit and aggregate capacities.

## Named fixtures

| Fixture/state | Global demand | Flow | Defect | Verdict |
|---|---:|---:|---:|---|
| N12 common-blue `[0,4,7,9]` | 68 | 68 | 0 | pass |
| N12 graph witness `[0,0,0,0]` | 110 | 110 | 0 | pass |
| N24 R1 fixed rows | 312 | 312 | 0 | pass |
| N167 fixed rows | 902 | 902 | 0 | pass |
| N175 fixed rows | 906 | 906 | 0 | pass |
| N311 fixed rows | 3,606 | 3,606 | 0 | pass |
| N89 singleton row database | 776 | 776 | 0 | pass |
| R35 N24 displayed tuple | 312 | 288 | 24 | fixed tuple fails |
| R35 prior one-row trade | 322 | 316 | 6 | fixed tuple fails |
| R35 Hamming <= 1 minimum | 330 | 324 | 6 | all 214 local states fail |
| N2943 all-anchor | 36,648 | 36,648 | 0 | pass |
| N3892 lex rows | 70,940 | 70,940 | 0 | pass |
| N78 rotor states 0,1,2,3 | 576 each | 576 each | 0 | all pass |

N2943 contains 13,540 inactive collision halves.  Its staged defects are
`3508,3508,22,0` after P1, P2, P3, and common-blue.  N3892 has active-only
demand 0 but global demand 70,940; its P1/P2/P3 defects are `388,372,0`.
These fixtures directly rule out substituting an active-only demand gate.

Literal assignments are exported for every passing named state, including
36,648 records for N2943 and 70,940 for N3892.  Verification checks actual
freeness, eligibility, unique unit keys, complete demand coverage, and every
active-edge load.

## Corrected failures

The R35 displayed tuple has min-cut shore owners `{6,8}`.  Shore demand is
144, direct key capacity is 116, and grouped active-edge capacity is 4, giving
capacity 120 and defect 24.

All 214 states at Hamming distance at most one from the displayed tuple fail.
The exact minimum is 6 at state
`[0,0,0,0,0,0,0,0,0,0,31,44]`, with demand 330 and flow 324.  The full defect
histogram is:

```text
6:57, 8:81, 14:6, 16:30, 22:24, 24:16
```

`r35_n24_hamming_le_one.json` contains every failing state.  Its
`globalGraphMinimumStatus` is explicitly unavailable because the complete row
product was not exhausted.  No missing relation is replaced by an empty set:
every one of these negative states explicitly enumerates all six relations.

## Exhaustive gates

The N12 common-blue graph was exhausted over all 2,400 row tuples.  Every tuple
has defect 0 under corrected P4, so the failure list is empty.

The graph census stops a row product only after finding exact defect 0.  If no
zero is found, it exhausts the complete product before reporting a graph
failure.

| Orders | Eligible systems | Available tuples | Examined tuples | Positive tuples before stop | Failed graph minima |
|---|---:|---:|---:|---:|---:|
| 5-10 | 6,421 | 50,104 | 6,664 | 243 | 0 |
| 11 | 64,287 | 1,035,476 | 64,291 | 4 | 0 |
| 12 | 921,910 | 39,142,819 | 921,911 | 1 | 0 |
| **5-12** | **992,618** | **40,228,399** | **992,866** | **248** | **0** |

Thus all 992,618 reconstructed graph systems through order 12 have exact
minimum defect 0 in this model.  This is a finite census statement, not a
general proof of the provider theorem.

## Relation availability

All six relations are executable and reconstructed from the graph and row
tuple.  There is no unavailable relation data in any verdict above.

P1 and P3 correspond to compiled eligibility predicates.  Common-blue has a
compiled terminal predicate but no production matching consumer.  P2 is an
archival executable relation without a named Lean disjunct.  P4 and P5 have
exact executable semantics but remain caller-supplied fields of production
`SixRelationEligible`.  The Lean abstraction therefore does not itself prove
that these executable relations are the eventual production instance.

For passing states, evaluation may stop after a subunion first reaches defect
0.  The artifact records later relations as `notEnumeratedFamilies`; adding
them cannot lower a zero defect.  This is an exact full-union verdict by
monotonicity, not missing data.  Every failing state enumerates all six.

## Strict-P4 archive

`counterexample_n89.json` preserves the discarded strict-P4 computation:
demand 776, flow 774, defect 2, shore `{0,1,2}`, shore demand 528, and capacity
526.  It is a negative verdict only for that stricter relation.  The independent
coherence-free replay in `n89_unscoped_p4_alternate.json` supplies 776 distinct
actual FreeHalf assignments and checks the same unit and grouped capacities.

## Hashes

Canonical payload SHA-256 values:

```text
named_results.json             ff818777b92a2c536b5ee5617b0c2d35a9fd7dd9b383e40e03cc541f7cb30551
N12 all-tuples                 572de1c48504daf92bdd72d78015d2a8b76944f39a4b07fa4c2c80a68a44e2cc
R35 Hamming<=1                 0db220001c6af794e5c46f9174a86a2b7f86e0bd492bd29ea1115a7342dd49d0
census N5-10                   a07974020e50b6b399d59269984186446a3de07e1f204454a272c486cd94a3ba
census N11                     00c1760f5b8d23fb38d71185367e46055519feeeeec139950eb7e6f6b3d8c5a6
census N12                     05c39e0ca3716cd86e66ddd165d97162b71aa86df413c358eed437365f9ddd32
N89 independent corrected P4  f3e74c613f213e9903461fe93f4f2a8f6c919d706ac2312b570ced4767a35c4c
global_softcap.py (file)       32c7f9bc0c4d2921d3b1fa5d8557ada0088eee8a024fdb90330023060101ac13
```

`MANIFEST.sha256` pins every delivered script, JSON file, report, and literal
certificate.

## Replay

From `E:\Projects\ErdosProblems`:

```powershell
python problems/23/writeup/_claude_r22_89_gate.py
python tmp/fanout/r53_global_softcap_gate/gate.py
python tmp/fanout/r53_global_softcap_gate/alternate_unscoped_p4.py
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 5 --n-max 10 --workers 16 --chunk-size 32 --output tmp/fanout/r53_global_softcap_gate/census_n5_n10.json
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 11 --n-max 11 --workers 32 --chunk-size 32 --output tmp/fanout/r53_global_softcap_gate/census_n11.json
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 12 --n-max 12 --workers 48 --chunk-size 64 --output tmp/fanout/r53_global_softcap_gate/census_n12.json
python tmp/fanout/r53_global_softcap_gate/verify.py
```

No `native_decide`, floating-point value, external LP solver, or guessed empty
relation is used.
