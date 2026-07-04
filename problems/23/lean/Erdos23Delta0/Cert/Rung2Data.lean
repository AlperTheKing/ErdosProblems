/- Generated aggregate imports for repaired Rung-2 exact certificate data. -/
import Erdos23Delta0.Cert.Rung2Support
import Erdos23Delta0.Cert.Rung2Data.Shard000
import Erdos23Delta0.Cert.Rung2Data.Shard001
import Erdos23Delta0.Cert.Rung2Data.Shard002
import Erdos23Delta0.Cert.Rung2Data.Shard003
import Erdos23Delta0.Cert.Rung2Data.Shard004
import Erdos23Delta0.Cert.Rung2Data.Shard005
import Erdos23Delta0.Cert.Rung2Data.Shard006
import Erdos23Delta0.Cert.Rung2Data.Shard007
import Erdos23Delta0.Cert.Rung2Data.Shard008
import Erdos23Delta0.Cert.Rung2Data.Shard009
import Erdos23Delta0.Cert.Rung2Data.Shard010
import Erdos23Delta0.Cert.Rung2Data.Shard011
import Erdos23Delta0.Cert.Rung2Data.Shard012
import Erdos23Delta0.Cert.Rung2Data.Shard013
import Erdos23Delta0.Cert.Rung2Data.Shard014
import Erdos23Delta0.Cert.Rung2Data.Shard015
import Erdos23Delta0.Cert.Rung2Data.Shard016
import Erdos23Delta0.Cert.Rung2Data.Shard017
import Erdos23Delta0.Cert.Rung2Data.Shard018
import Erdos23Delta0.Cert.Rung2Data.Shard019
import Erdos23Delta0.Cert.Rung2Data.Shard020
import Erdos23Delta0.Cert.Rung2Data.Shard021
import Erdos23Delta0.Cert.Rung2Data.Shard022
import Erdos23Delta0.Cert.Rung2Data.Shard023
import Erdos23Delta0.Cert.Rung2Data.Shard024
import Erdos23Delta0.Cert.Rung2Data.Shard025
import Erdos23Delta0.Cert.Rung2Data.Shard026

namespace Erdos23Delta0
namespace Cert

def rung2RepairedMeta : Rung2Meta := {
  chart := 0,
  dominant := 7,
  band := "near_2s_minus_1",
  support := "negative",
  columnsChecked := 43128,
  nonzeroSourceColumns := 2687,
  solutionRecords := 2687,
  solutionNegativeCount := 0,
  fullNegativeResidualCount := 0,
  fullMinResidual := "0",
  badRow := 71491,
  badBeta := [1, 1, 0, 0, 2, 2, 1, 0, 3, 1],
  repairSourceCol := 5251,
  repairColumnName := "F5",
  repairColumnKind := "gen",
  repairMultiplierExp := [1, 0, 0, 0, 2, 2, 1, 0, 3, 0],
  solutionSha256 := "41c837dfd5306b2e8dbe7212c3c6d5b74085b1d52037407bb40ab65a272db939",
  repairSummarySha256 := "59e64c98b44a303ce2c39e118a5b522d5ad7a3060ff35dec932dfaa08eb72134",
  checkSummarySha256 := "1dc626455950669f0d988497f56b0592f192f21e017915024d00801bb1990cae"
}

theorem rung2RepairedMeta_check : Rung2Meta.check rung2RepairedMeta = true := by
  rfl

def rung2CoeffShardChecks : List Bool := [
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard000,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard001,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard002,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard003,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard004,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard005,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard006,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard007,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard008,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard009,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard010,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard011,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard012,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard013,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard014,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard015,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard016,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard017,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard018,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard019,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard020,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard021,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard022,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard023,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard024,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard025,
  rung2CoeffListCheck rung2RepairedMeta.columnsChecked rung2CoeffsShard026
]

set_option maxRecDepth 200000 in
theorem rung2CoeffShardChecks_expected :
    rung2CoeffShardChecks = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true] := by
  rfl

def rung2CoeffShardLengths : List Nat := [
  rung2CoeffsShard000.length,
  rung2CoeffsShard001.length,
  rung2CoeffsShard002.length,
  rung2CoeffsShard003.length,
  rung2CoeffsShard004.length,
  rung2CoeffsShard005.length,
  rung2CoeffsShard006.length,
  rung2CoeffsShard007.length,
  rung2CoeffsShard008.length,
  rung2CoeffsShard009.length,
  rung2CoeffsShard010.length,
  rung2CoeffsShard011.length,
  rung2CoeffsShard012.length,
  rung2CoeffsShard013.length,
  rung2CoeffsShard014.length,
  rung2CoeffsShard015.length,
  rung2CoeffsShard016.length,
  rung2CoeffsShard017.length,
  rung2CoeffsShard018.length,
  rung2CoeffsShard019.length,
  rung2CoeffsShard020.length,
  rung2CoeffsShard021.length,
  rung2CoeffsShard022.length,
  rung2CoeffsShard023.length,
  rung2CoeffsShard024.length,
  rung2CoeffsShard025.length,
  rung2CoeffsShard026.length
]

set_option maxRecDepth 200000 in
theorem rung2CoeffShardLengths_expected :
    rung2CoeffShardLengths = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 87] := by
  rfl

theorem rung2CoeffShardCount : rung2CoeffShardChecks.length = 27 := by
  rfl

set_option maxRecDepth 200000 in
theorem rung2CoeffTotalRows : natListSum rung2CoeffShardLengths = 2687 := by
  rfl

set_option maxRecDepth 200000 in
theorem rung2CoeffTotalRows_matches_meta : natListSum rung2CoeffShardLengths = rung2RepairedMeta.solutionRecords := by
  rfl

end Cert
end Erdos23Delta0
