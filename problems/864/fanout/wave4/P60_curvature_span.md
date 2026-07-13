# P60: curvature-span audit and the strict tail lemma

## Verdict

The unconditional span statement suggested after P52 is false.  There is
an explicit infinite family of valid P52 data with

\[
                         W-G=(4+o(1))p^2.                     \tag{1}
\]

It is obtained by doubling the classical Erdos--Turan integer Sidon
ruler and taking any odd translate (G).  Thus positivity of the
palindromic staircase, the sparse signed curvature profile, exact tail
domination, and a (p)-term Sidon Newman factor do not by themselves
imply (W-G=o(p^2)).

There is, however, a strict strengthening of P52's tail lemma.  Put

\[
                         u_n:=2s_n \qquad(0\leq n<L).
\]

Then

\[
 \boxed{
 u_n=\#\{(i,j): |z_i-z_j|\leq n<G+z_i+z_j\}\geq1.}          \tag{2}
\]

The lower bound in (2) is sharp for arbitrarily large (p), even under
all P52 hypotheses.  The unweighted total variation is also exact:

\[
 \boxed{
   \sum_{n=1}^{L}|u_n-u_{n-1}|=2p^2-p,\qquad u_L:=0.}        \tag{3}
\]

Consequently total variation contains no span information.  Exact
tests also falsify the candidate \(\operatorname{rev}(c)\leq2p\), a
\(p-1\) tail floor on
([G,W)), adjacent Hankel log-concavity, and centered zero counts for
(P).  The five stored P52 rulers have 59 valid dangerous translates;
all were tested, as were all 6,783 pairs in the P52 census through
(W=18).

The surviving statement is narrower than (W-G=o(p^2)).  Since

\[
 G+2W=3p^2+3(W-p^2)-(W-G),                                  \tag{4}
\]

the target only needs the excess-compensated estimate

\[
             W-G\leq 3(W-p^2)+o(p^2)                         \tag{5}
\]

in the width-subcritical regime (W\leq(3/2+o(1))p^2).  When
(W=p^2+O(p^{3/2})), (5) reduces to the originally requested
(W-G=O(p^{3/2})).  None of the unconditional candidates tested here
can prove (5); a continuation must use width density together with the
support exclusion, not staircase positivity alone.

## 1. Exact strict-tail and variation lemma

Let

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\},\qquad L=G+2W,
\]

and retain the notation of P52.  No Sidon assumption is needed for the
first identity below; the Sidon and support-disjoint hypotheses are
used for its sparse-curvature consequence.

**Lemma P60.1 (ordered-pair tail, strictness, and fixed variation).**
For every (0\leq n<L),

\[
 2s_n=\sum_{i,j}
       {\mathbf 1}_{\{|z_i-z_j|\leq n<G+z_i+z_j\}}.           \tag{6}
\]

In particular (2s_n\geq1).  If (Z) is Sidon and
(D^+(Z)\cap(G+S(Z))=\varnothing), then (3) holds.

### Proof

The two multiplicity-weighted tails behind P52 (15) are

\[
 B_n:=\sum_{k>n}b_k
       =\#\{(i,j):G+z_i+z_j>n\}.                              \tag{7}
\]

and

\[
 M_n:=\#\{(i,j):i\ne j,\ |z_i-z_j|>n\}.                      \tag{8}
\]

For Sidon \(Z\), \(M_n=2|D^+(Z)\cap(n,W]|\), exactly the term in
P52 (15).  In general, the same coefficient summation with
multiplicities retained gives \(u_n=B_n-M_n\).  Every pair counted by
\(M_n\) is counted by \(B_n\), because

\[
 G+z_i+z_j-|z_i-z_j|=G+2\min(z_i,z_j)>0.                    \tag{9}
\]

Subtracting \(M_n\) from \(B_n\) proves (6), including the diagonal
pairs.  Strictness is immediate.  If (n<G), the pair ((0,0))
is counted; if (G\leq n<L), the pair ((W,W)) is counted.

For (3), (u_n-u_{n-1}=2c_n) for (n\geq1).  The positive atoms
have weight (2) at the (\binom p2) positive differences, while
the negative atoms have total absolute weight

\[
                 p+2\binom p2=p^2.                           \tag{10}
\]

Their supports are disjoint.  Therefore

\[
 \sum_{n=1}^{L}|u_n-u_{n-1}|
   =2\binom p2+p^2=2p^2-p.
\]

This proves the lemma.  QED.

The constant one in (2) cannot be increased as a function of (p).
For (p\geq3), set

\[
 Z_p=\{0\}\cup\{2\cdot4^j:0\leq j\leq p-2\},\qquad G=1.    \tag{11}
\]

Base-four uniqueness makes (Z_p) Sidon.  All its sums and
differences are even, so (G+S(Z_p)) is disjoint from (D^+(Z_p)).
Writing (W=2\cdot4^{p-2}), the previous mark is (W/4).  At

\[
                            n=W/2+1,                           \tag{12}
\]

the pair ((W,W)) is counted by (6).  Two marks at most (W/4)
have (1+z_i+z_j\leq n), while a pair containing (W) and a
smaller mark has difference at least (3W/4>n).  Hence
(u_n=1).  This is an infinite exact sharpness family.

## 2. Unconditional quadratic-span falsifier

Let (p) be an odd prime and, for (0\leq i<p), put

\[
 r_i\in\{0,\ldots,p-1\},\quad r_i\equiv i^2\pmod p,
 \qquad a_i=2pi+r_i,                                         \tag{13}
\]

\[
                         Z_p=\{2a_i:0\leq i<p\}.             \tag{14}
\]

The sequence (a_i) is strictly increasing.  It is Sidon: if
(a_i+a_j=a_k+a_l), then

\[
 2p(i+j-k-l)=r_k+r_l-r_i-r_j.                                \tag{15}
\]

The right side has absolute value below (2p), so both sides vanish.
Thus (i+j=k+l).  Reduction modulo (p), followed by

\[
 2ij=(i+j)^2-(i^2+j^2),                                     \tag{16}
\]

gives (ij\equiv kl\pmod p).  The two unordered pairs are the
roots of the same quadratic over (\mathbb F_p), hence
({i,j}={k,l}).  Doubling preserves the Sidon property.

Every element of (Z_p), every difference, and every sum is even.
Consequently every odd (G) satisfies

\[
                    D^+(Z_p)\cap(G+S(Z_p))=\varnothing.       \tag{17}
\]

Since (r_{p-1}=1),

\[
 W=4p(p-1)+2.                                                \tag{18}
\]

Taking (G=1) gives

\[
                       W-G=4p^2-4p+1,                         \tag{19}
\]

which proves (1).  This family retains the Sidon Newman factor, the
positive palindromic staircase, exact autocorrelation, strict tail
domination, and the disjoint sparse curvature profile.

The audit gives the following exact samples.  `rev(c)` counts sign
changes after zero coefficients are removed, and `rev(K)` does the
same for the adjacent Hankel minors in Section 3.

\[
\begin{array}{c|r|r|c|r|r}
p&W&\#\{\text{odd }G<W\}&(W-1)/p^2&\operatorname{rev}(c)&
 \operatorname{rev}(K)\\ \hline
3&26&13&25/9&4&9\\
7&170&85&169/49&18&53\\
13&626&313&625/169&48&179\\
23&2026&1013&2025/529&118&549
\end{array}                                                   \tag{20}
\]

This is not a counterexample to the desired endpoint estimate for
problem 864: here (G+2W=(8+o(1))p^2), already well above the target
(3p^2).  It is an exact falsifier to applying the proposed
curvature-span bound outside the width-subcritical regime.

## 3. Candidate gates

### 3.1 Total variation

Equation (3) proves that global total variation is exactly independent
of (G,W,Z).  Localizing the same mass to ([G,W]) does not repair the
basic issue: the radix family (11) has an arbitrarily long inversion
span and a point with (u_n=1), while the doubled family (14) has arc
area of order (p^4).  For the latter claim, take the ordered pairs
with both indices at least (\lceil3p/4\rceil).  There are
(\gg p^2) such pairs, and each contributes (\gg p^2) consecutive
indices to (6).  An unweighted variation argument is therefore dead.

### 3.2 Number of curvature reversals

The candidate

\[
                  \operatorname{rev}(c)\leq2p                \tag{21}
\]

is false.  The first census falsifier in \((W,p,G,Z)\) order is

\[
                     p=4,\quad Z=\{0,2,5,12\},\quad G=4.     \tag{22}
\]

Its differences are

\[
                         2,3,5,7,10,12,
\]

and its shifted sums are

\[
                 4,6,8,9,11,14,16,18,21,28.
\]

They are disjoint.  Reading their signs in increasing order gives ten
sign runs and therefore nine reversals, whereas (2p=8).  The five
stored translation families happen to satisfy the stronger
(2p-1) bound, with maximum 23 at (p=12,G=24), but (22) shows that
this is not structural.

### 3.3 Weighted-tail floors

The candidate (u_n\geq p-1) on (G\leq n<W) is false.  Take

\[
                      p=3,\quad Z=\{0,1,6\},\quad G=2.       \tag{23}
\]

Here

\[
 D^+(Z)=\{1,5,6\},\qquad G+S(Z)=\{2,3,4,8,9,14\},
\]

and the exact arc values are

\[
                         (u_2,u_3,u_4,u_5)=(4,2,1,3).         \tag{24}
\]

Thus (u_4=1<p-1).  The infinite family (11) proves that the strict
floor in (2), rather than any growing function of (p), is the sharp
unconditional statement.

### 3.4 Hankel minors

Put (H_n=2h_n) and

\[
                         K_n=H_nH_{n+2}-H_{n+1}^2.            \tag{25}
\]

For P52's structured counterexample
(Z=\{0,3,4\},G=2), its displayed autocorrelation gives

\[
                 K_0=-97,\qquad K_1=16,\qquad K_2=-88.       \tag{26}
\]

Hence (H) is neither log-concave nor log-convex, and even the first
three adjacent minors have two sign reversals.  Across the 59 stored
translates the maximum number of minor-sign reversals is 76, attained
for the (p=12) ruler at (G=24,44,49).  A fixed-sign or
single-reversal Hankel criterion is false.

### 3.5 Zero distribution

The zero count of (P) is independent of (G), so each translation
family is already a blindness test.  Exact counts for the five stored
Newman factors are

\[
\begin{array}{c|r|c|r}
p&W&N_{\mathbb D}(P)&|2N_{\mathbb D}(P)-W|\\ \hline
5&12&8&4\\
9&49&28&7\\
10&55&\text{unit root }-1&\text{--}\\
11&84&50&16\\
12&107&65&23
\end{array}                                                   \tag{27}
\]

Thus even the candidate

\[
                       |2N_{\mathbb D}(P)-W|\leq p            \tag{28}
\]

fails on two stored factors.  The (p=12) factor has the same 65
interior zeros for 27 valid shifts (G), whose inversion spans range
from 83 down to 1.  The (p=10) unit root also shows that a winding
argument must handle boundary zeros rather than assuming them away.

The counts in (27) are exact.  The checker applies the Cayley transform

\[
 C_Z(t)=\sum_{z\in Z}(1+t)^z(1-t)^{W-z}
       =(1-t)^WP\!\left({1+t\over1-t}\right),                \tag{29}
\]

tests imaginary-axis roots by an exact polynomial gcd, and counts
left-half-plane roots with a rational Routh table.  Reciprocal factors
give the complementary counts (4,21,34,42) in the four root-free
cases, independently checking that the totals are (W).

## 4. Exact computation

The audit is in

    problems/864/compute/p60/audit_curvature_span.py

and writes

    problems/864/compute/p60/audit_results.json

Run it with

    python -B problems/864/compute/p60/audit_curvature_span.py --max-width 18

All staircase, autocorrelation, curvature, tail, variation, reversal,
and Hankel calculations use integers.  Zero counts use exact integer
polynomials and rational Routh rows.

For each of the five stored P52 rulers, the audit tests every valid
shift (1\leq G<W), not only the recorded shift:

\[
\begin{array}{c|r|r|r|c|r|r}
p&W&\#G&\max(W-G)&N_{\mathbb D}(P)&
 \max\operatorname{rev}(c)&\max\operatorname{rev}(K)\\ \hline
5&12&2&6&8&5&4\\
9&49&6&31&28&13&24\\
10&55&3&13&-1\text{ root}&7&22\\
11&84&21&61&50&21&52\\
12&107&27&83&65&23&76
\end{array}                                                   \tag{30}
\]

The exhaustive census reproduces P52's 1,340 endpoint-normalized Sidon
rulers and 6,783 valid pairs with (W\leq18).  Every pair satisfies
(2)--(3).  It finds the exact falsifiers (22)--(24).  Among all 1,340
Newman factors, 318 have a unit-circle root.  Among the others, the
first failure of (28) is (Z=\{0,1,3,11\}), with
(N_{\mathbb D}(P)=3).

The same run verifies the doubled Erdos--Turan records for
(p=3,5,7,11,13,17,19,23) and the sharp-tail radix records for every
(3\leq p\leq9).

## 5. Reduced frontier

The strict tail (2) is a universal interval-overlap identity.  In
particular, it remains true before imposing Sidonicity or support
disjointness.  This explains why weighting tail domination alone does
not locate (G): the information responsible for the missing endpoint
is precisely the exclusion of coincident positive and negative atoms,
not positivity of their integrated path.

The correct target-sensitive defect is

\[
 \mathcal E(Z,G)
    :=(W-G)-3(W-p^2)=3p^2-(G+2W).                             \tag{31}
\]

For (W\geq(3/2-o(1))p^2), the width term alone gives the required
endpoint.  For smaller (W), it is enough to prove

\[
                     \max(\mathcal E(Z,G),0)=o(p^2).           \tag{32}
\]

Equivalently, it is enough that
(\mathcal E(Z,G)\leq o(p^2)).  In the near-minimal band
(W=p^2+O(p^{3/2})), this becomes the requested
(W-G=O(p^{3/2})) scale.  Away from that band, (32) allows exactly the
additional inversion span already paid for by the width excess.

Thus the surviving frontier is (32) under
(W\leq(3/2+o(1))p^2), using the disjoint sparse atoms themselves.
Global variation, a universal (p)-scale tail floor, bounded Hankel
oscillation, and a centered zero count are all exactly excluded by the
certificates above.

The public record still lists problem 864 as open and contains no
claimed partial solution (accessed 2026-07-12):
<https://www.erdosproblems.com/864>.  The general Newman-zero literature
also permits broad interior-zero counts without the present Sidon
constraint; see Hare--Jankauskas,
<https://arxiv.org/abs/1910.13994>.  The novelty gate found no published
curvature-span or excess-compensated estimate matching (32).

The undoubled ruler (13) is the classical Erdos--Turan construction:
<https://doi.org/10.1112/jlms/s1-16.4.212>.  No novelty is claimed for
that ruler.  The point here is its doubled odd-shift specialization as
an exact falsifier to an unconditional P52 curvature-span statement,
together with Lemma P60.1 and the reduced frontier (32).
