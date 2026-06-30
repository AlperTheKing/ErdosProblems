from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side

base_g6 = 'I?BD@g]Qo'
base_n, base_E = dec(base_g6)
base_side = [int(c) for c in '0001111000']


def blow(weights):
    off = []
    n = 0
    for w in weights:
        off.append(n)
        n += w
    E = []
    for a, b in base_E:
        for i in range(weights[a]):
            for j in range(weights[b]):
                E.append((off[a] + i, off[b] + j))
    side = []
    for v, w in enumerate(weights):
        side += [base_side[v]] * w
    return n, E, side


def scan(weights):
    n, E, side = blow(weights)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    if not Bconn(n, adj, side):
        return {'weights': weights, 'Bconn': False}
    st = struct_for_side(n, adj, side)
    if st is None:
        return {'weights': weights, 'struct': False}
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    over = []
    min_margin = None
    maxI = None
    for f in M:
        L = ell[f]
        for P in cyc[f]:
            R = sum(T[v] for v in P)
            if R > L * n:
                Pset = set(P)
                I = sum(F(1, len(cyc[g])) * sum(len(Pset & set(Q)) for Q in cyc[g]) for g in M)
                Def = n * n - 25 * len(M)
                margin = F(2) * Def - 75 * (I - n)
                over.append((f, tuple(P), I, margin))
                if min_margin is None or margin < min_margin:
                    min_margin = margin
                if maxI is None or I > maxI:
                    maxI = I
    return {
        'weights': weights,
        'n': n,
        'm': len(M),
        'ells': sorted(set(ell.values())),
        'over': len(over),
        'min_margin': min_margin,
        'maxI': maxI,
        'first': over[:3],
    }


def main():
    tests = []
    for t in [1, 2, 3]:
        tests.append([t] * base_n)
    tests += [
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 2, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 2, 1, 1],
        [2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 2, 1, 2, 1, 1],
    ]
    for w in tests:
        print(scan(w))


if __name__ == '__main__':
    main()
