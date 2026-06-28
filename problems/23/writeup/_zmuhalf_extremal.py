"""Dump the extremal ZMU-HALF case (max(Tu,Tv)=N/2) to understand the mechanism.
Witness: I?`DA`gd? edge (8,1) T=5,5 at N=10.
Print: the cut, T over all vertices, the bad edges + their geodesics, mu on edges around u,v,
and WHY both ends reach exactly N/2.
Exact Fraction."""
from fractions import Fraction as F
from _h import dec, loads, geos
from _zmu import mu_edges

def dump(g6):
    n,E=dec(g6); info=loads(n,E)
    N=info['n']; T=info['T']; side=info['side']; adj=info['adj']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    print(f"=== {g6} N={N} ===")
    print("side:", side)
    print("T:", [f"{i}:{str(T[i])}" for i in range(N)])
    s0=[i for i in range(N) if side[i]==0]; s1=[i for i in range(N) if side[i]==1]
    print(f"side0 ({len(s0)}): {s0}   side1 ({len(s1)}): {s1}")
    print("bad edges (f, ell, #geodesics):")
    for f in M:
        print(f"   {f} ell={ell[f]} ngeo={len(cyc[f])}: geodesics={cyc[f]}")
    # zero-mu both-positive edges
    print("zero-mu edges with both ends positive:")
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]>0 and T[v]>0:
            print(f"   edge ({u},{v}) side {side[u]}/{side[v]}: T={str(T[u])},{str(T[v])}  max={float(max(T[u],T[v]))}")
            # which bad edges pass through u, through v
            fu=[f for f in M if any(u in P for P in cyc[f])]
            fv=[f for f in M if any(v in P for P in cyc[f])]
            print(f"      bad edges thru u={u}: {fu}")
            print(f"      bad edges thru v={v}: {fv}")

if __name__=="__main__":
    dump("I?`DA`gd?")
