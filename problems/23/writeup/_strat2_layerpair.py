"""For A = sum_i L_i(f) <= N*ell(f), L_i(f)=sum_{v in I_i(f)} p_f(v) T_v (per-layer load mass).
Per-layer L_i<=N FAILS. Test weaker partial-sum/pairing structures that still imply A:
 (P1) symmetric pair: L_i + L_{h-i} <= 2N  for all i (h=ell(f)-1). avg of pair <=N. SUM over pairs = A.
 (P2) prefix/balanced: is there a 'discharging' where endpoints layers (small T) offset middle (large T)?
      Test running-average: for the multiset {L_i}, does sorting + pairing extremes give <=N each pair?
 (P3) endpoint law: L_0+L_h <= 2N? (layers 0,h are single vertices a,b with p_f=1; L_0=T_a,L_h=T_b).
 (P4) Just measure: count layers with L_i>N and by how much; is total excess <= total deficit (=A)?
EXACT census + blowups + N22 killer."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info,f):
    Ps=info['cyc'][f]; nf=len(Ps); cnt={}
    for P in Ps:
        for v in P: cnt[v]=cnt.get(v,0)+1
    return {v:F(cnt[v],nf) for v in cnt}

def bdist(info,s):
    adj=info['adj']; side=info['side']; d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def layers_of(info,f,T):
    a,b=f; h=info['ell'][f]-1
    da=bdist(info,a); db=bdist(info,b); pf=pf_vec(info,f)
    L=[F(0)]*(h+1)
    for v in pf:
        if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h:
            L[da[v]]+=pf[v]*T[v]
    return L,h

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    T={v:sum(ell[g]*pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    p1f=0;p1m=F(0); p3f=0;p3m=F(0); pairsort_f=0; pairsort_m=F(0)
    for f in M:
        L,h=layers_of(info,f,T)
        # P1 symmetric pair <=2N
        for i in range((h+2)//2):
            j=h-i
            pair=L[i]+L[j] if i!=j else 2*L[i]
            if pair>2*F(N): p1f+=1
            r=pair/(2*F(N))
            if r>p1m: p1m=r
        # P3 endpoints
        ep=L[0]+L[h]
        if ep>2*F(N): p3f+=1
        if ep/(2*F(N))>p3m: p3m=ep/(2*F(N))
        # P2 sorted extreme-pairing: sort L, pair smallest with largest, each pair <=2N?
        Ls=sorted(L); i,j=0,len(Ls)-1
        while i<j:
            pr=Ls[i]+Ls[j]
            if pr>2*F(N): pairsort_f+=1
            if pr/(2*F(N))>pairsort_m: pairsort_m=pr/(2*F(N))
            i+=1; j-=1
    return p1f,p1m,p3f,p3m,pairsort_f,pairsort_m

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

def run():
    P1f=0;P1m=F(0);P1g=None;P3f=0;P3m=F(0);PSf=0;PSm=F(0);PSg=None;ng=0
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            a1,m1,a3,m3,aps,mps=analyze(info)
            P1f+=a1; P3f+=a3; PSf+=aps
            if m1>P1m: P1m=m1; P1g=(g6,nn)
            if m3>P3m: P3m=m3
            if mps>PSm: PSm=mps; PSg=(g6,nn)
    print(f"=== layer-pairing tests for A, census graphs={ng} ===")
    print(f"  P1 sym-pair L_i+L_(h-i)<=2N: fail={P1f} worst/2N={float(P1m):.5f}@{P1g}")
    print(f"  P3 endpoints  L_0+L_h<=2N : fail={P3f} worst/2N={float(P3m):.5f}")
    print(f"  P2 sorted-extreme-pairing  : fail={PSf} worst/2N={float(PSm):.5f}@{PSg}")

if __name__=="__main__":
    run()
    print("--- N22 killer + blowups ---")
    for g6 in ["J???E?pNu\\?"]:
        n,E=dec(g6); info=loads(n,E)
        if info:
            a1,m1,a3,m3,aps,mps=analyze(info)
            print(f"  {g6} N={n}: P1 fail={a1} worst/2N={float(m1):.4f} | P2 fail={aps} worst/2N={float(mps):.4f}")
    for L,q in [(5,3),(7,2)]:
        nn=L*q; n,E=cycle_blowup(L,q); info=loads(n,E)
        if info:
            a1,m1,a3,m3,aps,mps=analyze(info)
            print(f"  C{L}[{q}] N={nn}: P1 worst/2N={float(m1):.4f} P2 worst/2N={float(mps):.4f}")
