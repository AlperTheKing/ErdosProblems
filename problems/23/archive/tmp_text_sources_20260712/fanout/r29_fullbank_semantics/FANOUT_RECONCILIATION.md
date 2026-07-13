# R29 FullBank semantic fanout reconciliation

Snapshot: 2026-07-11T15:16:24Z. This file reconciles nine disjoint child audits with the already-emitted `SEMANTICS.md` and `source_class_map.json`. It does not modify either deliverable.

## Exact verdict

1. The R29 all-anchor tuple has an exact Hall defect of `19953 - 19925 = 28` for `Erdos23Delta0.Gamma.ActiveScopedMinimumExchange.Available`.
2. That relation contains exactly same-first and row-companion eligibility, followed by `not ScopedReserved` (`ActiveScopedMinimumExchange.lean:136-147`). It contains no `commonBad`, outside-attachment, common-blue C5 terminal, Door, prune, or rational bank-token incidence.
3. Extending this FreeHalf relation by the compiled predicate `CheckedC5BaseTransfer.TerminalData.Valid` is exactly feasible on R29: `216` fresh keys exist, an explicit `28`-key injection repairs the full shore, and the independent verifier returns margin `0`.
4. This proves transfer-layer absorption only. No compiled `CheckedTransferMatching` declaration, terminal-to-typed-token adapter, graph-derived R29 `FullBankRelaxedCoverCert`, or graph-derived checked `FullBankGlobalPackage` exists.
5. Therefore the production FullBank question is **not decidable from the current APIs**: R29 is not a demonstrated FullBank falsifier, and production FullBank absorption is not yet a theorem. Any Boolean claim that production FullBank is “not falsified” must be read only as “the operational corrected transfer relation passes,” not as a constructed FullBank package.

## Production chains found

- Active-scoped chain: `Demand -> FreeHalf -> Available -> Matching`, with `Nonempty Matching <-> HallCondition` (`ActiveScopedMinimumExchange.lean:102-179`). This is the relation falsified by 28.
- Local FullBank chain: caller-supplied `inc`/`kap` plus `FullBankRelaxedCoverCert(lam,q,...)` imply banked cut domination and scaled Hall (`Ell5FullBankInterface.lean:27-60`; `Ell5FullBankHall.lean:50-66`). Existence is not supplied.
- Active-component constructors: caller-supplied Hall, incidence, and capacity hypotheses construct local certificates (`Ell5ActiveComponentHall.lean:14-54,111-133`; `Ell5ActiveComponentBankHall.lean:23-64,107-133`).
- Typed source chain: `CapSource = door | vertexSlack | c5Base | prune`; own-Door checking is compiled, but `DoorWallAdapter` remains caller-supplied (`Gamma/TypedFullBankSources.lean:24-164`; `Gamma/TypedOwnDoorHalfLayer.lean:35-85`).
- Global chain: a supplied `FullBankGlobalPackage.Checked` implies the length-surplus and Gamma bounds (`Gamma/FullBankToLengthSurplusCharge.lean:177-315`). The package stores aggregate spend, not local edge-to-token incidence.
- Separation theorem: a checked aggregate package can coexist with absence of half-layer routing (`AggregateLedgerNoIncidenceCounterexample.lean:145-157`). Thus the missing local/global bridge is logically substantive.

## Source-class consensus

| Class | Compiled status | In `ActiveScoped.Available` |
|---|---|---|
| sameFirst | direct predicate `sourceX = owner` | yes |
| rowCompanion | direct co-occurrence/co-occurrence/sigma predicate | yes |
| commonBad | Python/archive pattern; no named Lean constructor | no |
| common-blue C5 terminal | executable Lean checker | no; exact R29 extension repairs 28 |
| outsideAttachment | Python/archive only | no |
| Door | typed source and conditional local constructors | no |
| vertexSlack | conditional local sink; numerically pre-netted in HitNeed | no source/sink in `Available` |
| c5Base | typed tag plus standalone common-blue checker | no token/matching adapter |
| prune | typed tag and abstract ledger identities | no graph-derived provider |
| generic non-Door bank | abstract `JT`, `inc`, `kap` | no |
| endpoint reserve token | conditional consumer/provider record | no graph-derived assignment |
| component reserve/superadditivity slack | non-spendable aggregate ledger fields | no |

## Executable evidence

- Baseline relation: `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py::rebuild_scope,owner_sources`; exact demand `19953`, reach `19925`, defect `28`.
- Corrected terminal extension: `tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py`; exact output: `newC5BaseKeys=216`, `absorberHalfSlots=28`, `repairedFullShoreMargin=0`.
- Independent verifier: `tmp/fanout/r29_fullbank/E_source_search/lead/verify_c5base_absorber_independent.py`; exact output: `verdict=PASS`, `absorberCount=28`, `fullShoreMargin=0`.
- Strict written R23 four-pattern checker: `tmp/fanout/r29_fullbank/B_fourpattern/worker_5/checker.py`; outside capacity is zero under its component-equality predicate, so it retains the auxiliary defect.
- Generic full-bank flow checker: `tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py`; verifies supplied tokens/arcs only and is not an R29 provider.

Exact artifact hashes at this snapshot:

```text
653663a87635db27854a1cacb58497370faee9215b7547b46fa39771d5e57f9f  tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py
7572576bcdbc94390faac23b3b4cba0848b0799858a28ccfaa326293fa9497e9  tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.json
43e50aee99b019df6804aa173ba5456f4de2e5ec08b540e13f08349f1398012a  canonical 28-key assignment payload
ccab5e0f50eece849acb5d17d584990196409418c5af3db27b33a546a5fae860  independent verification record
```

## Child audit disposition

- Child 01: core matching/API audit; complete report, process exited nonzero after report emission.
- Child 02: outside-attachment audit; complete.
- Child 03: local/global FullBank chain audit; complete.
- Child 04: Door audit; complete.
- Child 05: vertex-slack audit; complete.
- Child 06: C5/prune audit; source builds succeeded, but its report writer failed under the Windows sandbox. Findings were recovered from its transcript and independently checked against source.
- Child 07: executable mapping; complete. It identified the important overclaim guardrail recorded in verdict item 5.
- Child 08: ActiveScoped-vs-FullBank difference audit; complete.
- Child 09: independent DAG/referee audit; complete.

All child processes have exited. No child changed production Lean source. Child reports live under `tmp/fanout/r29_fullbank_semantics/child_*/`.

## Deliverable review

`SEMANTICS.md` and `source_class_map.json` correctly enumerate the APIs and the exact transfer repair. The JSON parses with Python's standard `json` module. For production-status consumers, interpret `fullBankFalsifiedByR29: false` with the narrower operational meaning above; the strict compiled-production value is three-valued: `UNRESOLVED_PROVIDER_ABSENT`.
