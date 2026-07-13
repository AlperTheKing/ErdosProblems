#!/usr/bin/env python3
"""VERIFIER (adversarial) -- independent replay of the R46 18-vtx near-candidate
claims in farkas_dual Findings 4 and 5. Built from the R46 sec 8 text only.

  W1  fixture sanity: 24 blue edges, bipartite L|R, connected, the 25 listed atoms
      = EXACTLY the same-shore blue-distance-4 pairs (forced), atom-graph triangles
      = 30 = 10 (K5 on b) + 10 (v,bi,bj) + 10 (m,bi,bj), full graph triangle-free.
  W2  circuit: F_a = union of length-4 blue path edges; |F*| = 24; every edge
      multiplicity >= 2; max SDR = 24 (deficiency exactly 1); all 25 deletion-SDRs.
  W3  profile (existence level, both owners): Forced=Inc (every non-incident atom
      has an owner-avoiding row); every star pair {x4,xi} i<=3 covered by an
      owner-avoiding row; a full 25-row tuple realizing r(owner)=5 with owner-x4
      unselected and owner-x0..x3 selected exists (backtracking search).
  W4  kappa sweep vs FULL F* (gray code over 2^18): max kappa = 12; the set
      {b0,b1,b2,x4} attains it; list all argmaxes up to complement;
      kappa({b0..b4}) = 5.
  W5  singleSafe (R47 def: cross-shore non-blue pair, no common neighbour in
      blue+bad, and for every atom min-orientation d(s,u)+1+d(w,t) > 4 with blue
      distances): count of safe pairs among the 56 candidates (claim 0), plus the
      kill-reason decomposition (triangle vs distance).
  W6  ablations with the SHRUNKEN support semantics (support = union of the kept
      atoms' rows): full 25 -> ?, drop coverage (20) -> ?, drop b-clique (15) -> ?,
      owner stars only (10) -> ?; claims 12 / 9 / 11 / 6; check the double-star
      switch formula kappa = 2t - outward at S={v,m,interior}.
Pure integers, own code.
"""
from itertools import combinations

Lnames = ['v', 'm', 'a'] + ['b%d' % j for j in range(5)]
Rnames = ['x%d' % i for i in range(5)] + ['y%d' % j for j in range(5)]
names = Lnames + Rnames
I = {s: k for k, s in enumerate(names)}
N = 18
LS = frozenset(I[s] for s in Lnames)

BLUE = set()
for i in range(5):
    BLUE.add(frozenset((I['v'], I['x%d' % i])))
    BLUE.add(frozenset((I['m'], I['x%d' % i])))
for i in range(4):
    BLUE.add(frozenset((I['a'], I['x%d' % i])))
for j in range(5):
    BLUE.add(frozenset((I['a'], I['y%d' % j])))
    BLUE.add(frozenset((I['b%d' % j], I['y%d' % j])))
BLUE = frozenset(BLUE)
assert len(BLUE) == 24

ATOMS = []
for j in range(5):
    ATOMS.append(frozenset((I['v'], I['b%d' % j])))
for j in range(5):
    ATOMS.append(frozenset((I['m'], I['b%d' % j])))
for i, j in combinations(range(5), 2):
    ATOMS.append(frozenset((I['b%d' % i], I['b%d' % j])))
for j in range(5):
    ATOMS.append(frozenset((I['x4'], I['y%d' % j])))
assert len(ATOMS) == 25
ASET = frozenset(ATOMS)

ab = [set() for _ in range(N)]   # blue adjacency
for e in BLUE:
    u, w = tuple(e); ab[u].add(w); ab[w].add(u)
aall = [set(ab[u]) for u in range(N)]
for e in ASET:
    u, w = tuple(e); aall[u].add(w); aall[w].add(u)

def bfs(src):
    d = [None] * N; d[src] = 0; fr = [src]
    while fr:
        nx = []
        for u in fr:
            for w in ab[u]:
                if d[w] is None:
                    d[w] = d[u] + 1; nx.append(w)
        fr = nx
    return d

D = [bfs(u) for u in range(N)]
assert all(D[0][u] is not None for u in range(N)), "disconnected"

# ---------- W1 ----------
for e in BLUE:
    u, w = tuple(e); assert (u in LS) != (w in LS)
for e in ASET:
    u, w = tuple(e); assert (u in LS) == (w in LS)
forced = {frozenset((u, w)) for u, w in combinations(range(N), 2)
          if ((u in LS) == (w in LS)) and D[u][w] == 4}
assert forced == ASET, ("available distance-4 set differs", len(forced))
tri_atom = sum(1 for u, w, z in combinations(range(N), 3)
               if frozenset((u, w)) in ASET and frozenset((u, z)) in ASET
               and frozenset((w, z)) in ASET)
assert tri_atom == 30, tri_atom
bset = [I['b%d' % j] for j in range(5)]
t_b = sum(1 for c in combinations(bset, 3))
t_v = sum(1 for i, j in combinations(bset, 2))
assert t_b == 10 and t_v == 10
tri_full = sum(1 for u in range(N) for w in aall[u] if w > u
               for z in (aall[u] & aall[w]) if z > w)
assert tri_full == tri_atom, "full graph has non-atom triangles"
print("W1 PASS: atoms forced (25 = all same-shore d4 pairs); atom triangles = 30 (10+10+10)")

# ---------- W2 ----------
def rows_of(at):
    s, t = sorted(at)
    res = []
    for n1 in ab[s]:
        for n2 in ab[n1]:
            if n2 == s:
                continue
            for n3 in ab[n2]:
                if n3 in (s, n1):
                    continue
                if t in ab[n3] and t not in (s, n1, n2):
                    res.append((s, n1, n2, n3, t))
    return res

ROWS = {at: rows_of(at) for at in ATOMS}
F = {at: {frozenset((r[k], r[k + 1])) for r in ROWS[at] for k in range(4)}
     for at in ATOMS}
Fstar = set()
for at in ATOMS:
    assert ROWS[at], at
    Fstar |= F[at]
assert Fstar == set(BLUE), (len(Fstar))
mult = {e: sum(1 for at in ATOMS if e in F[at]) for e in BLUE}
assert min(mult.values()) >= 2, min(mult.values())

EIDX = {e: k for k, e in enumerate(sorted(BLUE, key=lambda e: sorted(e)))}

def sdr_size(atom_list):
    matched = {}          # edge index -> atom position
    def try_row(pos, seen):
        for e in F[atom_list[pos]]:
            ei = EIDX[e]
            if ei in seen:
                continue
            seen.add(ei)
            if ei not in matched or try_row(matched[ei], seen):
                matched[ei] = pos
                return True
        return False
    got = 0
    for pos in range(len(atom_list)):
        if try_row(pos, set()):
            got += 1
    return got

assert sdr_size(ATOMS) == 24
for at in ATOMS:
    assert sdr_size([o for o in ATOMS if o != at]) == 24, at
print("W2 PASS: |F*|=24, min multiplicity=%d>=2, max SDR=24 (deficiency 1), 25/25 deletion-SDRs"
      % min(mult.values()))

# ---------- W3 ----------
def profile_exists(owner, other):
    ow = I[owner]
    x4 = I['x4']
    # Forced = Inc
    for at in ATOMS:
        if ow in at:
            continue
        assert any(ow not in r for r in ROWS[at]), ("Forced != Inc", at)
    # coverage existence
    for i in range(4):
        xi = I['x%d' % i]
        ok = any(ow not in r and x4 in r and xi in r
                 for at in ATOMS if ow not in at for r in ROWS[at])
        assert ok, ("pair uncovered", owner, i)
    # explicit tuple: greedy with backtracking
    order = list(ATOMS)
    choice = {}
    def feasible(at, r):
        if ow in at:
            return True                      # incident rows always contain ow
        return ow not in r                   # keep r(ow) = 5 exactly
    def bt(k, seluse):
        if k == len(order):
            return True
        at = order[k]
        for r in ROWS[at]:
            if not feasible(at, r):
                continue
            choice[at] = r
            if bt(k + 1, None):
                return True
            del choice[at]
        return False
    assert bt(0, None), "no r(owner)=5 tuple"
    sup = {frozenset((r[k], r[k + 1])) for r in choice.values() for k in range(4)}
    # need owner-x4 unselected + owner-x0..3 selected + coverage within the tuple
    def tuple_ok(ch):
        s2 = {frozenset((r[k], r[k + 1])) for r in ch.values() for k in range(4)}
        if frozenset((ow, x4)) in s2:
            return False
        if any(frozenset((ow, I['x%d' % i])) not in s2 for i in range(4)):
            return False
        for i in range(4):
            xi = I['x%d' % i]
            if not any(ow not in r and x4 in r and xi in r for r in ch.values()):
                return False
        return True
    # search again with the full predicate (small space, prune by owner rows first)
    choice.clear()
    def bt2(k):
        if k == len(order):
            return tuple_ok(choice)
        at = order[k]
        for r in ROWS[at]:
            if ow in at:
                pass
            elif ow in r:
                continue
            choice[at] = r
            if bt2(k + 1):
                return True
            del choice[at]
        return False
    got = bt2(0)
    return got

assert profile_exists('v', 'm')
assert profile_exists('m', 'v')
print("W3 PASS: Forced=Inc, all 4 star pairs coverable, explicit r=5 tuple with active"
      " edge unselected exists at BOTH owners")

# ---------- gray-code sweep ----------
def sweep(atom_list, blue_list, want_all_argmax=False):
    """max over all 2^N subsets of  |atoms cap delta| - |blue cap delta| (gray code)"""
    inc_a = [[] for _ in range(N)]
    inc_b = [[] for _ in range(N)]
    for k, e in enumerate(atom_list):
        u, w = tuple(e); inc_a[u].append(k); inc_a[w].append(k)
    for k, e in enumerate(blue_list):
        u, w = tuple(e); inc_b[u].append(k); inc_b[w].append(k)
    across = [0] * len(atom_list)
    bcross = [0] * len(blue_list)
    side = [0] * N
    ka = 0; kb = 0
    best = 0; arg = [0]
    mask = 0
    for g in range(1, 1 << N):
        u = (g & -g).bit_length() - 1
        side[u] ^= 1
        mask ^= (1 << u)
        for k in inc_a[u]:
            e = atom_list[k]; a0, a1 = tuple(e)
            new = side[a0] ^ side[a1]
            ka += 1 if new else -1
            across[k] = new
        for k in inc_b[u]:
            e = blue_list[k]; a0, a1 = tuple(e)
            new = side[a0] ^ side[a1]
            kb += 1 if new else -1
            bcross[k] = new
        val = ka - kb
        if val > best:
            best = val; arg = [mask]
        elif val == best and want_all_argmax and len(arg) < 64:
            arg.append(mask)
    return best, arg

AL = sorted(ASET, key=lambda e: sorted(e))
BL = sorted(BLUE, key=lambda e: sorted(e))

def kappa_at(S, atom_list, blue_list):
    ms = 0
    for u in S:
        ms |= 1 << u
    ka = sum(1 for e in atom_list for u, w in [tuple(e)] if ((ms >> u) ^ (ms >> w)) & 1)
    kb = sum(1 for e in blue_list for u, w in [tuple(e)] if ((ms >> u) ^ (ms >> w)) & 1)
    return ka - kb

# ---------- W4 ----------
best, args = sweep(AL, BL, want_all_argmax=True)
Sstar = [I['b0'], I['b1'], I['b2'], I['x4']]
kS = kappa_at(Sstar, AL, BL)
kb5 = kappa_at([I['b%d' % j] for j in range(5)], AL, BL)
canon = set()
for mk in args:
    canon.add(min(mk, ((1 << N) - 1) ^ mk))
pretty = [sorted(names[u] for u in range(N) if (mk >> u) & 1) for mk in sorted(canon)]
print("W4: max kappa = %d ; argmax count (up to complement) = %d : %s" % (best, len(canon), pretty))
print("W4: kappa({b0,b1,b2,x4}) = %d ; kappa({b0..b4}) = %d" % (kS, kb5))
assert best == 12 and kS == 12 and kb5 == 5

# ---------- W5 ----------
safe = []
kill_tri_only = kill_dist_only = kill_both = 0
for u in sorted(LS):
    for w in sorted(set(range(N)) - LS):
        e = frozenset((u, w))
        if e in BLUE:
            continue
        tri = bool(aall[u] & aall[w])
        distkill = False
        for at in ATOMS:
            s, t = tuple(at)
            if min(D[s][u] + 1 + D[w][t], D[s][w] + 1 + D[u][t]) <= 4:
                distkill = True
                break
        if tri and distkill:
            kill_both += 1
        elif tri:
            kill_tri_only += 1
        elif distkill:
            kill_dist_only += 1
        else:
            safe.append((names[u], names[w]))
tot = 8 * 10 - 24
print("W5: candidates %d ; singleSafe = %d ; kills: tri-only %d, dist-only %d, both %d"
      % (tot, len(safe), kill_tri_only, kill_dist_only, kill_both))
assert kill_tri_only + kill_dist_only + kill_both + len(safe) == tot
assert len(safe) == 0, safe

# ---------- W6 ----------
def ablate(tag, keep):
    sup = set()
    for at in keep:
        sup |= F[at]
    al = sorted(keep, key=lambda e: sorted(e))
    bl = sorted(sup, key=lambda e: sorted(e))
    best2, args2 = sweep(al, bl, want_all_argmax=True)
    canon2 = set()
    for mk in args2:
        canon2.add(min(mk, ((1 << N) - 1) ^ mk))
    ex = [sorted(names[u] for u in range(N) if (mk >> u) & 1) for mk in sorted(canon2)][:4]
    print("W6 %-28s atoms=%2d |sup|=%2d max kappa=%2d argmaxes(<=4 shown)=%s"
          % (tag, len(keep), len(sup), best2, ex))
    return best2, sup, al, bl

owner_atoms = [at for at in ATOMS if I['v'] in at or I['m'] in at]
clique = [at for at in ATOMS if len(at & set(bset)) == 2]
cover = [at for at in ATOMS if I['x4'] in at]
assert len(owner_atoms) == 10 and len(clique) == 10 and len(cover) == 5

b_full, _, _, _ = ablate("FULL (25)", ATOMS)
b_nocov, _, _, _ = ablate("drop coverage (20)", owner_atoms + clique)
b_noclq, _, _, _ = ablate("drop b-clique (15)", owner_atoms + cover)
b_stars, sup_st, al_st, bl_st = ablate("owner stars only (10)", owner_atoms)
assert (b_full, b_nocov, b_noclq, b_stars) == (12, 9, 11, 6), (b_full, b_nocov, b_noclq, b_stars)
# double-star switch formula on the stars-only system
Sd1 = [I['v'], I['m']] + [I['x%d' % i] for i in range(4)]
Sd2 = [I['v'], I['m']] + [I['x%d' % i] for i in range(5)]
k1 = kappa_at(Sd1, al_st, bl_st)
k2 = kappa_at(Sd2, al_st, bl_st)
outward = sum(1 for e in sup_st for u, w in [tuple(e)]
              if (u in set(Sd2)) != (w in set(Sd2)))
print("W6 stars-only: kappa({v,m,x0..x3}) = %d ; kappa({v,m,x0..x4}) = %d ;"
      " outward support degree of {v,m,x0..x4} = %d ; 2t - outward = %d"
      % (k1, k2, outward, 10 - outward))
print("DONE v_near18")
