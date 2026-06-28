"""A-alltie dissection. For each (saturated u, zero-mu B-edge uv) case in the census loads-cut,
dump the full geodesic structure around u and v:
 - T(u), T(v), D(u), D(v), handshake check
 - For each bad edge f with p_f(u)>0: is u interior or endpoint of f's geodesics; do any geodesics of f use edge uv?
 - For each bad edge f with p_f(v)>0: same.
 - Verify SUPPORT-DISJOINTNESS: no single bad edge f has both u and v in its geodesic support.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def pf_of(info):
    N=info['n']; M=info['M']; cyc=info['cyc']
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for v in range(N):
            c=sum(1 for P in Ps if v in P)
            if c: pf[(f,v)]=F(c,k)
    return pf

def edge_in_geos(info, f, a, b):
    """count fraction of f's geodesics that use undirected edge (a,b)."""
    Ps=info['cyc'][f]; k=len(Ps)
    c=0
    for P in Ps:
        for i in range(len(P)-1):
            if {P[i],P[i+1]}=={a,b}: c+=1; break
    return F(c,k)

def role_at(info, f, u):
    """is u an endpoint of f, or interior to f's geodesics? returns ('endpoint'|'interior'|'mixed'|'none', count_interior_edges_weighted)"""
    Ps=info['cyc'][f]; k=len(Ps); a,b=f
    if u==a or u==b: return 'endpoint'
    # interior: count geodesics that contain u (all that do have u strictly interior since u!=a,b)
    cnt=sum(1 for P in Ps if u in P)
    return 'interior' if cnt>0 else 'none'

def dissect(g6, info):
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']
    mu=mu_edges(info)
    pf=pf_of(info)
    out=[]
    for e,val in mu.items():
        if val!=0: continue
        u0,v0=tuple(e)
        for (u,v) in [(u0,v0),(v0,u0)]:
            if T[u]!=N: continue
            # case found
            Du=sum(ell[f] for f in M if u in f)
            Dv=sum(ell[f] for f in M if v in f)
            # bad edges touching u
            fu=[f for f in M if (f,u) in pf]
            fv=[f for f in M if (f,v) in pf]
            # SUPPORT-DISJOINTNESS check
            both=[f for f in M if (f,u) in pf and (f,v) in pf]
            rep={
                'g6':g6,'u':u,'v':v,'Tu':T[u],'Tv':T[v],'N':N,'Du':Du,'Dv':Dv,
                'fu':[(f, str(pf[(f,u)]), role_at(info,f,u), ell[f]) for f in fu],
                'fv':[(f, str(pf[(f,v)]), role_at(info,f,v), ell[f]) for f in fv],
                'both':both,
            }
            out.append(rep)
    return out

if __name__=="__main__":
    print("=== A-alltie dissection ===")
    # 1) verify SUPPORT-DISJOINTNESS over census loads-cut, count violations
    print("--- SUPPORT-DISJOINTNESS (zero-mu uv with T(u)=N => no bad edge f has both u,v in supp) ---")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cases=0; supp_viol=0; halfviol=0; tvnonzero=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for rep in dissect(g6, info):
                cases+=1
                if rep['both']: supp_viol+=1
                if rep['Tv']!=0: tvnonzero+=1
        print(f"  N={nn}: sat-zero-mu cases={cases}  SUPPORT-DISJ-viol(both u,v in some supp)={supp_viol}  A-alltie-viol(Tv!=0)={tvnonzero}", flush=True)
    # 2) dump a few concrete cases for structural inspection
    print("--- concrete dumps ---")
    gate=["I??CABoNo","I??CF@wFo","J??CE?{{?]?","I?BD@g]Qo"]
    for g6 in gate:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        reps=dissect(g6, info)
        for rep in reps[:2]:
            print(f"  {g6}: u={rep['u']} T(u)={rep['Tu']}=N  v={rep['v']} T(v)={rep['Tv']}  D(u)={rep['Du']} D(v)={rep['Dv']}")
            print(f"     bad-edges thru u: {rep['fu']}")
            print(f"     bad-edges thru v: {rep['fv']}")
            print(f"     both: {rep['both']}")
