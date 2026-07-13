# Pattern-5 switch/soundness referee report

## Verdict

Pattern 5 has a rigorous **static** soundness lemma, but the stronger switch/terminal-to-token claim in R30 does not follow from the listed hypotheses.

What is derivable is exactly:

1. a Pattern-5 source is a genuine `FreeHalf`;
2. if its first coordinate is outside the active scope, it is not `ScopedReserved` (requiring both coordinates outside makes this orientation-independent);
3. the proposed set `S = K(x) union K(y)` has `0 <= sigma G c S` because `c` is a maximum cut;
4. the chosen attachments and active-component equalities identify a proposed destination owner component.

Items 1-4 do **not** construct a `c5Base` token, prove component-preserving transport, or prove global no-double-spend. The exact 2943 fixture is a concrete countermodel to interpreting the switch as a state transition preserving the selected rows/components: its R30 switch has positive loss but destroys 1014 selected rows.

No theorem about Erdos #23 is claimed here.

## Audited production definitions

- `FreeHalf` contains bounded distinct coordinates, one half bit, and `pairCount omega x y = 0`: `Gamma/MinimumDemandCollisionHall.lean:66-73`.
- `ScopedReserved` is `half = 0`, adjacency in `activeGraph`, and `ActiveOwner sourceX`: `Gamma/ActiveScopedMinimumExchange.lean:125-132`.
- `ActiveOwner` means that one listed bad atom has both endpoints reachable to the vertex in the off-support `activeGraph`: `Gamma/ActiveScopedMinimumExchange.lean:41-49`.
- `MicroDemand` has two collision halves but **25 microcopies per hit need**: `Gamma/CommonBlueExtendedMatching.lean:99-110`.
- `ResidualSourceTokenization.Data.source` requires a component-preserving embedding
  `((Debit x Fin 2) + (Slot x Fin 25)) -> (Source x Fin 2)`: `ResidualSourceTokenization.lean:27-40`.
- The FullBank ledger separately requires `no_double_spend`, `no_cross_component_spend`, and source uniqueness: `Gamma/FullBankToLengthSurplusCharge.lean:199-211`.
- There is currently no compiled `CheckedQuiescentAttachmentBaseTerminal`, `CheckedTransferMatching`, `ActiveComponentFullBankCert`, or `checkedFivePatternMatching_to_activeFullBank`.

The current `CommonBlueExtendedMatching.MicroAvailable` relation contains owner eligibility and `not ScopedReserved`, but no component assignment or terminal-to-token data (`Gamma/CommonBlueExtendedMatching.lean:132-145`).

## Proof-ready static lemma tree

Fix checked `G,c,bads,omega`. Write

```text
A_omega(v) := ActiveOwner G c omega v
Q_omega     := B induced on {v | not A_omega(v)}
K(x)        := the Q_omega component of x
S(x,y)      := K(x) union K(y)
```

For `s : FreeHalf G omega`, let `x=s.sourceX`, `y=s.sourceY`. A precise Pattern-5 witness may record:

```text
not A_omega(x), not A_omega(y),
a in A_omega intersect N_B(K(x)),
b in A_omega intersect N_B(K(y)),
ActiveReachable(v,a), ActiveReachable(v,b),
0 < pairCount omega v a,
0 < pairCount omega v b.
```

Here `ActiveReachable(v,a)` and `ActiveReachable(v,b)` should use the literal `activeGraph`; comparing implementation-dependent component labels is insufficient.

### L1. Source availability

The `FreeHalf` fields already prove `x != y` and `pairCount omega x y = 0`. No triangle-free or attachment hypothesis is used.

### L2. Reservation exclusion

```lean
theorem quiescent_freeHalf_not_scopedReserved
    {s : FreeHalf G omega}
    (hx : Not (ActiveOwner G c omega s.sourceX)) :
    Not (ScopedReserved G c omega s) := by
  intro h
  exact hx h.2.2
```

Thus half 0 is available when `x` is quiescent; half 1 is available even without `hx`. Requiring both `x,y` quiescent makes the result stable under reversing the ordered source pair. Triangle-freeness is not used.

### L3. Maximum-cut loss

For every vertex list `S`, not specifically a quiescent component union,

```lean
theorem pattern5_sigma_nonneg
    (hG : checkGraph G = true) (hmax : IsMaxCut G c) (S : List Nat) :
    0 <= sigma G c S :=
  (sigmaNonneg_of_badCount_min G c hG hmax.valid hmax.min_bad) S
```

Therefore `0 <= sigma G c (S(x,y))`. This uses maximum-cut minimality and graph/cut well-formedness only. Triangle-freeness, quiescence, attachments, and source freeness are not used.

Important: `sigma >= 0` says flipping `S` cannot improve the cut. It does not say the flip preserves the maximum cut. Preservation would require `sigma = 0`. The R30 fixture has `sigma=26`, so its flipped cut is strictly worse.

### L4. Static Pattern-5 availability

Define `Pattern5Owner G c omega owner s` by the quiescent-component and attachment witness above. Then the only unconditional relation theorem is

```text
Pattern5Owner owner s -> not ScopedReserved s
```

together with the independent max-cut fact `0 <= sigma(S(x,y))`. This suffices to add a **static matching arc** if Pattern 5 is declared as a supplied relation. It does not justify a `c5Base` token.

## Exact 2943 preservation countermodel

I replayed `problems/23/writeup/_claude_r29_pattern5_gate.py` at the all-anchor tuple and separately enumerated every selected row against `K(3)` using the same exact integer state.

The accepted local Pattern-5 facts hold:

```text
n = 2943
|A_omega| = 19
|K(3)| = 1379
boundary(K(3)) = {1,55}
source (3,56): pairCount = 0
3,56 not in A_omega
both source halves unreserved
owners 0,1,2 active in component 0
pairCount(owner,1) = 676 for each owner
dB(K) = 702, dM(K) = 676, sigma(K) = 26
```

Nevertheless the flip does not preserve the row state:

```text
selected vertices in K(3)                 = 1041
selected rows meeting both K and its complement = 1014
selected support-edge occurrences crossing K  = 1352
listed bad edges crossing K                    = 676
selected rows invalid after flipping K         = 1014
```

The first explicit row is

```text
(3,1,0,2,29).
```

Its edge `(3,1)` is blue and belongs to `selectedSupport`, with `3 in K(3)` and `1 in A_omega`. Flipping `K(3)` makes `(3,1)` monochromatic, so this row is no longer a blue path. The same flip also turns 676 listed bad edges blue. Thus the old bad-edge database, selected rows, and active-component state cannot be reused after the switch.

This is a countermodel to either of the following implicit conclusions:

```text
P5 conditions -> selected rows remain valid after flip S
P5 conditions -> the flipped state has the same active components/bad atoms
```

It is not a countermodel to the static inequality `0 <= sigma(S)`.

## Hidden assumptions required by a token theorem

### 1. Static witness versus transition

The theorem must say which interpretation is intended.

- **Static:** `S` only witnesses a max-cut inequality in the original state. Then no row/component preservation should appear in the conclusion.
- **Transition:** the proof moves to `flipCut c S`. Then it must rebuild the bad-edge database, rows, active graph, demands, and source universe. R30's hypotheses are insufficient, and the 2943 switch is not even another maximum cut.

### 2. Component ownership

The existence of chosen attachments `a,b` in the owner's active component does not imply that every active boundary vertex of `K(x) union K(y)` lies in that component. A one-component token theorem needs either:

```text
forall z in S, forall q in A_omega,
  blue(z,q) -> ActiveReachable(owner,q)
```

or an explicit multi-component routing/ledger allocation for all boundary effects. Also, the source vertices are physically quiescent, while `ResidualSourceTokenization.Data.source_component` requires the matched source to carry the destination component. That component map must be constructed from the chosen global assignment; it is not present in `MicroAvailable`.

### 3. Reservations

Pattern 5 itself introduces no new reserved edge. This only proves an empty **new reservation deduction**. It does not by itself prove disjointness from all pre-existing reserved half keys; that is exactly the `not ScopedReserved` lemma and must be checked for each assigned half.

If later adapters add reservations, availability must be recomputed after deducting the union of reserved old source halves. No idempotence assumption is justified.

### 4. Global no-double-spend

Local terminal validity is per `(owner,source,witness)` and does not prevent:

- the same half key being assigned to two demands;
- the same half key being emitted once for each of several attachment witnesses;
- the same physical half being emitted in two destination components;
- a collision cancellation and a positive token using the same half.

The required condition is one global injection from actual demand microcopies to normalized source-half keys. Attachment witnesses must not be part of source identity. The source key should be the literal `(omega,x,y,half)` (or its typed equivalent), globally deduplicated before matching.

The FullBank ledger's current uniqueness is on `(component,kind,sourceId)`; by itself it can permit the same physical source ID once in each component. A Pattern-5 provider needs a stronger cross-component injection from emitted tokens/micro-spends to physical half keys.

### 5. Switch loss is not reusable capacity

R23/R30 say the switch loss is not spent. This restriction is necessary. In the 2943 repair, the same set `K(3)` annotates many source halves and is eligible for three owners. If `sigma(K)=26` were treated as budget, reusing the same switch would multiply one quantity. Therefore:

```text
sigma(S) is an admissibility annotation only;
all quantitative capacity comes from distinct FreeHalf micro-units.
```

Any theorem using `sigma(S)` quantitatively needs a separate injective switch-loss ledger and is not established here.

### 6. Production scale

The R30 gate matches one copy of each `ActiveHitNeed`; production uses `ActiveHitNeed x Fin 25`. One free half supplies one micro-unit, while one hit token aggregates 25 distinct micro-units. Consequently a proof-ready provider must supply:

```text
((ActiveCollisionHalf) + (ActiveHitNeed x Fin 25))
  injects into FreeHalf,
```

with every assigned half Pattern-5/old-pattern eligible and unreserved. Collision images cancel only; they emit no token. For each hit slot, its 25 images jointly fund one cap `25*unit = 1/(2|Omega|)` when `unit=1/(50|Omega|)`. A single Pattern-5 half must not be assigned cap `1/(2|Omega|)`.

### 7. Triangle-freeness

Triangle-freeness is an upstream condition validating the ell-5 row geometry. It is unused in L1-L3. In particular it does not, from the stated P5 fields alone, prove:

- distinct attachment edges;
- edge-disjoint corridors;
- exclusive attachment to the owner component;
- preservation of selected rows;
- global source injectivity.

Any claimed triangle-free mechanism must be stated as an additional graph lemma with one of these explicit conclusions.

## Minimal sound adapter theorem

A safe end-to-end statement should take Pattern 5 as a supplied, checked relation and require the following independent data:

1. `M : MicroMatching` for the union of old patterns and Pattern 5;
2. every Pattern-5 image satisfies the static witness and `not ScopedReserved`;
3. `M.assign` is globally injective on literal half keys;
4. `ComponentPreserving M vertexComp debitComp sourceComp`;
5. Pattern-5 has an empty reservation set, and assignment images avoid the union of reservations introduced by other terminal kinds;
6. a typed injective base-key map for hit slots into `CapSource.c5Base`;
7. 25 distinct assigned micro-sources per hit slot and positive `unit`;
8. FullBank `no_double_spend`, `no_cross_component_spend`, and typed source uniqueness.

Under 1-7, the existing equivalence/adapter pattern can construct `ResidualSourceTokenization.Data`; under 8 it can enter the FullBank ledger. None of 3-8 follows from the local quiescent attachment predicate alone.

## Reproducibility

Exact gate command:

```powershell
python problems/23/writeup/_claude_r29_pattern5_gate.py
```

It returned the exact all-anchor values `|K|=1379`, boundary `[1,55]`, loss `702-676=26`, and full-shore `19953/19953`.

Audited SHA-256 values:

```text
_claude_r29_pattern5_gate.py                    0F41C17952B34987777F91B94B69A4AB395859C11DE8F31B1C56688A75847DD1
ActiveScopedMinimumExchange.lean                6AA3FDD19D15A4A5231494C6B92F3659BFCF13CFA1F2D900B6F3857EC1CF019D
MinimumDemandCollisionHall.lean                 EA36FC95B8FAD743DC8C11DB510284F6C109CE77319378E47CA56EF40C3EB1A7
ResidualSourceTokenization.lean                 6509C4F9443BEBF66A0EEA6BE7C6DFA03C0DCD3F72A6575C188B191D0253000E
```

All new checks in this lane used integer counts only. No floating-point computation, `native_decide`, `sorry`, or theorem claim was used.
