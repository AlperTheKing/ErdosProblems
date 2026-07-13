"""Rotor-edge existence census: single-atom row transitions between the two
owners' zero-vector profile states (exact joint CSP; complete, no sampling).

Question (matroid-exchange lens, R42 rotor edge): does there exist a pair of
full 25-row assignments (RA, RB), RA a v-profile state (active x0), RB an
m-profile state (active x0'), differing in EXACTLY ONE atom's row?

Joint constraints on the shared 24 atoms q != pivot:
  q in Inc(v): (first step at v) != x0   AND m not in row      [A-side + B-side]
  q in Inc(m): v not in row              AND (first step at m) != x0'
  q outside  : v not in row              AND m not in row
Pivot p: rA = A-side constraint w.r.t. v only; rB = B-side w.r.t. m only.
Global (A): steps of Inc(v) rows onto N(v)-x0 (all t-1 hit);
            each pair {x0,y} covered by a v-avoiding non-Inc(v) row of RA.
Global (B): mirror at m.
Search: DFS over atoms with exact pruning; every (pivot, rA, rB) exhausted.
"""

from __future__ import annotations

import json
from itertools import combinations

from fixtures import load_all, adjacency, norm
from profiles import owner_table, first_step

NODE_CAP = 2_000_000


class CapExceeded(Exception):
    pass


def joint_transition_exists(circ, v, x0, m, x0p, verbose=False):
    adj = adjacency(circ.n, circ.support)
    Yv = [y for y in adj[v] if y != x0]
    Ym = [y for y in adj[m] if y != x0p]
    inc_v = [i for i, a in enumerate(circ.atoms) if v in (a["u"], a["v"])]
    inc_m = [i for i, a in enumerate(circ.atoms) if m in (a["u"], a["v"])]
    assert not set(inc_v) & set(inc_m), "owners share an incident atom"

    def shared_candidates(q):
        a = circ.atoms[q]
        out = []
        for r in a["rows"]:
            if q in inc_v:
                if first_step(r, v) != x0 and m not in r:
                    out.append(r)
            elif q in inc_m:
                if v not in r and first_step(r, m) != x0p:
                    out.append(r)
            else:
                if v not in r and m not in r:
                    out.append(r)
        return out

    def a_side(q, rows):
        a = circ.atoms[q]
        if q in inc_v:
            return [r for r in rows if first_step(r, v) != x0]
        return [r for r in rows if v not in r]

    def b_side(q, rows):
        if q in inc_m:
            return [r for r in rows if first_step(r, m) != x0p]
        return [r for r in rows if m not in r]

    shared = {q: shared_candidates(q) for q in range(len(circ.atoms))}

    def covers(row, x, y, owner):
        return owner not in row and x in row and y in row

    stats = {"pivotRowPairsTried": 0, "feasible": [], "nodes": 0}

    for p in range(len(circ.atoms)):
        rows_p = circ.atoms[p]["rows"]
        ra_list = a_side(p, rows_p)
        rb_list = b_side(p, rows_p)
        for ra in ra_list:
            for rb in rb_list:
                if ra == rb:
                    continue
                stats["pivotRowPairsTried"] += 1
                # quick necessary condition: every non-pivot atom must have a
                # shared candidate
                if any(not shared[q] for q in range(len(circ.atoms)) if q != p):
                    continue
                if solve(circ, v, x0, m, x0p, Yv, Ym, inc_v, inc_m,
                         shared, p, ra, rb, covers, stats):
                    stats["feasible"].append({
                        "pivot": p,
                        "atom": [circ.atoms[p]["u"], circ.atoms[p]["v"]],
                        "rowA": list(ra), "rowB": list(rb)})
                    if len(stats["feasible"]) >= 4:
                        return stats
    return stats


def solve(circ, v, x0, m, x0p, Yv, Ym, inc_v, inc_m, shared, p, ra, rb,
          covers, stats):
    """DFS: assign shared rows; check both profiles."""
    n = len(circ.atoms)
    order = ([q for q in inc_v if q != p] + [q for q in inc_m if q != p]
             + [q for q in range(n) if q not in inc_v and q not in inc_m
                and q != p])
    # steps + coverage state trackers
    need_steps_v = set(Yv)
    need_steps_m = set(Ym)
    need_cov_v = set(Yv)
    need_cov_m = set(Ym)
    # pivot contributions
    if p in inc_v:
        need_steps_v.discard(first_step(ra, v))
    else:
        for y in list(need_cov_v):
            if covers(ra, x0, y, v):
                need_cov_v.discard(y)
    if p in inc_m:
        need_steps_m.discard(first_step(rb, m))
    else:
        for y in list(need_cov_m):
            if covers(rb, x0p, y, m):
                need_cov_m.discard(y)

    # potential suppliers per remaining condition, for pruning
    def can_supply(q, r):
        sv = set()
        sm = set()
        cv = set()
        cm = set()
        if q in inc_v:
            sv.add(first_step(r, v))
        else:
            for y in Yv:
                if covers(r, x0, y, v):
                    cv.add(y)
        if q in inc_m:
            sm.add(first_step(r, m))
        else:
            for y in Ym:
                if covers(r, x0p, y, m):
                    cm.add(y)
        return sv, sm, cv, cm

    supply = {q: [can_supply(q, r) for r in shared[q]] for q in order}
    # suffix potentials (depend only on position)
    L = len(order)
    suffix = [(set(), set(), set(), set()) for _ in range(L + 1)]
    for idx in range(L - 1, -1, -1):
        q = order[idx]
        sv = set().union(*(s[0] for s in supply[q])) if supply[q] else set()
        sm = set().union(*(s[1] for s in supply[q])) if supply[q] else set()
        cv = set().union(*(s[2] for s in supply[q])) if supply[q] else set()
        cm = set().union(*(s[3] for s in supply[q])) if supply[q] else set()
        nxt = suffix[idx + 1]
        suffix[idx] = (sv | nxt[0], sm | nxt[1], cv | nxt[2], cm | nxt[3])

    def dfs(idx, nsv, nsm, ncv, ncm):
        stats["nodes"] += 1
        if stats["nodes"] > NODE_CAP:
            raise CapExceeded
        if not (nsv or nsm or ncv or ncm):
            # all remaining atoms just need any shared candidate (nonempty
            # checked upfront)
            return True
        if idx == len(order):
            return False
        rest_sv, rest_sm, rest_cv, rest_cm = suffix[idx]
        if (nsv - rest_sv) or (nsm - rest_sm) or (ncv - rest_cv) or (ncm - rest_cm):
            return False
        q = order[idx]
        for k, r in enumerate(shared[q]):
            sv, sm, cv, cm = supply[q][k]
            if dfs(idx + 1, nsv - sv, nsm - sm, ncv - cv, ncm - cm):
                return True
        return False

    try:
        return dfs(0, frozenset(need_steps_v), frozenset(need_steps_m),
                   frozenset(need_cov_v), frozenset(need_cov_m))
    except CapExceeded:
        stats.setdefault("capExceeded", []).append(p)
        return False


def single_owner_realizable(circ, v, x0):
    """Sanity: is the v-profile realizable at all (ignore m)? Same DFS with
    m-constraints stripped, pivot-free."""
    class Dummy:
        pass
    # trick: run joint with m = v? cleaner: direct.
    adj = adjacency(circ.n, circ.support)
    Yv = [y for y in adj[v] if y != x0]
    inc_v = [i for i, a in enumerate(circ.atoms) if v in (a["u"], a["v"])]
    cands = {}
    for q, a in enumerate(circ.atoms):
        if q in inc_v:
            cands[q] = [r for r in a["rows"] if first_step(r, v) != x0]
        else:
            cands[q] = [r for r in a["rows"] if v not in r]
        if not cands[q]:
            return False
    need_steps = set(Yv)
    need_cov = set(Yv)
    order = sorted(range(len(circ.atoms)),
                   key=lambda q: (q not in inc_v, len(cands[q])))

    def supply(q, r):
        s, c = set(), set()
        if q in inc_v:
            s.add(first_step(r, v))
        else:
            for y in Yv:
                if v not in r and x0 in r and y in r:
                    c.add(y)
        return s, c

    sup = {q: [supply(q, r) for r in cands[q]] for q in order}

    def dfs(idx, ns, nc):
        if not (ns or nc):
            return True
        if idx == len(order):
            return False
        rest_s = set().union(*(s[0] for q in order[idx:] for s in sup[q]))
        rest_c = set().union(*(s[1] for q in order[idx:] for s in sup[q]))
        if (ns - rest_s) or (nc - rest_c):
            return False
        q = order[idx]
        for k in range(len(cands[q])):
            s, c = sup[q][k]
            if dfs(idx + 1, ns - s, nc - c):
                return True
        return False

    return dfs(0, frozenset(need_steps), frozenset(need_cov))


def main():
    out = {}
    for name, c in load_all().items():
        if c.n == 0 or name == "r34deg":
            continue
        tab = owner_table(c)
        zeros = [(w, x) for w, actives in tab.items()
                 for x, vec in actives.items() if vec == (0, 0, 0, 0)]
        rec = {"zeroVector": zeros,
               "realizable": {f"{w}@{x}": single_owner_realizable(c, w, x)
                              for (w, x) in zeros}}
        pairs = []
        for (w1, x1) in zeros:
            for (w2, x2) in zeros:
                if w1 != w2:
                    pairs.append(((w1, x1), (w2, x2)))
        cens = {}
        for (w1, x1), (w2, x2) in pairs:
            stats = joint_transition_exists(c, w1, x1, w2, x2)
            cens[f"{w1}@{x1}->{w2}@{x2}"] = {
                "pivotRowPairsTried": stats["pivotRowPairsTried"],
                "nodes": stats["nodes"],
                "feasibleTransitions": stats["feasible"],
                "capExceeded": stats.get("capExceeded", []),
            }
        rec["transitions"] = cens
        out[name] = rec
        print(name, json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
