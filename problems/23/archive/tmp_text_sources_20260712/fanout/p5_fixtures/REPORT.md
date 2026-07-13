# Pattern-5 fixture regate

Scope: independent integer-only audit of fixtures 24/167/175/311/3892/89/2943.
This is a fixture result only; it does not assert the universal matching statement or Erdős #23.

## Result

All requested active-scoped fixture certificates pass.  Every nonempty owner shore was
enumerated for each nonvacuous active fixture.  The 24 and 89 historical unscoped checks
were also rerun using the legacy loose P4 boundary predicate.

| Fixture/scope | |A| | owners | demand | reserved keys | P1-P4 sources | semantic P5 union | certificate sources | min certificate slack | shores |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2943 active | 19 | 17 | 23115 | 36 | 8363334 | 15374314 | 8363362 | 0 | 131071 |
| 24 active | 0 | 0 | 0 | 0 | 0 | 0 | 0 | vacuous | 0 |
| 24 legacy all | 0 | 9 | 312 | 0 | 714 | 714 | 714 | 318 | 511 |
| 167 active | 13 | 13 | 458 | 24 | 15426 | 50190 | 15426 | 3442 | 8191 |
| 175 active | 0 | 0 | 0 | 0 | 0 | 0 | 0 | vacuous | 0 |
| 311 active | 13 | 13 | 1064 | 24 | 71486 | 148946 | 71486 | 3730 | 8191 |
| 3892 active | 0 | 0 | 0 | 0 | 0 | 0 | 0 | vacuous | 0 |
| 89 active | 0 | 0 | 0 | 0 | 0 | 0 | 0 | vacuous | 0 |
| 89 legacy all | 0 | 12 | 776 | 0 | 13616 | 13616 | 13616 | 11702 | 4095 |

`semantic P5 union` is the number of distinct source keys reachable by at least one owner
after exposing every semantically eligible P5 terminal.  `certificate sources` uses no P5
key when P1-P4 already passes, and exactly the checked 28-key supplement on 2943.

## 2943 exact gate

The active scope has 17 positive-demand owners, not only hubs 0/1/2.  All 131071 nonempty
owner shores were checked.

- Old relation: the only negative shore is `{0,1,2}`, demand 19953, reach 19925, defect 28.
- Checked P5 certificate: keys `(3,x,h)` for even `x=56..82`, `h=0,1`.
- All 28 keys are Free, globally absent from every owner's P1-P4 pool, and outside all 36
  scoped reservations.
- The leaf-3 quiescent component has size 1379, boundary `{1,55}`, and exact loss
  `702-676=26`.
- Certificate relation: hub reach 19953, slack 0.  It is the sole zero-slack owner shore.
- Full semantic P5 was audited separately; it has many more valid keys and is not the
  zero-slack certificate.

## Fixture notes

- 167 is nonvacuous and passes P1-P4 before P5; P5 source eligibility and switch losses
  were nevertheless reconstructed and checked.
- The new selected row in 175 uses the old active edge `0-9`; the remaining off-support
  components contain no selected bad-edge endpoint pair, so active scope is empty.
- 3892's lexicographic row tuple leaves only off-support edge `{4,8}`.  Its component
  contains no bad-edge endpoint pair, so it is inactive under the current `ActiveOwner`.
- 24 and 89 are likewise active-scoped vacuous.  Their legacy unscoped owner relations
  pass all shores independently.

## 311 script discrepancy

`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py` canonicalizes
an attachment atom `(P4,P0)` to `(P0,P4)` and then applies a row template that expects the
original orientation.  Its first emitted row is `(167,239,9,175,303)`, whose first and last
steps are not blue edges.  The independent gate preserves the oriented endpoints and uses
the valid row `(303,239,9,175,167)`.  Pair-count vertex sets agree, but selected support and
active-edge calculations do not; the available script's structural row input should not be
used as a validity certificate.

## Reproduction

```powershell
python tmp/fanout/p5_fixtures/gate.py --legacy-small
python tmp/fanout/p5_fixtures/verify.py
```

Primary artifacts:

- `gate.py`: independent graph/source/reservation/shore reconstruction.
- `result.json`: full machine-readable fixture records and source bitset hashes.
- `shores_*.jsonl`: every nonempty owner shore for each nonvacuous relation.
- `verify.py` / `verification.json`: independent shore-table and 2943 certificate check.

Pinned hashes from the verified run:

- gate SHA-256: `e50054ec3ec6e9ad91191b20f65cae3d52dc7b888dd6a77e4fad5c1fe78d466f`
- result SHA-256: `7e86aa15506814ac45601c0bfa57211cbe9f9c9ac7bc95b39006d7b7abb3f11d`
