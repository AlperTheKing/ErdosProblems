r"""RCC PRIMAL/DUAL exact verifier (2026-07-08, Fable-5). Machine-checks BOTH certificate types of the
relaxed-cut-cover + bank LP (GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md Task 3) with exact Fractions:

  PRIMAL cert (cover lambda_U + flows q(c,j)):  coverage >= 1 per row; congestion <= 1 per support edge;
      routing sum_j q(c,j) >= load(c) per off-support edge; capacity sum_c q(c,j) <= kappa_j per sink.
  DUAL cert (alpha_e, beta_c, gamma_c, delta_j >= 0):  (D1) per-cut price domination over the DECLARED cut
      family; (D2) gamma_c <= delta_j for every allowed incidence I(c,j)=1; (D3) sum alpha > sum beta +
      sum kappa_j*delta_j.  A verified DUAL cert => the primal is INFEASIBLE for that config (Farkas).

Config JSON schema (abstract OR graph-derived; all rationals as "p/q" strings):
  { "n": int, "cut_edges": [[a,b],...], "rows": [[u,v],...],           # row = bad edge endpoints
    "F": [[a,b],...],                                                   # support cut edges
    "cuts": [[v,...],...] | "all",                                      # cut family (vertex subsets); "all" => 2^(n-1)
    "sinks": {"door": {"kappa": "p/q", "inc": "all"} , ...},            # incidence: "all" or explicit [[a,b],...]
    "primal": {"lambda": {"v1,v2,...": "p/q"}, "q": {"a,b|sink": "p/q"}},   # optional
    "dual":   {"alpha": {"u,v": "p/q"}, "beta": {"a,b": "p/q"},
               "gamma": {"a,b": "p/q"}, "delta": {"sink": "p/q"}} }      # optional
Run: python _claude_rcc_dual_verify.py config.json  (from problems/23/writeup)
"""
import json, sys
from fractions import Fraction
from itertools import combinations


def fr(x):
    return Fraction(x) if not isinstance(x, str) else Fraction(*[int(t) for t in x.split('/')]) if '/' in x else Fraction(int(x))


def ekey(e):
    return (min(e), max(e))


def sep(U, e):
    return (e[0] in U) != (e[1] in U)


def load_config(path):
    cfg = json.load(open(path))
    n = cfg['n']
    cut_edges = [ekey(e) for e in cfg['cut_edges']]
    rows = [tuple(e) for e in cfg['rows']]
    F = set(ekey(e) for e in cfg['F'])
    O = [c for c in cut_edges if c not in F]
    if cfg['cuts'] == 'all':
        cuts = []
        for r in range(1, n):
            for combo in combinations(range(1, n), r):
                cuts.append(frozenset(combo))
    else:
        cuts = [frozenset(U) for U in cfg['cuts']]
    sinks = {}
    for name, s in cfg.get('sinks', {}).items():
        inc = s.get('inc', 'all')
        incset = None if inc == 'all' else set(ekey(e) for e in inc)
        sinks[name] = dict(kappa=fr(s['kappa']), inc=incset)
    return cfg, n, cut_edges, rows, F, O, cuts, sinks


def verify_dual(rows, F, O, cuts, sinks, dual):
    alpha = {tuple(int(t) for t in k.split(',')): fr(v) for k, v in dual['alpha'].items()}
    beta = {ekey([int(t) for t in k.split(',')]): fr(v) for k, v in dual.get('beta', {}).items()}
    gamma = {ekey([int(t) for t in k.split(',')]): fr(v) for k, v in dual.get('gamma', {}).items()}
    delta = {k: fr(v) for k, v in dual.get('delta', {}).items()}
    ok = True
    if any(v < 0 for v in list(alpha.values()) + list(beta.values()) + list(gamma.values()) + list(delta.values())):
        print("  FAIL nonneg"); ok = False
    # (D1) over the declared family
    worst = None
    nfail = 0
    for U in cuts:
        lhs = sum(a for e, a in alpha.items() if sep(U, e))
        rhs = sum(b for c, b in beta.items() if c in F and sep(U, c)) + \
              sum(g for c, g in gamma.items() if c not in F and sep(U, c))
        if lhs > rhs:
            nfail += 1
            if nfail <= 5:
                print("  FAIL (D1) at U=%s: %s > %s" % (sorted(U), lhs, rhs))
            ok = False
        m = rhs - lhs
        worst = m if worst is None else min(worst, m)
    if nfail > 5:
        print("  ... (%d more D1 failures suppressed)" % (nfail - 5))
    # (D2)
    for c in O:
        g = gamma.get(c, Fraction(0))
        for name, s in sinks.items():
            allowed = (s['inc'] is None) or (c in s['inc'])
            if allowed and g > delta.get(name, Fraction(0)):
                print("  FAIL (D2) edge %s sink %s: gamma=%s > delta=%s" % (c, name, g, delta.get(name, Fraction(0)))); ok = False
    # (D3)
    lhs3 = sum(alpha.values())
    rhs3 = sum(beta.get(c, Fraction(0)) for c in F) + sum(s['kappa'] * delta.get(name, Fraction(0)) for name, s in sinks.items())
    strict = lhs3 > rhs3
    print("  (D1) min slack over %d cuts: %s | (D3): sum(alpha)=%s vs %s -> strict=%s" % (len(cuts), worst, lhs3, rhs3, strict))
    if not strict:
        print("  FAIL (D3) not strict"); ok = False
    return ok


def verify_primal(rows, F, O, cuts, sinks, primal):
    lam = {}
    for k, v in primal['lambda'].items():
        U = frozenset(int(t) for t in k.split(','))
        lam[U] = fr(v)
    qf = {}
    for k, v in primal.get('q', {}).items():
        epart, sink = k.split('|')
        c = ekey([int(t) for t in epart.split(',')])
        qf[(c, sink)] = fr(v)
    ok = True
    if any(v < 0 for v in list(lam.values()) + list(qf.values())):
        print("  FAIL nonneg"); ok = False
    for e in rows:
        cov = sum(w for U, w in lam.items() if sep(U, e))
        if cov < 1:
            print("  FAIL coverage row %s: %s" % (e, cov)); ok = False
    for c in F:
        cong = sum(w for U, w in lam.items() if sep(U, c))
        if cong > 1:
            print("  FAIL congestion %s: %s" % (c, cong)); ok = False
    for c in O:
        loadc = sum(w for U, w in lam.items() if sep(U, c))
        routed = sum(v for (cc, s), v in qf.items() if cc == c)
        if routed < loadc:
            print("  FAIL routing %s: routed %s < load %s" % (c, routed, loadc)); ok = False
    for name, s in sinks.items():
        used = sum(v for (cc, sk), v in qf.items() if sk == name)
        if used > s['kappa']:
            print("  FAIL capacity sink %s: %s > %s" % (name, used, s['kappa'])); ok = False
        for (cc, sk), v in qf.items():
            if sk == name and v > 0 and s['inc'] is not None and cc not in s['inc']:
                print("  FAIL incidence: edge %s may not spend sink %s" % (cc, name)); ok = False
    return ok


def main():
    path = sys.argv[1]
    cfg, n, cut_edges, rows, F, O, cuts, sinks = load_config(path)
    print("config: n=%d rows=%d |F|=%d |O|=%d cuts=%d sinks=%s" % (n, len(rows), len(F), len(O), len(cuts),
          {k: str(v['kappa']) for k, v in sinks.items()}))
    print("Hall defect |S|-|F| = %d" % (len(rows) - len(F)))
    if 'dual' in cfg:
        ok = verify_dual(rows, F, O, cuts, sinks, cfg['dual'])
        print("DUAL CERT: %s" % ("VERIFIED (primal INFEASIBLE, exact Farkas) -- decisive if config is cage-legal" if ok else "REJECTED"))
    if 'primal' in cfg:
        ok = verify_primal(rows, F, O, cuts, sinks, cfg['primal'])
        print("PRIMAL CERT: %s" % ("VERIFIED (cover+bank exact)" if ok else "REJECTED"))


if __name__ == '__main__':
    main()
