# Codex Wall Downstream Contract - 2026-07-09

This is a source audit of the already-written Lean downstream path from the
Gap#1 wall output to the final row/provider machinery. It is not a new proof
claim and it does not assert existence of the wall certificate.

## Wall Output Object

The typed wall output currently lives in:

```text
problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
```

The central object is:

```lean
FullBankGlobalPackage G c rows
FullBankGlobalPackage.Checked P
```

The spendable cap kinds are exactly:

```lean
CapKind.door
CapKind.vertexSlack
CapKind.c5Base
CapKind.prune
```

There is intentionally no eta-token cap kind. The eta/global reserve is handled
by non-spendable component and superadditivity slack fields.

## Checked Fields That Matter

`FullBankGlobalPackage.Checked` contains the downstream bookkeeping needed for
the wall-to-gamma route:

- `rows_length_eq_badCount`
- `row_length_ge_five`
- `row_local_component`
- `local_view_checked`
- `surplusInLocal_le_demand`
- `localCap_eq_kindSpends`
- `localCap_eq_spendOfLocal`
- `spend_nonneg`
- `tokenCap_nonneg`
- `no_double_spend`
- `no_cross_component_spend`
- `token_source_unique`
- `lengthSurplus_eq_localSurplus`
- `tokenCapTotal_eq_componentTokenCapTotal`
- `componentReserveSlack_nonneg`
- `componentReserveIdentity`
- `componentRowCountSum`
- `superadditivitySlack_nonneg`
- `superadditivityIdentity`

These fields are the contract the actual Gap#1 construction must satisfy.

## Downstream Theorems Already Present

The direct soundness theorem is:

```lean
FullBankGlobalPackage.fullBankGlobalPackage_sound :
  P.Checked -> lengthSurplusGD rows <= 25 * etaQ G c
```

The gamma route is:

```lean
FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage :
  P.Checked -> gammaOfGD G c rows <= (G.n : Rat)^2
```

The typed `LengthSurplusChargeCertV2` bridge lives in:

```text
problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean
```

It provides:

```lean
chargeCertProviderOfFullBankLedger
chargeCertProviderOfFullBankLedger_ok
gammaUpper_from_fullBankPackage_via_chargeCertV2
```

This confirms that, once a checked `FullBankGlobalPackage` exists, the old typed
charge-certificate route can also be fed.

## Row Dispatch Contract

The provider-facing row partition path lives in:

```text
problems/23/lean/Erdos23Delta0/Rows/RowPartition.lean
```

Important guardrail:

```lean
IsEQODL1Row = ComponentAllL5 (compOfRow i)
```

not `rowEll i = 5`. Mixed K2 components are routed wholesale to Branch-B,
including any length-5 rows inside them.

The row dispatch theorem is:

```lean
ODLFullRowPartitionView.rowGersh_of_partition
```

and the value-level all-row theorem is:

```lean
ODLFullRowPartitionView.allRowsGersh_of_partition
```

The graph-data beta route from a checked partition is:

```lean
ODLFullRowPartitionView.beta_bound_of_partitioned_provider
```

`PackageProviderSkeleton.lean` now records this as a direct official-form seam:

```lean
GraphDataPartitionProviderInputs G
graphData_beta_bound_of_partitionInputs
simpleGraph_beta_bound_of_partitionInputs
erdos23_fcForm_of_partitionInputs
```

This route bypasses the older length-only `Delta0CertBundles` dispatch and is
therefore the preferred target for the component-level RowPartition assembly.
It still depends on the same upstream wall package for Branch-B/mixed
components.

## Current Missing Upstream Content

The downstream arithmetic is not the current wall. The missing proof object is
one of the following:

1. Direct construction of:

```lean
P : FullBankGlobalPackage G c rows
hP : P.Checked
```

for every relevant Branch-B/mixed component wall instance; or

2. A W3/restricted-Farkas route that produces the same checked package or an
equivalent `FullBankRelaxedCoverCert`, including:

- finite rational restricted-Farkas / almost-squeeze source,
- closed weighted Hall completeness,
- positive root-block extraction / root-locality,
- closed-root exchange identity,
- global no-double-spend and reserve identities.

The existing `FullBankChargeCertProvider` is therefore downstream-only evidence.
It should not be counted as a Gap#1 proof.

## Next Gate

When the O14 Lean worker pool is free, the next mechanical gate for this audit is
to rebuild:

```text
Gamma/FullBankToLengthSurplusCharge.lean
Gamma/FullBankChargeCertProvider.lean
Rows/RowPartition.lean
PackageProviderSkeleton.lean
```

and axiom-probe the exported downstream declarations. Until then, this file is
only a source-level contract audit.
