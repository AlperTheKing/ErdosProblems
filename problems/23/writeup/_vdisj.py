"""Test vertex-level structure for a zero-mu edge uv (both T>0):
 (VD-full) are the union supports  U_u=union_{f:p_f(u)>0} supp(p_f)  and  U_v (sym)  vertex-DISJOINT?
 (VD-near) is u not in any F_v-support and v not in any F_u-support? (this is support-disjointness, already proven)
 (BUDGET) test T(u) <= |U_u| and T(v) <= |U_v| (load <= #vertices used)?  Then if U_u,U_v disjoint => SUM<=N.
Also try a WEAKER sufficient structure: the f-geodesics of F_u all avoid v, those of F_v all avoid u (proven),
plus do F_u-supports and F_v-supports overlap only on a controlled set?
Report on loads-cut census N<=11 + the C5-extremal witnesses."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def analyze(g6, info):
    N=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; mu=mu_edges(info)
    pf={}; supp={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); s=set()
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
    out=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if not (T[u]>0 and T[v]>0): continue
        Fu=[f for f in M if pf.get((f,u),0)>0]; Fv=[f for f in M if pf.get((f,v),0)>0]
        Uu=set().union(*[supp[f] for f in Fu]) if Fu else set()
        Uv=set().union(*[supp[f] for f in Fv]) if Fv else set()
        inter=Uu & Uv
        vd_full = (len(inter)==0)
        budget = (T[u]<=len(Uu)) and (T[v]<=len(Uv))
        out.append(dict(g6=g6,u=u,v=v,Tu=str(T[u]),Tv=str(T[v]),
                        Uu=len(Uu),Uv=len(Uv),inter=sorted(inter),vd_full=vd_full,
                        budget=budget,sum=str(T[u]+T[v]),N=N,disjsize=len(Uu)+len(Uv)-len(inter)))
    return out

if __name__=="__main__":
    print("=== vertex-disjointness / budget for zero-mu both-pos edges ===")
    nvd=0; ntot=0; nbud=0
    examples=[]
    for nn in range(10,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(g6,info):
                ntot+=1
                if r['vd_full']: nvd+=1
                if r['budget']: nbud+=1
                if len(examples)<8: examples.append(r)
    print(f"both-pos zero-mu edges: total={ntot} vertex-DISJOINT-supports={nvd} budget(T<=|U|)holds={nbud}")
    for e in examples: print("  ",e)
