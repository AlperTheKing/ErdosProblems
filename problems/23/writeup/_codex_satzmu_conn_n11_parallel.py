"""Parallel all-gamma-min SAT-ZMU-CONN scan for N=11."""

from multiprocessing import Pool
import subprocess

from _h import GENG, dec
from _codex_satzmu_conn import test_graph


def check(g6):
    n, E = dec(g6)
    ok, G, mult, info, bad = test_graph(g6, n, E)
    if ok:
        return (1, mult, None)
    return (1, mult, (g6, G, mult, bad, info["side"], [str(t) for t in info["T"]]))


def main():
    N = 11
    workers = 60
    g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
    tested = 0
    max_mult = 0
    with Pool(processes=workers) as pool:
        for cnt, mult, fail in pool.imap_unordered(check, g6s, chunksize=16):
            tested += cnt
            max_mult = max(max_mult, mult)
            if tested % 5000 == 0:
                print(f"tested={tested} max_mult={max_mult}", flush=True)
            if fail is not None:
                print("FAIL", fail, flush=True)
                return
    print(f"N=11 tested={tested} max_gamma_min_mult={max_mult} failures=0")


if __name__ == "__main__":
    main()
