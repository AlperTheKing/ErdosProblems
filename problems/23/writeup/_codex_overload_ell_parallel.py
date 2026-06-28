from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
import time

from _h import GENG, dec, loads


def test_g6(g6: str):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None:
        return ("skip", g6, None)
    O = [v for v, t in enumerate(info["T"]) if t > n]
    if not O:
        return ("skip", g6, None)

    max_ell = 0
    witness = None
    for v in O:
        inc = []
        for f in info["M"]:
            if any(v in path for path in info["cyc"][f]):
                inc.append(f)
                if info["ell"][f] > max_ell:
                    max_ell = info["ell"][f]
                    witness = (v, f, info["ell"][f])
    return ("ok", g6, dict(n=n, O=O, max_ell=max_ell, witness=witness))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=32)
    ns = ap.parse_args()

    out = subprocess.run(
        [GENG, "-tc", str(ns.n)], capture_output=True, text=True, check=True
    ).stdout.split()
    t0 = time.time()
    count = skip = 0
    max_ell = 0
    witness = None
    with mp.Pool(processes=ns.workers) as pool:
        for done, (st, g6, data) in enumerate(
            pool.imap_unordered(test_g6, out, chunksize=ns.chunksize), 1
        ):
            if st == "skip":
                skip += 1
            else:
                count += 1
                if data["max_ell"] > max_ell:
                    max_ell = data["max_ell"]
                    witness = (g6, data)
            if done % 5000 == 0:
                print(
                    f"done={done}/{len(out)} withO={count} skip={skip} "
                    f"max_ell={max_ell} witness={witness} elapsed={time.time()-t0:.1f}s",
                    flush=True,
                )
    print(
        f"FINAL n={ns.n} graphs={len(out)} withO={count} skip={skip} "
        f"max_ell={max_ell} witness={witness} elapsed={time.time()-t0:.1f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
