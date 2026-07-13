## The literal implication is false

The issue is the sentence

[
\max(E)\ge 3p^2-o(p^2)
\quad\Longleftrightarrow\quad
\delta=o(p^2).
]

The right-hand side is too strong: the left-hand side is a **one-sided** estimate, whereas (\delta=o(p^2)) is two-sided.

### Exact correction lemma

For every instance in the question,

[
\boxed{\max(E)=3p^2-p+b-2\delta.}
]

Consequently, for any sequence of admissible sets with (p\to\infty),

[
\boxed{\max(E)\ge 3p^2-o(p^2)
\iff
\delta_+=o(p^2),}
]

where (\delta_+=\max(\delta,0)). Equivalently,

[
\limsup_{p\to\infty}\frac{\delta}{p^2}\le 0.
]

#### Proof

Because (\max B=h-1),

[
\max E=b+2(h-1)=2h+b-2.
]

The definition of (\delta) gives

[
2h=3p^2-p+2-2\delta,
]

and hence

[
\max E
=3p^2-p+b-2\delta.
]

Thus

[
3p^2-\max E=p-b+2\delta.
]

For every real (x) and (y),

[
|(x+y)*+-x*+|\le |y|.
]

Taking (x=2\delta) and (y=p-b) gives

[
\left|(3p^2-\max E)*+-2\delta*+\right|\le p.
]

Since (p=o(p^2)), the asserted equivalence follows. ∎

In particular, a sequence with (\delta=-cp^2) satisfies the desired lower bound very comfortably but does **not** satisfy (\delta=o(p^2)).

---

# An explicit infinite counterfamily

The bare hypotheses do not imply the two-sided conclusion (\delta=o(p^2)).

Let (q\ge 3) be an odd prime, put (p=q), and for (0\le i<q) let

[
r_i\in{0,\ldots,q-1},\qquad r_i\equiv i^2\pmod q,
]

and define

[
z_i=2qi+r_i.
]

Set

[
Z_q={z_0,\ldots,z_{q-1}}.
]

We shall verify everything directly.

## 1. Ordering and diameter

Since (r_{i+1}-r_i\ge -(q-1)),

[
z_{i+1}-z_i
=2q+r_{i+1}-r_i
\ge q+1>0.
]

Thus

[
0=z_0<z_1<\cdots<z_{q-1}.
]

Also (r_{q-1}=1), so

[
W=z_{q-1}=2q(q-1)+1
=2q^2-2q+1.
]

## 2. (Z_q) is Sidon in the integers

Suppose

[
z_i+z_j=z_k+z_l.
]

Then

[
2q(i+j-k-l)=r_k+r_l-r_i-r_j.
]

The right side has absolute value at most (2q-2), while the left side is divisible by (2q). Therefore

[
i+j=k+l.
]

Reducing the original equality modulo (q) gives

[
i^2+j^2\equiv k^2+l^2\pmod q.
]

Using equality of the sums,

[
2ij=(i+j)^2-(i^2+j^2)
\equiv(k+l)^2-(k^2+l^2)
=2kl\pmod q.
]

Because (q) is odd,

[
ij\equiv kl\pmod q.
]

Thus the two monic polynomials

[
(X-i)(X-j),\qquad (X-k)(X-l)
]

have the same coefficients over (\mathbb F_q). Consequently

[
{i,j}={k,l}\pmod q.
]

All four indices lie in ({0,\ldots,q-1}), so their unordered pairs are equal as integer pairs. This proves integer Sidonicity, including diagonal sums.

## 3. Choice of (G) and the threefold condition

Put

[
G=W+1=2q^2-2q+2
]

and

[
E_q={G+2z:z\in Z_q}.
]

Affine transformations preserve Sidonicity, so (E_q) is Sidon.

Moreover,

[
\max E_q=G+2W=3W+1,
]

whereas every element of (E_q+E_q+E_q), even with repeated summands, is at least

[
3G=3W+3.
]

Therefore

[
\boxed{E_q\cap(E_q+E_q+E_q)=\varnothing.}
]

This is interval separation, so it covers all repeated-summand cases automatically.

## 4. The parameters (b,\gamma,h,\delta)

Here (W) is odd and (G=W+1) is even. Hence

[
b=2,
\qquad
\gamma=\frac{G-2}{2}=q^2-q.
]

Therefore

[
h=\gamma+W+1
=3q^2-3q+2.
]

Now

[
\begin{aligned}
\delta
&=\frac{3q^2-q+2}{2}-(3q^2-3q+2)\
&=\frac{-3q^2+5q-2}{2}.
\end{aligned}
]

Consequently,

[
\boxed{\frac{\delta}{p^2}
=\frac{-3q^2+5q-2}{2q^2}
\longrightarrow-\frac32.}
]

Thus this admissible sequence does not have (\delta=o(p^2)). On the other hand,

[
\max E_q=6q^2-6q+4,
]

so the desired lower estimate (\max E_q\ge 3p^2-o(p^2)) holds with a large margin. Notice also that (\delta_+=0) throughout this family, exactly as the corrected equivalence predicts.

---

# A completely verified finite member

Take (q=p=3). Then

[
Z={0,7,13},\qquad W=13,\qquad G=14,
]

and

[
E={14,28,40}.
]

Its unordered pair sums are

[
28,\ 42,\ 54,\ 56,\ 68,\ 80,
]

so (E) is Sidon. Also

[
\max E=40<42=3\min E,
]

hence (E\cap3E=\varnothing), including triples with repeated summands.

The normalized data are

[
b=2,\qquad \gamma=6,\qquad h=20,\qquad B={6,13,19}.
]

The integer sum and difference supports are

[
S={12,19,25,26,32,38},
]

and

[
D={-13,-7,-6,0,6,7,13}.
]

Reducing modulo (20),

[
S_h={5,6,12,18,19},
]

[
D_h={0,6,7,13,14}.
]

Therefore

[
a=6-5=1,\qquad c=7-5=2.
]

Furthermore,

[
-b-D_h
={4,5,11,12,18}\pmod {20},
]

so

[
I={5,12,18}.
]

The carry targets are

[
h-b=18,\qquad 2h-b=38.
]

All witnesses are as follows:

[
\begin{array}{c|c|c}
\text{level} & (s,d) & s\bmod 20\ \hline
1 & (12,6) & 12\
1 & (25,-7) & 5\
2 & (25,13) & 5\
2 & (32,6) & 12\
2 & (38,0) & 18
\end{array}
]

Thus residues (5) and (12) occur at both levels, and residue (18) occurs only at level two. Exhaustively,

[
{(s,d)\in S\times D:s+d=-2}=\varnothing,
]

so carry level zero is absent exactly as required.

Finally,

[
\delta=\frac{3\cdot3^2-3+2}{2}-20=13-20=-7.
]

Every property in the question is therefore verified exactly.

---

## Consequence for the requested lemma

Under the literal hypotheses, no lemma can validly conclude the two-sided statement

[
\delta=o(p^2),
]

because the prime family above is a counterexample. A valid closing lemma must instead conclude

[
\boxed{\delta_+=o(p^2)}
]

or begin with an additional hard-regime normalization such as (\delta\ge0), or at least

[
\delta\ge-o(p^2).
]

With that correction, the (p=168) Singer example remains fully relevant: it has positive (\delta), so the counterfamily above does not address its carry imbalance. Proving (\delta_+=o(p^2)) from the Sidon and carry-zero hypotheses is precisely the unresolved content. The current official entry still lists Erdős Problem 864 as open and records no claimed partial or complete solution in its comments. ([[erdosproblems.com](https://www.erdosproblems.com/864)][1])

[1]: https://www.erdosproblems.com/864 "https://www.erdosproblems.com/864"
