# Referee report on P70: uniform carry mixing for the natural Ruzsa lifts

## Verdict

**Valid after the explicit details below are inserted.** I found no
counterexample and no incorrect leading constant. The exact Fourier identity,
the surface count, the fibrewise square-root estimate, the removal of the
four-coordinate exceptional line, the moving-region argument, and the
ordered-to-unordered conversion all check out.

Two load-bearing steps are too compressed in the submitted version:

1. the Kummer--Artin--Schreier estimate needs an explicit geometric
   nontriviality and uniform-conductor check on every fibre; and
2. ordinary Weyl convergence must be upgraded to uniform discrepancy before
   the tetrahedron is allowed to move with \(t/n\).

Both omissions are repairable without changing the theorem. Complete repairs
are given below.

## 1. Exact CRT and Fourier identity

With
\[
 \delta_i=[e(g^i-1)]_p,\qquad
 q_i=[i-\delta_i]_{p-1},\qquad b_i=\delta_i+p q_i,
\]
one has \(b_i\equiv\delta_i\pmod p\) and
\(b_i\equiv\delta_i+q_i\equiv i\pmod {p-1}\). Thus this is the claimed CRT
representative.

For every integer \(m\),
\[
\begin{aligned}
 \exp(2\pi i m b_i/[p(p-1)])
 &=\exp(2\pi i m q_i/(p-1))
   \exp(2\pi i m\delta_i/[p(p-1)])\\
 &=\chi_m(g^i)
   \exp(-2\pi i m\delta_i/(p-1))
   \exp(2\pi i m\delta_i/[p(p-1)])\\
 &=\chi_m(g^i)\exp(-2\pi i m\delta_i/p)\\
 &=\chi_m(g^i)\psi(-me(g^i-1)).
\end{aligned}
\]
The third line uses
\[
 -\frac1{p-1}+\frac1{p(p-1)}=-\frac1p.
\]
The last equality is exact modulo \(p\). Hence (15), including its sign, is
correct.

## 2. Surface equations and \(Q_{e,t}=p^2+O(p)\)

Reduction modulo \(p-1\) gives
\[
 D=g^{a_4}=g^{-H}XYZ=\lambda XYZ.
\]
Reduction modulo \(p\) gives
\[
 e(X+Y+Z-D-2)=T,
\]
hence \(X+Y+Z-D=K=2+T/e\). Equations (9)--(11) are exact.

For \(X,Y\in\mathbb F_p^*\), let
\[
 d(X,Y)=1-\lambda XY,\qquad r(X,Y)=K-X-Y.
\]
If \(d\ne0\), there is one candidate \(Z=r/d\), allowed unless \(r=0\).
The pairs with \(d=0\) or \(r=0\) number \(O(p)\), uniformly in
\(\lambda,K\). If \(d=r=0\), then
\[
 XY=\lambda^{-1},\qquad X+Y=K,
\]
so there are at most two ordered pairs \((X,Y)\), each allowing \(p-1\)
nonzero values of \(Z\). Every other pair with \(d=0\) allows none.
Since \(D=\lambda XYZ\ne0\) automatically,
\[
 Q_{e,t}=(p-1)^2+O(p)=p^2+O(p)
\]
with an absolute uniform constant. No quadratic-size exceptional stratum is
missing.

## 3. Complete fibre classification

After deleting the \(O(p)\) exceptional surface points, fix
\(X\in\mathbb F_p^*\) and write
\[
 Z_X(Y)=\frac{K-X-Y}{1-\lambda XY}.
\]
Apart from an \(X\)-dependent constant phase, the inner trace function is
\[
 \chi_{m_2}(Y)\chi_{m_3}(Z_X(Y))
 \psi(-e f_X(Y)),\qquad
 f_X(Y)=m_2Y+m_3Z_X(Y).
\]

If \(m_2\ne0\pmod p\), the numerator obtained after multiplying by
\(1-\lambda XY\) has quadratic coefficient
\(-m_2\lambda X\ne0\). Since the denominator is linear, \(f_X\) cannot be
constant. It may simplify to a nonconstant linear polynomial, which still has
a simple pole at infinity.

If \(m_2=0\pmod p\) and \(m_3\ne0\pmod p\), the two linear numerator and
denominator are proportional exactly when
\[
 \lambda X(K-X)=1.
\]
This has at most two solutions \(X\). These are exactly the constant
additive-phase fibres.

If \(m_2=m_3=0\) and \(m_1\ne0\), fix \(Y\) and sum first in \(X\). Up to
deleting \(O(1)\) points, the inner sum is
\[
 \sum_X\chi_{m_1}(X)\psi(-em_1X),
\]
a Gauss sum of size at most \(\sqrt p\). For any fixed mode, taking
\(p>\max_i|m_i|\) prevents a nonzero integer coefficient from vanishing
modulo \(p\).

## 4. Repair of the Weil-bound invocation

On each nonexceptional fibre, remove the zeros and poles of
\[
 Y,\qquad K-X-Y,\qquad 1-\lambda XY,
\]
and infinity. There are at most four geometric punctures. The Kummer factors
are tamely ramified only at this bounded set. The Artin--Schreier factor is
defined by the degree-at-most-two rational function \(-ef_X(Y)\).

On every fibre classified above as nonconstant, after cancellation this
rational function has either a finite pole of order one or a pole at infinity
of order one. For sufficiently large \(p\), it cannot equal
\(F^p-F+c\): every pole of a nonconstant \(F^p-F\) has order divisible by
\(p\). Multiplication by \(e\ne0\) does not change pole order. Tame Kummer
monodromy cannot cancel this wild Artin--Schreier monodromy.

The resulting rank-one sheaf on a punctured projective line is therefore
geometrically nontrivial and has conductor bounded by an absolute constant.
Collisions of zeros and poles only lower that conductor. The curve Weil bound
gives
\[
 \left|\sum_Y
 \chi_{m_2}(Y)\chi_{m_3}(Z_X(Y))\psi(-ef_X(Y))\right|
 \le C_m\sqrt p.
\]
For modes in a fixed finite box, one constant works for the whole box. The at
most two constant-phase fibres contribute \(O(p)\) by the trivial bound.
Summing all fibres and restoring the \(O(p)\) deleted points yields
\[
 O_m(p\sqrt p)+O(p)=O_m(p^{3/2})
\]
uniformly in \(e,t\). This supplies the missing rigorous proof of (16),
including cancellations and all exceptional fibres.

## 5. Four-coordinate exceptional modes

For a four-coordinate mode, substitute \(D=X+Y+Z-K\). The additive phase is
constant exactly when
\[
 m_1+m_4=m_2+m_4=m_3+m_4=0,
\]
that is,
\[
 (m_1,m_2,m_3,m_4)=(r,r,r,-r).
\]
On this line the Kummer product is also constant:
\[
 \chi_r(XYZ/D)=\chi_r(\lambda^{-1}).
\]
For fixed integer modes and sufficiently large \(p\), reduction modulo \(p\)
introduces no additional line. Projection to the first three coordinates
sets \(m_4=0\), whose intersection with the exceptional line is only \(r=0\).
Thus no nonzero projected Fourier mode is exceptional. The claim following
(22) is correct.

## 6. Repair of uniform Weyl convergence

For every fixed \(M\), (13) and (16) imply
\[
 \sup_{e,t}\max_{0<\|m\|_\infty\le M}
 |\widehat\mu_{p,e,t}(m)|=O_M(p^{-1/2}).
\]
The three-dimensional Erdos--Turan--Koksma inequality then gives
\[
 \sup_{e,t}D^*(\mu_{p,e,t})
 \le C\left(\frac1M+O_M(p^{-1/2})\right).
\]
First choose \(M\) large, then \(p\) large. Therefore
\[
 \sup_{e,t}D^*(\mu_{p,e,t})\longrightarrow0.
\]

For every \(\theta\in[0,1)\), the boundary of
\[
 \mathcal T_\theta
 =\{u\in[0,1)^3:u_1+u_2+u_3\ge2+\theta\}
\]
is a uniformly bounded union of planar pieces. A grid of mesh \(\eta\)
gives inner and outer unions of axis-parallel boxes whose volume difference is
\(O(\eta)\), uniformly in \(\theta\). Hence
\[
 \sup_{e,t}\left|
 \mu_{p,e,t}(\mathcal T_{t/n})
 -\operatorname{vol}(\mathcal T_{t/n})
 \right|\longrightarrow0.
\]
This proves the needed uniformity for moving \(t/n\); no unsupported
pointwise-to-uniform inference remains.

## 7. Carry region and the factor \(1/2\)

For a modular solution, write
\[
 b_{a_1}+b_{a_2}+b_{a_3}-b_{a_4}=t+kn.
\]
Since \(0\le b_{a_4}<n\),
\[
 k=\left\lfloor
 \frac{b_{a_1}+b_{a_2}+b_{a_3}}n-\frac tn
 \right\rfloor.
\]
The upper inequality for \(k=2\) is automatic since every \(b_{a_i}<n\).
Thus \(k=2\) is exactly \(\mathcal T_{t/n}\). Under \(v_i=1-u_i\), this is
the simplex
\[
 v_1+v_2+v_3\le1-t/n,
\]
of volume \((1-t/n)^3/6\). Boundary equality has zero volume and is covered
by the discrepancy argument. Consequently the ordered top-carry count is
\[
 C_{e,t}=\frac{(1-t/n)^3}{6}p^2+o(p^2)
\]
uniformly in \(e,t\).

Every top-carry solution satisfies
\[
 b_{a_3}-b_{a_4}
 =2n+t-b_{a_1}-b_{a_2}\ge t+2>0,
\]
because \(b_{a_1}+b_{a_2}\le2n-2\). Thus the strict condition \(z>w\) is
automatic.

Off the diagonal \(a_1=a_2\), swapping \(a_1,a_2\) acts freely and exactly
one ordering has \(x<y\). If \(D_{e,t}\) is the number of diagonal top-carry
solutions, then exactly
\[
 C_{e,t}=2(R_{B_e}(t)-D_{e,t})+D_{e,t}
         =2R_{B_e}(t)-D_{e,t}.
\]
On the diagonal, (11) becomes
\[
 (1-\lambda X^2)Z=K-2X.
\]
There is at most one \(Z\) for each \(X\), except when both coefficients
vanish. This occurs for at most two \(X\)'s and contributes at most \(p-1\)
choices each. Hence \(D_{e,t}=O(p)\) uniformly, and
\[
 R_{B_e}(t)
 =\frac12C_{e,t}+O(p)
 =\frac{p^2}{12}(1-t/n)^3+o(p^2).
\]
The diagonal convention, strict difference orientation, and factor \(1/2\)
are all correct.

## 8. Independent exact cross-check

I reran

~~~text
python problems/864/compute/p70/verify_all_cut_records.py \
  problems/864/compute/p30/all_cuts_p257.json \
  problems/864/compute/p70/all_cuts_p263.json \
  problems/864/compute/p70/all_cuts_p269.json \
  problems/864/compute/p70/all_cuts_p271.json \
  problems/864/compute/p70/all_cuts_p277.json \
  problems/864/compute/p70/all_cuts_p281.json \
  problems/864/compute/p70/all_cuts_p283.json \
  problems/864/compute/p70/all_cuts_p293.json
~~~

The verifier exited successfully and exactly rechecked both extremal records
for every listed prime, including integer Sidonicity, positive-difference
uniqueness, diagonal sums, first missing centers, and reflected admissibility.
This is corroborative only; the theorem rests on the analytic argument.

## Final assessment

The first possible analytic gap was the fibrewise sheaf estimate; Section 4
closes it. The next was uniformity for moving \(t/n\); Section 6 closes it.
I therefore accept P70 as a rigorous closure of the natural Ruzsa-lift
construction lane. It does not, and does not claim to, resolve Problem 864.
