"""Dump the local-bank failing component (Bank0 gate first_local_fail)."""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


g6 = "H?AFBo]"
n, edges = dec(g6)
print("graph:", g6, "n:", n, "edges:", sorted(norm(e) for e in edges))

_adj, cuts = gmins(n, edges)
adj = adj_of(n, edges)
for side_s in cuts:
    side = [int(c) for c in side_s]
    if "".join(map(str, side)) != "000111100":
        continue
    st = struct_for_side(n, adj, side)
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    M = [norm(g) for g in M_raw]
    ell = {norm(g): ell_raw[g] for g in M_raw}
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)
    print("side:", side_s, "m:", len(M), "N^2-25m:", n * n - 25 * len(M))
    seen = set()
    for f in M:
        key = tuple(sorted(comp_of[f]))
        if key in seen:
            continue
        seen.add(key)
        csupp = set()
        for g in key:
            csupp |= supp[g]
        print("  component edges:", key)
        print("    ells:", [ell[g] for g in key])
        print("    m_C:", len(key), "|supp|:", len(csupp), "supp:", sorted(csupp))
        print("    25*m_C - |supp|^2 =", 25 * len(key) - len(csupp) ** 2)
        for g in key:
            print("    cyc[", g, "] len", len(cyc[g]), ":", cyc[g])
