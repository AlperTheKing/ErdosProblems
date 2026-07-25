"""audit_G10_local.py -- INDEPENDENT audit of G10-3 / G10-4 / G10-5 and of the
"combined content" claim of round3/G10.md section 1.

Everything here is exact (Fraction).  Each cut c of H gives
    Q_c(x* + t d) = q0(c) + q1(c) t + q2(c) t^2
with q0 = sum_{mono} x*_u x*_v, q1 = sum_{mono} (x*_u d_v + x*_v d_u), q2 = sum_{mono} d_u d_v.
psi(x*+td) = min_c Q_c ; the one-sided derivative at t=0+ is min{ q1(c) : q0(c) = psi(x*) }.
That is computed here directly from a full enumeration of all 2^(n-1) cuts -- no closed
form, no active-set theory -- and then compared with the report's closed form
    F_i = d_i + d_{i+1} + D_i + D_{i-1},   derivative = (min_i F_i)/5.
"""
import sys, random
from fractions import Fraction
sys.path.insert(0, '.')
from audit_G10_lib import (C, petersen, wagner, disjoint, cut_mono, psi_frac,
                           adjlist, is_tf, odd_girth, hom_to_C5, bip_graph)


def cut_poly(mono, x, d):
    """[(q0,q1,q2)] for every cut."""
    out = []
    for mo in mono:
        q0 = sum(x[u] * x[v] for u, v in mo)
        q1 = sum(x[u] * d[v] + x[v] * d[u] for u, v in mo)
        q2 = sum(d[u] * d[v] for u, v in mo)
        out.append((q0, q1, q2))
    return out


def deriv_at(mono, x, d):
    """exact one-sided derivative of psi along d at x (min of q1 over active cuts)."""
    P = cut_poly(mono, x, d)
    m = min(p[0] for p in P)
    return m, min(p[1] for p in P if p[0] == m)


def closed_form_F(n, E, cyc, d):
    """the report's closed form, re-derived independently."""
    A = adjlist(n, E)
    pos = {v: k for k, v in enumerate(cyc)}
    D = [Fraction(0)] * 5
    low = Fraction(0)
    for w in range(n):
        if w in pos:
            continue
        Aw = sorted(pos[u] for u in cyc if u in A[w])
        if len(Aw) == 2:
            j = [k for k in range(5) if {k, (k + 2) % 5} == set(Aw)]
            assert len(j) == 1, (Aw,)          # independent pairs of C5 are diagonals
            D[j[0]] += d[w]
        elif len(Aw) <= 1:
            low += d[w]
        else:
            raise AssertionError('N(w) cap C5 not independent -> triangle')
    return [d[cyc[i]] + d[cyc[(i + 1) % 5]] + D[i] + D[(i - 1) % 5] for i in range(5)], low


def rand_host(n, rng):
    E = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
    A = adjlist(n, E)
    P = [(i, j) for i in range(n) for j in range(i + 1, n) if not (i < 5 and j < 5)]
    rng.shuffle(P)
    for i, j in P:
        if rng.random() < .5:
            continue
        if A[i] & A[j]:
            continue
        E.append((i, j)); A[i].add(j); A[j].add(i)
    return n, sorted(E)


def part1_G10_3_and_4(trials=120, seed=99):
    rng = random.Random(seed)
    bad_cf = bad_sum = bad_pos = bad_flat = flat = 0
    for t in range(trials):
        n = rng.randint(6, 10)
        n, E = rand_host(n, rng)
        assert is_tf(n, E)
        cyc = (0, 1, 2, 3, 4)
        d = [Fraction(0)] * n
        for w in range(5, n):
            d[w] = Fraction(rng.randint(0, 4))
        tot = sum(d[5:])
        pr = [Fraction(rng.randint(-6, 6)) for _ in range(4)]
        pr.append(-tot - sum(pr))
        for i in range(5):
            d[cyc[i]] = pr[i]
        assert sum(d) == 0
        mono = cut_mono(n, E)
        x = [Fraction(1, 5)] * 5 + [Fraction(0)] * (n - 5)
        p0, dv = deriv_at(mono, x, d)
        F, low = closed_form_F(n, E, cyc, d)
        if p0 != Fraction(1, 25):
            bad_cf += 1
        if dv != min(F) / 5:
            bad_cf += 1
            print('CLOSED FORM MISMATCH', n, E, d, F, dv)
        if sum(F) != -2 * low:
            bad_sum += 1
            print('SUM IDENTITY FAILS', n, E, d, F, low)
        if all(f > 0 for f in F):
            bad_pos += 1
        if all(f == 0 for f in F):
            flat += 1
            S = sorted(set(cyc) | {w for w in range(n) if d[w] > 0})
            idx = {v: i for i, v in enumerate(S)}
            Es = [(idx[u], idx[v]) for u, v in E if u in idx and v in idx]
            if not hom_to_C5(len(S), Es):
                bad_flat += 1
                print('FLAT FACE NOT C5-COLOURABLE', n, E, d, S)
    print('[G10-3/G10-4] trials=%d  closed-form mismatches=%d  sum-identity failures=%d  '
          'all-F-positive=%d  flat dirs=%d  flat-face-not-hom-C5=%d'
          % (trials, bad_cf, bad_sum, bad_pos, flat, bad_flat))
    return bad_cf + bad_sum + bad_pos + bad_flat


def part2_every_point_is_on_a_ray():
    """The admissibility condition of G10-3 is  sum d = 0  and  d_w >= 0 off the C5.
    For ANY y in the simplex, d = y - x* satisfies both.  So 'no admissible straight ray
    from x* beats 1/25' is literally 'max_y psi(H,y) <= 1/25' = the conjecture for H."""
    n, E = petersen()
    mono = cut_mono(n, E)
    cyc = (0, 1, 2, 3, 4)
    x = [Fraction(1, 5)] * 5 + [Fraction(0)] * 5
    rng = random.Random(5)
    worst = None
    for t in range(200):
        w = [Fraction(rng.randint(0, 20)) for _ in range(n)]
        s = sum(w)
        if s == 0:
            continue
        y = [wi / s for wi in w]
        d = [y[v] - x[v] for v in range(n)]
        assert sum(d) == 0 and all(d[v] >= 0 for v in range(5, n))
        v = psi_frac(mono, y)
        if worst is None or v > worst:
            worst = v
    print('[ray-cover] 200 random simplex points of Petersen, each = x*+1*d with d admissible; '
          'max psi over them = %s (%.8f)' % (worst, float(worst)))


def part3_falsifier_rays():
    print('--- FALSIFIER A: a ray from a C5 point whose value RETURNS to the maximum ---')
    n, E = petersen()
    mono = cut_mono(n, E)
    x = [Fraction(1, 5)] * 5 + [Fraction(0)] * 5      # outer C5
    y = [Fraction(0)] * 5 + [Fraction(1, 5)] * 5      # inner C5 (5..9 induce a C5)
    d = [y[v] - x[v] for v in range(n)]
    assert sum(d) == 0 and all(d[v] >= 0 for v in range(5, n)), 'admissible in the sense of G10-3'
    p0, dv = deriv_at(mono, x, d)
    print('  psi(x*) = %s ; exact one-sided derivative along d = %s (%s 0)'
          % (p0, dv, '<' if dv < 0 else '>='))
    for num, den in [(0, 1), (1, 10), (1, 4), (1, 2), (3, 4), (9, 10), (1, 1)]:
        t = Fraction(num, den)
        z = [x[v] + t * d[v] for v in range(n)]
        print('    t=%-5s psi = %-14s = %.8f' % (t, psi_frac(mono, z), float(psi_frac(mono, z))))
    print('  => strictly negative first-order derivative, yet the ray comes back to the '
          'global maximum 1/25 at t=1.  First-order data at t=0 says NOTHING about t>0.')

    print('--- FALSIFIER B: same two lemmas at a C_g point, conclusion FALSE ---')
    n, E = disjoint(C(7), C(5))          # 0..6 = C7, 7..11 = C5, triangle-free
    assert is_tf(n, E) and odd_girth(n, E) == 5
    mono = cut_mono(n, E)
    x = [Fraction(1, 7)] * 7 + [Fraction(0)] * 5
    y = [Fraction(0)] * 7 + [Fraction(1, 5)] * 5
    d = [y[v] - x[v] for v in range(n)]
    p0, dv = deriv_at(mono, x, d)
    print('  host C7 u C5, x* = C7-concentration: psi(x*) = %s, derivative along d = %s' % (p0, dv))
    #   the C7 analogue of G10-3 holds verbatim here: every vertex off the C7 has
    #   N(w) cap C7 = empty, so F_i = d_i + d_{i+1} and sum_i F_i = 2*sum_{C7} d = -2*sum_{C5} d <= 0
    F = [d[i] + d[(i + 1) % 7] for i in range(7)]
    print('  F = %s ;  sum F = %s = -2*sum_{outside} d = %s  (so x* is first-order stationary,'
          ' exactly as in G10-3)' % ([str(f) for f in F], sum(F), -2 * sum(d[7:])))
    for num, den in [(0, 1), (1, 4), (1, 2), (3, 4), (1, 1)]:
        t = Fraction(num, den)
        z = [x[v] + t * d[v] for v in range(n)]
        print('    t=%-5s psi = %-16s = %.8f' % (t, psi_frac(mono, z), float(psi_frac(mono, z))))
    print('  => derivative -2/49 < 0 at t=0 and psi(t=1) = 1/25 > 1/49 = psi(x*).')
    print('  The inference "negative first-order derivative => the ray never beats psi(x*)"'
          ' is therefore FALSE.')


def part4_avgblock():
    print('--- G10-5 numbers ---')
    dv = (309, -809, -809, 309, 1000)
    s = sum(dv[i] * dv[(i + 1) % 5] for i in range(5))
    print('  sum d = %d ; sum_i d_i d_{i+1} = %d' % (sum(dv), s))
    n, E = C(5)
    mono = cut_mono(n, E)
    x = [Fraction(1, 5)] * 5
    d = [Fraction(z) for z in dv]
    # lambda = uniform over the 5 active cuts of C5 (mu_i = 1/5), computed independently
    P = lambda z: [sum(z[u] * z[v] for u, v in mo) for mo in mono]
    act = [k for k, mo in enumerate(mono) if sum(x[u] * x[v] for u, v in mo) == Fraction(1, 25)]
    lam = Fraction(1, len(act))
    for tden in (100000,):
        t = Fraction(1, tden)
        z = [x[i] + t * d[i] for i in range(5)]
        f = sum(lam * q for k, q in enumerate(P(z)) if k in act)
        print('  |active cuts| = %d ; f(x*+td) at t=1/%d : %s = %.12f  > 1/25 ? %s'
              % (len(act), tden, f, float(f), f > Fraction(1, 25)))
        print('  closed form 1/25 + (772519/5) t^2 = %s   matches: %s'
              % (Fraction(1, 25) + Fraction(772519, 5) * t * t,
                 f == Fraction(1, 25) + Fraction(772519, 5) * t * t))
        print('  psi at the same point = %s = %.12f  (<= 1/25 : %s)'
              % (psi_frac(mono, z), float(psi_frac(mono, z)), psi_frac(mono, z) <= Fraction(1, 25)))


def part5_hagg_witness():
    """Grotzsch, a = (k,k,k,k,k) on the C5, 1 on the apex, 0 on the copies."""
    n = 11
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(i, 5 + ((i + 1) % 5)), (i, 5 + ((i - 1) % 5))]
    E += [(5 + i, 10) for i in range(5)]
    E = sorted((min(u, v), max(u, v)) for u, v in E)
    assert is_tf(n, E), 'Grotzsch must be triangle-free'
    A = adjlist(n, E)
    mono = cut_mono(n, E)
    for k in (1, 3, 9, 20):
        a = [k] * 5 + [0] * 5 + [1]
        q = sum(a)
        F = min(sum(a[u] * a[v] for u, v in mo) for mo in mono)
        wdeg = min(sum(a[u] for u in A[v]) for v in range(n) if a[v] > 0)
        print('  k=%-3d q=%-4d bip=%-6d = k^2 ? %s ; min weighted degree over support = %d '
              '(<= 3q/8 = %.1f : %s) ; 25*bip - q^2 = %d'
              % (k, q, F, F == k * k, wdeg, 3 * q / 8, wdeg <= 3 * q / 8, 25 * F - q * q))


if __name__ == '__main__':
    bad = part1_G10_3_and_4(trials=int(sys.argv[1]) if len(sys.argv) > 1 else 120)
    print()
    part2_every_point_is_on_a_ray()
    print()
    part3_falsifier_rays()
    print()
    part4_avgblock()
    print()
    print('--- Haggkvist witness (report section 2) ---')
    part5_hagg_witness()
    print()
    print('TOTAL G10-3/G10-4 FAILURES:', bad)
