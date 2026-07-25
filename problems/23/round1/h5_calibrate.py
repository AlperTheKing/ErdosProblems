"""H5 calibration: prove the certification pipeline sound before trusting it at N=49/51/74/76.

  (a) C5[n] for n=2,3,4  -> exhaustive maxcut vs both CP-SAT models, must agree, bip must be n^2
  (b) C5[10]  (N=50)     -> CP-SAT must return maxcut=400, bip=100 exactly, status OPTIMAL
"""
import sys, time
from h5_core import (adj_from_edges, maxcut_exhaustive, maxcut_cpsat_xor,
                     maxcut_cpsat_metric, edges_from_adj, is_triangle_free,
                     cut_value, g6)


def c5_blowup(parts):
    """C5 blow-up with the 5 given part sizes; returns (n, adj)."""
    n = sum(parts)
    off, blocks = [], []
    s = 0
    for p in parts:
        blocks.append(list(range(s, s + p)))
        s += p
    edges = []
    for i in range(5):
        for u in blocks[i]:
            for v in blocks[(i + 1) % 5]:
                edges.append((u, v))
    return n, adj_from_edges(n, edges)


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    ok = True
    for nn in (2, 3, 4):
        n, adj = c5_blowup([nn] * 5)
        m = len(edges_from_adj(n, adj))
        t0 = time.time()
        ex, exside = maxcut_exhaustive(n, adj)
        t1 = time.time()
        sx, cx, _, bx = maxcut_cpsat_xor(n, adj, workers=workers, max_time=120)
        sm, cm, _, bm = maxcut_cpsat_metric(n, adj, workers=workers, max_time=120)
        exp_bip = nn * nn
        good = (ex == cx == cm) and (m - ex == exp_bip) and sx == "OPTIMAL" == sm \
               and is_triangle_free(n, adj) and cut_value(n, adj, exside) == ex
        ok &= good
        print(f"C5[{nn}] N={n} m={m}: exhaustive={ex}({t1-t0:.1f}s) xor={cx}[{sx}] "
              f"metric={cm}[{sm}] bip={m-ex} expect={exp_bip}  {'OK' if good else 'FAIL'}",
              flush=True)

    # the real calibration: N = 50
    n, adj = c5_blowup([10] * 5)
    m = len(edges_from_adj(n, adj))
    print(f"\nC5[10]: N={n} m={m} tri-free={is_triangle_free(n, adj)} g6len={len(g6(n,adj))}")
    for name, fn in (("metric", maxcut_cpsat_metric), ("xor", maxcut_cpsat_xor)):
        t0 = time.time()
        st, c, side, b = fn(n, adj, workers=workers, max_time=1800)
        dt = time.time() - t0
        rec = cut_value(n, adj, side) if side else None
        print(f"  {name}: status={st} maxcut={c} recount={rec} dual_bound={b} "
              f"bip={m-c if c else None} (want 100)  {dt:.1f}s", flush=True)
        ok &= (st == "OPTIMAL" and c == 400 and rec == 400 and m - c == 100)
    print("\nCALIBRATION", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
