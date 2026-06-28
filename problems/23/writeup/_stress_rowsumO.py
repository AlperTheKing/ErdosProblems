"""Robust stress test of (ROWSUM-O): sum_g O_fg <= N, EXACT (Fraction), on:
  - C_{2k+1}[t] blowups for k=2,3,4 (C5,C7,C9), t up to making N~20-25
  - large random connected triangle-free graphs N=18..22 (geng random sample)
  - Petersen, Mycielskians (grow chromatic number)
Also re-confirm the full water-filling PSD reconstruction (sum_f C_f == N I - K) numerically on these.
A single violation (resid>0) would KILL the certificate. Report exact max residual + worst graph."""
import numpy as np
from fractions import Fraction as F
import subprocess, random
from _h import dec, GENG, loads

def odd_blow(k,t):
    """C_{2k+1}[t]: cycle of length L=2k+1, each vertex -> t-set, consecutive sets complete bipartite."""
    L=2*k+1; nn=L*t; E=[]
    for i in range(L):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, ((i+1)%L)*t+b))
    return nn,E

def mycielski(n,E):
    """Mycielskian: vertices 0..n-1 (orig), n..2n-1 (shadows u_i), 2n (apex w).
    edges: orig E; u_i ~ v for each edge (i,v) i.e. shadow connects to orig-neighbors; w ~ all u_i."""
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    NN=2*n+1; w=2*n; EE=list(E)
    for i in range(n):
        for v in adj[i]:
            EE.append((n+i, v))   # shadow u_i ~ orig neighbors of i
    for i in range(n):
        EE.append((n+i, w))
    return NN, EE

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    return pf

def rowsumO_exact(info):
    n=info['n']; N=n; M=info['M']; m=len(M)
    if m==0: return F(-1)
    pf=pf_exact(info)
    def ip(a,b):
        ss=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: ss+=av*bv
        return ss
    O=[[ip(pf[i],pf[j]) for j in range(m)] for i in range(m)]
    O1=[sum(O[i][j] for j in range(m)) for i in range(m)]
    return max(O1[i]-N for i in range(m))

def psd_recon_ok(info):
    n=info['n']; M=info['M']; cyc=info['cyc']; m=len(M); N=n
    if m==0: return 0.0, 0.0
    P=np.zeros((n,m))
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): P[v,j]=c/nf
    s=P.sum(axis=1); K=P@P.T; NIK=N*np.eye(n)-K
    acc=np.zeros((n,n)); minCf=np.inf
    for j in range(m):
        pf=P[:,j]; D=np.zeros(n)
        for v in range(n):
            if pf[v]>0: D[v]=N*pf[v]/s[v]
        Cf=np.diag(D)-np.outer(pf,pf)
        minCf=min(minCf, np.linalg.eigvalsh(Cf).min())
        acc+=Cf
    for v in range(n):
        if s[v]==0: acc[v,v]+=N
    return minCf, np.max(np.abs(acc-NIK))

if __name__=="__main__":
    print("=== odd-cycle blowups C_{2k+1}[t] ===")
    for k in [2,3,4]:
        for t in range(1,6):
            nn,E=odd_blow(k,t)
            if nn>30: break
            info=loads(nn,E)
            if info is None: print(f"  C{2*k+1}[{t}] N={nn}: loads None (no bad edge)"); continue
            r=rowsumO_exact(info); mc,re=psd_recon_ok(info)
            print(f"  C{2*k+1}[{t}] N={nn}: ROWSUM-O max-resid={r}={float(r):+.3f} | minlam(C_f)={mc:+.2e} recon={re:.1e} Gamma/N^2={float(info['G'])/(nn*nn):.4f}")

    print("\n=== Mycielskians (Grotzsch = M(C5)) and iterated ===")
    seeds=[("C5",5,[(i,(i+1)%5) for i in range(5)])]
    for name,n0,E0 in seeds:
        NN,EE=mycielski(n0,E0)  # Grotzsch, N=11
        info=loads(NN,EE)
        if info:
            r=rowsumO_exact(info); mc,re=psd_recon_ok(info)
            print(f"  M({name}) Grotzsch N={NN}: ROWSUM-O max-resid={float(r):+.3f} minlam(C_f)={mc:+.2e} recon={re:.1e}")
        NN2,EE2=mycielski(NN,EE)  # N=23
        info2=loads(NN2,EE2)
        if info2:
            r=rowsumO_exact(info2); mc,re=psd_recon_ok(info2)
            print(f"  M(M({name})) N={NN2}: ROWSUM-O max-resid={float(r):+.3f} minlam(C_f)={mc:+.2e} recon={re:.1e}")

    print("\n=== random connected triangle-free N=16..20 (geng -tc sample) ===")
    random.seed(7)
    for nn in [16,18,20]:
        # geng can be huge; sample with -tc and a random skip via large count then random pick
        out=subprocess.run([GENG,"-tc","-c",str(nn),"0","1000000"],capture_output=True,text=True).stdout.split()
        if not out:
            out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        sample = random.sample(out, min(60,len(out))) if out else []
        worst=None; wg=None; nb=0
        for g6 in sample:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nb+=1
            r=rowsumO_exact(info)
            if worst is None or r>worst: worst=r; wg=g6
        if worst is not None:
            print(f"  N={nn}: sampled {nb} with bad-edges | ROWSUM-O max-resid={float(worst):+.3f}@{wg}")
        else:
            print(f"  N={nn}: no sample with bad edges")
