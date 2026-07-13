# P72: mixed completion slack

## Verdict

The first proposed statement is proved:

\[
                         w\le h_D.                       \tag{1}
\]

The second proposed statement

\[
              2v+w+u\le |D_R|+h_D                       \tag{2}
\]

is **blocked**: I found neither a proof nor a counterexample.  The exact
span-55 census has zero failures in all 30,899,206 nonempty-residual cases,
but that finite fact is not a proof of (2).  P73 and P74 supersede further
work on this exact strengthening: P73 reduces the original completion
charge to 35 finite boxes, and P74 proves the original charge eventually.

The argument below records the exact centered-coordinate count, proves
(1), proves (2) in the already known easy range, and identifies the precise
term lost by the centered union method.

## 1. Setup and two elementary exclusions

Use the notation of P56.  Thus

\[
 P=A\cap(\sigma-A),\qquad R=A\setminus P,
\]

\[
 |P|=c=2p+\delta,\qquad |R|=u,
\]

and the exceptional sum has at least two representations, so $c\ge3$.
Write

\[
 D=D^+(A)=D_P\mathbin{\dot\cup}D_R,
 \qquad h_D=L-|D|.
\]

For every unordered residual pair $i\le j$, put

\[
 t_{ij}=r_i+r_j-\sigma,
 \qquad d_{ij}=|t_{ij}|.
\]

All signed values $t_{ij}$ are nonzero and distinct.  Indeed, zero would
mean that both residual endpoints have their reflections in $A$, while
equality of two signed values would give two representations of the same
nonexceptional sum.

For every $d>0$, at most the two signed values $d,-d$ can occur.
Consequently

\[
 q_d\le2.                                                \tag{3}
\]

Moreover, virtual labels avoid $D_P$.  If $d=y-x\in D_P$, reflection
of the core pair gives the two core sums

\[
 \sigma+d=(\sigma-x)+y,
 \qquad
 \sigma-d=x+(\sigma-y).
\]

A residual pair with folded label $d$ would give a second representation
of one of these nonexceptional sums.  Hence

\[
                         q_d=0\quad(d\in D_P).           \tag{4}
\]

In particular, every occurrence counted by $v$ lies on a label in
$D_R$.

## 2. Centered signed-layer identity

Let

\[
 T=\{t_{ij}:1\le i\le j\le u\}
\]

and let $T_0=T\cap[-L,L]$.  Also put

\[
 \Delta=\{\pm d:d\in D\}\subset[-L,L]\setminus\{0\}.
\]

Let $a_{\rm in}$ be the number of labels $d\notin D$ with
$q_d=1$ and $d\le L$.  The intersection $T_0\cap\Delta$ has exactly
$v$ elements: signed residual sums are distinct, and each occurrence
whose folded label lies in $D$ contributes its one signed value.
Furthermore

\[
 |T_0|=v+a_{\rm in}+2w.                                 \tag{5}
\]

Both sets in the union below lie in the $2L$-element set
$[-L,L]\setminus\{0\}$.  Inclusion-exclusion therefore gives

\[
\begin{aligned}
 2L
 &\ge |\Delta\cup T_0|\\
 &=2|D|+|T_0|-|\Delta\cap T_0|\\
 &=2|D|+a_{\rm in}+2w.
\end{aligned}                                           \tag{6}
\]

Thus

\[
                    a_{\rm in}+2w\le2h_D.              \tag{7}
\]

In particular, (1) follows.  Equivalently, one may map every doubled
nondifference label to itself: if $q_d=2$, then both
$\sigma-d$ and $\sigma+d$ lie in $[0,2L]$, so
$d\le\min(\sigma,2L-\sigma)\le L$; since $d\notin D$, it is a genuine
difference hole.  Distinct doubled labels give distinct holes.

Equation (6) also exposes the limitation of the most direct centered
double count: the $v$ bad virtual occurrences are precisely the
intersection term, and cancel identically.

## 3. Exact form of the blocked inequality

Let $a$ denote the total number of labels $d\notin D$ with $q_d=1$,
including labels larger than $L$.  Counting virtual residual pairs gives

\[
                 \binom{u+1}{2}=v+a+2w.                \tag{8}
\]

P56 gives

\[
 |D_R|=cu+\binom u2.
\]

Substituting (8), the margin in (2) is exactly

\[
\begin{aligned}
 |D_R|+h_D-(2v+w+u)
 &=a+u(c-2)+h_D-(v-w).                                  \tag{9}
\end{aligned}
\]

Hence (2) is equivalent to

\[
                 v-w\le a+u(c-2)+h_D.                  \tag{10}
\]

This is the unresolved P72 statement.  Neither (7) nor the raw residual
difference count controls the intersection term $v$.  For example,
$v+w\le h_D$ is already false for

\[
 A=\{0,1,3,7,8\},\qquad \sigma=8,
\]

where $v=1,w=0,h_D=0$.  The still more direct inequality
$2v\le|D_R|$ has 136 exact failures in the span-55 census.

## 4. Easy range

For completeness, (2) does follow from cardinalities when

\[
                         u\le2c-5.                      \tag{11}
\]

Indeed, (8) implies $v\le\binom{u+1}{2}-2w$, while (1) gives
$h_D\ge w$.  Therefore

\[
\begin{aligned}
 |D_R|+h_D-(2v+w+u)
 &\ge cu+\binom u2+w
       -2\binom{u+1}{2}+4w-w-u\\
 &=\frac{u(2c-u-5)}2+4w\\
 &\ge0.
\end{aligned}                                           \tag{12}
\]

Thus any proof of (2) still needed beyond P72 would only concern
$u>2c-5$, exactly the range in which the scalar cardinality argument
loses the signed overlap information later retained by P73.

## 5. Status

* `w <= h_D`: proved by (6)--(7).
* `2v+w+u <= |D_R|+h_D`: no counterexample through the stated exact
  span-55 census, but no proof obtained.
* The weaker centered-union mechanism is exhausted by (6): its
  inclusion-exclusion cancels `v` exactly.
* No claim of the unrestricted mixed inequality is made in this note.
