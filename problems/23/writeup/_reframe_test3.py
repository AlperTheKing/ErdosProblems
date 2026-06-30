"""Pin down (Ff): sum_v (T_v-N)_+^2 <= N*(N^2-Gamma).  Does it imply SM? Test on the HARD battery.

Implication (Ff) => SM:  Let w_v=T_v-N, over2=sum_{w>0} w^2, under2=sum_{w<0} w^2.
sum_v w_v = Gamma-N^2 =: -D  (D=N^2-Gamma>=0 want).
We have coup = sum_v T_v w_v = sum_v (w_v+N) w_v = sum w^2 + N sum w = (over2+under2) - N*D.
SM <=> coup<=0 <=> over2+under2 <= N*D.
So SM needs BOTH over2 AND under2 bounded by N*D jointly: (over2+under2) <= N*D.
(Ff) only bounds over2<=N*D. So (Ff) ALONE is NOT sufficient (need under2 too). TEST: over2+under2<=N*D ?
Call it (SMQ): sum_v (T_v-N)^2 <= N*(N^2-Gamma).  [this is EXACTLY <=> SM, since =coup+N*D... wait]
Actually sum_v(T_v-N)^2 = over2+under2, and we showed coup=(over2+under2)-N*D. coup<=0 <=> over2+under2<=N*D.
So (SMQ): sum_v (T_v-N)^2 <= N*(N^2-Gamma)  IS EXACTLY EQUIVALENT to SM. Good -- that's the clean restatement.

So the genuinely-useful split is:  SMQ = (Ff: over2<=N*D) + (under-part: under2 <= N*D - over2).
Test whether the DECOMPOSED two-sided bound has a clean structure:
  (Ff)      over2  <= N*D                      [verified 0-fail; the EASY half]
  (Gg)      under2 <= N*D                       [the other half alone]
  (SMQ)     over2+under2 <= N*D                 [<=> SM exactly]
Report all + on Mycielskians + random high-gamma.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads
from _reframe_test import Kdata

def metrics(info):
    n,T,K,ell,M,pf=Kdata(info)
    N=n; Gamma=sum(L*L for L in ell.values()); D=N*N-Gamma
    over2=sum((x-N)*(x-N) for x in T if x>N)
    under2=sum((N-x)*(N-x) for x in T if x<N)
    return dict(N=N,Gamma=Gamma,D=D,over2=over2,under2=under2,
        Ff=over2<=N*D, Gg=under2<=N*D, SMQ=(over2+under2)<=N*D)

def myc(n,E):
    # Mycielskian: vertices 0..n-1 (orig), n..2n-1 (shadows u_i), 2n (apex w)
    m=2*n+1; EE=list(E)
    for (a,b) in E:
        EE.append((a, n+b)); EE.append((n+a, b))
    for i in range(n): EE.append((n+i, 2*n))
    return m,EE

if __name__=="__main__":
    print("=== census ===")
    for nn in range(5,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0;v={'Ff':0,'Gg':0,'SMQ':0}
        for g6 in out:
            info=loads(*dec(g6))
            if info is None: continue
            tot+=1; m=metrics(info)
            for k in v:
                if not m[k]: v[k]+=1
        print(f"N={nn}: tot={tot} Ff_viol={v['Ff']} Gg_viol={v['Gg']} SMQ_viol={v['SMQ']}")
    print("=== iterated Mycielskians from C5 (standing gate) ===")
    n,E=5,[(0,1),(1,2),(2,3),(3,4),(4,0)]  # C5
    for it in range(4):
        info=loads(n,E)
        if info is None: print(f"Myc^{it} N={n}: skip (maxcut all too big?)")
        else:
            m=metrics(info)
            print(f"Myc^{it}(C5) N={n} Gamma={m['Gamma']} D={m['D']} Ff={m['Ff']} Gg={m['Gg']} SMQ={m['SMQ']} over2={float(m['over2']):.1f} under2={float(m['under2']):.1f} NxD={m['N']*m['D']}")
        if n>23: break
        n,E=myc(n,E)
    print("=== random triangle-free high-gamma N=12 ===")
    random.seed(1); chk=0; vff=0; vsmq=0
    for _ in range(40):
        nn=12; adj=[set() for _ in range(nn)]; E=[]
        order=[(a,b) for a in range(nn) for b in range(a+1,nn)]; random.shuffle(order)
        for (a,b) in order:
            if any(c in adj[a] and c in adj[b] for c in range(nn)): continue
            adj[a].add(b); adj[b].add(a); E.append((a,b))
        info=loads(nn,E)
        if info is None: continue
        chk+=1; m=metrics(info)
        if not m['Ff']: vff+=1
        if not m['SMQ']: vsmq+=1
    print(f"random N=12: checked={chk} Ff_viol={vff} SMQ_viol={vsmq}")
