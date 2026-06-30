"""Stats for the observed star-laminar extra-door form.

For each blue-closed hull extra graph in the completed seed+moat battery,
check whether every nonempty right-door set is either a singleton or the full
extra-exit set.  In that case Hall reduces to:

    full_count >= #{exits with no singleton-door bad edge}.
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
        common = set(extra_b[0]) if extra_b else set()
        for e0 in extra_b[1:]:
            common &= set(e0)
        if common:
            acc["exit_star"][True] += 1
            hub = next(iter(common))
            in_seed = (seed_mask >> hub) & 1
            in_added = ((mask_s & ~seed_mask) >> hub) & 1
            hub_in_u = (mask_u >> hub) & 1
            hub_in_s = (mask_s >> hub) & 1
            acc["hub_in_u"][bool(hub_in_u)] += 1
            acc["hub_in_s"][bool(hub_in_s)] += 1
            if in_added:
                acc["hub_location"]["added"] += 1
            elif in_seed:
                acc["hub_location"]["seed"] += 1
            else:
                acc["hub_location"]["outside"] += 1
        else:
            acc["exit_star"][False] += 1
            if acc.get("first_nonstar") is None:
                acc["first_nonstar"] = extra_b
        door_sets = {}
        for f in extra_m:
            door_sets[f] = {e for e in extra_b if f in witnesses.get(e, set())}

        acc["cases"] += 1
        if any(s and len(s) != 1 and s != full for s in door_sets.values()):
            acc["star_fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (extra_b, extra_m, door_sets)
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
        missing = sum(1 for e in extra_b if singleton_count[e] == 0)
        acc["z_size"][len(extra_b)] += 1
        acc["branch_shape"][("inU" if common and ((mask_u >> next(iter(common))) & 1) else "outU", len(extra_b), missing)] += 1
        acc["missing_singletons"][missing] += 1
        acc["full_minus_missing"][full_count - missing] += 1
        branch_key = ("inU" if common and ((mask_u >> next(iter(common))) & 1) else "outU", len(extra_b), missing)
        acc["full_by_branch"][(branch_key, full_count)] += 1
        acc["empty_count"][empty_count] += 1
        if missing > 0 and full_count == missing and acc.get("first_tight") is None:
            acc["first_tight"] = (extra_b, extra_m, door_sets, full_count, missing, singleton_count)
        if full_count < missing:
            acc["reduced_hall_fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (extra_b, extra_m, door_sets, full_count, missing)


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
        "reduced_hall_fail": 0,
        "first_fail": None,
        "first_nonstar": None,
        "exit_star": Counter(),
        "hub_location": Counter(),
        "hub_in_u": Counter(),
        "hub_in_s": Counter(),
        "z_size": Counter(),
        "branch_shape": Counter(),
        "missing_singletons": Counter(),
        "full_minus_missing": Counter(),
        "full_by_branch": Counter(),
        "empty_count": Counter(),
        "first_tight": None,
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
    print("reduced_hall_fail:", acc["reduced_hall_fail"])
    print("exit_star:", dict(acc["exit_star"]))
    print("first_nonstar:", acc["first_nonstar"])
    print("hub_location:", dict(acc["hub_location"]))
    print("hub_in_u:", dict(acc["hub_in_u"]))
    print("hub_in_s:", dict(acc["hub_in_s"]))
    print("z_size:", dict(acc["z_size"]))
    print("branch_shape:", dict(acc["branch_shape"]))
    print("missing_singletons:", dict(acc["missing_singletons"]))
    print("full_minus_missing:", dict(acc["full_minus_missing"]))
    print("full_by_branch:", dict(acc["full_by_branch"]))
    print("empty_count:", dict(acc["empty_count"]))
    print("first_tight:", acc["first_tight"])
    print("first_fail:", acc["first_fail"])


if __name__ == "__main__":
    main()
