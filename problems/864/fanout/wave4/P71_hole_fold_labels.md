# P71: affine lifting falsifies the unrestricted hole-restricted fold bound

## Verdict

The proposed inequality is **false without a positive-defect hypothesis**
for the allowed value `b=1`. There is an infinite affine family of
counterexamples. A concrete member is

\[
\begin{split}
B=\{&3,5,69,169,211,223,251,329,373,403,409,501,505,519,\\
    &631,689,715,775,863,883,915,931,953,977,987\},
\end{split}                                             \tag{1}
\]

with

\[
             p=25,\qquad h=988,\qquad b=1.             \tag{2}
\]

All unordered sums, including diagonals, are distinct, the literal hole
holds, and

\[
                    C_S=49>47=2p-3.                    \tag{3}
\]

Thus complementary inner-edge labels and the full sum/difference
disjointness alone do not imply the claimed bound. This does not falsify the
hard-regime statement with positive compensated defect.

## 1. Affine lifting lemma

Let

\[
 A\subseteq\{0,\ldots,h_0-1\},\qquad \max A=h_0-1,
\]

be an integer Sidon set, with diagonal sums included.  For an integer
`q>=2`, define

\[
 B_q=qA+(q-1),\qquad h_q=qh_0.                         \tag{4}
\]

Then:

1. `max B_q=h_q-1`;
2. `B_q` is integer Sidon, including its diagonal sums;
3. `C_{S(B_q)}(h_q)=C_{S(A)}(h_0)`; and
4. `Delta^+(B_q)` is disjoint from `B_q+B_q+1`.

### Proof

The endpoint identity is

\[
 q(h_0-1)+(q-1)=qh_0-1=h_q-1.                         \tag{5}
\]

Every unordered sum in `B_q` has the form

\[
 q(a+a')+2(q-1),\qquad a\le a',\quad a,a'\in A.       \tag{6}
\]

Equality of two expressions in (6) is equivalent to equality of the
corresponding sums in `A`.  This proves Sidonicity, including the case
`a=a'`.

If `s` and `s+h_0` are sums of `A`, their affine images in (6) differ by
`qh_0=h_q`.  Conversely, two sums in (6) differing by `h_q` have original
sums differing by `h_0`.  Hence the shifted-sum fold count is preserved
exactly.

Finally, every positive difference in `B_q` is divisible by `q`, whereas

\[
 (qa+q-1)+(qa'+q-1)+1
   =q(a+a'+2)-1\equiv-1\pmod q.                        \tag{7}
\]

Therefore

\[
 \Delta^+(B_q)\cap(B_q+B_q+1)=\varnothing.            \tag{8}
\]

This is the full literal hole: if
`x+y+z+1=w` with all four variables in `B_q`, then
`w-z=x+y+1` would belong to the forbidden intersection (8).  Repetitions,
including `x=y`, were not excluded.  This proves the lemma.  In particular,
one unconditioned violation yields infinitely many `b=1` violations, one
for every `q>=2`.

## 2. Concrete base and lifted counterexample

Use the exact P53 ruler

\[
\begin{split}
A=\{&1,2,34,84,105,111,125,164,186,201,204,250,252,259,315,\\
    &344,357,387,431,441,457,465,476,488,493\}
\end{split}                                             \tag{9}
\]

at `h_0=494`.  Its 325 unordered sums are distinct and it has 49
`h_0`-folds.  Taking `q=2` in (4) gives exactly (1) and (2).  The 49 lower
members of the folded sum pairs are

```text
10, 74, 138, 216, 228, 256, 292, 332, 338, 376,
380, 392, 398, 408, 414, 442, 446, 462, 502, 504,
506, 508, 574, 584, 596, 620, 632, 654, 658, 670,
688, 702, 718, 738, 758, 778, 806, 842, 848, 858,
874, 882, 904, 914, 918, 920, 952, 966, 986.
```

For every listed `s`, both `s` and `s+988` are unique unordered sums of
`B`.  Since all elements of `B` are odd, all positive differences are even
and all elements of `B+B+1` are odd.  This gives an immediate independent
parity check of the literal `b=1` hole.

## 3. Exact standalone verifier

The following uses integer arithmetic only.  It checks all diagonals, every
positive difference, the support version of the hole, the equivalent
four-variable literal hole with repetitions, and every shifted sum fold.

```python
from collections import Counter

B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501,
    505, 519, 631, 689, 715, 775, 863, 883, 915, 931, 953,
    977, 987,
]
p, h, b = len(B), 988, 1

sum_count = Counter()
for i, x in enumerate(B):
    for y in B[i:]:
        sum_count[x + y] += 1

diff_count = Counter()
for i, x in enumerate(B):
    for y in B[i + 1:]:
        diff_count[y - x] += 1

folds = sorted(s for s in sum_count if s + h in sum_count)
support_hole = set(diff_count).isdisjoint({s + b for s in sum_count})
literal_hole = not any(
    x + y + z + b == w
    for x in B for y in B for z in B for w in B
)

assert max(B) == h - 1
assert len(sum_count) == p * (p + 1) // 2
assert max(sum_count.values()) == 1
assert len(diff_count) == p * (p - 1) // 2
assert max(diff_count.values()) == 1
assert support_hole and literal_hole
assert len(folds) == 49
assert len(folds) > 2 * p - 3

print({"p": p, "h": h, "b": b, "C_S": len(folds),
       "bound": 2 * p - 3})
```

The output is

```text
{'p': 25, 'h': 988, 'b': 1, 'C_S': 49, 'bound': 47}
```

## 4. Scope

This falsifies the statement with the parameter `b` allowed to be either
member of `{1,2}`: the member `b=1` already fails.  The affine congruence
argument is specific to `b=1`; it does not decide the separate assertion
obtained by fixing `b=2` only.

It also does not decide the positive-defect form needed in the endpoint
argument. For this family,

\[
 \delta_q=\frac{3p^2-p+2}{2}-h_q=926-494q<0
 \qquad(q\ge2).
\]

The exact member (1) has `delta=-62`. Hence P71 kills only the unrestricted
hole-conditioned inequality. The candidate

\[
 \delta>0\quad\Longrightarrow\quad C_S\le 2p-3
\]

remains open.
