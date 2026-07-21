"""Independent finite audit of the fixed irregular root-fibre obstruction.

This does not inspect a SAT encoding.  It checks the two stated fibres and
exhausts all labelled tournaments on R_7, confirming that regularity is
incompatible with the external-row equality forced by R_6.
"""

from itertools import combinations


R6 = (2, 3, 4, 5, 14)
R7 = (2, 3, 4, 5, 11)
CORE = tuple(sorted(set(R6) & set(R7)))
X = next(iter(set(R6) - set(CORE)))
Y = next(iter(set(R7) - set(CORE)))

assert CORE == (2, 3, 4, 5)
assert X == 14
assert Y == 11

pairs = tuple(combinations(R7, 2))
regular_count = 0
uniform_core_to_y_count = 0
patterns = set()

for mask in range(1 << len(pairs)):
    adjacency = {(v, w): 0 for v in R7 for w in R7}
    for bit, (a, b) in enumerate(pairs):
        if (mask >> bit) & 1:
            adjacency[a, b] = 1
        else:
            adjacency[b, a] = 1

    outdegrees = {
        v: sum(adjacency[v, w] for w in R7 if w != v) for v in R7
    }
    if any(outdegrees[v] != 2 for v in R7):
        continue

    regular_count += 1
    pattern = tuple(adjacency[v, Y] for v in CORE)
    patterns.add(pattern)
    assert sum(pattern) == 2
    if len(set(pattern)) == 1:
        uniform_core_to_y_count += 1

print(f"R6={R6}")
print(f"R7={R7}")
print(f"intersection={CORE}")
print(f"regular_tournaments_on_R7={regular_count}")
print(f"core_to_11_patterns={sorted(patterns)}")
print(f"uniform_core_to_11={uniform_core_to_y_count}")
print("certificate=UNSAT_LOCAL")

assert regular_count == 24
assert uniform_core_to_y_count == 0

