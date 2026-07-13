# Exact audit of `solve_bnb.cpp`

Date: 2026-07-12 (Europe/Istanbul)

Audited source SHA-256:
`A7AACE1AA2B04CF0711448B69377FA26FA3255E11D95314297CF9709B91C7B15`.
Toolchain: MSYS2 GCC 16.1.0, C++20, `-O3 -DNDEBUG -pthread` plus strict
warnings. Scope: literal semantics, incremental state, all branches and upper
bounds, symmetry, concurrency, terminal status, CP-SAT comparison, and the
independent candidate verifier.

## Verdict

The pruning bounds used for the OEIS-extension runs are sound. A fresh build
reproduced all six claimed endpoint equalities:

```text
F(70)=F(80)=14, F(81)=F(85)=15, F(86)=F(100)=16.
```

Monotonicity of `F` then proves the stated intervening values through 100.
The endpoint witnesses also pass `verify_census.py` after conversion to its
input schema.

There is one exact proof-status bug, outside the extension range:

```powershell
C:\tmp\solve_bnb_audit_gcc.exe --n 2 --threads 1 --heuristic-restarts 0
```

returns exit 0 and

```json
{"type":"result","n":2,"status":"proof-complete","lower_bound":1,"upper_bound":1,"maximum":1,"set":[1],"verified":true}
```

but `{1,2}` is a genuine Sidon set, so `F(2)=2`. The bug is not a false
pruning inequality. The exact-search root `{1,second}` is never published;
only states obtained by adding a third or later element are published at line
617. With zero heuristic restarts, lines 644-650 return before the increasing
greedy publishes `{1,2}`. Lines 887-903 nevertheless equate completion with
the incumbent and emit the false upper bound 1.

This falsifies the unqualified `proof-complete` contract and the statement in
`BNB_NOTES.md` lines 23-25 that disabling heuristics does not affect the exact
result. The minimal repair is to call
`shared.publish(state.chosen())` after lines 849-850 initialize every
second-element root and before line 855 calls `search`. No repair was made in
this audit.

The defect is sharply contained. For `N>=3`, `{1,2,3}` is admissible, so
`F(N)>=3`; every feasible searched state of size at least 3 is published when
its last element is added. Therefore the root-publication omission cannot
change a completed result for any OEIS-extension endpoint. For `N=2`, the
default positive restart count runs the increasing greedy and happens to
publish the correct pair, but correctness must not depend on that heuristic.

## Frozen convention

The source agrees with `STATEMENT.md` and the two Python programs:

- A representation is one unordered pair `(a,b)` with `a<=b`.
- Every diagonal `(a,a)` is counted.
- At most one sum value may have multiplicity at least 2.
- That exceptional value has no fixed multiplicity cap.
- `F(N)` maximizes cardinality over subsets of `[1,N]`.

`check_admissible` lines 47-83 sorts and range-checks a candidate, rejects
duplicates, loops over exactly `i<=j`, and counts all sums from 2 through
`2N`. It rejects exactly when a second distinct repeated sum value appears.
It imposes no cap on the surviving repeated value.

## Source-range audit

| Lines | Audit result |
|---|---|
| 32-45 | Options and checker result fields are adequate; no semantic branch is hidden here. |
| 47-83 | PASS: literal independent checker counts unordered pairs and diagonals exactly. |
| 85-96 | PASS: JSON array output is valid for integer sets. |
| 98-119 | PASS: `can_add(x)` tests every old-new sum and `2x`; these new sums are pairwise distinct because `x` is not already selected. |
| 121-153 | PASS: `add` updates exact counts, occupied slots, and the sole exception. A successful add creates at most one new occurrence of the known exception. |
| 156-173 | PASS: LIFO undo reverses every count and restores both exception fields. Search always obeys LIFO. |
| 175-209 | PASS: accessors are read-only; `uint16_t` counts cannot overflow because `N<=10000` and one sum has at most 5000 representations. |
| 211-233 | PASS: the universal distinct-sum timeout bound is sound. |
| 236-247 | PASS: the Sidon interval cap is the largest `k` satisfying `C(k,2)<=L-1`. |
| 249-283 | PASS: deadline/error flags are atomic; error text is mutex-protected. |
| 285-321 | PASS: every incumbent is independently checked before publication; `best_size` only increases through valid witnesses. |
| 324-352 | PASS: exception capacity counts every available complementary unordered pair, including a midpoint diagonal. |
| 354-382 | PASS: sum-slot capacity never underestimates the number of slots required by a feasible extension. Proof is below. |
| 384-449 | PASS: cardinality, coloring, sum-slot, and two Sidon-side caps are all upper bounds. |
| 451-547 | PASS: adjacency is pairwise compatibility; the greedy classes are independent sets, hence a proper coloring of the compatibility graph. |
| 549-580 | PASS: individually infeasible candidates are hereditary exclusions; raw cardinality and capacity pruning are sound. |
| 581-596 | PASS: reverse prefix coloring and the prefix capacity bound may return because color numbers are nondecreasing in `order`. |
| 598-623 | PASS with root caveat: child candidates are exactly earlier neighbors of `v`; recursion and undo are complete, but only the post-add state is published. |
| 626-642 | PASS: node aggregation and initialization helper do not affect search coverage. |
| 644-736 | Heuristics produce lower bounds only and all outputs are checked. FAIL at lines 648-650 in combination with the unpublished two-element roots: `R=0,N=2` loses the optimum. |
| 738-807 | PASS: numeric parsing is strict, limits are finite, and threads are capped at 64. |
| 809-823 | PASS: heuristics run before exact roots; roots partition translated sets by their unique second-smallest element. |
| 824-868 | PASS except root publication: atomic `fetch_add` assigns every root once; all workers join. The task cardinality prune at 844 uses the exact number `2+(N-second)` of possible root plus suffix elements. |
| 870-885 | PASS: a deadline noticed after apparent exhaustion is conservatively classified as timeout; the final witness is rechecked. |
| 887-930 | FAIL only for the root omission above: otherwise `complete` means no timeout/error after all roots joined. Timeout uses a sound unconditional upper bound and sets `maximum:null`. |
| 935-943 | PASS: command errors cannot be mislabeled proof-complete. |

## Bound proofs

### Fixed-sum multiplicity

For a fixed sum `e`, every element belongs to at most one representation,
namely `{x,e-x}`. Distinct unordered representations are vertex-disjoint,
except that there may be one one-vertex diagonal `{e/2,e/2}`. Hence a
`k`-element set has at most `ceil(k/2)` representations of `e`. Thus, among
the `P(k)=k(k+1)/2` unordered pair occurrences, concentrating all repetitions
at one value saves at most `ceil(k/2)-1` distinct sums. Lines 217-233 correctly
require

```text
P(k) - ceil(k/2) + 1 <= 2N-1.
```

### Incremental sum-slot bound

Suppose the current size is `k`, target size is `K`, and `t=K-k`. Exactly
`P(K)-P(k)` pair occurrences are new. All repetitions among those occurrences
must be at the one exceptional value.

If no exception exists yet, let `q` be the number of new occurrences at the
eventual exception. If that sum already had one old occurrence, the saving is
`q<=t`; otherwise the saving is `q-1<t`. Also its final multiplicity is at
most `ceil(K/2)`. Lines 365-367 use the possibly loose but valid cap
`min(t,ceil(K/2)-1)`.

If the exception already exists, each new representation uses a distinct new
element, so there are at most `t`. Lines 324-352 give the further exact
availability cap by counting complementary pairs in `chosen union candidates`.
Lines 369-375 take the minimum of availability, `ceil(K/2)`, and current
multiplicity plus `t`. Subtracting current multiplicity is exactly the maximum
number of saved new occurrences.

All other new occurrences need different, previously unoccupied sum values.
If the largest available element is `M`, every old or future sum lies in
`[2,2M]`, which has `2M-1` slots. Therefore lines 377-381 compare a lower
bound on fresh slots needed with the exact number of currently free slots in
that domain. A feasible target size can never fail this test.

### Sidon-side capacity

Once exception `e` exists, split at `floor(e/2)`. Two distinct sum
representations wholly in the high side have sum greater than `e`, impossible.
Two wholly in the low side have sum at most `e`; equality can only be the
single diagonal `{e/2,e/2}`, so it cannot repeat. Each side is therefore an
ordinary Sidon set, including the even-midpoint case.

A Sidon subset of an interval of length `L` has all `C(q,2)` positive
differences distinct in `[1,L-1]`, hence `C(q,2)<=L-1`. Lines 407-441 include
all chosen and still-available elements when computing each side's span and
count, so each resulting cap is at least the cardinality of any feasible
selected side. Summing the two caps is sound.

### Clique coloring and recursion

At a node, vertices are individually addable candidates and an edge means the
base together with that pair is admissible. Every feasible extension is a
clique because admissibility is hereditary under deletion. Lines 481-492
construct exactly this compatibility graph. Lines 517-545 greedily partition
vertices into independent sets, so a clique uses at most one vertex per color.
The recorded color number is therefore a valid clique cap for every emitted
prefix.

The recursion scans the colored order backward. For any nonempty feasible
extension, take its highest-index vertex `v`; all its other vertices are
earlier neighbors and therefore occur in `child_candidates`. Induction covers
that extension. Returning when a prefix color/capacity bound cannot beat the
incumbent is sound. Pairwise compatibility is only a relaxation, which can
increase an upper bound but cannot make it falsely small.

## Symmetry and partition

For nonempty `A`, put `m=min(A)` and translate every element by `1-m`. Every
pair sum is translated by the same constant `2(1-m)`, so every multiplicity is
preserved. The translated set lies in `[1,N-m+1]`, hence in `[1,N]`, and
contains 1. Since `N>=1` has a nonempty optimum, forcing 1 loses no optimum.

Every translated set of size at least 2 has a unique second-smallest element.
Lines 819-855 assign exactly one root to it and restrict all later values to
the suffix above it. No reflection or guessed exceptional sum is imposed.

## Concurrency and terminal status

- `next_task.fetch_add` gives each second-element root to exactly one worker.
- Each worker owns its `State`, recursion, and local node count.
- `best_size` is atomic and monotone. A stale smaller load only reduces
  pruning; every observed larger value came from an independently verified
  witness, so pruning against it is valid.
- `best_set`, output, and error text are protected by the shared mutex.
- A stale `stop=false` can only cause extra work. `stop=true` arises only from
  timeout or internal error, either of which prevents `proof-complete`.
- All workers join before final status and witness capture.
- A deadline crossed without an in-search poll is checked again at lines
  870-872, conservatively producing timeout.

Subject to the `N=2,R=0` publication defect, a `proof-complete` terminal record
means all translated roots were exhausted under proved upper bounds, and its
incumbent is a valid set. Thus for every `N>=3`, its equal lower/upper value is
exactly `F(N)`. For the six audited extension endpoints this proves the finite
values, not merely witness feasibility.

The JSON line itself is not a portable proof certificate. `verify_census.py`
correctly labels `optimality_certificate_checked:false`; it verifies witness
and metadata only. Global optimality remains certified by the audited program
and completed execution.

## Python cross-audit

`solve_cpsat.py` is semantically exact: diagonal terms are `x[a]`; each
off-diagonal term is constrained to the conjunction `x[a] and x[b]`; and
lines 67-68 make `z_s` equivalent to representation count at least 2. The sum
of all `z_s` is at most one. Its only symmetry is `x[1]=1`, justified above.
Only OR-Tools status `OPTIMAL` sets `finite_optimum_certified:true`.

`verify_census.py` independently enumerates `i<=j` pairs and diagonals and
rejects more than one repeated value. Its one-exception maximum-Sidon-subset
formula is exact: the representations of the exception are disjoint, and at
least one element must be removed from all but one of them. Its metadata check
does not prove a claimed global bound, as documented.

One ancillary documentation mismatch was found: `COMPUTATION.md` line 19 says
the 13 verifier self-tests include an exhaustive `[1,8]` subset cross-check,
but the current 13 methods in `VerifierSelfTests` contain no such exhaustive
test. This does not affect the BnB endpoint proof; the independent exhaustive
tests below replace that missing check for this audit.

## Commands and results

Strict fresh build (no warnings):

```powershell
g++ -std=c++20 -O3 -DNDEBUG -pthread -Wall -Wextra -Wpedantic `
  -Wconversion -Wshadow problems\864\compute\solve_bnb.cpp `
  -o C:\tmp\solve_bnb_audit_gcc.exe
```

Verifier regression suite:

```powershell
python problems/864/compute/verify_census.py --self-test
```

Result: 13 tests run, all `ok`.

Literal brute force enumerated every one of the
`sum(2^N,N=1..18)=524286` subsets. For each `N`, it counted sums with nested
`i<=j` loops, retained sets with at most one count at least 2, and compared the
maximum with four BnB runs `(threads,restarts)=(1,0),(4,0),(1,7),(4,7)`.
Result:

```text
N       1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
brute   1  2  3  3  4  4  5  5  5  5  6  6  6  6  7  7  7  7
BnB R=0 1  1  3  3  4  4  5  5  5  5  6  6  6  6  7  7  7  7
BnB R=7 1  2  3  3  4  4  5  5  5  5  6  6  6  6  7  7  7  7
```

The one- and four-thread results were identical in every row. CP-SAT with

```powershell
python problems/864/compute/solve_cpsat.py --range 1 18 `
  --workers 1 --time-limit 60
```

returned `OPTIMAL` and the brute-force sequence above for all 18 values.

An internal temporary harness included the audited source in one translation
unit and, for all ternary base/candidate assignments through `N=10`, compared
`State::can_add`, raw `extension_upper_bound`, every colored-prefix bound, and
the feasible-extension clique property against literal exhaustive subsets.
Harness SHA-256:
`10463C46805EF302C5313B9A209E022613AE68E37A4F8AD05A073EC7DE262947`.

```powershell
g++ -std=c++20 -O3 -DNDEBUG -pthread -Wall -Wextra -Wpedantic `
  -Wconversion -Wshadow C:\tmp\bnb_bound_harness.cpp `
  -o C:\tmp\bnb_bound_harness.exe
C:\tmp\bnb_bound_harness.exe
```

Result:

```text
PASS states=70933 raw_bounds=70933 colored_prefix_bounds=188030 feasible_extensions=1262767
```

Concurrency stress, always with `--heuristic-restarts 0`, compared 1, 2, 8,
32, and 64 threads. Every completed run agreed:

```text
F(20)=8, F(25)=9, F(30)=9, F(35)=10.
```

Timeout classification:

```powershell
C:\tmp\solve_bnb_audit_gcc.exe --n 100 --threads 4 `
  --heuristic-restarts 0 --timeout 0.000001
```

Result: exit 2, `status:"timeout"`, witnessed lower bound 1, unconditional
upper bound 19, and `maximum:null`.

Fresh production endpoint command:

```powershell
70,80,81,85,86,100 | ForEach-Object {
  C:\tmp\solve_bnb_audit_gcc.exe --n $_ --threads 32 --timeout 0 |
    Select-String '"type":"result"'
}
```

Result (total shell wall time 371.2 seconds):

| N | maximum | nodes | elapsed seconds | exception | multiplicity |
|---:|---:|---:|---:|---:|---:|
| 70 | 14 | 3,491,517 | 3.013084 | 70 | 7 |
| 80 | 14 | 19,332,154 | 17.134796 | 75 | 7 |
| 81 | 15 | 17,859,089 | 20.718978 | 82 | 8 |
| 85 | 15 | 31,214,103 | 41.898000 | 86 | 8 |
| 86 | 16 | 29,919,099 | 38.997634 | 87 | 8 |
| 100 | 16 | 221,447,050 | 248.969748 | 100 | 8 |

All six terminal records had exit 0, `status:"proof-complete"`, equal lower
and upper bounds, and `verified:true`. Independent `verify_census.py` analysis
found exactly one repeated sum in every witness. The respective
`(unordered-pair count, distinct-sum count)` values were `(105,99)`,
`(105,99)`, `(120,113)`, `(120,113)`, `(136,129)`, and `(136,129)`.
