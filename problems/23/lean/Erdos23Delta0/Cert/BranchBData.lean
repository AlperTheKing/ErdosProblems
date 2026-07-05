/- Generated aggregate imports for Branch-B certificate shards. -/
import Erdos23Delta0.Cert.BranchBSupport
import Erdos23Delta0.Cert.BranchBDictionaryAudit
import Erdos23Delta0.Cert.BranchBData.Shard000
import Erdos23Delta0.Cert.BranchBData.Shard001
import Erdos23Delta0.Cert.BranchBData.Shard002
import Erdos23Delta0.Cert.BranchBData.Shard003
import Erdos23Delta0.Cert.BranchBData.Shard004
import Erdos23Delta0.Cert.BranchBData.Shard005
import Erdos23Delta0.Cert.BranchBData.Shard006
import Erdos23Delta0.Cert.BranchBData.Shard007
import Erdos23Delta0.Cert.BranchBData.Shard008
import Erdos23Delta0.Cert.BranchBData.Shard009
import Erdos23Delta0.Cert.BranchBData.Shard010
import Erdos23Delta0.Cert.BranchBData.Shard011
import Erdos23Delta0.Cert.BranchBData.Shard012
import Erdos23Delta0.Cert.BranchBData.Shard013
import Erdos23Delta0.Cert.BranchBData.Shard014
import Erdos23Delta0.Cert.BranchBData.Shard015
import Erdos23Delta0.Cert.BranchBData.Shard016
import Erdos23Delta0.Cert.BranchBData.Shard017
import Erdos23Delta0.Cert.BranchBData.Shard018
import Erdos23Delta0.Cert.BranchBData.Shard019
import Erdos23Delta0.Cert.BranchBData.Shard020
import Erdos23Delta0.Cert.BranchBData.Shard021
import Erdos23Delta0.Cert.BranchBData.Shard022
import Erdos23Delta0.Cert.BranchBData.Shard023
import Erdos23Delta0.Cert.BranchBData.Shard024
import Erdos23Delta0.Cert.BranchBData.Shard025
import Erdos23Delta0.Cert.BranchBData.Shard026
import Erdos23Delta0.Cert.BranchBData.Shard027
import Erdos23Delta0.Cert.BranchBData.Shard028

namespace Erdos23Delta0
namespace Cert

def branchBShardChecks : List Bool := [
  rowPilotListCheck branchBRowsShard000,
  rowPilotListCheck branchBRowsShard001,
  rowPilotListCheck branchBRowsShard002,
  rowPilotListCheck branchBRowsShard003,
  rowPilotListCheck branchBRowsShard004,
  rowPilotListCheck branchBRowsShard005,
  rowPilotListCheck branchBRowsShard006,
  rowPilotListCheck branchBRowsShard007,
  rowPilotListCheck branchBRowsShard008,
  rowPilotListCheck branchBRowsShard009,
  rowPilotListCheck branchBRowsShard010,
  rowPilotListCheck branchBRowsShard011,
  rowPilotListCheck branchBRowsShard012,
  rowPilotListCheck branchBRowsShard013,
  rowPilotListCheck branchBRowsShard014,
  rowPilotListCheck branchBRowsShard015,
  rowPilotListCheck branchBRowsShard016,
  rowPilotListCheck branchBRowsShard017,
  rowPilotListCheck branchBRowsShard018,
  rowPilotListCheck branchBRowsShard019,
  rowPilotListCheck branchBRowsShard020,
  rowPilotListCheck branchBRowsShard021,
  rowPilotListCheck branchBRowsShard022,
  rowPilotListCheck branchBRowsShard023,
  rowPilotListCheck branchBRowsShard024,
  rowPilotListCheck branchBRowsShard025,
  rowPilotListCheck branchBRowsShard026,
  rowPilotListCheck branchBRowsShard027,
  rowPilotListCheck branchBRowsShard028
]

set_option maxRecDepth 20000 in
theorem branchBShardChecks_expected :
    branchBShardChecks = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true] := by
  rfl

def branchBShardLengths : List Nat := [
  branchBRowsShard000.length,
  branchBRowsShard001.length,
  branchBRowsShard002.length,
  branchBRowsShard003.length,
  branchBRowsShard004.length,
  branchBRowsShard005.length,
  branchBRowsShard006.length,
  branchBRowsShard007.length,
  branchBRowsShard008.length,
  branchBRowsShard009.length,
  branchBRowsShard010.length,
  branchBRowsShard011.length,
  branchBRowsShard012.length,
  branchBRowsShard013.length,
  branchBRowsShard014.length,
  branchBRowsShard015.length,
  branchBRowsShard016.length,
  branchBRowsShard017.length,
  branchBRowsShard018.length,
  branchBRowsShard019.length,
  branchBRowsShard020.length,
  branchBRowsShard021.length,
  branchBRowsShard022.length,
  branchBRowsShard023.length,
  branchBRowsShard024.length,
  branchBRowsShard025.length,
  branchBRowsShard026.length,
  branchBRowsShard027.length,
  branchBRowsShard028.length
]

def branchBShardCaseCountVectors : List (List Nat) := [
  branchBCaseCountVector branchBRowsShard000,
  branchBCaseCountVector branchBRowsShard001,
  branchBCaseCountVector branchBRowsShard002,
  branchBCaseCountVector branchBRowsShard003,
  branchBCaseCountVector branchBRowsShard004,
  branchBCaseCountVector branchBRowsShard005,
  branchBCaseCountVector branchBRowsShard006,
  branchBCaseCountVector branchBRowsShard007,
  branchBCaseCountVector branchBRowsShard008,
  branchBCaseCountVector branchBRowsShard009,
  branchBCaseCountVector branchBRowsShard010,
  branchBCaseCountVector branchBRowsShard011,
  branchBCaseCountVector branchBRowsShard012,
  branchBCaseCountVector branchBRowsShard013,
  branchBCaseCountVector branchBRowsShard014,
  branchBCaseCountVector branchBRowsShard015,
  branchBCaseCountVector branchBRowsShard016,
  branchBCaseCountVector branchBRowsShard017,
  branchBCaseCountVector branchBRowsShard018,
  branchBCaseCountVector branchBRowsShard019,
  branchBCaseCountVector branchBRowsShard020,
  branchBCaseCountVector branchBRowsShard021,
  branchBCaseCountVector branchBRowsShard022,
  branchBCaseCountVector branchBRowsShard023,
  branchBCaseCountVector branchBRowsShard024,
  branchBCaseCountVector branchBRowsShard025,
  branchBCaseCountVector branchBRowsShard026,
  branchBCaseCountVector branchBRowsShard027,
  branchBCaseCountVector branchBRowsShard028
]

def branchBShardCandidateCountVectors : List (List Nat) := [
  branchBCandidateCountVector branchBRowsShard000,
  branchBCandidateCountVector branchBRowsShard001,
  branchBCandidateCountVector branchBRowsShard002,
  branchBCandidateCountVector branchBRowsShard003,
  branchBCandidateCountVector branchBRowsShard004,
  branchBCandidateCountVector branchBRowsShard005,
  branchBCandidateCountVector branchBRowsShard006,
  branchBCandidateCountVector branchBRowsShard007,
  branchBCandidateCountVector branchBRowsShard008,
  branchBCandidateCountVector branchBRowsShard009,
  branchBCandidateCountVector branchBRowsShard010,
  branchBCandidateCountVector branchBRowsShard011,
  branchBCandidateCountVector branchBRowsShard012,
  branchBCandidateCountVector branchBRowsShard013,
  branchBCandidateCountVector branchBRowsShard014,
  branchBCandidateCountVector branchBRowsShard015,
  branchBCandidateCountVector branchBRowsShard016,
  branchBCandidateCountVector branchBRowsShard017,
  branchBCandidateCountVector branchBRowsShard018,
  branchBCandidateCountVector branchBRowsShard019,
  branchBCandidateCountVector branchBRowsShard020,
  branchBCandidateCountVector branchBRowsShard021,
  branchBCandidateCountVector branchBRowsShard022,
  branchBCandidateCountVector branchBRowsShard023,
  branchBCandidateCountVector branchBRowsShard024,
  branchBCandidateCountVector branchBRowsShard025,
  branchBCandidateCountVector branchBRowsShard026,
  branchBCandidateCountVector branchBRowsShard027,
  branchBCandidateCountVector branchBRowsShard028
]

def branchBShardGateBRowCounts : List Nat := [
  rowPilotGateBRowCount branchBRowsShard000,
  rowPilotGateBRowCount branchBRowsShard001,
  rowPilotGateBRowCount branchBRowsShard002,
  rowPilotGateBRowCount branchBRowsShard003,
  rowPilotGateBRowCount branchBRowsShard004,
  rowPilotGateBRowCount branchBRowsShard005,
  rowPilotGateBRowCount branchBRowsShard006,
  rowPilotGateBRowCount branchBRowsShard007,
  rowPilotGateBRowCount branchBRowsShard008,
  rowPilotGateBRowCount branchBRowsShard009,
  rowPilotGateBRowCount branchBRowsShard010,
  rowPilotGateBRowCount branchBRowsShard011,
  rowPilotGateBRowCount branchBRowsShard012,
  rowPilotGateBRowCount branchBRowsShard013,
  rowPilotGateBRowCount branchBRowsShard014,
  rowPilotGateBRowCount branchBRowsShard015,
  rowPilotGateBRowCount branchBRowsShard016,
  rowPilotGateBRowCount branchBRowsShard017,
  rowPilotGateBRowCount branchBRowsShard018,
  rowPilotGateBRowCount branchBRowsShard019,
  rowPilotGateBRowCount branchBRowsShard020,
  rowPilotGateBRowCount branchBRowsShard021,
  rowPilotGateBRowCount branchBRowsShard022,
  rowPilotGateBRowCount branchBRowsShard023,
  rowPilotGateBRowCount branchBRowsShard024,
  rowPilotGateBRowCount branchBRowsShard025,
  rowPilotGateBRowCount branchBRowsShard026,
  rowPilotGateBRowCount branchBRowsShard027,
  rowPilotGateBRowCount branchBRowsShard028
]

set_option maxRecDepth 20000 in
theorem branchBShardLengths_expected :
    branchBShardLengths = [500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 247] := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBShardCaseCountVectors_expected :
    branchBShardCaseCountVectors = [
      [23, 254, 223, 0, 0, 0],
      [0, 165, 335, 0, 0, 0],
      [0, 93, 407, 0, 0, 0],
      [0, 84, 399, 17, 0, 0],
      [0, 42, 448, 10, 0, 0],
      [0, 120, 287, 69, 24, 0],
      [0, 191, 173, 0, 0, 136],
      [0, 140, 312, 39, 9, 0],
      [0, 183, 317, 0, 0, 0],
      [0, 126, 374, 0, 0, 0],
      [0, 21, 335, 96, 48, 0],
      [0, 201, 299, 0, 0, 0],
      [0, 145, 355, 0, 0, 0],
      [0, 0, 500, 0, 0, 0],
      [0, 18, 482, 0, 0, 0],
      [0, 43, 297, 160, 0, 0],
      [0, 154, 346, 0, 0, 0],
      [0, 74, 426, 0, 0, 0],
      [0, 27, 473, 0, 0, 0],
      [0, 328, 114, 46, 12, 0],
      [0, 319, 114, 63, 4, 0],
      [0, 167, 184, 147, 2, 0],
      [0, 158, 225, 93, 24, 0],
      [11, 268, 221, 0, 0, 0],
      [0, 104, 351, 42, 3, 0],
      [0, 53, 447, 0, 0, 0],
      [0, 161, 339, 0, 0, 0],
      [0, 37, 445, 18, 0, 0],
      [0, 12, 235, 0, 0, 0]
    ] := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBShardCandidateCountVectors_expected :
    branchBShardCandidateCountVectors = [
      [500, 0, 0],
      [500, 0, 0],
      [500, 0, 0],
      [483, 17, 0],
      [490, 10, 0],
      [407, 93, 0],
      [500, 0, 0],
      [452, 48, 0],
      [500, 0, 0],
      [500, 0, 0],
      [356, 144, 0],
      [500, 0, 0],
      [500, 0, 0],
      [500, 0, 0],
      [500, 0, 0],
      [340, 160, 0],
      [500, 0, 0],
      [500, 0, 0],
      [500, 0, 0],
      [442, 58, 0],
      [433, 67, 0],
      [351, 149, 0],
      [383, 117, 0],
      [500, 0, 0],
      [455, 45, 0],
      [500, 0, 0],
      [500, 0, 0],
      [482, 18, 0],
      [247, 0, 0]
    ] := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBShardGateBRowCounts_expected :
    branchBShardGateBRowCounts = [0, 0, 0, 17, 10, 93, 0, 48, 0, 0, 144, 0, 0, 0, 0, 160, 0, 0, 0, 58, 67, 149, 117, 0, 45, 0, 0, 18, 0] := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBShardCount : branchBShardChecks.length = 29 := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBTotalRows : natListSum branchBShardLengths = 14247 := by
  rfl

end Cert
end Erdos23Delta0
