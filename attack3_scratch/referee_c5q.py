import pulp, networkx as nx, numpy as np

# C5[q] = blow-up of C5: 5 groups of q vertices, group i fully joined to group i+1 (mod 5).
def C5_blowup(q):
    G = nx.Graph()
    groups = [[(i,k) for k in range(q)] for i in range(5)]
    for v in [x for g in groups for x in g]:
        G.add_node(v)
    for i in range(5):
        for a in groups[i]:
            for b in groups[(i+1)%5]:
                G.add_edge(a,b)
    return G

def odd_cycles_edges(G, cap=200000):
    cycles = []
    cnt=0
    for cyc in nx.simple_cycles(G):
        L = len(cyc)
        if L >= 3 and L % 2 == 1:
            es = frozenset(frozenset((cyc[i], cyc[(i+1)%L])) for i in range(L))
            cycles.append((es, L)); cnt+=1
            if cnt>=cap: break
    return cycles

def nu_star(G):
    cycles = odd_cycles_edges(G)
    if not cycles: return 0.0
    prob = pulp.LpProblem("nu", pulp.LpMaximize)
    yv = [pulp.LpVariable("y%d"%i, lowBound=0) for i in range(len(cycles))]
    prob += pulp.lpSum(yv)
    from collections import defaultdict
    byedge = defaultdict(list)
    for i,(es,L) in enumerate(cycles):
        for e in es: byedge[e].append(yv[i])
    for e,t in byedge.items():
        prob += pulp.lpSum(t) <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(prob.objective)

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

for q in [1,2]:
    G = C5_blowup(q)
    N = G.number_of_nodes()
    nu = nu_star(G)
    tau = tau_int(G)
    target = 25.0*tau*tau/(N*N)
    print("C5[%d]: N=%d  tau=%d  nu*=%.4f  25t^2/N^2=%.4f  ratio nu*/target=%.4f" %
          (q,N,tau,nu,target, nu/target))
    # spectral
    nodes=list(G.nodes()); idx={v:i for i,v in enumerate(nodes)}
    A=np.zeros((N,N))
    for u,v in G.edges(): A[idx[u],idx[v]]=1; A[idx[v],idx[u]]=1
    ev=np.linalg.eigvalsh(A)
    # B = bipartite part of a max cut -- for C5[q] take cut between {0,2 groups}? approximate: use a max cut
    print("   lambda_min(K)=%.4f lambda1(K)=%.4f" % (ev.min(), ev.max()))
    E3 = tau*tau/(N*(-ev.min()))
    print("   E3=t^2/(N*(-lmin))=%.4f  E3/target=%.4f  (claim ~0.46 at q=2)" % (E3, E3/target))
