"""Audit the ONE enumeration restriction used by fam2_census.py:

    c(nu; lam, mu) != 0  =>  lam subset nu  and  mu subset nu.

We do it two ways.
(1) UNRESTRICTED exhaustive census for |nu| <= NSMALL: enumerate EVERY pair
    (lam, mu) of partitions with at most 5 parts and |lam|+|mu|=|nu|, run the
    full LP-free screen on those that violate containment, and assert the
    status is EMPTY (all of P(1..D+2) zero -- so also no saturation anomaly).
(2) Random sample of violating triples at larger |nu|, same assertion.
"""
import sys, os, random, json
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0")
from fam2_enum import parts_exact5
import tier0_screen as T


def parts_atmost5(N):
    out = []
    def rec(rem, k, mx, cur):
        if rem == 0:
            out.append(tuple(cur)); return
        if k == 0:
            return
        for p in range(min(mx, rem), 0, -1):
            if p * k < rem: break
            rec(rem - p, k - 1, p, cur + [p])
    rec(N, 5, N, [])
    return out


def contained(lam, nu):
    return all(lam[i] <= nu[i] for i in range(len(lam))) if len(lam) <= len(nu) else False


def gather(nmax, nmin=5):
    viol = []
    for N in range(nmin, nmax + 1):
        pa = {a: parts_atmost5(a) for a in range(0, N + 1)}
        pa[0] = [()]
        for nu in parts_exact5(N):
            for a in range(0, N + 1):
                for lam in pa[a]:
                    for mu in pa[N - a]:
                        if not (contained(lam, nu) and contained(mu, nu)):
                            viol.append((lam, mu, nu))
    return viol


def check(viol, tag, cap_n=200000):
    random.seed(20260722)
    if len(viol) > cap_n:
        viol = random.sample(viol, cap_n)
    bad = []
    st = Counter()
    for i in range(0, len(viol), 3000):
        block = [(list(l), list(m), list(v)) for (l, m, v) in viol[i:i + 3000]]
        for r in T.screen_triples(block):
            st[r["status"]] += 1
            if r["status"] != "EMPTY":
                bad.append(r)
    print("%s: %d violating triples screened, statuses=%s, NON-EMPTY=%d"
          % (tag, sum(st.values()), dict(st), len(bad)))
    return bad, st


if __name__ == "__main__":
    NSMALL = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    v = gather(NSMALL)
    print("unrestricted census |nu|<=%d : %d containment-violating triples" % (NSMALL, len(v)))
    bad1, st1 = check(v, "exhaustive |nu|<=%d" % NSMALL)

    # (2) random violating triples at larger |nu|
    random.seed(4242)
    big = []
    for N in (18, 22, 26):
        nus = parts_exact5(N)
        pa = {a: parts_atmost5(a) for a in range(0, N + 1)}
        pa[0] = [()]
        tries = 0
        got = 0
        while got < 20000 and tries < 400000:
            tries += 1
            nu = random.choice(nus)
            a = random.randrange(0, N + 1)
            if not pa[a] or not pa[N - a]:
                continue
            lam = random.choice(pa[a]); mu = random.choice(pa[N - a])
            if contained(lam, nu) and contained(mu, nu):
                continue
            big.append((lam, mu, nu)); got += 1
    bad2, st2 = check(big, "random |nu| in {18,22,26}")
    out = {"exhaustive_nmax": NSMALL, "exhaustive_violating": len(v),
           "exhaustive_status": {str(k): x for k, x in st1.items()},
           "exhaustive_nonempty": len(bad1),
           "random_status": {str(k): x for k, x in st2.items()},
           "random_nonempty": len(bad2),
           "counterexamples": (bad1 + bad2)[:20]}
    json.dump(out, open(os.path.join(HERE, "containment_audit.json"), "w"), indent=1)
    print("VERDICT:", "PASS" if not bad1 and not bad2 else "FAIL")
