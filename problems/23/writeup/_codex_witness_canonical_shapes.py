"""Fast witness-graph shape signatures for completed seed+moat switches.

This diagnostic records the actual bipartite witness relation

    F = delta_M(S)  --  E = delta_B(S)

using a color-refinement signature seeded by bad-edge lengths and exit lambdas.
It is intended to expose small finite shape families behind the Hall/SDR lemma.
The signature is a proof-scouting invariant, not an isomorphism certificate.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details


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


def wl_signature(f_lens, e_lams, mat):
    f_colors = [("F", x) for x in f_lens]
    e_colors = [("E", x) for x in e_lams]
    for _ in range(len(f_lens) + len(e_lams) + 2):
        next_f = []
        for i, c in enumerate(f_colors):
            nbr = sorted(e_colors[j] for j, bit in enumerate(mat[i]) if bit)
            next_f.append((c, tuple(nbr)))
        next_e = []
        for j, c in enumerate(e_colors):
            nbr = sorted(f_colors[i] for i in range(len(f_lens)) if mat[i][j])
            next_e.append((c, tuple(nbr)))
        # Canonicalize color labels by their sorted structural values so labels
        # remain deterministic and small.
        vals = sorted(set(next_f + next_e), key=repr)
        lab = {v: k for k, v in enumerate(vals)}
        new_f = [("F", lab[v]) for v in next_f]
        new_e = [("E", lab[v]) for v in next_e]
        if new_f == f_colors and new_e == e_colors:
            break
        f_colors, e_colors = new_f, new_e
    f_classes = sorted((c, f_lens[i], sum(mat[i])) for i, c in enumerate(f_colors))
    e_classes = sorted((c, e_lams[j], sum(mat[i][j] for i in range(len(f_lens)))) for j, c in enumerate(e_colors))
    edge_colors = sorted((f_colors[i], e_colors[j]) for i in range(len(f_lens)) for j in range(len(e_lams)) if mat[i][j])
    return (tuple(f_classes), tuple(e_classes), tuple(edge_colors))


def compact_signature(sig):
    f_classes, e_classes, edge_colors = sig
    f_counts = Counter(f_classes)
    e_counts = Counter(e_classes)
    block_edges = Counter(edge_colors)
    f_order = sorted(f_counts, key=repr)
    e_order = sorted(e_counts, key=repr)
    f_labels = {c[0]: idx for idx, c in enumerate(f_order)}
    e_labels = {c[0]: idx for idx, c in enumerate(e_order)}
    rows = []
    for fc in f_order:
        row = []
        for ec in e_order:
            row.append(block_edges[(fc[0], ec[0])])
        rows.append(tuple(row))
    f_desc = tuple((f_labels[c[0]], f_counts[c], c[1], c[2]) for c in f_order)
    e_desc = tuple((e_labels[c[0]], e_counts[c], c[1], c[2]) for c in e_order)
    return f_desc, e_desc, tuple(rows)


def shape_signature(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    f_lens = [ell[f] for f in F_edges]
    e_lams = [min(ell[f] for f in witnesses[e]) for e in E_edges]
    mat = [[1 if f in witnesses[e] else 0 for e in E_edges] for f in F_edges]

    return (tuple(sorted(f_lens)), tuple(sorted(e_lams)), wl_signature(f_lens, e_lams, mat))


def hall_profile(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    wit_of_f = {f: set() for f in F_edges}
    for e, fs in witnesses.items():
        for f in fs:
            wit_of_f[f].add(e)
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    thresholds = sorted({ell[f] + 1 for f in F_edges} | {lamb[e] + 1 for e in E_edges})
    min_slack = None
    zero = 0
    total = 0
    for t in thresholds:
        et = tuple(e for e in E_edges if lamb[e] < t)
        for bits in range(1 << len(et)):
            Y = {et[i] for i in range(len(et)) if (bits >> i) & 1}
            X = {f for f in F_edges if ell[f] < t and wit_of_f[f] <= Y}
            slack = len(Y) - len(X)
            total += 1
            zero += int(slack == 0)
            if min_slack is None or slack < min_slack:
                min_slack = slack
    return min_slack, zero, total


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

    for u in left:
        dfs(u, set())
    return match_r


def matching_summary(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    adj = {f: {e for e in E_edges if f in witnesses[e]} for f in F_edges}
    match_e = max_matching(F_edges, E_edges, adj)
    pairs = [(f, e) for e, f in sorted(match_e.items())]
    counts = Counter((ell[f], lamb[e], ell[f] > lamb[e]) for f, e in pairs)
    return dict(
        matched=len(pairs),
        exits=len(E_edges),
        strict=sum(1 for f, e in pairs if ell[f] > lamb[e]),
        counts=tuple(sorted((k, v) for k, v in counts.items())),
    )


def scan_cut(name, n, adj, side, acc, examples, max_add):
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
        seed, mask, psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        key = shape_signature(st, det)
        acc["shapes"][key] += 1
        acc["moat"][(mask & ~seed).bit_count()] += 1
        acc["psi"][psi] += 1
        if key not in examples:
            examples[key] = dict(
                name=name,
                n=n,
                side="".join(map(str, side)),
                v=v,
                R=str(rv),
                S=tuple(i for i in range(n) if (mask >> i) & 1),
                psi=psi,
                hall=hall_profile(st, det),
                matching=matching_summary(st, det),
            )


def scan_graph_allmax(name, n, edges, acc, examples, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, max_add)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    acc = {"shapes": Counter(), "moat": Counter(), "psi": Counter(), "no_switch": 0, "bad_terminal": 0}
    examples = {}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph_allmax("cen%d" % nn, n, edges, acc, examples, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_graph_allmax("H2-allmax", n, edges, acc, examples, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, examples, args.max_add)

    print("shape_count:", len(acc["shapes"]))
    print("moat:", dict(sorted(acc["moat"].items())))
    print("psi:", dict(sorted(acc["psi"].items())))
    print("no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    for idx, (key, count) in enumerate(acc["shapes"].most_common(args.top), 1):
        lens, lams, sig = key
        ex = examples[key]
        print("-" * 72)
        print("rank", idx, "count", count)
        print("F_lens", lens, "E_lambdas", lams)
        if args.compact:
            f_desc, e_desc, rows = compact_signature(sig)
            print("F_blocks (id,count,length,degree)", f_desc)
            print("E_blocks (id,count,lambda,degree)", e_desc)
            print("block_edge_counts rows=F_blocks cols=E_blocks", rows)
        else:
            print("signature", sig)
        print("hall(min,zero,total)", ex["hall"])
        print("matching", ex["matching"])
        print("example", ex)


if __name__ == "__main__":
    main()
