# O14 Listed Coverage Audit - 2026-07-09

This note records the non-payload O14 assembly obligation found while
Claude's `console4` generated-payload wave was running.  The generated chart
payloads may all verify and still leave this structural bridge to prove.

## Verified source surfaces

- `problems/23/lean/Erdos23Delta0/O14/Generated/ListedConcreteCover.lean`
  defines
  `ListedShapeCoverage := ∀ I : EQODL1ShapeInst G c rows Q,
  EQODL1ShapeSound I → ListedShape I.shape`.
- `problems/23/lean/Erdos23Delta0/O14/ListedChartCoverToODLFull.lean`
  consumes `ListedShapeCoverage`, `shapeInstOf`, `shapeSound`, `core_eq`, and
  `ChartBridgeInputs` to obtain the row ODL bound.
- `problems/23/lean/Erdos23Delta0/O14/Generated/ListedClassifier.lean`
  makes `ListedShape` a disjunction of the 108 certified `(kIdx,dIdx)` pairs.
  The listed-membership predicate does not use `seedShape`, `maskCode`,
  `orbitCode`, `routeCode`, or `sigCode`.
- `problems/23/lean/Erdos23Delta0/O14/EQODL1Shape.lean` currently defines
  `O14Closed`, `MaskSound`, `SeedSound`, `RouteSound`, and `ScalarSound` as
  `True`.  Thus `EQODL1ShapeSound` only constrains `Q.length = 5` today.

## Consequence

`ListedShapeCoverage` is not currently derivable from the existing
`EQODL1ShapeSound` definition for an arbitrary `I.shape`: the soundness fields
do not restrict `shape.kIdx` or `shape.dIdx`.  Final assembly therefore needs
one of the following:

1. strengthen the `EQODL1ShapeSound` predicates so semantic soundness implies
   one of the listed `(kIdx,dIdx)` pairs; or
2. prove a separate structural extractor theorem that constructs only listed
   descriptors and supplies `ListedShapeCoverage`; or
3. replace the current interface with an equivalent provider whose theorem
   does not leave `ListedShapeCoverage` as a free assumption.

An ASK with this exact question was posted to
`coordination/CODEX_TO_CLAUDE.md` for Claude/Fable design arbitration.

## Cleaner binding route found after source audit

`problems/23/lean/Erdos23Delta0/O14/ListedChartCoverToODLFull.lean` already
contains a lower-level theorem that does **not** require `ListedShapeCoverage`:

```lean
rowODL_of_listed_o14_eq_cover_semantic_tree
  (instOf : Seed3Node -> PayloadRef ->
      Generated.ListedShapeInst G c rows Q)
  (core_eq :
    forall n ref, n.kind = NodeKind.leaf LeafTag.EQ ref ->
      sem.coreOf n.id = (instOf n ref).inst.core)
  ...
```

This is the preferred final-assembly target if the structural extractor can
construct a `Generated.ListedShapeInst` for each EQ leaf.  Then the listed
proof is stored per leaf in the returned instance:

```lean
structure ListedShapeInst ... where
  inst : EQODL1ShapeInst G c rows Q
  listed : ListedShape inst.shape
```

and there is no free global theorem

```lean
forall I, EQODL1ShapeSound I -> ListedShape I.shape
```

to prove for arbitrary descriptors.

Thus the module-29 semantic bridge has two valid implementation choices:

1. **Direct-listed extractor (preferred):** build
   `Seed3Node -> PayloadRef -> Generated.ListedShapeInst G c rows Q` and use
   `rowODL_of_listed_o14_eq_cover_semantic_tree`.
2. **Global-coverage extractor:** keep `shapeInstOf` returning raw
   `EQODL1ShapeInst` and prove `Generated.ListedShapeCoverage`; this requires
   strengthening/replacing the placeholder `O14Closed`, `MaskSound`,
   `SeedSound`, `RouteSound`, and `ScalarSound` predicates.

The direct-listed extractor is the smaller proof obligation: it only needs to
prove the emitted descriptor for each real EQ leaf has one of the listed v108
`(kIdx,dIdx)` pairs, instead of proving a universal coverage theorem for every
syntactically possible `EQODL1ShapeInst`.

## Token audit

The following source files were scanned for `sorry`, `admit`,
`native_decide`, `Lean.ofReduceBool`, and `unsafe`; no hits were found:

- `Gamma/FullBankChargeCertProvider.lean`
- `BankedWallLPRestricted.lean`
- `O14/Generated/ChartPayloads/Chart000Bridge.lean`
- `O14/Generated/BridgeRegistry.lean`
- `O14/Generated/ListedConcreteCover.lean`
- `O14/ListedChartCoverToODLFull.lean`

Generated `#print axioms` probes remain in some generated bridge files.  They
are audit probes rather than proof shortcuts, but should be stripped or
isolated before the final polished PR if the release policy requires quiet
builds.
