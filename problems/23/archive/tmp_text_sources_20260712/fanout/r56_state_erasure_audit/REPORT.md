# R56 selected-detour state-erasure audit

## Verdict

The existing 15-pair selected-detour negative-switch catalogue is
**graph-only**.  Its cut witness computation reads only the fixed vertex
count, blue-edge set, bad-edge set, and the two chosen protection-window bad
edges.  It does not read a row tuple, `pairCount`, selected support, active
support, or any joint state mask.

This is Outcome A for the dependency question asked in R56, but only on the
existing six-window unit-detour catalogue.  It is **not** a proof that an
arbitrary R55 neutral branch exports one of these checked prefix payloads.
The universal missing bridge is now:

```text
R55 same-atom neutral branch
  -> graph-only CheckedNeutralProtectionPrefix
  -> cross-state opposite-corner overweight.
```

No `CheckedTwoProtectionPrefixSwitch` or
`coexistingTwoPrefix_stateErasure` theorem currently exists in the production
Lean tree.

## Exact replay

```powershell
python -B tmp/fanout/r56_state_erasure_audit/audit.py
```

The gate parses the AST of `minimum_sigma`, rejects any row/state dependency,
checks the repair cut formula, and independently recomputes every one of the
15 pair masks by exhaustive enumeration of all `2^15` normalized cuts.

Exact result:

```text
outcome                              GRAPH_ONLY_FOR_EXISTING_CATALOGUE
catalogue pairs                      15
minimum sigma = -1                   15/15
forbidden state identifiers          0
repair cut formula graph-only        true
universal extraction proved          false
```

The first minimum masks reproduce the posted catalogue exactly:

```text
(0,1) 65    (0,2) 193   (0,3) 1     (0,4) 2049  (0,5) 1592
(1,2) 193   (1,3) 65    (1,4) 2113  (1,5) 1080
(2,3) 193   (2,4) 2241  (2,5) 56
(3,4) 2049  (3,5) 6145  (4,5) 6145
```

All arithmetic is integer edge counting.  `result.json` is the canonical
machine-readable output.
