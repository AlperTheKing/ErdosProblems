"""Exact tester for O-HIT OR DESCEND SINGLE-PORT ROTATION.

For a gamma-min connected-B maximum cut and a saturated vertex v with a zero
B-neighbor, the candidate says that there is a shortest-geodesic prefix A and
a connected zero moat Z containing one zero port such that:

  pdef(A,Z)=0,
  Delta_beta(A)=e_B(v,Z),
  B after flipping S=A union Z is connected,
  and either the chosen geodesic contains an overloaded vertex or Gamma drops.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess

from _bdef_construct import Cn, mycielski
from _codex_direct_overload import build_adj, gamma_min_sides, named_cases
from _codex_direct_zero_sat_o import direct_sets
from _h import GENG, Bconn, dec, loads
from _satzmu_conn import struct_for_side
from _split_satzmu import battery
from _zeromoat import delta_beta, gamma_and_conn


def b_edges(adj, side, n):
    return {
        tuple(sorted((u, v)))
        for u in range(n)
        for v in adj[u]
        if v > u and side[u] != side[v]
    }


def b_boundary_count(adj, side, S, n):
    total = 0
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v] and ((u in S) ^ (v in S)):
                total += 1
    return total


def b_between_count(adj, side, A, Z):
    total = 0
    for u in A:
        for v in adj[u]:
            if v in Z and side[u] != side[v]:
                total += 1
    return total


def connected_zero_subsets(adj, side, zero, z, n):
    zeros = sorted(zero)
    idx = {v: i for i, v in enumerate(zeros)}
    if z not in idx:
        return []
    out = []
    bit_z = 1 << idx[z]
    for mask in range(1, 1 << len(zeros)):
        if not (mask & bit_z):
            continue
        S = {zeros[i] for i in range(len(zeros)) if (mask >> i) & 1}
        seen = {z}
        stack = [z]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y in S and y not in seen and side[x] != side[y]:
                    seen.add(y)
                    stack.append(y)
        if seen == S:
            out.append(S)
    return out


def prefixes_through_v(M, cyc, v):
    for f in M:
        for P in cyc[f]:
            if v not in P:
                continue
            i = P.index(v)
            yield f, tuple(P), set(P[: i + 1])
            yield f, tuple(P), set(P[i:])


def test_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return [], []
    M, _ell, T, _mu, cyc = st
    O = {v for v in range(n) if T[v] > n}
    if not O:
        return [], []
    zero = {v for v in range(n) if T[v] == 0}
    direct = direct_sets(n, cyc)
    G0, _ = gamma_and_conn(adj, side, n)
    records = []
    violations = []
    for v in range(n):
        zports = [z for z in adj[v] if side[v] != side[z] and z in zero]
        if T[v] != n or not zports:
            continue
        direct_os = tuple(sorted(o for o in O if o in direct[v]))
        found = False
        best = None
        for z in zports:
            for Z in connected_zero_subsets(adj, side, zero, z, n):
                r = b_between_count(adj, side, {v}, Z)
                if r == 0:
                    continue
                bd_Z = b_boundary_count(adj, side, Z, n)
                for _f, P, A in prefixes_through_v(M, cyc, v):
                    pdef = bd_Z - 2 * b_between_count(adj, side, A, Z) + r
                    dA = delta_beta(adj, side, A, n)
                    score = (abs(pdef), abs(dA - r))
                    if best is None or score < best[0]:
                        best = (score, {"z": z, "Z": tuple(sorted(Z)), "P": P, "pdef": pdef, "dA": dA, "r": r})
                    if pdef != 0 or dA != r:
                        continue
                    S = A | Z
                    side2 = [1 - side[w] if w in S else side[w] for w in range(n)]
                    GS, bc = gamma_and_conn(adj, side2, n)
                    if not bc or GS is None:
                        continue
                    ohit = bool(set(P) & O)
                    if ohit or GS < G0:
                        found = True
                        best = (score, {"z": z, "Z": tuple(sorted(Z)), "P": P, "pdef": pdef, "dA": dA, "r": r, "ohit": ohit, "GS": GS, "G0": G0})
                        break
                if found:
                    break
            if found:
                break
        rec = {"v": v, "zports": tuple(sorted(zports)), "O": tuple(sorted(O)), "direct_O": direct_os, "found": found, "best": best}
        records.append(rec)
        if not found:
            violations.append(rec)
    return violations, records


def load_case(name, n, edges):
    info = loads(n, edges)
    if info is None:
        return name, 0, None, 0
    viol, records = test_side(n, info["adj"], info["side"])
    return name, len(viol), viol[:1] if viol else None, len(records)


def worker_load(task):
    return load_case(*task)


def run_n12_leaf(verbose=False):
    g6 = "J?AADBWM_}?"
    _n0, e0 = dec(g6)
    adj = build_adj(12, list(e0) + [(8, 11)])
    total = 0
    premise = 0
    first = None
    for side in gamma_min_sides(12, adj):
        viol, records = test_side(12, adj, side)
        total += len(viol)
        premise += len(records)
        first = first or (viol[0] if viol else None)
        if verbose:
            for rec in records:
                print("  rec", rec, flush=True)
    print(f"n12_leaf premise={premise} violations={total} first={first}", flush=True)
    return total


def run_stress():
    total = 0
    premise = 0
    first = None
    cases = list(battery()) + named_cases()
    for name, n, edges in cases:
        _name, count, witness, records = load_case(name, n, edges)
        print(f"stress {name} premise={records} violations={count}", flush=True)
        total += count
        premise += records
        first = first or ((_name, witness) if witness else None)
    print(f"stress_total premise={premise} violations={total} first={first}", flush=True)
    return total


def all_gamma_graph_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    local = 0
    premise = 0
    first = None
    side_count = 0
    for side in gamma_min_sides(nn, adj):
        side_count += 1
        viol, records = test_side(nn, adj, side)
        local += len(viol)
        premise += len(records)
        first = first or (viol[0] if viol else None)
    return g6, side_count, premise, local, first


def run_all_gamma_parallel(nmin, nmax, workers):
    grand = 0
    first = None
    total_sides = 0
    total_premise = 0
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        premise = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for g6, side_count, rec_count, count, witness in pool.imap_unordered(all_gamma_graph_case, g6s, chunksize=16):
                    sides += side_count
                    premise += rec_count
                    local += count
                    first = first or ((g6, witness) if witness else None)
        else:
            for g6 in g6s:
                _g6, side_count, rec_count, count, witness = all_gamma_graph_case(g6)
                sides += side_count
                premise += rec_count
                local += count
                first = first or ((g6, witness) if witness else None)
        grand += local
        total_sides += sides
        total_premise += premise
        print(
            f"all_gamma_parallel N={n} graphs={len(g6s)} sides={sides} premise={premise} violations={local}",
            flush=True,
        )
    print(
        f"all_gamma_parallel_total sides={total_sides} premise={total_premise} violations={grand} first={first}",
        flush=True,
    )
    return grand


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n12-leaf", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--stress", action="store_true")
    ap.add_argument("--all-gamma-parallel", action="store_true")
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    total = 0
    if args.n12_leaf:
        total += run_n12_leaf(args.verbose)
    if args.stress:
        total += run_stress()
    if args.all_gamma_parallel:
        total += run_all_gamma_parallel(args.nmin, args.nmax, args.workers)
    if not (args.n12_leaf or args.stress or args.all_gamma_parallel):
        total += run_n12_leaf(args.verbose)
        total += run_stress()
    print(f"TOTAL violations={total}", flush=True)


if __name__ == "__main__":
    main()
