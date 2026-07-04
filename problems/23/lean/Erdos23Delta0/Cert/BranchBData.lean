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

set_option maxRecDepth 20000 in
theorem branchBShardLengths_expected :
    branchBShardLengths = [500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 247] := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBShardCount : branchBShardChecks.length = 29 := by
  rfl

set_option maxRecDepth 20000 in
theorem branchBTotalRows : natListSum branchBShardLengths = 14247 := by
  rfl

end Cert
end Erdos23Delta0
