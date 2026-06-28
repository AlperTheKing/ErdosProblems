"""Deep structural dump for A-alltie. For a chosen graph + loads-cut, find a saturated u
with a zero-mu incident edge uv, and print the full local picture:
 - T(u)=N decomposition: which bad edges f route through u, p_f(u), and which incident B-edges they use
 - the neighborhood of v: T(v), and (if T(v)>0) which f route through v
 - layer indices to see geodesic geometry
Aim: confirm the mechanism 'saturated u with idle corridor uv => v carries no geodesic'."""
from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges

def Bnbrs(info,x):
    adj=info['adj']; side=info['side']
    return [w for w in adj[x] if side[w]!=side[x]]

def dump(g6):
    n,E=dec(g6); info=loads(n,E)
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    print(f"\n### {g6} N={N}  side={info['side']}")
    print(f"  M={M}")
    print(f"  ell={ {f:info['ell'][f] for f in M} }")
    print(f"  T={[ (i,str(T[i])) for i in range(N) ]}")
    # p_f(v)
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for v in range(N):
            c=sum(1 for P in Ps if v in P)
            if c: pf[(f,v)]=F(c,k)
    # find sat u with zero-mu edge
    found=False
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]==N:
                found=True
                print(f"\n  >>> saturated u={a} (T=N={N}), zero-mu edge ({a},{b}), T(v={b})={T[b]}")
                # bad edges through u
                print(f"      edge ({a},{b}) mu={mu[e]}")
                print(f"      u={a} B-nbrs and incident mu:")
                for w in Bnbrs(info,a):
                    print(f"          {a}-{w}: mu={mu.get(frozenset((a,w)),F(0))}")
                print(f"      bad edges f with p_f(u={a})>0:")
                for f in M:
                    if pf.get((f,a),0):
                        endpt = a in f
                        print(f"          f={f} ell={ell[f]} p_f(u)={pf[(f,a)]}  (u is {'ENDPOINT' if endpt else 'interior'})")
                print(f"      v={b} B-nbrs and incident mu:")
                for w in Bnbrs(info,b):
                    print(f"          {b}-{w}: mu={mu.get(frozenset((b,w)),F(0))}  T({w})={T[w]}")
                print(f"      bad edges f with p_f(v={b})>0:")
                for f in M:
                    if pf.get((f,b),0):
                        print(f"          f={f} ell={ell[f]} p_f(v)={pf[(f,b)]}")
    if not found:
        print("  (no saturated u with zero-mu incident edge on loads-cut)")

if __name__=="__main__":
    import sys
    gs=sys.argv[1:] if len(sys.argv)>1 else ["I??CABoNo","I??CF@wFo"]
    for g6 in gs: dump(g6)
