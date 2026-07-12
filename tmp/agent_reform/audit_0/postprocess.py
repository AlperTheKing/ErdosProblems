# exact-rational postprocess of scan_out.txt: forced kappa per graph, ranked
import re, sys
from fractions import Fraction
rows = []
for line in open("scan_out.txt"):
    m = re.match(r"(\S+) n=(\d+) e=(\d+) beta=(\d+) Rbest=(\d+) C5=(\d+) tr5mod10=(\d+) propA=(\S+)", line)
    if not m: continue
    name, n, e, beta, R, C5, t5m, pa = m.group(1), *map(int, m.groups()[1:7]), m.group(8)
    assert t5m == 0, ("tr(A^5) not divisible by 10 -> triangle or bug", name)
    assert pa == "OK", ("PROP-A VIOLATION", name)
    x = Fraction(25*beta, n*n)
    y = Fraction(3125*R, n**5)
    if x > 1:
        print("!!! CONJECTURE CE:", name, x); continue
    if x == 1:
        stat = "TIGHT-OK" if y >= 1 else "APS-NEEDS-INF(!!)"
        print(f"x=1 point: {name} y={y} {stat}")
        continue
    kap = (1-y)/(1-x)
    rows.append((kap, name, n, beta, R, C5, x, y))
rows.sort(reverse=True)
print(f"total graphs parsed: {len(rows)}")
print("== TOP 25 forced kappa (ALL-cut exact) ==")
for kap,name,n,beta,R,C5,x,y in rows[:25]:
    print(f"  {float(kap):8.4f} = {kap}  {name} N={n} beta={beta} Rbest={R} #C5={C5} x={x}")
over6 = [r for r in rows if r[0] > 6]
print(f"graphs forcing kappa > 6: {len(over6)}")
mx = max(rows)[0]
print(f"MAX forced kappa overall: {max(rows)[1]} = {mx} ({float(mx):.5f})")
# trend by N
byn = {}
for kap,name,n,*_ in rows:
    if n not in byn or kap > byn[n][0]: byn[n]=(kap,name)
print("== worst forced kappa by N ==")
for n in sorted(byn):
    print(f"  N={n:2d}: {float(byn[n][0]):8.4f}  {byn[n][1]}")
# cross-checks
for line in open("scan_out.txt"):
    if line.startswith("XCHK") or line.startswith("C13(1,5)[2]") or line.startswith("Petersen[2]") or line.startswith("Groetzsch[2]") or line.startswith("C5[5]"):
        print("XCHK/BLOWUP:", line.strip())
