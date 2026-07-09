import Erdos23Delta0.Ell5CSReduction
import Erdos23Delta0.MaxCutVertexIneq
import Erdos23Delta0.Ell5GraphBridge
import Erdos23Delta0.PathRigidity
import Erdos23Delta0.Ell5AtomBase
import Erdos23Delta0.Ell5AtomGraph
import Erdos23Delta0.CageSuperadditivity
import Erdos23Delta0.Ell5GeodesicUnion
import Erdos23Delta0.Ell5F5LiftInterface
import Erdos23Delta0.Ell5FullBankInterface
import Erdos23Delta0.O14.EQODL1CoverInterface
import Erdos23Delta0.O14.EQODL1LeafProvider
import Erdos23Delta0.O14.ChartCoverToODLFull

/-! Integration check: forces all seven session modules to load and typecheck TOGETHER (catches olean staleness /
    cross-module conflict before assembly). The imports themselves are the test; the `#check`s pin the public
    interface names that downstream assembly will consume. Not part of the proof; a QA probe. -/

namespace Erdos23Delta0
namespace IntegrationCheck

#check @Ell5CSReduction.hall_le_five
#check @Ell5GraphBridge.ell5_support_card_ge_four
#check @PathRigidity.edges_determine_badedge
#check @Ell5AtomBase.ell5_base_case
#check @Ell5AtomGraph.ell5_atom_of_badEdge
#check @CageSuperadditivity.card_le_Nsq_div_25
#check @CageSuperadditivity.gamma_le_Nsq_of_components
#check @Ell5GeodesicUnion.no_three_common_edges_len4_same_endpoints
#check @Ell5GeodesicUnion.geodesics_union_ge_six
#check @Ell5GeodesicUnion.no_minimal_violator_card_six_geodesicSupport
#check @Ell5F5LiftInterface.no_card_seven_violator_of_no_realizable_f5_core_shape_gate
#check @Ell5FullBankInterface.graph_bankedCutDomination_of_cert
#check @Ell5FullBankInterface.graph_no_dualCert_of_cert
#check @O14.EQODL1CoverInterface.goal_of_checkEQODL1CoverCert
#check @O14.EQODL1CoverInterface.coreODLGoal_of_checkEQODL1CoverCert
#check @O14.EQODL1LeafProvider.leafProviders_of_concreteChecksWithEQ
#check @O14.EQODL1LeafProvider.resolvedODL_eq_leaf_of_o14_cover
#check @O14.EQODL1LeafProvider.concreteChecksWithEQ_of_o14_cover
#check @O14.ChartCoverToODLFull.rowODL_of_o14_eq_cover_semantic_tree

end IntegrationCheck
end Erdos23Delta0
