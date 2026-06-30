"""Confirm H?AFBo] blowups (t=2,3, fixed base side) R<0 sites obey the L=Lmax selector + strict-mix."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _csmspec import build_K2


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def Lset(v, M, ell, cyc):
    s = set()
    for f in M:
        for Q in cyc[f]:
            if v in Q:
                s.add(ell[f]); break
    return s


def bd(adj, side, S):
    dB = dM = 0
    for u in S:
        for w in adj[u]:
            if w in S:
                continue
            if side[u] != side[w]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def bundleL(v, M, ell, cyc, L):
    rows = []
    for f in M:
        if ell[f] != L:
            continue
        for Q in cyc[f]:
            if v in Q:
                rows.append(list(Q))
    out = []
    for o in (0, 1):
        pref = set(); suff = set()
        for Q in rows:
            q = Q if o == 0 else Q[::-1]; i = q.index(v)
            pref.update(q[:i + 1]); suff.update(q[i:])
        out.append(frozenset(pref)); out.append(frozenset(suff))
    return out


hN, hE = dec('H?AFBo]'); base = [int(c) for c in '111110000']
tot = 0; lmax_ok = 0; mixed = 0
for t in (2, 3):
    nn, EE = vertex_blowup(hN, hE, t)
    side = [base[v // t] for v in range(nn)]
    adj = [set() for _ in range(nn)]
    for x, y in EE:
        adj[x].add(y); adj[y].add(x)
    if not Bconn(nn, adj, side):
        continue
    st = struct_for_side(nn, adj, side)
    if st is None:
        continue
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        continue
    N = F(nn); K2 = build_K2(nn, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(nn)) for v in range(nn)]
    neg = [v for v in range(nn) if R[v] < 0]
    g0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        tot += 1; Ls = Lset(v, M, ell, cyc); Lmn = min(Ls); Lmx = max(Ls)
        if Lmx > Lmn:
            mixed += 1
        ok = False
        for S in bundleL(v, M, ell, cyc, Lmx):
            if v not in S or len(S) == 0 or len(S) == nn:
                continue
            if bd(adj, side, S) != 0:
                continue
            s2 = side[:]
            for u in S:
                s2[u] ^= 1
            g2 = gamma_of(nn, adj, s2)
            if g2 is not None and g2 < g0:
                ok = True; break
        if ok:
            lmax_ok += 1
    print('t=%d nn=%d: R<0 sites=%d' % (t, nn, len(neg)))
print('H-blowups: total R<0=%d mixed=%d Lmax_ok=%d' % (tot, mixed, lmax_ok))
print('VERDICT:', 'L=Lmax + strict-mix HOLD on H-blowups' if (mixed == tot and lmax_ok == tot) else 'FAIL')
