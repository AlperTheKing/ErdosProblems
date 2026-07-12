# Variant: per-vertex capacity min(d(w)/10, N/25)  (x50 scale: min(5*d(w), 2N)).
# Feasible => beta <= N^2/25 still (termwise min <= N/25). More local Hall candidate.
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\discharging")
from flow_check import (maxcut_enumerate, side_of, Dinic, build_adj,
                        petersen, grotzsch, chvatal, clebsch, gp, blowup, C5, C7,
                        rand_maximal_tf, rand_sparse_tf)
from collections import deque

def transport_check_cap(N, adj, side, r, capfun):
    m = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(N)]
    beta2 = sum(m)
    supply = [25 * mv for mv in m]
    badj = [[w for w in adj[v] if side[w] != side[v]] for v in range(N)]
    balls = []
    for v in range(N):
        dist = {v: 0}
        q = deque([v])
        while q:
            u = q.popleft()
            if dist[u] == r:
                continue
            for w in badj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        balls.append(sorted(dist.keys()))
    D = Dinic(2 * N + 2)
    src, sink = 0, 2 * N + 1
    for v in range(N):
        if supply[v] > 0:
            D.add(src, 1 + v, supply[v])
        D.add(N + 1 + v, sink, capfun(v))
    for v in range(N):
        if supply[v] > 0:
            for w in balls[v]:
                D.add(1 + v, N + 1 + w, 10 ** 18)
    need = 25 * beta2
    fl = D.maxflow(src, sink)
    return fl == need, need - fl

def run(name, N, edges, cap_cuts=100):
    adj = build_adj(N, edges)
    deg = [len(adj[v]) for v in range(N)]
    mc, masks = maxcut_enumerate(N, edges, cap_cuts=cap_cuts)
    beta = len(edges) - mc
    if beta == 0:
        print(f"{name}: beta=0 skip"); return
    capfun = lambda v: min(5 * deg[v], 2 * N)
    feas = 0
    worst = None
    for mask in masks:
        side = side_of(mask, N)
        ok, defect = transport_check_cap(N, adj, side, 2, capfun)
        if ok: feas += 1
        elif worst is None or defect > worst[1]:
            worst = (mask, defect)
    v = "ALL" if feas == len(masks) else ("SOME(%d/%d)" % (feas, len(masks)) if feas else "NONE")
    print(f"{name}: N={N} beta={beta} degcap r=2 -> {v}" + (f" defect50x={worst[1]}" if worst else ""))
    sys.stdout.flush()

if __name__ == "__main__":
    run("petersen", *petersen())
    run("grotzsch", *grotzsch())
    run("chvatal", *chvatal())
    run("clebsch", *clebsch())
    run("GP(7,2)", *gp(7, 2))
    run("GP(9,2)", *gp(9, 2))
    run("C5", 5, C5)
    for w in [(1,1,1,1,1),(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),(1,1,1,1,2),
              (1,1,1,2,2),(1,2,2,3,3),(2,2,3,3,3),(1,3,1,3,1),(2,3,2,3,2),
              (4,4,1,4,4),(1,4,4,1,4),(3,4,3,4,3)]:
        run(f"C5blow{w}", *blowup(C5, list(w)))
    run("C7blow2", *blowup(C7, [2]*7))
    run("petersen_blow2", *blowup(petersen()[1], [2]*10))
    bad = 0
    for N in (10, 12, 14, 16):
        for seed in range(40):
            n, E = rand_maximal_tf(N, 1000 * N + seed)
            adj = build_adj(n, E)
            deg = [len(adj[x]) for x in range(n)]
            mc, masks = maxcut_enumerate(n, E, cap_cuts=60)
            beta = len(E) - mc
            if beta == 0: continue
            capfun = lambda v: min(5 * deg[v], 2 * n)
            allok = True
            for mask in masks:
                side = side_of(mask, n)
                ok, defect = transport_check_cap(n, adj, side, 2, capfun)
                if not ok:
                    allok = False
                    print(f"  !! degcap fail maxTF_N{N}_s{seed} mask={mask} defect={defect}")
                    break
            bad += 0 if allok else 1
    for N in (12, 14, 16):
        for seed in range(30):
            n, E = rand_sparse_tf(N, (N * N) // 5, 7000 * N + seed)
            adj = build_adj(n, E)
            deg = [len(adj[x]) for x in range(n)]
            mc, masks = maxcut_enumerate(n, E, cap_cuts=60)
            beta = len(E) - mc
            if beta == 0: continue
            capfun = lambda v: min(5 * deg[v], 2 * n)
            for mask in masks:
                side = side_of(mask, n)
                ok, defect = transport_check_cap(n, adj, side, 2, capfun)
                if not ok:
                    bad += 1
                    print(f"  !! degcap fail spTF_N{N}_s{seed} mask={mask} defect={defect}")
                    break
    print(f"DEGCAP RANDOM DONE bad={bad}")
