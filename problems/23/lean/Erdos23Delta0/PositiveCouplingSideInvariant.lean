import Erdos23Delta0.TypedPositiveCapacityMixedPath

/-!
# Local side invariance implies positive-capacity corner separation

After the sink-kind reduction, the global no-mixed-component theorem needs
only two local geometric checks: primitive escape-block steps and shared
`c5Base`/`prune` fibers must preserve the chosen corner-side label.  Door
steps are trivial and vertex-slack steps keep the inside endpoint fixed.

This module proves the resulting local-to-global path argument.  It does not
assert that the real extractor satisfies either local check.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP} {V W : Type*}
variable (S : PositiveSinkSemantics V I)

/-- Primitive escape-block transitions preserve an inside-vertex label. -/
def PrimitivePreservesInsideLabel
    (primitive : I.Port → I.Port → Prop) (label : V → W) : Prop :=
  ∀ {p q : I.Port}, PrimitiveCoupled primitive p q →
    label (S.inside p) = label (S.inside q)

/-- The only nontrivial shared sink kinds left after Door/vertex-slack
elimination preserve the same inside-vertex label. -/
def BasePrunePreservesInsideLabel (label : V → W) : Prop :=
  ∀ {p q : I.Port} {s : I.Sink},
    I.legal p s → I.legal q s → 0 < I.cap s →
      (S.kind s = .c5Base ∨ S.kind s = .prune) →
        label (S.inside p) = label (S.inside q)

/-- Every edge of the positive coupling graph preserves the label once the
two genuinely geometric step classes do. -/
theorem positiveCouplingGraph_adj_preserves_label
    (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port) (label : V → W)
    (hprimitive : PrimitivePreservesInsideLabel S primitive label)
    (hbasePrune : BasePrunePreservesInsideLabel S label)
    {p q : I.Port}
    (hAdj :
      (couplingGraph (positiveCapacityLP I) primitive parent).Adj p q) :
    label (S.inside p) = label (S.inside q) := by
  classical
  by_cases hmove : S.inside p = S.inside q
  · exact congrArg label hmove
  · rcases moving_graphAdj_is_primitive_or_basePrune
      S primitive parent hAdj hmove with hprim | ⟨s, hps, hqs, hcap, hkind⟩
    · exact hprimitive hprim
    · exact hbasePrune hps hqs hcap hkind

/-- If every graph edge preserves a label, every finite walk preserves it. -/
theorem walk_preserves_label_of_adj
    {P W : Type*} {G : SimpleGraph P} (label : P → W)
    (hedge : ∀ {p q : P}, G.Adj p q → label p = label q)
    {p q : P} (w : G.Walk p q) : label p = label q := by
  induction w with
  | nil => rfl
  | @cons u v q huv w ih => exact (hedge huv).trans ih

/-- Oppositely labelled corner seeds cannot lie in one positive-capacity
coupling component when primitive and base/prune steps preserve the label. -/
theorem noMixedPositiveCapacityComponent_of_sideInvariant
    (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port) (label : V → W)
    (hprimitive : PrimitivePreservesInsideLabel S primitive label)
    (hbasePrune : BasePrunePreservesInsideLabel S label)
    (hseeds :
      ∀ p ∈ seedL, ∀ q ∈ seedR,
        label (S.inside p) ≠ label (S.inside q)) :
    NoMixedPositiveCapacityComponent I primitive parent seedL seedR := by
  intro p hp q hq hreach
  rcases hreach with ⟨w⟩
  have hedge :
      ∀ {r t : I.Port},
        (couplingGraph (positiveCapacityLP I) primitive parent).Adj r t →
          label (S.inside r) = label (S.inside t) := by
    intro r t hAdj
    exact positiveCouplingGraph_adj_preserves_label
      S primitive parent label hprimitive hbasePrune hAdj
  exact hseeds p hp q hq
    (walk_preserves_label_of_adj (fun r => label (S.inside r))
      hedge w)

#print axioms positiveCouplingGraph_adj_preserves_label
#print axioms walk_preserves_label_of_adj
#print axioms noMixedPositiveCapacityComponent_of_sideInvariant

end ClosedShore
end Wall
end Erdos23Delta0
