# P73: completion overlap structure and a finite reduction

## Verdict

I did not find a proof of the unrestricted inequality

\[
                         2\beta\le h_S.                 \tag{1}
\]

There is, however, an exact additive-energy identity for its left side and
a rigorous reduction of the remaining infinite problem to 35 finite
parameter boxes.  The reduction uses two mechanisms which are absent from
the failed local charges `2v<=dR` and `v+2w<=2hD`:

1. the non-forced kernel created by reflected completion is the overlap
   defect of three explicit sum layers;
2. every admissible set contains a large genuine Sidon transversal, while
   the whole set has a precisely bounded positive-difference multiplicity.
   A weighted short-difference argument converts either fact into a lower
   bound for the span.

Consequently, (1) is proved except possibly in the following cases (the
span-55 census has already been applied):

\[
\begin{array}{c|c|c|c}
(p,\delta)&u&|A|=2p+\delta+u&\hbox{only spans still requiring a check}\\ \hline
(1,1)&8\le u\le26&11\le |A|\le29&56\le L\le
 \left\lceil(3u^2+9u+8)/4\right\rceil-1\\
(2,0)&7\le u\le17&11\le |A|\le21&56\le L\le
 \left\lceil(3u^2+11u+16)/4\right\rceil-1\\
(2,1)&7\le u\le11&12\le |A|\le16&56\le L\le
 \left\lceil(3u^2+13u+24)/4\right\rceil-1.
\end{array}                                               \tag{2}
\]

In particular, a counterexample to (1), if one exists, has at most 29
points and span at most 567.  This is a finite reduction, not a proof by
extrapolation from the census.

## 1. Setup

Use the notation of P56. Thus `A subset [0,L]` is endpoint-normalized with
`min A=0`, `max A=L`, is admissible, and `sigma` is its unique repeated
unordered sum.

\[
 P=A\cap(\sigma-A),\qquad R=A\setminus P,
\]

\[
 |P|=c=2p+\delta,\qquad |R|=u,
\]

where `delta` records the exceptional midpoint.  We only consider `u>0`.
The reflected completion is

\[
 F=P\cup R\cup(\sigma-R).
\]

Let `S=A+A` denote the support of unordered sums (the support is the same
for ordered sums), and put

\[
 h_S=|[0,2L]\setminus S|.
\]

P56 gives

\[
 h_S=2L-left(2p(p+\delta)+cu+\binom{u+1}{2}\right).     \tag{3}
\]

For `i<=j`, the virtual completion label is

\[
 d_{ij}=|r_i+r_j-\sigma|.
\]

The completion defect `beta` is the total excess when these virtual labels
are added to the old positive-difference labels.

## 2. Exact three-layer overlap identity

Separate the original sum support into

\[
 C=P+P,\qquad T=S\setminus C.
\]

Every sum represented by a pair touching `R` is unique and is not in `C`,
so `T` is exactly that residual sum layer.  Define its reflected layer and
the nonzero residual-difference layer by

\[
 J=2\sigma-T,
\]

\[
 K=\{\sigma+r-r':r,r'\in R,\ r\ne r'\}.
\]

### Lemma P73.1 (completion overlap identity)

One has

\[
 F+F=C\cup T\cup J\cup K                              \tag{4}
\]

and

\[
 \boxed{
  2\beta
   =|J\cap S|+|K\cap(S\cup J)|.
 }                                                       \tag{5}
\]

Equivalently,

\[
 2\beta=|C|+2|T|+|K|-|C\cup T\cup J\cup K|.            \tag{6}
\]

#### Proof

The sums in `F+F` have four types.  Core-core sums form `C`.  Sums in the
original half which touch `R` form `T`.  Reflecting both endpoints of such
a pair gives `J`.  A mixed pair `r+(sigma-r')` gives `sigma+r-r'`; the case
`r=r'` is the exceptional label `sigma`, already in `C`, and the other
cases give `K`.  This proves (4).

The positive differences represented by a pair touching `R` are globally
unique.  In particular, the ordered nonzero residual differences are all
distinct, so

\[
 |K|=u(u-1).
\]

If the completion introduced no new collision, its sum support would have

\[
 |C|+2|T|+u(u-1)
\]

labels.  The completed set is symmetric about `sigma/2`.  Each unit of
positive-difference defect removes the two sum labels `sigma-d` and
`sigma+d`.  Hence its actual sum support has size

\[
 |F+F|=|C|+2|T|+u(u-1)-2\beta,
\]

which proves (6).  Finally `C` and `T` are disjoint, `S=C disjoint_union T`,
and `|J|=|T|`.  Add `J` to `S`, then add `K`; ordinary inclusion-exclusion
turns (6) into (5).  QED.

Thus `2 beta` is not merely bounded by an additive energy: it is exactly
the non-forced rank defect of the reflected residual-sum layer and the
residual-difference layer over the original sum support.

An independent exhaustive rebuild checked (4)--(6) on all 3,008
nonempty-residual admissible sets of span at most 18.

## 3. A weighted lower bound for almost-Sidon rulers

The following lemma is the main new mechanism.  It is useful independently
of completion.

For integers `m>=0` and `e>=0`, put

\[
 e_m=\min(e,\lfloor m/2\rfloor)
\]

and let

\[
 \mathbf b(m,e)=(1,1,2,2,\ldots,e_m,e_m,
                 e_m+1,e_m+2,\ldots,m-e_m)              \tag{7}
\]

(with the evident omission of the doubled initial block when `e_m=0`).
Write

\[
 Q(m,e)=\sum_j b_j
 =\frac{e_m(e_m+1)+(m-e_m)(m-e_m+1)}2.                  \tag{8}
\]

For `n>=2` and `1<=h<n`, define

\[
 M_{n,h}=hn-\frac{h(h+1)}2,                             \tag{9}
\]

and, for `1<=t<n`,

\[
 \lambda_t(n,h)=
 \sum_{j=1}^h
 \#\{i:0\le i<n-j,\ i<t\le i+j\}.                     \tag{10}
\]

Let `lambda_(1)<=...<=lambda_(n-1)` be these coefficients in increasing
order, let `C_{n,h}=max_t lambda_t(n,h)`, and set

\[
 W(n,h,e)=\sum_{j=1}^{n-1}\lambda_{(j)}b_j(n-1,e).      \tag{11}
\]

Finally define the completely explicit integer

\[
 \mathcal G(n,e)=
 \max_{1\le h<n}
 \left[
 Q(n-1,e)+
 \left\lceil
  \frac{(Q(M_{n,h},e)-W(n,h,e))_+}{C_{n,h}}
 \right\rceil
 \right].                                               \tag{12}
\]

### Lemma P73.2 (weighted short-difference bound)

Let `B={b_0<...<b_{n-1}}` be an integer set.  Suppose every positive
difference has at most two representations and the total difference excess

\[
 \sum_{d>0}(r_{B-B}(d)-1)_+
\]

is at most `e`.  Then

\[
 \boxed{\operatorname{span}(B)\ge\mathcal G(n,e).}      \tag{13}
\]

#### Proof

Put `g_t=b_t-b_{t-1}`.  Select all differences

\[
 b_{i+j}-b_i\qquad(1\le j\le h,\ 0\le i<n-j).
\]

There are `M_{n,h}` of them.  Their multiplicities are at most two and
their total excess is at most `e`.  Among all positive integer multisets
with those constraints, the componentwise smallest sorted multiset is
`b(M_{n,h},e)`.  Therefore their sum is at least
`Q(M_{n,h},e)`.

On the other hand, the same sum is

\[
 \sum_{t=1}^{n-1}\lambda_t(n,h)g_t.                    \tag{14}
\]

The consecutive gaps themselves are positive differences, so they also
have multiplicity at most two and total excess at most `e`.  Sort the gaps
and use rearrangement.  Their minimal sorted baseline is
`b(n-1,e)`.  Any additional total gap length can be placed, in this
relaxation, on a coefficient no larger than `C_{n,h}`.  Hence, writing
`L=sum g_t`,

\[
 \sum_t\lambda_tg_t
 \le W(n,h,e)+C_{n,h}(L-Q(n-1,e)).                      \tag{15}
\]

Combine the lower bound with (15), solve for `L`, take the ceiling, and
then maximize over `h`.  This is (13).  QED.

This is a difference-energy argument with an order-sensitive endpoint
correction.  The ordinary Erdos--Turan short-difference estimate results
from discarding the baseline term in (15).

## 4. Two large Sidon witnesses inside `A`

The difference support of `A` has a particularly simple multiplicity
profile.  All differences represented by a pair touching `R` are unique
and disjoint from core differences.  Core differences have multiplicity at
most two.  Since

\[
 \binom c2-|D^+(P)|
 =\binom{2p+\delta}{2}-p(p+\delta)
 =p(p+\delta-1),                                        \tag{16}
\]

Lemma P73.2 applied to the whole set gives

\[
 L\ge\mathcal G(2p+\delta+u,\ p(p+\delta-1)).           \tag{17}
\]

There is also a genuine Sidon subset of size `u+p+1`.  If `delta=0`, keep
one complete exceptional pair and one point from every other reflected
pair.  If `delta=1`, keep the midpoint and one point from each reflected
pair.  In either case adjoin all of `R`.  A repeated sum in this subset
would have to be `sigma`, but the construction retains exactly one
representation of `sigma`.  Thus

\[
 L\ge\mathcal G(u+p+1,0).                               \tag{18}
\]

Define

\[
 B(p,\delta,u)=\max\{
 \mathcal G(2p+\delta+u,p(p+\delta-1)),
 \mathcal G(u+p+1,0)\}.                                 \tag{19}
\]

Equations (17)--(19) use only positive-difference multiplicities and the
linear order; they do not assume the desired completion inequality.

## 5. Reduction of `2 beta <= h_S`

There are `binom(u+1,2)` virtual residual pairs, so always

\[
 \beta\le\binom{u+1}{2}.                                \tag{20}
\]

Combining (3) and (20) proves (1) whenever

\[
 L\ge R(p,\delta,u):=
 p(p+\delta)+\frac{cu}{2}+\frac{3u(u+1)}4.              \tag{21}
\]

P61 already proves (1) when

\[
 u\le2c-5.                                               \tag{22}
\]

For the complementary range, exact evaluation of (12) gives

\[
 B(p,\delta,u)\ge R(p,\delta,u)                         \tag{23}
\]

for every parameter triple except

\[
\begin{array}{c|c}
(p,\delta)&u\\ \hline
(1,1)&2\le u\le26,\\
(2,0)&4\le u\le17,\\
(2,1)&6\le u\le11.
\end{array}                                              \tag{24}
\]

This is a finite integer calculation using the displayed formula (12), not
a search over sets. There are 45 triples in (24). The exact span-55 census
`compute/p66/decomposition_L55.json` has no failure of (1), reducing (24)
to the 35 boxes in (2). The stored artifact's SHA-256 is
`FF5C2F7A993CD48DCCAB18F4F249EBB1CD467AA61C74217A4DE8A04DB15EEB88`.

For completeness, the extrema of the residual boxes are

\[
\begin{array}{c|c|c}
(p,\delta)&\max u&\lceil R(p,\delta,u)\rceil\\ \hline
(1,1)&26&568,\\
(2,0)&17&268,\\
(2,1)&11&133.
\end{array}                                              \tag{25}
\]

Thus any falsifier has `L<ceil(R)` and hence the absolute bound `L<=567`.

## 6. Exact arithmetic checker for the parameter reduction

The following short program evaluates (7)--(23), asserts exactly the three
rows in (24), and prints them. It uses integer arithmetic only.

~~~python
def qsum(m, e):
    e = min(e, m // 2)
    return (e*(e+1) + (m-e)*(m-e+1)) // 2

def baseline(m, e):
    e = min(e, m // 2)
    return ([x for i in range(1, e+1) for x in (i, i)]
            + list(range(e+1, m-e+1)))

def G(n, e):
    ans = 0
    for h in range(1, n):
        lam = []
        for t in range(1, n):
            z = 0
            for j in range(1, h+1):
                lo = max(0, t-j)
                hi = min(t-1, n-j-1)
                z += max(0, hi-lo+1)
            lam.append(z)
        lam.sort()
        C = max(lam)
        b = baseline(n-1, e)
        W = sum(x*y for x, y in zip(lam, b))
        M = h*n - h*(h+1)//2
        extra = max(0, qsum(M, e)-W)
        ans = max(ans, qsum(n-1, e)+(extra+C-1)//C)
    return ans

bad = []
for delta in (0, 1):
    for p in range(1, 100):
        if p + delta < 2:
            continue
        c = 2*p + delta
        for u in range(max(1, 2*c-4), 500):
            e = p*(p+delta-1)
            lower = max(G(c+u, e), G(u+p+1, 0))
            four_R = (4*p*(p+delta) + 2*c*u
                      + 3*u*(u+1))
            if 4*lower < four_R:
                bad.append((p, delta, u))

expected = ([(1, 1, u) for u in range(2, 27)]
            + [(2, 0, u) for u in range(4, 18)]
            + [(2, 1, u) for u in range(6, 12)])
assert sorted(bad) == sorted(expected)
print(sorted(bad))
~~~

The loop bound 500 is certified as follows. Put `s=u+p+1`. The ordinary
short-difference choice `h=floor(sqrt(s))` in (12) gives

`G(s,0)>=s^2-3s^(3/2)`.

In the complementary P61 range `u>=2c-4`, one has `s<=3u/2` in either tail
`u>=500` or `p>=100`. Direct expansion gives

`s^2-R=(u^2+4pu+5u+8p+4)/4` for `delta=0`,

`s^2-R=(u^2+4pu+3u+4p+4)/4` for `delta=1`.

Thus `s^2-R>=u^2/4`. For `u>=500`, the required comparison follows from
`(u^2/4)^2>=9(3u/2)^3`, valid for `u>=486`. If `p>=100` and `u<500`, then
`s^2-R>=u^2/4+100u`; it is enough that
`(u+400)^2>=486u`, whose difference is
`u^2+314u+160000>0`. Hence the exact loop domain `p<100,u<500` contains
every parameter triple not eliminated analytically.

## 7. Remaining precise lemma

The original infinite completion problem has therefore been replaced by
the following strictly finite statement.

**Finite completion-overlap lemma.** For the 35 parameter boxes in (2),
every endpoint-normalized admissible `A subset [0,L]` satisfies

\[
 |J\cap S|+|K\cap(S\cup J)|\le |[0,2L]\setminus S|.     \tag{26}
\]

This lemma has a concrete mechanism: (5) identifies its left side as the
two actual overlap layers, and Lemma P73.2 bounds every configuration
outside the finite boxes by weighted positive-difference energy.  A finite
SAT/CP search for (26) needs only the ranges in (2), not unbounded `p,u,L`.

The result also explains why a proof based only on the scalar fields
`v,w,h_D,d_R` stalled.  Those fields forget whether a defect comes from
`J intersect S` or from `K intersect (S union J)`.  Equation (5) retains
that missing incidence structure.
