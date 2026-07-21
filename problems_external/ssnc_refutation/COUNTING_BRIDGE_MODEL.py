"""One finite root-incidence model for the order-19 counting bridge.

This is not an oriented-graph or SSNC counterexample search.  It asks only
whether the exact parameter sums, target capacities, source incidence lower
bounds, missing-pair avoidance, linear block intersections, and disjoint-good
block lemma are jointly feasible in the irregular q=19, e=0 cell.
"""

from ortools.sat.python import cp_model


N = 19

# Missing graph: C9 on 0,...,8; leaves 9,10 at 0 and one leaf at 1,...,8.
missing_edges = {
    tuple(sorted((i, (i + 1) % 9))) for i in range(9)
}
missing_edges.update({(0, 9), (0, 10)})
missing_edges.update({(i, i + 10) for i in range(1, 9)})

mu = [4] + [3] * 8 + [1] * 10
root_sizes = [2 * degree - 1 for degree in mu]

model = cp_model.CpModel()
x = [[model.new_bool_var(f"x_{u}_{v}") for v in range(N)] for u in range(N)]

# Exact saturated target capacities and exact source incidence degree three.
for u in range(N):
    model.add(sum(x[u]) == root_sizes[u])
for v in range(N):
    model.add(sum(x[u][v] for u in range(N)) == 3)

# Literal unreachable incidences have zero diagonal.
for u in range(N):
    model.add(x[u][u] == 0)

# Saturated root blocks contain no missing pair.
for u in range(N):
    for a, b in sorted(missing_edges):
        model.add(x[u][a] + x[u][b] <= 1)

# A stronger condition than the counting bridge requires: blocks are linear.
for u in range(N):
    for w in range(u + 1, N):
        for a in range(N):
            for b in range(a + 1, N):
                model.add(x[u][a] + x[u][b] + x[w][a] + x[w][b] <= 3)

solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 1
solver.parameters.random_seed = 0
solver.parameters.max_time_in_seconds = 30.0
status = solver.solve(model)

status_name = solver.status_name(status)
print(f"status={status_name}")
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise SystemExit(1)

blocks = [tuple(v for v in range(N) if solver.value(x[u][v])) for u in range(N)]
rows = [tuple(u for u in range(N) if solver.value(x[u][v])) for v in range(N)]

for u, block in enumerate(blocks):
    print(f"R_{u}={block}")
for v, row in enumerate(rows):
    print(f"W_{v}={row}")

assert [len(block) for block in blocks] == root_sizes
assert all(len(row) == 3 for row in rows)
assert all(u not in blocks[u] for u in range(N))
assert all(
    not ({a, b} <= set(block))
    for block in blocks
    for a, b in missing_edges
)
assert all(
    len(set(blocks[u]) & set(blocks[w])) <= 1
    for u in range(N)
    for w in range(u + 1, N)
)
assert not any(root_sizes[u] == 3 for u in range(N))

print("checks=PASS")
print(f"sum_mu={sum(mu)} q={sum(mu)//2} sum_r={sum(root_sizes)}")
print("good_targets=0")

