# P52: arc spectral factor and curvature obstruction

## Verdict

Keep

\[
 P(x)=\sum_{z\in Z}x^z,\qquad
 A=P P^\#,\qquad B=x^G P^2,
\]

where

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\}
\]

is Sidon, `#` sends (x) to (x^{-1}), and

\[
             D^+(Z)\cap(G+S_2(Z))=\varnothing.                 \tag{1}
\]

There is an exact arc-sensitive spectral factor not isolated in P47.  Put

\[
 P^*(x)=x^W P(x^{-1}),\qquad
 Q(x)=P^*(x)-x^{G+W}P(x).
\]

Then (Q=(1-x)R), where (R) has a positive palindromic unimodal
integer coefficient sequence.  On the unit circle,

\[
 A-\operatorname {Re}B
   ={1\over2}|Q|^2
   =(1-\cos\theta)|R|^2.                                      \tag{2}
\]

The autocorrelation of (R) gives a proved tail domination between the
positive differences and the shifted sums; see (15).  This is stronger
than scalar Parseval data and genuinely uses the one-sided placement of
the common Newman factor.

The natural next Hankel candidate is false.  If (h_n) is half the
aperiodic autocorrelation of (R), let (s_n=h_n-h_{n+1}).  Positivity
and unimodality of (R) do imply (s_n\geq0), but they do **not** imply
that (s_n) is unimodal.  Such unimodality would force (G\geq W).  The
fully structured exact counterexample

\[
                    p=3,\qquad Z=\{0,3,4\},\qquad G=2             \tag{3}
\]

already falsifies it.  It retains the Sidon Newman factor, both exact
profiles, nonnegative self-reciprocal (A), common factorization,
all-circle equality, disjoint supports, and the one-sided orientation.

The principal Toeplitz Gram matrix on the two obvious translate
families is also exactly blind to the arc: its spectrum depends only on
(p), not on (G,W), or (Z).  Thus neither this block spectrum nor
first-order autocorrelation unimodality can yield the missing leading
unit.  The remaining analytic frontier is narrower: control the
**span** of the curvature reversals in (13), rather than trying to
exclude such reversals.

## 1. Exact spectral staircase lemma

Write (b_n=[x^n]B) and put (L=G+2W).

**Lemma P52.1 (Toeplitz blocks, staircase factor, and tail
domination).**  Under (1), the following statements hold.

1.  In the (A)-weighted monomial inner product

    \[
       \langle x^u,x^v\rangle_A
          :=\operatorname {CT}_x(Ax^u x^{-v}),                  \tag{4}
    \]

    the Gram matrix on

    \[
       \{-z:z\in Z\}\ \cup\ \{G+z:z\in Z\}
    \]

    is

    \[
       \bigl((p-1)I_p+J_p\bigr)
       \ \oplus\
       \bigl((p-1)I_p+J_p\bigr).                               \tag{5}
    \]

    Its spectrum is

    \[
       (2p-1)^2,\qquad (p-1)^{,2p-2},                          \tag{6}
    \]

    where superscripts in (6) denote multiplicities.

2.  The polynomial (Q) is divisible by (1-x).  If

    \[
                         Q(x)=(1-x)R(x),
       \qquad R(x)=\sum_{n=0}^{L-1}r_nx^n,                      \tag{7}
    \]

    then

    \[
    r_n=
    \begin{cases}
      |\{z\in Z:z\geq W-n\}|,&0\leq n<W,\\
      p,&W\leq n<G+W,\\
      |\{z\in Z:z>n-G-W\}|,&G+W\leq n<L.
    \end{cases}                                                \tag{8}
    \]

    In particular, every (r_n) is positive, and

    \[
                      r_n=r_{L-1-n}.                            \tag{9}
    \]

    The sequence rises by zeroes and ones, has a central plateau of
    height (p) and length (G), and then falls symmetrically.

3.  The exact first two staircase statistics are

    \[
       R(1)=pG+2\sum_{i=0}^{p-1}z_i,                            \tag{10}
    \]

    \[
       \sum_{n=0}^{L-1}r_n^2
        =p^2G+2\sum_{i=0}^{p-1}(2p-2i-1)z_i.                   \tag{11}
    \]

    Consequently Cauchy--Schwarz, equivalently the Fejer point-value
    bound for (|R|^2), gives the exact arc inequality

    \[
      \left(pG+2\sum_i z_i\right)^2
       \leq L\left(p^2G+2\sum_i(2p-2i-1)z_i\right).            \tag{12}
    \]

4.  Define

    \[
       T=A-{B+B^\#\over2},\qquad
       H={1\over2}RR^\#,
       \qquad c_n=[x^n]T,\quad h_n=[x^n]H.
    \]

    Then

    \[
               T=(2-x-x^{-1})H,\qquad
               c_n=2h_n-h_{n-1}-h_{n+1}.                       \tag{13}
    \]

    For (n>0), condition (1) and the exact profiles give

    \[
    c_n=
    \begin{cases}
       1,&n\in D^+(Z),\\
       -\tfrac12,&n=G+2z_i,\\
       -1,&n=G+z_i+z_j\quad(i<j),\\
       0,&\text{otherwise}.
    \end{cases}                                                \tag{14}
    \]

5.  The sequence (h_0,h_1,\ldots,h_L=0) is nonincreasing.  Hence,
    for every (0\leq n<L),

    \[
    \boxed{
      s_n:=h_n-h_{n+1}
       ={1\over2}\sum_{\substack{k>n}}b_k
          -|D^+(Z)\cap(n,W]|
       \geq0.}                                                  \tag{15}
    \]

    Thus the coefficient-weighted shifted-sum distribution dominates
    the positive-difference distribution in every upper tail.

### Proof

For (5), the coefficient of (A) at zero is (p), and its coefficient
at every nonzero signed difference of (Z) is one.  The within-family
blocks in (4) are therefore ((p-1)I+J).  A cross entry is

\[
                         [x^{G+z_i+z_j}]A,
\]

which is zero by (1).  The eigenvalues of ((p-1)I+J) are (2p-1)
once and (p-1) with multiplicity (p-1), proving (5)--(6).

The positive terms of (Q) occur at (W-Z), and its negative terms at
(G+W+Z).  These two sets lie respectively in ([0,W]) and
([G+W,L]).  Also (Q(1)=p-p=0).  Dividing by (1-x) says that (r_n)
is the cumulative sum of the coefficients of (Q) through exponent
(n).  This gives (8).  Formula (9), positivity, and unimodality are
then immediate.

The first arc of the staircase has total coefficient sum
(\sum_i z_i), the central plateau contributes (pG), and the last arc
is its reverse.  This proves (10).  If (u_n=r_n) for (0\leq n<W),
then

\[
  \sum_{n=0}^{W-1}u_n^2
    =\sum_{i,j}\min(z_i,z_j)
    =\sum_i(2p-2i-1)z_i.
\]

Adding the reverse arc and plateau proves (11).  Applying
((\sum r_n)^2\leq L\sum r_n^2) proves (12).

On (|x|=1), multiplication by (x^W) does not change modulus, and

\[
\begin{aligned}
 {1\over2}|Q|^2
  &={1\over2}|P^\#-x^GP|^2\\
  &=A-{B+B^\#\over2}.
\end{aligned}
\]

Combining this with (Q=(1-x)R) proves (2) and (13).  P47's exact
profiles and (1) then give (14).

It remains to prove the monotonicity used in (15).  By (8)--(9), every
superlevel set

\[
                         I_m=\{n:r_n\geq m\}
\]

is a centered integer interval.  The layer-cake expansion gives

\[
  2h_n=\sum_jr_jr_{j+n}
      =\sum_{a,b}|I_a\cap(I_b-n)|.                              \tag{16}
\]

For two centered intervals the overlap in (16) is nonincreasing as
(n\geq0) increases.  Thus (h_n\geq h_{n+1}).  Finally, (13) gives
(c_k=s_k-s_{k-1}).  Summing from (k=n+1) through (L), using
(h_L=h_{L+1}=0), yields

\[
                         s_n=-\sum_{k=n+1}^L c_k.
\]

Substitution of (14) is exactly (15).  QED.

## 2. The single-peak Hankel candidate is false

The staircase (r) is symmetric unimodal, and its autocorrelation
(h) is symmetric unimodal by the proof above.  A natural strengthening
is:

> **Candidate SC.**  The nonnegative slope sequence
> (s_n=h_n-h_{n+1}), (0\leq n<L), is unimodal: it first
> nondecreases and then nonincreases.

This is precisely a one-inflection assertion for the Hankel/Toeplitz
coefficient sequence (h).  It would locate the arc.  Indeed,
disjointness gives

\[
                       c_G=-\tfrac12,\qquad c_W=1.              \tag{17}
\]

Since (c_k=s_k-s_{k-1}), if (G<W), (17) is a decrease of (s)
followed by a later increase.  Candidate SC would therefore imply
(G\geq W), stronger than the desired asymptotic inequality.

For (3), however,

\[
 P=1+x^3+x^4,qquad
 A=3+x+x^{-1}+x^3+x^{-3}+x^4+x^{-4},
\]

\[
 B=x^2+2x^5+2x^6+x^8+2x^9+x^{10}.                             \tag{18}
\]

The six unordered sums of (Z) are

\[
                         0,3,4,6,7,8,
\]

so (Z) is Sidon.  The positive differences are (1,3,4), while the
support of (B) is (2,5,6,8,9,10); hence (1) holds.  Equations
(18) display the exact profiles (3,1^6) and (1^3,2^3).

The spectral factors are

\[
 Q=1+x+x^4-x^6-x^9-x^{10},
\]

\[
 R=1+2x+2x^2+2x^3+3x^4+3x^5
       +2x^6+2x^7+2x^8+x^9.                                  \tag{19}
\]

In nonnegative lags, the exact integer certificate is

\[
 2(h_0,\ldots,h_{10})
   =(44,41,36,32,26,18,12,8,4,1,0),                            \tag{20}
\]

\[
 2(s_0,\ldots,s_9)=(3,5,4,6,8,6,4,4,3,1).                    \tag{21}
\]

The segment (5,4,6) in (21) decreases and then increases.  Equivalently,

\[
 2(c_0,\ldots,c_{10})
   =(6,2,-1,2,2,-2,-2,0,-1,-2,-1),                            \tag{22}
\]

so the negative curvature at (G=2) is immediately followed by positive
curvature at the difference (3).  This exactly falsifies Candidate SC.

## 3. Exact computation

The audit is in

    problems/864/compute/p52/audit_arc_spectral_factor.py

and writes

    problems/864/compute/p52/audit_results.json

Run it with

    python -B problems/864/compute/p52/audit_arc_spectral_factor.py --max-width 18

All polynomial, Toeplitz, autocorrelation, slope, and curvature checks
use integers; the factors of (1/2) in (H,T,s,c) are cleared.

The script first rechecks the five stored P47 witnesses.  Every witness
passes (2), (5), both exact profiles, all-circle autocorrelation equality,
and every tail inequality (15).  Every one falsifies Candidate SC:

\[
\begin{array}{c|c|c|c|c}
p&G&W&L&R(1)^2/\sum r_n^2\\ \hline
5&6&12&30&5202/193\\
9&18&49&116&118336/1151\\
10&42&55&152&522242/4001\\
11&23&84&191&1901641/11245\\
12&24&107&238&846400/4093
\end{array}                                                     \tag{23}
\]

The exhaustive census covers every endpoint-normalized Sidon ruler with
(W\leq18), and every dangerous gap (1\leq G<W):

\[
\begin{array}{c|r|r}
p&\text{Sidon rulers}&\text{valid }(Z,G)\text{ pairs}\\ \hline
2&18&153\\
3&144&1309\\
4&548&3484\\
5&614&1823\\
6&16&14\\ \hline
\text{total}&1340&6783
\end{array}                                                     \tag{24}
\]

All 6783 pairs pass (15); the minimum value of (2s_n) is one.  All
6783 fail Candidate SC, as (17) already predicts.  In lexicographic
order ((p,W,G,Z)), (3) is the first counterexample with (p\geq3).
The JSON file contains its full Gram matrix and the certificates
(18)--(22).

## 4. Winding and the reduced frontier

Away from unit-circle zeros of (P), the relative phase is

\[
              \Theta={B\over A}=x^{G+W}{P\over P^*}.            \tag{25}
\]

If (P) has no unit-circle zeros and (N_{\mathbb D}(P)) denotes its
number of zeros in the open unit disk, the argument principle gives

\[
                 \operatorname {wind}(\Theta)
                    =G+2N_{\mathbb D}(P).                       \tag{26}
\]

Thus winding does not isolate (G) without a separate zero-distribution
estimate for this sparse Newman factor.  The finite Toeplitz matrix (5)
does even less: all its scalar spectral data are exactly independent of
the arc parameters.

The surviving inequality (15) says that (s_n\) never becomes negative.
The falsifier shows that asking (s_n) to have a single peak is already
too strong, even with every P52 structural hypothesis.  A successful
continuation must instead bound how far a decrease of (s) can precede
a later increase.  By (14), the extremal such curvature inversion has
negative index (G) and positive index (W), so its span is exactly

\[
                              W-G.                               \tag{27}
\]

Consequently the strictly narrower frontier is an
(o(p^2)) bound for the curvature-inversion span in (27), in the
subcritical regime where the Sidon width bound alone does not finish the
problem.  Such a bound must use arithmetic information beyond symmetric
unimodality of (R), monotonicity of its autocorrelation, and the
principal Gram spectrum (6).  No such bound is proved here.

The public problem record still lists Erdos #864 as open and records no
partial solution.  The source audit in P49 likewise finds no applicable
published theorem with the needed leading constant.  See
<https://www.erdosproblems.com/864> (accessed 2026-07-12).
