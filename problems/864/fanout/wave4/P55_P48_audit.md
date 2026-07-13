# P55: audit of the P48 heterogeneous span claim

## Verdict

There are two different statements hidden in the phrase "disjoint positive
difference sets."

1. If it means only
   \[
   D^+(X)\cap D^+(Y)=\varnothing,                 \tag{1}
   \]
   the claimed span bound is false. An exact infinite counterexample is
   \[
   X_q=\{0,1\},\qquad
   Y_q=\{0,2,4,\ldots,2(q-1)\}.                  \tag{2}
   \]
   Here the two positive-difference sets are respectively
   \(\{1\}\) and \(\{2,4,\ldots,2(q-1)\}\), but, with
   \(p=|X_q|+|Y_q|=q+2\),
   \[
   U+V=2q-1=o(p^2).                              \tag{3}
   \]
   The failure is that differences inside \(Y_q\) have many
   representations.

2. Under P48's actual obstruction hypothesis that the guarded union \(E\)
   is Sidon, the validity gate also says that \(X\) and \(Y\) are Sidon,
   including diagonal pair sums. Thus every positive difference occurring
   inside either component has exactly one endpoint pair, and (1) makes all
   those differences globally distinct. Under this intended hypothesis the
   span claim is true, with the following explicit bound. If
   \(p=|X|+|Y|\ge 9\) and \(h=\lfloor\sqrt p\rfloor\), then
   \[
   \boxed{
   U+V\ \ge\ {h\over h+1}
      \left(p-{3h+1\over2}\right)^2
   \ \ge\ p^2\left(1-{4\over\sqrt p}-{1\over p}\right).}
                                                               \tag{4}
   \]

Consequently P48's fully range-guarded heterogeneous-union obstruction is
valid, but inequality (3) in P48 must explicitly inherit the internal Sidon
hypotheses. Cross-disjointness of the two difference-value sets alone is
not enough.

## 1. Conventions and hypotheses

All sets below are finite sets of integers. Integrality is essential: the
proof packs distinct positive differences into the positive integers. Over
the reals, an arbitrary common rescaling would destroy any lower bound of
the form (4).

Write
\[
X=\{0=x_0<x_1<\cdots<x_{m-1}=U\},\qquad
Y=\{0=y_0<y_1<\cdots<y_{n-1}=V\},               \tag{5}
\]
and \(p=m+n\). Endpoint-normalized means exactly that the minima are zero
and the displayed maxima \(U,V\) are attained. A one-point component is
allowed, with span zero; the proof also covers that case.

The positive-difference convention is
\[
D^+(A)=\{a_j-a_i:0\le i<j<|A|\}.                \tag{6}
\]
Zero differences are excluded. If zero were included, every two nonempty
sets would have a common difference and (1) would be unusable.

The hypothesis needed for (4) is the global internal-difference condition
\[
\begin{split}
|D^+(X)|&={m\choose2},\\
|D^+(Y)|&={n\choose2},\\
D^+(X)\cap D^+(Y)&=\varnothing.
\end{split}                                      \tag{7}
\]
Thus (7), unlike (1) alone, asserts both internal injectivity and cross
disjointness.

For an integer set, internal injectivity in (7) is equivalent to Sidonicity
with diagonal sums included. Indeed, if
\(a'-a=b'-b>0\), then
\[
a'+b=b'+a.                                      \tag{8}
\]
Uniqueness of unordered pair sums forces the two endpoint pairs to agree.
Conversely, suppose two distinct unordered pairs satisfy
\(a+b=c+d\). Order them as \(a\le b\), \(c\le d\), and, after swapping the
pairs, take \(a<c\). Then \(b>d\) and
\[
b-d=c-a>0,                                      \tag{9}
\]
which is a repeated positive difference. This also catches diagonal
collisions: for example, \(0+2=1+1\) corresponds to
\(1-0=2-1\). Off-diagonal pair-sum uniqueness is therefore insufficient.

## 2. Short-lag packing lemma

Let
\[
A=\{0=a_0<a_1<\cdots<a_{r-1}=W\}               \tag{10}
\]
have distinct positive differences. For an integer \(k\) with
\(1\le k\le r-1\), select all differences whose index lag is at most
\(k\):
\[
\mathcal L_k(A)
=\{a_{i+s}-a_i:1\le s\le k,\ 0\le i<r-s\}.
                                                               \tag{11}
\]
Their number is
\[
L_k(r)=\sum_{s=1}^k(r-s)
=kr-{k(k+1)\over2}.                             \tag{12}
\]

For each fixed lag \(s\), telescoping at the two ends gives
\[
\begin{split}
\sum_{i=0}^{r-s-1}(a_{i+s}-a_i)
&=\sum_{j=r-s}^{r-1}a_j-\sum_{j=0}^{s-1}a_j\\
&\le sW.
\end{split}                                      \tag{13}
\]
Consequently
\[
\sum_{d\in\mathcal L_k(A)}d
\le {k(k+1)\over2}W.                            \tag{14}
\]
The selected values are distinct positive integers, so their sum is at
least \(1+2+\cdots+L_k(r)\). Hence
\[
L_k(r)(L_k(r)+1)\le k(k+1)W.                    \tag{15}
\]

The same argument applies to selected lags from both \(X\) and \(Y\).
Under (7) their union is still a set of distinct positive integers, while
the right side of (14) becomes the corresponding weighted sum of \(U\)
and \(V\).

## 3. Explicit heterogeneous bound

Assume (7), let \(p=m+n\ge9\), and put
\(h=\lfloor\sqrt p\rfloor\). There are two cases.

### Case 1: both components have at least \(h+1\) points

Use lags \(1,\ldots,h\) in both components. The total number of selected
differences is
\[
L=h m-{h(h+1)\over2}
  +h n-{h(h+1)\over2}
 =h(p-h-1).                                     \tag{16}
\]
Equations (13)--(15), now summed over both components, give the exact
inequality
\[
U+V\ge {L(L+1)\over h(h+1)}.                    \tag{17}
\]
Dropping the positive \(+1\) factor yields
\[
U+V\ge {h\over h+1}(p-h-1)^2
\ge {h\over h+1}
       \left(p-{3h+1\over2}\right)^2.           \tag{18}
\]

### Case 2: one component has at most \(h\) points

Let the smaller size be \(s\le h\), and let the other component have size
\(q=p-s\) and span \(W\). Since \(p\ge9\), one has \(h\ge3\) and
\(q\ge p-h\ge h+1\), so lags through \(h\) are available in the larger
component. They give
\[
K=hq-{h(h+1)\over2}.                            \tag{19}
\]
The one-component form of (15) gives the exact inequality
\[
U+V\ge W\ge {K(K+1)\over h(h+1)}.               \tag{20}
\]
Using \(q\ge p-h\) and again dropping the positive \(+1\) factor,
\[
\begin{split}
U+V
&\ge {h\over h+1}
       \left(q-{h+1\over2}\right)^2\\
&\ge {h\over h+1}
       \left(p-{3h+1\over2}\right)^2.
\end{split}                                      \tag{21}
\]
This proves the first inequality in (4) uniformly, including arbitrarily
unbalanced component sizes.

For the simpler displayed error, set
\[
a={1\over h+1},\qquad c={3h+1\over2p}.           \tag{22}
\]
The first lower bound in (4), divided by \(p^2\), is
\((1-a)(1-c)^2\). For \(p\ge9\), \(0<c<1\), and therefore
\[
1-(1-a)(1-c)^2
=a+(1-a)(2c-c^2)\le a+2c.                       \tag{23}
\]
Since \(h+1>\sqrt p\) and \(h\le\sqrt p\),
\[
a+2c
\le {1\over\sqrt p}+{3\over\sqrt p}+{1\over p}.
                                                               \tag{24}
\]
This proves the second inequality in (4), and in particular
\(U+V\ge(1-o(1))p^2\).

## 4. Application to P48's guarded union

Take integers \(G,T\) satisfying
\[
G>\max(U,V),\qquad T>G+3U,                       \tag{25}
\]
and set
\[
Z=X\cup(T+Y),\qquad E=G+2Z.                     \tag{26}
\]
The guards give \(T>U\), so the union is disjoint and \(|E|=m+n=p\).
Also, the affine lift satisfies
\(e_i+e_j=e_k+e_l\) if and only if
\(z_i+z_j=z_k+z_l\), including when either pair is diagonal.
The three unordered pair-sum bands of \(Z\) are
\[
[0,2U],\qquad[T,T+U+V],\qquad[2T,2T+2V].         \tag{27}
\]
The guards imply \(T>2U\) and \(T>U+V\), so these bands are disjoint.
The two internal bands are Sidon exactly when the two internal parts of
(7) hold. Two cross sums agree nontrivially exactly when a positive
difference of \(X\) equals a positive difference of \(Y\). Thus, with
diagonal sums retained,
\[
E\text{ is Sidon}\quad\Longleftrightarrow\quad (7).             \tag{28}
\]

Repeated summands are also harmless for the three-sum exclusion under the
strict guards. The equality of a target in \(E\) with three elements of
\(E\) is equivalent to
\[
z_t=G+z_a+z_b+z_c.                              \tag{29}
\]
A low target is at most \(U<G\). For a high target, which is at most
\(T+V\), the right side of (29) is below \(T\) if it has no high summand,
is above \(T+V\) if it has exactly one, and is above \(T+V\) if it has at
least two. This classifies high summands with multiplicity, so it includes
\(z_a=z_b\), \(z_b=z_c\), and \(z_a=z_b=z_c\). Therefore
\[
E\cap3E=\varnothing.                             \tag{30}
\]

Finally,
\[
\begin{split}
\max E
&=G+2(T+V)\\
&>3G+6U+2V\\
&>5(U+V),
\end{split}                                      \tag{31}
\]
because the last difference is \(3(G-V)+U>0\). Combining (4) and (31)
gives the explicit guarded-union estimate
\[
{\max E\over p^2}
>5\left(1-{4\over\sqrt p}-{1\over p}\right),   \tag{32}
\]
and hence
\[
\liminf_{p\to\infty}{\max E\over p^2}\ge5.    \tag{33}
\]

## 5. Exact computation

The independent checker is
`problems/864/compute/p55/audit_span_claim.py`. The command

```text
python problems/864/compute/p55/audit_span_claim.py --max-span 18 --gate-span 9
```

produced `problems/864/compute/p55/audit_span_results.json` and checked:

* all 262,144 endpoint-normalized integer subsets through span 18;
* 1,341 strong Sidon rulers, with 2,355 additional sets rejected because
  off-diagonal sums were unique but a diagonal-sensitive collision remained;
* all 5,776 ordered ruler pairs through span 9 against the guarded validity
  gate, including 1,019 cross-disjoint pairs and all repeated-summand
  triples;
* all 91,947 ordered difference-disjoint pairs through span 18, including
  72 pairs with \(p\ge9\), against the exact inequalities (17) and (20);
* the unbalanced branch (20) on explicit strong-Sidon pairs at
  \(p=9,16,25,36\); and
* the literal cross-disjoint-only counterexample (2) at
  \(q=8,16,32,64\).

The computation is not used as a proof of (4); it independently audits the
endpoint, diagonal, zero-difference, cross-disjointness, and repeated-triple
conventions used in the proof.
