"""EXACT gate of Codex block-240 LOW-XSLACK (strengthened c=25 deposit-half sublemma).
For every full-low band [a,b]=[t_j,t_{j+1}] with 2*b<=N, H={v:T(v)>a}, h=|H|, dm=delta_M(H),
non(H)=#nonedges across cut (H,V\H) in full G:
   N*(non(H)+2*dm) >= h*(25|M| - N*h).      (LOW-XSLACK)
Algebraically equivalent to  h*(N^2-25|M|) >= N*sigma(H),  sigma=delta_B-delta_M (I verify both forms agree).
=> deposit half (which has extra +25(N-a-b)>=0 credit). Full battery; report violations + min margin + the
agreement check."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary_counts(n,adj,side,H):
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
    m=len(M); D=n*n-25*m
    levs=sorted(set(v for v in T if v>0))
    levs=[F(0)]+levs
    for j in range(len(levs)-1):
        a=levs[j]; b=levs[j+1]
        if 2*b>n: continue                      # full-low band only
        H=set(v for v in range(n) if T[v]>a)
        if not H: continue
        h=len(H); dB,dM=boundary_counts(n,adj,side,H); sig=dB-dM
        # edges across cut (H, V\H): dB+dM ; non-edges across = h(N-h)-(dB+dM)
        non=h*(n-h)-(dB+dM)
        lhsC=F(n)*(non+2*dM); rhsC=h*(25*m-n*h)      # Codex form
        marginC=lhsC-rhsC
        marginAlt=F(h)*D-F(n)*sig                      # equivalent form h*D - N*sigma
        if marginC!=marginAlt: acc['mismatch']+=1
        acc['nb']+=1
        if marginC<acc['minm'][0]: acc['minm']=(marginC,name,n,m,h,dM,non,str(a),str(b))
        if marginC<0:
            acc['viol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,h,dM,non,str(a),str(b),str(marginC))

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
    acc={'nb':0,'viol':0,'mismatch':0,'first':None,'minm':(F(10**18),'','','','','','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d mismatch=%d minm=%s"%(acc['viol'],acc['mismatch'],float(acc['minm'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
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
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                        ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  full-low bands tested=%d  LOW-XSLACK violations=%d  form-mismatch=%d"%(acc['nb'],acc['viol'],acc['mismatch']),flush=True)
    print("  MIN margin = %s at (name,N,|M|,h,dm,non,a,b)=%s"%(float(acc['minm'][0]),acc['minm'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === LOW-XSLACK %s (forms agree: %s) ==="%("HOLDS" if not acc['viol'] else "FAILS","yes" if not acc['mismatch'] else "NO"),flush=True)
