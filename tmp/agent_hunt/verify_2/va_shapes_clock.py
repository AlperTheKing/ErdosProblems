#!/usr/bin/env python3
"""VERIFY_2 script A: independent re-verification of AGENT-HOMOLOGY Claims 1 and 3.

Written from scratch (adversarial verifier). Only the CONVENTIONS were aligned with
the colleague's report so numbers are comparable:
  Claim 1: labelled connected bipartite graphs on vertex set {0..n-1} (spanning),
    e edges, marked vertex of degree exactly 1; "admitting" = exists same-class
    pair {a,b} with NO common neighbour inside the shape.  Iso classes via full
    permutation canonicalization of (edge set, marked vertex).
  Claim 3: cyclic words over {O,P,N}, L in 1..9, start values r0 in [t-4, t+4],
    consistency = every O has pre-value exactly t, total delta 0.
Independent additions (adversarial hardening):
  A1: for the shapes, ALSO classify capture pairs by incident/remote and verify the
      e=4 admitting set is EXACTLY all end-marked labelled P5 with the single
      incident end pair; verify NO remote pair exists at e<=4 and remote exists at e=5.
  A2: bipartition ambiguity check: a connected bipartite graph has exactly 2
      colourings (swap); capture-pair set is invariant (same-class relation).
  A3: clock lemma: widen start range to [t-9, t+9] and prove-by-enumeration that all
      consistent words with >=1 O have r0 in {t, t+1} anyway (range adequacy).
  A4: clock lemma conclusions checked independently: confinement, cyclic strict
      alternation, expulsion pre-value t+1, plus #O=#P (already forced).
"""
import sys
from itertools import combinations, permutations, product
from collections import defaultdict

# ---------------- Claim 1: sterile shapes ----------------

def connected_span(n, es):
    adj = defaultdict(set)
    verts = set()
    for u, w in es:
        adj[u].add(w); adj[w].add(u)
        verts |= {u, w}
    if verts != set(range(n)):
        return False
    seen = {0}
    st = [0]
    while st:
        u = st.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); st.append(w)
    return len(seen) == n

def two_colour(n, es):
    adj = defaultdict(set)
    for u, w in es:
        adj[u].add(w); adj[w].add(u)
    col = {}
    for s in range(n):
        if s in col:
            continue
        col[s] = 0
        st = [s]
        while st:
            u = st.pop()
            for w in adj[u]:
                if w not in col:
                    col[w] = 1 - col[u]
                    st.append(w)
                elif col[w] == col[u]:
                    return None
    return col

def capture_pairs(n, es, col):
    adj = defaultdict(set)
    for u, w in es:
        adj[u].add(w); adj[w].add(u)
    return [(a, b) for a, b in combinations(range(n), 2)
            if col[a] == col[b] and not (adj[a] & adj[b])]

def canon_marked(n, es, v):
    best = None
    esf = [tuple(e) for e in es]
    for p in permutations(range(n)):
        key = (tuple(sorted(tuple(sorted((p[u], p[w]))) for u, w in esf)), p[v])
        if best is None or key < best:
            best = key
    return best

def is_path_end_marked(n, es, v):
    deg = defaultdict(int)
    adj = defaultdict(set)
    for u, w in es:
        deg[u] += 1; deg[w] += 1
        adj[u].add(w); adj[w].add(u)
    ds = sorted(deg[i] for i in range(n))
    if not (ds.count(1) == 2 and all(d <= 2 for d in ds)):
        return False
    return deg[v] == 1

def run_shapes(max_e=5, require_deg1=True):
    stats = {}
    admit_classes = {}
    for e in range(1, max_e + 1):
        raw = 0
        raw_admit = 0
        classes = {}
        for n in range(2, e + 2):
            for es in combinations(list(combinations(range(n), 2)), e):
                if not connected_span(n, es):
                    continue
                col = two_colour(n, es)
                if col is None:
                    continue
                deg = defaultdict(int)
                for u, w in es:
                    deg[u] += 1; deg[w] += 1
                pairs = capture_pairs(n, es, col)
                for v in range(n):
                    if require_deg1 and deg[v] != 1:
                        continue
                    raw += 1
                    if not pairs:
                        continue
                    raw_admit += 1
                    key = canon_marked(n, es, v)
                    if key not in classes:
                        inc = tuple(p for p in pairs if v in p)
                        rem = tuple(p for p in pairs if v not in p)
                        classes[key] = (n, es, v, inc, rem)
        stats[e] = (raw, raw_admit, len(classes))
        admit_classes[e] = classes
    return stats, admit_classes

def claim1():
    print("== Claim 1: sterile shapes (deg-1 marked) ==")
    stats, classes = run_shapes(5, require_deg1=True)
    ok = True
    for e in sorted(stats):
        raw, ra, nc = stats[e]
        print(f" e={e}: raw={raw} raw_admitting={ra} classes={nc}")
    # C6a
    le3_raw = sum(stats[e][0] for e in (1, 2, 3))
    le3_adm = sum(stats[e][1] for e in (1, 2, 3))
    print(f" C6a: e<=3 raw total={le3_raw} (report: 44), admitting={le3_adm} (report: 0)")
    ok &= (le3_raw == 44 and le3_adm == 0)
    # C6b
    raw4, adm4, nc4 = stats[4]
    c6b_shape = True
    rem4_total = 0
    for key, (n, es, v, inc, rem) in classes[4].items():
        rem4_total += len(rem)
        if not (n == 5 and is_path_end_marked(n, es, v) and len(inc) == 1 and len(rem) == 0):
            c6b_shape = False
    print(f" C6b: e=4 raw={raw4} (report: 320) admitting={adm4} (report: 120) "
          f"classes={nc4} (report: 1) all-P5-end-marked-single-incident={c6b_shape} "
          f"remote-pairs-at-4={rem4_total} (report: 0)")
    ok &= (raw4 == 320 and adm4 == 120 and nc4 == 1 and c6b_shape and rem4_total == 0)
    # C6c
    _, _, nc5 = stats[5]
    n_rem5 = sum(1 for (n, es, v, inc, rem) in classes[5].values() if rem)
    print(f" C6c: e=5 classes={nc5} (report: 5) classes-with-remote={n_rem5} (>0 required)")
    ok &= (nc5 == 5 and n_rem5 > 0)
    # C6d unrestricted marking
    stats2, _ = run_shapes(3, require_deg1=False)
    le3_adm2 = sum(stats2[e][1] for e in (1, 2, 3))
    print(f" C6d: e<=3 admitting with UNRESTRICTED marking = {le3_adm2} (report: 0)")
    ok &= (le3_adm2 == 0)
    print(f" CLAIM1 VERDICT: {'PASS' if ok else 'FAIL'}")
    return ok

# ---------------- Claim 3: mover clock ----------------

def clock_consistent(word, r0, t):
    r = r0
    vals = [r]
    for ev in word:
        if ev == 'O':
            if r != t:
                return None
            r += 1
        elif ev == 'P':
            r -= 1
        vals.append(r)
    if r != r0:
        return None
    return vals

def claim3():
    print("== Claim 3: mover-clock lemma ==")
    ok = True
    for t in (3, 7):
        n_cons = 0
        viol = []
        starts_seen = set()
        for L in range(1, 10):
            for word in product('OPN', repeat=L):
                if word.count('O') != word.count('P'):
                    continue
                for r0 in range(t - 4, t + 5):
                    vals = clock_consistent(word, r0, t)
                    if vals is None:
                        continue
                    n_cons += 1
                    if word.count('O') == 0:
                        continue
                    starts_seen.add(r0 - t)
                    conf = all(v in (t, t + 1) for v in vals)
                    evs = [ev for ev in word if ev != 'N']
                    alt = all(evs[k] != evs[(k + 1) % len(evs)] for k in range(len(evs)))
                    pre_ok = all(vals[i] == t + 1 for i, ev in enumerate(word) if ev == 'P')
                    if not (conf and alt and pre_ok):
                        viol.append((word, r0))
        print(f" t={t}: consistent pairs={n_cons} (report: 1085) violations={len(viol)} "
              f"(report: 0); O-containing start offsets seen={sorted(starts_seen)}")
        ok &= (n_cons == 1085 and not viol)
        # A3 range adequacy: widen to +-9, verify all O-containing consistent starts
        # still land in {t, t+1}
        extra = []
        for L in range(1, 10):
            for word in product('OPN', repeat=L):
                if word.count('O') != word.count('P') or word.count('O') == 0:
                    continue
                for r0 in list(range(t - 9, t - 4)) + list(range(t + 5, t + 10)):
                    if clock_consistent(word, r0, t) is not None:
                        extra.append((word, r0))
        print(f" t={t}: consistent O-containing pairs OUTSIDE [t-4,t+4]: {len(extra)} "
              f"(0 required for range adequacy)")
        ok &= not extra
    print(f" CLAIM3 VERDICT: {'PASS' if ok else 'FAIL'}")
    return ok

if __name__ == '__main__':
    r1 = claim1()
    r3 = claim3()
    print(f"SCRIPT-A OVERALL: claim1={'PASS' if r1 else 'FAIL'} claim3={'PASS' if r3 else 'FAIL'}")
