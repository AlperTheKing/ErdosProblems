# Child 01 — core `CheckedTransferMatching` semantic audit

## Findings

### Bottom line

There is no production Lean declaration named `CheckedTransferMatching`, `CheckedTransferTrace`, `CheckedTransferEdge`, `TransferObligation`, `FreeHalfKey`, `CollisionHalfKey`, or `HitNeedKey`. A scoped exact-symbol search over `problems/23/lean/Erdos23Delta0/Gamma/*.lean` found none. These names occur only in planned prose: R19 lists the proposed stack and soundness chain (`problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md:29-34`); R20 explicitly calls the complete checker a “spec” (`problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:39-50`).

The actual compiled surfaces are:

1. collision-only `CanonicalCollisionHall.CollisionMatching`;
2. separate active-scoped `ActiveScopedMinimumExchange.Matching`, with collision plus HitNeed demands;
3. standalone Boolean common-blue and row-companion terminal checkers, not connected to either matcher.

No searched Gamma Lean file connects either matcher to banked tokens, `EndpointReserveHall`, or `ActiveComponentFullBankCert`. The goal’s `CheckedTransferMatching ... => banked token family` chain is a requirement, not current semantics (`GOAL_LOOP.md:16`); coordination describes compiling that stack as pending (`coordination/CLAUDE_TO_CODEX.md:13807-13810`).

### Row choices, counts, and nominal score

The selected row tuple is exactly

```lean
abbrev RowChoice (bads : List BadEdgeData) :=
  (i : Fin bads.length) -> Fin (bads.get i).rows.length
```

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:23-25`). Selected rows are `List.ofFn fun i => (bads.get i).rows.get (omega i)` (`.../MinimumDemandRowSelection.lean:58-61`), and co-occurrence is

```lean
def pairCount ... (omega : RowChoice bads) (x y : Nat) : Nat :=
  ((selectedRows omega).filter fun row =>
    decide (x ∈ row.verts ∧ y ∈ row.verts)).length
```

(`.../MinimumDemandRowSelection.lean:78-82`). The older executable score is `2 * collisionUnits G omega + 2 * (activeEdges G c omega).length` (`.../MinimumDemandRowSelection.lean:103-106`), with `collisionUnits` summing `pairCount omega x y - 1` over ordered pairs (`.../MinimumDemandRowSelection.lean:84-89`). `minDemandChoice` is a `noncomputable` finite minimizer (`.../MinimumDemandRowSelection.lean:108-114`), whose conclusion is `obligationScore ... (minDemandChoice ...).1 <= obligationScore ... eta` (`.../MinimumDemandRowSelection.lean:116-121`).

### Collision obligations and source slots

```lean
structure CollisionHalf (G : GraphData) ... (omega : RowChoice bads) where
  owner : Fin G.n
  other : Fin G.n
  copy : Fin (pairCount omega owner.1 other.1 - 1)
  half : Fin 2
```

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:54-62`). `copy` represents repeated-pair multiplicity; `half` gives two obligations per unit.

The only compiled free-half/source-token type is:

```lean
structure FreeHalf (G : GraphData) ... (omega : RowChoice bads) where
  sourceX : Fin G.n
  sourceY : Fin G.n
  half : Fin 2
  distinct : sourceX ≠ sourceY
  free : pairCount omega sourceX.1 sourceY.1 = 0
```

(`.../MinimumDemandCollisionHall.lean:64-73`). A `FreeHalf` value itself is the source slot; there is no separate source ID/key or token record. Old reservation is exactly `s.half.1 = 0 ∧ normEdge s.sourceX.1 s.sourceY.1 ∈ activeEdges G c omega` (`.../MinimumDemandCollisionHall.lean:75-80`).

### Base eligibility actually compiled

The prose pattern `sameFirst` is compiled as `SameOwner d s := s.sourceX = d.owner` (`.../MinimumDemandCollisionHall.lean:82-87`). It ignores `d.other`, `copy`, and both half fields.

Row companion is exactly:

```lean
def RowCompanion ... (d : CollisionHalf G omega)
    (s : FreeHalf G omega) : Prop :=
  0 < pairCount omega d.owner.1 s.sourceX.1 ∧
  0 < pairCount omega d.owner.1 s.sourceY.1 ∧
  0 ≤ sigma G c [s.sourceX.1, s.sourceY.1]
```

(`.../MinimumDemandCollisionHall.lean:89-97`). Source-pair freeness comes separately from `FreeHalf.free`.

The production union is only `Eligible := SameOwner d s ∨ RowCompanion G c d s`, followed by `Available := Eligible G c d s ∧ ¬Reserved G c omega s` (`.../MinimumDemandCollisionHall.lean:99-109`). There is no `CommonBad` disjunct. R20 says row companion “STRICTLY generalizes common-bad-neighbour” (`problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:26-32`), but no compiled theorem derives `RowCompanion` from bad adjacency. `commonBad` is only indirectly intended to be represented.

### Actual collision matcher and consumers

```lean
structure CollisionMatching ... (omega : RowChoice bads) where
  assign : CollisionHalf G omega → FreeHalf G omega
  injective : Function.Injective assign
  eligible : ∀ d, Eligible G c d (assign d)
  unreserved : ∀ d, ¬ Reserved G c omega (assign d)
```

(`.../MinimumDemandCollisionHall.lean:118-125`). It has no trace field and emits no token. Its exact theorem is `Nonempty (CollisionMatching G c omega) ↔ CollisionHallCondition G c omega` (`.../MinimumDemandCollisionHall.lean:135-154`), where the source neighborhood is `∃ d ∈ A, Available G c d s` (`.../MinimumDemandCollisionHall.lean:127-133`). This is equivalence, not graph-theoretic existence.

`MinimumDemandCollisionHall` merely abbreviates `Nonempty (CollisionMatching ... canonicalChoice)` (`.../MinimumDemandCollisionHall.lean:162-166`). `RealTwoRowExchangeComplete` is an abstract implication from `TriangleFree`, `IsMaxCut`, `BConnected`, and `CompleteShortestRowDB` to `TwoRowExchangeComplete` (`.../MinimumDemandCollisionHall.lean:190-199`). The reduction theorem consumes such a hypothesis (`.../MinimumDemandCollisionHall.lean:228-239`).

### Active-scoped obligations and matcher

`ActiveOwner` means some selected bad atom has both endpoints reachable to `v` in the off-support `activeGraph` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:28-49`). The scoped collision type is `{d : CollisionHalf G omega // ActiveOwner G c omega d.owner}` (`.../ActiveScopedMinimumExchange.lean:51-54`).

Endpoint obligations are:

```lean
noncomputable def hitNeedUnits ... (v : Fin G.n) : Nat :=
  activeDegree G c omega v - (G.n - selectedLoad omega v.1)
abbrev ActiveHitNeed ... :=
  Σ v : Fin G.n, Fin (hitNeedUnits G c omega v)
```

(`.../ActiveScopedMinimumExchange.lean:80-100`), where `selectedLoad omega v = 5 * pairCount omega v v` (`.../ActiveScopedMinimumExchange.lean:75-78`). The exact obligation universe and owner are:

```lean
abbrev Demand ... := ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega
def demandOwner ...
  | Sum.inl d => d.1.owner
  | Sum.inr h => h.1
```

(`.../ActiveScopedMinimumExchange.lean:102-123`). No `TransferObligation` exists.

Active reservation is `s.half.1 = 0 ∧ (activeGraph G c omega).Adj s.sourceX s.sourceY ∧ ActiveOwner G c omega s.sourceX` (`.../ActiveScopedMinimumExchange.lean:125-133`). The direct matcher is:

```lean
structure Matching ... (omega : RowChoice bads) where
  assign : Demand G c omega → FreeHalf G omega
  injective : Function.Injective assign
  available : ∀ d, Available G c d (assign d)
```

(`.../ActiveScopedMinimumExchange.lean:154-158`), with exact equivalence `Nonempty (Matching G c omega) ↔ HallCondition G c omega` (`.../ActiveScopedMinimumExchange.lean:167-179`). It has no trace or token output.

### Standalone checked terminals

The corrected C5 checker is common-**blue**, not `commonBad`. Its `TerminalData` is `(sourceX, sourceY, owner : Nat)` (`problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean:24-29`). `Valid` requires bounds/distinctness plus

```lean
blueb G c T.sourceX T.owner = true /\
blueb G c T.sourceY T.owner = true /\
dM G c T.switch + 2 <= dB G c T.switch
```

(`.../CheckedC5BaseTransfer.lean:35-43`). `check := decide (T.Valid G c)` and `check_eq_true_iff` are executable checker/soundness (`.../CheckedC5BaseTransfer.lean:45-56`). Consequences are `0 <= adjustedSurplus` (`.../CheckedC5BaseTransfer.lean:58-67`) and `(2 : Int) <= sigma G c T.switch` (`.../CheckedC5BaseTransfer.lean:69-75`). No theorem converts this terminal into `Eligible`, `Available`, `FreeHalf`, or a matcher edge.

The row checker’s executable pieces are `checkRowSelection` (`problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:22-32`), `pairFree` (`.../CheckedRowCompanionBaseTransfer.lean:34-41`), and `TerminalData.check := decide RawValid` (`.../CheckedRowCompanionBaseTransfer.lean:70-98`). `RawValid` requires bounds, distinct sources, selected row refs, literal `(owner,source)` witnesses, pair freeness, nonnegative `sigma`, and owner membership in the supplied `activeVertices` list (`.../CheckedRowCompanionBaseTransfer.lean:70-85`).

Its proof object repeats those fields (`.../CheckedRowCompanionBaseTransfer.lean:107-123`). The named constructor theorem has conclusion

```lean
CheckedRowCompanionBaseTerminal G c bads selected activeVertices T
```

from `T.check ... = true` (`.../CheckedRowCompanionBaseTransfer.lean:125-136`); converse is `check_eq_true_of_checked` (`.../CheckedRowCompanionBaseTransfer.lean:138-147`). `companion_rows_distinct` concludes `T.leftRow ≠ T.rightRow` (`.../CheckedRowCompanionBaseTransfer.lean:160-179`). No theorem turns this object into the pair-count `RowCompanion` relation or a matching edge.

## Dependency chain and consumers

1. `CheckedRowCompanionBaseTransfer` imports `CheckedC5BaseTransfer` (`.../CheckedRowCompanionBaseTransfer.lean:1`).
2. `MinimumDemandRowSelection` imports the row checker (`.../MinimumDemandRowSelection.lean:1`) but references none of its terminal/checker symbols: import-only dependency.
3. `MinimumDemandCollisionHall` imports row selection and defines the collision/free universes, two-disjunct eligibility, and `CollisionMatching` (`.../MinimumDemandCollisionHall.lean:1,54-140`).
4. `CollisionOwnerHallReduction` proves owner invariance `Available G c d s ↔ Available G c e s` when `d.owner=e.owner` (`problems/23/lean/Erdos23Delta0/Gamma/CollisionOwnerHallReduction.lean:56-62`) and collision Hall equivalent to owner Hall (`.../CollisionOwnerHallReduction.lean:130-136`).
5. `TwoRowRectangleExchange.HallFailureHasDescent` consumes `¬Nonempty (CollisionMatching G c omega)` as an abstract premise (`problems/23/lean/Erdos23Delta0/Gamma/TwoRowRectangleExchange.lean:193-208`); its final reduction consumes `RealHallFailureHasDescent` and concludes `MinimumDemandCollisionHall` (`.../TwoRowRectangleExchange.lean:218-228`).
6. `ActiveScopedMinimumExchange` imports `TwoRowRectangleExchange` (`.../ActiveScopedMinimumExchange.lean:1`), reuses `CollisionHalf`/`FreeHalf`, and defines a new `Demand`, `Available`, and `Matching`. `MinimumGlobalChoiceActiveScopedHall` is exactly `Nonempty (Matching ... canonicalChoice)` (`.../ActiveScopedMinimumExchange.lean:220-223`). `realMinimumGlobalChoiceActiveScopedHall_of_descent` takes `RealHallFailureHasMonotoneOneRowDescent` as an argument (`.../ActiveScopedMinimumExchange.lean:239-247`); it does not provide it.
7. `ActiveScopedOwnerHallReduction` builds owner demand/source sets from `Demand`, `FreeHalf`, and `Available` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean:22-38`), proves `Nonempty (Matching G c omega) ↔ ScopedOwnerHallCondition G c omega` (`.../ActiveScopedOwnerHallReduction.lean:121-126`), and identifies matching failure with an owner-shore defect (`.../ActiveScopedOwnerHallReduction.lean:128-137`).
8. No production FullBank consumer of either matcher was found. R20’s `checkedBaseCorridorPruneMatching_to_activeFullBank` is planned prose (`problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:47-50`).

## Comparison with `ActiveScopedMinimumExchange.Available`

The exact active predicate is:

```lean
def EligibleOwner ... (owner : Fin G.n) (s : FreeHalf G omega) : Prop :=
  s.sourceX = owner ∨
    (0 < pairCount omega owner.1 s.sourceX.1 ∧
     0 < pairCount omega owner.1 s.sourceY.1 ∧
     0 ≤ sigma G c [s.sourceX.1, s.sourceY.1])
def Available ... (d : Demand G c omega) (s : FreeHalf G omega) : Prop :=
  EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s
```

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-147`).

| Item | Status in active `Available` | Exact comparison |
|---|---|---|
| Collision obligations | Present, scoped | `Demand.inl` admits only `ActiveOwner` collision halves (`.../ActiveScopedMinimumExchange.lean:51-54,102-106`). |
| HitNeed | Present | `Demand.inr` is the dependent residual `ActiveHitNeed` fiber (`.../ActiveScopedMinimumExchange.lean:80-106`). |
| `FreeHalf` | Present, reused | Matching codomain is the collision module’s `FreeHalf`; no key/token type (`.../ActiveScopedMinimumExchange.lean:154-158`). |
| `sameFirst` | Present inline | First disjunct is exactly `s.sourceX = owner` (`.../ActiveScopedMinimumExchange.lean:136-142`). |
| `commonBad` | Absent; indirect at most | No bad-edge adjacency occurs. A common-bad pair works only if it satisfies both positive `pairCount` tests and `sigma≥0`; no implication theorem was found. |
| `rowCompanion` | Present inline | Second disjunct is the pair-count/sigma predicate (`.../ActiveScopedMinimumExchange.lean:139-142`). |
| Corrected common-blue C5 terminal | Absent | No `blueb` or `dM+2≤dB` condition. |
| Checked row terminal object | Absent | No row refs, `pairFree`, selection checker, or checked proof object. |
| Transfer/prune traces | Absent | `Matching` contains only `assign`, `injective`, `available` (`.../ActiveScopedMinimumExchange.lean:154-158`). |
| Bank token kind/capacity/support/sourceId | Absent | None is a field of `Demand`, `Available`, or `Matching`. |

R29 is explicitly a falsifier to this selector/matching route, not to Erdős #23 (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:3-12`). It states that the abstract interface remains valid but its real-graph provider is false and full-bank capacity is absent from active-scoped `FreeHalf` matching (`.../R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`).

## Executable implementations

These are audit/gate scripts, not production Lean.

### Explicit three-pattern gate

`_claude_r22_89_gate.py` builds ordered co-occurrence counts, `badnb`, row `companions`, collision demand, and free ordered cells (`problems/23/writeup/_claude_r22_89_gate.py:98-128`). Its exact function is:

```python
def reach(v, x, y):
    if x == v: return True
    if x != y and x in badnb[v] and y in badnb[v] and loss({x,y}) >= 0: return True
    if x != y and x in companions[v] and y in companions[v] and loss({x,y}) >= 0: return True
    return False
```

(`.../_claude_r22_89_gate.py:129-134`): same-first/same-owner, `commonBad`, then `rowCompanion`. It constructs a Dinic network from owner capacities to free ordered-pair cells of capacity two (`.../_claude_r22_89_gate.py:135-178`). This is the cleanest executable with all three explicit branches.

### Staged aggregate gate

`_claude_r20_staged_matching_gate.py.run` computes stage-1 residual from exact `Fraction` collision/free expectations and `hitneed` (`problems/23/writeup/_claude_r20_staged_matching_gate.py:144-162`), stage 2 over `badnb[v] × badnb[v]` with `2*free_mass` (`.../_claude_r20_staged_matching_gate.py:163-183`), and stage 3 over deterministic row companions (`.../_claude_r20_staged_matching_gate.py:184-209`). It is fixture-specific aggregate accounting, not a general injection; its header says prune is not implemented (`.../_claude_r20_staged_matching_gate.py:1-6`).

### Current R29 reconstruction

`rebuild_owner_hall.py.rebuild_scope` rebuilds selected rows, ordered pair counts, active components, collision, and truncated-Nat HitNeed (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:52-97`). `owner_sources` uses:

- `companions[o] = {x | pair[o,x] > 0}`;
- `masks[(x,y,h)]`, owner-availability bitmasks;
- `reason[(x,y,h)]`, bit 1 same-first and bit 2 row-companion (`.../rebuild_owner_hall.py:100-135`).

The same-first loop uses `(o,y,h)` with `pair[o,y]==0` and excludes active half-zero reservation (`.../rebuild_owner_hall.py:110-119`). The row-companion loop requires both coordinates in `companions[o]`, distinct/free coordinates, exact integer `sigma2≥0`, and the same reservation (`.../rebuild_owner_hall.py:120-134`). There is no explicit `commonBad` branch; it is represented only through the broader companion test. The emitted schema is “ordered FreeHalf source triples” (`.../rebuild_owner_hall.py:153-173`). `reason_mask` is an edge classification, not a transfer trace.

### Older common-blue executable

`_codex_r19_global_base_census.py.global_candidates` has same-owner sources (`problems/23/writeup/_codex_r19_global_base_census.py:62-67`), then a two-**blue**-neighbor `dM+2≤dB` `c5Base` branch (`.../_codex_r19_global_base_census.py:68-78`), and optional row companions (`.../_codex_r19_global_base_census.py:79-89`). That middle branch implements `CheckedC5BaseTransfer.Valid`, not `commonBad`. `full_matching` is an augmenting-path injection over source triples (`.../_codex_r19_global_base_census.py:93-120`).

No executable found defines trace concatenation, prune transport, component evidence per edge, or token emission.

## Contradictions / ambiguities

1. Goal and R19/R20 specify `CheckedTransferMatching`; production has only direct matchers.
2. The named three-pattern relation becomes only two disjuncts in both Lean `Available` predicates; `commonBad` has no named predicate or subsumption theorem.
3. “Common” drifts: `CheckedC5BaseTransfer` means common-blue plus reserved-edge surplus (`.../CheckedC5BaseTransfer.lean:35-43`), while Python `commonBad` means two bad neighbors (`.../_claude_r22_89_gate.py:116-133`).
4. The checked row terminal is disconnected from pair-count eligibility despite being transitively imported.
5. `obligationScore = 2*collisionUnits + 2*|activeEdges|` (`.../MinimumDemandRowSelection.lean:103-106`) is not active `Demand` cardinality: HitNeed is slack-reduced and collisions are owner-scoped (`.../ActiveScopedMinimumExchange.lean:51-106`). The later `scopedObligationScore := Fintype.card (Demand G c omega)` is different (`.../ActiveScopedMinimumExchange.lean:249-253`).
6. Active real descent is an abstract hypothesis consumed by reductions; R29 falsifies its real provider for the current score (`.../R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`).
7. No compiled FullBank consequence follows from either matching structure.

## Unresolved gaps

- Production definitions of checked obligation keys, traces, matching, and emitted tokens are absent.
- No theorem connects either checked terminal to direct eligibility.
- No theorem proves `commonBad` is subsumed by row companion under complete row-database hypotheses.
- No checked prune trace/injective slot-transport implementation was found.
- No matcher-to-`EndpointReserveHall`/FullBank consumer was found.
- The global `obligationScore` and active `scopedObligationScore` selectors must not be interchanged.

## Commands run

All searches were read-only. Two initial broad recursive searches timed out and were replaced by these scoped commands.

```powershell
rg -n "^" tmp/fanout/r29_fullbank_semantics/COMMON.md
rg -n "^" GOAL_LOOP.md
rg -n "^" problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
rg -n -C 4 "CheckedTransferMatching|sameFirst|commonBad|rowCompanion|TransferObligation|FreeHalfKey|ActiveScopedMinimumExchange" coordination/CLAUDE_TO_CODEX.md
rg -n -C 8 "FreeHalfKey|CollisionHalfKey|HitNeedKey|TransferObligation|TransferTrace|CheckedTransferMatching|sameFirst|commonBad|rowCompanion|transferToken" problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md
rg -n "^" problems/23/lean/Erdos23Delta0/Gamma/{MinimumDemandRowSelection,MinimumDemandCollisionHall,CheckedC5BaseTransfer,CheckedRowCompanionBaseTransfer,ActiveScopedMinimumExchange,ActiveScopedOwnerHallReduction,CollisionOwnerHallReduction,TwoRowRectangleExchange}.lean
Select-String -Path problems/23/lean/Erdos23Delta0/Gamma/*.lean -SimpleMatch -Pattern CheckedTransferMatching,TransferObligation,FreeHalfKey,CollisionHalfKey,HitNeedKey,TransferTrace,sameFirst,commonBad,rowCompanion
Select-String -Path problems/23/lean/Erdos23Delta0/Gamma/*.lean -SimpleMatch -Pattern ActiveComponentFullBankCert,EndpointReserveHall_to_fullBank,checkedTransferMatching_to_activeFullBank,checkedBaseCorridorPruneMatching_to_activeFullBank,CheckedTransferMatching,CheckedTransferTrace
rg -l -i -S "samefirst|sameowner|commonbad|rowcompanion" problems/23/writeup tmp/fanout/r29_gate tmp/fanout/global_min_proof -g "*.py"
rg -n "^" problems/23/writeup/_claude_r22_89_gate.py
rg -n "^" problems/23/writeup/_claude_r20_staged_matching_gate.py
rg -n "^" problems/23/writeup/_codex_r19_global_base_census.py
rg -n "^" tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
rg -n -S "\bsorry\b|\badmit\b|native_decide|sorryAx" <eight cited Lean files>
Get-FileHash -Algorithm SHA256 -LiteralPath <each cited source>
```

The forbidden-token search returned no hits for all eight cited Lean files. No Lean build was run: this was a read-only semantic audit, not a compilation audit. The active goal was accessible through the verbatim goal block in `GOAL_LOOP.md:10-17`; no separate attachment interface was exposed.

## Exact SHA-256 hashes of cited sources

```text
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
bfb75636d5e11b7f3d251cb20a64a5227f5b870938f1d1b715f38d400903adfc  problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md
cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5  problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md
e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean
ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0  problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean
84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
6a4d47533d10e4b04eb19cda0d0554658abd434c94c04566a01916708a90e8f0  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean
cc91b2629f6518758ed3cc1a5f3f1dca1b0c95a88efae243978a060e23809d7d  problems/23/lean/Erdos23Delta0/Gamma/CollisionOwnerHallReduction.lean
6afe14d3a7b69b5c0a8193325896aea2061fb3c54965642b73f8a95200255258  problems/23/lean/Erdos23Delta0/Gamma/TwoRowRectangleExchange.lean
6ef8a3af62b615791ccaf4e17bd1def4aeec59ec5dea8a975a0ae5891d4a2338  problems/23/writeup/_claude_r20_staged_matching_gate.py
80191648ac38b353df13cf3ca700cecb86b6f683e80584eea2296f841a7df5d4  problems/23/writeup/_claude_r22_89_gate.py
b49e9a2add265052605ac412449b9fb12b1b879cc67e254b68189db7b831a737  problems/23/writeup/_codex_r19_global_base_census.py
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
```
