import Erdos23Delta0.Gamma.CommonBlueExtendedMatching
namespace Erdos23Delta0.Gamma.CommonBlueExtendedMatching
open CertGraph MinimumDemandRowSelection CanonicalCollisionHall

def UniversalCommonBlueHall (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads, HallCondition G c omega

def UniversalCommonBlueMatching (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads, Nonempty (Matching G c omega)

theorem universalCommonBlueMatching_iff_hall (G : GraphData) (c : CutData) (bads : List BadEdgeData) :
    UniversalCommonBlueMatching G c bads ↔ UniversalCommonBlueHall G c bads := by
  constructor
  · intro h omega
    exact (matching_nonempty_iff_hall G c omega).mp (h omega)
  · intro h omega
    exact (matching_nonempty_iff_hall G c omega).mpr (h omega)

def RealUniversalCommonBlueHall (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  checkGraph G = true → TriangleFree G → IsMaxCut G c → BConnected G c →
  GammaMinimalConnected G c → CompleteShortestRowDB G c bads →
  UniversalCommonBlueHall G c bads

theorem realUniversalCommonBlueMatching_of_hall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hgraph : checkGraph G = true) (htri : TriangleFree G) (hmax : IsMaxCut G c) (hconn : BConnected G c)
    (hgamma : GammaMinimalConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hHall : RealUniversalCommonBlueHall G c bads) :
    UniversalCommonBlueMatching G c bads := by
  apply (universalCommonBlueMatching_iff_hall G c bads).mpr
  exact hHall hgraph htri hmax hconn hgamma hdb

#print axioms universalCommonBlueMatching_iff_hall
#print axioms realUniversalCommonBlueMatching_of_hall
end Erdos23Delta0.Gamma.CommonBlueExtendedMatching


