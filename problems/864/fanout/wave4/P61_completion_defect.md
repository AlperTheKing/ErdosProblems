# P61: two-scale completion defect and reflection-shift cancellation

## Verdict

P56 can be strengthened without assuming that the residual is negligible.
The missing observation is to apply the reflected bound twice: once to the
paired core and once to a repaired virtual completion.  The core application
pays the reflection shift with the opposite sign.

Use the P56 notation

\[
 P=A\cap(\sigma-A),\qquad R=A\setminus P,
\]

\[
 |P|=c=2p+\delta,\qquad |R|=u,\qquad k=c+u,
\]

\[
 L=\max A-\min A,\qquad
 \tau=|\sigma-\min A-\max A|,
\]

and let

\[
 \beta=(p+u)(p+u+\delta)-|D^+(A\cup(\sigma-R))|,
 \qquad b=\min(u,\beta).
\]

Let \(H_\delta(q)\) be the minimum span of a fully reflected admissible
set with \(q\) off-diagonal reflected pairs and midpoint flag \(\delta\).
Then

\[
 \boxed{L-\tau\ge H_\delta(p)}                                      \tag{1}
\]

and

\[
 \boxed{
 L+\tau\ge
 \max\left\{
 H_\delta(p+u-b),
 |D^+(A)|+\binom{u-b+1}{2}
 \right\}.
 }                                                                  \tag{2}
\]

Consequently

\[
 \boxed{
 2L\ge H_\delta(p)+
 \max\left\{
 H_\delta(p+u-b),
 |D^+(A)|+\binom{u-b+1}{2}
 \right\}.
 }                                                                  \tag{3}
\]

The exact original difference-label count is

\[
 |D^+(A)|=p(p+\delta)+cu+\binom u2.                                 \tag{4}
\]

Thus (2) retains every original residual difference label, including those
incident to residual points deleted by the P56 repair, as well as every
surviving virtual label.  Equation (3) is a shift-free quantitative
completion inequality.  It has no hypothesis on \(u/k\).

If the reflected sharp bound is available as

\[
 H_\delta(q)\ge {3\over4}(2q+\delta)^2-E_\delta(q),                 \tag{5}
\]

then (3) gives, already from its first branch,

\[
 \boxed{
 L\ge {3\over4}k^2+{3\over4}\Xi(k,u,b)
 -{E_\delta(p)+E_\delta(p+u-b)\over2},
 }                                                                  \tag{6}
\]

where

\[
 \boxed{
 \Xi(k,u,b)=u^2-2b(k+u)+2b^2.
 }                                                                  \tag{7}
\]

Hence the reflected sharp bound implies the general sharp bound whenever

\[
 \boxed{
 3\Xi(k,u,b)\ge
 2E_\delta(p)+2E_\delta(p+u-b).
 }                                                                  \tag{8}
\]

This is genuinely beyond P56's one-sided credit: (8) has no \(\tau\) term.
For example, if \(u=k/2\) and \(b\le k/12\), then

\[
 \Xi(k,u,b)\ge {k^2\over72}.                                      \tag{9}
\]

Thus any uniform reflected estimate with \(E_\delta(q)=o(q^2)\) proves the
general estimate in this fixed positive-density residual regime, regardless
of the size of the reflection shift.  In general, with

\[
 x={u\over k},\qquad y={b\over k},
\]

the positive-credit range is

\[
 0\le y<\rho(x):=
 {1+x-\sqrt{1+2x-x^2}\over2}.                                    \tag{10}
\]

No assertion \(u=o(k)\) is used or follows from (10).

## 1. Core geometry pays the shift

Write

\[
 a=\min A,\quad z=\max A,\quad m=\min P.
\]

Because \(P\) is reflected about \(\sigma/2\), its maximum is
\(\sigma-m\).  Put

\[
 \ell=m-a\ge0,\qquad r=z-(\sigma-m)\ge0.
\]

Then, exactly,

\[
 L=\operatorname{span}(P)+\ell+r,qquad
 \sigma-a-z=\ell-r.                                             \tag{11}
\]

It follows that

\[
 L-\tau
 =\operatorname{span}(P)+2\min(\ell,r)
 \ge\operatorname{span}(P).                                    \tag{12}
\]

The core \(P\) is itself fully reflected and admissible, with \(p\) pairs
and midpoint flag \(\delta\).  Therefore

\[
 \operatorname{span}(P)\ge H_\delta(p),
\]

which proves (1).  Equivalently,

\[
 \boxed{\tau\le L-H_\delta(p).}                                 \tag{13}
\]

This is the required quantitative control of the reflection shift.  A large
one-sided extension is already paid for in the span outside the paired core.

## 2. Every original residual difference label survives the accounting

Apply P56.1.  It gives a set \(X\subseteq R\), with

\[
 t:=|X|\le b,
\]

such that, for \(Y=R\setminus X\),

\[
 F_X=P\cup Y\cup(\sigma-Y)
\]

is fully reflected and admissible.  It has \(p+u-t\) reflected pairs, so

\[
 L+\tau\ge\operatorname{span}(F_X)
 \ge H_\delta(p+u-t)
 \ge H_\delta(p+u-b).                                    \tag{14}
\]

There is a second, independent lower bound on \(L+\tau\).  P56's repair
marks every colliding virtual residual pair and deletes an endpoint of each
marked pair.  Hence the surviving virtual labels

\[
 Q_Y=\{|y_i+y_j-\sigma|:y_i,y_j\in Y,\ i\le j\}
\]

are distinct and lie outside the whole of \(D^+(A)\), not merely outside
the differences of \(A\setminus X\).  Therefore

\[
 |D^+(A)\mathbin{\dot\cup}Q_Y|
 =|D^+(A)|+\binom{u-t+1}{2}.                              \tag{15}
\]

Every label in (15) is a positive difference of

\[
 A\cup(\sigma-Y)\subseteq A\cup(\sigma-R),
\]

whose span is exactly \(L+\tau\).  Packing in
\([1,L+\tau]\), and using \(t\le b\), gives

\[
 L+\tau\ge |D^+(A)|+\binom{u-t+1}{2}
 \ge |D^+(A)|+\binom{u-b+1}{2}.                         \tag{16}
\]

Equations (14) and (16) prove (2).  Adding (1) proves (3).

The label term has the equivalent deletion form

\[
 \boxed{
 |D^+(A)|+\binom{u-b+1}{2}
 =(p+u-b)(p+u-b+\delta)
   +bk-\binom{b+1}{2}.
 }                                                                  \tag{17}
\]

Here \(bk-\binom{b+1}{2}\) is exactly the number of original positive
difference pairs incident to a specified set of \(b\) residual points.
All are globally unique by P56's residual-difference lemma.

## 3. Sharp-bound algebra

Put

\[
 q=p+u-b,\qquad 2p+\delta=c=k-u,\qquad
 2q+\delta=k+u-2b.                                      \tag{18}
\]

The first branch of (3), followed by (5), gives

\[
 L\ge {3\over8}\left((k-u)^2+(k+u-2b)^2\right)
 -{E_\delta(p)+E_\delta(q)\over2}.                      \tag{19}
\]

The exact identity

\[
 (k-u)^2+(k+u-2b)^2
 =2k^2+2\left(u^2-2b(k+u)+2b^2\right)                  \tag{20}
\]

turns (19) into (6).  This proves (7)-(8).

For fixed \(x=u/k\), the normalized expression in (7) is

\[
 {\Xi\over k^2}=x^2-2(1+x)y+2y^2.                       \tag{21}
\]

Its smaller zero is (10), proving the stated positive-density regime.  At
\(x=1/2\), the expression is decreasing for \(0\le y\le1/12\), and direct
substitution at \(y=1/12\) gives \(1/72\), proving (9).

By contrast, P56 alone requires its residual credit to pay \(\tau\):

\[
 {3\over4}\left((k+u-2b)^2-k^2\right)\ge\tau
\]

before errors.  The two-scale argument removes this restriction rather than
estimating \(\tau\) by a tautologically larger copy of \(L\).

## 4. What direct sum-hole charging can and cannot prove

Let

\[
 h_S=2L-\left(2p(p+\delta)+cu+\binom{u+1}{2}\right).    \tag{22}
\]

P56's exact sum count shows that \(h_S\) is precisely the number of missing
sum labels in the integer interval \([2\min A,2\max A]\).

There is a proved collision charge in a substantial finite-ratio range.

**Lemma P61.2.**  If

\[
 u\le2c-5,                                                \tag{23}
\]

then

\[
 \boxed{2\beta\le h_S.}                                 \tag{24}
\]

**Proof.**  The number of virtual residual pairs is \(\binom{u+1}{2}\), so
the definition of collision excess gives

\[
 \beta\le\binom{u+1}{2}.                                \tag{25}
\]

The exact difference-label packing (4) gives

\[
 L\ge p(p+\delta)+cu+\binom u2.                          \tag{26}
\]

Substitution into (22) yields

\[
 h_S\ge {u(2c+u-3)\over2}.                              \tag{27}
\]

Condition (23) is equivalent to

\[
 2c+u-3\ge2u+2.
\]

Thus (27) is at least \(u(u+1)=2\binom{u+1}{2}\), and
(24) follows from (25).  QED.

Condition (23) allows \(u/c\) to approach \(2\), so Lemma P61.2 is not an
\(u=o(k)\) statement.  The unrestricted strengthening \(2\beta\le h_S\)
survived every exact test below, but is not used as a theorem here.

Two tempting local strengthenings are false.

### The shift cannot be charged to sum holes

The natural joint bound

\[
 2\beta+\tau\le h_S                                    \tag{28}
\]

has smallest endpoint-normalized falsifier

\[
 A=\{0,1,2,5\},\qquad \sigma=2.                         \tag{29}
\]

Here

\[
 P=\{0,1,2\},\quad R=\{5\},\quad
 (p,\delta,u,L,\tau,\beta)=(1,1,1,5,3,0),
\]

and (22) gives \(h_S=2\).  Thus (28) reads \(3\le2\).  This explains why
the geometric cancellation (1), rather than a local hole charge for
\(\tau\), is necessary.

### Residual-difference count alone does not pay two units per collision

Let

\[
 D_R=\{d\in D^+(A):d\text{ has a representation touching }R\}.
\]

The natural collision budget

\[
 2\beta+u\le|D_R|=cu+\binom u2                          \tag{30}
\]

has smallest endpoint-normalized falsifier

\[
 A=\{0,4,6,7,12\},\qquad \sigma=12.                     \tag{31}
\]

Its paired core is \(\{0,6,12\}\), its residual is \(\{4,7\}\), and its
three virtual labels are

\[
 |4+4-12|=4,\qquad |4+7-12|=1,\qquad |7+7-12|=2.
\]

All three lie in \(D^+(A)\), so \(\beta=3\).  But \(|D_R|=7\), and (30)
reads \(8\le7\).  The extra difference holes in this example are essential;
one cannot prove (24) by charging only the cardinality of \(D_R\).

## 5. Exact computation

The full P56 census was independently rebuilt by

~~~text
python -B problems/864/compute/p61/audit_completion_defect.py \
  --max-n 22 \
  --output problems/864/compute/p61/census_label_charges.json
~~~

It enumerates all

\[
 \sum_{N=2}^{22}2^{N-2}=2{,}097{,}151
\]

endpoint-normalized subsets.  It found the same \(11{,}969\) admissible sets
and the same \(8{,}458\) P56 records with a repeated exception and nonempty
residual.  For every record it rebuilt all sums, differences, virtual
labels, the P56 repair, (1)-(4), (15)-(17), and the two credit expressions
using integer arithmetic.

With the error terms in (5) set to zero only for comparing the two algebraic
gates, the counts are

\[
\begin{array}{c|r}
\text{gate}&\text{records}\ \hline
\text{P56 one-sided credit holds}&5{,}480\\
\text{P61 two-scale credit holds}&5{,}582\\
\text{P61 holds while P56 fails}&334\\
\text{same, with }u\ge k/3&26.
\end{array}                                               \tag{32}
\]

The smallest record in the third row is

\[
 A=\{0,1,2,9\},\quad
 (k,u,\tau,\beta)=(4,1,7,0).                             \tag{33}
\]

P56's cleared zero-error credit is \(-1\), while
\(\Xi=1\).  A witness with residual proportion at least \(1/3\) is

\[
 A=\{0,1,2,5,21\},\quad
 (k,u,\tau,\beta)=(5,2,19,0),                            \tag{34}
\]

for which the corresponding cleared values are \(-4\) and \(\Xi=4\).
These finite records compare implications of a hypothetical reflected sharp
bound; they are not claims that (5) has zero finite error.

The same auditor finds no failure of the unrestricted experimental bound
\(2\beta\le h_S\) in the \(8{,}458\)-record census.  The smallest margin is
one, at \(A=\{0,1,3,7,8\}\).  A stress extension through \(N=36\) checks
\(510{,}030\) admissible sets and \(412{,}860\) nonempty-residual records,
again with minimum margin one.  This evidence is recorded separately from
the proved range (23).

Stored extremizers and large construction records were rebuilt by

~~~text
python -B problems/864/compute/p61/audit_stored_extremizers.py
~~~

The exact corpus consists of:

\[
\begin{array}{c|r|r|r}
\text{source}&\text{rows}&\text{fully reflected}&u>0\\ \hline
\text{certified optima }N\le55&55&40&12\\
\text{later endpoint certificates through }N=100&6&6&0\\
\text{P20 extremizer/construction samples}&193&157&33.
\end{array}                                               \tag{35}
\]

Rows without an exceptional sum account for the remaining entries.  Every
admissibility condition, core/shift identity, repaired-label packing bound,
and tested hole inequality passes.  The largest nonempty-residual sample has

\[
 k=252,\qquad c=168,\qquad u=84,\qquad \beta=0,\qquad\tau=15,
\]

so this audit includes a residual of fixed positive proportion.  The
machine-readable output is

~~~text
problems/864/compute/p61/stored_extremizers_audit.json
~~~

## 6. Frontier

The reflection shift is no longer an independent obstruction: (1) pays it
from the paired core, and (3) removes it exactly.  The remaining completion
frontier is the label-collision ratio \(b/k\).  Under a reflected sharp
theorem, the precise sufficient region is (8), or asymptotically (10), even
when \(u=\Theta(k)\).

The unrestricted experimental charge \(2\beta\le h_S\) would give a simple
sum-hole control of \(\beta\), but (28) and (30) show that neither \(\tau\)
nor the residual-difference count can be folded into that statement in the
most direct way.  Any stronger universal estimate must use the placement of
the exact residual sum and difference labels, not only their cardinalities.
