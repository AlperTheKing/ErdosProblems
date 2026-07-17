# C46: global weighted potential and mass transport

## Verdict

No estimate

\[
                         H(X)\le Q(X)+o(X)
\]

is proved here, and no counterexample to that estimate is claimed.

The natural genuinely decaying global potential tested in this lane is
false. It combines obstruction-rank discount with a finite-mass bank over
all canonical components:

\[
 {\cal D}_t(X)=
 \sum_{\substack{h\le X\\h\ {\rm hard}}}t^{\rho(h)}
 -
 \sum_{\substack{q\ {\rm target}\\2q-1\le X}}
       2^{1-j(q)}t^{\rho(q)}.                              \tag{1}
\]

Here \(j(q)\) is the ordinal of the target child \(2q-1\) among the targets
in the canonical T2/T3 component of \(q\). The sums in (1) are global:
credit from any component pays any hard source.

The proposed additive-one potential

\[
                         {\cal D}_t(X)\le1                 \tag{WP1}
\]

is exactly false for the actual least grounded \(G\). At \(t=99/100\), its
first failure is at \(X=1644\), where

\[
 {\cal D}_{99/100}(1644)
 ={2070022193351\over2000000000000}>1.
\]

At \(X=2064\),

\[
 {\cal D}_{99/100}(2064)
 ={358639165423\over100000000000}
 =3.58639165423.                                          \tag{2}
\]

An independent trial-divisor implementation with literal descending
grounded stages verifies (2). Thus rank weights, coordinate prefixes, and
global canonical-component credit do not yield even the analogue of C31's
single dummy unit for this genuinely decaying mass-two bank.

There is one positive structural result. Canonical generated T3 exits
launch disjoint injective transport chains. Every terminated chain lands
at a distinct \(Q\)-target, possibly in an unrelated canonical component.
This gives an exact telescoping identity, but its active-chain frontier is
not proved to be \(o(X)\). The frontier is therefore not a sublinear error
term available for the requested estimate.

## 1. Setup

Let

\[
 {\cal A}=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let \(G\) be the least subset of \({\cal A}\) containing \(2,3\) and
closed under \(a,b\mapsto ab-1\) for distinct \(a<b\). Put
\({\cal M}={\cal A}\setminus G\).

For a hole \(n\), use the C31 obstruction rank

\[
 \rho(n)=0
 \quad\hbox{if \(n+1\) has no admissible factor pair},
\]

\[
 \rho(n)=1+\max_{ab=n+1}
   \min\{\rho(x):x\in\{a,b\}\cap{\cal M}\}.               \tag{3}
\]

A hard hole and a target have the C31/C39 meanings. A target parent \(q\)
is a hole with generated seed-2 child \(2q-1\); its coordinate is the
child and its rank is \(\rho(q)\).

The canonical hole parent is

\[
 \pi(n)=(n+1)/2\quad(n>3\hbox{ odd}),
\]

or

\[
 \pi(n)=(n+1)/3\quad(n\hbox{ seed-3-easy even}).
\]

The roots are exactly the splitless and hard holes. For a target parent
\(q\), let \(r(q)\) be its canonical root and order all target children in
that component by child coordinate. The resulting ordinal is \(j(q)\).

The component weights

\[
                         u_j=2^{1-j}                      \tag{4}
\]

satisfy \(0<u_j\le1\) and

\[
                         \sum_{j\ge1}u_j=2.               \tag{5}
\]

Thus (4) is a front-loaded finite-mass forest bank, while (1) still permits
unrestricted cancellation between different components. It is not the
component-local matching killed at \(74\) in C39.

## 2. Why the potential would suffice

For \(0<t<1\), define

\[
 H_t(X)=\sum_{\substack{h\le X\\h\ {\rm hard}}}t^{\rho(h)},
\qquad
 W_t(X)=\sum_{\substack{q\ {\rm target}\\2q-1\le X}}
                u_{j(q)}t^{\rho(q)}.
\]

Then \({\cal D}_t=H_t-W_t\), and \(W_t(X)\le Q(X)\).

### Lemma 1

Every hole \(n\) satisfies

\[
                         \rho(n)\le\log_2(n-1).            \tag{6}
\]

### Proof

If \(\rho(n)=r>0\), a pair attaining the maximum in (3) has a missing
endpoint \(p\) of rank \(r-1\). Its other endpoint is at least \(2\), so

\[
                         p-1\le{n-1\over2}.
\]

Iterating through ranks \(r,r-1,\ldots,0\) ends at a hole at least \(2\).
Hence \(n-1\ge2^r\), proving (6). QED.

### Proposition 2

Suppose \(t_X\to1\),

\[
                 (1-t_X)\log X\longrightarrow0,           \tag{7}
\]

and, for some \(B(X)=o(X)\),

\[
                         {\cal D}_{t_X}(X)\le B(X).         \tag{8}
\]

Then \(H(X)\le Q(X)+o(X)\).

### Proof

Bernoulli's inequality and (6) give

\[
 0\le H(X)-H_{t_X}(X)
 \le (1-t_X)\log_2(X-1)\,H(X)=o(X).
\]

Using \(W_{t_X}\le Q\) in (8) yields

\[
 H(X)\le H_{t_X}(X)+o(X)
 \le W_{t_X}(X)+B(X)+o(X)
 \le Q(X)+o(X).
\]

QED.

Thus (1) is not decorative: a near-unit version with a sublinear boundary
would prove the requested sufficient estimate.

## 3. Exact Abel telescoping

For a rank cutoff \(d\), put

\[
 Q^u_{\le d}(X)=
 \sum_{\substack{q\ {\rm target},\,2q-1\le X\\\rho(q)\le d}}u_{j(q)}
\]

and

\[
 B^u_d(X)=H_{\le d}(X)-Q^u_{\le d}(X).
\]

Every event of rank \(r\) contributes

\[
 (1-t)\sum_{d=r}^{\infty}t^d=t^r.
\]

Therefore the potential has the exact telescoping identity

\[
 \boxed{\displaystyle
 {\cal D}_t(X)=(1-t)\sum_{d\ge0}t^d B^u_d(X).}             \tag{9}
\]

No matching graph or componentwise sign is used in (9). It is a global
mass transport over rank prefixes, with the canonical forest entering only
through the target weights (4).

For comparison, replacing every \(u_j\) by \(1\) gives the rank-only Abel
potential

\[
 (1-t)\sum_{d\ge0}t^d
       \bigl(H_{\le d}(X)-Q_{\le d}(X)\bigr).              \tag{10}
\]

The exact sweep found no positive value of (10), at any integer cutoff
through \(10^6\), for

\[
 t\in\{1/2,2/3,3/4,9/10,99/100,999/1000\}.
\]

This is finite evidence only. The failure below is caused specifically by
the finite-mass forest transport, not by an implementation of rank alone.

## 4. Sharp six-by-six obstruction

At \(X=186\), the complete hard ledger is

\[
\begin{array}{c|rrrrrr}
h&54&74&114&144&174&186\\ \hline
\rho(h)&2&2&2&3&2&2.
\end{array}
\]

The complete target ledger is

\[
\begin{array}{c|rrrrrr}
\hbox{child}&41&69&77&125&131&149\\
\hbox{parent}&21&35&39&63&66&75\\
\rho(\hbox{parent})&2&1&1&3&0&1\\
\hbox{canonical root}&6&18&20&6&66&38\\
j&1&1&1&2&1&1.
\end{array}                                               \tag{11}
\]

Thus there are five first-component exits and one second exit. If first
exits have weight \(1\), second exits have weight \(\alpha\), and later
exits have weight zero, then the exact unranked defect is

\[
                         6-(5+\alpha)=1-\alpha.           \tag{12}
\]

Consequently every \(\alpha<1\) fails at \(186\). More generally, among
nonincreasing component weights \(0\le u_j\le1\) with total mass at most
two, (11) forces

\[
                         u_1=u_2=1.
\]

This exhausts the entire mass-two budget and leaves no strict contraction
or tail mass. The geometric weights (4), for which \(u_2=1/2\), have defect
\(1/2\).

The degenerate extremal bank

\[
 u_1=u_2=1,\qquad u_j=0\quad(j\ge3)
\]

had no unranked prefix failure through \(10^6\). This is finite evidence,
not a proof. Accordingly, (12) falsifies every mass-two bank with genuine
decay or positive tail that is required to have zero boundary at \(186\);
it does not falsify the full-weight first-two diagnostic from C39/C43.

Including rank discount gives the exact polynomial

\[
\begin{aligned}
 {\cal D}_t(186)
 &=5t^2+t^3-
   \left(t^2+3t+\frac12t^3+1\right)\\
 &=\frac12t^3+4t^2-3t-1.                                 \tag{13}
\end{aligned}
\]

The zero of (13) in \((0,1)\) lies strictly between
\(917/1000\) and \(918/1000\). At \(t=19/20\),

\[
 {\cal D}_{19/20}(186)={3019\over16000},
\]

which exceeds the vanishing candidate boundary \(1-t=1/20\) by

\[
                         {2219\over16000}.                \tag{14}
\]

The full, undiscounted rank potential at this cutoff is instead

\[
 4t^2-3t-1=(4t+1)(t-1)\le0.
\]

The second exit at child \(125\), with full rank-three weight, is exactly
what repairs the rank-only potential. Any strict forest discount removes
that repair.

## 5. Additive-one falsifier

The obstruction is not limited to a zero boundary. At \(X=2064\), the
coefficient of \(t^d\) in (1), by exact rank, is

\[
 \left(
 -44,\ -14,\ {109\over2},\ -{5\over4},\
 2,\ {11\over4},\ 5
 \right).                                                \tag{15}
\]

There are \(101\) hard sources and \(104\) unweighted targets through this
cutoff. Substituting \(t=99/100\) in (15) gives (2), so

\[
 {\cal D}_{99/100}(2064)-1
 ={258639165423\over100000000000}>0.                     \tag{16}
\]

The first failure of (WP1) is already at \(X=1644\). The exact sweep through
\(10^6\) finds the maximum for \(t=99/100\) at \(X=2064\), and its last
positive event at \(X=2166\). These are finite statements.

At \(t=1\), (15) sums to \(5\), while the actual unweighted count has
\(H(2064)-Q(2064)=101-104=-3\). The eight units lost are later-component
targets whose weights are below one. Hence (16) is a falsifier to the
weighted potential, not to \(H\le Q+o(X)\).

## 6. An injective global T3 transport

The following transport is independent of the failed potential and is
genuinely cross-component.

Let a canonical generated T3 exit be

\[
                         x_0=3q-1\in G,
\]

where \(q\) is an odd hole. The start \(x_0\) is even. On generated states
\(x>3\), define a partial map

\[
 F(x)=
 \begin{cases}
 3x-1,&x\text{ odd},\\
 3x/2,&x\text{ even and }3x/2\in G.
 \end{cases}                                             \tag{17}
\]

If \(x\) is even and \(y=3x/2\) is a hole, then

\[
                         3x-1=2y-1\in G,                  \tag{18}
\]

because \(3,x\in G\). Thus (18) is a \(Q\)-target and the chain terminates.

### Lemma 3

The chains (17) rooted at distinct canonical generated T3 exits are
vertex-disjoint. Distinct terminated chains give distinct \(Q\)-targets.

### Proof

Every step strictly increases its state. An odd input in (17) has output
congruent to \(2\pmod3\), with unique inverse \((z+1)/3\). An even input
has output divisible by \(3\), with unique inverse \(2z/3\). The two image
classes are disjoint, so \(F\) is injective.

A start \(x_0=3q-1\) is \(2\pmod3\). Its only possible predecessor is \(q\),
which is a hole and hence outside the generated-state domain. Therefore no
start lies later on another start's chain. Finally, the terminal child
\(3x-1\) uniquely determines the terminal state \(x\), proving distinctness.
QED.

For a cutoff \(X\), let \(T(X)\) count chains whose terminal \(Q\)-child has
arrived by \(X\), and let \(A(X)\) count the remaining active chains rooted
at starts at most \(X\). Monotonicity and Lemma 3 give the exact telescoping
identity

\[
                         R_3(X)=T(X)+A(X),                \tag{19}
\]

with

\[
                         T(X)\le Q(X).                    \tag{20}
\]

The first nonlocal example is

\[
 q=15,\quad x_0=44,\quad y={3x_0\over2}=66,\quad
 131=3x_0-1=2y-1.
\]

Here \(15\) lies in the canonical component rooted at \(8\), while the
target parent \(66\) is a different canonical root. This transport therefore
does what the component-local mechanism at \(74\) cannot do.

The exact frontier census is

\[
\begin{array}{r|r|r|r}
X&R_3(X)&T(X)&A(X)\\ \hline
10^4&138&29&109\\
10^5&1231&346&885\\
10^6&9351&2545&6806.
\end{array}
\]

There were no state collisions and all terminal children were distinct.
However, no argument here proves \(A(X)=o(X)\). The elementary bound maps a
start back to its odd hole parent at scale \(X/3\), which gives only an
unknown hole count. Replacing \(A(X)\) by \(o(X)\) in (19) would therefore
be an unsupported step.

## 7. Exact computation

The primary implementation uses an SPF table, enumerates every admissible
factor pair, reconstructs the least grounded \(G\) in increasing order,
computes (3), builds canonical roots and target ordinals, and sweeps every
event prefix after clearing all denominators.

Through \(10^6\) it obtains

\[
 H=45583,\qquad Q=67537,\qquad \max\rho=14.
\]

The independent verifier uses trial divisors and separately iterates the
literal descending grounded approximants. Through \(2500\), the stages
stabilize after nine updates. It reports zero membership or death-rank
mismatches and verifies (11)-(16) exactly.

Reproduction:

~~~powershell
python problems/424/compute/wave4/C46_weighted_potential/audit_weighted_potential.py --limit 1000000 --output problems/424/compute/wave4/C46_weighted_potential/audit_1m.json

python problems/424/compute/wave4/C46_weighted_potential/verify_trial_186.py --limit 2500 --output problems/424/compute/wave4/C46_weighted_potential/verify_2500.json
~~~

SHA-256:

~~~text
audit_weighted_potential.py  0FD432AED1C8950556E4F28B8A822CE0B0F12B8E0AFCDFBA42488A9BB8404C84
verify_trial_186.py           CCC72FD3F9FFA43933B448D1E65383FEEFCC11FAC6FD5E0D7FD8B55831223805
audit_1m.json                 0804F73725041DD63ACB75E9712558EC033FDE4F6E122CDD04141B5A5BF8859D
verify_2500.json              B8680A2EF40C8F18ED1C49FBF10F21084E9B9FC97DF2DC4760B66B7CADBCBFA8
~~~

## 8. Status and prior-art comparison

C39's source \(74\) rules out transport confined to a source's canonical
component. Lemma 3 supplies an explicit transport that crosses components,
and (9) pools all component credit globally. The new obstruction occurs
later: finite-mass component weights destroy a rank cancellation that needs
the second exit at full unit weight.

The public [Problem 424 page](https://www.erdosproblems.com/424) remains
open and lists the original positive-density question, with no posted
partial result of this form. The exact claims here are the transport lemma,
the telescoping identities (9) and (19), and the falsifiers (14) and (16).
No claim of (WP1), \(A(X)=o(X)\), \(H(X)\le Q(X)+o(X)\), or density
\(2/3\) is made.
