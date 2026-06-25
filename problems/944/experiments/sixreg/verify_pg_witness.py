# Independent verification of the PG(2,5) v=0 witness colouring (2026-06-12).
# Rebuilds the incidence graph independently and checks: (a) colouring is a
# proper 3-colouring of G-0, (b) every colour appears exactly 2x on N(0).
WITNESS = ("0:-1 1:1 2:1 3:1 4:1 5:1 6:1 7:1 8:1 9:1 10:1 11:0 12:0 13:0 14:0 "
           "15:0 16:0 17:0 18:0 19:0 20:0 21:0 22:0 23:0 24:0 25:0 26:0 27:0 "
           "28:0 29:0 30:0 31:2 32:0 33:2 34:2 35:2 36:2 37:0 38:2 39:2 40:2 "
           "41:2 42:1 43:2 44:2 45:2 46:2 47:1 48:2 49:2 50:2 51:2 52:2 53:2 "
           "54:2 55:2 56:2 57:2 58:2 59:2 60:2 61:2")

reps = []
for a in range(5):
    for b in range(5):
        for c in range(5):
            if a == b == c == 0:
                continue
            if (a and a != 1) or (not a and b and b != 1) or (not a and not b and c != 1):
                continue
            reps.append((a, b, c))
assert len(reps) == 31, len(reps)

adj = {x: set() for x in range(62)}
for i in range(31):
    for j in range(31):
        if sum(reps[i][t] * reps[j][t] for t in range(3)) % 5 == 0:
            adj[i].add(31 + j)
            adj[31 + j].add(i)
assert all(len(adj[x]) == 6 for x in range(62)), "not 6-regular"

col = {}
for tok in WITNESS.split():
    v, c = tok.split(":")
    col[int(v)] = int(c)
assert col[0] == -1 and all(col[x] in (0, 1, 2) for x in range(1, 62))

# (a) properness on G - 0
bad = [(x, y) for x in range(1, 62) for y in adj[x] if y != 0 and y > x and col[x] == col[y]]
assert not bad, f"improper edges: {bad[:5]}"

# (b) counts on N(0)
from collections import Counter
cnt = Counter(col[w] for w in adj[0])
print("N(0) =", sorted(adj[0]), "colour counts:", dict(cnt))
assert all(v <= 2 for v in cnt.values()), "count >2"
print("VERIFIED: proper 3-colouring of G-0 with balanced (<=2,<=2,<=2) trace on N(0)")
