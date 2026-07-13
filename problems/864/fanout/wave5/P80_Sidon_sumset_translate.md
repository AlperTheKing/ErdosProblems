# P80: endpoint-normalized Sidon sumset translate

## Verdict

The proposed inequality is **false**, even with the endpoint normalization
exactly as stated.  Let

\[
\begin{split}
B=\{&0,6,13,85,89,121,141,152,196,245,247,257,274,327,345,\\
    &370,404,418,439,444,472,536,558,573,581,582,620,623,639\}
\end{split}                                                    \tag{1}
\]

and put

\[
                         p=|B|=29,\qquad h=640.                \tag{2}
\]

Then `B` is contained in `[0,h-1]` and `max(B)=639=h-1`.  Exact
integer enumeration gives

\[
 |B+B|={29\cdot30\over2}=435,
 \qquad |\Delta^+(B)|={29\cdot28\over2}=406,                  \tag{3}
\]

with every representation count in (3) equal to one.  Thus `B` is Sidon
with all diagonal sums included.  Nevertheless,

\[
 C_S=|\{s\in B+B:s+640\in B+B\}|=58>57=2|B|-1.              \tag{4}
\]

This is an explicit exact counterexample, so no extra assumption such as a
literal hole may be inferred or used.

## Exact fold certificate

The 58 lower sums are

```text
0, 12, 26, 85, 89, 91, 121, 134, 141, 165,
170, 174, 178, 196, 202, 230, 237, 241, 245, 257,
260, 263, 273, 287, 304, 336, 337, 340, 345, 346,
351, 359, 368, 386, 398, 417, 424, 443, 452, 455,
478, 491, 514, 519, 522, 523, 524, 541, 556, 557,
561, 564, 565, 572, 580, 581, 600, 619
```

For each displayed `s`, both `s` and `s+640` have a unique unordered pair
label.  The folds split into 47 off-diagonal/off-diagonal folds, six with
a low diagonal only, four with a high diagonal only, and one with both
pairs diagonal.  The SHA-256 of the comma-separated list (1), with no
spaces, is

```text
cdd6607fd6bfcd330359251fc3ff89656b0f4087dd21772f2515ef392d90c3fb
```

## Standalone verifier

The following uses exact integer arithmetic and reconstructs every pair
label rather than trusting the displayed list.

```python
from collections import Counter
from hashlib import sha256

B = [
    0, 6, 13, 85, 89, 121, 141, 152, 196, 245,
    247, 257, 274, 327, 345, 370, 404, 418, 439, 444,
    472, 536, 558, 573, 581, 582, 620, 623, 639,
]
h = 640
p = len(B)

sum_count = Counter(
    x + y for i, x in enumerate(B) for y in B[i:]
)
diff_count = Counter(
    y - x for i, x in enumerate(B) for y in B[i + 1:]
)
sum_pair = {
    x + y: (x, y) for i, x in enumerate(B) for y in B[i:]
}
folds = [
    (s, sum_pair[s], sum_pair[s + h])
    for s in sorted(sum_pair) if s + h in sum_pair
]

assert B == sorted(set(B))
assert min(B) == 0 and max(B) == h - 1
assert len(sum_count) == p * (p + 1) // 2 == 435
assert max(sum_count.values()) == 1
assert len(diff_count) == p * (p - 1) // 2 == 406
assert max(diff_count.values()) == 1
assert len(folds) == 58 > 2 * p - 1 == 57
assert sha256(
    ",".join(map(str, B)).encode("ascii")
).hexdigest() == (
    "cdd6607fd6bfcd330359251fc3ff89656"
    "b0f4087dd21772f2515ef392d90c3fb"
)

print({"p": p, "h": h, "C_S": len(folds), "bound": 2 * p - 1})
```

It prints

```text
{'p': 29, 'h': 640, 'C_S': 58, 'bound': 57}
```

## Ordering and graph audit

The standard ordering reduction is valid but does not prove the proposed
bound.  Write a fold as

\[
 a+b+h=c+d,\qquad a\le b,\quad c\le d.                \tag{5}
\]

Since `d<=h-1`,

\[
 c=a+b+h-d\ge a+b+1>b.
\]

Hence every fold has

\[
                         a\le b<c\le d,                \tag{6}
\]

and determines complementary nested differences

\[
                         (c-b)+(d-a)=h.                 \tag{7}
\]

Integer Sidonicity makes every positive difference unique.  Charging a
fold to its central edge `[b,c]`, or to its outer edge `[a,d]`, is therefore
injective.  For (1), each canonical graph has 58 distinct edges on 29
marks.  The central graph uses 27 vertices, has maximum degree 7,
degeneracy 3, and 429 crossing edge pairs in mark order.  The outer graph
uses 24 vertices, has maximum degree 10, degeneracy 4, and 865 crossing
pairs.  Thus the exact canonical graph reduction itself realizes the
violation in (4); forest, planar, and `2p-1` edge claims cannot follow from
(6)-(7).

## Polynomial and autocorrelation audit

Let

\[
 P(x)=\sum_{b\in B}x^b,
 \qquad U(x)=\sum_{s\in B+B}x^s.
\]

The unweighted support autocorrelation is exactly

\[
 [x^{640}]U(x)U(x^{-1})=C_S=58.                       \tag{8}
\]

If `q(s)` is the coefficient of `x^s` in `P(x)^2`, then `q(s)=1` on a
diagonal sum and `q(s)=2` otherwise.  The corresponding ordered, weighted
autocorrelation is

\[
 [x^{640}]P(x)^2P(x^{-1})^2
   =\sum_s q(s)q(s+640)
   =47\cdot4+10\cdot2+1=209.                          \tag{9}
\]

Thus both the support polynomial and the ordered polynomial record the
same obstruction exactly.  Passing to weighted autocorrelation does not
recover the false support bound.

## Search scope

The ruler in (1) is the normalized P20 source `bose-22e836643a82`.  An
exact bitset scan tested every endpoint shift `h=width+gamma+1` with
`0<=gamma<width` for the 133 distinct P20 rulers: 590,650 parameter rows
were checked and 122,240 violate `C_S<=2p-1`.  The witness (1) has the
smallest order among those corpus violations.  No claim of global
minimality is needed for the falsification.
