import subprocess
from fractions import Fraction as F

from _h import dec, GENG, loads
from _edgeload import edge_loads


def scan(nmin=7, nmax=10):
    totals = dict(zero=0, both_load=0, sat_endpoint=0, both_pos_under=0)
    examples = {}
    for nn in range(nmin, nmax + 1):
        local = dict(zero=0, both_load=0, sat_endpoint=0, both_pos_under=0)
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None or not any(t > n for t in info["T"]):
                continue
            mu, _ = edge_loads(info)
            for e in info["Bset"]:
                val = mu.get(e, F(0))
                if val != 0:
                    continue
                a, b = e
                Ta, Tb = info["T"][a], info["T"][b]
                local["zero"] += 1
                totals["zero"] += 1
                if Ta > 0 and Tb > 0:
                    local["both_load"] += 1
                    totals["both_load"] += 1
                    examples.setdefault("both_load", (nn, g6, e, Ta, Tb, sorted(info["T"])))
                if Ta == n or Tb == n:
                    local["sat_endpoint"] += 1
                    totals["sat_endpoint"] += 1
                    examples.setdefault("sat_endpoint", (nn, g6, e, Ta, Tb, sorted(info["T"])))
                if 0 < Ta <= n and 0 < Tb <= n:
                    local["both_pos_under"] += 1
                    totals["both_pos_under"] += 1
                    examples.setdefault("both_pos_under", (nn, g6, e, Ta, Tb, sorted(info["T"])))
        print(f"N={nn}: {local}")
    print("TOTAL", totals)
    for k, v in examples.items():
        print("EX", k, v)


if __name__ == "__main__":
    scan()
