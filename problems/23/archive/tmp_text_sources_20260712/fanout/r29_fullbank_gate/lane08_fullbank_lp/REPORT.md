# R29 FullBank LP instantiation audit

## Verdict

**UNDEFINED.** The implemented production relation cannot be instantiated for the R29 hub shore. The audit therefore proves neither:

- PASS: a production `FullBankRelaxedCoverCert`/checked `FullBankGlobalPackage` absorbs the auxiliary 28-unit defect; nor
- FAIL: a Hall/LP defect survives after every production source class.

The reason is definition-level, not numerical: there is no compiled R29 provider for the mapping from auxiliary obligations to FullBank atoms/local covers, the four-kind token table, available capacities, port-to-token incidence, or the routing matrix. `FullBankPortSinks.lean` explicitly says legal edge-to-token incidence is absent (lines 80-81).

## Exact reconstruction

`verify.py` imports the deterministic constructor at `tmp/fanout/r29_gate/lead/r29_lead_gate.py:129-276`, replaces all 676 selector rows by `anchorRow`, and independently rebuilds pair counts, selected support, active components, collision, HitNeed, and owner-source masks.

The reconstructed data are:

- vertices `2943`, blue/cut edges `7039`, bad edges/rows `1383`;
- selected vertices `2127`, selected support edges `2797`, off-support blue edges `4242`;
- off-support load classes for the full selected core: `1370` internal load-1 ports, `2760` boundary load-`1/2` ports, `112` load-0 ports; total `2750`;
- active edges `1370`, active vertices `19`, demanded active edges `18`;
- each owner `0,1,2` has collision `6650`, HitNeed `1`, demand `6651`;
- full owner shore demand `19953`, reachable auxiliary sources `19925`, defect `28`.

The source histogram is `5775,5775,5775,2600` for owner masks `1,2,4,7`; reason counts are `17325` same-first and `2600` row-companion. The rebuilt source-record SHA256 is `359dfa71a302e007812d0ea9945dd355fabc4c3b0ae50f10ef7acaf741cd84d9`.

The auxiliary result is a FAIL only for the `Gamma/ActiveScoped*` relation. It is not a production FullBank FAIL.

## Implemented finite LP contract

`FullBankRelaxedCoverCert` is defined at `Ell5FullBankInterface.lean:27-40`. For finite sets `S,F,O,J,K`, separators `sep`, cut boundaries `dB`, incidence `inc`, and capacities `kap`, its exact variables and constraints are:

```text
lambda_k >= 0
q_cj >= 0

r in S:  1 <= sum[k in K, r in sep(k)] lambda_k
c in F:  sum[k in K, c in dB(k)] lambda_k <= 1
c in O:  sum[k in K, c in dB(k)] lambda_k <= sum[j in J] q_cj
j in J:  sum[c in O] q_cj <= kap(j)
q_cj > 0 => inc(c,j)
```

The graph specialization fixes `sep(k)=deltaM(G,cut,Ufam(k))` and `dB(k)=deltaB(G,cut,Ufam(k))` (`Ell5FullBankInterface.lean:62-71`). The Hall consumer additionally needs `Disjoint F O`, `dB(k) subset F union O`, and `card(sep(k)) <= card(dB(k))` (`Ell5FullBankHall.lean:50-66`). The wall adapter transports exactly the same incidence and capacities (`Ell5FullBankWallAdapter.lean:27-49`).

## Exact hub-shore singleton shells

These are the only finite graph-derived LP shells emitted by this lane. They instantiate the compiled half-singleton constructor with `K=C`, `U_x={x}`, and `lambda_x=1/2`. They state required capacities; they do not assert those capacities are available in production.

For the literal owner shore `C={0,1,2}`:

- `S` is empty;
- `F={(0,1),(0,2)}`;
- `O=blue minus F` has `7037` ports: `55` boundary load-`1/2` and `6982` load-0;
- exact external load and Door capacity requirement are `55/2`.

Thus the literal graph-edge LP has no atom corresponding to the 19,953 auxiliary obligations. This is the first missing adapter made quantitative.

The active-component closure of the hub shore is

```text
C={0,1,2,55,2762,2763,2764,2765,2766,2771,2772,2773,2774,
   2780,2781,2782,2783,2929,2930}.
```

Its exact sets are:

- `S={(2762,2766)}`;
- `F={(0,1),(0,2),(2762,2763),(2763,2764),(2764,2765),(2765,2766),`
  `(2771,2772),(2772,2773),(2773,2774),(2780,2781),(2781,2782),(2782,2783)}`;
- `O=blue minus F` has `7027` ports: `18` internal load-1, `1441` boundary load-`1/2`, and `5568` load-0;
- exact total external load is `18 + 1441/2 = 1477/2`.

The separator and boundary lists for every singleton cut, all `O` ports, all nonzero routing arcs, and every required sink capacity are serialized in `RESULT.json`.

## Source classes, incrementally and without overlap

For the 19-vertex shell, the graph-derived required routing is partitioned before capacity is summed:

| Class | New ports after earlier classes | Exact nonzero incidence and load | Exact required capacity | Production available capacity |
|---|---:|---|---:|---|
| `door` | 1441 boundary ports | `e -> door(e)`, `q=1/2` | `1441/2` total, `1/2` each | UNDEFINED |
| `vertexSlack` | 18 internal ports | `e -> vertex(x)` for both endpoints, `q=1/2` per arc | `18` total | UNDEFINED |
| `c5Base` | UNDEFINED | no compiled R29 port enumeration/token/incidence | UNDEFINED | UNDEFINED |
| `prune` | UNDEFINED | no compiled graph transition/token/incidence | UNDEFINED | UNDEFINED |

The exact vertexSlack requirements are:

```text
0:1/2, 1:1/2, 2:1/2, 55:2,
2762:1/2, 2763:1, 2764:3/2, 2765:1, 2766:1/2,
2771:1, 2772:1, 2773:1, 2774:1,
2780:1, 2781:1, 2782:1, 2783:1, 2929:1, 2930:1.
```

The Door and vertex port sets are disjoint, so their required totals do not double-spend a port. No `c5Base` or `prune` amount is added: absence of a provider is not zero capacity.

The mixed routing formula is implemented in `Ell5SingletonVertexSlack.lean:481-650`, and the graph-facing internal-endpoint/Boundary-Door constructor is at `Ell5InternalEndpointSlackFullBank.lean:72-100`. Both take legality and capacity inequalities as hypotheses.

## Why all four production classes remain uninstantiated

- `door`, `vertexSlack`, `c5Base`, and `prune` are only enumerated as `CapKind` at `Gamma/FullBankToLengthSurplusCharge.lean:25-30`. A concrete package would need all token records and `capQ` values (`:69-82`) plus every `Checked` field (`:177-227`). No R29 package exists.
- Hall-scale token capacity is `capQ/25` (`Gamma/FullBankPortSinks.lean:41-49`), but there is no token table to evaluate it.
- Typed own-Door checking needs supplied `portEdge`, `token`, and `doorOf` data (`Gamma/TypedFullBankSources.lean:91-112`) and a separately supplied wall-sink adapter (`Gamma/TypedOwnDoorHalfLayer.lean:34-42`).
- The C5-base checker validates one literal terminal and explicitly leaves permanently-Free ownership and global matching separate (`Gamma/CheckedC5BaseTransfer.lean:13-15,24-43`). It supplies no sink token, capacity, or port incidence.
- Row-companion checking likewise leaves source slots and global matching separate (`Gamma/CheckedRowCompanionBaseTransfer.lean:6-13,107-123`).
- `prune` has an enum/source-key constructor but no compiled graph-derived transition, slot transport, capacity, or incidence provider (`Gamma/TypedFullBankSources.lean:24-41`).
- The aggregate ledger cannot imply incidence; this logical separation is machine-proved by `AggregateLedgerNoIncidenceCounterexample.lean:6-16,152-157`.

`RESULT.json` records 12 missing provider fields with required types, reasons, and line references. Until those fields are supplied, comparing defect `28` with `1477/2` (or any other singleton load) is ill-typed: they index different finite objects.

## Exact check outcome

The two singleton shells pass every constraint after assigning synthetic capacities equal to their required routed flow. This verifies the finite arithmetic and constructor shape only. The complete production LP was not solved because its `Atom/S`, `J`, `kap`, `inc`, and `q` data are undefined.

Accordingly:

- production absorption of 28: **UNDEFINED**;
- production FullBank Hall defect after all source classes: **UNDEFINED**;
- auxiliary ActiveScoped Hall defect: **verified 28**.

## Replay commands

From `tmp/fanout/r29_fullbank_gate/lane08_fullbank_lp`:

```powershell
python verify.py
python -m py_compile verify.py
python -c "import json; d=json.load(open('RESULT.json')); assert d['decision']=='UNDEFINED'; print(d['exact_assertions'])"
Get-FileHash -Algorithm SHA256 verify.py,RESULT.json,REPORT.md,HASHES.json
```

The successful verifier summary was:

```json
{"decision":"UNDEFINED","defect":28,"demand":19953,"hub_component_singleton_external_load":{"denominator":2,"numerator":1477},"hub_component_vertices":19,"missing_provider_fields":12,"reach":19925}
```

## Hashes

Critical authoritative identities:

- reconstructed cage: `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`;
- D09 encoded all-anchor tuple: `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901`;
- raw 1,383-row list encoding used here: `ab37d295364a110795388fbb8bb695f5ae849514348ff84bc29edf8ca57493f9`;
- authoritative cut certificate: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`;
- lead constructor: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`;
- `Ell5FullBankInterface.lean`: `8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104`;
- `Gamma/FullBankPortSinks.lean`: `ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6`;
- `Gamma/FullBankToLengthSurplusCharge.lean`: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`.

All 29 audited input/source hashes are embedded in `RESULT.json` under `source_sha256`. Delivered artifact hashes are in `HASHES.json`.
