import Erdos23Delta0.Gamma.CommonBlueExtendedMatching
import Erdos23Delta0.Gamma.ActiveScopedCoordinateTransport

/-!
# Static endpoint sources created by a live R37 detour

For a live row replacement

`[a, x, m, y, b] -> [a, x, v, y, b]`,

a unique old endpoint pair `(m,a)` (respectively `(m,b)`) becomes a free
ordered pair in the post-detour row choice.  The old row supplies the common
blue owner `x` (respectively `y`).  If the corresponding two-vertex switch
has sigma at least two, both physical halves satisfy the production
`CommonBlueOwner` predicate.  Triangle-freeness also shows that neither half
is an active-edge reservation.

This module is deliberately static.  It does not prove the hypotheses
`2 <= sigma G c [m,a]` or `2 <= sigma G c [m,b]`, and `unreserved` does not
mean unused by an already chosen matching.
-/

namespace Erdos23Delta0
namespace Gamma
namespace LiveDetourEndpointSource

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange
open CommonBlueExtendedMatching

attribute [local instance] Classical.propDecidable

private theorem adjb_of_blueb
    {G : GraphData} {c : CutData} {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem blueb_comm (G : GraphData) (c : CutData) (u v : Nat) :
    blueb G c u v = blueb G c v u := by
  unfold blueb
  rw [adjb_comm]
  by_cases h : sideb c u = sideb c v <;> simp [h, Ne.symm]

private theorem adjb_of_active_adj
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {u v : Fin G.n}
    (h : (activeGraph G c omega).Adj u v) :
    adjb G u.1 v.1 = true := by
  rcases h with ⟨hne, hmem⟩
  have hedge : normEdge u.1 v.1 ∈ G.edges := by
    simp only [activeEdges, List.mem_filter] at hmem
    exact hmem.1
  unfold adjb
  simp only [Bool.and_eq_true, decide_eq_true_eq]
  exact ⟨fun huv => hne (Fin.ext huv), hedge⟩

/-- A common-blue source pair cannot itself be an active edge in a
triangle-free graph: together with its common blue owner it would form a
triangle. -/
theorem commonBlueOwner_not_activeAdj_of_triangleFree
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {owner : Fin G.n} {s : FreeHalf G omega}
    (htri : TriangleFree G) (hcommon : CommonBlueOwner G c owner s) :
    ¬(activeGraph G c omega).Adj s.sourceX s.sourceY := by
  intro hactive
  have hvalid := hcommon
  unfold CommonBlueOwner at hvalid
  have hxoBlue : blueb G c s.sourceX.1 owner.1 = true :=
    hvalid.2.2.2.2.1
  have hyoBlue : blueb G c s.sourceY.1 owner.1 = true :=
    hvalid.2.2.2.2.2.1
  have hxo : adjb G s.sourceX.1 owner.1 = true := adjb_of_blueb hxoBlue
  have hoy : adjb G owner.1 s.sourceY.1 = true := by
    rw [adjb_comm]
    exact adjb_of_blueb hyoBlue
  have hxy : adjb G s.sourceX.1 s.sourceY.1 = true :=
    adjb_of_active_adj hactive
  have hxoNe : s.sourceX.1 ≠ owner.1 := by
    unfold adjb at hxo
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hxo
    exact hxo.1
  have hoyNe : owner.1 ≠ s.sourceY.1 := by
    unfold adjb at hoy
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hoy
    exact hoy.1
  exact htri s.sourceX.1 owner.1 s.sourceY.1
    s.sourceX.isLt owner.isLt s.sourceY.isLt hxoNe hoyNe
    (Fin.val_injective.ne s.distinct) ⟨hxo, hoy, hxy⟩

/-- Production reservation exclusion for every triangle-free common-blue
source. -/
theorem commonBlueOwner_not_scopedReserved_of_triangleFree
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {owner : Fin G.n} {s : FreeHalf G omega}
    (htri : TriangleFree G) (hcommon : CommonBlueOwner G c owner s) :
    ¬ScopedReserved G c omega s := by
  intro hreserved
  exact (commonBlueOwner_not_activeAdj_of_triangleFree htri hcommon)
    hreserved.2.1

/-- The older active-half reservation is excluded as well. -/
theorem commonBlueOwner_not_reserved_of_triangleFree
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {owner : Fin G.n} {s : FreeHalf G omega}
    (htri : TriangleFree G) (hcommon : CommonBlueOwner G c owner s) :
    ¬Reserved G c omega s := by
  intro hreserved
  exact (commonBlueOwner_not_activeAdj_of_triangleFree htri hcommon)
    ⟨s.distinct, hreserved.2⟩

/-- If the changed row is the unique selected row containing a pair and the
replacement omits that pair, then its post-replacement multiplicity is zero.
-/
theorem pairCount_replaceOne_eq_zero_of_unique_old_pair
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length)
    (p q : Nat)
    (hpOld : p ∈ ((bads.get index).rows.get (omega index)).verts)
    (hqOld : q ∈ ((bads.get index).rows.get (omega index)).verts)
    (hnew : ¬(p ∈ ((bads.get index).rows.get replacement).verts ∧
      q ∈ ((bads.get index).rows.get replacement).verts))
    (hunique : pairCount omega p q = 1) :
    pairCount (replaceOne omega index replacement) p q = 0 := by
  classical
  let oldSet := Finset.univ.filter fun j : Fin bads.length =>
    p ∈ ((bads.get j).rows.get (omega j)).verts ∧
      q ∈ ((bads.get j).rows.get (omega j)).verts
  let newSet := Finset.univ.filter fun j : Fin bads.length =>
    p ∈ ((bads.get j).rows.get (replaceOne omega index replacement j)).verts ∧
      q ∈ ((bads.get j).rows.get (replaceOne omega index replacement j)).verts
  have hiOld : index ∈ oldSet := by
    exact Finset.mem_filter.mpr ⟨Finset.mem_univ index, hpOld, hqOld⟩
  have hOldCard : oldSet.card = 1 := by
    simpa [oldSet, ActiveScopedMinimumExchange.pairCount_eq_card_filter] using
      hunique
  have hsub : newSet ⊆ oldSet.erase index := by
    intro j hj
    have hjNew :
        p ∈ ((bads.get j).rows.get (replaceOne omega index replacement j)).verts ∧
          q ∈ ((bads.get j).rows.get
            (replaceOne omega index replacement j)).verts := by
      simpa [newSet] using hj
    have hji : j ≠ index := by
      intro h
      subst j
      rw [replaceOne_apply_self] at hjNew
      exact hnew hjNew
    have hjOld :
        p ∈ ((bads.get j).rows.get (omega j)).verts ∧
          q ∈ ((bads.get j).rows.get (omega j)).verts := by
      simpa only [replaceOne_apply_of_ne omega index j replacement hji] using
        hjNew
    exact Finset.mem_erase.mpr ⟨hji, by simpa [oldSet] using hjOld⟩
  have hEraseCard : (oldSet.erase index).card = 0 := by
    rw [Finset.card_erase_of_mem hiOld, hOldCard]
  rw [ActiveScopedMinimumExchange.pairCount_eq_card_filter]
  change newSet.card = 0
  exact Nat.eq_zero_of_le_zero
    (hEraseCard ▸ Finset.card_le_card hsub)

/-- Literal checked data for the live one-row detour.  The replacement is
required to be a checked row, even though endpoint-source freeness only uses
its displayed vertex list and `middle_ne`. -/
structure LiveDetourData
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length)
    (a x m y b v : Fin G.n) : Prop where
  old_verts : ((bads.get index).rows.get (omega index)).verts =
    [a.1, x.1, m.1, y.1, b.1]
  new_verts : ((bads.get index).rows.get replacement).verts =
    [a.1, x.1, v.1, y.1, b.1]
  old_valid : checkRow5 G c (bads.get index).u (bads.get index).v
    ((bads.get index).rows.get (omega index)) = true
  new_valid : checkRow5 G c (bads.get index).u (bads.get index).v
    ((bads.get index).rows.get replacement) = true
  middle_ne : m ≠ v

namespace LiveDetourData

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {omega : RowChoice bads} {index : Fin bads.length}
  {replacement : Fin (bads.get index).rows.length}
  {a x m y b v : Fin G.n}

def postChoice
    (_D : LiveDetourData G c omega index replacement a x m y b v) :
    RowChoice bads :=
  replaceOne omega index replacement

theorem old_nodup
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    [a.1, x.1, m.1, y.1, b.1].Nodup := by
  have h := D.old_valid
  unfold checkRow5 at h
  rw [D.old_verts] at h
  simp only [Bool.and_eq_true] at h
  have hdec : decide [a.1, x.1, m.1, y.1, b.1].Nodup = true := by
    aesop
  exact of_decide_eq_true hdec

theorem old_blue_steps
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    blueb G c a.1 x.1 = true ∧
      blueb G c x.1 m.1 = true ∧
      blueb G c m.1 y.1 = true ∧
      blueb G c y.1 b.1 = true := by
  have h := D.old_valid
  unfold checkRow5 at h
  rw [D.old_verts] at h
  simp only [Bool.and_eq_true] at h
  have hpath :
      (List.zip [a.1, x.1, m.1, y.1, b.1]
        [a.1, x.1, m.1, y.1, b.1].tail).all
          (fun p => blueb G c p.1 p.2) = true := by
    aesop
  simpa using hpath

theorem middle_ne_old_vertices
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    m.1 ≠ a.1 ∧ m.1 ≠ x.1 ∧ m.1 ≠ y.1 ∧ m.1 ≠ b.1 := by
  have hnd := D.old_nodup
  simp at hnd
  aesop

theorem middle_not_mem_new
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    m.1 ∉ ((bads.get index).rows.get replacement).verts := by
  rw [D.new_verts]
  have hold := D.middle_ne_old_vertices
  have hmv : m.1 ≠ v.1 := by
    intro h
    exact D.middle_ne (Fin.ext h)
  simp [hold.1, hold.2.1, hmv, hold.2.2.1, hold.2.2.2]

theorem left_distinct
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    m ≠ a := by
  intro h
  exact D.middle_ne_old_vertices.1 (congrArg Fin.val h)

theorem right_distinct
    (D : LiveDetourData G c omega index replacement a x m y b v) :
    m ≠ b := by
  intro h
  exact D.middle_ne_old_vertices.2.2.2 (congrArg Fin.val h)

theorem left_pairCount_post_eq_zero
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 a.1 = 1) :
    pairCount D.postChoice m.1 a.1 = 0 := by
  apply pairCount_replaceOne_eq_zero_of_unique_old_pair omega index replacement
  · rw [D.old_verts]
    simp
  · rw [D.old_verts]
    simp
  · intro h
    exact D.middle_not_mem_new h.1
  · exact hunique

theorem right_pairCount_post_eq_zero
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 b.1 = 1) :
    pairCount D.postChoice m.1 b.1 = 0 := by
  apply pairCount_replaceOne_eq_zero_of_unique_old_pair omega index replacement
  · rw [D.old_verts]
    simp
  · rw [D.old_verts]
    simp
  · intro h
    exact D.middle_not_mem_new h.1
  · exact hunique

/-- Canonical post-detour left endpoint half `(m,a,bit)`. -/
def leftHalf
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 a.1 = 1) (bit : Fin 2) :
    FreeHalf G D.postChoice where
  sourceX := m
  sourceY := a
  half := bit
  distinct := D.left_distinct
  free := D.left_pairCount_post_eq_zero hunique

/-- Canonical post-detour right endpoint half `(m,b,bit)`. -/
def rightHalf
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 b.1 = 1) (bit : Fin 2) :
    FreeHalf G D.postChoice where
  sourceX := m
  sourceY := b
  half := bit
  distinct := D.right_distinct
  free := D.right_pairCount_post_eq_zero hunique

theorem leftHalf_commonBlue
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 a.1 = 1)
    (hsigma : (2 : Int) ≤ sigma G c [m.1, a.1]) (bit : Fin 2) :
    CommonBlueOwner G c x (D.leftHalf hunique bit) := by
  have hsteps := D.old_blue_steps
  have hmx : blueb G c m.1 x.1 = true := by
    rw [blueb_comm]
    exact hsteps.2.1
  have hbound : dM G c [m.1, a.1] + 2 ≤ dB G c [m.1, a.1] := by
    unfold sigma at hsigma
    omega
  change m.1 < G.n ∧ a.1 < G.n ∧ x.1 < G.n ∧ m.1 ≠ a.1 ∧
    blueb G c m.1 x.1 = true ∧ blueb G c a.1 x.1 = true ∧
      dM G c [m.1, a.1] + 2 ≤ dB G c [m.1, a.1]
  exact ⟨m.isLt, a.isLt, x.isLt, Fin.val_injective.ne D.left_distinct,
    hmx, hsteps.1, hbound⟩

theorem rightHalf_commonBlue
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (hunique : pairCount omega m.1 b.1 = 1)
    (hsigma : (2 : Int) ≤ sigma G c [m.1, b.1]) (bit : Fin 2) :
    CommonBlueOwner G c y (D.rightHalf hunique bit) := by
  have hsteps := D.old_blue_steps
  have hby : blueb G c b.1 y.1 = true := by
    rw [blueb_comm]
    exact hsteps.2.2.2
  have hbound : dM G c [m.1, b.1] + 2 ≤ dB G c [m.1, b.1] := by
    unfold sigma at hsigma
    omega
  change m.1 < G.n ∧ b.1 < G.n ∧ y.1 < G.n ∧ m.1 ≠ b.1 ∧
    blueb G c m.1 y.1 = true ∧ blueb G c b.1 y.1 = true ∧
      dM G c [m.1, b.1] + 2 ≤ dB G c [m.1, b.1]
  exact ⟨m.isLt, b.isLt, y.isLt, Fin.val_injective.ne D.right_distinct,
    hsteps.2.2.1, hby, hbound⟩

/-- Full static production facts for either physical left endpoint half. -/
theorem leftHalf_sound
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (htri : TriangleFree G)
    (hunique : pairCount omega m.1 a.1 = 1)
    (hsigma : (2 : Int) ≤ sigma G c [m.1, a.1]) (bit : Fin 2) :
    CommonBlueOwner G c x (D.leftHalf hunique bit) ∧
      ¬ScopedReserved G c D.postChoice (D.leftHalf hunique bit) ∧
      ¬Reserved G c D.postChoice (D.leftHalf hunique bit) ∧
      (commonBlueTerminalData x (D.leftHalf hunique bit)).check G c = true := by
  have hcommon := D.leftHalf_commonBlue hunique hsigma bit
  exact ⟨hcommon,
    commonBlueOwner_not_scopedReserved_of_triangleFree htri hcommon,
    commonBlueOwner_not_reserved_of_triangleFree htri hcommon,
    commonBlue_check_eq_true hcommon⟩

/-- Full static production facts for either physical right endpoint half. -/
theorem rightHalf_sound
    (D : LiveDetourData G c omega index replacement a x m y b v)
    (htri : TriangleFree G)
    (hunique : pairCount omega m.1 b.1 = 1)
    (hsigma : (2 : Int) ≤ sigma G c [m.1, b.1]) (bit : Fin 2) :
    CommonBlueOwner G c y (D.rightHalf hunique bit) ∧
      ¬ScopedReserved G c D.postChoice (D.rightHalf hunique bit) ∧
      ¬Reserved G c D.postChoice (D.rightHalf hunique bit) ∧
      (commonBlueTerminalData y (D.rightHalf hunique bit)).check G c = true := by
  have hcommon := D.rightHalf_commonBlue hunique hsigma bit
  exact ⟨hcommon,
    commonBlueOwner_not_scopedReserved_of_triangleFree htri hcommon,
    commonBlueOwner_not_reserved_of_triangleFree htri hcommon,
    commonBlue_check_eq_true hcommon⟩

end LiveDetourData

#print axioms pairCount_replaceOne_eq_zero_of_unique_old_pair
#print axioms commonBlueOwner_not_scopedReserved_of_triangleFree
#print axioms LiveDetourData.left_pairCount_post_eq_zero
#print axioms LiveDetourData.right_pairCount_post_eq_zero
#print axioms LiveDetourData.leftHalf_sound
#print axioms LiveDetourData.rightHalf_sound

end LiveDetourEndpointSource
end Gamma
end Erdos23Delta0





