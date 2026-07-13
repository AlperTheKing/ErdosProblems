# A05: exact priority-queue generator

## Definition

Let

\[
A_0=\{2,3\},\qquad
A_{n+1}=A_n\cup\{xy-1:x,y\in A_n,\ x\ne y\},\qquad
A=\bigcup_{n\geq 0}A_n.
\]

For a positive integer `X`, the program computes
`A_X = A intersection {1,...,X}`. All integers are Python arbitrary-precision
integers. A census digest is SHA-256 of the ASCII string formed by joining the
increasing elements with commas and with no trailing newline.

Implementation:
[`generator.py`](../../compute/wave1/A05/generator.py). Tests:
[`test_generator.py`](../../compute/wave1/A05/test_generator.py).

## Algorithm

Maintain an increasing list `values` of accepted values, an `accepted` set, a
min-heap of candidate values, and a `queued` set that deduplicates the heap.
Initially accept the seeds at most `X`. Initial candidates are made with
`combinations(values, 2)`, so the two operands are distinct.

On removing the least candidate `v`, accept it. If there were `k` accepted
values before `v`, inspect exactly the pairs `(values[i], v)` for `0 <= i < k`,
in increasing `i`, and enqueue `values[i]*v-1` when it is at most `X`. The loop
stops at its first product above `X`. Here `values[i] < v`, so every inspected
pair has distinct operands. In particular, the pair `(v,v)` is never inspected.
Different distinct pairs may have the same product-minus-one; `queued` removes
only this candidate-value duplication and does not introduce any equal-operand
pair.

## Exactness lemma

**Lemma.** For every integer `X >= 1`, `generated_up_to(X)` terminates and
returns, in strictly increasing order, exactly `A intersection {1,...,X}`. Every
non-seed value returned has a derivation `xy-1` with `x,y in A`, `x != y`, and
`x,y` returned earlier.

**Proof.** First, every member of `A` is at least 2, by induction on its first
stage of appearance. If `x,y in A` and `x != y`, then

\[
xy-1-x=x(y-1)-1\geq1,
\quad
xy-1-y=y(x-1)-1\geq1.
\]

Thus every permitted child `xy-1` is strictly larger than each of its two
distinct operands. Consequently, a child at most `X` has both operands below
it and at most `X`; values above `X` can never be needed to generate a value at
most `X`.

Soundness follows by induction over heap removals. The seeds are in `A`. Every
initial non-seed candidate uses the sole unordered pair of distinct seeds.
Every later candidate is `xv-1`, where `x` was accepted before `v` and hence
`x < v`, so `x != v`; by the induction hypothesis both operands are in `A`.
Closure of `A` under products of distinct operands therefore puts the candidate
in `A`.

For ordering, every candidate inserted when `v` is accepted is larger than
`v`. The heap removes its least entry, so after accepting `v`, all later
removals are larger than `v`. This also proves that `values` stays increasing.
It makes the early `break` valid: for fixed `v`, `values[i]*v-1` increases with
`i`.

There are only `X` possible positive candidate values at most `X`. A value is
never queued twice simultaneously, and after it is removed it is accepted and
can never be queued again. Hence the loop terminates.

For completeness, suppose after termination that `t` is the least member of
`A intersection {1,...,X}` not accepted. It is not a seed. Taking the first
stage in which `t` appears gives `t=xy-1` for some `x,y in A` with `x != y`.
The growth inequality gives `x,y<t`; minimality of `t` says both were accepted.
Assume `x<y`. If `(x,y)=(2,3)`, the initial distinct-seed pairing queued `t`.
Otherwise, when `y` was accepted, `x` was among its strictly earlier values,
so the algorithm inspected the distinct pair `(x,y)` and queued `t` (or `t`
was already queued or accepted). Since `t<=X`, the bound check could not omit
it. At termination the heap is empty, contradicting that `t` was never
accepted. Therefore no such `t` exists. This proves exactness and the stated
distinct-operand derivation. QED.

## Tests and exact replay

From `problems/424/compute/wave1/A05`:

```powershell
python -m unittest -v
python generator.py --cross-check 10000
python generator.py --census 10 100 1000 10000 100000 1000000
```

The tests check every bound from 1 through 300 against a separate literal
fixed-point closure, check the full set at 5000 against that oracle, check
small boundary cases, and check the stated prefix. The oracle also uses only
`combinations(sorted(current), 2)`, hence never tests an equal-operand pair.
Observed output:

```text
Ran 5 tests in 0.260s
OK
OK X=10000 count=3207 sha256=936fc959fb34ba2e77477b66bc7e1d6d381e13b7abe378a08e5b7f3f56e8794f
X       count  density       decimal         max_element  sha256
10      4      2/5           0.400000000000  9            df96c726842c0826692d9a0762a042522a4602e350698430eef4d369eb5699f4
100     23     23/100        0.230000000000  99           5e2046e576568fe61a86971b63efc80d4f9553bdf07c94f3af58ef17dd249612
1000    250    1/4           0.250000000000  999          e48f2273cd087855176ae345df7ac830f0f6d333012668a605ba529430545a5c
10000   3207   3207/10000    0.320700000000  9999         936fc959fb34ba2e77477b66bc7e1d6d381e13b7abe378a08e5b7f3f56e8794f
100000  39843  39843/100000  0.398430000000  99999        8ea540464d0ef4ec231847fc3a7fc1aeca20da3332a6860be119fef27d29132c
1000000 457599 457599/1000000 0.457599000000 999999       cf19538b78162ed2bf89f1b99f99fc2eaad86b4f28607a8d4ead7451fed3098b
```

An independent ascending-divisor implementation was also compared
element-for-element at `X=100000`:

```powershell
$env:PYTHONPATH='problems/424/compute/wave1/A05;problems/424/compute/generator_b'
python -c "from generator import generated_up_to,canonical_digest; from generate_divisors import generate; a=generated_up_to(100000); b=generate(100000)[0]; assert a==b; print(f'OK X=100000 count={len(a)} sha256={canonical_digest(a)}')"
```

It prints:

```text
OK X=100000 count=39843 sha256=8ea540464d0ef4ec231847fc3a7fc1aeca20da3332a6860be119fef27d29132c
```

## Limitations

The exact fraction, not the decimal rendering, is the authoritative density
in each census row. Let `N_X=|A_X|` and let `P_X` be the number of unordered
distinct pairs `{x,y}` from `A_X` with `xy-1<=X`. The generator uses `O(N_X)`
stored integers and expected `O(P_X + N_X log N_X)` time under the standard
expected-constant-time model for Python sets. The literal fixed-point oracle is
intentionally much slower.

This proves exactness only for each finite truncation. The six census values,
including their apparent increase, do not imply any lower bound on the
infinite liminf and do not settle Problem 424.
