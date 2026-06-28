r"""Verify the CONSTRUCTIVE step of the support-disjointness proof:
For every bad edge f and every B-edge uv with u,v BOTH on f's geodesic interval
(d_a(u)+d_b(u)=L and d_a(v)+d_b(v)=L), the edge uv IS an edge of some shortest a-b path,
hence contributes positive mu (i.e. uv in cyc-edges of f). This is the contrapositive used in the proof.
We check: enumerate all (f, B-edge uv) with both endpoints on interval; confirm uv appears as a
consecutive pair in at least one geodesic P in cyc[f] (=> mu(uv)>0). 0 failures => proof step valid.
Loads-cut census N<=11 + ALL connected cuts N<=8."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, Bconn, geos

def bfs(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        x=q.popleft()
        for w in adj[x]:
            if side[w]!=side[x] and w not in d: d[w]=d[x]+1; q.append(w)
    return d

def check(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    fails=0; checked=0
    for f in M:
        s,t=f
        Ps=geos(adj,side,s,t)
        if not Ps: continue
        L=len(Ps[0])-1
        da=bfs(adj,side,s); db=bfs(adj,side,t)
        # geodesic consecutive-edge set
        gedges=set()
        for P in Ps:
            for i in range(len(P)-1):
                gedges.add((min(P[i],P[i+1]),max(P[i],P[i+1])))
        # all B-edges with both endpoints on interval
        for u in range(n):
            for v in adj[u]:
                if v<=u or side[u]==side[v]: continue
                onu=(da.get(u,99)+db.get(u,99)==L); onv=(da.get(v,99)+db.get(v,99)==L)
                if onu and onv:
                    checked+=1
                    if (u,v) not in gedges:
                        fails+=1
    return checked,fails

if __name__=="__main__":
    print("=== proof-step check: both-on-interval B-edge => is a geodesic edge (mu>0) ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tc=0; tf=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            c,f=check(info['n'],info['adj'],info['side']); tc+=c; tf+=f
        print(f"  loads-cut census N={nn}: both-on-interval B-edges checked={tc} NOT-a-geodesic-edge={tf}",flush=True)
    for nn in [7,8]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tc=0; tf=0
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                c,f=check(n,adj,side); tc+=c; tf+=f
        print(f"  ALL conn cuts N={nn}: checked={tc} NOT-a-geodesic-edge={tf}",flush=True)
