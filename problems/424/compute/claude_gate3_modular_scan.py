"""Gate-3 (R1 (43)-(46)) modular falsifier scan.
R_M = least subset of Z/M containing {2,3} closed under (r,s) -> r*s-1 (equal residues
ALLOWED => over-approximation of G mod M). U_q = {u mod q : (3u mod 3q) in R_{3q}}.
If U_q * U_q != Z/q for ANY q => density-one / cofinite R-A covering is globally
impossible (complete falsifier). Passing proves nothing.
Exact BFS closure; scan q in a list.
"""
import sys, hashlib

def closure_mod(M):
    R = set()
    frontier = [2 % M, 3 % M]
    R.update(frontier)
    while frontier:
        new = set()
        Rl = list(R)
        for a in frontier:
            for b in Rl:
                z1 = (a * b - 1) % M
                if z1 not in R and z1 not in new:
                    new.add(z1)
        frontier = list(new)
        R.update(new)
    return R

def scan(qs):
    fails = []
    for q in qs:
        M = 3 * q
        R = closure_mod(M)
        U = set(u for u in range(q) if (3 * (u % M)) % M in R or (3 * u) % M in R)
        # careful: u ranges mod q; 3u mod 3q depends on u mod q exactly (3(u+q) = 3u+3q ≡ 3u mod 3q) ✓
        UU = set((u * v) % q for u in U for v in U)
        ok = len(UU) == q
        print(f"q={q}: |R_{M}|={len(R)}/{M}  |U|={len(U)}/{q}  |U*U|={len(UU)}/{q}  {'OK' if ok else 'FAIL'}")
        if not ok:
            missing = sorted(set(range(q)) - UU)[:20]
            print(f"   FAIL classes (first 20): {missing}")
            fails.append(q)
    return fails

qs = list(range(2, 121)) + [125, 128, 169, 243, 256, 289, 343, 512]
fails = scan(qs)
print()
print("VERDICT:", ("FALSIFIED at q in " + str(fails)) if fails else "all scanned q PASS (U_q*U_q = Z/q)")
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
