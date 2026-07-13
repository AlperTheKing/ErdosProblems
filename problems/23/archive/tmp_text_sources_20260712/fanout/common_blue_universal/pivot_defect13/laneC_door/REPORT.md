# Door audit — N=12 defect-13 shore

Verdict: Door does not pay the 13-unit Hall defect.

The canonical graph6 decode and production row-family selection give deficient shore `{10,11}`, demand 72, existing CommonBlue reach 59, and defect 13. Its raw graph boundary is:

- blue boundary (`dB=8`): `(0,10)`, `(0,11)`, `(1,10)`, `(1,11)`, `(2,10)`, `(3,10)`, `(5,10)`, `(5,11)`;
- bad boundary (`dM=2`): `(7,11)`, `(8,11)`;
- raw `sigma=dB-dM=6`.

At the Door-bank scale `capQ=25*sigma=150`, hence Hall capacity is exactly `capQ/25=6`. Thus even the aggregate upper bound is 7 below the required 13. This arithmetic alone rules out a Door-only payment; it is not asserted as a FullBank repair.

Typed-source audit: production `CapSource.door(edge)` requires the literal extractor exit-edge key. `OwnEdgeDoorSourceData.Checked` additionally requires injective `portEdge`, source equality to that exact Door key, and `capQ>=25`. The canonical graph/row code for this fixture constructs neither `TypedGlobalLedgerData` nor an `OwnEdgeDoorSourceData` adapter. Therefore the eight blue-boundary edges above are candidate raw exit edges, not fabricated typed Door tokens. Literal constructed typed keys, legal port incidences, and checked spend assignments are all empty for this replay. Consequently no per-token no-double-spend claim is available beyond the production conditional theorem; aggregate 150 cannot be assigned to ports by itself.

Production guardrails used: `CommonBlueExtendedMatching.lean`, `ResidualSourceTokenization.lean`, `FullBankToLengthSurplusCharge.lean`, `TypedFullBankSources.lean`, `FullBankPortSinks.lean`, `ActiveScopedMinimumExchange.lean`, `CheckedC5BaseTransfer.lean`, and the canonical `n12_pht.py` extractor/row-family code.

Replay: `python replay_door.py` from this directory (or by repository-relative path). It uses integer arithmetic only and asserts `(dB,dM,sigma)=(8,2,6)` and `(demand,defect)=(72,13)` before writing `result.json`.
