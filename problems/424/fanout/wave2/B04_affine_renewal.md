# B04: collision-exact affine renewal

## Audit verdict

**NOT SOLVED.** This lane does not prove or disprove

\[
\liminf_{X\to\infty}\frac{S(X)}X>0.
\]

The strongest exact results are:

1. a complete affine-word multiplicity model;
2. the first explicit word-collision falsifier;
3. a collision-exact Dirichlet renewal identity;
4. rigorous zero-density and positive-density certificate theorems; and
5. an exact computation showing that all map relations through length 12 do
   not satisfy the zero-density certificate.

The load-bearing unresolved term is the orbit-value collision multiplicity,
not raw word growth.

Code:
[affine_relations.py](../../compute/wave2/B04/affine_relations.py) and
[test_affine_relations.py](../../compute/wave2/B04/test_affine_relations.py).

## 1. Exact orbit reduction

The only licensed seed exits are

\[
T_3(2)=5,\quad T_5(2)=9,\quad T_2(3)=5,\quad T_5(3)=14,
\quad T_2(5)=9,\quad T_3(5)=14.
\]

Every value reached from 9 or 14 is greater than 5 and increases under every
\(T_k\). Therefore the restriction \(x\ne k\) is automatic thereafter, and

\[
S=\{2,3,5\}\cup{\cal O}(9)\cup{\cal O}(14).                 \tag{1}
\]

For a word \(w=(k_1,\ldots,k_m)\) in application order, write

\[
F_w=T_{k_m}\circ\cdots\circ T_{k_1},\qquad F_w(x)=P_wx-C_w.
\]

Appending \(k\) sends

\[
(P,C)\longmapsto(kP,kC+1).                                \tag{2}
\]

Hence

\[
P_w=\prod_{j=1}^m k_j,\qquad
\frac{C_w}{P_w}=\sum_{j=1}^m\frac1{k_1\cdots k_j},\qquad
0<C_w<P_w,                                                  \tag{3}
\]

and for every root \(a\ge2\),

\[
(a-1)P_w<F_w(a)<aP_w.                                      \tag{4}
\]

## 2. Multiplicities and falsifier

Map equality and orbit-value equality are exactly

\[
F_w=F_v\iff(P_w,C_w)=(P_v,C_v),                            \tag{5}
\]

\[
F_w(a)=F_v(b)\iff P_wa-C_w=P_vb-C_v.                       \tag{6}
\]

Both are integer tests. Distinct words cannot be counted as distinct values.

**Falsifier.** The first map collision occurs at length 6:

\[
255232=322255,
\]

because both words give

\[
(P,C)=(600,381),\qquad F(x)=600x-381.                       \tag{7}
\]

Thus any proof using \(3^m\) distinct affine maps, or assigning multiplicity
one to map words, is false from \(m=6\).

Exact fibers computed by (2) are:

| depth | words | distinct maps | maximum fiber | distinct-map \(\sum P^{-1}\) |
|---:|---:|---:|---:|---:|
| 5 | 243 | 243 | 1 | \(28629151/24300000\) |
| 6 | 729 | 728 | 2 | \(886288681/729000000\) |
| 9 | 19,683 | 19,485 | 3 | \(26078537525671/19683000000000\) |
| 12 | 531,441 | 518,933 | 4 | \(760718858225819761/531441000000000000\) |

## 3. Normal-form zero-density certificate

Let \({\cal R}\) be a finite set of oriented relations \(u\to v\) with
\(F_u=F_v\), \(|u|=|v|\), and \(v<u\) lexicographically. Let
\(L_{\cal R}\) avoid every left side as a factor, and let
\(A_{\cal R}(s)\) be its forbidden-pattern automaton with edge weight
\(k^{-s}\).

### Theorem 1

If

\[
\rho(A_{\cal R}(1))<1,                                    \tag{8}
\]

then

\[
\sum_{n\in S}\frac1n<\infty,\qquad \frac{S(X)}X\to0.        \tag{9}
\]

### Proof

Each rewrite preserves the affine map and strictly decreases a fixed-length
word, so rewriting terminates. Every represented map therefore has a word in
\(L_{\cal R}\), without requiring uniqueness. By (1) and (4),

\[
\sum_{n\in S}\frac1n
\le O(1)+\left(\frac18+\frac1{13}\right)
\sum_{w\in L_{\cal R}}P_w^{-1}.
\]

The last sum is the matrix geometric series for \(A_{\cal R}(1)\), which
converges under (8). A convergent harmonic sum implies zero density because

\[
\frac{|S\cap(N,X]|}{X}
\le\sum_{\substack{n>N\\n\in S}}\frac1n.
\]

\(\square\)

### Exact finite outcome

Orienting every noncanonical map word through depth 12 and removing rules
which contain an older left side gives 363 relations and a 1,195-state
avoidance automaton.

This finite relation system is rigorously supercritical. Exact rational
dynamic programming gives

\[
A_{\cal R}(1)^{50}{\bf1}\ge q{\bf1}
\]

on every nonterminal state, with

\[
q=
\frac{
7337430420190612870534198123742011913722783939570987104017205260347585141
}{
7178979876918525887702490000000000000000000000000000000000000000000000000
}>1.                                                       \tag{10}
\]

Hence \(\rho(A_{\cal R}(1))^{50}\ge q>1\), so these relations do not prove
zero density. This is a bounded exact result, not a claim about all relations.

## 4. Collision-exact Dirichlet renewal

Put

\[
H(s)=\sum_{n\in S}n^{-s}\qquad(s>1).
\]

Let \(m(n)\) be the number of licensed immediate parents:

\[
m(n)=\#\left\{k\in\{2,3,5\}:k\mid n+1,\ (n+1)/k\in S,\
(n+1)/k != k\right\},
\]

and define

\[
\Delta(s)=\sum_{n\ge1}\max(m(n)-1,0)n^{-s}.                 \tag{11}
\]

Exact inclusion-exclusion gives

\[
H(s)=2^{-s}+3^{-s}
+\sum_{k\in\{2,3,5\}}\sum_{\substack{x\in S\\x\ne k}}
(kx-1)^{-s}-\Delta(s).                                     \tag{12}
\]

For

\[
E_k(s)=\sum_{\substack{x\in S\\x\ne k}}
\big((kx-1)^{-s}-(kx)^{-s}\big),
\]

the series \(E_k\) is holomorphic on \(\Re s>0\). Rearranging (12) yields

\[
\boxed{\Delta(s)=
\left(2^{-s}+3^{-s}+5^{-s}-1\right)H(s)+G(s)},              \tag{13}
\]

where

\[
G(s)=2^{-s}+3^{-s}-2^{-2s}-3^{-2s}-5^{-2s}
+E_2(s)+E_3(s)+E_5(s)
\]

is holomorphic on \(\Re s>0\). Therefore, if \(H(s)\to\infty\) as
\(s\downarrow1\),

\[
\frac{\Delta(s)}{H(s)}\to
\frac12+\frac13+\frac15-1=\frac1{30}.                      \tag{14}
\]

The critical collision coefficient \(1/30\) is thus exact. Identity (13)
does not separate positive density from a slowly vanishing density.

## 5. Positive-density certificate with exact multiplicity

For a licensed representation language \({\cal L}\) based at 9 and 14, let

\[
r_{\cal L}(n)=
\#\{(a,w):a\in\{9,14\},\ w\in{\cal L},\ F_w(a)=n\}.
\]

### Theorem 2

If constants \(c>0\), \(C<\infty\) satisfy

\[
\sum_{n\le X}r_{\cal L}(n)\ge cX+o(X),\qquad
\sum_{n\le X}r_{\cal L}(n)^2\le CX+o(X),                   \tag{15}
\]

then

\[
\liminf_{X\to\infty}\frac{S(X)}X\ge\frac{c^2}{C}>0.        \tag{16}
\]

### Proof

Cauchy--Schwarz, with the exact multiplicities, gives

\[
\left(\sum_{n\le X}r_{\cal L}(n)\right)^2
\le
|\{n\le X:r_{\cal L}(n)>0\}|
\left(\sum_{n\le X}r_{\cal L}(n)^2\right).
\]

The support is contained in \(S\). Divide by \(X^2\) and apply (15).
\(\square\)

For a regular language, the first estimate is a standard finite-state
renewal calculation. The unresolved requirement is the second estimate:
accepted collision pairs must be in exact bijection with the integer
solutions of (6). Counting arbitrary pairs, or only same-map pairs (5), is
insufficient.

## 6. Final status and prior art

The supplied census through \(10^9\) is compatible with both a positive
limit and slow decay. The neighboring B02 audit extends the decline through
\(10^{11}\) and finds decreasing modular occupancy through \(30^7\), but
neither is asymptotic proof.

Shamazov--Talambutsa,
[On orbit sets generated by semigroups of one-dimensional affine
functions](https://arxiv.org/abs/2507.06875), proves positive density for
exact covering systems. That hypothesis gives multiplicity at most one and
does not hold here. Relation (7) also shows that the present semigroup is not
free.

**Final B04 status: not solved.** The concrete frontier is an
orbit-relative pair language proving (15), a larger relation system proving
(8), or the summable excess-collision estimate isolated in B02.

## 7. Reproduction

~~~powershell
cd problems/424/compute/wave2/B04
python -m unittest -v test_affine_relations.py
python affine_relations.py --max-depth 12 --normal-length 40
~~~
