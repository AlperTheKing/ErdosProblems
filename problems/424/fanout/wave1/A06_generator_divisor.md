# A06: exact divisor-recursion generator

## Definitions

Let

\[
A_0=\{2,3\},\qquad
A_{r+1}=A_r\cup\{xy-1:x,y\in A_r,\ x\ne y\},\qquad
A=\bigcup_{r\geq 0}A_r.
\]

Define Boolean values \(b_n\), in increasing order of \(n\), by

\[
b_1=0,\quad b_2=b_3=1,
\]

and, for \(n\geq4\),

\[
b_n=1\quad\Longleftrightarrow\quad
\exists d,q\geq2:\ dq=n+1,\ d<q,\ b_d=b_q=1. \tag{1}
\]

The strict inequality \(d<q\), rather than \(d\leq q\), is the distinct-value
condition.  The implementation enumerates divisors \(d\mid n+1\) only while
`d*d < n+1`, and sets `q = (n+1)//d`.

## Exactness lemma

**Lemma.** For every positive integer \(n\), \(b_n=1\) if and only if
\(n\in A\). Consequently, computing (1) through \(n=X\) gives exactly
\(A\cap[1,X]\); no value above \(X\) can affect the answer.

**Proof.** Every element of every \(A_r\) is at least 2. If \(x,y\geq2\),
\(x\ne y\), and \(n=xy-1\), orient the pair as \(2\leq d<q\). Then

\[
d<n=dq-1,\qquad q<n=dq-1,
\]

because \(dq-1\geq2q-1>q\), and similarly for \(d\).

Use strong induction on \(n\). The claims for \(1,2,3\) follow from the
definition and the lower bound 2. If (1) accepts an \(n\geq4\), its witness
\(d,q<n\) belongs to \(A\) by induction, so closure gives \(n=dq-1\in A\).
Conversely, if \(n\in A\setminus\{2,3\}\), take the first stage at which it
appears. Then \(n=xy-1\) for distinct \(x,y\) from the preceding stage.
Orienting them as \(d<q\) gives \(d,q<n\); induction gives \(b_d=b_q=1\),
so (1) accepts \(n\). This proves both directions. The same inequalities show
that the recurrence is one-pass and independent of values above \(X\). \(\square\)

## Implementation and independent check

The dependency-free Python program is
[`divisor_generator.py`](../../compute/wave1/A06/divisor_generator.py).
Its primary generator uses an exact smallest-prime-factor sieve to factor each
\(n+1\), enumerates its divisors, and retains the smaller factor of a witness.
An exhaustive assertion checks every retained witness \(d,q\):

\[
2\leq d<q<n,\qquad dq=n+1,\qquad b_d=b_q=1.
\]

The independent generator does not factor integers. It maintains a min-heap of
forward-generated candidates. When a new value \(y\) is accepted, it forms
\(xy-1\) with each older accepted value \(x\), stopping once the product
exceeds \(X\). Since one value is new and one is older, every such pair has
\(x\ne y\). Induction on the output value proves completeness: the two parents
of any \(n\in A\) are smaller than \(n\), so both are accepted before \(n\),
and their pair is inserted when the later parent is accepted.

The first 55 generated values were asserted equal to the values displayed by
[OEIS A005244](https://oeis.org/A005244):

```text
2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69, 77,
80, 81, 84, 87, 98, 99, 101, 105, 122, 125, 129, 131, 134, 137, 149,
152, 153, 158, 159, 161, 164, 167, 173, 194, 195, 197, 201, 204, 206,
209, 219, 230, 233, 237, 239, 242, 243, 249
```

In particular, `8` and `24` are absent. Their only factor pairs are
\(8+1=3\cdot3\) and \(24+1=5\cdot5\), so either value would be an exact
counterexample to an implementation that accidentally permitted equal inputs.

## Reproduction

From `E:\Projects\ErdosProblems`, run:

```powershell
python problems/424/compute/wave1/A06/divisor_generator.py --limit 10000000
```

The run performed on 2026-07-13 produced:

```text
limit=10000000
member_count=4952270
divisor_forward_equal=true
oeis_prefix_terms=55
oeis_prefix_equal=true
distinctness_sentinels=8:false,24:false
membership_bytearray_sha256=7f5f29e1d5733d623c514c98c183796c3ab15a99d9ad9e5f0c9ff6ea627d85a0
last_10=9999981,9999983,9999984,9999986,9999987,9999989,9999993,9999995,9999998,9999999
```

The digest is SHA-256 of the `bytearray` indexed from 0 through \(X\), with
byte `1` exactly at accepted indices and byte `0` elsewhere. Thus the digest
commits to every membership decision, including 0 and 1, not merely the count.

## Limitations

This is an exact finite computation, not a proof of positive lower density.
It uses \(O(X)\) memory; the divisor pass also enumerates the divisors of every
integer through \(X+1\), while the forward pass enumerates all accepted pairs
whose product is at most \(X+1\). The two Python implementations and the
55-term external prefix reduce implementation risk but are not formal
verification, and no inference about the limit inferior is made from the
finite count \(4{,}952{,}270\) at \(X=10^7\).
