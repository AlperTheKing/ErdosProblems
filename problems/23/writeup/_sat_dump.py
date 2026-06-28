"""Dump the local structure of a SATURATED underloaded vertex q (T[q]=N) to find why leak[q]>0.
For the saturated q, list the bad edges f through q (p_f(q)>0), their ell, supp(f), and which of
those supports touch O. We want to SEE the mechanism forcing some f to reach O."""
from fractions import Fraction as F
from _h import dec, GENG, loads
from _cond1_proof import build_K
from _schur_spec import pf_exact

def dump(g6, blowt=1):
    n,E=dec(g6)
    if blowt>1:
        EE=[]
        for (a,b) in E:
            for i in range(blowt):
                for j in range(blowt): EE.append((a*blowt+i,b*blowt+j))
        n,E=n*blowt,EE
    info=loads(n,E)
    P,M,ell,nn=pf_exact(info)
    K,T,O,Q,N,_=build_K(info)
    Oset=set(O)
    sat=[q for q in Q if T[q]==F(N)]
    print(f"g6={g6} blow={blowt} N={N} |O|={len(O)} O={O} saturated-Q-verts={sat}")
    for q in sat:
        print(f"  q={q} T[q]={float(T[q])}=N. bad edges through q:")
        leak=F(0)
        for fi in range(len(M)):
            pq=P[fi].get(q,F(0))
            if pq>0:
                supp=set(P[fi].keys())
                hitsO=supp & Oset
                # contribution to leak from this f: p_f(q)*sum_{o in O} p_f(o)
                contrib=pq*sum(P[fi].get(o,F(0)) for o in O)
                leak+=contrib
                print(f"    f={M[fi]} ell={ell[M[fi]]} p_f(q)={float(pq):.3f} supp_size={len(supp)} "
                      f"O-in-supp={sorted(hitsO)} leak_contrib={float(contrib):.4f}")
        print(f"    => leak[q]={float(leak):.4f}")

if __name__=="__main__":
    dump("H?bBF_{")        # N=9, saturated vertex 7, O={8}
    print()
    dump("I?BD@g]Qo")      # N=10, sat=[7,9], O=[5,6,8]
