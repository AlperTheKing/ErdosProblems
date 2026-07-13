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
import Erdos23Delta0.Cert.Rung2SourceData.Shard015
import Erdos23Delta0.Cert.Rung2SourceData.Shard016
import Erdos23Delta0.Cert.Rung2SourceData.Shard017
import Erdos23Delta0.Cert.Rung2SourceData.Shard018
import Erdos23Delta0.Cert.Rung2SourceData.Shard019
import Erdos23Delta0.Cert.Rung2SourceData.Shard020
import Erdos23Delta0.Cert.Rung2SourceData.Shard021
import Erdos23Delta0.Cert.Rung2SourceData.Shard022
import Erdos23Delta0.Cert.Rung2SourceData.Shard023
import Erdos23Delta0.Cert.Rung2SourceData.Shard024

namespace Erdos23Delta0
namespace Cert

def rung2SourceMeta : Rung2SourceMeta := {
  chart := 6,
  dominant := 5,
  band := "near_2s_minus_1",
  support := "negative",
  columnsChecked := 29759,
  nonzeroSourceColumns := 2432,
  solutionRecords := 2432,
  solutionNegativeCount := 0,
  fullNegativeResidualCount := 0,
  fullMinResidual := "0",
  fullZeroResidualCount := 158472,
  targetBetaMode := "prepared_p_beta",
  targetBetaJsonSha256 := "",
  targetBetaNonzeroCount := 0,
  solutionSha256 := "3f754ef9ccd615fce0071319e36398251a0f9d56de621584a61fdbcca3824976",
  checkSummarySha256 := "1e3fe681108140e43e86c35a5f99abf7c75e9a262d6fde4d9ebf708dcf30ffff",
  modularSummarySha256 := "492bfd3274c5ca3f55f039acc15482d855a7cf1295de0f7c59034bd8d7e912b6"
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
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard005,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard006,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard007,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard008,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard009,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard010,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard011,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard012,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard013,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard014,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard015,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard016,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard017,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard018,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard019,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard020,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard021,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard022,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard023,
  rung2SourceCoeffListCheck rung2SourceMeta.columnsChecked rung2SourceCoeffsShard024
]

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffShardChecks_expected :
    rung2SourceCoeffShardChecks = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true] := by
  rfl

set_option maxRecDepth 2000000 in
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
  rung2SourceCoeffsShard014.length,
  rung2SourceCoeffsShard015.length,
  rung2SourceCoeffsShard016.length,
  rung2SourceCoeffsShard017.length,
  rung2SourceCoeffsShard018.length,
  rung2SourceCoeffsShard019.length,
  rung2SourceCoeffsShard020.length,
  rung2SourceCoeffsShard021.length,
  rung2SourceCoeffsShard022.length,
  rung2SourceCoeffsShard023.length,
  rung2SourceCoeffsShard024.length
]

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffShardLengths_expected :
    rung2SourceCoeffShardLengths = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 32] := by
  rfl

theorem rung2SourceCoeffShardCount : rung2SourceCoeffShardChecks.length = 25 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffTotalRows : natListSum rung2SourceCoeffShardLengths = 2432 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceCoeffTotalRows_matches_meta : natListSum rung2SourceCoeffShardLengths = rung2SourceMeta.solutionRecords := by
  rfl

end Cert
end Erdos23Delta0
