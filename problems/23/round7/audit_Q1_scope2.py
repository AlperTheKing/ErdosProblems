"""audit_Q1_scope2.py -- second scope test (the first, on odd cycles alone, was inconclusive):
is the odd-BFS-layer cut ALWAYS a union of neighbourhoods, over the whole n<=10 census?
Plus: fam == bip for every integer weighting of C5 with sum <= 12 (the section-3 calibration).
"""
from collections import deque
import subprocess
from fractions import Fraction as F
from audit_Q1_core import g6, edges, eS_table, bip_weighted, fam_union_weighted

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


def unions(m, A):
    U = [0] * (1 << m)
    for S in range(1, 1 << m):
        v = (S & -S).bit_length() - 1
        U[S] = U[S & (S - 1)] | A[v]
    return set(U)


geng = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
say("=== is the odd-BFS-layer set always a union of neighbourhoods? (connected triangle-free n<=10) ===")
tot = 0
bad = 0
example = None
for nn in range(5, 11):
    p = subprocess.run([geng, "-t", "-c", "-q", str(nn)], capture_output=True, text=True)
    for line in p.stdout.split():
        m, A = g6(line)
        U = unions(m, A)
        for root in range(m):
            dist = [-1] * m
            dist[root] = 0
            dq = deque([root])
            while dq:
                v = dq.popleft()
                for w in range(m):
                    if A[v] >> w & 1 and dist[w] < 0:
                        dist[w] = dist[v] + 1
                        dq.append(w)
            odd = 0
            for v in range(m):
                if dist[v] % 2 == 1:
                    odd |= 1 << v
            tot += 1
            if odd not in U:
                bad += 1
                if example is None:
                    example = (line, root, sorted(v for v in range(m) if odd >> v & 1))
say(f"  rooted BFS instances tested: {tot};  odd-layer set NOT a union of neighbourhoods: {bad}")
say(f"  first example: {example}")

say("\n=== C5 calibration: fam == bip for every integer a with sum <= 12 ===")
n5, adj5 = g6("DUW")


def comps(k, tot_):
    if k == 1:
        yield (tot_,)
        return
    for v in range(tot_ + 1):
        for rest in comps(k - 1, tot_ - v):
            yield (v,) + rest


nbad = 0
ntest = 0
worst = None
for W in range(1, 13):
    for a in comps(5, W):
        b, _ = bip_weighted(n5, adj5, a)
        f, _ = fam_union_weighted(n5, adj5, a)
        ntest += 1
        if b != f:
            nbad += 1
        r = F(25 * b, W * W)
        if worst is None or r > worst[0]:
            worst = (r, a, W)
say(f"  tested {ntest} weight vectors on C5 (sum<=12): fam != bip in {nbad} cases")
say(f"  max 25*bip/W^2 = {worst[0]} at a={worst[1]} W={worst[2]}")

say("\n=== census total quoted in the summary ===")
counts = {5: 6, 6: 19, 7: 59, 8: 267, 9: 1380, 10: 9832, 11: 90842, 12: 1144061}
say(f"  sum over n=5..12 = {sum(counts.values())}   (summary says 1 236 380)")
say(f"  sum over n=1..12 = {sum(counts.values()) + 1 + 1 + 1 + 3}")

with open("audit_Q1_scope2.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
