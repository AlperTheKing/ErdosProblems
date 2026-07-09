import Erdos23Delta0.Cert.Rung2SourceData
import Erdos23Delta0.O14.Generated.Classifier

/-!
# O14 generated chart payload 000: pilot source-data hook

This pilot imports the existing accepted source-solution data for ledger
numeric-order `0` (chart `5`, dominant `13`) and exposes small rfl-checkable
facts.  It is not yet the final ConeCert-to-CoreODLGoal chart soundness module.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated
namespace ChartPayloads
namespace Chart000

open Cert

def payloadMeta : Rung2SourceMeta := Cert.rung2SourceMeta

theorem payloadMeta_check : Rung2SourceMeta.check payloadMeta = true := by
  exact Cert.rung2SourceMeta_check

theorem payloadMeta_chart : payloadMeta.chart = 5 := by
  rfl

theorem payloadMeta_dominant : payloadMeta.dominant = 13 := by
  rfl

theorem payloadMeta_solution_records : payloadMeta.solutionRecords = 1414 := by
  rfl

theorem coeff_total_rows_matches_meta :
    Cert.natListSum Cert.rung2SourceCoeffShardLengths = payloadMeta.solutionRecords := by
  exact Cert.rung2SourceCoeffTotalRows_matches_meta

#print axioms payloadMeta_check
#print axioms coeff_total_rows_matches_meta

end Chart000
end ChartPayloads
end Generated
end O14
end Erdos23Delta0
