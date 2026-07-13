"""ADVERSARIAL VERIFIER (verify_0) for the matroid-lens report.

Everything reimplemented from scratch (graph6, shortest rows, matching,
classifier, census, fibers). Pure python, exact integers. Sources of truth:
  - engine artifacts tmp/fanout/r42_graph_specific_exclusion/*.json (hits),
  - R46 sec.8 text (near-candidate construction),
  - R48 T5LocalOwnerProfile definition (classifier),
  - R42 (18)-(22) single-row rotor transition semantics.
Does NOT import anything from tmp/agent_hunt/matroid/.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from itertools import combinations
from pathlib import Path

WS = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")
OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\verify_0")

FAILURES = []


def check(label, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    if not cond:
        FAILURES.append((label, detail))
    print(f"[{tag}] {label}" + (f" | {detail}" if detail else ""))
    return cond


def norm(u, v):
    return (u, v) if u < v else (v, u)


# ------------------------------------------------------------ graph6 (mine)
def g6(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for b in data[1:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    edges, idx = [], 0
    for v in range(1, n):
        for u in range(v):
            if bits[idx]:
                edges.append((u, v))
            idx += 1
    return n, sorted(edges)


# ------------------------------------------------------------ graph utils
def make_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return [sorted(x) for x in adj]


def bfs(adj, s):
    d = [-1] * len(adj)
    d[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    return d


def rows4(adj, u, v):
    """All shortest u->v paths of length exactly 4 (list of 5-tuples)."""
    d = bfs(adj, u)
    assert d[v] == 4, (u, v, d[v])
    out = []
    stack = [(u,)]
    while stack:
        p = stack.pop()
        last = p[-1]
        if len(p) == 5:
            if last == v:
                out.append(p)
            continue
        for w in adj[last]:
            if d[w] == len(p):
                stack.append(p + (w,))
    return sorted(out)


def redges(row):
    return frozenset(norm(row[i], row[i + 1]) for i in range(len(row) - 1))


# ------------------------------------------------------------ matching (mine)
def kuhn(left, adjmap, right_all=None):
    """Max bipartite matching, left ids -> iterables of right ids."""
    mr = {}
    ml = {}

    def aug(u, seen):
        for w in adjmap.get(u, ()):
            if w in seen:
                continue
            seen.add(w)
            if w not in mr or aug(mr[w], seen):
                mr[w] = u
                ml[u] = w
                return True
        return False

    for u in left:
        aug(u, set())
    return ml


# ------------------------------------------------------------ fixture model
class Fix:
    def __init__(self, name, n, shoreL, shoreR, support, atoms):
        self.name = name
        self.n = n
        self.L = set(shoreL)
        self.R = set(shoreR)
        self.support = sorted(norm(*e) for e in support)
        self.sset = set(self.support)
        self.atoms = atoms  # list of dict(u, v, rows[tuple5], foot frozenset)
        for a in atoms:
            a["foot"] = frozenset().union(*(redges(r) for r in a["rows"]))


def load_hit(fname, name):
    src = json.loads((WS / fname).read_text(encoding="utf-8"))
    hit = src["hit"]
    n, edges = g6(hit["graph6"])
    Lc, Rc = src["left"], src["right"]
    adj = make_adj(n, edges)
    atoms = []
    stored_row_mismatch = 0
    for rec in hit["selectedAtoms"]:
        u, v = rec["u"], rec["v"]
        mine = rows4(adj, u, v)
        stored = sorted(tuple(r) for r in rec["rows"])
        mine_rev = sorted(tuple(reversed(r)) for r in mine)
        if stored != mine and stored != sorted(mine_rev):
            stored_row_mismatch += 1
        atoms.append({"u": u, "v": v, "rows": mine})
    check(f"{name}: stored rows == my recomputed complete families",
          stored_row_mismatch == 0, f"mismatches={stored_row_mismatch}")
    fx = Fix(name, n, range(Lc), range(Lc, Lc + Rc), edges, atoms)
    fx.graph6 = hit["graph6"]
    return fx


def build_nearcand():
    # R46 sec.8: L={v,m,a,b0..b4}=0..7, R={x0..x4,y0..y4}=8..17
    V, M, A = 0, 1, 2
    B = list(range(3, 8))
    X = list(range(8, 13))
    Y = list(range(13, 18))
    edges = []
    for x in X:
        edges += [(V, x), (M, x)]
    for x in X[:4]:
        edges.append((A, x))
    for y in Y:
        edges.append((A, y))
    for j in range(5):
        edges.append((B[j], Y[j]))
    assert len(edges) == 24
    adj = make_adj(18, edges)
    pairs = ([(V, b) for b in B] + [(M, b) for b in B]
             + list(combinations(B, 2)) + [(X[4], y) for y in Y])
    atoms = [{"u": u, "v": v, "rows": rows4(adj, u, v)} for u, v in pairs]
    return Fix("nearcand", 18, range(8), range(8, 18), edges, atoms)


def build_r34deg():
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    row = (0, 1, 2, 3, 4)
    atoms = [{"u": 0, "v": 4, "rows": [row]} for _ in range(5)]
    return Fix("r34deg", 5, [0, 2, 4], [1, 3], edges, atoms)


class AbsFix:
    """Abstract circuit: ground set of 'edge' ids, atoms = footprints."""

    def __init__(self, name, ground, foots):
        self.name = name
        self.support = list(ground)
        self.atoms = [{"foot": frozenset(f)} for f in foots]


def load_t4abs():
    src = json.loads((WS / "t4_support_circuit_hit.json").read_text())
    return AbsFix("t4abs", range(15), [tuple(r) for r in src["rows"]])


# ------------------------------------------------------------ circuit axioms
def axiom_report(fx, exp_total, exp_tri=None):
    name = fx.name
    A = len(fx.atoms)
    E = len(fx.support)
    eidx = {e: i for i, e in enumerate(fx.support)}
    foot = [sorted(eidx[e] for e in a["foot"]) for a in fx.atoms]

    # union completeness
    union = set().union(*(a["foot"] for a in fx.atoms))
    check(f"{name}: union of footprints == all {E} support edges",
          union == set(fx.support))

    # dependence: no full SDR (rank < A)
    full = kuhn(range(A), {i: foot[i] for i in range(A)})
    check(f"{name}: rank == |F*| == {E} (dependent family)", len(full) == E,
          f"rank={len(full)}")

    # deletion SDRs
    sizes = []
    for ex in range(A):
        m = kuhn([i for i in range(A) if i != ex],
                 {i: foot[i] for i in range(A) if i != ex})
        sizes.append(len(m))
    check(f"{name}: all {A} deletion-SDRs perfect (size {E})",
          sizes == [E] * A, f"sizes={sorted(set(sizes))}")

    # multiplicity
    mult = {e: 0 for e in fx.support}
    for a in fx.atoms:
        for e in a["foot"]:
            mult[e] += 1
    minmult = min(mult.values())
    check(f"{name}: every support edge multiplicity >= 2", minmult >= 2,
          f"min={minmult}")

    # CLAIM 1: allowed incidences == total incidences
    total = sum(len(f) for f in foot)
    allowed = 0
    for a in range(A):
        for e in foot[a]:
            m = kuhn([i for i in range(A) if i != a],
                     {i: [x for x in foot[i] if x != e]
                      for i in range(A) if i != a})
            if len(m) == E - 1:
                allowed += 1
    check(f"{name}: CLAIM1 allowed == total == {exp_total}",
          allowed == total == exp_total,
          f"allowed={allowed} total={total}")

    rep = {"atoms": A, "edges": E, "total": total, "allowed": allowed,
           "minMult": minmult}

    if isinstance(fx, Fix):
        # triangles of support+atom union graph
        uedges = set(fx.support) | {norm(a["u"], a["v"]) for a in fx.atoms}
        adjs = [set() for _ in range(fx.n)]
        for u, v in uedges:
            adjs[u].add(v)
            adjs[v].add(u)
        tri = sum(1 for u in range(fx.n) for v in adjs[u] if v > u
                  for w in adjs[u] & adjs[v] if w > v)
        if exp_tri is not None:
            check(f"{name}: triangle count == {exp_tri}", tri == exp_tri,
                  f"tri={tri}")
        rep["triangles"] = tri

        # shores + distances + distinct pairs
        sameshore = all((a["u"] in fx.L) == (a["v"] in fx.L) for a in fx.atoms)
        bip = all((u in fx.L) != (v in fx.L) for u, v in fx.support)
        distinct = (len({norm(a["u"], a["v"]) for a in fx.atoms}) == A
                    or name == "r34deg")  # degenerate-by-design fixture
        adj = make_adj(fx.n, fx.support)
        d4 = all(bfs(adj, a["u"])[a["v"]] == 4 for a in fx.atoms)
        check(f"{name}: atoms same-shore, support bipartite, pairs distinct, "
              f"all endpoint distances exactly 4",
              sameshore and bip and distinct and d4,
              f"ss={sameshore} bip={bip} dis={distinct} d4={d4}")

        # CLAIM 2: visitor pigeonhole
        deg = [0] * fx.n
        for u, v in fx.support:
            deg[u] += 1
            deg[v] += 1
        vis = [set() for _ in range(fx.n)]
        for i, a in enumerate(fx.atoms):
            for (x, y) in a["foot"]:
                vis[x].add(i)
                vis[y].add(i)
        slacks = {u: len(vis[u]) - deg[u] for u in range(fx.n) if deg[u] >= 1}
        viol = [u for u, s in slacks.items() if s < 1]
        rep["pigeonholeMinSlack"] = min(slacks.values())
        check(f"{name}: CLAIM2 pigeonhole visitors>=deg+1 everywhere",
              not viol, f"violations={viol} minSlack={rep['pigeonholeMinSlack']}")
    return rep


# ------------------------------------------------------------ profiles (mine)
def inc_atoms(fx, w):
    return [i for i, a in enumerate(fx.atoms) if w in (a["u"], a["v"])]


def first_step(row, w):
    if row[0] == w:
        return row[1]
    if row[-1] == w:
        return row[-2]
    raise AssertionError


def classifier(fx, adj, w, x0):
    Yv = [y for y in adj[w] if y != x0]
    inc = inc_atoms(fx, w)
    non = [i for i in range(len(fx.atoms)) if i not in inc]
    e_forced = sum(1 for i in non
                   if all(w in r for r in fx.atoms[i]["rows"]))
    # steps
    i_step = 0
    step_edges = []
    for i in inc:
        st = {first_step(r, w) for r in fx.atoms[i]["rows"]} & set(Yv)
        if not st:
            i_step += 1
        step_edges += [(y, i) for y in st]
    am = {}
    for y, i in step_edges:
        am.setdefault(("y", y), []).append(("a", i))
    d_step = len(Yv) - len(kuhn(list(am), am))
    # coverage
    cov_edges = []
    for y in Yv:
        for i in non:
            if any(w not in r and x0 in r and y in r
                   for r in fx.atoms[i]["rows"]):
                cov_edges.append((y, i))
    am = {}
    for y, i in cov_edges:
        am.setdefault(("y", y), []).append(("a", i))
    d_cov = len(Yv) - len(kuhn(list(am), am))
    return (e_forced, i_step, d_step, d_cov)


def owner_table(fx):
    adj = make_adj(fx.n, fx.support)
    bad = [0] * fx.n
    for a in fx.atoms:
        bad[a["u"]] += 1
        bad[a["v"]] += 1
    tab = {}
    for w in range(fx.n):
        if len(adj[w]) == 5 and bad[w] == 5:
            tab[w] = {x: classifier(fx, adj, w, x) for x in adj[w]}
    return tab


# ---------------------------------------------------- profile states (mine)
def state_ok(fx, assign, w, x0, label):
    """Full explicit check that assign (atom->row) realizes profile (w,x0)."""
    adj = make_adj(fx.n, fx.support)
    Yv = [y for y in adj[w] if y != x0]
    ok = True
    det = []
    # rows legal
    for i, r in assign.items():
        if r not in fx.atoms[i]["rows"]:
            ok = False
            det.append(f"atom{i} row not in DB")
    if set(assign) != set(range(len(fx.atoms))):
        ok = False
        det.append("not a full assignment")
    S = set().union(*(redges(r) for r in assign.values()))
    rcount = sum(1 for r in assign.values() if w in r)
    if rcount != 5:
        ok = False
        det.append(f"r({w})={rcount}")
    if norm(w, x0) in S:
        ok = False
        det.append("active edge selected")
    for y in Yv:
        if norm(w, y) not in S:
            ok = False
            det.append(f"edge ({w},{y}) unselected")
    for y in Yv:
        if not any(w not in r and x0 in r and y in r for r in assign.values()):
            ok = False
            det.append(f"pair ({x0},{y}) uncovered")
    check(label, ok, "; ".join(det))
    return ok


def construct_state(fx, w, x0):
    """Greedy construction from the two matchings; returns assign or None."""
    adj = make_adj(fx.n, fx.support)
    Yv = [y for y in adj[w] if y != x0]
    inc = inc_atoms(fx, w)
    non = [i for i in range(len(fx.atoms)) if i not in inc]
    # step matching
    am = {}
    for i in inc:
        for y in {first_step(r, w) for r in fx.atoms[i]["rows"]} & set(Yv):
            am.setdefault(("y", y), []).append(("a", i))
    ms = kuhn(list(am), am)
    if len(ms) != len(Yv):
        return None
    assign = {}
    for (ty, y), (ta, i) in ms.items():
        assign[i] = next(r for r in fx.atoms[i]["rows"]
                         if first_step(r, w) == y)
    for i in inc:
        if i not in assign:
            cand = [r for r in fx.atoms[i]["rows"]
                    if first_step(r, w) in Yv]
            if not cand:
                return None
            assign[i] = cand[0]
    # coverage matching
    am = {}
    for y in Yv:
        for i in non:
            if any(w not in r and x0 in r and y in r
                   for r in fx.atoms[i]["rows"]):
                am.setdefault(("y", y), []).append(("a", i))
    mc = kuhn(list(am), am)
    if len(mc) != len(Yv):
        return None
    for (ty, y), (ta, i) in mc.items():
        assign[i] = next(r for r in fx.atoms[i]["rows"]
                         if w not in r and x0 in r and y in r)
    for i in non:
        if i not in assign:
            cand = [r for r in fx.atoms[i]["rows"] if w not in r]
            if not cand:
                return None
            assign[i] = cand[0]
    return assign


# ---------------------------------------------------- bi-stuck + census
def bistuck(fx, v, m):
    incs = set(inc_atoms(fx, v)) | set(inc_atoms(fx, m))
    return [i for i in range(len(fx.atoms)) if i not in incs
            and all(v in r or m in r for r in fx.atoms[i]["rows"])]


def census(fx, v, xv, m, xm):
    """Exhaustive single-pivot transition search v-profile -> m-profile.
    Returns (pairsTried, feasibleList)."""
    adj = make_adj(fx.n, fx.support)
    Yv = [y for y in adj[v] if y != xv]
    Ym = [y for y in adj[m] if y != xm]
    iv, im = set(inc_atoms(fx, v)), set(inc_atoms(fx, m))
    assert not (iv & im)
    nA = len(fx.atoms)

    def aside(i, rows):
        if i in iv:
            return [r for r in rows if first_step(r, v) != xv]
        return [r for r in rows if v not in r]

    def bside(i, rows):
        if i in im:
            return [r for r in rows if first_step(r, m) != xm]
        return [r for r in rows if m not in r]

    shared = {i: bside(i, aside(i, fx.atoms[i]["rows"])) for i in range(nA)}
    pairs = 0
    feas = []
    for p in range(nA):
        ra_list = aside(p, fx.atoms[p]["rows"])
        rb_list = bside(p, fx.atoms[p]["rows"])
        blocked = [q for q in range(nA) if q != p and not shared[q]]
        for ra in ra_list:
            for rb in rb_list:
                if ra == rb:
                    continue
                pairs += 1
                if blocked:
                    continue
                if joint_dfs(fx, v, xv, m, xm, Yv, Ym, iv, im, shared, p,
                             ra, rb):
                    feas.append((p, ra, rb))
    return pairs, feas


def joint_dfs(fx, v, xv, m, xm, Yv, Ym, iv, im, shared, p, ra, rb):
    """Full joint CSP (only reached if the per-atom filter passes)."""
    nA = len(fx.atoms)
    need_sv, need_sm = set(Yv), set(Ym)
    need_cv, need_cm = set(Yv), set(Ym)

    def contrib(i, r, sv, sm, cv, cm):
        if i in iv:
            sv.add(first_step(r, v))
        else:
            for y in Yv:
                if v not in r and xv in r and y in r:
                    cv.add(y)
        if i in im:
            sm.add(first_step(r, m))
        else:
            for y in Ym:
                if m not in r and xm in r and y in r:
                    cm.add(y)

    sv, sm, cv, cm = set(), set(), set(), set()
    contrib(p, ra, sv, set(), cv, set())
    contrib(p, rb, set(), sm, set(), cm)
    need_sv -= sv
    need_sm -= sm
    need_cv -= cv
    need_cm -= cm
    order = [q for q in range(nA) if q != p]

    def dfs(idx, nsv, nsm, ncv, ncm):
        if not (nsv or nsm or ncv or ncm):
            return True
        if idx == len(order):
            return False
        q = order[idx]
        for r in shared[q]:
            sv, sm, cv, cm = set(), set(), set(), set()
            contrib(q, r, sv, sm, cv, cm)
            if dfs(idx + 1, nsv - sv, nsm - sm, ncv - cv, ncm - cm):
                return True
        return False

    return dfs(0, frozenset(need_sv), frozenset(need_sm),
               frozenset(need_cv), frozenset(need_cm))


# ---------------------------------------------------- hub theorem (claim 4)
def hub_checks(fx, v, s, m, exp_inc):
    adj = make_adj(fx.n, fx.support)
    name = fx.name
    check(f"{name}: hub s={s} degree 2 with N(s)=={{{v},{m}}}",
          sorted(adj[s]) == sorted([v, m]),
          f"N({s})={adj[s]}")
    incs = inc_atoms(fx, s)
    check(f"{name}: |Inc({s})| == {exp_inc}", len(incs) == exp_inc,
          f"got {len(incs)}")
    # row-level lemma: every v-avoiding row containing s and some y in N(v)-s
    # has s as an endpoint and first edge (s,m)
    Yv = [y for y in adj[v] if y != s]
    viol = 0
    wit = 0
    for i, a in enumerate(fx.atoms):
        for r in a["rows"]:
            if v in r or s not in r:
                continue
            if not any(y in r for y in Yv):
                continue
            wit += 1
            endp = r[0] == s or r[-1] == s
            fe = endp and first_step(r, s) == m
            if not (endp and fe and i in incs):
                viol += 1
    check(f"{name}: CLAIM4(a) every coverage-shaped row at hub {s} "
          f"(owner {v}) is s-anchored with first edge ({s},{m})",
          viol == 0, f"witnessRows={wit} violations={viol}")
    # Inc(s) subset of bistuck(v,m)
    bs = set(bistuck(fx, v, m))
    check(f"{name}: CLAIM4(b) Inc({s}) subset of biStuck({v},{m})",
          set(incs) <= bs, f"inc={incs} bs={sorted(bs)}")
    return len(incs)


# ---------------------------------------------------- fiber forcing (claim 5)
def fiber_report(fx, v, x0):
    adj = make_adj(fx.n, fx.support)
    Yv = [y for y in adj[v] if y != x0]
    inc = set(inc_atoms(fx, v))
    fibers = {}
    for y in Yv:
        fibers[y] = [(i, r) for i, a in enumerate(fx.atoms) if i not in inc
                     for r in a["rows"]
                     if v not in r and x0 in r and y in r]
    tail = [norm(x0, z) for z in adj[x0] if z != v]
    forced = {}
    for e in tail:
        forced[e] = [y for y, fib in fibers.items()
                     if fib and all(e in redges(r) for _, r in fib)]
    full = all(forced[e] for e in tail)
    return {"fiberSizes": {y: len(f) for y, f in fibers.items()},
            "tail": tail, "forced": forced, "full": full,
            "fibers": fibers}


# ---------------------------------------------------- engine state replay
def engine_state_check(fx, verif_file, label):
    src = json.loads((WS / verif_file).read_text())
    w, x0 = src["owner"], src["activeNeighbour"]
    pairmap = {norm(a["u"], a["v"]): i for i, a in enumerate(fx.atoms)}
    assign = {}
    for k, r in src["selectedRows"].items():
        r = tuple(r)
        i = pairmap[norm(r[0], r[-1])]
        rr = r if r in fx.atoms[i]["rows"] else tuple(reversed(r))
        assign[i] = rr
    return state_ok(fx, assign, w, x0,
                    f"{label}: archived engine state realizes profile "
                    f"({w}@{x0}) under MY checker")


# ---------------------------------------------------- artifact sha replay
def artifact_sha():
    p = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\matroid"
             r"\matroid_lens_results.json")
    payload = json.loads(p.read_text(encoding="utf-8"))
    claimed = payload.pop("canonicalSha256")
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       default=str)
    got = hashlib.sha256(canon.encode("ascii")).hexdigest()
    check("artifact: embedded canonicalSha256 reproducible from content",
          got == claimed, f"claimed={claimed[:12]} got={got[:12]}")


def main():
    sys.setrecursionlimit(100000)
    print("== loading fixtures ==")
    h298 = load_hit("t5_classifier_v_l9_r9_1000.json", "hit298")
    h264 = load_hit("t5_live_x_classifier_v_l9_r9_5000.json", "hit264")
    nc = build_nearcand()
    r34 = build_r34deg()
    t4 = load_t4abs()
    check("hit298: graph6 matches R49 archive",
          h298.graph6 == "Q??????wE_[?EGs?D_@A?C_B???")
    check("hit264: graph6 matches R50 archive",
          h264.graph6 == "Q??????wE_Bws?s?DCD??@?@???")

    print("\n== circuit axioms + CLAIM 1 + CLAIM 2 ==")
    rep298 = axiom_report(h298, 220, 0)
    rep264 = axiom_report(h264, 210, 0)
    repnc = axiom_report(nc, 215, 30)
    rep34 = axiom_report(r34, 20)
    rept4 = axiom_report(t4, 64)
    check("CLAIM2: min slack (visitors-deg) == 1 on hit298",
          rep298["pigeonholeMinSlack"] == 1,
          f"got {rep298['pigeonholeMinSlack']}")
    check("CLAIM2: min slack (visitors-deg) == 1 on hit264",
          rep264["pigeonholeMinSlack"] == 1,
          f"got {rep264['pigeonholeMinSlack']}")
    check("CLAIM2: min slack (visitors-deg) == 3 on nearcand",
          repnc["pigeonholeMinSlack"] == 3,
          f"got {repnc['pigeonholeMinSlack']}")

    print("\n== profile classifier tables ==")
    tabs = {}
    for fx in (h298, h264, nc):
        tabs[fx.name] = owner_table(fx)
    z298 = sorted((w, x) for w, ac in tabs["hit298"].items()
                  for x, vec in ac.items() if vec == (0, 0, 0, 0))
    z264 = sorted((w, x) for w, ac in tabs["hit264"].items()
                  for x, vec in ac.items() if vec == (0, 0, 0, 0))
    znc = sorted((w, x) for w, ac in tabs["nearcand"].items()
                 for x, vec in ac.items() if vec == (0, 0, 0, 0))
    check("hit298: zero-vector set == {(0,17),(1,17)}",
          z298 == [(0, 17), (1, 17)], f"got {z298}")
    check("hit264: zero-vector set == {(0,9)}", z264 == [(0, 9)],
          f"got {z264}")
    check("nearcand: zero-vector set == {(0,12),(1,12)}",
          znc == [(0, 12), (1, 12)], f"got {znc}")
    ef1 = {x: vec[0] for x, vec in tabs["hit264"].get(1, {}).items()}
    check("hit264: owner 1 eForced == 2 at every active",
          ef1 and all(v == 2 for v in ef1.values()), f"got {ef1}")
    print("  hit264 eligible owners:", sorted(tabs["hit264"]))
    print("  hit298 eligible owners:", sorted(tabs["hit298"]))
    print("  nearcand eligible owners:", sorted(tabs["nearcand"]))

    print("\n== CLAIM 3: bi-stuck + realizability + transition census ==")
    bs298 = bistuck(h298, 0, 1)
    bs264 = bistuck(h264, 0, 1)
    bsnc = bistuck(nc, 0, 1)
    check("hit298: biStuck(0,1) count == 8", len(bs298) == 8,
          f"got {len(bs298)}: {[norm(h298.atoms[i]['u'], h298.atoms[i]['v']) for i in bs298]}")
    check("hit264: biStuck(0,1) count == 2", len(bs264) == 2,
          f"got {len(bs264)}: {[norm(h264.atoms[i]['u'], h264.atoms[i]['v']) for i in bs264]}")
    check("nearcand: biStuck(0,1) count == 5", len(bsnc) == 5,
          f"got {len(bsnc)}: {[norm(nc.atoms[i]['u'], nc.atoms[i]['v']) for i in bsnc]}")

    for fx, zeros in ((h298, z298), (h264, z264), (nc, znc)):
        for (w, x) in zeros:
            a = construct_state(fx, w, x)
            ok = a is not None and state_ok(
                fx, a, w, x,
                f"{fx.name}: profile state ({w}@{x}) constructed+verified")
            if a is not None and ok:
                # claim-4 corollaries on the explicit state where hub is d2
                adj = make_adj(fx.n, fx.support)
                if len(adj[x]) == 2:
                    mm = [z for z in adj[x] if z != w][0]
                    S = set().union(*(redges(r) for r in a.values()))
                    latent = fx.sset - S
                    comp = latent_component(fx, latent, w, x)
                    check(f"{fx.name}: state ({w}@{x}): edge ({x},{mm}) "
                          f"selected and active component == {{{w},{x}}}",
                          norm(x, mm) in S and comp == {w, x},
                          f"comp={sorted(comp)}")

    for fx, zeros in ((h298, z298), (nc, znc)):
        combos = [((w1, x1), (w2, x2)) for (w1, x1) in zeros
                  for (w2, x2) in zeros if w1 != w2]
        for (w1, x1), (w2, x2) in combos:
            pairs, feas = census(fx, w1, x1, w2, x2)
            exp = 128 if fx.name == "hit298" else 200
            check(f"{fx.name}: census {w1}@{x1}->{w2}@{x2}: 0 feasible over "
                  f"{exp} pivot row-pairs",
                  len(feas) == 0 and pairs == exp,
                  f"pairs={pairs} feasible={len(feas)}")

    print("\n== CLAIM 4: shared-d2-hub checks ==")
    hub_checks(h298, 0, 17, 1, 4)
    hub_checks(h298, 1, 17, 0, 4)
    hub_checks(nc, 0, 12, 1, 5)
    hub_checks(nc, 1, 12, 0, 5)
    adj264 = make_adj(h264.n, h264.support)
    check("hit264: hub 9 is NOT d2-co-owned (degree 3) — outside Claim4 class",
          len(adj264[9]) == 3, f"N(9)={adj264[9]}")

    print("\n== CLAIM 5: fiber forcing ==")
    expect = {
        ("hit298", 0, 17): {"blanket": [(1, 17)]},
        ("hit298", 1, 17): {"blanket": [(0, 17)]},
        ("hit264", 0, 9): {"blanket": [(1, 9), (2, 9)]},
        ("nearcand", 0, 12): {"blanket": [(1, 12)]},
        ("nearcand", 1, 12): {"blanket": [(0, 12)]},
    }
    for fx, zeros in ((h298, z298), (h264, z264), (nc, znc)):
        for (w, x) in zeros:
            fr = fiber_report(fx, w, x)
            exp = expect[(fx.name, w, x)]
            check(f"{fx.name}: fiber FULL_BLANKET at ({w}@{x}), tail == "
                  f"{exp['blanket']}",
                  fr["full"] and sorted(fr["tail"]) == sorted(exp["blanket"]),
                  f"tail={fr['tail']} forced={ {str(k): v for k, v in fr['forced'].items()} }")
            if (fx.name, w, x) == ("hit264", 0, 9):
                f19 = fr["forced"].get((1, 9), [])
                f29 = fr["forced"].get((2, 9), [])
                sizes = fr["fiberSizes"]
                check("hit264: (1,9) forced by all four fibers {10,12,13,15}",
                      sorted(f19) == [10, 12, 13, 15], f"got {f19}")
                check("hit264: (2,9) forced exactly by fiber y=15",
                      f29 == [15], f"got {f29}")
                check("hit264: fiber sizes {10:3,12:3,13:3,15:1}",
                      sizes == {10: 3, 12: 3, 13: 3, 15: 1}, f"got {sizes}")
                if sizes.get(15) == 1:
                    (i, r) = fr["fibers"][15][0]
                    check("hit264: unique y=15 witness row == (15,2,9,1,17)",
                          r == (15, 2, 9, 1, 17) or r == (17, 1, 9, 2, 15),
                          f"got {r}")

    print("\n== engine archived states replayed under my checker ==")
    engine_state_check(h298, "t5_classifier_v_l9_r9_hit_verification.json",
                       "hit298")
    engine_state_check(h264,
                       "t5_live_x_classifier_v_l9_r9_hit_verification.json",
                       "hit264")

    print("\n== artifact canonical sha ==")
    artifact_sha()

    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES:")
        for l, d in FAILURES:
            print("  -", l, "|", d)
    else:
        print("ALL CHECKS PASSED")
    (OUT / "verify0_summary.json").write_text(json.dumps(
        {"failures": FAILURES}, indent=1))


def latent_component(fx, latent, w, x0):
    """Component of the active edge (w,x0) in the latent graph."""
    adjl = {}
    for (u, v) in latent:
        adjl.setdefault(u, []).append(v)
        adjl.setdefault(v, []).append(u)
    seen = {w, x0}
    q = deque([w, x0])
    while q:
        u = q.popleft()
        for v in adjl.get(u, ()):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return seen


if __name__ == "__main__":
    main()
