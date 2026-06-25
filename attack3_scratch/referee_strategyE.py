import itertools, pulp, networkx as nx, numpy as np
from fractions import Fraction

# ---- canonical K23-N13 from rg_referee_k23.py ----
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

def to_nx(N, A):
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for u in range(N):
        for v in range(N):
            if u < v and (A[u]>>v)&1:
                G.add_edge(u, v)
    return G

def odd_cycles_edges(G):
    cycles = []
    for cyc in nx.simple_cycles(G):
        L = len(cyc)
        if L >= 3 and L % 2 == 1:
            es = frozenset(frozenset((cyc[i], cyc[(i+1)%L])) for i in range(L))
            cycles.append((es, L))
    return cycles

def nu_star(G):
    cycles = odd_cycles_edges(G)
    if not cycles: return 0.0, 0
    prob = pulp.LpProblem("nu", pulp.LpMaximize)
    yv = [pulp.LpVariable("y%d"%i, lowBound=0) for i in range(len(cycles))]
    prob += pulp.lpSum(yv)
    for e in [frozenset(e) for e in G.edges()]:
        t = [yv[i] for i,(es,L) in enumerate(cycles) if e in es]
        if t: prob += pulp.lpSum(t) <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(prob.objective), len(cycles)

def tau_int(G):
    cycles = odd_cycles_edges(G)
    if not cycles: return 0
    prob = pulp.LpProblem("tau", pulp.LpMinimize)
    xe = {frozenset(e): pulp.LpVariable("x%d"%i, cat="Binary") for i,e in enumerate(G.edges())}
    prob += pulp.lpSum(xe.values())
    for (es,L) in cycles:
        prob += pulp.lpSum(xe[e] for e in es) >= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return round(pulp.value(prob.objective))

def maxcut_bruteforce(G):
    nodes = list(G.nodes()); n = len(nodes)
    idx = {v:i for i,v in enumerate(nodes)}
    edges = [(idx[u],idx[v]) for u,v in G.edges()]
    best=-1; bsol=None
    for mask in range(1<<(n-1)):
        s=[(mask>>i)&1 for i in range(n)]
        c=sum(1 for (u,v) in edges if s[u]!=s[v])
        if c>best: best=c; bsol=s
    return best, bsol, nodes

G = to_nx(*gpt_k23())
N = G.number_of_nodes(); E = G.number_of_edges()
nu, ncyc = nu_star(G)
tau = tau_int(G)
mc, sol, nodes = maxcut_bruteforce(G)
beta = E - mc
print("=== K23-N13 ===")
print("N=%d  E=%d  maxcut=%d  beta=%d  #odd_cycles=%d" % (N,E,mc,beta,ncyc))
print("tau(int min odd transversal) =", tau)
print("nu* (frac odd-cycle packing) =", nu, " (claim: 10/3 = %.4f)"%(10/3))

# bad edges M of the max cut
side = {nodes[i]: sol[i] for i in range(len(nodes))}
M = [(u,v) for u,v in G.edges() if side[u]==side[v]]
B = nx.Graph(); B.add_nodes_from(G.nodes())
for u,v in G.edges():
    if side[u]!=side[v]: B.add_edge(u,v)
m = len(M)
print("|M| (bad edges of a max cut) =", m, " M=", M)

# ---- kappa* / target numbers ----
t = tau
target_D25 = 25.0*t*t/(N*N)
print("\n--- D25 numbers ---")
print("25 t^2 / N^2 =", target_D25, " (claim n^2/(25t)=%.4f i.e. 169/100)"%(N*N/(25*t)))
print("nu* >= 25 t^2/N^2 ?  %.4f >= %.4f  -> %s" % (nu, target_D25, nu+1e-9>=target_D25))
print("nu* <= N^2/25 ?  %.4f <= %.4f  -> %s" % (nu, N*N/25.0, nu<=N*N/25.0+1e-9))

# ---- Spectral candidates E1, E2, E3 (colleague's) ----
# B = bipartite cut-part. lambda1(B) = largest adjacency eigenvalue, lambda_min = most negative.
def adj_eigs(H):
    nodes_h = list(H.nodes()); idx={v:i for i,v in enumerate(nodes_h)}
    Amat = np.zeros((len(nodes_h),len(nodes_h)))
    for u,v in H.edges():
        Amat[idx[u],idx[v]] = 1; Amat[idx[v],idx[u]] = 1
    ev = np.linalg.eigvalsh(Amat)
    return ev.min(), ev.max()
lmin_B, lmax_B = adj_eigs(B)
lmin_K, lmax_K = adj_eigs(G)
print("\n--- spectral ---")
print("lambda1(B)=%.4f  lambda_min(B)=%.4f" % (lmax_B, lmin_B))
print("lambda1(K)=%.4f  lambda_min(K)=%.4f" % (lmax_K, lmin_K))
E1 = t*t/(N*lmax_B) if lmax_B>0 else float('inf')
E2 = (-lmin_K)*t/N
E3 = t*t/(N*(-lmin_K)) if lmin_K<0 else float('inf')
print("E1 = t^2/(N*lambda1(B)) = %.4f" % E1)
print("E2 = (-lmin)*t/N        = %.4f" % E2)
print("E3 = t^2/(N*(-lmin))    = %.4f" % E3)
print("E1<=nu*? %s   E3<=nu*? %s   (claim: both valid lower bounds)" % (E1<=nu+1e-9, E3<=nu+1e-9))
print("E1>=target? %s  E3>=target? %s  (claim: both UNDERSHOOT)" % (E1>=target_D25, E3>=target_D25))
print("E1/target=%.3f  E3/target=%.3f" % (E1/target_D25, E3/target_D25))
