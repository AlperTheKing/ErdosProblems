"""Debug one CLOSED-B-NEIGHBORHOOD ROW HALL min-cut witness.

The main gate reports the max bank-use ratio at klane-L14k4.  This script
reconstructs that instance and prints the Hall min-cut shadow for the target
row, including old cut-boundary counts of the blue-closed vertex set.
"""

import contextlib
import io
from collections import Counter, defaultdict
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_row_union_hall_gate import eligible_vertices, hall_excess
    from _codex_rowcap_non5_half_gate import adj_of
    from _satzmu_conn import kcomponents, struct_for_side
    from _wf_lrsbreak_0 import build_k_lane
    from _wf_lrsbreak_0c import greedy_chords


def boundary_counts(edges, side, U):
    U = set(U)
    b = m = 0
    b_edges = []
    m_edges = []
    for a, c in edges:
        if (a in U) == (c in U):
            continue
        if side[a] != side[c]:
            b += 1
            b_edges.append((a, c))
        else:
            m += 1
            m_edges.append((a, c))
    return b, m, b_edges, m_edges


def main():
    L, k, gap = 14, 4, 8
    bad = greedy_chords(L, k, gap)
    n, edges, side, _ = build_k_lane(L, k, bad)
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        raise RuntimeError("struct_for_side failed")
    M, _ell, _T, _mu, cyc = st

    b_adj = [set() for _ in range(n)]
    for u, v in edges:
        if side[u] != side[v]:
            b_adj[u].add(v)
            b_adj[v].add(u)

    comp_map, find = kcomponents(n, cyc)
    fs = [g for g in M if find(cyc[g][0][0]) == find(0)]
    all_rows = []
    for g in fs:
        den = F(len(cyc[g]))
        for p in cyc[g]:
            all_rows.append((g, tuple(p), set(p), den))

    target_f = (0, 14)
    target_q = tuple(range(15))
    qset = set(target_q)
    agg = Counter()
    members = defaultdict(list)
    total = F(0)
    for g, prow, pset, den in all_rows:
        inter = len(qset & pset)
        if not inter:
            continue
        mass = F(inter, 1) / den
        ev = eligible_vertices(pset, b_adj, "bclosed1")
        agg[ev] += mass
        members[ev].append((g, prow, mass, inter, den))
        total += mass

    demands = [(mass, verts) for verts, mass in agg.items()]
    excess, chosen = hall_excess(n, demands, want_witness=True)
    U = set()
    selected_mass = F(0)
    selected_types = []
    for i in chosen:
        mass, verts = demands[i]
        selected_mass += mass
        U.update(verts)
        selected_types.append((mass, verts, members[verts]))

    eta = F(n * n, 25) - len(M)
    bank = eta / 2 - F(len(target_q) ** 2 - 25, 50)
    b, m, b_edges, m_edges = boundary_counts(edges, side, U)

    print("instance=klane-L14k4")
    print(f"N={n} |M|={len(M)} eta={eta} bank={bank}")
    print(f"target_f={target_f} target_q={target_q}")
    print(f"total_demand={total}")
    print(f"hall_excess={excess} bank_ratio={excess / bank if bank else 'NA'} margin={bank-excess}")
    print(f"selected_mass={selected_mass} |U|={len(U)} selected_mass-|U|={selected_mass - len(U)}")
    print(f"U={tuple(sorted(U))}")
    print(f"delta_B(U)={b} delta_M(U)={m} sigma={b-m}")
    print(f"B_boundary={b_edges}")
    print(f"M_boundary={m_edges}")
    print("selected eligible types:")
    for idx, (mass, verts, rows) in enumerate(selected_types):
        print(f"  type {idx}: mass={mass} |E|={len(verts)} E={verts} row_count={len(rows)}")
        for g, prow, row_mass, inter, den in rows[:8]:
            print(f"    g={g} inter={inter} den={den} mass={row_mass} P={prow}")
        if len(rows) > 8:
            print(f"    ... {len(rows)-8} more")


if __name__ == "__main__":
    main()
