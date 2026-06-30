"""Gate the star-door capacity decomposition.

For each blue-closed hull extra graph in the selected seed+moat battery,
the observed star-door Hall condition is

    full_count >= missing_singleton_exits.

With notation:
    surplus = |Y| - |X|
    gap = |delta_B(U)| - |delta_M(U)|
    empty = # extra bad edges with no extra exit doors
    dup = sum_z max(0, singleton_count[z] - 1)

the exact identity should be

    full_count - missing = surplus - empty - dup - gap.

Thus Hall reduces to the capacity inequality

    surplus >= empty + dup + gap.
"""

from collections import Counter
from fractions import Fraction as F
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


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
        added, _negpsi, mask, psi = cand
        gamma2 = gamma_of(n, adj, flip_side(side, mask))
        if gamma2 is None or gamma2 >= gamma0:
            continue
        key = (added, -psi, mask)
        if best is None or key < best[0]:
            best = (key, seed, mask, psi)
    return None if best is None else best[1:]


def scan_switch(n, adj, side, st, seed_mask, mask_s, acc):
    cyc = st[4]
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None:
        return
    cross = list(det["cross_m"])
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: set() for f in cross}
    for e, fs in witnesses.items():
        for f in fs:
            exits_of_f[f].add(e)
    prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in cross}

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
        extra_b = tuple(sorted(bdu - y_set))
        extra_m = tuple(sorted(mdu - x_set))
        if not extra_b:
            continue

        full = set(extra_b)
        door_sets = {f: {e for e in extra_b if f in witnesses.get(e, set())} for f in extra_m}
        if any(s and len(s) != 1 and s != full for s in door_sets.values()):
            acc["star_fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = ("star_fail", extra_b, extra_m, door_sets)
            continue

        singleton_count = Counter()
        full_count = 0
        empty_count = 0
        for s in door_sets.values():
            if not s:
                empty_count += 1
            elif s == full:
                full_count += 1
            else:
                singleton_count[next(iter(s))] += 1

        covered = sum(1 for e in extra_b if singleton_count[e] > 0)
        missing = len(extra_b) - covered
        dup = sum(max(0, c - 1) for c in singleton_count.values())
        surplus = len(y_set) - len(x_set)
        gap = len(bdu) - len(mdu)
        lhs = full_count - missing
        rhs = surplus - empty_count - dup - gap

        acc["cases"] += 1
        acc["surplus"] [surplus] += 1
        acc["empty"] [empty_count] += 1
        acc["dup"] [dup] += 1
        acc["gap"] [gap] += 1
        acc["margin"] [rhs] += 1
        acc["full_minus_missing"] [lhs] += 1
        acc["z_size"] [len(extra_b)] += 1
        acc["capacity_slack"] [surplus - empty_count - dup - gap] += 1

        if lhs != rhs:
            acc["identity_fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (
                    "identity",
                    extra_b,
                    extra_m,
                    door_sets,
                    dict(
                        full=full_count,
                        missing=missing,
                        surplus=surplus,
                        empty=empty_count,
                        dup=dup,
                        gap=gap,
                        lhs=lhs,
                        rhs=rhs,
                    ),
                )
        if rhs < 0:
            acc["capacity_fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (
                    "capacity",
                    extra_b,
                    extra_m,
                    door_sets,
                    dict(
                        full=full_count,
                        missing=missing,
                        surplus=surplus,
                        empty=empty_count,
                        dup=dup,
                        gap=gap,
                        lhs=lhs,
                        rhs=rhs,
                    ),
                )


def scan_cut(n, adj, side, acc):
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
        got = best_seed_moat_mask(n, adj, side, st, v, 1)
        if got is None:
            acc["no_switch"] += 1
            continue
        seed, mask, _psi = got
        acc["switches"] += 1
        scan_switch(n, adj, side, st, seed, mask, acc)


def main():
    acc = {
        "switches": 0,
        "cases": 0,
        "no_switch": 0,
        "star_fail": 0,
        "identity_fail": 0,
        "capacity_fail": 0,
        "first_fail": None,
        "surplus": Counter(),
        "empty": Counter(),
        "dup": Counter(),
        "gap": Counter(),
        "margin": Counter(),
        "full_minus_missing": Counter(),
        "z_size": Counter(),
        "capacity_slack": Counter(),
    }
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            adj = adj_from_edges(n, edges)
            for side in maxcut_all(n, adj):
                scan_cut(n, adj, side, acc)
    n, edges, _inherited_side = h_blowup(2)
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(n, adj, side, acc)

    print("switches:", acc["switches"])
    print("cases:", acc["cases"])
    print("no_switch:", acc["no_switch"])
    print("star_fail:", acc["star_fail"])
    print("identity_fail:", acc["identity_fail"])
    print("capacity_fail:", acc["capacity_fail"])
    print("surplus:", dict(acc["surplus"]))
    print("empty:", dict(acc["empty"]))
    print("dup:", dict(acc["dup"]))
    print("gap:", dict(acc["gap"]))
    print("margin:", dict(acc["margin"]))
    print("full_minus_missing:", dict(acc["full_minus_missing"]))
    print("z_size:", dict(acc["z_size"]))
    print("capacity_slack:", dict(acc["capacity_slack"]))
    print("first_fail:", acc["first_fail"])
    print("VERDICT:", "PASS" if not acc["star_fail"] and not acc["identity_fail"] and not acc["capacity_fail"] else "FAIL")


if __name__ == "__main__":
    main()
