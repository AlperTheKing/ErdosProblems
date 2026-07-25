"""Distribution of the discrete partials  D_i = 6a1(g + 4*e_i) - 6a1(g).

Step 4 keeps realisability (4 | Aw+Bw-Cw is preserved by g_i -> g_i+4 only for
some i, so we instead re-fix and correct).  We use step 4 on each coordinate,
which changes Aw+Bw-Cw by a multiple of 4 always, hence preserves realisability.

If every partial is >= 0 in every chamber then a1 = grad.g >= 0 on the
nonnegative orthant and KTT holds at r=4.  A single strictly negative partial
is the door to a counterexample: push that coordinate.
"""
import random, sys, os, math, json
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from search import a1x6

def partials(g, step=4):
    r = a1x6(g)
    if r[0] != "ok":
        return None, None
    base = r[1]
    out = []
    for k in range(9):
        h = list(g); h[k] += step
        r2 = a1x6(tuple(h))
        out.append(r2[1] - base if r2[0] == "ok" else None)
    return base, out

if __name__ == "__main__":
    seed = int(sys.argv[1]); N = int(sys.argv[2]); K = int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else "iso"
    random.seed(seed)
    cnt = Counter(); neg = []
    perc = [Counter() for _ in range(9)]
    done = 0
    while done < N:
        if mode == "iso":
            g = tuple(random.randint(1, K) for _ in range(9))
        else:
            g = tuple(max(1, int(10 ** random.uniform(0, math.log10(K)))) for _ in range(9))
        g = kt4.fix_gap(g)
        base, P = partials(g)
        if P is None or any(x is None for x in P):
            continue
        done += 1
        for k, x in enumerate(P):
            perc[k][x] += 1
            cnt[x] += 1
            if x < 0:
                neg.append((g, k, x, base))
    print("seed", seed, "N", done, "K", K, mode)
    print("partial-value histogram (all coords):", dict(sorted(cnt.items())[:20]))
    print("min partial:", min(cnt), " #negative:", sum(v for k, v in cnt.items() if k < 0))
    for k in range(9):
        print("  coord %d: min=%s" % (k, min(perc[k])), dict(sorted(perc[k].items())[:6]))
    if neg:
        print("NEGATIVE PARTIALS (first 10):")
        for t in neg[:10]:
            print("   ", t)
