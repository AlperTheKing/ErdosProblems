"""R38 weak-free attachment hunt via balanced 24-cage deletions.

Delete blue lock edges together with bad atoms, preserving the displayed cut
size balance often destroyed by blue-only mutations.  A candidate is accepted
only after exact maxcut, complete shortest rows, exhaustive defect minimization,
and a weak-free attachment audit at every minimum tuple.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL_PATH = ROOT / "tmp/fanout/r35_24_trade/evaluate_trade.py"
R37_PATH = ROOT / "tmp/fanout/r37_sink_scc_hunt/sink_scc_gate.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = load("r38_trade_model", MODEL_PATH)
R37 = load("r38_r37_helpers", R37_PATH)
R37.M = M
BASE_BLUE = frozenset(M.BLUE)
BASE_BADS = tuple(M.BADS)
BASE_ROWS = tuple(M.DISPLAYED_ROWS)
BASE_EDGES = frozenset(M.EDGES)
ALL_SUPPORT = frozenset(M.edge(row[i], row[i + 1]) for row in BASE_ROWS for i in range(4))
OPTIONAL = tuple(sorted(BASE_BLUE - ALL_SUPPORT))


def adjacency(edges):
    out = [set() for _ in range(M.N)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


def connected(edges):
    adj = adjacency(edges)
    seen, stack = {0}, [0]
    while stack:
        x = stack.pop()
        for y in adj[x] - seen:
            seen.add(y)
            stack.append(y)
    return len(seen) == M.N


def configure(drop_blue, drop_atoms):
    keep = tuple(i for i in range(len(BASE_BADS)) if i not in drop_atoms)
    bads = tuple(BASE_BADS[i] for i in keep)
    displayed_rows = tuple(BASE_ROWS[i] for i in keep)
    support = {M.edge(row[j], row[j + 1]) for row in displayed_rows for j in range(4)}
    blue = set(BASE_BLUE) - set(drop_blue)
    if not support <= blue or not connected(blue):
        return None
    M.BLUE = blue
    M.BAD = set(bads)
    M.BADS = list(bads)
    M.EDGES = blue | set(bads)
    M.BLUE_ADJ = adjacency(blue)
    M.SIGNED_DEGREE = [0] * M.N
    M.EDGE_SIGN = {}
    for sign, family in ((1, M.BLUE), (-1, M.BAD)):
        for x, y in family:
            M.SIGNED_DEGREE[x] += sign
            M.SIGNED_DEGREE[y] += sign
            M.EDGE_SIGN[M.edge(x, y)] = sign
    M.ROW_FAMILIES = [M.shortest_rows(*bad) for bad in M.BADS]
    if any(not family for family in M.ROW_FAMILIES):
        return None
    try:
        displayed = tuple(M.ROW_FAMILIES[i].index(row) for i, row in enumerate(displayed_rows))
    except ValueError:
        return None
    M.RADICES = tuple(len(family) for family in M.ROW_FAMILIES)
    M.DISPLAYED = displayed
    return displayed, blue, bads, displayed_rows


def exact_maxcut(edges):
    adj = [tuple(xs) for xs in adjacency(edges)]
    side = [0] * M.N
    cut = best = 0
    for step in range(1, 1 << (M.N - 1)):
        bit = (step & -step).bit_length() - 1
        v = bit + 1
        old = side[v]
        crossing = sum(side[u] != old for u in adj[v])
        cut += len(adj[v]) - 2 * crossing
        side[v] ^= 1
        best = max(best, cut)
    return best


def weak_attachment_audit(state, certificate):
    rows = [M.ROW_FAMILIES[i][state[i]] for i in range(len(M.BADS))]
    support = {M.edge(row[i], row[i + 1]) for row in rows for i in range(4)}
    selected = set().union(*map(set, rows))
    active_edges = {e for e in M.BLUE if e[0] in selected and e[1] in selected and e not in support}
    active_adj = adjacency(active_edges)
    pair = [[sum(x in row and y in row for row in rows) for y in range(M.N)] for x in range(M.N)]
    shore = certificate["mincut"]["shore_owners"]
    probes = []
    all_weak = True
    no_detour = True
    for owner in shore:
        active_neighbors = sorted(active_adj[owner])
        support_neighbors = sorted(y for y in range(M.N) if M.edge(owner, y) in support)
        for x in active_neighbors:
            for y in support_neighbors:
                if x == y:
                    continue
                sigma = M.SIGNED_DEGREE[x] + M.SIGNED_DEGREE[y] - 2 * M.EDGE_SIGN.get(M.edge(x, y), 0)
                free = pair[x][y] == 0
                weak = free and sigma in (0, 1)
                detour = not free
                probes.append({"owner": owner, "x": x, "y": y, "pairCount": pair[x][y], "sigma": sigma,
                               "weakFree": weak, "detourBranch": detour})
                all_weak &= weak
                no_detour &= not detour
    return {
        "deficientOwners": shore,
        "probes": probes,
        "allProbesWeakFree": bool(probes) and all_weak,
        "noDetourBranch": bool(probes) and no_detour,
        "otherRelationReach": certificate["mincut"]["shore_reach"],
        "shoreDemand": certificate["mincut"]["shore_demand"],
    }


def run(args):
    records = []
    counts = Counter()
    finalists = []
    variants = []
    for blue_count in (1, 2):
        for drop_blue in itertools.combinations(OPTIONAL, blue_count):
            for drop_atoms in itertools.combinations(range(len(BASE_BADS)), blue_count):
                variants.append((drop_blue, drop_atoms))
    variants = variants[args.variant_offset:args.variant_offset + args.variant_limit]

    for index, (drop_blue, drop_atoms) in enumerate(variants):
        configured = configure(drop_blue, set(drop_atoms))
        record = {"index": index, "dropBlue": [list(e) for e in drop_blue], "dropAtoms": list(drop_atoms)}
        if configured is None:
            record["status"] = "structural_reject"
            counts[record["status"]] += 1
            records.append(record)
            continue
        displayed, blue, bads, _ = configured
        record["rowFamilySizes"] = list(M.RADICES)
        record["tupleProduct"] = math.prod(M.RADICES)
        shown = M.evaluate(displayed, certificate=True, include_common_blue=True)
        record["displayedDefect"] = shown["defect"]
        if shown["defect"] == 0:
            record["status"] = "zero_displayed"
        elif record["tupleProduct"] <= args.tuple_bound:
            minimum = shown["defect"]
            minima = []
            for state in itertools.product(*(range(r) for r in M.RADICES)):
                defect = M.evaluate(state, include_common_blue=True)["defect"]
                if defect < minimum:
                    minimum, minima = defect, [state]
                elif defect == minimum:
                    minima.append(state)
                if minimum == 0:
                    break
            record["exactMinimum"] = minimum
            if minimum == 0:
                record["status"] = "zero_exhaustive"
            else:
                record["status"] = "positive_exact_minimum"
                record["minimumStates"] = len(minima)
                finalists.append((record, drop_blue, drop_atoms, minima))
        else:
            zero, searched = R37.find_zero(displayed, args.beam_budget)
            record["beamStates"] = searched
            if zero is not None:
                record["status"] = "zero_beam"
                record["zeroState"] = list(zero)
            else:
                record["status"] = "bounded_unresolved"
        counts[record["status"]] += 1
        records.append(record)

    witnesses = []
    for record, drop_blue, drop_atoms, minima in finalists:
        displayed, blue, bads, _ = configure(drop_blue, set(drop_atoms))
        record["intendedCut"] = len(blue)
        record["exactMaxcut"] = exact_maxcut(set(blue) | set(bads))
        record["realCanonical"] = record["intendedCut"] == record["exactMaxcut"]
        audits = []
        for state in minima:
            cert = M.evaluate(state, certificate=True, include_common_blue=True)
            audits.append({"state": list(state), **weak_attachment_audit(state, cert)})
        record["minimumAudits"] = audits
        record["weakDeadEndAtEveryMinimum"] = bool(audits) and all(
            a["allProbesWeakFree"] and a["noDetourBranch"] and a["otherRelationReach"] == 0
            for a in audits
        )
        if record["realCanonical"] and record["weakDeadEndAtEveryMinimum"]:
            witnesses.append(record["index"])

    payload = {
        "schema": "r38-weak-free-balanced-mutation-hunt-v1",
        "acceptance": "real canonical, positive exact defect minimum, every deficient attachment weak-free, no detour, zero other relation reach",
        "variantLimit": args.variant_limit,
        "variantOffset": args.variant_offset,
        "tupleBound": args.tuple_bound,
        "beamBudget": args.beam_budget,
        "counts": dict(sorted(counts.items())),
        "witnesses": witnesses,
        "records": records,
        "verdict": "DECISIVE_WITNESS" if witnesses else "BOUNDED_ZERO_FAILURE",
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    (HERE / "manifest.json").write_bytes(text.encode("ascii"))
    print(json.dumps({"verdict": payload["verdict"], "counts": payload["counts"], "witnesses": witnesses,
                      "sha256": hashlib.sha256(text.encode("ascii")).hexdigest()}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant-limit", type=int, default=600)
    parser.add_argument("--variant-offset", type=int, default=0)
    parser.add_argument("--tuple-bound", type=int, default=250_000)
    parser.add_argument("--beam-budget", type=int, default=5_000)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
