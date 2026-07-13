# P04: energy/Fourier lane

## Verdict

There is an exact energy and higher fibre-moment lemma.  It handles diagonal
pairs and an exceptional fibre of arbitrary multiplicity.  It also gives an
exact description of every repeated difference.

The scalar moment plus interval-support route does not give the leading
constant `4/3` in `|A|^2 <= (4/3+o(1))N`.  After the exceptional Fourier
coefficient is removed, every fixed Holder moment gives only

\[
 |A|^2\le (4+o(1))N.
\]

The standard Fejer/sliding-window argument uses more location information but,
with only the global interval as support, gives only

\[
 |A|^2\le (2+o(1))N.
\]

The tempting local estimate that would turn this into `4/3` is explicitly
false on the Erdos--Freud reflected family.  On that family the missing factor
comes instead from the two separated spatial blocks.  Thus a sharp Fourier
argument needs a spatial concentration-versus-repeated-difference lemma; no
further scalar energy identity can supply it.

## 1. Exact sum-fibre profile

Let `A subseteq [1,N]`, `k=|A|`, and suppose the unique repeated unordered sum
is `sigma`.  Put

\[
 \mu(s)=\#\{\{a,b\}:a,b\in A,\ a\le b,\ a+b=s\},
 \qquad m=\mu(\sigma)\ge2,
\]

and retain the diagonal indicator

\[
 \delta={\bf1}_{\{\sigma/2\in A\}}\in\{0,1\}.
\]

Thus there are `t=m-delta` off-diagonal complementary pairs on the exceptional
fibre.  For ordered representations define

\[
 r(s)=\#\{(a,b)\in A^2:a+b=s\},\qquad
 q=r(\sigma)=2m-\delta=2t+\delta.
\]

Finally let

\[
 P=A\cap(\sigma-A).
\]

The exceptional representations are disjoint complementary pairs, apart from
the possible midpoint.  Consequently

\[
 |P|=q\le k.                                                   \tag{1}
\]

### Lemma 1 (all ordered sum-fibre moments)

The coefficient multiset of `r` is exactly

\[
 \begin{array}{c|c}
 \text{coefficient}&\text{number of sum values}\\ \hline
 q&1\\
 1&k-\delta\\
 2&\binom{k}{2}-t.
 \end{array}                                                   \tag{2}
\]

In particular,

\[
 |A+A|=1+k-\delta+\binom{k}{2}-\frac{q-\delta}{2}
       =\binom{k+1}{2}-(m-1),                                 \tag{3}
\]

and, for every integer `p>=1`,

\[
 \begin{aligned}
 M_p^+(A):=\sum_s r(s)^p
 &=q^p+(k-\delta)+2^p\left(\binom{k}{2}-\frac{q-\delta}{2}\right)\\
 &=k+2^p\binom{k}{2}+q^p-\delta-2^{p-1}(q-\delta).             \tag{4}
 \end{aligned}
\]

If

\[
 h(s)=r(s)-q{\bf1}_{\{s=\sigma\}},                            \tag{5}
\]

then the exceptional spike is removed exactly, not bounded:

\[
 \sum_s h(s)=k^2-q,                                           \tag{6}
\]

\[
 \sum_s h(s)^p=(k-\delta)+2^p
 \left(\binom{k}{2}-\frac{q-\delta}{2}\right),               \tag{7}
\]

and especially

\[
 \sum_s h(s)^2=2k^2-k-2q+\delta.                              \tag{8}
\]

**Proof.**  Every diagonal `a+a` outside `sigma` is a singleton unordered
fibre and hence has ordered coefficient one; there are `k-delta` of these.
There are `binom(k,2)` off-diagonal pairs, of which `t` lie over `sigma`.
Every remaining off-diagonal pair is alone on its unordered fibre and gives
ordered coefficient two.  The exceptional ordered coefficient is
`2t+delta=q`.  This proves (2), and all the displayed identities follow by
summing its three rows.  Notice that no upper bound on `m` was used.  QED.

For a genuine Sidon set there is no `sigma`; setting `q=delta=0` in (4), (6),
(7), and (8) gives the correct formulas, while (3) is replaced by
`|A+A|=binom(k+1,2)`.

## 2. Exact differences and additive energy

Define the ordered difference function

\[
 d(x)=\#\{(a,b)\in A^2:a-b=x\}.
\]

### Lemma 2 (reflection is the only repeated-difference mechanism)

For every `x != 0`,

\[
 d(x)\in\{0,1,2\}.                                            \tag{9}
\]

Let

\[
 {\cal R}=\{x\in\{1,\ldots,N-1\}:d(x)=2\},\qquad R=|{\cal R}|.
\]

Then

\[
 R=\frac{1}{2}\left(\binom q2-\frac{q-\delta}{2}\right)
  =\frac{q^2-2q+\delta}{4}.                                   \tag{10}
\]

Among positive differences, exactly `R` values have multiplicity two and
exactly

\[
 \binom{k}{2}-2R                                               \tag{11}
\]

values have multiplicity one.  Hence

\[
 |(A-A)\cap\mathbb Z_{>0}|=\binom{k}{2}-R\le N-1.              \tag{12}
\]

For every integer `p>=1`, all difference-fibre moments are therefore

\[
 \begin{aligned}
 M_p^-(A):=\sum_x d(x)^p
 &=k^p+2\left(\binom{k}{2}-2R+2^pR\right)\\
 &=k^p+k(k-1)+2(2^p-2)R.                                     \tag{13}
 \end{aligned}
\]

**Proof.**  Suppose `x != 0` and

\[
 a-b=c-d=x
\]

are distinct ordered representations.  Then `a+d=b+c`.  The unordered pairs
`{a,d}` and `{b,c}` are distinct: equality of those multisets would either
make the ordered difference representations equal or force `x=0`.  Therefore
their common sum must be `sigma`, and

\[
 c=\sigma-b,\qquad d=\sigma-a.                                \tag{14}
\]

Thus a second representation, when it exists, is the unique reflected one;
this proves (9).  It exists precisely when `a,b in P`, except that reflection
fixes the representation when `a+b=sigma`.

There are `binom(q,2)` two-element subsets of `P`.  Reflection partitions
them into two-cycles, except for the `t=(q-delta)/2` exceptional complementary
pairs.  Each two-cycle gives one doubled positive difference.  This proves
(10).  Since the total number of positive-difference representations is
`binom(k,2)`, (11)--(13) follow.  QED.

Taking `p=2` in either (4) or (13) gives the exact additive energy

\[
 \begin{aligned}
 E(A)&:=\#\{(a,b,c,d)\in A^4:a+b=c+d\}\\
 &=\sum_s r(s)^2=\sum_x d(x)^2\\
 &=2k^2-k+q^2-2q+\delta
  =2k^2-k+4R.                                                  \tag{15}
 \end{aligned}
\]

Thus the number of ordered nontrivial additive quadruples, after removing the
`2k^2-k` identical-or-swapped ones, is exactly

\[
 q^2-2q+\delta=4R.                                            \tag{16}
\]

In terms of the original unordered exceptional multiplicity,

\[
 E(A)=
 \begin{cases}
 2k^2-k+4m(m-1),&\delta=0,\\
 2k^2-k+4(m-1)^2,&\delta=1.
 \end{cases}                                                   \tag{17}
\]

This is valid for every `2<=m<=ceil(k/2)` allowed by the problem.

## 3. Fourier forms and what is, and is not, a higher moment

Use normalized Haar measure on `T=R/Z`, put `e(x)=exp(2 pi i x)`, and define

\[
 F(\theta)=\sum_{a\in A}e(a\theta),\quad
 G(\theta)=|F(\theta)|^2,\quad
 H(\theta)=F(\theta)^2-qe(\sigma\theta).                      \tag{18}
\]

Their Fourier coefficients are respectively

\[
 F(\theta)^2=\sum_s r(s)e(s\theta),\qquad
 G(\theta)=\sum_xd(x)e(x\theta),\qquad
 H(\theta)=\sum_sh(s)e(s\theta).                             \tag{19}
\]

Parseval and (15) give

\[
 \int_{\mathbb T}|F(\theta)|^4\,d\theta
 =2k^2-k+q^2-2q+\delta,                                      \tag{20}
\]

while exact spike removal gives

\[
 \int_{\mathbb T}|F(\theta)^2-qe(\sigma\theta)|^2\,d\theta
 =2k^2-k-2q+\delta.                                          \tag{21}
\]

For every integer `p>=2`, coefficient orthogonality gives the genuine
multi-frequency identities

\[
 M_p^+(A)=\int_{\mathbb T^{p-1}}
 \left(\prod_{j=1}^{p-1}F(\theta_j)^2\right)
 F\left(-\sum_{j=1}^{p-1}\theta_j\right)^2\,d\boldsymbol\theta, \tag{22}
\]

\[
 \sum_sh(s)^p=\int_{\mathbb T^{p-1}}
 \left(\prod_{j=1}^{p-1}H(\theta_j)\right)
 H\left(-\sum_{j=1}^{p-1}\theta_j\right)\,d\boldsymbol\theta, \tag{23}
\]

and

\[
 M_p^-(A)=\int_{\mathbb T^{p-1}}
 \left(\prod_{j=1}^{p-1}G(\theta_j)\right)
 G\left(-\sum_{j=1}^{p-1}\theta_j\right)\,d\boldsymbol\theta. \tag{24}
\]

These are higher moments of the pair-sum or difference *fibres*.  They must
not be confused with the usual one-frequency even moments.  If
`r_j(n)=1_A^{*j}(n)`, then

\[
 \int_{\mathbb T}|F(\theta)|^{2j}\,d\theta=\sum_nr_j(n)^2.     \tag{25}
\]

For `j>=3`, (25) is not determined by `k,q,delta`, or even by all the moments
in (4).  For example, the two genuine Sidon sets

\[
 A_0=\{1,2,4\},\qquad A_1=\{1,2,5\}\subseteq[1,5]             \tag{26}
\]

both have three ordered sum coefficients equal to one and three equal to two.
Thus both have

\[
 M_p^+=3+3\cdot2^p\quad(p\ge1),\qquad \int|F|^4=15.
\]

Direct ordered triple-sum enumeration gives

\[
 \int|F_{A_0}|^6=99,\qquad \int|F_{A_1}|^6=93.                \tag{27}
\]

Indeed the nonzero triple-representation multiplicities are respectively
`1` twice, `3` five times, `4` once, `6` once, and `1` three times, `3` six
times, `6` once.  More generally,

\[
 \int|F|^6=\sum_{a,b\in A}\sum_s r(s)r(s+a-b),                \tag{28}
\]

which exposes the positional autocorrelations absent from (4).

## 4. Scalar interval support cannot produce `4/3`

The deflated coefficients `h` occupy at most `2N-2` positions of
`[2,2N]`.  Holder, (6), and (7) give, for every fixed integer `p>1`, the exact
inequality

\[
 (k^2-q)^p\le(2N-2)^{p-1}
 \left[(k-\delta)+2^p
 \left(\binom{k}{2}-\frac{q-\delta}{2}\right)\right].         \tag{29}
\]

For `p=2` this is

\[
 (k^2-q)^2\le(2N-2)(2k^2-k-2q+\delta).                       \tag{30}
\]

Since `q<=k`, every fixed `p` in (29) has the same leading consequence

\[
 k^2\le(4+o(1))N,                                             \tag{31}
\]

not `4N/3`.

This is an information-theoretic barrier for the coefficient histogram, not
just a weak choice of `p`.  Let `k` be even and suppose

\[
 1+\frac{k^2}{2}\le2N-1.                                     \tag{32}
\]

One can place in `[2,2N]` a nonnegative integer sequence `rho` having one
coefficient `k`, exactly `k` coefficients `1`, and exactly
`k(k-2)/2` coefficients `2`.  Then

\[
 \sum_s\rho(s)=k^2,
 \qquad
 \sum_s\rho(s)^p=k^p+k+2^p\frac{k(k-2)}2                     \tag{33}
\]

for every `p>=1`.  These are exactly all the sum-fibre moments in the
maximally paired case `q=k,delta=0`.  A symmetric placement on
`[-N+1,N-1]` also matches all difference-fibre moments in that case.  Condition
(32) permits `k^2=4N+O(1)`.

The synthetic profile need not be the convolution square of a set.  That is
precisely the point: interval support, integrality, the exceptional spike, and
the complete scalar moment sequence do not retain the nonlinear positional
constraint `rho=1_A*1_A`.

## 5. The exact `4/3` bridge and why global Fejer support misses it

Combining (3), (10), and (12) gives a useful exact identity:

\[
 |A+A|+|(A-A)\cap\mathbb Z_{>0}|
 =k^2+1-\frac{q^2+3\delta}{4}.                                \tag{34}
\]

This display is for the repeated-fibre case fixed in Section 1.  If there is
no exceptional fibre, the corresponding left side is exactly `k^2`, and the
ordinary Sidon interval bound applies.

Therefore the still-unproved interval packing estimate

\[
 |A+A|+|(A-A)\cap\mathbb Z_{>0}|\le N+o(N)                   \tag{35}
\]

would immediately settle the problem, because `q<=k` makes the left side of
(34) at least `3k^2/4+O(1)`.  Equation (35) is not supplied by the raw
supports: the sum set and positive difference set live in different intervals,
and (33) shows that their scalar profiles do not create an injection into `N`
positions.

The same obstruction appears quantitatively in the Fejer kernel.  For an
integer `u>=1`, let

\[
 C_j=\#\{a\in A:0\le j-a<u\},\qquad
 L_u(A)=|\{j:C_j>0\}|,
\]

and define the weighted doubled-difference mass

\[
 W_{\cal R}(u)=\sum_{\substack{x\in{\cal R}\\x<u}}(u-x).
\]

The exact sliding-window/Fourier identity is

\[
 \sum_jC_j^2=ku+2\sum_{x=1}^{u-1}(u-x)d(x).                  \tag{36}
\]

Since `d(x)<=1+1_{x in R}`, Cauchy and (36) prove

\[
 (ku)^2
 \le L_u(A)\left[u(k+u-1)+2W_{\cal R}(u)\right].             \tag{37}
\]

Using only `L_u(A)<=N+u-1` gives

\[
 k^2\le(N+u-1)
 \left(1+\frac{k-1}{u}+\frac{2W_{\cal R}(u)}{u^2}\right).     \tag{38}
\]

For `k=o(u)` and `u=o(N)`, the trivial sharp bound
`W_R(u)<=u(u-1)/2` yields only `k^2<=(2+o(1))N`.  A global-support
derivation of `4/3` from (38) would require, for some such scale,

\[
 W_{\cal R}(u)\le(1/6+o(1))u^2.                              \tag{39}
\]

The next section gives an explicit asymptotic falsifier to (39).

The exact spatial quantity retained by (37) shows the missing input.  It would
be sufficient to prove, at some mesoscopic `u`,

\[
 \frac{L_u(A)}N
 \left(1+\frac{2W_{\cal R}(u)}{u^2}\right)
 \le\frac43+o(1).                                             \tag{40}
\]

No claim that (40) is proved is made here.  It is the concentration-versus-
repetition frontier left after the exact Fourier calculation.

## 6. Symbolic Erdos--Freud audit

Let `B subseteq [1,L]` be Sidon, `|B|=b`, put

\[
 \sigma=3L+1,\qquad A=B\cup(\sigma-B)\subseteq[1,3L],
 \qquad N=3L.                                                  \tag{41}
\]

The two blocks are disjoint and contain no midpoint.  Every `b in B` gives
one unordered exceptional representation `b+(sigma-b)=sigma`.  Hence

\[
 k=2b,\qquad m=b,\qquad\delta=0,\qquad q=2b=k.                 \tag{42}
\]

Substitution into the preceding identities gives, with no asymptotic
simplification,

\[
 R=b(b-1),                                                     \tag{43}
\]

\[
 |A+A|=2b^2+1,\qquad |(A-A)\cap\mathbb Z_{>0}|=b^2,            \tag{44}
\]

\[
 M_p^+(A)=M_p^-(A)
 =(2b)^p+2b+2^{p+1}b(b-1),                                   \tag{45}
\]

\[
 E(A)=12b^2-6b,qquad E(A)-(2k^2-k)=4b(b-1),                  \tag{46}
\]

\[
 \sum_sh(s)^2=8b^2-6b,                                      \tag{47}
\]

and

\[
 |A+A|+|(A-A)\cap\mathbb Z_{>0}|=3b^2+1.                    \tag{48}
\]

Thus (34)--(35) are symbolically sharp on this family: for dense Sidon sets
`b^2=(1+o(1))L`, the right side of (48) is `N+o(N)`, and
`k^2=(4/3+o(1))N`.

The scalar support inequality (30), by contrast, becomes

\[
 (4b^2-2b)^2\le(2N-2)(8b^2-6b).                              \tag{49}
\]

With `N=3L` and `b^2=(1+o(1))L`, the two leading sides of (49) are
`16b^4` and `48b^4`; the interval-moment argument loses a factor of three on
the extremal model.

Finally, the doubled positive differences can be written exactly.  If
`b_i<b_j` are in `B`, then

\[
 b_j-b_i=(\sigma-b_i)-(\sigma-b_j)                            \tag{50}
\]

is a doubled low difference, while

\[
 \sigma-b_i-b_j=(\sigma-b_i)-b_j=(\sigma-b_j)-b_i             \tag{51}
\]

is a doubled high difference.  The two classes have `binom(b,2)` values each;
the remaining `b` positive differences `sigma-2b_i` are single.  Because
`B subseteq[1,L]`, the values in (50) are at most `L-1`, whereas those in
(51) are at least `L+1`.

For `u<=L`, it follows exactly that

\[
 W_{\cal R}(u)=W_B(u):=
 \sum_{\substack{b_j-b_i<u\\i<j}}(u-(b_j-b_i)).               \tag{52}
\]

Applying (36) to `B` itself gives

\[
 \frac{b^2u^2}{L+u-1}\le bu+2W_B(u),                         \tag{53}
\]

while Sidonicity gives `W_B(u)<=u(u-1)/2`.  For every scale satisfying
`b=o(u)` and `u=o(L)`, (53) and `b^2=(1+o(1))L` therefore give

\[
 W_{\cal R}(u)=W_B(u)=(1/2+o(1))u^2.                         \tag{54}
\]

For example, one may take `u=floor(L^{3/4})`.  Since `N=3L`, (54) covers
every scale allowed in (39), namely `k=o(u)` and `u=o(N)`.  It is therefore
the promised explicit falsifier to (39), including its existential
quantifier.

It also verifies the spatial frontier (40) on the model.  The `u`-window
support of the two separated blocks satisfies

\[
 L_u(A)\le2(L+u-1)=(2/3+o(1))N.                              \tag{55}
\]

Combining (54) and (55), the left side of (40) is at most

\[
 (2/3+o(1))(1+2\cdot(1/2+o(1)))=4/3+o(1).                    \tag{56}
\]

Thus the Erdos--Freud family has the largest possible local repeated-
difference weight, but its effective window support is only two thirds of the
ambient interval.  Replacing that effective support by the whole interval is
the precise loss in the global energy/Fourier lane.

## Result

Lemmas 1 and 2, identities (20)--(24), and the window inequality (37) are
proved exact statements with diagonals and arbitrary exceptional
multiplicity.  Equations (33) and (54) are explicit barriers: all scalar fibre
moments plus interval support allow leading constant `4`, and the local bound
needed to make global Fejer support yield `4/3` is false on Erdos--Freud.

The surviving sharp frontier is the spatial tradeoff (40), or an equivalent
proof of the hybrid packing estimate (35).  Either must use the locations of
the reflected pairs; it cannot be recovered from additive energy or the full
scalar fibre-moment sequence alone.
