# Independent brute-force cross-check of piece_hunt.exe results.
# For sampled pieces (g6, |Col|, frozenflag) from rec_m*.txt:
#   - decode g6, stubs at x = 6 - deg(x), |S| must be 8
#   - Col(P): enumerate ALL 3^m colourings, keep proper ones, project stub codes
#   - frozen flag: exists v such that NO proper colouring of P-v has every
#     colour used <= 2 times on N(v) cap V(P)   (eta-free criterion, derived
#     independently: v full => deficits sum to #v-stubs, so eta always fills)
# Compare both against the record line. Any mismatch = implementation bug.
import sys, itertools, random

def g6_decode(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        x = ord(ch) - 63
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j); adj[j].add(i)
            idx += 1
    return n, adj

def check_piece(g6, rec_tsize, rec_frozen):
    n, adj = g6_decode(g6)
    stubs = []          # ordered stub anchors: vertex order, 6-deg each
    for x in range(n):
        stubs += [x] * (6 - len(adj[x]))
    assert len(stubs) == 8, f"|S|={len(stubs)}"
    # all proper colourings (brute force over 3^n)
    proper = []
    for cols in itertools.product(range(3), repeat=n):
        if all(cols[u] != cols[v] for u in range(n) for v in adj[u] if u < v):
            proper.append(cols)
    codes = set()
    for cols in proper:
        code = sum(cols[stubs[s]] * 3**s for s in range(8))
        codes.add(code)
    ok_t = (len(codes) == rec_tsize)
    # frozen: some v with no proper colouring of P-v having N(v)-internal counts <= 2
    frozen = 0
    for v in range(n):
        rest = [x for x in range(n) if x != v]
        found = False
        for cols in itertools.product(range(3), repeat=n - 1):
            cmap = dict(zip(rest, cols))
            if any(cmap[u] == cmap[w] for u in rest for w in adj[u] if w != v and u < w):
                continue
            cnt = [0, 0, 0]
            for u in adj[v]:
                cnt[cmap[u]] += 1
            if max(cnt) <= 2:
                found = True
                break
        if not found:
            frozen = 1
            break
    ok_f = (frozen == rec_frozen)
    return ok_t, ok_f, len(codes), frozen

def main():
    random.seed(944)
    fails = 0
    total = 0
    for fn in sys.argv[1:]:
        lines = [l.split() for l in open(fn) if l.strip()]
        sample = random.sample(lines, min(12, len(lines)))
        for parts in sample:
            g6, m, tsz, fr = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
            ok_t, ok_f, t2, f2 = check_piece(g6, tsz, fr)
            total += 1
            tag = "OK" if (ok_t and ok_f) else "MISMATCH"
            if not (ok_t and ok_f):
                fails += 1
            print(f"{tag} {fn} {g6} rec(|T|={tsz},f={fr}) brute(|T|={t2},f={f2})")
    print(f"checked={total} FAILS={fails}")

if __name__ == "__main__":
    main()
