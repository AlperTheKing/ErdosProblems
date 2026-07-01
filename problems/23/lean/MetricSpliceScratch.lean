import Mathlib

/-!
Scratch formalization for the metric part of the two-contact splice lemma.

This file is not the final Formal Conjectures target.  It isolates the Nat
arithmetic behind the row-side splice:

* an `f`-row through a witness exit `q` is shortest;
* forcing the same `f` terminals through a non-witness exit `p` costs an
  extra slack `s`;
* therefore the `g` middle segment through `p` is at least `s` longer than the
  corresponding `f` middle segment;
* substituting the `f` middle into the shortest `g` row saves at least `s`.
-/

namespace Erdos23
namespace MetricSplice

theorem middle_segment_saves_slack
    (fLeft fMid fRight gLeft gMid gRight Df Dg s : Nat)
    (hfShortest : fLeft + fMid + fRight = Df)
    (hfViaP : Df + s ≤ fLeft + gMid + fRight)
    (hgShortest : gLeft + gMid + gRight = Dg) :
    gLeft + fMid + gRight + s ≤ Dg := by
  omega

theorem replacement_saves_two
    (fLeft fMid fRight gLeft gMid gRight Df Dg s : Nat)
    (hfShortest : fLeft + fMid + fRight = Df)
    (hfViaP : Df + s ≤ fLeft + gMid + fRight)
    (hgShortest : gLeft + gMid + gRight = Dg)
    (hs : 2 ≤ s) :
    gLeft + fMid + gRight + 2 ≤ Dg := by
  have hsaves : gLeft + fMid + gRight + s ≤ Dg :=
    middle_segment_saves_slack
      fLeft fMid fRight gLeft gMid gRight Df Dg s
      hfShortest hfViaP hgShortest
  omega

theorem replacement_length_le_sub_two
    (fLeft fMid fRight gLeft gMid gRight Df Dg s : Nat)
    (hfShortest : fLeft + fMid + fRight = Df)
    (hfViaP : Df + s ≤ fLeft + gMid + fRight)
    (hgShortest : gLeft + gMid + gRight = Dg)
    (hs : 2 ≤ s) :
    gLeft + fMid + gRight ≤ Dg - 2 := by
  have hsaves : gLeft + fMid + gRight + 2 ≤ Dg :=
    replacement_saves_two
      fLeft fMid fRight gLeft gMid gRight Df Dg s
      hfShortest hfViaP hgShortest hs
  omega

theorem spliced_walk_length_le_sub_two {V : Type*} {G : SimpleGraph V}
    {tauF z w sigmaF tauG sigmaG : V}
    (fLeft : G.Walk tauF z) (fMid : G.Walk z w) (fRight : G.Walk w sigmaF)
    (gLeft : G.Walk tauG z) (gMid : G.Walk z w) (gRight : G.Walk w sigmaG)
    (Df Dg s : Nat)
    (hfShortest : ((fLeft.append fMid).append fRight).length = Df)
    (hfViaP : Df + s ≤ ((fLeft.append gMid).append fRight).length)
    (hgShortest : ((gLeft.append gMid).append gRight).length = Dg)
    (hs : 2 ≤ s) :
    ((gLeft.append fMid).append gRight).length ≤ Dg - 2 := by
  simp only [SimpleGraph.Walk.length_append] at hfShortest hfViaP hgShortest ⊢
  exact replacement_length_le_sub_two
    fLeft.length fMid.length fRight.length
    gLeft.length gMid.length gRight.length
    Df Dg s hfShortest hfViaP hgShortest hs

theorem spliced_dist_le_sub_two {V : Type*} {G : SimpleGraph V}
    {tauF z w sigmaF tauG sigmaG : V}
    (fLeft : G.Walk tauF z) (fMid : G.Walk z w) (fRight : G.Walk w sigmaF)
    (gLeft : G.Walk tauG z) (gMid : G.Walk z w) (gRight : G.Walk w sigmaG)
    (Df Dg s : Nat)
    (hfShortest : ((fLeft.append fMid).append fRight).length = Df)
    (hfViaP : Df + s ≤ ((fLeft.append gMid).append fRight).length)
    (hgShortest : ((gLeft.append gMid).append gRight).length = Dg)
    (hs : 2 ≤ s) :
    G.dist tauG sigmaG ≤ Dg - 2 := by
  exact le_trans (SimpleGraph.dist_le ((gLeft.append fMid).append gRight))
    (spliced_walk_length_le_sub_two
      fLeft fMid fRight gLeft gMid gRight Df Dg s
      hfShortest hfViaP hgShortest hs)

theorem spliced_dist_contradicts_shortest {V : Type*} {G : SimpleGraph V}
    {tauF z w sigmaF tauG sigmaG : V}
    (fLeft : G.Walk tauF z) (fMid : G.Walk z w) (fRight : G.Walk w sigmaF)
    (gLeft : G.Walk tauG z) (gMid : G.Walk z w) (gRight : G.Walk w sigmaG)
    (Df Dg s : Nat)
    (hfShortest : ((fLeft.append fMid).append fRight).length = Df)
    (hfViaP : Df + s ≤ ((fLeft.append gMid).append fRight).length)
    (hgShortest : ((gLeft.append gMid).append gRight).length = Dg)
    (hs : 2 ≤ s)
    (hdist : G.dist tauG sigmaG = Dg)
    (hDg : 2 ≤ Dg) :
    False := by
  have hle : G.dist tauG sigmaG ≤ Dg - 2 :=
    spliced_dist_le_sub_two
      fLeft fMid fRight gLeft gMid gRight Df Dg s
      hfShortest hfViaP hgShortest hs
  rw [hdist] at hle
  omega

/--
Combined row-side strictness lemma: an even nonzero terminal slack supplies the
`2 ≤ s` input needed for the metric splice.
-/
theorem spliced_dist_le_of_even_nonzero_slack {V : Type*} {G : SimpleGraph V}
    {tauF z w sigmaF tauG sigmaG : V}
    (fLeft : G.Walk tauF z) (fMid : G.Walk z w) (fRight : G.Walk w sigmaF)
    (gLeft : G.Walk tauG z) (gMid : G.Walk z w) (gRight : G.Walk w sigmaG)
    (Df Dg s : Nat)
    (hfShortest : ((fLeft.append fMid).append fRight).length = Df)
    (hfViaP : Df + s ≤ ((fLeft.append gMid).append fRight).length)
    (hgShortest : ((gLeft.append gMid).append gRight).length = Dg)
    (heven : (2 : Nat) ∣ s) (hne : s ≠ 0) :
    G.dist tauG sigmaG ≤ Dg - 2 := by
  have hs : 2 ≤ s := by
    rcases heven with ⟨k, rfl⟩
    cases k with
    | zero =>
        simp at hne
    | succ k =>
        omega
  exact spliced_dist_le_sub_two
    fLeft fMid fRight gLeft gMid gRight Df Dg s
    hfShortest hfViaP hgShortest hs

theorem spliced_even_slack_contradicts_shortest {V : Type*} {G : SimpleGraph V}
    {tauF z w sigmaF tauG sigmaG : V}
    (fLeft : G.Walk tauF z) (fMid : G.Walk z w) (fRight : G.Walk w sigmaF)
    (gLeft : G.Walk tauG z) (gMid : G.Walk z w) (gRight : G.Walk w sigmaG)
    (Df Dg s : Nat)
    (hfShortest : ((fLeft.append fMid).append fRight).length = Df)
    (hfViaP : Df + s ≤ ((fLeft.append gMid).append fRight).length)
    (hgShortest : ((gLeft.append gMid).append gRight).length = Dg)
    (heven : (2 : Nat) ∣ s) (hne : s ≠ 0)
    (hdist : G.dist tauG sigmaG = Dg)
    (hDg : 2 ≤ Dg) :
    False := by
  have hle : G.dist tauG sigmaG ≤ Dg - 2 :=
    spliced_dist_le_of_even_nonzero_slack
      fLeft fMid fRight gLeft gMid gRight Df Dg s
      hfShortest hfViaP hgShortest heven hne
  rw [hdist] at hle
  omega

end MetricSplice
end Erdos23
