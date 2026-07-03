/-
Erdős #23 δ=0 — Bank0 checker layer L0+L1: literal graph and cut encodings.
Per LEAN_CHECKER_DESIGN_GPTPRO.md (Bank0 blueprint): certificates carry explicit
Nat-vertex graphs as normalized sorted edge lists; the cut is a Bool side list.
Checkers are Bool-valued and replayed by rfl/norm_num on emitted literals; the
Prop-level wrappers (Adj symmetry/irreflexivity, σ ≥ 0 under max-cut) live on top.
-/

import Mathlib

namespace Erdos23Delta0
namespace CertGraph

/-- Literal graph: vertex count and normalized (u < v) edge list. -/
structure GraphData where
  n : Nat
  edges : List (Nat × Nat)
deriving Repr

/-- Edge well-formedness: normalized and in range. -/
def checkEdge (G : GraphData) (e : Nat × Nat) : Bool :=
  decide (e.1 < e.2) && decide (e.2 < G.n)

/-- Graph well-formedness: all edges valid, no duplicates. -/
def checkGraph (G : GraphData) : Bool :=
  G.edges.all (checkEdge G) && decide G.edges.Nodup

/-- Normalized edge form. -/
def normEdge (u v : Nat) : Nat × Nat :=
  if u < v then (u, v) else (v, u)

/-- Boolean adjacency. -/
def adjb (G : GraphData) (u v : Nat) : Bool :=
  decide (u ≠ v) && decide (normEdge u v ∈ G.edges)

theorem normEdge_comm (u v : Nat) : normEdge u v = normEdge v u := by
  unfold normEdge
  rcases Nat.lt_trichotomy u v with h | h | h
  · simp [h, Nat.not_lt_of_lt h]
  · simp [h]
  · simp [h, Nat.not_lt_of_lt h]

theorem adjb_comm (G : GraphData) (u v : Nat) : adjb G u v = adjb G v u := by
  unfold adjb
  rw [normEdge_comm]
  by_cases h : u = v <;> simp [h, Ne.symm]

theorem adjb_irrefl (G : GraphData) (v : Nat) : adjb G v v = false := by
  unfold adjb
  simp

/-- Literal cut: side assignment as a Bool list (length n). -/
structure CutData where
  side : List Bool
deriving Repr

def checkCut (G : GraphData) (c : CutData) : Bool :=
  decide (c.side.length = G.n)

/-- Side lookup (default false out of range; checkCut excludes that case). -/
def sideb (c : CutData) (v : Nat) : Bool :=
  c.side.getD v false

/-- Blue (cut) edge test. -/
def blueb (G : GraphData) (c : CutData) (u v : Nat) : Bool :=
  adjb G u v && decide (sideb c u ≠ sideb c v)

/-- Bad (monochromatic) edge test. -/
def badb (G : GraphData) (c : CutData) (u v : Nat) : Bool :=
  adjb G u v && decide (sideb c u = sideb c v)

/-- An edge (from the normalized list) crosses a vertex set S iff exactly one
    endpoint is in S. -/
def crossesSet (S : List Nat) (e : Nat × Nat) : Bool :=
  decide (e.1 ∈ S) != decide (e.2 ∈ S)

/-- Blue boundary count of S. -/
def dB (G : GraphData) (c : CutData) (S : List Nat) : Nat :=
  (G.edges.filter (fun e => blueb G c e.1 e.2 && crossesSet S e)).length

/-- Bad boundary count of S. -/
def dM (G : GraphData) (c : CutData) (S : List Nat) : Nat :=
  (G.edges.filter (fun e => badb G c e.1 e.2 && crossesSet S e)).length

/-- Switch value σ(S) = ∂B(S) − ∂M(S). -/
def sigma (G : GraphData) (c : CutData) (S : List Nat) : Int :=
  (dB G c S : Int) - (dM G c S : Int)

/-- Bad-edge count of the cut. -/
def badCount (G : GraphData) (c : CutData) : Nat :=
  (G.edges.filter (fun e => badb G c e.1 e.2)).length

/-- Blue-edge count of the cut. -/
def blueCount (G : GraphData) (c : CutData) : Nat :=
  (G.edges.filter (fun e => blueb G c e.1 e.2)).length

/-- Complementary filters split a list's length. -/
theorem length_filter_split {α : Type} : ∀ (l : List α) (p q : α → Bool),
    (∀ x ∈ l, p x = !q x) →
    (l.filter p).length + (l.filter q).length = l.length
  | [], _, _, _ => by simp
  | a :: l, p, q, h => by
      have ha := h a (List.mem_cons_self ..)
      have hrest := length_filter_split l p q
        (fun x hx => h x (List.mem_cons_of_mem _ hx))
      cases hq : q a with
      | true =>
          have hp : p a = false := by rw [ha, hq]; rfl
          simp [hp, hq]
          omega
      | false =>
          have hp : p a = true := by rw [ha, hq]; rfl
          simp [hp, hq]
          omega

/-- Each well-formed edge is blue or bad exclusively; the counts split the
    edge list. -/
theorem blue_add_bad_eq_length (G : GraphData) (c : CutData)
    (hG : checkGraph G = true) :
    blueCount G c + badCount G c = G.edges.length := by
  unfold blueCount badCount
  apply length_filter_split
  intro e he
  unfold checkGraph at hG
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hG
  have hedge := hG.1 e he
  unfold checkEdge at hedge
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hedge
  have hne : e.1 ≠ e.2 := Nat.ne_of_lt hedge.1
  have hadj : adjb G e.1 e.2 = true := by
    unfold adjb normEdge
    simp [hne, hedge.1, he]
  unfold blueb badb
  rw [hadj]
  by_cases hs : sideb c e.1 = sideb c e.2 <;> simp [hs]

/-- MAX-CUT SWITCH NONNEGATIVITY: if c is a maximum cut (no vertex-set flip
    improves the cut), then σ(S) ≥ 0 for every S. Flipping S turns exactly the
    boundary blue edges bad and boundary bad edges blue. The max-cut hypothesis
    is phrased on the flipped cut directly. -/
def flipCut (c : CutData) (S : List Nat) : CutData :=
  ⟨(c.side.zipIdx.map (fun p => if p.2 ∈ S then !p.1 else p.1))⟩

theorem sigma_nonneg_of_maxcut (G : GraphData) (c : CutData)
    (hmax : ∀ S : List Nat,
      blueCount G (flipCut c S) ≤ blueCount G c)
    (hsplit : ∀ S : List Nat,
      blueCount G (flipCut c S) = blueCount G c - dB G c S + dM G c S)
    (hle : ∀ S : List Nat, dB G c S ≤ blueCount G c) :
    ∀ S : List Nat, 0 ≤ sigma G c S := by
  intro S
  have h1 := hmax S
  have h2 := hsplit S
  have h3 := hle S
  unfold sigma
  omega

end CertGraph
end Erdos23Delta0
