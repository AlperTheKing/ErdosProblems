"""Parallel N=11 scan for saturated-boundary deficit inequality."""

from multiprocessing import Pool
import subprocess

from _h import GENG, dec, loads
from _codex_sat_boundary_deficit import violations


def check(g6):
    info = loads(*dec(g6))
    if info is None:
        return (1, None)
    bad = violations(info)
    if bad:
        return (1, (g6, bad[0]))
    return (1, None)


def main():
    workers = 60
    g6s = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True).stdout.split()
    tested = 0
    with Pool(processes=workers) as pool:
        for cnt, fail in pool.imap_unordered(check, g6s, chunksize=64):
            tested += cnt
            if tested % 5000 == 0:
                print(f"tested={tested}", flush=True)
            if fail is not None:
                print("FAIL", fail, flush=True)
                return
    print(f"N=11 tested={tested} saturated-boundary-deficit failures=0")


if __name__ == "__main__":
    main()
