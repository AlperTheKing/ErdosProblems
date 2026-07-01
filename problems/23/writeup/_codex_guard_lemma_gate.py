"""Gate Claude/GPT-Pro's guard lemma on selected seed+moat switches.

For each selected R[v] < 0 seed+moat switch S, recover leaf-cap petals P_K
as subsets of S whose external B/M boundary partitions match a leaf cap K:

  delta_B(P_K, V\S) = K,
  delta_M(P_K, V\S) = N(K),

where N(K) are crossing bad edges witnessed by exits in K.  Then check the
boundary identities for S\P_K and the guard inequality

  |G_K| >= |I_K| + 1,

with I_K = delta_B(P_K, S\P_K) and G_K = delta_M(P_K, S\P_K).

This is a diagnostic/exact gate, not a proof.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def edge(u, v):
    return (u, v) if u < v else (v, u)


def mask_of(vertices):
    mask = 0
    for v in vertices:
        mask |= 1 << v
    return mask


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def inside_endpoint(e, smask):
    a, b = e
    ain = (smask >> a) & 1
    bin_ = (smask >> b) & 1
    if ain and not bin_:
        return a
    if bin_ and not ain:
        return b
    return None


def leaf_caps(miss_sets):
    nonempty = [set(s) for s in miss_sets if s]
    for i, a in enumerate(nonempty):
        for b in nonempty[i + 1:]:
            if not (a <= b or b <= a or a.isdisjoint(b)):
                return None
    leaves = []
    for s in nonempty:
        if not any(t < s for t in nonempty):
            if not any(t == s for t in leaves):
                leaves.append(s)
    return leaves


def two_cap_data(det):
    cset = tuple(sorted(det["cross_m"]))
    eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in cset}
    miss_sets = [set(eset) - exits_of_f[f] for f in cset]
    leaves = leaf_caps(miss_sets)
    if leaves is None or len(leaves) > 2:
        return None
    leaf_union = set().union(*leaves) if leaves else set()
    if any(witnesses[e] != set(cset) for e in set(eset) - leaf_union):
        return None
    for ms in miss_sets:
        rebuilt = set()
        for leaf in leaves:
            if leaf <= ms:
                rebuilt |= leaf
        if rebuilt != ms:
            return None
    return cset, eset, witnesses, exits_of_f, leaves


def boundary_between(n, adj, side, left_mask, right_mask):
    b_edges = set()
    m_edges = set()
    for u in range(n):
        if not ((left_mask >> u) & 1):
            continue
        for v in adj[u]:
            if not ((right_mask >> v) & 1):
                continue
            e = edge(u, v)
            if side[u] == side[v]:
                m_edges.add(e)
            else:
                b_edges.add(e)
    return b_edges, m_edges


def boundary_to_complement(n, adj, side, mask):
    comp = ((1 << n) - 1) ^ mask
    return boundary_between(n, adj, side, mask, comp)


def recover_petals(n, adj, side, smask, cset, eset, exits_of_f, cap):
    cap = set(cap)
    nk = {f for f in cset if exits_of_f[f] & cap}
    forced_in = set()
    forced_out = set()
    for e in eset:
        v = inside_endpoint(e, smask)
        if v is None:
            return None, "bad-exit-endpoint"
        (forced_in if e in cap else forced_out).add(v)
    for f in cset:
        v = inside_endpoint(f, smask)
        if v is None:
            return None, "bad-cross-endpoint"
        (forced_in if f in nk else forced_out).add(v)
    if forced_in & forced_out:
        return None, "forced-conflict"

    s_vertices = set(mask_tuple(n, smask))
    undecided = sorted(s_vertices - forced_in - forced_out)
    petals = []
    outside = ((1 << n) - 1) ^ smask
    forced_in_mask = mask_of(forced_in)
    for bits in range(1 << len(undecided)):
        pmask = forced_in_mask
        for i, v in enumerate(undecided):
            if (bits >> i) & 1:
                pmask |= 1 << v
        if pmask == 0 or pmask == smask:
            continue
        ext_b, ext_m = boundary_between(n, adj, side, pmask, outside)
        if ext_b != cap:
            continue
        if ext_m != nk:
            continue
        rest = smask & ~pmask
        i_b, g_m = boundary_between(n, adj, side, pmask, rest)
        rest_b, rest_m = boundary_to_complement(n, adj, side, rest)
        expected_rest_b = (set(eset) - cap) | i_b
        expected_rest_m = (set(cset) - nk) | g_m
        identities_ok = (rest_b == expected_rest_b and rest_m == expected_rest_m)
        petals.append(dict(mask=pmask, I=i_b, G=g_m, N=nk, identities_ok=identities_ok,
                           rest_b=rest_b, rest_m=rest_m,
                           expected_rest_b=expected_rest_b, expected_rest_m=expected_rest_m))
    return petals, None


def check_switch(name, n, adj, side, st, v, seed, moat, acc):
    smask = mask_of(set(seed) | set(moat))
    det = terminal_shadow_details(n, adj, side, st, smask)
    if det is None:
        acc["bad_terminal"] += 1
        acc.setdefault("first", ("bad_terminal", name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat))))
        return
    data = two_cap_data(det)
    if data is None:
        acc["bad_twocap"] += 1
        acc.setdefault("first", ("bad_twocap", name, n, "".join(map(str, side)), v, det))
        return
    cset, eset, _witnesses, exits_of_f, leaves = data
    acc["switches"] += 1
    if not leaves:
        acc["no_caps"] += 1
        return
    for cap in leaves:
        acc["caps"] += 1
        petals, err = recover_petals(n, adj, side, smask, cset, eset, exits_of_f, cap)
        if err:
            acc["recover_error"] += 1
            acc.setdefault("first", ("recover_error", err, name, n, "".join(map(str, side)), v, tuple(sorted(cap))))
            continue
        if not petals:
            acc["no_petal"] += 1
            acc.setdefault("first", ("no_petal", name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat)), tuple(sorted(cap)), cset, eset))
            continue
        acc["petal_count"][len(petals)] += 1
        for p in petals:
            if not p["identities_ok"]:
                acc["identity_fail"] += 1
                acc.setdefault("first", ("identity_fail", name, n, "".join(map(str, side)), v, tuple(sorted(cap)), mask_tuple(n, p["mask"]), tuple(sorted(p["rest_b"])), tuple(sorted(p["expected_rest_b"])), tuple(sorted(p["rest_m"])), tuple(sorted(p["expected_rest_m"]))))
            margin = len(p["G"]) - len(p["I"]) - 1
            acc["margin"][margin] += 1
            if margin < 0:
                acc["guard_fail"] += 1
                acc.setdefault("first", ("guard_fail", name, n, "".join(map(str, side)), v, tuple(sorted(seed)), tuple(sorted(moat)), tuple(sorted(cap)), mask_tuple(n, p["mask"]), tuple(sorted(p["I"])), tuple(sorted(p["G"])), margin))


def process_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            acc["neg"] += 1
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                acc["no_seedmoat"] += 1
                acc.setdefault("first", ("no_seedmoat", name, n, "".join(map(str, side)), v, str(rv)))
                continue
            seed, moat, _drop = sm
            check_switch(name, n, adj, side, st, v, seed, moat, acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--hblow", type=int, default=2)
    args = ap.parse_args()

    acc = Counter()
    acc["margin"] = Counter()
    acc["petal_count"] = Counter()

    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            process_graph(f"cen{nn}:{g6}", n, edges, acc)
            if acc.get("first") is not None and acc.get("first")[0] in {"guard_fail", "identity_fail", "no_petal", "recover_error", "bad_terminal", "bad_twocap", "no_seedmoat"}:
                break
        print("N", nn, "neg", acc["neg"], "caps", acc["caps"], "guard_fail", acc["guard_fail"], "first", acc.get("first"), flush=True)
        if acc.get("first") is not None and acc.get("first")[0] in {"guard_fail", "identity_fail", "no_petal", "recover_error", "bad_terminal", "bad_twocap", "no_seedmoat"}:
            break

    if acc.get("first") is None and args.hblow:
        hn, he = dec("H?AFBo]")
        n, edges = vertex_blowup(hn, he, args.hblow)
        process_graph(f"H?AFBo]x{args.hblow}", n, edges, acc)

    print("=" * 72)
    print("neg", acc["neg"], "switches", acc["switches"], "caps", acc["caps"], "no_caps", acc["no_caps"])
    print("bad_terminal", acc["bad_terminal"], "bad_twocap", acc["bad_twocap"], "no_seedmoat", acc["no_seedmoat"])
    print("recover_error", acc["recover_error"], "no_petal", acc["no_petal"], "identity_fail", acc["identity_fail"], "guard_fail", acc["guard_fail"])
    print("petal_count", sorted(acc["petal_count"].items()))
    print("margin", sorted(acc["margin"].items()))
    print("first", acc.get("first"))
    ok = acc["guard_fail"] == 0 and acc["identity_fail"] == 0 and acc["no_petal"] == 0 and acc["recover_error"] == 0 and acc["bad_terminal"] == 0 and acc["bad_twocap"] == 0 and acc["no_seedmoat"] == 0
    print("VERDICT", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()


