"""Gate the refined deficient-cap component classification.

This verifies the finite shadow suggested by the glued-C5 stress:
deficient-cap switches decompose, by bad-geodesic support components, into
zero-Psi pure odd-cycle baggage and positive nested 5/7 cores.

The script intentionally tests a small, exact corpus:
  * connected triangle-free census N<=10;
  * the canonical deficient atom glued to a C5 by a cut bridge.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, add_edges, is_triangle_free, union_disjoint
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _codex_defcap_template_cert import CANONICAL_G6


def row_support(cyc, f):
    out = set()
    for path in cyc[f]:
        out.update(path)
    return frozenset(out)


def support_components(fset, cyc):
    supports = {f: row_support(cyc, f) for f in fset}
    unseen = set(fset)
    comps = []
    while unseen:
        start = unseen.pop()
        comp = {start}
        q = [start]
        while q:
            f = q.pop()
            for g in list(unseen):
                if supports[f] & supports[g]:
                    unseen.remove(g)
                    comp.add(g)
                    q.append(g)
        comps.append(tuple(sorted(comp)))
    return tuple(sorted(comps))


def component_signature(comp, det, ell):
    comp = set(comp)
    witnesses = {e: set(det["witnesses"][e]) for e in det["bdy_b"]}
    ecomp = tuple(sorted(e for e, fs in witnesses.items() if fs & comp))
    surplus = sum(ell[f] ** 2 for f in comp)
    for e in ecomp:
        surplus -= min(ell[f] ** 2 for f in witnesses[e] & comp)
    return (len(comp), tuple(sorted(ell[f] for f in comp)), surplus, len(ecomp))


def component_private_shared_core(comp, det, ell):
    """Return True iff comp has the generalized positive nested-core form.

    Form: two bad edges of lengths L and L+2, two exits.  In the local
    deficient core the restricted witness sets are {short} and {short,long}.
    When the deficient cap lives in a disjoint pure-cycle baggage component,
    the same positive 5/7 core can have both exits shared by {short,long}.
    The algebraic sign proof works for both patterns for all odd L>=5.
    """
    comp = tuple(sorted(comp))
    if len(comp) != 2:
        return False
    f_short, f_long = sorted(comp, key=lambda f: (ell[f], f))
    L = ell[f_short]
    if L < 5 or L % 2 == 0 or ell[f_long] != L + 2:
        return False
    witnesses = {e: set(det["witnesses"][e]) & set(comp) for e in det["bdy_b"]}
    ecomp = tuple(sorted(e for e, fs in witnesses.items() if fs))
    if len(ecomp) != 2:
        return False
    restricted = sorted(tuple(sorted(fs)) for e, fs in witnesses.items() if fs)
    shared = tuple(sorted([f_short, f_long]))
    private_shared = [tuple([f_short]), shared]
    double_shared = [shared, shared]
    return restricted in (private_shared, double_shared)


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, _T, _mu, cyc = st
        if not M:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            bad = deficient_cap_subset(leaves, exits_of_f, fset)
            if bad is None:
                continue
            acc["defcap"] += 1
            comps = support_components(fset, cyc)
            sigs = tuple(component_signature(c, det, ell) for c in comps)
            acc["sigs"][sigs] += 1
            for comp, sig in zip(comps, sigs):
                is_pure_baggage = sig[0] == 1 and sig[2] == 0 and sig[3] == 1 and sig[1][0] % 2 == 1
                is_nested_core = component_private_shared_core(comp, det, ell)
                ok = is_pure_baggage or is_nested_core
                if not ok:
                    acc["fail"] += 1
                    if acc["first"] is None:
                        acc["first"] = dict(
                            name=name,
                            n=n,
                            side="".join(map(str, side)),
                            S=tuple(i for i in range(n) if (mask >> i) & 1),
                            sigs=sigs,
                            cross=tuple(sorted(fset)),
                            bdy=tuple(sorted(det["bdy_b"])),
                            bad=bad,
                        )
                    return


def canonical_plus_c5():
    n0, e0 = dec(CANONICAL_G6)
    n, edges = union_disjoint((n0, e0), (5, Cn(5)))
    n, edges = add_edges((n, edges), [(0, n0)])
    assert is_triangle_free(n, edges)
    return n, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--glued-c5", action="store_true")
    args = ap.parse_args()

    acc = {"defcap": 0, "fail": 0, "first": None, "sigs": Counter()}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if args.glued_c5 and acc["first"] is None:
        n, edges = canonical_plus_c5()
        scan_graph("canonical+C5", n, edges, acc)

    print("defcap:", acc["defcap"])
    print("fail:", acc["fail"])
    print("signatures:")
    for sig, count in sorted(acc["sigs"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(" ", count, sig)
    print("first:", acc["first"])
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
