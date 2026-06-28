"""Find & dump an N=10 census FULL-ZMU violation (zero-mu edge, both T>0) on loads-cut.
Show T(u),T(v),N and the layer geometry. Contrast: here neither endpoint saturated => A-alltie safe.
Goal: understand the geometric config FULL-ZMU allows, and why saturation T=N would break it."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads
from _zmu import mu_edges

def bfs(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        x=q.popleft()
        for w in adj[x]:
            if side[w]!=side[x] and w not in d: d[w]=d[x]+1; q.append(w)
    return d

def find_and_dump(limit=2):
    outg=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
    shown=0
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
        M=info['M']; ell=info['ell']; cyc=info['cyc']; mu=mu_edges(info)
        for e,val in mu.items():
            if val!=0: continue
            u,v=tuple(e)
            if T[u]>0 and T[v]>0:
                print(f"\n### {g6} N={N} side={side} M={M} ell={[ell[f] for f in M]}")
                print(f"  T={[str(t) for t in T]}")
                print(f"  FULL-ZMU viol: zero-mu edge ({u},{v}), T(u)={T[u]}, T(v)={T[v]} (neither=N={N})")
                for f in M:
                    s,t=f; da=bfs(adj,side,s); db=bfs(adj,side,t); L=ell[f]-1
                    onu=(da.get(u,99)+db.get(u,99)==L); onv=(da.get(v,99)+db.get(v,99)==L)
                    print(f"    f=({s},{t}) L={L}: u={u} (da={da.get(u,'-')},db={db.get(u,'-')},onI={onu}) "
                          f"v={v} (da={da.get(v,'-')},db={db.get(v,'-')},onI={onv})")
                shown+=1
                break
        if shown>=limit: break

if __name__=="__main__":
    find_and_dump(3)
