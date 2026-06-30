"""EXACT gate of Codex block-275 PREHALF bridges. Bands as PREHALF. eta=N^2/25-m.
  A_j = w_j*(N+eta-t_j-t_{j+1})*|H_j| ;  B_j = 25*A_j - N*w_j*sigma_j.
  Jpre={j:2 t_j<N}; A_pre=sum_Jpre A_j; P_pre=5 A_pre - N sum_Jpre w_j sigma_j; W_neg=sum_{2t_j>=N,B_j<0}(-B_j).
  (BRIDGE-A)  W_neg <= 20*A_pre.      (BRIDGE-P)  W_neg <= P_pre.
Full battery; report viol + first witness each."""
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
    m=len(M); eta=F(n*n,25)-m
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    A_pre=F(0); wsig_pre=F(0); W_neg=F(0)
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
        Aj=wj*(F(n)+eta-tj-tn)*h
        Bj=25*Aj-F(n)*wj*sig
        if 2*tj<F(n):
            A_pre+=Aj; wsig_pre+=wj*sig
        elif Bj<0:
            W_neg+=(-Bj)
    P_pre=5*A_pre-F(n)*wsig_pre
    acc['nb']+=1
    mA=20*A_pre-W_neg; mP=P_pre-W_neg
    if mA<acc['mA'][0]: acc['mA']=(mA,name,n,m)
    if mP<acc['mP'][0]: acc['mP']=(mP,name,n,m)
    if mA<0:
        acc['vA']+=1
        if acc['fA'] is None: acc['fA']=(name,''.join(map(str,side)),n,m,str(A_pre),str(P_pre),str(W_neg))
    if mP<0:
        acc['vP']+=1
        if acc['fP'] is None: acc['fP']=(name,''.join(map(str,side)),n,m,str(A_pre),str(P_pre),str(W_neg))

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
    acc={'nb':0,'vA':0,'vP':0,'fA':None,'fP':None,'mA':(F(10**18),'','',''),'mP':(F(10**18),'','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: vA=%d vP=%d"%(acc['vA'],acc['vP']),flush=True)
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
    print("  blow-ups + Mycielskians + glued done (vA=%d vP=%d)"%(acc['vA'],acc['vP']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (vA=%d vP=%d)"%(nn,acc['vA'],acc['vP']),flush=True)
    print("\n  configs=%d"%acc['nb'],flush=True)
    print("  BRIDGE-A (W_neg<=20*A_pre): viol=%d min margin=%s at %s"%(acc['vA'],float(acc['mA'][0]),acc['mA'][1:]),flush=True)
    if acc['fA']: print("    first A viol: %s"%(acc['fA'],),flush=True)
    print("  BRIDGE-P (W_neg<=P_pre): viol=%d min margin=%s at %s"%(acc['vP'],float(acc['mP'][0]),acc['mP'][1:]),flush=True)
    if acc['fP']: print("    first P viol: %s"%(acc['fP'],),flush=True)
    print("  === BRIDGE-A %s ; BRIDGE-P %s ==="%("HOLDS=>PREHALF from P_pre>=0" if not acc['vA'] else "FAILS","HOLDS" if not acc['vP'] else "FAILS"),flush=True)
