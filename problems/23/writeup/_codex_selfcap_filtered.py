from fractions import Fraction as F
import subprocess
import sys

from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges


def check_info(info, name):
    if info is None:
        return []
    B = build(info)
    n = B["n"]
    O = B["O"]
    if not O:
        return []
    failures = []
    for C in components(B["K"], n):
        Cs = set(C)
        if Cs & O:
            continue
        d = analyze_one(B, C)
        if d["nFC"] == 0:
            continue
        max_t = max(B["T"][v] for v in C)
        gamma = d["GammaC"]
        ok = max_t <= len(C) and gamma <= F(len(C) * len(C))
        if not ok:
            failures.append(
                {
                    "name": name,
                    "C": tuple(C),
                    "O": tuple(sorted(O)),
                    "maxT": max_t,
                    "size": len(C),
                    "GammaC": gamma,
                    "dB": d["dB"],
                }
            )
    return failures


def census(n_min=5, n_max=11):
    total = 0
    failures = []
    for n in range(n_min, n_max + 1):
        out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        count = 0
        fail = 0
        for g6 in out:
            info = loads(*dec(g6))
            fs = check_info(info, g6)
            count += 1
            fail += len(fs)
            failures.extend(fs)
            if failures:
                break
        total += count
        print(f"census N={n}: graphs={count} failures={fail}", flush=True)
        if failures:
            break
    return total, failures


def constructions():
    tests = []
    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(island, g15)
    n, E = add_edges((n, E), [(0, 5)])
    tests.append(("C5+MycC7 bridge", loads(n, E)))
    for name, info in tests:
        fs = check_info(info, name)
        print(f"construction {name}: failures={len(fs)}")
        for f in fs[:3]:
            print("  ", f)


if __name__ == "__main__":
    total, failures = census()
    print("TOTAL_GRAPHS", total)
    print("FIRST_FAILURE", failures[0] if failures else None)
    constructions()
    sys.exit(1 if failures else 0)
