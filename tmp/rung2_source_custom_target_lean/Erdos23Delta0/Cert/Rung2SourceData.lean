/- Generated aggregate imports for Rung-2 source-certificate data. -/
import Erdos23Delta0.Cert.Rung2SourceSupport
import Erdos23Delta0.Cert.Rung2SourceData.Shard000
import Erdos23Delta0.Cert.Rung2SourceData.Shard001
import Erdos23Delta0.Cert.Rung2SourceData.Shard002
import Erdos23Delta0.Cert.Rung2SourceData.Shard003
import Erdos23Delta0.Cert.Rung2SourceData.Shard004
import Erdos23Delta0.Cert.Rung2SourceData.Shard005

namespace Erdos23Delta0
namespace Cert

def rung2SourceMeta : Rung2SourceMeta := {
  chart := 3,
  dominant := 7,
  band := "near_2s_minus_1",
  support := "negative",
  columnsChecked := 43131,
  nonzeroSourceColumns := 2621,
  solutionRecords := 2621,
  solutionNegativeCount := 0,
  fullNegativeResidualCount := 0,
  fullMinResidual := "0",
  fullZeroResidualCount := 162477,
  targetBetaMode := "custom",
  targetBetaJsonSha256 := "fd24b4a072b18531f721a895034a3ade731d279a5e4ebf971e45b2ca62012d38",
  targetBetaNonzeroCount := 7720,
  solutionSha256 := "7a2485b8ddc439743629c4ae83b06aed161ca8fdf0727321655bd295296cc527",
  checkSummarySha256 := "4f411e4010b31a5043b3f12ee49b7504aca48a1a42fa5a450bf83d8319297b3d",
  modularSummarySha256 := ""
}

theorem rung2SourceMeta_check : Rung2SourceMeta.check rung2SourceMeta = true := by
  rfl

set_option maxRecDepth 2000000 in
def rung2SourceCoeffShardChecks : List Bool := [
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard000,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard001,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard002,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard003,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard004,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard005
]

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffShardChecks_expected :
    rung2SourceCoeffShardChecks = [true, true, true, true, true, true] := by
  rfl

set_option maxRecDepth 2000000 in
def rung2SourceCoeffShardLengths : List Nat := [
  rung2SourceCoeffsShard000.length,
  rung2SourceCoeffsShard001.length,
  rung2SourceCoeffsShard002.length,
  rung2SourceCoeffsShard003.length,
  rung2SourceCoeffsShard004.length,
  rung2SourceCoeffsShard005.length
]

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffShardLengths_expected :
    rung2SourceCoeffShardLengths = [500, 500, 500, 500, 500, 121] := by
  rfl

theorem rung2SourceCoeffShardCount : rung2SourceCoeffShardChecks.length = 6 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffTotalRows : natListSum rung2SourceCoeffShardLengths = 2621 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffTotalRows_matches_meta : natListSum rung2SourceCoeffShardLengths = rung2SourceMeta.solutionRecords := by
  rfl

end Cert
end Erdos23Delta0
