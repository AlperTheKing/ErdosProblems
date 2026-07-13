"""Exact obstruction to score-difference negative cycles."""
from itertools import permutations

# Two binary row coordinates.  00 is a strict Hamming-one local minimum,
# while the simultaneous two-row trade 00 -> 11 strictly lowers the score.
F = {(0, 0): 0, (1, 0): 2, (0, 1): 2, (1, 1): -1}

assert F[1, 0] - F[0, 0] == 2
assert F[0, 1] - F[0, 0] == 2
assert F[1, 1] - F[0, 0] == -1

# Every simple directed cycle in the Hamming square has zero total weight
# when edge weight is the exact potential difference F(v)-F(u).
V = list(F)
cycles = []
for k in range(2, 5):
    for cyc in permutations(V, k):
        if cyc[0] != min(cyc):
            continue
        closed = cyc + (cyc[0],)
        if all(sum(a != b for a, b in zip(closed[j], closed[j+1])) == 1
               for j in range(k)):
            total = sum(F[closed[j+1]] - F[closed[j]] for j in range(k))
            assert total == 0
            cycles.append((closed, total))

assert cycles
print("states=4 local_deltas=2,2 simultaneous_delta=-1")
print(f"simple_directed_cycles_checked={len(cycles)} all_cycle_sums=0")
