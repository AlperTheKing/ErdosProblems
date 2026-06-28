"""Sanity + slack distribution: confirm A (R_f<=N ell_f), ROWSUM-O (O1_f<=N), CW-T, CW-S are NON-trivial
(i.e. residuals are genuinely negative, tight=0 only at extremals). Print min residual (most slack) and
count of tight (==0) edges, on a few representative graphs + extremals. EXACT."""
import subprocess
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
    O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        di=pf[i]
        for j in range(m):
            s=F(0)
            for v,pv in di.items():
                pw=pf[j].get(v)
                if pw is not None: s+=pv*pw
            O[i][j]=s
    ellv=[F(ell[M[g]]) for g in range(m)]
    K=[[F(0)]*n for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items(): K[v][w]+=pv*pw
    T=[sum(ellv[g]*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    S=[sum(pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    R=[sum(O[i][j]*ellv[j] for j in range(m)) for i in range(m)]
    O1=[sum(O[i][j] for j in range(m)) for i in range(m)]
    KT=[sum(K[v][w]*T[w] for w in range(n)) for v in range(n)]
    KS=[sum(K[v][w]*S[w] for w in range(n)) for v in range(n)]
    return dict(n=n,N=N,m=m,O=O,ellv=ellv,R=R,O1=O1,T=T,S=S,KT=KT,KS=KS)

def report(label, info):
    d=build(info); N=d['N']; m=d['m']; n=d['n']
    # A residuals R_f - N ell_f
    Ares=[d['R'][f]-F(N)*d['ellv'][f] for f in range(m)]
    RSres=[d['O1'][f]-F(N) for f in range(m)]
    CWTres=[d['KT'][v]-F(N)*d['T'][v] for v in range(n) if d['T'][v]>0]
    CWSres=[d['KS'][v]-F(N)*d['S'][v] for v in range(n) if d['S'][v]>0]
    def stat(res):
        if not res: return ("--","--","--")
        mx=max(res); mn=min(res); tight=sum(1 for x in res if x==0)
        return (float(mx),float(mn),tight)
    aA=stat(Ares); aRS=stat(RSres); aT=stat(CWTres); aS=stat(CWSres)
    print(f"{label} N={N} m={m}:")
    print(f"   A  (R-N ell)   max={aA[0]} min={aA[1]} tight={aA[2]}/{m}")
    print(f"   RSO(O1-N)      max={aRS[0]} min={aRS[1]} tight={aRS[2]}/{m}")
    print(f"   CWT(KT-N T)    max={aT[0]} min={aT[1]} tight={aT[2]}")
    print(f"   CWS(KS-N S)    max={aS[0]} min={aS[1]} tight={aS[2]}")

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

if __name__=="__main__":
    # a generic non-extremal census graph (overloaded): I?ABCc]}? was max overload
    for g6 in ["I?ABCc]}?","G?`F`w","I?bBF_{{?","FCp`_"]:
        n,E=dec(g6); info=loads(n,E)
        if info: report(g6,info)
    print("--- extremal ---")
    for L,q in [(5,2),(5,3),(7,2)]:
        n,E=cycle_blowup(L,q); info=loads(n,E)
        if info: report(f"C{L}[{q}]",info)
