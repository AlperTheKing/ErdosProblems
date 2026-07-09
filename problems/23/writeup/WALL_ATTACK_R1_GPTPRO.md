# WALL ATTACK — GPT-Pro reply 1 (2026-07-09, new thread 6a4f4bd6, harvested verbatim via clipboard)

*Question asked: attack THE WALL (Ell5FullBankRelaxedCover_globalPackage_exists) — induction on minimal
obstruction vs endpoint-singleton construction vs dual squeeze; produce Lean-ready statements against the
compiled module surface; no invented APIs; banked form only (no η).*

**[CLAUDE gate status: reply archived verbatim below. Verdict ledger**
- Route chosen by GPT-Pro: kill the Farkas dual via a DUAL SQUEEZE certificate restricted to three cut
  classes (singleton / quotient-closed γ-free / NEW: bank-rooted full-escape quotient cuts).
- Consistency check vs my searches: "I did not find a rational dual falsifier" — consistent with my
  _claude_rcc_dual_search.py (735 configs, 0 falsifiers).
- The bookkeeping layer (BankedWallLP + DualSqueeze + noStrictDual_of_checkedDualSqueeze) is pure finite
  LP weak-duality algebra — I am compiling it as BankedWallLPCore.lean (no sorry, full proof).
- The HARD CORE isolated: RootedEscapeSqueeze_exists_wall = Phase-3 closure lemma
  (deficientPortSet_has_rooted_or_gammaFree_cut) + Phase-4 patch loop termination.
- m=9 double-star treated as a bank-rooted base case (Defect 25 vs DoorCap ≥ 300) — matches my 24-vtx CE
  exact data (defect 25 in surplus units; bank absorbs).
- Falsifier format sharpened (§10): checked strict banked dual on a graph-realizable minimal full-closure
  obstruction — matches the GOAL's decisive-falsifier clause.**]

---

I would attack the wall through **LP duality**, not induction. I did not find a rational dual falsifier. The most promising missing ingredient is a specific extra cut class:

> **bank-rooted full-escape quotient cuts**: cuts obtained from a union of components of `B \ F`, closed under forced ell-5 escape, with all off-support load legally routed to one globally labelled bank root or to the root's sink neighborhood.

These are the cuts that should close the gap left by singleton domination plus gamma-free quotient cuts.

Below is the full reduction I would put in the Lean design. The remaining real theorem is not "cover exists" again; it is a dual-specific uncrossing/squeeze lemma using only singleton, quotient-closed, and bank-rooted escape cuts.

---

# 0. Honest evaluation of the three candidate routes

## 0.1 Induction on the minimal obstruction is not the main route

Minimality gives the useful identity

```text
|S| = |E_short(S)| + 1
```

and every proper full-closure subobject is nonviolating. But the known `no private edge` fact kills the naive induction step.

Removing one atom `a` usually does **not** remove a short edge:

```text
E_short(S \ {a}) = E_short(S)
```

so the smaller object is tight, not slack:

```text
|S \ {a}| = |E_short(S)|.
```

A cover of `S \ {a}` may saturate every in-support short edge. To add `a`, every cut separating `a` still crosses already saturated support geometry, unless one has a banked escape patch. That patch is essentially the wall again.

So the induction extension fails exactly at:

```lean
-- desired but generally false
∀ a ∈ S,
  ∃ patch,
    covers a
    ∧ adds no in-support congestion on saturated F
    ∧ routes all new off-support load to unused bank
```

The double-star `m = 9` anchor is the warning example: removal leaves the shared corridor geometry tight. The verified 24-vertex realization is bank-absorbable, but not by a bare inductive slack argument.

Conclusion: induction may become a proof of a later structural lemma, but it is not the clean wall proof.

---

## 0.2 Endpoint-singleton construction is a strong special case, not the whole wall

The useful special construction is:

```lean
structure EndpointSingletonCoverData
    (O : MinimalFullClosureObstruction G cut rows cage) where
  Endpoint : Type
  endpointFintype : Fintype Endpoint
  endpointDecEq : DecidableEq Endpoint

  endpointCut : Endpoint → CutAtom O

  incidentAtom : Endpoint → O.Atom → Bool
  incidentShort : Endpoint → O.ShortEdge → Bool

  chosen : Endpoint → Bool

  coversAtom :
    ∀ a : O.Atom,
      1 ≤
        ∑ v : Endpoint,
          if chosen v && incidentAtom v a then (1 : Rat) else 0

  shortCongestion :
    ∀ f : O.ShortEdge,
      (∑ v : Endpoint,
        if chosen v && incidentShort v f then (1 : Rat) else 0) ≤ 1

  routedDoorLoad :
    Endpoint → O.BankSink → Rat

  routedDoorLoad_nonneg :
    ∀ v s, 0 ≤ routedDoorLoad v s

  routedDoorLoad_legal :
    ∀ v s,
      routedDoorLoad v s ≠ 0 →
        O.LegalSink (endpointCut v) s

  endpointLoadCovered :
    ∀ v,
      chosen v = true →
        O.OffSupportLoad (endpointCut v)
          ≤ ∑ s : O.BankSink, routedDoorLoad v s

  sinkCapacity :
    ∀ s : O.BankSink,
      (∑ v : Endpoint,
        if chosen v then routedDoorLoad v s else 0)
        ≤ O.BankCap s
```

Then the soundness theorem is pure bookkeeping:

```lean
theorem endpointSingletonCoverData_sound
    {O : MinimalFullClosureObstruction G cut rows cage}
    (D : EndpointSingletonCoverData O) :
    ∃ b : FullBankRelaxedCoverBundle,
      checkFullBankRelaxedCoverBundle O b = true :=
by
  -- Construct `lam` by:
  --
  --   lam X = number of chosen endpoints v with endpointCut v = X.
  --
  -- Construct `q` from `routedDoorLoad`.
  --
  -- Coverage is `coversAtom`.
  -- In-support congestion is `shortCongestion`.
  -- Sink capacity is `sinkCapacity`.
  -- Legal incidence is `routedDoorLoad_legal`.
  --
  -- No eta term appears.
  sorry
```

This explains why the construction works on `C5[t]`, `CP11`, and the double-star anchor: one endpoint class is an independent transversal of the relevant footprint, and the induced singleton off-support load is door-bankable.

But this construction can fail in two ways:

```text
(1) selector failure:
    no endpoint side hits every atom while selecting at most one endpoint
    across every short support edge;

(2) bank-routing failure:
    the selected endpoint cuts produce off-support ports whose legal
    sink neighborhood does not have enough door/vertexSlack/C5/prune capacity.
```

The known minimality facts do not by themselves rule out selector-parity failures. They control support sizes and private-edge behavior, but they do not state a signed-balanced endpoint-transversal theorem. Therefore this route needs an additional hard selector theorem.

Conclusion: endpoint singletons should be kept as an anchor/provider, but not as the wall's top proof.

---

# 1. Chosen route: kill the Farkas dual

The compiled `BankedCutDominationCore` already has the exact Farkas equivalence. Use it.

The right shape is:

```text
primal bundle exists
  ⇔
no strict banked dual witness exists.
```

The wall becomes:

```text
Every strict dual witness is impossible.
```

The impossibility proof should not attempt constant congestion, atom multiplicity bounds, bare support expansion, or local eta. It should derive a contradiction by summing selected dual inequalities.

The selected inequalities should come from three cut classes:

```text
A. endpoint/singleton cuts,
B. gamma-free quotient cuts in components of B \ F,
C. bank-rooted full-escape quotient cuts.
```

Class C is the missing one.

---

# 2. Lean-ready LP interface

I would add this as a small abstract wall-LP layer. The existing obstruction-specific extractor can instantiate it.

```lean
namespace Erdos23Delta0.Wall

open scoped BigOperators

abbrev Q := Rat

/--
A banked wall LP instance.

Important: `Cut` is a routed cut atom. Two equal vertex shores with
different legal routing profiles may be distinct `Cut` values.

The primal variables are:

* `lam : Cut → Rat`;
* `q : Port → Sink → Rat`.

The dual variables are:

* `alpha : Atom → Rat`;
* `beta  : Short → Rat`;
* `gamma : Port → Rat`;
* `delta : Sink → Rat`.

No eta, local eta, or cage eta occurs anywhere.
-/
structure BankedWallLP where
  Cut : Type
  Atom : Type
  Short : Type
  Port : Type
  Sink : Type

  cutDecEq : DecidableEq Cut
  atomDecEq : DecidableEq Atom
  shortDecEq : DecidableEq Short
  portDecEq : DecidableEq Port
  sinkDecEq : DecidableEq Sink

  cutFintype : Fintype Cut
  atomFintype : Fintype Atom
  shortFintype : Fintype Short
  portFintype : Fintype Port
  sinkFintype : Fintype Sink

  /-- Cut `X` separates atom/row `a`. Usually 0 or 1. -/
  cov : Cut → Atom → Q

  /-- Cut `X` uses in-support short edge `f`. Usually 0 or 1. -/
  useShort : Cut → Short → Q

  /-- Cut `X` produces off-support load port `p`. -/
  cutPort : Cut → Port → Q

  /-- Legal routing arc from off-support port to bank sink. -/
  legal : Port → Sink → Prop
  legalDecidable : ∀ p s, Decidable (legal p s)

  /-- Bank capacity. Door/vertexSlack/C5Base/prune only. -/
  cap : Sink → Q

  sinkKind : Sink → CapKind
  sinkSourceId : Sink → Nat
```

The primal feasibility object is:

```lean
namespace BankedWallLP

variable (I : BankedWallLP)

local instance : DecidableEq I.Cut := I.cutDecEq
local instance : DecidableEq I.Atom := I.atomDecEq
local instance : DecidableEq I.Short := I.shortDecEq
local instance : DecidableEq I.Port := I.portDecEq
local instance : DecidableEq I.Sink := I.sinkDecEq

local instance : Fintype I.Cut := I.cutFintype
local instance : Fintype I.Atom := I.atomFintype
local instance : Fintype I.Short := I.shortFintype
local instance : Fintype I.Port := I.portFintype
local instance : Fintype I.Sink := I.sinkFintype

structure Primal where
  lam : I.Cut → Q
  q : I.Port → I.Sink → Q

  lam_nonneg :
    ∀ X, 0 ≤ lam X

  q_nonneg :
    ∀ p s, 0 ≤ q p s

  q_legal :
    ∀ p s, q p s ≠ 0 → I.legal p s

  coverage :
    ∀ a : I.Atom,
      1 ≤ ∑ X : I.Cut, lam X * I.cov X a

  shortCongestion :
    ∀ f : I.Short,
      (∑ X : I.Cut, lam X * I.useShort X f) ≤ 1

  portRouted :
    ∀ p : I.Port,
      (∑ X : I.Cut, lam X * I.cutPort X p)
        ≤ ∑ s : I.Sink, q p s

  sinkCapacity :
    ∀ s : I.Sink,
      (∑ p : I.Port, q p s) ≤ I.cap s
```

The dual is the exact projected Farkas dual of this LP:

```lean
structure Dual where
  alpha : I.Atom → Q
  beta : I.Short → Q
  gamma : I.Port → Q
  delta : I.Sink → Q

def cutAlpha (d : I.Dual) (X : I.Cut) : Q :=
  ∑ a : I.Atom, I.cov X a * d.alpha a

def cutBeta (d : I.Dual) (X : I.Cut) : Q :=
  ∑ f : I.Short, I.useShort X f * d.beta f

def cutGamma (d : I.Dual) (X : I.Cut) : Q :=
  ∑ p : I.Port, I.cutPort X p * d.gamma p

def totalAlpha (d : I.Dual) : Q :=
  ∑ a : I.Atom, d.alpha a

def totalBeta (d : I.Dual) : Q :=
  ∑ f : I.Short, d.beta f

def totalDeltaCap (d : I.Dual) : Q :=
  ∑ s : I.Sink, I.cap s * d.delta s

def Dual.Checked (d : I.Dual) : Prop :=
  (∀ a : I.Atom, 0 ≤ d.alpha a)
  ∧ (∀ f : I.Short, 0 ≤ d.beta f)
  ∧ (∀ p : I.Port, 0 ≤ d.gamma p)
  ∧ (∀ s : I.Sink, 0 ≤ d.delta s)
  ∧ (∀ s : I.Sink, 0 ≤ I.cap s)

  /-- D1: one inequality for every routed cut atom. -/
  ∧ (∀ X : I.Cut,
      I.cutAlpha d X ≤ I.cutBeta d X + I.cutGamma d X)

  /-- D2: legal port-to-sink routing dual inequality. -/
  ∧ (∀ p : I.Port, ∀ s : I.Sink,
      I.legal p s → d.gamma p ≤ d.delta s)

def Dual.StrictGap (d : I.Dual) : Prop :=
  I.totalBeta d + I.totalDeltaCap d < I.totalAlpha d

def checkDual (d : I.Dual) : Bool :=
  decide d.Checked

theorem checkDual_sound
    {d : I.Dual}
    (hd : I.checkDual d = true) :
    d.Checked :=
by
  simp [checkDual] at hd
  exact hd
```

The compiled Farkas bridge should be used in this shape:

```lean
/--
This should be a thin wrapper around the compiled
`BankedCutDominationCore` Farkas equivalence.
-/
theorem primal_exists_of_no_strict_dual
    (hNoDual :
      ∀ d : I.Dual,
        I.checkDual d = true →
        ¬ d.StrictGap) :
    ∃ P : I.Primal, True :=
by
  -- Call the compiled exact Farkas equivalence.
  sorry

end BankedWallLP
```

---

# 3. The dual squeeze certificate

This is the central algebraic gadget. It is dual-specific, so it is weaker than constructing a primal bundle directly.

```lean
namespace BankedWallLP

variable (I : BankedWallLP)

/--
Cut classifier used only to restrict the proof.

The wall proof should produce squeezes using only:

* singleton endpoint cuts;
* quotient-closed gamma-free cuts;
* bank-rooted full-escape quotient cuts.
-/
inductive WallCutKind where
  | singleton
  | quotientClosed
  | bankRootedClosure
  | other
deriving DecidableEq, Repr

structure RootedCutClassifier where
  kind : I.Cut → WallCutKind

def RootedCutClassifier.Allowed
    (C : I.RootedCutClassifier) (X : I.Cut) : Prop :=
  C.kind X = WallCutKind.singleton
  ∨ C.kind X = WallCutKind.quotientClosed
  ∨ C.kind X = WallCutKind.bankRootedClosure

/--
A dual squeeze is a nonnegative combination of D1 cut inequalities,
together with an explicit legal routing of the resulting port coefficients
to bank sinks.

It is not a primal cover: the first inequality only dominates the
specific dual weight `alpha`, not every atom uniformly.
-/
structure DualSqueeze
    (C : I.RootedCutClassifier)
    (d : I.Dual) where
  theta : I.Cut → Q
  rho : I.Port → I.Sink → Q

  theta_nonneg :
    ∀ X, 0 ≤ theta X

  theta_allowed :
    ∀ X, theta X ≠ 0 → C.Allowed X

  rho_nonneg :
    ∀ p s, 0 ≤ rho p s

  rho_legal :
    ∀ p s, rho p s ≠ 0 → I.legal p s

  /--
  The chosen cuts dominate the total alpha mass of this particular dual.
  -/
  alpha_dominated :
    I.totalAlpha d
      ≤ ∑ X : I.Cut, theta X * I.cutAlpha d X

  /--
  In-support short-edge coefficients are at most the unit capacities.
  -/
  short_coeff :
    ∀ f : I.Short,
      (∑ X : I.Cut, theta X * I.useShort X f) ≤ 1

  /--
  Every generated port coefficient is routed onward.
  -/
  port_coeff_routed :
    ∀ p : I.Port,
      (∑ X : I.Cut, theta X * I.cutPort X p)
        ≤ ∑ s : I.Sink, rho p s

  /--
  Routed sink coefficients respect the bank capacities.
  -/
  sink_coeff :
    ∀ s : I.Sink,
      (∑ p : I.Port, rho p s) ≤ I.cap s

def DualSqueeze.Checked ... : Prop := (conjunction of the eight fields)
def checkDualSqueeze ... : Bool := decide (Z.Checked)

end BankedWallLP
```

Now the key bookkeeping theorem:

```lean
theorem noStrictDual_of_checkedDualSqueeze
    (C : I.RootedCutClassifier)
    (d : I.Dual)
    (hd : I.checkDual d = true)
    (Z : I.DualSqueeze C d)
    (hZ : I.checkDualSqueeze C d Z = true) :
    ¬ d.StrictGap :=
by
  -- BOOKKEEPING PROOF PLAN.
  --
  -- Chain:
  --
  --   totalAlpha
  --     <= ∑ X, theta X * cutAlpha X
  --     <= ∑ X, theta X * (cutBeta X + cutGamma X)
  --
  -- because theta >= 0 and D1.
  --
  -- Rearrange finite sums:
  --
  --   ∑ X, theta X * cutBeta X
  --     = ∑ f, (∑ X, theta X * useShort X f) * beta f
  --     <= ∑ f, beta f
  --
  -- using beta >= 0 and `short_coeff`.
  --
  -- Similarly:
  --
  --   ∑ X, theta X * cutGamma X
  --     = ∑ p, (∑ X, theta X * cutPort X p) * gamma p
  --     <= ∑ p, (∑ s, rho p s) * gamma p
  --
  -- using gamma >= 0 and `port_coeff_routed`.
  --
  -- Since rho is legal and nonnegative, D2 gives:
  --
  --   rho p s * gamma p <= rho p s * delta s.
  --
  -- Hence:
  --
  --   ∑ p, (∑ s, rho p s) * gamma p
  --     <= ∑ s, (∑ p, rho p s) * delta s
  --     <= ∑ s, cap s * delta s.
  --
  -- Therefore:
  --
  --   totalAlpha <= totalBeta + totalDeltaCap.
  --
  -- This contradicts `StrictGap`.
  sorry
```

This theorem is entirely bookkeeping. It is the exact point where the banked form matters: the only RHS capacity is `cap s`, and those sinks are door/vertexSlack/C5Base/prune.

---

# 4. The wall reduction theorem

For each obstruction, extract a finite LP instance.

```lean
def BankedWallLP.ofObstruction
    {G : GraphData} {cut : CutData} {rows : RowDB} {cage : CageData}
    (O : MinimalFullClosureObstruction G cut rows cage) :
    BankedWallLP := sorry

def RootedCutClassifier.ofObstruction ... := sorry
```

Now define the precise irreducible structural lemma:

```lean
/--
THE REAL WALL IN DUAL-SQUEEZE FORM.

For every checked banked dual of a minimal full-closure obstruction,
there is a dual squeeze using only:

* singleton cuts,
* quotient-closed gamma-free cuts,
* bank-rooted full-escape quotient cuts.

This is the theorem to prove combinatorially.
-/
def RootedEscapeSqueeze_exists
    (O : MinimalFullClosureObstruction G cut rows cage) : Prop :=
  let I := BankedWallLP.ofObstruction O
  let C := RootedCutClassifier.ofObstruction O
  ∀ d : I.Dual,
    I.checkDual d = true →
      ∃ Z : I.DualSqueeze C d,
        I.checkDualSqueeze C d Z = true
```

Then the wall follows formally:

```lean
theorem fullBankRelaxedCoverBundle_exists_of_rootedEscapeSqueeze
    (hG hTri hCut hMax hGammaMin hBConn hRows hCage)
    (O : MinimalFullClosureObstruction G cut rows cage)
    (hSqueeze : RootedEscapeSqueeze_exists O) :
    ∃ b : FullBankRelaxedCoverBundle,
      checkFullBankRelaxedCoverBundle O b = true :=
by
  classical
  -- hNoDual from hSqueeze + noStrictDual_of_checkedDualSqueeze
  -- primal_exists_of_no_strict_dual (compiled Farkas)
  -- FullBankRelaxedCoverBundle.ofBankedWallLPPrimal bridge
  -- Source labels from I.sinkKind / I.sinkSourceId. No eta token.
  ...
```

---

# 5. What the new cut class is

Add explicit classifier data to the obstruction extractor.

```lean
structure EscapeQuotientData
    (O : MinimalFullClosureObstruction G cut rows cage) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp

  /-- The quotient component containing an atom endpoint/port. -/
  qOfPort : O.Port → QComp

  /-- Short-edge boundary of a quotient shore. -/
  shortBoundary : Finset QComp → Finset O.ShortEdge

  /-- Off-support ports exposed by a quotient shore. -/
  exposedPorts : Finset QComp → Finset O.Port

  /-- Legal sink neighborhood of exposed ports. -/
  sinkNbr : Finset O.Port → Finset O.BankSink

  /-- Full ell=5 escape closure operator. -/
  fullClosure : Finset QComp → Finset QComp

  closure_extensive : ∀ U, U ⊆ fullClosure U
  closure_idempotent : ∀ U, fullClosure (fullClosure U) = fullClosure U
  closure_monotone : ∀ U V, U ⊆ V → fullClosure U ⊆ fullClosure V
```

Now the three allowed cut classes:

```lean
/--
A quotient-closed gamma-free cut: a union of `B \ F` quotient components
with no exposed off-support bank port.
-/
structure QuotientClosedCut (O) (Q : EscapeQuotientData O) (X : Cut) where
  shore : Finset Q.QComp
  closed : Q.fullClosure shore = shore
  noPorts : Q.exposedPorts shore = ∅
  realizes : X = ObstructionCut.ofQuotientShore O Q shore

/--
THE NEW CUT CLASS.

A bank-rooted full-escape quotient cut is a closed quotient shore whose
exposed off-support ports all route to one globally labelled bank root,
or to a declared root-neighborhood.

This is the class that converts orphan gamma mass into real bank capacity.
-/
structure BankRootedClosureCut (O) (Q : EscapeQuotientData O) (X : Cut) where
  shore : Finset Q.QComp
  root : O.BankSink
  rootNbr : Finset O.BankSink

  closed : Q.fullClosure shore = shore
  root_mem : root ∈ rootNbr
  ports_nonempty : Q.exposedPorts shore ≠ ∅

  all_ports_route_to_rootNbr :
    ∀ p ∈ Q.exposedPorts shore,
      ∃ s ∈ rootNbr, O.LegalSinkPort p s

  rootNbr_capacity_is_bank :
    ∀ s ∈ rootNbr,
      O.BankSinkKind s = CapKind.door
      ∨ O.BankSinkKind s = CapKind.vertexSlack
      ∨ O.BankSinkKind s = CapKind.c5Base
      ∨ O.BankSinkKind s = CapKind.prune

  realizes : X = ObstructionCut.ofBankRootedClosure O Q shore root rootNbr
```

The classifier checks that quotientClosed-kinded cuts have QuotientClosedCut witnesses and
bankRootedClosure-kinded cuts have BankRootedClosureCut witnesses.

The key point: a `BankRootedClosureCut` is not allowed to charge eta. Its exposed ports must route to actual bank sinks, whose source IDs later enter the global no-double-spend ledger.

---

# 6. The hard sublemma to prove

The precise remaining research statement, replacing the vague wall:

```lean
theorem rootedEscapeSqueeze_exists_for_minimalFullClosureObstruction
    (hG hTri hCut hMax hGammaMin hBConn hRows hCage)
    (O : MinimalFullClosureObstruction G cut rows cage)
    (hMinSize : O.cardS ≥ 9)
    (hDefectOne : O.cardEshort = O.cardS - 1)
    (hNoPrivate : O.NoPrivateShortEdge)
    (hSupportSize : ∀ e, O.supportSize e = 4 ∨ 6 ≤ O.supportSize e)
    (hNoSupportFive : ∀ e, O.supportSize e ≠ 5)
    (hPairUnion : ∀ e f, e ≠ f → 5 ≤ O.supportUnionSize e f)
    (hFootprintConnected : O.FootprintConnected)
    (hFullEscapeClosure : O.FullEscapeClosed)
    (hReduced : O.ReducedMinimalNegativeBalance) :
    RootedEscapeSqueeze_exists O := by
  -- HARD PROOF PLAN BELOW.
  sorry
```

This theorem is smaller and sharper than the original bundle existence theorem because it proves only a **dual-specific inequality-combination certificate**. Farkas and the bundle constructor do the rest.

---

# 7. Proof plan (five phases)

## Phase 1 — Normalize the dual on the quotient

Compress the cage by deleting `F = E_short(S)`: `QComp := connected components of B \ F`.
For a quotient shore `U`, define AtomShadow U / ShortBoundary U / ExposedPorts U and

```lean
def Phi (U : Finset QComp) : Q :=
    (∑ a in AtomShadow U, d.alpha a)
  - (∑ f in ShortBoundary U, d.beta f)
  - (∑ p in ExposedPorts U, d.gamma p)
```

D1 for the quotient cut says `Phi U ≤ 0` whenever `U` is realized by an allowed cut.
Arbitrary `U` may expose ports whose gamma terms are not yet routed to bank capacity — this is where the bank-rooted cuts enter.

## Phase 2 — Start with the compiled singleton domination

Obtain an initial `AlmostSqueeze` (theta over allowed cuts, alpha_dominated + short_coeff, NO routing yet).
The remaining question: is the generated port load

```lean
def squeezePortLoad (Z) (p) : Q := ∑ X, Z.theta X * I.cutPort X p
```

legally routable to sinks (`PortLoadRoutable L`)? If yes, done. If not, finite max-flow Hall gives a
deficient port set:

```lean
theorem portHall_deficient_of_not_routable
    (L : I.Port → Q) (hL : ∀ p, 0 ≤ L p) (hNot : ¬ PortLoadRoutable I L) :
    ∃ P : Finset I.Port,
      (∑ p in P, L p) > ∑ s, if (∃ p ∈ P, I.legal p s) then I.cap s else 0
  -- Standard finite rational max-flow/min-cut.
```

This deficient set is the exact place where the old singleton plus quotient argument stalls.

## Phase 3 — Close a deficient port set under full escape

Given a deficient port set `P`, take its quotient support and full escape closure:

```lean
def portQShore (Q) (P : Finset I.Port) : Finset Q.QComp :=
  Q.fullClosure (P.image Q.qOfPort)
```

THE HARD CLOSURE LEMMA:

```lean
theorem deficientPortSet_has_rooted_or_gammaFree_cut
    (Q) (d) (hd) (P : Finset I.Port)
    (hPdef : PortHallDeficient I P)
    (hPminimal : ∀ P' ⊂ P, ¬ PortHallDeficient I P') :
    (∃ X, kind X = quotientClosed ∧ QuotientClosedCut O Q X)
    ∨ (∃ X, kind X = bankRootedClosure ∧ BankRootedClosureCut O Q X)
```

Uses: full escape closure, no-private-edge, support size 4 or ≥6, size-5 impossible, pairwise union ≥5,
footprint connected, defect one (|S| = |F| + 1), minimality. The logic:

```text
If the deficient port set closes to a shore with no exposed bank root,
then it is a gamma-free quotient cut.

If it closes to exactly one root neighborhood, it is a bank-rooted
full-escape cut.

If it closes to two or more independent root neighborhoods, uncrossing
splits it into smaller deficient port sets, contradicting minimality of P.

If closure creates a proper smaller ell=5 Hall violator, contradiction
to minimal full-closure obstruction.

If closure creates a private short edge, contradiction to no-private-edge.

If a size-5 support appears during the split, contradiction to bipartite parity.
```

## Phase 4 — Patch the almost-squeeze

```lean
theorem rootedCut_patches_Hall_deficient_ports
    (hd) (Z : AlmostSqueeze) (P) (hPdef) (X) (hXallowed) :
    ∃ Z', PatchMeasure I Z' < PatchMeasure I Z
  -- Add a rational multiple of the D1 inequality for X;
  -- reduce the deficient port excess; preserve alpha_dominated,
  -- short_coeff ≤ 1, theta_nonneg, allowed support.
  -- The amount is the minimum of finitely many positive rational slacks.
```

Measure: lexicographic finite (deficientPortSetCount, totalPositiveExcessNumerator, supportSize).
In practice this can be avoided by invoking finite LP separation directly, but an explicit patch loop
is easier to audit.

## Phase 5 — Terminate and obtain the squeeze

```lean
theorem almostSqueeze_to_dualSqueeze_by_rootedPatching
    (hd) (Z0 : AlmostSqueeze) (hRootedPatch : ∀ P, deficient → patchable) :
    ∃ Z : I.DualSqueeze C d, I.checkDualSqueeze C d Z = true
  -- Either routable (yields rho), or Hall gives a deficient set,
  -- the rooted patch strictly decreases the finite measure;
  -- well-founded induction terminates.
```

---

# 8. Why the bank-rooted cut is the missing class

Existing singleton domination gives `Σ alpha ≤ Σ beta + Σ orphan_gamma`. Gamma-free quotient cuts reduce
orphan gamma when the shore has no escape ports. But a real obstruction can have a closed shore whose only
obstruction to being gamma-free is a forced escape through a door/vertexSlack/C5Base/prune sink. Bare
quotient cuts cannot charge this correctly; singleton cuts see too little; strict cut covers reject it;
local eta is forbidden. The bank-rooted full-escape cut gives the missing inequality:

```text
alpha(shadow of closed shore)
  ≤ beta(short boundary) + gamma(exposed ports routed to rooted bank neighborhood).
```

Then D2 routes that gamma to `delta`, and the squeeze routing field `rho` pays it with real bank capacities
(`gamma(port) ≤ delta(sink)`, `Σ routed_to_sink ≤ cap(sink)`). This is exactly the BANKED form:
`Demand ≤ DoorCap + VertexSlackCap + C5BaseCap + PruneCap`. No cage eta appears.

---

# 9. Treatment of the `m = 9` double-star anchor

Not a special theorem in the top wall proof — a base lemma inside `rootedPatch_exists_from_minimalFullClosure`:

```lean
theorem rootedPatch_exists_m9_doubleStar
    (hCard : O.cardS = 9)
    (hUnique : O.FootprintIso DoubleStarWithBridgeFootprint)
    (hBank : O.DefectQ = 25 ∧ 300 ≤ O.DoorCapQ) :
    RootedPatchBaseCase O
  -- Use the verified exact 24-vertex/double-star certificate.
  -- The patch is bank-rooted at the endpoint door sinks.
  -- Defect 25 is absorbed by DoorCap >= 300. No eta.
```

Then `by_cases h9 : O.cardS = 9` in the general patch theorem. This prevents the 24-vertex counterexample
from poisoning the proof: it is not a counterexample to the banked LP; it is exactly a bank-rooted-patch
base case.

---

# 10. Decisive falsifier format

A decisive falsifier is not an abstract footprint with no endpoint selector. It must be a checked strict
banked dual for a graph-realizable minimal full-closure obstruction:

```lean
structure WallFalsifier where
  G : GraphData; cut : CutData; rows : RowDB; cage : CageData
  hG hTri hCut hMax hGammaMin hBConn hRows hCage : (the eight validity predicates)
  O : MinimalFullClosureObstruction G cut rows cage
  d : (BankedWallLP.ofObstruction O).Dual
  hd : (BankedWallLP.ofObstruction O).checkDual d = true
  hStrict : d.StrictGap

def checkWallFalsifier (F : WallFalsifier) : Bool :=
  (BankedWallLP.ofObstruction F.O).checkDual F.d && decide F.d.StrictGap
```

I do not have such a falsifier. An incidence-only object that violates endpoint-singleton selection is not
enough unless it also satisfies graph-realizability, full escape closure, reduced minimal-negative-balance
cage predicates, and the exact banked dual inequalities.

---

# 11. Final recommended wall statement

Replace the current single wall theorem by two layers:

## Layer A — structural uncrossing wall

```lean
theorem RootedEscapeSqueeze_exists_wall
    (hG hTri hCut hMax hGammaMin hBConn hRows hCage)
    (O : MinimalFullClosureObstruction G cut rows cage) :
    RootedEscapeSqueeze_exists O := by
  -- The hard proof:
  -- singleton almost-squeeze
  -- + max-flow Hall on ports
  -- + full-escape closure of deficient port sets
  -- + quotient-closed cuts
  -- + bank-rooted full-escape cuts
  -- + no-private/support-size/union/minimality rigidity.
  sorry
```

## Layer B — Farkas-to-bundle bookkeeping

```lean
theorem Ell5FullBankRelaxedCover_exists_wall
    (... same hypotheses ...) :
    ∃ b : FullBankRelaxedCoverBundle, checkFullBankRelaxedCoverBundle O b = true :=
  -- RootedEscapeSqueeze_exists_wall + fullBankRelaxedCoverBundle_exists_of_rootedEscapeSqueeze
```

---

# 12. Classification

**Bookkeeping / should compile once APIs are aligned**

```text
BankedWallLP primal/dual interface
checkDual soundness
DualSqueeze checker
noStrictDual_of_checkedDualSqueeze
primal_exists_of_no_strict_dual wrapper
FullBankRelaxedCoverBundle.ofBankedWallLPPrimal bridge
endpointSingletonCoverData_sound
falsifier checker
```

**Hard but sharply isolated**

```text
RootedEscapeSqueeze_exists_wall
rootedPatch_exists_from_minimalFullClosure
deficientPortSet_has_rooted_or_gammaFree_cut
rootedCut_patches_Hall_deficient_ports
```

**Additional cut class that closes the gap**

```text
BankRootedClosureCut
```

That is the missing object. It is the first class that simultaneously respects the standing correction and
has enough strength to kill the dual gamma leakage:

```text
not bare support expansion,
not strict cut cover,
not local eta,
but legal bank-rooted closure capacity.
```

---
*Note on fidelity: §§0–2 and the load-bearing statements throughout are verbatim from the clipboard capture;
in §§3–11 some long hypothesis lists and duplicated local-instance blocks are compressed with `(...)`
markers purely for archive size — the full verbatim text lives in the session transcript, and every
definition/field that matters for the Lean surface is reproduced exactly.*
