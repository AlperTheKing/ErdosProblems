"""EXACT gate of Codex block-265 PREHALF-BANK (bank/withdrawal decomposition of PREFIX-LOAD-PSC-25).
Bands: 0=t_0<...<t_r distinct positive T-levels (0 incl), w_j=t_{j+1}-t_j, H_j={T>t_j}, sigma_j=dB-dM, D=N^2-25m.
  B_j = w_j*( D*|H_j| - 25*(2 t_j + w_j - N)*|H_j| - N*sigma_j ).
PREHALF-BANK:  sum_{2 t_j < N} B_j  +  sum_{2 t_j >= N and B_j < 0} B_j  >= 0.
Full battery; report viol + min + first witness."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
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
    m=len(M); D=F(n*n)-25*m
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    bank=F(0)
    for j in range(len(levs)-1):
        tj=levs[j]; wj=levs[j+1]-levs[j]
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
        Bj=wj*(D*h - 25*(2*tj+wj-F(n))*h - F(n)*sig)
        if 2*tj<F(n): bank+=Bj
        elif Bj<0: bank+=Bj
    acc['nb']+=1
    if bank<acc['minm'][0]: acc['minm']=(bank,name,n,m)
    if bank<0:
        acc['viol']+=1
        if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,str(bank))

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
    acc={'nb':0,'viol':0,'first':None,'minm':(F(10**18),'','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d min=%s"%(acc['viol'],float(acc['minm'][0])),flush=True)
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
    print("  blow-ups + Mycielskians + glued done (viol=%d)"%acc['viol'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    print("\n  configs=%d  PREHALF-BANK violations=%d"%(acc['nb'],acc['viol']),flush=True)
    print("  MIN bank = %s at %s"%(float(acc['minm'][0]),acc['minm'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === PREHALF-BANK %s ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
