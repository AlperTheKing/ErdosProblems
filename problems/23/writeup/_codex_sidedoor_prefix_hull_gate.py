r"""Gate the SIDE-DOOR PREFIX HULL atom on seed+moat switches.

For a neutral terminal-shadow switch S, crossing bad edges C, and old B-exits E,
test the right-closed cutoff Hall residual:

    X = {f in C : ell[f] < t and Wit(f) subset Y},  Y subset E_<t.

For deficient pairs |X|>|Y|, form the closed trapped prefix hull U and check:

    |delta_B(U) \ Y| <= |delta_M(U) \ X|.

Optionally test the sharper side-door matching from extra B-boundary edges to
extra bad-boundary edges.  This is a diagnostic gate for the final K2T switch
bridge, not a proof artifact.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def edge(u, v):
    return (u, v) if u < v else (v, u)


def mask_from_set(vertices):
    mask = 0
    for v in vertices:
        mask |= 1 << v
    return mask


def mask_tuple(n, mask):
    return tuple(v for v in range(n) if (mask >> v) & 1)


def edge_boundary(n, adj, side, mask):
    b_edges = set()
    m_edges = set()
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            e = (u, v)
            if side[u] == side[v]:
                m_edges.add(e)
            else:
                b_edges.add(e)
    return b_edges, m_edges


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def crossing_prefixes(mask_s, f, paths):
    """Return exit-edge -> list[prefix-mask] for f crossing S.

    The path is oriented from the S-side endpoint of f.  Each valid row must be
    a terminal prefix in S, as guaranteed by terminal_shadow_details.
    """
    u, v = f
    u_in = (mask_s >> u) & 1
    v_in = (mask_s >> v) & 1
    if u_in == v_in:
        return None
    tau = u if u_in else v
    out = {}
    for path0 in paths:
        path = list(path0)
        if path[0] != tau:
            path = list(reversed(path))
        if path[0] != tau:
            return None
        bits = [(mask_s >> x) & 1 for x in path]
        if bits[0] != 1 or bits[-1] != 0:
            return None
        r = 0
        while r + 1 < len(bits) and bits[r + 1] == 1:
            r += 1
        if any(bits[j] for j in range(r + 1, len(bits))):
            return None
        if r > len(path) - 2:
            return None
        ex = edge(path[r], path[r + 1])
        out.setdefault(ex, []).append(mask_from_set(path[: r + 1]))
    return out


def terminal_segment_orientations(mask_s, path0):
    """Yield oriented terminal-in-S path prefixes as vertex lists."""
    for path in (list(path0), list(reversed(path0))):
        bits = [(mask_s >> x) & 1 for x in path]
        if not bits or bits[0] != 1:
            continue
        r = 0
        while r + 1 < len(bits) and bits[r + 1] == 1:
            r += 1
        if any(bits[j] for j in range(r + 1, len(bits))):
            continue
        yield path[: r + 1]


def first_u_exit_on_terminal_segment(seg, mask_u):
    for a, b in zip(seg, seg[1:]):
        if ((mask_u >> a) & 1) and not ((mask_u >> b) & 1):
            return edge(a, b)
    return None


def max_matching(left, right, adj):
    match_r = {}

    def dfs(u, seen):
        for v in adj.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or dfs(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    size = 0
    for u in left:
        if dfs(u, set()):
            size += 1
    return size


def door_matching_size(n, adj, side, st, mask_s, mask_u, b_extra, m_extra, y_set, x_set, witnesses):
    M, _ell, _T, _mu, cyc = st
    e_set = set(witnesses)
    adj_door = {b: set() for b in b_extra}
    for b in b_extra:
        # External extra exit of the original switch S.
        if b in e_set and b not in y_set:
            for g in witnesses[b]:
                if g in m_extra:
                    a, c = g
                    s_end = a if ((mask_s >> a) & 1) else c if ((mask_s >> c) & 1) else None
                    if s_end is not None and ((mask_u >> s_end) & 1):
                        adj_door[b].add(g)

        # Internal side-door: first edge by which a terminal row leaves U.
        for g in m_extra:
            for path in cyc[g]:
                opened = False
                for seg in terminal_segment_orientations(mask_s, path):
                    if first_u_exit_on_terminal_segment(seg, mask_u) == b:
                        adj_door[b].add(g)
                        opened = True
                        break
                if opened:
                    break
    return max_matching(tuple(sorted(b_extra)), tuple(sorted(m_extra)), adj_door)


def test_sidedoor_for_switch(n, adj, side, st, mask_s, max_et, want_matching=False):
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        return dict(status="not-terminal")

    M, ell, _T, _mu, cyc = st
    C = set(det["cross_m"])
    E = set(det["bdy_b"])
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    wit_of_f = {f: set() for f in C}
    for e, fs in witnesses.items():
        for f in fs:
            wit_of_f.setdefault(f, set()).add(e)
    lamb = {e: min(ell[f] for f in fs) for e, fs in witnesses.items()}

    prefixes = {}
    for f in C:
        pref = crossing_prefixes(mask_s, f, cyc[f])
        if pref is None:
            return dict(status="bad-prefix")
        prefixes[f] = pref

    thresholds = sorted({ell[f] + 1 for f in C} | {lamb[e] + 1 for e in E})
    checked = deficient = skipped = count_fail = match_fail = 0
    first = None

    for t in thresholds:
        et = tuple(sorted(e for e in E if lamb[e] < t))
        if len(et) > max_et:
            skipped += 1
            continue
        for bits in range(1 << len(et)):
            Y = {et[i] for i in range(len(et)) if (bits >> i) & 1}
            X = {f for f in C if ell[f] < t and wit_of_f[f] <= Y}
            checked += 1
            if len(X) <= len(Y):
                continue
            deficient += 1
            mask_u = 0
            for f in X:
                for e in wit_of_f[f]:
                    for pmask in prefixes[f].get(e, ()):
                        mask_u |= pmask
            bdu, mdu = edge_boundary(n, adj, side, mask_u)
            b_extra = bdu - Y
            m_extra = mdu - X
            if len(b_extra) > len(m_extra):
                count_fail += 1
                if first is None:
                    first = dict(
                        t=t,
                        Y=tuple(sorted(Y)),
                        X=tuple(sorted(X)),
                        U=mask_tuple(n, mask_u),
                        Bextra=tuple(sorted(b_extra)),
                        Mextra=tuple(sorted(m_extra)),
                    )
                continue
            if want_matching:
                msize = door_matching_size(n, adj, side, st, mask_s, mask_u, b_extra, m_extra, Y, X, witnesses)
                if msize < len(b_extra):
                    match_fail += 1
                    if first is None:
                        first = dict(
                            t=t,
                            Y=tuple(sorted(Y)),
                            X=tuple(sorted(X)),
                            U=mask_tuple(n, mask_u),
                            Bextra=tuple(sorted(b_extra)),
                            Mextra=tuple(sorted(m_extra)),
                            matching=msize,
                        )

    return dict(
        status="ok",
        psi=det["psi"],
        cross=len(C),
        exits=len(E),
        checked=checked,
        deficient=deficient,
        skipped=skipped,
        count_fail=count_fail,
        match_fail=match_fail,
        first=first,
    )


def best_seed_moat_mask(n, adj, side, st, v, max_add):
    gamma0 = gamma_of(n, adj, side)
    _M, ell, _T, _mu, cyc = st
    best = None
    for seed in length_bundle_half_switches(ell, cyc, v):
        if not ((seed >> v) & 1):
            continue
        cand = best_moat_completion(n, adj, side, st, seed, max_add)
        if cand is None:
            continue
        added, negpsi, mask, psi = cand
        gamma2 = gamma_of(n, adj, flip_side(side, mask))
        if gamma2 is None or gamma2 >= gamma0:
            continue
        key = (added, -psi, mask)
        if best is None or key < best[0]:
            best = (key, seed, mask, psi)
    return None if best is None else best[1:]


def scan_cut(name, n, adj, side, acc, max_add, max_et, want_matching):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    neg = [v for v, r in enumerate(R) if r < 0]
    if not neg:
        return
    acc["cuts"] += 1
    for v in neg:
        acc["neg"] += 1
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            if acc["first"] is None:
                acc["first"] = (name, n, "".join(map(str, side)), v, str(R[v]), "no-switch")
            continue
        seed, mask, psi = got
        res = test_sidedoor_for_switch(n, adj, side, st, mask, max_et, want_matching)
        acc["switches"] += 1
        acc["checked"] += res.get("checked", 0)
        acc["deficient"] += res.get("deficient", 0)
        acc["skipped"] += res.get("skipped", 0)
        acc["status"][res["status"]] += 1
        acc["psi"][psi] += 1
        acc["moat_size"][(mask & ~seed).bit_count()] += 1
        if res.get("count_fail", 0) or res.get("match_fail", 0) or res["status"] != "ok":
            acc["fail"] += 1
            if acc["first"] is None:
                acc["first"] = (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(R[v]),
                    "seed",
                    mask_tuple(n, seed),
                    "S",
                    mask_tuple(n, mask),
                    res,
                )


def scan_graph_allmax(name, n, edges, acc, max_add, max_et, want_matching):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add, max_et, want_matching)


def new_acc():
    return dict(
        cuts=0,
        neg=0,
        switches=0,
        no_switch=0,
        checked=0,
        deficient=0,
        skipped=0,
        fail=0,
        first=None,
        status=Counter(),
        psi=Counter(),
        moat_size=Counter(),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=3)
    parser.add_argument("--max-et", type=int, default=14)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--matching", action="store_true")
    args = parser.parse_args()

    acc = new_acc()
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph_allmax("cen%d" % nn, n, edges, acc, args.max_add, args.max_et, args.matching)
        print(
            "census N=%d neg=%d switches=%d deficient=%d fail=%d"
            % (nn, acc["neg"], acc["switches"], acc["deficient"], acc["fail"]),
            flush=True,
        )

    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_graph_allmax("H?AFBo][2]-allmax", n, edges, acc, args.max_add, args.max_et, args.matching)
        print(
            "after H2 allmax neg=%d switches=%d deficient=%d fail=%d"
            % (acc["neg"], acc["switches"], acc["deficient"], acc["fail"]),
            flush=True,
        )

    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]-inherited" % t, n, adj_from_edges(n, edges), side, acc, args.max_add, args.max_et, args.matching)

    print("=" * 72)
    print("cuts with R<0:", acc["cuts"])
    print("negative vertices:", acc["neg"])
    print("switches tested:", acc["switches"], "no switch:", acc["no_switch"])
    print("Hall pairs checked:", acc["checked"], "deficient:", acc["deficient"], "skipped thresholds:", acc["skipped"])
    print("status:", dict(acc["status"]))
    print("moat size:", dict(sorted(acc["moat_size"].items())))
    print("Psi:", dict(sorted(acc["psi"].items())))
    print("fail:", acc["fail"], acc["first"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
