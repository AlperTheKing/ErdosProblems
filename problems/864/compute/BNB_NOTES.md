# Independent branch-and-bound solver

`solve_bnb.cpp` computes the exact maximum for the literal Problem 864
convention: unordered pairs `a <= b`, diagonals included, and at most one sum
value with multiple representations.  The exceptional value has no
multiplicity cap.

## Build and run

MinGW GCC:

```powershell
g++ -std=c++20 -O3 -DNDEBUG -pthread problems\864\compute\solve_bnb.cpp -o solve_bnb.exe
.\solve_bnb.exe --n 69 --threads 16 --timeout 3600
```

Clang:

```powershell
clang++ -std=c++20 -O3 -DNDEBUG -pthread problems\864\compute\solve_bnb.cpp -o solve_bnb.exe
```

`--timeout 0` (the default) has no deadline.  `--threads` is capped at 64.
`--heuristic-restarts 0` disables lower-bound heuristics; this does not change
the exact result.  Every two-element exact-search root is published before
recursion, so correctness does not depend on a heuristic incumbent.  Stdout is
newline-delimited JSON.  Candidate records
are independently checked from scratch.  The final record has status
`proof-complete`, `timeout`, or `internal-error`.  Exit codes are respectively
0, 2, and 3 (invalid command lines use 1).

## Exactness

The search uses one symmetry reduction.  Translating a nonempty set by
`a -> a-min(A)+1` shifts every pair sum by the same constant, preserves all
multiplicities, and leaves the translated set in `[1,N]`.  Thus some optimum
contains 1.  No reflection or exceptional-sum symmetry is assumed.

Subproblems are partitioned by the second-smallest selected element.  At each
node, adding `x` creates the distinct new sums `x+a` for old `a`, together with
`2x`.  The reversible state rejects exactly when these sums would make two
different repeated values.  Every feasible extension is a clique in the
node's pairwise compatibility graph, so a proper greedy coloring is a valid
cardinality upper bound even though pairwise compatibility is only a
relaxation of full admissibility.

The sum-capacity bound uses the fact that one fixed sum has at most
`ceil(k/2)` unordered representations.  Once the exceptional sum `e` is
known, each side of the split at `e/2` is an ordinary Sidon set; its positive
differences are distinct.  These facts only prune branches whose cardinality
cannot beat the incumbent.  Exhausting all subproblems therefore certifies the
reported maximum.  On timeout, the reported lower bound is witnessed and the
upper bound is the unconditional distinct-sum bound, not a claim of
optimality.
