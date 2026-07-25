"""Emit graph6 for EVERY triangle-free circulant on Z_n, n in [lo,hi], with its
connection set and independence number.  bip is computed by h3_engine.exe."""
import sys, itertools
from h3_gen import g6, circulant, is_triangle_free, alpha

lo, hi = int(sys.argv[1]), int(sys.argv[2])
for n in range(lo, hi + 1):
    for r in range(1, n // 2 + 1):
        for S in itertools.combinations(range(1, n // 2 + 1), r):
            E = circulant(n, S)
            if not is_triangle_free(n, E):
                continue
            print(f"{g6(n, E)}\t{n}\t{list(S)}\t{len(E)}\t{alpha(n, E)}")
