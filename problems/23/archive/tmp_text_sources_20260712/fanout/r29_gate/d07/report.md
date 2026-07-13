# R29 Hamming-one local-delta audit: NOT REPRODUCIBLE

## Verdict

The all-459004 claim is not accepted. The workspace has no canonical 2943-vertex graph, cut, 676×680 selector-row database, or selected tuple. Consequently there are no 459004 concrete replacements to exhaust, and the three requested universal conditions cannot be evaluated on the claimed instance. This is a certificate-level falsifier: the archived prose asserts an exhaustive computation but supplies neither its input nor a replayable output.

## Independent symbolic/local derivation

For an ordered coordinate pair `(x,y)`, let `c_xy` be its old selected-row count and let `p_xy,q_xy` be its 0/1 membership in the removed row `P` and inserted row `Q`. From the Lean definition, its collision-unit delta is exactly

`[c_xy-p_xy+q_xy-1]_+ - [c_xy-1]_+`.

Thus a pair newly added by `Q` contributes `+1` iff `c_xy>=1`; a pair removed with `P` contributes `-1` iff `c_xy>=2`; otherwise it contributes zero. The score collision term is twice the sum of these deltas. `audit.py` exhaustively checks all valid `(c,p,q)` with `0<=c<8` (30 exact integer cases).

For a new vertex `v in Q\P`, its diagonal `(v,v)` creates score `+2` iff `v` already occurred in at least one other selected row. “Previously in exactly one row” is sufficient but not established by the archive. If its old multiplicity is zero, the diagonal contribution is **0**, immediately falsifying the stated mechanism. If old multiplicity exceeds one, the diagonal still adds `+2`, so “exactly one” is stronger than necessary.

## Three adversarial conditions

1. Positive-score vertices can deactivate: undecidable without the graph, cut, old/new selected vertex union, and support edges. The exact active-edge delta depends on every blue edge whose endpoint-presence or support-membership changes; no monotonicity follows from the collision formula.
2. `Q\P` always nonempty: undecidable without the 680 serialized rows per selector. Distinct row indices do not imply distinct vertex sets; two different paths may have `Q\P=empty`.
3. Every new vertex creates diagonal collision 2: true precisely when each `v in Q\P` has old row multiplicity at least one. The archive gives no multiplicity table, so this universal premise is unverified.

## Exhaustive exact validation

The symbolic formula and diagonal criterion were exhaustively validated with integers by `audit.py`. Instance exhaustion was blocked by absent input data, not computational limits. Repository search found the R29 numeric/hash claims only in prose/status/audit derivatives, never in a graph constructor or row certificate. The claimed `00186166...` target artifact is unidentified.

Run: `python tmp/fanout/r29_gate/d07/audit.py`.

## SHA256

- `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- `problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean`: `e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a`
- `audit.py`: `7cfb169ea98c9ff0ab1bff36e52784a4b025cef707e31a4e7a1eddbe34210143`
- `audit.json`: `e424fe3d2ef803b22d5398e74583df02fe93943a773b7a3c48b84d05fcf620d0`

## Proof gaps

Missing: canonical graph and cut; maximum-cut certificate; complete row serialization and distinctness; selected tuple; per-replacement `Q\P`; old vertex multiplicities; active-edge before/after sets; exact 459004 score table; minimum/multiplicity/sharp witness; full SHA256 and serialization convention. Until supplied, none of the three instance-universal conditions or the `>=30813` conclusion is proved.
