/- Generated aggregate imports for Rung-2 source-certificate data. -/
import Erdos23Delta0.Cert.Rung2SourceSupport
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard000
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard001
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard002
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard003
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard004
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard005
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard006
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard007
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard008
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard009
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard010
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard011
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard012
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard013
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard014
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard015
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard016
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard017
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard018
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard019
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard020
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard021
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard022
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard023
import Erdos23Delta0.Cert.Rung2SourceData.K6F6.Shard024

namespace Erdos23Delta0
namespace Cert

def rung2SourceK6F6Meta : Rung2SourceMeta := {
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

theorem rung2SourceK6F6Meta_check : Rung2SourceMeta.check rung2SourceK6F6Meta = true := by
  rfl

set_option maxRecDepth 2000000 in
def rung2SourceK6F6CoeffShardChecks : List Bool := [
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard000,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard001,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard002,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard003,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard004,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard005,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard006,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard007,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard008,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard009,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard010,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard011,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard012,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard013,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard014,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard015,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard016,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard017,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard018,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard019,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard020,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard021,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard022,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard023,
  rung2SourceCoeffListCheck rung2SourceK6F6Meta.columnsChecked rung2SourceK6F6CoeffsShard024
]

set_option maxRecDepth 2000000 in
theorem rung2SourceK6F6CoeffShardChecks_expected :
    rung2SourceK6F6CoeffShardChecks = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true] := by
  rfl

set_option maxRecDepth 2000000 in
def rung2SourceK6F6CoeffShardLengths : List Nat := [
  rung2SourceK6F6CoeffsShard000.length,
  rung2SourceK6F6CoeffsShard001.length,
  rung2SourceK6F6CoeffsShard002.length,
  rung2SourceK6F6CoeffsShard003.length,
  rung2SourceK6F6CoeffsShard004.length,
  rung2SourceK6F6CoeffsShard005.length,
  rung2SourceK6F6CoeffsShard006.length,
  rung2SourceK6F6CoeffsShard007.length,
  rung2SourceK6F6CoeffsShard008.length,
  rung2SourceK6F6CoeffsShard009.length,
  rung2SourceK6F6CoeffsShard010.length,
  rung2SourceK6F6CoeffsShard011.length,
  rung2SourceK6F6CoeffsShard012.length,
  rung2SourceK6F6CoeffsShard013.length,
  rung2SourceK6F6CoeffsShard014.length,
  rung2SourceK6F6CoeffsShard015.length,
  rung2SourceK6F6CoeffsShard016.length,
  rung2SourceK6F6CoeffsShard017.length,
  rung2SourceK6F6CoeffsShard018.length,
  rung2SourceK6F6CoeffsShard019.length,
  rung2SourceK6F6CoeffsShard020.length,
  rung2SourceK6F6CoeffsShard021.length,
  rung2SourceK6F6CoeffsShard022.length,
  rung2SourceK6F6CoeffsShard023.length,
  rung2SourceK6F6CoeffsShard024.length
]

set_option maxRecDepth 2000000 in
theorem rung2SourceK6F6CoeffShardLengths_expected :
    rung2SourceK6F6CoeffShardLengths = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 32] := by
  rfl

theorem rung2SourceK6F6CoeffShardCount : rung2SourceK6F6CoeffShardChecks.length = 25 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceK6F6CoeffTotalRows : natListSum rung2SourceK6F6CoeffShardLengths = 2432 := by
  rfl

set_option maxRecDepth 2000000 in
theorem rung2SourceK6F6CoeffTotalRows_matches_meta : natListSum rung2SourceK6F6CoeffShardLengths = rung2SourceK6F6Meta.solutionRecords := by
  rfl

end Cert
end Erdos23Delta0
