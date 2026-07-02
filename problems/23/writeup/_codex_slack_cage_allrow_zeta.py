"""Driver for the compiled all-row Slack-CAGE zeta scanner.

This script extracts exact shortest-row data for a selected named graph and
connected gamma-minimum maximum cut, compiles the C++ scanner if needed, and
feeds it an integer-scaled instance.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import math
import os
import subprocess
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_mycgrotzsch_exact_maxcut_c5lift import (
        enumerate_maxcuts_gray,
        gamma_for_side,
        side_list,
        side_string,
    )
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


HERE = Path(__file__).resolve().parent
CPP = HERE / "_codex_slack_cage_allrow_zeta.cpp"
EXE = HERE / "_codex_slack_cage_allrow_zeta.exe"


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def graph_by_name(name: str):
    def petersen():
        edges = []
        for i in range(5):
            edges.append((i, (i + 1) % 5))
            edges.append((5 + i, 5 + ((i + 2) % 5)))
            edges.append((i, 5 + i))
        return 10, edges

    def blowup_graph(graph, t):
        n, edges = graph
        out = []
        for u, v in edges:
            for i in range(t):
                for j in range(t):
                    out.append((t * u + i, t * v + j))
        return t * n, out

    if name == "Grotzsch":
        return mycielski(5, Cn(5))
    if name == "MycGrotzsch":
        return mycielski(*mycielski(5, Cn(5)))
    if name == "Petersen":
        return petersen()
    if name == "Petersen2":
        return blowup_graph(petersen(), 2)
    if name == "MycPetersen":
        return mycielski(*petersen())
    if name == "MycC7":
        return mycielski(7, Cn(7))
    if name == "MycC9":
        return mycielski(9, Cn(9))
    if name == "MycC11":
        return mycielski(11, Cn(11))
    if name == "C7Grotzsch":
        block1 = (7, Cn(7))
        block2 = mycielski(5, Cn(5))
        n, edges = union_disjoint(block1, block2)
        return n, edges + [(0, block1[0] + 0)]
    if name.startswith("g6:"):
        return dec(name[3:])
    raise ValueError(f"unknown graph: {name}")


def gamma_min_sides(n, edges):
    adj = adj_of(n, edges)
    if n <= 23:
        best, max_sides = enumerate_maxcuts_gray(n, edges)
        connected = []
        gammas = []
        for side_int in max_sides:
            side = side_list(n, side_int)
            if not Bconn(n, adj, side):
                continue
            gamma = gamma_for_side(n, adj, side)
            if gamma is None:
                continue
            connected.append(side_int)
            gammas.append(gamma)
        min_gamma = min(gammas) if gammas else None
        gmin = [s for s, g in zip(connected, gammas) if g == min_gamma]
        return best, min_gamma, [side_list(n, s) for s in gmin], [side_string(n, s) for s in gmin]

    _adj, cuts = gmins(n, edges)
    best = None
    min_gamma = None
    out = []
    out_s = []
    for side_s in cuts:
        side = [int(c) for c in side_s]
        gamma = gamma_for_side(n, adj, side)
        if gamma is None:
            continue
        if min_gamma is None or gamma < min_gamma:
            min_gamma = gamma
            out = [side]
            out_s = ["".join(map(str, side))]
        elif gamma == min_gamma:
            out.append(side)
            out_s.append("".join(map(str, side)))
    return best, min_gamma, out, out_s


def compile_cpp(force: bool):
    if EXE.exists() and not force and EXE.stat().st_mtime >= CPP.stat().st_mtime:
        return
    cmd = [
        "g++",
        "-O3",
        "-march=native",
        "-fopenmp",
        "-std=c++17",
        str(CPP),
        "-o",
        str(EXE),
    ]
    subprocess.run(cmd, check=True)


def build_payload(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        raise RuntimeError("struct_for_side failed")
    M_raw, _ell_raw, _T, _mu, cyc_raw = st
    M = [norm(g) for g in M_raw]
    Mset = set(M)
    E = {norm(e) for e in edges}
    B = sorted(E - Mset)

    scale = 25
    for g in M_raw:
        scale = math.lcm(scale, len(cyc_raw[g]))
    eta_int = (n * n - 25 * len(M)) * (scale // 25)

    lines = [f"{n} {scale} {eta_int}"]
    lines.append(str(len(B)))
    for u, v in B:
        lines.append(f"{u} {v}")
    lines.append(str(len(M)))
    for u, v in sorted(Mset):
        lines.append(f"{u} {v}")

    atoms = []
    targets = []
    for g in M_raw:
        coeff = scale // len(cyc_raw[g])
        for P in cyc_raw[g]:
            row = tuple(P)
            atoms.append((coeff, row))
            targets.append(row)

    lines.append(str(len(atoms)))
    for coeff, row in atoms:
        lines.append(" ".join([str(coeff), str(len(row)), *map(str, row)]))
    lines.append(str(len(targets)))
    for row in targets:
        lines.append(" ".join([str(len(row)), *map(str, row)]))
    return "\n".join(lines) + "\n", len(M), len(targets), scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="MycGrotzsch")
    ap.add_argument("--side-index", type=int, default=0)
    ap.add_argument("--threads", type=int, default=60)
    ap.add_argument("--force-compile", action="store_true")
    args = ap.parse_args()

    n, edges = graph_by_name(args.graph)
    maxcut_value, min_gamma, sides, side_strings = gamma_min_sides(n, edges)
    if not sides:
        raise SystemExit("no connected gamma-min maximum cut found")
    side = sides[args.side_index]
    payload, m, nrows, scale = build_payload(n, edges, side)

    compile_cpp(args.force_compile)
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(args.threads)
    print("=== all-row Slack-CAGE driver ===")
    print("graph:", args.graph)
    print("n:", n)
    print("edges:", len(edges))
    print("maxcut_value:", maxcut_value)
    print("min_gamma_connected_maxcuts:", min_gamma)
    print("gamma_min_connected_sides:", len(sides))
    print("side:", side_strings[args.side_index])
    print("m:", m)
    print("rows:", nrows)
    print("scale:", scale)
    print("threads:", args.threads)
    print("--- scanner ---", flush=True)
    proc = subprocess.run(
        [str(EXE), str(args.threads)],
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )
    print(proc.stdout, end="")
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
