#!/usr/bin/env python
"""fam1 extended: same base cell, perturbation budget L1 <= B (B given).

usage: gen_fam1b.py OUT KMIN KMAX BUDGET [EXCLUDE.batch ...]
Emits only triples not already present in the EXCLUDE files.
"""
import sys, itertools

def base(k):
    return ([2, 2, 1], [k, 3, 2, 1], [k + 1, 4, 3, 2, 1])

def valid(p):
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    if not q:
        return None
    if any(x <= 0 for x in q):
        return None
    for i in range(len(q) - 1):
        if q[i] < q[i + 1]:
            return None
    return tuple(q)

def slots(trip):
    return [(w, i) for w in range(3) for i in range(len(trip[w]) + 1)]

def apply_delta(trip, moves):
    ls = [list(trip[0]), list(trip[1]), list(trip[2])]
    for (w, i, dv) in moves:
        if i >= len(ls[w]):
            if dv <= 0:
                return None
            ls[w].append(dv)
        else:
            ls[w][i] += dv
    out = []
    for w in range(3):
        v = valid(ls[w])
        if v is None:
            return None
        out.append(v)
    if sum(out[0]) + sum(out[1]) != sum(out[2]):
        return None
    return tuple(out)

def deltas(S, budget):
    """all integer vectors on S with 0 < sum|d| <= budget, as move lists"""
    n = len(S)
    res = []
    for support_size in range(1, budget + 1):
        for supp in itertools.combinations(range(n), support_size):
            # magnitudes >=1 summing to <= budget
            def rec(idx, rem, acc):
                if idx == support_size:
                    res.append(list(acc))
                    return
                for mag in range(1, rem - (support_size - idx - 1) + 1):
                    for sgn in (1, -1):
                        acc.append((S[supp[idx]][0], S[supp[idx]][1], sgn * mag))
                        rec(idx + 1, rem - mag, acc)
                        acc.pop()
            rec(0, budget, [])
    return res

def main():
    out, kmin, kmax, budget = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    seen = set()
    for ex in sys.argv[5:]:
        for line in open(ex):
            line = line.strip()
            if line:
                a, b, c = line.split(";")
                seen.add((tuple(map(int, a.split(","))),
                          tuple(map(int, b.split(","))),
                          tuple(map(int, c.split(",")))))
    order = []
    for k in range(kmin, kmax + 1):
        trip = base(k)
        S = slots(trip)
        b0 = apply_delta(trip, [])
        if b0 and b0 not in seen:
            seen.add(b0); order.append(b0)
        for mv in deltas(S, budget):
            t = apply_delta(trip, mv)
            if t and t not in seen:
                seen.add(t); order.append(t)
    with open(out, "w") as f:
        for (l, m, n) in order:
            f.write("%s;%s;%s\n" % (",".join(map(str, l)),
                                    ",".join(map(str, m)),
                                    ",".join(map(str, n))))
    sys.stderr.write("emitted %d new triples\n" % len(order))

if __name__ == "__main__":
    main()
