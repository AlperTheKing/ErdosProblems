# FullBank compiled-chain axiom/shortcut audit

## Verdict

- **FORBIDDEN findings: 0.** No `sorry`, `admit`, `native_decide`, `sorryAx`, or project-specific axiom occurs in the audited chain.
- **ALLOWED findings:** every one of the 13 load-bearing declarations printed exactly `[propext, Classical.choice, Quot.sound]`. These are the standard Lean/mathlib foundational axioms allowed by this audit.
- The local transitive import surface is 12 production `.lean` files. It contains 0 shortcut-token hits and 0 explicit `axiom`/`opaque` declarations.
- A broader scan of the entire `problems/23/lean/Erdos23Delta0` production tree also found 0 case-sensitive word hits for `sorry|admit|native_decide`.

## Commands and counts

Repository-wide shortcut scan:

```powershell
rg -n -S "\b(sorry|admit|native_decide)\b" problems\23\lean\Erdos23Delta0 -g "*.lean"
```

Result: exit 1 (no matches), **0 hits**.

Local import-closure enumeration (seeds: `Ell5FullBankInterface`, `Ell5FullBankAssignedSink`, `Ell5FullBankHall`, `Gamma.FullBankToLengthSurplusCharge`, `Gamma.FullBankChargeCertProvider`): a PowerShell queue converted module dots to paths, read only leading `import` declarations, and recursively enqueued local modules under `problems/23/lean`.

Result: **12 local files**:

```text
Erdos23Delta0/BankedCutDominationCore.lean
Erdos23Delta0/CertGraph.lean
Erdos23Delta0/Ell5FullBankAssignedSink.lean
Erdos23Delta0/Ell5FullBankHall.lean
Erdos23Delta0/Ell5FullBankInterface.lean
Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean
Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
Erdos23Delta0/GammaAggregation.lean
Erdos23Delta0/MaxCutVertexIneq.lean
Erdos23Delta0/RelaxedCoverBanked.lean
Erdos23Delta0/RelaxedCoverDuality.lean
Erdos23Delta0/RelaxedCutCover.lean
```

Closure scans:

```powershell
Select-String -LiteralPath <each-of-12-files> -Pattern '\b(sorry|admit|native_decide)\b' -CaseSensitive
Select-String -LiteralPath <each-of-12-files> -Pattern '^\s*(axiom|opaque)\s+' -CaseSensitive
```

Results: `LOCAL_CLOSURE_COUNT=12`, `SHORTCUT_HITS=0`, `AXIOM_OR_OPAQUE_DECL_HITS=0`.

Compiled probe command (Lean 4.27.0, cached compiled FullBank tree plus the Formal Conjectures/mathlib package paths):

```powershell
$paths=@('E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1','E:\Projects\ErdosProblems\problems\23\lean','E:\Projects\ErdosProblems\formal-conjectures\.lake\build\lib\lean')
$paths += Get-ChildItem 'E:\Projects\ErdosProblems\formal-conjectures\.lake\packages' -Directory | % { Join-Path $_.FullName '.lake\build\lib\lean' } | ? { Test-Path $_ }
$env:LEAN_PATH=$paths -join ';'
elan run leanprover/lean4:v4.27.0 lean E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank\F_lean\d7_axioms\REPORT.md
```

The report file temporarily contained the imports and 13 `#print axioms` commands listed below, then was replaced with this report. Result: **exit 0**, 13/13 declarations printed.

## Load-bearing `#print axioms` findings

Each command below returned exactly `depends on axioms: [propext, Classical.choice, Quot.sound]`:

```lean
#print axioms Erdos23Delta0.Ell5FullBankInterface.bankedCutDomination_of_cert
#print axioms Erdos23Delta0.Ell5FullBankInterface.no_dualCert_of_cert
#print axioms Erdos23Delta0.Ell5FullBankInterface.graph_bankedCutDomination_of_cert
#print axioms Erdos23Delta0.Ell5FullBankInterface.graph_no_dualCert_of_cert
#print axioms Erdos23Delta0.Ell5FullBankAssignedSink.cert_of_assignedSink
#print axioms Erdos23Delta0.Ell5FullBankAssignedSink.bankedCutDomination_of_assignedSink
#print axioms Erdos23Delta0.Ell5FullBankAssignedSink.no_dualCert_of_assignedSink
#print axioms Erdos23Delta0.Ell5FullBankHall.external_load_le_bank_of_cert
#print axioms Erdos23Delta0.Ell5FullBankHall.hall_bound_of_fullBank_cert
#print axioms Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.fullBankGlobalPackage_sound
#print axioms Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage
#print axioms Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.chargeCertProviderOfFullBankLedger_ok
#print axioms Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.gammaUpper_from_fullBankPackage_via_chargeCertV2
```

Exact classification:

| Finding | Count | Classification |
|---|---:|---|
| `propext` | 13/13 declarations | ALLOWED |
| `Classical.choice` | 13/13 declarations | ALLOWED |
| `Quot.sound` | 13/13 declarations | ALLOWED |
| `sorryAx` | 0/13 declarations | FORBIDDEN, absent |
| Any project-specific axiom | 0/13 declarations | FORBIDDEN, absent |
| `sorry` source token | 0/12 closure files; 0 in full Erdős23 tree | FORBIDDEN, absent |
| `admit` source token | 0/12 closure files; 0 in full Erdős23 tree | FORBIDDEN, absent |
| `native_decide` source token | 0/12 closure files; 0 in full Erdős23 tree | FORBIDDEN, absent |
| Explicit `axiom` or `opaque` declaration | 0/12 closure files | FORBIDDEN if nonstandard/load-bearing, absent |

## Scope note

This establishes that the compiled implication machinery is axiom-clean under the stated allowlist. It does not establish existence of a `FullBankRelaxedCoverCert` or a `FullBankGlobalPackage.Checked`; those remain input hypotheses/structures to the audited implications, not axioms hidden by the theorem chain.
