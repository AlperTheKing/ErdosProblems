"""Gate whether deficient-cap two-cap switches are necessarily nonminimal.

The minimalized-selector route wants:

    minimal neutral terminal-shadow Gamma-decreasing switch
      => no deficient side cap.

This script tests the contrapositive on the broader class where deficient caps
actually occur.  It enumerates neutral terminal-shadow switches with positive
Psi and two-cap decomposition.  If a cap subset Y has |N(Y)| <= |Y|, it checks
whether there is a proper smaller subset U inside S that is still neutral,
terminal-shadow valid, B-connected after flip, and Gamma-decreasing.

Two strengths are reported:

  some_smaller: at least one proper smaller descent subset exists.
  all_vertex_smaller: for every vertex v in S, some proper smaller descent
      subset containing v exists.

The second form is the relevant one for selected switches, where the minimal
switch is required to contain the negative-residual vertex.
"""

import argparse
import itertools
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _construction_gate import boundary_delta, flip, gamma_of
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset


def vertices(mask, n):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def proper_submasks_containing(mask, n, required=None):
    verts = vertices(mask, n)
    req = set() if required is None else {required}
    free = [v for v in verts if v not in req]
    # Increasing size gives a small witness.
    for k in range(0, len(free)):
        for sub in itertools.combinations(free, k):
            umask = 0
            for v in req:
                umask |= 1 << v
            for v in sub:
                umask |= 1 << v
            if umask and umask != mask:
                yield umask


def is_descent(n, adj, side, st, gamma0, umask):
    U = set(vertices(umask, n))
    if boundary_delta(n, adj, side, U) != 0:
        return False
    det = terminal_shadow_details(n, adj, side, st, umask)
    if det is None:
        return False
    g2 = gamma_of(n, adj, flip(side, U))
    return g2 is not None and g2 < gamma0


def find_smaller(n, adj, side, st, gamma0, mask, required=None):
    for umask in proper_submasks_containing(mask, n, required):
        if is_descent(n, adj, side, st, gamma0, umask):
            return umask
    return None


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell = st[0], st[1]
        if not M:
            continue
        gamma0 = sum(ell[f] ** 2 for f in M)
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, set(vertices(mask, n))) != 0:
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

            some = find_smaller(n, adj, side, st, gamma0, mask)
            if some is None:
                acc["some_fail"] += 1
                if acc["first"] is None:
                    acc["first"] = (
                        "some_fail",
                        name,
                        n,
                        "".join(map(str, side)),
                        vertices(mask, n),
                        det["psi"],
                        bad,
                    )
                return
            acc["some_ok"] += 1

            bad_vertices = []
            witnesses = {}
            for v in vertices(mask, n):
                got = find_smaller(n, adj, side, st, gamma0, mask, required=v)
                if got is None:
                    bad_vertices.append(v)
                else:
                    witnesses[v] = vertices(got, n)
            if bad_vertices:
                acc["all_vertex_fail"] += 1
                if acc["first"] is None:
                    acc["first"] = (
                        "all_vertex_fail",
                        name,
                        n,
                        "".join(map(str, side)),
                        vertices(mask, n),
                        det["psi"],
                        bad,
                        tuple(bad_vertices),
                        witnesses,
                    )
                return
            acc["all_vertex_ok"] += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    args = parser.parse_args()
    acc = Counter()
    acc["first"] = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N", nn, dict(acc), flush=True)
        if acc["first"] is not None:
            break
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
