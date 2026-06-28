"""Classify which bad-edge subsets minimize the P5 support-Hall slack."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _codex_p5_support_hall import check_config
from _h import GENG, dec
from _angleD_O1 import gmin_sides


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = skips = nonfull = 0
    size_hist = {}
    examples = []
    for side in sides:
        r = check_config(n, adj, side)
        if r is None:
            continue
        if r["status"] == "skip":
            skips += 1
            continue
        total += 1
        if r["status"] != "ok":
            examples.append((g6, "".join(map(str, side)), r["status"], r.get("worst")))
            continue
        m = r["m"]
        mask = r["worst"][1]
        if mask != (1 << m) - 1:
            nonfull += 1
            sz = mask.bit_count()
            size_hist[sz] = size_hist.get(sz, 0) + 1
            if len(examples) < 5:
                examples.append((g6, "".join(map(str, side)), m, r["worst"]))
    return total, skips, nonfull, size_hist, examples


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    total = skips = nonfull = 0
    examples = []
    hist = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, s, nf, h, ex = fut.result()
            total += t
            skips += s
            nonfull += nf
            for k, v in h.items():
                hist[k] = hist.get(k, 0) + v
            for e in ex:
                if len(examples) < 10:
                    examples.append(e)
    print(f"workers {workers}")
    print(f"configs {total}")
    print(f"skips {skips}")
    print(f"nonfull_worst {nonfull}")
    print(f"nonfull_size_hist {hist}")
    print(f"examples {examples}")


if __name__ == "__main__":
    main()
