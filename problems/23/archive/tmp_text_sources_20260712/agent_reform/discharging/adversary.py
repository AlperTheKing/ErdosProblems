# Adversarial search against HALL-2 (uniform cap): score(G) = min over optimal cuts of
# t_min(cut) = smallest integer capacity t (x50 scale; lemma uses t=2N) with radius-2
# transport feasible. Counterexample iff score > 2N. Balanced C5 blow-ups: score == 2N.
import sys, random
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\discharging")
from flow_check import maxcut_enumerate, side_of, Dinic, blowup, C5
from collections import deque

def tmin_for_cut(N, adj, side):
    m = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(N)]
    beta2 = sum(m)
    if beta2 == 0:
        return 0
    supply = [25 * mv for mv in m]
    badj = [[w for w in adj[v] if side[w] != side[v]] for v in range(N)]
    balls = []
    for v in range(N):
        dist = {v: 0}
        q = deque([v])
        while q:
            u = q.popleft()
            if dist[u] == 2:
                continue
            for w in badj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        balls.append(sorted(dist.keys()))
    def feas(t):
        D = Dinic(2 * N + 2)
        src, sink = 0, 2 * N + 1
        for v in range(N):
            if supply[v] > 0:
                D.add(src, 1 + v, supply[v])
            D.add(N + 1 + v, sink, t)
        for v in range(N):
            if supply[v] > 0:
                for w in balls[v]:
                    D.add(1 + v, N + 1 + w, 10 ** 18)
        return D.maxflow(src, sink) == 25 * beta2
    lo, hi = 1, 25 * beta2   # t = 25*beta2 always feasible (one vertex could hold all? no; but sup per vertex <=25m<=25beta2; ball>=self+... ) safe upper: supply max per ball vertex
    # ensure hi feasible
    while not feas(hi):
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if feas(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

def graph_score(N, edges, cap_cuts=40):
    adjs = [set() for _ in range(N)]
    for a, b in edges:
        adjs[a].add(b); adjs[b].add(a)
    adj = [sorted(s) for s in adjs]
    mc, masks = maxcut_enumerate(N, edges, cap_cuts=cap_cuts)
    beta = len(edges) - mc
    if beta == 0:
        return 0, beta
    return min(tmin_for_cut(N, adj, side_of(msk, N)) for msk in masks), beta

def is_tf_after_add(adjs, i, j):
    return not (adjs[i] & adjs[j])

def hill_climb(N, iters, seed):
    rng = random.Random(seed)
    # start from a C5 blowup-ish partition graph
    w = [N // 5] * 5
    for k in range(N - 5 * (N // 5)):
        w[k] += 1
    _, edges = blowup(C5, w)
    edges = set(edges)
    adjs = [set() for _ in range(N)]
    for a, b in edges:
        adjs[a].add(b); adjs[b].add(a)
    best_score, beta = graph_score(N, list(edges))
    best_edges = set(edges)
    cur_score = best_score
    for it in range(iters):
        # random move
        if rng.random() < 0.5 and edges:
            e = rng.choice(list(edges))
            edges.discard(e)
            adjs[e[0]].discard(e[1]); adjs[e[1]].discard(e[0])
            undo = ("add", e)
        else:
            i, j = rng.randrange(N), rng.randrange(N)
            if i == j: continue
            i, j = min(i, j), max(i, j)
            if (i, j) in edges or not is_tf_after_add(adjs, i, j):
                continue
            edges.add((i, j))
            adjs[i].add(j); adjs[j].add(i)
            undo = ("del", (i, j))
        s, b = graph_score(N, list(edges))
        if s >= cur_score and b > 0:
            cur_score = s
            if s > best_score:
                best_score = s
                best_edges = set(edges)
                print(f"  N={N} it={it} new best score={s} (2N={2*N}) beta={b}")
                sys.stdout.flush()
                if s > 2 * N:
                    print("  *** HALL-2 COUNTEREXAMPLE ***", sorted(edges))
                    return best_score, best_edges
        else:
            # revert
            kind, e = undo
            if kind == "add":
                edges.add(e); adjs[e[0]].add(e[1]); adjs[e[1]].add(e[0])
            else:
                edges.discard(e); adjs[e[0]].discard(e[1]); adjs[e[1]].discard(e[0])
    return best_score, best_edges

def theta_family():
    # hubs 0,1; a paths of length2 via x; b paths of length3 via y-z; then small blowups
    out = []
    for a in range(0, 4):
        for b in range(1, 4):
            V = 2 + a + 2 * b
            E = []
            idx = 2
            for _ in range(a):
                E += [(0, idx), (1, idx)]; idx += 1
            for _ in range(b):
                E += [(0, idx), (idx, idx + 1), (1, idx + 1)]; idx += 2
            out.append((f"theta(a{a},b{b})", V, E))
    return out

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "theta":
        for name, V, E in theta_family():
            # base + uniform blowups by 2 and 3 while N<=21
            for t in (1, 2, 3):
                N2 = V * t
                if N2 > 21: continue
                if t == 1:
                    n, ee = V, E
                else:
                    n, ee = blowup(E, [t] * V)
                s, b = graph_score(n, ee, cap_cuts=60)
                flag = "***CE***" if s > 2 * n else "ok"
                print(f"{name} x{t}: N={n} beta={b} score={s} 2N={2*n} {flag}")
                sys.stdout.flush()
    elif mode == "climb":
        N = int(sys.argv[2]); iters = int(sys.argv[3]); seeds = int(sys.argv[4])
        overall = 0
        for sd in range(seeds):
            s, be = hill_climb(N, iters, 999 + sd)
            overall = max(overall, s)
            print(f"seed {sd}: best={s} (2N={2*N})")
            sys.stdout.flush()
        print(f"CLIMB N={N} overall best={overall} vs 2N={2*N} -> {'FALSIFIED' if overall>2*N else 'survives'}")
