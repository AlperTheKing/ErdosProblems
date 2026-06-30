"""EXACT gate of Codex block-287 component-share dominance: for every high negative band j (2t_j>=N, B_j<0)
and every K-component C:  |H_j cap C| * A_pre <= |H_j| * A_pre(C).  (=> D_C <= (A_pre(C)/A_pre) W_neg, so global
BRIDGE-A coef c gives component coef c.) Full battery; report viol + first witness."""
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
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]; comps=sorted(set(cid))
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    # A_pre and A_pre(C)
    Apre=F(0); ApreC={c:F(0) for c in comps}
    highnegbands=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
        cnt={c:0 for c in comps}
        for v in H: cnt[cid[v]]+=1
        if 2*tj<F(n):
            coef=wj*(F(n)+eta-tj-tn)
            Apre+=coef*h
            for c in comps: ApreC[c]+=coef*cnt[c]
        else:
            Bj=wj*(25*(F(n)+eta-tj-tn)*h - F(n)*sig)
            if Bj<0: highnegbands.append((h,cnt))
    for (h,cnt) in highnegbands:
        for c in comps:
            acc['rows']+=1
            # |H_j cap C| * A_pre <= |H_j| * A_pre(C)
            if cnt[c]*Apre > h*ApreC[c]:
                acc['viol']+=1
                if acc['first'] is None: acc['first']=(name,n,m,c,cnt[c],h,str(Apre),str(ApreC[c]))

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
    acc={'rows':0,'viol':0,'first':None}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d"%acc['viol'],flush=True)
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
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol=%d)"%(nn,acc['viol']),flush=True)
    print("\n  rows=%d  COMPONENT-SHARE-DOMINANCE violations=%d"%(acc['rows'],acc['viol']),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === COMPONENT-SHARE-DOMINANCE %s ==="%("HOLDS => global BRIDGE-A coef c gives component coef c" if not acc['viol'] else "FAILS"),flush=True)
