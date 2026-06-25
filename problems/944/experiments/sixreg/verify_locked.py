# Independent brute-force verification of locked-vertex COUNTS (piece_hunt
# 'locked' mode) on bipartite kappa=8 pieces. Pure python, shares no code.
# locked v <=> NO proper 3-colouring of P-v has every colour <=2 on N(v).
import sys, itertools

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

def locked_count(n, adj):
    edges = [(u, w) for u in range(n) for w in adj[u] if u < w]
    locked = 0
    for v in range(n):
        rest = [x for x in range(n) if x != v]
        pos = {x: i for i, x in enumerate(rest)}
        redges = [(pos[u], pos[w]) for (u, w) in edges if u != v and w != v]
        nbrs = [pos[u] for u in adj[v]]
        found = False
        for cols in itertools.product(range(3), repeat=n - 1):
            if any(cols[a] == cols[b] for (a, b) in redges):
                continue
            cnt = [0, 0, 0]
            for u in nbrs:
                cnt[cols[u]] += 1
            if max(cnt) <= 2:
                found = True
                break
        if not found:
            locked += 1
    return locked

def main():
    fails = total = 0
    for fn in sys.argv[1:]:
        for line in open(fn):
            parts = line.split()
            if len(parts) < 6:
                continue
            g6, m, tsz, lk = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
            n, adj = g6_decode(g6)
            bl = locked_count(n, adj)
            total += 1
            tag = "OK" if bl == lk else "MISMATCH"
            if bl != lk:
                fails += 1
            print(f"{tag} {g6} rec_locked={lk} brute_locked={bl}", flush=True)
    print(f"checked={total} FAILS={fails}")

if __name__ == "__main__":
    main()
