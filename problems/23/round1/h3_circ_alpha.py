"""Exhaustive sweep of triangle-free circulants on Z_n: report (alpha, m) for all,
and emit graph6 of every circulant attaining the minimum alpha at that order
(= cyclic Ramsey-critical triangle-free graphs).  bip is computed separately by
h3_engine.exe on the emitted graph6 list.
"""
import sys, itertools
from h3_gen import g6, circulant, is_triangle_free, alpha

lo, hi = int(sys.argv[1]), int(sys.argv[2])
out = open(sys.argv[3], "w") if len(sys.argv) > 3 else sys.stdout

for n in range(lo, hi + 1):
    best = None
    reps = []
    cnt = 0
    for r in range(1, n // 2 + 1):
        for S in itertools.combinations(range(1, n // 2 + 1), r):
            E = circulant(n, S)
            if not is_triangle_free(n, E):
                continue
            cnt += 1
            a = alpha(n, E)
            if best is None or a < best:
                best = a
                reps = [(S, len(E), a)]
            elif a == best:
                reps.append((S, len(E), a))
    # among min-alpha circulants keep the ones with most edges first
    reps.sort(key=lambda t: -t[1])
    print(f"# n={n} triangle_free_circulants={cnt} min_alpha={best} n_attaining={len(reps)}", file=out)
    for S, m, a in reps[:12]:
        print(f"{g6(n, circulant(n, S))} n={n} S={list(S)} m={m} alpha={a}", file=out)
    out.flush()
