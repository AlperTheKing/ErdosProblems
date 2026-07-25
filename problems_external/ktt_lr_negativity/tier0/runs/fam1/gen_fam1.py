#!/usr/bin/env python
"""Generate family fam1: the verified NON-LATTICE refuter cell
       lam=(2,2,1), mu=(k,3,2,1), nu=(k+1,4,3,2,1),  k = 4..60
   plus ALL single- and two-box perturbations of all three partitions.

A "perturbation" is an integer vector delta on the 15 slots
   lam[0..2] + append,  mu[0..3] + append,  nu[0..4] + append
with  sum |delta| <= 2, subject to
   (a) balance  |lam|+|mu| = |nu|   preserved,
   (b) every partition stays weakly decreasing with nonnegative parts.
Single-box moves (|delta|_1 = 1) can never satisfy (a), so the surviving set
is exactly {base} U {two-box moves}; both are emitted (the base is delta=0).

Output: lines "lam;mu;nu" for tier0_screen.py --batch, deduplicated.
"""
import sys, json, itertools

KMIN, KMAX = 4, 60


def base(k):
    return ([2, 2, 1], [k, 3, 2, 1], [k + 1, 4, 3, 2, 1])


def valid(p):
    """weakly decreasing, nonnegative, at least one positive part"""
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    if not q:
        return None
    if any(x <= 0 for x in q):
        return None            # no zeros in the middle, no negatives
    for i in range(len(q) - 1):
        if q[i] < q[i + 1]:
            return None
    return tuple(q)


def slots(trip):
    """(which partition, index) for every modifiable slot, incl. one append"""
    out = []
    for w in range(3):
        for i in range(len(trip[w]) + 1):
            out.append((w, i))
    return out


def apply_delta(trip, moves):
    """moves = list of (w, i, dv); returns validated triple or None"""
    ls = [list(trip[0]), list(trip[1]), list(trip[2])]
    for (w, i, dv) in moves:
        if i == len(ls[w]):
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


def perturbations(trip):
    """all deltas with L1 norm 0 or 2 (norm 1 cannot balance)"""
    res = []
    b = apply_delta(trip, [])
    if b:
        res.append(b)
    S = slots(trip)
    # two units on one slot
    for (w, i) in S:
        for dv in (2, -2):
            t = apply_delta(trip, [(w, i, dv)])
            if t:
                res.append(t)
    # one unit on each of two distinct slots
    for (a, c) in itertools.combinations(S, 2):
        for d1 in (1, -1):
            for d2 in (1, -1):
                t = apply_delta(trip, [(a[0], a[1], d1), (c[0], c[1], d2)])
                if t:
                    res.append(t)
    return res


def main():
    seen = set()
    order = []
    for k in range(KMIN, KMAX + 1):
        for t in perturbations(base(k)):
            if t not in seen:
                seen.add(t)
                order.append(t)
    with open(sys.argv[1], "w") as f:
        for (l, m, n) in order:
            f.write("%s;%s;%s\n" % (",".join(map(str, l)),
                                    ",".join(map(str, m)),
                                    ",".join(map(str, n))))
    sys.stderr.write("emitted %d distinct triples\n" % len(order))


if __name__ == "__main__":
    main()
