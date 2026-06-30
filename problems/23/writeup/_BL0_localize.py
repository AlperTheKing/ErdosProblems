"""De-circularize B_L>=0: replace the GLOBAL (N^2-Gamma) by a LOCAL lower bound, and see what
survives.  N^2-Gamma = sum_v (N - T_v).  The path P only touches L vertices.  Candidate local
surrogates for L*(N^2-Gamma):
   (a) restrict the global sum to the path itself:  L * sum_{i}(N - T_i)/?  -- but that loses sign.
We instead test SCALE-FREE normalized forms and a per-row CERTIFICATE structure:

  Write t_i = T_i/N in [?].  B_L/N^2 = L(1-gamma) + (25/N)(L - sum t_i) - (1/N^2)(S^2 - L^2 q),
  gamma=Gamma/N^2, S=sum t_i.   As N->infty (graphon/blow-up limit) the lower-order terms vanish
  and B_L/N^2 -> L(1-gamma) >= 0.  So the CONTENT at finite N is the O(1/N) and O(1/N^2) terms.
  Reorganize EXACTLY (no Gamma-circularity) using the load identity sum_v T_v = Gamma:
    L(N^2 - Gamma) = L * sum_v (N - T_v).
  Define for the path:  Din = sum_{i}(N - T_i)  (path underload, signed),  Dout = sum_{v notin P}(N-T_v).
  Then L(N^2-Gamma) = L*(Din + Dout), and 25(LN - sum T_i) = 25*Din.
    B_L = L*Dout + (L+25)*Din - (S^2 - L^2 q).
  Now test which of these is the binding/provable piece, and whether B_L >= (L+25)*Din - (S^2-L^2q)
  (i.e. dropping the nonneg-looking L*Dout) STILL holds -- if Dout>=0 always that would localize it.
  Also test the CLEAN candidate:  (L+25)*Din >= S^2 - L^2 q   (path-only, NO global Gamma!).
  ALL exact.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos
from _bdef_construct import Cn, mycielski

def adjof(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<n):
        side=[(mask>>i)&1 for i in range(n)]; c=cutsize(n,adj,side)
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return cuts
def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M or not Bconn(n,adj,side): return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    return M,ell,T,cyc

def analyze(n,E,allcuts=True,seedcut=None):
    adj=adjof(n,E)
    cuts = all_maxcuts(n,adj) if allcuts else [seedcut]
    res=dict(nDoutNeg=0,nDinNeg=0,nPathOnlyFail=0,minPathSlack=None,minB=None,rows=0,
             minDout=None)
    for side in cuts:
        if side is None: continue
        st=struct(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st; N=F(n); Gamma=sum(T)
        Tall=sum(N-T[v] for v in range(n))  # = N^2-Gamma
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                res['rows']+=1
                Ti=[T[P[i]] for i in range(L)]
                Pset=set(P)
                Din=sum(N-Ti[i] for i in range(L))
                Dout=Tall - Din
                h=[Ti[i]/N for i in range(L)]; S=sum(h)
                q=min(h[i]*h[(i+1)%L] for i in range(L))
                disp=S*S-(L*L)*q
                B=L*(N*N-Gamma)+25*(L*N-sum(Ti))-disp
                if Dout<0: res['nDoutNeg']+=1
                if Din<0: res['nDinNeg']+=1
                if res['minDout'] is None or Dout<res['minDout']: res['minDout']=Dout
                # path-only candidate: (L+25)*Din >= disp
                pslack=(L+25)*Din - disp
                if pslack<0: res['nPathOnlyFail']+=1
                if res['minPathSlack'] is None or pslack<res['minPathSlack']:
                    res['minPathSlack']=pslack
                if res['minB'] is None or B<res['minB']: res['minB']=B
    return res

def main():
    agg=dict(nDoutNeg=0,nDinNeg=0,nPathOnlyFail=0,minPathSlack=None,rows=0,minDout=None)
    # census N<=10 (all max cuts, not just gmin -- broader)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); r=analyze(n,E,allcuts=True)
            agg['nDoutNeg']+=r['nDoutNeg']; agg['nDinNeg']+=r['nDinNeg']
            agg['nPathOnlyFail']+=r['nPathOnlyFail']; agg['rows']+=r['rows']
            for k in ('minPathSlack','minDout'):
                if r[k] is not None and (agg[k] is None or r[k]<agg[k]): agg[k]=r[k]
    print("CENSUS N<=10 (all max cuts):")
    print("  rows:", agg['rows'])
    print("  Dout<0 rows (global-tail underload negative):", agg['nDoutNeg'])
    print("  Din<0 rows (path overloaded net):", agg['nDinNeg'])
    print("  min Dout:", agg['minDout'])
    print("  PATH-ONLY candidate (L+25)Din >= S^2-L^2q  FAIL count:", agg['nPathOnlyFail'],
          " min path slack:", agg['minPathSlack'])

if __name__=="__main__":
    main()
