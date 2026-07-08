"""V3 adversarial re-census (fresh code, integers only).

For every connected triangle-free graph on n vertices (5..NMAX), every MAXIMUM cut:
  - blue graph = cut (bichromatic) edges; bad edges = monochromatic edges
  - ell=5 atoms: bad edges with blue-dist(u,v) = 4
  - support P_e = set of blue edges lying on some length-4 blue geodesic u->v
  - checks:
    C1: support size never 5 (histogram)
    C2: per-edge multiplicity mu histogram (max over census)
    C3: Hall violations (bipartite matching atoms->support edges); count deficient cuts
    C4: endpoint position classes: each (atom, support edge) occupies exactly one
        position k in {1,2,3,4}; count anomalies
    C5: count graphs / max cuts (compare 11563 / 23449 for n=5..10)
  Also track Gamma-min max cuts separately (Gamma = sum ell(e)^2 over bad edges,
  ell = blue dist+1, infinite dist -> cut excluded from Gamma-min candidacy).
"""
import sys, subprocess
from collections import deque, Counter

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def parse_graph6(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj

def bfs_dist(n, nbr, src):
    d = [-1] * n
    d[src] = 0
    q = deque([src])
    while q:
        x = q.popleft()
        for y in nbr[x]:
            if d[y] < 0:
                d[y] = d[x] + 1
                q.append(y)
    return d

def hopcroft_matching(natoms, adjsets):
    # simple augmenting-path matching, atoms -> edges (edge ids hashable)
    match_edge = {}   # edge -> atom
    def try_aug(a, seen):
        for e in adjsets[a]:
            if e in seen: continue
            seen.add(e)
            if e not in match_edge or try_aug(match_edge[e], seen):
                match_edge[e] = a
                return True
        return False
    cnt = 0
    for a in range(natoms):
        if try_aug(a, set()):
            cnt += 1
    return cnt

def process_graph(n, adj):
    full = (1 << n) - 1
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if (adj[i] >> j) & 1]
    # max cut
    best = -1
    bestmasks = []
    for mask in range(1 << (n - 1)):   # vertex n-1 fixed on side 0
        c = 0
        for (i, j) in edges:
            c += ((mask >> i) ^ (mask >> j)) & 1
        if c > best:
            best = c; bestmasks = [mask]
        elif c == best:
            bestmasks.append(mask)
    out = []
    for mask in bestmasks:
        blue_nbr = [[] for _ in range(n)]
        bad = []
        for (i, j) in edges:
            if ((mask >> i) ^ (mask >> j)) & 1:
                blue_nbr[i].append(j); blue_nbr[j].append(i)
            else:
                bad.append((i, j))
        dist = [bfs_dist(n, blue_nbr, s) for s in range(n)]
        gamma = 0
        infinite = False
        atoms = []
        for (u, v) in bad:
            d = dist[u][v]
            if d < 0:
                infinite = True
                continue
            ell = d + 1
            gamma += ell * ell
            if d == 4:
                atoms.append((u, v))
        supports = []
        for (u, v) in atoms:
            sup = set()
            for a in range(n):
                for b in blue_nbr[a]:
                    if a < b:
                        for (x, y) in ((a, b), (b, a)):
                            du = dist[u][x]; dv = dist[y][v]
                            if du >= 0 and dv >= 0 and du + 1 + dv == 4:
                                sup.add((a, b))
                                break
            supports.append(frozenset(sup))
        out.append((mask, best, gamma, infinite, atoms, supports, dist))
    return out, best

def main():
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    tot_graphs = 0; tot_maxcuts = 0
    supsize_hist = Counter()
    mu_hist = Counter()
    mu_max_witness = None
    hall_viol = 0
    hall_viol_gammamin = 0
    pos_anomalies = 0
    size5 = 0
    atoms_per_cut = Counter()
    mu_hist_gmin = Counter()
    for n in range(nmin, nmax + 1):
        p = subprocess.run([GENG, "-q", "-c", "-t", str(n)],
                           capture_output=True, text=True)
        for line in p.stdout.splitlines():
            nn, adj = parse_graph6(line)
            tot_graphs += 1
            cuts, best = process_graph(nn, adj)
            gammas = [g for (_, _, g, inf, _, _, _) in cuts if not inf]
            gmin = min(gammas) if gammas else None
            for (mask, cval, gamma, inf, atoms, supports, dist) in cuts:
                tot_maxcuts += 1
                is_gmin = (not inf) and gamma == gmin
                atoms_per_cut[len(atoms)] += 1
                mu = Counter()
                for s in supports:
                    supsize_hist[len(s)] += 1
                    if len(s) == 5:
                        size5 += 1
                        print("SIZE5 WITNESS", line.strip(), mask)
                    for e in s:
                        mu[e] += 1
                for e, m in mu.items():
                    mu_hist[m] += 1
                    if is_gmin:
                        mu_hist_gmin[m] += 1
                    if mu_max_witness is None or m > mu_max_witness[0]:
                        mu_max_witness = (m, line.strip(), mask, e, is_gmin)
                # Hall check
                if atoms:
                    mm = hopcroft_matching(len(atoms), supports)
                    if mm < len(atoms):
                        hall_viol += 1
                        if is_gmin:
                            hall_viol_gammamin += 1
                        print("HALL VIOLATION", line.strip(), mask, len(atoms), mm)
                # endpoint position classes
                for (u, v), s in zip(atoms, supports):
                    for (a, b) in s:
                        poss = set()
                        for (x, y) in ((a, b), (b, a)):
                            du = dist[u][x]; dv = dist[y][v]
                            if du >= 0 and dv >= 0 and du + 1 + dv == 4:
                                poss.add(du + 1)
                        if len(poss) != 1:
                            pos_anomalies += 1
                            print("POSITION ANOMALY", line.strip(), mask, (u, v), (a, b), poss)
        print(f"n={n} done graphs_cum={tot_graphs} maxcuts_cum={tot_maxcuts}", flush=True)
    print("=== SUMMARY ===")
    print("graphs:", tot_graphs, "maxcuts:", tot_maxcuts)
    print("support size hist:", dict(sorted(supsize_hist.items())))
    print("size5 count:", size5)
    print("mu hist (all maxcuts):", dict(sorted(mu_hist.items())))
    print("mu hist (gamma-min maxcuts):", dict(sorted(mu_hist_gmin.items())))
    print("mu max witness (mu, g6, mask, edge, is_gmin):", mu_max_witness)
    print("hall violations:", hall_viol, " at gamma-min:", hall_viol_gammamin)
    print("position anomalies:", pos_anomalies)
    print("atoms-per-cut hist:", dict(sorted(atoms_per_cut.items())))

main()
