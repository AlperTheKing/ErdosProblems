# Independent implementation audit: fixed `K_19-C_19` CNF

Status: **PASS**.

Audit date: 2026-07-21. The frozen generator is projection-equivalent to the
frozen semantic specification. No encoding, map, scope, symmetry, or pinned
calibration defect was found. No unpinned production solver was launched.
This result validates the implementation only; it is not evidence that the
formula is SAT or UNSAT.

## Frozen inputs

| Artifact | SHA-256 |
|---|---|
| `CYCLE19_CNF_SPEC.md` | `987F891E548A1E14DC482180387AE26DD5B0158B894EF904082FD69E8863A378` |
| `engine/generate_cycle19_cnf.py` | `F1431BDC588728ACE5545ED2D43D427BEC5CCE9B72913ADF5651B0DDEE1955E4` |
| `engine/tests/test_cycle19_cnf.py` | `03D10BECCB69041202095FC30EBE917040558AA2A46F9923339459BE12DE855B` |
| `engine/audit_cycle19_cnf.py` | `FD7A593B13A08B2ADE164E5D10B86DA8203998DDD90AADB2769AB7757549F503` |
| `engine/tests/test_cycle19_audit.py` | `843A1204ADACB5842E39139C9EDB50F07CCA367184B15CD6109103149BAECC4D` |
| frozen `cycle19.cnf` | `A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38` |
| frozen `manifest.json` | `4CF5469273AD6F2DF524EC21B30379151D174B2533AF0BC463A33A6DDA4D687E` |

The manifest records variable-map hash
`0051A5F158A6A0B0870A8787700ED86E2C573394640B9F7F336A454E9E57B57B`
and the same generator hash shown above.

A fresh in-memory generation produced a byte-identical DIMACS file. Its
manifest JSON was structurally identical and became byte-identical to the
frozen manifest under the same Windows CRLF translation used by
`Path.write_text`; the resulting hash was the frozen hash above.

## Optimized-domain reconciliation

The full reference formula deliberately allocates every array entry. The
production generator omits only entries whose truth value follows from the
fixed support and the one-variable orientation convention.

| Family | Reference | Generator | Reason for difference |
|---|---:|---:|---|
| orientation | 152 | 152 | no difference |
| `p` | 6,859 | 4,560 | omit 1,995 loop/missing-step entries and 304 return entries `v->w->v`, which equal `a and not a` |
| `reach2` | 361 | 342 | omit the 19 diagonal values, all structurally false |
| `unreachable` | 361 | 342 | omit the 19 diagonal values, all fixed false by definition |
| semantic total | 7,733 | 5,396 | exact sum of the preceding projections |

There are 4,864 triples whose two edge positions are present in the fixed
support. Exactly 304 have target equal to source and would require both
orientations of one present edge. Removing these leaves the 4,560 allocated
path variables. Every off-diagonal reach OR ranges over all remaining
possible path variables; every omitted input is constant false.

The optimized clause ledger is exact:

| Block | Clauses |
|---|---:|
| 4,560 three-clause path equivalences | 13,680 |
| reach: 4,560 short implications plus 342 complete reverse OR clauses | 4,902 |
| `z`: 304 present directions times 3 plus 38 missing directions times 2 | 988 |
| 19 sequential exact-8 degree counters | 4,864 |
| 19 row plus 19 column sequential exact-3 counters | 6,840 |
| symmetry unit | 1 |
| **total** | **31,275** |

The 5,852 cardinality auxiliaries split into 19 disjoint degree ranges of 128
variables and 38 disjoint ledger ranges of 90 variables. Therefore the
optimized instance has 11,248 variables and 31,275 clauses. These are the
frozen DIMACS and manifest counts.

## Raw semantic-clause comparison

An independent parser read the frozen DIMACS and variable map. A separate
reconstruction used only the fixed-cycle predicate and the names in the map;
it did not call generator clause-building methods.

The following checks all passed.

1. The edge domain was exactly the 152 present unordered pairs. There was no
   variable for a loop or any of the 19 missing pairs, including `{18,0}`.
2. `edge(0,2)` was variable 1, so `X(0,2)=1` and `X(2,0)=-1`. For every other
   present pair, the independently reconstructed signed literal agreed with
   all path, degree, and `z` clauses.
3. The path-variable domain was exactly the 4,560 nonconstant, off-return
   triples. Each variable had both forward implications and the reverse AND
   clause with the correct signed arc literals.
4. Every one of the 342 off-diagonal reach variables had all of its short
   `p -> reach` clauses and one complete `reach -> OR p` clause. No possible
   nonconstant intermediate was missing.
5. Every present off-diagonal `z` had the three-clause equivalence including
   direct-arc exclusion. Every missing direction had exactly the two-clause
   reduction `z iff not reach`. No diagonal `z` variable existed.
6. The complete independently reconstructed semantic clause multiset was
   identical to the first 19,570 clauses of the raw DIMACS.
7. The only clause involving orientation variables alone, and the only unit
   clause in the full formula, was `[1]`, the signed unit `X(0,2)`. No root
   triple, reversal, or additional arc symmetry was present.

## Sequential cardinality and scope audit

The raw blocks and manifest auxiliary ranges gave the following exact scope
inventory:

- 19 `outdegree(v)=8` blocks, each over the 16 correctly signed outgoing
  literals, with 128 private auxiliaries and 256 clauses;
- 19 `source-unreachable(v)=3` blocks, each over the 18 targets in row `v`,
  with 90 private auxiliaries and 180 clauses; and
- 19 `target-roots(u)=3` blocks, each over the 18 sources in column `u`, with
  90 private auxiliaries and 180 clauses.

For every block, the set of semantic input IDs was exactly the intended row,
column, or signed degree list. Its auxiliary IDs were exactly its declared
range, and no clause shared auxiliary variables across scopes.

The checks included:

- 969 valid/invalid pinned assignments distributed over all 57 actual blocks,
  with zero SAT-status mismatches;
- all 65,536 assignments to the actual `outdegree(0)=8` block: exactly 12,870
  assignments were SAT, equal to `binom(16,8)`, with zero mismatches;
- all 262,144 assignments to the actual
  `source-unreachable(0)=3` block: exactly 816 were SAT, equal to
  `binom(18,3)`, with zero mismatches;
- all 16 assignments to the frozen signed fixture
  `Exactly(2,[a,not b,c,not d])`, with zero mismatches; and
- the frozen 5-by-5 row/column fixture: the original assignment passed rows
  and failed columns, its transpose failed rows and passed columns, and the
  circulant assignment passed both.

Thus the count reduction from the subset reference encoding is explained
entirely by the calibrated sequential counters; it does not change the
cardinality predicates or couple scopes.

## Pinned calibration completeness

Both calibration templates pin all 152 orientation variables. Comparing the
pinned builder with the otherwise identical unpinned calibration builder
showed exactly 152 appended orientation-unit clauses, in canonical edge order.
There is no unpinned orientation variable in either calibration.

Each pinned instance had:

```text
semantic variables: 5,396
cardinality auxiliaries: 2,432
variables: 7,828
clauses: 24,587
indicators replayed: 4,560 + 342 + 342 = 5,244
```

CaDiCaL 1.9.5 returned SAT for both fully determined definitional instances.
All 5,244 path, reach, and unreachable indicators agreed with an independent
scalar evaluation in both cases. The assumption test also forced the
opposite value of every one of these indicators to UNSAT. The full-ledger
formula correctly rejected the pinned circulant near-miss, which has two,
not three, unreachable vertices in every row and column.

For an additional raw-DIMACS replay, the `triangle-switch` calibration was
serialized, parsed by `audit_cycle19_cnf.py`, and then passed to CaDiCaL from
the parsed clauses. Results were:

```text
raw DIMACS SHA-256: 8BBDA67D2463141E0C18E5B2EC5586FEDB02C0D785EA52D326B69C8084661400
variables / clauses: 7,828 / 24,587
orientation units: 152, exact pin match
all raw clauses true under returned model: yes
independent indicators replayed: 5,244
mismatches: 0
```

The decoded orientation passed the independent fixed-support oracle and was
byte-for-byte equal as a Boolean matrix to the requested pin. This was a
fully pinned calibration, not a solve of the production formula.

## Executed commands and results

From `problems_external/ssnc_refutation/engine`:

```powershell
python -m unittest discover -s tests -p 'test_cycle19*.py' -v
```

Result: 17 tests, all passed in 0.716 seconds.

```powershell
python generate_cycle19_cnf.py calibrate --template all --solver cadical195
```

Result: two `CALIBRATION_PASS` records, 5,244 indicators each, zero
mismatches.

```powershell
python audit_cycle19_cnf.py --oracle-samples 1000 --seed 19031996 --dimacs instances\cycle19-fixed-v1\cycle19.cnf
```

Result:

```text
ORACLE_AUDIT_OK
random orientations: 1,000
DIMACS variables / clauses: 11,248 / 31,275
tautological clauses: 0
duplicate-literal clauses: 0
DIMACS SHA-256: A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38
```

Two independent Python-from-stdin audit harnesses then performed the raw
semantic-clause/scope checks and the pinned raw-DIMACS/model replay described
above. They returned `RAW_STRUCTURE_PASS`,
`ACTUAL_SEQCOUNTER_EXHAUSTIVE_PASS`, `ROW_COLUMN_FIXTURE_PASS`, and
`RAW_DIMACS_MODEL_REPLAY_PASS`.

## Decision

**PASS.** The optimized formula and map implement the frozen
`K_19-C_19` specification exactly after projection of structurally false
array entries. The signed constants, reverse clauses, direct and diagonal
exclusions, row and column axes, private sequential-counter ranges, and sole
`0->2` symmetry unit all agree with the specification. The pinned
calibrations are complete over the orientation variables and all allocated
semantic indicators.

This audit licenses only the already registered bounded proof-producing run.
It makes no SAT, UNSAT, counterexample, or SSNC claim by itself.
