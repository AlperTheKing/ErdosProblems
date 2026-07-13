"""Zero-vector local-profile classifier for every (owner, active) pair (exact).

Replicates verify_t5_local_classifier_hit.local_vector but pure python:
  vector = (eForced, iStep, dStep, dCoverage); zero-vector <=> full local profile
  realizable (R48 T5LocalOwnerProfile iff).
Owner eligibility: blue degree 5 and bad degree 5 (dB = dM = 5).
"""

from __future__ import annotations

import json

from fixtures import load_all, adjacency, max_matching, norm


def first_step(row, owner):
    if row[0] == owner:
        return row[1]
    if row[-1] == owner:
        return row[-2]
    raise AssertionError


def local_vector(circ, owner, active):
    adj = adjacency(circ.n, circ.support)
    neighbours = sorted(adj[owner])
    support = [y for y in neighbours if y != active]
    incident = [i for i, a in enumerate(circ.atoms)
                if owner in (a["u"], a["v"])]
    nonincident = [i for i in range(len(circ.atoms)) if i not in incident]
    forced = [i for i in range(len(circ.atoms))
              if all(owner in row for row in circ.atoms[i]["rows"])]
    e_forced = len(set(forced) - set(incident))

    step_inc = []
    empty = 0
    for i in incident:
        steps = {first_step(r, owner) for r in circ.atoms[i]["rows"]} & set(support)
        if not steps:
            empty += 1
        step_inc.extend((y, i) for y in steps)
    adj_map = {}
    for y, i in step_inc:
        adj_map.setdefault(("y", y), []).append(("a", i))
    m = max_matching(list(adj_map), None, adj_map)
    step_rank = len(m)

    cov_inc = []
    for y in support:
        for i in nonincident:
            if any(owner not in row and active in row and y in row
                   for row in circ.atoms[i]["rows"]):
                cov_inc.append((y, i))
    adj_map = {}
    for y, i in cov_inc:
        adj_map.setdefault(("y", y), []).append(("a", i))
    m = max_matching(list(adj_map), None, adj_map)
    cov_rank = len(m)
    t1 = len(support)
    return (e_forced, empty, t1 - step_rank, t1 - cov_rank)


def owner_table(circ):
    adj = adjacency(circ.n, circ.support)
    bad_deg = [0] * circ.n
    for a in circ.atoms:
        bad_deg[a["u"]] += 1
        bad_deg[a["v"]] += 1
    table = {}
    for w in range(circ.n):
        if len(adj[w]) == 5 and bad_deg[w] == 5:
            actives = {}
            for x in adj[w]:
                actives[x] = local_vector(circ, w, x)
            table[w] = actives
    return table


def main():
    out = {}
    for name, c in load_all().items():
        if c.n == 0 or name == "r34deg":
            continue
        tab = owner_table(c)
        rec = {}
        for w, actives in tab.items():
            rec[str(w)] = {str(x): list(v) for x, v in sorted(actives.items())}
        zero = [(w, x) for w, actives in tab.items()
                for x, v in actives.items() if v == (0, 0, 0, 0)]
        out[name] = {"eligibleOwners": sorted(tab), "classifiers": rec,
                     "zeroVector": sorted(zero)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
