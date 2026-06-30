"""EXACT gate of Codex block-253 corridor blocks C1, C2 (min-free geodesic blocks for FULL-LOW-INTERNAL).
For every full-low band [a,b] with 2*b<=N, H={v:T>a}, h=|H|, L=V\\H, Gamma=sum ell^2, Lambda=sum ell.
q_H(x,y) for x in H, y in L: 0 if cut edge, 2 if bad edge, 1 if nonedge.
  C1: W_out + h*T(H) + 2*h*Lambda >= h*Gamma,  W_out=sum_{x in H,y in L} q*T(y).
  C2: W_in >= (N-h)*(T(H)-2*Lambda),           W_in =sum_{x in H,y in L} q*T(x).
Full battery; report viol + min margin each."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    badset=set((min(a,b),max(a,b)) for a,b in M)
    Gamma=sum(ell[f]**2 for f in M); Lam=sum(ell[f] for f in M)
    levs=[F(0)]+sorted(set(v for v in T if v>0))
    for j in range(len(levs)-1):
        a=levs[j]; b=levs[j+1]
        if 2*b>n: continue
        H=[v for v in range(n) if T[v]>a]
        if not H: continue
        Hset=set(H); h=len(H); L=[v for v in range(n) if v not in Hset]
        TH=sum(T[v] for v in H)
        Wout=F(0); Win=F(0)
        for x in H:
            for y in L:
                e=(min(x,y),max(x,y))
                if y in adj[x]:
                    q=2 if e in badset else 0   # cut edge if bichromatic; bad if monochromatic
                    # determine cut vs bad: edge present; bad iff same side
                    if side[x]==side[y]: q=2
                    else: q=0
                else:
                    q=1
                if q:
                    Wout+=q*T[y]; Win+=q*T[x]
        m1=Wout + F(h)*TH + 2*F(h)*Lam - F(h)*Gamma
        m2=Win - F(n-h)*(TH-2*Lam)
        acc['nb']+=1
        if m1<acc['m1'][0]: acc['m1']=(m1,name,n,len(M),h)
        if m2<acc['m2'][0]: acc['m2']=(m2,name,n,len(M),h)
        if m1<0:
            acc['v1']+=1
            if acc['f1'] is None: acc['f1']=(name,''.join(map(str,side)),n,h,str(m1))
        if m2<0:
            acc['v2']+=1
            if acc['f2'] is None: acc['f2']=(name,''.join(map(str,side)),n,h,str(m2))

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
    acc={'nb':0,'v1':0,'v2':0,'f1':None,'f2':None,'m1':(F(10**18),'','','',''),'m2':(F(10**18),'','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: v1=%d v2=%d"%(acc['v1'],acc['v2']),flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done (v1=%d v2=%d)"%(acc['v1'],acc['v2']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (v1=%d v2=%d)"%(nn,acc['v1'],acc['v2']),flush=True)
    print("\n  full-low bands=%d"%acc['nb'],flush=True)
    print("  C1 violations=%d  min margin=%s at %s"%(acc['v1'],float(acc['m1'][0]),acc['m1'][1:]),flush=True)
    print("  C2 violations=%d  min margin=%s at %s"%(acc['v2'],float(acc['m2'][0]),acc['m2'][1:]),flush=True)
    if acc['f1']: print("  first C1 viol: %s"%(acc['f1'],),flush=True)
    if acc['f2']: print("  first C2 viol: %s"%(acc['f2'],),flush=True)
    print("  === C1 %s ; C2 %s ==="%("HOLDS" if not acc['v1'] else "FAILS","HOLDS" if not acc['v2'] else "FAILS"),flush=True)
