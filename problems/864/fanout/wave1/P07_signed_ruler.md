# P07: fully reflected signed-ruler core

## Verdict

The target

\[
 \operatorname{span}(A)\ge (3-o(1))p^2
\]

is not proved here.  There is, however, an exact coupling-sensitive
rank-window inequality.  It strictly strengthens the ordinary Golomb-ruler
window bound by charging every shifted sum label which excludes a possible
difference.  The finite P03 example shows an exact obstruction: on its whole
overlap interval the difference labels and shifted sum labels form a
partition.  Consequently **every** nonnegative interval-weighted packing
inequality on that overlap is an equality for that example; range separation,
or a universal positive packing slack, is false.

There is also a larger exact finite falsifier to the unqualified coefficient
`3` inequality.  Nine lower representatives give a fully reflected
admissible set of span `116`, whereas `3p^2=243`.  This is not an asymptotic
disproof.

## 1. Exact signed-ruler normalization

Translate so that \(x_1=0\), and put

\[
 L=\sigma,\qquad W=x_p,\qquad G=L-2W>0.
\]

Reverse the lower ruler by setting

\[
 Z=\{W-x:x\in X\}=\{0=z_0<z_1<\cdots<z_{p-1}=W\}.
\]

Write

\[
 D(Z)=\{z_j-z_i:0\le i<j<p\},
 \qquad
 S(Z)=\{z_i+z_j:0\le i\le j<p\}.
\]

Then the two label families in the question are exactly

\[
 \{d_{ij}}=D(Z),\qquad
 \{c_{ij}:i<j\}\mathbin{\dot\cup}\{e_i\}=G+S(Z).       \tag{1}
\]

Indeed,

\[
 L-x_i-x_j=G+(W-x_i)+(W-x_j),
\]

and the diagonal case is \(L-2x_i=e_i\).  Thus full label distinctness is
equivalent to the two exact conditions

\[
 Z\text{ is Sidon (diagonals included)},
 \qquad
 D(Z)\cap(G+S(Z))=\varnothing.                              \tag{2}
\]

This is stronger than a marginal count.  It is also precisely the
forbidden-center criterion \(L\notin S(X)+D(X)\), rewritten so that the
overlap occurs inside \([1,W]\).  The coupling \(d_{ij}+c_{ij}=e_i\) is
retained by (1), not imposed as an extra independent relation.

## 2. Coupled interval-window lemma

For \(1\le r<p\), let

\[
 V_r=\{z_{i+h}-z_i:1\le h\le r,\ 0\le i<p-h\},
\]

and put

\[
 M_r=|V_r|=rp-\frac{r(r+1)}2,
 \qquad T_r=\sum_{v\in V_r}v.
\]

The cardinality formula uses Sidonicity, hence all selected differences are
distinct.  For an integer \(u\ge1\), define the coupled shifted-sum weight

\[
 \Phi_{Z,G}(u)
 =\sum_{0\le i\le j<p}(u-G-z_i-z_j)_+,
 \qquad y_+=\max(y,0).
\]

**Lemma 1 (exact cutoff inequality).**  Under (2), for every \(r,u\),

\[
 \boxed{
 uM_r-\binom u2+\Phi_{Z,G}(u)
 \ \le\ T_r\ \le\ \binom{r+1}{2}W.}                       \tag{3}
\]

**Proof.**  For every positive integer \(v\),

\[
 v\ge u-(u-v)_+.
\]

Summing over the distinct set \(V_r\subseteq D(Z)\) gives

\[
 T_r\ge uM_r-\sum_{v\in V_r,\ v<u}(u-v).                   \tag{4}
\]

By (2), no integer \(G+z_i+z_j\) belongs to \(V_r\).  All these shifted
sums are distinct.  Therefore their weights can be removed from the total
triangular capacity below \(u\):

\[
 \sum_{v\in V_r,\ v<u}(u-v)
 \le \sum_{t=1}^{u-1}(u-t)
      -\sum_{i\le j}(u-G-z_i-z_j)_+
 =\binom u2-\Phi_{Z,G}(u).                                  \tag{5}
\]

Equations (4)-(5) prove the lower bound.  If
\(g_j=z_{j+1}-z_j\), then a fixed gap \(g_j\) occurs at most \(h\) times
among the lag-\(h\) differences.  Hence

\[
 T_r\le\sum_{h=1}^r h\sum_jg_j
 =\binom{r+1}{2}W,
\]

which proves (3).  QED.

The term \(\Phi_{Z,G}\) is the information discarded by the ordinary
rank-window argument.  It measures shifted sum labels below the chosen
cutoff with their exact triangular weights.  No separation of the \(D\) and
\(G+S\) ranges is assumed.

There is also a useful complete-weight form.  For every nonnegative function
\(w:\{1,\ldots,W\}\to\mathbb R_{\ge0}\),

\[
 \sum_{d\in D(Z)}w(d)
 +\sum_{h\in(G+S(Z))\cap[1,W]}w(h)
 \le\sum_{t=1}^Ww(t).                                      \tag{6}
\]

This is immediate from (2), but it identifies exactly what any
nonnegative interval-packing argument can see.

## 3. Exact audit of the P03 interlacing example

P03 used

\[
 X=\{0,1,3,8,12\},\qquad L=30.
\]

Thus \(W=12\), \(G=6\), and

\[
 Z=\{0,4,9,11,12\}.
\]

Direct enumeration gives

\[
 D(Z)=\{1,2,3,4,5,7,8,9,11,12\},                           \tag{7}
\]

while

\[
 (G+S(Z))\cap[1,W]=\{6,10\}.                               \tag{8}
\]

Consequently

\[
 D(Z)\mathbin{\dot\cup}\bigl((G+S(Z))\cap[1,W]\bigr)
 =\{1,2,\ldots,12\}.                                       \tag{9}
\]

Thus (6) is an equality for **every** nonnegative weight \(w\).  The labels
interlace as

\[
 6\ (G+S),\ 7,8,9\ (D),\ 10\ (G+S),\ 11,12\ (D),
\]

so neither \(G\ge W\) nor disjoint \(d/c\) bands may be inserted into a
proof.

The cutoff lemma can also be audited numerically without relaxation:

\[
\begin{array}{c|c|c|c|c}
r&M_r&T_r&\max_u\{uM_r-\binom u2+\Phi(u)\}&\text{maximizing }u\\ \hline
1&4&12&10&5\\
2&7&31&30&9\\
3&9&50&50&12\\
4&10&62&62&13
\end{array}                                                 \tag{10}
\]

In particular, the coupled lower bound is exact for \(r=3,4\).  This is a
falsifier to any proposed universal strict improvement obtained solely by
choosing a different nonnegative interval weight on the same packing.

## 4. Explicit \(p=9\) finite falsifier to coefficient 3

Take

\[
 X=\{0,1,3,11,15,20,36,43,49\},\qquad \sigma=L=116.         \tag{11}
\]

Here \(p=9\), \(W=49\), \(G=18\), and

\[
 Z=\{0,6,13,29,34,38,46,48,49\}.
\]

The complete positive-difference certificate is

\[
\begin{aligned}
D(Z)=\{&1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,\\
      &23,25,28,29,32,33,34,35,36,38,40,42,43,46,48,49\}.
\end{aligned}                                               \tag{12}
\]

The complete shifted-sum certificate, equal to the union of all \(c_{ij}\)
and \(e_i\), is

\[
\begin{aligned}
18+S(Z)=\{&18,24,30,31,37,44,47,52,53,56,58,60,62,64,65,66,
67,69,70,72,73,76,77,79,80,81,85,86,90,93,94,95,96,98,\\
&100,101,102,104,105,110,112,113,114,115,116\}.
\end{aligned}                                               \tag{13}
\]

List (12) has \(\binom92=36\) entries, list (13) has
\(\binom{10}2=45\) entries, and the displayed lists are disjoint.  Hence all
\(81=p^2\) labels are distinct.  By (1)-(2), the fully reflected set

\[
\begin{aligned}
A=X\cup(116-X)=\{&0,1,3,11,15,20,36,43,49,67,73,80,\\
                  &96,101,105,113,115,116\}
\end{aligned}
\]

is admissible with sole repeated sum \(116\).  Its span is

\[
 \operatorname{span}(A)=116<243=3p^2.                       \tag{14}
\]

This exactly falsifies a finite bound of the form \(L\ge3p^2-C\) with any
universal \(C<127\), but it says nothing by itself about the requested
asymptotic \(3-o(1)\) coefficient.

## 5. Reproducible finite optimization audit

An OR-Tools CP-SAT model used integer variables
\(0=z_0<\cdots<z_{p-1}\), \(G\ge1\), imposed `AllDifferent` on

\[
 \{z_j-z_i:i<j\}\cup\{G+z_i+z_j:i\le j\},
\]

and minimized \(G+2z_{p-1}\).  With 16 workers and a 120-second cap per
instance, it returned proved `OPTIMAL` values

\[
\begin{array}{c|rrrrrrrr}
p&2&3&4&5&6&7&8&9\\ \hline
L_{\min}&4&10&19&30&48&68&85&116.
\end{array}                                                 \tag{15}
\]

The \(p=9\) witness (11) is therefore also the optimum of this exact finite
model.  A \(p=10\) run found \(L=152\) with lower bound \(134\) before the
120-second cap, so no optimality claim is made there.  The explicit
certificates (12)-(13), not the solver status, prove the finite falsifier.

## 6. Precise surviving obstruction

Lemma 1 is the desired interval-weighted inequality using the coupling.  Its
uncontrolled term is now explicit:

\[
 \Phi_{Z,G}(u)=\sum_{i\le j}(u-G-z_i-z_j)_+.
\]

To derive \(L\ge(3-o(1))p^2\) from (3), one needs a proved lower bound for
this truncated sum energy at a cutoff compatible with the rank-window upper
bound, uniformly over Sidon rulers (Z\).  Ordinary marginal counts do not
supply such a bound, and (9) shows there is no universal finite packing
slack to invoke.  Any successful continuation must prove a quantitative
distribution theorem for the *same* ruler \(Z\); assuming asymptotic band
separation would simply assume the missing theorem.
