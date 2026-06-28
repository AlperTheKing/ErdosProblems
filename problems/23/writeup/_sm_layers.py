"""Stronger/cleaner forms of (Cycle-SM), all => Gamma<=N^2:
 (Layer-SM)  per geodesic layer I_i(f)={v:d_B(a,v)=i,d_B(v,b)=h-i}: sum_{v in I_i} p_f(v) T(v) <= N.
             (since sum_{v in I_i} p_f(v)=1, this is 'layer-average load <= N'.)  Strongest/cleanest.
 (Cycle-A)   per individual shortest cycle C of f:  sum_{v in C} T(v) <= N*ell(f).
Both => (Cycle-SM) => (SM) => Gamma<=N^2. Test census N<=11 exact; report violations + tightness."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from collections import deque

def layers_of(info,f):
    """I_i(f): partition geodesic vertices by (d_B from a). Returns dict i->set, and p_f(v)."""
    a,b=f; n=info['n']; adj=info['adj']; side=info['side']
    # B-distance from a
    da={a:0}; q=deque([a])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if side[x]!=side[y] and y not in da: da[y]=da[x]+1; q.append(y)
    Ps=info['cyc'][f]; nf=len(Ps); ell=info['ell'][f]
    cnt={}
    for P in Ps:
        for v in P: cnt[v]=cnt.get(v,0)+1
    pf={v:F(c,nf) for v,c in cnt.items()}
    lay={}
    for v in pf:
        i=da[v]; lay.setdefault(i,set()).add(v)
    return lay,pf

def test(info):
    n=info['n']; T=info['T']; N=n; M=info['M']; cyc=info['cyc']; ell=info['ell']
    worstL=None; worstA=None
    for f in M:
        lay,pf=layers_of(info,f)
        for i,S in lay.items():
            val=sum(pf[v]*T[v] for v in S)   # layer-average load (since sum pf=1 over layer)
            slack=N-val
            if worstL is None or slack<worstL: worstL=slack
        for P in cyc[f]:
            val=sum(T[v] for v in P)
            slack=N*ell[f]-val
            if worstA is None or slack<worstA: worstA=slack
    return worstL,worstA

def run(Nmax,Nmin=5):
    print("--- (Layer-SM) layer-avg load<=N  and  (Cycle-A) sum_{v in C}T<=N*ell ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; Lbad=0; Abad=0; Lmin=None; Amin=None; Lg=None; Ag=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; wL,wA=test(info)
            if wL<0: Lbad+=1
            if wA<0: Abad+=1
            if Lmin is None or wL<Lmin: Lmin=wL; Lg=g6
            if Amin is None or wA<Amin: Amin=wA; Ag=g6
        print(f"  N={nn}: cfg={nt} | (Layer-SM) viol:{Lbad} (min slack={float(Lmin):+.4f}@{Lg}) | (Cycle-A) viol:{Abad} (min slack={float(Amin):+.4f}@{Ag})",flush=True)

if __name__=="__main__":
    run(11,5)
