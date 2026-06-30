"""Random exact gate for the abstract 5-layer PMS matrix theorem.

This is deliberately not a graph-census gate.  It samples the finite
five-layer abstraction from the OC-PMS proposal:

  A0 -- A1 -- A2 -- A3 -- A4, with bad edges A4--A0.

For a distinguished row x0-x1-x2-x3-x4 plus bad edge x4-x0, it enforces:

  * all row B-edges and the row bad edge are present;
  * every bad edge has at least one length-4 B-path through the layers;
  * full cut-domination delta_M(S) <= delta_B(S), all S;

and then checks the exact PMS inequality

  s_P <= N + (2/75) * (N^2 - 25 m).

The gamma-tie condition is not encoded here; failures are therefore useful
counterexamples to the cut-domination-only PMS theorem, while passes are only
evidence for the stronger theorem.
"""

from fractions import Fraction as F
import random


def offsets(sizes):
    out = [0]
    for s in sizes:
        out.append(out[-1] + s)
    return out


def vid(off, layer, idx):
    return off[layer] + idx


def edge_key(a, b):
    return (a, b) if a < b else (b, a)


def random_sizes(rng, n):
    sizes = [1, 1, 1, 1, 1]
    for _ in range(n - 5):
        sizes[rng.randrange(5)] += 1
    return sizes


def build_sample(rng, n, p_b, p_m):
    sizes = random_sizes(rng, n)
    off = offsets(sizes)

    B = set()
    M = set()

    # B-edges only between consecutive layers.
    for layer in range(4):
        for i in range(sizes[layer]):
            for j in range(sizes[layer + 1]):
                if rng.random() < p_b:
                    B.add(edge_key(vid(off, layer, i), vid(off, layer + 1, j)))

    # Bad edges only between A4 and A0.
    for i in range(sizes[4]):
        for j in range(sizes[0]):
            if rng.random() < p_m:
                M.add(edge_key(vid(off, 4, i), vid(off, 0, j)))

    # Distinguished row.
    for layer in range(4):
        B.add(edge_key(vid(off, layer, 0), vid(off, layer + 1, 0)))
    M.add(edge_key(vid(off, 4, 0), vid(off, 0, 0)))

    return sizes, off, B, M


def adj_between(sizes, off, B, layer):
    mat = [[False] * sizes[layer + 1] for _ in range(sizes[layer])]
    for i in range(sizes[layer]):
        a = vid(off, layer, i)
        for j in range(sizes[layer + 1]):
            b = vid(off, layer + 1, j)
            mat[i][j] = edge_key(a, b) in B
    return mat


def path_data(sizes, off, B):
    A01 = adj_between(sizes, off, B, 0)
    A12 = adj_between(sizes, off, B, 1)
    A23 = adj_between(sizes, off, B, 2)
    A34 = adj_between(sizes, off, B, 3)

    # total paths from A0[a] to A4[e]
    total = [[0] * sizes[4] for _ in range(sizes[0])]
    through = {}
    for a in range(sizes[0]):
        for e in range(sizes[4]):
            cnt = 0
            c1 = c2 = c3 = 0
            for b in range(sizes[1]):
                if not A01[a][b]:
                    continue
                for c in range(sizes[2]):
                    if not A12[b][c]:
                        continue
                    for d in range(sizes[3]):
                        if A23[c][d] and A34[d][e]:
                            cnt += 1
                            if b == 0:
                                c1 += 1
                            if c == 0:
                                c2 += 1
                            if d == 0:
                                c3 += 1
            total[a][e] = cnt
            through[(a, e)] = (c1, c2, c3)
    return total, through


def cut_dominated(n, B, M):
    B_list = list(B)
    M_list = list(M)
    for mask in range(1, 1 << (n - 1)):
        db = 0
        dm = 0
        for a, b in B_list:
            if ((mask >> a) ^ (mask >> b)) & 1:
                db += 1
        for a, b in M_list:
            if ((mask >> a) ^ (mask >> b)) & 1:
                dm += 1
        if dm > db:
            return False, mask, db, dm
    return True, None, None, None


def pms_margin(sizes, off, B, M):
    total, through = path_data(sizes, off, B)
    x0 = vid(off, 0, 0)
    x4 = vid(off, 4, 0)
    endpoint = sum(1 for e in M if x0 in e) + sum(1 for e in M if x4 in e)
    internal = F(0)

    for e in M:
        a, b = e
        if off[4] <= a < off[5]:
            a4 = a - off[4]
            a0 = b - off[0]
        else:
            a4 = b - off[4]
            a0 = a - off[0]
        z = total[a0][a4]
        if z <= 0:
            return None, ("no_path", e)
        c1, c2, c3 = through[(a0, a4)]
        internal += F(c1 + c2 + c3, z)

    s_p = F(endpoint) + internal
    n = sum(sizes)
    m = len(M)
    margin = F(n) + F(2, 75) * (n * n - 25 * m) - s_p
    return margin, (s_p, n, m)


def run(seed=20260630, trials=20000):
    rng = random.Random(seed)
    acc = {
        "trials": 0,
        "path_ok": 0,
        "cd_ok": 0,
        "fail": 0,
        "min_margin": None,
        "min_ex": None,
        "first_fail": None,
    }
    probs = [(0.35, 0.25), (0.45, 0.30), (0.55, 0.35), (0.70, 0.45)]
    for t in range(trials):
        n = rng.randint(10, 14)
        p_b, p_m = probs[rng.randrange(len(probs))]
        sizes, off, B, M = build_sample(rng, n, p_b, p_m)
        acc["trials"] += 1
        margin_data = pms_margin(sizes, off, B, M)
        if margin_data[0] is None:
            continue
        margin, detail = margin_data
        acc["path_ok"] += 1
        ok, mask, db, dm = cut_dominated(n, B, M)
        if not ok:
            continue
        acc["cd_ok"] += 1
        if acc["min_margin"] is None or margin < acc["min_margin"]:
            acc["min_margin"] = margin
            acc["min_ex"] = (sizes, len(B), len(M), detail, str(margin))
        if margin < 0:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (
                    sizes,
                    sorted(B),
                    sorted(M),
                    detail,
                    str(margin),
                )
                break
    return acc


if __name__ == "__main__":
    acc = run()
    print("PMS 5-layer random matrix gate")
    print("trials", acc["trials"], "path_ok", acc["path_ok"], "cd_ok", acc["cd_ok"])
    print("fail", acc["fail"])
    print("min_margin", acc["min_margin"], acc["min_ex"])
    if acc["first_fail"]:
        print("FIRST_FAIL", acc["first_fail"])
    print("VERDICT", "FAIL" if acc["fail"] else "no failure in random cut-domination samples")
