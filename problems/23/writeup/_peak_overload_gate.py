"""EXACT gate for the user's PEAK TERMINAL-OVERLOAD lemma (second message).

Row atoms a=(f,Q), mu_a=1/|cyc[f]|, L_a=ell[f], V_a=V(Q).  For v=q_i in Q: I^-={q_0..q_i}, I^+={q_i..q_{L-1}}.
  omega^v_{L,e}(x) = sum_{a:L_a=L,v in V_a} mu_a 1_{x in I^e};  m_L(v)=sum mu_a.
  Omega_{L,e}(v) = sum_x omega(x)(T(x)-N) - (m_L/2)(T(v)-N).
  COAREA (3): D(v) = sum_L (Omega_{L,-}+Omega_{L,+}) = -R[v].   [verify]
  PEAK (4): (L*,e*) = argmax_{m_L>0} Omega_{L,e}(v)/(L*m_L(v)).   S* = {x: omega^v_{L*,e*}(x)>0}.
  LEMMA (6)+(7): S* neutral (delta_B=delta_M), B-connected after, terminal-shadow safe, Psi(S*)>0
                 (equivalently Gamma(after)<Gamma(before)).
Gate: for each R[v]<0, build the peak bundle S*, check it is a valid neutral Gamma-decreasing descent. Report first
failure (peak bundle BAD). Exact Fraction.  Special-cases H?AFBo] v=6 (expected refutation).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import gamma_of, boundary_delta, flip


def peak_bundle(n, side, st, v, T, N):
    """Return (Omega by (L,e)), coarea_sum, peak (L*,e*,score), bundle S*."""
    M, ell, T2, mu, cyc = st
    # rows through v, grouped by length
    # omega^v_{L,e}: dict (L,e)-> {x: weight}; m_L: dict L->weight
    omega = {}   # (L,e) -> dict x->Fraction
    mL = {}
    for f in M:
        L = ell[f]; k = len(cyc[f]); w = F(1, k)
        for Q in cyc[f]:
            Q = list(Q)
            if v not in Q:
                continue
            i = Q.index(v)
            Iminus = Q[:i + 1]
            Iplus = Q[i:]
            mL[L] = mL.get(L, F(0)) + w
            for (e, I) in (('-', Iminus), ('+', Iplus)):
                d = omega.setdefault((L, e), {})
                for x in I:
                    d[x] = d.get(x, F(0)) + w
    # Omega_{L,e}(v)
    Om = {}
    for (L, e), d in omega.items():
        s = sum(d[x] * (T[x] - N) for x in d)
        Om[(L, e)] = s - (mL[L] / 2) * (T[v] - N)
    coarea = sum(Om.values())
    # peak by score Omega/(L*m_L)
    best = None
    for (L, e), val in Om.items():
        if mL[L] <= 0:
            continue
        score = val / (L * mL[L])
        if best is None or score > best[0]:
            best = (score, L, e)
    if best is None:
        return Om, coarea, None, None
    score, Lst, est = best
    Sstar = frozenset(x for x in omega[(Lst, est)] if omega[(Lst, est)][x] > 0)
    return Om, coarea, (Lst, est, score), Sstar


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in range(n):
        if R[v] >= 0:
            continue
        acc['neg'] += 1
        Om, coarea, peak, Sstar = peak_bundle(n, side, st, v, T, N)
        # verify coarea (3): coarea == -R[v]
        if coarea != -R[v]:
            acc['coarea_fail'] += 1
            if acc['cx'] is None:
                acc['cx'] = (name, n, v, str(coarea), str(-R[v]))
        if peak is None or Sstar is None or len(Sstar) == 0 or len(Sstar) == n:
            acc['peak_bad'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), v, 'no-valid-peak')
            continue
        # check peak bundle S* is neutral + B-conn-after + Gamma-decreasing
        neutral = boundary_delta(n, adj, side, Sstar) == 0
        g2 = gamma_of(n, adj, flip(side, Sstar))
        good = neutral and (g2 is not None) and (g2 < gamma0)
        if good:
            acc['peak_good'] += 1
        else:
            acc['peak_bad'] += 1
            if acc['ex'] is None:
                Lst, est, score = peak
                acc['ex'] = (name, n, ''.join(map(str, side)), v, 'peak(L=%d,%s) S*=%s neutral=%s g2=%s gamma0=%d' % (Lst, est, sorted(Sstar), neutral, g2, gamma0))


def process(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def main():
    acc = dict(neg=0, peak_good=0, peak_bad=0, coarea_fail=0, ex=None, cx=None)
    # focused: H?AFBo] first (expect v=6 refutation)
    n, E = dec("H?AFBo]"); process("H?AFBo]", n, E, acc)
    print("H?AFBo]: neg=%d peak_good=%d peak_bad=%d coarea_fail=%d %s" % (acc['neg'], acc['peak_good'], acc['peak_bad'], acc['coarea_fail'], acc['ex'] or ''), flush=True)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            nn2, E2 = dec(g6); process("cen%d" % nn, nn2, E2, acc)
        print("after census N=%d: neg=%d peak_good=%d peak_bad=%d coarea_fail=%d" % (nn, acc['neg'], acc['peak_good'], acc['peak_bad'], acc['coarea_fail']), flush=True)
    print("=" * 55)
    print("R<0 vertices:", acc['neg'], " peak bundle GOOD:", acc['peak_good'], " peak bundle BAD:", acc['peak_bad'])
    print("coarea (3) failures:", acc['coarea_fail'], acc['cx'] or '')
    print("first peak-BAD:", acc['ex'] or 'NONE')
    print("VERDICT:", "PEAK TERMINAL-OVERLOAD LEMMA HOLDS (peak bundle always good)" if acc['peak_bad'] == 0
          else "PEAK LEMMA REFUTED -- the peak normalized-overload bundle is NOT always a valid descent")


if __name__ == "__main__":
    main()
