"""Probe sub-lemmas for the fan-averaging var ineq.  (★): ell*<S^2> + ell*<S>(n-<S>) <= n^2.
Candidate sub-lemmas to falsify on the standing gate:
  (L1)  S(v) <= n/5  pointwise on f's support?
  (STRONG) ell*<S>*(Smax+n-<S>) <= n^2   (sufficient since <S^2><=Smax*<S>)
Exact Fraction; battery = census<=11 + Myc + blowups.
"""
from fractions import Fraction as F
from _wf_var_0 import build, iter_battery


if __name__ == "__main__":
    print("=== probe sub-lemmas ===", flush=True)
    nrows = 0
    L1_fail = 0; L1_worst = None
    Smax_le_n = 0
    strong_fail = 0; strong_worst = None
    smean_worst = None
    for nm, n, adj, s in iter_battery():
        b = build(n, adj, s)
        if b is None:
            continue
        M, ell, T, mu, cyc, S, pf = b
        for f in M:
            if len(cyc[f]) < 2:
                continue
            d = pf[f]; ll = sum(d.values())
            smean = sum(d[v] * S[v] for v in d) / ll
            Smax = max(S[v] for v in d)
            nrows += 1
            for v in d:
                if S[v] > F(n, 5):
                    L1_fail += 1
                    exc = S[v] - F(n, 5)
                    if L1_worst is None or exc > L1_worst[0]:
                        L1_worst = (exc, nm, f, v, str(S[v]), n)
                    break
            if Smax <= n:
                Smax_le_n += 1
            lhs = ll * smean * (Smax + F(n) - smean)
            slack = F(n) ** 2 - lhs
            if slack < 0:
                strong_fail += 1
                if strong_worst is None or slack < strong_worst[0]:
                    strong_worst = (slack, nm, f, n, str(smean), str(Smax), str(ll))
            r = smean / F(n, 5)
            if smean_worst is None or r > smean_worst[0]:
                smean_worst = (r, nm, f, n)
    print("nonunique rows:", nrows)
    print(f"L1 (S(v)<=n/5) fails: {L1_fail}  worst-excess: {L1_worst}")
    print(f"Smax<=n count: {Smax_le_n}/{nrows}")
    print(f"STRONG ell*<S>*(Smax+n-<S>)<=n^2 fails: {strong_fail}  worst: {strong_worst}")
    print(f"max <S>/(n/5): {float(smean_worst[0]):.4f} at {smean_worst[1:]}")
