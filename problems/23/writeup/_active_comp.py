"""EXACT gate of Codex block-289 active-component containment. For every high neg band j (2t_j>=N, B_j<0):
(1) H_j contained in a single K-component C_j; (2) every prehalf positive band H_k contained in the same C_j.
K-components via kcomponents(n,cyc). Full battery (esp glued islands where prehalf may span components).
Report viol(1), viol(2), first witness."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary(n,adj,side,H):
    dB=dM=0
    for u in H:
        for v in adj[u]:
            if v in H: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); eta=F(n*n,25)-m
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    highneg=[]; prehalfpos=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=[v for v in range(n) if T[v]>tj]
        if not H: continue
        h=len(H); dB,dM=boundary(n,adj,side,set(H)); sig=dB-dM
        coef=wj*(F(n)+eta-tj-tn)
        if 2*tj<F(n) and coef>0:
            prehalfpos.append((set(cid[v] for v in H),H))
        elif 2*tj>=F(n):
            Bj=wj*(25*(F(n)+eta-tj-tn)*h - F(n)*sig)
            if Bj<0: highneg.append((set(cid[v] for v in H),H))
    for (compsj,Hj) in highneg:
        acc['nhigh']+=1
        if len(compsj)!=1:
            acc['v1']+=1
            if acc['f1'] is None: acc['f1']=(name,n,m,len(compsj))
            continue
        Cj=next(iter(compsj))
        for (compsk,Hk) in prehalfpos:
            acc['npre']+=1
            if compsk!={Cj}:
                acc['v2']+=1
                if acc['f2'] is None: acc['f2']=(name,''.join(map(str,side)),n,m,Cj,sorted(compsk))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nhigh':0,'npre':0,'v1':0,'v2':0,'f1':None,'f2':None}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: v1=%d v2=%d"%(acc['v1'],acc['v2']),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done (v1=%d v2=%d)"%(acc['v1'],acc['v2']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (v1=%d v2=%d)"%(nn,acc['v1'],acc['v2']),flush=True)
    print("\n  high-neg bands=%d prehalf comparisons=%d"%(acc['nhigh'],acc['npre']),flush=True)
    print("  (1) H_j in single K-component: violations=%d %s"%(acc['v1'],acc['f1'] or ''),flush=True)
    print("  (2) H_k in same C_j: violations=%d %s"%(acc['v2'],acc['f2'] or ''),flush=True)
    print("  === ACTIVE-COMPONENT-CONTAINMENT %s ==="%("HOLDS" if (acc['v1']==0 and acc['v2']==0) else "FAILS"),flush=True)
