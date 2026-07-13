# R29 FullBank semantic/API audit

## Verdict

The exact split verdict is:

- **Operational CheckedTransfer semantics absorb the 28.**  Adding the
  compiled corrected common-blue terminal predicate gives 216 fresh
  unreserved FreeHalf keys.  An explicit 28-key subset extends the old flow;
  exact max flow is `19953`, and all eight owner shores pass.
- **Production Lean has not connected that absorber to FullBank.**  The
  `CheckedTransferMatching` consumer/provider and terminal-to-token adapter do
  not exist in the Lean tree.  Thus absorption is exact semantic/computational
  evidence, not yet a kernel theorem constructing a checked FullBank package.
- **R29 is not a real FullBank falsifier.**  It falsifies the narrower
  `ActiveScoped.Available` relation and, under strict component equalities, the
  auxiliary four-pattern relation.  It does not exhibit a deficient shore
  under the corrected common-blue transfer relation.

1. `ActiveScopedMinimumExchange.Available` is exactly an injective relation
   from active collision/HitNeed obligations to `FreeHalf` triples.  Its only
   positive eligibility is same-first or row-companion; its only exclusion is
   the active half-zero reservation
   (`Gamma/ActiveScopedMinimumExchange.lean:102-147,154-158`).  R29 exactly
   falsifies this auxiliary relation: demand `19953`, reach `19925`, defect
   `28`.
2. No declaration named `CheckedTransferMatching`,
   `ActiveComponentFullBankCert`,
   `checkedTransferMatching_to_activeFullBank`, or
   `checkedBaseCorridorPruneMatching_to_activeFullBank` exists in the
   production Lean tree.  Those names occur only in R19-R23 design prose.
3. The compiled local FullBank primal, `FullBankRelaxedCoverCert`, has genuine
   rational routing fields `q`, `hroute`, `hcap`, and `hqinc`, but its
   `inc`/`kap` data are caller inputs
   (`Ell5FullBankInterface.lean:23-40`).  The compiled global package has the
   four cap kinds and aggregate spend bookkeeping, but no edge/port incidence
   or local `q` flow (`Gamma/FullBankToLengthSurplusCharge.lean:25-45,67-82,
   131-143,174-227`).
4. There is no compiled adapter from a checked local
   `FullBankRelaxedCoverCert` to a checked `FullBankGlobalPackage`.  The source
   search `rg -n "FullBankRelaxedCoverCert" .../Gamma` returns no match.
   `FullBankPortSinks` explicitly records that legal edge-to-token incidence
   is absent and therefore its finite sinks do not assert Hall
   (`Gamma/FullBankPortSinks.lean:80-81`).

Consequently, the current kernel surface has no R29
`CheckedTransferMatching`/FullBank instance on which absorption can yet be
stated as a theorem.  Calling the absent provider's capacity zero is also
incorrect: absence of an instantiation is not graph-theoretic absence.  The
exact corrected-terminal flow does, however, rule out R29 as the decisive
  transfer-aware falsifier requested by the goal.

## Fanout reconciliation

Nine disjoint read-only audits were launched and all child processes are now
closed.  Children 02-05 and 07-09 exited 0 with reports.  Child 01 produced a
complete core-transfer report before a model-capacity exit (`exit 1`).  Child
06 hit a revoked OAuth token plus a Windows patch-sandbox failure and produced
no usable report (`exit -1`); its c5Base/prune scope was independently covered
by child 03, child 07, child 09, the exact c5Base executable, and the lead
audit.  The reconciled findings are reflected below; child reports remain in
`tmp/fanout/r29_fullbank_semantics/child_01` through `child_09`.

The reports agree on the production boundary: `CheckedTransferMatching` and
`ActiveComponentFullBankCert` are absent; ActiveScoped has only same-first and
row-companion; local and global FullBank APIs are disconnected; typed
incidence providers are missing.  The only numerical disagreement concerned
outsideAttachment, traced to the written component-equality condition being
absent from loose Python gates.  The corrected common-blue c5Base audit is
independent of that ambiguity and supplies the exact 28-key repair.

## ActiveScoped relation

The source universe comes from `CanonicalCollisionHall.FreeHalf`: an ordered
pair `(sourceX,sourceY)`, a bit `half : Fin 2`, distinct coordinates, and
`pairCount omega sourceX sourceY = 0`
(`Gamma/MinimumDemandCollisionHall.lean:64-73`).

The exact demand is

```lean
ActiveCollisionHalf G c omega + ActiveHitNeed G c omega
```

where `ActiveCollisionHalf` filters collision halves by `ActiveOwner`, and
`ActiveHitNeed` has `hitNeedUnits = activeDegree - (G.n - selectedLoad)`
(`Gamma/ActiveScopedMinimumExchange.lean:41-54,66-106`).  `HitNeed` is a
demand class.  It is not a `vertexSlack` bank token.

The exact relation is:

```lean
EligibleOwner G c owner s :=
  s.sourceX = owner OR
  (0 < pairCount omega owner s.sourceX AND
   0 < pairCount omega owner s.sourceY AND
   0 <= sigma G c [s.sourceX, s.sourceY])

ScopedReserved G c omega s :=
  s.half.1 = 0 AND activeGraph.Adj s.sourceX s.sourceY AND
  ActiveOwner G c omega s.sourceX

Available G c d s :=
  EligibleOwner G c (demandOwner d) s AND NOT ScopedReserved G c omega s
```

(`Gamma/ActiveScopedMinimumExchange.lean:125-147`).  `Matching` is an
injective `Demand -> FreeHalf` satisfying `Available`, and
`matching_nonempty_iff_hall` is the exact finite Hall equivalence
(`:154-179`).

Thus `Available` directly contains only:

- same-first (`s.sourceX = owner`);
- row-companion co-occurrence of both source coordinates plus nonnegative
  two-vertex switch loss;
- active half-zero reservation.

It contains no `CapKind`, token, rational capacity, component spend,
edge-to-token incidence, Door, external component, trace, rank, or slot
transport field.

## Transfer pattern audit

### Same-first

Compiled and directly present in `Available` at
`ActiveScopedMinimumExchange.lean:136-142`.  The older collision-only API calls
the same predicate `SameOwner` (`MinimumDemandCollisionHall.lean:82-87`).

### Row-companion

Compiled and directly present in `Available` at
`ActiveScopedMinimumExchange.lean:136-142`; the collision-only form is
`RowCompanion` (`MinimumDemandCollisionHall.lean:89-103`).  A separate literal
checker, `CheckedRowCompanionBaseTerminal`, validates selected row witnesses,
Free pair status, nonnegative switch loss, and active owner
(`Gamma/CheckedRowCompanionBaseTransfer.lean:57-123`).  Its theorems only
convert the Boolean check to that proof object and prove the two witness rows
distinct (`:125-179`); no theorem consumes it into a matching or FullBank
certificate.

### Common-bad/common-blue

There is no `commonBad` constructor in `Available`.  The compiled
`CheckedC5BaseTransfer.TerminalData.Valid` instead checks the corrected R19
**common-blue** terminal:

```lean
blueb G c sourceX owner = true AND
blueb G c sourceY owner = true AND
dM G c [sourceX,sourceY] + 2 <= dB G c [sourceX,sourceY]
```

(`Gamma/CheckedC5BaseTransfer.lean:24-56`).  It proves adjusted surplus
nonnegative and `2 <= sigma` (`:58-75`).  The file explicitly says permanent
Free ownership and global matching are separate layers (`:13-15`).  No
compiled theorem maps this terminal to `CapSource.c5Base`, a ledger token,
`Available`, or `FullBankRelaxedCoverCert`.

Independent exact enumeration found 1,412 valid ordered terminals: 4 for
owner 0 and 704 for each of owners 1 and 2.  After deduplication against the
old relation they add 216 fresh unreserved half keys.  The resulting
owner-mask capacities are `{1:5775, 2:5879, 3:4, 4:5879, 5:4, 7:2600}`.
All eight shore deficiencies are nonpositive, and exact max flow is `19953`.

One explicit 28-key absorber for owner 2 is
`(x,2930,h)`, `x=29..42`, `h=0,1`; every key has switch surplus 3 and is
unreserved.  This settles the operational matching question.  It remains a
concrete adapter target, rather than a production FullBank theorem, because no
compiled consumer maps these terminals to `CapSource.c5Base`, global unique
tokens/incidence, or a checked package.

### Outside attachment

No production Lean declaration/checker exists.  R23 prose requires outside
vertices, attachment witnesses, nonnegative switch loss, and additionally
`comp(a)=comp(owner)=comp(b)`
(`writeup/WALL_ATTACK_R23_GPTPRO56.md:7-15,29-34`).  The archived executable
`_claude_r23_outside_attachment_gate.py:91-133` omits those component
equalities.  This discrepancy is material on R29:

- loose attachment-only implementation: 676 eligible singleton outside
  vertices per hub, 912600 new half slots, max flow 19953;
- strict selected-component implementation: zero eligible outside vertices,
  so the auxiliary demand remains deficient by 28.

Neither implementation is production Lean.  The loose PASS cannot establish
the named R23 relation with its written component equalities; the strict FAIL
is a falsifier only to that auxiliary four-pattern FreeHalf relation, not to
FullBank.

### Prune

Compiled only as the tag `CapKind.prune` and typed key
`CapSource.prune PruneKey`
(`Gamma/FullBankToLengthSurplusCharge.lean:25-31`;
`Gamma/TypedFullBankSources.lean:23-41`).  There is no compiled prune trace,
rank decrease, injective slot transport, graph constructor, incidence, or
capacity theorem.  It is absent from `Available`.

## FullBank source and sink classes

### Local primal

`FullBankRelaxedCoverCert S F O J K sep dB inc kap` routes each off-support
edge `c : O` to sinks `j : J` using rational `q c j`.  Positive flow must
satisfy `inc c j`, and total flow into `j` is bounded by `kap j`
(`Ell5FullBankInterface.lean:27-40`).  It implies banked cut domination and
excludes the corresponding exact rational dual (`:42-60`).  This is the
semantic FullBank object, but no existence/provider theorem is compiled.

`Ell5FullBankHall.hall_bound_of_fullBank_cert` derives the scaled Hall/bank
inequality from a certificate plus support decomposition and per-cut
cardinality (`Ell5FullBankHall.lean:50-66`).

### Active-component flow

`Ell5ActiveComponentHall` uses sources
`E0 O D = {e // e in O and e notin D}` and vertex sinks
`V0 C = {x // x in C}`.  Its demand is the rational active block load, its
incidence is caller-supplied endpoint legality, and its Hall condition sums
sink capacities (`Ell5ActiveComponentHall.lean:14-54`).  Given that Hall
hypothesis plus own-Door hypotheses for `D`, it constructs a
`FullBankRelaxedCoverCert` (`:111-133,146-212`).

`Ell5ActiveComponentBankHall` replaces vertex sinks by a generic bank pool
`JT`, then adjoins edge-indexed Door sinks as a disjoint sum.  It still assumes
the non-Door Hall condition and separate Door incidence/capacity
(`Ell5ActiveComponentBankHall.lean:23-64,107-133`).  There is no compiled
`ActiveComponentFullBankCert` type.

### Endpoint reserve

`EndpointReserveHall` uses sink type `V + JT`: left sinks have vertex slack;
right sinks are reserve tokens with positive endpoint mass
(`EndpointReserveHall.lean:27-54`).  `endpointReserveHallOn` assumes
nonnegative assignment mass, per-token no-double-spend, pointwise budget, and
explicit endpoint/token support sets (`:140-154`).

`CollisionTokenAssignment.Assignment` is the provider seam: it stores
`eta`, nonnegativity, token capacity, need coverage, and endpoint legality
(`CollisionTokenAssignment.lean:25-35`).  `hall_of_assignment` only consumes
such an assignment (`:46-75`); no graph-derived assignment exists for R29.

`ResidualSourceTokenization.Data` is an intermediate abstract micro-matching:

```lean
((Debit * Fin 2) + (Slot * Fin 25)) embeds into (Source * Fin 2)
```

with component preservation and a positive rational unit
(`ResidualSourceTokenization.lean:27-42`).  It turns each `Slot` into one token
of capacity `25 * unit`, legal exactly at edges incident with its owner, and
constructs a `CollisionTokenAssignment.Assignment` (`:59-77,99-116`).  No
theorem builds this `Data` from ActiveScoped `Matching` or the corrected c5
terminals; it is another explicit provider seam.

### Door

`CapSource.door edge`, `vertexSlack vertex`, `c5Base base`, and `prune key` are
the four typed source constructors (`Gamma/TypedFullBankSources.lean:23-41`).
`OwnEdgeDoorSourceData.Checked` requires injective port-edge keys, exact Door
source equality, and raw `capQ >= 25` (`:91-128`).  It proves own-Door
legality/injectivity and Hall cap at least one (`:130-164`).

`DoorWallAdapter` is still an explicit hypothesis carrying an injective token
embedding, legal-incidence interpretation, and cap equality
(`Gamma/TypedOwnDoorHalfLayer.lean:34-42`).  With it,
`halfLayerRouted_of_checkedEdgeDoorSources` constructs the wall routing
(`:59-85`).  No R29 `OwnEdgeDoorSourceData.Checked`/adapter instance is in
production.

The all-Door fast path similarly assumes `ownDoor_inc` and unit
`ownDoor_capacity` for every off-support cut edge
(`EndpointHalfDoorComplete.lean:19-32`).  Its constructor is valid once those
hypotheses are supplied (`:65-99`), but it does not derive bank ownership or
connect to `FullBankGlobalPackage` (`:34-39`).  Therefore an external script
that declares every off-support edge to own a unit Door constructs a
conditional local certificate, not the real graph-derived provider demanded
by the goal.

### Vertex slack

The mixed singleton constructor sends boundary edges to own Doors and internal
off-support edges to endpoint sinks.  It assumes internal endpoint capacity,
endpoint legality, Door legality, and Door capacity
(`Ell5InternalEndpointSlackFullBank.lean:72-100`).  Those assumptions are not
fields of `Available` and are not derived for R29.

### Global package

`FullBankGlobalPackage` stores component/local ownership and an aggregate
ledger (`Gamma/FullBankToLengthSurplusCharge.lean:124-143`).  `Checked` proves
kind-spend identities, nonnegative spend, no double spend, no cross-component
spend, token uniqueness, component reserve identities, and global residual
accounting (`:174-227`).  It does not store edge/port incidence or `q`.

`fullBankGlobalPackage_sound` proves the length-surplus target and
`gammaUpper_from_fullBankGlobalPackage` proves `Gamma <= N^2`
(`:286-315`).  `FullBankChargeCertProvider` only repackages an already checked
package into the typed charge API
(`Gamma/FullBankChargeCertProvider.lean:51-93`).  No theorem constructs the
checked package from graph data.

The exact countermodel
`checkedAggregatePackage_and_noHalfLayerRouting` proves that a checked
aggregate package can coexist with failure of half-layer routing
(`AggregateLedgerNoIncidenceCounterexample.lean:145-157`).  Therefore the
missing incidence adapter cannot be inferred from current package fields.

## Executable map

Current exact scripts relevant to R29 are:

| Script | Executable semantics | Status |
|---|---|---|
| `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py` | ActiveScoped same-first + row-companion FreeHalf relation | canonical defect-28 replay |
| `tmp/fanout/r29_fullbank/B_fourpattern/worker_5/checker.py` | strict written R23 component equalities | pattern 4 adds 0; auxiliary defect 28 |
| `tmp/fanout/r29_fullbank_gate/verify.py` | loose R23 attachment rule without component equality | reports 912600 added slots; not the written strict predicate |
| `tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py` | exact corrected common-blue terminal enumeration | 216 fresh keys; emits a 28-key repaired injection |
| `tmp/fanout/r29_fullbank/E_source_search/lead/verify_c5base_absorber_independent.py` | independent exact audit of the 28 terminal records and all shores | PASS; repaired full-shore margin 0 |
| `problems/23/writeup/_claude_r20_staged_matching_gate.py` | staged sameFirst/commonBad/rowCompanion fixtures | executable fixture gate, not Lean provider |
| `problems/23/writeup/_claude_r23_outside_attachment_gate.py` | loose outside-attachment on 89/311 | executable fixture gate, omits written component equality |
| `tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py` | denominator-scaled integer flow over supplied typed tokens/arcs | generic verifier; no R29 provider |
| `Gamma/CheckedC5BaseTransfer.lean` | kernel Boolean check of one common-blue terminal | compiled validator, no consumer adapter |
| `Gamma/CheckedRowCompanionBaseTransfer.lean` | kernel Boolean check of one row-companion terminal | compiled validator, no consumer adapter |
| `Gamma/TypedFullBankSources.lean` | kernel `decide` checker for supplied own-Door arrays | compiled validator, not extractor |
| `ResidualSourceTokenization.lean` | proof constructor from a supplied injective micro-source embedding | compiled adapter, no graph-derived `Data` |

No exact executable emits an R29 checked `FullBankGlobalPackage`, a local
certificate-to-global-package bridge, or a compiled `CheckedTransferMatching`.

## Exact decision table

| Claim | Decision |
|---|---|
| R29 falsifies `ActiveScopedMinimumExchange.Available` Hall | **Yes**, defect 28. |
| R29 falsifies strict written R23 four-pattern FreeHalf relation | **Yes**, according to the exact strict checker; still auxiliary. |
| Loose outside-attachment absorbs 28 | **Yes computationally**, but it omits a written predicate and is not compiled. |
| Common-blue c5 terminal supplies 28 candidate fresh keys | **Yes computationally**, but no compiled matching/token adapter consumes them. |
| Corrected operational transfer relation absorbs 28 | **Yes**: 216 fresh common-blue keys, explicit 28-key extension, exact flow 19953. |
| Production `CheckedTransferMatching` theorem absorbs 28 | **Not yet expressible**: no such production declaration/instance. |
| Production real FullBank is falsified by R29 | **No**: the corrected transfer relation has no deficient shore; the full provider is also absent. |
| Production real FullBank theorem absorbs 28 | **Not yet compiled**: local/global FullBank surfaces are not instantiated or connected. |

The next load-bearing implementation is not another source count.  It is a
single graph-derived adapter that fixes the exact transfer relation, consumes
checked terminals into typed unique tokens/incidence, and constructs either a
local `FullBankRelaxedCoverCert` plus a global-package bridge or directly a
checked `FullBankGlobalPackage` carrying equivalent incidence semantics.

## Verification commands

```powershell
rg -n "CheckedTransferMatching|ActiveComponentFullBankCert|checkedTransferMatching_to_activeFullBank|checkedBaseCorridorPruneMatching_to_activeFullBank" problems/23/lean/Erdos23Delta0 --glob '*.lean'
rg -n "FullBankRelaxedCoverCert" problems/23/lean/Erdos23Delta0/Gamma --glob '*.lean'
python -B tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
python -B tmp/fanout/r29_fullbank/B_fourpattern/worker_5/checker.py
python -B tmp/fanout/r29_fullbank_gate/verify.py
python -B tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py tmp/fanout/r29_fullbank/C_fullbank/d6_flow/input.json
```

All reported arithmetic is integer or exact rational.  No float,
`native_decide`, `sorry`, or invented theorem is used as evidence.

The load-bearing terminal module was independently rebuilt with production
root/cache settings: rc `0`; printed axioms were exactly subsets
`[propext, Quot.sound]`; the forbidden-token scan had zero hits.  Audit olean
SHA-256: `b2a98b0eecb673bd40e8979397a84875e3afa2bd57e3a640dfa9b37faa5a9d01`.
