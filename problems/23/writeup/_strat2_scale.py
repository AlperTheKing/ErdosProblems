"""STRATEGY 2 probe: similarity-transformed row-sum certificates for N*I - K PSD.
N*I-K PSD <=> rho(K)<=N (K PSD). Try D-scaled Gershgorin/row-sum: for diagonal D>0,
  rho(K) = rho(D^{-1/2} K D^{-1/2}) <= max_v (1/sqrt(D_v)) sum_w K_vw sqrt(D_w)   [row sum of scaled K]
If this <= N for some manifest D (D=T, D=S, D=1...) we get rho(K)<=N MANIFESTLY (Gershgorin/Perron on nonneg K).
Recall K>=0 entrywise so rho(K) <= max_v (1/d_v) sum_w K_vw d_w for ANY positive vector d (Collatz-Wielandt).
So: EXISTS positive d with (K d)_v <= N d_v for all v  <=>  rho(K) <= N  (Perron-Frobenius, since K>=0 irreducible-ish).
The cert is the PERRON eigenvector. Question: is there a STRUCTURAL d (T, S, ell-weighted...) that works census-wide?
Test candidates d and report max_v (Kd)_v / d_v (want <= N)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, blow

def build(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']; m=len(M)
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    K=[[F(0)]*n for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items():
                K[v][w]+=pv*pw
    T=[sum(ell[M[g]]*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    S=[sum(pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    return n,N,K,T,S,pf

def cw_ratio(K,d,n):
    """max_v (Kd)_v / d_v ; if all d_v>0. returns (maxratio, argv)."""
    best=None; bv=None
    for v in range(n):
        if d[v]==0:
            # (Kd)_v must be 0 for ratio to be defined; if not, infinite
            kd=sum(K[v][w]*d[w] for w in range(n))
            if kd!=0: return None, v
            continue
        kd=sum(K[v][w]*d[w] for w in range(n))
        r=kd/d[v]
        if best is None or r>best: best=r; bv=v
    return best, bv

def run(nmin,nmax,limit=None):
    print(f"=== Collatz-Wielandt structural-d census N={nmin}..{nmax} ===")
    # candidates: d=1 (rowsum=T), d=T, d=S, d=sqrt? (no, keep rational): d=T^2, d=S*?, d=T+ something
    names=['d=1','d=T','d=S','d=T2','d=S2','d=TS']
    worst={nm:(F(0),None) for nm in names}
    fails={nm:0 for nm in names}; ng=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            n,N,K,T,S,pf=build(info)
            cand={'d=1':[F(1)]*n,'d=T':T,'d=S':S,'d=T2':[t*t for t in T],
                  'd=S2':[s*s for s in S],'d=TS':[T[v]*S[v] for v in range(n)]}
            for nm,d in cand.items():
                r,v=cw_ratio(K,d,n)
                if r is None:
                    fails[nm]+=1; continue
                if r>F(N): fails[nm]+=1
                ratio=r/F(N)
                if ratio>worst[nm][0]: worst[nm]=(ratio,(g6,v,str(r),N))
    print(f"graphs={ng}")
    for nm in names:
        wr,wg=worst[nm]
        print(f"  {nm:6s}: fails(max(Kd/d)>N or d=0-incompat):{fails[nm]:4d} | worst max_v(Kd)_v/(N d_v)={float(wr):.5f} @ {wg}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups (extremal) ===")
    for t in range(1,7):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        n,N,K,T,S,pf=build(info)
        cand={'d=1':[F(1)]*n,'d=T':T,'d=S':S}
        for nm,d in cand.items():
            r,v=cw_ratio(K,d,n)
            print(f"  C5[{t}] N={n} {nm}: max(Kd/d)={float(r):.4f} (N={n})")
