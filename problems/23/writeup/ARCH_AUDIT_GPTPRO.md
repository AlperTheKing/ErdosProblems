# Architecture red-team audit — GPT-Pro (2026-07-09)

*The final design-phase deliverable: end-to-end edge walk of the composed DAG. VERDICT: "The composed DAG is
sound if two missing wiring edges are added explicitly." ASCII-sanitized; [C: ...] = Claude notes.*

## Verdict + the four MISSING-SPECs
- **MISSING-SPEC 1 (CRITICAL, "the largest non-wall wiring risk")**: FullBankRelaxedCoverCert/BankedCutDomination
  package → LengthSurplusChargeCertV2/ChargeCertProvider. Required module
  `Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge` with `FullBankGlobalPackage` (certs bundle + check +
  GlobalLedgerData + ledger_check) and `chargeProvider_of_fullBankPackage : ... → ChargeCertProvider G c rows`
  (equivalently ∃ F cert, ResidualFormulasFor ∧ checkLengthSurplusChargeCertV2 = true). Must compile banked
  Hall/ledger certificates into Σ(ell²−25) ≤ 25η ⟺ Γ ≤ N², outputting the ACTUAL ResidualFormulas +
  LengthSurplusChargeCertV2 (gammaUpper_from_chargeCertV2 is the only accepted route).
- **MISSING-SPEC 2 (CRITICAL)**: row coverage/partition: `rowCoverage_EQ_or_BranchB(_orGreenLeaf)` — every
  RowDB row is EQODL1 / BranchB / other-green-leaf. "Non-EQ L=5 rows must be accounted for explicitly by the
  row partition. Do not assume they vanish." Disconnection handled by M6BlueConnectivity + RowDB.ofCut.
- MISSING-SPEC 3: final O14 payload soundness mode = Lean-checked generated ConeCert payloads (chartSoundNNN via
  coreODLGoal_of_coneCert + fields + semantic target binding), never SHA-only. [C: already the adopted plan.]
- MISSING-SPEC 4: **global ledger no-double-spend** inside FullBankGlobalPackage: tokens not double-spent across
  cages/prefixes; global reserve identity matches N²−Γ; no illegal η_C. `fullBankGlobalPackage_sound` must be a
  PREMISE of chargeProvider_of_fullBankPackage.

## Status map (headline items)
- **A (top)**: final Delta0Package fields enumerated (goodCut, odlProvider+check, rowCoverage, o14Provider+check,
  branchBProvider+check, bank0/a1Proper packages); FCBridge COMPILED; assembly SPEC'D/partial.
- **B (GoodCutData)**: selection COMPILED (MaxCutSelection + M6BlueConnectivity); gammaOfCut at GraphData level +
  GammaMinimalConnected instantiation + badCount_eq_of_isMaxCut (= edgeCount − cutVal, max cuts share cutVal) =
  BUILDABLE-FROM-SPEC; RowDB.ofCut + RowDBFactsGeneral = SPEC'D (no research); GammaBetaFacts = buildable except
  the charge-cert input (→ MISSING-SPEC 1).
- **C (per-row GERSH)**: Branch-A O14 chain COMPILED (interfaces+pilot) / ENGINEERING (108 payloads, shape
  extraction); Branch-B chain COMPILED (21-26 + bridge), WALL (provider existence);
  all_rows_gersh_of_coreGoals COMPILED-if-ODLFullProvider.sound; row partition = MISSING-SPEC 2.
- **D (wall consumption)**: D1 wall→GammaBetaFacts = MISSING-SPEC 1; D2 wall→BranchBProvider = SPEC'D/buildable
  once wall certs exist (`branchBProvider_of_fullBankPackage` statement given).
- **E (lens lane)**: honest verdict — **NOT load-bearing for the final CertGraph assembly**; the package consumes
  FullBankRelaxedCoverCert/LengthSurplusChargeCertV2 + BranchBProvider + ODLFull, not the lens Props. Lens
  machinery = proof infrastructure for the wall (load-bearing only if GPT-5.6 proves FullBankHall via lens
  reductions) or redundant insurance. [C: T8 build continues — cheap, and insurance has value — but priority
  below the two critical specs.]
- **F**: complete obligation list (compiled / buildable-from-spec / THE-WALL [now ONE wall:
  Ell5FullBankRelaxedCover_exists = BankedCutDomination = FullBankHall = SSE = pureUPOK0_fullBankCert_exists =
  ReducedNonBaseGeodesicHall] / missing-spec 1-4).

## Final risk summary (verbatim-ish)
"The composed architecture assembles if and only if the two missing specs are filled" — the translation module +
the row partition; everything else is compiled, buildable, or the wall.
