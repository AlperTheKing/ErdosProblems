"""Gate path-level 5/7 theta containment in deficient-cap positive cores.

This builds on _codex_defcap_component_class_gate.py.  For every positive
support component in a deficient-cap terminal-shadow switch, assert that its
two bad edges have lengths 5 and 7 and that some shortest row of the length-7
edge contains contiguously a one-ended core of a shortest row of the length-5
edge.  In the canonical atom:

    short: 0-6-9-3-8
    long:  1-6-9-3-8-2-7

the contained core is 6-9-3-8, i.e. the short row with one terminal endpoint
trimmed.

Pure odd-cycle zero-Psi baggage components are allowed and ignored.
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
from _codex_defcap_component_class_gate import support_components, component_signature


def is_contiguous_subpath(needle, haystack):
    needle = list(needle)
    haystack = list(haystack)
    k = len(needle)
    if k > len(haystack):
        return False
    rev = list(reversed(needle))
    for i in range(len(haystack) - k + 1):
        block = haystack[i : i + k]
        if block == needle or block == rev:
            return True
    return False


def theta_witness(comp, cyc, ell):
    comp = tuple(sorted(comp))
    if len(comp) != 2:
        return None
    short, long = sorted(comp, key=lambda f: (ell[f], f))
    if ell[short] != 5 or ell[long] != 7:
        return None
    for p in cyc[long]:
        for q in cyc[short]:
            if is_contiguous_subpath(q, p):
                return short, long, "full", tuple(q), tuple(p)
            if is_contiguous_subpath(q[1:], p):
                return short, long, "trim_left", tuple(q), tuple(p)
            if is_contiguous_subpath(q[:-1], p):
                return short, long, "trim_right", tuple(q), tuple(p)
    return None


def canonical_plus_c5():
    n0, e0 = dec(CANONICAL_G6)
    n, edges = union_disjoint((n0, e0), (5, Cn(5)))
    n, edges = add_edges((n, edges), [(0, n0)])
    assert is_triangle_free(n, edges)
    return n, edges


def scan_graph(name, n, edges, acc, example_limit):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        _M, ell, _T, _mu, cyc = st
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
            for comp in support_components(fset, cyc):
                sig = component_signature(comp, det, ell)
                is_pure_baggage = sig[0] == 1 and sig[2] == 0 and sig[3] == 1 and sig[1][0] % 2 == 1
                if is_pure_baggage:
                    acc["baggage"] += 1
                    continue
                acc["positive"] += 1
                wit = theta_witness(comp, cyc, ell)
                if wit is None:
                    acc["fail"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "S": tuple(i for i in range(n) if (mask >> i) & 1),
                            "comp": tuple(sorted(comp)),
                            "sig": sig,
                            "cross": tuple(sorted(fset)),
                            "bdy": tuple(sorted(det["bdy_b"])),
                            "bad": bad,
                        }
                    return
                acc["theta"] += 1
                short, long, mode, q, p = wit
                acc["theta_sig"][(ell[short], ell[long], mode, len(q), len(p))] += 1
                if len(acc["examples"]) < example_limit:
                    acc["examples"].append(
                        {
                            "name": name,
                            "short": short,
                            "long": long,
                            "mode": mode,
                            "q": q,
                            "p": p,
                        }
                    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--glued-c5", action="store_true")
    ap.add_argument("--examples", type=int, default=6)
    args = ap.parse_args()

    acc = Counter()
    acc["theta_sig"] = Counter()
    acc["examples"] = []
    acc["first"] = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc, args.examples)
            if acc["first"] is not None:
                break
        if acc["first"] is not None:
            break
    if args.glued_c5 and acc["first"] is None:
        n, edges = canonical_plus_c5()
        scan_graph("canonical+C5", n, edges, acc, args.examples)

    theta_sig = acc.pop("theta_sig")
    examples = acc.pop("examples")
    first = acc.pop("first")
    print("defcap:", acc["defcap"], "positive:", acc["positive"], "baggage:", acc["baggage"])
    print("theta:", acc["theta"], "fail:", acc["fail"])
    print("theta_sig:", dict(theta_sig))
    print("first:", first or "")
    print("examples:")
    for ex in examples:
        print(ex)
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
