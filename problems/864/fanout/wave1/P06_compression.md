# P06: exact exchange calculus and a one-point compression falsifier

Let

\[
r_A(t)=\#\{\{a,b\}:a,b\in A,\ a\leq b,\ a+b=t\},
\qquad
R(A)=\{t:r_A(t)\geq2\}.
\]

Thus `A` is admissible exactly when \(|R(A)|\leq1\).  The purpose of this
note is to test one-point compression or reflection-closing exchanges, not to
infer an asymptotic statement from finite data.

## 1. Exact delete-insert lemma

For a finite integer set \(B\) and \(y\notin B\), put

\[
 \Sigma(B)=\{b+b':b,b'\in B,\ b\leq b'\},
 \qquad
 J_y(B)=\{2y\}\cup\{y+b:b\in B\}.
\]

**Lemma 1 (complete collision audit).**  If \(C=B\cup\{y\}\), then, for
every integer \(t\),

\[
 r_C(t)=r_B(t)+{\bf1}_{J_y(B)}(t),                                      \tag{1}
\]

and consequently

\[
 R(C)=R(B)\cup\bigl(\Sigma(B)\cap J_y(B)\bigr).                         \tag{2}
\]

In particular, if \(A\subseteq[N]\), \(x\in A\),
\(B=A\setminus\{x\}\), and \(y\in[N]\setminus B\), then the exchange
\(A-x+y\) is admissible if and only if

\[
 \left|R(B)\cup\bigl(\Sigma(B)\cap J_y(B)\bigr)\right|\leq1.            \tag{3}
\]

**Proof.**  The pairs of \(C\) not already present in \(B\) are exactly
\(\{y,y\}\) and \(\{y,b\}\) for \(b\in B\).  Their sums are all distinct:
the map \(b\mapsto y+b\) is injective, and \(2y=y+b\) would force
\(b=y\notin B\).  Hence each element of \(J_y(B)\) contributes exactly one
new representation and there are no collisions between two new pairs.  This
proves (1).  A sum is repeated after insertion precisely when it was already
repeated, or it had one old representation and belongs to \(J_y(B)\).  This
is exactly (2), and (3) follows from the definition of admissibility. \(\square\)

This includes every diagonal: the new diagonal is the explicitly listed
sum \(2y\), while old diagonals are already counted by \(r_B\).  It also
handles an exceptional sum of arbitrary multiplicity, since (1) merely adds
zero or one to that multiplicity and imposes no upper bound on it.

There are exactly two exception-relocation cases after deleting \(x\) from an
admissible set whose exception is \(\sigma\):

* If \(R(B)=\{\sigma\}\), insertion is safe exactly when
  \(\Sigma(B)\cap J_y(B)\subseteq\{\sigma\}\); the exception stays at
  \(\sigma\).
* If \(R(B)=\varnothing\), insertion is safe exactly when
  \(|\Sigma(B)\cap J_y(B)|\leq1\).  An empty intersection leaves a Sidon set;
  a singleton \(\{\tau\}\) relocates the exception to \(\tau\).

These alternatives are exhaustive by (2).

## 2. Reflection-closing specialization and midpoint parity

For a proposed center \(\sigma\), define

\[
 P_\sigma(A)=A\cap(\sigma-A),\qquad p_\sigma(A)=|P_\sigma(A)|.
\]

Suppose \(B=A\setminus\{x\}\) still has exception \(\sigma\), and choose
\(u\in B\) with \(y=\sigma-u\in[N]\setminus B\).  Then adding \(y\) creates
the reflection pair \(\{u,y\}\) at \(\sigma\).  Lemma 1 gives the following
necessary and sufficient reflection-exchange test:

\[
 B\cup\{\sigma-u\}\text{ is admissible}
 \quad\Longleftrightarrow\quad
 \Sigma(B)\cap J_{\sigma-u}(B)\subseteq\{\sigma\}.                     \tag{4}
\]

Thus checking only the intended new representation of \(\sigma\) is not
enough: every value \((\sigma-u)+b\), and the diagonal
\(2(\sigma-u)\), must be checked against every old sum in \(\Sigma(B)\).

There is also a parity obstruction independent of admissibility.  Reflection
on \(P_\sigma(A)\) has two-point orbits \(\{a,\sigma-a\}\), except for the
possible fixed point \(\sigma/2\).  Therefore

\[
 p_\sigma(A)=2q+\delta,\qquad
 \delta={\bf1}_{\{\sigma\ \mathrm{even},\ \sigma/2\in A\}}.                \tag{5}
\]

In particular, when \(\sigma\) is odd and \(|A|\) is odd,
\(p_\sigma(A)\leq |A|-1\).  If equality holds, no cardinality-preserving
one-point exchange can strictly increase closure about that same center.  A
compression theorem must therefore either allow a multi-point exchange or
prove that the exception can be relocated to a center with a larger score.
Equation (5) explicitly covers the midpoint: it contributes one point, not a
two-point orbit and not two elements.

## 3. Exact extremal falsifier, even allowing exception relocation

Consider

\[
 N=10,\qquad A=\{1,3,4,8,10\}.
\]

Its unordered sums, separated so that diagonals are visible, are

\[
\begin{array}{c|c}
\text{diagonals}&2,6,8,16,20\\
\text{off-diagonals}&4,5,9,11,7,11,13,12,14,18.
\end{array}
\]

Hence \(R(A)=\{11\}\), with the two representations
\(1+10=3+8=11\), and every other sum is unique.  Thus \(A\) is admissible.
Moreover

\[
 P_{11}(A)=\{1,3,8,10\},\qquad p_{11}(A)=4.
\]

The sole unpaired point is \(4\), and its missing mate \(7\) lies in
\([10]\); in fact every \(11-a\), \(a\in A\), lies in \([10]\).  This is
not a boundary obstruction.  Since the center is odd and \(|A|=5\), (5)
already rules out a strict same-center score increase.

The following is stronger.  For an admissible set \(C\), define its current
closure score to be \(p_\tau(C)\) when \(R(C)=\{\tau\}\), and zero when
\(R(C)=\varnothing\).

**Proposition 2 (one-point exchange falsifier).**  The set \(A\) above is a
cardinality maximizer for \(N=10\), but no cardinality-preserving one-point
exchange \(C=A-x+y\) is admissible with current closure score greater than
four, even when the exceptional sum is allowed to relocate.

Here is the complete collision audit.  The possible genuinely new values are
\(y\in\{2,5,6,7,9\}\).  Each table entry is the full repeated-sum support
\(R(A-x+y)\); every displayed sum has multiplicity exactly two.

\[
\begin{array}{c|ccccc}
x\backslash y&2&5&6&7&9\\ \hline
1&\{6,12\}&\{8,13\}&\{12,14,16\}&\{11,14\}&\{12,13,18\}\\
3&\{12\}&\{9\}&\{12,14,16\}&\{8,11,14\}&\{18\}\\
4&\{4,11\}&\{6,11,13\}&\{9,11,16\}&\{11\}&\{11,18\}\\
8&\{4,5,6\}&\{6,8\}&\{7\}&\{8,11,14\}&\{13\}\\
10&\{4,5,6\}&\{6,8,9\}&\{7,9,12\}&\{8,11\}&\{12\}
\end{array}                                                               \tag{6}
\]

Thus exactly seven of the 25 exchanges are admissible.  Their relocated
exceptions and scores are

\[
\begin{array}{c|c|c}
x\to y&\tau&p_\tau(A-x+y)\\ \hline
3\to2&12&4\\
3\to5&9&4\\
3\to9&18&3\\
4\to7&11&4\\
8\to6&7&4\\
8\to9&13&4\\
10\to9&12&4
\end{array}                                                               \tag{7}
\]

All other exchanges have at least two repeated sums by (6).  Notice in
particular what happens when the missing mate \(7\) is inserted.  Removing
\(4\) merely moves the unique unpaired point from \(4\) to \(7\), leaving
the score at four.  Removing any of \(1,3,8,10\) is inadmissible.  The new
diagonal \(7+7=14\) causes one of the extra collisions when \(x=1,3,8\),
while the old diagonal \(4+4=8\) causes an extra collision when
\(x=3,8,10\).  Hence neither diagonals nor midpoint parity are hidden in the
table.

## 4. Reproducible exact experiment

The following dependency-free Python program checks all \(2^{10}=1024\)
subsets, establishes \(F(10)=5\), and audits all 25 exchanges by the exact
definition.  It uses integer arithmetic only.

```python
N = 10
A = {1, 3, 4, 8, 10}

def reps(S):
    L = sorted(S)
    d = {}
    for i, a in enumerate(L):
        for b in L[i:]:                 # includes a = b diagonals
            d[a + b] = d.get(a + b, 0) + 1
    return d

def repeated(S):
    return {s: m for s, m in reps(S).items() if m >= 2}

def score(S):
    R = repeated(S)
    if len(R) != 1:
        return 0
    sigma = next(iter(R))
    return sum(sigma - a in S for a in S)

counts = {}
maxsets = []
for mask in range(1 << N):
    S = {i + 1 for i in range(N) if (mask >> i) & 1}
    if len(repeated(S)) <= 1:
        counts[len(S)] = counts.get(len(S), 0) + 1
        if not maxsets or len(S) > len(maxsets[0]):
            maxsets = [S]
        elif len(S) == len(maxsets[0]):
            maxsets.append(S)

print(sorted(counts.items()))
print(len(maxsets[0]), len(maxsets), A in maxsets, repeated(A), score(A))

for x in sorted(A):
    for y in sorted(set(range(1, N + 1)) - A):
        C = (A - {x}) | {y}
        R = repeated(C)
        print(x, y, sorted(R.items()), len(R) <= 1, score(C))
```

The first two output lines are

```text
[(0, 1), (1, 10), (2, 45), (3, 120), (4, 182), (5, 36)]
5 36 True {11: 2} 4
```

There are no admissible sets of size six because size six is absent from the
complete count, so \(A\) is an exact extremizer.  The remaining 25 output
lines reproduce (6) and (7).

## 5. Verdict for the compression route

Lemma 1 is a rigorous local exchange tool: it reduces every admissibility
check to intersections of explicit old and new sum sets and fully permits an
exception of arbitrary multiplicity.  Proposition 2 kills the universal
one-point strategy

\[
\text{``exchange one point of an extremizer to strictly increase reflection
closure, allowing the exception to relocate.''}
\]

The falsifier is exact, is itself cardinality-maximizing, has no reflected
mate outside the ambient interval, and audits parity, the absent midpoint at
the odd center, exception relocation, diagonals, and every newly created
collision.  Any viable compression theorem needs a genuinely multi-point
move or an additional structural hypothesis excluding this extremizer.
