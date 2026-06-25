import itertools, pulp, networkx as nx
from fractions import Fraction

def odd_cycles_edges(G):
    cycles = []
    for cyc in nx.simple_cycles(G):
        L = len(cyc)
        if L >= 3 and L % 2 == 1:
            es = frozenset(frozenset((cyc[i], cyc[(i+1)%L])) for i in range(L))
            cycles.append((es, L, tuple(cyc)))
    return cycles

def fractional_odd_cycle_packing(G):
    cycles = odd_cycles_edges(G)
    if not cycles:
        return 0.0, 0
    prob = pulp.LpProblem("nu_star", pulp.LpMaximize)
    yv = [pulp.LpVariable("y%d"%i, lowBound=0) for i in range(len(cycles))]
    prob += pulp.lpSum(yv)
    edges = [frozenset(e) for e in G.edges()]
    for e in edges:
        terms = [yv[i] for i,(es,L,_) in enumerate(cycles) if e in es]
        if terms:
            prob += pulp.lpSum(terms) <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(prob.objective), len(cycles)

def tau_odd_transversal(G):
    cycles = odd_cycles_edges(G)
    if not cycles:
        return 0
    prob = pulp.LpProblem("tau", pulp.LpMinimize)
    edges = [frozenset(e) for e in G.edges()]
    xe = {e: pulp.LpVariable("x%d"%i, cat="Binary") for i,e in enumerate(edges)}
    prob += pulp.lpSum(xe.values())
    for (es,L,_) in cycles:
        prob += pulp.lpSum(xe[e] for e in es) >= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return round(pulp.value(prob.objective))

def tau_star_fractional(G):
    # fractional odd-cycle EDGE cover (LP relaxation of tau). By LP duality = nu*.
    cycles = odd_cycles_edges(G)
    if not cycles:
        return 0.0
    prob = pulp.LpProblem("tau_star", pulp.LpMinimize)
    edges = [frozenset(e) for e in G.edges()]
    xe = {e: pulp.LpVariable("x%d"%i, lowBound=0) for i,e in enumerate(edges)}
    prob += pulp.lpSum(xe.values())
    for (es,L,_) in cycles:
        prob += pulp.lpSum(xe[e] for e in es) >= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(prob.objective)

def build_subdiv_k23(subcounts):
    # subcounts: dict (i,j)-> number of internal subdivision vertices on edge a_i b_j
    # A = {('a',0),('a',1)}, B = {('b',0),('b',1),('b',2)}
    G = nx.Graph()
    A = [('a',0),('a',1)]
    B = [('b',0),('b',1),('b',2)]
    for v in A+B: G.add_node(v)
    for i in range(2):
        for j in range(3):
            s = subcounts[(i,j)]
            path = [A[i]] + [('s',i,j,k) for k in range(s)] + [B[j]]
            for u,w in zip(path, path[1:]):
                G.add_edge(u,w)
    return G

# Search for a 13-vertex subdivided K_{2,3} with tau=4 and check nu*, kappa proxies.
# total vertices = 5 + sum(subcounts). need sum = 8.
best = []
from itertools import product
# each edge gets 0..2 subdivisions; constrain sum==8 across 6 edges
for sc in product(range(0,4), repeat=6):
    if sum(sc) != 8: continue
    subcounts = {(i,j): sc[3*i+j] for i in range(2) for j in range(3)}
    G = build_subdiv_k23(subcounts)
    if not nx.is_connected(G): continue
    # triangle-free? girth check
    has_tri = any(len(c)==3 for c in nx.simple_cycles(G))
    if has_tri: continue
    # 2-connected?
    if not nx.is_biconnected(G): continue
    N = G.number_of_nodes()
    if N != 13: continue
    tau = tau_odd_transversal(G)
    if tau != 4: continue
    nu, ncyc = fractional_odd_cycle_packing(G)
    best.append((sc, N, tau, nu, ncyc, G.number_of_edges()))

print("Found", len(best), "subdivided-K23 N=13 tau=4 atoms")
for (sc,N,tau,nu,ncyc,m) in best[:30]:
    target = 25*tau*tau/(N*N)
    print("subcounts", sc, "N", N, "E", m, "tau", tau, "nu*", round(nu,4),
          "target25t2/N2", round(target,4), "nu*>=target?", nu+1e-9>=target)
