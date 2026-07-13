# P27: Singer tetrahedral completion and STM

Status: **proved, conditional only on P29's stated Katz theorem**.  The
hypergeometric factor ledger in P29 is correctly normalized.  The zero-wrap
integer tetrahedron has normalized Fourier-algebra norm

\[
 \|W_d\|_{A(\mathbb Z_v^3)}
 :=\frac1{v^3}\sum_{r,s,t\pmod v}|\widehat W_d(r,s,t)|
 \ll \log^3(2v)                                             \tag{1}
\]

uniformly for \(1\le d<v\).  This includes all coincident-frequency
strata.  Combining (1) with P29's bound (21a) proves STM with \(K=3\), in
fact uniformly over the full range \(1\le d<v\).

## 1. Independent audit of P29's normalization

Put \(Q=q^3\), \(v=(Q-1)/(q-1)=q^2+q+1\), and let
\(K=\mathbb F_Q\).  Let \(X_0\) be the \(v\) multiplicative characters of
\(K^*\) trivial on \(\mathbb F_q^*\).  With P29's conventions,

\[
 \chi_j(\alpha)=e_v(-j),\qquad
 F(j)=\widehat{1_D}(j)=\frac{g(\chi_j)}q\quad(j\ne0).        \tag{2}
\]

The denominator in (2) is exactly \(q\).  Indeed, additive orthogonality
gives

\[
\begin{aligned}
 (q-1)F(j)
 &=\sum_{\substack{x\in K^*\\ \operatorname{Tr}(x)=0}}\chi_j(x)\\
 &=\frac1q\sum_{b\in\mathbb F_q}
       \sum_{x\in K^*}\chi_j(x)\Psi(bx)
 =\frac{q-1}{q}g(\chi_j).
\end{aligned}                                               \tag{3}
\]

The \(b=0\) term vanishes and the other \(q-1\) terms are equal because
\(\chi_j\) is trivial on \(\mathbb F_q^*\).

For nonzero output frequencies let \(A=\chi_r\), \(B=\chi_s\),
\(C=\chi_t\).  The ordinary-Gauss model is therefore

\[
 M=\frac1{vq^4}\sum_{\chi\in X_0}
 g(\chi)g(A\chi^{-1})g(B\chi^{-1})g(C\chi^{-1})
 \chi(\alpha^d).                                          \tag{4}
\]

There is one factor \(q^{-1}\) for each of the four Singer coefficients
and one Fourier-inversion factor \(v^{-1}\).

To audit the hypergeometric scale, extend the sum to all multiplicative
characters \(X\) of \(K^*\):

\[
 S(z)=\sum_{\chi\in X}
 g(\chi)g(A\chi^{-1})g(B\chi^{-1})g(C\chi^{-1})\chi(z).
                                                               \tag{5}
\]

Expanding the four Gauss sums and using character orthogonality gives the
exact identity

\[
 S(z)=(Q-1)H(z),                                           \tag{6}
\]

where

\[
 H(z)=
 \sum_{\substack{x_0,x_1,x_2,x_3\in K^*\\
                  z x_0=x_1x_2x_3}}
 A(x_1)B(x_2)C(x_3)\Psi(x_0+x_1+x_2+x_3).                 \tag{7}
\]

Thus \(Q-1\) occurs once, from multiplicative-character orthogonality.
Under Katz's Mellin convention, \(Q^{-3/2}H(z)\), up to a unit phase and
the harmless change \(z\mapsto-z^{-1}\), is the trace of the normalized
type-\((1,3)\) hypergeometric sheaf.  Replacing \(\chi\) by \(\chi^{-1}\)
interchanges the labels \((1,3)\) and \((3,1)\); this convention change
does not alter rank, weight, or scale.  Since \(1,A,B,C\) have no
cross-side cancellation when \(r,s,t\ne0\), the sheaf has rank \(3\) and
P29's cited Katz-Deligne theorem gives

\[
 |H(z)|\le3Q^{3/2},\qquad
 |S(z)|\le3(Q-1)Q^{3/2}.                                  \tag{8}
\]

Repeated characters among \(A,B,C\) remain on the same side of the
hypergeometric datum and cause no cancellation.

Finally,

\[
 1_{\chi\in X_0}=\frac1{q-1}\sum_{b\in\mathbb F_q^*}\chi(b),            \tag{9}
\]

so restricting (5) to \(X_0\) is an average, not an additional factor of
\(q-1\).  Equations (4), (8), and (9) give

\[
\begin{aligned}
 |M|
 &\le \frac{3(Q-1)Q^{3/2}}{vq^4}\\
 &=3(q-1)\sqrt q.                                         \tag{10}
\end{aligned}
\]

This checks every potentially ambiguous factor:

\[
 F(j):q^{-1},\quad
 \text{four factors}:q^{-4},\quad
 \text{DFT}:v^{-1},\quad
 S/H:Q-1,\quad
 H\text{ scale}:Q^{3/2},\quad
 X_0\text{ projection}:1.                                \tag{11}
\]

The exceptional summation indices are exactly the distinct elements of
\(\{0,r,s,t\}\).  Restoring \(F(0)=q+1\) in place of \(q^{-1}g(1)\) is
therefore still divided by \(v\); P29's correction \(9q^{3/2}\) has no
missing factor.  If an output frequency is zero, the flatness identity
\(|F(k)|^2=q+v1_{k=0}\) gives directly

\[
 \widehat G_d(0,s,t)=qQ_{s,t}(d)+F(s)F(t),\qquad
 |Q_{s,t}(d)|\le2,                                       \tag{12}
\]

so the zero-frequency treatment is also normalized correctly.  The audit
therefore finds no normalization obstruction to P29's
\(12q^{3/2}\) bound.

## 2. Exact wrap decomposition

Represent every element of \(\mathbb Z_v\) by its integer in
\(\{0,\ldots,v-1\}\), denoted \([x]\).  For \(1\le d<v\), define

\[
 W_{d,j}(x,y,z)
 =1_{\{jv\le [x]+[y]+[z]<jv+d\}},\qquad j=0,1,2.           \tag{13}
\]

Since \(0\le[x]+[y]+[z]\le3v-3\), reduction modulo \(v\) gives the
pointwise, disjoint identity

\[
 1_{\{[x+y+z]<d\}}
 =W_{d,0}(x,y,z)+W_{d,1}(x,y,z)+W_{d,2}(x,y,z).            \tag{14}
\]

The integer tetrahedron in P26 is exactly the zero-wrap lane

\[
 W_d:=W_{d,0}
 =1_{\{[x]+[y]+[z]<d\}}.                                  \tag{15}
\]

Thus (14) identifies all cyclic aliases, while (15) isolates the required
lane before Fourier inversion.  No cyclic interval kernel is being
silently substituted for the integer tetrahedron.

## 3. Fourier-algebra norm of the zero-wrap tetrahedron

Use

\[
 \widehat W_d(r,s,t)
 =\sum_{x,y,z\pmod v}W_d(x,y,z)e_v(-rx-sy-tz).             \tag{16}
\]

### Proposition 1

There is an absolute constant \(C\) such that, for every odd \(v\ge3\) and
every \(1\le d<v\),

\[
 \frac1{v^3}\sum_{r,s,t\pmod v}|\widehat W_d(r,s,t)|
 \le C\log^3(2v).                                         \tag{17}
\]

#### Proof

Put \(\omega=e_v(-1)\), \(m=d-1\), and

\[
 \lambda_0=1,\quad\lambda_1=\omega^r,\quad
 \lambda_2=\omega^s,\quad\lambda_3=\omega^t.
\]

Adding the slack variable \(u=m-x-y-z\) gives the exact kernel

\[
\begin{aligned}
 \widehat W_d(r,s,t)
 &=\sum_{x+y+z\le m}\lambda_1^x\lambda_2^y\lambda_3^z\\
 &=h_m(\lambda_0,\lambda_1,\lambda_2,\lambda_3),           \tag{18}
\end{aligned}
\]

where \(h_m\) is the complete homogeneous polynomial.  Equivalently, with
\(\phi(z)=z^{m+3}=z^{d+2}\), (18) is the third divided difference

\[
 \phi[\lambda_0,\lambda_1,\lambda_2,\lambda_3].            \tag{19}
\]

Repeated nodes in (19) are Hermite divided differences.  This is the
mechanism that handles coincident frequencies.

For \(u\ne0\pmod v\), set

\[
 D(u)=|1-\omega^u|^{-1},\qquad
 H_j=\sum_{u\ne0}D(u)^j.
\]

Writing \(\|u\|_v=\min([u],v-[u])\), the elementary inequality
\(\sin x\ge2x/\pi\) on \([0,\pi/2]\) gives

\[
 D(u)\le\frac{v}{4\|u\|_v}.                               \tag{20}
\]

Consequently

\[
\begin{aligned}
 H_1&\le\frac v2(1+\log v),\\
 H_2&\le\frac{\pi^2}{48}v^2,\\
 H_3&\le\frac{\zeta(3)}{32}v^3.                           \tag{21}
\end{aligned}
\]

We now sum (19) over the five multiplicity partitions of the frequency
multiset \(\{0,r,s,t\}\).  Put \(n=d+2\le v+1\).

**Four distinct nodes, \(1+1+1+1\).**  The ordinary divided-difference
formula is

\[
 \widehat W_d(r,s,t)
 =\sum_{i=0}^3
   \frac{\lambda_i^n}{\prod_{j\ne i}(\lambda_i-\lambda_j)}.            \tag{22}
\]

For the \(i=0\) term, summing the absolute denominator gives at most
\(H_1^3\).  For the \(i=1\) term it gives

\[
 \sum_{r,s,t}D(r)D(r-s)D(r-t)\le H_1^3,                 \tag{23}
\]

and similarly for \(i=2,3\).  Hence this stratum contributes at most
\(4H_1^3=O(v^3\log^3(2v))\).

**One double node, \(2+1+1\).**  Write the nodes as \(a,a,b,c\), all three
displayed values distinct.  Confluence in (22) gives the exact formula

\[
\begin{aligned}
 \phi[a,a,b,c]
 &=
 \left.\frac{d}{dz}
   \frac{\phi(z)}{(z-b)(z-c)}\right|_{z=a}\\
 &\quad+\frac{\phi(b)}{(b-a)^2(b-c)}
       +\frac{\phi(c)}{(c-a)^2(c-b)}.                    \tag{24}
\end{aligned}
\]

If

\[
 A=|a-b|^{-1},\quad B=|a-c|^{-1},\quad C=|b-c|^{-1},
\]

then

\[
 |\phi[a,a,b,c]|
 \le nAB+A^2B+AB^2+A^2C+B^2C.                            \tag{25}
\]

Either the repeated node is \(1\), or one singleton is \(1\).  There are
only constantly many assignments to the labelled slots
\((0,r,s,t)\).  In both cases, summing two independent chord differences
and dropping distinctness restrictions bounds (25) by

\[
 O(nH_1^2+H_1H_2)
 =O(v^3\log^2(2v)).                                      \tag{26}
\]

For example,
\(\sum_{u,w}D(u)^2D(w)\le H_2H_1\) and
\(\sum_{u,w}D(u)^2D(u-w)\le H_2H_1\); these cover every
cubic-denominator term in (25).

**Two double nodes, \(2+2\).**  The nodes must be \(1,1,a,a\), up to
labelling.  Hermite confluence gives

\[
 \phi[a,a,b,b]
 =
 \left.\frac{d}{dz}\frac{\phi(z)}{(z-b)^2}\right|_{z=a}
 +\left.\frac{d}{dz}\frac{\phi(z)}{(z-a)^2}\right|_{z=b}.               \tag{27}
\]

With \(D=|a-b|^{-1}\),

\[
 |\phi[a,a,b,b]|\le2nD^2+4D^3.                           \tag{28}
\]

There is one free nonzero frequency, so this stratum sums to

\[
 O(nH_2+H_3)=O(v^3).                                     \tag{29}
\]

**One triple node, \(3+1\).**  For nodes \(a,a,a,b\),

\[
 \phi[a,a,a,b]
 =\left.\frac12\frac{d^2}{dz^2}
       \frac{\phi(z)}{z-b}\right|_{z=a}
  +\frac{\phi(b)}{(b-a)^3}.                              \tag{30}
\]

Thus

\[
 |\phi[a,a,a,b]|
 \le\frac{n(n-1)}2D+nD^2+2D^3.                           \tag{31}
\]

The possibilities are \(1,1,1,a\) and \(1,a,a,a\), with constantly many
labellings.  Their total is

\[
 O(n^2H_1+nH_2+H_3)=O(v^3\log(2v)).                      \tag{32}
\]

**Four equal nodes, \(4\).**  This is only \((r,s,t)=(0,0,0)\), and

\[
 \widehat W_d(0,0,0)=h_m(1,1,1,1)=\binom{d+2}{3}=O(v^3). \tag{33}
\]

Adding (22)-(33) proves

\[
 \sum_{r,s,t}|\widehat W_d(r,s,t)|
 =O(v^3\log^3(2v)),
\]

which is (17).  The constants in (20)-(33) do not depend on \(d\).
\(\square\)

The completion cost in (17) is therefore proved directly.  In particular,
it is not inferred from a one-dimensional interval kernel, and no
independent-sign estimate is used at frequency collisions.

## 4. Passage from (21a) to STM

Let \(C\subset\mathbb Z_v\) be any affine Singer set represented in
\(\{0,\ldots,v-1\}\), let \(f=1_C\), and put

\[
 G_d(x,y,z)=f(x)f(y)f(z)f(x+y+z-d\pmod v).                \tag{34}
\]

On the support of \(W_d\), the last argument has canonical representative
\(v-d+x+y+z\).  Hence P26's ordered witness count is exactly

\[
\begin{aligned}
 E_C^{\rm ord}(d)
 &=\sum_{x+y+z<d}f(x)f(y)f(z)f(v-d+x+y+z)\\
 &=\sum_{x,y,z\pmod v}G_d(x,y,z)W_d(x,y,z).               \tag{35}
\end{aligned}
\]

Three-dimensional Fourier inversion gives

\[
 E_C^{\rm ord}(d)
 =\frac1{v^3}\sum_{r,s,t}
   \widehat G_d(r,s,t)\overline{\widehat W_d(r,s,t)}.      \tag{36}
\]

Let

\[
 m_C(d)=\#\{(x,y)\in C^2:x+y=d\pmod v\}.
\]

Strong modular Sidonicity gives \(m_C(d)\le2\).  Taking
\((s,t)=(0,0)\) in (12) yields the exact zero coefficient

\[
 \widehat G_d(0,0,0)=p^2+qm_C(d),\qquad p=q+1.             \tag{37}
\]

Since \(p^2=v+q\),

\[
 \widehat G_d(0,0,0)-\frac{p^4}{v}
 =q\left(m_C(d)-\frac{p^2}{v}\right)=O(q).                \tag{38}
\]

Using (33), the zero-frequency term in (36) is therefore

\[
 \rho^4\binom{d+2}{3}+O(q),\qquad \rho=\frac pv.           \tag{39}
\]

For every nonzero frequency triple, P29 gives
\(|\widehat G_d(r,s,t)|\le12q^{3/2}\).  Proposition 1 now gives

\[
\begin{aligned}
 \left|
 \frac1{v^3}\sum_{(r,s,t)\ne(0,0,0)}
 \widehat G_d(r,s,t)\overline{\widehat W_d(r,s,t)}
 \right|
 &\le12q^{3/2}\|W_d\|_A\\
 &\ll q^{3/2}\log^3(2v).                                  \tag{40}
\end{aligned}
\]

Thus, uniformly for \(1\le d<v\),

\[
 E_C^{\rm ord}(d)
 =\rho^4\binom{d+2}{3}
  +O(q^{3/2}\log^3(2v)).                                  \tag{41}
\]

It remains to restore unordered pairs.  Let \(T_{\rm diag}(d)\) be (35)
with the first two variables equal.  The ambient number of such lattice
points is

\[
 N_{\rm diag}(d)
 =\#\{(a,z)\in\mathbb Z_{\ge0}^2:2a+z<d\}
 =\left\lfloor\frac{(d+1)^2}{4}\right\rfloor.              \tag{42}
\]

The actual diagonal is only \(O(q)\).  For each \(a\in C\) with \(2a<d\),
the remaining two Singer elements must satisfy

\[
 \gamma-\delta=v-d+2a\pmod v,                             \tag{43}
\]

and the residue on the right lies in \(\{1,\ldots,v-1\}\).  The perfect
difference property supplies at most one ordered pair
\((\gamma,\delta)\).  Therefore

\[
 0\le T_{\rm diag}(d)\le p.                               \tag{44}
\]

Also

\[
 0\le\rho^3N_{\rm diag}(d)\le\frac{p^3}{4v}=O(q).          \tag{45}
\]

Since

\[
 E_C(d)=\frac{E_C^{\rm ord}(d)+T_{\rm diag}(d)}2,          \tag{46}
\]

equations (41)-(46) prove the following.

### Theorem 2 (STM with a proved completion cost)

For every prime power \(q\), every affine Singer cut \(C\), and every
\(1\le d<v\),

\[
\boxed{
 E_C(d)=
 \frac{\rho^4}{2}\binom{d+2}{3}
 +\frac{\rho^3}{2}\left\lfloor\frac{(d+1)^2}{4}\right\rfloor
 +O\!\left(q^{3/2}\log^3(2v)\right).
 }                                                        \tag{47}
\]

The implied constant is absolute.  Since \(\log(2v)=O(\log q)\), (47) is
STM with \(K=3\).

For fixed \(\epsilon>0\) and \(d\ge\epsilon v\), the first main term alone
satisfies

\[
 \frac{\rho^4}{2}\binom{d+2}{3}
 \ge\frac{\epsilon^3p^4}{12v}
 =\Omega_\epsilon(q^2).                                  \tag{48}
\]

This dominates the error in (47).  Hence every cut and every
\(d\in[\epsilon v,(1-\epsilon)v]\) has \(E_C(d)>0\) for all sufficiently
large \(q\).  This proves the uniform theorem posed in P27.

## 5. Independent finite audit

The script

    problems/864/compute/p27/audit_tetrahedron_wiener.py

checks only the Fourier-completion argument; it does not rerun the carry
audit.  It verified:

1. the three-lane wrap identity (14) in 15,868 pointwise cases;
2. (18) against a direct three-dimensional FFT in 15,368 cases, with
   maximum residual \(2.15\cdot10^{-13}\);
3. the distinct formula (22) and all three Hermite formulas
   (24), (27), and (30), over 73,984 cases in total; and
4. the coincidence masks as an exact partition of frequency space.

For \(d=\lfloor3v/4\rfloor\), the measured normalized Wiener norms were

\[
\begin{array}{c|c|ccccc}
v&\|W_d\|_A&4&3+1&2+2&2+1+1&1+1+1+1\\ \hline
17& 7.1018&.0741&1.1128&.3131&4.2044&1.3974\\
31&10.7357&.0772&1.3732&.3206&6.2193&2.7454\\
61&15.8069&.0714&1.5465&.3057&8.6301&5.2531\\
101&20.5503&.0710&1.7217&.3042&10.7874&7.6660
\end{array}
\]

The output is stored in

    problems/864/compute/p27/tetrahedron_wiener_audit.json.

These computations audit identities and normalizations only.  The uniform
polylogarithmic estimate is Proposition 1, and the asymptotic conclusion is
Theorem 2.
