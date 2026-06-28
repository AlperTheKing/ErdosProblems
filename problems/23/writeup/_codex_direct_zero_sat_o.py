"""Exact tester for qualitative DIRECT-ZERO-SAT-O.

Candidate:

If a gamma-min connected-B maximum cut has O={T>N} nonempty, T[v] == N,
and v has a B-neighbour z with T[z] == 0, then v shares at least one shortest
bad-edge geodesic with some overloaded vertex o in O.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import multiprocessing as mp
import subprocess

from _bdef_construct import Cn, mycielski
from _codex_direct_overload import build_adj, direct_sets, gamma_min_sides, named_cases
from _h import Bconn, GENG, dec, loads, maxcut_all
from _satzmu_conn import struct_for_side
from _split_satzmu import battery


def violations_for_side(n, adj, side, include_records=False):
    st = struct_for_side(n, adj, side)
    if st is None:
        return [], []
    _bad, _ell, T, _mu, cyc = st
    O = {v for v in range(n) if T[v] > n}
    if not O:
        return [], []
    direct = direct_sets(n, cyc)
    zero = {v for v in range(n) if T[v] == 0}
    viol = []
    records = []
    for v in range(n):
        zbd = sum(1 for w in adj[v] if side[v] != side[w] and w in zero)
        if T[v] != n or zbd == 0:
            continue
        direct_os = tuple(sorted(o for o in O if o in direct[v]))
        rec = {
            "v": v,
            "zbd": zbd,
            "O": tuple(sorted(O)),
            "direct_O": direct_os,
        }
        if not direct_os:
            viol.append(rec)
        if include_records:
            records.append(rec)
    return viol, records


def load_case(name, n, edges):
    info = loads(n, edges)
    if info is None:
        return name, 0, None
    viol, _records = violations_for_side(n, info["adj"], info["side"])
    return name, len(viol), viol[:2] if viol else None


def worker_load(task):
    return load_case(*task)


def run_n12_leaf(verbose=False):
    g6 = "J?AADBWM_}?"
    n0, e0 = dec(g6)
    adj = build_adj(12, list(e0) + [(8, 11)])
    sides = gamma_min_sides(12, adj)
    total = 0
    first = None
    records = []
    for side in sides:
        viol, recs = violations_for_side(12, adj, side, include_records=verbose)
        total += len(viol)
        first = first or (viol[0] if viol else None)
        records.extend(recs)
    print(f"n12_leaf gamma_min_sides={len(sides)} violations={total} first={first}", flush=True)
    if verbose:
        for rec in records:
            print("  rec", rec, flush=True)
    return total


def run_glued():
    total = 0
    first = None
    cases = 0
    for name, n, edges in battery():
        cases += 1
        _name, count, witness = load_case(name, n, edges)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"glued_load cases={cases} violations={total} first={first}", flush=True)
    return total


def run_named():
    total = 0
    first = None
    for name, n, edges in named_cases():
        _name, count, witness = load_case(name, n, edges)
        print(f"named {name} violations={count}", flush=True)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"named_total violations={total} first={first}", flush=True)
    return total


def run_census_loads(nmin, nmax, workers):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = []
        for g6 in g6s:
            nn, edges = dec(g6)
            tasks.append((g6, nn, edges))
        local = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for name, count, witness in pool.imap_unordered(worker_load, tasks, chunksize=16):
                    local += count
                    first = first or ((name, witness) if witness else None)
        else:
            for task in tasks:
                name, count, witness = worker_load(task)
                local += count
                first = first or ((name, witness) if witness else None)
        grand += local
        print(f"census_load N={n} graphs={len(tasks)} violations={local}", flush=True)
    print(f"census_load_total violations={grand} first={first}", flush=True)
    return grand


def all_gamma_graph_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    local = 0
    first = None
    side_count = 0
    for side in gamma_min_sides(nn, adj):
        side_count += 1
        viol, _records = violations_for_side(nn, adj, side)
        local += len(viol)
        first = first or (viol[0] if viol else None)
    return g6, side_count, local, first


def all_max_graph_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    local = 0
    first = None
    side_count = 0
    premise = 0
    for side in maxcut_all(nn, adj):
        if not Bconn(nn, adj, side):
            continue
        side_count += 1
        viol, records = violations_for_side(nn, adj, side, include_records=True)
        local += len(viol)
        premise += len(records)
        first = first or (viol[0] if viol else None)
    return g6, side_count, premise, local, first


def all_gamma_summary_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    side_count = 0
    premise = 0
    viol = 0
    zbd_counter = Counter()
    direct_count_counter = Counter()
    o_count_counter = Counter()
    quantitative_slack_counter = Counter()
    first_record = None
    for side in gamma_min_sides(nn, adj):
        side_count += 1
        st = struct_for_side(nn, adj, side)
        if st is None:
            continue
        _bad, _ell, T, _mu, cyc = st
        O = {v for v in range(nn) if T[v] > nn}
        if not O:
            continue
        direct = direct_sets(nn, cyc)
        zero = {v for v in range(nn) if T[v] == 0}
        for v in range(nn):
            zbd = sum(1 for w in adj[v] if side[v] != side[w] and w in zero)
            if T[v] != nn or zbd == 0:
                continue
            direct_os = tuple(sorted(o for o in O if o in direct[v]))
            direct_over = sum(T[o] - nn for o in direct_os)
            slack = 2 * direct_over - zbd
            premise += 1
            zbd_counter[zbd] += 1
            direct_count_counter[len(direct_os)] += 1
            o_count_counter[len(O)] += 1
            quantitative_slack_counter[slack] += 1
            rec = {
                "side": side,
                "v": v,
                "zbd": zbd,
                "O": tuple(sorted(O)),
                "direct_O": direct_os,
                "slack": slack,
            }
            first_record = first_record or rec
            if not direct_os:
                viol += 1
    return {
        "g6": g6,
        "side_count": side_count,
        "premise": premise,
        "viol": viol,
        "zbd": zbd_counter,
        "direct_count": direct_count_counter,
        "o_count": o_count_counter,
        "qslack": quantitative_slack_counter,
        "first": first_record,
    }


def first_direct_witness(v, o, cyc):
    for f, paths in cyc.items():
        for path in paths:
            support = set(path)
            if v in support and o in support:
                return f, tuple(path)
    return None


def first_incident_direct_witness(v, o, cyc):
    for f, paths in cyc.items():
        if v not in f:
            continue
        for path in paths:
            support = set(path)
            if v in support and o in support:
                return f, tuple(path)
    return None


def co_traffic_weight(v, o, ell, cyc):
    total = 0
    for f, paths in cyc.items():
        L = ell[f]
        denom = len(paths)
        for path in paths:
            support = set(path)
            if v in support and o in support:
                total += Fraction(L, denom)
    return total


def cut_distance(n, adj, side, src, dst):
    if src == dst:
        return 0
    seen = {src}
    q = [(src, 0)]
    for x, d in q:
        for y in adj[x]:
            if side[x] == side[y] or y in seen:
                continue
            if y == dst:
                return d + 1
            seen.add(y)
            q.append((y, d + 1))
    return None


def all_gamma_records_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    records = []
    side_index = -1
    for side in gamma_min_sides(nn, adj):
        side_index += 1
        st = struct_for_side(nn, adj, side)
        if st is None:
            continue
        bad, ell, T, _mu, cyc = st
        O = {v for v in range(nn) if T[v] > nn}
        if not O:
            continue
        direct = direct_sets(nn, cyc)
        zero = {v for v in range(nn) if T[v] == 0}
        for v in range(nn):
            zports = tuple(sorted(w for w in adj[v] if side[v] != side[w] and w in zero))
            if T[v] != nn or not zports:
                continue
            direct_os = tuple(sorted(o for o in O if o in direct[v]))
            if not direct_os:
                witness = None
                incident_witness = None
                d_b_vo = None
                d_b_zo = None
            else:
                witness = first_direct_witness(v, direct_os[0], cyc)
                incident_witness = first_incident_direct_witness(v, direct_os[0], cyc)
                d_b_vo = cut_distance(nn, adj, side, v, direct_os[0])
                d_b_zo = tuple(cut_distance(nn, adj, side, z, direct_os[0]) for z in zports)
                co_weight = co_traffic_weight(v, direct_os[0], ell, cyc)
            records.append(
                {
                    "g6": g6,
                    "side_index": side_index,
                    "side": tuple(side),
                    "v": v,
                    "zports": zports,
                    "O": tuple(sorted(O)),
                    "direct_O": direct_os,
                    "T": tuple(T),
                    "M": tuple(sorted(tuple(sorted(e)) for e in bad)),
                    "ell": {tuple(sorted(k)): val for k, val in ell.items()},
                    "witness": witness,
                    "incident_witness": incident_witness,
                    "dB_v_o": d_b_vo,
                    "dB_z_o": d_b_zo,
                    "co_weight": co_weight if direct_os else None,
                }
            )
    return records


def run_all_gamma_parallel(nmin, nmax, workers):
    grand = 0
    first = None
    total_sides = 0
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for g6, side_count, count, witness in pool.imap_unordered(all_gamma_graph_case, g6s, chunksize=16):
                    sides += side_count
                    local += count
                    first = first or ((g6, witness) if witness else None)
        else:
            for g6 in g6s:
                _g6, side_count, count, witness = all_gamma_graph_case(g6)
                sides += side_count
                local += count
                first = first or ((g6, witness) if witness else None)
        grand += local
        total_sides += sides
        print(
            f"all_gamma_parallel N={n} graphs={len(g6s)} gamma_min_sides={sides} violations={local}",
            flush=True,
        )
    print(
        f"all_gamma_parallel_total sides={total_sides} violations={grand} first={first}",
        flush=True,
    )
    return grand


def run_all_max_parallel(nmin, nmax, workers):
    grand = 0
    first = None
    total_sides = 0
    total_premise = 0
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        sides = 0
        premise = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for g6, side_count, rec_count, count, witness in pool.imap_unordered(all_max_graph_case, g6s, chunksize=16):
                    sides += side_count
                    premise += rec_count
                    local += count
                    first = first or ((g6, witness) if witness else None)
        else:
            for g6 in g6s:
                _g6, side_count, rec_count, count, witness = all_max_graph_case(g6)
                sides += side_count
                premise += rec_count
                local += count
                first = first or ((g6, witness) if witness else None)
        total_sides += sides
        total_premise += premise
        grand += local
        print(
            f"all_max_parallel N={n} graphs={len(g6s)} connected_maxcuts={sides} premise={premise} violations={local}",
            flush=True,
        )
    print(
        f"all_max_parallel_total sides={total_sides} premise={total_premise} violations={grand} first={first}",
        flush=True,
    )
    return grand


def run_all_gamma_summary(nmin, nmax, workers):
    grand_premise = 0
    grand_viol = 0
    total_sides = 0
    zbd_counter = Counter()
    direct_count_counter = Counter()
    o_count_counter = Counter()
    qslack_counter = Counter()
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local_premise = 0
        local_viol = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                iterator = pool.imap_unordered(all_gamma_summary_case, g6s, chunksize=16)
                for res in iterator:
                    sides += res["side_count"]
                    local_premise += res["premise"]
                    local_viol += res["viol"]
                    zbd_counter.update(res["zbd"])
                    direct_count_counter.update(res["direct_count"])
                    o_count_counter.update(res["o_count"])
                    qslack_counter.update(res["qslack"])
                    first = first or res["first"]
        else:
            for res in map(all_gamma_summary_case, g6s):
                sides += res["side_count"]
                local_premise += res["premise"]
                local_viol += res["viol"]
                zbd_counter.update(res["zbd"])
                direct_count_counter.update(res["direct_count"])
                o_count_counter.update(res["o_count"])
                qslack_counter.update(res["qslack"])
                first = first or res["first"]
        total_sides += sides
        grand_premise += local_premise
        grand_viol += local_viol
        print(
            f"summary N={n} graphs={len(g6s)} gamma_min_sides={sides} premise={local_premise} violations={local_viol}",
            flush=True,
        )
    print(f"summary_total sides={total_sides} premise={grand_premise} violations={grand_viol}", flush=True)
    print(f"zbd={dict(sorted(zbd_counter.items()))}", flush=True)
    print(f"direct_count={dict(sorted(direct_count_counter.items()))}", flush=True)
    print(f"O_count={dict(sorted(o_count_counter.items()))}", flush=True)
    print(f"quantitative_slack={dict(sorted((str(k), v) for k, v in qslack_counter.items()))}", flush=True)
    print(f"first={first}", flush=True)
    return grand_viol


def run_all_gamma_records(nmin, nmax, workers):
    records = []
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for recs in pool.imap_unordered(all_gamma_records_case, g6s, chunksize=16):
                    records.extend(recs)
        else:
            for g6 in g6s:
                records.extend(all_gamma_records_case(g6))
        print(f"records N={n} count={len(records)}", flush=True)
    for rec in records:
        print(rec, flush=True)
    print(f"records_total count={len(records)}", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n12-leaf", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--stress", action="store_true")
    ap.add_argument("--census-loads", action="store_true")
    ap.add_argument("--all-gamma-parallel", action="store_true")
    ap.add_argument("--all-max-parallel", action="store_true")
    ap.add_argument("--all-gamma-summary", action="store_true")
    ap.add_argument("--all-gamma-records", action="store_true")
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    total = 0
    if args.n12_leaf:
        total += run_n12_leaf(args.verbose)
    if args.stress:
        total += run_glued()
        total += run_named()
    if args.census_loads:
        total += run_census_loads(args.nmin, args.nmax, args.workers)
    if args.all_gamma_parallel:
        total += run_all_gamma_parallel(args.nmin, args.nmax, args.workers)
    if args.all_max_parallel:
        total += run_all_max_parallel(args.nmin, args.nmax, args.workers)
    if args.all_gamma_summary:
        total += run_all_gamma_summary(args.nmin, args.nmax, args.workers)
    if args.all_gamma_records:
        total += run_all_gamma_records(args.nmin, args.nmax, args.workers)
    if not (
        args.n12_leaf
        or args.stress
        or args.census_loads
        or args.all_gamma_parallel
        or args.all_max_parallel
        or args.all_gamma_summary
        or args.all_gamma_records
    ):
        total += run_n12_leaf(args.verbose)
        total += run_glued()
        total += run_named()
    print(f"TOTAL violations={total}", flush=True)


if __name__ == "__main__":
    main()
