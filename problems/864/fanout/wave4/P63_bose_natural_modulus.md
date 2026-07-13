# P63: natural-modulus Bose lifts have no literal hole eventually

## 1. Result

Let \(q\) be a prime power, put \(h=q^2-1\), choose a primitive element
\(\theta\in\mathbb F_{q^2}\), and define the Bose--Chowla set

\[
 \mathcal B_q=\{e(t)\in\mathbb Z/h\mathbb Z:
                 \theta^{e(t)}=\theta+t,\ t\in\mathbb F_q\}.
\]

The following theorem closes the natural-modulus construction sidecar.

**Theorem P63 (uniform Bose carry mixing).** Uniformly over

\[
 u\in(\mathbb Z/h\mathbb Z)^*,\qquad
 c\in\mathbb Z/h\mathbb Z,\qquad b\in\{1,2\},
\]

let

\[
 R_{u,c}=\{[ue(t)+c]_h:t\in\mathbb F_q\}
          \subseteq\{0,\ldots,h-1\}.
\]

The number of ordered quadruples in \(R_{u,c}^4\) satisfying the literal
integer equation

\[
                 x_1+x_2+x_3+b=x_4                         \tag{1}
\]

is

\[
                 \left(\frac16+o(1)\right)q^2,             \tag{2}
\]

where the \(o(1)\) is uniform in \(u,c,b\). In particular, for all
sufficiently large prime powers \(q\), every affine Bose lift and both
values of \(b\) have a literal solution of (1).

Consequently, the zero-fold literal holes found through \(q=23\) cannot
persist along an infinite Bose--Chowla sequence at the natural modulus.
This result does not assert that the first hole-free parameter is \(25\):
the finite census proves that statement only for the tested parameters
through \(64\).

The mechanism is a carry law. The modular Bose equation has
\(q^2+O(q)\) solutions. Their normalized exponent representatives become
Haar distributed on the torus

\[
 \mathbb T_0=\{x\in(\mathbb R/\mathbb Z)^4:
                    x_1+x_2+x_3-x_4=0\},                  \tag{3}
\]

and the carry-zero sheet occupies exactly \(1/6\) of this torus.

## 2. Independent audit of the construction equivalence

Let

\[
 Z=\{0=z_0<\cdots<z_{q-1}=W\}\subseteq[0,h-1]
\]

be any cyclic lift of an affine copy of \(\mathcal B_q\). Put

\[
 \gamma=h-W-1,\qquad G=2\gamma+b.                         \tag{4}
\]

The natural-modulus gate used in P62 is

\[
 D^+(Z)\cap(G+S(Z))=\varnothing,                          \tag{5}
\]

where \(S(Z)\) contains all unordered sums, including \(2z\). Set
\(B=\gamma+Z\). Rearranging an equality gives the exact equivalence

\[
\begin{aligned}
 -b\in3B-B
 &\iff \exists x,y,t,w\in Z:
       2\gamma+x+y+t-w=-b\\
 &\iff \exists x,y,t,w\in Z:
       w-t=G+x+y\\
 &\iff D^+(Z)\cap(G+S(Z))\ne\varnothing .                \tag{6}
\end{aligned}
\]

No distinctness is imposed in (6), so diagonals and every repeated positive
summand are retained.

There are two equivalent constructions. First,

\[
 E=2B+b=G+2Z                                              \tag{7}
\]

is a positive same-parity Sidon set and

\[
 E\cap3E=\varnothing\quad\Longleftrightarrow\quad
 -b\notin3B-B.                                            \tag{8}
\]

Second, put \(X=W-Z\) and

\[
 L=G+2W=2h-2+b,\qquad A_0=X\cup(L-X).                    \tag{9}
\]

Condition (5) says exactly that the only repeated unordered sum of \(A_0\)
is \(L\), with \(q\) representations. The two blocks are disjoint because
\(G>0\). Translating by one gives an admissible \(2q\)-set in
\([1,L+1]\). Thus an infinite sequence of natural holes would have

\[
 \frac{2q}{\sqrt{L+1}}\longrightarrow\sqrt2,              \tag{10}
\]

which would disprove the proposed \(2/\sqrt3\) constant. Theorem P63 rules
out precisely this construction lane.

## 3. Exact two-parameter description of the modular solutions

Fix \(u,c,b\), and let

\[
 a=u^{-1}(-2c-b)\pmod h,\qquad \alpha=\theta^a.            \tag{11}
\]

Writing \(A_t=\theta+t\), the modular equation associated with (1) is

\[
        A_{t_1}A_{t_2}A_{t_3}=\alpha A_{t_4}.              \tag{12}
\]

Let \(K=\mathbb F_{q^2}\), let coefficient conjugation be
\(\sigma:x\mapsto x^q\), and put \(\kappa=\theta-\theta^q\). For a rational
expression in variables over \(\mathbb F_q\), superscript \(\sigma\) means
that its coefficients are conjugated while its variables are fixed. Thus
on \(\mathbb F_q\)-points \(P^\sigma=P^q\), but \(P^\sigma\) has the same
degree as \(P\).

For fixed \(t_1,t_2\), set

\[
             P=\frac{A_{t_1}A_{t_2}}{\alpha}.             \tag{13}
\]

If \(P\notin\mathbb F_q\), (12) has exactly one completion. It is

\[
 t_3=\frac{\kappa-P\theta+P^\sigma\theta^q}
           {P-P^\sigma},\qquad
 A_{t_4}=P A_{t_3}.                                      \tag{14}
\]

Indeed, the first expression is fixed by conjugation, and direct
substitution gives \(A_{t_4}-A_{t_4}^q=\kappa\), so both \(t_3,t_4\) lie
in \(\mathbb F_q\). Conversely, subtracting the conjugate of
\(P(\theta+t_3)=\theta+t_4\) forces (14).

If \(P\in\mathbb F_q\), there are no completions unless \(P=1\); when
\(P=1\), every \(t_3=t_4\) is a completion. For each \(t_1\), the affine
\(\mathbb F_q\)-line

\[
       A_{t_1}(\theta+\mathbb F_q)/\alpha
\]

meets \(\mathbb F_q\) in at most one point. It cannot equal
\(\mathbb F_q\): equality of directions would put \(A_{t_1}/\alpha\) in
\(\mathbb F_q^*\), after which the offset
\((A_{t_1}/\alpha)\theta\) is not in \(\mathbb F_q\). Hence there are at
most \(q\) scalar pairs. Bose Sidonicity gives at most two ordered pairs
with \(A_{t_1}A_{t_2}=\alpha\). Therefore the total number
\(Q_q(\alpha)\) of solutions of (12) satisfies

\[
             Q_q(\alpha)=q^2+O(q)                        \tag{15}
\]

uniformly in \(\alpha\). More explicitly, if \(s\le q\) is the number of
scalar pairs and \(i\le2\) is the number of ordered identity pairs, then

\[
             Q_q(\alpha)=q^2-s+qi.                       \tag{16}
\]

## 4. The character-sum estimate

We use the following bounded-complexity consequence of the Grothendieck
trace formula and Deligne's weight theorem.

**Lemma 4.1 (Bose surface estimate).** Let
\(\chi_1,\ldots,\chi_4\) be multiplicative characters of \(K^*\). If there
is no character \(\chi\) for which

\[
       (\chi_1,\chi_2,\chi_3,\chi_4)
          =(\chi,\chi,\chi,\chi^{-1}),                    \tag{17}
\]

then, uniformly in \(\alpha\in K^*\),

\[
 \left|\sum_{(t_1,t_2,t_3,t_4)\ {\rm satisfying}\ (12)}
       \prod_{j=1}^4\chi_j(A_{t_j})\right|
       =O(q^{3/2}).                                       \tag{18}
\]

The implied constant is absolute.

**Proof.** Remove the \(O(q)\) scalar pairs in Section 3. Formula (14)
identifies the remaining solution variety with the open subset

\[
 U=\{(t_1,t_2)\in\mathbb A^2:P-P^\sigma\ne0\}.            \tag{19}
\]

Using (12), the summand, up to the constant
\(\chi_4(\alpha^{-1})\), becomes

\[
 (\chi_1\chi_4)(A_{t_1})
 (\chi_2\chi_4)(A_{t_2})
 (\chi_3\chi_4)(A_{t_3(t_1,t_2)}).                       \tag{20}
\]

Regard \(K^*\) as the \(\mathbb F_q\)-points of the two-dimensional torus
\(T=\operatorname{Res}_{K/\mathbb F_q}\mathbb G_m\). A multiplicative
character of \(K^*\) gives its rank-one tame Lang sheaf on \(T\). Pulling
the three sheaves in (20) back to \(U\) gives a rank-one sheaf pure of
weight zero. Its ramification divisor has bounded degree independent of
\(q,\alpha\), and of the orders of the characters: \(P-P^\sigma\), the
numerator \(1-P^\sigma\), and all coordinate functions in (14) have degree
at most two. No degree-\(q\) Frobenius polynomial is used here.

The tensor product in (20) is geometrically constant only when all three
characters \(\chi_j\chi_4\) are trivial. Here is the required monodromy
check. Over \(\overline{\mathbb F}_q\), a generic point of the vertical
divisor \(t_1=-\theta\) is neither a zero nor a pole of the other two
coordinate functions, so its tame inertia forces
\(\chi_1\chi_4=1\). The conjugate vertical divisor gives the other
geometric character of the restriction-of-scalars torus. The two horizontal
divisors similarly force \(\chi_2\chi_4=1\). After these characters are
removed, a generic component of \(1-P^\sigma=0\), the numerator of

\[
       A_{t_3}=\kappa\,\frac{1-P^\sigma}{P-P^\sigma},      \tag{21}
\]

and its conjugate force \(\chi_3\chi_4=1\). Thus geometric constancy is
equivalent to (17).

Compactify \(U\) in \(\mathbb P^1\times\mathbb P^1\). The number and
degrees of the boundary and ramification components are bounded absolutely,
so the compactly supported Betti numbers of the tame rank-one sheaf are
bounded absolutely. Geometric nonconstancy gives \(H_c^4=0\) by Poincare
duality. The remaining cohomology has weights at most \(3\), and the trace
formula therefore gives \(O(q^{3/2})\). Reinstating the scalar locus changes
the sum by only \(O(q)\). This proves (18). QED.

## 5. Weyl limit and the one-sixth carry

Let \(\mathcal V_{q,u,c,b}\subseteq R_{u,c}^4\) be the modular solution set
and put the uniform probability measure on the normalized tuples

\[
        (x_1/h,x_2/h,x_3/h,x_4/h).                        \tag{22}
\]

For a fixed Fourier mode
\(n=(n_1,n_2,n_3,n_4)\in\mathbb Z^4\), its unnormalized Fourier coefficient
is the sum in Lemma 4.1 with

\[
                    \chi_j(\theta)=
           \exp(2\pi i u n_j/h),                          \tag{23}
\]

apart from a harmless translation phase. Since \(u\) is a unit, for all
large \(h\), condition (17) fails exactly when

\[
                  n_1=n_2=n_3=-n_4.                      \tag{24}
\]

In this exceptional case the phase is constant on the modular equation and
tends to \(1\). In every other case, (15) and (18) make the normalized
coefficient \(O(q^{-1/2})\), uniformly in \(u,c,b\). Weyl's criterion gives
uniform weak convergence to Haar measure on the torus (3).

Projection of Haar measure on (3) to \((x_1,x_2,x_3)\) is ordinary Lebesgue
measure on \([0,1)^3\). For a modular solution, the carry is zero exactly
when

\[
                    x_1+x_2+x_3+b<h.                     \tag{25}
\]

After division by \(h\), the limiting boundary
\(y_1+y_2+y_3=1\) has measure zero, while

\[
 \operatorname{vol}\{(y_1,y_2,y_3)\in[0,1)^3:
                         y_1+y_2+y_3<1\}=\frac16.          \tag{26}
\]

Equations (15), (25), and (26) prove (2). Uniformity follows by
contradiction: any sequence of parameters violating uniform convergence
has the same Fourier limit by the uniform estimate (18). This completes
the proof of Theorem P63.

## 6. Exact finite verification

Two independent executable checks accompany the theorem.

    python -B problems/864/compute/p63/audit_natural_bose_holes.py \
      --parameters 3 4 5 7 8 9 11 13 16 17 19 23 25 27 29 \
      --output problems/864/compute/p63/natural_bose_holes_q29.json

This regenerates every affine/cut lift, checks (5) both as a support
intersection and as an ordered \(3B-B\) count, constructs \(E\) and \(A_0\),
and performs a fresh diagonal-inclusive sum census on every valid row. It
finds respectively \(2,1,1,0\) valid \(b=1\) lifts at
\(q=17,19,23,25\). At \(q=25\), the minimum support hit count is \(3\)
and the corresponding ordered carry-zero count is \(4\).

    python -B problems/864/compute/p63/audit_bose_parametrization.py \
      --parameters 3 4 5 7 8 9 11 13 \
      --output problems/864/compute/p63/bose_parametrization.json

The same command was run for \(q=16,17,19,23\), with output
problems/864/compute/p63/bose_parametrization_large.json. For twenty-four
independently selected affine/cut targets in total, it constructs (14) in
the finite field, compares its entire solution set with all \(q^4\) ordered
tuples, and verifies (16) exactly. All comparisons pass.
The larger P62 audit supplies the independent zero-valid census at every
tested prime power \(25\le q\le64\).

## 7. Scope

P63 proves alternative (A) for the assigned sidecar: natural-modulus
Bose--Chowla literal holes cannot persist infinitely. It does not rule out
centers at a different modulus, a non-affine rearrangement of Bose points,
or a different algebraic family. It therefore closes one negative
construction mechanism, not Erdos Problem 864 itself.

The analytic input in Lemma 4.1 is the standard trace-formula consequence
of Deligne's weight theorem; a primary source is P. Deligne, *La conjecture
de Weil II*, Publ. Math. IHES 52 (1980), 137--252. The proof above records
the specialization and the nonconstant-monodromy check needed here, so no
generic equidistribution assertion is used without its exceptional
character line.
