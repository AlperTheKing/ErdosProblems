"""H2_types.py -- enumerate all realisable combinatorial TYPES of a k-atom measure
on the circle graph Gamma.

For k atoms at positions p_0 < ... < p_{k-1} the whole problem (adjacency AND the
arc-cut family) depends only on which pairs satisfy circular distance > 1/3.
Equivalently on b_i = #{ j != i : p_j in (p_i, p_i+1/3] }, since
    B_i := {j : d(p_i,p_j) <= 1/3} = [i-a_i, i+b_i]   (a cyclic interval),
    N(i) = complement of B_i.
The type is therefore the cyclic word (b_0,...,b_{k-1}) up to rotation/reflection.
This is a finite set; realisability is decided by exhibiting integer gap vectors,
i.e. by running over k-subsets of Gamma_n for a range of n.
"""
import sys, itertools
from functools import lru_cache


def type_of(pos, n):
    """pos = sorted tuple of k integer positions in Z_n.  Returns canonical type."""
    k = len(pos)
    b = []
    for i in range(k):
        cnt = 0
        for t in range(1, k):
            j = (i + t) % k
            d = (pos[j] - pos[i]) % n
            if 3 * d <= n:
                cnt += 1
            else:
                break
        b.append(cnt)
    return canon(tuple(b))


def canon(b):
    k = len(b)
    cands = []
    for r in range(k):
        cands.append(tuple(b[(r + i) % k] for i in range(k)))
    # reflection: reversing the circular order maps b -> a (backward counts).
    # compute a from b directly for the reflected word
    rb = tuple(reversed(b))
    for r in range(k):
        cands.append(tuple(rb[(r + i) % k] for i in range(k)))
    return min(cands)


def adj_from_type(b):
    """adjacency (list of frozensets) of the type."""
    k = len(b)
    A = [set() for _ in range(k)]
    for i in range(k):
        for t in range(b[i] + 1, k):
            j = (i + t) % k
            A[i].add(j)
    # symmetrise defensively (a realisable type is already symmetric)
    for i in range(k):
        for j in list(A[i]):
            A[j].add(i)
    return [frozenset(s) for s in A]


def enumerate_types(k, nmax):
    seen = {}
    for n in range(k, nmax + 1):
        if n % 3 == 0:
            continue          # avoid exact-1/3 ties; every open cell is seen for other n
        for rest in itertools.combinations(range(1, n), k - 1):
            pos = (0,) + rest
            t = type_of(pos, n)
            if t not in seen:
                seen[t] = (n, pos)
    return seen


def is_symmetric(b):
    A = [set() for _ in range(len(b))]
    k = len(b)
    for i in range(k):
        for t in range(b[i] + 1, k):
            A[i].add((i + t) % k)
    return all((j in A[i]) == (i in A[j]) for i in range(k) for j in range(k) if i != j)


if __name__ == "__main__":
    for k in range(4, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 9):
        nmax = {4: 24, 5: 26, 6: 26, 7: 24, 8: 22, 9: 20, 10: 19}.get(k, 18)
        seen = enumerate_types(k, nmax)
        # keep only types with min degree >= 1 and triangle-free (automatic)
        keep = {}
        for t, w in seen.items():
            A = adj_from_type(t)
            if min(len(s) for s in A) < 1:
                continue
            keep[t] = w
        print(f"k={k}: realisable types (nmax={nmax}) = {len(seen)}, "
              f"with min-degree>=1 = {len(keep)}")
        sys.stdout.flush()
