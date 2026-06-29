"""M-HUNT census (gold standard, construction-free): over EVERY triangle-free graph N<=11,
compute the TRUE global max cut via maxcut_all (exact), then for EVERY global-max connected-B cut
check for a P-contained interior-overlap (lemma (M)). Also count overlaps on SUB-max cuts (near-miss).

This is the definitive adversarial test at small N: if a verified-global-max P-contained
interior-overlap exists on any triangle-free graph up to N=11, it is found here. EXACT.
Run from .../problems/23/writeup."""
import subprocess
from _h import dec, GENG, maxcut_all
from _wf_mhunt_1 import find_overlaps_on_cut, cutsize

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def scan(n,E,g6,acc):
    adj=adj_of(n,E)
    cuts=maxcut_all(n,adj); truemax=cutsize(n,adj,cuts[0])
    for m in range(1<<(n-1)):
        s=[(m>>v)&1 for v in range(n)]
        c=cutsize(n,adj,s)
        st,ov=find_overlaps_on_cut(n,adj,s)
        if st!='ok' or not ov: continue
        if c==truemax:
            acc['glob']+=1
            if acc['witness'] is None:
                acc['witness']=dict(g6=g6,n=n,side=s[:],truemax=truemax,
                                    edges=sorted((min(a,b),max(a,b)) for a,b in E),
                                    rec=ov[0],allrecs=ov)
        else:
            acc['sub']+=1

if __name__=="__main__":
    print("=== M-HUNT census: ALL triangle-free graphs N<=11, verified global-max overlap check ===",flush=True)
    acc={'glob':0,'sub':0,'witness':None}
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        g0=acc['glob']; s0=acc['sub']
        for g6 in outg:
            n,E=dec(g6); scan(n,E,g6,acc)
            if acc['witness'] is not None: break
        print(f"  N={nn}: graphs={len(outg)}  overlap-on-GLOBAL(+{acc['glob']-g0})  overlap-on-SUB-nearmiss(+{acc['sub']-s0})"
              + (" *** WITNESS ***" if acc['witness'] else ""),flush=True)
        if acc['witness'] is not None: break
    print(f"\n  TOTAL overlap-on-GLOBAL-max cuts = {acc['glob']}   overlap-on-SUB-max (near-miss) = {acc['sub']}",flush=True)
    if acc['witness']:
        w=acc['witness']
        print(f"  *** WITNESS g6={w['g6']} N={w['n']} truemax={w['truemax']}",flush=True)
        print(f"  side={w['side']}",flush=True)
        print(f"  edges={w['edges']}",flush=True)
        print(f"  rec f={w['rec']['f']} P={w['rec']['P']} c1={w['rec']['c1']} c2={w['rec']['c2']}",flush=True)
    else:
        print("  NO verified-global-max P-contained interior-overlap in census N<=11 (lemma (M) holds).",flush=True)
