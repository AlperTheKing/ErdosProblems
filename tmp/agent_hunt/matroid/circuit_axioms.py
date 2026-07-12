"""Exact replay of transversal-circuit axioms + matroid invariants on all fixtures.

Checks (all exact, integer only):
  1. deletion-SDRs: for every atom a, atoms-minus-a has a perfect SDR onto ALL support
     edges via footprints (sizes must be [|F*|] * n_atoms).
  2. multiplicity(e) >= 2 for all e.
  3. triangle count of blue+bad graph (graph fixtures only).
  4. VISITOR PIGEONHOLE (t-uniform circuit fact, proof = delete-one-visitor):
     for every support vertex u with deg(u) >= 1: |N_visit(u)| >= deg(u) + 1,
     where N_visit(u) = atoms whose footprint contains an edge at u.
  5. TWO-OWNER STAR HALL MARGINS: for owners (v, m), all subsets T of St(v) u St(m):
     margin h(T) = |{a : footprint(a) meets T}| - |T|; circuit forces min >= 1
     (delete-one form). Report the exact min margin and argmin.
  6. Allowed incidences: (a,e) usable in some maximum matching of the atom/edge
     bipartite footprint graph; report counts + connectivity of B.
"""

from __future__ import annotations

import json
from itertools import combinations

from fixtures import load_all, max_matching, adjacency, norm


def deletion_sdr_sizes(circ):
    edges = list(range(len(circ.support)))
    e_index = {e: i for i, e in enumerate(circ.support)}
    foot = [sorted(e_index[e] for e in a["footprint"]) for a in circ.atoms]
    sizes = []
    for excl in range(len(circ.atoms)):
        adj_map = {i: foot[i] for i in range(len(circ.atoms)) if i != excl}
        m = max_matching(list(adj_map), edges, adj_map)
        sizes.append(len(m))
    return sizes


def multiplicities(circ):
    mult = {e: 0 for e in circ.support}
    for a in circ.atoms:
        for e in a["footprint"]:
            mult[e] += 1
    return mult


def triangle_count(circ):
    if circ.n == 0:
        return None
    edges = set(circ.support)
    for a in circ.atoms:
        if a["u"] >= 0:
            edges.add(norm(a["u"], a["v"]))
    adj = [set() for _ in range(circ.n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    count = 0
    for u in range(circ.n):
        for v in adj[u]:
            if v <= u:
                continue
            count += len([w for w in adj[u] & adj[v] if w > v])
    return count


def visitors(circ):
    """N_visit[u] = set of atom indices whose footprint touches vertex u."""
    if circ.n == 0:
        return None
    vis = [set() for _ in range(circ.n)]
    for i, a in enumerate(circ.atoms):
        for (x, y) in a["footprint"]:
            vis[x].add(i)
            vis[y].add(i)
    return vis


def check_pigeonhole(circ):
    if circ.n == 0:
        return None
    deg = [0] * circ.n
    for u, v in circ.support:
        deg[u] += 1
        deg[v] += 1
    vis = visitors(circ)
    bad = []
    for u in range(circ.n):
        if deg[u] >= 1 and len(vis[u]) < deg[u] + 1:
            bad.append((u, deg[u], len(vis[u])))
    slack = min((len(vis[u]) - deg[u]) for u in range(circ.n) if deg[u] >= 1)
    return {"violations": bad, "minSlack": slack}


def star_hall_margins(circ, v, m):
    """Exact Hall margins over all subsets of the two owner stars."""
    star = [e for e in circ.support if v in e or m in e]
    meets = []
    for e in star:
        meets.append(frozenset(i for i, a in enumerate(circ.atoms)
                               if e in a["footprint"]))
    n = len(star)
    best = None
    for size in range(1, n + 1):
        for T in combinations(range(n), size):
            cover = frozenset().union(*(meets[i] for i in T))
            h = len(cover) - size
            if best is None or h < best[0]:
                best = (h, [star[i] for i in T])
    union_all = frozenset().union(*meets)
    return {"starEdges": star, "minMargin": best[0], "argmin": best[1],
            "visitorUnion": len(union_all)}


def allowed_incidences(circ):
    """(a,e) pairs usable in some maximum matching (size |F*|) of B."""
    edges = list(range(len(circ.support)))
    e_index = {e: i for i, e in enumerate(circ.support)}
    foot = [sorted(e_index[e] for e in a["footprint"]) for a in circ.atoms]
    n_atoms = len(circ.atoms)
    full = len(circ.support)
    # baseline maximum matching
    adj_map = {i: foot[i] for i in range(n_atoms)}
    base = max_matching(list(range(n_atoms)), edges, adj_map)
    assert len(base) == full, ("max matching not full", len(base))
    allowed = 0
    total = sum(len(f) for f in foot)
    per_atom = [0] * n_atoms
    for a in range(n_atoms):
        for e in foot[a]:
            # force (a,e): delete both, ask for matching of size full-1 on the rest
            adj2 = {i: [x for x in foot[i] if x != e]
                    for i in range(n_atoms) if i != a}
            m = max_matching(list(adj2), [x for x in edges if x != e], adj2)
            if len(m) == full - 1:
                allowed += 1
                per_atom[a] += 1
    # connectivity of B
    comp = {}
    def root(x):
        while comp.get(x, x) != x:
            comp[x] = comp.get(comp[x], comp[x])
            x = comp[x]
        return x
    for a in range(n_atoms):
        for e in foot[a]:
            ra, re = root(("a", a)), root(("e", e))
            if ra != re:
                comp[ra] = re
    roots = {root(("a", a)) for a in range(n_atoms)} | {root(("e", e)) for e in edges}
    return {"totalIncidences": total, "allowed": allowed,
            "perAtomAllowedMin": min(per_atom), "connectedComponentsOfB": len(roots)}


def main():
    circuits = load_all()
    results = {}
    for name, c in circuits.items():
        rec = {"atoms": len(c.atoms), "supportEdges": len(c.support)}
        sizes = deletion_sdr_sizes(c)
        rec["deletionSdrAllFull"] = (sizes == [len(c.support)] * len(c.atoms))
        rec["deletionSdrSizes"] = sorted(set(sizes))
        mult = multiplicities(c)
        rec["minMultiplicity"] = min(mult.values())
        rec["triangles"] = triangle_count(c)
        rec["pigeonhole"] = check_pigeonhole(c)
        rec["allowed"] = allowed_incidences(c)
        if name in ("hit298", "hit264", "nearcand"):
            v, m = (0, 1)
            rec["starHall_v0_m1"] = star_hall_margins(c, v, m)
        results[name] = rec
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
