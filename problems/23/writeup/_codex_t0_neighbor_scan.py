"""Scan B-neighbors of T=0 vertices in O-nonempty small census graphs."""

from collections import Counter
from multiprocessing import Pool
import subprocess

from _h import GENG, dec, loads


def scan_one(g6):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None:
        return None
    T = info["T"]
    O = [v for v, t in enumerate(T) if t > n]
    if not O:
        return None
    vals = []
    sat_hits = []
    for v, tv in enumerate(T):
        if tv != 0:
            continue
        for w in info["adj"][v]:
            e = (v, w) if v < w else (w, v)
            if e not in info["Bset"]:
                continue
            vals.append(n - T[w])
            if T[w] == n:
                sat_hits.append((v, w))
    if not vals:
        return {"graphs": 1, "with_t0": 0, "vals": [], "sat_hits": []}
    return {"graphs": 1, "with_t0": 1, "vals": vals, "sat_hits": sat_hits}


def main():
    workers = 60
    for N in range(7, 12):
        g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
        total_o = 0
        with_t0 = 0
        sat_hits = []
        margins = Counter()
        min_margin = None
        min_wit = None
        with Pool(processes=workers) as pool:
            for g6, res in zip(g6s, pool.imap(scan_one, g6s, chunksize=64)):
                if res is None:
                    continue
                total_o += res["graphs"]
                with_t0 += res["with_t0"]
                for m in res["vals"]:
                    margins[str(m)] += 1
                    if min_margin is None or m < min_margin:
                        min_margin = m
                        min_wit = g6
                if res["sat_hits"]:
                    sat_hits.append((g6, res["sat_hits"]))
                    break
        print(
            f"N={N}: Ographs={total_o} Ographs_with_T0={with_t0} "
            f"min_neighbor_margin={min_margin} min_wit={min_wit} sat_hits={sat_hits[:1]}"
        )
        print(f"  margins={dict(sorted(margins.items()))}")
        if sat_hits:
            break


if __name__ == "__main__":
    main()
