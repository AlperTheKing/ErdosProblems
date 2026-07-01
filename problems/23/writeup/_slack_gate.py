"""Verify Codex's TH-Corridor SLACK FORMULA characterization of witnessing (22:37):
For a completed terminal-shadow switch S, crossing bad edge f=(tau_f,sigma_f) with tau_f in S,
and exit e=(x_e,y_e) with x_e in S:
  D_f = ell(f)-1
  s_f(e) = d_{B[S]}(tau_f,x_e) + 1 + d_{B[V\\S]}(y_e,sigma_f) - D_f.
Claim: f witnesses e iff s_f(e)=0, and nonzero slack is >= 2 (by parity).
Cross-check s_f(e)==0 against MY witness_structure witness relation. EXACT. Battery census R<0 + H2x.
Run from problems/23/writeup."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure


def edge(u, v):
    return (u, v) if u < v else (v, u)


def bdist_within(adj, side, verts, s, t):
    """shortest path s->t using BLUE edges with both endpoints in `verts`."""
    if s not in verts or t not in verts:
        return -1
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in verts and side[u] != side[v] and v not in d:
                d[v] = d[u] + 1; q.append(v)
    return d.get(t, -1)


def check_switch(name, n, adj, side, st, Sset, acc):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    if not crossM or not bdyB:
        return
    witset = set(wit.keys())   # (f,e) pairs that actually witness
    Vall = set(range(n)); Out = Vall - Sset
    acc['switches'] += 1
    for f in crossM:
        a, b = f
        tau = a if a in Sset else b
        sig = b if a in Sset else a
        if tau not in Sset or sig in Sset:
            continue  # f must cross S
        Df = ell[f] - 1
        for e in bdyB:
            x, y = e
            xe = x if x in Sset else y
            ye = y if x in Sset else x
            if xe not in Sset or ye in Sset:
                continue
            d_in = bdist_within(adj, side, Sset, tau, xe)
            d_out = bdist_within(adj, side, Out, ye, sig)
            acc['pairs'] += 1
            actual_wit = (f, e) in witset
            if d_in < 0 or d_out < 0:
                # no restricted path; slack undefined. If actual witness, that's a mismatch.
                if actual_wit:
                    acc['nopath_but_wit'] += 1
                    if acc['ex'] is None:
                        acc['ex'] = (name, n, ''.join(map(str, side)), f, e, 'd_in=%d d_out=%d' % (d_in, d_out))
                continue
            s = d_in + 1 + d_out - Df
            slack0 = (s == 0)
            if slack0 != actual_wit:
                acc['mismatch'] += 1
                if acc['ex'] is None:
                    acc['ex'] = (name, n, ''.join(map(str, side)), f, e, 's=%d wit=%s' % (s, actual_wit))
            if s != 0:
                acc['nonzero'] += 1
                if s < 2:
                    acc['slack_lt2'] += 1
                    if acc['ex2'] is None:
                        acc['ex2'] = (name, n, ''.join(map(str, side)), f, e, 's=%d' % s)


def process(name, n, edges, acc, max_add=1):
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        g0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, g0, max_moat=max_add)
            if sm is None:
                continue
            seed, moat, _drop = sm
            check_switch(name, n, adj, side, st, set(seed) | set(moat), acc)


def main():
    acc = dict(switches=0, pairs=0, mismatch=0, nopath_but_wit=0, nonzero=0, slack_lt2=0, ex=None, ex2=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process('cen%d' % nn, n, E, acc)
        print('  census N=%d: switches=%d pairs=%d mismatch=%d' % (nn, acc['switches'], acc['pairs'], acc['mismatch']), flush=True)
    n, E = vertex_blowup(*dec('H?AFBo]'), 2); process('H2x', n, E, acc)
    print('=' * 60)
    print('switches:', acc['switches'], 'f-e pairs:', acc['pairs'])
    print('slack==0 vs witness MISMATCH:', acc['mismatch'], acc['ex'] or '')
    print('no restricted path but witnesses:', acc['nopath_but_wit'])
    print('nonzero slack:', acc['nonzero'], '| of which < 2 (parity violation):', acc['slack_lt2'], acc['ex2'] or '')
    ok = acc['mismatch'] == 0 and acc['nopath_but_wit'] == 0 and acc['slack_lt2'] == 0 and acc['pairs'] > 0
    print('VERDICT:', 'SLACK FORMULA VERIFIED: s_f(e)=0 <=> f witnesses e, nonzero slack >= 2'
          if ok else 'SLACK FORMULA FAILS')


if __name__ == '__main__':
    main()
