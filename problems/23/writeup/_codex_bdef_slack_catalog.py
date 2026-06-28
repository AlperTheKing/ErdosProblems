from fractions import Fraction as F
import subprocess

from _h import dec, GENG, loads
from _bdef_theory import run


def scan_census(nmin=5, nmax=10):
    buckets = {
        "whole": [],
        "proper_o_empty": [],
        "proper_o_nonempty": [],
        "proper_nontriv_o_nonempty": [],
    }
    counts = {k: 0 for k in buckets}
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            B, comps = run(g6, info)
            o_nonempty = bool(B["O"])
            for C, d in comps:
                slack = d["deficit"] - d["dB"]
                key = "whole" if len(C) == n else ("proper_o_nonempty" if o_nonempty else "proper_o_empty")
                counts[key] += 1
                buckets[key].append((slack, nn, g6, C, d["deficit"], d["dB"], sorted(B["O"])))
                if o_nonempty and len(C) != n and not all(B["T"][v] == 0 for v in C):
                    counts["proper_nontriv_o_nonempty"] += 1
                    buckets["proper_nontriv_o_nonempty"].append(
                        (slack, nn, g6, C, d["deficit"], d["dB"], sorted(B["O"]))
                    )
    for key in buckets:
        buckets[key].sort(key=lambda x: (x[0], x[1], x[2], len(x[3])))
        print(f"== {key} count={counts[key]} ==")
        for item in buckets[key][:8]:
            slack, nn, g6, C, deficit, dB, O = item
            print(
                f"N={nn} g6={g6} sz={len(C)} slack={slack} "
                f"deficit={deficit} dB={dB} O={O} C={C}"
            )


if __name__ == "__main__":
    scan_census()
