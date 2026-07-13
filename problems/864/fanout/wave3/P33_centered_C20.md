# P33: the centered C20 factorization

## Verdict

**PROVED EXACT REDUCTION AND GAP/ONSET COROLLARY; C20 REMAINS OPEN.**

The duplicate-only P23 obstruction does not apply to C20. With the centered
convention \(Z_H=D_H-Q_H\), C20 admits an exact factorization into a linear
gap-defect inequality plus a term of known sign. In particular, put

\[
 G_H:=N+H-1-M_H
\]

for the number of holes in the ambient thickening interval. Define

\[
\begin{aligned}
 \Phi_H={}&6M_H(H^2+2Z_H)-8NH^2-9H^3-9N(k-1)H,\\
 \Psi_H={}&8NZ_H-12H^2G_H+3H^3-12H^2-9N(k-1)H.
\end{aligned}
\]

Then the exact identity is

\[
 \boxed{\Phi_H
 =\Psi_H+2(3M_H-2N)(2Z_H-H^2).}                 \tag{1}
\]

C20 is exactly \(\Phi_H\le0\). Since admissibility gives
\(2Z_H\le H(H-1)<H^2\), (1) proves C20 immediately when
\(3M_H\le2N\), and reduces the remaining case \(3M_H\ge2N\) to the
single sufficient inequality

\[
 \boxed{
 8N(D_H-Q_H)
 \le 12H^2G_H-3H^3+12H^2+9N(k-1)H.}            \tag{LG33}
\]

This reduction is valid for every positive \(H\). The C20 choice
\(H=\lceil N^{2/3}\rceil\) enters only when applying it.

A proved gap-large criterion and the P22 colored onset identity give an
explicit regime in which (LG33), hence C20, holds. What is not proved is
(LG33) for every admissible set in the high-support regime.

## 1. Centered identity

For \(d>0\), let

\[
 \nu_A(d)=|\{(a,b)\in A^2:a-b=d\}|.
\]

Admissibility implies \(\nu_A(d)\in\{0,1,2\}\). For \(1\le d<H\), set

\[
\begin{aligned}
 D_H&=\sum_{\nu_A(d)=2}(H-d),\\
 Q_H&=\sum_{\nu_A(d)=0}(H-d),\\
 W_H&=\sum_{d=1}^{H-1}(H-d)\nu_A(d).
\end{aligned}
\]

The labels with multiplicity zero, one, and two partition
\(\{1,\ldots,H-1\}\). Therefore

\[
 \boxed{
 Z_H=D_H-Q_H
     =W_H-\binom H2,\qquad
 H^2+2Z_H=H+2W_H.}                              \tag{2}
\]

Thus the centered C20 factor is

\[
 1+\frac{2Z_H}{H^2}
 =\frac{H+2W_H}{H^2}.                            \tag{3}
\]

Equation (2) is the point at which the P23 duplicate-only calculation
changes: replacing \(Z_H\) by \(D_H\) discards the entire \(Q_H\) term.

Also \(D_H\le\binom H2\) and \(Q_H\ge0\), so

\[
 2Z_H\le H(H-1)<H^2.                             \tag{4}
\]

No asymptotic estimate is used here.

## 2. Exact tangent-gap factorization

Write

\[
 x=\frac{M_H}{N},\qquad
 y=\frac{2Z_H}{H^2},\qquad
 b=\frac HN+\frac{k-1}{H}.
\]

The C20 excess is

\[
 F=x(1+y)-\frac43-\frac32b.                      \tag{5}
\]

There is an exact tangent identity at the sharp point
\((x,y)=(2/3,1)\):

\[
 \boxed{
 F=\frac23\left(3x+y-3-\frac94b\right)
   +\left(x-\frac23\right)(y-1).}                \tag{6}
\]

Multiplying (6) by \(6NH^2\) gives (1). Indeed,

\[
 6NH^2F=\Phi_H,
\]

while four times \(NH^2\) times the parenthesis in (6) is

\[
\begin{aligned}
 &12M_HH^2+8NZ_H-12NH^2-9H^3-9N(k-1)H\\
 &\quad=8NZ_H-12H^2G_H+3H^3-12H^2-9N(k-1)H\\
 &\quad=\Psi_H,
\end{aligned}
\]

using \(M_H=N+H-1-G_H\). The remaining product in (6) clears to
\(2(3M_H-2N)(2Z_H-H^2)\). This proves (1).

If \(3M_H\le2N\), then (3)-(4) give

\[
 \frac{M_H}{N}\left(1+\frac{2Z_H}{H^2}\right)
 \le\frac23\left(2-\frac1H\right)<\frac43,
\]

so C20 holds without its correction term. If \(3M_H\ge2N\), then the
last term in (1) is nonpositive by (4). Hence

\[
 \Psi_H\le0\quad\Longrightarrow\quad
 \Phi_H\le0,
\]

which is precisely (LG33) implying C20.

## 3. A proved gap-large criterion

The universal centered bound \(Z_H\le H(H-1)/2\) yields

\[
\begin{aligned}
 \Psi_H\le{}&
 4NH(H-1)-12H^2G_H+3H^3-12H^2\\
 &\qquad{}-9N(k-1)H.
\end{aligned}
\]

Consequently the following condition is sufficient for C20:

\[
 \boxed{
 G_H\ge
 \frac{N(H-1)}{3H}+\frac H4-1
 -\frac{3N(k-1)}{4H}.}                         \tag{7}
\]

This is an exact finite statement, with no floor or limiting convention:
multiplying (7) by \(12H^2\) makes the displayed upper bound for
\(\Psi_H\) nonpositive. If \(3M_H\le2N\), the earlier direct argument
applies; otherwise (1) completes the proof.

The remaining condition (LG33) can equivalently be read as the
missing-difference gate

\[
 \boxed{
 Q_H\ge D_H-
 \frac{12H^2G_H-3H^3+12H^2+9N(k-1)H}{8N}.}      \tag{8}
\]

Unlike the withdrawn P23 argument, (8) cannot be checked from duplicate
mass alone.

## 4. Colored onset corollary

Use the P22 notation. Let \(C=A\cap(\sigma-A)\) be the reflected core,
let \(r=|A\setminus C|\), and let \(L_C=\max C-\min C\). P22 proves

\[
 M_H(A)\le L_C+(r+1)H-\Gamma_H,                  \tag{9}
\]

where \(\Gamma_H\) is its colored onset defect: equation (21) in the
no-midpoint case and equation (24) in the midpoint case. Therefore

\[
 \boxed{
 G_H\ge N-1-L_C-rH+\Gamma_H.}                    \tag{10}
\]

Combining (7) and (10) gives the following proved conditional form of C20:

\[
\begin{split}
 N-1-L_C-rH+\Gamma_H
 \ge{}&\frac{N(H-1)}{3H}+\frac H4-1\\
     &-\frac{3N(k-1)}{4H}
 \quad\Longrightarrow\quad \text{C20}.           \tag{11}
\end{split}
\]

In particular, without a midpoint one may use the \(j=2\) onset

\[
 \Gamma_H\ge(u_1+u_2-2H)_+.
\]

This is the exact place where the gap/onset mechanism enters the centered
problem. Large duplicate weight is not itself the gate; either ambient
holes/onset satisfy (11), or missing labels must supply (8).

## 5. Corrected P23 check

For the \(p=503\) P23 construction at
\(H=\lceil N^{2/3}\rceil\), the exact values are

\[
\begin{gathered}
 N=1010022,\quad k=1004,\quad H=10067,\quad M_H=1019964,\\
 D_H=25058720,\quad Q_H=25569511,\quad Z_H=-510791,\\
 G_H=N+H-1-M_H=124.
\end{gathered}
\]

The centered cleared C20 margin is

\[
 \Phi_H=-305894457730641<0.
\]

The duplicate-only substitution would change \(Z_H\) by \(Q_H\), reversing
the conclusion. The small value of \(G_H\) does not cause a failure because
the missing-difference term makes \(Z_H\) negative.

## 6. Exact verification

The scripts in **problems/864/compute/p33/** use integer arithmetic for
every accepted result.

* **audit_centered_c20.py** streams all 1,811,499 P20 profiles. At the 193
  prescribed scales it finds no C20 or (LG33) failure and checks
  \(Z_H=D_H-Q_H\).
* **exhaustive_centered_c20.py** checks all 8,388,607 endpoint-normalized
  subsets for \(2\le N\le24\). Exactly 21,673 are admissible; none
  falsifies C20 or (LG33).
* **reflected_subsets.py** checks all 131,072 reflected pair-deletion subsets
  of the strongest P20 witness. The full set remains the maximizer, with
  required coefficient \(12313/9025\).
* **audit_p30_reflections.py** independently rebuilds the 256 fresh P30
  \(p=257\) reflections, including diagonals and missing differences.
* **ruzsa_fft_centered_search.py** uses GPU convolution only to propose a
  center, then verifies the hole against exact integer sum/difference
  supports and computes literal \(D_H,Q_H,Z_H\). It checks 10 cuts at
  \(p=1009\), 10 cuts at \(p=4001\), and 125 further \(p=4001\) cuts
  \(e=1+32j\). None is a centered C20 falsifier.

These computations verify the algebra and guard against the earlier
convention error. They are not a proof of (LG33).

## 7. Remaining frontier

The exact open lemma exposed by this lane is (LG33) for

\[
 H=\lceil N^{2/3}\rceil,\qquad 3M_H\ge2N.
\]

Equivalently, one must force the missing-difference lower bound (8), or force
enough ambient gap/onset mass through (11). P22's duplicate-only
gap-defect inequality cannot be inserted here with its symbol \(Z_H\):
under the centered convention its duplicate term is \(D_H\), and
\(Q_H\) is an independent, favorable term which must remain in every gate.
