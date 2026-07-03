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

/-! ### L2: rows and the all-ℓ=5 row database (blueprint §L2). -/

/-- A length-five row: the bad-edge id and its five vertices in order. -/
structure Row5 where
  badId : Nat
  verts : List Nat
deriving Repr

/-- Row well-formedness against the graph, cut, and its bad edge (u,v):
    five in-range distinct vertices from u to v, four blue steps, bad closing. -/
def checkRow5 (G : GraphData) (c : CutData) (u v : Nat) (r : Row5) : Bool :=
  decide (r.verts.length = 5) &&
  r.verts.all (fun w => decide (w < G.n)) &&
  decide r.verts.Nodup &&
  decide (r.verts.head? = some u) &&
  decide (r.verts.getLast? = some v) &&
  (List.zip r.verts r.verts.tail).all (fun p => blueb G c p.1 p.2) &&
  badb G c u v

/-- A bad edge with its full shortest-row list (|cyc| = rows.length). -/
structure BadEdgeData where
  u : Nat
  v : Nat
  rows : List Row5
deriving Repr

def checkBadEdge (G : GraphData) (c : CutData) (b : BadEdgeData) : Bool :=
  badb G c b.u b.v &&
  decide (b.rows ≠ []) &&
  b.rows.all (checkRow5 G c b.u b.v)

/-- Distance certificate: no blue connection of length ≤ 3 between the bad
    endpoints (with the length-4 row displayed, this pins dist = 4, ℓ = 5).
    Path-freeness is certified as literal exclusion lists checked elsewhere;
    here the record carries the checked flags. -/
structure Dist4Cert where
  noBlueLen1 : Bool
  noBlueLen2 : Bool
  noBlueLen3 : Bool
deriving Repr

def Dist4Cert.ok (d : Dist4Cert) : Bool :=
  d.noBlueLen1 && d.noBlueLen2 && d.noBlueLen3

/-! ### L3: row atoms and integer pressure arithmetic (blueprint §L3).
All loads are cleared by a global denominator D: an atom (weight, vertex)
contributes weight = D / |cyc(badId)| for each row occurrence, so that
sNum U = D·s(U). -/

/-- One cleared row-load atom. -/
structure AtomData where
  weight : Nat
  vertex : Nat
  badId : Nat
  rowId : Nat
deriving Repr

/-- Atom consistency: weight · rowCount(badId) = D and the vertex lies on the
    referenced row. rowCounts is the per-bad-edge row count list. -/
def checkAtom (D : Nat) (rowCounts : List Nat) (bads : List BadEdgeData)
    (a : AtomData) : Bool :=
  match rowCounts.get? a.badId, bads.get? a.badId with
  | some rc, some b =>
      decide (a.weight * rc = D) &&
      (match b.rows.get? a.rowId with
       | some r => decide (a.vertex ∈ r.verts)
       | none => false)
  | _, _ => false

def checkAtoms (D : Nat) (rowCounts : List Nat) (bads : List BadEdgeData)
    (atoms : List AtomData) : Bool :=
  decide (0 < D) && atoms.all (checkAtom D rowCounts bads)

/-- Cleared load numerator sNum(U) = D·s(U). -/
def sNum (atoms : List AtomData) (U : List Nat) : Nat :=
  ((atoms.filter (fun a => decide (a.vertex ∈ U))).map AtomData.weight).sum

/-- Cleared pressure Π_D(U) = 5·sNum(U) − D·N·|U|. -/
def pressureNum (G : GraphData) (atoms : List AtomData) (D : Nat)
    (U : List Nat) : Int :=
  (5 * sNum atoms U : Int) - (D * G.n * U.length : Int)

/-- Cleared Hall slack ν₀,D(C) = D·N·|C| − 5·sNum(C) = −Π_D(C). -/
def nu0Num (G : GraphData) (atoms : List AtomData) (D : Nat)
    (C : List Nat) : Int :=
  (D * G.n * C.length : Int) - (5 * sNum atoms C : Int)

theorem nu0_eq_neg_pressure (G : GraphData) (atoms : List AtomData) (D : Nat)
    (C : List Nat) : nu0Num G atoms D C = -pressureNum G atoms D C := by
  unfold nu0Num pressureNum
  ring

/-- Corridor-partition additivity core (blueprint L3/O1): sNum is additive over
    a list-level split of U (the disjoint owned cores concatenate to U). -/
theorem sNum_append : ∀ (atoms : List AtomData) (U₁ U₂ : List Nat),
    (∀ a ∈ atoms, ¬(a.vertex ∈ U₁ ∧ a.vertex ∈ U₂)) →
    sNum atoms (U₁ ++ U₂) = sNum atoms U₁ + sNum atoms U₂
  | [], _, _, _ => by simp [sNum]
  | a :: as, U₁, U₂, hdisj => by
      have hd := hdisj a (List.mem_cons_self ..)
      have ih := sNum_append as U₁ U₂
        (fun x hx => hdisj x (List.mem_cons_of_mem _ hx))
      unfold sNum at *
      by_cases h1 : a.vertex ∈ U₁
      · have h2 : a.vertex ∉ U₂ := fun h => hd ⟨h1, h⟩
        have hm : a.vertex ∈ U₁ ++ U₂ := List.mem_append.mpr (Or.inl h1)
        simp only [List.filter_cons, hm, h1, h2, decide_true, decide_false,
          if_true, if_false, List.map_cons, List.sum_cons]
        omega
      · by_cases h2 : a.vertex ∈ U₂
        · have hm : a.vertex ∈ U₁ ++ U₂ := List.mem_append.mpr (Or.inr h2)
          simp only [List.filter_cons, hm, h1, h2, decide_true, decide_false,
            if_true, if_false, List.map_cons, List.sum_cons]
          omega
        · have hm : a.vertex ∉ U₁ ++ U₂ := by
            rw [List.mem_append]
            rintro (h | h)
            · exact h1 h
            · exact h2 h
          simp only [List.filter_cons, hm, h1, h2, decide_false, if_false]
          omega

/-- Pressure additivity over a disjoint split (the LOAD_ACCOUNT obligation in
    integer form): ν₀ of the concatenation is the sum of the parts. -/
theorem nu0_append (G : GraphData) (atoms : List AtomData) (D : Nat)
    (U₁ U₂ : List Nat)
    (hdisj : ∀ a ∈ atoms, ¬(a.vertex ∈ U₁ ∧ a.vertex ∈ U₂)) :
    nu0Num G atoms D (U₁ ++ U₂) = nu0Num G atoms D U₁ + nu0Num G atoms D U₂ := by
  unfold nu0Num
  rw [sNum_append atoms U₁ U₂ hdisj, List.length_append]
  push_cast
  ring

end CertGraph
end Erdos23Delta0
