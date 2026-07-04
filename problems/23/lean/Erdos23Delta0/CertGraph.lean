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
  match rowCounts[a.badId]?, bads[a.badId]? with
  | some rc, some b =>
      decide (a.weight * rc = D) &&
      (match b.rows[a.rowId]? with
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
        rw [List.filter_cons_of_pos (by simpa using hm),
          List.filter_cons_of_pos (by simpa using h1),
          List.filter_cons_of_neg (by simpa using h2)]
        simp only [List.map_cons, List.sum_cons]
        omega
      · by_cases h2 : a.vertex ∈ U₂
        · have hm : a.vertex ∈ U₁ ++ U₂ := List.mem_append.mpr (Or.inr h2)
          rw [List.filter_cons_of_pos (by simpa using hm),
            List.filter_cons_of_neg (by simpa using h1),
            List.filter_cons_of_pos (by simpa using h2)]
          simp only [List.map_cons, List.sum_cons]
          omega
        · have hm : a.vertex ∉ U₁ ++ U₂ := by
            rw [List.mem_append]
            rintro (h | h)
            · exact h1 h
            · exact h2 h
          rw [List.filter_cons_of_neg (by simpa using hm),
            List.filter_cons_of_neg (by simpa using h1),
            List.filter_cons_of_neg (by simpa using h2)]
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
    match bads[gid]? with
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
  exact (h.2 i (List.mem_finRange i)).2

/-- Fact extraction: pairwise class disjointness. -/
theorem checkBankBlock_disjoint (G : GraphData) (bads : List BadEdgeData)
    (b : BankBlock) (h : checkBankBlock G bads b = true) :
    ∀ i j : Fin 5, i ≠ j → ∀ v ∈ b.classes i, v ∉ b.classes j := by
  intro i j hij v hv
  unfold checkBankBlock at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  have hb := h.1.1.2 i (List.mem_finRange i) j (List.mem_finRange j)
  rw [Bool.or_eq_true] at hb
  rcases hb with heq | hall
  · exact absurd (of_decide_eq_true heq) hij
  · exact of_decide_eq_true (List.all_eq_true.mp hall v hv)

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
        simp [hp, hq, ih] <;> omega

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
  simp [List.getElem?_eq_getElem hv]

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
    cases hc : crossesSet S e <;> simp
  have e2 : G.edges.filter (fun e => !crossesSet S e &&
      (if crossesSet S e then blueb G c e.1 e.2 else badb G c e.1 e.2))
      = G.edges.filter (fun e => !crossesSet S e && badb G c e.1 e.2) := by
    apply List.filter_congr
    intro e _
    cases hc : crossesSet S e <;> simp
  have e3 : G.edges.filter (fun e => crossesSet S e && badb G c e.1 e.2)
      = G.edges.filter (fun e => badb G c e.1 e.2 && crossesSet S e) := by
    apply List.filter_congr
    intro e _
    cases hc : crossesSet S e <;> cases hb : badb G c e.1 e.2 <;> simp
  rw [e1, e2] at h1
  rw [e3] at h2
  omega

/-- σ(S) ≥ 0 at a maximum cut, derived from the flip identity and the
    total-count split (blue + bad = all edges, for both cuts). -/
theorem sigma_nonneg_of_isMaxCut (G : GraphData) (c : CutData) (S : List Nat)
    (hlen : c.side.length = G.n) (hG : checkGraph G = true)
    (_hflip_len : (flipCut c S).side.length = G.n)
    (hmax : badCount G c ≤ badCount G (flipCut c S)) :
    0 ≤ sigma G c S := by
  have h := badCount_flip_eq G c S hlen hG
  unfold sigma
  omega

/-! ### B2: owned-core corridor partition checker (blueprint §3 + canon).
The packet is BY CONSTRUCTION the concatenation of the owned cores, so
LOAD_ACCOUNT additivity is repeated `nu0_append` over the pairwise-disjoint
pieces — no coverage pigeonhole. The consumer presents the packet in
corridor-partitioned order (emission convention). -/

/-- Partition certificate: owned cores (vertex lists) plus the index of the
    claimed negative corridor. -/
structure CorridorPartitionCert where
  corridors : List (List Nat)
  negIdx : Nat
deriving Repr

/-- The packet represented by the partition. -/
def partPacket (c : CorridorPartitionCert) : List Nat :=
  c.corridors.flatMap id

/-- Boolean pairwise-disjointness of vertex lists. -/
def pairwiseDisjB : List (List Nat) → Bool
  | [] => true
  | co :: rest =>
      rest.all (fun co' => co.all (fun v => decide (v ∉ co'))) &&
      pairwiseDisjB rest

/-- Partition obligations: cores duplicate-free and nonempty, pairwise
    disjoint, in graph range, and the claimed corridor has ν₀ < 0. -/
def checkCorridorPartition (G : GraphData) (atoms : List AtomData) (D : Nat)
    (c : CorridorPartitionCert) : Bool :=
  c.corridors.all (fun co =>
    decide (co ≠ []) && decide co.Nodup &&
    co.all (fun v => decide (v < G.n))) &&
  pairwiseDisjB c.corridors &&
  (match c.corridors[c.negIdx]? with
   | some co => decide (nu0Num G atoms D co < 0)
   | none => false)

/-- Head-vs-tail disjointness extracted from the boolean check. -/
theorem pairwiseDisjB_head (co : List Nat) (rest : List (List Nat))
    (h : pairwiseDisjB (co :: rest) = true) :
    ∀ v ∈ co, v ∉ rest.flatMap id := by
  unfold pairwiseDisjB at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  intro v hv hmem
  rw [List.mem_flatMap] at hmem
  obtain ⟨co', hco', hvco'⟩ := hmem
  exact h.1 co' hco' v hv hvco'

theorem pairwiseDisjB_tail (co : List Nat) (rest : List (List Nat))
    (h : pairwiseDisjB (co :: rest) = true) :
    pairwiseDisjB rest = true := by
  unfold pairwiseDisjB at h
  simp only [Bool.and_eq_true] at h
  exact h.2

/-- LOAD_ACCOUNT (B2 additivity): ν₀ of the packet is the sum of the
    per-corridor ν₀ values, from pairwise disjointness alone. -/
theorem nu0_partition (G : GraphData) (atoms : List AtomData) (D : Nat) :
    ∀ (cos : List (List Nat)), pairwiseDisjB cos = true →
    nu0Num G atoms D (cos.flatMap id)
      = (cos.map (nu0Num G atoms D)).sum
  | [], _ => by simp [nu0Num, sNum]
  | co :: rest, h => by
      have hd := pairwiseDisjB_head co rest h
      have ih := nu0_partition G atoms D rest (pairwiseDisjB_tail co rest h)
      simp only [List.flatMap_cons, List.map_cons, List.sum_cons, id_eq]
      rw [nu0_append G atoms D co (rest.flatMap id)
        (fun a _ => fun ⟨h1, h2⟩ => hd a.vertex h1 h2), ih]

/-- Negative-corridor extraction: a passing partition check yields a corridor
    with strictly negative ν₀ (the corridor the dichotomy consumes). -/
theorem negative_corridor_of_check (G : GraphData) (atoms : List AtomData)
    (D : Nat) (c : CorridorPartitionCert)
    (h : checkCorridorPartition G atoms D c = true) :
    ∃ co ∈ c.corridors, nu0Num G atoms D co < 0 := by
  unfold checkCorridorPartition at h
  simp only [Bool.and_eq_true] at h
  rcases hg : c.corridors[c.negIdx]? with _ | co
  · rw [hg] at h
    simp at h
  · rw [hg] at h
    rcases List.getElem?_eq_some_iff.mp hg with ⟨hlt, hco⟩
    refine ⟨co, hco ▸ List.getElem_mem hlt, ?_⟩
    have := h.2
    simpa using this

/-! ### Canon: completed switches (interface-canon items 1-2).
The completion-trace step enums are data (replay semantics live in the trace
module); the arithmetic and boundary checks are verified here against the
graph, per the canon: boundaries RECOMPUTED, never trusted. -/

/-- Switch-completion step kinds (canon item 2; replay semantics deferred). -/
inductive SwitchCompletionStep
  | OpSegment
  | OpTerminal
  | OpNoncross
  | OpTwin
  | OpFlat5
deriving Repr, DecidableEq

/-- Completion trace (data layer). -/
structure SwitchCompletionTrace where
  start : List Nat
  steps : List SwitchCompletionStep
  final : List Nat
deriving Repr

/-- The canonical completed-switch certificate (canon item 1). -/
structure CompletedSwitchCert where
  S : List Nat
  completionTrace : SwitchCompletionTrace
  blueBoundary : List (Nat × Nat)
  badBoundary : List (Nat × Nat)
  sigmaVal : Int
  oldLenSq : Nat
  newLenSq : Nat
  KVal : Nat
  nuVal : Int
  nuKVal : Int
  flipCutValid : Bool
  flipBConnected : Bool
deriving Repr

/-- Boundary and arithmetic checks (canon: recompute, never trust):
    declared boundaries match the recomputed filters, σ matches the count
    difference, K = oldLenSq, ν = new − old, ν_K = ν + K·σ. -/
def checkCompletedSwitch (G : GraphData) (c : CutData)
    (w : CompletedSwitchCert) : Bool :=
  decide (w.blueBoundary = G.edges.filter
    (fun e => blueb G c e.1 e.2 && crossesSet w.S e)) &&
  decide (w.badBoundary = G.edges.filter
    (fun e => badb G c e.1 e.2 && crossesSet w.S e)) &&
  decide (w.sigmaVal = (w.blueBoundary.length : Int) - w.badBoundary.length) &&
  decide (w.KVal = w.oldLenSq) &&
  decide (w.nuVal = (w.newLenSq : Int) - w.oldLenSq) &&
  decide (w.nuKVal = w.nuVal + w.KVal * w.sigmaVal)

/-- Fact extraction: a passing switch check pins σ to the graph-level value. -/
theorem checkCompletedSwitch_sigma (G : GraphData) (c : CutData)
    (w : CompletedSwitchCert) (h : checkCompletedSwitch G c w = true) :
    w.sigmaVal = sigma G c w.S := by
  unfold checkCompletedSwitch at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  unfold sigma dB dM
  rw [h.1.1.1.2, h.1.1.1.1.1, h.1.1.1.1.2]

/-- Fact extraction: the ν_K ledger identity. -/
theorem checkCompletedSwitch_nuK (G : GraphData) (c : CutData)
    (w : CompletedSwitchCert) (h : checkCompletedSwitch G c w = true) :
    w.nuKVal = ((w.newLenSq : Int) - w.oldLenSq) + w.oldLenSq * w.sigmaVal := by
  unfold checkCompletedSwitch at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  rw [h.2, h.1.2, h.1.1.2]

/-! ### B3: CrossCap capacity certificate (blueprint §CROSSCAP).
The corridor engine's flow argument establishes the scalar capacity inequality
5·sNum(C) + D·N·∂B(C) ≤ D·N·|C| + D·N·∂M(C). Any demand-conserving,
capacity-respecting flow witnesses exactly this inequality (total demand ≤
total capacity), so the checker consumes the inequality on RECOMPUTED
boundary counts and load numerators; the demand/slot/flow lists are
emitter-side payload kept for cross-validation. Soundness needs no
Γ-minimality: a passing check on a ν₀-negative corridor forces
σ(corridor) < 0, contradicting max-cut switch nonnegativity. -/

/-- CrossCap certificate (blueprint field set; declared boundaries are
    compared against recomputation, demand/slot/flow lists are payload). -/
structure CrossCapCert where
  corridor : List Nat
  blueBoundary : List (Nat × Nat)
  badBoundary : List (Nat × Nat)
  rowDemands : List (Nat × Int)
  blueDemands : List (Nat × Int)
  vertexSlots : List (Nat × Int)
  badSlots : List (Nat × Int)
  flows : List (Nat × Nat × Int)
  residuals : List Int
deriving Repr

/-- CrossCap check: corridor well-formed, declared boundaries match the
    recomputed filters (canon: recompute, never trust), and the capacity
    inequality holds on recomputed counts. -/
def checkCrossCap (G : GraphData) (c : CutData) (atoms : List AtomData)
    (D : Nat) (w : CrossCapCert) : Bool :=
  decide (w.corridor ≠ []) && decide w.corridor.Nodup &&
  w.corridor.all (fun v => decide (v < G.n)) &&
  decide (w.blueBoundary = G.edges.filter
    (fun e => blueb G c e.1 e.2 && crossesSet w.corridor e)) &&
  decide (w.badBoundary = G.edges.filter
    (fun e => badb G c e.1 e.2 && crossesSet w.corridor e)) &&
  decide (5 * sNum atoms w.corridor + D * G.n * dB G c w.corridor
    ≤ D * G.n * w.corridor.length + D * G.n * dM G c w.corridor)

/-- Nat-to-Int rearrangement for the capacity inequality. -/
private theorem crossCap_rearrange (a b c d : Nat) (h : a + b ≤ c + d) :
    (b : Int) - (d : Int) ≤ (c : Int) - (a : Int) := by
  omega

/-- Fact extraction: the capacity inequality in ν₀/σ form,
    D·N·σ(C) ≤ ν₀,D(C). -/
theorem checkCrossCap_ineq (G : GraphData) (c : CutData)
    (atoms : List AtomData) (D : Nat) (w : CrossCapCert)
    (h : checkCrossCap G c atoms D w = true) :
    ((D : Int) * G.n) * sigma G c w.corridor ≤ nu0Num G atoms D w.corridor := by
  unfold checkCrossCap at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  have h2 := crossCap_rearrange _ _ _ _ h.2
  unfold sigma nu0Num
  push_cast at h2 ⊢
  nlinarith [h2]

/-- CROSSCAP SOUNDNESS: a passing capacity check on a ν₀-negative corridor
    contradicts max-cut switch nonnegativity (no Γ-minimality needed):
    D·N·σ ≤ ν₀ < 0 with σ ≥ 0 is impossible. -/
theorem crossCap_sound (G : GraphData) (c : CutData) (atoms : List AtomData)
    (D : Nat) (w : CrossCapCert)
    (hcheck : checkCrossCap G c atoms D w = true)
    (hneg : nu0Num G atoms D w.corridor < 0)
    (hmax : ∀ S : List Nat, 0 ≤ sigma G c S) : False := by
  have h1 := checkCrossCap_ineq G c atoms D w hcheck
  have h3 : (0 : Int) ≤ ((D : Int) * G.n) * sigma G c w.corridor :=
    mul_nonneg (by positivity) (hmax w.corridor)
  exact absurd (le_trans h3 h1) (not_le.mpr hneg)

/-- Dichotomy consumer edge: a passing corridor partition plus a CrossCap
    certificate on its negative corridor refute max-cut — i.e. under max-cut
    no such configuration exists. Stated on an explicit corridor so the
    lens-gate layer can select which corridor carries the CrossCap. -/
theorem partition_crossCap_sound (G : GraphData) (c : CutData)
    (atoms : List AtomData) (D : Nat) (pc : CorridorPartitionCert)
    (w : CrossCapCert)
    (hpc : checkCorridorPartition G atoms D pc = true)
    (hsel : pc.corridors[pc.negIdx]? = some w.corridor)
    (hcheck : checkCrossCap G c atoms D w = true)
    (hmax : ∀ S : List Nat, 0 ≤ sigma G c S) : False := by
  have hneg : nu0Num G atoms D w.corridor < 0 := by
    unfold checkCorridorPartition at hpc
    simp only [Bool.and_eq_true] at hpc
    have := hpc.2
    rw [hsel] at this
    simpa using this
  exact crossCap_sound G c atoms D w hcheck hneg hmax

/-! ### B1: bank closure trace replay checker (C1-C4, archived contract).
State = the packet vertex set only; every step is monotone and carries its own
metadata, checked locally against the literal graph/cut/row database. Closedness
is verified RELATIVE to a provided basis; basis completeness is an external
certificate. v1 deviations (all checker-weakenings, hence sound): sortedness is
not enforced (Nodup + range only); the C4 protected-cell payload is deferred to
the protected-cell module; C2 family equality is exact-list (canonical emission
order); C4 witness rows accept either orientation. -/

/-- Row reference: bad-edge id + row index within that bad edge. -/
structure RowRef where
  badId : Nat
  rowIdx : Nat
deriving Repr, DecidableEq

/-- A row prefix: which row, and how many leading vertices (1..4). -/
structure RowPrefixData where
  ref : RowRef
  prefixLen : Nat
deriving Repr, DecidableEq

inductive COrientation
  | forward
  | reverse
deriving Repr, DecidableEq

/-- Closure step kinds (archived C1-C4 contract; C4 carries an explicit trigger). -/
inductive BankClosureStep
  | c1RowInterval (badId rowIdx a b : Nat)
  | c2RowFamily (badId : Nat) (orient : COrientation) (terminal : Nat)
      (firstExit : Nat × Nat) (fam : List RowPrefixData)
  | c3BlueDetour (badId rowIdx edgePos : Nat) (path : List Nat)
  | c4TerminalShadow (shadow trigger : List Nat) (firstExit : Nat × Nat)
      (cell : List Nat) (witnessRows : List RowPrefixData)
deriving Repr

/-- Row-family basis item (terminal-shadow type + its complete family). -/
structure RowFamilyItem where
  badId : Nat
  orient : COrientation
  terminal : Nat
  firstExit : Nat × Nat
  fam : List RowPrefixData
deriving Repr, DecidableEq

structure DetourItem where
  ref : RowRef
  edgePos : Nat
  path : List Nat
deriving Repr, DecidableEq

structure ShadowItem where
  shadow : List Nat
  trigger : List Nat
  firstExit : Nat × Nat
  cell : List Nat
  witnessRows : List RowPrefixData
deriving Repr, DecidableEq

/-- Closedness basis: closure is checked relative to these lists. -/
structure BankClosureBasis where
  rowIntervalBasis : List RowRef
  rowFamilyBasis : List RowFamilyItem
  detourBasis : List DetourItem
  shadowBasis : List ShadowItem
deriving Repr

/-- Pressure claim carried by a trace. -/
inductive PressureClaim
  | none
  | positive
  | nonpos
  | negativeNu0
deriving Repr, DecidableEq

/-- The closure trace object. -/
structure BankClosureTrace where
  start : List Nat
  steps : List BankClosureStep
  final : List Nat
  pressureClaim : PressureClaim
deriving Repr

/-- Row lookup by reference. -/
def getRow (bads : List BadEdgeData) (r : RowRef) : Option Row5 :=
  match bads[r.badId]? with
  | some b => b.rows[r.rowIdx]?
  | none => none

/-- Orient a row so position 0 is the declared terminal end. -/
def orientedVerts (row : Row5) (o : COrientation) : List Nat :=
  match o with
  | .forward => row.verts
  | .reverse => row.verts.reverse

/-- Monotone absorption: append then dedup. -/
def absorbV (U adds : List Nat) : List Nat := (U ++ adds).dedup

theorem mem_absorbV_left (U adds : List Nat) (v : Nat) (hv : v ∈ U) :
    v ∈ absorbV U adds :=
  List.mem_dedup.mpr (List.mem_append.mpr (Or.inl hv))

/-- The complete row-prefix family of a terminal-shadow type, computed from
    the row database (canonical order). -/
def familyOf (bads : List BadEdgeData) (badId : Nat) (o : COrientation)
    (terminal : Nat) (fe : Nat × Nat) : List RowPrefixData :=
  match bads[badId]? with
  | none => []
  | some b =>
      (List.range b.rows.length).flatMap (fun ri =>
        match b.rows[ri]? with
        | none => []
        | some row =>
            let R := orientedVerts row o
            if R.getD 0 0 = terminal then
              (List.range 4).filterMap (fun l0 =>
                let l := l0 + 1
                if normEdge (R.getD (l - 1) 0) (R.getD l 0) = normEdge fe.1 fe.2
                then some ⟨⟨badId, ri⟩, l⟩ else none)
            else [])

/-- Activation of one row prefix by the current packet. -/
def activatedB (bads : List BadEdgeData) (o : COrientation) (U : List Nat)
    (p : RowPrefixData) : Bool :=
  match getRow bads p.ref with
  | none => false
  | some row =>
      let R := orientedVerts row o
      decide (R.getD 0 0 ∈ U) && decide (R.getD (p.prefixLen - 1) 0 ∈ U)

/-- All vertices absorbed by a row-prefix family. -/
def famPrefixVerts (bads : List BadEdgeData) (o : COrientation)
    (fam : List RowPrefixData) : List Nat :=
  fam.flatMap (fun p =>
    match getRow bads p.ref with
    | some row => (orientedVerts row o).take p.prefixLen
    | none => [])

/-- Witness-row check for C4: some orientation puts the prefix inside the
    shadow with the declared first exit. -/
def checkWitnessRow (bads : List BadEdgeData) (shadow : List Nat)
    (fe : Nat × Nat) (p : RowPrefixData) : Bool :=
  match getRow bads p.ref with
  | none => false
  | some row =>
      let tryO (o : COrientation) : Bool :=
        let R := orientedVerts row o
        decide (1 ≤ p.prefixLen) && decide (p.prefixLen ≤ 4) &&
        ((R.take p.prefixLen).all (fun w => decide (w ∈ shadow))) &&
        decide (normEdge (R.getD (p.prefixLen - 1) 0) (R.getD p.prefixLen 0)
          = normEdge fe.1 fe.2)
      tryO .forward || tryO .reverse

/-- Single-step precondition check, returning the vertices to absorb. -/
def stepAdds (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (basis : BankClosureBasis) (U : List Nat) :
    BankClosureStep → Option (List Nat)
  | .c1RowInterval badId rowIdx a b =>
      match getRow bads ⟨badId, rowIdx⟩ with
      | none => none
      | some row =>
          let vs := row.verts
          let i := vs.findIdx (· == a)
          let j := vs.findIdx (· == b)
          let lo := min i j
          let hi := max i j
          let adds := (vs.drop lo).take (hi - lo + 1)
          if decide (vs.length = 5) && decide (a ∈ vs) && decide (b ∈ vs) &&
             decide (a ∈ U) && decide (b ∈ U) &&
             adds.all (fun w => decide (w < G.n))
          then some adds else none
  | .c2RowFamily badId o terminal fe fam =>
      let adds := famPrefixVerts bads o fam
      if (match bads[badId]? with
          | some bE => decide (terminal = bE.u) || decide (terminal = bE.v)
          | none => false) &&
         blueb G c fe.1 fe.2 &&
         decide (fam = familyOf bads badId o terminal fe) &&
         fam.any (activatedB bads o U) &&
         adds.all (fun w => decide (w < G.n))
      then some adds else none
  | .c3BlueDetour badId rowIdx edgePos path =>
      match getRow bads ⟨badId, rowIdx⟩ with
      | none => none
      | some row =>
          let vs := row.verts
          let u := vs.getD edgePos 0
          let v := vs.getD (edgePos + 1) 0
          if decide (edgePos < 4) && decide (vs.length = 5) &&
             blueb G c u v && decide (u ∈ U) && decide (v ∈ U) &&
             decide (path ≠ []) && decide path.Nodup &&
             path.all (fun w => decide (w < G.n)) &&
             ((decide (path.head? = some u) && decide (path.getLast? = some v)) ||
              (decide (path.head? = some v) && decide (path.getLast? = some u))) &&
             (path.zip path.tail).all (fun e =>
               blueb G c e.1 e.2 && decide (normEdge e.1 e.2 ≠ normEdge u v))
          then some path else none
  | .c4TerminalShadow shadow trigger fe cell witnessRows =>
      if shadow.all (fun w => decide (w ∈ cell)) &&
         cell.all (fun w => decide (w < G.n)) &&
         blueb G c fe.1 fe.2 &&
         (decide (fe.1 ∈ shadow) != decide (fe.2 ∈ shadow)) &&
         trigger.all (fun w => decide (w ∈ U)) &&
         decide ((⟨shadow, trigger, fe, cell, witnessRows⟩ : ShadowItem)
           ∈ basis.shadowBasis) &&
         witnessRows.all (checkWitnessRow bads shadow fe)
      then some cell else none

/-- Single-step replay: verify preconditions, return the absorbed state. -/
def replayClosureStep (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (basis : BankClosureBasis) (U : List Nat) (st : BankClosureStep) :
    Option (List Nat) :=
  (stepAdds G c bads basis U st).map (absorbV U)

/-- Trace replay by explicit recursion over the step list. -/
def replayTraceAux (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (basis : BankClosureBasis) : List Nat → List BankClosureStep →
    Option (List Nat)
  | U, [] => some U
  | U, st :: rest =>
      match replayClosureStep G c bads basis U st with
      | none => none
      | some U₁ => replayTraceAux G c bads basis U₁ rest

def replayTrace (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (basis : BankClosureBasis) (tr : BankClosureTrace) : Option (List Nat) :=
  replayTraceAux G c bads basis tr.start tr.steps

/-- Relative closedness of a vertex set against the provided basis (graph and
    cut kept in the signature for interface stability; membership-only checks). -/
def checkClosed (_G : GraphData) (_c : CutData) (bads : List BadEdgeData)
    (basis : BankClosureBasis) (U : List Nat) : Bool :=
  basis.rowIntervalBasis.all (fun r =>
    match getRow bads r with
    | none => false
    | some row =>
        let vs := row.verts
        (List.range 5).all (fun i => (List.range 5).all (fun j =>
          !(decide (i < j) && decide (vs.getD i 0 ∈ U) &&
            decide (vs.getD j 0 ∈ U)) ||
          ((vs.drop i).take (j - i + 1)).all (fun w => decide (w ∈ U))))) &&
  basis.rowFamilyBasis.all (fun f =>
    !(f.fam.any (activatedB bads f.orient U)) ||
    (famPrefixVerts bads f.orient f.fam).all (fun w => decide (w ∈ U))) &&
  basis.detourBasis.all (fun d =>
    match getRow bads d.ref with
    | none => false
    | some row =>
        let u := row.verts.getD d.edgePos 0
        let v := row.verts.getD (d.edgePos + 1) 0
        !(decide (u ∈ U) && decide (v ∈ U)) ||
        d.path.all (fun w => decide (w ∈ U))) &&
  basis.shadowBasis.all (fun s =>
    !(s.trigger.all (fun w => decide (w ∈ U))) ||
    s.cell.all (fun w => decide (w ∈ U)))

/-- Pressure-claim check on a final set. -/
def checkPressureClaim (G : GraphData) (atoms : List AtomData) (D : Nat)
    (U : List Nat) : PressureClaim → Bool
  | .none => true
  | .positive => decide (0 < pressureNum G atoms D U)
  | .nonpos => decide (pressureNum G atoms D U ≤ 0)
  | .negativeNu0 => decide (nu0Num G atoms D U < 0)

/-- Full trace checker (graph/cut checks assumed global per contract). -/
def checkBankClosureTrace (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat)
    (basis : BankClosureBasis) (tr : BankClosureTrace) : Bool :=
  decide tr.start.Nodup && tr.start.all (fun v => decide (v < G.n)) &&
  decide tr.final.Nodup && tr.final.all (fun v => decide (v < G.n)) &&
  decide (replayTrace G c bads basis tr = some tr.final) &&
  checkClosed G c bads basis tr.final &&
  checkPressureClaim G atoms D tr.final tr.pressureClaim

/-- Every successful step is monotone. -/
theorem replayStep_subset (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (basis : BankClosureBasis) (U U' : List Nat)
    (st : BankClosureStep)
    (h : replayClosureStep G c bads basis U st = some U') :
    ∀ v ∈ U, v ∈ U' := by
  intro v hv
  unfold replayClosureStep at h
  rcases ho : stepAdds G c bads basis U st with _ | adds
  · rw [ho] at h
    simp at h
  · rw [ho] at h
    simp at h
    subst h
    exact mem_absorbV_left _ _ _ hv

/-- Trace replay is monotone. -/
theorem replayTraceAux_subset (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (basis : BankClosureBasis) :
    ∀ (steps : List BankClosureStep) (U V : List Nat),
    replayTraceAux G c bads basis U steps = some V →
    ∀ v ∈ U, v ∈ V
  | [], U, V, h => by
      simp only [replayTraceAux, Option.some.injEq] at h
      subst h
      exact fun v hv => hv
  | st :: rest, U, V, h => by
      simp only [replayTraceAux] at h
      rcases hstep : replayClosureStep G c bads basis U st with _ | U₁
      · rw [hstep] at h
        simp at h
      · rw [hstep] at h
        simp at h
        intro v hv
        exact replayTraceAux_subset G c bads basis rest U₁ V h v
          (replayStep_subset G c bads basis U U₁ st hstep v hv)

/-- Pressure fact extraction. -/
theorem checkPressureClaim_positive (G : GraphData) (atoms : List AtomData)
    (D : Nat) (U : List Nat)
    (h : checkPressureClaim G atoms D U .positive = true) :
    0 < pressureNum G atoms D U := by
  simpa [checkPressureClaim] using h

theorem checkPressureClaim_nonpos (G : GraphData) (atoms : List AtomData)
    (D : Nat) (U : List Nat)
    (h : checkPressureClaim G atoms D U .nonpos = true) :
    pressureNum G atoms D U ≤ 0 := by
  simpa [checkPressureClaim] using h

theorem checkPressureClaim_negativeNu0 (G : GraphData) (atoms : List AtomData)
    (D : Nat) (U : List Nat)
    (h : checkPressureClaim G atoms D U .negativeNu0 = true) :
    nu0Num G atoms D U < 0 := by
  simpa [checkPressureClaim] using h

/-- MAIN TRACE SOUNDNESS (consumer-facing): a passing trace yields containment,
    relative closedness of the final set, and the pressure claim. -/
theorem bankClosureTrace_sound (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat)
    (basis : BankClosureBasis) (tr : BankClosureTrace)
    (h : checkBankClosureTrace G c bads atoms D basis tr = true) :
    (∀ v ∈ tr.start, v ∈ tr.final) ∧
    checkClosed G c bads basis tr.final = true ∧
    checkPressureClaim G atoms D tr.final tr.pressureClaim = true := by
  unfold checkBankClosureTrace at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact ⟨replayTraceAux_subset G c bads basis tr.steps tr.start tr.final
    (by simpa [replayTrace] using h.1.1.2), h.1.2, h.2⟩

/-! ### B10: blue-pendant peel — graph-side structural checker (audited contract).
This layer verifies the literal peel data P0-P6: set hygiene, induced small
graph and restricted cut recomputed and compared, pendant boundary (every
removed-to-kept edge lands on the root), blue-only appendage (hence bad-count
equality, recomputed on both sides), parity records, blue-connected appendage
(bounded reachability), and row invisibility. The Assembly-level PeelCert
wraps this with smallRows/smallCert and the preservation Props (P-MaxCut,
P-GammaMinimal, ...), per the archived Bank0 assembly contract and audit
item 5 (small-graph checkGraph/checkCut carried there). -/

/-- Graph-side peel data. -/
structure PeelData where
  removed : List Nat
  root : Nat
  keepMap : List Nat
  smallG : GraphData
  smallCut : CutData
  parity : List Bool
deriving Repr

/-- Induced edge list on the kept vertices (small indices, normalized i < j). -/
def inducedEdges (G : GraphData) (keepMap : List Nat) : List (Nat × Nat) :=
  (List.range keepMap.length).flatMap (fun i =>
    (List.range keepMap.length).filterMap (fun j =>
      if i < j && adjb G (keepMap.getD i 0) (keepMap.getD j 0)
      then some (i, j) else none))

/-- One blue-reachability expansion step inside a domain. -/
def blueReachStep (G : GraphData) (c : CutData) (dom S : List Nat) :
    List Nat :=
  (S ++ dom.filter (fun v => S.any (fun u => blueb G c u v))).dedup

/-- Fueled reachability iteration. -/
def iterReach (G : GraphData) (c : CutData) (dom : List Nat) :
    Nat → List Nat → List Nat
  | 0, S => S
  | n + 1, S => iterReach G c dom n (blueReachStep G c dom S)

/-- P0: set hygiene and keepMap correctness. -/
def checkPeelSets (G : GraphData) (p : PeelData) : Bool :=
  decide (p.removed ≠ []) && decide p.removed.Nodup &&
  p.removed.all (fun v => decide (v < G.n)) &&
  decide (p.root < G.n) && decide (p.root ∉ p.removed) &&
  decide (p.keepMap
    = (List.range G.n).filter (fun v => decide (v ∉ p.removed))) &&
  decide (p.smallG.n = p.keepMap.length)

/-- P1: induced small graph and restricted small cut, recomputed. -/
def checkPeelInduced (G : GraphData) (c : CutData) (p : PeelData) : Bool :=
  decide (p.smallG.edges = inducedEdges G p.keepMap) &&
  decide (p.smallCut.side.length = p.smallG.n) &&
  (List.range p.keepMap.length).all (fun i =>
    decide (sideb p.smallCut i = sideb c (p.keepMap.getD i 0)))

/-- P2: pendant boundary — every removed-to-kept edge lands on the root. -/
def checkPeelPendant (G : GraphData) (p : PeelData) : Bool :=
  G.edges.all (fun e =>
    !(decide (e.1 ∈ p.removed) != decide (e.2 ∈ p.removed)) ||
    (decide (e.1 ∈ p.removed) && decide (e.2 = p.root)) ||
    (decide (e.2 ∈ p.removed) && decide (e.1 = p.root)))

/-- P3: blue-only appendage — every edge touching removed is blue. -/
def checkPeelBlueApp (G : GraphData) (c : CutData) (p : PeelData) : Bool :=
  G.edges.all (fun e =>
    !(decide (e.1 ∈ p.removed) || decide (e.2 ∈ p.removed)) ||
    blueb G c e.1 e.2)

/-- Bad-count equality and strict size decrease, both recomputed. -/
def checkPeelCounts (G : GraphData) (c : CutData) (p : PeelData) : Bool :=
  decide (badCount G c = badCount p.smallG p.smallCut) &&
  decide (p.smallG.n < G.n)

/-- P5: parity records relative to the root. -/
def checkPeelParity (c : CutData) (p : PeelData) : Bool :=
  decide (p.parity.length = p.removed.length) &&
  (List.range p.removed.length).all (fun i =>
    decide (p.parity.getD i false
      = (sideb c (p.removed.getD i 0) != sideb c p.root)))

/-- P4: blue-connected appendage — every removed vertex is blue-reachable
    from the root inside removed ∪ {root}. -/
def checkPeelReach (G : GraphData) (c : CutData) (p : PeelData) : Bool :=
  p.removed.all (fun v =>
    decide (v ∈ iterReach G c (p.root :: p.removed)
      (p.removed.length + 1) [p.root]))

/-- P6: row invisibility — no database row uses a removed vertex. -/
def checkPeelRows (bads : List BadEdgeData) (p : PeelData) : Bool :=
  bads.all (fun b => b.rows.all (fun r =>
    r.verts.all (fun v => decide (v ∉ p.removed))))

/-- Full graph-side peel check (P0-P6). -/
def checkPeel (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (p : PeelData) : Bool :=
  checkPeelSets G p && checkPeelInduced G c p && checkPeelPendant G p &&
  checkPeelBlueApp G c p && checkPeelCounts G c p && checkPeelParity c p &&
  checkPeelReach G c p && checkPeelRows bads p

/-- Fact extraction: exact bad-count transfer (the bank-inequality carrier). -/
theorem checkPeel_badCount_eq (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    badCount G c = badCount p.smallG p.smallCut := by
  unfold checkPeel checkPeelCounts at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1.1.1.2.1

/-- Fact extraction: strict vertex-count decrease (the induction carrier). -/
theorem checkPeel_nlt (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    p.smallG.n < G.n := by
  unfold checkPeel checkPeelCounts at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1.1.1.2.2

/-- Bank-inequality transfer across a peel: the induction hypothesis at the
    smaller size lifts to the big graph (audit-canonical Nat form). -/
theorem peel_bank_transfer (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true)
    (hIH : 25 * badCount p.smallG p.smallCut ≤ p.smallG.n ^ 2) :
    25 * badCount G c ≤ G.n ^ 2 := by
  rw [checkPeel_badCount_eq G c bads p h]
  exact le_trans hIH (Nat.pow_le_pow_left
    (Nat.le_of_lt (checkPeel_nlt G c bads p h)) 2)

end CertGraph
end Erdos23Delta0
