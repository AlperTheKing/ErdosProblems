# P84: phase Fourier identities for the loose-fold frontier

## Verdict

This note does not prove `C_S=o(p^2)` and does not construct an infinite
counterfamily. It gives an exact polynomial formulation of both sides of the
frontier and identifies the missing analytic input.

Put

\[
 P(x)=\sum_{t\in B}x^t,\qquad P^\#(x)=P(x^{-1}),
 \qquad R=PP^\#,
 \qquad Q_b=x^bP^2.
\]

The literal hole is exactly coefficientwise orthogonality of `R` and `Q_b`,
while the weighted fold count is their common lag-`h` autocorrelation:

\[
 [x^{-b}]P^3P^\#=\sum_n [x^n]R\,[x^n]Q_b=0,             \tag{1}
\]

\[
 RR^\#=Q_bQ_b^\#=P^2(P^\#)^2,
 \qquad
 E_h:=[x^h]P^2(P^\#)^2.                                \tag{2}
\]

Here `C_S<=E_h<=4C_S`. Thus (1) and (2) place the problem exactly inside
the P47 equal-modulus pair, but at the distinguished endpoint lag `h`.

There is also an exact tensor formula for loose triangles. Its Fourier form
uses a three-dimensional product of two-frequency slices of a quartic fold
kernel. The hole (1) is only one diagonal quartic average and is not a
factor of that product. Ordinary Holder estimates give only the sharp
`O(p^3)` scale.

An exact finite search found the stronger candidate

\[
                         T_F\le C_S.                    \tag{3}
\]

There are zero failures in all 464,981 positive-defect literal holes of the
complete width-30 P46 domain, in all 134 positive-defect stored P46/P20
rows, and in P75. If (3) were proved, P82.2 would immediately imply
`C_S=o(p^2)`. No injection or analytic proof of (3) is obtained here, so it
is a finite-data conjecture, not a lemma.

## 1. The exact equal-modulus pair

Write

\[
 r_n=[x^n]R,
 \qquad q_n=[x^n]Q_b=[x^{n-b}]P^2.
\]

Every term in `sum_n r_n q_n` is nonnegative. Expanding one term counts
`w-z=n` and `x+y=n-b`, hence

\[
 \sum_n r_nq_n
 =\#\{(x,y,z,w)\in B^4:x+y+z+b=w\}
 =[x^{-b}]P^3P^\#.                                     \tag{4}
\]

Consequently the literal hole is equivalent to disjoint coefficient
supports of `R` and `Q_b`. The identity

\[
 RR^\#=(PP^\#)^2=(x^bP^2)(x^{-b}(P^\#)^2)=Q_bQ_b^\#   \tag{5}
\]

then proves equality of every aperiodic autocorrelation lag. In particular,

\[
 E_h=\sum_n r_{n+h}r_n=\sum_n q_{n+h}q_n.              \tag{6}
\]

The second expression is the ordered shifted-sum count. For one canonical
fold `a+c+h=u+v`, its contribution is

\[
 (2-\mathbf 1_{a=c})(2-\mathbf 1_{u=v})\in\{1,2,4\}.
\]

This proves `C_S<=E_h<=4C_S` exactly.

On the unit circle, write
`P(e^{i\theta})=\rho(\theta)e^{i\phi(\theta)}` away from its zeros.
Equations (1)-(2) become

\[
 0={1\over2\pi}\int_0^{2\pi}
     \rho(\theta)^4e^{i(2\phi(\theta)+b\theta)}\,d\theta,              \tag{7}
\]

\[
 E_h={1\over2\pi}\int_0^{2\pi}
     \rho(\theta)^4e^{-ih\theta}\,d\theta.             \tag{8}
\]

Thus the hole is a zero moment of the nonlinear phase `2 phi+b theta`,
whereas folds are a moment of the linear endpoint phase `-h theta`. Any
successful one-circle estimate must control their joint distribution under
the measure `rho^4 d theta`; either marginal alone loses the needed phase.

## 2. Exact canonical triangle trace

Let `f=1_B`. Define the canonical fold tensor

\[
 F_h(a,c,u)=f(a)f(c)f(u)f(a+c+h-u)
 \mathbf 1_{a\le c<u\le a+c+h-u}.                     \tag{9}
\]

Its three two-coordinate shadows are

\[
 M_{AC}(a,c)=\sum_rF_h(a,c,r),\quad
 M_{AU}(a,u)=\sum_zF_h(a,z,u),\quad
 M_{CU}(c,u)=\sum_xF_h(x,c,u).                         \tag{10}
\]

P82.1 says that all three matrices are zero-one and each has exactly `C_S`
ones. Expanding the shadow-triangle count gives the exact identity

\[
 \boxed{
 C_S+T_F=
 \sum_{a,c,u}M_{AC}(a,c)M_{AU}(a,u)M_{CU}(c,u).}       \tag{11}
\]

Indeed, expanding (10) gives the three folds in P82(8). If all three are
the same, the term is one of the `C_S` canonical triangles; otherwise it is
one loose fold triangle.

The three-function Holder/Finner inequality gives

\[
 C_S+T_F
 \le \|M_{AC}\|_2\|M_{AU}\|_2\|M_{CU}\|_2
 =C_S^{3/2}.                                           \tag{12}
\]

This is sharp for general tripartite shadow data. When `C_S` has positive
quadratic density, (12) is only `O(p^3)`, exactly the scale that P82 needs
to improve to little-oh.

## 3. The quartic fold kernel and its Fourier slices

Dropping the order cut in (9) gives

\[
 K_h(a,c,u)=f(a)f(c)f(u)f(a+c+h-u).                    \tag{13}
\]

Its multivariate generating function is the exact constant term

\[
 \mathcal K_h(X,Y,Z)=\operatorname{CT}_t
 t^hP(Xt)P(Yt)P(Zt^{-1})P(t^{-1}).                    \tag{14}
\]

Define its three marginals as in (10), and let `widetilde Theta_h` be their
triangle contraction as in (11). Every canonical term remains, so

\[
                         C_S+T_F\le\widetilde\Theta_h. \tag{15}
\]

The benefit of (13) is a closed Fourier formula. Take an integer `m>3h`,
embed `[0,h-1]` in `Z_m`, put `e_m(t)=exp(2 pi i t/m)`, and normalize

\[
 \widehat f(\xi)=\sum_xf(x)e_m(-\xi x).
\]

For the three-variable transform use

\[
 \widehat K_h(\alpha,\beta,\gamma)
 =\sum_{a,c,u}K_h(a,c,u)e_m(-\alpha a-\beta c-\gamma u).
\]

There is no modular wrap in (13), and character orthogonality gives

\[
 \widehat K_h(\alpha,\beta,\gamma)
 ={1\over m}\sum_t e_m(th)
 \widehat f(\alpha-t)\widehat f(\beta-t)
 \widehat f(t+\gamma)\widehat f(t).                   \tag{16}
\]

Fourier inversion in the three shared shadow variables gives

\[
 \boxed{
 \widetilde\Theta_h={1\over m^3}
 \sum_{\alpha,\beta,\gamma}
 \widehat K_h(\alpha,\beta,0)
 \widehat K_h(-\alpha,0,\gamma)
 \widehat K_h(0,-\beta,-\gamma).}                    \tag{17}
\]

In the same normalization, the hole is the single diagonal average

\[
 0={1\over m}\sum_t e_m(-bt)
       \widehat f(t)^3\widehat f(-t),                  \tag{18}
\]

and the fold coefficient is the single fourth-moment coefficient

\[
 E_h={1\over m}\sum_t e_m(ht)|\widehat f(t)|^4.       \tag{19}
\]

Equations (17)-(19) isolate the analytic obstruction. The zero in (18)
does not delete any factor in (17): (17) uses three full families of
off-diagonal two-frequency convolutions. Taking absolute values and using
the Sidon fourth moment

\[
 {1\over m}\sum_t|\widehat f(t)|^4=2p^2-p             \tag{20}
\]

recovers Holder-scale bounds, but erases (18). A phase-sensitive completion
must control the joint off-diagonal slices in (17), not only the diagonal
quartic coefficient (18) or the scalar lag (19).

There is a second loss in passing from (11) to (17): the order cut in (9)
is absent. On P75 the exact values are

\[
 [x^{-1}]P^3P^\#=0,\quad C_S=51,\quad E_h=174,
 \quad C_S+T_F=76,
 \quad \widetilde\Theta_h=1296.                       \tag{21}
\]

Thus the unrestricted quartic tensor is already more than seventeen times
the canonical trace on a valid positive-defect hole. A proof through (17)
must either retain the order mask or prove cancellation strong enough to
pay for this enlargement.

## 4. A macroscopic-lag generic obstruction

P47's palindromic family makes the scalar obstruction quantitative. Put

\[
 r=\binom p2,\qquad
 F_p(x)=p+\sum_{-r\le j\le r,\ j\ne0}x^{2j},
 \qquad H_p(x)=xF_p(x).                               \tag{22}
\]

The coefficient supports are disjoint, all coefficients are nonnegative,
`F_p` has the exact profile `p,1^{p(p-1)}`, and `|F_p|=|H_p|` on the whole
unit circle. Nevertheless their common autocorrelation at the macroscopic
lag `2r=p(p-1)` is

\[
 \operatorname{AC}_{F_p}(2r)
 =\operatorname{AC}_{H_p}(2r)
 =r-1+2p={p^2+3p-2\over2}.                            \tag{23}
\]

After a common shift the ambient endpoint is
`4r+1=2p^2-2p+1`. Hence disjoint coefficient supports, equal all-circle
modulus, all common autocorrelation identities, palindromicity, and the
exact first coefficient profile do not imply a subquadratic distinguished
lag.

This is an analytic barrier, not a reflected-ruler counterfamily. The pair
in (22) does not retain the `1^p,2^{binom(p,2)}` profile of `x^bP^2`, the
common Sidon Newman factor, or the pointwise positivity
`R(e^{i\theta})=|P(e^{i\theta})|^2`. Those are precisely the structures a
successful phase inequality must still use.

## 5. The finite `T_F<=C_S` candidate

The identity (11) suggests a much stronger possible endpoint theorem:

\[
 \tag{C84}
 T_F(B,h)\le C_S(B,h)
 \quad\text{for every endpoint fold system.}
\]

If C84 holds, then `T_F<=p(p+1)/2=O(p^2)`. If the uniform little-oh claim
for `C_S` failed, P82.2 would instead give `T_F>=eta p^3` along a sequence,
a contradiction. Thus C84 would close the reflected-center fold frontier
without a quantitative removal bound.

The exact checks are:

* all 464,981 positive-defect literal holes with ruler width at most 30:
  zero failures; only 1,037 rows have `T_F>0`, and the maximum ratio is
  `T_F/C_S=1/2`, at `B={3,11,14,23,27,28}`, `h=29`, `b=1`;
* all 134 positive-defect stored P46/P20 rows: zero failures; the largest
  triangle count is `(C_S,T_F)=(256,144)` at
  `singer-e82f2d6a63ca`, while the largest ratio is `80/141` at
  `singer-natural-fb93340eb02a`;
* P75: `(C_S,T_F)=(51,25)`.

This census does not prove C84. The generic Finner bound (12) permits many
more triangles, and no injection from loose triangles to canonical folds is
known. C84 is therefore a concrete combinatorial continuation exposed by
the Fourier attack, not an accepted bridge.

## 6. Reproduction and claim boundary

All computational decisions use integer arithmetic. Run

```powershell
python -m py_compile problems/864/compute/p84/audit_phase_fourier.py
python -B problems/864/compute/p84/audit_phase_fourier.py
python -m py_compile problems/864/compute/p84/search_triangle_bound.py
python -B problems/864/compute/p84/search_triangle_bound.py `
  --max-width 30 `
  --output problems/864/compute/p84/triangle_bound_w30.json
```

The proved outputs of P84 are (1)-(20), the exact P75 values (21), and the
generic macroscopic-lag obstruction (23). The width-30 and stored-row data
support C84 but do not establish it. No `o(p^3)` joint estimate and no
infinite admissible counterfamily is claimed.
