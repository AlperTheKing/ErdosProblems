import Erdos23Delta0.O14.EQODL1CoverInterface

/-!
# O14 EQ-ODL1 structural shape

This is the stable, non-generated descriptor layer for module 29.  Generated
chart-key files classify `O14Shape` values; semantic extraction modules later
provide `EQODL1ShapeSound` from route-tree / seed / mask data.
-/

namespace Erdos23Delta0
namespace O14

open CertGraph
open ODLFull

/-- Finite structural descriptor used by the generated 108-chart classifier. -/
structure O14Shape where
  kIdx : Nat
  dIdx : Nat
  seedShape : Nat
  maskCode : Nat
  orbitCode : Nat
  routeCode : Nat
  sigCode : Nat
deriving DecidableEq, Repr

/-- Bounds emitted from the v108 manifest/numeric-map layer. -/
structure O14Bounds where
  kMax : Nat
  dMax : Nat
  seedShapeMax : Nat
  maskCodeMax : Nat
  orbitCodeMax : Nat
  routeCodeMax : Nat
  sigCodeMax : Nat
deriving Repr

/-- The generated classifier only consumes shapes inside these emitted bounds. -/
def O14Shape.Valid (B : O14Bounds) (s : O14Shape) : Prop :=
  s.kIdx < B.kMax ∧
  s.dIdx < B.dMax ∧
  s.seedShape < B.seedShapeMax ∧
  s.maskCode < B.maskCodeMax ∧
  s.orbitCode < B.orbitCodeMax ∧
  s.routeCode < B.routeCodeMax ∧
  s.sigCode < B.sigCodeMax

/-- Boolean list membership helper for generated chart domains. -/
def inListNat (x : Nat) : List Nat → Bool
  | [] => false
  | y :: ys => (x == y) || inListNat x ys

theorem inListNat_sound {x : Nat} {xs : List Nat}
    (h : inListNat x xs = true) : x ∈ xs := by
  induction xs with
  | nil =>
      simp [inListNat] at h
  | cons y ys ih =>
      simp [inListNat] at h
      rcases h with hxy | htail
      · simp [hxy]
      · exact List.mem_cons_of_mem y (ih htail)

/-- Raw EQ-ODL1 row instance: the row is in the database and is an EQ length-5
row.  The generated structural classifier works on these rows after the route
tree supplies a concrete shape descriptor. -/
structure EQODL1RawInst (rows : RowDB) (Q : RowCert) : Prop where
  row_mem : RowInDB rows Q
  isEQ : Q.length = 5

/-- One classified EQ-ODL1 instance with its support-local ODL core. -/
structure EQODL1ShapeInst (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) where
  raw : EQODL1RawInst rows Q
  core : ODLCoreData G c rows Q
  shape : O14Shape

/-- Placeholder predicate for the O14 route-closure obligation.
This non-generated shape layer names the obligation; downstream semantic
modules refine/prove the real route-tree predicate. -/
def O14Closed {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (_I : EQODL1ShapeInst G c rows Q) : Prop := True

/-- Placeholder predicate for mask semantics. -/
def MaskSound {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (_I : EQODL1ShapeInst G c rows Q) : Prop := True

/-- Placeholder predicate for seed semantics. -/
def SeedSound {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (_I : EQODL1ShapeInst G c rows Q) : Prop := True

/-- Placeholder predicate for route semantics. -/
def RouteSound {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (_I : EQODL1ShapeInst G c rows Q) : Prop := True

/-- Placeholder predicate for scalar side-condition semantics. -/
def ScalarSound {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (_I : EQODL1ShapeInst G c rows Q) : Prop := True

/-- Semantic bridge obligations supplied outside the generated chart-key files.
The generator classifies; route-tree and mask/seed modules prove these facts
for real instances. -/
structure EQODL1ShapeSound {G : GraphData} {c : CutData} {rows : RowDB}
    {Q : RowCert} (I : EQODL1ShapeInst G c rows Q) : Prop where
  eq_len5 : Q.length = 5
  o14Closed : O14Closed I
  maskSound : MaskSound I
  seedSound : SeedSound I
  routeSound : RouteSound I
  scalarSound : ScalarSound I

end O14
end Erdos23Delta0
