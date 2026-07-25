"""audit_Q2_v2_c.py -- AUDIT pass 2, block C: exhaustive maximal-triangle-free N<=12.

Own geng invocation, own graph6 decoder, own maximality filter, own max-cut,
own switch-star / family-(*) tests.  All integer arithmetic.
"""
import sys, subprocess
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_v2_core import (g6, g6_encode, pc, edges, is_trianglefree, is_maximal_tf,
                              mono, sigma, delta_recompute, delta_formula, indep_sets)

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
HR = "=" * 78
print(HR); print("C1  counts of maximal triangle-free graphs (own geng + own filter)")
print(HR)
Q2counts = {3: 1, 4: 2, 5: 3, 6: 4, 7: 6, 8: 10, 9: 16, 10: 31, 11: 61, 12: 147}
graphs = {}
for n in range(3, 13):
    out = subprocess.run([GENG, "-t", "-c", str(n)], capture_output=True, text=True).stdout.split()
    keep = []
    for line in out:
        nn, adj = g6(line)
        if is_maximal_tf(nn, adj):
            keep.append((line, nn, adj))
    graphs[n] = keep
    flag = "ok" if Q2counts[n] == len(keep) else f"<<< MISMATCH Q2.md says {Q2counts[n]}"
    print(f"   n={n:3d}: {len(keep):5d}   (Q2.md {Q2counts[n]:5d})  {flag}   "
          f"[connected tri-free total {len(out)}]")
tot = sum(len(graphs[n]) for n in range(5, 13))
print(f"   total 5<=n<=12 = {tot}   Q2.md says 278   {'ok' if tot==278 else 'MISMATCH'}")
# also count DISCONNECTED maximal triangle-free graphs (geng -t -c drops them)
dis = 0
for n in range(3, 10):
    out = subprocess.run([GENG, "-t", str(n)], capture_output=True, text=True).stdout.split()
    for line in out:
        nn, adj = g6(line)
        if is_maximal_tf(nn, adj):
            comp = [False] * nn
            st = [0]; comp[0] = True
            while st:
                x = st.pop()
                for y in range(nn):
                    if (adj[x] >> y) & 1 and not comp[y]:
                        comp[y] = True; st.append(y)
            if not all(comp):
                dis += 1
print(f"   disconnected maximal triangle-free graphs on 3..9 vertices = {dis} "
      f"(so 'connected' is not a restriction here)")

print(); print(HR); print("C2  PART A (maximum cuts) / PART B (locally-good, bound-violating)")
print(HR)


def star_ok(n, adj, Y, sg):
    for v in range(n):
        yv = (Y >> v) & 1
        NB = adj[v] & (Y if not yv else ~Y) & ((1 << n) - 1)
        rhs = 0
        j = NB
        while j:
            b = j & -j; k = b.bit_length() - 1; j ^= b
            if 2 - sg[k] > 0:
                rhs += 2 - sg[k]
        if sg[v] < rhs:
            return False
    return True


def star_family_ok(n, adj, Y, indcache):
    for v in range(n):
        Nv = adj[v]
        for T in indcache[v]:
            if delta_recompute(n, adj, Y, Nv | T) > 0:
                return False
    return True


nmax = 0
partA = 0
failA_bound = failA_charge = failA_star = 0
partB = []
for n in range(5, 13):
    for (line, nn, adj) in graphs[n]:
        full = (1 << nn) - 1
        indcache = [indep_sets(nn, adj, full & ~adj[v]) for v in range(nn)]
        monos = [mono(nn, adj, Y) for Y in range(1 << (nn - 1))]
        best = min(monos)
        for Y in range(1 << (nn - 1)):
            M = monos[Y]
            sg = sigma(nn, adj, Y)
            if M == best:
                partA += 1
                if 25 * M > nn * nn:
                    failA_bound += 1
                    print("   PART-A BOUND FAILURE", line, hex(Y), M)
                dM = [(pc(adj[v]) - sg[v]) // 2 for v in range(nn)]
                summu = sum(F(nn) - F(25, 2) * dM[v] for v in range(nn))
                if summu != nn * nn - 25 * M:
                    failA_charge += 1
                    print("   PART-A CHARGE FAILURE", line, hex(Y))
                if not star_family_ok(nn, adj, Y, indcache):
                    failA_star += 1
                    print("   PART-A (*) FAILURE", line, hex(Y))
            if 25 * M > nn * nn:
                if all(s >= 0 for s in sg) and star_ok(nn, adj, Y, sg) and \
                   star_family_ok(nn, adj, Y, indcache):
                    partB.append((line, nn, Y, M))
print(f"   maximum cuts examined (vertex 0 pinned) = {partA}   Q2.md says 587  "
      f"{'ok' if partA==587 else '<<< MISMATCH'}")
print(f"   PART A failures of 25|M| <= N^2 : {failA_bound}   (Q2.md: 0)")
print(f"   PART A charge-identity failures : {failA_charge}   (Q2.md: 0)")
print(f"   PART A (*) failures             : {failA_star}   (Q2.md: 0)")
print(f"   PART B (sigma>=0 + switch-star + (*) but 25|M|>N^2) : {len(partB)}   "
      f"Q2.md says 15  {'ok' if len(partB)==15 else '<<< MISMATCH'}")
gs = sorted(set(x[0] for x in partB))
print(f"   distinct graphs carrying them: {len(gs)}  {gs}")
bestr = None
for (line, nn, Y, M) in partB:
    print(f"      {line:14s} N={nn} cut=0x{Y:x} M={M} 25M-N^2=+{25*M-nn*nn}  "
          f"25M/N^2={F(25*M, nn*nn)}")
    r = F(25 * M, nn * nn)
    if bestr is None or r > bestr[0]:
        bestr = (r, line, Y, M)
print(f"   best PART-B ratio = {bestr[0]} at {bestr[1]} cut=0x{bestr[2]:x} M={bestr[3]}   "
      f"Q2.md says 150/144 = {F(150,144)}  {'ok' if bestr[0]==F(150,144) else 'MISMATCH'}")

print(); print(HR); print("C3  is the champion K??FF?^Fvw^_ the blow-up C5[2,2,3,2,3] = W*(1,1)?")
print(HR)
line = "K??FF?^Fvw^_"
n, adj = g6(line)
print(f"   decoded n={n} |E|={len(edges(n,adj))} tri-free={is_trianglefree(n,adj)} "
      f"maximal={is_maximal_tf(n,adj)}")
seen = {}
for v in range(n):
    seen.setdefault(adj[v], []).append(v)
cl = list(seen.values())
print(f"   twin classes (identical neighbourhoods): {cl}  sizes {[len(c) for c in cl]}")
q = len(cl)
qadj = [[1 if (adj[cl[i][0]] >> cl[j][0]) & 1 else 0 for j in range(q)] for i in range(q)]
print("   quotient adjacency:")
for row in qadj:
    print("      " + "".join(map(str, row)))
deg = [sum(r) for r in qadj]
iscycle = q == 5 and all(d == 2 for d in deg)
# walk the cycle to read off the class sizes in cyclic order
order = [0]
prev = -1
cur = 0
for _ in range(4):
    nxt = [j for j in range(q) if qadj[cur][j] and j != prev][0]
    order.append(nxt); prev, cur = cur, nxt
sizes = [len(cl[i]) for i in order]
print(f"   quotient is a 5-cycle: {iscycle};  class sizes in cyclic order = {sizes}")
print(f"   -> G = C5{sizes};  Q2.md claims C5[2,2,3,2,3] = W*(1,1)")
rot = [sizes[i:] + sizes[:i] for i in range(5)]
rot += [list(reversed(r)) for r in rot]
print(f"   equals C5[2,2,3,2,3] up to rotation/reflection: {[2,2,3,2,3] in rot}")
