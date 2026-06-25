#!/usr/bin/env python3
# Referee C stress test: generate RANDOM small instances of the extremal
# configurations described in the refutation, apply the proof-skeleton's
# repair recipes VERBATIM, and check properness + ban-avoidance.
#
# Configurations (always: bipartite, Delta<=6, exactly six deg-5 anchors
# x0x1x2|y0y1y2, all others deg 6, connected; rainbow bans gamma(x_i)=i,
# gamma(y_j)=j):
#   T1: anchor core = full K_{3,3}                     (Counterexample A type)
#   T2: anchor core = K_{3,3} - PM, plus a non-anchor blocker us ~ y0,y1,y2
#   T3: anchor core = K_{3,3} - PM, NO blocker on either side
# Recipes tested verbatim (skeleton step (3)):
#   R1: sigma=(2,0,2), tau=(1,0,1)   ("two-valued families")
#   R2: sigma=tau=(1,2,0)            (cyclic; also the other cycle (2,0,1))
# Ground truth per instance: full exhaustive search (anchors free, bans on).
# Also: T0 = random NON-extremal gammas on the same graphs; recipe = skeleton
# steps (1)-(2) base+relocation, applied verbatim, then verified.
import itertools, random

ANCH_X = ['x0', 'x1', 'x2']; ANCH_Y = ['y0', 'y1', 'y2']
ANCH = ANCH_X + ANCH_Y
BAN = {f'x{i}': i for i in range(3)}; BAN.update({f'y{j}': j for j in range(3)})

def gen_instance(rng, typ, nside):
    P = ANCH_X + [f'p{k}' for k in range(nside - 3)]
    Q = ANCH_Y + [f'q{k}' for k in range(nside - 3)]
    req = []
    if typ == 1:
        req += [(f'x{i}', f'y{j}') for i in range(3) for j in range(3)]
    else:
        req += [(f'x{i}', f'y{j}') for i in range(3) for j in range(3) if i != j]
    if typ == 2:
        req += [('p0', f'y{j}') for j in range(3)]
    forb = set()
    if typ in (2, 3):
        forb = {(f'x{i}', f'y{i}') for i in range(3)}
    for _ in range(4000):                                   # retries
        target = {v: (5 if v in ANCH else 6) for v in P + Q}
        adj = {v: set() for v in P + Q}
        ok = True
        for a, b in req:
            adj[a].add(b); adj[b].add(a)
        rem = {v: target[v] - len(adj[v]) for v in P + Q}
        if any(r < 0 for r in rem.values()):
            raise RuntimeError('bad construction')
        while True:
            cand = [(a, b) for a in P for b in Q
                    if rem[a] > 0 and rem[b] > 0 and b not in adj[a]
                    and (a, b) not in forb]
            if not cand:
                break
            a, b = rng.choice(cand)
            adj[a].add(b); adj[b].add(a)
            rem[a] -= 1; rem[b] -= 1
        if any(rem.values()):
            continue                                        # deadlock; retry
        # connectivity
        seen = {P[0]}; st = [P[0]]
        while st:
            v = st.pop()
            for u in adj[v]:
                if u not in seen: seen.add(u); st.append(u)
        if len(seen) != len(P) + len(Q):
            continue
        if typ == 3:                                        # reject blockers
            if any(set(ANCH_Y) <= adj[p] for p in P if p not in ANCH_X):
                continue
            if any(set(ANCH_X) <= adj[q] for q in Q if q not in ANCH_Y):
                continue
        # final hypothesis audit
        deg5 = sorted(v for v in P + Q if len(adj[v]) == 5)
        assert deg5 == sorted(ANCH) and all(len(adj[v]) == 6 for v in P + Q if v not in ANCH)
        assert all(((a in set(P)) != (b in set(P))) for a in adj for b in adj[a])
        return P, Q, adj
    return None

def proper_and_banfree(adj, ban, col, dom=None):
    """check colouring col (possibly partial: dom = vertices it covers)"""
    bad = []
    for v in (dom or col):
        if ban.get(v) == col[v]:
            bad.append(('ban', v))
        for u in adj[v]:
            if u in col and col[u] == col[v]:
                bad.append(('edge', v, u))
    return bad

def search(adj, ban, fixed=None, cap=1):
    order = [v for v in adj if not fixed or v not in fixed]
    order.sort(key=lambda v: -len(adj[v]))
    col = dict(fixed) if fixed else {}
    cnt = 0
    def rec(d):
        nonlocal cnt
        if cnt >= cap: return
        if d == len(order):
            cnt += 1; return
        v = order[d]
        for c in range(3):
            if ban.get(v) == c: continue
            if any(col.get(u) == c for u in adj[v]): continue
            col[v] = c; rec(d + 1); del col[v]
    rec(0)
    return cnt

def base_relocate(adj, P, ban, p, q):
    """skeleton steps (1)-(2) verbatim: base (p,q), relocate clashing anchors to c"""
    c = 3 - p - q
    col = {v: (p if v in set(P) else q) for v in adj}
    for a in ANCH:
        if ban[a] == col[a]:
            col[a] = c
    return col

rng = random.Random(20260612)
print('=' * 78)
print('PART 1: extremal configurations, recipes verbatim')
print('=' * 78)
summary = {}
for typ, label in ((1, 'T1 full-K33'), (2, 'T2 K33-PM+blocker'), (3, 'T3 K33-PM no-blocker')):
    res = {'R1_ban_fail': 0, 'R1_other': 0,
           'R2a_improper': 0, 'R2a_noext': 0, 'R2a_ext': 0,
           'R2b_improper': 0, 'R2b_noext': 0, 'R2b_ext': 0,
           'truth_colourable': 0, 'n': 0}
    for k in range(30):
        nside = rng.choice([9, 10])
        inst = gen_instance(rng, typ, nside)
        if inst is None:
            continue
        P, Q, adj = inst
        res['n'] += 1
        # --- R1 verbatim: sigma=(2,0,2), tau=(1,0,1) on anchors
        colR1 = {f'x{i}': (2, 0, 2)[i] for i in range(3)}
        colR1.update({f'y{j}': (1, 0, 1)[j] for j in range(3)})
        bad = proper_and_banfree(adj, BAN, colR1)
        if ('ban', 'x2') in bad:
            res['R1_ban_fail'] += 1
        elif bad:
            res['R1_other'] += 1
        # --- R2 verbatim: cyclic sigma=tau, both cycles
        for cyc, ki, kn, ke in (((1, 2, 0), 'R2a_improper', 'R2a_noext', 'R2a_ext'),
                                ((2, 0, 1), 'R2b_improper', 'R2b_noext', 'R2b_ext')):
            colR2 = {f'x{i}': cyc[i] for i in range(3)}
            colR2.update({f'y{j}': cyc[j] for j in range(3)})
            bad = proper_and_banfree(adj, BAN, colR2)
            if bad:
                res[ki] += 1
            else:
                ext = search(adj, BAN, fixed=colR2)
                res[kn if ext == 0 else ke] += 1
        # --- ground truth
        if search(adj, BAN) > 0:
            res['truth_colourable'] += 1
    summary[typ] = res
    print(f"{label}: {res['n']} instances")
    print(f"   R1 (2,0,2)/(1,0,1): ban-violation at x2 in {res['R1_ban_fail']}/{res['n']}"
          f" (other failure: {res['R1_other']})")
    print(f"   R2 cyclic (1,2,0): improper-on-anchors {res['R2a_improper']},"
          f" proper-but-NO-extension {res['R2a_noext']}, extends {res['R2a_ext']}")
    print(f"   R2 cyclic (2,0,1): improper-on-anchors {res['R2b_improper']},"
          f" proper-but-NO-extension {res['R2b_noext']}, extends {res['R2b_ext']}")
    print(f"   ground truth: ban-avoiding colouring exists in"
          f" {res['truth_colourable']}/{res['n']} instances")

print('=' * 78)
print('PART 2: NON-extremal gammas on the same graph family;')
print('        skeleton steps (1)-(2) base+relocation recipe verbatim')
print('=' * 78)
tested = repaired = allkilled = 0
fails = []
for k in range(120):
    typ = rng.choice([1, 2, 3])
    inst = gen_instance(rng, typ, rng.choice([9, 10]))
    if inst is None:
        continue
    P, Q, adj = inst
    gam = {a: rng.randrange(3) for a in ANCH}
    # which ordered bases (p,q) survive? (killed iff exists edge x~y anchors,
    # gam[x]=p, gam[y]=q)
    killed = set()
    for x in ANCH_X:
        for y in ANCH_Y:
            if y in adj[x]:
                killed.add((gam[x], gam[y]))
    bases = [(p, q) for p in range(3) for q in range(3) if p != q and (p, q) not in killed]
    tested += 1
    if not bases:
        allkilled += 1
        continue
    p, q = bases[0]
    col = base_relocate(adj, P, gam, p, q)
    bad = proper_and_banfree(adj, gam, col)
    if bad:
        fails.append((typ, gam, (p, q), bad[:3]))
    else:
        repaired += 1
print(f"random-gamma instances tested: {tested}; all-6-bases-killed: {allkilled}; "
      f"base+relocate VERBATIM succeeded (proper + ban-avoiding, re-verified): {repaired}")
print(f"VERBATIM FAILURES of steps (1)-(2) recipe: {len(fails)}")
for f in fails[:10]:
    print('   FAIL:', f)
print('=' * 78)
print('PART 3: which random gammas kill all 6 bases? (should require rainbow'
      ' biclique labels; cross-check)')
cnt_killall = 0
for k in range(400):
    inst = gen_instance(rng, 1, 9)     # full K33 core => all label pairs adjacent
    if inst is None: continue
    P, Q, adj = inst
    gam = {a: rng.randrange(3) for a in ANCH}
    killed = {(gam[x], gam[y]) for x in ANCH_X for y in ANCH_Y if y in adj[x]}
    if all((p, q) in killed for p in range(3) for q in range(3) if p != q):
        cnt_killall += 1
        rainbowX = {gam[x] for x in ANCH_X} == {0, 1, 2}
        rainbowY = {gam[y] for y in ANCH_Y} == {0, 1, 2}
        assert rainbowX and rainbowY, (gam, 'all-killed without rainbow?!')
print(f"   T1 random gammas with ALL 6 bases killed: {cnt_killall}/400; "
      f"every such gamma was rainbow/rainbow (assert passed)")
