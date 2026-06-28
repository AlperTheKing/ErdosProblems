import subprocess
from collections import Counter

from _h import dec, GENG, loads


def scan(nmin=7, nmax=10):
    hist = Counter()
    examples = {}
    for nn in range(nmin, nmax + 1):
        local = Counter()
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None or not any(t > n for t in info["T"]):
                continue
            Mset = set(info["Mset"])
            Bset = set(info["Bset"])
            for v, Tv in enumerate(info["T"]):
                if Tv != 0:
                    continue
                bdeg = sum(1 for e in Bset if v in e)
                mdeg = sum(1 for e in Mset if v in e)
                key = (bdeg, mdeg)
                local[key] += 1
                hist[key] += 1
                examples.setdefault(key, (nn, g6, v, sorted(info["T"])))
        print(f"N={nn}: {dict(local)}")
    print("TOTAL", dict(hist))
    for k, v in sorted(examples.items()):
        print("EX", k, v)


if __name__ == "__main__":
    scan()
