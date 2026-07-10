import Erdos23Delta0.ClosedShoreExtraction

/-!
# Horn closure quotient for the banked wall

This module is a small adapter for the current Gap#1 W3 route.  It does not
construct the graph-side forced-escape rules.  Instead it provides a generic
finite Horn-closure implementation that can instantiate
`AbstractEscapeQuotient` once the real forced-ell=5 adapter supplies:

* a quotient component type;
* a list of Horn implications between components; and
* the exposed-port map.

The graph-side content remains in the construction of those fields and in the
separate closed-Hall/root-extraction/exchange theorems.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- A finite Horn implication: if every component in `pre` is present, then
`post` is forced into the closure. -/
structure HornRule (α : Type*) where
  pre : Finset α
  post : α

/-- A shore is closed under a rule predicate when every applicable implication
has its post component in the shore. -/
def HornClosed {α : Type*} (rules : HornRule α → Prop)
    (U : Finset α) : Prop :=
  ∀ r : HornRule α, rules r → r.pre ⊆ U → r.post ∈ U

/-- The least Horn-closed superset of `U`, defined as the intersection of all
Horn-closed supersets of `U`. -/
noncomputable def hornClosure {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U : Finset α) : Finset α := by
  classical
  exact Finset.univ.filter fun x =>
    ∀ W : Finset α, U ⊆ W → HornClosed rules W → x ∈ W

theorem hornClosure_extensive {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U : Finset α) :
    U ⊆ hornClosure rules U := by
  classical
  intro x hx
  simp [hornClosure]
  intro W hUW _hClosed
  exact hUW hx

theorem hornClosure_le_of_closed {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U W : Finset α)
    (hUW : U ⊆ W) (hWclosed : HornClosed rules W) :
    hornClosure rules U ⊆ W := by
  classical
  intro x hx
  have hxAll :
      ∀ W' : Finset α, U ⊆ W' → HornClosed rules W' → x ∈ W' := by
    simpa [hornClosure] using hx
  exact hxAll W hUW hWclosed

theorem hornClosure_closed {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U : Finset α) :
    HornClosed rules (hornClosure rules U) := by
  classical
  intro r hr hpre
  simp [hornClosure]
  intro W hUW hWclosed
  apply hWclosed r hr
  intro x hxpre
  exact hornClosure_le_of_closed rules U W hUW hWclosed (hpre hxpre)

theorem hornClosure_idempotent {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U : Finset α) :
    hornClosure rules (hornClosure rules U) = hornClosure rules U := by
  classical
  apply le_antisymm
  · exact hornClosure_le_of_closed rules (hornClosure rules U)
      (hornClosure rules U) (by intro x hx; exact hx)
      (hornClosure_closed rules U)
  · exact hornClosure_extensive rules (hornClosure rules U)

theorem hornClosure_monotone {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) {U V : Finset α} (hUV : U ⊆ V) :
    hornClosure rules U ⊆ hornClosure rules V := by
  classical
  intro x hx
  have hxAll :
      ∀ W : Finset α, U ⊆ W → HornClosed rules W → x ∈ W := by
    simpa [hornClosure] using hx
  simp [hornClosure]
  intro W hVW hWclosed
  exact hxAll W (fun y hy => hVW (hUV hy)) hWclosed

/-- Fixed points of the Horn closure are exactly Horn-closed finite shores. -/
theorem hornClosure_eq_self_iff {α : Type*} [Fintype α] [DecidableEq α]
    (rules : HornRule α → Prop) (U : Finset α) :
    hornClosure rules U = U ↔ HornClosed rules U := by
  classical
  constructor
  · intro h
    rw [← h]
    exact hornClosure_closed rules U
  · intro hClosed
    apply le_antisymm
    · exact hornClosure_le_of_closed rules U U (by intro x hx; exact hx) hClosed
    · exact hornClosure_extensive rules U

/-- Data sufficient to build the abstract W3 quotient from Horn closure.  The
real forced-ell=5 graph adapter should construct this object; this structure
only supplies the closure algebra. -/
structure HornEscapeSurface (I : BankedWallLP) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp
  ruleList : List (HornRule QComp)
  exposedPorts : Finset QComp → Finset I.Port

namespace HornEscapeSurface

attribute [instance] qDecEq qFintype

/-- Rule predicate induced by the finite rule list. -/
def rules (S : HornEscapeSurface I) (r : HornRule S.QComp) : Prop :=
  r ∈ S.ruleList

/-- Horn closure associated with the surface. -/
noncomputable def fullClosure (S : HornEscapeSurface I)
    (U : Finset S.QComp) : Finset S.QComp :=
  hornClosure S.rules U

/-- Surface-level version of `hornClosure_eq_self_iff`. -/
theorem fullClosure_eq_self_iff (S : HornEscapeSurface I)
    (U : Finset S.QComp) :
    S.fullClosure U = U ↔ HornClosed S.rules U :=
  hornClosure_eq_self_iff S.rules U

/-- The `AbstractEscapeQuotient` consumed by the compiled W3 skeleton. -/
noncomputable def toQ (S : HornEscapeSurface I) : AbstractEscapeQuotient I :=
  { QComp := S.QComp
    qDecEq := S.qDecEq
    qFintype := S.qFintype
    fullClosure := S.fullClosure
    exposedPorts := S.exposedPorts
    closure_extensive := hornClosure_extensive S.rules
    closure_idempotent := hornClosure_idempotent S.rules
    closure_monotone := fun _ _ hUV => hornClosure_monotone S.rules hUV }

/-- A root-fiber closure gate in the form suggested by GPT-Pro.  The actual
root blocks and support relation are supplied by the graph-to-wall adapter. -/
def RootFiberClosed (S : HornEscapeSurface I)
    {RootBlock : Type*} [Fintype RootBlock]
    (rootFiber : RootBlock → Finset S.QComp) : Prop :=
  ∀ b : RootBlock, HornClosed S.rules (rootFiber b)

/-- Root-fiber Horn closure gives the fixed-point equation required by
`PositiveRootBlockClosedExtraction`. -/
theorem fullClosure_rootFiber_eq_self (S : HornEscapeSurface I)
    {RootBlock : Type*} [Fintype RootBlock]
    (rootFiber : RootBlock → Finset S.QComp)
    (hClosed : S.RootFiberClosed rootFiber) (b : RootBlock) :
    S.fullClosure (rootFiber b) = rootFiber b :=
  (S.fullClosure_eq_self_iff (rootFiber b)).mpr (hClosed b)

/-- A Horn-closed shore exposes a closed port set for the W3 quotient. -/
theorem closedPortSet_of_hornClosed (S : HornEscapeSurface I)
    (U : Finset S.QComp) (hClosed : HornClosed S.rules U) :
    ClosedPortSet S.toQ (S.exposedPorts U) :=
  ⟨U, (S.fullClosure_eq_self_iff U).mpr hClosed, rfl⟩

/-- Root-fiber closure exposes a closed port set for every root fiber. -/
theorem closedPortSet_rootFiber (S : HornEscapeSurface I)
    {RootBlock : Type*} [Fintype RootBlock]
    (rootFiber : RootBlock → Finset S.QComp)
    (hClosed : S.RootFiberClosed rootFiber) (b : RootBlock) :
    ClosedPortSet S.toQ (S.exposedPorts (rootFiber b)) :=
  S.closedPortSet_of_hornClosed (rootFiber b) (hClosed b)

/-- Atom/root purity gate in adapter-neutral form. -/
def AtomRootPure (S : HornEscapeSurface I)
    {Root : Type*} {RootBlock : Type*}
    (legalRoot : Root → Prop)
    (rootBlockOf : ∀ r : Root, legalRoot r → RootBlock)
    (supportedOnRoot : S.QComp → Root → Prop) : Prop :=
  ∀ c r s (hr : legalRoot r) (hs : legalRoot s),
    supportedOnRoot c r →
      supportedOnRoot c s →
        rootBlockOf r hr = rootBlockOf s hs

end HornEscapeSurface

end ClosedShore
end Wall
end Erdos23Delta0
