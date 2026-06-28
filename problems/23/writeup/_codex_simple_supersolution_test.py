"""Test explicit Collatz supersolutions for K=P P^T.

Candidate:
  g(v) = min(1, T(v)/N), where T=K 1.
If K g <= N g entrywise and g>0, Perron-Frobenius gives rho(K)<=N.
"""

from fractions import Fraction as F
import argparse
import subprocess

from _h import GENG, dec, loads
from _codex_schur_rowsum_exact import exact_K_T


def check_info(info):
    n = info["n"]
    K, T = exact_K_T(info)
    g = [min(F(1), T[v] / n) for v in range(n)]
    worst = None
    for v in range(n):
        kg = sum(K[v][w] * g[w] for w in range(n))
        gap = kg - n * g[v]
        item = (gap, v, kg, g[v], T[v])
        if worst is None or item[0] > worst[0]:
            worst = item
    return worst


def run_named():
    for g6 in [
        "I?BD@g]Qo",
        "I?ABCc]}?",
        "J?`@C_W{Ck?",
        "J?AA@AW^?}?",
        "I?AAD@wF_",
    ]:
        n, e = dec(g6)
        info = loads(n, e)
        gap, v, kg, gv, Tv = check_info(info)
        print(
            f"{g6} N={n} Gamma={info['G']} "
            f"max(Kg-Ng)={gap} ({float(gap):+.6f}) v={v} Kg={kg} g={gv} T={Tv}",
            flush=True,
        )


def run_census(nmax=10, stride=1):
    count = 0
    bad = 0
    worst = None
    for n in range(5, nmax + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True
        ).stdout.split()[::stride]
        for g6 in graphs:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            count += 1
            item = check_info(info) + (g6, nn, info["G"], len(info["M"]))
            if item[0] > 0:
                bad += 1
            if worst is None or item[0] > worst[0]:
                worst = item
        print(f"N={n} done", flush=True)
    print(f"census count={count} bad={bad} worst={worst}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["named", "census"], default="named")
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()
    if args.mode == "named":
        run_named()
    else:
        run_census(args.nmax, args.stride)
