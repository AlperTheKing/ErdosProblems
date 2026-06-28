"""At each saturated u (T(u)=N), examine U_u = union of supports of F_u={f:p_f(u)>0}.
Questions:
  - |U_u| vs N=T(u): is T(u)<=|U_u| (budget) at saturated vertices?
  - Which vertices are NOT in U_u (the 'uncovered' set)? Are they exactly the dead-net T=0 vertices?
  - For the zero-mu neighbor v: confirm v not in U_u (support-disjointness), v in uncovered set.
This tells us whether budget alone is too weak (|U_u|>=N forced) and what really happens.
Loads-cut census N<=11 + the rich witnesses. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def analyze(g6, info, dump=False):
    N=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; mu=mu_edges(info)
    pf={}; supp={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); s=set()
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
    rows=[]
    for u in range(N):
        if T[u]!=N: continue
        Fu=[f for f in M if pf.get((f,u),0)>0]
        Uu=set().union(*[supp[f] for f in Fu]) if Fu else set()
        uncovered=[x for x in range(N) if x not in Uu]
        dead=[x for x in range(N) if T[x]==0]
        budget = (T[u]<=len(Uu))
        rows.append((u,len(Uu),N,budget,uncovered,dead))
        if dump:
            print(f"   {g6} u={u}: T(u)=N={N}, |U_u|={len(Uu)}, budget(T<=|U|)={budget}")
            print(f"      uncovered (not in U_u)={uncovered}  dead(T=0)={dead}  equal={set(uncovered)==set(dead)}")
    return rows

if __name__=="__main__":
    print("=== budget at saturated vertices ===")
    for g6 in ["I??E@fKJ_","I??CF@wFo","I??CABoNo"]:
        n,E=dec(g6); info=loads(n,E); analyze(g6,info,dump=True)
    # census: count saturated u with budget fail, and whether uncovered==dead always
    tot=0; budfail=0; unc_eq_dead=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for (u,Uu,N,bud,unc,dead) in analyze(g6,info):
                tot+=1
                if not bud: budfail+=1
                if set(unc)==set(dead): unc_eq_dead+=1
        print(f"  census N={nn}: saturated-u={tot} budget-fail={budfail} uncovered==dead-set={unc_eq_dead}",flush=True)
