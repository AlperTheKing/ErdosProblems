"""Gate the no-two-hole residual corridor atom.

For each selected completed seed+moat switch, apply the rare stage-0
matching, form residual connected components, and look for a row f in F1
that misses two exits in one component.  Such a pair yields a shortest
exit co-witness corridor.  If a corridor appears, this diagnostic tries the
two proposed certificates:

  * long-lambda endpoint: a shorter B-path inside the row-union disk;
  * min-lambda endpoints: a negative rare-cost alternating exchange.

The expected proof-domain result is stronger: no such corridor exists.
"""

import argparse
import subprocess
from collections import Counter, deque

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def edge(u, v):
    return (u, v) if u < v else (v, u)


def vertices_of_mask(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def in_out(pair, mask):
    a, b = pair
    ina = (mask >> a) & 1
    inb = (mask >> b) & 1
    if ina and not inb:
        return a, b
    if inb and not ina:
        return b, a
    return None, None


def path_exit(path0, mask, tau):
    path = list(path0)
    if path[0] != tau:
        path = list(reversed(path))
    if path[0] != tau:
        return None
    bits = [(mask >> x) & 1 for x in path]
    if bits[0] != 1 or bits[-1] != 0:
        return None
    r = 0
    while r + 1 < len(bits) and bits[r + 1] == 1:
        r += 1
    if any(bits[j] for j in range(r + 1, len(bits))):
        return None
    if r > len(path) - 2:
        return None
    return edge(path[r], path[r + 1]), path


def paths_for_exit(cyc, h, mask, e):
    tau, _sig = in_out(h, mask)
    if tau is None:
        return []
    out = []
    for path0 in cyc[h]:
        got = path_exit(path0, mask, tau)
        if got is None:
            continue
        ex, path = got
        if ex == e:
            out.append(path)
    return out


def shortest_exit_path(cr, adj1, f, miss_pair):
    crs = tuple(cr)
    j_adj = {e: set() for e in crs}
    hinge = {}
    for a in crs:
        for b in crs:
            if a >= b:
                continue
            gs = sorted(g for g, es in adj1.items() if a in es and b in es)
            if gs:
                j_adj[a].add(b)
                j_adj[b].add(a)
                hinge[(a, b)] = gs[0]
                hinge[(b, a)] = gs[0]
    start, goal = miss_pair
    q = deque([start])
    prev = {start: None}
    while q:
        e = q.popleft()
        if e == goal:
            break
        for nb in sorted(j_adj[e]):
            if nb not in prev:
                prev[nb] = e
                q.append(nb)
    if goal not in prev:
        return None, None
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    # For a closest missed pair, internal exits should be f-seen.
    if any(x not in adj1[f] for x in path[1:-1]):
        return path, None
    hs = [hinge[(path[i - 1], path[i])] for i in range(1, len(path))]
    return path, hs


def alt_reach_cost_drop(F0, E0, witnesses, matching, deg_f1, root):
    """Return a matched E0 exit with larger rare cost if reachable."""
    if root not in E0:
        return None
    matched_e = set(matching.values())
    q = deque([("e", root)])
    seen_e = {root}
    seen_f = set()
    while q:
        typ, obj = q.popleft()
        if typ == "e":
            for f in F0:
                if f in witnesses[obj] and f not in seen_f:
                    seen_f.add(f)
                    q.append(("f", f))
        else:
            e = matching.get(obj)
            if e is not None and e not in seen_e:
                seen_e.add(e)
                q.append(("e", e))
    better = [e for e in seen_e & matched_e if deg_f1[e] > deg_f1[root]]
    return min(better, key=lambda e: (deg_f1[e], e)) if better else None


def disk_shorter_certificate(st, mask, f, corridor, hinges, adj1):
    _M, ell, _T, _mu, cyc = st
    disk = {}

    def add_path(path):
        for a, b in zip(path, path[1:]):
            disk.setdefault(a, set()).add(b)
            disk.setdefault(b, set()).add(a)

    involved = {f, *hinges}
    # f rows for internal tight exits.
    for e in corridor[1:-1]:
        for path in paths_for_exit(cyc, f, mask, e):
            add_path(path)
    # hinge rows for both adjacent exits.
    for i, g in enumerate(hinges, start=1):
        for e in (corridor[i - 1], corridor[i]):
            for path in paths_for_exit(cyc, g, mask, e):
                add_path(path)

    def dist(a, b):
        q = deque([(a, 0)])
        seen = {a}
        while q:
            u, d = q.popleft()
            if u == b:
                return d
            for w in disk.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    q.append((w, d + 1))
        return None

    for h in sorted(involved):
        a, b = h
        d = dist(a, b)
        if d is not None and d <= ell[h] - 3:
            return h, d, ell[h] - 1
    return None


def check(st, det, mask):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb.values())
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return True, "skip_no_F1", {}
    E0 = tuple(e for e in E if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", {}
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    stats = Counter()
    for cl, cr in components(F1, rem, adj1):
        cr = tuple(cr)
        for f in cl:
            misses = [e for e in cr if e not in adj1[f]]
            stats[("row_miss", len(misses))] += 1
            if len(misses) < 2:
                continue
            best = None
            for i, e0 in enumerate(misses):
                for ek in misses[i + 1 :]:
                    path, hinges = shortest_exit_path(cr, adj1, f, (e0, ek))
                    if path is None or hinges is None:
                        continue
                    key = (len(path), path, hinges)
                    if best is None or key < best:
                        best = key
            if best is None:
                return False, "no_corridor_path", {"f": f, "misses": tuple(misses), "cr": cr}
            _plen, corridor, hinges = best
            end_tiers = tuple("min" if lamb[e] == min_lam else "long" for e in (corridor[0], corridor[-1]))
            stats[("corridor", end_tiers)] += 1
            if any(lamb[e] > min_lam for e in (corridor[0], corridor[-1])):
                cert = disk_shorter_certificate(st, mask, f, corridor, hinges, adj1)
                if cert is None:
                    return False, "long_no_shorter_disk", {
                        "f": f,
                        "corridor": tuple(corridor),
                        "hinges": tuple(hinges),
                        "lambda": tuple((e, lamb[e]) for e in corridor),
                    }
                stats[("long_cert", cert[0])] += 1
            else:
                drops = []
                for e in (corridor[0], corridor[-1]):
                    u = alt_reach_cost_drop(F0, E0, witnesses, m0, deg_f1, e)
                    if u is not None:
                        drops.append((e, u, deg_f1[e], deg_f1[u]))
                if not drops:
                    return False, "min_no_rare_exchange", {
                        "f": f,
                        "corridor": tuple(corridor),
                        "hinges": tuple(hinges),
                        "deg": tuple(sorted((e, deg_f1[e]) for e in E0)),
                        "stage0": tuple(sorted(m0.items())),
                    }
                stats[("rare_exchange", len(drops))] += 1
    return True, "ok", {"stats": dict(stats)}


def scan_selected_cut(name, n, adj, side, acc, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        ok, status, info = check(st, det, mask)
        acc["tested"] += 1
        acc["status"][status] += 1
        if status == "ok":
            acc["stats"].update(info["stats"])
        if not ok and acc["first"] is None:
            acc["first"] = {
                "name": name,
                "n": n,
                "side": "".join(map(str, side)),
                "v": v,
                "S": vertices_of_mask(n, mask),
                "status": status,
                "info": info,
            }
            return


def scan_selected_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_selected_cut(name, n, adj, side, acc, max_add)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h2-allmax", action="store_true")
    ap.add_argument("--h-inherited", type=int, default=0)
    ap.add_argument("--max-add", type=int, default=1)
    args = ap.parse_args()
    acc = {
        "tested": 0,
        "no_switch": 0,
        "bad_terminal": 0,
        "status": Counter(),
        "stats": Counter(),
        "first": None,
    }
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_selected_allmax("cen%d" % nn, n, edges, acc, args.max_add)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if acc["first"] is None and args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_selected_allmax("H2-allmax", n, edges, acc, args.max_add)
    if acc["first"] is None:
        for t in range(2, args.h_inherited + 1):
            n, edges, side = h_blowup(t)
            scan_selected_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add)
            if acc["first"] is not None:
                break
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
