# R53 adaptive edge-cap referee audit

## Executive verdict

| Item | Verdict | Exact condition / failure |
|---|---|---|
| Total **global** collision flow with unit capacity on actual `FreeHalf` keys implies `N^2 - 25|M| >= 0` | **TRUE** | Demand must be all `MinimumDemandCollisionHall.CollisionHalf`, every demand row must carry exactly one unit, and every sink must be an actual `MinimumDemandCollisionHall.FreeHalf`. The edge aggregate cap and integrality are unnecessary for this implication. |
| Stronger R53 count `collisionUnits + |I_act| <= FreePairs` | **TRUE, CONDITIONAL** | Requires pairwise-disjoint four-key blocks `K_e` contained in `FreeHalf`, one for every edge counted by `I_act`, plus `sum_{d,s in K_e} x d s <= 2`. The four-key/disjointness graph adapter is not in production Lean. |
| Reuse `ActiveScopedMinimumExchange.Demand` as the flow domain | **FALSE** | That domain contains only `ActiveCollisionHalf` plus active hit needs; inactive global collision mass is absent. A total flow on that domain need not bound `CollisionResidualIdentity.collisionMass`. |
| Use raw `CheckedMicroReservationLedger.PhysicalHalfKey` as sinks without a freeness realization | **FALSE** | `PhysicalHalfKey` has coordinates and a half bit but no `sourceX != sourceY` or `pairCount = 0` field. The finite countermodel below has a total raw-key flow and residual `-9`. |
| “Adaptive reservation is weaker than fixed `ScopedReserved`” | **LOCAL ONLY** | On an active-owner edge it is a strict relaxation. If the cap is imposed on every `activeEdges` entry, it is stricter on inactive-component edges, where `ScopedReserved` reserves nothing. The full production objects also have different demand types, so they are globally incomparable. |
| `FractionalCollisionFlowWithEdgeCaps` / `canonicalSoftEdgeCapFeasibleTuple_exists` | **ABSENT** | No declaration with either name, and no declaration carrying the required edge-group capacity contract, exists under `problems/23/lean/Erdos23Delta0`. |

## Exact counting proof

Fix a checked row choice `omega` and put

```text
n(x,y) := pairCount omega x y
C      := sum_(x,y) (n(x,y) - 1)             = collisionUnits G omega
Foff   := #{(x,y) | x != y and n(x,y) = 0}
Fall   := #{(x,y) | n(x,y) = 0}              = freeMass n
D      := CollisionHalf G omega
S      := FreeHalf G omega
```

The source definitions give

```text
|D| = 2*C                         (one `copy : Fin (n-1)` and `half : Fin 2`)
|S| = 2*Foff                      (one `half : Fin 2` for each distinct free ordered pair)
Foff <= Fall
collisionMass n = C.
```

Locations: `pairCount` and `collisionUnits` are
`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:78-89`;
`CollisionHalf` is
`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:54-62`;
`FreeHalf` is the *proof-carrying* source type at
`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:64-73`;
`freeMass` and `collisionMass` are
`problems/23/lean/Erdos23Delta0/CollisionResidualIdentity.lean:23-29`.

Let `x : D -> S -> Rat` satisfy

```text
(T1)  0 <= x d s
(T2)  sum_s x d s = 1                 for every d : D
(T3)  sum_d x d s <= 1                for every s : S
```

Eligibility support and edge caps may be added, but are not used below. Finite
sum interchange gives

```text
2*C = |D|
    = sum_d 1
    = sum_d sum_s x(d,s)               by T2
    = sum_s sum_d x(d,s)
   <= sum_s 1                          by T3
    = |S|
    = 2*Foff
   <= 2*Fall.
```

Hence `collisionMass n <= freeMass n`. If each selected row contributes 25
ordered-pair incidences, then
`CollisionResidualIdentity.residual_nonneg_of_collision_le_free` at
`problems/23/lean/Erdos23Delta0/CollisionResidualIdentity.lean:82-93` yields

```text
0 <= card(V)^2 - 25*m.
```

The exact signed identity used by that theorem is
`free_sub_collision_eq_residual` at
`problems/23/lean/Erdos23Delta0/CollisionResidualIdentity.lean:72-80`.
The production row count is
`CollisionCoveragePotential.totalPairIncidences_eq_twentyFive_mul_length` at
`problems/23/lean/Erdos23Delta0/Gamma/CollisionCoveragePotential.lean:219-253`.
No component owner, inactive collapse, bank token, `ScopedReserved`, or
integral matching occurs in this implication.

### Stronger edge-cost inequality

For each counted active undirected edge `e`, suppose `K_e subset S` has exactly
four elements, the `K_e` are pairwise disjoint, and

```text
sum_d sum_(s in K_e) x(d,s) <= 2.
```

Unit key caps on all remaining sources then give

```text
2*C = total flow
    <= (|S| - 4*|I_act|) + 2*|I_act|
     = 2*Foff - 2*|I_act|,
```

so `C + |I_act| <= Foff`. This is the precise version of
`WALL_ATTACK_R53_GPTPRO56.md:9-12,27-31`. It is stronger than the residual
bound, but it is not currently a Lean theorem.

## Four-key audit

| Required fact | Source facts | Verdict |
|---|---|---|
| An active edge is an undirected, nonloop graph edge absent from selected path support | `activeEdges` filters internal blue graph edges and excludes `selectedSupport`: `Gamma/MinimumDemandRowSelection.lean:91-101`; `activeGraph.Adj` normalizes it: `Gamma/ActiveScopedMinimumExchange.lean:28-39`. | Present as definitions. |
| Its two orientations each have `pairCount = 0` | `pairCount` counts co-occurrence, not path-edge occurrence: `Gamma/MinimumDemandRowSelection.lean:78-82`. A checked row is five distinct vertices, four blue path edges, and one bad closing edge: `CertGraph.lean:160-175`. Triangle-freeness is `CertGraph.lean:2398-2402`. These facts imply that a blue graph edge between two co-occurring row vertices must be a path edge, contradicting absence from `selectedSupport` (`rowPathEdges`/`selectedSupport`: `Gamma/MinimumDemandRowSelection.lean:68-76`). | Mathematically valid under `TriangleFree G` and checked selected rows; **missing compiled adapter**. No theorem states `e in activeEdges -> pairCount omega e.1 e.2 = 0`. |
| Exactly four actual source keys | Once both ordered pair counts are zero and endpoints differ, `FreeHalf` supplies `(u,v,0)`, `(u,v,1)`, `(v,u,0)`, `(v,u,1)` by `Gamma/MinimumDemandCollisionHall.lean:64-73`. | Conditional on the previous missing lemma. |
| Different active edges have disjoint four-key blocks | Physical keys retain ordered coordinates and half bit: `Gamma/CheckedMicroReservationLedger.lean:44-53`. `checkGraph` requires normalized, duplicate-free edges: `CertGraph.lean:20-26`. | Mathematically valid under `checkGraph G = true`; no packaged edge-block equivalence/cardinality theorem exists. |
| Raw physical keys are automatically free | `PhysicalHalfKey` has only `sourceX`, `sourceY`, `half`: `Gamma/CheckedMicroReservationLedger.lean:49-53`. Only `PhysicalHalfKey.ofFreeHalf` maps a proof-carrying source to a raw key: lines `65-72`; injectivity is lines `74-87`. | **False.** The reverse realization is a required field/lemma. |

Required production adapter, currently absent:

```text
activeEdgeFreeHalfBlock :
  checkGraph G = true -> TriangleFree G -> AllBadsChecked G c bads ->
  e in activeEdges G c omega ->
  {s : FreeHalf G omega | normEdge s.sourceX s.sourceY = e}.card = 4
```

The exact statement should additionally expose a disjoint block map if the
proof sums aggregate caps over `activeEdges.length`.

## Comparison with fixed reservations

| Axis | Global fixed object | Active-scoped fixed object | R53 adaptive object |
|---|---|---|---|
| Collision domain | All `CollisionHalf`: `Gamma/MinimumDemandCollisionHall.lean:120-125`. | `ActiveCollisionHalf` only, plus `ActiveHitNeed`: `Gamma/ActiveScopedMinimumExchange.lean:51-54,102-106`. | Must be **all** `CollisionHalf` for the direct residual proof. R53 does not define the type. |
| Fixed ban | `Reserved` bans half zero on every `activeEdges` key: `Gamma/MinimumDemandCollisionHall.lean:75-80`. | `ScopedReserved` bans half zero only when the key is an active-graph edge **and** `ActiveOwner sourceX`: `Gamma/ActiveScopedMinimumExchange.lean:125-132`. | No half is pre-banned; every key has cap 1 and a four-key edge block has aggregate cap 2. |
| Assignment | Integral injection, eligibility, unreserved proof: `Gamma/MinimumDemandCollisionHall.lean:118-125`. | Integral injection of the active demand, with `Available := EligibleOwner and not ScopedReserved`: `Gamma/ActiveScopedMinimumExchange.lean:144-158`. | Proposed fractional/integral grouped-cap flow; no declaration. |
| Inactive component edge | Global fixed `Reserved` still removes both half-zero orientations. | `ScopedReserved` removes zero keys because `ActiveOwner` is false. | If R53 caps every `activeEdges` entry, it removes two units and is stricter than the scoped object on this edge. |
| Count consequence | A global matching is enough after missing cardinal adapters. | Does not control inactive global collision mass. | Enough iff its demand and sink types are global/proof-carrying. |

### Strict local relaxation witness

One active-owner edge has keys
`K = {uv0, uv1, vu0, vu1}` and two obligations `a,b`, with only
`a--uv0` and `b--uv1` eligible. The adaptive assignment uses `uv0,uv1`, obeys
unit caps and aggregate cap 2. Fixed `ScopedReserved` deletes `uv0`, so no
total fixed matching exists. Thus the adaptive source rule is strictly weaker
on an active-owner edge.

### Global non-comparability witness

Let the same four-key block lie in an inactive component and give three
obligations three distinct eligible keys. `ScopedReserved` is false on all
four keys because of its `ActiveOwner` conjunct
(`Gamma/ActiveScopedMinimumExchange.lean:127-132`), so the fixed injection
exists. An aggregate edge cap 2 forbids the adaptive flow. Therefore the R53
model is not globally weaker if `I_act` means all entries of `activeEdges`.
It becomes a genuine relaxation of fixed reservation only if its capped edge
set is restricted to active-owner components and the demand domain is held
fixed.

## Integrality audit

| Claim | Verdict | Production status |
|---|---|---|
| The exact grouped-cap polytope is integral | **TRUE** when every key belongs to at most one active-edge block. Use the network `src -> demand (cap 1) -> key (cap 1) -> edge-group (cap 2) -> sink`; nonactive keys go directly to the sink. Integer max-flow yields an integral solution. | No such network or extraction theorem is compiled. |
| Existing `capacitatedBipartiteFlow_exists` proves this integrality | **FALSE** | `problems/23/lean/Erdos23Delta0/CapacitatedHallFlow.lean:150-164` produces a rational one-layer bipartite flow with one capacity per sink. It neither expresses simultaneous unit-key and group caps nor returns an integral flow. |
| Integrality is needed for the `N^2-25|M|` implication | **FALSE** | The finite-sum argument above uses only total demand and unit sink caps. |
| Prior physical-key ledger is the same object | **FALSE** | `PhysicalHalfExclusive` gives unit raw-key capacity at `Gamma/CheckedMicroReservationLedger.lean:151-155`, but there is no active-edge aggregate cap. Its `Checked` structure also requires `BaseKeyComponentCoherent` at lines `168-182`. |

## Ranked production gaps

| Rank | Gap | Exact Lean names / locations | Consequence |
|---|---|---|---|
| P0 | Global-domain contract absent | Nearest global domain: `MinimumDemandCollisionHall.CollisionHalf`, `Gamma/MinimumDemandCollisionHall.lean:54-62`. Existing active domain: `ActiveScopedMinimumExchange.ActiveCollisionHalf`, `Gamma/ActiveScopedMinimumExchange.lean:51-54`. Proposed `FractionalCollisionFlowWithEdgeCaps` is absent. | Reusing the active domain makes the claimed implication false. |
| P0 | Sink freeness/distinctness contract absent | Actual source: `MinimumDemandCollisionHall.FreeHalf`, `Gamma/MinimumDemandCollisionHall.lean:64-73`. Raw key lacking proofs: `CheckedMicroReservationLedger.PhysicalHalfKey`, `Gamma/CheckedMicroReservationLedger.lean:44-53`. | Raw-key capacity alone can prove a false bound; finite countermodel below. |
| P0 | Full-shore Hall inequality already contains the target count | `CollisionResidualIdentity.lean:82-85` explicitly warns that matching every collision debit into free sources proves the residual and cannot be an independent bank construction without stronger graph geometry. | `canonicalSoftEdgeCapFeasibleTuple_exists` is actual theorem progress only if proved from graph structure without assuming the residual/free-capacity inequality. A Hall proof that imports `N^2-25|M| >= 0` is circular. |
| P1 | Active-edge four-free-key/disjoint-block adapter absent | Definitions at `Gamma/MinimumDemandRowSelection.lean:68-101`; checked row facts at `CertGraph.lean:160-175`; triangle-free at `CertGraph.lean:2398-2402`; graph normalization at `CertGraph.lean:20-26`. | The stronger `C+|I_act|<=Foff` subtraction is not yet justified in Lean. |
| P1 | Cardinal/mass adapters absent | `CollisionHalf`, `FreeHalf`: `Gamma/MinimumDemandCollisionHall.lean:54-73`; masses: `CollisionResidualIdentity.lean:23-29`; list count: `Gamma/MinimumDemandRowSelection.lean:84-89`. | No compiled theorem currently turns a flow into `collisionMass <= freeMass`. Required equalities are `card CollisionHalf = 2*collisionUnits`, `card FreeHalf = 2*Foff`, and `collisionMass(pairCount)=collisionUnits`. |
| P1 | List-sum/Fintype-sum incidence adapter absent | `totalPairIncidences_eq_twentyFive_mul_length`: `Gamma/CollisionCoveragePotential.lean:219-253`; residual theorem expects a double Fintype sum: `CollisionResidualIdentity.lean:74-80`. | The exact `htotal` argument is not produced by the edge-cap modules. |
| P1 | `bads.length = |M|` adapter absent on the row-DB path | `CompleteShortestRowDB` has checked/nodup/coverage fields at `Gamma/MinimumDemandCollisionHall.lean:29-47`, but no length theorem. Existing `checkBankBlockCover_badCount` proves the equality only from a bank-block certificate at `CertGraph.lean:1379-1389`. | A direct edge-cap theorem reaches `25*bads.length`; reaching `25*badCount G c` still needs a non-bank database cardinality lemma or an explicit equality hypothesis. |
| P2 | Grouped-cap integrality/extraction absent | Existing rational result: `CapacitatedHallFlow.capacitatedBipartiteFlow_exists`, `CapacitatedHallFlow.lean:150-225`. Existing ordinary Hall/injection: `MinimumDemandCollisionHall.collisionMatching_nonempty_iff_hall`, `Gamma/MinimumDemandCollisionHall.lean:127-154`. | Needed only if downstream code requires an integral matching; not needed for scalar counting soundness. |
| P2 | Capped edge scope is unspecified | `activeEdges` is all off-support internal blue edges: `Gamma/MinimumDemandRowSelection.lean:91-101`; `ScopedReserved` additionally requires `ActiveOwner`: `Gamma/ActiveScopedMinimumExchange.lean:125-132`. | “Weaker than scoped reservation” has no global truth value until `I_act` is defined. |
| P3 | Selection theorem absent | R53 names `canonicalSoftEdgeCapFeasibleTuple_exists` at `WALL_ATTACK_R53_GPTPRO56.md:18-19,27-31`; no Lean declaration exists. | Corpus feasibility is search evidence, not a production theorem. |

## Explicit finite countermodel to a raw-key or active-scoped adapter

Let `V = Fin 4`, `m = 1`, and

```text
n(x,y) = 2  if 4*x+y < 9,
         1  otherwise.
```

Then all 16 ordered pairs are covered, exactly nine have one collision unit,
and

```text
sum_(x,y) n(x,y) = 25,
freeMass n          = 0,
collisionMass n     = 9,
|V|^2 - 25*m        = 16 - 25 = -9.
```

Take the sink carrier to be raw off-diagonal physical keys
`(x,y,h)` with `x != y`, not `FreeHalf`. There are `4*3*2 = 24` such keys.
Designate `{0,1}` as one active edge; its four-key block has aggregate cap 2.
There are 20 raw keys outside that block, so inject the 18 collision halves
into any 18 of them. Every key cap is 1 and the active-edge aggregate spend is
`0 <= 2`; eligibility may be the complete relation. This is a total edge-cap
flow but the target residual is negative. The only failed semantic condition
is that none of these raw keys is free (`n(x,y)>0` everywhere).

This is not a countermodel to the correctly typed theorem with sinks
`FreeHalf`; it proves that the raw-key-to-free-source production adapter is
logically necessary.

The arithmetic part was compiled through Lean stdin against
`CollisionResidualIdentity.lean` (exit code 0, no `native_decide`):

```lean
def n4 (x y : Fin 4) : Nat :=
  if x.1 * 4 + y.1 < 9 then 2 else 1

example : freeMass n4 = 0 := by
  norm_num [freeMass, n4, Fin.sum_univ_succ]

example : collisionMass n4 = 9 := by
  norm_num [collisionMass, n4, Fin.sum_univ_succ]

example : (∑ x : Fin 4, ∑ y : Fin 4, (n4 x y : ℤ)) = 25 := by
  norm_num [n4, Fin.sum_univ_succ]

example : ¬ 0 ≤ (Fintype.card (Fin 4) : ℤ)^2 - 25 * (1 : ℤ) := by
  norm_num
```

## R53 line audit

| R53 lines | Audit result |
|---|---|
| 7-9 | The fixed half-zero mechanism matches `ScopedReserved` only for actual `FreeHalf` keys on active-owner components (`ActiveScopedMinimumExchange.lean:125-132`). The rotor fixture itself is not a compiled theorem. |
| 9-12 | Final counting implication is sound under the global/proof-carrying flow contract. “Four keys” additionally needs triangle-free checked-row realization; “every active edge removes exactly 2” is false as a description of `ScopedReserved` on inactive components. |
| 12-13 | Adaptive-versus-fixed local separation is correct; the two-obligation witness above proves strictness. |
| 18-19 | `canonicalSoftEdgeCapFeasibleTuple_exists` is only a proposed name. No declaration or production adapter exists. |
| 27-31 | The cap model is mathematically a standard integral layered network when edge blocks are disjoint. It is not the one-layer rational theorem currently compiled. The stated count follows fractionally and does not require integrality. |
| 39-45 | Cross-tuple exposure arithmetic does not supply any field of a production edge-cap flow and does not discharge global demand conservation, source realization, or grouped capacities. |
| 47-51 | Corpus passes and probability estimates are not theorem progress. `erdos23_of_softCollisionFlow` is also absent. |

## Infrastructure versus theorem progress

| Classification | Compiled content | What it establishes |
|---|---|---|
| Actual theorem progress | `CollisionResidualIdentity.free_sub_collision_eq_residual`, `CollisionResidualIdentity.lean:74-80` | Exact signed `free - collision = N^2 - 25m` identity. |
| Actual theorem progress | `CollisionCoveragePotential.totalPairIncidences_eq_twentyFive_mul_length`, `Gamma/CollisionCoveragePotential.lean:221-253` | Every checked selected row contributes exactly 25 ordered incidences. |
| Interface infrastructure | `MinimumDemandCollisionHall.CollisionMatching` and Hall equivalence, `Gamma/MinimumDemandCollisionHall.lean:118-154` | Global fixed-reservation matching contract; no existence theorem from graph geometry. |
| Interface infrastructure | `ActiveScopedMinimumExchange.Matching`, `Gamma/ActiveScopedMinimumExchange.lean:144-177` | Active-scoped fixed-reservation matching contract; omits inactive collision mass. |
| Interface infrastructure | `CheckedMicroReservationLedger.PhysicalHalfKey` / `PhysicalHalfExclusive`, `Gamma/CheckedMicroReservationLedger.lean:44-87,151-155` | Canonical raw key identity and unit capacity; no freeness realization and no aggregate edge cap. |
| Interface infrastructure | `CapacitatedHallFlow.capacitatedBipartiteFlow_exists`, `CapacitatedHallFlow.lean:150-225` | Rational one-layer capacitated flow; no grouped cap and no integrality. |
| Not yet formalized | R53 grouped edge-cap flow, four-key graph adapter, count adapter, selection theorem | No production theorem beyond the prior interfaces. |

**Referee disposition:** the adaptive edge-cap implication is sound and
coherence/component/bank-free only in the global `CollisionHalf -> FreeHalf`
form. R53's present prose does not yet specify that form, does not define the
capped edge scope, and has no production adapter. The adaptive rule is a new
grouped-cap interface, strictly weaker than fixed reservation only on
active-owner edge blocks; it is not globally weaker than
`ActiveScopedMinimumExchange` as currently defined.
