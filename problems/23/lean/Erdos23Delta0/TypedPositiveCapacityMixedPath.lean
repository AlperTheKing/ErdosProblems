import Erdos23Delta0.PositiveCapacityMixedPath

/-!
# Sink-kind reduction on a harmful positive-capacity path

The abstract wall LP intentionally forgets extractor sink labels.  This file
records the two locality properties that the real four-kind bank interface
must export and proves the resulting path reduction:

* an edge-labelled Door has a subsingleton legal port fiber;
* every port legal to `vertexSlack(v)` has inside endpoint `v`.

Consequently, a coupling step which changes the inside graph vertex is either
a primitive escape-block step or is witnessed by a `c5Base`/`prune` sink.
Every path between corner seeds with distinct inside endpoints contains such
a moving step.  Thus Door and vertex-slack bookkeeping cannot be the remaining
geometric obstruction.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- The four official positive-capacity sink kinds, at the coupling layer. -/
inductive CouplingSinkKind where
  | door
  | vertexSlack
  | c5Base
  | prune
  deriving DecidableEq, Repr

/-- The sink-locality data actually used to classify a coupling step. -/
structure PositiveSinkSemantics (V : Type*) (I : BankedWallLP) where
  kind : I.Sink → CouplingSinkKind
  inside : I.Port → V
  vertexOwner : I.Sink → V
  door_fiber_subsingleton :
    ∀ {s : I.Sink}, kind s = .door →
      ∀ {p q : I.Port}, I.legal p s → I.legal q s → p = q
  vertexSlack_owner :
    ∀ {s : I.Sink}, kind s = .vertexSlack →
      ∀ {p : I.Port}, I.legal p s → inside p = vertexOwner s

variable {V : Type*} (S : PositiveSinkSemantics V I)

/-- A positive coupling-graph edge which moves the inside endpoint cannot be
created by an edge-specific Door or by one vertex-slack star. -/
theorem moving_graphAdj_is_primitive_or_basePrune
    (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port) {p q : I.Port}
    (hAdj :
      (couplingGraph (positiveCapacityLP I) primitive parent).Adj p q)
    (hmove : S.inside p ≠ S.inside q) :
    PrimitiveCoupled primitive p q ∨
      ∃ s : I.Sink,
        I.legal p s ∧ I.legal q s ∧ 0 < I.cap s ∧
          (S.kind s = .c5Base ∨ S.kind s = .prune) := by
  rcases positiveCouplingStep_of_graphAdj primitive parent hAdj with
    ⟨_hp, _hq, hprimitive | ⟨s, hps, hqs, hcap⟩⟩
  · exact Or.inl hprimitive
  · cases hkind : S.kind s with
    | door =>
        have hpq : p = q :=
          S.door_fiber_subsingleton hkind hps hqs
        exact (hAdj.ne hpq).elim
    | vertexSlack =>
        have hpInside : S.inside p = S.vertexOwner s :=
          S.vertexSlack_owner hkind hps
        have hqInside : S.inside q = S.vertexOwner s :=
          S.vertexSlack_owner hkind hqs
        exact (hmove (hpInside.trans hqInside.symm)).elim
    | c5Base =>
        exact Or.inr ⟨s, hps, hqs, hcap, Or.inl hkind⟩
    | prune =>
        exact Or.inr ⟨s, hps, hqs, hcap, Or.inr hkind⟩

/-- A walk whose endpoint labels differ has an adjacent label-changing step. -/
theorem walk_exists_inside_change
    {P W : Type*} {G : SimpleGraph P} (inside : P → W)
    {p q : P} (w : G.Walk p q) (hpq : inside p ≠ inside q) :
    ∃ u v : P, G.Adj u v ∧ inside u ≠ inside v := by
  induction w with
  | nil => exact (hpq rfl).elim
  | @cons u v q huv w ih =>
      by_cases huvInside : inside u = inside v
      · have hvq : inside v ≠ inside q := by
          intro h
          exact hpq (huvInside.trans h)
        exact ih hvq
      · exact ⟨u, v, huv, huvInside⟩

/-- Failure of positive-capacity corner separation has a genuinely moving
primitive or `c5Base`/`prune` step.  Door and vertex-slack steps have been
eliminated before any corridor geometry is invoked. -/
theorem exists_moving_primitive_or_basePrune_step_of_not_noMixed
    (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port)
    (hseedL : seedL ⊆ parent) (hseedR : seedR ⊆ parent)
    (hcorners :
      ∀ p ∈ seedL, ∀ q ∈ seedR, S.inside p ≠ S.inside q)
    (hbad :
      ¬NoMixedPositiveCapacityComponent I primitive parent seedL seedR) :
    ∃ u v : I.Port,
      (couplingGraph (positiveCapacityLP I) primitive parent).Adj u v ∧
      S.inside u ≠ S.inside v ∧
      (PrimitiveCoupled primitive u v ∨
        ∃ s : I.Sink,
          I.legal u s ∧ I.legal v s ∧ 0 < I.cap s ∧
            (S.kind s = .c5Base ∨ S.kind s = .prune)) := by
  obtain ⟨p, hpL, q, hqR, _hp, _hq, w, _hw⟩ :=
    exists_simplePath_of_not_noMixedPositiveCapacityComponent
      primitive parent seedL seedR hseedL hseedR hbad
  obtain ⟨u, v, huv, hmove⟩ :=
    walk_exists_inside_change S.inside w (hcorners p hpL q hqR)
  exact ⟨u, v, huv, hmove,
    moving_graphAdj_is_primitive_or_basePrune S primitive parent huv hmove⟩

#print axioms moving_graphAdj_is_primitive_or_basePrune
#print axioms walk_exists_inside_change
#print axioms exists_moving_primitive_or_basePrune_step_of_not_noMixed

end ClosedShore
end Wall
end Erdos23Delta0
