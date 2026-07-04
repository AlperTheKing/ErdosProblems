/- Generated aggregate imports for Rung-2 source-certificate data. -/
import Erdos23Delta0.Cert.Rung2SourceSupport
import Erdos23Delta0.Cert.Rung2SourceData.Shard000
import Erdos23Delta0.Cert.Rung2SourceData.Shard001
import Erdos23Delta0.Cert.Rung2SourceData.Shard002
import Erdos23Delta0.Cert.Rung2SourceData.Shard003
import Erdos23Delta0.Cert.Rung2SourceData.Shard004
import Erdos23Delta0.Cert.Rung2SourceData.Shard005
import Erdos23Delta0.Cert.Rung2SourceData.Shard006
import Erdos23Delta0.Cert.Rung2SourceData.Shard007
import Erdos23Delta0.Cert.Rung2SourceData.Shard008
import Erdos23Delta0.Cert.Rung2SourceData.Shard009
import Erdos23Delta0.Cert.Rung2SourceData.Shard010
import Erdos23Delta0.Cert.Rung2SourceData.Shard011
import Erdos23Delta0.Cert.Rung2SourceData.Shard012
import Erdos23Delta0.Cert.Rung2SourceData.Shard013
import Erdos23Delta0.Cert.Rung2SourceData.Shard014

namespace Erdos23Delta0
namespace Cert

def rung2SourceMeta : Rung2SourceMeta := {
  chart := 5,
  dominant := 13,
  band := "near_2s_minus_1",
  support := "negative",
  columnsChecked := 29801,
  nonzeroSourceColumns := 1414,
  solutionRecords := 1414,
  solutionNegativeCount := 0,
  fullNegativeResidualCount := 0,
  fullMinResidual := "0",
  fullZeroResidualCount := 161567,
  solutionSha256 := "9313ea2e4e96310f4f7bfb0423f2ee666cfd1ae1b98e1e9eebb5326b4e4e213f",
  checkSummarySha256 := "d97a32ed061e8ccafc9c1fcef1a919d0986c712d7ab2a0baf8e4630426e4bca8",
  modularSummarySha256 := "7df9bc0f071d0e2dd655f52c2c693e8b9dfd090d0fdd1352edaa8674be9f450c"
}

theorem rung2SourceMeta_check : Rung2SourceMeta.check rung2SourceMeta = true := by
  rfl

def rung2SourceCoeffShardChecks : List Bool := [
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard000,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard001,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard002,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard003,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard004,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard005,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard006,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard007,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard008,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard009,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard010,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard011,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard012,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard013,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard014
]

set_option maxRecDepth 200000 in
theorem rung2SourceCoeffShardChecks_expected :
    rung2SourceCoeffShardChecks = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true] := by
  rfl

def rung2SourceCoeffShardLengths : List Nat := [
  rung2SourceCoeffsShard000.length,
  rung2SourceCoeffsShard001.length,
  rung2SourceCoeffsShard002.length,
  rung2SourceCoeffsShard003.length,
  rung2SourceCoeffsShard004.length,
  rung2SourceCoeffsShard005.length,
  rung2SourceCoeffsShard006.length,
  rung2SourceCoeffsShard007.length,
  rung2SourceCoeffsShard008.length,
  rung2SourceCoeffsShard009.length,
  rung2SourceCoeffsShard010.length,
  rung2SourceCoeffsShard011.length,
  rung2SourceCoeffsShard012.length,
  rung2SourceCoeffsShard013.length,
  rung2SourceCoeffsShard014.length
]

set_option maxRecDepth 200000 in
theorem rung2SourceCoeffShardLengths_expected :
    rung2SourceCoeffShardLengths = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 14] := by
  rfl

theorem rung2SourceCoeffShardCount : rung2SourceCoeffShardChecks.length = 15 := by
  rfl

set_option maxRecDepth 200000 in
theorem rung2SourceCoeffTotalRows : natListSum rung2SourceCoeffShardLengths = 1414 := by
  rfl

set_option maxRecDepth 200000 in
theorem rung2SourceCoeffTotalRows_matches_meta : natListSum rung2SourceCoeffShardLengths = rung2SourceMeta.solutionRecords := by
  rfl

end Cert
end Erdos23Delta0
