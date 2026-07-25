"""H2_run_opt.py -- many-restart global maximisation of 25*ARCBOUND on Gamma_m.

Target: any x on the simplex with 25*ARCBOUND(x) > 1 refutes the arc-cut conjecture.
Reference points: the five-atom configuration gives exactly 1.
"""
import sys, numpy as np
from H2_opt import make, all_F, arcbound_np, lp_ascent


def five_atom(m):
    x = np.zeros(m)
    for t in range(5):
        x[(t * m) // 5] = 0.2
    return x


def run(m, ntrials=40, seed=0, iters=120):
    a, b = make(m)
    rng = np.random.default_rng(seed)
    best = (-1, None)
    # deterministic seeds
    seeds = [np.ones(m) / m, five_atom(m)]
    # perturbed five-atom seeds
    for _ in range(6):
        x = five_atom(m) + 0.02 * rng.random(m)
        seeds.append(x / x.sum())
    for _ in range(ntrials):
        k = int(rng.integers(4, min(m, 16)) + 1)
        pos = rng.choice(m, size=k, replace=False)
        x = np.zeros(m)
        x[pos] = rng.random(k)
        if x.sum() == 0:
            continue
        seeds.append(x / x.sum())
    for _ in range(max(4, ntrials // 4)):
        x = rng.random(m)
        seeds.append(x / x.sum())
    for si, x0 in enumerate(seeds):
        x, v = lp_ascent(x0, m, a, b, iters=iters, nact=80, radius=0.6, seed=si)
        r = 25 * v
        if r > best[0]:
            best = (r, x.copy())
            if r > 1.0 + 1e-9:
                print(f"  !!! m={m} seed#{si} 25*AB = {r:.12f} > 1")
                np.save(f"H2_hit_m{m}_s{si}.npy", x)
    return best


if __name__ == "__main__":
    ms = [int(t) for t in sys.argv[1:]] or [23, 25, 29, 31, 37, 41]
    for m in ms:
        r, x = run(m, ntrials=int(30), seed=m)
        supp = np.argwhere(x > 1e-9).ravel()
        print(f"m={m:4d}  best 25*ARCBOUND = {r:.12f}   support={len(supp)}  "
              f"{[(int(i), round(float(x[i]), 6)) for i in supp][:14]}")
        sys.stdout.flush()
