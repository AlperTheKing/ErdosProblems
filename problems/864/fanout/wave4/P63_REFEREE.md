# Referee report on P63: Bose natural-modulus carry mixing

## Verdict

**Validated, after supplying two omitted arithmetic-geometric details.**  I
found no counterexample to Lemma 4.1.  The exceptional character line is
exactly the one stated in (17), the top compactly supported cohomology does
vanish off that line, and the resulting estimate is uniform in
\(q,\alpha,u,c,b\).  However, the sentence invoking Deligne alone is not a
complete proof as written: one must also (i) compute geometric local
monodromy after splitting the restriction-of-scalars torus and (ii) invoke a
uniform Betti-number bound for bounded-complexity tame rank-one sheaves.  The
details below supply both points.

The elementary parametrization in Section 3 is correct.  In particular, the
scalar locus contributes at most \(2q\) solutions, not \(q^2\): there are at
most two ordered pairs with \(P=1\), and each has \(q\) completions.

## 1. The Lang sheaf has uniformly bounded conductor

Fix a characteristic \(p\), an auxiliary prime \(\ell\ne p\), and an
embedding of the relevant roots of unity into
\(\overline{\mathbb Q}_\ell\).  Put

\[
 T=\operatorname {Res}_{\mathbb F_{q^2}/\mathbb F_q}\mathbb G_m.
\]

A character \(\eta:T(\mathbb F_q)=\mathbb F_{q^2}^*\to
\overline{\mathbb Q}_\ell^*\) defines the usual rank-one Lang local system
\(\mathcal L_\eta\) on \(T\).  It is pure of weight zero.  It is also tame at
a toric compactification, uniformly in the order of \(\eta\), because that
order divides \(q^2-1\) and is therefore prime to \(p\).  For a rank-one tame
character, the conductor along a boundary component is either zero or one;
it does not grow with the order of the character.

Here is the local-monodromy calculation that is implicit in P63.  Over
\(\overline{\mathbb F}_q\), write

\[
 T_{\overline{\mathbb F}_q}\simeq\mathbb G_m^2
\]

with coordinates corresponding to the two embeddings of
\(\mathbb F_{q^2}\).  Geometric Frobenius interchanges the coordinates and
raises them to the \(q\)-th power, so the Lang map has exponent matrix

\[
 \begin{pmatrix}-1&q\\q&-1\end{pmatrix}.
\]

Consequently the two geometric tame inertia characters of
\(\mathcal L_\eta\) are represented, up to a simultaneous unit and
inversion, by

\[
 (qr,r)\pmod {q^2-1},
\]

where \(r=0\) if and only if \(\eta=1\).  Since
\(\gcd(q,q^2-1)=1\), triviality of either displayed inertia character already
forces \(\eta=1\).  This is the precise fact needed in the divisor argument;
it is stronger than merely saying that a multiplicative character gives a
Lang sheaf.

## 2. Exact geometric-constancy test

Set

\[
 \eta_1=\chi_1\chi_4,\qquad
 \eta_2=\chi_2\chi_4,\qquad
 \eta_3=\chi_3\chi_4.
\]

Write \(a=\theta\), \(a'=\theta^q\), and use coordinates \(x=t_1\),
\(y=t_2\).  Over the algebraic closure the two components of
\(A_{t_1}\) are \(a+x\) and \(a'+x\), and similarly for \(A_{t_2}\).
At the generic point of the divisor \(x=-a\), neither \(A_{t_2}\) nor
\(A_{t_3}\) has a zero or pole.  Thus local inertia there, or equivalently at
its conjugate \(x=-a'\), forces \(\eta_1=1\).  The horizontal divisors
\(y=-a\) and \(y=-a'\) similarly force \(\eta_2=1\).

For the third coordinate, formula (14) gives both split components explicitly:

\[
 a+t_3=(a-a')\frac{1-P^\sigma}{P-P^\sigma},\qquad
 a'+t_3=(a-a')\frac{1-P}{P-P^\sigma}.                 \tag{R1}
\]

The curve

\[
 C^\sigma:\ (a'+x)(a'+y)=\alpha^q
\]

is a smooth irreducible hyperbola because \(\alpha\ne0\).  It is not a
component of \(P-P^\sigma=0\): on \(C^\sigma\) the latter equation is
\(P=1\), and the curves \(P=1\) and \(P^\sigma=1\) cannot coincide since
\(a\ne a'\).  At the generic point of \(C^\sigma\), the first component in
(R1) vanishes, the second equals \(-(a-a')\), and all previously considered
coordinates are nonzero and finite.  Its inertia therefore forces
\(\eta_3=1\).  The conjugate curve gives the same conclusion from the other
split component.

It follows that the tensor product in (20) is geometrically constant if and
only if

\[
 \eta_1=\eta_2=\eta_3=1,
\]

which is equivalent to

\[
 (\chi_1,\chi_2,\chi_3,\chi_4)
   =(\chi,\chi,\chi,\chi^{-1}).
\]

There are no additional exceptional characters depending on \(\alpha\),
including when \(\alpha\in\mathbb F_q^*\).  In that case
\(P-P^\sigma\) drops in degree, but the two hyperbolas above still do not
coincide, so the same generic-divisor argument applies.

Strictly, the pullback sheaf is not defined on all of the set denoted \(U\)
in (19), because the split coordinate functions can vanish at geometric
points.  Let \(V\) be the further complement of all their zero and pole
divisors.  This does not change the trace sum: \(V(\mathbb F_q)=U(\mathbb
F_q)\), since every \(A_t=\theta+t\) occurring in an
\(\mathbb F_q\)-solution is a nonzero element of \(K\).  The divisor
calculation above takes place on the boundary of \(V\).  This harmless
shrinking should be made explicit in the final proof.

## 3. Uniform Betti bound and the exponent \(3/2\)

Let \(j:V\hookrightarrow X=\mathbb P^1\times\mathbb P^1\).  The zeros and
poles of the six split coordinate functions appearing above, together with
\(P-P^\sigma=0\) and the divisors at infinity, form a divisor with an
absolute bound on:

* the number of irreducible components;
* the bidegree of every component (at most \((2,2)\));
* all tame conductor exponents (at most one for this rank-one sheaf).

These bounds are independent of \(q,\alpha\), and the character orders.
Shared components or specializations of \(\alpha\) can only reduce the
number of distinct components.  By Bezout, a bounded number of point
blowups resolves this divisor to a simple-normal-crossings divisor, with an
absolute bound on the resulting incidence data.

The standard bounded-complexity theorem for tame rank-one sheaves on the
complement of such a divisor now gives

\[
 \sum_i\dim H_c^i(V_{\overline{\mathbb F}_q},\mathcal L)\le C           \tag{R2}
\]

for an absolute constant \(C\).  This is the extra input needed in addition
to Deligne's weight theorem.  In this particular surface case, (R2) also
follows by applying the tame Grothendieck--Ogg--Shafarevich formula on the
fibres of either projection after the bounded resolution and then using the
Leray spectral sequence.  Every fibre has a bounded number of punctures and
rank one, so both the fibre cohomology and the finite exceptional-fibre
contribution are bounded absolutely.

The open set \(V\) is a geometrically connected smooth surface.  Off the
exceptional character line, Section 2 shows that \(\mathcal L\) is
geometrically nonconstant.  Poincare duality therefore gives

\[
 H_c^4(V_{\overline{\mathbb F}_q},\mathcal L)
 \simeq H^0(V_{\overline{\mathbb F}_q},\mathcal L^\vee)^\vee(-2)=0.
\]

Deligne's theorem bounds the weights of \(H_c^i\) by \(i\).  Since only
\(i\le3\) remains and (R2) bounds the total dimension, the trace formula
gives

\[
 \left|\sum_{V(\mathbb F_q)}\operatorname {tr}(\operatorname {Frob},
 \mathcal L)\right|\le Cq^{3/2}.
\]

Adding back the at most \(2q\) scalar-locus solutions preserves this bound.
Thus (18), including its uniformity and its absolute implied constant, is
justified.

## 4. Uniform Weyl-to-carry passage

For a fixed Fourier mode \(n\in\mathbb Z^4\), multiplication by the unit
\(u\) is invertible modulo \(h=q^2-1\).  Once \(h>2\max_i|n_i|\), the
exceptional congruences are equivalent to the integer identities

\[
 n_1=n_2=n_3=-n_4.
\]

On this annihilator line the phase on the modular solution set is
\(\exp(-2\pi i n_1b/h)\), which tends uniformly to one for
\(b\in\{1,2\}\).  Off the line, Lemma 4.1 and
\(Q_q(\alpha)=q^2+O(q)\) give a normalized Fourier coefficient
\(O(q^{-1/2})\), uniformly in \(u,c,b\).

To make the final indicator argument uniform, fix \(\varepsilon>0\) and
sandwich the indicator of

\[
 \{(y_1,y_2,y_3):y_1+y_2+y_3<1\}
\]

between continuous functions whose Haar integrals differ by at most
\(\varepsilon\); this is possible because the boundary plane has measure
zero.  Approximate both functions by trigonometric polynomials.  Their
Fourier supports are finite, so the preceding uniform coefficient bounds
apply simultaneously to every parameter choice.  Finally, replacing the
threshold \(1\) by \(1-b/h\) changes only a boundary layer of measure
\(o(1)\), uniformly for \(b=1,2\).  Hence the carry-zero proportion tends
uniformly to \(1/6\).

This proves the stated asymptotic count and the eventual absence of literal
natural-modulus holes.  It does not extend to different moduli or to
non-affine reorderings, exactly as stated in Section 7.

## 5. Referee disposition

P63 may be used as a proved sidecar lemma provided the final exposition
retains the split-torus calculation, formula (R1), and an explicit citation
or proof of the uniform tame Betti bound (R2).  Citing *Weil II* alone covers
the weight estimate but not (R2).  With that bibliographic repair, no
load-bearing gap remains in P63.
