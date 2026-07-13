"""Exact independent incremental audit of the R29 lead candidate.

The lead module is used only as the untrusted input constructor and shortest-row
enumerator.  Scoring and every replacement delta below are independently coded.
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = HERE.parent.parent / "lead" / "r29_lead_gate.py"


def load_input():
    spec = importlib.util.spec_from_file_location("untrusted_lead_input", LEAD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod, mod.build()


def edge(a, b):
    return (a, b) if a < b else (b, a)


def canonical_bytes(d):
    obj = {"n": d["n"], "blue": [list(x) for x in sorted(d["blue"])],
           "bad": [list(x) for x in sorted(d["bad"])],
           "rows": [list(x) for x in d["rows"]]}
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 676
    lead, d = load_input()
    rows = d["rows"]
    n = d["n"]
    rowcnt = collections.Counter(x for r in rows for x in r)
    paircnt = collections.Counter((x, y) for r in rows for x in r for y in r)
    supportcnt = collections.Counter(edge(a, b) for r in rows for a, b in zip(r, r[1:]))
    selected = set(rowcnt)
    active0 = d["blue"] - set(supportcnt)
    adj0 = [set() for _ in range(n)]
    for a, b in active0:
        if a in selected and b in selected:
            adj0[a].add(b); adj0[b].add(a)

    # Independent baseline rooted-component calculation.
    comp = [-1] * n
    comps = []
    for s in sorted(selected):
        if comp[s] >= 0: continue
        cid = len(comps); q = [s]; comp[s] = cid; vs = []
        for u in q:
            vs.append(u)
            for v in adj0[u]:
                if comp[v] < 0: comp[v] = cid; q.append(v)
        comps.append(vs)
    rooted = {comp[a] for a, b in d["bad"] if a in selected and b in selected and comp[a] == comp[b]}
    active_vertices0 = {v for v in selected if comp[v] in rooted}
    assert len(rooted) == 1, rooted
    root_cid = next(iter(rooted))
    degree0 = {v: sum(comp[w] == root_cid for w in adj0[v]) for v in active_vertices0}

    def owner_collision(v, pc=paircnt):
        return 2 * sum(max(0, pc[v, y] - 1) for y in selected)

    def hit(v, degree, rc):
        return max(0, degree - max(0, n - 5 * rc))

    coll0 = {v: owner_collision(v) for v in active_vertices0}
    coll_all = {v: owner_collision(v) for v in selected}
    hit0 = {v: hit(v, degree0[v], rowcnt[v]) for v in active_vertices0}
    score0 = sum(coll0.values()) + sum(hit0.values())
    assert score0 == 30811
    positive = {v for v in active_vertices0 if coll0[v] + hit0[v] > 0}

    blue_adj = lead.adjacency(n, d["blue"])
    hist = collections.Counter()
    min_delta = None; min_count = 0; witness = None
    qminus_empty = None; diagonal_fail = None; owner_fail = None
    active_set_fail = None
    replacements = 0
    selected_set_change = None

    # Reachability in A' = A0 - deleted + added.  Search stops at a known
    # positive owner; persistence is checked separately by searching each owner.
    def reaches_core(start, deleted, added_adj, vanished, forbidden_owner=None):
        if start in vanished: return False
        seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            if u in positive and u != forbidden_owner:
                return True
            for v in adj0[u] | added_adj.get(u, set()):
                if edge(u, v) in deleted or v not in selected or v in vanished or v in seen: continue
                seen.add(v); stack.append(v)
        return False

    for family_i in range(lo, hi):
        idx = d["selectorStart"] + family_i
        P = rows[idx]
        family = lead.shortest_rows(blue_adj, *d["atoms"][idx])
        assert len(family) == 680 and P in family
        for Q in family:
            if Q == P: continue
            replacements += 1
            Ps, Qs = set(P), set(Q)
            newv = Qs - Ps
            if not newv and qminus_empty is None:
                qminus_empty = {"family": family_i, "P": P, "Q": Q}
            bad_diag = [v for v in newv if rowcnt[v] == 0]
            if bad_diag and diagonal_fail is None:
                diagonal_fail = {"family": family_i, "P": P, "Q": Q, "vertices": bad_diag}
            vanished = {v for v in Ps-Qs if rowcnt[v] == 1}
            if vanished and selected_set_change is None:
                selected_set_change = {"family":family_i,"P":list(P),"Q":list(Q),
                                       "vanished":sorted(vanished)}
            ds = collections.Counter(edge(a,b) for a,b in zip(Q,Q[1:]))
            ds.subtract(edge(a,b) for a,b in zip(P,P[1:]))
            deleted = {e for e,x in ds.items() if x > 0 and supportcnt[e] == 0}
            added = {e for e,x in ds.items() if x < 0 and supportcnt[e] == 1}
            added_adj = collections.defaultdict(set)
            for a,b in added: added_adj[a].add(b); added_adj[b].add(a)

            # Exact positive-owner persistence check for every replacement.
            for v in positive:
                if (v in vanished or v in {x for e in deleted for x in e}) and not reaches_core(v, deleted, added_adj, vanished, v):
                    owner_fail = {"family":family_i,"P":P,"Q":Q,"owner":v}
                    break
            if owner_fail: break

            touched = set(P) | set(Q) | {x for e in deleted | added for x in e}
            is_active = {v: (v not in vanished and (v in positive or reaches_core(v, deleted, added_adj, vanished))) for v in touched}
            if active_set_fail is None:
                lost = sorted(v for v in touched if v in active_vertices0 and not is_active[v])
                if lost: active_set_fail = {"family":family_i,"P":P,"Q":Q,"lost":lost}

            # Pair-count collision delta only has owners in P union Q.
            delta = 0
            for v in set(P) | set(Q):
                old = coll0.get(v, 0) if v in active_vertices0 else 0
                if is_active[v]:
                    val = coll_all.get(v, 0)
                    for y in Ps | Qs:
                        c0 = paircnt[v,y]
                        c = c0 - (v in Ps and y in Ps) + (v in Qs and y in Qs)
                        val += 2 * (max(0, c - 1) - max(0, c0 - 1))
                    delta += val - old
                else:
                    delta -= old

            # Only touched vertices can have a degree/row-count HitNeed change.
            for v in touched:
                oldh = hit0.get(v, 0) if v in active_vertices0 else 0
                if is_active[v]:
                    deg = 0
                    for w in adj0[v] | added_adj.get(v,set()):
                        if edge(v,w) in deleted or w in vanished: continue
                        wa = (w in positive or (w in touched and is_active.get(w,False)) or
                              (w not in touched and w in active_vertices0))
                        if wa: deg += 1
                    rc = rowcnt[v] - (v in Ps) + (v in Qs)
                    newh = hit(v, deg, rc)
                else: newh = 0
                delta += newh - oldh
            hist[delta] += 1
            if min_delta is None or delta < min_delta:
                min_delta, min_count = delta, 1
                witness = {"family":family_i,"P":list(P),"Q":list(Q),"delta":delta}
            elif delta == min_delta: min_count += 1
        if owner_fail: break

    result = {
      "input_sha256": hashlib.sha256(canonical_bytes(d)).hexdigest(),
      "lead_source_sha256": hashlib.sha256(LEAD.read_bytes()).hexdigest(),
      "baseline_score": score0, "replacements": replacements,
      "family_range": [lo, hi],
      "q_minus_p_empty_falsifier": qminus_empty,
      "diagonal_collision_falsifier": diagonal_fail,
      "positive_owner_persistence_falsifier": owner_fail,
      "whole_active_set_persistence_falsifier": active_set_fail,
      "selected_set_change_witness": selected_set_change,
      "minimum_delta": min_delta, "minimum_multiplicity": min_count,
      "sharp_witness": witness,
      "delta_histogram": {str(k):v for k,v in sorted(hist.items())},
    }
    raw = json.dumps(result, sort_keys=True, indent=2) + "\n"
    (HERE/("audit_result.json" if (lo,hi)==(0,676) else f"part_{lo}_{hi}.json")).write_text(raw)
    print(raw, end="")

if __name__ == "__main__": main()
