"""A-alltie exact probe. For the loads-cut, find every zero-mu B-edge uv with T(u)=N.
Record T(v), and the local geodesic structure around v: which bad edges have p_f(v)>0,
and for each such f, which incident B-edges of v its geodesics use (and their mu).
Goal: understand WHY T(v)=0 must hold, or find the obstruction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def analyze(g6, info, verbose=False):
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    # p_f(v) for each f,v
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for v in range(N):
            c=sum(1 for P in Ps if v in P)
            if c: pf[(f,v)]=F(c,k)
    res=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]==N and T[b]!=0:
                res.append((g6,a,b,float(T[b])))
                if verbose:
                    print(f"  VIOL {g6}: T(u={a})=N={N}, edge ({a},{b}) zero-mu, T(v={b})={T[b]}={float(T[b])}")
    return res

if __name__=="__main__":
    print("=== A-alltie probe: zero-mu edge uv, T(u)=N, record T(v) ===")
    # loads-cut gate graphs
    gate=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","I??CABoNo","I??CF@wFo"]
    for g6 in gate:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        analyze(g6, info, verbose=True)
    # census loads-cut: count sat+zero-mu coincidences and any A-violation
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nviol=0; ncases=0; minTv=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            N=info['n']; T=info['T']
            if not any(t==N for t in T): continue
            mu=mu_edges(info)
            for e,val in mu.items():
                if val!=0: continue
                u,v=tuple(e)
                for (a,b) in [(u,v),(v,u)]:
                    if T[a]==N:
                        ncases+=1
                        if T[b]!=0:
                            nviol+=1
                        else:
                            pass
        print(f"  census N={nn} loads-cut: (sat u, zero-mu uv) cases={ncases} A-violations(T(v)!=0)={nviol}", flush=True)
