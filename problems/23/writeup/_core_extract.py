"""Extract the exact 5/7 deficient-core structure from I?AEBAwF_: the two bad edges f0(ell=5),f1(ell=7),
their geodesic sets cyc[f0],cyc[f1], the K2-support component V, the loads T, and R_local per vertex.
Reveals the pattern to generalize R_local to the nested L/(L+2) core for general odd L>=5."""
import sys
from fractions import Fraction as F
from _h import dec, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _defcap_component_mine import k2_components

cn, cE = dec('I?AEBAwF_')
adj = adj_from_edges(cn, cE)
found = False
for side in maxcut_all(cn, adj):
    if found:
        break
    if not Bconn(cn, adj, side):
        continue
    st = struct_for_side(cn, adj, side)
    if st is None:
        continue
    M, ell, T, mu, cyc = st
    if not M:
        continue
    K2 = build_K2(cn, M, cyc)
    Tf = [sum(K2[v][w] for w in range(cn)) for v in range(cn)]
    for mask in range(1, (1 << cn) - 1):
        if boundary_delta(cn, adj, side, mask) != 0:
            continue
        Sset = set(i for i in range(cn) if (mask >> i) & 1)
        res = witness_structure(cn, adj, side, st, Sset)
        if res is None:
            continue
        crossM, bdyB, wit = res
        if not crossM or not bdyB:
            continue
        witnesses = {}
        for (f, e) in wit:
            witnesses.setdefault(e, set()).add(f)
        for e in bdyB:
            witnesses.setdefault(e, set())
        if any(not witnesses[e] for e in bdyB):
            continue
        psi = sum(ell[f] ** 2 for f in crossM) - sum(min(ell[f] for f in witnesses[e]) ** 2 for e in bdyB)
        if psi <= 0:
            continue
        det = {'cross_m': tuple(sorted(crossM)), 'bdy_b': tuple(sorted(bdyB)),
               'witnesses': {e: tuple(sorted(witnesses[e])) for e in bdyB}}
        data = two_cap_data(det)
        if data is None:
            continue
        fset, eset, exits_of_f, leaves = data
        if deficient_cap_subset(leaves, exits_of_f, fset) is None:
            continue
        comps = k2_components(cn, K2)
        for comp in comps:
            V = set(comp)
            cross_in = [f for f in crossM if f[0] in V or f[1] in V]
            if len(cross_in) == 2 and sorted(ell[f] for f in cross_in) == [5, 7]:
                f0 = [f for f in cross_in if ell[f] == 5][0]
                f1 = [f for f in cross_in if ell[f] == 7][0]
                Rloc = {u: F(len(comp)) * Tf[u] - sum(K2[u][w] * Tf[w] for w in V) for u in comp}
                print("5/7 CORE in I?AEBAwF_  side=%s  S=%s" % (''.join(map(str, side)), sorted(Sset)))
                print(" f0 (ell=5) =", f0, " #geodesics=", len(cyc[f0]))
                for P in cyc[f0]:
                    print("    f0 geo:", P)
                print(" f1 (ell=7) =", f1, " #geodesics=", len(cyc[f1]))
                for P in cyc[f1]:
                    print("    f1 geo:", P)
                print(" V_comp =", sorted(comp), " |V|=", len(comp))
                print(" T on comp:", {u: str(Tf[u]) for u in sorted(comp)})
                print(" R_local :", {u: str(Rloc[u]) for u in sorted(comp)})
                print(" min R_local =", str(min(Rloc.values())))
                # the K2 block on the component
                print(" K2 block (nonzero):")
                for u in sorted(comp):
                    row = {w: str(K2[u][w]) for w in sorted(comp) if K2[u][w] != 0}
                    print("   ", u, "->", row)
                found = True
                break
        if found:
            break
