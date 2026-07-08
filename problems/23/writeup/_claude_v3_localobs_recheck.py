"""V3: independent LocalObstruction(m) enumeration, m=6..10.
LocalObstruction(m): connected bipartite F with m-1 edges (n=5..m vertices),
m distinct vertex pairs at d_F=4, supports (union of length-4 F-geodesic edges)
union to E(F), every edge in >=2 supports, pair-graph H triangle-free.
Report: #(F footprints with >=1 witness), #(atom-sets), and for m=9 the explicit witness.
"""
import subprocess, sys
from collections import deque, Counter
from itertools import combinations

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def parse_graph6(line):
    data=[ord(c)-63 for c in line.strip()]
    n=data[0]; bits=[]
    for x in data[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    adj=[[] for _ in range(n)]; idx=0; edges=[]
    for j in range(1,n):
        for i in range(j):
            if bits[idx]: adj[i].append(j); adj[j].append(i); edges.append((i,j))
            idx+=1
    return n,adj,edges

def bfs(n,adj,s):
    d=[-1]*n; d[s]=0; q=deque([s])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if d[y]<0: d[y]=d[x]+1; q.append(y)
    return d

def run(m):
    e = m-1
    footprints = 0
    atomsets = 0
    witnesses = []
    cand_graphs = 0
    for n in range(5, m+1):
        p = subprocess.run([GENG,"-q","-c","-b",str(n),f"{e}:{e}"],
                           capture_output=True,text=True)
        for line in p.stdout.splitlines():
            nn,adj,edges = parse_graph6(line)
            dist=[bfs(nn,adj,s) for s in range(nn)]
            pairs=[]
            for u in range(nn):
                for v in range(u+1,nn):
                    if dist[u][v]==4:
                        sup=set()
                        for (a,b) in edges:
                            for (x,y) in ((a,b),(b,a)):
                                if dist[u][x]+1+dist[y][v]==4:
                                    sup.add((a,b)); break
                        pairs.append(((u,v),frozenset(sup)))
            if len(pairs) < m: continue
            cand_graphs += 1
            alledges=frozenset(edges)
            found_this_F=False
            for combo in combinations(range(len(pairs)), m):
                # union covers all edges, each edge >=2
                cnt=Counter()
                for i in combo:
                    for ed in pairs[i][1]: cnt[ed]+=1
                if len(cnt)!=len(edges): continue
                if min(cnt.values())<2: continue
                # H triangle-free: pairs as edges
                pset=set(pairs[i][0] for i in combo)
                nbrH={}
                for (u,v) in pset:
                    nbrH.setdefault(u,set()).add(v); nbrH.setdefault(v,set()).add(u)
                tri=False
                for (u,v) in pset:
                    if nbrH[u] & nbrH[v]: tri=True; break
                if tri: continue
                atomsets+=1
                found_this_F=True
                if len(witnesses)<3:
                    witnesses.append((line.strip(), n, edges, [pairs[i][0] for i in combo]))
            if found_this_F: footprints+=1
    print(f"m={m}: candidate graphs (>= m dist-4 pairs) = {cand_graphs}, "
          f"footprints with witness = {footprints}, atom-sets = {atomsets}")
    for w in witnesses:
        print("   witness:", w)

for m in range(6, int(sys.argv[1])+1):
    run(m)
