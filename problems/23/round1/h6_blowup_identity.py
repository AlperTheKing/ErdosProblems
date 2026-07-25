"""H6 sanity check: brute-force verification of the blow-up identity

    bip(G[t_1..t_n]) = min over cuts (S,S^c) of G of sum_{ij in E, same side} t_i t_j,

in particular bip(G[t]) = t^2 * bip(G) for balanced blow-ups.

Everything here is exhaustive: maxcut of the blow-up is computed by enumerating
ALL 2^(N-1) bipartitions of the blow-up itself (no heuristics), and compared with
the template-cut formula.  Integer arithmetic only.
"""
import itertools, sys

def parse_g6(s):
    s = s.strip()
    n = ord(s[0]) - 63
    bits = []
    for c in s[1:]:
        v = ord(c) - 63
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    E, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E

def to_g6(n, E):
    bits = []
    S = set(map(tuple, (tuple(sorted(e)) for e in E)))
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in S else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

def bip_bruteforce(n, E):
    """exhaustive: min over all 2^(n-1) bipartitions of #same-side edges"""
    best = len(E)
    for mask in range(1 << (n - 1)):
        m = mask << 1
        c = 0
        for (a, b) in E:
            if ((m >> a) & 1) == ((m >> b) & 1):
                c += 1
                if c >= best:
                    break
        if c < best:
            best = c
    return best

def blowup(n, E, t):
    """vertex-weighted blow-up: returns (N, edge list)"""
    start, N = [], 0
    for i in range(n):
        start.append(N)
        N += t[i]
    EE = []
    for (a, b) in E:
        for u in range(start[a], start[a] + t[a]):
            for v in range(start[b], start[b] + t[b]):
                EE.append((u, v))
    return N, EE

def template_formula(n, E, t):
    best = None
    for mask in range(1 << (n - 1)):
        m = mask << 1
        q = 0
        for (a, b) in E:
            if ((m >> a) & 1) == ((m >> b) & 1):
                q += t[a] * t[b]
        if best is None or q < best:
            best = q
    return best

def has_triangle(n, E):
    adj = [0] * n
    for (a, b) in E:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return any(adj[a] & adj[b] for (a, b) in E)

TESTS = {
    "C5":       (5, [(0,1),(1,2),(2,3),(3,4),(0,4)]),
    "C7":       (7, [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(0,6)]),
    "Petersen": (10, [(0,1),(1,2),(2,3),(3,4),(0,4),(5,7),(7,9),(9,6),(6,8),(8,5),
                      (0,5),(1,6),(2,7),(3,8),(4,9)]),
    "WagnerV8": (8, [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(0,7),
                     (0,4),(1,5),(2,6),(3,7)]),
    "C5+chordless_path": (6, [(0,1),(1,2),(2,3),(3,4),(0,4),(4,5),(5,1)]),
}

def main():
    print("== blow-up identity check: bip(G[t]) via exhaustive 2^(N-1) enumeration ==")
    for name, (n, E) in TESTS.items():
        assert not has_triangle(n, E), name
        b = bip_bruteforce(n, E)
        print(f"\n{name}: n={n} m={len(E)} g6={to_g6(n,E)}  bip(G)={b}  bip/n^2={b/n**2:.6f}")
        # balanced blow-ups
        for t in (1, 2, 3):
            if n * t > 20:
                continue
            tv = [t] * n
            N, EE = blowup(n, E, tv)
            assert not has_triangle(N, EE), "blow-up has a triangle!"
            exact = bip_bruteforce(N, EE)
            form = template_formula(n, E, tv)
            ok = (exact == form == t * t * b)
            print(f"  t={t}: N={N} exhaustive bip={exact}  formula={form}  t^2*bip(G)={t*t*b}  {'OK' if ok else 'MISMATCH'}")
            assert ok, (name, t, exact, form)
        # unbalanced blow-ups
        for tv in ([2,1,1,1,1], [3,1,2,1,1], [1,2,1,3,2]):
            if len(tv) != n or sum(tv) > 20:
                continue
            N, EE = blowup(n, E, tv)
            assert not has_triangle(N, EE)
            exact = bip_bruteforce(N, EE)
            form = template_formula(n, E, tv)
            print(f"  t={tv}: N={N} exhaustive bip={exact} formula={form} {'OK' if exact==form else 'MISMATCH'}")
            assert exact == form
    print("\nALL BLOW-UP IDENTITY CHECKS PASSED")

if __name__ == "__main__":
    main()
