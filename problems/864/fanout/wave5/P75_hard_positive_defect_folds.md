# P75: exact positive-defect counterexample to the P65 fold bound

## Verdict

The surviving implication is **false**, already for `b=1`.  With the
P45/P46/P65 convention `max(B)=h-1`, take

\[
\begin{split}
B=\{&3,5,69,169,211,223,251,329,373,403,409,501,505,519,\\
    &631,639,689,715,775,863,883,915,931,953,977,987\}.
\end{split}                                             \tag{1}
\]

Then

\[
 p=26,\qquad h=988,\qquad b=1,\qquad
 \delta={3p^2-p+2\over2}-h=14>0,                       \tag{2}
\]

all unordered sums (including the diagonals) are distinct, the literal
hole holds, and

\[
 C_S=51>49=2p-3.                                       \tag{3}
\]

Thus positive defect does not repair the unrestricted P71 affine lift.
The P65 bound cannot be used in the completion argument.

## 1. Construction from P71

Let `A` be the 25-mark P71 ruler at `h=988`, and adjoin the single mark
`639`.  An exhaustive exact scan of the 469 odd candidates in `[1,986]`
finds that `639` is the unique candidate preserving integer Sidonicity.
It creates exactly two new shifted-sum folds:

\[
 3+639+988=715+915,\qquad
 223+639+988=863+987.                                  \tag{4}
\]

The original P71 ruler has 49 folds, so (4) raises the count to 51.
Increasing the order from 25 to 26 changes the defect from `-62` to

\[
 {3\cdot26^2-26+2\over2}-988=1002-988=14.             \tag{5}
\]

Every mark in (1) is odd.  Consequently every positive difference is
even, whereas every element of `B+B+1` is odd.  Therefore

\[
 \Delta^+(B)\cap(B+B+1)=\varnothing.                  \tag{6}
\]

By the exact equivalence in P65, (6) is the full literal condition

\[
 -1\notin3B-B,                                         \tag{7}
\]

with all repeated-variable cases included.

## 2. Exact fold certificate

The 51 lower members `s` for which both `s` and `s+988` are unordered
sums are

```text
10, 74, 138, 216, 228, 256, 292, 332, 338, 376,
380, 392, 398, 408, 414, 442, 446, 462, 502, 504,
506, 508, 574, 584, 596, 620, 632, 642, 654, 658,
670, 688, 702, 718, 738, 758, 778, 806, 842, 848,
858, 862, 874, 882, 904, 914, 918, 920, 952, 966,
986
```

Exact enumeration gives

\[
 |B+B|={26\cdot27\over2}=351,\qquad
 |\Delta^+(B)|={26\cdot25\over2}=325,                 \tag{8}
\]

and every representation count in (8) is one.  The SHA-256 of the
comma-separated list (1), with no spaces, is

```text
5652cbb942876b59a3584fff40c45a0d96f127978f04c3e5837bedfbc262fa53
```

## 3. Standalone exact verifier

The following checker uses integer arithmetic only.  It independently
checks every diagonal-inclusive unordered sum, every positive difference,
the support form and direct four-variable form of the hole, the defect, and
all shifted folds.

```python
from collections import Counter

B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
p, h, b = len(B), 988, 1

sum_count = Counter(
    x + y for i, x in enumerate(B) for y in B[i:]
)
diff_count = Counter(
    y - x for i, x in enumerate(B) for y in B[i + 1:]
)

folds = sorted(s for s in sum_count if s + h in sum_count)
support_hole = set(diff_count).isdisjoint(
    {s + b for s in sum_count}
)
literal_hole = not any(
    x + y + z + b == w
    for x in B for y in B for z in B for w in B
)
delta = (3 * p * p - p + 2) // 2 - h

assert max(B) == h - 1
assert len(sum_count) == p * (p + 1) // 2
assert max(sum_count.values()) == 1
assert len(diff_count) == p * (p - 1) // 2
assert max(diff_count.values()) == 1
assert support_hole and literal_hole
assert delta == 14 > 0
assert len(folds) == 51
assert len(folds) > 2 * p - 3

print({
    "p": p, "h": h, "b": b, "delta": delta,
    "C_S": len(folds), "bound": 2 * p - 3,
})
```

It prints

```text
{'p': 26, 'h': 988, 'b': 1, 'delta': 14, 'C_S': 51, 'bound': 49}
```

## 4. Scope and obstruction

This is an exact finite falsifier to the statement requested in P75.  It
also identifies why the positive-defect repair fails: the P71 parity lift
misses the threshold by only 62 defect units, while one Sidon-preserving
odd insertion adds 76 defect units and two folds.  The parity separation
continues to certify the complete literal hole.  Therefore no argument
using only positive defect, the literal hole, and the P65 complementary
fold labels can prove `C_S<=2p-3`; any replacement must weaken the numerical
bound or use additional hypotheses from the surrounding completion problem.
