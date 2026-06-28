"""Layer-geometry dump at a saturated u with zero-mu edge uv.
For each bad edge f through u, show layer index of u and v relative to f's endpoints (BFS distance),
and whether v is in the geodesic interval of f at all (could it host a geodesic?).
Aim: see WHY v carries no geodesic when uv idle and u saturated."""
from fractions import Fraction as F
from collections import deque
from _h import dec, loads
from _zmu import mu_edges

def bfs(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        x=q.popleft()
        for w in adj[x]:
            if side[w]!=side[x] and w not in d: d[w]=d[x]+1; q.append(w)
    return d

def dump(g6):
    n,E=dec(g6); info=loads(n,E)
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    print(f"\n### {g6} N={N} side={side}  M={M} ell={[ell[f] for f in M]}")
    print(f"  T={[str(t) for t in T]}")
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]!=N: continue
            print(f"  sat u={a}, zero-mu edge ({a},{b}), T(v={b})={T[b]}")
            for f in M:
                s,t=f
                da=bfs(adj,side,s); db=bfs(adj,side,t)
                L=ell[f]-1  # = d_B(s,t)
                # v on geodesic interval iff da[b]+db[b]==L
                on_u = (da.get(a,99)+db.get(a,99)==L)
                on_v = (da.get(b,99)+db.get(b,99)==L)
                print(f"     f=({s},{t}) L={L}: u layer da={da.get(a,'-')},db={db.get(a,'-')} onInterval={on_u} | "
                      f"v layer da={db and da.get(b,'-')},db={db.get(b,'-')} onInterval={on_v}")
            break  # one direction per edge

if __name__=="__main__":
    import sys
    for g6 in (sys.argv[1:] or ["I??E@fKJ_","I??CF@wFo"]):
        dump(g6)
