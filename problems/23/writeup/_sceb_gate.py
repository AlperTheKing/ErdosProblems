"""EXACT gate of Codex block-255 SCEB (Subset Corridor-Exit Bound). For every full-low band (2b<=N), H={T>a},
O_H={v in H:T>N}, corridor intervals I (maximal cyclic P cap H runs, weight w(I)=ell/|cyc|). For every Z subset H:
  excess(Z)=sum_{v in Z}(T[v]-N)  <=  exit_O(Z)=sum_I w(I)*|I cap Z cap O_H|*1_{I not subset of Z}.
Z=H gives FULL-LOW-INTERNAL. Brute-force Z for h<=16 (larger bands covered by verified LBCT max-flow duality).
Report violations + min margin + first witness."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def cyclic_intervals(P,Hset):
    L=len(P); inH=[P[i] in Hset for i in range(L)]
    if all(inH): return [list(P)]
    if not any(inH): return []
    start=next(i for i in range(L) if not inH[i])
    ivs=[]; cur=[]
    for k in range(L):
        i=(start+k)%L
        if inH[i]: cur.append(P[i])
        else:
            if cur: ivs.append(cur); cur=[]
    if cur: ivs.append(cur)
    return ivs

HCAP=16
def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    levs=[F(0)]+sorted(set(v for v in T if v>0))
    for j in range(len(levs)-1):
        a=levs[j]; b=levs[j+1]
        if 2*b>n: continue
        H=[v for v in range(n) if T[v]>a]
        if not H: continue
        h=len(H)
        if h>HCAP: acc['skipped']+=1; continue
        Hset=set(H); idx={v:i for i,v in enumerate(H)}
        OH=set(v for v in H if T[v]>n)
        # intervals as bitmask over H, plus weight, plus O-members bitmask
        ivs=[]
        for f in M:
            w=F(ell[f],len(cyc[f]))
            for P in cyc[f]:
                for I in cyclic_intervals(P,Hset):
                    Im=0; Om=0
                    for v in I:
                        Im|=(1<<idx[v])
                        if v in OH: Om|=(1<<idx[v])
                    ivs.append((w,Im,Om))
        exc=[T[v]-F(n) for v in H]   # per-H-vertex excess
        acc['nb']+=1
        for Zm in range(1,1<<h):
            ex=F(0)
            zb=Zm
            i=0
            while zb:
                if zb&1: ex+=exc[i]
                zb>>=1; i+=1
            if ex<=0: continue
            exo=F(0)
            for (w,Im,Om) in ivs:
                if Im & ~Zm:   # I not subset of Z (has a bit outside Z)
                    cnt=bin(Om & Zm).count('1')
                    if cnt: exo+=w*cnt
            m=exo-ex
            if m<acc['minm'][0]: acc['minm']=(m,name,n,h)
            if m<0:
                acc['viol']+=1
                if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,h,Zm,str(ex),str(exo))
                return

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
    acc={'nb':0,'viol':0,'skipped':0,'first':None,'minm':(F(10**18),'','','')}
    for c in (5,7,9):
        for t in range(1,5):
            n,E=blowup([t]*c)
            if n>24: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>24: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(nm,nn,adj,s,acc)
    print("  structured: viol=%d skipped(h>%d)=%d"%(acc['viol'],HCAP,acc['skipped']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    print("\n  bands tested(h<=%d)=%d  skipped(h>cap)=%d  SCEB violations=%d"%(HCAP,acc['nb'],acc['skipped'],acc['viol']),flush=True)
    print("  MIN margin = %s at %s"%(float(acc['minm'][0]),acc['minm'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === SCEB %s (h>cap bands covered by verified LBCT) ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
