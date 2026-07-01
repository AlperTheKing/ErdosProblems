import Mathlib

/-!
Scratch formalization for the S2 reduced-theta core.

This file is not the final Formal Conjectures target.  It isolates the Nat
arithmetic behind `S2-Core 1` from
`problems/23/writeup/S2_FROZEN_STATEMENT.md`.
-/

namespace Erdos23
namespace S2Core

open SimpleGraph

/-- A walk is shortest among walks with the same endpoints. -/
def WalkShortest {V : Type*} {G : SimpleGraph V} {u v : V} (p : G.Walk u v) : Prop :=
  ∀ q : G.Walk u v, p.length ≤ q.length

/-- Prefixes of shortest walks are shortest. -/
theorem shortest_takeUntil_of_shortest {V : Type*} {G : SimpleGraph V}
    [DecidableEq V] {u v w : V}
    {p : G.Walk u v} (hp : WalkShortest p) (hw : w ∈ p.support) :
    WalkShortest (p.takeUntil w hw) := by
  intro q
  let r := p.dropUntil w hw
  have hp' : p.length ≤ (q.append r).length := hp (q.append r)
  have hlen : (p.takeUntil w hw).length + r.length = p.length := by
    calc
      (p.takeUntil w hw).length + r.length =
          ((p.takeUntil w hw).append r).length := by
        exact (SimpleGraph.Walk.length_append (p.takeUntil w hw) r).symm
      _ = p.length := by
        change ((p.takeUntil w hw).append (p.dropUntil w hw)).length = p.length
        exact congrArg (fun q => q.length) (p.take_spec hw)
  have hmain :
      (p.takeUntil w hw).length + r.length ≤ q.length + r.length := by
    simpa [SimpleGraph.Walk.length_append, hlen.symm, r] using hp'
  exact (Nat.add_le_add_iff_right).mp hmain

/-- Suffixes of shortest walks are shortest. -/
theorem shortest_dropUntil_of_shortest {V : Type*} {G : SimpleGraph V}
    [DecidableEq V] {u v w : V}
    {p : G.Walk u v} (hp : WalkShortest p) (hw : w ∈ p.support) :
    WalkShortest (p.dropUntil w hw) := by
  intro q
  let l := p.takeUntil w hw
  have hp' : p.length ≤ (l.append q).length := hp (l.append q)
  have hlen : l.length + (p.dropUntil w hw).length = p.length := by
    calc
      l.length + (p.dropUntil w hw).length =
          (l.append (p.dropUntil w hw)).length := by
        exact (SimpleGraph.Walk.length_append l (p.dropUntil w hw)).symm
      _ = p.length := by
        change ((p.takeUntil w hw).append (p.dropUntil w hw)).length = p.length
        exact congrArg (fun q => q.length) (p.take_spec hw)
  have hmain :
      l.length + (p.dropUntil w hw).length ≤ l.length + q.length := by
    simpa [SimpleGraph.Walk.length_append, hlen.symm, l] using hp'
  exact (Nat.add_le_add_iff_left).mp hmain

/-- A subwalk obtained by dropping to `a` and then taking until `b` is shortest. -/
theorem shortest_takeUntil_dropUntil_of_shortest {V : Type*} {G : SimpleGraph V}
    [DecidableEq V] {u v a b : V}
    {p : G.Walk u v} (hp : WalkShortest p) (ha : a ∈ p.support)
    (hb : b ∈ (p.dropUntil a ha).support) :
    WalkShortest ((p.dropUntil a ha).takeUntil b hb) :=
  shortest_takeUntil_of_shortest (shortest_dropUntil_of_shortest hp ha) hb

/-- Two shortest walks with the same endpoints have equal length. -/
theorem length_eq_of_shortest {V : Type*} {G : SimpleGraph V} {u v : V}
    {p q : G.Walk u v} (hp : WalkShortest p) (hq : WalkShortest q) :
    p.length = q.length :=
  Nat.le_antisymm (hp q) (hq p)

/--
In a shortest walk, there is no graph edge joining two nonconsecutive positions:
such an edge would splice out the intervening segment.
-/
theorem no_adj_getVert_of_shortest {V : Type*} {G : SimpleGraph V} {u v : V}
    {p : G.Walk u v} (hp : WalkShortest p) {i j : ℕ}
    (hij : i + 1 < j) (hj : j ≤ p.length) :
    ¬ G.Adj (p.getVert i) (p.getVert j) := by
  intro hadj
  have hi : i ≤ p.length := by omega
  let edge : G.Walk (p.getVert i) (p.getVert j) :=
    SimpleGraph.Walk.cons hadj SimpleGraph.Walk.nil
  let q : G.Walk u v := ((p.take i).append edge).append (p.drop j)
  have hq_lt : q.length < p.length := by
    simp [q, edge, SimpleGraph.Walk.length_append, SimpleGraph.Walk.take_length,
      SimpleGraph.Walk.drop_length, SimpleGraph.Walk.length_cons,
      SimpleGraph.Walk.length_nil, Nat.min_eq_left hi]
    omega
  have hq_ge : p.length ≤ q.length := hp q
  omega

/--
Row-facing form of the previous lemma: a shortest corridor has no shortcut edge
between nonconsecutive corridor positions.
-/
theorem no_nonconsecutive_shortcut_of_shortest_corridor
    {V : Type*} {J : SimpleGraph V} {u v : V} {corridor : J.Walk u v}
    (hshort : WalkShortest corridor) {i j : ℕ}
    (hij : i + 1 < j) (hj : j ≤ corridor.length)
    (hshortcut : J.Adj (corridor.getVert i) (corridor.getVert j)) :
    False :=
  no_adj_getVert_of_shortest hshort hij hj hshortcut

/-- The exit co-witness graph induced by a witness relation. -/
def coWitnessGraph {A B : Type*} (W : A → B → Prop) : SimpleGraph B where
  Adj e e' := e ≠ e' ∧ ∃ a, W a e ∧ W a e'
  symm := by
    intro e e' h
    rcases h with ⟨hne, a, he, he'⟩
    exact ⟨hne.symm, a, he', he⟩
  loopless := by
    intro e h
    exact h.1 rfl

/-- A common witness gives an edge in the co-witness graph. -/
theorem coWitnessGraph_adj_of_common_witness {A B : Type*} {W : A → B → Prop}
    {a : A} {e e' : B} (hne : e ≠ e') (he : W a e) (he' : W a e') :
    (coWitnessGraph W).Adj e e' :=
  ⟨hne, a, he, he'⟩

/--
A hinge/common witness cannot witness two nonconsecutive exits on a shortest
co-witness corridor.
-/
theorem no_nonconsecutive_common_witness_of_shortest_corridor
    {A B : Type*} {W : A → B → Prop}
    {u v : B} {corridor : (coWitnessGraph W).Walk u v}
    (hshort : WalkShortest corridor) {i j : ℕ}
    (hij : i + 1 < j) (hj : j ≤ corridor.length)
    {a : A}
    (hne : corridor.getVert i ≠ corridor.getVert j)
    (hi : W a (corridor.getVert i))
    (hjw : W a (corridor.getVert j)) :
    False :=
  no_nonconsecutive_shortcut_of_shortest_corridor hshort hij hj
    (coWitnessGraph_adj_of_common_witness hne hi hjw)

/--
If the endpoints of a corridor are chosen with minimum walk length among
distinct marked pairs, then no internal corridor vertex is marked.

This is the pure graph kernel behind: after choosing two missed exits at
minimum `J`-distance, all internal exits of the shortest `J`-corridor are
witnessed by the reference row.
-/
theorem no_internal_marked_of_minimal_marked_corridor
    {V : Type*} {J : SimpleGraph V} {u v : V} {corridor : J.Walk u v}
    (Marked : V → Prop) (hu : Marked u) (hv : Marked v) (huv : u ≠ v)
    (hmin :
      ∀ {x y : V}, Marked x → Marked y → x ≠ y → ∀ q : J.Walk x y,
        corridor.length ≤ q.length)
    {i : ℕ} (hi0 : 0 < i) (hil : i < corridor.length) :
    ¬ Marked (corridor.getVert i) := by
  intro hm
  by_cases hne_u : u ≠ corridor.getVert i
  · have hle := hmin hu hm hne_u (corridor.take i)
    have htake : (corridor.take i).length = i := by
      rw [SimpleGraph.Walk.take_length]
      exact Nat.min_eq_left (le_of_lt hil)
    rw [htake] at hle
    omega
  · push_neg at hne_u
    have h_eq : corridor.getVert i = u := hne_u.symm
    have hne_v : corridor.getVert i ≠ v := by
      intro hvtx
      exact huv (h_eq.symm.trans hvtx)
    have hle := hmin hm hv hne_v (corridor.drop i)
    rw [SimpleGraph.Walk.drop_length] at hle
    omega

theorem replacement_length_le
    (pref oldArm newArm suffix D : Nat)
    (hD : D = pref + oldArm + suffix)
    (hsave : newArm + 2 ≤ oldArm) :
    pref + newArm + suffix ≤ D - 2 := by
  subst D
  omega

theorem replacement_length_lt
    (pref oldArm newArm suffix D : Nat)
    (hD : D = pref + oldArm + suffix)
    (hsave : newArm + 2 ≤ oldArm) :
    pref + newArm + suffix < D := by
  subst D
  omega

theorem replacement_walk_length_le {V : Type*} {G : SimpleGraph V}
    {a r s b : V}
    (pref : G.Walk a r) (oldArm newArm : G.Walk r s) (suffix : G.Walk s b)
    (D : Nat)
    (hD : D = ((pref.append oldArm).append suffix).length)
    (hsave : newArm.length + 2 ≤ oldArm.length) :
    ((pref.append newArm).append suffix).length ≤ D - 2 := by
  subst D
  simp only [SimpleGraph.Walk.length_append]
  omega

theorem replacement_walk_length_lt {V : Type*} {G : SimpleGraph V}
    {a r s b : V}
    (pref : G.Walk a r) (oldArm newArm : G.Walk r s) (suffix : G.Walk s b)
    (D : Nat)
    (hD : D = ((pref.append oldArm).append suffix).length)
    (hsave : newArm.length + 2 ≤ oldArm.length) :
    ((pref.append newArm).append suffix).length < D := by
  subst D
  simp only [SimpleGraph.Walk.length_append]
  omega

def ShorterWalk {V : Type*} (G : SimpleGraph V) (a b : V) (D : Nat) : Prop :=
  ∃ p : G.Walk a b, p.length ≤ D - 2

theorem shorterWalk_of_replacement {V : Type*} {G : SimpleGraph V}
    {a r s b : V}
    (pref : G.Walk a r) (oldArm newArm : G.Walk r s) (suffix : G.Walk s b)
    (D : Nat)
    (hD : D = ((pref.append oldArm).append suffix).length)
    (hsave : newArm.length + 2 ≤ oldArm.length) :
    ShorterWalk G a b D := by
  refine ⟨(pref.append newArm).append suffix, ?_⟩
  exact replacement_walk_length_le pref oldArm newArm suffix D hD hsave

theorem dist_le_of_shorterWalk {V : Type*} {G : SimpleGraph V}
    {a b : V} {D : Nat}
    (h : ShorterWalk G a b D) :
    G.dist a b ≤ D - 2 := by
  rcases h with ⟨p, hp⟩
  exact le_trans (SimpleGraph.dist_le p) hp

theorem replacement_dist_le {V : Type*} {G : SimpleGraph V}
    {a r s b : V}
    (pref : G.Walk a r) (oldArm newArm : G.Walk r s) (suffix : G.Walk s b)
    (D : Nat)
    (hD : D = ((pref.append oldArm).append suffix).length)
    (hsave : newArm.length + 2 ≤ oldArm.length) :
    G.dist a b ≤ D - 2 := by
  exact dist_le_of_shorterWalk
    (shorterWalk_of_replacement pref oldArm newArm suffix D hD hsave)

theorem no_replacement_of_dist_eq {V : Type*} {G : SimpleGraph V}
    {a b : V} {D : Nat}
    (hdist : G.dist a b = D)
    (hD : 2 ≤ D)
    (hshort : ShorterWalk G a b D) :
    False := by
  have hle : G.dist a b ≤ D - 2 := dist_le_of_shorterWalk hshort
  rw [hdist] at hle
  omega

def IsTriangle {V : Type*} (G : SimpleGraph V) (u x v : V) : Prop :=
  u ≠ x ∧ x ≠ v ∧ v ≠ u ∧ G.Adj u x ∧ G.Adj x v ∧ G.Adj v u

theorem triangle_of_adj {V : Type*} {G : SimpleGraph V} {u x v : V}
    (hux : G.Adj u x) (hxv : G.Adj x v) (hvu : G.Adj v u)
    (hux_ne : u ≠ x) (hxv_ne : x ≠ v) (hvu_ne : v ≠ u) :
    IsTriangle G u x v := by
  exact ⟨hux_ne, hxv_ne, hvu_ne, hux, hxv, hvu⟩

theorem triangle_of_blue_and_bad {V : Type*} {G B : SimpleGraph V} {u x v : V}
    (hB : B ≤ G)
    (hux : B.Adj u x) (hxv : B.Adj x v) (huv : G.Adj u v)
    (hux_ne : u ≠ x) (hxv_ne : x ≠ v) (hvu_ne : v ≠ u) :
    IsTriangle G u x v := by
  exact triangle_of_adj (hB hux) (hB hxv) huv.symm hux_ne hxv_ne hvu_ne

theorem s2_core_wrapper {V : Type*} {G : SimpleGraph V}
    {a r s b u x v : V} {Door : Prop}
    (pref : G.Walk a r) (oldArm newArm : G.Walk r s) (suffix : G.Walk s b)
    (D : Nat)
    (hD : D = ((pref.append oldArm).append suffix).length)
    (hgeom :
      Door ∨
      IsTriangle G u x v ∨
      newArm.length + 2 ≤ oldArm.length) :
    Door ∨ IsTriangle G u x v ∨ ShorterWalk G a b D := by
  rcases hgeom with hdoor | hrest
  · exact Or.inl hdoor
  rcases hrest with htri | hsave
  · exact Or.inr (Or.inl htri)
  · exact Or.inr (Or.inr (shorterWalk_of_replacement pref oldArm newArm suffix D hD hsave))

end S2Core
end Erdos23
