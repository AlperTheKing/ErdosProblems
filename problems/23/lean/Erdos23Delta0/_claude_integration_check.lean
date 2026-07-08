import Erdos23Delta0.Ell5CSReduction
import Erdos23Delta0.MaxCutVertexIneq
import Erdos23Delta0.Ell5GraphBridge
import Erdos23Delta0.PathRigidity
import Erdos23Delta0.Ell5AtomBase
import Erdos23Delta0.Ell5AtomGraph
import Erdos23Delta0.CageSuperadditivity

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

end IntegrationCheck
end Erdos23Delta0
