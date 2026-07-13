# Fixed-exception CP-SAT sidecar

`fixed_exception_parallel.py` decides the literal finite Problem 864 question
at a fixed `N` and size exactly `k`. It uses unordered pairs `a <= b`, counts
diagonals, permits at most one repeated sum, and places no upper bound on that
sum's multiplicity.

## Exact branch partition

For each `s` the model contains

```text
x_a = 1 iff a is selected,
y_ab = x_a AND x_b for a < b,
y_aa = x_a,
r_s = sum(y_ab : a <= b and a+b=s).
```

The three linear constraints `y_ab <= x_a`, `y_ab <= x_b`, and
`y_ab >= x_a+x_b-1` encode each off-diagonal conjunction exactly. Every model
also imposes `sum(x_a)=k` and `x_1=1`.

The branches are disjoint and exhaustive:

1. The ordinary branch imposes `r_s <= 1` for every `s`.
2. The branch for `sigma` imposes `r_sigma >= 2` and `r_s <= 1` for every
   `s != sigma`.

A `sigma` branch is launched exactly when `[1,N]` has at least two ambient
unordered pairs summing to `sigma`. Values with fewer than two pairs cannot
satisfy `r_sigma >= 2`, so omitting them removes no candidate. An admissible
set has either no repeated sum or one unique repeated value, hence belongs to
exactly one launched branch.

## Translation normalization

The only symmetry constraint is `min(A)=1`. Let a nonempty candidate have
`m=min(A)` and define

```text
A' = {a-m+1 : a in A}.
```

Then `A'` is contained in `[1,N-m+1]`, hence in `[1,N]`, and has the same
cardinality. The map

```text
(a,b) -> (a-m+1,b-m+1)
```

is a bijection on unordered pairs, including diagonals, and sends sum `s` to
`s-2m+2`. It therefore preserves every representation multiplicity and shifts
the exceptional label without changing admissibility. Enumerating every
possible translated `sigma` proves that `x_1=1` loses no size-`k` candidate.
No reflection or endpoint normalization is used.

## Modes

`--mode existence` asks whether any branch contains a size-`k` candidate. One
self-checked candidate proves `FEASIBLE`; all branches must return
`INFEASIBLE` to prove global infeasibility. With no candidate, any timed-out or
otherwise unresolved branch makes the aggregate `UNKNOWN`.

`--mode min-multiplicity` minimizes the exceptional multiplicity over all
size-`k` candidates and all branches. The ordinary branch has multiplicity
zero. A fixed branch has the unconditional lower bound two.

`--mode max-unpaired` maximizes the number of elements not used by a
representation of the exceptional sum. For the ordinary branch all `k`
elements are defined to be unpaired. In a fixed branch, distinct
representations of one sum are element-disjoint except for the possible single
diagonal. If `d` is one when `sigma/2` is selected and zero otherwise, then

```text
paired elements   = 2*r_sigma-d,
unpaired elements = k-2*r_sigma+d.
```

The two optimization modes are independent, not a lexicographic objective.
They are intended for a `k` already known to be feasible, although an all-
branch infeasibility result is still reported correctly.

For optimization, `OPTIMAL` is emitted only when a checked incumbent equals
the aggregate lower bound (minimization) or upper bound (maximization).
Unresolved branches retain solver-independent integer bounds: `0` or `2` for
minimum multiplicity, and `k`, `k-3`, or `k-4` for maximum unpaired count as
applicable. CP-SAT's `BestObjectiveBound()` is intentionally excluded from
acceptance because its Python API is floating-point. Thus a timed-out branch
can be harmless only when its elementary integer bound cannot improve the
incumbent. Otherwise the aggregate status is `UNKNOWN`.

## Parallel execution and JSONL

Branches run in a `ProcessPoolExecutor`. `--workers` is capped at 64, and every
child sets `num_search_workers=1`, so at most 64 one-thread CP-SAT solvers run
concurrently. Python's Windows `ProcessPoolExecutor` has a 61-child limit, so
the runner uses 61 processes when `--workers 64` is requested there.
`--time-limit` is per branch; zero means no deadline.

The parent is the only JSONL writer. Stdout contains, in order:

1. one `run_start` record;
2. one `branch` record per completed branch, in completion order;
3. one final `aggregate` record.

`--output` mirrors the same lines to a file, replacing it unless `--append` is
given. Each candidate is checked from scratch before emission: domain, exact
size, `min(A)=1`, every unordered representation including diagonals, branch
membership, exceptional multiplicity, paired/unpaired elements, and objective
value. The aggregate winner is checked a second time. Solver infeasibility and
optimality statuses remain OR-Tools CP-SAT results, not independently emitted
proof certificates.

Aggregate statuses are:

- `FEASIBLE`: existence has a checked witness;
- `INFEASIBLE`: every branch is proved infeasible;
- `OPTIMAL`: an optimization incumbent meets the valid global bound;
- `UNKNOWN`: unresolved work leaves the requested decision or optimum open;
- `ERROR`: an execution/model error leaves the result open and no valid bound
  closes it.

Exit code is `0` for `FEASIBLE`, `INFEASIBLE`, or `OPTIMAL`; `2` for
`UNKNOWN`; and `3` for `ERROR`.

## Commands

```powershell
python problems/864/compute/fixed_exception_parallel.py --self-test

python problems/864/compute/fixed_exception_parallel.py `
  --N 70 --k 15 --mode existence --workers 64 --time-limit 3600 `
  --output problems/864/compute/fixed_N70_k15.jsonl

python problems/864/compute/fixed_exception_parallel.py `
  --N 100 --k 16 --mode min-multiplicity --workers 64 --time-limit 3600

python problems/864/compute/fixed_exception_parallel.py `
  --N 100 --k 16 --mode max-unpaired --workers 64 --time-limit 3600
```

The built-in self-test compares every branch and all three aggregate modes at
`N=12` against literal subset enumeration. It also checks all nonempty subsets
through `N=6` for the translation bijection, checks a diagonal collision, and
tests that an unresolved ordinary branch remains `UNKNOWN` in the global
minimum.
