# P58: exact counterexample to the square fold-repair candidate

## Verdict

The proposed exact inequality

\[
 \max\{\delta-5(C_S+C_D),0\}^2\leq 4p^3                 \tag{1}
\]

is false.  A counterexample is

\[
\begin{aligned}
 p&=14, &h&=183, &b&=1,\\
 B&=\{33,60,72,75,79,81,95,119,124,132,149,150,160,182\}.
                                                               \tag{2}
\end{aligned}
\]

It has

\[
 C_S=C_D=0,\qquad \delta=105,
\]

and therefore

\[
 \max\{\delta-5(C_S+C_D),0\}^2=105^2=11025
 >10976=4\cdot14^3.                                      \tag{3}
\]

The failure margin is `49`, and the exact normalized ratio is

\[
 {105^2\over14^3}={225\over56}>4.                         \tag{4}
\]

Thus the constant `2` in
`delta <= 5(C_S+C_D)+2p^(3/2)` cannot be universal.  This finite
counterexample does not disprove an unspecified-constant
`O(p^(3/2))` replacement; no such replacement is proved here.

## 1. Endpoint and Sidon certificate

The set in (2) is contained in `[0,182]` and has maximum `182=h-1`.
Direct subtraction of its \(\binom{14}{2}=91\) increasing pairs gives

\[
\begin{split}
D^+=\{&1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,\\
&25,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,\\
&48,49,50,51,52,53,54,55,57,58,59,60,62,63,64,65,68,69,70,71,72,74,\\
&75,77,78,79,81,85,86,87,88,89,90,91,99,100,101,103,107,110,116,117,\\
&122,127,149\}.                                           \tag{5}
\end{split}
\]

There are exactly 91 displayed values, so every positive integer difference
has one representation.  Hence (2) is integer Sidon, including diagonals:
a collision with a diagonal, such as \(2x=y+z\), would repeat the positive
difference \(x-y=z-x\).

Moreover, direct inspection of (5) gives the disjoint partition

\[
 D^+\mathbin{\dot\cup}(183-D^+)=\{1,\ldots,182\}.          \tag{6}
\]

Consequently the 183 elements of \(D=B-B\), including zero, occupy every
residue modulo 183 exactly once.  Thus

\[
 |D|=|D\bmod183|=183,\qquad C_D=0.                        \tag{7}
\]

The same perfect-difference property makes unordered pair sums injective
modulo 183.  Indeed, from

\[
 x+y\equiv z+w\pmod {183}
\]

one gets \(x-z\equiv w-y\); uniqueness in (6) makes the two unordered
pairs equal.  This also handles diagonal sums because 183 is odd.  Therefore

\[
 |S|=\binom{15}{2}=105=|S\bmod183|,\qquad C_S=0.          \tag{8}
\]

Equations (7)-(8) verify, rather than assume, the exact relation
\(C_S\leq C_D\leq4C_S\) in this example.

## 2. Literal `3B-B` hole, with repetitions

Since every sum \(s\in S\) is positive,

\[
 -1\in3B-B
 \quad\Longleftrightarrow\quad
 s+1\in D^+\text{ for some }s\in S.                      \tag{9}
\]

This equivalence retains diagonal sums: \(s=x+y\) permits \(x=y\).
For (2), the only possible intersection lies between 66 and 148.  Exact
subtraction gives

\[
\begin{split}
 (D^+-1)\cap[66,148]=\{&67,68,69,70,71,73,74,76,77,78,80,84,85,86,87,\\
 &88,89,90,98,99,100,102,106,109,115,116,121,126,148\},   \tag{10}
\end{split}
\]

whereas exact diagonal-inclusive addition gives

\[
 S\cap[66,148]
 =\{66,93,105,108,112,114,120,128,132,135,139,141,144,147\}.
                                                               \tag{11}
\]

The displayed sets are disjoint.  Since \(\min S=66\) and
\(\max(D^+-1)=148\), (9)-(11) prove

\[
                         -1\notin3B-B.                    \tag{12}
\]

The standalone checker also evaluates all \(14^4=38416\) ordered choices
\((x,y,z,w)\in B^4\) and finds zero solutions of
\(x+y+z-w=-1\).  Thus repeated positive summands, all diagonal choices,
and the \(z=w\) cases are explicitly present in the verification.

## 3. Defect arithmetic

For \(p=14\),

\[
 {3p^2-p+2\over2}=288,
 \qquad
 \delta=288-h=105>0.                                    \tag{13}
\]

Combining (7), (8), and (13) gives (3) exactly.  No estimate, numerical
rounding, or inference from the surrounding finite corpus enters the
counterexample.

More generally, the source of the arithmetic is transparent.  A Singer
perfect difference set of size \(p\) has modulus
\(h=p^2-p+1\).  Whenever one of its top-translated integer lifts satisfies
the literal hole for `b=1` or `b=2`, it has clean folds and

\[
 C_S=C_D=0,\qquad
 \delta={p(p+1)\over2}.                                  \tag{14}
\]

Then (1) becomes \((p+1)^2\leq16p\), which first fails at \(p=14\).
Statement (14) is only a conditional description of the clean Singer
mechanism; no assertion about infinitely many literal holes is made.

## 4. Exact computation

The independent verifier is

```text
problems/864/compute/p58/verify_counterexample.py
```

Run from the repository root:

```powershell
python -m py_compile problems/864/compute/p58/verify_counterexample.py
python -B problems/864/compute/p58/verify_counterexample.py `
  --output problems/864/compute/p58/counterexample_certificate.json
```

It reconstructs every unordered sum and ordered difference, checks the
perfect residue partition, evaluates all ordered quadruples, and emits the
full sum and positive-difference supports.  The exact output summary is

```text
p=14 h=183 b=1 C_S=0 C_D=0 delta=105
ordered quadruples checked=38416
candidate lhs=11025 rhs=10976 failure margin=49
```

The discovery scan is

```powershell
python -B problems/864/compute/p58/scan_singer_counterexamples.py `
  --q 13 `
  --output problems/864/compute/p58/singer_q13_scan.json
```

It checks both values of `b` on 476 distinct affine top lifts from the 60
unit classes of the Singer set in `Z/183Z`: 952 exact profiles in total.
There are six literal holes, all six falsify (1), and (2) is one of them.
These scan counts record search provenance only; Sections 1-3 are the
standalone finite proof.
