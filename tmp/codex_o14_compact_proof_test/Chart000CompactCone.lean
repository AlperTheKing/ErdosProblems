import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeSupport
import Erdos23Delta0.O14.CompactPilot.Chart000ScaledDirect000
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS000
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS001
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS002
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS003
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS004
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS005
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS006
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS007
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS008
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS009
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS010
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS011
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS012
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS013
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS014
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS015
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS016
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS017
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS018
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS019
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS020
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS021
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS022
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS023
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS024
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS025
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS026
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS027
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS028
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS029
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS030
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS031
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS032
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS033
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS034
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS035
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS036
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS037
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS038
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS039
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS040
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS041
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS042
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS043
import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeMS044

namespace Erdos23Delta0
namespace O14
namespace CompactPilot
namespace Chart000CompactCone

open PolyCert
open ODLFull
open ConeEvalBridge

set_option maxHeartbeats 0
set_option maxRecDepth 2000000

def baseShards : List NF := [
  Chart000ScaledDirect000.baseTerms
]

theorem hbaseShards : baseShards.all NF.allCoeffNonneg = true := by
  simp [baseShards, Chart000ScaledDirect000.hbaseTerms]

def base : NF := baseShards.flatten

theorem hbase : NF.allCoeffNonneg base = true := by
  exact Generated.ChartPayloads.Chart000Cone.Support.nf_allCoeffNonneg_flatten_true baseShards hbaseShards

def multShards : List (List NF) := [
  Generated.ChartPayloads.Chart000Cone.MS000.mults,
  Generated.ChartPayloads.Chart000Cone.MS001.mults,
  Generated.ChartPayloads.Chart000Cone.MS002.mults,
  Generated.ChartPayloads.Chart000Cone.MS003.mults,
  Generated.ChartPayloads.Chart000Cone.MS004.mults,
  Generated.ChartPayloads.Chart000Cone.MS005.mults,
  Generated.ChartPayloads.Chart000Cone.MS006.mults,
  Generated.ChartPayloads.Chart000Cone.MS007.mults,
  Generated.ChartPayloads.Chart000Cone.MS008.mults,
  Generated.ChartPayloads.Chart000Cone.MS009.mults,
  Generated.ChartPayloads.Chart000Cone.MS010.mults,
  Generated.ChartPayloads.Chart000Cone.MS011.mults,
  Generated.ChartPayloads.Chart000Cone.MS012.mults,
  Generated.ChartPayloads.Chart000Cone.MS013.mults,
  Generated.ChartPayloads.Chart000Cone.MS014.mults,
  Generated.ChartPayloads.Chart000Cone.MS015.mults,
  Generated.ChartPayloads.Chart000Cone.MS016.mults,
  Generated.ChartPayloads.Chart000Cone.MS017.mults,
  Generated.ChartPayloads.Chart000Cone.MS018.mults,
  Generated.ChartPayloads.Chart000Cone.MS019.mults,
  Generated.ChartPayloads.Chart000Cone.MS020.mults,
  Generated.ChartPayloads.Chart000Cone.MS021.mults,
  Generated.ChartPayloads.Chart000Cone.MS022.mults,
  Generated.ChartPayloads.Chart000Cone.MS023.mults,
  Generated.ChartPayloads.Chart000Cone.MS024.mults,
  Generated.ChartPayloads.Chart000Cone.MS025.mults,
  Generated.ChartPayloads.Chart000Cone.MS026.mults,
  Generated.ChartPayloads.Chart000Cone.MS027.mults,
  Generated.ChartPayloads.Chart000Cone.MS028.mults,
  Generated.ChartPayloads.Chart000Cone.MS029.mults,
  Generated.ChartPayloads.Chart000Cone.MS030.mults,
  Generated.ChartPayloads.Chart000Cone.MS031.mults,
  Generated.ChartPayloads.Chart000Cone.MS032.mults,
  Generated.ChartPayloads.Chart000Cone.MS033.mults,
  Generated.ChartPayloads.Chart000Cone.MS034.mults,
  Generated.ChartPayloads.Chart000Cone.MS035.mults,
  Generated.ChartPayloads.Chart000Cone.MS036.mults,
  Generated.ChartPayloads.Chart000Cone.MS037.mults,
  Generated.ChartPayloads.Chart000Cone.MS038.mults,
  Generated.ChartPayloads.Chart000Cone.MS039.mults,
  Generated.ChartPayloads.Chart000Cone.MS040.mults,
  Generated.ChartPayloads.Chart000Cone.MS041.mults,
  Generated.ChartPayloads.Chart000Cone.MS042.mults,
  Generated.ChartPayloads.Chart000Cone.MS043.mults,
  Generated.ChartPayloads.Chart000Cone.MS044.mults
]

def slackShards : List (List NF) := [
  Generated.ChartPayloads.Chart000Cone.MS000.slacks,
  Generated.ChartPayloads.Chart000Cone.MS001.slacks,
  Generated.ChartPayloads.Chart000Cone.MS002.slacks,
  Generated.ChartPayloads.Chart000Cone.MS003.slacks,
  Generated.ChartPayloads.Chart000Cone.MS004.slacks,
  Generated.ChartPayloads.Chart000Cone.MS005.slacks,
  Generated.ChartPayloads.Chart000Cone.MS006.slacks,
  Generated.ChartPayloads.Chart000Cone.MS007.slacks,
  Generated.ChartPayloads.Chart000Cone.MS008.slacks,
  Generated.ChartPayloads.Chart000Cone.MS009.slacks,
  Generated.ChartPayloads.Chart000Cone.MS010.slacks,
  Generated.ChartPayloads.Chart000Cone.MS011.slacks,
  Generated.ChartPayloads.Chart000Cone.MS012.slacks,
  Generated.ChartPayloads.Chart000Cone.MS013.slacks,
  Generated.ChartPayloads.Chart000Cone.MS014.slacks,
  Generated.ChartPayloads.Chart000Cone.MS015.slacks,
  Generated.ChartPayloads.Chart000Cone.MS016.slacks,
  Generated.ChartPayloads.Chart000Cone.MS017.slacks,
  Generated.ChartPayloads.Chart000Cone.MS018.slacks,
  Generated.ChartPayloads.Chart000Cone.MS019.slacks,
  Generated.ChartPayloads.Chart000Cone.MS020.slacks,
  Generated.ChartPayloads.Chart000Cone.MS021.slacks,
  Generated.ChartPayloads.Chart000Cone.MS022.slacks,
  Generated.ChartPayloads.Chart000Cone.MS023.slacks,
  Generated.ChartPayloads.Chart000Cone.MS024.slacks,
  Generated.ChartPayloads.Chart000Cone.MS025.slacks,
  Generated.ChartPayloads.Chart000Cone.MS026.slacks,
  Generated.ChartPayloads.Chart000Cone.MS027.slacks,
  Generated.ChartPayloads.Chart000Cone.MS028.slacks,
  Generated.ChartPayloads.Chart000Cone.MS029.slacks,
  Generated.ChartPayloads.Chart000Cone.MS030.slacks,
  Generated.ChartPayloads.Chart000Cone.MS031.slacks,
  Generated.ChartPayloads.Chart000Cone.MS032.slacks,
  Generated.ChartPayloads.Chart000Cone.MS033.slacks,
  Generated.ChartPayloads.Chart000Cone.MS034.slacks,
  Generated.ChartPayloads.Chart000Cone.MS035.slacks,
  Generated.ChartPayloads.Chart000Cone.MS036.slacks,
  Generated.ChartPayloads.Chart000Cone.MS037.slacks,
  Generated.ChartPayloads.Chart000Cone.MS038.slacks,
  Generated.ChartPayloads.Chart000Cone.MS039.slacks,
  Generated.ChartPayloads.Chart000Cone.MS040.slacks,
  Generated.ChartPayloads.Chart000Cone.MS041.slacks,
  Generated.ChartPayloads.Chart000Cone.MS042.slacks,
  Generated.ChartPayloads.Chart000Cone.MS043.slacks,
  Generated.ChartPayloads.Chart000Cone.MS044.slacks
]

def mults : List NF := multShards.flatten
def slacks : List NF := slackShards.flatten

theorem hmultShards :
    multShards.all (fun xs => xs.all NF.allCoeffNonneg) = true := by
  simp [multShards, Generated.ChartPayloads.Chart000Cone.MS000.hmults, Generated.ChartPayloads.Chart000Cone.MS001.hmults, Generated.ChartPayloads.Chart000Cone.MS002.hmults, Generated.ChartPayloads.Chart000Cone.MS003.hmults, Generated.ChartPayloads.Chart000Cone.MS004.hmults, Generated.ChartPayloads.Chart000Cone.MS005.hmults, Generated.ChartPayloads.Chart000Cone.MS006.hmults, Generated.ChartPayloads.Chart000Cone.MS007.hmults, Generated.ChartPayloads.Chart000Cone.MS008.hmults, Generated.ChartPayloads.Chart000Cone.MS009.hmults, Generated.ChartPayloads.Chart000Cone.MS010.hmults, Generated.ChartPayloads.Chart000Cone.MS011.hmults, Generated.ChartPayloads.Chart000Cone.MS012.hmults, Generated.ChartPayloads.Chart000Cone.MS013.hmults, Generated.ChartPayloads.Chart000Cone.MS014.hmults, Generated.ChartPayloads.Chart000Cone.MS015.hmults, Generated.ChartPayloads.Chart000Cone.MS016.hmults, Generated.ChartPayloads.Chart000Cone.MS017.hmults, Generated.ChartPayloads.Chart000Cone.MS018.hmults, Generated.ChartPayloads.Chart000Cone.MS019.hmults, Generated.ChartPayloads.Chart000Cone.MS020.hmults, Generated.ChartPayloads.Chart000Cone.MS021.hmults, Generated.ChartPayloads.Chart000Cone.MS022.hmults, Generated.ChartPayloads.Chart000Cone.MS023.hmults, Generated.ChartPayloads.Chart000Cone.MS024.hmults, Generated.ChartPayloads.Chart000Cone.MS025.hmults, Generated.ChartPayloads.Chart000Cone.MS026.hmults, Generated.ChartPayloads.Chart000Cone.MS027.hmults, Generated.ChartPayloads.Chart000Cone.MS028.hmults, Generated.ChartPayloads.Chart000Cone.MS029.hmults, Generated.ChartPayloads.Chart000Cone.MS030.hmults, Generated.ChartPayloads.Chart000Cone.MS031.hmults, Generated.ChartPayloads.Chart000Cone.MS032.hmults, Generated.ChartPayloads.Chart000Cone.MS033.hmults, Generated.ChartPayloads.Chart000Cone.MS034.hmults, Generated.ChartPayloads.Chart000Cone.MS035.hmults, Generated.ChartPayloads.Chart000Cone.MS036.hmults, Generated.ChartPayloads.Chart000Cone.MS037.hmults, Generated.ChartPayloads.Chart000Cone.MS038.hmults, Generated.ChartPayloads.Chart000Cone.MS039.hmults, Generated.ChartPayloads.Chart000Cone.MS040.hmults, Generated.ChartPayloads.Chart000Cone.MS041.hmults, Generated.ChartPayloads.Chart000Cone.MS042.hmults, Generated.ChartPayloads.Chart000Cone.MS043.hmults, Generated.ChartPayloads.Chart000Cone.MS044.hmults]

theorem hmults : mults.all NF.allCoeffNonneg = true := by
  exact Generated.ChartPayloads.Chart000Cone.Support.all_nf_allCoeffNonneg_flatten_true multShards hmultShards

theorem coreODLGoal_of_compactCone
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q)
    (target : NF) (env : Var -> Rat)
    (hvars : forall v, 0 <= env v)
    (hslacks : ∀ s ∈ slacks, 0 <= NF.eval env s)
    (hidEval :
      NF.eval env target = NF.eval env (comboNF base mults slacks))
    (htarget : NF.eval env target = coreDefect core) :
    CoreODLGoal G c rows Q core := by
  exact coreODLGoal_of_coneEval core target base mults slacks env
    hvars hbase hmults hslacks hidEval htarget

end Chart000CompactCone
end CompactPilot
end O14
end Erdos23Delta0
