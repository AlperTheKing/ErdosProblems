"""
GAP#1 TASK D3 census: ell=5 atom supports at maximum cuts of connected triangle-free graphs N<=10.

For every connected triangle-free graph (geng -c -t), every MAXIMUM cut (all of them; Gamma-min flagged):
  atoms  = monochromatic edges (u,v) with d_B(u,v) = 4  (ell = 5)
  P_e    = union of edges of ALL shortest blue geodesics u..v   (the multi-geodesic support)
Checks:
  (H) Hall: every nonempty subset S of atoms has |S| <= |union P_e|   (violations recorded)
  (D) dichotomy: |P_e| never equals 5  (claim: 4 = unique geodesic, or >= 6)
  (M) per-edge multiplicity mult(c) = #atoms with c in P_e : distribution + max, witnesses
  (U) pairwise |P_e u P_f| >= 5 sanity
All exact integer arithmetic.
"""
import sys, os, json, subprocess
from collections import deque, Counter
from multiprocessing import Pool

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def parse_g6(s):
    s = s.strip()
    data = [ord(c) - 63 for c in s]
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
                adj[i] |= (1 << j)
                adj[j] |= (1 << i)
            idx += 1
    return n, adj

def bfs_dist(nbr, n, src):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        x = q.popleft()
        for y in nbr[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist

def process_line(g6):
    n, adj = parse_g6(g6)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                edges.append((i, j))
    nmask = (1 << n) - 1
    # max cut: vertex 0 fixed on side 0; mask = side-1 set among vertices 1..n-1
    best = -1
    bestmasks = []
    for m in range(1 << (n - 1)):
        mask = m << 1
        cut = 0
        mm = mask
        while mm:
            v = (mm & -mm).bit_length() - 1
            cut += bin(adj[v] & ~mask & nmask).count("1")
            mm &= mm - 1
        if cut > best:
            best = cut
            bestmasks = [mask]
        elif cut == best:
            bestmasks.append(mask)

    INF = 10 ** 9
    results = []  # per max cut: (mask, gamma, atoms, supports, ...)
    for mask in bestmasks:
        blue_nbr = [[] for _ in range(n)]
        blue_edges = []
        bad_edges = []
        for (i, j) in edges:
            si = (mask >> i) & 1
            sj = (mask >> j) & 1
            if si != sj:
                blue_nbr[i].append(j)
                blue_nbr[j].append(i)
                blue_edges.append((i, j))
            else:
                bad_edges.append((i, j))
        gamma = 0
        dists = {}
        ok = True
        atom_list = []
        for (u, v) in bad_edges:
            if u not in dists:
                dists[u] = bfs_dist(blue_nbr, n, u)
            d = dists[u][v]
            if d < 0:
                ok = False
                break
            ell = d + 1
            gamma += ell * ell
            if d == 4:
                atom_list.append((u, v))
        if not ok:
            results.append((mask, None, [], []))
            continue
        # supports
        eidx = {e: k for k, e in enumerate(blue_edges)}
        sups = []
        for (u, v) in atom_list:
            if u not in dists:
                dists[u] = bfs_dist(blue_nbr, n, u)
            if v not in dists:
                dists[v] = bfs_dist(blue_nbr, n, v)
            du = dists[u]
            dv = dists[v]
            sup = 0
            for (x, y) in blue_edges:
                if (du[x] >= 0 and dv[y] >= 0 and du[x] + 1 + dv[y] == 4) or \
                   (du[y] >= 0 and dv[x] >= 0 and du[y] + 1 + dv[x] == 4):
                    sup |= 1 << eidx[(x, y)]
            sups.append(sup)
        results.append((mask, gamma, atom_list, sups))

    gammas = [g for (_, g, _, _) in results if g is not None]
    gmin = min(gammas) if gammas else None

    out = {
        "graphs": 1,
        "cuts": len(bestmasks),
        "hall_viol": [],
        "size5": [],
        "pairU_viol": [],
        "size_hist": Counter(),
        "mult_hist": Counter(),
        "mult_hist_gmin": Counter(),
        "max_mult": 0,
        "max_mult_gmin": 0,
        "witness": None,        # for max multiplicity overall
        "witness_gmin": None,
        "hall_skipped": 0,
    }
    for (mask, gamma, atoms, sups) in results:
        if gamma is None:
            continue
        is_gmin = (gamma == gmin)
        k = len(atoms)
        for s in sups:
            out["size_hist"][bin(s).count("1")] += 1
            if bin(s).count("1") == 5:
                out["size5"].append((g6, mask, atoms))
        # pairwise union
        for a in range(k):
            for b in range(a + 1, k):
                if bin(sups[a] | sups[b]).count("1") < 5:
                    out["pairU_viol"].append((g6, mask, atoms[a], atoms[b]))
        # multiplicity
        if k:
            cnt = Counter()
            allsup = 0
            for s in sups:
                allsup |= s
            b = allsup
            while b:
                c = (b & -b)
                mult = sum(1 for s in sups if s & c)
                ci = c.bit_length() - 1
                out["mult_hist"][mult] += 1
                if is_gmin:
                    out["mult_hist_gmin"][mult] += 1
                if mult > out["max_mult"]:
                    out["max_mult"] = mult
                    out["witness"] = (g6, mask, ci, atoms, gamma == gmin)
                if is_gmin and mult > out["max_mult_gmin"]:
                    out["max_mult_gmin"] = mult
                    out["witness_gmin"] = (g6, mask, ci, atoms)
                b &= b - 1
        # Hall over all nonempty subsets
        if k > 0:
            if k > 20:
                out["hall_skipped"] += 1
            else:
                U = [0] * (1 << k)
                for smask in range(1, 1 << k):
                    low = (smask & -smask).bit_length() - 1
                    U[smask] = U[smask & (smask - 1)] | sups[low]
                    if bin(smask).count("1") > bin(U[smask]).count("1"):
                        out["hall_viol"].append((g6, mask, smask, atoms, is_gmin))
    out["size_hist"] = dict(out["size_hist"])
    out["mult_hist"] = dict(out["mult_hist"])
    out["mult_hist_gmin"] = dict(out["mult_hist_gmin"])
    return out

def merge(tot, o):
    tot["graphs"] += o["graphs"]
    tot["cuts"] += o["cuts"]
    tot["hall_viol"] += o["hall_viol"]
    tot["size5"] += o["size5"]
    tot["pairU_viol"] += o["pairU_viol"]
    tot["hall_skipped"] += o["hall_skipped"]
    for h in ("size_hist", "mult_hist", "mult_hist_gmin"):
        for kk, vv in o[h].items():
            tot[h][kk] = tot[h].get(kk, 0) + vv
    if o["max_mult"] > tot["max_mult"]:
        tot["max_mult"] = o["max_mult"]
        tot["witness"] = o["witness"]
    if o["max_mult_gmin"] > tot["max_mult_gmin"]:
        tot["max_mult_gmin"] = o["max_mult_gmin"]
        tot["witness_gmin"] = o["witness_gmin"]

def main():
    nlo, nhi = int(sys.argv[1]), int(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    grand = {}
    for n in range(nlo, nhi + 1):
        p = subprocess.run([GENG, "-q", "-c", "-t", str(n)], capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        tot = {"graphs": 0, "cuts": 0, "hall_viol": [], "size5": [], "pairU_viol": [],
               "size_hist": {}, "mult_hist": {}, "mult_hist_gmin": {},
               "max_mult": 0, "max_mult_gmin": 0, "witness": None, "witness_gmin": None,
               "hall_skipped": 0}
        with Pool(workers) as pool:
            for o in pool.imap_unordered(process_line, lines, chunksize=max(1, len(lines)//(workers*8) or 1)):
                merge(tot, o)
        # trim long lists
        for key in ("hall_viol", "size5", "pairU_viol"):
            if len(tot[key]) > 20:
                tot[key] = tot[key][:20] + [f"...(+{len(tot[key])-20} more)"]
        grand[n] = tot
        print(f"n={n}: graphs={tot['graphs']} cuts={tot['cuts']} "
              f"hallViol={len(tot['hall_viol'])} size5={len(tot['size5'])} pairUviol={len(tot['pairU_viol'])} "
              f"sizeHist={tot['size_hist']} maxMult={tot['max_mult']} maxMultGmin={tot['max_mult_gmin']}", flush=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d3_census_out.json"), "w") as f:
        json.dump(grand, f, indent=1, default=str)
    print("DONE")

if __name__ == "__main__":
    main()
