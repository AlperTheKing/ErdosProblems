#!/usr/bin/env python3
"""Exact C5-homomorphism/core audit for the Wave-4 rotor fixtures.

The script deliberately keeps four notions separate:

* a production graph (all blue and bad edges),
* the displayed maximum-cut candidate,
* the complete-row support F*, and
* a support-only rooted t=5 hit padded to the production order 25.

SAT/CP-SAT is used only with integer/Boolean constraints.  Every positive
witness is checked again by direct set arithmetic before it is serialized.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import runpy
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ortools.sat.python import cp_model
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "audit_result.json"

Edge = tuple[int, int]
Row = tuple[int, int, int, int, int]


def edge(u: int, v: int) -> Edge:
    if u == v:
        raise ValueError(f"loop {u}")
    return (u, v) if u < v else (v, u)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Fixture:
    name: str
    scope: str
    n: int
    blue: set[Edge]
    bad: set[Edge]
    side: list[int]
    support: set[Edge] = field(default_factory=set)
    atoms: list[Edge] = field(default_factory=list)
    rows: dict[Edge, list[Row]] = field(default_factory=dict)
    nominal_t: int | None = None
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def edges(self) -> set[Edge]:
        return self.blue | self.bad


def adjacency(n: int, edges: Iterable[Edge]) -> list[set[int]]:
    ans = [set() for _ in range(n)]
    for u, v in edges:
        if not (0 <= u < v < n):
            raise AssertionError((n, u, v))
        ans[u].add(v)
        ans[v].add(u)
    return ans


def derive_side(n: int, blue: set[Edge], bad: set[Edge]) -> list[int]:
    """Recover a displayed cut from blue/bad parity constraints."""
    signed = [(u, v, 1) for u, v in blue] + [(u, v, 0) for u, v in bad]
    inc: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, parity in signed:
        inc[u].append((v, parity))
        inc[v].append((u, parity))
    side = [-1] * n
    for root in range(n):
        if side[root] >= 0:
            continue
        side[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v, parity in inc[u]:
                wanted = side[u] ^ parity
                if side[v] < 0:
                    side[v] = wanted
                    queue.append(v)
                elif side[v] != wanted:
                    raise AssertionError(("inconsistent displayed cut", u, v))
    return side


def simple_triangle_count(n: int, edges: set[Edge]) -> int:
    adj = adjacency(n, edges)
    return sum(
        1
        for u in range(n)
        for v in adj[u]
        if u < v
        for w in (adj[u] & adj[v])
        if v < w
    )


def all_blue_rows(adj: list[set[int]], source: int, target: int) -> list[Row]:
    out: list[Row] = []

    def visit(path: list[int]) -> None:
        if len(path) == 5:
            if path[-1] == target:
                out.append(tuple(path))
            return
        for nxt in sorted(adj[path[-1]]):
            if nxt in path:
                continue
            if len(path) == 4 and nxt != target:
                continue
            visit(path + [nxt])

    visit([source])
    return out


def complete_row_audit(f: Fixture) -> dict[str, Any]:
    if not f.atoms:
        return {"applicable": False, "reason": "no atom database"}
    blue_adj = adjacency(f.n, f.blue)
    listed_keys = [edge(*a) for a in f.atoms]
    covered_once = len(listed_keys) == len(set(listed_keys)) and set(listed_keys) == f.bad
    missing: list[list[int]] = []
    extra: list[list[int]] = []
    row_support: set[Edge] = set()
    total_actual = 0
    total_listed = 0
    for atom in sorted(f.bad):
        actual = set(all_blue_rows(blue_adj, atom[0], atom[1]))
        listed = set(f.rows.get(atom, []))
        # Accept a source database whose atom orientation is reversed.
        listed_oriented = {
            r if (r[0], r[-1]) == atom else tuple(reversed(r)) for r in listed
        }
        total_actual += len(actual)
        total_listed += len(listed_oriented)
        for r in actual - listed_oriented:
            missing.append(list(r))
        for r in listed_oriented - actual:
            extra.append(list(r))
        for r in listed_oriented:
            row_support.update(edge(r[i], r[i + 1]) for i in range(4))
    return {
        "applicable": True,
        "covers_all_bad_edges_once": covered_once,
        "listed_rows": total_listed,
        "actual_simple_blue_length4_rows": total_actual,
        "missing_row_count": len(missing),
        "extra_row_count": len(extra),
        "missing_row_sample": missing[:3],
        "extra_row_sample": extra[:3],
        "row_support_cardinality": len(row_support),
        "declared_support_cardinality": len(f.support),
        "row_support_equals_declared": row_support == f.support,
        "complete": covered_once and not missing and not extra,
    }


def minimum_switch_sigma(f: Fixture, timeout: float = 120.0) -> dict[str, Any]:
    """Minimize crossed-blue minus crossed-bad over all vertex switches."""
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x_{v}") for v in range(f.n)]
    if f.n:
        model.add(x[0] == 0)
    signed_terms = []
    y_vars: dict[Edge, cp_model.IntVar] = {}
    for uv in sorted(f.edges):
        u, v = uv
        y = model.new_bool_var(f"cross_{u}_{v}")
        model.add_allowed_assignments(
            [x[u], x[v], y], [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
        )
        y_vars[uv] = y
        signed_terms.append(y if uv in f.blue else -y)
    sigma = model.new_int_var(-len(f.bad), len(f.blue), "sigma")
    model.add(sigma == sum(signed_terms))
    model.minimize(sigma)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.random_seed = 0
    status = solver.solve(model)
    status_name = solver.status_name(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": status_name}
    switch = [v for v in range(f.n) if solver.value(x[v])]
    direct = sum(((u in switch) != (v in switch)) for u, v in f.blue) - sum(
        ((u in switch) != (v in switch)) for u, v in f.bad
    )
    value = solver.value(sigma)
    if direct != value:
        raise AssertionError((direct, value))
    beta = len(f.bad) + value
    return {
        "status": status_name,
        "minimum_sigma": value,
        "switch": switch,
        "displayed_cut_is_maximum": status == cp_model.OPTIMAL and value >= 0,
        "beta": beta if status == cp_model.OPTIMAL else None,
        "D_ext": f.n * f.n - 25 * beta if status == cp_model.OPTIMAL else None,
        "objective_bound": int(round(solver.best_objective_bound)),
    }


def c5_homomorphism(f: Fixture) -> dict[str, Any]:
    def var(v: int, colour: int) -> int:
        return 1 + 5 * v + colour

    with Solver(name="cadical195") as solver:
        for v in range(f.n):
            solver.add_clause([var(v, c) for c in range(5)])
            for a in range(5):
                for b in range(a + 1, 5):
                    solver.add_clause([-var(v, a), -var(v, b)])
        for u, v in sorted(f.edges):
            for a in range(5):
                for b in range(5):
                    if (a - b) % 5 not in (1, 4):
                        solver.add_clause([-var(u, a), -var(v, b)])
        sat = solver.solve()
        if not sat:
            return {"sat": False, "solver": "cadical195"}
        model = set(lit for lit in solver.get_model() if lit > 0)
    labels = [next(c for c in range(5) if var(v, c) in model) for v in range(f.n)]
    if any((labels[u] - labels[v]) % 5 not in (1, 4) for u, v in f.edges):
        raise AssertionError("invalid C5 homomorphism")
    return {"sat": True, "solver": "cadical195", "labels": labels}


def aligned_core(f: Fixture, timeout: float = 120.0) -> dict[str, Any]:
    """Maximize min_i |X_i| for the displayed aligned C5 cut pattern."""
    all_pairs = {(u, v) for u in range(f.n) for v in range(u + 1, f.n)}
    nonedges = all_pairs - f.edges
    best: dict[str, Any] | None = None
    for complement in (0, 1):
        pattern = [complement ^ s for s in (0, 0, 1, 0, 1)]
        model = cp_model.CpModel()
        x = [[model.new_bool_var(f"x_{v}_{i}") for i in range(5)] for v in range(f.n)]
        for v in range(f.n):
            model.add(sum(x[v]) <= 1)
            for i in range(5):
                if f.side[v] != pattern[i]:
                    model.add(x[v][i] == 0)
        q = model.new_int_var(0, f.n // 5, "q")
        for i in range(5):
            model.add(sum(x[v][i] for v in range(f.n)) >= q)
        for u, v in nonedges:
            for i in range(5):
                j = (i + 1) % 5
                model.add(x[u][i] + x[v][j] <= 1)
                model.add(x[v][i] + x[u][j] <= 1)
        model.maximize(q)
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.max_time_in_seconds = timeout
        solver.parameters.random_seed = 0
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            candidate = {"status": solver.status_name(status), "q": -1}
        else:
            classes = [[v for v in range(f.n) if solver.value(x[v][i])] for i in range(5)]
            qv = min(map(len, classes))
            for i in range(5):
                for u in classes[i]:
                    for v in classes[(i + 1) % 5]:
                        if edge(u, v) not in f.edges:
                            raise AssertionError(("noncomplete core", i, u, v))
            candidate = {
                "status": solver.status_name(status),
                "q": qv,
                "classes": classes,
                "cut_pattern": pattern,
                "objective_bound": int(round(solver.best_objective_bound)),
            }
        if best is None or candidate["q"] > best["q"]:
            best = candidate
    assert best is not None
    if f.nominal_t is not None and best["q"] >= 0:
        best["K"] = f.nominal_t - best["q"]
        best["K_le_3"] = best["K"] <= 3
    return best


def graph_field_audit(f: Fixture) -> dict[str, Any]:
    row = complete_row_audit(f)
    t = f.nominal_t
    return {
        "graph_checked": len(f.edges) == len(set(f.edges))
        and not (f.blue & f.bad)
        and all(0 <= u < v < f.n for u, v in f.edges),
        "cut_checked": len(f.side) == f.n
        and all(f.side[u] != f.side[v] for u, v in f.blue)
        and all(f.side[u] == f.side[v] for u, v in f.bad),
        "triangle_count": simple_triangle_count(f.n, f.edges),
        "triangle_free": simple_triangle_count(f.n, f.edges) == 0,
        "vertex_window": t is not None and f.n == 5 * t,
        "bad_window": t is not None and len(f.bad) == t * t,
        "circuit_cardinality": t is not None and len(f.support) + 1 == len(f.bad),
        "complete_rows": row,
    }


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_p5_cages() -> list[Fixture]:
    gate_path = ROOT / "tmp/fanout/p5_fixtures/gate.py"
    gate = load_module("wave4_p5_gate", gate_path)
    out = []
    for name in ("24", "167", "175", "311", "3892", "89", "2943"):
        src = gate.BUILDERS[name]()
        blue, bad = set(src.blue), set(src.bad)
        side = derive_side(src.n, blue, bad)
        rows: dict[Edge, list[Row]] = {}
        for a, r in zip(src.atoms, src.rows):
            rows.setdefault(edge(*a), []).append(tuple(r))
        out.append(
            Fixture(
                name=f"p5_cage_{name}",
                scope="real cage / selected-row diagnostic",
                n=src.n,
                blue=blue,
                bad=bad,
                side=side,
                support={edge(r[i], r[i + 1]) for r in src.rows for i in range(4)},
                atoms=[edge(*a) for a in src.atoms],
                rows=rows,
                source=str(gate_path.relative_to(ROOT)),
                metadata={"fixture": name},
            )
        )
    return out


def load_r41() -> Fixture:
    path = ROOT / "tmp/fanout/r41_rotor_realization/manifest.json"
    data = json.loads(path.read_text())
    blue = {edge(*e) for e in data["blue"]}
    bad = {edge(*e) for e in data["bad"]}
    side = derive_side(data["structural"]["n"], blue, bad)
    rows: dict[Edge, list[Row]] = {}
    for atom, family in zip(sorted(bad), data["completeFamilies"]):
        rows[atom] = [tuple(r) for r in family]
    support = {edge(r[i], r[i + 1]) for fam in rows.values() for r in fam for i in range(4)}
    return Fixture(
        name="r41_real_saturated_cage",
        scope="real maximum-cut cage; not an M3 rotor",
        n=data["structural"]["n"],
        blue=blue,
        bad=bad,
        side=side,
        support=support,
        atoms=sorted(bad),
        rows=rows,
        source=str(path.relative_to(ROOT)),
        metadata={"canonicalPayloadSha256": data["canonicalPayloadSha256"]},
    )


def load_r40_n78() -> Fixture:
    path = ROOT / "problems/23/writeup/_claude_r40_n78_instance_gate.py"
    ns = runpy.run_path(str(path), run_name="wave4_r40_fixture")
    blue = {edge(*tuple(e)) for e in ns["blue"]}
    bad = {edge(*tuple(e)) for e in ns["bad"]}
    side = list(ns["side"])
    fams = ns["fams"]
    rows = {edge(*a): [tuple(r) for r in fam] for a, fam in fams.items()}
    support = {edge(r[i], r[i + 1]) for fam in rows.values() for r in fam for i in range(4)}
    return Fixture(
        name="r40_n78_grafted_rotor_cage",
        scope="real four-state defect-zero cage; not balanced-deficiency M3",
        n=ns["N"],
        blue=blue,
        bad=bad,
        side=side,
        support=support,
        atoms=sorted(bad),
        rows=rows,
        source=str(path.relative_to(ROOT)),
        metadata={"sourceSha256": sha256(path)},
    )


def load_t5_support_hits() -> list[Fixture]:
    directory = ROOT / "tmp/fanout/r42_graph_specific_exclusion"
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        hit = data.get("hit")
        if (
            data.get("schema") == "rooted-t5-support-circuit-search-v1"
            and hit
            and len(hit.get("selectedAtoms", [])) == 25
            and len(hit.get("supportEdges", [])) == 24
        ):
            candidates.append((path, data))
    seen: set[str] = set()
    out: list[Fixture] = []
    for path, data in candidates:
        hit = data["hit"]
        blue = {edge(*e) for e in hit["supportEdges"]}
        bad = {edge(a["u"], a["v"]) for a in hit["selectedAtoms"]}
        signature = hashlib.sha256(
            json.dumps([sorted(blue), sorted(bad)], separators=(",", ":")).encode()
        ).hexdigest()
        if signature in seen:
            continue
        seen.add(signature)
        left = int(data["left"])
        support_n = max(v for e in blue | bad for v in e) + 1
        if support_n > 25:
            raise AssertionError(support_n)
        side = [0 if v < left else 1 for v in range(support_n)] + [0] * (25 - support_n)
        rows: dict[Edge, list[Row]] = {}
        for atom in hit["selectedAtoms"]:
            key = edge(atom["u"], atom["v"])
            rows[key] = [tuple(r) for r in atom["rows"]]
        out.append(
            Fixture(
                name=f"t5_support_{path.stem}",
                scope="accepted support circuit padded by isolated vertices; not production",
                n=25,
                blue=blue,
                bad=bad,
                side=side,
                support=blue.copy(),
                atoms=sorted(bad),
                rows=rows,
                nominal_t=5,
                source=str(path.relative_to(ROOT)),
                metadata={
                    "supportOrder": support_n,
                    "graph6": hit.get("graph6"),
                    "sourceCanonicalSha256": data.get("canonicalSha256"),
                    "projection": "seven isolated vertices added only when support order is 18",
                },
            )
        )
    return out


def c5_blowup(class_sizes: list[int]) -> tuple[int, list[list[int]], set[Edge]]:
    classes: list[list[int]] = []
    cursor = 0
    for size in class_sizes:
        classes.append(list(range(cursor, cursor + size)))
        cursor += size
    edges = {
        edge(u, v)
        for i in range(5)
        for u in classes[i]
        for v in classes[(i + 1) % 5]
    }
    return cursor, classes, edges


def adversarial_deleted_matching(t: int = 8) -> Fixture:
    n, classes, edges = c5_blowup([t] * 5)
    deleted = {edge(classes[0][i], classes[1][i]) for i in range(t)}
    edges -= deleted
    side_pattern = [0, 0, 1, 0, 1]
    side = [0] * n
    for i, cls in enumerate(classes):
        for v in cls:
            side[v] = side_pattern[i]
    bad = {e for e in edges if side[e[0]] == side[e[1]]}
    blue = edges - bad
    return Fixture(
        name=f"adversarial_deleted_matching_t{t}",
        scope="generic stability guardrail",
        n=n,
        blue=blue,
        bad=bad,
        side=side,
        nominal_t=t,
        source="constructed in audit_extraction.py",
        metadata={"deletedMatching": sorted(deleted)},
    )


def adversarial_glued_block(k: int = 5) -> Fixture:
    n1, c1, e1 = c5_blowup([k] * 5)
    # Glue vertex 0 of C5[1] to vertex 0 of the large block.
    new = [0, n1, n1 + 1, n1 + 2, n1 + 3]
    e2 = {edge(new[i], new[(i + 1) % 5]) for i in range(5)}
    n = n1 + 4
    edges = e1 | e2
    side = [0] * n
    pattern = [0, 0, 1, 0, 1]
    for i, cls in enumerate(c1):
        for v in cls:
            side[v] = pattern[i]
    for i, v in enumerate(new):
        side[v] = pattern[i]
    bad = {e for e in edges if side[e[0]] == side[e[1]]}
    return Fixture(
        name=f"adversarial_glued_c5_k{k}",
        scope="generic stability guardrail",
        n=n,
        blue=edges - bad,
        bad=bad,
        side=side,
        source="constructed in audit_extraction.py",
    )


def neutral_transport_countermodel() -> dict[str, Any]:
    states = []
    for i in range(2):
        obligations = [f"u{i}", f"v{i}"]
        key = f"p{i}"
        realized = {o: [key] for o in obligations}
        matching = {obligations[0]: key}
        states.append(
            {
                "obligations": obligations,
                "realized": realized,
                "maximum_matching": matching,
                "rank": 1,
                "defect": 1,
            }
        )
    ledgers = []
    for i in range(2):
        old, new = states[i], states[1 - i]
        carry = set(old["maximum_matching"]) & set(new["obligations"])
        born = len(set(new["obligations"]) - set(old["obligations"]))
        dead_unmatched = len(
            (set(old["obligations"]) - set(new["obligations"]))
            - set(old["maximum_matching"])
        )
        broken_live = len(set(old["maximum_matching"]) & set(new["obligations"]) - carry)
        reoptimized = new["rank"] - len(carry)
        delta = born + broken_live - dead_unmatched - reoptimized
        if (born, dead_unmatched, broken_live, reoptimized, delta) != (2, 1, 0, 1, 0):
            raise AssertionError("neutral ledger arithmetic")
        ledgers.append(
            {
                "B": born,
                "U": dead_unmatched,
                "L": broken_live,
                "A_reopt": reoptimized,
                "defect_delta": delta,
            }
        )
    return {
        "scope": "transport-only; no graph/row/profile fields",
        "states": states,
        "ledgers": ledgers,
        "balanced": all(x["B"] + x["L"] == x["U"] + x["A_reopt"] for x in ledgers),
    }


def audit_fixture(f: Fixture, include_core: bool = True) -> dict[str, Any]:
    result = {
        "name": f.name,
        "scope": f.scope,
        "source": f.source,
        "source_sha256": sha256(ROOT / f.source) if f.source and (ROOT / f.source).is_file() else None,
        "metadata": f.metadata,
        "counts": {
            "n": f.n,
            "blue": len(f.blue),
            "bad": len(f.bad),
            "edges": len(f.edges),
            "support": len(f.support),
            "atoms": len(f.atoms),
        },
        "m3_graph_fields": graph_field_audit(f),
        "maximum_cut": minimum_switch_sigma(f),
        "c5_homomorphism": c5_homomorphism(f),
    }
    if include_core:
        result["aligned_complete_c5_core"] = aligned_core(f)
    else:
        result["aligned_complete_c5_core"] = {
            "skipped": True,
            "reason": "fixture is not at an M3 window and has more than 100 vertices",
        }
    hom = result["c5_homomorphism"]["sat"]
    core = result["aligned_complete_c5_core"]
    result["extraction_conclusion"] = {
        "c5_hom": hom,
        "aligned_K_le_3": bool(core.get("K_le_3", False)),
        "holds": hom or bool(core.get("K_le_3", False)),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="skip the two largest p5 cages")
    args = parser.parse_args()

    real = load_p5_cages()
    real.extend([load_r41(), load_r40_n78()])
    support_hits = load_t5_support_hits()
    adversarial = [adversarial_deleted_matching(), adversarial_glued_block()]

    if args.quick:
        real = [f for f in real if f.n <= 400]

    results = []
    for f in real + support_hits + adversarial:
        results.append(audit_fixture(f, include_core=f.n <= 100))

    payload = {
        "schema": "wave4-rotor-c5-core-audit-v1",
        "script_sha256": sha256(Path(__file__)),
        "solvers": {"homomorphism": "PySAT cadical195", "optimization": "OR-Tools CP-SAT, one worker"},
        "fixtures": results,
        "neutral_transport_countermodel": neutral_transport_countermodel(),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "fixture_count": len(results),
        "support_hit_count": len(support_hits),
        "output_sha256": sha256(OUT),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
