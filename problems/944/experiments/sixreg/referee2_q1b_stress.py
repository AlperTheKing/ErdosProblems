# referee2_q1b_stress.py
# Adversarial stress test of the claimed refutation's CASE ANALYSIS:
#  (i)  random instances satisfying ALL lemma hypotheses, random bans;
#       whenever >= 1 ordered base survives, apply the salvage repair recipe
#       VERBATIM (base colouring + relocate clashing anchors to third colour)
#       for EVERY surviving base and check properness + ban-avoidance;
#  (ii) whenever ALL 6 bases are killed, verify step-(2)'s structural claim
#       (3+3 split, rainbow labels both sides, all 6 cross anchor edges) and
#       test claim (3a): any matched anchor edge => graph UNSAT;
#  (iii) targeted extremal instances (rainbow bans, all 6 cross edges,
#       random matched set M, random fillers): M != {} must be UNSAT,
#       M == {} outcome recorded (claimed filler-dependent).
import itertools, random
from collections import deque

COL = (0, 1, 2)

def build(edges):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return adj

def connected(adj):
    vs = list(adj)
    seen = {vs[0]}; dq = deque([vs[0]])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); dq.append(w)
    return len(seen) == len(adj)

def hyp_ok(P, Q, edges, anchors):
    adj = build(edges)
    Pset, Aset = set(P), set(anchors)
    if set(adj) != set(P) | set(Q): return None
    if not all((u in Pset) != (v in Pset) for u, v in edges): return None
    d5 = sorted(v for v in adj if len(adj[v]) == 5)
    if d5 != sorted(anchors): return None
    if not all(len(adj[v]) == 6 for v in adj if v not in Aset): return None
    if not connected(adj): return None
    # parity identity from the writeup's sharpening of step (2)
    aP = sum(1 for a in anchors if a in Pset)
    aQ = len(anchors) - aP
    assert 6 * len(P) - aP == len(edges) == 6 * len(Q) - aQ, "parity identity fails"
    return adj

def realize_bipartite(pdef, qdef, rng, existing, tries=300):
    """Random simple bipartite graph with the given residual degrees,
    avoiding 'existing' edges. Returns edge set or None."""
    for _ in range(tries):
        pd = dict(pdef); qd = dict(qdef); E = set()
        ok = True
        order = [p for p in pd for _ in range(pd[p])]
        rng.shuffle(order)
        for p in order:
            cands = [q for q in qd if qd[q] > 0 and (p, q) not in existing and (p, q) not in E]
            if not cands:
                ok = False; break
            q = rng.choice(cands)
            E.add((p, q)); qd[q] -= 1
        if ok and all(v == 0 for v in qd.values()):
            return E
    return None

def gen33(rng, n=9, force_cross=None, forceM=None, rainbow=False):
    X = ['x1', 'x2', 'x3']; Y = ['y1', 'y2', 'y3']
    Ps = [f'p{i}' for i in range(n)]; Qs = [f'q{i}' for i in range(n)]
    if rainbow:
        permx = list(COL); rng.shuffle(permx)
        permy = list(COL); rng.shuffle(permy)
        gamma = {f'x{i+1}': permx[i] for i in range(3)}
        gamma.update({f'y{i+1}': permy[i] for i in range(3)})
    else:
        gamma = {a: rng.choice(COL) for a in X + Y}
    A = set()
    if force_cross:
        for x in X:
            for y in Y:
                if gamma[x] != gamma[y]:
                    A.add((x, y))
        for x in X:
            for y in Y:
                if gamma[x] == gamma[y] and (forceM == 'all' or
                        (forceM == 'random' and rng.random() < 0.5)):
                    A.add((x, y))
    else:
        p_edge = rng.choice([0.15, 0.4, 0.7])
        for x in X:
            for y in Y:
                if rng.random() < p_edge:
                    A.add((x, y))
    edges = set(A)
    pdef = {p: 6 for p in Ps}; qdef = {q: 6 for q in Qs}
    for x in X:
        need = 5 - sum(1 for y in Y if (x, y) in A)
        for q in rng.sample(Qs, need):
            edges.add((x, q)); qdef[q] -= 1
    for y in Y:
        need = 5 - sum(1 for x in X if (x, y) in A)
        for p in rng.sample(Ps, need):
            edges.add((p, y)); pdef[p] -= 1
    if min(pdef.values()) < 0 or min(qdef.values()) < 0:
        return None
    F = realize_bipartite(pdef, qdef, rng, edges)
    if F is None:
        return None
    edges |= F
    P = X + Ps; Q = Y + Qs
    adj = hyp_ok(P, Q, edges, X + Y)
    if adj is None:
        return None
    return P, Q, edges, adj, X + Y, gamma, A

def gen60(rng, nP=7):
    X = [f'x{i}' for i in range(1, 7)]          # all six anchors on P side
    nQ = nP + 5
    Ps = [f'p{i}' for i in range(nP)]; Qs = [f'q{i}' for i in range(nQ)]
    gamma = {a: rng.choice(COL) for a in X}
    edges = set(); qdef = {q: 6 for q in Qs}
    for x in X:
        for q in rng.sample(Qs, 5):
            edges.add((x, q)); qdef[q] -= 1
    if min(qdef.values()) < 0:
        return None
    F = realize_bipartite({p: 6 for p in Ps}, qdef, rng, edges)
    if F is None:
        return None
    edges |= F
    P = X + Ps; Q = Qs
    adj = hyp_ok(P, Q, edges, X)
    if adj is None:
        return None
    return P, Q, edges, adj, X, gamma, set()

def killed_bases(anchor_edges, gamma):
    killed = set()
    for x, y in anchor_edges:
        if gamma[x] != gamma[y]:
            killed.add((gamma[x], gamma[y]))
    return killed

def apply_recipe(P, Q, edges, anchors, gamma, base):
    """The salvage recipe VERBATIM: base colouring + relocate every clashing
    anchor to the third colour. Returns (psi, proper?, bans_ok?)."""
    p, q = base; c = 3 - p - q
    Pset = set(P)
    psi = {v: (p if v in Pset else q) for v in P + Q}
    for a in anchors:
        if a in Pset and gamma[a] == p:
            psi[a] = c
        if a not in Pset and gamma[a] == q:
            psi[a] = c
    proper = all(psi[u] != psi[v] for u, v in edges)
    bans = all(psi[a] != gamma[a] for a in anchors)
    return psi, proper, bans

def exact_unsat(P, Q, adj, anchors, banned):
    """Complete decision: True iff NO proper ban-avoiding colouring exists."""
    Aset = set(anchors)
    pF = [v for v in P if v not in Aset]
    qF = [v for v in Q if v not in Aset]
    for ac in itertools.product(COL, repeat=len(anchors)):
        col = dict(zip(anchors, ac))
        if any(col[a] == banned.get(a, -1) for a in anchors):
            continue
        if any(w in col and col[w] == col[a] for a in anchors for w in adj[a]):
            continue
        allowed = []
        ok = True
        for pv in pF:
            al = [cc for cc in COL if all(col.get(w) != cc for w in adj[pv])]
            if not al:
                ok = False; break
            allowed.append(al)
        if not ok:
            continue
        for pc in itertools.product(*allowed):
            colp = dict(zip(pF, pc))
            good = True
            for qv in qF:
                free = {0, 1, 2}
                for w in adj[qv]:
                    free.discard(col[w] if w in col else colp[w])
                if not free:
                    good = False; break
            if good:
                return False
    return True

rng = random.Random(20260612)
fail_log = []

# ---------- (i)+(ii): random 3+3 instances ----------
n_inst = n_surv = n_recipe_ok = n_recipe_fail = n_allkilled = 0
n_extremal_confirmed = n_extremal_violated = 0
allkilled_results = []
trials = 0
while n_inst < 500 and trials < 5000:
    trials += 1
    g = gen33(rng, n=rng.choice([9, 10, 12]))
    if g is None:
        continue
    P, Q, edges, adj, anchors, gamma, A = g
    n_inst += 1
    killed = killed_bases(A, gamma)
    survivors = [(p, q) for p in COL for q in COL if p != q and (p, q) not in killed]
    if survivors:
        n_surv += 1
        for base in survivors:
            psi, proper, bans = apply_recipe(P, Q, edges, anchors, gamma, base)
            if proper and bans:
                n_recipe_ok += 1
            else:
                n_recipe_fail += 1
                fail_log.append(("recipe-fail", base, gamma, sorted(A)))
    else:
        n_allkilled += 1
        # verify step-(2) structural claim
        gx = [gamma[f'x{i}'] for i in (1, 2, 3)]
        gy = [gamma[f'y{i}'] for i in (1, 2, 3)]
        rainbow = sorted(gx) == [0, 1, 2] and sorted(gy) == [0, 1, 2]
        cross_ok = all(any((x, y) in A and gamma[x] == p and gamma[y] == q
                           for x in ('x1', 'x2', 'x3') for y in ('y1', 'y2', 'y3'))
                       for p in COL for q in COL if p != q)
        if rainbow and cross_ok:
            n_extremal_confirmed += 1
        else:
            n_extremal_violated += 1
            fail_log.append(("step2-claim-violated", gamma, sorted(A)))
        M = [(x, y) for (x, y) in A if gamma[x] == gamma[y]]
        unsat = exact_unsat(P, Q, adj, anchors, gamma)
        allkilled_results.append((len(M), unsat))
        if M and not unsat:
            fail_log.append(("3a-violated", gamma, sorted(A)))
print(f"[3+3 random] instances={n_inst} with-survivor={n_surv} "
      f"recipe applications OK={n_recipe_ok} FAIL={n_recipe_fail}")
print(f"[3+3 random] all-killed={n_allkilled} extremal-pattern confirmed={n_extremal_confirmed} "
      f"violated={n_extremal_violated}; (|M|,UNSAT) outcomes={allkilled_results}")

# ---------- (i): 6+0 split ----------
n_inst = n_ok = n_fail = 0
trials = 0
while n_inst < 150 and trials < 2000:
    trials += 1
    g = gen60(rng, nP=rng.choice([7, 9]))
    if g is None:
        continue
    P, Q, edges, adj, anchors, gamma, A = g
    n_inst += 1
    survivors = [(p, q) for p in COL for q in COL if p != q]   # nothing killed
    for base in survivors:
        psi, proper, bans = apply_recipe(P, Q, edges, anchors, gamma, base)
        if proper and bans:
            n_ok += 1
        else:
            n_fail += 1
            fail_log.append(("recipe-fail-60", base, gamma))
print(f"[6+0 random] instances={n_inst} recipe applications OK={n_ok} FAIL={n_fail}")

# ---------- (iii): targeted extremal configurations ----------
res = {}
n_3a_viol = 0
made = 0
trials = 0
while made < 240 and trials < 4000:
    trials += 1
    g = gen33(rng, n=9, force_cross=True,
              forceM=rng.choice(['none', 'random', 'all']), rainbow=True)
    if g is None:
        continue
    P, Q, edges, adj, anchors, gamma, A = g
    made += 1
    M = [(x, y) for (x, y) in A if gamma[x] == gamma[y]]
    unsat = exact_unsat(P, Q, adj, anchors, gamma)
    res.setdefault(len(M), [0, 0])
    res[len(M)][0 if unsat else 1] += 1
    if M and not unsat:
        n_3a_viol += 1
        fail_log.append(("3a-violated-targeted", gamma, sorted(A)))
print(f"[extremal targeted] made={made}; per |M|: " +
      ", ".join(f"|M|={k}: UNSAT={v[0]} SAT={v[1]}" for k, v in sorted(res.items())))
print(f"[extremal targeted] claim-(3a) violations (M nonempty but SAT): {n_3a_viol}")

if fail_log:
    print("\nFAILURES FOUND:")
    for f in fail_log[:20]:
        print("  ", f)
else:
    print("\nNO failures: recipe verbatim-correct on every surviving base; "
          "step-(2) extremal characterization and claim (3a) confirmed on all generated instances.")
