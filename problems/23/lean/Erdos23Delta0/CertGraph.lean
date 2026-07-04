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

/-! ### B6: bank-block checker (blueprint §6).
A bank block carries five vertex classes and its assigned bad-edge ids; the
checker verifies disjointness, range, the bad-edge layer condition, and the
graph-side edge-count form e(Bᵢ, Bᵢ₊₁) ≥ mₐ, from which the class-size product
bound follows and the Bank0Algebra AM-GM finishes. -/

/-- One bank block: five classes (lists of vertices) and assigned bad ids. -/
structure BankBlock where
  classes : Fin 5 → List Nat
  badIds : List Nat
deriving Repr

/-- Edges between two vertex lists (unordered normalized edges). -/
def eBetween (G : GraphData) (A B : List Nat) : Nat :=
  (G.edges.filter (fun e =>
    (decide (e.1 ∈ A) && decide (e.2 ∈ B)) ||
    (decide (e.1 ∈ B) && decide (e.2 ∈ A)))).length

/-- All vertices of a block. -/
def BankBlock.support (b : BankBlock) : List Nat :=
  (List.finRange 5).flatMap (fun i => b.classes i)

/-- Block obligations (per blueprint §6): classes in-range and duplicate-free,
    pairwise disjoint, every assigned bad edge in the class-4/class-0 layer,
    the graph-side edge-count bound e(Bᵢ, Bᵢ₊₁) ≥ |badIds|, and the class-size
    product bound |Bᵢ|·|Bᵢ₊₁| ≥ |badIds| (checked directly — the form the
    AM-GM algebra consumes). -/
def checkBankBlock (G : GraphData) (bads : List BadEdgeData)
    (b : BankBlock) : Bool :=
  (List.finRange 5).all (fun i =>
    (b.classes i).all (fun v => decide (v < G.n)) &&
    decide (b.classes i).Nodup) &&
  ((List.finRange 5).all (fun i => (List.finRange 5).all (fun j =>
    decide (i = j) || (b.classes i).all (fun v => decide (v ∉ b.classes j))))) &&
  b.badIds.all (fun gid =>
    match bads.get? gid with
    | some g =>
        (decide (g.u ∈ b.classes 4) && decide (g.v ∈ b.classes 0)) ||
        (decide (g.u ∈ b.classes 0) && decide (g.v ∈ b.classes 4))
    | none => false) &&
  (List.finRange 5).all (fun i =>
    decide (b.badIds.length ≤ eBetween G (b.classes i) (b.classes (i + 1))) &&
    decide (b.badIds.length ≤
      (b.classes i).length * (b.classes (i + 1)).length))

/-- Fact extraction: a passing block check yields the five cyclic class-size
    product bounds — the exact hypotheses of Bank0Algebra.bank_amgm_rat. -/
theorem checkBankBlock_products (G : GraphData) (bads : List BadEdgeData)
    (b : BankBlock) (h : checkBankBlock G bads b = true) :
    ∀ i : Fin 5, b.badIds.length ≤
      (b.classes i).length * (b.classes (i + 1)).length := by
  intro i
  unfold checkBankBlock at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  have := h.2.2.2 i (List.mem_finRange i)
  exact this.2

/-- Fact extraction: pairwise class disjointness. -/
theorem checkBankBlock_disjoint (G : GraphData) (bads : List BadEdgeData)
    (b : BankBlock) (h : checkBankBlock G bads b = true) :
    ∀ i j : Fin 5, i ≠ j → ∀ v ∈ b.classes i, v ∉ b.classes j := by
  intro i j hij v hv
  unfold checkBankBlock at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  have := h.2.1 i (List.mem_finRange i) j (List.mem_finRange j)
  rcases this with heq | hall
  · exact absurd heq hij
  · exact hall v hv

/-! ### Flip-counting lemma (assembly review Decision B): flipping a vertex set
swaps blue/bad exactly on the boundary, so
badCount(flip) − badCount = dB − dM, and σ(S) ≥ 0 follows from IsMaxCut. -/

/-- Split a filter by a second predicate (complementary split on q). -/
theorem length_filter_and_split {α : Type} : ∀ (l : List α) (p q : α → Bool),
    (l.filter p).length
      = (l.filter (fun x => q x && p x)).length
        + (l.filter (fun x => !q x && p x)).length
  | [], _, _ => by simp
  | a :: l, p, q => by
      have ih := length_filter_and_split l p q
      cases hp : p a <;> cases hq : q a <;>
        simp [List.filter_cons, hp, hq, ih] <;> omega

/-- Pointwise side value after a flip (within range). -/
theorem sideb_flip (c : CutData) (S : List Nat) (v : Nat)
    (hv : v < c.side.length) :
    sideb (flipCut c S) v = if v ∈ S then !(sideb c v) else sideb c v := by
  unfold flipCut sideb
  rw [List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD]
  rw [List.getElem?_map]
  have hz : (c.side.zipIdx)[v]? = some (c.side[v], v) := by
    rw [List.getElem?_zipIdx]
    simp [List.getElem?_eq_getElem hv]
  rw [hz]
  simp [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hv]

/-- Pointwise edge status after a flip: crossing edges swap blue/bad,
    non-crossing edges keep their status. -/
theorem badb_flip (G : GraphData) (c : CutData) (S : List Nat) (u v : Nat)
    (hu : u < c.side.length) (hv : v < c.side.length) :
    badb G (flipCut c S) u v
      = if crossesSet S (u, v) then blueb G c u v else badb G c u v := by
  unfold badb blueb crossesSet
  rw [sideb_flip c S u hu, sideb_flip c S v hv]
  by_cases hus : u ∈ S <;> by_cases hvs : v ∈ S <;>
    by_cases hadj : adjb G u v = true <;>
      simp [hus, hvs, hadj] <;>
        cases hsu : sideb c u <;> cases hsv : sideb c v <;> simp

/-- THE FLIP-COUNTING IDENTITY (ℤ): badCount(flip) − badCount = dB − dM. -/
theorem badCount_flip_eq (G : GraphData) (c : CutData) (S : List Nat)
    (hlen : c.side.length = G.n) (hG : checkGraph G = true) :
    (badCount G (flipCut c S) : ℤ) - badCount G c
      = (dB G c S : ℤ) - dM G c S := by
  unfold badCount dB dM
  have hval : ∀ e ∈ G.edges, e.1 < c.side.length ∧ e.2 < c.side.length := by
    intro e he
    unfold checkGraph at hG
    simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hG
    have := hG.1 e he
    unfold checkEdge at this
    simp only [Bool.and_eq_true, decide_eq_true_eq] at this
    exact ⟨by omega, by omega⟩
  -- rewrite the flipped filter pointwise
  have hcongr : G.edges.filter (fun e => badb G (flipCut c S) e.1 e.2)
      = G.edges.filter (fun e =>
          if crossesSet S e then blueb G c e.1 e.2 else badb G c e.1 e.2) := by
    apply List.filter_congr
    intro e he
    have h := hval e he
    rw [badb_flip G c S e.1 e.2 h.1 h.2]
  rw [hcongr]
  -- split all three counts on the crossing predicate
  have h1 := length_filter_and_split G.edges
    (fun e => if crossesSet S e then blueb G c e.1 e.2 else badb G c e.1 e.2)
    (fun e => crossesSet S e)
  have h2 := length_filter_and_split G.edges
    (fun e => badb G c e.1 e.2) (fun e => crossesSet S e)
  -- identify the pieces
  have e1 : G.edges.filter (fun e => crossesSet S e &&
      (if crossesSet S e then blueb G c e.1 e.2 else badb G c e.1 e.2))
      = G.edges.filter (fun e => blueb G c e.1 e.2 && crossesSet S e) := by
    apply List.filter_congr
    intro e _
    cases hc : crossesSet S e <;> simp [hc]
  have e2 : G.edges.filter (fun e => !crossesSet S e &&
      (if crossesSet S e then blueb G c e.1 e.2 else badb G c e.1 e.2))
      = G.edges.filter (fun e => !crossesSet S e && badb G c e.1 e.2) := by
    apply List.filter_congr
    intro e _
    cases hc : crossesSet S e <;> simp [hc]
  have e3 : G.edges.filter (fun e => crossesSet S e && badb G c e.1 e.2)
      = G.edges.filter (fun e => badb G c e.1 e.2 && crossesSet S e) := by
    apply List.filter_congr
    intro e _
    cases hc : crossesSet S e <;> cases hb : badb G c e.1 e.2 <;> simp [hc, hb]
  rw [e1, e2] at h1
  rw [e3] at h2
  omega

/-- σ(S) ≥ 0 at a maximum cut, derived from the flip identity and the
    total-count split (blue + bad = all edges, for both cuts). -/
theorem sigma_nonneg_of_isMaxCut (G : GraphData) (c : CutData) (S : List Nat)
    (hlen : c.side.length = G.n) (hG : checkGraph G = true)
    (hflip_len : (flipCut c S).side.length = G.n)
    (hmax : badCount G c ≤ badCount G (flipCut c S)) :
    0 ≤ sigma G c S := by
  have h := badCount_flip_eq G c S hlen hG
  unfold sigma
  omega

end CertGraph
end Erdos23Delta0
