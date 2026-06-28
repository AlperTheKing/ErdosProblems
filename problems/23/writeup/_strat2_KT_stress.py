"""STRESS the Collatz-Wielandt certificate  (K d)_v <= N d_v for d=T and d=S, EXACTLY.
If true for all v on all tri-free graphs => rho(K) <= N (since K>=0 entrywise, Collatz-Wielandt)
=> N*I-K PSD => sum_v T^2 = ell^T O ell <= N*Gamma => Gamma <= N^2.  THIS IS A REAL CERTIFICATE.

Test on the hardest known cases: large C(2k+1) blowups (N up to ~24 via direct B-side construction,
NO maxcut search needed -- blowup of an odd cycle: the unique max cut is the cycle bipartition-ish),
Mycielskians, Grotzsch, the N=22 sandwich-killer witness, random tri-free, AND census N<=11.
Reports max_v (Kd)_v/(N d_v) - want <= 1 (=1 at extremals)."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads

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
    return n,N,K,T,S

def cw_max(K,d,n,N):
    """max_v (Kd)_v/(N d_v); skip v with d_v=0 (must then have (Kd)_v=0)."""
    best=F(0); bv=None; incompat=False
    for v in range(n):
        kd=sum(K[v][w]*d[w] for w in range(n))
        if d[v]==0:
            if kd!=0: incompat=True
            continue
        r=kd/(F(N)*d[v])
        if r>best: best=r; bv=v
    return best, bv, incompat

def test_g6(g6, t=1):
    n0,E0=dec(g6)
    if t>1:
        n=n0*t; E=[]
        for (a,b) in E0:
            for i in range(t):
                for j in range(t): E.append((a*t+i,b*t+j))
    else:
        n,E=n0,E0
    info=loads(n,E)
    if info is None: return None
    n,N,K,T,S=build(info)
    rT,vT,iT=cw_max(K,T,n,N)
    rS,vS,iS=cw_max(K,S,n,N)
    return dict(N=N,rT=rT,rS=rS,iT=iT,iS=iS,vT=vT)

# ---- direct odd-cycle blowup (no maxcut search; B = the cycle bipartition cross-edges) ----
def cycle_blowup_info(L, q):
    """C_L[q]: L parts of size q in a ring; build info dict directly with the canonical max cut
    = alternate the ring? For odd L there's no bipartition; max cut here we just defer to loads()."""
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

def run():
    print("=== EXACT Collatz-Wielandt cert (Kd)_v <= N d_v, d=T and d=S ===")
    print("--- census N=7..11 ---")
    worstT=F(0);wgT=None; worstS=F(0);wgS=None; failT=0;failS=0;ng=0
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            r=test_g6(g6)
            if r is None: continue
            ng+=1
            if r['iT'] or r['rT']>1: failT+=1
            if r['iS'] or r['rS']>1: failS+=1
            if r['rT']>worstT: worstT=r['rT']; wgT=(g6,nn)
            if r['rS']>worstS: worstS=r['rS']; wgS=(g6,nn)
    print(f"  census graphs={ng}: d=T fails:{failT} worst={float(worstT):.5f}@{wgT} | d=S fails:{failS} worst={float(worstS):.5f}@{wgS}")

    print("--- odd-cycle blowups C_L[q], N up to ~24 ---")
    for L in [5,7,9]:
        for q in range(1,6):
            nn=L*q
            if nn>26: continue
            n,E=cycle_blowup_info(L,q)
            info=loads(n,E)
            if info is None: print(f"  C{L}[{q}] N={nn}: loads None (maxcut?)"); continue
            n,N,K,T,S=build(info)
            rT,vT,iT=cw_max(K,T,n,N); rS,vS,iS=cw_max(K,S,n,N)
            print(f"  C{L}[{q}] N={nn}: d=T max={float(rT):.5f}(incompat={iT}) d=S max={float(rS):.5f}")

    print("--- named witnesses + blowups ---")
    named=[("J???E?pNu\\?",2,"N22-killer x2"),("J???E?pNu\\?",1,"N22-killer"),
           ("J?AEB?oE?W?",2,"tightN11x2"),("H?bB@_W",3,"tightN9x3"),
           ("I?rFf_{N?",2,"tightN10x2")]
    for g6,t,nm in named:
        r=test_g6(g6,t)
        if r is None: print(f"  {nm}: loads None"); continue
        print(f"  {nm} N={r['N']}: d=T max={float(r['rT']):.5f}(incompat={r['iT']}) d=S max={float(r['rS']):.5f}(incompat={r['iS']})")

if __name__=="__main__":
    run()
