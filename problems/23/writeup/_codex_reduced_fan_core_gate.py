"""Gate the reduced fan-core expansion (RFC) atom.

For selected seed+moat switches and every X subset crossing bad edges:

  Y = Wit(X)
  U = blue-closed prefix hull of X inside S
  B+ = delta_B(U) \\ Y
  M+ = delta_M(U) \\ X

Build the extra-door graph D_X from B+ to M+ using first exits of shortest
rows from the U-side endpoint of g in M+.  Then enumerate reduced subsets
Z subset B+:

  H=N(Z),  |D_Z(g)|>=2 for every g in H,

and check |H|>=|Z|.  This is a direct exact gate for the "no reduced
deficient fan core" lemma.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary, mask_tuple
from _codex_blueclosed_hull_gate import blue_close_inside_s


def edge(u, v):
    return (u, v) if u < v else (v, u)


def first_exit_door(mask_u, path0):
    for path in (list(path0), list(reversed(path0))):
        bits = [(mask_u >> x) & 1 for x in path]
        if not bits or bits[0] != 1 or bits[-1] != 0:
            continue
        r = 0
        while r + 1 < len(bits) and bits[r + 1] == 1:
            r += 1
        if any(bits[j] for j in range(r + 1, len(bits))):
            continue
        if r > len(path) - 2:
            continue
        return edge(path[r], path[r + 1])
    return None


def door_graph(st, mask_u, bplus, mplus):
    _M, _ell, _T, _mu, cyc = st
    bplus = set(bplus)
    out = {g: set() for g in mplus}
    for g in mplus:
        for path in cyc[g]:
            e = first_exit_door(mask_u, path)
            if e in bplus:
                out[g].add(e)
    return out


def scan_switch(n, adj, side, st, mask_s, acc):
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        return
    cross = list(det["cross_m"])
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: set() for f in cross}
    for e, fs in witnesses.items():
        for f in fs:
            exits_of_f[f].add(e)
    prefixes = {f: crossing_prefixes(mask_s, f, st[4][f]) for f in cross}

    for bits in range(1, 1 << len(cross)):
        x_set = {cross[i] for i in range(len(cross)) if (bits >> i) & 1}
        y_set = set().union(*(exits_of_f[f] for f in x_set))
        mask_u = 0
        for f in x_set:
            for e in exits_of_f[f]:
                for pmask in prefixes[f].get(e, ()):
                    mask_u |= pmask
        mask_u = blue_close_inside_s(n, adj, side, mask_s, mask_u)
        bdu, mdu = edge_boundary(n, adj, side, mask_u)
        bplus = tuple(sorted(bdu - y_set))
        mplus = tuple(sorted(mdu - x_set))
        if not bplus:
            continue

        doors = door_graph(st, mask_u, bplus, mplus)
        acc["cases"] += 1
        acc["z_size"][len(bplus)] += 1
        acc["h_size"][len(mplus)] += 1

        for zbits in range(1, 1 << len(bplus)):
            Z = {bplus[i] for i in range(len(bplus)) if (zbits >> i) & 1}
            H = {g for g in mplus if doors.get(g, set()) & Z}
            if not H:
                # Nonempty Z with no neighbor is already reduced-deficient.
                reduced = True
            else:
                reduced = all(len(doors.get(g, set()) & Z) >= 2 for g in H)
            if not reduced:
                continue
            acc["reduced"] += 1
            if len(H) < len(Z):
                acc["fail"] += 1
                if acc["first"] is None:
                    acc["first"] = dict(
                        S=mask_tuple(n, mask_s),
                        X=tuple(sorted(x_set)),
                        Y=tuple(sorted(y_set)),
                        U=mask_tuple(n, mask_u),
                        Bplus=bplus,
                        Mplus=mplus,
                        Z=tuple(sorted(Z)),
                        H=tuple(sorted(H)),
                        doors={g: tuple(sorted(v)) for g, v in sorted(doors.items())},
                    )
                return


def scan_cut(name, n, adj, side, acc, max_add):
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
        acc["switches"] += 1
        scan_switch(n, adj, side, st, mask, acc)


def scan_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add)
        if acc["first"] is not None:
            return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    args = parser.parse_args()

    acc = {
        "switches": 0,
        "cases": 0,
        "reduced": 0,
        "fail": 0,
        "first": None,
        "no_switch": 0,
        "z_size": Counter(),
        "h_size": Counter(),
    }
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, acc, args.max_add)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if args.h2_allmax and acc["first"] is None:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, args.max_add)
    for t in range(2, args.h_inherited + 1):
        if acc["first"] is not None:
            break
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add)

    print("switches:", acc["switches"], "no_switch:", acc["no_switch"])
    print("cases:", acc["cases"], "reduced subsets:", acc["reduced"])
    print("z_size:", dict(acc["z_size"]))
    print("h_size:", dict(acc["h_size"]))
    print("fail:", acc["fail"], acc["first"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
