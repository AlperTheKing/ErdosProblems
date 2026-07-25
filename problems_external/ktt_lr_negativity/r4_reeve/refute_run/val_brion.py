import random, sys
from fractions import Fraction
sys.path.insert(0, r"C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\f1987d98-c6e4-47b0-90c4-e402adf2c40c\scratchpad\ktt")
import kt4

def pev(P, n):
    return P[0] + P[1] * n + P[2] * n * n + P[3] * n ** 3

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 6
NTRY = int(sys.argv[3]) if len(sys.argv) > 3 else 300

nok = nlow = nempty = nbad = 0
fails = []
stats = {}
tried = 0
while tried < NTRY:
    g = kt4.fix_gap(tuple(random.randint(1, KMAX) for _ in range(9)))
    A, b, bad = kt4.gap_rows(g)
    if bad:
        continue
    ds, bs = kt4.reduce_rows(A, b)
    if any(x.denominator != 1 for x in bs if isinstance(x, Fraction)):
        pass
    r = kt4.ehrhart_brion(ds, bs)
    tried += 1
    st = r["status"]
    stats[st] = stats.get(st, 0) + 1
    if st != "ok":
        if st == "bad":
            nbad += 1
            fails.append(("BADVERTEX", g, r["bad"][:3]))
        continue
    nok += 1
    P = r["poly"]
    # exact cross-checks
    if P[0] != 1:
        fails.append(("a0", g, [str(x) for x in P])); continue
    V = kt4.normalized_volume(ds, bs)
    if P[3] * 6 != V:
        fails.append(("vol", g, str(P[3] * 6), str(V))); continue
    for n in (1, 2, 3):
        L = kt4.count_lattice(ds, bs, n)
        if pev(P, n) != L:
            fails.append(("L%d" % n, g, str(pev(P, n)), L)); break

print("tried", tried, "status", stats)
print("fails", len(fails))
for f in fails[:10]:
    print("  ", f)
