"""Gate near-witness persistence for the row-side rare-monotonicity atom.

For each completed terminal-shadow switch, enumerate triples (r, a, b, g)
where

  * r is a longer crossing bad edge (F1),
  * r witnesses exit a but not exit b,
  * g is a crossing bad edge witnessing both a and b.

The RM persistence claim is that such non-persistence must already trigger
the reduced-theta/S2 mechanism.  This gate uses the same computational
surrogate as the corridor checks: build the row disk from terminal rows

    r through a,  g through a,  g through b,

and assert that the disk contains a restricted-blue shortcut of length
at most ell(h)-3 for h in {r,g}.

The gate does not use row_miss <= 1.
"""

import argparse
import subprocess
from collections import Counter, deque

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_th_corridor_gate import paths_for_exit, vertices_of_mask


def disk_shortcut_for_triple(st, mask, r, a_exit, b_exit, g):
    _M, ell, _T, _mu, cyc = st
    disk = {}

    def add_path(path):
        for u, v in zip(path, path[1:]):
            disk.setdefault(u, set()).add(v)
            disk.setdefault(v, set()).add(u)

    counts = Counter()
    for path in paths_for_exit(cyc, r, mask, a_exit):
        add_path(path)
        counts["r/a"] += 1
    for path in paths_for_exit(cyc, g, mask, a_exit):
        add_path(path)
        counts["g/a"] += 1
    for path in paths_for_exit(cyc, g, mask, b_exit):
        add_path(path)
        counts["g/b"] += 1

    if not counts["r/a"] or not counts["g/a"] or not counts["g/b"]:
        return None, {"missing_paths": dict(counts)}

    def dist(src, dst):
        q = deque([(src, 0)])
        seen = {src}
        while q:
            u, d = q.popleft()
            if u == dst:
                return d
            for v in disk.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    q.append((v, d + 1))
        return None

    certs = []
    for h in (r, g):
        d = dist(h[0], h[1])
        if d is not None and d <= ell[h] - 3:
            certs.append((h, d, ell[h] - 1))
    if certs:
        return min(certs, key=lambda x: (x[1], x[0])), {"paths": dict(counts)}
    return None, {"paths": dict(counts), "disk_vertices": len(disk)}


def check(st, det, mask):
    _M, ell, _T, _mu, _cyc = st
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    if not F or len(F) != len(E):
        return True, "skip_unbalanced", {"stats": {}}
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    min_len = min(ell[f] for f in F)
    F1 = tuple(f for f in F if ell[f] > min_len)
    if not F1:
        return True, "skip_no_F1", {"stats": {}}

    exits_by_f = {f: {e for e in E if f in witnesses[e]} for f in F}
    stats = Counter()
    for r in F1:
        seen = exits_by_f[r]
        for a in sorted(seen):
            for b in sorted(set(E) - seen):
                co = [g for g in F if g != r and a in exits_by_f[g] and b in exits_by_f[g]]
                if not co:
                    continue
                stats["nonpersist_pair"] += 1
                for g in co:
                    stats["triple"] += 1
                    cert, info = disk_shortcut_for_triple(st, mask, r, a, b, g)
                    if cert is None:
                        return False, "rm_no_s2", {
                            "r": r,
                            "a": a,
                            "b": b,
                            "g": g,
                            "ell_r": ell[r],
                            "ell_g": ell[g],
                            "info": info,
                        }
                    stats["s2_cert"] += 1
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
        acc["stats"].update(info.get("stats", {}))
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
