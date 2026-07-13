"""Independent exact R29 reconstruction and FullBank-class referee gate.

This file does not import any R29 fanout artifact.  It reconstructs the graph
from the archived R29 construction, enumerates every shortest selector row,
and proves the hub-shore ActiveScoped demand/reach formulas from structural
properties shared by every selector choice.

The production FullBank interfaces are then audited by type and by the
four concrete transfer patterns.  Integer/Fraction arithmetic only.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def E(u: int, v: int) -> tuple[int, int]:
    if u == v:
        raise ValueError("loop")
    return (u, v) if u < v else (v, u)


def adj(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    out = [set() for _ in range(n)]
    for u, v in edges:
        if v in out[u]:
            raise ValueError("duplicate edge")
        out[u].add(v)
        out[v].add(u)
    return out


def distances(a: list[set[int]], s: int) -> list[int]:
    d = [-1] * len(a)
    d[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in a[u]:
            if d[v] == -1:
                d[v] = d[u] + 1
                q.append(v)
    return d


def geodesics4(a: list[set[int]], s: int, t: int) -> tuple[tuple[int, ...], ...]:
    ds = distances(a, s)
    dt = distances(a, t)
    if ds[t] != 4:
        raise AssertionError((s, t, ds[t]))
    rows: list[tuple[int, ...]] = []

    def walk(path: list[int]) -> None:
        u = path[-1]
        if len(path) == 5:
            if u == t:
                rows.append(tuple(path))
            return
        for v in sorted(a[u]):
            if ds[v] == ds[u] + 1 and ds[v] + dt[v] == 4:
                walk(path + [v])

    walk([s])
    if len(rows) != len(set(rows)):
        raise AssertionError("duplicate shortest rows")
    return tuple(rows)


@dataclass
class Cage:
    n: int
    blue: set[tuple[int, int]]
    bad: set[tuple[int, int]]
    side: tuple[int, ...]
    atoms: tuple[tuple[int, int], ...]
    rigid_rows: tuple[tuple[int, ...], ...]
    selector_atoms: tuple[tuple[int, int], ...]
    selector_displayed: tuple[tuple[int, ...], ...]
    selector_anchor: tuple[tuple[int, ...], ...]
    selector_region: tuple[int, ...]
    cable: frozenset[tuple[int, int]]
    circuit_active: frozenset[tuple[int, int]]
    circuit_offset: int
    z_l: int
    z_r: int


def add_circuit(blue: set[tuple[int, int]], bad: set[tuple[int, int]],
                side: list[int], offset: int) -> tuple[int, list[tuple[int, int]],
                                                       set[tuple[int, int]]]:
    base_blue = {E(i, (i + 1) % 26) for i in range(26)} | {E(26, 0)}
    atoms = sorted({E(i, (i + 4) % 26) for i in range(26)} |
                   {E(26, 3), E(26, 23)})
    orbit = [(9 * k) % 26 for k in range(13)]
    active = {E(orbit[k], orbit[k + 1]) for k in range(12)}
    if len(side) != offset:
        raise AssertionError("circuit offset")
    side.extend([i & 1 for i in range(26)] + [1])
    blue.update(E(offset + u, offset + v) for u, v in base_blue | active)
    bad.update(E(offset + u, offset + v) for u, v in atoms)
    nxt = offset + 27
    for u, v in atoms:
        inner = list(range(nxt, nxt + 5))
        nxt += 5
        for k in range(1, 6):
            side.append(side[offset + u] ^ (k & 1))
        path = [offset + u, *inner, offset + v]
        blue.update(E(x, y) for x, y in zip(path, path[1:]))
    return nxt, [E(offset + u, offset + v) for u, v in atoms], {
        E(offset + u, offset + v) for u, v in active
    }


def construct() -> Cage:
    r, c_l, c_r = 0, 1, 2
    left = list(range(3, 29))
    right = list(range(29, 55))
    anchor = 55
    side = [0, 1, 1] + [0] * 52 + [1]
    blue = {E(r, c_l), E(r, c_r)}
    blue |= {E(c_l, x) for x in left}
    blue |= {E(c_r, x) for x in right}
    traffic_atoms = [E(x, y) for x in left for y in right]
    bad = set(traffic_atoms)
    traffic_rows = [(x, c_l, r, c_r, y) for x in left for y in right]

    next_v = 56
    arm_regions: list[list[tuple[int, int, int]]] = []
    for leaves in (left, right):
        arms: list[tuple[int, int, int]] = []
        for leaf in leaves:
            for _ in range(26):
                x, y = next_v, next_v + 1
                next_v += 2
                side += [1, 0]
                blue |= {E(leaf, x), E(x, y), E(y, anchor)}
                arms.append((leaf, x, y))
        if len(arms) != 676:
            raise AssertionError("arm count")
        arm_regions.append(arms)
    if next_v != 2760:
        raise AssertionError(next_v)

    q_vertices = (2760, 2761)
    side += [0, 0]
    selector_atoms: list[tuple[int, int]] = []
    selector_displayed: list[tuple[int, ...]] = []
    selector_anchor: list[tuple[int, ...]] = []
    selector_region: list[int] = []
    for region, (q, arms) in enumerate(zip(q_vertices, arm_regions)):
        f_arms, d_arms = arms[:338], arms[338:]
        for j in range(338):
            _lf, x_f, _y_f = f_arms[j]
            _lfn, _x_fn, y_f_next = f_arms[(j + 1) % 338]
            _ld, x_d, _y_d = d_arms[j]
            _ldn, _x_dn, y_d_next = d_arms[(j + 1) % 338]
            path = (q, x_f, y_f_next, x_d, y_d_next)
            blue.update(E(x, y) for x, y in zip(path, path[1:]))
            atom = E(q, y_d_next)
            bad.add(atom)
            selector_atoms.append(atom)
            selector_displayed.append(tuple(reversed(path)))
            selector_anchor.append((y_d_next, anchor, y_f_next, x_f, q))
            selector_region.append(region)

    circuit_offset = 2762
    next_v, circuit_atoms, circuit_active = add_circuit(
        blue, bad, side, circuit_offset
    )
    if next_v != 2929:
        raise AssertionError(next_v)

    z_l, z_r = next_v, next_v + 1
    next_v += 2
    side += [0, 0]
    midpoint = circuit_offset + 2
    cable = frozenset({E(r, anchor), E(anchor, midpoint),
                       E(c_l, z_l), E(z_l, anchor),
                       E(c_r, z_r), E(z_r, anchor)})
    blue.update(cable)

    seed_atoms: list[tuple[int, int]] = []
    seed_rows: list[tuple[int, ...]] = []
    for seed in (anchor, z_l, z_r):
        inner = list(range(next_v, next_v + 4))
        next_v += 4
        for k in range(1, 5):
            side.append(side[seed] ^ (k & 1))
        row = (seed, *inner)
        blue.update(E(x, y) for x, y in zip(row, row[1:]))
        atom = E(seed, inner[-1])
        bad.add(atom)
        seed_atoms.append(atom)
        seed_rows.append(row)

    if next_v != 2943 or len(side) != 2943:
        raise AssertionError((next_v, len(side)))
    a_blue = adj(next_v, blue)
    circuit_rows = [geodesics4(a_blue, *atom)[0] for atom in circuit_atoms]
    rigid_rows = tuple(traffic_rows + circuit_rows + seed_rows)
    atoms = tuple(traffic_atoms + selector_atoms + circuit_atoms + seed_atoms)
    return Cage(next_v, blue, bad, tuple(side), atoms, rigid_rows,
                tuple(selector_atoms), tuple(selector_displayed),
                tuple(selector_anchor), tuple(selector_region), cable,
                frozenset(circuit_active), circuit_offset, z_l, z_r)


def selected_support(rows: tuple[tuple[int, ...], ...]) -> set[tuple[int, int]]:
    return {E(x, y) for row in rows for x, y in zip(row, row[1:])}


def pair_counts(rows: tuple[tuple[int, ...], ...]) -> Counter[tuple[int, int]]:
    counts: Counter[tuple[int, int]] = Counter()
    for row in rows:
        for x in row:
            for y in row:
                counts[x, y] += 1
    return counts


def components(vertices: set[int], edges: set[tuple[int, int]]) -> tuple[dict[int, int], list[set[int]]]:
    aa: dict[int, set[int]] = {v: set() for v in vertices}
    for u, v in edges:
        if u in aa and v in aa:
            aa[u].add(v)
            aa[v].add(u)
    lab: dict[int, int] = {}
    blocks: list[set[int]] = []
    for root in sorted(vertices):
        if root in lab:
            continue
        cid = len(blocks)
        block = {root}
        lab[root] = cid
        q = [root]
        while q:
            u = q.pop()
            for v in aa[u]:
                if v not in lab:
                    lab[v] = cid
                    block.add(v)
                    q.append(v)
        blocks.append(block)
    return lab, blocks


def scoped(cage: Cage, rows: tuple[tuple[int, ...], ...]) -> dict:
    counts = pair_counts(rows)
    U = {v for row in rows for v in row}
    support = selected_support(rows)
    active_edges = {e for e in cage.blue if e[0] in U and e[1] in U and e not in support}
    comp, blocks = components(U, active_edges)
    active_cids = {
        comp[u] for u, v in cage.bad if u in comp and v in comp and comp[u] == comp[v]
    }
    active_vertices = {v for v in U if comp[v] in active_cids}
    active_only = {e for e in active_edges if comp[e[0]] in active_cids}
    degree = Counter()
    for u, v in active_only:
        degree[u] += 1
        degree[v] += 1
    row_count = Counter(v for row in rows for v in row)
    collision = {
        v: 2 * sum(max(0, counts[v, z] - 1) for z in range(cage.n))
        for v in active_vertices
    }
    hitneed = {
        v: max(0, degree[v] - max(0, cage.n - 5 * row_count[v]))
        for v in active_vertices
    }
    return dict(counts=counts, U=U, support=support, active_edges=active_edges,
                comp=comp, blocks=blocks, active_cids=active_cids,
                active_vertices=active_vertices, active_only=active_only,
                degree=degree, row_count=row_count, collision=collision,
                hitneed=hitneed,
                score=sum(collision.values()) + sum(hitneed.values()))


def active_scoped_hub_reach(cage: Cage, state: dict) -> dict:
    hubs = {0, 1, 2}
    counts = state["counts"]
    companions = {v: {z for z in range(cage.n) if counts[v, z] > 0} for v in hubs}
    same_only = 0
    companion_only = 0
    overlap = 0
    reserved_removed = 0
    total = 0
    for x in range(cage.n):
        for y in range(cage.n):
            if x == y or counts[x, y] != 0:
                continue
            same = x in hubs
            rc = any(x in companions[v] and y in companions[v] for v in hubs)
            if not (same or rc):
                continue
            if same and rc:
                overlap += 2
            elif same:
                same_only += 2
            else:
                companion_only += 2
            total += 2
            if E(x, y) in state["active_edges"] and x in state["active_vertices"]:
                total -= 1
                reserved_removed += 1
    return dict(total=total, sameOnly= same_only, rowCompanionOnly=companion_only,
                overlap=overlap, reservedRemoved=reserved_removed,
                companions={str(v): sorted(companions[v]) for v in hubs})


def active_scoped_hub_source_set(cage: Cage, state: dict) -> set[tuple[int, int, int]]:
    hubs = {0, 1, 2}
    counts = state["counts"]
    companions = {v: {z for z in range(cage.n) if counts[v, z] > 0} for v in hubs}
    out: set[tuple[int, int, int]] = set()
    for x in range(cage.n):
        for y in range(cage.n):
            if x == y or counts[x, y] != 0:
                continue
            if not (x in hubs or any(x in companions[v] and y in companions[v] for v in hubs)):
                continue
            out.add((x, y, 1))
            if not (E(x, y) in state["active_edges"] and x in state["active_vertices"]):
                out.add((x, y, 0))
    return out


def checked_c5base_hub_sources(cage: Cage, state: dict) -> dict:
    """Replay `CheckedC5BaseTransfer.TerminalData.Valid` on hub owners.

    The matching layer additionally requires a permanently Free ordered-pair
    half.  We count unique half keys and remove overlap with the auxiliary
    ActiveScoped neighborhood.
    """
    counts = state["counts"]
    aB = adj(cage.n, cage.blue)
    aM = adj(cage.n, cage.bad)
    legacy = active_scoped_hub_source_set(cage, state)
    union: set[tuple[int, int, int]] = set()
    owner_sources: dict[int, set[tuple[int, int, int]]] = {}
    owner_terms: dict[int, list[tuple[int, int, int, int, int]]] = {}
    for owner in (0, 1, 2):
        sources: set[tuple[int, int, int]] = set()
        terms: list[tuple[int, int, int, int, int]] = []
        for x in sorted(aB[owner]):
            for y in sorted(aB[owner]):
                if x == y or counts[x, y] != 0:
                    continue
                dB = len(aB[x]) + len(aB[y]) - (2 if y in aB[x] else 0)
                dM = len(aM[x]) + len(aM[y]) - (2 if y in aM[x] else 0)
                if dM + 2 <= dB:
                    terms.append((x, y, dB, dM, dB - dM - 2))
                    sources.add((x, y, 0))
                    sources.add((x, y, 1))
        owner_sources[owner] = sources
        owner_terms[owner] = terms
        union |= sources
    new = union - legacy
    overlap = union & legacy
    return {
        "validOrderedTerminalsByOwner": {str(o): len(owner_terms[o]) for o in owner_terms},
        "halfKeysByOwner": {str(o): len(owner_sources[o]) for o in owner_sources},
        "uniqueHalfKeys": len(union),
        "overlapWithActiveScoped": len(overlap),
        "newHalfKeys": len(new),
        "newHalfKeysByEligibleOwner": {
            str(o): len(owner_sources[o] - legacy) for o in owner_sources
        },
        "adjustedSurplusRangeByOwner": {
            str(o): [min(t[4] for t in owner_terms[o]), max(t[4] for t in owner_terms[o])]
            for o in owner_terms
        },
        "newKeySHA256": hashlib.sha256(json.dumps(sorted(new), separators=(",", ":")).encode()).hexdigest(),
        "sampleNewKeys": [list(k) for k in sorted(new)[:12]],
    }


def construct_extended_owner_matching(cage: Cage, state: dict) -> dict:
    """Construct a full owner-level injection using ActiveScoped plus checked C5-base.

    Every demand with one owner has the same owner-only eligibility predicate,
    so an injection of owner-indexed demand copies is an injection of the
    actual CollisionHalf/HitNeed sum type after choosing any fixed enumeration.
    """
    counts = state["counts"]
    aB = adj(cage.n, cage.blue)
    aM = adj(cage.n, cage.bad)
    demands = {v: state["collision"].get(v, 0) + state["hitneed"].get(v, 0)
               for v in sorted(state["active_vertices"])}
    demands = {v: d for v, d in demands.items() if d}
    used: set[tuple[int, int, int]] = set()
    assigned: dict[int, list[tuple[tuple[int, int, int], str]]] = {v: [] for v in demands}

    def free(key: tuple[int, int, int]) -> bool:
        x, y, _h = key
        return x != y and counts[x, y] == 0

    def reserved(key: tuple[int, int, int]) -> bool:
        x, y, h = key
        return h == 0 and E(x, y) in state["active_edges"] and x in state["active_vertices"]

    def boundary_surplus(x: int, y: int) -> int:
        dB = len(aB[x]) + len(aB[y]) - (2 if y in aB[x] else 0)
        dM = len(aM[x]) + len(aM[y]) - (2 if y in aM[x] else 0)
        return dB - dM

    def add(owner: int, key: tuple[int, int, int], relation: str) -> bool:
        if key in used or not free(key) or reserved(key):
            return False
        x, y, _ = key
        if relation == "sameFirst":
            assert x == owner
        elif relation == "rowCompanion":
            assert counts[owner, x] > 0 and counts[owner, y] > 0
            assert boundary_surplus(x, y) >= 0
        elif relation == "checkedC5Base":
            assert x in aB[owner] and y in aB[owner]
            assert boundary_surplus(x, y) >= 2
            assert E(x, y) not in cage.blue  # triangle-free common-blue pair
        else:
            raise AssertionError(relation)
        used.add(key)
        assigned[owner].append((key, relation))
        return True

    # First exhaust owner-private same-first keys.  Distinct first coordinates
    # make these pools disjoint across owners.
    for owner, demand in demands.items():
        for y in range(cage.n):
            for h in (0, 1):
                if len(assigned[owner]) >= demand:
                    break
                add(owner, (owner, y, h), "sameFirst")
            if len(assigned[owner]) >= demand:
                break

    # The three hubs are the only owners not already easily covered.  Add all
    # genuinely new checked common-blue keys before consuming the shared
    # left-left/right-right row-companion pool.
    hubs = (0, 1, 2)
    legacy = active_scoped_hub_source_set(cage, state)
    for owner in hubs:
        for x in sorted(aB[owner]):
            for y in sorted(aB[owner]):
                for h in (0, 1):
                    key = (x, y, h)
                    if key in legacy:
                        continue
                    if len(assigned[owner]) < demands[owner]:
                        add(owner, key, "checkedC5Base")

    hub_companions = sorted({z for z in range(cage.n) if counts[0, z] > 0})
    shared_row_keys = []
    for x in hub_companions:
        for y in hub_companions:
            for h in (0, 1):
                key = (x, y, h)
                if free(key) and not reserved(key):
                    shared_row_keys.append(key)
    for owner in hubs:
        for key in shared_row_keys:
            if len(assigned[owner]) >= demands[owner]:
                break
            add(owner, key, "rowCompanion")

    # Anchor 55 needs 892 row-companion keys beyond its owner-private pool.
    # Generate only as many as needed; exact validity is checked by add().
    anchor = 55
    if len(assigned[anchor]) < demands[anchor]:
        companions = sorted(z for z in range(cage.n) if counts[anchor, z] > 0)
        for x in companions:
            if len(assigned[anchor]) >= demands[anchor]:
                break
            for y in companions:
                if len(assigned[anchor]) >= demands[anchor]:
                    break
                for h in (0, 1):
                    if len(assigned[anchor]) >= demands[anchor]:
                        break
                    add(anchor, (x, y, h), "rowCompanion")

    if any(len(assigned[v]) != demands[v] for v in demands):
        raise AssertionError({v: (len(assigned[v]), demands[v]) for v in demands})
    if len(used) != sum(demands.values()):
        raise AssertionError("matching not injective")
    breakdown = {
        str(v): dict(Counter(relation for _key, relation in assigned[v]))
        for v in assigned
    }
    serial = [
        [owner, i, *key, relation]
        for owner in sorted(assigned)
        for i, (key, relation) in enumerate(assigned[owner])
    ]
    cert_payload = {
        "schema": "r29-owner-source-injection-v1",
        "allAnchor": True,
        "assignments": serial,
    }
    cert_raw = json.dumps(cert_payload, sort_keys=True, separators=(",", ":")).encode()
    cert_path = HERE / "r29_extended_owner_matching.json"
    cert_path.write_bytes(cert_raw + b"\n")
    return {
        "demand": sum(demands.values()),
        "assignedDistinctSources": len(used),
        "perOwnerDemand": {str(v): demands[v] for v in demands},
        "perOwnerRelationBreakdown": breakdown,
        "assignmentSHA256": hashlib.sha256(cert_raw).hexdigest(),
        "assignmentFile": str(cert_path.relative_to(ROOT)) if 'ROOT' in globals() else cert_path.name,
    }


def hub_demand(cage: Cage, state: dict) -> dict:
    per = {}
    for v in (0, 1, 2):
        per[v] = state["collision"].get(v, 0) + state["hitneed"].get(v, 0)
    return {"perOwner": {str(k): v for k, v in per.items()}, "total": sum(per.values()),
            "collision": sum(state["collision"].get(v, 0) for v in per),
            "hitNeed": sum(state["hitneed"].get(v, 0) for v in per)}


def outside_components(cage: Cage, U: set[int]) -> tuple[dict[int, int], list[set[int]], list[set[int]]]:
    outside = set(range(cage.n)) - U
    internal = {e for e in cage.blue if e[0] in outside and e[1] in outside}
    labels, blocks = components(outside, internal)
    atts: list[set[int]] = [set() for _ in blocks]
    for u, v in cage.blue:
        if u in outside and v in U:
            atts[labels[u]].add(v)
        elif v in outside and u in U:
            atts[labels[v]].add(u)
    return labels, blocks, atts


def outside_attachment_hub_sources(cage: Cage, state: dict) -> dict:
    labels, blocks, atts = outside_components(cage, state["U"])
    counts = state["counts"]
    hub_comp = state["comp"][0]
    qualifying: dict[int, set[int]] = {}
    for owner in (0, 1, 2):
        good_components = {
            cid for cid, att in enumerate(atts)
            if any(counts[owner, a] > 0 and a in state["comp"] and
                   state["comp"][a] == hub_comp for a in att)
        }
        qualifying[owner] = {x for cid in good_components for x in blocks[cid]}
    sources = set()
    for owner, xs in qualifying.items():
        for x in xs:
            for y in xs:
                if x != y and counts[x, y] == 0:
                    sources.add((x, y, 0))
                    sources.add((x, y, 1))
    return {
        "outsideVertices": sum(len(b) for b in blocks),
        "outsideComponents": len(blocks),
        "qualifyingVerticesPerOwner": {str(k): len(v) for k, v in qualifying.items()},
        "distinctFreeHalfSources": len(sources),
    }


def component_block_diagnostic(cage: Cage, state: dict) -> dict:
    """Compiled block-constructor diagnostic for C=selected vertices, F=support.

    This is not claimed to be the missing real provider.  It computes the
    graph-derived quantities that the existing constructor would consume.
    """
    U = state["U"]
    O = cage.blue - state["support"]
    D = {e for e in O if (e[0] in U) ^ (e[1] in U)}

    def owner(v: int):
        if v not in U:
            return ("outside", v)
        cid = state["comp"][v]
        if cid in state["active_cids"]:
            return ("vertex", v)
        return ("component", cid)

    positive_internal = []
    zero_internal = []
    for e in O - D:
        u, v = e
        if u in U and v in U:
            (positive_internal if owner(u) != owner(v) else zero_internal).append(e)
    hub_internal = [e for e in positive_internal if e[0] in {0,1,2} or e[1] in {0,1,2}]
    total_load = Fraction(len(D), 2) + len(positive_internal)
    return {
        "Ccard": len(U), "offSupportBlue": len(O), "doorBoundaryEdges": len(D),
        "positiveInternalBlockEdges": len(positive_internal),
        "zeroInternalBlockEdges": len(zero_internal),
        "hubPositiveInternalEdges": [list(e) for e in sorted(hub_internal)],
        "totalBlockLoad": str(total_load),
    }


def canonical_hashes(cage: Cage, baseline: tuple[tuple[int, ...], ...]) -> dict[str, str]:
    graph_rows = {
        "n": cage.n,
        "blue": [list(e) for e in sorted(cage.blue)],
        "bad": [list(e) for e in sorted(cage.bad)],
        "rows": [list(row) for row in baseline],
    }
    payload = {
        "n": cage.n,
        "blue": sorted(cage.blue),
        "bad": sorted(cage.bad),
        "side": cage.side,
        "rows": baseline,
        "selector_anchor_rows": cage.selector_anchor,
        "selector_start": 676,
    }
    graph_raw = json.dumps(graph_rows, sort_keys=True, separators=(",", ":")).encode()
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=list).encode()
    return {
        "graphAndBaselineRows": hashlib.sha256(graph_raw).hexdigest(),
        "extendedRefereePayload": hashlib.sha256(raw).hexdigest(),
    }


def maxcut_partition_certificate(cage: Cage) -> dict:
    """Exact five-class upper bound and attaining-cut certificate."""
    graph = cage.blue | cage.bad
    selector_cycles = [set(selected_support((row,))) | {atom}
                       for row, atom in zip(cage.selector_displayed, cage.selector_atoms)]
    selector_edges = set().union(*selector_cycles)
    if any(len(cyc) != 5 for cyc in selector_cycles):
        raise AssertionError("selector cycle size")
    if sum(map(len, selector_cycles)) != len(selector_edges):
        raise AssertionError("selector cycles not edge-disjoint")

    circuit_vertices = set(range(cage.circuit_offset, cage.circuit_offset + 167))
    circuit_edges = {e for e in graph if e[0] in circuit_vertices and e[1] in circuit_vertices}
    seed_rows = cage.rigid_rows[-3:]
    seed_atoms = cage.atoms[-3:]
    seed_cycles = [set(selected_support((row,))) | {atom}
                   for row, atom in zip(seed_rows, seed_atoms)]
    seed_edges = set().union(*seed_cycles)
    if any(len(cyc) != 5 for cyc in seed_cycles) or sum(map(len, seed_cycles)) != len(seed_edges):
        raise AssertionError("seed cycles")
    cable_edges = set(cage.cable)
    locked_edges = graph - selector_edges - circuit_edges - seed_edges - cable_edges
    classes = [locked_edges, selector_edges, seed_edges, circuit_edges, cable_edges]
    if set().union(*classes) != graph:
        raise AssertionError("class cover")
    if sum(len(x) for x in classes) != len(graph):
        raise AssertionError("class overlap")
    if [len(x) for x in classes] != [4786, 3380, 15, 235, 6]:
        raise AssertionError([len(x) for x in classes])

    # Locked double-star quotient: choose four core colors and only the counts
    # of color-one leaves on each shore.  Every 3-edge arm is optimized
    # independently, giving 3 cuts if its endpoints differ and 2 otherwise.
    t = 26
    locked_best = -1
    locked_achievers = 0
    for bits in range(16):
        r = (bits >> 0) & 1
        cl = (bits >> 1) & 1
        cr = (bits >> 2) & 1
        anchor = (bits >> 3) & 1
        for nl in range(t + 1):
            for nr in range(t + 1):
                cut = int(r != cl) + int(r != cr)
                cut += nl * int(1 != cl) + (t - nl) * int(0 != cl)
                cut += nr * int(1 != cr) + (t - nr) * int(0 != cr)
                cut += nl * (t - nr) + (t - nl) * nr
                opposite = (nl if anchor == 0 else t - nl) + (nr if anchor == 0 else t - nr)
                cut += t * (3 * opposite + 2 * (2 * t - opposite))
                if cut > locked_best:
                    locked_best, locked_achievers = cut, 1
                elif cut == locked_best:
                    locked_achievers += 1
    if locked_best != 4110:
        raise AssertionError(locked_best)

    # The 28 private circuit 7-cycles are edge-disjoint.  They force at least
    # 28 monochromatic edges in every cut of the 235-edge circuit class.
    local_atoms = sorted({E(i, (i + 4) % 26) for i in range(26)} |
                         {E(26, 3), E(26, 23)})
    circuit_private_cycles = []
    nxt = cage.circuit_offset + 27
    for u, v in local_atoms:
        inner = list(range(nxt, nxt + 5))
        nxt += 5
        path = [cage.circuit_offset + u, *inner, cage.circuit_offset + v]
        atom = E(cage.circuit_offset + u, cage.circuit_offset + v)
        circuit_private_cycles.append({E(x, y) for x, y in zip(path, path[1:])} | {atom})
    if any(len(cyc) != 7 for cyc in circuit_private_cycles):
        raise AssertionError("circuit cycle size")
    if sum(map(len, circuit_private_cycles)) != len(set().union(*circuit_private_cycles)):
        raise AssertionError("circuit private cycles overlap")

    upper = [locked_best, 4 * 676, 4 * 3, 235 - 28, 6]
    attained = [len(cage.blue & cls) for cls in classes]
    if upper != [4110, 2704, 12, 207, 6] or attained != upper:
        raise AssertionError((upper, attained))
    return {
        "classOrder": ["lockedDoubleStar", "selectorC5", "seedC5", "circuit", "cable"],
        "classEdgeCounts": [len(x) for x in classes],
        "upperBounds": upper,
        "attainedBlueCounts": attained,
        "maxCut": sum(upper),
        "lockedQuotientCases": 16 * 27 * 27,
        "lockedQuotientAchievers": locked_achievers,
        "selectorEdgeDisjointOddCycles": 676,
        "seedEdgeDisjointOddCycles": 3,
        "circuitEdgeDisjointPrivateOddCycles": 28,
    }


def main() -> None:
    cage = construct()
    all_edges = cage.blue | cage.bad
    if not cage.blue.isdisjoint(cage.bad):
        raise AssertionError("edge color overlap")
    if (cage.n, len(cage.blue), len(cage.bad), len(all_edges)) != (2943, 7039, 1383, 8422):
        raise AssertionError("counts")
    if not all(cage.side[u] != cage.side[v] for u, v in cage.blue):
        raise AssertionError("blue is not the cut")
    if not all(cage.side[u] == cage.side[v] for u, v in cage.bad):
        raise AssertionError("bad is not monochromatic")
    maxcut_cert = maxcut_partition_certificate(cage)
    if maxcut_cert["maxCut"] != len(cage.blue):
        raise AssertionError(maxcut_cert)
    aa = adj(cage.n, all_edges)
    triangles = [(u, v) for u, v in all_edges if aa[u] & aa[v]]
    if triangles:
        raise AssertionError(("triangle", triangles[0]))
    ab = adj(cage.n, cage.blue)
    if len({i for i, d in enumerate(distances(ab, 0)) if d >= 0}) != cage.n:
        raise AssertionError("B disconnected")

    selector_families: list[tuple[tuple[int, ...], ...]] = []
    row_hist = Counter()
    for atom in cage.atoms:
        fam = geodesics4(ab, *atom)
        row_hist[len(fam)] += 1
    for atom in cage.selector_atoms:
        selector_families.append(geodesics4(ab, *atom))
    if row_hist != Counter({1: 707, 680: 676}):
        raise AssertionError(row_hist)
    if sum(k * v for k, v in row_hist.items()) != 460387:
        raise AssertionError("row total")
    if any(len([r for r in fam if 55 in r]) != 676 or
           len([r for r in fam if 55 not in r]) != 4
           for fam in selector_families):
        raise AssertionError("selector split")
    if any(any(v <= 54 for v in row) for fam in selector_families for row in fam):
        raise AssertionError("selector row hits hub-companion core")
    if any(any(e in cage.cable for e in selected_support((row,)))
           for fam in selector_families for row in fam):
        raise AssertionError("selector row uses cable")
    if any(selected_support((row,)) & (set(cage.cable) | set(cage.circuit_active))
           for fam in selector_families for row in fam):
        raise AssertionError("selector row consumes fixed active witness")
    if any(anchor not in fam for anchor, fam in zip(cage.selector_anchor, selector_families)):
        raise AssertionError("advertised anchor absent")
    commonblue_vertex_pool = set(range(55)) | {55, cage.z_l, cage.z_r}
    if any(len(set(row) & commonblue_vertex_pool) > 1
           for fam in selector_families for row in fam):
        raise AssertionError("selector can change common-blue source freeness")

    baseline = cage.rigid_rows[:676] + cage.selector_displayed + cage.rigid_rows[676:]
    all_anchor = cage.rigid_rows[:676] + cage.selector_anchor + cage.rigid_rows[676:]
    baseline_state = scoped(cage, baseline)
    anchor_state = scoped(cage, all_anchor)
    if anchor_state["score"] != 23115:
        raise AssertionError(anchor_state["score"])

    # Selector-independent active witness: cable plus fixed circuit active path.
    rigid_selected = {v for row in cage.rigid_rows for v in row}
    invariant_active = set(cage.cable) | set(cage.circuit_active)
    if any(u not in rigid_selected or v not in rigid_selected for u, v in invariant_active):
        raise AssertionError("active witness endpoint not rigid-selected")
    rigid_support = selected_support(cage.rigid_rows)
    if invariant_active & rigid_support:
        raise AssertionError("active witness consumed by rigid support")
    inv_comp, inv_blocks = components(rigid_selected, invariant_active)
    hub_cid = inv_comp[0]
    if not all(inv_comp[h] == hub_cid for h in (0, 1, 2)):
        raise AssertionError("hubs not joined by fixed active witness")
    witness_atoms = [e for e in cage.bad if e[0] in inv_comp and e[1] in inv_comp and
                     inv_comp[e[0]] == hub_cid == inv_comp[e[1]]]
    if not witness_atoms:
        raise AssertionError("no fixed bad atom activates hub component")

    demand = hub_demand(cage, anchor_state)
    reach = active_scoped_hub_reach(cage, anchor_state)
    if demand != {"perOwner": {"0": 6651, "1": 6651, "2": 6651},
                  "total": 19953, "collision": 19950, "hitNeed": 3}:
        raise AssertionError(demand)
    if reach["total"] != 19925 or reach["reservedRemoved"] != 3:
        raise AssertionError(reach)
    if reach["sameOnly"] != 17328 or reach["rowCompanionOnly"] != 2600 or reach["overlap"] != 0:
        raise AssertionError(reach)

    # The theorem-level invariant uses universal row facts, not sampling.
    hub_companions = set(range(55))
    if any(set(reach["companions"][str(h)]) != hub_companions for h in (0, 1, 2)):
        raise AssertionError("hub companion sets")
    hub_incident = {e for e in cage.blue if 0 in e or 1 in e or 2 in e}
    expected_active_hub = {E(0, 55), E(1, cage.z_l), E(2, cage.z_r)}
    traffic_support = selected_support(cage.rigid_rows[:676])
    if hub_incident - traffic_support != expected_active_hub:
        raise AssertionError((hub_incident - traffic_support, expected_active_hub))

    # Concrete transfer-pattern audit on the all-anchor minimizer.
    bad_neighbors = {h: {v for e in cage.bad if h in e for v in e if v != h}
                     for h in (0, 1, 2)}
    if any(bad_neighbors.values()):
        raise AssertionError("commonBad unexpectedly available")
    outside = outside_attachment_hub_sources(cage, anchor_state)
    if outside["distinctFreeHalfSources"] != 0:
        raise AssertionError(outside)
    four_pattern_reach = reach["total"]  # commonBad=0, outsideAttachment=0.
    if demand["total"] - four_pattern_reach != 28:
        raise AssertionError("four-pattern defect")
    checked_c5base = checked_c5base_hub_sources(cage, anchor_state)
    if checked_c5base["newHalfKeys"] != 216:
        raise AssertionError(checked_c5base)
    checked_c5base_reach = four_pattern_reach + checked_c5base["newHalfKeys"]
    if checked_c5base_reach != 20141 or checked_c5base_reach - demand["total"] != 188:
        raise AssertionError((checked_c5base_reach, demand))
    extended_matching = construct_extended_owner_matching(cage, anchor_state)
    if extended_matching["demand"] != 23115 or extended_matching["assignedDistinctSources"] != 23115:
        raise AssertionError(extended_matching)

    block_diag_anchor = component_block_diagnostic(cage, anchor_state)
    block_diag_baseline = component_block_diagnostic(cage, baseline_state)

    # A concrete selector-dependence witness for pattern 4: choose the
    # lexicographically first local row in every selector family.
    lex_local_rows = tuple(min(row for row in fam if 55 not in row)
                           for fam in selector_families)
    all_lex_local = cage.rigid_rows[:676] + lex_local_rows + cage.rigid_rows[676:]
    lex_local_state = scoped(cage, all_lex_local)
    lex_local_outside = outside_attachment_hub_sources(cage, lex_local_state)
    if lex_local_outside["distinctFreeHalfSources"] != 60:
        raise AssertionError(lex_local_outside)
    if hub_demand(cage, lex_local_state) != demand:
        raise AssertionError("hub demand changed under lex-local selector witness")
    if active_scoped_hub_reach(cage, lex_local_state)["total"] != reach["total"]:
        raise AssertionError("scoped reach changed under lex-local selector witness")

    theorem_invariant = {
        "selectorRowsAvoidHubCompanionCore": True,
        "selectorRowsAvoidCable": True,
        "fixedHubCompanionSet": list(range(55)),
        "fixedActiveHubEdges": [list(e) for e in sorted(expected_active_hub)],
        "fixedActiveWitnessBadEdge": list(sorted(witness_atoms)[0]),
        "hubPairCountsSelectorIndependent": True,
        "hubActiveDegreeSelectorIndependent": True,
        "hubDemandSelectorIndependent": demand,
        "scopedReachSelectorIndependent": reach,
        "proofBasis": [
            "all 459680 selector-row alternatives avoid vertices 0..54",
            "all selector-row supports avoid the six cable edges",
            "all selector-row supports avoid the rigid circuit active path",
            "rigid traffic rows fix every pairCount involving a hub",
            "rigid traffic support consumes every non-cable blue edge incident to a hub",
            "the cable plus rigid circuit path fixes hub ActiveOwner and degree one",
        ],
    }

    production_audit = {
        "sameFirst": {"allAnchorReach": 17325, "selectorInvariantAtHubShore": True},
        "commonBad": {"allAnchorAddedReach": 0, "selectorInvariantAtHubShore": True,
                      "reason": "the three hubs have no bad neighbors"},
        "rowCompanion": {"allAnchorAddedReach": 2600, "selectorInvariantAtHubShore": True},
        "outsideAttachment": {"allAnchorAddedReach": 0,
                              "selectorInvariantAtHubShore": False,
                              "lexAllLocalAddedReach": 60,
                              "reason": "exact all-anchor versus lex-all-local witness: 0 versus 60"},
        "fourPatternTotal": four_pattern_reach,
        "fourPatternDefect": 28,
        "checkedC5BaseTransfer": {
            "leanPredicate": "blue(x,owner) and blue(y,owner) and dM([x,y])+2<=dB([x,y])",
            **checked_c5base,
            "reachAfterUnion": checked_c5base_reach,
            "hubShoreMargin": checked_c5base_reach - demand["total"],
            "absorbsKnownHubShore": True,
            "selectorInvariantAtHubShore": True,
            "fullOwnerLevelInjection": extended_matching,
        },
        "door": {
            "role": "routes boundary off-support edge blockLoad, not CollisionHalf demand",
            "allAnchorComponentBlockDiagnostic": block_diag_anchor,
            "selectorDependentDiagnostic": block_diag_anchor != block_diag_baseline,
        },
        "vertexSlack": {
            "role": "routes non-Door off-support edge endpoint load, not CollisionHalf demand",
            "hubRawSlackUnits": {str(h): max(0, cage.n - 5 * anchor_state["row_count"][h])
                                 for h in (0,1,2)},
            "hubHitNeedUnits": {str(h): anchor_state["hitneed"][h] for h in (0,1,2)},
        },
        "c5Base": {
            "role": "CheckedC5BaseTransfer supplies common-blue FreeHalf terminals; a HitNeed use emits a c5Base token",
            "newCommonBlueHalfKeys": checked_c5base["newHalfKeys"],
            "absorbsKnownHubShore": True,
        },
        "prune": {
            "status": "UNINSTANTIATED",
            "reason": "no compiled graph-derived CheckedPruneStep/CheckedTransferMatching provider exists",
        },
        "interfaceVerdict": (
            "R29 exactly falsifies the stale four-pattern relation at the hub shore, but the compiled "
            "CheckedC5BaseTransfer common-blue predicate adds 216 nonoverlapping FreeHalf keys and absorbs "
            "that shore with margin 188. Door and vertexSlack are different demand/capacity types. "
            "The complete production matching/provider is still absent, so this is not a FullBankGlobalPackage proof."
        ),
    }

    result = {
        "counts": {"n": cage.n, "blue": len(cage.blue), "bad": len(cage.bad),
                   "edges": len(all_edges), "gamma": 25 * len(cage.bad),
                   "rowHistogram": {str(k): v for k, v in sorted(row_hist.items())},
                   "totalShortestRows": 460387},
        "maxCutCertificate": maxcut_cert,
        "canonicalSHA256": canonical_hashes(cage, baseline),
        "allAnchor": {"score": anchor_state["score"], "selectedVertices": len(anchor_state["U"]),
                      "activeVertices": len(anchor_state["active_vertices"]),
                      "demand": demand, "reach": reach,
                      "outsideAttachment": outside},
        "theoremLevelInvariant": theorem_invariant,
        "productionAudit": production_audit,
        "sampleEvidenceOnly": {
            "baselineScore": baseline_state["score"],
            "lexAllLocalScore": lex_local_state["score"],
            "lexAllLocalOutsideAttachment": lex_local_outside,
            "baselineComponentBlockDiagnostic": block_diag_baseline,
            "allAnchorComponentBlockDiagnostic": block_diag_anchor,
        },
    }
    out = HERE / "r29_referee_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
