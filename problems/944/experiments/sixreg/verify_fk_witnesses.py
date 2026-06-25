# Independent verification of ALL 62 (FK)-refutation witnesses (2026-06-12).
# H* = PG(2,5) incidence minus edges (0,32),(7,41),(15,33).
# For each v: check the witness is a proper 3-colouring of H*-v with every
# colour appearing <=2 times on N_{H*}(v). Also re-derive H* invariants.
import re
from collections import Counter

reps = []
for a in range(5):
    for b in range(5):
        for c in range(5):
            if a == b == c == 0:
                continue
            if (a and a != 1) or (not a and b and b != 1) or (not a and not b and c != 1):
                continue
            reps.append((a, b, c))
assert len(reps) == 31

adj = {x: set() for x in range(62)}
for i in range(31):
    for j in range(31):
        if sum(reps[i][t] * reps[j][t] for t in range(3)) % 5 == 0:
            adj[i].add(31 + j)
            adj[31 + j].add(i)
for a, b in [(0, 32), (7, 41), (15, 33)]:
    adj[a].discard(b)
    adj[b].discard(a)

degs = Counter(len(adj[x]) for x in range(62))
sum_b = sum(6 - len(adj[x]) for x in range(62))
n_full = sum(1 for x in range(62) if len(adj[x]) == 6)
print(f"H*: degree profile {dict(degs)}, sum_b={sum_b}, full vertices={n_full}")
assert sum_b == 6 and n_full == 56

ok = 0
for line in open(r"E:\Projects\ErdosProblems\problems\944\experiments\sixreg\fk_witnesses.txt"):
    m = re.match(r"WITNESS v=(\d+): (.+)", line)
    if not m:
        continue
    v = int(m.group(1))
    col = [int(t) for t in m.group(2).split()]
    assert len(col) == 62 and col[v] == -1
    assert all(col[x] in (0, 1, 2) for x in range(62) if x != v)
    for x in range(62):
        if x == v:
            continue
        for y in adj[x]:
            if y != v and col[x] == col[y]:
                raise AssertionError(f"v={v}: improper edge ({x},{y})")
    cnt = Counter(col[w] for w in adj[v])
    if any(c > 2 for c in cnt.values()):
        raise AssertionError(f"v={v}: bad trace {dict(cnt)}")
    ok += 1
print(f"VERIFIED: {ok}/62 witnesses are proper 3-colourings of H*-v with <=2 per colour on N(v)")
assert ok == 62
print("(FK) REFUTED: H* has NO frozen vertex at all (a fortiori no frozen full vertex)")
