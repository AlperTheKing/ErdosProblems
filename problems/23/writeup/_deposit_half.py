"""Test the DEPOSIT-HALF sub-lemma of PREFIX-LOAD-PSC: is the per-level net n_j>=0 termwise on the
credit levels?  Split candidates: (a) 2*t_j <= N, (b) 2*t_{j+1} <= N (interval fully in 2s<=N).
n_j = D w_j|H_j| - A_j, D=N^2-25|M|, A_j=25 w_j(2t_j+w_j-N)|H_j| + N w_j sigma_j.
If n_j>=0 on the deposit half, PREFIX reduces to bounding the withdrawals (2t>N) by the banked surplus.
EXACT Fraction. Report first violation in each split + min net in each region."""
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
    for j in range(len(levels)-1):
        tj=levels[j]; wj=levels[j+1]-levels[j]; tnext=levels[j+1]
        Hset=set(v for v in range(n) if T[v]>tj)
        if not Hset: continue
        Hsz=len(Hset); dB,dM=boundary(n,adj,side,Hset); sig=dB-dM
        Aj=25*wj*(2*tj+wj-F(n))*Hsz + F(n)*wj*sig
        nj=D*wj*Hsz-Aj
        netnorm=nj/wj   # per-unit-width net (scale out w_j)
        if 2*tj<=n:   # split (a): t_j in credit region
            acc['na']+=1
            if netnorm<acc['mina'][0]: acc['mina']=(netnorm,name,n,m,str(tj))
            if nj<0:
                acc['va']+=1
                if acc['fa'] is None: acc['fa']=(name,n,m,str(tj),str(wj),Hsz,sig,float(nj))
        if 2*tnext<=n:  # split (b): whole interval in credit region 2s<=N
            acc['nb']+=1
            if netnorm<acc['minb'][0]: acc['minb']=(netnorm,name,n,m,str(tj))
            if nj<0:
                acc['vb']+=1
                if acc['fb'] is None: acc['fb']=(name,n,m,str(tj),str(wj),Hsz,sig,float(nj))

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
    acc={'na':0,'nb':0,'va':0,'vb':0,'fa':None,'fb':None,
         'mina':(F(10**18),'','','',''),'minb':(F(10**18),'','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); analyze("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (va=%d vb=%d)"%(nn,acc['va'],acc['vb']),flush=True)
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
    print("\n  SPLIT (a) 2 t_j <= N: levels=%d  violations(n_j<0)=%d  min net/w=%s at %s"%(acc['na'],acc['va'],float(acc['mina'][0]),acc['mina'][1:]),flush=True)
    if acc['fa']: print("    first (a) viol: %s"%(acc['fa'],),flush=True)
    print("  SPLIT (b) 2 t_{j+1} <= N: levels=%d  violations(n_j<0)=%d  min net/w=%s at %s"%(acc['nb'],acc['vb'],float(acc['minb'][0]),acc['minb'][1:]),flush=True)
    if acc['fb']: print("    first (b) viol: %s"%(acc['fb'],),flush=True)
    print("  === DEPOSIT-HALF (a) %s ; (b) %s ==="%("HOLDS termwise" if not acc['va'] else "FAILS","HOLDS termwise" if not acc['vb'] else "FAILS"),flush=True)
