"""Diagnostic on PREFIX-LOAD-PSC structure (does it bite harder than the full sum?).
Per config record: full_sum S_r, min_prefix min_k S_k, GAP=S_r-min_prefix (>0 => prefix binds strictly),
and whether per-level net n_j is non-increasing (=> S_k concave => PREFIX <=> S_r>=0 + monotone).
EXACT Fraction. Battery = same as _prefix_loadpsc_gate."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary(n,adj,side,Hset):
    dB=dM=0
    for u in Hset:
        for v in adj[u]:
            if v in Hset: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def analyze(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); D=F(n*n)-25*m
    levels=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    nets=[]
    for j in range(len(levels)-1):
        tj=levels[j]; wj=levels[j+1]-levels[j]
        Hset=set(v for v in range(n) if T[v]>tj)
        if not Hset: continue
        Hsz=len(Hset); dB,dM=boundary(n,adj,side,Hset); sig=dB-dM
        Aj=25*wj*(2*tj+wj-F(n))*Hsz + F(n)*wj*sig
        nets.append(D*wj*Hsz-Aj)
    if not nets: return
    pref=[]; s=F(0)
    for x in nets: s+=x; pref.append(s)
    full=pref[-1]; minp=min(pref); gap=full-minp
    mono = all(nets[i+1]<=nets[i] for i in range(len(nets)-1))
    acc['n']+=1
    if gap>acc['maxgap'][0]: acc['maxgap']=(gap,name,n,m,len(nets))
    if minp<acc['minpref'][0]: acc['minpref']=(minp,name,n,m)
    if not mono:
        acc['nonmono']+=1
        if acc['firstnm'] is None: acc['firstnm']=(name,n,m,len(nets),[float(x) for x in nets])
    else: acc['mono']+=1

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

if __name__=="__main__":
    acc={'n':0,'mono':0,'nonmono':0,'firstnm':None,
         'maxgap':(F(-1),'','','',''),'minpref':(F(10**18),'','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); analyze("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (nonmono so far=%d)"%(nn,acc['nonmono']),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): analyze("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: analyze(name,nn,adj,s,acc)
    print("\n  configs=%d  per-level-net non-increasing: %d / non-monotone: %d"%(acc['n'],acc['mono'],acc['nonmono']),flush=True)
    print("  MIN prefix sum = %s at %s"%(float(acc['minpref'][0]),acc['minpref'][1:]),flush=True)
    print("  MAX gap (full_sum - min_prefix) = %s at %s"%(float(acc['maxgap'][0]),acc['maxgap'][1:]),flush=True)
    if acc['firstnm']: print("  first non-monotone net seq: %s"%(acc['firstnm'],),flush=True)
    print("  INTERPRETATION: gap==0 everywhere => PREFIX <=> LOAD-PSC-25 (prefix never binds strictly);",flush=True)
    print("                  non-increasing nets => S_k concave => PREFIX reduces to LOAD-PSC-25 + level-monotone.",flush=True)
