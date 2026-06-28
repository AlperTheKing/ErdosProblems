import subprocess

from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one


def scan(nmin=5, nmax=10):
    bad = 0
    worst = None
    total = 0
    for nn in range(nmin, nmax + 1):
        local_bad = 0
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            B = build(info)
            for C in components(B["K"], B["n"]):
                d = analyze_one(B, C)
                slack = d["deficit"] - d["dB"]
                total += 1
                if slack < 0:
                    bad += 1
                    local_bad += 1
                    record = (slack, nn, g6, C, sorted(B["O"]), d["deficit"], d["dB"])
                    if worst is None or record < worst:
                        worst = record
        print(f"N={nn}: local_bad={local_bad} total_bad={bad} worst={worst}")
    print("TOTAL", total, "bad", bad, "worst", worst)


if __name__ == "__main__":
    scan()
