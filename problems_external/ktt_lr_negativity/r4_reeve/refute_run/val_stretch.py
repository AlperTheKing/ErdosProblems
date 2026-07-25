import random, sys, subprocess, os
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4

ENG = r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\engine"
random.seed(99)

cases = []
while len(cases) < 60:
    K = random.choice([2, 3, 4, 6])
    g = kt4.fix_gap(tuple(random.randint(1, K) for _ in range(9)))
    A, b, bad = kt4.gap_rows(g)
    if bad: continue
    ds, bs = kt4.reduce_rows(A, b)
    r = kt4.ehrhart_brion(ds, bs)
    if r["status"] != "ok": continue
    lam, mu, nu = kt4.realise(g)
    cases.append((g, lam, mu, nu, r["poly"]))

lines = []
for g, lam, mu, nu, P in cases:
    for n in (1, 2, 3, 4):
        lines.append("%s;%s;%s" % (
            ",".join(str(n * x) for x in lam),
            ",".join(str(n * x) for x in mu),
            ",".join(str(n * x) for x in nu)))
open("stretch.batch", "w").write("\n".join(lines) + "\n")

A_out = subprocess.run([os.path.join(ENG, "lr_hive.exe"), "--batch", "stretch.batch"],
                       capture_output=True, text=True).stdout.split()
B_out = subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"),
                        "--batch", "stretch.batch"], capture_output=True, text=True).stdout.split()

bad = 0
i = 0
for g, lam, mu, nu, P in cases:
    for n in (1, 2, 3, 4):
        want = P[0] + P[1]*n + P[2]*n*n + P[3]*n**3
        a = A_out[i]; b = B_out[i]; i += 1
        if str(want) != a or str(want) != b:
            bad += 1
            if bad < 6:
                print("MISMATCH", g, lam, mu, nu, "n=", n, "brion=", want, "A=", a, "B=", b)
print("checked", i, "stretched LR values against BOTH engines; mismatches =", bad)
