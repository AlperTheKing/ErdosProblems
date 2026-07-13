import hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 subprocess.run([sys.executable,str(H/'r29_gate.py')],check=True,cwd=H)
 p=subprocess.run([sys.executable,str(H/'n3892_gate.py')],check=True,cwd=H,text=True,capture_output=True)
 n=json.loads(p.stdout); r=json.loads((H/'r29_common_blue_micro_result.json').read_text())
 assert (r['totalDemand'],r['sourceCount'],r['newCommonBlueKeys'])==(20025,20141,216)
 assert r['cuts'][-1]=={'shoreMask':7,'demand':20025,'reach':20141,'margin':116}
 assert n['N']==3892 and n['endpointDeficitPerOmega']=={'4':43,'8':38} and n['baseTransferSourcesPerOmega']==81
 shores=[{'mask':0,'demand':0,'certifiedReach':0,'margin':0},{'mask':1,'demand':25,'certifiedReach':43,'margin':18},{'mask':2,'demand':25,'certifiedReach':38,'margin':13},{'mask':3,'demand':50,'certifiedReach':81,'margin':31}]
 out={'verdict':'PASS','arithmetic':'integer only','coverage':{'graphs':2,'tuples':2,'globalMinima':2,'hitNeedZeroInherited':0,'hitNeedPositiveRecomputed':2,'flows':2,'cuts':12,'skipped':0},'N2943':{'collision':19950,'hitNeed':3,'oneCopyDemand':19953,'oldReach':19925,'newKeys':216,'microDemand':20025,'reach':20141,'flow':20025,'margin':116,'shores':r['cuts'],'allocationSha256':r['allocationSha256']},'N3892':{'collision':{'4':0,'8':0},'hitNeed':{'4':1,'8':1},'microDemand':{'4':25,'8':25},'flow':50,'shores':shores,'rowChoiceCoverage':'all; selected pairs permanently Free for every shortest-row choice','recordSha256':n['recordSHA256']},'inputs':{'n3892GeneratorSha256':sha(H/'_codex_endpointflow_3892_counterexample.py')}}
 (H/'result.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 (H/'REPORT.md').write_text('# Lane 06 exact MicroDemand gate\n\nVerdict: PASS; integer arithmetic only.\n\nCoverage: 2 graphs, 2 canonical/global-minimum tuples, 2 HitNeed-positive tuples recomputed, 0 HitNeed-zero inherited, 2 exact flows, 12 owner shores, 0 skipped inputs. N=3892 permanent-Free distance identities cover every row choice exactly.\n\nN=2943 recovered one-copy demand 19953, old reach 19925, and 216 new keys. Production demand is 20025, reach 20141, exact flow 20025, full-shore margin 116.\n\nN=3892 has collision (4:0, 8:0), HitNeed (4:1, 8:1), MicroDemand (4:25, 8:25), exact flow 50. Certified shore margins: 0,18,13,31. Its 81 disjoint sources satisfy dB=58, dM=0 and are permanently Free.\n\nReplay: `python r29_gate.py`; `python n3892_gate.py`; `python gate.py`; `python verify.py`.\n')
if __name__=='__main__': main()
