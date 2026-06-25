#!/usr/bin/env python3
"""
Computational probe of the (unproven) CF inequality from GPT Q9:
   tau_K(G) <= (N^2/5 - e)/2      (+ o(N^2))
for triangle-free G in the medium band (density 0.2486..0.3197).

tau_K(G) = min over phi: V -> V(Clebsch) of sum_{uv in E} cost(phi(u),phi(v)),
cost = (4 - |a xor b|)/2 in {0,1,2} for |a xor b| in {4,2,0}  (a,b even subsets of [5]).
A homomorphism G->Clebsch gives tau_K=0.  We UPPER-bound tau_K by greedy local search
with random restarts (an upper bound is exactly what CF needs).

Test on: C5[n] (tau_K=0, RHS=0, tight); structured non-C5-hom band hard cores
(Petersen[2], Cayley(Z20)); random triangle-free band graphs N=15,20,25.
Report tau_K_ub and RHS=(N^2/5-e)/2 and whether tau_K_ub <= RHS.
"""
import itertools, random
random.seed(11)

# Clebsch labels = 16 even subsets of [5], as 5-bit masks with even popcount
LABELS = [m for m in range(32) if bin(m).count('1') % 2 == 0]
assert len(LABELS) == 16

def cost(a, b):
    return (4 - bin(a ^ b).count('1')) // 2  # in {0,1,2}

# precompute cost table over the 16 labels
LC = {(a, b): cost(a, b) for a in LABELS for b in LABELS}

def tau_K_ub(N, adj, restarts=60, sweeps=40):
    """greedy local-search upper bound on tau_K."""
    nbr = [[] for _ in range(N)]
    for u in range(N):
        for v in range(N):
            if (adj[u] >> v) & 1:
                nbr[u].append(v)
    best = None
    for _ in range(restarts):
        lab = [random.choice(LABELS) for _ in range(N)]
        improved = True
        sw = 0
        while improved and sw < sweeps:
            improved = False
            sw += 1
            order = list(range(N)); random.shuffle(order)
            for u in order:
                # pick label minimizing sum of costs to neighbors
                bestc, bestl = None, lab[u]
                for L in LABELS:
                    c = 0
                    for w in nbr[u]:
                        c += LC[(L, lab[w])]
                    if bestc is None or c < bestc:
                        bestc, bestl = c, L
                if bestl != lab[u]:
                    lab[u] = bestl
                    improved = True
        tot = 0
        for u in range(N):
            for w in nbr[u]:
                if w > u:
                    tot += LC[(lab[u], lab[w])]
        if best is None or tot < best:
            best = tot
    return best

def edges_to_adj(N, edges):
    adj = [0] * N
    for u, v in edges:
        adj[u] |= 1 << v; adj[v] |= 1 << u
    return adj

def c5_blowup(n):
    parts = [list(range(i*n, i*n+n)) for i in range(5)]
    E = []
    for p in range(5):
        for u in parts[p]:
            for v in parts[(p+1)%5]:
                E.append((u, v))
    return 5*n, E

def petersen2():
    E=[(0,2),(0,3),(1,2),(1,3),(2,4),(2,5),(3,4),(3,5),(4,6),(4,7),(5,6),(5,7),
       (6,8),(6,9),(7,8),(7,9),(8,0),(8,1),(9,0),(9,1),(10,14),(10,15),(11,14),(11,15),
       (14,18),(14,19),(15,18),(15,19),(18,12),(18,13),(19,12),(19,13),(12,16),(12,17),
       (13,16),(13,17),(16,10),(16,11),(17,10),(17,11),(0,10),(0,11),(1,10),(1,11),
       (2,12),(2,13),(3,12),(3,13),(4,14),(4,15),(5,14),(5,15),(6,16),(6,17),(7,16),(7,17),
       (8,18),(8,19),(9,18),(9,19)]
    return 20, E

def cayley(N, conn):
    E=[]
    for v in range(N):
        for s in conn:
            w=(v+s)%N
            if v<w: E.append((v,w))
            elif w<v: E.append((w,v))
    return N, list(set(E))

def rand_band(N, elo, ehi):
    """random triangle-free graph with edge count in [elo,ehi]."""
    for _ in range(200):
        adj=[0]*N; pairs=[(u,v) for u in range(N) for v in range(u+1,N)]
        random.shuffle(pairs); e=0; E=[]
        target=random.randint(elo,ehi)
        for (u,v) in pairs:
            if e>=target: break
            if adj[u]&adj[v]: continue
            adj[u]|=1<<v; adj[v]|=1<<u; E.append((u,v)); e+=1
        if elo<=e<=ehi:
            return N,E,e
    return None

def band_e(N):
    C2=N*(N-1)/2
    return int(0.2486*C2)+1, int(0.3197*C2)

def report(tag, N, edges):
    adj=edges_to_adj(N,edges); e=len(set((min(a,b),max(a,b)) for a,b in edges))
    rhs=(N*N/5 - e)/2
    tk=tau_K_ub(N,adj)
    dens=2*e/(N*(N-1))
    ok = tk <= rhs + 1e-9
    print(f"  {tag:22s} N={N} e={e} dens={dens:.4f}  tau_K_ub={tk}  RHS=(N^2/5-e)/2={rhs:.1f}  CF_ok={ok}")
    return ok

def main():
    print("CF test: tau_K_ub <= (N^2/5 - e)/2 ?  (tau_K_ub = local-search upper bound)")
    print("Reference (C5[n], should be tight tau_K=0=RHS):")
    for n in (2,3,4,5):
        N,E=c5_blowup(n); report(f"C5[{n}]",N,E)
    print("Structured non-C5-hom band hard cores:")
    N,E=petersen2(); report("Petersen[2]",N,E)
    N,E=cayley(20,[1,4,9]); report("Cay(Z20,1,4,9)",N,E)
    N,E=cayley(20,[2,5,9]); report("Cay(Z20,2,5,9)",N,E)
    print("Random triangle-free band graphs:")
    fails=0; tested=0
    for N in (15,20,25):
        lo,hi=band_e(N)
        for _ in range(12):
            r=rand_band(N,lo,hi)
            if r is None: continue
            N2,E,e=r
            tested+=1
            if not report(f"rand N={N}",N2,E): fails+=1
    print(f"\nrandom band: tested={tested}, CF_FAILS(tau_K_ub>RHS)={fails}")
    print("(note: tau_K_ub is an UPPER bound; CF_ok=True is genuine support, CF_ok=False may be heuristic slack)")
    print("DONE")

if __name__=="__main__":
    main()
