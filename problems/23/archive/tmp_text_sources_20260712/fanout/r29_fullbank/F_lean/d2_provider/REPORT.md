# Full-bank producer/provider audit

Scope: `problems/23/lean/**/*.lean`, excluding `**/Generated/**`. Read-only audit; no build and no source-tree edits.

## `rg` commands and counts

```powershell
rg -n --glob '*.lean' --glob '!**/Generated/**' 'FullBankRelaxedCoverCert|FullBankGlobalPackage\.Checked' problems/23/lean
```

Literal-count follow-up:

```powershell
rg -n --glob '*.lean' --glob '!**/Generated/**' --fixed-strings 'FullBankRelaxedCoverCert' problems/23/lean
# 36 occurrences in 18 files

rg -n --glob '*.lean' --glob '!**/Generated/**' --fixed-strings 'FullBankGlobalPackage' problems/23/lean
# 44 occurrences in 5 files

rg -n --glob '*.lean' --glob '!**/Generated/**' --fixed-strings 'P.Checked' problems/23/lean
# 21 occurrences in 5 files (includes unrelated `Checked` namespaces unless inspected)

rg -n --glob '*.lean' --glob '!**/Generated/**' 'FullBankGlobalPackage .*where|: FullBankGlobalPackage|\.Checked := by' problems/23/lean/Erdos23Delta0
# exactly one FullBankGlobalPackage construction and one proof of that package's Checked:
# AggregateLedgerNoIncidenceCounterexample.lean:34,49
```

Declaration-name search:

```powershell
rg -n --glob '*.lean' --glob '!**/Generated/**' '^(noncomputable )?def (certificate|certificate_|cert_|certOf|fullBank|.*fullBank.*|.*FullBank.*)' problems/23/lean/Erdos23Delta0
```

## Target definitions (exact signatures)

`Ell5FullBankInterface.lean:27`:

```lean
structure FullBankRelaxedCoverCert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ) where
```

`Ell5FullBankInterface.lean:64` is only an abbreviation, not existence:

```lean
abbrev GraphFullBankRelaxedCoverCert
    (G : SimpleGraph V) (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop) (kap : JT → ℚ) :=
  FullBankRelaxedCoverCert S F O J K
    (fun k => deltaM G cut (Ufam k))
    (fun k => deltaB G cut (Ufam k)) inc kap
```

`Gamma/FullBankToLengthSurplusCharge.lean:134,177`:

```lean
structure FullBankGlobalPackage (G : GraphData) (c : CutData) (rows : RowDB) where
  componentCount : Nat
  localCount : Nat
  tokenCount : Nat
  compN : Fin componentCount → ℚ
  componentRowCountQ : Fin componentCount → ℚ
  compOfRow : Fin rows.rowList.length → Fin componentCount
  localOfRow : Fin rows.rowList.length → Fin localCount
  localCover : Fin localCount → FullBankLocalCover componentCount
  ledger : GlobalLedgerData componentCount localCount tokenCount

structure FullBankGlobalPackage.Checked (P : FullBankGlobalPackage G c rows) : Prop where
  -- fields run from rows_length_eq_badCount through superadditivityIdentity
```

## Producers of `FullBankRelaxedCoverCert`

Abstract/generic wrappers (they do not derive existence from a graph):

```lean
certOfPrimal
  ...
  (P : Wall.Primal (wallLP S F O J K sep dB inc kap)) :
  FullBankRelaxedCoverCert S F O J K sep dB inc kap

cert_of_assignedSink
  ...
  (hcap : ∀ j ∈ J, (∑ c ∈ O, assignedSinkQ K lam dB sink c j) ≤ kap j) :
  FullBankRelaxedCoverCert S F O J K sep dB inc kap

nonempty_cert_iff_nonempty_primal
  ... :
  Nonempty (FullBankRelaxedCoverCert S F O J K sep dB inc kap) ↔
    Nonempty (Wall.Primal (wallLP S F O J K sep dB inc kap))
```

Thus `certOfPrimal` merely repackages an already supplied primal, `cert_of_assignedSink` merely repackages supplied coverage/capacity proofs, and the iff transports the same missing existence.

Graph-shaped but conditional constructors (exact result signatures; every one takes Hall/flow/capacity/boundary hypotheses):

```lean
certificate_of_activeComponent_mixedDoorEndpointHall ... :
  FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
    (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
    (fun b => deltaB G s (blockSet C (componentOwner comp active) b)) inc kap

certificate_of_activeComponent_mixedDoorEndpointFlow ... :
  FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
    (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
    (fun b => deltaB G s (blockSet C (componentOwner comp active) b)) inc kap

certificate_of_activeComponent_mixedDoorBankHall ... :
  FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
    (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
    (fun b => deltaB G s (blockSet C (componentOwner comp active) b))
    (combinedInc incBase incDoor) (combinedCap kapBase kapDoor)

certificate_of_blockCore_mixedDoorBankFlow ... :
  FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
    (fun b => deltaM G s (blockSet C block b))
    (fun b => deltaB G s (blockSet C block b)) inc kap

certificate_of_blockCore_mixedDoorEndpointFlow ... :
  FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
    (fun b => deltaM G s (blockSet C block b))
    (fun b => deltaB G s (blockSet C block b)) inc kap

certificate_of_blockSingleton_boundaryDoors ... :
  FullBankRelaxedCoverCert S F O O Finset.univ
    (fun b => deltaM G s (blockSet C block b))
    (fun b => deltaB G s (blockSet C block b)) inc kap

certificate_of_internalEndpointSlack_boundaryDoors ... :
  FullBankRelaxedCoverCert S F (cutEdges G s \ F) Finset.univ C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_assignedSink ... :
  FullBankRelaxedCoverCert S F O J C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_boundaryCount ... :
  FullBankRelaxedCoverCert S F O J C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_vertexSlack ... :
  FullBankRelaxedCoverCert S F O C C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_allDoors ... :
  FullBankRelaxedCoverCert S F O O C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_mixedDoorVertex ... :
  FullBankRelaxedCoverCert S F O Finset.univ C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_mixedDoorVertexCount ... :
  FullBankRelaxedCoverCert S F O Finset.univ C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap

certificate_of_singletonCore_mixedDoorEndpointFlow ... :
  FullBankRelaxedCoverCert S F O Finset.univ C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap
```

Real finite-data/check-derived producer:

```lean
InactiveComponentBlockChecker.certificate_of_check (hcheck : check G D = true) :
  FullBankRelaxedCoverCert
    D.selectedAtoms D.support D.offSupport D.offSupport Finset.univ
    (fun b => deltaM G D.cut (blockSet D.core D.blockLabel b))
    (fun b => deltaB G D.cut (blockSet D.core D.blockLabel b))
    (fun c j => D.legal c j = true) D.capacity
```

This is genuinely checker-derived from `D`, but still requires a supplied accepted `Candidate`; there is no theorem producing such a `D` for arbitrary graph-derived data.

Closed fixtures only:

```lean
Wall24PrimalFixture.certificate :
  FullBankRelaxedCoverCert rows support outside sinks cuts
    separated boundary legalVertexSlack vertexSlackCap

Wall359PrimalFixture.certificate :
  FullBankRelaxedCoverCert rows support outside sinks cuts
    separated boundary legalVertexSlack vertexSlackCap
```

`EndpointHalfDoorComplete.fullBankBundle_of_endpointHalfDoorComplete` contains a local certificate but its public result is `EndpointHalfDoorFullBankBundle ...`; it assumes `EndpointHalfDoorComplete ...`, so it is another conditional wrapper, not graph-derived existence.

## Producers/providers of `FullBankGlobalPackage.Checked`

There is exactly one inhabitant in the searched tree:

```lean
AggregateLedgerNoIncidenceCounterexample.emptyPackage :
  FullBankGlobalPackage emptyGraph emptyCut emptyRows

AggregateLedgerNoIncidenceCounterexample.emptyPackage_checked :
  emptyPackage.Checked
```

This is the zero-vertex/zero-row counterexample fixture, not a provider for graph-derived `(G,c,rows)`.

All other occurrences consume `h : P.Checked`. In particular the misleadingly named provider bridge has the exact direction:

```lean
chargeCertProviderOfFullBankLedger
    (_P : FullBankGlobalPackage G c rows) : LengthSurplusChargeCertV2

chargeCertProviderOfFullBankLedger_ok
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    LengthSurplusChargeCertV2.check G c rows
      (chargeCertProviderOfFullBankLedger P) = true
```

It consumes `P.Checked`; it does not construct either `P` or the proof.

## Exact first missing real provider

The first missing real provider is not an adapter from a supplied primal/Hall witness and not the empty fixture. It is graph-derived existence of an accepted full-bank object. At the older relaxed-cover seam, the tree itself names the absent theorem in comments as `Ell5FullBankRelaxedCover_exists`; no declaration with that name exists. Its essential missing result is:

```lean
Nonempty (GraphFullBankRelaxedCoverCert G cut S F O J K Ufam inc kap)
```

for the canonical objects derived from the relevant graph/cut/row/component data, with no primal, flow, Hall, capacity, or accepted-check witness passed in.

At the later global-ledger seam, the corresponding (and strictly necessary before any `FullBankGlobalPackage` soundness theorem can fire) missing provider has exact target shape:

```lean
∃ P : FullBankGlobalPackage G c rows, P.Checked
```

for graph-derived `G`, selected/good `c`, and its `rows`. No declaration in the tree has this result type. Therefore the earliest actual gap is graph-side certificate/package existence; `certOfPrimal`, `cert_of_assignedSink`, Hall/flow specializations, charge-cert conversion, and soundness theorems are downstream abstract wrappers.
