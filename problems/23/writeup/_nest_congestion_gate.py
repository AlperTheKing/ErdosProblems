"""Exact-test the GPT-Pro NEST proposal + its bundle-proof crux (unit edge congestion).
(A) NEST: for all nested B<=A<=M, <S_A,S_B> = sum_{f in A,g in B} O[f,g] <= N|B|. CLAIM equivalent to ROWSUM-O
    (since S_A<=S_M pointwise => <S_A,S_B> <= sum_{g in B} ROWSUM(g)). Test NEST-FAIL vs ROWSUM-FAIL: expect equal.
(B) UNIT EDGE CONGESTION W(x,y)=sum_{f in M}(frac of f-geodesics using edge xy) <= 1 for every edge -- the
    generalized min-product, the crux of the proposed BUNDLE-MAVG proof. Expect FAILURE at nested-unique-path
    rows (e.g. K??CB@OBDOAp edge (4,9) carries 2). Report max congestion + where it fails.
Census N<=11 + N=12 witnesses + structured. Exact Fraction."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def analyze(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    M=list(M)
    # p_f vectors and O Gram
    pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    # O[f,g]=<p_f,p_g>
    O={}
    for f in M:
        for g in M:
            df=pf[f]; dg=pf[g]
            O[(f,g)]=sum(df[v]*dg.get(v,F(0)) for v in df)
    rowsum={f: sum(O[(f,g)] for g in M) for f in M}
    rowsumO_fail = any(rowsum[f] > n for f in M)
    # NEST over nested pairs (cap |M| to keep 3^|M| sane; if too big, test A=M slice which dominates)
    nest_fail=False
    if len(M)<=9:
        idx=list(range(len(M)))
        for ra in range(1,len(M)+1):
            for A in itertools.combinations(idx,ra):
                Aset=[M[i] for i in A]
                for rb in range(1,ra+1):
                    for B in itertools.combinations(A,rb):
                        Bset=[M[i] for i in B]
                        val=sum(O[(M[i],M[j])] for i in A for j in B)
                        if val > F(n)*len(Bset): nest_fail=True; break
                    if nest_fail: break
            if nest_fail: break
    else:
        # dominating slice A=M: sum_{g in B} rowsum[g] <= N|B| <=> rowsum<=N each
        nest_fail = rowsumO_fail
    # edge congestion W(x,y) = sum_f frac of f-geodesics using edge (x,y)
    W={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for P in Ps:
            for i in range(len(P)-1):
                e=(min(P[i],P[i+1]),max(P[i],P[i+1]))
                W[e]=W.get(e,F(0))+F(1,k)
    maxW = max(W.values()) if W else F(0)
    cong_fail = maxW > 1
    return rowsumO_fail, nest_fail, cong_fail, maxW

def run(name,n,E):
    adj,cuts=gmins(n,E)
    rf=nf=cf=0; mx=F(0); cong_wit=None
    for s in cuts:
        r=analyze(n,adj,s)
        if r is None: continue
        rowsumO_fail,nest_fail,cong_fail,maxW=r
        rf+=rowsumO_fail; nf+=nest_fail; cf+=cong_fail
        if maxW>mx: mx=maxW; cong_wit=''.join(map(str,s))
    return name,len(cuts),rf,nf,cf,mx,cong_wit

if __name__=="__main__":
    print("=== NEST vs ROWSUM-O (equivalence) + UNIT EDGE CONGESTION W<=1 (exact) ===",flush=True)
    print("  census: N cuts rowsumO-FAIL NEST-FAIL CONG-FAIL maxW",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        T=rf=nf=cf=0; mx=F(0)
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                r=analyze(n,adj,s)
                if r is None: continue
                T+=1; a,b,c,w=r; rf+=a; nf+=b; cf+=c
                if w>mx: mx=w
        print(f"  N={nn}: cuts={T} rowsumO-FAIL={rf} NEST-FAIL={nf} CONG-FAIL={cf} maxW={mx}={float(mx):.3f}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp(nested)",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc(bandkill)",)+dec("K??CE@A{?]Fc"),
           ("GDSKVG",)+dec("GDSKVG"),
           ("Grotzsch",)+mycielski(5,Cn(5)),
           ("M(C7)",)+mycielski(7,Cn(7)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)]
    print("  [witnesses/structured]: name cuts rowsumO-FAIL NEST-FAIL CONG-FAIL maxW wit",flush=True)
    for it in extra:
        print("   ",run(*it),flush=True)
