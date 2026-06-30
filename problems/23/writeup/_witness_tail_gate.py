"""EXACT gate of Codex block-263 WITNESS-ANCHORED-TAIL (sharpened Branch-A / P198 proof target).
For each no-bracket P-contained position-flow deficit (contained_flow_failures): reconstruct load, find the
min-slack Hall interval [a,b] (min_interval_slack), reconstruct P-contained intervals (contained_intervals).
CLAIM: among closed prefix/suffix tails at atom endpoints {lo-1,lo,hi,hi+1} of intervals TOUCHING [a,b]
(lo in [a,b] or hi in [a,b] or straddling lo<a,hi>b), at least one has boundary_gain>0.
Full battery (gmins + structured + cases + Mycielskian + glued). Report deficits, positive, misses, first miss."""
import subprocess
from fractions import Fraction as F
from _codex_net_globalmax_probe import contained_flow_failures, cases, build_pd, add_cut_path
from _codex_pcontained_interval_witness_gate import min_interval_slack
from _closed_tail_switch_gate import b_closed_tail
from _M_tailswitch_gate import boundary_gain
from _overlap_switch_probe import contained_intervals
from _satzmu_conn import struct_for_side
from _h import dec, GENG, Bconn
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

def run_side(name,n,edges,side,acc):
    adj=adj_of(n,edges)
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    for (f,path,chords,spans,total,flow) in contained_flow_failures(n,adj,side):
        # reconstruct load
        L=len(path)
        load=[F(0)]*L
        for (lo,hi,g) in chords:
            k=len(cyc[g])
            for i in range(lo,hi+1): load[i]+=F(1,k)
        slack,info=min_interval_slack(load,spans)
        if info is None: continue
        a,b,dem,cap=info
        # P-contained intervals
        try:
            ivs=contained_intervals(M,cyc,f,path)
        except Exception:
            ivs=[(lo,hi) for (lo,hi,_g) in chords]
        # normalize ivs to (lo,hi)
        norm=[]
        for it in ivs:
            if len(it)>=2: norm.append((it[0],it[1]))
        acc['deficits']+=1
        found=False
        for (lo,hi) in norm:
            touch = (a<=lo<=b) or (a<=hi<=b) or (lo<a and hi>b)
            if not touch: continue
            for k in (lo-1,lo,hi,hi+1):
                if not (0<=k<L): continue
                for raw in (set(path[:k+1]), set(path[k:])):
                    if not raw: continue
                    W=b_closed_tail(n,adj,side,path,raw)
                    if boundary_gain(n,adj,side,W)>0:
                        found=True; break
                if found: break
            if found: break
        if found: acc['pos']+=1
        else:
            acc['miss']+=1
            if acc['first'] is None: acc['first']=(name,n,L,str(slack))

def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    acc=dict(deficits=0,pos=0,miss=0,first=None)
    for name,n,edges,side in cases():
        run_side("case:"+name,n,edges,side,acc)
    for reps in (1,2):
        n,edges=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
        for _ in range(reps): n,edges,side=add_cut_path(n,list(edges),side,2,6,6)
        run_side("ballast%d"%reps,n,sorted(set(edges)),side,acc)
    print("  cases+ballast: deficits=%d pos=%d miss=%d"%(acc['deficits'],acc['pos'],acc['miss']),flush=True)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: run_side(nm,nn,E,s,acc)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): run_side("C%d[%d]"%(c,t),n,E,s,acc)
    print("  + Mycielskian/glued/blowups: deficits=%d pos=%d miss=%d"%(acc['deficits'],acc['pos'],acc['miss']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: run_side("cen%s"%g6,n,E,s,acc)
        print("  census N=%d done: deficits=%d miss=%d"%(nn,acc['deficits'],acc['miss']),flush=True)
    print("\n  WITNESS-ANCHORED-TAIL: deficits=%d  witness_anchored_positive=%d  MISSES=%d"%(acc['deficits'],acc['pos'],acc['miss']),flush=True)
    if acc['first']: print("  first miss: %s"%(acc['first'],),flush=True)
    print("  === %s ==="%("HOLDS => Branch-A P198 lemma (anchored atom-tail) survives full battery" if acc['miss']==0 else "FAILS -- miss found"),flush=True)
