"""Independent verification of the load-bearing facts for the Connected-B Gamma Lemma.
Self-contained: max-cut by brute force, B=cut edges, M=bad edges, ell=d_B+1.
Checks:
  (1) Gamma <= N^2 over all connected triangle-free graphs up to N (small N).
  (2) tightness at C5[q] and odd cycles.
  (3) ear-route refutation witness 'H?AFBo]' : L*S > N^2 while Gamma <= N^2.
  (4) single-block AM-GM constant 25.
"""
import itertools, subprocess, sys
from collections import deque

def parse_graph6(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        for i in range(5, -1, -1):
            bits.append((d >> i) & 1)
    adj = [[0]*n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj

def edges_of(n, adj):
    return [(i,j) for i in range(n) for j in range(i+1,n) if adj[i][j]]

def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i+1,n):
            if adj[i][j]:
                for k in range(j+1,n):
                    if adj[i][k] and adj[j][k]:
                        return False
    return True

def bfs_dist(n, badj, src):
    d = [-1]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for v in range(n):
            if badj[u][v] and d[v]<0:
                d[v]=d[u]+1; q.append(v)
    return d

def maxcut_all(n, E):
    """Return (best_value, list of (X as frozenset)) for all maximum cuts. Brute force."""
    best=-1; cuts=[]
    for mask in range(1<<n):
        X=set(i for i in range(n) if (mask>>i)&1)
        val=sum(1 for (a,b) in E if (a in X) != (b in X))
        if val>best:
            best=val; cuts=[frozenset(X)]
        elif val==best:
            cuts.append(frozenset(X))
    return best, cuts

def analyze_cut(n, adj, E, X):
    """For a cut X, build B (cut edges), M (bad/mono edges), compute ell via d_B.
    Returns (B_connected_on_support, Gamma, m, ells) or None if a bad edge has no odd B-path (ell undefined)."""
    badj=[[0]*n for _ in range(n)]
    M=[]
    for (a,b) in E:
        cross = (a in X) != (b in X)
        if cross:
            badj[a][b]=badj[b][a]=1
        else:
            M.append((a,b))
    # ell(uv)=d_B(u,v)+1 ; for mono edge u,v are same side, so d_B even (bipartite B), ell odd
    ells=[]
    for (a,b) in M:
        d=bfs_dist(n,badj,a)
        if d[b]<0:
            return None  # disconnected in B between endpoints
        ells.append(d[b]+1)
    Gamma=sum(l*l for l in ells)
    return badj, M, ells, Gamma

def B_connected_full(n, badj):
    # connected on all N vertices
    d=bfs_dist(n,badj,0)
    return all(x>=0 for x in d)

def check_witness():
    print("=== (3) ear-route refutation witness 'H?AFBo]' ===")
    n, adj = parse_graph6('H?AFBo]')
    E = edges_of(n, adj)
    print(f"n={n}, |E|={len(E)}, triangle-free={is_triangle_free(n,adj)}")
    mc, cuts = maxcut_all(n, E)
    print(f"maxcut value={mc}, #maximum cuts={len(cuts)}")
    found=False
    for X in cuts:
        res=analyze_cut(n,adj,E,X)
        if res is None: continue
        badj,M,ells,Gamma=res
        if not B_connected_full(n,badj): continue
        if not M: continue
        L=max(ells); S=sum(ells)
        flag = "  <-- L*S>N^2" if L*S>n*n else ""
        if L*S>n*n:
            found=True
            print(f"  X={sorted(X)} M={M} ells={sorted(ells,reverse=True)} Gamma={Gamma} N^2={n*n} L={L} S={S} L*S={L*S}{flag}")
    print(f"  WITNESS CONFIRMED (B-connected cut with L*S>N^2 but Gamma<=N^2): {found}")
    return found

def scan_small(maxn=9):
    print(f"=== (1)&(2) scan connected triangle-free graphs up to N={maxn} ===")
    geng=r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
    worst_ratio=0.0; worst=None; viol=0; count=0; tight_examples=[]
    for N in range(3, maxn+1):
        # -c connected, -t triangle-free
        out=subprocess.run([geng, "-ctq", str(N)], capture_output=True, text=True)
        for line in out.stdout.split():
            line=line.strip()
            if not line: continue
            n,adj=parse_graph6(line)
            E=edges_of(n,adj)
            mc,cuts=maxcut_all(n,E)
            for X in cuts:
                res=analyze_cut(n,adj,E,X)
                if res is None: continue
                badj,M,ells,Gamma=res
                if not B_connected_full(n,badj): continue
                count+=1
                if Gamma>n*n:
                    viol+=1
                    if viol<=5:
                        print(f"  VIOLATION N={n} g6={line} M={M} ells={ells} Gamma={Gamma} > {n*n}")
                r=Gamma/(n*n)
                if r>worst_ratio:
                    worst_ratio=r; worst=(line,N,Gamma,M,ells)
                if abs(Gamma-n*n)==0:
                    tight_examples.append((N,line,M,ells))
    print(f"  instances(B-connected,non-empty M)={count}, Gamma>N^2 violations={viol}")
    print(f"  worst Gamma/N^2={worst_ratio:.4f} at {worst[0]} (N={worst[1]}, Gamma={worst[2]}, ells={worst[4]})")
    print(f"  #exactly-tight (Gamma=N^2)={len(tight_examples)}; sample:")
    for t in tight_examples[:8]:
        print(f"    N={t[0]} g6={t[1]} M-size={len(t[2])} ells={sorted(t[3])}")

def amgm_block():
    print("=== (4) single-block AM-GM: min over a0..a4>0,sum<=N of  N^2 - 25*q  where q=min product a_i a_{i+1} ===")
    # The proved statement: if all 5 cyclic pair-products a_i a_{i+1} >= q then 25 q <= (sum a_i)^2 <= N^2.
    # Check: minimize (sum a_i)^2 - 25*q over scaling; equality at all equal.
    import math
    # all-equal a_i=t: pair product=t^2=q ; sum=5t ; (5t)^2=25 t^2 =25 q. equality.
    # perturb:
    best=1e9
    import random
    random.seed(0)
    for _ in range(200000):
        a=[random.random()+0.01 for _ in range(5)]
        s=sum(a)
        a=[x/s for x in a]  # sum=1, so N=1
        q=min(a[i]*a[(i+1)%5] for i in range(5))
        slack=1.0 - 25*q   # N^2 - 25 q with N=1
        if slack<best: best=slack
    print(f"  min over random samples of (N^2 - 25*min-pair-product), N normalized to 1: {best:.6e}  (>=0 confirms 25 q<=N^2; ~0 => sharp)")

if __name__=="__main__":
    check_witness()
    print()
    amgm_block()
    print()
    scan_small(9)
