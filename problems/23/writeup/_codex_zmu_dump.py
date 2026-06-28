from fractions import Fraction as F
import subprocess

from _h import dec, GENG, loads
from _zmu import mu_edges


def dump(max_examples=12, nmin=9, nmax=11):
    shown = 0
    for nn in range(nmin, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            info = loads(n, E)
            if info is None or not any(t > n for t in info["T"]):
                continue
            mu = mu_edges(info)
            Mdeg = [0] * n
            Bdeg = [0] * n
            for a, b in info["Mset"]:
                Mdeg[a] += 1
                Mdeg[b] += 1
            for a, b in info["Bset"]:
                Bdeg[a] += 1
                Bdeg[b] += 1
            zero = [tuple(sorted(e)) for e, val in mu.items() if val == 0]
            if not zero:
                continue
            print("GRAPH", nn, g6, "O", [v for v, t in enumerate(info["T"]) if t > n])
            print(" side", info["side"])
            print(" T", [str(t) for t in info["T"]])
            print(" M", info["M"])
            print(" Bzero", zero)
            for e in zero:
                a, b = e
                print(
                    "  e", e,
                    "T", str(info["T"][a]), str(info["T"][b]),
                    "Bdeg", Bdeg[a], Bdeg[b],
                    "Mdeg", Mdeg[a], Mdeg[b],
                    "adj", sorted(info["adj"][a]), sorted(info["adj"][b]),
                )
            shown += 1
            if shown >= max_examples:
                return


if __name__ == "__main__":
    dump()
