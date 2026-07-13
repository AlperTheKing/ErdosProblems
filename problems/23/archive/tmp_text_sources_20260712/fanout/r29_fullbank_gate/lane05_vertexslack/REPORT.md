# R29 FullBank vertexSlack audit

## Verdict

**UNDEFINED** for the decisive production question.

The compiled code does not provide a graph/row-to-`vertexSlack` constructor for R29. It therefore does not define the R29 token set, `kap`, ledger `capQ`, component assignment, legal obligation/port incidence, or a no-double-spend relation shared with the `FreeHalf` transfer sources. Consequently neither of these claims is verified:

- PASS: the complete implemented FullBank relation absorbs the 28-unit hub-shore defect;
- FAIL: a Hall/LP defect survives after every implemented production source class.

There is an exact conditional result: under the ordinary residual formula `s(v)=max(0,N-T(v))`, with `T(v)=5` times row occurrence, the three hub owners each have zero `vertexSlack`. Hence owner-local `vertexSlack` adds exactly `0` to the auxiliary 19,925 `FreeHalf` sources and leaves defect `28`. This is not a FullBank instance because the required incidence and capacity bridges are absent.

## Exact reconstruction and result

`replay_vertexslack_audit.py` imports `r29_lead_gate.py.build`, replaces all 676 selector rows by their recorded deterministic anchor rows, and independently rebuilds row occurrences, pair counts, support, active components, collision demand, HitNeed demand, and both current `FreeHalf` eligibility rules. It checks every selected row against its bad atom and blue path.

Exact reconstructed values:

| quantity | value |
|---|---:|
| vertices `N` | 2,943 |
| blue / bad / total edges | 7,039 / 1,383 / 8,422 |
| rows / anchor replacements | 1,383 / 676 |
| selected / active vertices | 2,127 / 19 |
| active / demanded-active edges | 1,370 / 18 |
| hub demand per owner | 6,651 |
| hub-shore demand | 19,953 |
| distinct reachable `FreeHalf` sources | 19,925 |
| defect | 28 |

The source histogram is recomputed as owner masks `1:5775`, `2:5775`, `4:5775`, `7:2600`; reason masks are same-first `1:17325` and row-companion `2:2600`.

For each owner `v in {0,1,2}`:

- row occurrence is `676`;
- `T(v)=5*676=3380`;
- `N-T(v)=2943-3380=-437`;
- `s(v)=max(0,-437)=0`;
- demand is `6650` collision units plus `1` HitNeed unit.

Thus the conditional owner-local incremental capacity is `min(28,0+0+0)=0`, with residual defect `28`.

The same formula gives total slack `43,785` over all 19 active vertices and `8,628,427` over all graph vertices. Neither total is reachable capacity for the hub shore: using a non-owner vertex sink requires precisely the missing legal incidence/flow adapter. These totals are reported only as nonbinding envelopes and are not added to `FreeHalf` reach.

## Implemented `vertexSlack` contract

The local singleton certificate is exact but parametrized:

- `halfWeight=1/2`, and `endpointQ(e,x)=1/2` exactly when `x` is an endpoint of `e`: `Ell5SingletonVertexSlack.lean:163-167`.
- The load at a vertex equals half the number of incident edges in `O`: `Ell5SingletonVertexSlack.lean:219-222`.
- The canonical vertex specialization takes arbitrary `inc` and `kap`; callers must prove endpoint legality and `(# incident O edges)/2 <= kap(x)`: `Ell5SingletonVertexSlack.lean:381-420`.
- In the mixed constructor, edges in explicit `D` use their own Door, while edges in `O\D` use endpoint slack: `Ell5SingletonVertexSlack.lean:481-500,512-534,619-650`.
- The internal-endpoint bridge fixes `D` as the boundary filter, but still requires caller-supplied `slack`, `kap`, endpoint legality, Door legality, and Door capacity: `Ell5InternalEndpointSlackFullBank.lean:56-104`.
- Fractional endpoint flow is also caller-supplied and capacity constrained, not extracted from graph data: `Ell5SingletonEndpointFlow.lean:30-73`.

The global layer uses a different scaling:

- local relaxed certificates use rational `kap` directly: `Ell5FullBankInterface.lean:23-40`;
- their Hall consequence multiplies total `kap` by 25: `Ell5FullBankHall.lean:50-66`;
- global ledger sinks define Hall capacity as `capQ/25`: `Gamma/FullBankPortSinks.lean:41-49`.

No compiled theorem identifies local `kap(vertexSlack(v))` with global `capQ/25`. The conditional `max(0,N-T)` arithmetic is implemented as residual arithmetic in `Gamma/ActiveScopedMinimumExchange.lean:75-85` and `CollisionReserveCounting.lean:89-107`, but neither file constructs a FullBank `vertexSlack` sink.

## Constructor and incidence audit

Repository-wide tracked-source searches found zero non-definition occurrences of both:

- `certificate_of_singletonCore_vertexSlack`;
- `certificate_of_internalEndpointSlack_boundaryDoors`.

`CapSource.vertexSlack(vertex)` exists as a typed label at `Gamma/TypedFullBankSources.lean:24-29`, and typed tokens exist at lines 61-89. The only concrete incidence checker in that module is for own-edge Doors, lines 91-166. It is not a graph-to-`vertexSlack` extractor and is not integrated into `FullBankGlobalPackage`.

`FullBankGlobalPackage` stores aggregate component/local ownership and an untyped token/spend matrix (`Gamma/FullBankToLengthSurplusCharge.lean:131-143,177-209`), but no port-to-token legality relation. The production guardrail says this explicitly at `Gamma/FullBankPortSinks.lean:80-81`. `AggregateLedgerNoIncidenceCounterexample.lean:6-16` proves that aggregate checked fields cannot supply routing.

The missing API/hypotheses are:

1. an R29/core extractor producing `S,F,O,D,C` from graph, cut, and row data;
2. a compiled definition/theorem fixing `slack(v)` and `kap(vertexSlack(v))`;
3. typed `vertexSlack` tokens inserted into `FullBankGlobalPackage` with the `/25` scaling proved;
4. legal port or obligation-to-vertex incidence for those tokens;
5. one no-double-spend relation joining transfer `FreeHalf`, Door, and `vertexSlack` sources.

## Overlap audit

Door and `vertexSlack` load are disjoint only conditionally on an explicit `D`: the mixed constructor routes `D` to own Doors and `O\D` to vertices. No R29 `D` extractor exists, so the production Door overlap cannot be instantiated.

Transfer `FreeHalf` sources and `vertexSlack` tokens have no compiled common source universe or incidence relation. Their capacities therefore cannot be summed. The only overlap-safe incremental claim available here is zero, because all three conditional owner slacks are zero.

## Replay commands

From `E:\Projects\ErdosProblems`:

```powershell
python tmp\fanout\r29_fullbank_gate\lane05_vertexslack\replay_vertexslack_audit.py
python -m py_compile tmp\fanout\r29_fullbank_gate\lane05_vertexslack\replay_vertexslack_audit.py
Get-FileHash -Algorithm SHA256 tmp\fanout\r29_fullbank_gate\lane05_vertexslack\replay_vertexslack_audit.py,tmp\fanout\r29_fullbank_gate\lane05_vertexslack\result.json
```

Expected first-command summary:

```json
{"active_component_slack_nonbinding":"43785","conditional_increment":"0","defect":28,"demand":19953,"owner_slack":"0","reach":19925,"verdict":"UNDEFINED"}
```

## SHA256

- `replay_vertexslack_audit.py`: `d1d1a27163cfd7e4092ea4fdd3ac5665c81dfed9fc18cd87d691c9677ba86191`
- `result.json`: `d8b376627f99cf4b448aab058d57bfb1041c3b89cd46b616989ac0cb53e679cf`
- imported lead constructor: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- reference cut certificate: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`
- reconstructed canonical cage payload: `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`
- `COMMON.md`: `ce98df7cf9d517cb1b5b94cf7a8c55b862834446f3c7fafdA8e4d9968b69506a` (case-insensitive hex)
- R29 writeup: `5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42`

The complete SHA256 map for all audited Lean modules is in `result.json`.