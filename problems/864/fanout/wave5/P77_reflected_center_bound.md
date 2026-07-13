# P77: an unconditional one-fold fourth-order spike inequality

## Verdict

This note does not prove the fully reflected center bound. It gives a new
exact inequality which removes the difference-fold term from P69. For every
literal reflected hole, the compensated center deficit satisfies

\[
 \boxed{
 L_h^5\Lambda(B,h,b)\ge
 {\bigl({\cal E}-p+b-10C_S\bigr)_+\over128}.}
 \tag{1}
\]

Here \({\cal E}=3p^2-M\), \(C_S\) is the modular sum-fold count in the
parity normalization, and \(\Lambda\) is the nonzero fourth-order Fourier
coefficient from P69. The formerly proposed positive-defect P65 assertion
\(C_S\le2p-3\) would turn (1) into

\[
 \boxed{
 L_h^5\Lambda(B,h,b)\ge
 {\bigl({\cal E}-21p+b+30\bigr)_+\over128}.}
 \tag{2}
\]

The implication from (1) to (2) is valid algebraically, but P75 gives an
exact positive-defect counterexample to P65. Therefore (2) cannot be used
unconditionally and the modular sum-fold alternative remains. The surviving
result is (1), a dependency compression involving the actual fold count.

## 1. Exact normalization of the original center problem

Let

\[
 B_0=\{0=b_0<\cdots<b_{p-1}=W\}\subseteq[0,W]
\]

be integer Sidon, with diagonal sums included.  Suppose \(M>2W\) and

\[
 M\notin S(B_0)+\Delta^+(B_0).                       \tag{3}
\]

Put

\[
 Z=W-B_0,\qquad G=M-2W.                              \tag{4}
\]

Reflection preserves the positive-difference support and sends
\(S(B_0)\) to \(2W-S(Z)\).  Hence (3) is exactly

\[
 \Delta^+(Z)\cap\bigl(G+S(Z)\bigr)=\varnothing.       \tag{5}
\]

Choose

\[
 b=\begin{cases}1,&G\text{ odd},\\2,&G\text{ even},\end{cases}
 \qquad
 \gamma={G-b\over2},
 \qquad
 B=\gamma+Z,
 \qquad
 h=\gamma+W+1.                                      \tag{6}
\]

Then \(B\subseteq\{0,\ldots,h-1\}\), \(\max B=h-1\), and (5) is
equivalent to

\[
                         -b\notin3B-B.                 \tag{7}
\]

Indeed, an equality \(x+y+z+b=w\) in \(B\), after subtracting the
translations in (6), is exactly

\[
 G+z_x+z_y=z_w-z_z,
\]

which is forbidden by (5), and the converse is the same calculation
backwards.  Repetitions, including \(x=y\), are retained.

The normalized parameters obey

\[
 h={M-b+2\over2},
 \qquad
 \delta={3p^2-p+2\over2}-h,
 \qquad
 {\cal E}:=3p^2-M=2\delta+p-b.                       \tag{8}
\]

Thus the desired assertion \(M\ge(3-o(1))p^2\) is exactly the one-sided
claim \(\delta_+=o(p^2)\).

## 2. Fold-eliminated Fourier lemma

Reduce the literal sum and difference supports of \(B\) modulo \(h\), and
write

\[
 C_S=|S(B)|-|\overline{S(B)}|,
 \qquad
 C_D=|B-B|-|\overline{B-B}|.                         \tag{9}
\]

Let \(L_h=2+H_{\lfloor h/2\rfloor}\), and let \(\Lambda(B,h,b)\) be the
maximum nonzero Fourier coefficient of the four-point incidence function
\({\cal G}_{h-b}\) defined in P69.

### Lemma P77.1 (one-fold spike inequality)

Under (7), if \(h\ge4\), then (1) holds.

### Proof

P45's exact modular energy identity gives

\[
 C_D=\sum_{s,s+h\in S(B)}q(s)q(s+h),                 \tag{10}
\]

where every factor \(q(s)\) is either one or two.  Each folded sum fiber
contributes once to \(C_S\), so (10) gives the pointwise bound

\[
                         C_D\le4C_S.                  \tag{11}
\]

P69.1 gives, for the modular quadruple count \(Q_b(B)\),

\[
 Q_b(B)\ge\bigl(\delta-C_S-C_D\bigr)_+.
\]

Using (11),

\[
 Q_b(B)\ge\bigl(\delta-5C_S\bigr)_+.                \tag{12}
\]

P69.2 gives

\[
 \Lambda(B,h,b)\ge
 {Q_b(B)\binom{h-b+2}{3}\over4h^3L_h^5}.             \tag{13}
\]

For \(b\in\{1,2\}\) and \(h\ge4\), P69's exact elementary estimate is

\[
                         {\binom{h-b+2}{3}\over h^3}
                         \ge{1\over16}.               \tag{14}
\]

Equations (12)--(14) imply

\[
 L_h^5\Lambda(B,h,b)
 \ge {\bigl(\delta-5C_S\bigr)_+\over64}.
\]

Substituting \(2\delta={\cal E}-p+b\) from (8) proves (1).  QED.

### Conditional calculation P77.2 (premise falsified by P75)

Assume \(\delta>0\) and the positive-defect P65 bound

\[
                         C_S\le2p-3.                  \tag{15}
\]

Then (2) holds.

### Proof

Insert (15) into (1):

\[
 {\cal E}-p+b-10C_S
 \ge {\cal E}-p+b-20p+30
 = {\cal E}-21p+b+30.
\]

QED.

The premise (15) is false in general by P75, so this conditional calculation
is not available in the proof program.

### Conditional calculation P77.3 (not an unconditional target)

Suppose counterfactually that P65 holds for every positive-defect
normalization. If, uniformly
over all data (3)--(7),

\[
                         L_h^5\Lambda(B,h,b)=o(p^2),  \tag{16}
\]

then

\[
                         M\ge(3-o(1))p^2.             \tag{17}
\]

Conversely, if some sequence satisfies
\({\cal E}\ge\varepsilon p^2\) for a fixed \(\varepsilon>0\), then for all
sufficiently large \(p\),

\[
                         L_h^5\Lambda(B,h,b)
                         \ge {\varepsilon p^2\over256}. \tag{18}
\]

### Proof

If (17) fails by a fixed proportion, then \(\delta>0\) by (8).  Equation
(2) and (16) give \({\cal E}=o(p^2)\), a contradiction.  For (18), choose
\(p\) so large that \(21p-b-30\le\varepsilon p^2/2\) and use (2).
QED.

## 3. Why this does not yet close the theorem

The standard modular fourth-moment estimate is not strong enough for (16).
P45 gives the modular additive energy

\[
 \sum_rR_-(r)^2=2p^2-p+2C_D.
\]

Even after (15) and (11), this is only \(O(p^2)\).  Hölder applied to the
Fourier expansion of \({\cal G}_{h-b}\) therefore gives only an
\(O(p^2)\) coefficient bound.  Explicitly, if \(f=1_B\), each coefficient
has the form

\[
 {1\over h}\sum_t
 \widehat f(t)\widehat f(\alpha-t)
 \widehat f(\beta-t)\widehat f(\gamma-t)
\]

up to harmless signs and a unit phase.  Four-factor Holder and Parseval
bound its absolute value by

\[
 {1\over h}\sum_t|\widehat f(t)|^4
 =\sum_rR_-(r)^2=O(p^2).                              \tag{19}
\]

This does not imply the little-o estimate required in (16), especially
after the factor \(L_h^5\).  Thus the fourth moment plus P65 cannot finish
the argument.  A successful continuation must exploit either the literal
carry-zero exclusion inside the phase of a nonzero coefficient, or an
inverse theorem showing that a spike of size (18) contradicts the endpoint
normalization and positive defect.

This also explains why the already closed natural Singer, Bose--Chowla, and
Ruzsa lanes do not settle the arbitrary-ruler theorem: their special
character-sum estimates establish the required decay for those families,
but no uniform inverse statement for all integer Sidon rulers is currently
available.

## 4. Exact finite audit

The stored P46 report contains 134 positive-defect reflected rows.  An
independent integer scan of those rows checked

\[
 C_S\le2p-3,
 \qquad
 C_D\le4C_S,
 \qquad
 C_S+C_D\le10p-15.
\]

There were zero failures of all three inequalities in that stored corpus;
the largest value of
\((C_S+C_D)-(10p-15)\) was \(-3\).  This is only a finite check of the
P65 hypothesis. P75 lies outside that corpus and falsifies P65. Lemma
P77.1 itself is exact and follows from the proved P45 and P69 identities,
not from the census.

## 5. Claim boundary

The new unconditional statement is (1). Statement (2) has a false premise
by P75 and is not part of the live route. Neither a suitable joint bound on
`C_S` and `Lambda` nor the coefficient-three reflected center theorem is
proved. No infinite sub-three counterfamily is constructed.
