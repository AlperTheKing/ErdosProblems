import Erdos23Delta0.DisjointPetalHalfSqueeze

/-!
# Exact checker for the disjoint-petal half-layer fast path

This module turns the proof-facing fields of `DisjointPetalRouteData` into one
finite decidable payload.  It does not assert that a real extractor emits such
a payload; an accepted payload constructs `HalfLayerRouted` and excludes a
checked strict dual through the already compiled half-layer theorem.
-/

namespace Erdos23Delta0
namespace DisjointPetalHalfSqueezeChecker

open scoped BigOperators
open MaxCutVertexIneq
open Wall
open DisjointPetalHalfSqueeze

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {I : BankedWallLP} {q : Nat}

local instance legalDecidable (p : I.Port) (s : I.Sink) :
    Decidable (I.legal p s) := I.legalDecidable p s

/-- Concrete finite payload presented to the checker. -/
structure Candidate (V : Type*) [Fintype V] [DecidableEq V]
    (I : BankedWallLP) (q : Nat) where
  walls : Fin q → I.Cut
  shore : Fin q → Finset V
  shortEdge : I.Short → Sym2 V
  portEdge : I.Port → Sym2 V
  door : I.Port → I.Sink

variable (C : Candidate V I q)

/-- All exact structural and routing obligations except the dual-dependent
positive-alpha TwoCover. -/
def Candidate.Valid [DecidableEq I.Sink] : Prop :=
  (∀ i j, i ≠ j → Disjoint (C.shore i) (C.shore j)) ∧
  (∀ i f,
    I.useShort (C.walls i) f =
      if edgeBoundary (C.shore i) (C.shortEdge f) = true then 1 else 0) ∧
  (∀ i p,
    I.cutPort (C.walls i) p =
      if edgeBoundary (C.shore i) (C.portEdge p) = true then 1 else 0) ∧
  Function.Injective C.door ∧
  (∀ p, I.legal p (C.door p)) ∧
  (∀ p, 1 ≤ I.cap (C.door p)) ∧
  (∀ s, 0 ≤ I.cap s)

instance candidateValidDecidable [DecidableEq I.Sink] :
    Decidable C.Valid := by
  unfold Candidate.Valid
  infer_instance

/-- Kernel-replayable structural payload checker. -/
def checkCandidate [DecidableEq I.Sink] : Bool := decide C.Valid

theorem checkCandidate_eq_true_iff [DecidableEq I.Sink] :
    checkCandidate C = true ↔ C.Valid := by
  simp [checkCandidate]

/-- Convert an accepted finite payload to the proof-facing route data. -/
def routeDataOfCheck [DecidableEq I.Sink]
    (hC : checkCandidate C = true) :
    DisjointPetalRouteData (V := V) I C.walls := by
  rcases (checkCandidate_eq_true_iff C).1 hC with
    ⟨hdisjoint, hshort, hport, hinjective, hlegal, hcapacity, hnonneg⟩
  exact
    { shore := C.shore
      shortEdge := C.shortEdge
      portEdge := C.portEdge
      petals_disjoint := hdisjoint
      short_is_boundary := hshort
      port_is_boundary := hport
      door := C.door
      door_injective := hinjective
      door_legal := hlegal
      door_capacity := hcapacity
      sink_capacity_nonneg := hnonneg }

/-- Dual-dependent exact TwoCover condition. -/
def PositiveAlphaTwoCover (d : Dual I) : Prop :=
  ∀ a : I.Atom, 0 < d.alpha a →
    ∑ i : Fin q, I.cov (C.walls i) a = 2

instance positiveAlphaTwoCoverDecidable (d : Dual I) :
    Decidable (PositiveAlphaTwoCover C d) := by
  unfold PositiveAlphaTwoCover
  infer_instance

def checkPositiveAlphaTwoCover (d : Dual I) : Bool :=
  decide (PositiveAlphaTwoCover C d)

theorem checkPositiveAlphaTwoCover_eq_true_iff (d : Dual I) :
    checkPositiveAlphaTwoCover C d = true ↔ PositiveAlphaTwoCover C d := by
  simp [checkPositiveAlphaTwoCover]

/-- End-to-end finite checker soundness: accepted geometry, own-Doors, and
positive-alpha TwoCover exclude the supplied checked strict dual. -/
theorem noStrictDual_of_checks [DecidableEq I.Sink]
    (d : Dual I) (hd : d.Checked)
    (hC : checkCandidate C = true)
    (htwo : checkPositiveAlphaTwoCover C d = true) :
    ¬ d.StrictGap :=
  noStrictDual_of_disjointPetalTwoCover d hd C.walls
    ((checkPositiveAlphaTwoCover_eq_true_iff C d).1 htwo)
    (routeDataOfCheck C hC)

#print axioms checkCandidate_eq_true_iff
#print axioms routeDataOfCheck
#print axioms checkPositiveAlphaTwoCover_eq_true_iff
#print axioms noStrictDual_of_checks

end DisjointPetalHalfSqueezeChecker
end Erdos23Delta0
