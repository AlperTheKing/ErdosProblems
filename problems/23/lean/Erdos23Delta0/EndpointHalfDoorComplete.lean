import Erdos23Delta0.Ell5SingletonVertexSlack
import Erdos23Delta0.Ell5FullBankWallAdapter

/-!
# Endpoint-half all-Door fast path

This module packages the R7 fast path in which every off-support cut edge has
its own legal Door sink.  It deliberately makes no exact-one-fiber assumption.
-/

namespace Erdos23Delta0

open Finset MaxCutVertexIneq
open RelaxedCoverGraphBridge
open Ell5FullBankInterface Ell5SingletonVertexSlack

variable {V : Type} [DecidableEq V]

/-- The precise hypotheses needed by the endpoint-half all-Doors constructor.

The off-support edge set is definitionally `cutEdges G s \ F`.  Thus its graph
and cut facts need not be stored again: they follow from membership. -/
structure EndpointHalfDoorComplete
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V) (S F : Finset (Sym2 V))
    (inc : Sym2 V → Sym2 V → Prop) (kap : Sym2 V → ℚ) : Prop where
  rows : ∀ e ∈ S,
    e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2
  support : ∀ e ∈ F,
    e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2
  ownDoor_inc : ∀ e ∈ cutEdges G s \ F, inc e e
  ownDoor_capacity : ∀ e ∈ cutEdges G s \ F, (1 : ℚ) ≤ kap e

/-- Adapter-level output of the R7 fast path.

There is no current R7 `FullBankLPBundle` type carrying extractor labels or
global-package semantics.  This structure therefore records exactly the
available semantic content: the relaxed-cover certificate, its canonical
`Wall.Primal`, and exclusion of every checked strict dual for that wall. -/
structure EndpointHalfDoorFullBankBundle
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V) (S F : Finset (Sym2 V))
    (inc : Sym2 V → Sym2 V → Prop) (kap : Sym2 V → ℚ) where
  cert :
    FullBankRelaxedCoverCert S F (cutEdges G s \ F) (cutEdges G s \ F) C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap
  primal : Wall.Primal
    (Ell5FullBankWallAdapter.wallLP
      S F (cutEdges G s \ F) (cutEdges G s \ F) C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap)
  primal_canonical : primal =
    Ell5FullBankWallAdapter.primalOfCert
      S F (cutEdges G s \ F) (cutEdges G s \ F) C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap cert
  noStrictDual : ∀ d : Wall.Dual
      (Ell5FullBankWallAdapter.wallLP
        S F (cutEdges G s \ F) (cutEdges G s \ F) C
        (fun x => deltaM G s ({x} : Finset V))
        (fun x => deltaB G s ({x} : Finset V)) inc kap),
    d.Checked → ¬ d.StrictGap

/-- Build the endpoint-half Door certificate and expose its canonical wall
primal.  Each off-support edge routes only to its own Door sink. -/
noncomputable def fullBankBundle_of_endpointHalfDoorComplete
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V) (S F : Finset (Sym2 V))
    (inc : Sym2 V → Sym2 V → Prop) (kap : Sym2 V → ℚ)
    (h : EndpointHalfDoorComplete G s C S F inc kap) :
    EndpointHalfDoorFullBankBundle G s C S F inc kap := by
  let cert :
      FullBankRelaxedCoverCert S F (cutEdges G s \ F) (cutEdges G s \ F) C
        (fun x => deltaM G s ({x} : Finset V))
        (fun x => deltaB G s ({x} : Finset V)) inc kap :=
    certificate_of_singletonCore_allDoors G s C S F (cutEdges G s \ F) inc kap
      (by
        intro e he
        exact le_trans (by norm_num) (h.ownDoor_capacity e he))
      h.rows h.support
      (by
        intro e he
        have heCut : e ∈ cutEdges G s := (Finset.mem_sdiff.mp he).1
        simpa [cutEdges] using heCut)
      h.ownDoor_inc h.ownDoor_capacity
  exact
    { cert := cert
      primal := Ell5FullBankWallAdapter.primalOfCert
        S F (cutEdges G s \ F) (cutEdges G s \ F) C
        (fun x => deltaM G s ({x} : Finset V))
        (fun x => deltaB G s ({x} : Finset V)) inc kap cert
      primal_canonical := rfl
      noStrictDual := by
        intro d hd
        exact Ell5FullBankWallAdapter.noStrictDualOfCert
          S F (cutEdges G s \ F) (cutEdges G s \ F) C
          (fun x => deltaM G s ({x} : Finset V))
          (fun x => deltaB G s ({x} : Finset V)) inc kap cert d hd }

end Erdos23Delta0
