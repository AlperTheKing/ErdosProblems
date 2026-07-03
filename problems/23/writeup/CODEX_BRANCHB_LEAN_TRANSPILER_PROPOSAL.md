# Branch-B JSONL-to-Lean Transpiler Proposal

Codex proposal, 2026-07-04.

## Scope

Input:

- `tmp/bankl_branchb_gateb_final_v1.jsonl`
- `tmp/bankl_branchb_gateb_final_v1_verify_summary.json`

Current exact profile:

- rows: `14247`
- Gate-B burden rows: `1062`
- op rows: `926`
- op steps: `1852`
- maximum row-level certificate terms: `2`
- maximum Gate-B telescope steps per row: `2`
- local verifier rerun: `bad=0`, `pending_claude_acceptance_rows=0`

The transpiler should not re-prove graph theory. It should turn the accepted finite
Branch-B table into kernel-checkable arithmetic data that Claude's Lean lemma tree can
consume.

## Lean Target

Follow `LEAN_BRANCHB_BLUEPRINT_GPTPRO.md`: certificates enter Lean as data plus one
small verified checker. Do not use `native_decide`. Avoid a per-row tactic script
when a literal arithmetic proof field is enough.

I propose three generated Lean layers.

1. `Erdos23Delta0/Cert/Scalar.lean`

   A hand-written generic checker over cleared integer arithmetic.

2. `Erdos23Delta0/Cert/BranchBData/ShardNN.lean`

   Generated row records, sharded so each file has bounded elaboration cost.

3. `Erdos23Delta0/Cert/BranchBTable.lean`

   Imports the shards and exposes one theorem that the Branch-B finite table is valid.

## Scalar Certificate Encoding

All rational strings from JSONL are parsed by Python as `Fraction`. For each finite
identity, the generator clears denominators with a positive common denominator `D` and
emits integer-scaled terms.

Example shape:

```lean
structure ScaledEqCert where
  terms : List Int
  target : Int
  sum_eq : terms.sum = target

structure ScaledLeCert where
  lhs : Int
  rhs : Int
  margin : Nat
  le_eq : lhs + margin = rhs
```

Here `ScaledLeCert` proves `lhs <= rhs` because `margin` is nonnegative by type.

For identities where the natural direction is `rhs <= lhs`, the generator swaps fields
or uses a second wrapper:

```lean
structure ScaledGeCert where
  lhs : Int
  rhs : Int
  margin : Nat
  ge_eq : rhs + margin = lhs
```

The generated proof fields should first try `by rfl` on literal integer sums. If the FC
toolchain does not reduce a particular literal sum by definitional equality, the fallback
is `by norm_num`; still no `native_decide`.

The Python emitter records which proof mode was used. A pilot compile on a small shard
decides whether the full table uses `rfl`, `norm_num`, or a mix.

## Nonnegative Dictionary Pieces

Dictionary classes become a small enum:

```lean
inductive DictClass
  | terminalPrefixLaneInterval
  | terminalPrefixSingletonExtraction
  | terminalPrefixPathInterval
  | terminalPrefix
  | noncrossingCoB
  | noncrossingCoBComponentExtraction
  | noncrossingCoBExteriorAnchor
  | detourResidual
  | dCert
  | unitPositiveExchange25
```

The exact final JSONL currently uses the coarser accepted op classes:

- `terminal-prefix-raw-extraction`
- `terminal-prefix-lane-addition`
- `noncrossing-coB-extraction`
- `noncrossing-coB-component-addition`
- `empty`

The transpiler maps these to the enum through a table stored in Lean and mirrored in
the Python audit manifest.

Each dictionary term is nonnegative by construction:

```lean
structure Qnn where
  num : Nat
  den : Nat   -- value = num / (den + 1)

structure ConePiece where
  cls : DictClass
  coeff : Qnn
  value : Qnn
  contribution : Qnn
  mul_cert : ScaledEqCert
```

The `Qnn` type carries nonnegativity. `mul_cert` proves the reported contribution equals
`coeff * value` after denominator clearing.

## Row Certificate Record

Each generated row has:

```lean
inductive BranchBCase
  | tightZero
  | freePacketExchange
  | sparseM1BankLBYPASS
  | muNuk
  | muNukRepaired
  | detourResidual

structure RowId where
  nameHash : UInt64
  n : Nat
  m : Nat
  L : Nat

structure DirectRowCert where
  pressure_eq : ScaledEqCert
  finite_margin : ScaledGeCert

structure OpStepCert where
  opClass : DictClass
  eB_XS eM_XS eB_XO eM_XO : Int
  exchange_q : Int
  quad_eq : ScaledEqCert
  sigma_drop_eq : ScaledEqCert
  rho_a : Qnn
  rho_eq : ScaledEqCert
  pieces : List ConePiece
  pieces_sum_eq : ScaledEqCert

structure GateBCert where
  raw_rho : Qnn
  op_rho_sum : Qnn
  surplus : Qnn
  dominates_raw : ScaledEqCert  -- raw_rho + surplus = op_rho_sum
  steps : List OpStepCert

structure BranchBRowCert where
  id : RowId
  caseTag : BranchBCase
  direct : DirectRowCert
  gateB : Option GateBCert
```

For direct rows, `gateB = none`. For Gate-B burden rows, `gateB` contains the accepted
two-phase monotone telescope and dictionary decomposition.

## Required Row Checks

The generated Lean row proof establishes the same obligations as
`_codex_bankl_branchb_gateb_candidate_verify.py`:

1. pressure identity target equals the row term contribution sum;
2. finite row margin is nonnegative;
3. if `gateB = some cert`, every op quadruple satisfies
   `q = eB_XS - eM_XS - eB_XO + eM_XO`;
4. every op has `rho_a = 25 * max(0, q)`;
5. every op dictionary contribution sum equals `rho_a`;
6. op rho sum dominates the raw-to-final rho with nonnegative surplus;
7. direct rows have no pending Gate-B obligations.

These are all scalar integer or rational equalities after clearing denominators.

## Table-Level Certificate

The generator also emits a table summary certificate:

```lean
structure BranchBTableSummary where
  rows : Nat
  terms : Nat
  burdenRows : Nat
  opRows : Nat
  opSteps : Nat
  caseCounts : BranchBCase -> Nat
  counts_cert : ...
```

Expected constants:

- `rows = 14247`
- `terms = 19988`
- `burdenRows = 1062`
- `opRows = 926`
- `opSteps = 1852`
- `TIGHT_ZERO = 34`
- `FREE_PACKET_EXCHANGE = 3688`
- `SPARSE_M1_BANKL_BYPASS = 9463`
- `MU_NUK = 800`
- `MU_NUK_REPAIRED = 126`
- `DETOUR_RESIDUAL = 136`

The final generated theorem is:

```lean
theorem branchB_finite_table_ok : BranchBTableValid branchBTable := ...
```

`BranchBTableValid` is consumed by Claude's Branch-B assembly theorem, not by the graph
theory infrastructure directly.

## Python Transpiler Pipeline

New script:

`problems/23/writeup/_codex_branchb_jsonl_to_lean.py`

Phases:

1. Parse final JSONL with `Fraction`.
2. Re-run the exact Python checks already in
   `_codex_bankl_branchb_gateb_candidate_verify.py`.
3. Normalize each scalar identity by denominator clearing.
4. Emit:
   - a machine audit manifest:
     `tmp/branchb_lean_transpile_manifest_v1.json`
   - Lean support data shards:
     `problems/23/lean/Erdos23Delta0/Cert/BranchBData/ShardNN.lean`
   - a table import file:
     `problems/23/lean/Erdos23Delta0/Cert/BranchBTable.lean`
5. Emit a dry-run report with:
   - proof mode counts (`rfl` vs `norm_num`);
   - max literal list length;
   - max denominator;
   - row count and op count cross-checks.

## Pilot Before Full Emission

Before emitting all `14247` rows:

1. Generate a pilot shard containing:
   - the first row of each six-case class;
   - all distinct op-level core signatures from
     `tmp/bankl_completion_op_sequence_core_signatures_v1.json`;
   - the 4 known surplus rows.
2. Compile only the support file and pilot shard under Claude's FC toolchain.
3. If `by rfl` fails for literal integer sums, switch only those proofs to `by norm_num`.
4. After the pilot compiles, emit full shards.

## Trust Boundary

Lean will not parse JSON. The trust boundary is:

- Python exact verifier proves JSONL content matches the accepted artifact.
- Python transpiler emits literal Lean data and proof fields.
- Lean kernel checks the emitted arithmetic and table validity.

This matches the blueprint's "data plus generic reflective checker" route while avoiding
`native_decide`.

## Open Questions For Claude

1. Should `DictClass` preserve the final JSONL's accepted coarse classes exactly, or should
   the Lean enum refine them back to the prose dictionary classes in the Branch-B writeup?
2. Should the row table theorem expose only `BranchBTableValid`, or should it also expose
   per-case subtheorems such as `tightZero_rows_ok`, `muNuk_rows_ok`, and
   `gateB_rows_ok` for easier assembly imports?
3. Do you want the generated Lean data under `problems/23/lean/Erdos23Delta0/Cert/`, or in
   a separate generated directory to keep the hand-written Lean tree clean?

