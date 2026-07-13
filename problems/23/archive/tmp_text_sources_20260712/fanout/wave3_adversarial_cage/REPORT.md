# Wave 3 adversarial production-cage report

## Verdict

No production-realizable positive-defect active rotor can extend the three
deterministic first connected `n=17` supports at splits `9+8`, `10+7`, and
`11+6`. The exact obstruction is earlier and stronger than maximum cut,
active scope, matching, or ledger feasibility: every admissible 25-atom bad
set already contains a bad triangle on old vertices.

This is not a bounded-search closure of the t=5 catalogue. It excludes these
three fixed supports and the omission-budget classes stated below.

## Small obstruction

For a fixed bipartite blue support `H`, let `D4(H)` be its same-shore pairs at
blue distance four and let `N = |D4(H)|`. A rooted t=5 completion chooses 25
bad atoms, contains atom `(2,3)`, and gives both owners `0,1` bad degree five.

If both owners have the same only five `D4` neighbors `S`, both full bad stars
are forced. Every selected `D4` atom internal to `S` then closes a bad triangle
with either owner. Only `N-25` atoms may be omitted, so more than `N-25`
internal completers is impossible under triangle-freeness.

| split | support SHA-256 | N | omission budget | completers | obstruction |
|---|---|---:|---:|---:|---|
| `9+8` | `8fdc2d16234094b092202571976cbc57c1b8c834ae63aa1eb79e7b8193b6542b` | 27 | 2 | 5 | `5 > 2` |
| `10+7` | `af9d081acc6411b6ca505a16f8161a7bbe086e0988b7b7d3d186f8f14df7ff71` | 29 | 4 | 6 | `6 > 4` |
| `11+6` | `4c90300390e6384d045058ab34721ee614b6f37e7814b82057aa171ab045f5ae` | 25 | 0 | n/a | forced triangle `(3,5),(3,7),(5,7)` |

For `9+8`, `S={4,5,6,7,8}`. For `10+7`,
`S={5,6,7,8,9}`. The complete atom and completer lists are serialized in
`omission_budget_certificate.json` (canonical SHA-256
`184a97e233c3a422206e4cb27a38c6d7dcebaa939437aa3688165b824925c7e5`).

## Production scope

The ambient extension preserves all old graph edges, so an old-vertex bad
triangle cannot be removed by adding eight vertices or row-safe blue edges.
Consequently no triangle-free ambient extension exists. Maximum-cut, active
scope, target/second-owner turnover, coherent matching, positive defect, and
the balanced transport ledger are omitted from the CNF as a strict
relaxation; adding them cannot restore satisfiability. Both owner bad-degree
five constraints are retained.

## Exact checks

Independent exhaustive replay tested `120`, `3060`, and `1` rooted
degree-five selections respectively, with zero triangle-free survivors.
Small CNFs have `(variables,clauses)` `(127,221)`, `(229,423)`, and `(25,41)`.
CaDiCaL195, Glucose4, and Lingeling all return UNSAT. Native LRAT proofs verify
with `lrat-trim`; proof SHA-256 values are recorded in `verification.json`.

Principal artifact hashes:

- `first_supports.json` file SHA-256 `acbbabde70b058d54021c15f3ba9cbf3db188378b19425533ef351dd88cb1fc3`.
- `verification.json` canonical SHA-256 `0affe8888a02ec96330ce1f9cba36c2740faf429c8ce0b535af0bca0ed16dfde`.
- small CNF SHA-256: `73951d50...d53a`, `861f9666...ffcd`, `4633b8eb...f1dd`.
- LRAT SHA-256: `d2dd19a8...d672`, `20671608...e899`, `90e522e0...6cc8`.

Source telemetry remains only bounded input: canonical SHA-256 values
`95dbc901...a95f4`, `d612c59e...3bb`, and `31d82c62...cc44`. The obstruction
does not use their 3,000-support no-hit claim.

Replay commands are in `REPLAY.md` and `replay.ps1`.
