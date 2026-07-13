The FreeHalf deficit 28 creates no residual FullBank obligation.

For the canonical R29 all-anchor core:

- `S`: 1,383 bad row-closing edges.
- `F`: 2,797 selected blue support edges.
- `O = B \ F`: 4,242 off-support blue ports.
- `J = O`: 4,242 edge-specific Door sinks.
- `C`: 2,803 selected row vertices.
- `K = C`: 2,803 singleton cuts.

With `λ(x)=1/2`, the `O` loads are:

- 56 boundary ports of load `1/2`;
- 4,074 internal ports of load `1`;
- 112 ports outside `C` of load `0`;
- total routed load `4102`.

Assigning every `c ∈ O` to its own Door gives capacity demand at most one per sink. Thus the exact `FullBankRelaxedCoverCert` Hall residual is zero, independently of the FreeHalf owner-shore calculation `19953 − 19925 = 28`.

The semantic reason is that these are different LPs:

- `FreeHalf` counts injectively consumable ordered triples `(sourceX, sourceY, half)`, one integral unit each, restricted by owner eligibility.
- FullBank routes rational cut-boundary load `q(c,j)` into reusable typed capacity sinks. An edge-specific Door directly absorbs its port load.

Four current FullBank source kinds audit:

- `door`: fully typed and checked; own-edge legality, injectivity, and capacity are compiled. Raw capacity `25` becomes one Hall unit after division by 25.
- `vertexSlack`: represented and has endpoint-local routing constructors; singleton incidence consumes `1/2` per incident port.
- `c5Base`: represented as a typed source kind, but no adapter currently connects it to the `FullBankRelaxedCoverCert` sink type.
- `prune`: likewise represented only at the typed-ledger/coupling layer; no certificate adapter exists.

The active-scoped `FreeHalf` API itself exposes only `SameOwner` and `RowCompanion`; it does not represent these four FullBank capacity kinds.

Smallest true statement: the R29 all-anchor core admits the singleton all-Door FullBank certificate with `J=O`, `K=C`, `λ=1/2`, own-Door incidence, and unit Hall capacity per Door.

Smallest falsifier: any implication

```text
FreeHalf Hall deficit > 0  ⇒  FullBank Hall deficit > 0
```

is false. R29 supplies `28 > 0` on the left and an explicit zero-residual FullBank certificate on the right.

Replay:

```powershell
python problems\23\writeup\_codex_r29_fullbank_semantic_audit.py
python tmp\fanout\r29_gate\d05\retry2\rebuild_owner_hall.py
```

Checker: [_codex_r29_fullbank_semantic_audit.py](E:/Projects/ErdosProblems/problems/23/writeup/_codex_r29_fullbank_semantic_audit.py)