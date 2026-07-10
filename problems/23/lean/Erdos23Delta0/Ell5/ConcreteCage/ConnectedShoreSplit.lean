import Erdos23Delta0.Ell5.ConcreteCage.Ell5ProperShoreSplit

/-!
# Connected-shore splits

A finite nontrivial connected graph has a vertex whose deletion leaves a
connected induced graph.  Taking that vertex as a singleton shore gives two
connected complementary shores.  The relative version below transports this
construction from a graph induced on a finite vertex set back to the ambient
graph.

For a connected concrete cage with at least two vertices, these two shores
supply both `ProperRelative` witnesses.  If all owned atoms have length five,
the existing proper-shore theorem then packages them as a pure-lens cage
split.
-/

namespace SimpleGraph

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {H : SimpleGraph V}

/-- A finite nontrivial connected graph has a nonempty proper finite shore
whose two complementary induced graphs are connected.  The shore constructed
here is a singleton containing a leaf of a spanning tree. -/
theorem Connected.exists_connected_finset_split [Nontrivial V]
    (hconn : H.Connected) :
    ∃ U : Finset V,
      U.Nonempty ∧ U ≠ univ ∧
        (H.induce (U : Set V)).Connected ∧
          (H.induce ((Uᶜ : Finset V) : Set V)).Connected := by
  obtain ⟨v, hv⟩ :=
    hconn.exists_connected_induce_compl_singleton_of_finite_nontrivial
  refine ⟨{v}, singleton_nonempty v, singleton_ne_univ v, ?_, ?_⟩
  · rw [coe_singleton, induce_singleton_eq_top]
    exact connected_top
  · have hset : (({v}ᶜ : Finset V) : Set V) = ({v} : Set V)ᶜ := by
      ext x
      simp
    rw [hset]
    exact hv

/-- Relative connected-shore split inside a finite vertex set.  The output is
stated in the ambient vertex type, rather than in the subtype on `S`. -/
theorem exists_connected_finset_split_of_induce (H : SimpleGraph V) (S : Finset V)
    (hcard : 2 ≤ S.card) (hconn : (H.induce (S : Set V)).Connected) :
    ∃ U : Finset V,
      U.Nonempty ∧ U ⊆ S ∧ U ≠ S ∧
        (H.induce (U : Set V)).Connected ∧
          (H.induce ((S \ U : Finset V) : Set V)).Connected := by
  have hcard' : 1 < S.card := by omega
  letI : Nontrivial (S : Set V) :=
    Fintype.one_lt_card_iff_nontrivial.mp (by simpa using hcard')
  obtain ⟨v, hv⟩ :=
    hconn.exists_connected_induce_compl_singleton_of_finite_nontrivial
  let U : Finset V := {v.1}
  have hUne : U.Nonempty := by simp [U]
  have hUsub : U ⊆ S := by
    rw [show U = {v.1} from rfl, singleton_subset_iff]
    exact v.2
  have hUneS : U ≠ S := by
    intro hUS
    have : U.card < S.card := by
      simp [U]
      omega
    rw [hUS] at this
    exact (lt_self_iff_false S.card).mp this
  have hUconn : (H.induce (U : Set V)).Connected := by
    change (H.induce (({v.1} : Finset V) : Set V)).Connected
    rw [coe_singleton, induce_singleton_eq_top]
    exact connected_top
  let f :
      (H.induce (S : Set V)).induce ({v}ᶜ : Set (S : Set V)) →g
        H.induce ((S \ U : Finset V) : Set V) :=
    { toFun := fun x =>
        ⟨x.1.1, by
          rw [Finset.mem_coe, Finset.mem_sdiff]
          refine ⟨x.1.2, ?_⟩
          change x.1.1 ∉ ({v.1} : Finset V)
          rw [Finset.mem_singleton]
          intro hx
          apply x.2
          simp only [Set.mem_singleton_iff]
          exact Subtype.ext hx⟩
      map_rel' := by
        intro x y hxy
        exact hxy }
  have hf : Function.Surjective f := by
    intro y
    have hyS : y.1 ∈ S := (Finset.mem_sdiff.mp y.2).1
    have hyne : y.1 ≠ v.1 := by
      intro hy
      exact (Finset.mem_sdiff.mp y.2).2 (Finset.mem_singleton.mpr hy)
    let xS : (S : Set V) := ⟨y.1, hyS⟩
    have hxcomp : xS ∈ ({v}ᶜ : Set (S : Set V)) := by
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      intro hx
      apply hyne
      exact congrArg Subtype.val hx
    refine ⟨⟨xS, hxcomp⟩, ?_⟩
    apply Subtype.ext
    rfl
  exact ⟨U, hUne, hUsub, hUneS, hUconn, hv.map f hf⟩

end SimpleGraph

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- A connected concrete cage on at least two vertices has complementary
restrictions that are both proper relative to the cage. -/
theorem exists_proper_restrict_pair_of_connected
    (C : AmbientCage G c)
    (hconn : ((Distances.blueGraph G c).induce (C.verts : Set V)).Connected)
    (hcard : 2 ≤ C.verts.card) :
    ∃ U : Finset V,
      U.Nonempty ∧ U ⊆ C.verts ∧ U ≠ C.verts ∧
        ProperRelative C (restrict C U) ∧
          ProperRelative C (restrictCompl C U) := by
  obtain ⟨U, hUne, hUsub, hUneC, hUconn, hcompconn⟩ :=
    SimpleGraph.exists_connected_finset_split_of_induce
      (Distances.blueGraph G c) C.verts hcard hconn
  have hdouble : C.verts \ (C.verts \ U) = U := by
    ext x
    constructor
    · intro hx
      rw [Finset.mem_sdiff] at hx
      by_contra hxU
      exact hx.2 (Finset.mem_sdiff.mpr ⟨hx.1, hxU⟩)
    · intro hxU
      exact Finset.mem_sdiff.mpr
        ⟨hUsub hxU, fun hx => (Finset.mem_sdiff.mp hx).2 hxU⟩
  have hleft : ProperRelative C (restrict C U) := by
    refine
      { verts_subset := ?_
        verts_ne := ?_
        insideBlueConnected := ?_
        complementBlueConnected := ?_ }
    · change U ⊆ C.verts
      exact hUsub
    · change U ≠ C.verts
      exact hUneC
    · change ((Distances.blueGraph G c).induce (U : Set V)).Connected
      exact hUconn
    · change
        ((Distances.blueGraph G c).induce
          ((C.verts \ U : Finset V) : Set V)).Connected
      exact hcompconn
  have hright : ProperRelative C (restrictCompl C U) := by
    refine
      { verts_subset := ?_
        verts_ne := ?_
        insideBlueConnected := ?_
        complementBlueConnected := ?_ }
    · change C.verts \ U ⊆ C.verts
      exact Finset.sdiff_subset
    · change C.verts \ U ≠ C.verts
      intro heq
      obtain ⟨x, hxU⟩ := hUne
      have hxDiff : x ∈ C.verts \ U := by
        rw [heq]
        exact hUsub hxU
      exact (Finset.mem_sdiff.mp hxDiff).2 hxU
    · change
        ((Distances.blueGraph G c).induce
          ((C.verts \ U : Finset V) : Set V)).Connected
      exact hcompconn
    · change
        ((Distances.blueGraph G c).induce
          ((C.verts \ (C.verts \ U) : Finset V) : Set V)).Connected
      rw [hdouble]
      exact hUconn
  exact ⟨U, hUne, hUsub, hUneC, hleft, hright⟩

/-- Connectedness and two vertices supply the proper shores required by the
all-length-five concrete pure-lens split theorem. -/
theorem exists_pureLensCageSplit_of_all_ell5_connected
    (F : BankFrame (V := V)) (C : AmbientCage G c)
    (hconn : ((Distances.blueGraph G c).induce (C.verts : Set V)).Connected)
    (hcard : 2 ≤ C.verts.card)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    ∃ U : Finset V,
      U.Nonempty ∧ U ⊆ C.verts ∧ U ≠ C.verts ∧
        ProperRelative C (restrict C U) ∧
          ProperRelative C (restrictCompl C U) ∧
            Ell5PureLensCageInterface.PureLensCageSplit
              (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
              C (restrict C U) (restrictCompl C U) := by
  obtain ⟨U, hUne, hUsub, hUneC, hleft, hright⟩ :=
    exists_proper_restrict_pair_of_connected C hconn hcard
  exact
    ⟨U, hUne, hUsub, hUneC, hleft, hright,
      pureLensCageSplit_of_all_ell5_proper_shores F C U hell5 hleft hright⟩

end ConcreteCage
end Ell5
end Erdos23Delta0
