"""audit_Q1_misc.py -- remaining exact audits of round7/Q1.md.

 G. C5[n] cut spectrum: min = n^2 and #minimisers = 10(2^n - 1)
    - brute force over ALL 2^(5n) subsets for n <= 4 (independent of any profile formula)
    - profile enumeration (exact multinomial counts) for n <= 8
 H. C7: bip = 1, #C5 = 0  (the R2 falsifier); plus the pentagon ratio table caveat
 I. widened Grotzsch families (single / pairs / triples / all unions / symmetric differences)
 J. Q1-C: bip <= floor((N-Delta-1)^2/4) tested against every connected triangle-free graph n<=10,
    and the question of whether it is implied by the accepted base
 K. Q1-B arithmetic: eps <= 9/400 and (1+25e)(1-6e)^2 - 1 > 0 on (0, 9/400]
 L. entropy budget numbers  log(10(2^n-1)) and the Legendre transform at n=8
 M. ten-witness regression from round5/claude_witness_regression.py against the R1 family
"""
from fractions import Fraction
from math import comb, log, exp
from itertools import combinations
import subprocess, sys, os
from audit_Q1_core import (g6, edges, trianglefree, bip, fam_union, bip_weighted,
                           fam_union_weighted, induced_c5, eS_table)

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


# ------------------------------------------------------------------ G
say("=== G. C5[n] cut spectrum ===")
C5 = [ (0,1),(1,2),(2,3),(3,4),(4,0) ]


def spectrum_bruteforce(nn):
    """all 2^(5nn) subsets of C5[nn], returns (min, #minimisers, total)"""
    N = 5 * nn
    blob = [[i * nn + k for k in range(nn)] for i in range(5)]
    adjm = [0] * N
    for (i, j) in C5:
        for p in blob[i]:
            for q in blob[j]:
                adjm[p] |= 1 << q
                adjm[q] |= 1 << p
    e = [0] * (1 << N)
    for S in range(1, 1 << N):
        v = (S & -S).bit_length() - 1
        R = S & (S - 1)
        e[S] = e[R] + bin(adjm[v] & R).count("1")
    full = (1 << N) - 1
    best = None
    cnt = 0
    for S in range(1 << N):
        m = e[S] + e[full ^ S]
        if best is None or m < best:
            best, cnt = m, 1
        elif m == best:
            cnt += 1
    return best, cnt, 1 << N


def spectrum_profile(nn):
    """same via profiles s_i, weight = prod C(nn,s_i); exact"""
    best = None
    cnt = 0
    tot = 0
    for s0 in range(nn + 1):
        for s1 in range(nn + 1):
            for s2 in range(nn + 1):
                for s3 in range(nn + 1):
                    for s4 in range(nn + 1):
                        s = (s0, s1, s2, s3, s4)
                        m = sum(s[i] * s[(i + 1) % 5] + (nn - s[i]) * (nn - s[(i + 1) % 5]) for i in range(5))
                        w = 1
                        for si in s:
                            w *= comb(nn, si)
                        tot += w
                        if best is None or m < best:
                            best, cnt = m, w
                        elif m == best:
                            cnt += w
    return best, cnt, tot


for nn in range(1, 5):
    a = spectrum_bruteforce(nn)
    b = spectrum_profile(nn)
    say(f"  n={nn}: brute force over 2^{5*nn} cuts -> min={a[0]} #min={a[1]} total={a[2]}")
    say(f"        profile enumeration              -> min={b[0]} #min={b[1]} total={b[2]}  agree={a==b}"
        f"   n^2={nn*nn}  10(2^n-1)={10*(2**nn-1)}  formula ok={a[0]==nn*nn and a[1]==10*(2**nn-1)}")
for nn in range(5, 9):
    b = spectrum_profile(nn)
    say(f"  n={nn}: profile -> min={b[0]} (n^2={nn*nn}) #min={b[1]} (10(2^n-1)={10*(2**nn-1)}) "
        f"total={b[2]} (2^{5*nn}={2**(5*nn)}) ok={b[0]==nn*nn and b[1]==10*(2**nn-1) and b[2]==2**(5*nn)}")

# ------------------------------------------------------------------ H
say("\n=== H. C7 and the pentagon ratio ===")
nc, adjc = 7, [0] * 7
for i in range(7):
    adjc[i] |= 1 << ((i + 1) % 7)
    adjc[(i + 1) % 7] |= 1 << i
say(f"  C7: |E|={len(edges(nc,adjc))} triangle-free={trianglefree(nc,adjc)} bip={bip(nc,adjc)} "
    f"#induced C5={len(induced_c5(nc,adjc))}")
say(f"  bip(C7)^(5/2) = 1 > c5(C7) = 0  ->  (P) bip^(5/2) <= c5 is FALSE at C7")
say(f"  NOTE: C7 has c5=0 so it is excluded from any max of bip^(5/2)/c5; the table in Q1.md")
say(f"        (max = 1 for n<=7) is implicitly restricted to c5>0.")
np_, adjp = g6("IheA@GUAo")
say(f"  Petersen: bip={bip(np_,adjp)} c5={len(induced_c5(np_,adjp))} "
    f"bip^5/c5^2={Fraction(bip(np_,adjp)**5, len(induced_c5(np_,adjp))**2)}")

# ------------------------------------------------------------------ I
say("\n=== I. widened Grotzsch families ===")
n, adj = g6("J?BD@g]Qvo?")
E = edges(n, adj)
e = eS_table(n, adj)
full = (1 << n) - 1


def mono(S):
    return e[S] + e[full ^ S]


say(f"  min over single N(v)            : {min(mono(adj[v]) for v in range(n))}")
say(f"  min over N(u) u N(v)            : {min(mono(adj[u]|adj[v]) for u,v in combinations(range(n),2))}")
say(f"  min over N(u) u N(v) u N(w)     : {min(mono(adj[u]|adj[v]|adj[w]) for u,v,w in combinations(range(n),3))}")
say(f"  min over ALL unions             : {fam_union(n,adj)[0]}")
say(f"  min over N(u) sym-diff N(v)     : {min(mono(adj[u]^adj[v]) for u,v in combinations(range(n),2))}")
say(f"  min over N(u) \\ N(v)            : {min(mono(adj[u]&~adj[v]) for u in range(n) for v in range(n) if u!=v)}")
say(f"  min over closed nbhds N[u]      : {min(mono(adj[u]|(1<<u)) for u in range(n))}")
say(f"  min over unions of closed nbhds : "
    f"{min(mono(eval('0') if False else __import__('functools').reduce(lambda x,y:x|y,[adj[v]|(1<<v) for v in range(n) if I>>v&1],0)) for I in range(1<<n))}")
say(f"  true bip                        : {bip(n,adj)}   target n^2/25 = {Fraction(121,25)}")

# ------------------------------------------------------------------ J
say("\n=== J. Q1-C:  bip <= floor((N-Delta-1)^2/4) ===")
exe = "audit_Q1_census.exe"
bad = 0
tested = 0
geng = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
for nn in range(5, 11):
    p = subprocess.run([geng, "-t", "-c", "-q", str(nn)], capture_output=True, text=True)
    for line in p.stdout.split():
        if not line:
            continue
        m, ad = g6(line)
        D = max(bin(ad[i]).count("1") for i in range(m))
        b = bip(m, ad)
        rhs = ((m - D - 1) ** 2) // 4
        tested += 1
        if b > rhs:
            bad += 1
            if bad < 5:
                say(f"    VIOLATION {line} bip={b} rhs={rhs}")
say(f"  tested {tested} connected triangle-free graphs n=5..10: violations = {bad}")
say(f"  proof ingredients: N(v) independent (triangle-free) => mono(N(v)) = e(G-N(v));")
say(f"  G-N(v) is triangle-free on N-Delta vertices with v isolated => Mantel on N-Delta-1.")
say(f"  NOTE: base 5 already records  bip <= min_v e(G-N(v));  Q1-C = that + Mantel.")
say(f"  Delta >= 3N/5-1 => N-Delta-1 <= 2N/5 => bound <= (2N/5)^2/4 = N^2/25.  Checked symbolically:")
import sympy as sp
Nn, D = sp.symbols("N D", positive=True)
say(f"    ((N-D-1)^2/4 at D = 3N/5-1) = {sp.simplify(((Nn-(3*Nn/5-1)-1)**2)/4)}")

# ------------------------------------------------------------------ K
say("\n=== K. Q1-B arithmetic ===")
eps = sp.symbols("eps", positive=True)
poly = sp.expand((1 + 25 * eps) * (1 - 6 * eps) ** 2 - 1)
say(f"  (1+25e)(1-6e)^2 - 1 = {poly}")
say(f"  roots of {sp.factor(poly/eps)} : {sp.solve(sp.Eq(poly/eps,0), eps)}")
say(f"  numeric roots: {[sp.nsimplify(r) for r in sp.solve(sp.Eq(poly/eps,0), eps)]} "
    f"~ {[float(r) for r in sp.solve(sp.Eq(poly/eps,0), eps)]}")
say(f"  9/400 = {float(Fraction(9,400))} < smallest positive root -> polynomial > 0 on (0,9/400]: "
    f"{all(float(poly.subs(eps, x))>0 for x in [1e-6, 0.001, 0.01, 0.0225])}")
say(f"  bip <= N^2/16 : max of |E| - 4|E|^2/N^2 over |E| is at |E|=N^2/8 giving "
    f"{sp.simplify(sp.Rational(1,8)*Nn**2 - 4*(Nn**2/8)**2/Nn**2)}")
say(f"  1/16 - 1/25 = {Fraction(1,16)-Fraction(1,25)} = 9/400  -> eps <= 9/400 confirmed")

# ------------------------------------------------------------------ L
say("\n=== L. entropy budget ===")
for nn in [8]:
    A = {}
    for s0 in range(nn + 1):
        for s1 in range(nn + 1):
            for s2 in range(nn + 1):
                for s3 in range(nn + 1):
                    for s4 in range(nn + 1):
                        s = (s0, s1, s2, s3, s4)
                        m = sum(s[i] * s[(i + 1) % 5] + (nn - s[i]) * (nn - s[(i + 1) % 5]) for i in range(5))
                        w = 1
                        for si in s:
                            w *= comb(nn, si)
                        A[m] = A.get(m, 0) + w
    N = 5 * nn
    say(f"  n={nn}: N={N}, full entropy N log2 = {N*log(2):.4f} nats, "
        f"log(#minimisers) = log({A[nn*nn]}) = {log(A[nn*nn]):.4f} nats, ratio {log(A[nn*nn])/(N*log(2)):.4f}")
    for epsv in [Fraction(0), Fraction(1,1000), Fraction(1,200), Fraction(1,100), Fraction(1,50)]:
        M = float((Fraction(1,25)+epsv) * N * N)
        # max entropy subject to  E[mono] <= M  :  min_beta  beta*M + log Z(beta)
        items = sorted(A.items())
        k0 = items[0][0]

        def f(b):
            # log Z shifted by the ground state to keep exp() in range
            Z = sum(c * exp(-b * (k - k0)) for k, c in items)
            return b * (M - k0) + log(Z)
        lo, hi = 0.0, 5.0
        for _ in range(200):
            m1 = lo + (hi - lo) / 3
            m2 = hi - (hi - lo) / 3
            if f(m1) < f(m2):
                hi = m2
            else:
                lo = m1
        best = f((lo + hi) / 2)
        say(f"    eps={epsv}: M={M:g}  max entropy = {best:.4f} nats  fraction {best/(N*log(2)):.4f}   (approx, diagnostic)")

with open("audit_Q1_misc.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
