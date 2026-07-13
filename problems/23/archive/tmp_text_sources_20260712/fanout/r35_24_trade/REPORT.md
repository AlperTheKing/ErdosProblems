# R35 real-24 full collision-defect trade

## Verdict

The exact 24-vertex cage has a zero-defect no-common-blue row tuple.
Moreover, one row replacement from the displayed deficient tuple is a strict
`CheckedCollisionDefectTrade` and also decreases the injective mixed-radix
tuple rank required by `CheckedCollisionLexTrade`.

The displayed tuple's full coherent defect is `68`, not the central-owner
value `24` reported by the earlier endpoint-diversity lane.  The full minimum
Hall shore is the two-owner set `{7,8}`:

```text
total demand                 240
maximum coherent matching   172
full defect                   68
shore {7,8} demand           144
shore {7,8} neighbor keys     76
shore deficiency              68
```

The exact trade changes only bad atom 9, whose ordered endpoints are
`(9,21)`:

```text
old row index 15: (9,12,15,18,21)
new row index  7: (9, 7,16,19,21)
```

At the new tuple:

```text
total demand                 250
maximum coherent matching   250
full defect                    0
tuple rank       90510000000000 -> 90502000000000
```

Thus the same one-row change is both defect-improving and rank-decreasing.
The zero-defect conclusion does not depend on rank: `certificate.json`
contains an explicit assignment of every one of the 250 occurrence-level
collision obligations to a distinct legal source half.

## Evaluated semantics

`evaluate_trade.py` reconstructs the exact graph, all 12 bad atoms, and all
complete shortest-row families.  Their sizes are

```text
(10,10,10,10,10,10,10,10,10,45,45,45).
```

For every tested tuple it recomputes, rather than freezes:

- selected support and selected vertex union;
- selected off-support active graph and active bad-containing components;
- every occurrence-level `CollisionObligation`, including producer atom,
  positive occurrence ordinal, copy, half, and component label;
- ordered `FreeHalf` keys and `ScopedReserved` half-zero removal;
- P1 same-first, P3 row-companion with exact two-vertex switch loss,
  strict P4 outside-selected components, and P5 outside-active-scope
  components with exact integer union-switch loss;
- the global injective matching and base-key component coherence condition.

Common-blue and P2/common-bad are absent.  This is exactly the requested
no-common-blue P1/P3/strict-P4/P5 union.

All positive-demand owners in both certificate states lie in active component
label `0`.  Therefore the full `BaseKeyComponentCoherent` check is satisfied
for every assigned ordered-pair base; it is not approximated owner by owner.

## Search and certificate

The deterministic search evaluated 90 distinct complete row tuples.  It
started from the displayed tuple and enumerated row-family replacements in
database order.  The zero-defect tuple was found at Hamming distance one, so
no sampling or floating-point optimization was needed.

`certificate.json` contains:

- the complete graph, cut-edge set, bad-atom order, row-family sizes, and both
  complete tuples;
- the old integral max-flow and Hall min-cut certificate;
- all 250 new obligation-to-source assignments;
- the changed atom, exact defects, and exact mixed-radix ranks.

Replay from the workspace root:

```powershell
python tmp/fanout/r35_24_trade/evaluate_trade.py
python tmp/fanout/r35_24_trade/verify_certificate.py
python -m py_compile tmp/fanout/r35_24_trade/evaluate_trade.py tmp/fanout/r35_24_trade/verify_certificate.py
```

Expected verifier summary:

```text
REPLAY=PASS
old=demand:240 matched:172 defect:68
old_min_cut=shore:[7, 8] demand:144 reach:76
new=demand:250 matched:250 defect:0
changed_atoms=[9] rank:90510000000000->90502000000000
```

No floating point, `native_decide`, or heuristic result is used in the
certificate or its replay.
