# O14 compact payload redesign (2026-07-09)

## Verdict

The current `ConePairs` emission format is not PR-viable.  This is not a
chunk-size tuning problem.  The pair layer must be removed and replaced by a
sparse source-matrix certificate.

The `O14/Generated/ChartPayloads` tree remains frozen while this design is
reviewed.  No generated payload source was changed during this audit.

## Measured obstruction

Current generated Lean source totals:

| kind | files | source size |
|---|---:|---:|
| `ConePairs` | 34,763 | 31.94 GB |
| `ConeBase` | 108 | 2.14 GB |
| `ConeMS` | 7,933 | 0.88 GB |
| all other chart modules | 325 | about 0.01 GB |

Measured `.olean` sizes in the retained cache:

| chart/kind | files | `.olean` size |
|---|---:|---:|
| Chart000 `ConePairs` | 364 | 5.88 GB |
| Chart000 `ConeBase` | 1 | 71.76 MB |
| Chart000 `ConeMS` | 45 | 0.04 GB |
| Chart001 partial `ConePairs` | 168 | 14.75 GB, 83.75 MB average |

Claude measured 4,967 shard oleans at 401.6 GB and projected about 3.4 TB for
the current 42,390-shard wave.  The source tree itself is already about 35 GB.

Changing `pair_chunk` cannot meet the target.  Chart000 used roughly half-size
pair files and still spent 5.88 GB on pair oleans alone.

## What the pair layer proves

`_codex_o14_chunked_cone_export.py` creates `combo_order_chunks` by taking each
raw product-term block `right` and setting `left := collect(right)`.  The
generated pair theorems prove only these local tautologies:

```text
eval(collect(raw chunk)) = eval(raw chunk).
```

For Chart000 v2 this expands:

```text
727 pair equalities
46,521 raw terms
46,228 locally collected terms
8,344 distinct power lists
```

The exporter separately computes `bucket_chunks(target_nf, combo_nf)` after
checking `target_nf == combo_nf`, but the sharded emitter does not emit those
83 target chunks.  Consequently the current `ChunkedCone.Witness` factory
still takes both decisive semantic equalities as arguments:

```lean
hcombo  : eval rawChunks = eval (comboNF base mults slacks)
htarget : eval collectedChunks = coreDefect core
```

So the enormous pair payload is neither a complete target identity certificate
nor a compact representation of the accepted source LP certificate.

## Replacement certificate

Certify the exact source LP equation before expanding products into monomials.
The source checker already verifies this object exactly.

### Shared chart-family template

For each chart/dominant template, define once:

```lean
structure SparseColumn (Row : Type) where
  terms : List (Row × Rat)

structure ConeTemplate (Row Col : Type) where
  targetCoeff : Row -> Rat
  column : Col -> SparseColumn Row
  multiplier : Col -> NF
  slack : Col -> NF
  basis : Row -> NF
  columnSemantics : forall c env,
    NF.eval env (NF.mul (multiplier c) (slack c)) =
      Finset.univ.sum fun r => (column c).coeff r * NF.eval env (basis r)
  targetSemantics : forall env,
    targetPolynomial.eval env =
      Finset.univ.sum fun r => targetCoeff r * NF.eval env (basis r)
```

The column semantic lemmas depend only on the chart template, not on one of the
108 rational LP solutions.  They must therefore be shared, not duplicated in
every slot.

### Per-slot sparse solution

```lean
structure SparseConeSolution (T : ConeTemplate Row Col) where
  weight : Col -> Rat
  residual : Row -> Rat
  weight_nonneg : forall c, 0 <= weight c
  residual_nonneg : forall r, 0 <= residual r
  row_eq : forall r,
    T.targetCoeff r = residual r +
      Finset.univ.sum fun c => weight c * (T.column c).coeff r
```

`row_eq` is the exact rational source-matrix equation.  Its proof shards contain
small scalar equalities, not expanded polynomial NFs.  The generic soundness
theorem rearranges finite sums, applies `columnSemantics`, and obtains the same
nonnegative cone evaluation consumed by `ODLFull`.

The generated slot payload is then only:

* sparse rational `weight` values;
* sparse rational `residual` values;
* exact row equations;
* references to one shared chart-family template.

No `combo_order_chunks`, `ConePairs`, or per-product monomial expansion appears
in a slot payload.

## Compact literal encoding

If ordinary Lean literals remain too large, add a second, semantics-neutral
packing layer:

* one dictionary of distinct rational numerators/denominators;
* sparse entries as `(rowId, coeffId)` pairs;
* row proofs sharded at 32-64 scalar equations;
* a verified decoder and checker using kernel reduction (`rfl`/ordinary
  `decide` only), never `native_decide` or `Lean.ofReduceBool`.

Packing is not the soundness argument.  `SparseConeSolution.sound` is.  The
decoder merely reconstructs its fields.

## Pilot gate

Build a Chart000 prototype outside the frozen generated tree.

Acceptance conditions:

1. Exact reconstruction of the same source solution and residual.
2. `SparseConeSolution.sound` reaches `CoreODLGoal` through the real API.
3. Plain `lake env lean`; no external heartbeat flag.
4. Forbidden scan zero.
5. Axioms exactly `[propext, Classical.choice, Quot.sound]`.
6. Chart000 generated source at most 25 MB.
7. Chart000 total `.olean` mass at most 400 MB.
8. Projected 108-chart `.olean` mass at most 50 GB.

Only after this pilot is independently rebuilt should all 108 payloads be
regenerated.  The current per-chart staged wave can still serve as a temporary
correctness audit, but its artifacts must not be the final PR representation.

## Chart000 pilot measurements

The first source-matrix prototype stored the 1,414 rational weights once and
proved each canonical residual directly over `Rat`.  It rebuilt all 8,344
active rows exactly, but missed gate 7 narrowly:

| format | source | `.olean` | build |
|---|---:|---:|---:|
| shared rational weights | 1.00 MB | 5.84 MB | 25.85 s |
| 131 rational residual shards | 2.88 MB | 434.76 MB | 294.75 s / 32 workers |
| total | 3.88 MB | 440.60 MB | 320.60 s |

Two constant-size Boolean-checker attempts were rejected.  Imported `Rat`
division does not reduce definitionally under `rfl` or ordinary `decide`, and a
single common-denominator `Int` fold over the densest rows overflows Lean's
default thread stack.  Neither route is suitable for plain CI.

The successful representation clears rational denominators before emission.
For one slot, let `D` be the positive least common multiple of all solution
weight denominators.  Store each weight as the nonnegative integer

```text
W_c = D * weight(c).
```

For each row choose a positive row denominator `C_r`, and prove the integer
inequality

```text
D*C_r*target(r) - sum_c W_c*(C_r*columnCoeff(c,r)) >= 0.
```

All factors are exact integers.  A generic denominator-clearing lemma maps
this inequality back to the canonical rational residual.  On Chart000, direct
integer residual shards give:

| format | source | `.olean` | build |
|---|---:|---:|---:|
| 131 common-denominator integer shards | 18.49 MB | 93.48 MB | 257.74 s / 32 workers |

All 8,344 rows rebuilt with return code zero under a plain `lake env lean`.
The densest 64-row shard is 3.33 MB, versus 16.03 MB for the rational form.
This clears gates 3, 6, and 7 with substantial room.  The remaining pilot
obligation is to instantiate `SparseConeMatrix.Template` and connect these
integer residual lemmas through the denominator-clearing kernel to
`SparseConeMatrix.Solution.coreODLGoal`; only then can gate 2 be claimed.

The denominator-clearing kernel and generated semantic row adapters now also
rebuild.  Each row has a sparse integer record, a direct exact integer
inequality, and the derived theorem

```text
0 <= targetRat D row - weightedSumRat D weight row.
```

The shared weight function carries kernel-reduced equations for every selected
column.  Full semantic-pilot measurements are:

| artifact | `.olean` |
|---|---:|
| shared denominator/weight function | 6.97 MB |
| 131 integer + rational residual shards | 278.29 MB |
| total | 285.26 MB |

All 131 semantic shards rebuilt with return code zero in 355.42 seconds on 32
workers.  The source/token scan has zero occurrences of `sorry`, `admit`,
`native_decide`, or `Lean.ofReduceBool`.  Axiom probes for the generic
denominator lemmas and generated row theorems report exactly
`[propext, Classical.choice, Quot.sound]`.

This closes the arithmetic and size halves of the Chart000 pilot.  The open
semantic obligation is now narrower: define the chart source-matrix
`SparseConeMatrix.Template`, identify these active-row residuals with its
`canonicalResidual`, and discharge the shared target/column polynomial
semantics before invoking `coreODLGoal`.

## Full compact-cone pilot

The pilot now also emits the Bernstein base polynomial, reuses the accepted 45
Chart000 multiplier/slack shards, and compiles the thin theorem

```text
Chart000CompactCone.coreODLGoal_of_compactCone
```

through the real `coreODLGoal_of_coneEval` API.  As in the accepted
`Chart000Bridge`, the caller supplies the structural `hidEval` and `htarget`
bindings; the generated payload proves exact base and multiplier
nonnegativity.  No `ConePairs` module is imported.

After removing one redundant exported theorem per active row, a clean 32-worker
build gave:

| artifact | `.olean` |
|---|---:|
| 131 semantic residual/base shards | 381.75 MB |
| shared denominator/weight function | 6.97 MB |
| thin compact-cone bridge | 0.54 MB |
| reused Chart000 multiplier/slack shards | 39.21 MB |
| reused Chart000 support | 0.11 MB |
| **all-in Chart000** | **428.58 MB** |

All 131 shards and the bridge returned code zero.  The all-in Chart000 figure
projects to 43.11 GiB for 108 equally large charts, below gate 8's 50 GB limit.
The generated compact source is 28.14 MB.  Thus the current format passes the
global PR-viability gate but narrowly misses the deliberately stricter pilot
gates 6 and 7 (25 MB source and 400 MB all-in).  Those misses are recorded, not
waived; an independent rebuild should decide whether the global 50 GB gate is
the operative acceptance threshold.

The final probe reports exactly `[propext, Classical.choice, Quot.sound]` for
the denominator-clearing lemmas, a generated row theorem, a shard
`hbaseTerms`, and `coreODLGoal_of_compactCone`.  The forbidden-token scan is
zero.

A source-minimizing variant that evaluated each sparse row directly removed
the duplicated integer expression, but increased the densest shard olean from
9.06 MB to 13.60 MB and slowed its build to 56.5 seconds.  It is rejected for
final emission.

## Rejected alternatives

* Smaller pair chunks: Chart000 already disproves viability.
* Larger pair chunks plus larger `simp` budgets: worsens superlinear proof-term
  growth and build memory.
* A compressed string whose parser is trusted: unacceptable.  Any packed form
  needs a proved decoder/checker and ordinary kernel reduction.
* Keeping pair shards only for one-time verification: useful as an external
  audit, but does not produce a buildable formal-conjectures artifact.
