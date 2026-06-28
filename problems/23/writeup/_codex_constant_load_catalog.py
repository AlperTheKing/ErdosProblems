"""Catalog constant-load K/omega components.

This is structure mining for the proof of CONSTANT-LOAD-COMPONENT-BRIDGE.
It prints examples and boundary invariants, not a proof.
"""
import subprocess
from collections import Counter

from _h import GENG, dec
from _codex_constant_load_component import build_adj
from _codex_constant_load_selfcap import connected_gamma_min_sides
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def graph_edges(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


def catalog_side(name, n, adj, side, limit, rows):
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    comps, _ = kcomponents(n, cyc)
    B = {edge_key(u, v) for u, v in graph_edges(adj) if side[u] != side[v]}
    Mset = {edge_key(u, v) for u, v in graph_edges(adj) if side[u] == side[v]}
    for comp in comps.values():
        cset = {v for v in comp if T[v] > 0}
        if not cset or len(cset) == n:
            continue
        vals = {T[v] for v in cset}
        if len(vals) != 1:
            continue
        lam = next(iter(vals))
        boundary = [edge_key(u, v) for u in cset for v in adj[u] if v not in cset]
        boundary = sorted(set(boundary))
        b_boundary = [e for e in boundary if e in B]
        m_boundary = [e for e in boundary if e in Mset]
        pos_mu_boundary = [e for e in b_boundary if mu.get(e, 0) > 0]
        outside_loads = sorted({str(T[v]) for e in b_boundary for v in e if v not in cset})
        inside_boundary_loads = sorted({str(T[v]) for e in b_boundary for v in e if v in cset})
        rows.append(
            dict(
                graph=name,
                size=len(cset),
                lambda_=str(lam),
                boundary=len(boundary),
                b_boundary=len(b_boundary),
                m_boundary=len(m_boundary),
                pos_mu_boundary=len(pos_mu_boundary),
                inside_boundary_loads=inside_boundary_loads,
                outside_loads=outside_loads,
                C=sorted(cset),
            )
        )
        if len(rows) >= limit:
            return


def catalog_graph(name, n, edges, limit, rows):
    adj = build_adj(n, edges)
    for side in connected_gamma_min_sides(n, adj):
        catalog_side(name, n, adj, side, limit, rows)
        if len(rows) >= limit:
            return


def main():
    rows = []
    for nn in range(7, 12):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            catalog_graph(g6, n, edges, 40, rows)
            if len(rows) >= 40:
                break
        if len(rows) >= 40:
            break
    print("=== first census constant-load components ===")
    for r in rows[:20]:
        print(r)

    print("=== aggregate census rows ===")
    print("count", len(rows))
    print("lambda,size", Counter((r["lambda_"], r["size"]) for r in rows))
    print("boundary signature", Counter((r["b_boundary"], r["m_boundary"], r["pos_mu_boundary"]) for r in rows))

    print("=== glued examples ===")
    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    grows = []
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, edges = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    edges = edges + [(i, iN + j)]
                if n > 22 or not is_triangle_free(n, edges):
                    continue
                catalog_graph(f"isl{iN}+gad{gN}+{br}", n, edges, 12, grows)
    for r in grows[:12]:
        print(r)


if __name__ == "__main__":
    main()
