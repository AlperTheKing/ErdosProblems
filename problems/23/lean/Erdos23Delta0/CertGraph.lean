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

/-- Graph-side peel data (rootSmallIdx: the small index of the root, per the
    SigmaChain provider contract). -/
structure PeelData where
  removed : List Nat
  root : Nat
  keepMap : List Nat
  rootSmallIdx : Nat
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
  decide (p.smallG.n = p.keepMap.length) &&
  decide (p.rootSmallIdx < p.keepMap.length) &&
  decide (p.keepMap.getD p.rootSmallIdx 0 = p.root)

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

/-! ### Bank0 cross certificate: the partition + CrossCap dichotomy bundle.
Combines the B2 corridor partition (which certifies a ν₀-negative corridor)
with the B3 CrossCap capacity certificate on that same corridor; a passing
bundle contradicts max-cut switch nonnegativity outright. This is the `cross`
constructor payload of the Bank0 assembly dispatch. -/

structure Bank0CrossCert where
  partition : CorridorPartitionCert
  crossCap : CrossCapCert
deriving Repr

/-- The bundle check: partition valid, the CrossCap corridor is exactly the
    partition's claimed negative corridor, and the capacity check passes. -/
def checkBank0Cross (G : GraphData) (c : CutData) (atoms : List AtomData)
    (D : Nat) (w : Bank0CrossCert) : Bool :=
  checkCorridorPartition G atoms D w.partition &&
  decide (w.partition.corridors[w.partition.negIdx]? = some w.crossCap.corridor) &&
  checkCrossCap G c atoms D w.crossCap

/-- BANK0 CROSS SOUNDNESS: a passing bundle refutes max-cut — under max-cut
    no such configuration exists (the assembly derives its inequality from
    False). -/
theorem bank0Cross_sound (G : GraphData) (c : CutData)
    (atoms : List AtomData) (D : Nat) (w : Bank0CrossCert)
    (h : checkBank0Cross G c atoms D w = true)
    (hmax : ∀ S : List Nat, 0 ≤ sigma G c S) : False := by
  unfold checkBank0Cross at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact partition_crossCap_sound G c atoms D w.partition w.crossCap
    h.1.1 h.1.2 h.2 hmax

/-! ### B5: global C5 labelling checker (the `globalC5` Bank0 payload).
A single bank block whose five classes partition ALL vertices, with every
bad edge (recomputed) in the V4-V0 layer and the five cyclic template bounds
badCount ≤ e(Vᵢ,Vᵢ₊₁) ≤ |Vᵢ|·|Vᵢ₊₁| verified numerically. The AM-GM finish
25·badCount ≤ N² is composed in the Assembly module via
Bank0Algebra.bank_amgm_rat from the facts extracted here. -/

/-- Global C5 check over a bank block whose classes cover the whole graph. -/
def checkGlobalC5 (G : GraphData) (c : CutData) (b : BankBlock) : Bool :=
  decide ((b.classes 0).length + (b.classes 1).length + (b.classes 2).length
    + (b.classes 3).length + (b.classes 4).length = G.n) &&
  (List.finRange 5).all (fun i =>
    (b.classes i).all (fun v => decide (v < G.n)) &&
    decide (b.classes i).Nodup) &&
  (List.finRange 5).all (fun i => (List.finRange 5).all (fun j =>
    decide (i = j) ||
    (b.classes i).all (fun v => decide (v ∉ b.classes j)))) &&
  (G.edges.filter (fun e => badb G c e.1 e.2)).all (fun e =>
    (decide (e.1 ∈ b.classes 4) && decide (e.2 ∈ b.classes 0)) ||
    (decide (e.1 ∈ b.classes 0) && decide (e.2 ∈ b.classes 4))) &&
  (List.finRange 5).all (fun i =>
    decide (badCount G c ≤ eBetween G (b.classes i) (b.classes (i + 1))) &&
    decide (badCount G c
      ≤ (b.classes i).length * (b.classes (i + 1)).length))

/-- Fact extraction: the five class sizes sum to the vertex count. -/
theorem checkGlobalC5_sizes (G : GraphData) (c : CutData) (b : BankBlock)
    (h : checkGlobalC5 G c b = true) :
    (b.classes 0).length + (b.classes 1).length + (b.classes 2).length
      + (b.classes 3).length + (b.classes 4).length = G.n := by
  unfold checkGlobalC5 at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  exact h.1.1.1.1

/-- Fact extraction: the five cyclic class-size products dominate badCount —
    exactly the hypotheses of Bank0Algebra.bank_amgm_rat. -/
theorem checkGlobalC5_products (G : GraphData) (c : CutData) (b : BankBlock)
    (h : checkGlobalC5 G c b = true) :
    ∀ i : Fin 5, badCount G c
      ≤ (b.classes i).length * (b.classes (i + 1)).length := by
  unfold checkGlobalC5 at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  intro i
  exact (h.2 i (List.mem_finRange i)).2

/-! ### GlobalC5 arithmetic finish (self-contained AM-GM spine, mirroring the
proven Bank0Algebra route so the payload closes inside this file). -/

private theorem sqrtHalfAdd (m a b : ℝ) (_hm : 0 ≤ m) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (h : m ≤ a * b) : Real.sqrt m ≤ (a + b) / 2 := by
  have hsq : m ≤ ((a + b) / 2) ^ 2 := by nlinarith [sq_nonneg (a - b)]
  have h1 : Real.sqrt m ≤ Real.sqrt (((a + b) / 2) ^ 2) := Real.sqrt_le_sqrt hsq
  have h2 : Real.sqrt (((a + b) / 2) ^ 2) = (a + b) / 2 := by
    rw [Real.sqrt_sq (by linarith)]
  linarith [h1, h2.le, h2.ge]

private theorem bankAmgmReal (m n0 n1 n2 n3 n4 : ℝ)
    (hm : 0 ≤ m) (h0 : 0 ≤ n0) (h1 : 0 ≤ n1) (h2 : 0 ≤ n2) (h3 : 0 ≤ n3)
    (h4 : 0 ≤ n4)
    (p0 : m ≤ n0 * n1) (p1 : m ≤ n1 * n2) (p2 : m ≤ n2 * n3)
    (p3 : m ≤ n3 * n4) (p4 : m ≤ n4 * n0) :
    25 * m ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
  have s0 := sqrtHalfAdd m n0 n1 hm h0 h1 p0
  have s1 := sqrtHalfAdd m n1 n2 hm h1 h2 p1
  have s2 := sqrtHalfAdd m n2 n3 hm h2 h3 p2
  have s3 := sqrtHalfAdd m n3 n4 hm h3 h4 p3
  have s4 := sqrtHalfAdd m n4 n0 hm h4 h0 p4
  have hsum : 5 * Real.sqrt m ≤ n0 + n1 + n2 + n3 + n4 := by linarith
  have hs : 0 ≤ Real.sqrt m := Real.sqrt_nonneg m
  have hsq : (5 * Real.sqrt m) ^ 2 ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
    have hns : 0 ≤ 5 * Real.sqrt m := by linarith
    nlinarith [hsum, hns]
  have hval : (5 * Real.sqrt m) ^ 2 = 25 * m := by
    have := Real.sq_sqrt hm
    nlinarith [this]
  linarith [hsq, hval.le, hval.ge]

/-- Nat-level cyclic bank AM-GM. -/
theorem bank_amgm_nat (m n0 n1 n2 n3 n4 : Nat)
    (p0 : m ≤ n0 * n1) (p1 : m ≤ n1 * n2) (p2 : m ≤ n2 * n3)
    (p3 : m ≤ n3 * n4) (p4 : m ≤ n4 * n0) :
    25 * m ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
  have hr := bankAmgmReal (m : ℝ) n0 n1 n2 n3 n4
    (by positivity) (by positivity) (by positivity) (by positivity)
    (by positivity) (by positivity)
    (by exact_mod_cast p0) (by exact_mod_cast p1) (by exact_mod_cast p2)
    (by exact_mod_cast p3) (by exact_mod_cast p4)
  exact_mod_cast hr

/-- GLOBAL-C5 BANK BOUND: a passing global labelling check yields the Bank0
    scalar inequality outright — the `globalC5` constructor is self-closing. -/
theorem globalC5_bound (G : GraphData) (c : CutData) (b : BankBlock)
    (h : checkGlobalC5 G c b = true) :
    25 * badCount G c ≤ G.n ^ 2 := by
  have hs := checkGlobalC5_sizes G c b h
  have hp := checkGlobalC5_products G c b h
  rw [← hs]
  exact bank_amgm_nat (badCount G c) _ _ _ _ _
    (hp 0) (hp 1) (hp 2) (hp 3) (hp 4)

/-! ### B6b: bank-block cover groundwork (checker + counting helpers).
The full 25·badCount ≤ n² composition over a block cover lands with the
assembly dispatch; here: the cover checker (per-block checks, exact bad-edge
list linkage, bad-id count partition, disjoint in-range supports) and the
pure counting lemmas the composition consumes. -/

/-- A duplicate-free list of naturals below n has length at most n. -/
theorem nodupLt_length_le (l : List Nat) (n : Nat) (hnd : l.Nodup)
    (hlt : ∀ x ∈ l, x < n) : l.length ≤ n := by
  have h1 : l.toFinset ⊆ Finset.range n := by
    intro x hx
    rw [List.mem_toFinset] at hx
    exact Finset.mem_range.mpr (hlt x hx)
  have h2 := Finset.card_le_card h1
  rw [Finset.card_range] at h2
  rwa [List.toFinset_card_of_nodup hnd] at h2

/-- Σ aᵢ² ≤ (Σ aᵢ)² over Nat lists. -/
theorem natSumSq_le_sqSum : ∀ l : List Nat,
    (l.map (· ^ 2)).sum ≤ l.sum ^ 2
  | [] => by simp
  | a :: l => by
      have ih := natSumSq_le_sqSum l
      simp only [List.map_cons, List.sum_cons]
      calc a ^ 2 + (List.map (· ^ 2) l).sum
          ≤ a ^ 2 + l.sum ^ 2 := Nat.add_le_add_left ih _
        _ ≤ (a + l.sum) ^ 2 := by
            have h : (a + l.sum) ^ 2 = a ^ 2 + l.sum ^ 2 + 2 * (a * l.sum) := by
              ring
            rw [h]
            exact Nat.le_add_right _ _

/-- Support length is the sum of the five class lengths. -/
theorem support_length (b : BankBlock) :
    b.support.length = (b.classes 0).length + (b.classes 1).length
      + (b.classes 2).length + (b.classes 3).length
      + (b.classes 4).length := by
  have h5 : List.finRange 5 = [0, 1, 2, 3, 4] := by decide
  unfold BankBlock.support
  rw [h5]
  simp only [List.flatMap_cons, List.flatMap_nil, List.length_append,
    List.length_nil]
  omega

/-- Bank-block cover certificate: the blocks whose banks jointly pay
    the whole bad mass. -/
structure BankBlockCoverCert where
  blocks : List BankBlock
deriving Repr

/-- Cover check: every block passes, the bad-edge data list is EXACTLY the
    recomputed bad edges of the cut, the block bad-id counts partition it,
    and the block supports are jointly duplicate-free and in range. -/
def checkBankBlockCover (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (w : BankBlockCoverCert) : Bool :=
  w.blocks.all (checkBankBlock G bads) &&
  decide (bads.map (fun bd => normEdge bd.u bd.v)
    = (G.edges.filter (fun e => badb G c e.1 e.2)).map
        (fun e => normEdge e.1 e.2)) &&
  decide ((w.blocks.flatMap (fun b => b.badIds)).length = bads.length) &&
  decide (w.blocks.flatMap BankBlock.support).Nodup &&
  (w.blocks.flatMap BankBlock.support).all (fun v => decide (v < G.n))

/-- Fact extraction: the bad-edge data list counts the cut's bad edges. -/
theorem checkBankBlockCover_badCount (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (w : BankBlockCoverCert)
    (h : checkBankBlockCover G c bads w = true) :
    badCount G c = bads.length := by
  unfold checkBankBlockCover at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  have hm := congrArg List.length h.1.1.1.2
  simp only [List.length_map] at hm
  unfold badCount
  omega

/-- Constant-multiple of a list sum. -/
theorem sum_map_mul_const (k : Nat) : ∀ l : List Nat,
    (l.map (fun x => k * x)).sum = k * l.sum
  | [] => by simp
  | a :: l => by
      simp only [List.map_cons, List.sum_cons, sum_map_mul_const k l]
      ring

/-- BANK-BLOCK COVER BOUND: a passing cover check yields the Bank0 scalar
    inequality — badCount splits over the blocks, each block pays via the
    cyclic AM-GM, and the disjoint supports square-sum below n². -/
theorem coverBound (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (w : BankBlockCoverCert)
    (h : checkBankBlockCover G c bads w = true) :
    25 * badCount G c ≤ G.n ^ 2 := by
  have hbc := checkBankBlockCover_badCount G c bads w h
  unfold checkBankBlockCover at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at h
  have hall := h.1.1.1.1
  have hlen := h.1.1.2
  have hnodup := h.1.2
  have hrange := h.2
  have hblock : ∀ b ∈ w.blocks,
      25 * b.badIds.length ≤ b.support.length ^ 2 := by
    intro b hb
    have hp := checkBankBlock_products G bads b (hall b hb)
    rw [support_length b]
    exact bank_amgm_nat _ _ _ _ _ _ (hp 0) (hp 1) (hp 2) (hp 3) (hp 4)
  have e1 : (w.blocks.flatMap (fun b => b.badIds)).length
      = (w.blocks.map (fun b => b.badIds.length)).sum := by
    rw [List.length_flatMap]
  have e2 : (w.blocks.flatMap BankBlock.support).length
      = (w.blocks.map (fun b => b.support.length)).sum := by
    rw [List.length_flatMap]
  have hmm : (w.blocks.map (fun b => 25 * b.badIds.length)).sum
      = 25 * (w.blocks.map (fun b => b.badIds.length)).sum := by
    have := sum_map_mul_const 25 (w.blocks.map (fun b => b.badIds.length))
    simpa [List.map_map, Function.comp] using this
  have step1 : (w.blocks.map (fun b => 25 * b.badIds.length)).sum
      ≤ (w.blocks.map (fun b => b.support.length ^ 2)).sum :=
    List.sum_le_sum hblock
  have step2 : (w.blocks.map (fun b => b.support.length ^ 2)).sum
      ≤ ((w.blocks.map (fun b => b.support.length)).sum) ^ 2 := by
    have := natSumSq_le_sqSum (w.blocks.map (fun b => b.support.length))
    simpa [List.map_map, Function.comp] using this
  have step3 : (w.blocks.map (fun b => b.support.length)).sum ≤ G.n := by
    rw [← e2]
    exact nodupLt_length_le _ _ hnodup (fun x hx => hrange x hx)
  calc 25 * badCount G c
      = 25 * (w.blocks.map (fun b => b.badIds.length)).sum := by
        rw [hbc, ← hlen, e1]
    _ = (w.blocks.map (fun b => 25 * b.badIds.length)).sum := hmm.symm
    _ ≤ (w.blocks.map (fun b => b.support.length ^ 2)).sum := step1
    _ ≤ ((w.blocks.map (fun b => b.support.length)).sum) ^ 2 := step2
    _ ≤ G.n ^ 2 := Nat.pow_le_pow_left step3 2

/-! ### NCHBank wrapper: scalar-bank-safe routing (audit canonical form).
Routes a non-C5-hom seed situation to one of the closed scalar-bank payloads;
never consumes ODL-only NCH-def. The peel route recurses at the Bank0Cert
level, not here; the future non-C5-hom seed-bank constructor is added when
its certificate family exists (accepting fewer certs is sound). -/

inductive NCHBankCert
  | toGlobalC5 (b : BankBlock)
  | toCover (w : BankBlockCoverCert)
  | toCross (w : Bank0CrossCert)
deriving Repr

def checkNCHBank (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (atoms : List AtomData) (D : Nat) : NCHBankCert → Bool
  | .toGlobalC5 b => checkGlobalC5 G c b
  | .toCover w => checkBankBlockCover G c bads w
  | .toCross w => checkBank0Cross G c atoms D w

/-- NCHBank soundness: every route yields the scalar bank inequality (the
    cross route via refutation of max-cut). -/
theorem nchBank_sound (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (atoms : List AtomData) (D : Nat) (cert : NCHBankCert)
    (h : checkNCHBank G c bads atoms D cert = true)
    (hmax : ∀ S : List Nat, 0 ≤ sigma G c S) :
    25 * badCount G c ≤ G.n ^ 2 := by
  cases cert with
  | toGlobalC5 b => exact globalC5_bound G c b h
  | toCover w => exact coverBound G c bads w h
  | toCross w => exact (bank0Cross_sound G c atoms D w h hmax).elim

/-! ### BANK0 DISPATCH: the certificate inductive and its soundness.
The five routes compose the closed payloads; the max-cut switch hypothesis is
threaded through peel chains as an explicit Prop (`SigmaChain`) which the
assembly provider discharges from IsMaxCut plus the P-MaxCut preservation
lemma — nothing here is assumed silently. -/

/-- σ-nonnegativity of all switches (what IsMaxCut supplies at the top). -/
def sigmaNonneg (G : GraphData) (c : CutData) : Prop :=
  ∀ S : List Nat, 0 ≤ sigma G c S

/-- The Bank0 certificate: four terminal routes plus the peel recursion
    (carrying the smaller instance's row/atom data). -/
inductive Bank0Cert
  | globalC5 (b : BankBlock)
  | bankBlocks (w : BankBlockCoverCert)
  | cross (w : Bank0CrossCert)
  | nch (n : NCHBankCert)
  | peel (p : PeelData) (smallBads : List BadEdgeData)
      (smallAtoms : List AtomData) (rest : Bank0Cert)

/-- Dispatch checker (structurally recursive on the certificate). -/
def checkBank0Cert (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (atoms : List AtomData) (D : Nat) : Bank0Cert → Bool
  | .globalC5 b => checkGlobalC5 G c b
  | .bankBlocks w => checkBankBlockCover G c bads w
  | .cross w => checkBank0Cross G c atoms D w
  | .nch n => checkNCHBank G c bads atoms D n
  | .peel p smallBads smallAtoms rest =>
      checkPeel G c bads p &&
      checkBank0Cert p.smallG p.smallCut smallBads smallAtoms D rest

/-- The switch hypothesis at every level of the peel chain. -/
def SigmaChain (G : GraphData) (c : CutData) : Bank0Cert → Prop
  | .peel p _ _ rest => sigmaNonneg G c ∧ SigmaChain p.smallG p.smallCut rest
  | _ => sigmaNonneg G c

/-- BANK0 SOUNDNESS: every certified route yields 25·badCount ≤ n². -/
theorem bank0Cert_sound :
    ∀ (cert : Bank0Cert) (G : GraphData) (c : CutData)
      (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat),
    checkBank0Cert G c bads atoms D cert = true →
    SigmaChain G c cert →
    25 * badCount G c ≤ G.n ^ 2
  | .globalC5 b, G, c, _, _, _, h, _ => globalC5_bound G c b h
  | .bankBlocks w, G, c, bads, _, _, h, _ => coverBound G c bads w h
  | .cross w, G, c, _, atoms, D, h, hs =>
      (bank0Cross_sound G c atoms D w h hs).elim
  | .nch n, G, c, bads, atoms, D, h, hs =>
      nchBank_sound G c bads atoms D n h hs
  | .peel p sB sA rest, G, c, bads, _, D, h, hs => by
      simp only [checkBank0Cert, Bool.and_eq_true] at h
      have hIH := bank0Cert_sound rest p.smallG p.smallCut sB sA D h.2 hs.2
      exact peel_bank_transfer G c bads p h.1 hIH

/-! ### SigmaChain provider, stage A: σ-nonnegativity ↔ badCount-minimality
(archived P-MaxCut preservation contract §4; peel-independent half). -/

/-- Bad counts agree for cuts with identical sides on all vertices. -/
theorem badCount_congr (G : GraphData) (c1 c2 : CutData)
    (hG : checkGraph G = true)
    (hs : ∀ v < G.n, sideb c1 v = sideb c2 v) :
    badCount G c1 = badCount G c2 := by
  unfold badCount
  congr 1
  apply List.filter_congr
  intro e he
  have hedge : checkEdge G e = true := by
    unfold checkGraph at hG
    simp only [Bool.and_eq_true, List.all_eq_true] at hG
    exact hG.1 e he
  unfold checkEdge at hedge
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hedge
  have h1 : e.1 < G.n := lt_trans hedge.1 hedge.2
  have h2 : e.2 < G.n := hedge.2
  unfold badb
  rw [hs e.1 h1, hs e.2 h2]

/-- Bad-count minimality over all valid cuts (what IsMaxCut means here). -/
def BadCountMinimal (G : GraphData) (c : CutData) : Prop :=
  ∀ d : CutData, checkCut G d = true → badCount G c ≤ badCount G d

/-- Vertices whose side differs between two cuts. -/
def symmDiffSupport (G : GraphData) (c d : CutData) : List Nat :=
  (List.range G.n).filter (fun v => sideb c v != sideb d v)

theorem flipCut_side_length (c : CutData) (S : List Nat) :
    (flipCut c S).side.length = c.side.length := by
  simp [flipCut]

/-- Flipping the symmetric difference lands exactly on the other cut. -/
theorem flip_symmDiff_sides (G : GraphData) (c d : CutData)
    (hc : checkCut G c = true) (_hd : checkCut G d = true) :
    ∀ v < G.n, sideb (flipCut c (symmDiffSupport G c d)) v = sideb d v := by
  intro v hv
  unfold checkCut at hc
  simp only [decide_eq_true_eq] at hc
  have hvlen : v < c.side.length := by omega
  rw [sideb_flip c _ v hvlen]
  by_cases hmem : v ∈ symmDiffSupport G c d
  · have hne : sideb c v != sideb d v := by
      unfold symmDiffSupport at hmem
      simp only [List.mem_filter, List.mem_range] at hmem
      exact hmem.2
    rw [if_pos hmem]
    revert hne
    cases sideb c v <;> cases sideb d v <;> simp
  · rw [if_neg hmem]
    have heq : ¬(sideb c v != sideb d v) := by
      intro hne
      exact hmem (by
        unfold symmDiffSupport
        simp only [List.mem_filter, List.mem_range]
        exact ⟨hv, hne⟩)
    revert heq
    cases sideb c v <;> cases sideb d v <;> simp

theorem badCount_flip_symmDiff (G : GraphData) (c d : CutData)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hd : checkCut G d = true) :
    badCount G (flipCut c (symmDiffSupport G c d)) = badCount G d :=
  badCount_congr G _ d hG (flip_symmDiff_sides G c d hc hd)

/-- σ-nonnegativity gives global bad-count minimality (any valid cut is the
    flip of c at their symmetric difference). -/
theorem badCount_min_of_sigmaNonneg (G : GraphData) (c : CutData)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hSig : sigmaNonneg G c) : BadCountMinimal G c := by
  intro d hd
  have hlen : c.side.length = G.n := by
    unfold checkCut at hc
    simpa using hc
  have hflip := badCount_flip_eq G c (symmDiffSupport G c d) hlen hG
  have hs := hSig (symmDiffSupport G c d)
  have heq := badCount_flip_symmDiff G c d hG hc hd
  unfold sigma at hs
  omega

/-- Bad-count minimality gives σ-nonnegativity (every flip is a valid cut). -/
theorem sigmaNonneg_of_badCount_min (G : GraphData) (c : CutData)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hMin : BadCountMinimal G c) : sigmaNonneg G c := by
  intro S
  have hlen : c.side.length = G.n := by
    unfold checkCut at hc
    simpa using hc
  have hvalid : checkCut G (flipCut c S) = true := by
    unfold checkCut at hc ⊢
    rw [flipCut_side_length]
    exact hc
  have hmin := hMin (flipCut c S) hvalid
  have hflip := badCount_flip_eq G c S hlen hG
  unfold sigma
  omega

theorem sigmaNonneg_iff_badCount_min (G : GraphData) (c : CutData)
    (hG : checkGraph G = true) (hc : checkCut G c = true) :
    sigmaNonneg G c ↔ BadCountMinimal G c :=
  ⟨badCount_min_of_sigmaNonneg G c hG hc,
   sigmaNonneg_of_badCount_min G c hG hc⟩

/-! ### SigmaChain provider, stage B1: the cut-extension construction
(archived contract §1; the badCount bijection and transfer follow). -/

/-- First index of a value in a list. -/
def idxOf? : List Nat → Nat → Option Nat
  | [], _ => none
  | a :: l, v => if a = v then some 0 else (idxOf? l v).map (· + 1)

theorem idxOf?_getD : ∀ (l : List Nat) (v i : Nat),
    idxOf? l v = some i → l.getD i 0 = v
  | [], _, _, h => by simp [idxOf?] at h
  | a :: l, v, i, h => by
      unfold idxOf? at h
      by_cases hav : a = v
      · rw [if_pos hav] at h
        simp only [Option.some.injEq] at h
        subst h
        simpa using hav
      · rw [if_neg hav] at h
        rcases hm : idxOf? l v with _ | j
        · rw [hm] at h
          simp at h
        · rw [hm] at h
          simp only [Option.map_some, Option.some.injEq] at h
          subst h
          simpa using idxOf?_getD l v j hm

theorem idxOf?_lt : ∀ (l : List Nat) (v i : Nat),
    idxOf? l v = some i → i < l.length
  | [], _, _, h => by simp [idxOf?] at h
  | a :: l, v, i, h => by
      unfold idxOf? at h
      by_cases hav : a = v
      · rw [if_pos hav] at h
        simp only [Option.some.injEq] at h
        subst h
        simp
      · rw [if_neg hav] at h
        rcases hm : idxOf? l v with _ | j
        · rw [hm] at h
          simp at h
        · rw [hm] at h
          simp only [Option.map_some, Option.some.injEq] at h
          subst h
          have := idxOf?_lt l v j hm
          simp
          omega

theorem idxOf?_isSome_of_mem : ∀ (l : List Nat) (v : Nat),
    v ∈ l → (idxOf? l v).isSome
  | [], _, h => by simp at h
  | a :: l, v, h => by
      unfold idxOf?
      by_cases hav : a = v
      · rw [if_pos hav]; rfl
      · rw [if_neg hav]
        rcases List.mem_cons.mp h with h' | h'
        · exact absurd h'.symm hav
        · have := idxOf?_isSome_of_mem l v h'
          rcases hm : idxOf? l v with _ | j
          · rw [hm] at this; simp at this
          · rfl

/-- Extended side assignment: kept vertices read the small cut through the
    keep map; removed vertices take the small root's current side XOR their
    parity record (contract §1.3; the none branch is unreachable under a
    passing peel check). -/
def extSide (p : PeelData) (d : CutData) (v : Nat) : Bool :=
  match idxOf? p.keepMap v with
  | some i => sideb d i
  | none =>
      match idxOf? p.removed v with
      | some r => Bool.xor (sideb d p.rootSmallIdx) (p.parity.getD r false)
      | none => false

/-- The extended big cut. -/
def extendCut (G : GraphData) (p : PeelData) (d : CutData) : CutData :=
  ⟨(List.range G.n).map (fun v => extSide p d v)⟩

/-- Extension validity: the side list has length exactly n. -/
theorem checkCut_extendCut (G : GraphData) (p : PeelData) (d : CutData) :
    checkCut G (extendCut G p d) = true := by
  unfold checkCut extendCut
  simp

/-- Extended sides evaluate pointwise through extSide. -/
theorem sideb_extendCut (G : GraphData) (p : PeelData) (d : CutData)
    (v : Nat) (hv : v < G.n) :
    sideb (extendCut G p d) v = extSide p d v := by
  unfold sideb extendCut
  rw [List.getD_eq_getElem?_getD, List.getElem?_map]
  simp [List.getElem?_range hv]

/-! ### SigmaChain provider, stage B2: bad-count preservation under extension.
Kernel per the archived SigmaChain contract: appendage edges are never bad
under ANY extension (P2 pendant-through-root + P3 blue-only + P5 parity),
kept big edges are exactly the mapped small edges (induced correspondence),
and badness transports through the keep map. Two generic filter lemmas carry
the counting; the transfer chain then closes Bank0 self-containment. -/

/-- Edge range facts from graph well-formedness. -/
theorem checkGraph_edge_range (G : GraphData) (hG : checkGraph G = true) :
    ∀ e ∈ G.edges, e.1 < e.2 ∧ e.2 < G.n := by
  unfold checkGraph at hG
  simp only [Bool.and_eq_true, List.all_eq_true] at hG
  intro e he
  have hedge := hG.1 e he
  unfold checkEdge at hedge
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hedge
  exact hedge

/-- Edge-list nodup from graph well-formedness. -/
theorem checkGraph_edges_nodup (G : GraphData) (hG : checkGraph G = true) :
    G.edges.Nodup := by
  unfold checkGraph at hG
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hG
  exact hG.2

/-- Both endpoints kept. -/
def edgeKept (p : PeelData) (e : Nat × Nat) : Bool :=
  decide (e.1 ∈ p.keepMap) && decide (e.2 ∈ p.keepMap)

/-- Small-index edge pushed through the keep map. -/
def smallEdgeToBig (p : PeelData) (e : Nat × Nat) : Nat × Nat :=
  (p.keepMap.getD e.1 0, p.keepMap.getD e.2 0)

/-- Generic: if failing q forces failing p, pre-filtering by q is invisible. -/
theorem length_filter_eq_filter_filter_of_false {α : Type} (l : List α)
    (p q : α → Bool) (h : ∀ x ∈ l, q x = false → p x = false) :
    (l.filter p).length = ((l.filter q).filter p).length := by
  rw [List.filter_filter]
  have h' : ∀ a ∈ l, p a = (p a && q a) := by
    intro a ha
    cases hq : q a with
    | true => simp
    | false => simp [h a ha hq]
  rw [List.filter_congr h']

/-- Generic: filtered length transports along a map that permutes onto the
    target and intertwines the predicates. -/
theorem length_filter_eq_of_map_perm {α β : Type} (l : List α) (r : List β)
    (f : α → β) (p : α → Bool) (q : β → Bool)
    (hpred : ∀ x ∈ l, p x = q (f x)) (hperm : (l.map f).Perm r) :
    (l.filter p).length = (r.filter q).length := by
  have hmap : (l.filter p).map f = (l.map f).filter q := by
    rw [List.filter_map]
    exact congrArg (List.map f)
      (List.filter_congr (fun x hx => by simpa [Function.comp] using hpred x hx))
  calc (l.filter p).length
      = ((l.filter p).map f).length := by simp
    _ = ((l.map f).filter q).length := by rw [hmap]
    _ = (r.filter q).length := (hperm.filter q).length_eq

theorem idxOf?_eq_none_of_not_mem (l : List Nat) (v : Nat) (h : v ∉ l) :
    idxOf? l v = none := by
  rcases hm : idxOf? l v with _ | i
  · rfl
  · have hi := idxOf?_lt l v i hm
    have hg := idxOf?_getD l v i hm
    have hmem : l.getD i 0 ∈ l := by
      rw [List.getD_eq_getElem _ _ hi]
      exact List.getElem_mem hi
    rw [hg] at hmem
    exact absurd hmem h

theorem idxOf?_nodup_getD : ∀ (l : List Nat), l.Nodup → ∀ i, i < l.length →
    idxOf? l (l.getD i 0) = some i
  | [], _, i, hi => by simp at hi
  | a :: t, _, 0, _ => by simp [idxOf?]
  | a :: t, hnd, i + 1, hi => by
      have hti : i < t.length := by simpa using hi
      have hv : (a :: t).getD (i + 1) 0 = t.getD i 0 := by simp
      unfold idxOf?
      rw [hv]
      have hne : a ≠ t.getD i 0 := by
        intro heq
        have hmem : t.getD i 0 ∈ t := by
          rw [List.getD_eq_getElem _ _ hti]
          exact List.getElem_mem hti
        rw [← heq] at hmem
        exact (List.nodup_cons.mp hnd).1 hmem
      rw [if_neg hne,
        idxOf?_nodup_getD t (List.nodup_cons.mp hnd).2 i hti]
      rfl

/-- P0 facts: keep map literal, root data, small size. -/
theorem checkPeel_sets_facts (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    p.keepMap = (List.range G.n).filter (fun v => decide (v ∉ p.removed)) ∧
    p.root < G.n ∧ p.root ∉ p.removed ∧ p.smallG.n = p.keepMap.length ∧
    p.rootSmallIdx < p.keepMap.length ∧
    p.keepMap.getD p.rootSmallIdx 0 = p.root := by
  unfold checkPeel at h
  simp only [Bool.and_eq_true] at h
  have hS := h.1.1.1.1.1.1.1
  unfold checkPeelSets at hS
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hS
  exact ⟨hS.1.1.1.2, hS.1.1.1.1.1.2, hS.1.1.1.1.2, hS.1.1.2, hS.1.2, hS.2⟩

/-- P1 fact: the small edge list is the induced list. -/
theorem checkPeel_smallG_edges (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    p.smallG.edges = inducedEdges G p.keepMap := by
  unfold checkPeel at h
  simp only [Bool.and_eq_true] at h
  have hI := h.1.1.1.1.1.1.2
  unfold checkPeelInduced at hI
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hI
  exact hI.1.1

/-- P2 facts: a half-removed edge pins its kept endpoint to the root. -/
theorem checkPeel_pendant_fact (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    (∀ e ∈ G.edges, e.1 ∈ p.removed → e.2 ∉ p.removed → e.2 = p.root) ∧
    (∀ e ∈ G.edges, e.2 ∈ p.removed → e.1 ∉ p.removed → e.1 = p.root) := by
  unfold checkPeel at h
  simp only [Bool.and_eq_true] at h
  have hP := h.1.1.1.1.1.2
  unfold checkPeelPendant at hP
  rw [List.all_eq_true] at hP
  constructor
  · intro e he h1 h2
    have hx := hP e he
    simpa [h1, h2] using hx
  · intro e he h1 h2
    have hx := hP e he
    simpa [h1, h2] using hx

/-- P3 fact: every edge touching the removed set is blue under c. -/
theorem checkPeel_blueApp_fact (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    ∀ e ∈ G.edges, (e.1 ∈ p.removed ∨ e.2 ∈ p.removed) →
      sideb c e.1 ≠ sideb c e.2 := by
  unfold checkPeel at h
  simp only [Bool.and_eq_true] at h
  have hB := h.1.1.1.1.2
  unfold checkPeelBlueApp at hB
  rw [List.all_eq_true] at hB
  intro e he hor
  have hx := hB e he
  rcases hor with h1 | h1 <;>
    · simp only [h1, decide_true, Bool.true_or, Bool.or_true, Bool.not_true,
        Bool.false_or] at hx
      unfold blueb at hx
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hx
      exact hx.2

/-- P5 fact: parity records are the side flags relative to the root. -/
theorem checkPeel_parity_fact (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (h : checkPeel G c bads p = true) :
    ∀ r, r < p.removed.length →
      p.parity.getD r false
        = ((sideb c (p.removed.getD r 0)) != (sideb c p.root)) := by
  unfold checkPeel at h
  simp only [Bool.and_eq_true] at h
  have hP := h.1.1.2
  unfold checkPeelParity at hP
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    List.mem_range] at hP
  exact fun r hr => hP.2 r hr

/-- Keep-map membership characterization. -/
theorem keepMap_mem_iff (G : GraphData) (p : PeelData)
    (hkm : p.keepMap
      = (List.range G.n).filter (fun v => decide (v ∉ p.removed)))
    (v : Nat) : v ∈ p.keepMap ↔ v < G.n ∧ v ∉ p.removed := by
  rw [hkm]
  simp [List.mem_filter, List.mem_range]

theorem keepMap_nodup (G : GraphData) (p : PeelData)
    (hkm : p.keepMap
      = (List.range G.n).filter (fun v => decide (v ∉ p.removed))) :
    p.keepMap.Nodup := by
  rw [hkm]
  exact List.Nodup.filter _ (List.nodup_range)

theorem keepMap_pairwise_lt (G : GraphData) (p : PeelData)
    (hkm : p.keepMap
      = (List.range G.n).filter (fun v => decide (v ∉ p.removed))) :
    p.keepMap.Pairwise (· < ·) := by
  rw [hkm]
  exact List.Pairwise.filter _ (List.pairwise_lt_range)

/-- Strict monotonicity of keep-map entries. -/
theorem keepMap_getD_lt_getD (p : PeelData)
    (hpw : p.keepMap.Pairwise (· < ·)) (i j : Nat) (hij : i < j)
    (hj : j < p.keepMap.length) :
    p.keepMap.getD i 0 < p.keepMap.getD j 0 := by
  have hi : i < p.keepMap.length := lt_trans hij hj
  rw [List.getD_eq_getElem _ _ hi, List.getD_eq_getElem _ _ hj]
  exact List.pairwise_iff_getElem.mp hpw i j hi hj hij

/-- Kept vertices read the small cut at their unique keep index. -/
theorem extSide_kept (p : PeelData) (d : CutData)
    (hnd : p.keepMap.Nodup) (i : Nat) (hi : i < p.keepMap.length) :
    extSide p d (p.keepMap.getD i 0) = sideb d i := by
  unfold extSide
  rw [idxOf?_nodup_getD p.keepMap hnd i hi]

/-- Removed vertices take root-side xor parity at their index. -/
theorem extSide_removed (p : PeelData) (d : CutData) (v : Nat)
    (hnk : v ∉ p.keepMap) (r : Nat) (hr : idxOf? p.removed v = some r) :
    extSide p d v
      = Bool.xor (sideb d p.rootSmallIdx) (p.parity.getD r false) := by
  unfold extSide
  rw [idxOf?_eq_none_of_not_mem p.keepMap v hnk, hr]

/-- Membership characterization of the induced edge list. -/
theorem mem_inducedEdges (G : GraphData) (km : List Nat) (i j : Nat) :
    (i, j) ∈ inducedEdges G km ↔
      i < km.length ∧ j < km.length ∧ i < j ∧
        adjb G (km.getD i 0) (km.getD j 0) = true := by
  unfold inducedEdges
  simp only [List.mem_flatMap, List.mem_filterMap, List.mem_range,
    Option.ite_none_right_eq_some, Option.some.injEq, Prod.mk.injEq,
    Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨a, ha, b, hb, ⟨hab, hadj⟩, rfl, rfl⟩
    exact ⟨ha, hb, hab, hadj⟩
  · rintro ⟨hi, hj, hij, hadj⟩
    exact ⟨i, hi, j, hj, ⟨hij, hadj⟩, rfl, rfl⟩

/-- The induced edge list has no duplicates. -/
theorem inducedEdges_nodup (G : GraphData) (km : List Nat) :
    (inducedEdges G km).Nodup := by
  unfold inducedEdges
  rw [List.nodup_flatMap]
  constructor
  · intro i _
    refine List.Nodup.filterMap ?_ List.nodup_range
    intro a a' b hba hba'
    simp only [Option.mem_def, Option.ite_none_right_eq_some,
      Option.some.injEq] at hba hba'
    have h2 : (i, a) = (i, a') := hba.2.trans hba'.2.symm
    simpa using congrArg Prod.snd h2
  · refine List.Pairwise.imp ?_ List.pairwise_lt_range
    intro a b hab x hxa hxb
    simp only [List.mem_filterMap, List.mem_range,
      Option.ite_none_right_eq_some] at hxa hxb
    obtain ⟨ja, _, _, heqa⟩ := hxa
    obtain ⟨jb, _, _, heqb⟩ := hxb
    rw [← heqb] at heqa
    simp only [Option.some.injEq] at heqa
    have : a = b := by simpa using congrArg Prod.fst heqa
    omega

/-- Projection 1: an edge not fully kept is an appendage edge and is never
    bad under any extension (P2 + P3 + P5). -/
theorem peel_appendage_edge_not_bad_under_extend (G : GraphData)
    (c : CutData) (bads : List BadEdgeData) (p : PeelData) (d : CutData)
    (hG : checkGraph G = true) (hPeel : checkPeel G c bads p = true) :
    ∀ e ∈ G.edges, edgeKept p e = false →
      badb G (extendCut G p d) e.1 e.2 = false := by
  obtain ⟨hkm, hrootn, hrootnr, _, hidxlt, hgetDroot⟩ :=
    checkPeel_sets_facts G c bads p hPeel
  have hnd_km : p.keepMap.Nodup := keepMap_nodup G p hkm
  have hmemkm := keepMap_mem_iff G p hkm
  have hpend := checkPeel_pendant_fact G c bads p hPeel
  have hblue := checkPeel_blueApp_fact G c bads p hPeel
  have hpar := checkPeel_parity_fact G c bads p hPeel
  have hrange := checkGraph_edge_range G hG
  rintro ⟨u, v⟩ he hnk
  obtain ⟨huv, hvn⟩ := hrange (u, v) he
  have hun : u < G.n := lt_trans huv hvn
  have hrootside : extSide p d p.root = sideb d p.rootSmallIdx := by
    have h0 := idxOf?_nodup_getD p.keepMap hnd_km p.rootSmallIdx hidxlt
    rw [hgetDroot] at h0
    unfold extSide
    rw [h0]
  have hremside : ∀ w, w ∈ p.removed →
      extSide p d w = Bool.xor (sideb d p.rootSmallIdx)
        ((sideb c w) != (sideb c p.root)) := by
    intro w hw
    have hwnk : w ∉ p.keepMap := fun hmem => ((hmemkm w).mp hmem).2 hw
    rcases hio : idxOf? p.removed w with _ | r
    · have hsome := idxOf?_isSome_of_mem p.removed w hw
      rw [hio] at hsome
      simp at hsome
    · have hr := idxOf?_lt p.removed w r hio
      have hg := idxOf?_getD p.removed w r hio
      rw [extSide_removed p d w hwnk r hio, hpar r hr, hg]
  have hne : sideb (extendCut G p d) u ≠ sideb (extendCut G p d) v := by
    rw [sideb_extendCut G p d u hun, sideb_extendCut G p d v hvn]
    by_cases hu_r : u ∈ p.removed <;> by_cases hv_r : v ∈ p.removed
    · have hbc : sideb c u ≠ sideb c v := hblue (u, v) he (Or.inl hu_r)
      rw [hremside u hu_r, hremside v hv_r]
      revert hbc
      cases hcu : sideb c u <;> cases hcv : sideb c v <;>
        cases hcr : sideb c p.root <;>
        cases hs0 : sideb d p.rootSmallIdx <;> decide
    · have hveq : v = p.root := hpend.1 (u, v) he hu_r hv_r
      have hbc : sideb c u ≠ sideb c v := hblue (u, v) he (Or.inl hu_r)
      rw [hveq] at hbc
      rw [hremside u hu_r, hveq, hrootside]
      revert hbc
      cases hcu : sideb c u <;> cases hcr : sideb c p.root <;>
        cases hs0 : sideb d p.rootSmallIdx <;> decide
    · have hueq : u = p.root := hpend.2 (u, v) he hv_r hu_r
      have hbc : sideb c u ≠ sideb c v := hblue (u, v) he (Or.inr hv_r)
      rw [hueq] at hbc
      rw [hremside v hv_r, hueq, hrootside]
      revert hbc
      cases hcv : sideb c v <;> cases hcr : sideb c p.root <;>
        cases hs0 : sideb d p.rootSmallIdx <;> decide
    · have hkept : edgeKept p (u, v) = true := by
        unfold edgeKept
        simp only [Bool.and_eq_true, decide_eq_true_eq]
        exact ⟨(hmemkm u).mpr ⟨hun, hu_r⟩, (hmemkm v).mpr ⟨hvn, hv_r⟩⟩
      rw [hkept] at hnk
      simp at hnk
  unfold badb
  rw [decide_eq_false hne]
  simp

/-- Projection 2: mapped small edges permute onto the kept big edges. -/
theorem peel_small_edges_perm_kept_big_edges (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (hG : checkGraph G = true) (hPeel : checkPeel G c bads p = true) :
    (p.smallG.edges.map (smallEdgeToBig p)).Perm
      (G.edges.filter (edgeKept p)) := by
  obtain ⟨hkm, _, _, _, _, _⟩ := checkPeel_sets_facts G c bads p hPeel
  have hEdges := checkPeel_smallG_edges G c bads p hPeel
  have hnd_km : p.keepMap.Nodup := keepMap_nodup G p hkm
  have hpw := keepMap_pairwise_lt G p hkm
  have hmemkm := keepMap_mem_iff G p hkm
  have hrange := checkGraph_edge_range G hG
  rw [hEdges]
  refine List.perm_of_nodup_nodup_toFinset_eq ?_ ?_ ?_
  · refine List.Nodup.map_on ?_ (inducedEdges_nodup G p.keepMap)
    rintro ⟨x1, x2⟩ hx ⟨y1, y2⟩ hy hf
    rw [mem_inducedEdges] at hx hy
    obtain ⟨hx1, hx2, -, -⟩ := hx
    obtain ⟨hy1, hy2, -, -⟩ := hy
    have h1 : p.keepMap.getD x1 0 = p.keepMap.getD y1 0 :=
      congrArg Prod.fst hf
    have h2 : p.keepMap.getD x2 0 = p.keepMap.getD y2 0 :=
      congrArg Prod.snd hf
    rw [List.getD_eq_getElem _ _ hx1, List.getD_eq_getElem _ _ hy1] at h1
    rw [List.getD_eq_getElem _ _ hx2, List.getD_eq_getElem _ _ hy2] at h2
    have e1 : x1 = y1 := (hnd_km.getElem_inj_iff).mp h1
    have e2 : x2 = y2 := (hnd_km.getElem_inj_iff).mp h2
    rw [e1, e2]
  · exact List.Nodup.filter _ (checkGraph_edges_nodup G hG)
  · apply Finset.ext
    rintro ⟨u, v⟩
    simp only [List.mem_toFinset, List.mem_map, List.mem_filter]
    constructor
    · rintro ⟨⟨i, j⟩, hmem, heq⟩
      rw [mem_inducedEdges] at hmem
      obtain ⟨hi, hj, hij, hadj⟩ := hmem
      have hu : p.keepMap.getD i 0 = u := congrArg Prod.fst heq
      have hv : p.keepMap.getD j 0 = v := congrArg Prod.snd heq
      have hlt : p.keepMap.getD i 0 < p.keepMap.getD j 0 :=
        keepMap_getD_lt_getD p hpw i j hij hj
      have hedge : (u, v) ∈ G.edges := by
        unfold adjb at hadj
        simp only [Bool.and_eq_true, decide_eq_true_eq] at hadj
        have hm := hadj.2
        unfold normEdge at hm
        rw [if_pos hlt] at hm
        rw [hu, hv] at hm
        exact hm
      refine ⟨hedge, ?_⟩
      unfold edgeKept
      simp only [Bool.and_eq_true, decide_eq_true_eq]
      constructor
      · rw [← hu, List.getD_eq_getElem _ _ hi]
        exact List.getElem_mem hi
      · rw [← hv, List.getD_eq_getElem _ _ hj]
        exact List.getElem_mem hj
    · rintro ⟨hmem, hkept⟩
      unfold edgeKept at hkept
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hkept
      obtain ⟨hukm, hvkm⟩ := hkept
      obtain ⟨i, hi, hu⟩ := List.mem_iff_getElem.mp hukm
      obtain ⟨j, hj, hv⟩ := List.mem_iff_getElem.mp hvkm
      have huv : u < v := (hrange (u, v) hmem).1
      have hgu : p.keepMap.getD i 0 = u := by
        rw [List.getD_eq_getElem _ _ hi]; exact hu
      have hgv : p.keepMap.getD j 0 = v := by
        rw [List.getD_eq_getElem _ _ hj]; exact hv
      have hij : i < j := by
        rcases Nat.lt_trichotomy i j with h | h | h
        · exact h
        · subst h
          rw [hu] at hv
          omega
        · have hlt := List.pairwise_iff_getElem.mp hpw j i hj hi h
          rw [hu, hv] at hlt
          omega
      refine ⟨(i, j), ?_, ?_⟩
      · rw [mem_inducedEdges]
        refine ⟨hi, hj, hij, ?_⟩
        rw [hgu, hgv]
        unfold adjb normEdge
        rw [if_pos huv]
        simp [Nat.ne_of_lt huv, hmem]
      · unfold smallEdgeToBig
        rw [hgu, hgv]

/-- Projection 3: badness transports through the keep map on kept edges. -/
theorem peel_badb_small_compat_extend (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData) (d : CutData)
    (hPeel : checkPeel G c bads p = true) :
    ∀ e ∈ p.smallG.edges,
      badb p.smallG d e.1 e.2
        = badb G (extendCut G p d)
            (p.keepMap.getD e.1 0) (p.keepMap.getD e.2 0) := by
  obtain ⟨hkm, _, _, _, _, _⟩ := checkPeel_sets_facts G c bads p hPeel
  have hEdges := checkPeel_smallG_edges G c bads p hPeel
  have hnd_km : p.keepMap.Nodup := keepMap_nodup G p hkm
  have hmemkm := keepMap_mem_iff G p hkm
  rintro ⟨i, j⟩ he
  have he' := he
  rw [hEdges, mem_inducedEdges] at he'
  obtain ⟨hi, hj, hij, hadj⟩ := he'
  have hun : p.keepMap.getD i 0 < G.n := by
    have hmem : p.keepMap.getD i 0 ∈ p.keepMap := by
      rw [List.getD_eq_getElem _ _ hi]
      exact List.getElem_mem hi
    exact ((hmemkm _).mp hmem).1
  have hvn : p.keepMap.getD j 0 < G.n := by
    have hmem : p.keepMap.getD j 0 ∈ p.keepMap := by
      rw [List.getD_eq_getElem _ _ hj]
      exact List.getElem_mem hj
    exact ((hmemkm _).mp hmem).1
  have hsu : sideb (extendCut G p d) (p.keepMap.getD i 0) = sideb d i := by
    rw [sideb_extendCut G p d _ hun, extSide_kept p d hnd_km i hi]
  have hsv : sideb (extendCut G p d) (p.keepMap.getD j 0) = sideb d j := by
    rw [sideb_extendCut G p d _ hvn, extSide_kept p d hnd_km j hj]
  have hadjS : adjb p.smallG i j = true := by
    unfold adjb
    simp only [Bool.and_eq_true, decide_eq_true_eq]
    refine ⟨Nat.ne_of_lt hij, ?_⟩
    unfold normEdge
    rw [if_pos hij]
    exact he
  unfold badb
  rw [hsu, hsv, hadjS, hadj]

/-- B2 core: the three semantic facts give exact bad-count preservation. -/
theorem badCount_extendCut_eq_core (G : GraphData) (p : PeelData)
    (d : CutData)
    (h_notKept_notBad : ∀ e ∈ G.edges, edgeKept p e = false →
      badb G (extendCut G p d) e.1 e.2 = false)
    (h_edges_perm : (p.smallG.edges.map (smallEdgeToBig p)).Perm
      (G.edges.filter (edgeKept p)))
    (h_bad_compat : ∀ e ∈ p.smallG.edges,
      badb p.smallG d e.1 e.2
        = badb G (extendCut G p d)
            (p.keepMap.getD e.1 0) (p.keepMap.getD e.2 0)) :
    badCount G (extendCut G p d) = badCount p.smallG d := by
  unfold badCount
  have hbig := length_filter_eq_filter_filter_of_false G.edges
    (fun e => badb G (extendCut G p d) e.1 e.2) (edgeKept p)
    (fun e he hq => h_notKept_notBad e he hq)
  have hsmall := length_filter_eq_of_map_perm p.smallG.edges
    (G.edges.filter (edgeKept p)) (smallEdgeToBig p)
    (fun e => badb p.smallG d e.1 e.2)
    (fun e => badb G (extendCut G p d) e.1 e.2)
    (fun e he => h_bad_compat e he) h_edges_perm
  exact hbig.trans hsmall.symm

/-- STAGE B2 (SigmaChain provider): extending any small cut preserves the
    bad count exactly. -/
theorem badCount_extendCut_eq (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData) (d : CutData)
    (hG : checkGraph G = true) (hPeel : checkPeel G c bads p = true) :
    badCount G (extendCut G p d) = badCount p.smallG d :=
  badCount_extendCut_eq_core G p d
    (peel_appendage_edge_not_bad_under_extend G c bads p d hG hPeel)
    (peel_small_edges_perm_kept_big_edges G c bads p hG hPeel)
    (peel_badb_small_compat_extend G c bads p d hPeel)

/-- The induced small graph is well-formed. -/
theorem checkGraph_smallG_of_peel (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (hPeel : checkPeel G c bads p = true) :
    checkGraph p.smallG = true := by
  obtain ⟨_, _, _, hn, _, _⟩ := checkPeel_sets_facts G c bads p hPeel
  have hEdges := checkPeel_smallG_edges G c bads p hPeel
  unfold checkGraph
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  constructor
  · rintro ⟨i, j⟩ he
    rw [hEdges, mem_inducedEdges] at he
    obtain ⟨_, hj, hij, _⟩ := he
    unfold checkEdge
    simp only [Bool.and_eq_true, decide_eq_true_eq]
    exact ⟨hij, by rw [hn]; exact hj⟩
  · rw [hEdges]
    exact inducedEdges_nodup G p.keepMap

/-- The restricted small cut is well-formed. -/
theorem checkCut_smallCut_of_peel (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (hPeel : checkPeel G c bads p = true) :
    checkCut p.smallG p.smallCut = true := by
  unfold checkPeel at hPeel
  simp only [Bool.and_eq_true] at hPeel
  have hI := hPeel.1.1.1.1.1.1.2
  unfold checkPeelInduced at hI
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hI
  unfold checkCut
  simp only [decide_eq_true_eq]
  exact hI.1.2

/-- Minimality transfers to the peeled instance: any small competitor
    extends to a big competitor with the same bad count. -/
theorem small_badCount_min_of_peel (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (hG : checkGraph G = true) (hPeel : checkPeel G c bads p = true)
    (hMin : BadCountMinimal G c) :
    BadCountMinimal p.smallG p.smallCut := by
  intro d _
  have h1 := checkPeel_badCount_eq G c bads p hPeel
  have h2 := hMin (extendCut G p d) (checkCut_extendCut G p d)
  have h3 := badCount_extendCut_eq G c bads p d hG hPeel
  omega

/-- σ ≥ 0 descends through a peel. -/
theorem sigmaNonneg_small_of_peel (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (p : PeelData)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hPeel : checkPeel G c bads p = true)
    (hs : sigmaNonneg G c) : sigmaNonneg p.smallG p.smallCut := by
  have hmin := badCount_min_of_sigmaNonneg G c hG hc hs
  have hminS := small_badCount_min_of_peel G c bads p hG hPeel hmin
  exact sigmaNonneg_of_badCount_min p.smallG p.smallCut
    (checkGraph_smallG_of_peel G c bads p hPeel)
    (checkCut_smallCut_of_peel G c bads p hPeel) hminS

/-- SIGMACHAIN PROVIDER: top-level σ ≥ 0 supplies the whole chain. -/
theorem sigmaChain_of_sigmaNonneg :
    ∀ (cert : Bank0Cert) (G : GraphData) (c : CutData)
      (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat),
    checkGraph G = true → checkCut G c = true →
    checkBank0Cert G c bads atoms D cert = true →
    sigmaNonneg G c →
    SigmaChain G c cert
  | .globalC5 _, _, _, _, _, _, _, _, _, hs => hs
  | .bankBlocks _, _, _, _, _, _, _, _, _, hs => hs
  | .cross _, _, _, _, _, _, _, _, _, hs => hs
  | .nch _, _, _, _, _, _, _, _, _, hs => hs
  | .peel p sB sA rest, G, c, bads, _, D, hG, hc, h, hs => by
      simp only [checkBank0Cert, Bool.and_eq_true] at h
      exact ⟨hs, sigmaChain_of_sigmaNonneg rest p.smallG p.smallCut sB sA D
        (checkGraph_smallG_of_peel G c bads p h.1)
        (checkCut_smallCut_of_peel G c bads p h.1)
        h.2
        (sigmaNonneg_small_of_peel G c bads p hG hc h.1 hs)⟩

/-- BANK0 SELF-CONTAINED: checkers plus top-level σ ≥ 0 give the bank
    inequality — no per-level hypotheses remain. -/
theorem bank0_of_maxcut (cert : Bank0Cert) (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hchk : checkBank0Cert G c bads atoms D cert = true)
    (hs : sigmaNonneg G c) :
    25 * badCount G c ≤ G.n ^ 2 :=
  bank0Cert_sound cert G c bads atoms D hchk
    (sigmaChain_of_sigmaNonneg cert G c bads atoms D hG hc hchk hs)

/-! ### Assembly layer, stage 1: rational quantities and η-bridges (per the
archived 19-declaration contract; draft ASSEMBLY_LEAN_DRAFT_GPTPRO). The two
scalar theorems are copied verbatim from BranchAInterface.lean / BankL.lean
(single-file pattern; imports do not resolve across these standalone files). -/

/-- η = (N² − 25m)/25 as an exact rational. -/
def etaQ (G : GraphData) (c : CutData) : ℚ :=
  ((G.n : ℚ) ^ 2 - 25 * (badCount G c : ℚ)) / 25

/-- ρ_L = (L² − 25)/50. -/
def rhoQ (L : Nat) : ℚ :=
  ((L : ℚ) ^ 2 - 25) / 50

/-- τ = 5m/N (uniform width threshold). -/
def tauQ (G : GraphData) (c : CutData) : ℚ :=
  5 * (badCount G c : ℚ) / (G.n : ℚ)

/-- Bank0 discharge: a passing certificate under top-level σ ≥ 0 yields η ≥ 0. -/
theorem etaNonneg_of_bank0 (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (atoms : List AtomData) (D : Nat)
    (cert : Bank0Cert)
    (hG : checkGraph G = true) (hc : checkCut G c = true)
    (hchk : checkBank0Cert G c bads atoms D cert = true)
    (hs : sigmaNonneg G c) :
    0 ≤ etaQ G c := by
  have hb : 25 * badCount G c ≤ G.n ^ 2 :=
    bank0_of_maxcut cert G c bads atoms D hG hc hchk hs
  have hbq : (25 : ℚ) * (badCount G c : ℚ) ≤ (G.n : ℚ) ^ 2 := by
    exact_mod_cast hb
  unfold etaQ
  have hnum : 0 ≤ (G.n : ℚ) ^ 2 - 25 * (badCount G c : ℚ) := by
    nlinarith
  exact div_nonneg hnum (by norm_num)

/-- max(a, b) = b + max(a − b, 0) (copied from BranchAInterface). -/
theorem max_shift (a b : ℚ) : max a b = b + max (a - b) 0 := by
  rcases le_total a b with h | h
  · rw [max_eq_right h, max_eq_right (by linarith : a - b ≤ 0)]
    ring
  · rw [max_eq_left h, max_eq_left (by linarith : (0:ℚ) ≤ a - b)]
    ring

/-- net-DW′ assembly (copied from BranchAInterface): uniform width plus the
    C5-RS bound gives the GERSH row bound for the width-clamped row sum. -/
theorem netDW_assembly (N eta tau : ℚ) (s : Fin 5 → ℚ)
    (htau : 5*tau = N - 25*eta/N)
    (hrs : (∑ i, max (s i - tau) 0) ≤ (1 + 25/N)*eta) :
    (∑ i, max (s i) tau) ≤ N + eta := by
  have hsum : (∑ i, max (s i) tau) =
      5*tau + ∑ i, max (s i - tau) 0 := by
    have h1 : (∑ i, max (s i) tau) =
        ∑ i, (tau + max (s i - tau) 0) := by
      exact Finset.sum_congr rfl (fun i _ => max_shift (s i) tau)
    rw [h1, Finset.sum_add_distrib]
    simp [Finset.card_univ]
  rw [hsum, htau]
  have hexp : (1 + 25/N)*eta = eta + 25*eta/N := by
    rw [add_mul, one_mul, div_mul_eq_mul_div]
  linarith [hrs]

/-- ρ_L ≥ 0 for L > 5. -/
theorem rho_nonneg_of_len_gt5 {L : Nat} (hL : 5 < L) : 0 ≤ rhoQ L := by
  unfold rhoQ
  have hLq : (5 : ℚ) < (L : ℚ) := by exact_mod_cast hL
  have hnum : 0 ≤ (L : ℚ) ^ 2 - 25 := by nlinarith
  exact div_nonneg hnum (by norm_num)

/-- Bank-L reserve gives η ≥ 0 for L > 5. -/
theorem eta_nonneg_of_bankL {G : GraphData} {c : CutData} {L : Nat}
    (hL : 5 < L) (hBankL : 2 * rhoQ L ≤ etaQ G c) : 0 ≤ etaQ G c := by
  have hrho : 0 ≤ rhoQ L := rho_nonneg_of_len_gt5 hL
  nlinarith

/-- Bank-L ⟹ GERSH for L > 5 (copied from BankL, Decision C.4 form). -/
theorem gersh_Lgt5_of_bankL (R N eta L : ℚ) (hL : 5 < L)
    (hbankL : 2 * ((L^2 - 25)/50) ≤ eta)
    (hupo : R ≤ N + eta/2 - (L^2 - 25)/50) : R ≤ N + eta := by
  have hrho : 0 < (L^2 - 25)/50 := by nlinarith
  nlinarith

/-! ### Assembly layer, stage 2: provider-facing interfaces, row layer, the
Branch-A/Branch-B trichotomy, row aggregation, and the final GraphData /
SimpleGraph statements (per the 3-gap fill; data-carrying packages are
Type-valued — Prop structures cannot project data fields). BConnected and
GammaMinimalConnected are SCAFFOLDING stubs (True) until the exists_good_cut
provider module lands; nothing below eliminates them. -/

/-- Max cut as validity plus bad-count minimality. -/
structure IsMaxCut (G : GraphData) (c : CutData) : Prop where
  valid : checkCut G c = true
  min_bad : ∀ d : CutData, checkCut G d = true →
    badCount G c ≤ badCount G d

/-- Triangle-freeness of the literal graph. -/
def TriangleFree (G : GraphData) : Prop :=
  ∀ a b d : Nat, a < G.n → b < G.n → d < G.n →
    a ≠ b → b ≠ d → a ≠ d →
    ¬ (adjb G a b = true ∧ adjb G b d = true ∧ adjb G a d = true)

/-- Scaffolding stub (upgraded by the exists_good_cut provider module). -/
def BConnected (_G : GraphData) (_c : CutData) : Prop := True

/-- Scaffolding stub (upgraded by the exists_good_cut provider module). -/
def GammaMinimalConnected (_G : GraphData) (_c : CutData) : Prop := True

/-- Certificate-carried row record: loads and row sum are certificate data,
    tied together by the coherence field; semantics enter via RowDBFacts. -/
structure RowCert where
  badId : Nat
  verts : List Nat
  load5 : Fin 5 → ℚ
  rowSumQ : ℚ
  sum_load5_of_len5 :
    verts.length = 5 → rowSumQ = ∑ i : Fin 5, load5 i

namespace RowCert

def length (Q : RowCert) : Nat := Q.verts.length

end RowCert

/-- Row database. -/
structure RowDB where
  rowList : List RowCert

def RowInDB (rows : RowDB) (Q : RowCert) : Prop := Q ∈ rows.rowList

def rowLoadAt (_G : GraphData) (_c : CutData) (_rows : RowDB) (Q : RowCert)
    (i : Fin 5) : ℚ := Q.load5 i

def rowSum (_G : GraphData) (_c : CutData) (_rows : RowDB) (Q : RowCert) :
    ℚ := Q.rowSumQ

/-- General row-database facts (both branches). -/
structure RowDBFactsGeneral (G : GraphData) (c : CutData) (rows : RowDB) :
    Prop where
  length_ge_five : ∀ Q : RowCert, RowInDB rows Q → 5 ≤ Q.length

/-- All-length-5 refinement (Bank0 side). -/
structure RowDBFactsAll5 (G : GraphData) (c : CutData) (rows : RowDB) :
    Prop extends RowDBFactsGeneral G c rows where
  all_len5 : ∀ Q : RowCert, RowInDB rows Q → Q.length = 5

/-- GERSH row bound. -/
def RowGershBound (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Prop :=
  rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c

def rowSurplusAt (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (i : Fin 5) : ℚ :=
  rowLoadAt G c rows Q i - tauQ G c

def XMask (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (A : Finset (Fin 5)) : ℚ :=
  ∑ i ∈ A, rowSurplusAt G c rows Q i

def positiveMask (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Finset (Fin 5) :=
  Finset.univ.filter (fun i : Fin 5 => 0 < rowSurplusAt G c rows Q i)

/-- C5-RS: positive-part surplus bound. -/
def C5RS (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) :
    Prop :=
  (∑ i : Fin 5, max (rowSurplusAt G c rows Q i) 0) ≤
    (1 + (25 : ℚ) / (G.n : ℚ)) * etaQ G c

theorem sum_max_eq_XMask_positiveMask (G : GraphData) (c : CutData)
    (rows : RowDB) (Q : RowCert) :
    (∑ i : Fin 5, max (rowSurplusAt G c rows Q i) 0) =
      XMask G c rows Q (positiveMask G c rows Q) := by
  classical
  unfold XMask positiveMask
  symm
  rw [Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro i _
  by_cases hp : 0 < rowSurplusAt G c rows Q i
  · have hnonneg : 0 ≤ rowSurplusAt G c rows Q i := le_of_lt hp
    simp [hp, max_eq_left hnonneg]
  · have hle : rowSurplusAt G c rows Q i ≤ 0 := le_of_not_gt hp
    simp [hp, max_eq_right hle]

theorem XMask_univ_eq_rowSum_sub_5tau (G : GraphData) (c : CutData)
    (rows : RowDB) (Q : RowCert) (hLen : Q.length = 5) :
    XMask G c rows Q Finset.univ = rowSum G c rows Q - 5 * tauQ G c := by
  classical
  unfold XMask rowSurplusAt rowLoadAt rowSum
  have hsum := Q.sum_load5_of_len5 hLen
  rw [hsum, Finset.sum_sub_distrib]
  have hconst : (∑ _i : Fin 5, tauQ G c) = 5 * tauQ G c := by
    simp
  rw [hconst]

theorem eta_tau_identity (G : GraphData) (c : CutData) (hNpos : 0 < G.n) :
    (G.n : ℚ) + etaQ G c - 5 * tauQ G c =
      (1 + (25 : ℚ) / (G.n : ℚ)) * etaQ G c := by
  have hNne : (G.n : ℚ) ≠ 0 := by
    exact_mod_cast (ne_of_gt hNpos)
  unfold etaQ tauQ
  field_simp
  ring

/-- F1 ruling: the full-mask bound is derived from the ambient ODL bound. -/
theorem fullMaskBound_of_odlFull (G : GraphData) (c : CutData)
    (rows : RowDB) (Q : RowCert) (hLen : Q.length = 5) (hNpos : 0 < G.n)
    (hodl : rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c) :
    XMask G c rows Q Finset.univ ≤
      (1 + (25 : ℚ) / (G.n : ℚ)) * etaQ G c := by
  rw [XMask_univ_eq_rowSum_sub_5tau G c rows Q hLen]
  have hid := eta_tau_identity G c hNpos
  nlinarith

/-- Branch-A per-row inputs (providers fill these; fullMask derived). -/
structure BranchAInputs (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Prop where
  hLen : Q.length = 5
  hNpos : 0 < G.n
  etaNonneg : 0 ≤ etaQ G c
  a1Proper : ∀ A : Finset (Fin 5), A.Nonempty → A ≠ Finset.univ →
    XMask G c rows Q A ≤
      ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c
  odlFull : rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c

/-- C5-RS trichotomy: P = ∅ / P = univ / proper. -/
theorem c5RS_of_branchA_inputs {G : GraphData} {c : CutData} {rows : RowDB}
    {Q : RowCert} (h : BranchAInputs G c rows Q) :
    C5RS G c rows Q := by
  classical
  let P : Finset (Fin 5) := positiveMask G c rows Q
  have hsum : (∑ i : Fin 5, max (rowSurplusAt G c rows Q i) 0) =
      XMask G c rows Q P := by
    simpa [P] using sum_max_eq_XMask_positiveMask G c rows Q
  unfold C5RS
  rw [hsum]
  by_cases hPempty : P = ∅
  · rw [hPempty]
    simp only [XMask, Finset.sum_empty]
    have hcoef : 0 ≤ (1 : ℚ) + (25 : ℚ) / (G.n : ℚ) := by
      have hNq : (0 : ℚ) < (G.n : ℚ) := by exact_mod_cast h.hNpos
      positivity
    exact mul_nonneg hcoef h.etaNonneg
  · by_cases hPuniv : P = Finset.univ
    · rw [hPuniv]
      exact fullMaskBound_of_odlFull G c rows Q h.hLen h.hNpos h.odlFull
    · have hPnonempty : P.Nonempty :=
        Finset.nonempty_iff_ne_empty.mpr hPempty
      have ha1 := h.a1Proper P hPnonempty hPuniv
      have hcoef : ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) ≤
          ((25 : ℚ) / (G.n : ℚ) + 1) := by
        norm_num
      have hmul : ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c ≤
          ((25 : ℚ) / (G.n : ℚ) + 1) * etaQ G c :=
        mul_le_mul_of_nonneg_right hcoef h.etaNonneg
      calc XMask G c rows Q P
          ≤ ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c := ha1
        _ ≤ ((25 : ℚ) / (G.n : ℚ) + 1) * etaQ G c := hmul
        _ = (1 + (25 : ℚ) / (G.n : ℚ)) * etaQ G c := by ring

/-- Branch A GERSH: C5-RS plus positive-part domination close the row. -/
theorem gersh_L5_of_branchA_inputs {G : GraphData} {c : CutData}
    {rows : RowDB} {Q : RowCert} (h : BranchAInputs G c rows Q) :
    RowGershBound G c rows Q := by
  have hRS : C5RS G c rows Q := c5RS_of_branchA_inputs h
  have hsumLoads : rowSum G c rows Q =
      ∑ i : Fin 5, rowLoadAt G c rows Q i := by
    unfold rowSum rowLoadAt
    exact Q.sum_load5_of_len5 h.hLen
  have hposDom : ∑ i : Fin 5, (rowLoadAt G c rows Q i - tauQ G c) ≤
      ∑ i : Fin 5, max (rowLoadAt G c rows Q i - tauQ G c) 0 :=
    Finset.sum_le_sum (fun i _ => le_max_left _ _)
  have hleft : rowSum G c rows Q - 5 * tauQ G c ≤
      (1 + (25 : ℚ) / (G.n : ℚ)) * etaQ G c := by
    rw [hsumLoads]
    have hconst : (∑ _i : Fin 5, tauQ G c) = 5 * tauQ G c := by
      simp
    have hx : (∑ i : Fin 5, (rowLoadAt G c rows Q i - tauQ G c)) =
        (∑ i : Fin 5, rowLoadAt G c rows Q i) - 5 * tauQ G c := by
      rw [Finset.sum_sub_distrib, hconst]
    have hchain := le_trans hposDom hRS
    rw [hx] at hchain
    exact hchain
  have hid := eta_tau_identity G c h.hNpos
  unfold RowGershBound
  nlinarith

/-- Branch-B per-row inputs. -/
structure BranchBInputs (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Prop where
  hLen : 5 < Q.length
  bankL : 2 * rhoQ Q.length ≤ etaQ G c
  bankedUPO : rowSum G c rows Q ≤
    (G.n : ℚ) + etaQ G c / 2 - rhoQ Q.length

/-- Branch B GERSH (Bank-L reserve argument, direct). -/
theorem gersh_Lgt5_of_branchB_inputs {G : GraphData} {c : CutData}
    {rows : RowDB} {Q : RowCert} (h : BranchBInputs G c rows Q) :
    RowGershBound G c rows Q := by
  unfold RowGershBound
  have hrho : 0 ≤ rhoQ Q.length := rho_nonneg_of_len_gt5 h.hLen
  nlinarith [h.bankL, h.bankedUPO]

/-- Per-cut inputs across the whole row database. -/
structure Delta0Inputs (G : GraphData) (c : CutData) (rows : RowDB) :
    Prop where
  etaNonneg : 0 ≤ etaQ G c
  branchA : ∀ Q : RowCert, RowInDB rows Q → Q.length = 5 →
    BranchAInputs G c rows Q
  branchB : ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
    BranchBInputs G c rows Q

/-- Every database row satisfies GERSH. -/
theorem all_rows_gersh {G : GraphData} {c : CutData} {rows : RowDB}
    (hRows : RowDBFactsGeneral G c rows)
    (hDelta : Delta0Inputs G c rows) :
    ∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q := by
  intro Q hQ
  have hLenLower : 5 ≤ Q.length := hRows.length_ge_five Q hQ
  by_cases hEq : Q.length = 5
  · exact gersh_L5_of_branchA_inputs (hDelta.branchA Q hQ hEq)
  · have hGt : 5 < Q.length := by omega
    exact gersh_Lgt5_of_branchB_inputs (hDelta.branchB Q hQ hGt)

/-- Γ/β provider facts (Type-valued: carries the two rational values). -/
structure GammaBetaFacts (G : GraphData) (c : CutData) (rows : RowDB) where
  gammaVal : ℚ
  betaVal : ℚ
  gammaLower : 25 * (badCount G c : ℚ) ≤ gammaVal
  gammaUpper_of_all_rows_gersh :
    (∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q) →
      gammaVal ≤ (G.n : ℚ) ^ 2
  beta_eq_badCount : betaVal = (badCount G c : ℚ)

/-- Γ squeeze: 25m ≤ Γ ≤ N² gives β ≤ N²/25. -/
theorem beta_bound_of_gamma {G : GraphData} {c : CutData} {rows : RowDB}
    (facts : GammaBetaFacts G c rows)
    (hGamma : facts.gammaVal ≤ (G.n : ℚ) ^ 2) :
    facts.betaVal ≤ (G.n : ℚ) ^ 2 / 25 := by
  rw [facts.beta_eq_badCount]
  nlinarith [facts.gammaLower, hGamma]

/-- The selected good cut and its facts (Type-valued: carries GammaBetaFacts). -/
structure GoodCutData (G : GraphData) (c : CutData) (rows : RowDB) where
  maxCut : IsMaxCut G c
  gammaMin : GammaMinimalConnected G c
  bConnected : BConnected G c
  rowsFacts : RowDBFactsGeneral G c rows
  gammaBeta : GammaBetaFacts G c rows

/-- δ=0 on literal graph data, from a selected good cut. -/
theorem erdos23_delta0_graphData_from_good_cut {G : GraphData}
    {c : CutData} {rows : RowDB}
    (_hGraph : checkGraph G = true) (_hCut : checkCut G c = true)
    (_hTri : TriangleFree G) (hGood : GoodCutData G c rows)
    (hDelta : Delta0Inputs G c rows) :
    hGood.gammaBeta.betaVal ≤ (G.n : ℚ) ^ 2 / 25 := by
  have hAllRows : ∀ Q : RowCert, RowInDB rows Q →
      RowGershBound G c rows Q :=
    all_rows_gersh hGood.rowsFacts hDelta
  have hGammaUpper : hGood.gammaBeta.gammaVal ≤ (G.n : ℚ) ^ 2 :=
    hGood.gammaBeta.gammaUpper_of_all_rows_gersh hAllRows
  exact beta_bound_of_gamma hGood.gammaBeta hGammaUpper

/-- Certified Branch-A bundle (extension point for artifact-backed forms). -/
structure BranchACertBundle (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Prop where
  inputs : BranchAInputs G c rows Q

structure BranchBCertBundle (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) : Prop where
  inputs : BranchBInputs G c rows Q

structure Delta0CertBundles (G : GraphData) (c : CutData) (rows : RowDB) :
    Prop where
  etaNonneg : 0 ≤ etaQ G c
  branchA : ∀ Q : RowCert, RowInDB rows Q → Q.length = 5 →
    BranchACertBundle G c rows Q
  branchB : ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
    BranchBCertBundle G c rows Q

theorem delta0_inputs_of_cert_bundles {G : GraphData} {c : CutData}
    {rows : RowDB} (h : Delta0CertBundles G c rows) :
    Delta0Inputs G c rows where
  etaNonneg := h.etaNonneg
  branchA := fun Q hQ hLen => (h.branchA Q hQ hLen).inputs
  branchB := fun Q hQ hLen => (h.branchB Q hQ hLen).inputs

theorem erdos23_delta0_graphData_from_bundles {G : GraphData}
    {c : CutData} {rows : RowDB}
    (hGraph : checkGraph G = true) (hCut : checkCut G c = true)
    (hTri : TriangleFree G) (hGood : GoodCutData G c rows)
    (hBundles : Delta0CertBundles G c rows) :
    hGood.gammaBeta.betaVal ≤ (G.n : ℚ) ^ 2 / 25 :=
  erdos23_delta0_graphData_from_good_cut hGraph hCut hTri hGood
    (delta0_inputs_of_cert_bundles hBundles)

/-- Everything the existence provider must deliver for one graph. -/
structure GoodCutPackage (G : GraphData) where
  cut : CutData
  rows : RowDB
  hCut : checkCut G cut = true
  good : GoodCutData G cut rows
  delta : Delta0CertBundles G cut rows

theorem erdos23_delta0_graphData_from_package {G : GraphData}
    (hGraph : checkGraph G = true) (hTri : TriangleFree G)
    (pkg : GoodCutPackage G) :
    pkg.good.gammaBeta.betaVal ≤ (G.n : ℚ) ^ 2 / 25 :=
  erdos23_delta0_graphData_from_bundles hGraph pkg.hCut hTri pkg.good
    pkg.delta

/-- Bridge data from a Mathlib SimpleGraph to the literal layer. -/
structure SimpleGraphBridge {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] where
  G : GraphData
  hGraph : checkGraph G = true
  tri_transfer : Gs.CliqueFree 3 → TriangleFree G
  pkg : GoodCutPackage G
  betaSimpleVal : ℚ
  beta_transfer : betaSimpleVal = pkg.good.gammaBeta.betaVal
  n_transfer : (Fintype.card V : ℚ) = (G.n : ℚ)

/-- δ=0 through the bridge: β ≤ (card V)²/25. -/
theorem erdos23_delta0_simpleGraph {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hTri : Gs.CliqueFree 3) (bridge : SimpleGraphBridge Gs) :
    bridge.betaSimpleVal ≤ (Fintype.card V : ℚ) ^ 2 / 25 := by
  have hGD : bridge.pkg.good.gammaBeta.betaVal ≤
      (bridge.G.n : ℚ) ^ 2 / 25 :=
    erdos23_delta0_graphData_from_package bridge.hGraph
      (bridge.tri_transfer hTri) bridge.pkg
  rw [bridge.beta_transfer, bridge.n_transfer]
  exact hGD

end CertGraph
end Erdos23Delta0
