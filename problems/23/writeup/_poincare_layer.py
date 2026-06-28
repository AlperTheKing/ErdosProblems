"""Layer-variance decomposition of the Poincare LHS.
SPEC <=> for all x: sum_f E_f(x) >= sum_v (T(v)-N) x_v^2, where
  E_f(x) = ell(f)*sum_v p_f(v) x_v^2 - (sum_v p_f(v) x_v)^2 = WITHIN_f + BETWEEN_f,
  m_i = sum_{v in I_i} p_f(v) x_v  (layer-i conditional mean, layer mass=1),
  WITHIN_f  = ell * sum_i ( sum_{v in I_i} p_f(v) x_v^2 - m_i^2 )   (Jensen >=0 each layer)
  BETWEEN_f = ell * sum_i (m_i - mbar)^2,  mbar = (1/ell) sum_i m_i   (variance of the layer-mean profile)
BETWEEN_f is the variance of x's profile along the odd cycle C_ell (length>=5): odd-girth enters here.
Verify decomp exactly; measure how much overload each piece pays."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _schur_spec import pf_exact
from collections import deque
import random, subprocess
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def prep(info):
    P,M,ell,n=pf_exact(info)
    adj=info['adj']; side=info['side']
    Lf=[]  # per f: list of layers (each list of vertices), pf dict, L
    for fi,f in enumerate(M):
        a,b=f
        d={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        pf=P[fi]; L=ell[f]
        layers={}
        for v in pf: layers.setdefault(d[v],[]).append(v)
        Lf.append(([layers.get(i,[]) for i in range(L)], pf, L))
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    return Lf,T,M,n

def E_decomp(Lf_entry, x):
    layers,pf,L = Lf_entry
    m=[sum(pf[v]*x[v] for v in lyr) for lyr in layers]
    q=[sum(pf[v]*x[v]**2 for v in lyr) for lyr in layers]
    within = L*sum(q[i]-m[i]**2 for i in range(L))
    mbar = sum(m)/L
    between = L*sum((m[i]-mbar)**2 for i in range(L))
    Ef = L*sum(q) - (sum(m))**2
    return Ef, within, between

def run_check(info, trials, seed):
    Lf,T,M,n=prep(info); N=n
    rnd=random.Random(seed)
    minslack=None
    # also measure: can BETWEEN alone (within=0) pay the overload? i.e. is sum_f BETWEEN_f >= RHS?
    min_between_slack=None
    for _ in range(trials):
        x=[F(rnd.randint(-4,4)) for _ in range(n)]
        E_tot=F(0); B_tot=F(0)
        for entry in Lf:
            Ef,within,between=E_decomp(entry,x)
            assert Ef==within+between
            E_tot+=Ef; B_tot+=between
        rhs=sum((T[v]-N)*x[v]**2 for v in range(n))
        s=E_tot-rhs
        sb=B_tot-rhs
        if minslack is None or s<minslack: minslack=s
        if min_between_slack is None or sb<min_between_slack: min_between_slack=sb
    return minslack, min_between_slack, N

if __name__=="__main__":
    print('=== layer decomposition exact + does BETWEEN alone suffice? ===')
    for t in [2,3]:
        nn,EE=blow(t); info=loads(nn,EE)
        ms,mb,N=run_check(info,8,t)
        print('C5[%d] N=%d: full slack min=%s  | BETWEEN-only slack min=%s'%(t,N,str(ms),str(mb)))
    bad_full=0; bad_between=0; tested=0
    for nn in [8,9,10,11]:
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        stride=1 if nn<=9 else (10 if nn==10 else 80)
        for g6 in out[::stride]:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            tested+=1
            ms,mb,N=run_check(info,3,hash(g6)%9999)
            if ms<0: bad_full+=1; print('  FULL VIOLATION %s slack=%s'%(g6,str(ms)))
            if mb<0: bad_between+=1
    print('census tested=%d: FULL violations=%d  BETWEEN-only violations=%d'%(tested,bad_full,bad_between))
