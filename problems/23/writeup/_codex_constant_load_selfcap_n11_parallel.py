"""64-worker N=11 scan for CONSTANT-LOAD-SELFCAP.

This is evidence only. Acceptance still belongs to the Claude exact gate.
"""
from multiprocessing import Pool
import subprocess

from _h import GENG, dec
from _codex_constant_load_selfcap import check_graph


def check(g6):
    n, edges = dec(g6)
    r = check_graph(g6, n, edges)
    if r["bad"]:
        return (1, r["total"], (g6, r["first"]))
    return (1, r["total"], None)


def main():
    # Windows multiprocessing wait handles cap out below 64 worker processes.
    workers = 60
    g6s = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True).stdout.split()
    tested = 0
    comps = 0
    with Pool(processes=workers) as pool:
        for cnt, total, fail in pool.imap_unordered(check, g6s, chunksize=16):
            tested += cnt
            comps += total
            if tested % 5000 == 0:
                print(f"tested={tested} const_load_comps={comps}", flush=True)
            if fail is not None:
                print(f"FAIL tested={tested} comps={comps} witness={fail}", flush=True)
                return
    print(f"N=11 tested={tested} const_load_comps={comps} selfcap_bad=0", flush=True)


if __name__ == "__main__":
    main()
