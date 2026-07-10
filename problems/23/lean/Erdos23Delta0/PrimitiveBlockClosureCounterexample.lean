import Erdos23Delta0.NoMixedCornerPortComponent
import Erdos23Delta0.BankedWallHornQuotient

/-!
# Directed closure is not undirected block saturation

The abstract escape-quotient axioms describe a closure operator, not a
partition closure. A one-way implication on two elements satisfies every
closure axiom but has a closed singleton that is not saturated under the
symmetrized primitive relation. Thus PrimitiveBlockClosureExactOn is an
independent hypothesis; it does not follow from AbstractEscapeQuotient.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore
namespace PrimitiveBlockClosureCounterexample

def tinyLP : BankedWallLP where
  Cut := PUnit
  Atom := PUnit
  Short := PUnit
  Port := Fin 2
  Sink := PUnit
  cutFintype := inferInstance
  atomFintype := inferInstance
  shortFintype := inferInstance
  portFintype := inferInstance
  sinkFintype := inferInstance
  cov := fun _ _ => 0
  useShort := fun _ _ => 0
  cutPort := fun _ _ => 0
  legal := fun _ _ => False
  legalDecidable := fun _ _ => inferInstance
  cap := fun _ => 0

def oneWayClosure (U : Finset (Fin 2)) : Finset (Fin 2) :=
  if (0 : Fin 2) ∈ U then insert (1 : Fin 2) U else U

theorem oneWayClosure_extensive (U : Finset (Fin 2)) :
    U ⊆ oneWayClosure U := by
  intro x hx
  by_cases h0 : (0 : Fin 2) ∈ U
  · simp [oneWayClosure, h0, hx]
  · simpa [oneWayClosure, h0] using hx

theorem oneWayClosure_idempotent (U : Finset (Fin 2)) :
    oneWayClosure (oneWayClosure U) = oneWayClosure U := by
  by_cases h0 : (0 : Fin 2) ∈ U
  · have h0' : (0 : Fin 2) ∈ insert (1 : Fin 2) U := by simp [h0]
    simp [oneWayClosure, h0, h0']
  · simp [oneWayClosure, h0]

theorem oneWayClosure_monotone (U W : Finset (Fin 2)) (hUW : U ⊆ W) :
    oneWayClosure U ⊆ oneWayClosure W := by
  intro x hx
  by_cases h0U : (0 : Fin 2) ∈ U
  · have h0W : (0 : Fin 2) ∈ W := hUW h0U
    simp only [oneWayClosure, if_pos h0U, if_pos h0W, Finset.mem_insert] at hx ⊢
    exact hx.elim Or.inl (fun hxU => Or.inr (hUW hxU))
  · have hxU : x ∈ U := by simpa [oneWayClosure, h0U] using hx
    exact oneWayClosure_extensive W (hUW hxU)

def tinyQ : AbstractEscapeQuotient tinyLP where
  QComp := Fin 2
  qDecEq := inferInstance
  qFintype := inferInstance
  fullClosure := oneWayClosure
  exposedPorts := id
  closure_extensive := oneWayClosure_extensive
  closure_idempotent := oneWayClosure_idempotent
  closure_monotone := oneWayClosure_monotone

def primitive (p q : Fin 2) : Prop :=
  p = 0 ∧ q = 1

instance primitiveDecidable : DecidableRel primitive := by
  intro p q
  unfold primitive
  infer_instance

def parent : Finset (Fin 2) := Finset.univ
def closedSingleton : Finset (Fin 2) := {(1 : Fin 2)}

theorem closedSingleton_isClosed :
    ClosedPortSet tinyQ closedSingleton := by
  refine ⟨closedSingleton, ?_, rfl⟩
  change oneWayClosure closedSingleton = closedSingleton
  have h0 : (0 : Fin 2) ∉ closedSingleton := by
    intro h
    have heq : (0 : Fin 2) = 1 := Finset.mem_singleton.mp h
    exact (by decide : (0 : Fin 2) ≠ 1) heq
  simp [oneWayClosure, h0]

theorem closedSingleton_not_primitiveSaturated :
    ¬ PrimitiveBlockSaturatedIn (I := tinyLP) primitive parent closedSingleton := by
  intro hsat
  have h1 : (1 : Fin 2) ∈ closedSingleton := by simp [closedSingleton]
  have h0parent : (0 : Fin 2) ∈ parent := by simp [parent]
  have hcoupled :
      PrimitiveCoupled (I := tinyLP) primitive (1 : Fin 2) (0 : Fin 2) := by
    right
    exact ⟨rfl, rfl⟩
  have h0 := hsat h1 h0parent hcoupled
  have heq : (0 : Fin 2) = 1 := Finset.mem_singleton.mp h0
  exact (by decide : (0 : Fin 2) ≠ 1) heq

theorem primitiveBlockClosureExactOn_fails :
    ¬ PrimitiveBlockClosureExactOn tinyQ primitive parent := by
  intro hexact
  have hsub : closedSingleton ⊆ parent := by
    intro p hp
    simp [parent]
  have hiff := hexact closedSingleton hsub
  have hsaturated :
      PrimitiveBlockSaturatedIn (I := tinyLP) primitive parent closedSingleton :=
    hiff.mp closedSingleton_isClosed
  exact closedSingleton_not_primitiveSaturated hsaturated

/-- The same countermodel inside the repository's finite Horn adapter. -/
def rule01 : HornRule (Fin 2) where
  pre := {(0 : Fin 2)}
  post := 1

def hornSurface : HornEscapeSurface tinyLP where
  QComp := Fin 2
  qDecEq := inferInstance
  qFintype := inferInstance
  ruleList := [rule01]
  exposedPorts := id

theorem closedSingleton_hornClosed :
    HornClosed hornSurface.rules closedSingleton := by
  intro r hr hpre
  have hre : r = rule01 := by
    simpa [HornEscapeSurface.rules, hornSurface] using hr
  subst r
  have h0 : (0 : Fin 2) ∈ closedSingleton := hpre (by simp [rule01])
  have heq : (0 : Fin 2) = 1 := Finset.mem_singleton.mp h0
  exact ((by decide : (0 : Fin 2) ≠ 1) heq).elim

theorem closedSingleton_isHornSurfaceClosed :
    ClosedPortSet hornSurface.toQ closedSingleton :=
  hornSurface.closedPortSet_of_hornClosed closedSingleton closedSingleton_hornClosed

theorem hornPrimitiveBlockClosureExactOn_fails :
    ¬ PrimitiveBlockClosureExactOn hornSurface.toQ primitive parent := by
  intro hexact
  have hsub : closedSingleton ⊆ parent := by
    intro p hp
    simp [parent]
  have hiff := hexact closedSingleton hsub
  have hsaturated :
      PrimitiveBlockSaturatedIn (I := tinyLP) primitive parent closedSingleton :=
    hiff.mp closedSingleton_isHornSurfaceClosed
  exact closedSingleton_not_primitiveSaturated hsaturated

#print axioms oneWayClosure_monotone
#print axioms closedSingleton_isClosed
#print axioms primitiveBlockClosureExactOn_fails
#print axioms hornPrimitiveBlockClosureExactOn_fails

end PrimitiveBlockClosureCounterexample
end ClosedShore
end Wall
end Erdos23Delta0
