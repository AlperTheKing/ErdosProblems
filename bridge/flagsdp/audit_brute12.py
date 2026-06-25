"""D5 INDEPENDENT audit. Fast numpy-vectorized exact max-cut over all 2^(n-1) cuts at once.
Cross-checks brute_dmono.py for n=9..11, then runs n=12 (band-only + global) which the
pure-python version is too slow for. Independent maxcut algorithm: build edge list, enumerate
all side-assignments as a bit matrix, count cut edges by XOR of endpoint side bits.

Also independently checks triangle-freeness of each enumerated graph (don't trust the flag
of fe.enumerate_graphs)."""
import sys, time
import numpy as np
import flag_engine as fe

LO, HI = 0.2486, 0.3197

def edges_of(n, A):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (A[u] >> v) & 1]

def is_triangle_free(n, A):
    for u in range(n):
        for v in range(u + 1, n):
            if not ((A[u] >> v) & 1):
                continue
            # common neighbor w
            for w in range(v + 1, n):
                if ((A[u] >> w) & 1) and ((A[v] >> w) & 1):
                    return False
    return True

def maxcut_vec(n, edges):
    """Exact max-cut via full enumeration, vectorized over all 2^(n-1) assignments.
    Fix vertex 0 to side 0 (WLOG). side bits for vertices 1..n-1 enumerated."""
    M = 1 << (n - 1)
    # masks: rows = assignments, columns = vertices 1..n-1
    idx = np.arange(M, dtype=np.int64)
    # side[v] for v in 1..n-1 ; side[0]=0
    sides = np.zeros((M, n), dtype=np.int8)
    for j in range(1, n):
        sides[:, j] = (idx >> (j - 1)) & 1
    best = 0
    cut_total = np.zeros(M, dtype=np.int32)
    for (u, v) in edges:
        cut_total += (sides[:, u] ^ sides[:, v])
    return int(cut_total.max())

def run(n, band_only=False):
    C2 = n * (n - 1) // 2
    best_band = (-1.0, 0, 0, 0.0)
    best_all = (-1.0, 0, 0, 0.0)
    cnt = 0
    tf_fail = 0
    for (nn, A) in fe.enumerate_graphs(n, triangle_free=True):
        cnt += 1
        if not is_triangle_free(n, A):
            tf_fail += 1
            continue
        e = sum(1 for u in range(n) for v in range(u + 1, n) if (A[u] >> v) & 1)
        de = e / C2
        inband = LO <= de <= HI
        if band_only and not inband:
            continue
        edges = edges_of(n, A)
        mc = maxcut_vec(n, edges)
        dm = 2 * (e - mc) / (n * n)
        if dm > best_all[0]:
            best_all = (dm, e, mc, de)
        if inband and dm > best_band[0]:
            best_band = (dm, e, mc, de)
    return best_band, best_all, cnt, tf_fail

if __name__ == "__main__":
    n0 = int(sys.argv[1])
    n1 = int(sys.argv[2])
    band_only = len(sys.argv) > 3 and sys.argv[3] == "band"
    for n in range(n0, n1 + 1):
        t = time.time()
        bb, ba, cnt, tff = run(n, band_only=band_only)
        dt = time.time() - t
        mode = "BAND-ONLY" if band_only else "ALL"
        print(f"n={n} [{mode}] graphs={cnt} tf_fail={tff} | IN BAND max d_mono={bb[0]:.6f} "
              f"(e={bb[1]} mc={bb[2]} d_edge={bb[3]:.4f}) | ALL max d_mono={ba[0]:.6f} "
              f"(e={ba[1]} mc={ba[2]} d_edge={ba[3]:.4f}) | {dt:.1f}s [target 0.0800607]", flush=True)
    print("DONE", flush=True)
