"""Does D2 imply SM? And is D2 strictly easier (i.e. has slack where SM is tight differently)?

D2:  sum_v (T_v-N)_+^2 <= T^T B T,  where B=diag(T)-K, T^T B T = sum_v T_v^3 - sum_v T_v (KT)_v.

CLAIM (the reduction D2 => SM): need an INDEPENDENT bound on T^T B T from above by N*(N^2-Gamma)?
No. Let's find the real chain.

Better: T^T B T = sum_v T_v[ T_v^2 - (KT)_v ].  Using K1=T => (K(T-N1))_v = (KT)_v - N T_v.
So T_v^2-(KT)_v = T_v^2 - N T_v - (K(T-N1))_v = T_v(T_v-N) - (K w)_v,  w:=T-N1.
=> T^T B T = sum_v T_v[ T_v(T_v-N) - (Kw)_v ]
           = sum_v T_v^2(T_v-N)  -  sum_v T_v (Kw)_v
           = sum_v T_v^2 w_v  -  T^T K w.
And T^T K w = (KT)^T w ... = sum_v (KT)_v w_v.  With KT=K T.
Hmm getting circular. Let me just EMPIRICALLY test the candidate reduction:

  (RED)  N*(N^2 - Gamma)  >=  T^T B T   ??   If TRUE, then since coup = sum T(T-N) and
         we want coup<=0... let's just test several inequalities and report which hold and which
         give a clean chain to SM.

Test battery of inequalities (all should be exact-rational):
 (A) coup = sum_v T_v(T_v-N) <= 0                      [<=> SM, the target]
 (D2) over2 := sum (T_v-N)_+^2 <= TBT                  [my candidate, verified 0-fail census<=10]
 (E)  TBT <= N*(N^2-Gamma)                             [if true with D2... chain?]
 (F)  over2 <= N*(N^2-Gamma)                           [direct: overload L2 <= N*underload-mass]
 (G)  coup <= over2 - under2... identity check
 (U)  under2 := sum (N-T_v)_+^2;  is over2<=under2 ?   (we know U_over<=U_under L1 was false at N=22 blowup)
Report each.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _reframe_test import Kdata, from_g6

def allmetrics(info):
    n,T,K,ell,M,pf=Kdata(info)
    N=n
    Gamma=sum(L*L for L in ell.values())
    KT=[F(0)]*n
    for (v,w),val in K.items(): KT[v]+=val*T[w]
    TBT=sum(T[v]*T[v]*T[v] for v in range(n))-sum(T[v]*KT[v] for v in range(n))
    over2=sum((x-N)*(x-N) for x in T if x>N)
    under2=sum((N-x)*(N-x) for x in T if x<N)
    coup=sum(x*(x-N) for x in T)
    rhs=N*(N*N-Gamma)
    return dict(N=N,Gamma=Gamma,coup=coup,over2=over2,under2=under2,TBT=TBT,rhs=rhs,
        A=coup<=0, D2=over2<=TBT, E=TBT<=rhs, Ff=over2<=rhs, U=over2<=under2)

if __name__=="__main__":
    print("=== witnesses (N=22 sandwich-killer is the discriminator) ===")
    for g6,t in [("J???E?pNu\\?",2)]:
        info=from_g6(g6,t); m=allmetrics(info)
        print(g6,t, {k:(float(v) if isinstance(v,F) else v) for k,v in m.items()})
    print("=== census: count violations of each ===")
    keys=['A','D2','E','Ff','U']
    for nn in range(5,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; viol={k:0 for k in keys}
        for g6 in out:
            info=loads(*dec(g6))
            if info is None: continue
            tot+=1; m=allmetrics(info)
            for k in keys:
                if not m[k]: viol[k]+=1
        print(f"N={nn}: tot={tot} " + " ".join(f"{k}_viol={viol[k]}" for k in keys))
    # blowups
    print("=== blowups ===")
    def Cblow(k,q):
        L=2*k+1; m=L*q; E=[]
        for i in range(L):
            for a in range(q):
                for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
        return m,E
    for (k,q) in [(2,3),(2,4),(3,3),(4,2)]:
        m_,E=Cblow(k,q); info=loads(m_,E)
        if info is None: print(f"C{2*k+1}[{q}] skip"); continue
        m=allmetrics(info)
        print(f"C{2*k+1}[{q}] N={m['N']} A={m['A']} D2={m['D2']} E={m['E']} Ff={m['Ff']} U={m['U']} coup={float(m['coup']):.1f} over2={float(m['over2']):.2f} TBT={float(m['TBT']):.2f}")
