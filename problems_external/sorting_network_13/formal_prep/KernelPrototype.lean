import Mathlib

/-!
Compile-only preparation for a possible 44-comparator certificate.

This file deliberately contains no 44-comparator claim.  It proves the generic
finite-verifier bridge, smoke-tests it on two channels, and records Bert
Dobbelaere's published 45-comparator network only for certificate-shape and
length checks.  No `sorry` or `native_decide` is used.
-/

namespace SortingNetworkFormalPrep

set_option autoImplicit false

/-- A comparator joins two channels.  Endpoint order is canonicalized when
the comparator is applied, so the representation has no proof fields. -/
abbrev Comparator (n : ℕ) := Fin n × Fin n

/-- A comparator network is an ordered list of comparators. -/
abbrev Network (n : ℕ) := List (Comparator n)

/-- Apply a comparator to a binary input, placing the minimum on the lower
channel and the maximum on the higher channel. -/
def applyComparator {n : ℕ} (c : Comparator n) (input : Fin n → Bool) :
    Fin n → Bool :=
  fun k =>
    if k = min c.1 c.2 then min (input c.1) (input c.2)
    else if k = max c.1 c.2 then max (input c.1) (input c.2)
    else input k

/-- Apply all comparators from left to right. -/
def run {n : ℕ} (network : Network n) (input : Fin n → Bool) : Fin n → Bool :=
  network.foldl (fun state c => applyComparator c state) input

/-- A binary channel assignment is sorted when it is monotone in the channel
index. -/
def BinarySorted {n : ℕ} (input : Fin n → Bool) : Prop :=
  (List.ofFn input).Pairwise (· ≤ ·)

/-- Executable sortedness check used by the finite verifier. -/
def binarySortedCheck {n : ℕ} (input : Fin n → Bool) : Bool :=
  decide ((List.ofFn input).Pairwise (· ≤ ·))

/-- Add one leading channel to a binary input. -/
def prepend {n : ℕ} (head : Bool) (tail : Fin n → Bool) : Fin (n + 1) → Bool :=
  Fin.cases head tail

/-- A structurally executable list containing every binary input exactly once. -/
def allBinaryInputs : (n : ℕ) → List (Fin n → Bool)
  | 0 => [fun i => Fin.elim0 i]
  | n + 1 =>
      (allBinaryInputs n).map (prepend false) ++
        (allBinaryInputs n).map (prepend true)

/-- Every binary channel assignment occurs in `allBinaryInputs`. -/
theorem mem_allBinaryInputs {n : ℕ} (input : Fin n → Bool) :
    input ∈ allBinaryInputs n := by
  induction n with
  | zero =>
      simp only [allBinaryInputs, List.mem_singleton]
      funext i
      exact Fin.elim0 i
  | succ n ih =>
      let tail : Fin n → Bool := fun i => input i.succ
      have htail : tail ∈ allBinaryInputs n := ih tail
      have hreconstruct : prepend (input 0) tail = input := by
        funext i
        refine Fin.cases ?_ (fun j => ?_) i
        · rfl
        · rfl
      rw [← hreconstruct]
      cases h : input 0 with
      | false =>
          simp only [allBinaryInputs, List.mem_append, List.mem_map]
          exact Or.inl ⟨tail, htail, rfl⟩
      | true =>
          simp only [allBinaryInputs, List.mem_append, List.mem_map]
          exact Or.inr ⟨tail, htail, rfl⟩

/-- Executable enumeration of every binary input. -/
def verifyBinary {n : ℕ} (network : Network n) : Bool :=
  (allBinaryInputs n).all fun input => binarySortedCheck (run network input)

/-- The zero-one finite test for a comparator network. -/
def SortsBinary {n : ℕ} (network : Network n) : Prop :=
  ∀ input : Fin n → Bool, BinarySorted (run network input)

/-- The executable verifier is true exactly when the semantic binary sorting
property holds. -/
theorem verifyBinary_eq_true_iff {n : ℕ} (network : Network n) :
    verifyBinary network = true ↔ SortsBinary network := by
  simp [verifyBinary, binarySortedCheck, SortsBinary, BinarySorted, mem_allBinaryInputs]

/-- There is a binary sorting network on `n` channels with exactly `k`
comparators. -/
def HasSizeSorter (n k : ℕ) : Prop :=
  ∃ network : Network n, network.length = k ∧ SortsBinary network

/-- `k` is the minimum comparator count among binary sorting networks on `n`
channels. -/
def IsOptimalSize (n k : ℕ) : Prop :=
  HasSizeSorter n k ∧ ∀ network : Network n, SortsBinary network → k ≤ network.length

/-- The logical injection point: an upper-bound certificate and an independent
lower-bound theorem imply exact optimality. -/
theorem isOptimalSize_of_certificate_of_lowerBound {n k : ℕ}
    (upper : HasSizeSorter n k)
    (lower : ∀ network : Network n, SortsBinary network → k ≤ network.length) :
    IsOptimalSize n k :=
  ⟨upper, lower⟩

/-- Published 13-channel, 45-comparator fixture from SorterHunter commit
`392762f916688756242d90febced98ad157bc6d2`.  This is calibration data, not a
new result. -/
def dobbelaere45 : Network 13 :=
  [(0, 12), (1, 10), (2, 9), (3, 7), (5, 11), (6, 8),
   (1, 6), (2, 3), (4, 11), (7, 9), (8, 10), (0, 4),
   (1, 2), (3, 6), (7, 8), (9, 10), (11, 12), (4, 6),
   (5, 9), (8, 11), (10, 12), (0, 5), (3, 8), (4, 7),
   (6, 11), (9, 10), (0, 1), (2, 5), (6, 9), (7, 8),
   (10, 11), (1, 3), (2, 4), (5, 6), (9, 10), (1, 2),
   (3, 4), (5, 7), (6, 8), (2, 3), (4, 5), (6, 7),
   (8, 9), (3, 4), (5, 6)]

set_option maxHeartbeats 0 in
set_option maxRecDepth 1000000 in
/-- Kernel reduction confirms the published calibration fixture has length
45. -/
theorem dobbelaere45_length : dobbelaere45.length = 45 := by
  decide

/-- Minimal smoke-test certificate for the generic verifier. -/
def oneComparator : Network 2 := [(0, 1)]

/-- The generic executable-verifier bridge succeeds without trusted native
evaluation on its smallest nontrivial case. -/
theorem oneComparator_sorts_binary : SortsBinary oneComparator := by
  apply (verifyBinary_eq_true_iff oneComparator).mp
  decide

end SortingNetworkFormalPrep
