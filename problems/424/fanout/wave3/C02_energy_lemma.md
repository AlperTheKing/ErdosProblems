# C02: quantified variable-scale energy lemma for the cross-colour channel

## Verdict

The energy reduction is rigorous, but the available closure facts do not
verify its asymptotic hypothesis. In particular, the finite observation

\[
E_\times(U,V)/(|U||V|)\mathrel{\approx}1
\]

does not by itself give density. The density-scale normalization also contains
the pair-mass factor \(|U||V|/(YZ)\), and the diagonal part of the energy makes
that factor unavoidable.

Below, (P) is the sharp packed criterion, (A) is its canonical annular form,
and (U) is a clean stronger inequality which would settle the problem. No
proof of (A) or (U) is claimed.

## 1. Closure facts and the cross-colour channel

Write

\[
G_i=\{g\in G:g\equiv i\pmod 3\},\qquad
G_i(N)=|G_i\cap[1,N]|.
\]

The set of residues \(\{0,2\}\pmod 3\) contains the seeds and is closed under
\((x,y)\mapsto xy-1\): the three possible product residues give
\(0\cdot0-1\equiv2\), \(0\cdot2-1\equiv2\), and
\(2\cdot2-1\equiv0\). Hence

\[
G=G_0\mathbin{\dot\cup}G_2.                                      \tag{1}
\]

If \(u\in G_0\) and \(v\in G_2\), then \(u\ne v\) automatically. Thus the
distinct-value rule licenses the operation, and

\[
uv-1\in G_2,\qquad G_0G_2-1\subseteq G_2.                         \tag{2}
\]

Put \(P=G_0G_2\). Translation by \(-1\) is injective, and its image in (2)
is disjoint from \(G_0\). Therefore, for every \(N\ge1\),

\[
|G\cap[1,N]|\ge G_0(N)+|P\cap[2,N+1]|.                            \tag{3}
\]

In particular,

\[
\underline d(G)\ge \underline d(G_0)+\underline d(P).            \tag{4}
\]

There is no factor \(1/9\) in (3)-(4).

## 2. Exact energy normalization

It is useful first to allow a finite relation
\(\mathcal R\subseteq G_0\times G_2\), not necessarily a full Cartesian
product. Define

\[
r_{\mathcal R}(n)=|\{(u,v)\in\mathcal R:uv=n\}|,
\quad M(\mathcal R)=|\mathcal R|,
\quad E_\times(\mathcal R)=\sum_n r_{\mathcal R}(n)^2.             \tag{5}
\]

For Cartesian reservoirs \(\mathcal R=U\times V\), abbreviate these as
\(M=|U||V|\) and \(E_\times(U,V)\). The energy counts ordered quadruples
\((u,v,u',v')\) satisfying \(uv=u'v'\).

Let \(\operatorname{supp}(\mathcal R)=\{uv:(u,v)\in\mathcal R\}\). Then
Cauchy--Schwarz gives exactly

\[
M(\mathcal R)^2
=\left(\sum_n r_{\mathcal R}(n)\right)^2
\le |\operatorname{supp}(\mathcal R)|E_\times(\mathcal R),
\]

so

\[
|\operatorname{supp}(\mathcal R)|
\ge \frac{M(\mathcal R)^2}{E_\times(\mathcal R)}.                 \tag{6}
\]

The representation-diagonal terms
\((u,v)=(u',v')\) contribute exactly \(M(\mathcal R)\), whence

\[
E_\times(\mathcal R)\ge M(\mathcal R).                            \tag{7}
\]

This energy diagonal is not the forbidden closure diagonal \(u=v\). The
latter never occurs in \(G_0\times G_2\). Also, there is no automatic second
representation \((v,u)\): the coloured orientation requires the first
coordinate to lie in \(G_0\) and the second in \(G_2\).

For later comparison, let

\[
D(X)=\max_{1\le n\le X}\tau(n).
\]

If every product in \(\mathcal R\) is at most \(X\), then
\(r_{\mathcal R}(n)\le\tau(n)\), and hence

\[
E_\times(\mathcal R)
\le D(X)\sum_n r_{\mathcal R}(n)
=D(X)M(\mathcal R).                                               \tag{8}
\]

Thus divisor multiplicity always gives (6) with lower bound \(M/D(X)\).
The classical bound \(D(X)=X^{o(1)}\) controls collisions only
subpolynomially; it does not supply the linear pair mass needed below.

## 3. Master packed-energy lemma

**Lemma (variable-scale packed energy).** For every sufficiently large
integer \(N\), suppose there are a finite index set \(J_N\), nonempty finite
reservoirs

\[
U_{N,j}\subseteq G_0,\qquad V_{N,j}\subseteq G_2\quad(j\in J_N),
\]

and pairwise disjoint integer sets

\[
I_{N,j}\subseteq[2,N+1]
\]

such that \(U_{N,j}V_{N,j}\subseteq I_{N,j}\). Put

\[
M_{N,j}=|U_{N,j}||V_{N,j}|,
\quad E_{N,j}=E_\times(U_{N,j},V_{N,j}),
\quad Q_N=\sum_{j\in J_N}\frac{M_{N,j}^2}{E_{N,j}}.               \tag{9}
\]

Then

\[
|G\cap[1,N]|\ge G_0(N)+Q_N                                      \tag{10}
\]

and consequently

\[
\underline d(G)
\ge \underline d(G_0)+\liminf_{N\to\infty}\frac{Q_N}{N}.         \tag{P}
\]

In particular, a sufficient condition for positive lower density is

\[
\liminf_{N\to\infty}\frac1N
\sum_{j\in J_N}
\frac{|U_{N,j}|^2|V_{N,j}|^2}
     {E_\times(U_{N,j},V_{N,j})}>0.                               \tag{11}
\]

**Proof.** Equation (6) gives at least \(M_{N,j}^2/E_{N,j}\) distinct
products in \(I_{N,j}\). The sets \(I_{N,j}\) are disjoint, so these lower
bounds may be summed. Translating every product by \(-1\) gives distinct
members of \(G_2\cap[1,N]\), by (2), and these do not overlap
\(G_0\cap[1,N]\). This proves (10). Divide by \(N\) and take liminf. QED.

The same proof works for relations
\(\mathcal R_{N,j}\subseteq G_0\times G_2\) whose product supports lie in
the disjoint sets \(I_{N,j}\). This relation form permits a Cartesian
rectangle to be sliced by actual product range before applying energy.

### Interval-normalized form

Let \(L_{N,j}=|I_{N,j}|\). If

\[
E_{N,j}\le
\kappa_{N,j}\frac{M_{N,j}^2}{L_{N,j}},                            \tag{12}
\]

then its contribution to (9) is at least \(L_{N,j}/\kappa_{N,j}\).
Thus the exact weighted sufficient condition is

\[
\liminf_{N\to\infty}\frac1N
\sum_{j\in J_N}\frac{L_{N,j}}{\kappa_{N,j}}>0.                   \tag{13}
\]

For example, fixed constants \(K<\infty\), \(\eta>0\), together with

\[
\kappa_{N,j}\le K\quad(j\in J_N),
\qquad
\sum_{j\in J_N}L_{N,j}\ge(\eta-o(1))N                           \tag{14}
\]

for every sufficiently large \(N\), imply
\(\underline d(G)\ge\underline d(G_0)+\eta/K\). Any \(o(1)\) used in
the second part of (14) is taken as \(N\to\infty\). If the first part is
instead stated as \(\kappa_{N,j}\le K+o(1)\), that error must be uniform in
\(j\), or the exceptional blocks must have total \(L_{N,j}=o(N)\).

### Near-diagonal-energy plus pair-mass form

Define

\[
\lambda_{N,j}=\frac{E_{N,j}}{M_{N,j}}\ge1.                        \tag{15}
\]

Then the contribution in (9) is \(M_{N,j}/\lambda_{N,j}\). Hence a
frequently more useful sufficient pair of estimates is

\[
\lambda_{N,j}\le K\quad(j\in J_N),
\qquad
\sum_{j\in J_N}M_{N,j}\ge(\mu-o(1))N,                            \tag{16}
\]

uniformly for all large \(N\). It gives
\(\underline d(G)\ge\underline d(G_0)+\mu/K\). Conversely, (7) shows
that any successful packed certificate necessarily has

\[
\sum_{j\in J_N}M_{N,j}\ge Q_N.                                  \tag{17}
\]

Thus collision control cannot compensate for sublinear total pair supply.

## 4. Dyadic rectangles, product ranges, and scale gaps

Take positive reals \(Y_j,Z_j\), put \(S_j=Y_jZ_j\), and suppose

\[
U_j\subseteq G_0\cap(Y_j/2,Y_j],
\qquad
V_j\subseteq G_2\cap(Z_j/2,Z_j].                                 \tag{18}
\]

Then the exact product and output ranges are

\[
U_jV_j\subseteq(S_j/4,S_j],\qquad
U_jV_j-1\subseteq(S_j/4-1,S_j-1].                                \tag{19}
\]

To count the outputs below \(N\), it is enough that \(S_j\le N+1\).
Define the normalization used by `claude_rc_energy_probe.py`:

\[
\kappa_j
=\frac{E_\times(U_j,V_j)S_j}{|U_j|^2|V_j|^2}.                    \tag{20}
\]

Equations (6) and (20) give \(|U_jV_j|\ge S_j/\kappa_j\), not merely
an unscaled \(1/\kappa_j\). If the bands \((S_j/4,S_j]\) are pairwise
disjoint, (P) becomes

\[
\underline d(G)\ge\underline d(G_0)+
\liminf_{N\to\infty}\frac1N
\sum_{\substack{j:S_j\le N+1}}
\frac{S_j}{\kappa_j}.                                            \tag{21}
\]

For increasing scales, the bands in (19) are disjoint whenever

\[
S_{j+1}\ge4S_j.                                                   \tag{22}
\]

Equality is allowed because the lower endpoint in (19) is open.

There are two independent lower bounds on (20). Let

\[
H(S)=|3\mathbb N\cap(S/4,S]|=S/4+O(1).
\]

All cross-colour products are multiples of \(3\), so (6)-(7) imply

\[
\kappa_j\ge
\max\left\{\frac{S_j}{|U_j||V_j|},\frac{S_j}{H(S_j)}\right\}
=\max\left\{\frac{S_j}{|U_j||V_j|},4+O(S_j^{-1})\right\}.        \tag{23}
\]

In particular, a uniform bound \(\kappa_j\le K\) forces

\[
|U_j||V_j|\ge S_j/K,
\quad
\frac{|U_j|}{Y_j}\frac{|V_j|}{Z_j}\ge1/K.                       \tag{24}
\]

This is the diagonal barrier: bounded density-scale energy already demands
positive-proportion occupancy in both chosen factor windows. The empirical
quantity \(E/(|U||V|)\) tests \(\lambda_j\), not (24).

### A fixed lacunary family

Suppose a fixed infinite family satisfies

\[
4\le S_{j+1}/S_j\le R<\infty,\qquad \kappa_j\le K<\infty         \tag{25}
\]

for all sufficiently large \(j\). Then (22) prevents overlap. If
\(S_j-1\le N<S_{j+1}-1\), all outputs from block \(j\) have appeared and

\[
\frac{|G\cap[1,N]|}{N}\ge\frac{S_j}{K N}\ge\frac1{KR}+o(1).
\]

Therefore

\[
\underline d(G)\ge1/(KR).                                       \tag{26}
\]

The exact sum in (21) can improve this constant. The upper ratio bound in
(25) is essential: bounded \(\kappa_j\) on a sequence with
\(S_{j+1}/S_j\to\infty\) gives no positive lower density between scales.

More generally, if certificates at cutoffs \(N_j\) give
\(Q_{N_j}\ge\delta N_j\) and \(N_{j+1}/N_j\le R\), monotonicity gives
\(\underline d(G)\ge\delta/R\). No overlap condition between different
certificates is needed in this checkpoint argument, because certificates
from different cutoffs are not being summed. Without bounded multiplicative
gaps, a subsequence estimate controls at most upper density.

### What fails when product bands overlap

Disjointness of the factor reservoirs is neither necessary nor sufficient
for adding their Cauchy--Schwarz bounds. What must be disjoint is the set of
products being counted. If product bands overlap, set

\[
r(n)=\sum_j r_j(n).
\]

The relevant pooled energy is

\[
\sum_n r(n)^2
=\sum_jE_j+2\sum_{i<j}\sum_n r_i(n)r_j(n),                       \tag{27}
\]

which contains cross-scale collision terms. One must either bound (27),
select a disjoint subfamily, or slice the pair relations into disjoint product
ranges. Simply summing \(M_j^2/E_j\) in the presence of overlapping product
supports is invalid.

## 5. Canonical annular criterion and the exact missing inequality

For \(k\ge1\), let

\[
I_k=(2^{k-1},2^k]\cap\mathbb N,
\quad
\mathcal R_k=\{(u,v)\in G_0\times G_2:uv\in I_k\},                \tag{28}
\]

and write \(M_k=|\mathcal R_k|\), \(E_k=E_\times(\mathcal R_k)\).
Set \(M_k^2/E_k=0\) when \(M_k=0\). The annuli are disjoint, so (6) gives

\[
|G\cap[1,2^K-1]|
\ge G_0(2^K-1)+\sum_{k\le K}\frac{M_k^2}{E_k}.                   \tag{29}
\]

Consequently, the fully quantified aggregate energy condition

\[
\boxed{
\Delta:=\liminf_{K\to\infty}2^{-K}
\sum_{k\le K}\frac{M_k^2}{E_k}>0
}                                                                 \tag{A}
\]

implies

\[
\underline d(G)\ge\underline d(G_0)+\Delta/2>0.                 \tag{30}
\]

Indeed, when \(2^K-1\le N<2^{K+1}-1\), equation (3) lets one add the
current baseline \(G_0(N)\) to all product blocks through \(I_K\). The
factor \(1/2\) in (30) is therefore lost only on the product contribution
when transferring from dyadic endpoints to all integer cutoffs. It disappears
if the corresponding truncated-annulus estimate is proved uniformly for
every \(N\).

A clean, stronger theorem which implies (A) is the following single
uniform inequality: there exist \(C<\infty\) and \(k_0\) such that for every
\(k\ge k_0\),

\[
\boxed{
E_k\le C\frac{M_k^2}{2^k}.
}                                                                 \tag{U}
\]

Indeed, (U) gives \(M_k^2/E_k\ge2^k/C\), so (29) and monotonicity imply
\(\underline d(G)\ge1/C\). The normalization has two useful adversarial
checks:

1. From \(E_k\ge M_k\), (U) forces \(M_k\ge2^k/C\). Thus (U) contains a
   linear pair-supply theorem, not just a collision estimate.
2. Products in \(I_k\) are multiples of \(3\), of which there are
   \(2^k/6+O(1)\). Therefore Cauchy--Schwarz forces
   \(C\ge2^k/(2^k/6+O(1))\) for every large \(k\); since \(C\) is fixed,
   taking \(k\to\infty\) gives \(C\ge6\) in this normalization.

Equivalently, a transparent sufficient split of (U) is

\[
M_k\ge\mu2^k,\qquad E_k\le K M_k                             \tag{31}
\]

with fixed \(\mu>0\), \(K<\infty\), uniformly for every large \(k\).
Then (U) holds with \(C=K/\mu\). The computation in the supplied probe tests
finite rectangular analogues of the second inequality in (31); it does not
prove the first inequality or the required uniformity.

Condition (A) is the exact weakest statement isolated here for the canonical
full annular relations. For arbitrary adaptive singleton relations, a packed
criterion can be made tautologically equal to counting \(G_0G_2\) itself.
Thus an actual advance must establish (A), (U), or (P) for an explicitly
specified reservoir family without first knowing its distinct products.

## 6. Strongest closure-specific attempt available here

### 6.1 Injective transfer between the two colours

The seed \(2\in G_2\) gives two injective closure maps:

\[
u\in G_0\Longrightarrow 2u-1\in G_2,
\qquad
v\in G_2\setminus\{2\}\Longrightarrow2v-1\in G_0.               \tag{32}
\]

For the second map, excluding \(v=2\) is required by the distinct-input
rule. Let \(Z>4\), take any finite
\(V\subseteq G_2\cap(Z/2,Z]\), and set

\[
U=2V-1\subseteq G_0\cap(Z-1,2Z-1].                              \tag{33}
\]

If \(m=|V|\), then \(|U||V|=m^2\), every product is below \(2Z^2\), and
(7)-(8) give

\[
m^2\le E_\times(U,V)\le D(2Z^2)m^2,                             \tag{34}
\]

\[
|UV|\ge\frac{m^2}{D(2Z^2)},                                    \tag{35}
\]

and, with ambient product scale \(S=2Z^2\),

\[
\frac{2Z^2}{m^2}
\le\frac{2Z^2E_\times(U,V)}{m^4}
\le\frac{2Z^2D(2Z^2)}{m^2}.                                    \tag{36}
\]

Thus this closure-specific construction has a rigorous subpolynomial
collision bound, but bounded density-scale energy in (36) still requires
\(m\gg Z\). No available theorem gives such a linear lower bound for these
\(G_2\) windows.

### 6.2 Exact base-30 reservoirs fail the diagonal test

The block construction in `fanout/wave2/B07_nonlinear_bootstrap.md` gives,
for \(n\ge1\),

\[
\mathcal B_n=
\left\{9\cdot30^n-\sum_{j=0}^{n-1}b_j30^j:
b_j\in\{9,10,13,16,19,21\}\right\}\subseteq G.                  \tag{37}
\]

The \(6^n\) values are distinct and satisfy

\[
8\cdot30^n<x<9\cdot30^n.                                       \tag{38}
\]

Modulo \(3\), only the least significant digit \(b_0\) matters. The two
choices \(9,21\) give residue \(0\), and the four choices
\(10,13,16,19\) give residue \(2\). Hence, exactly,

\[
U_n:=\mathcal B_n\cap G_0,\quad |U_n|=2\cdot6^{n-1},
\qquad
V_n:=\mathcal B_n\cap G_2,\quad |V_n|=4\cdot6^{n-1}.             \tag{39}
\]

Use \(Y_n=Z_n=9\cdot30^n\) and \(S_n=81\cdot900^n\). For these genuine
dyadic reservoirs,

\[
M_n=|U_n||V_n|=8\cdot36^{n-1}.
\]

The diagonal bound alone gives

\[
\kappa_n
=\frac{E_\times(U_n,V_n)S_n}{M_n^2}
\ge\frac{S_n}{M_n}
=\frac{729}{2}\,25^n.                                           \tag{40}
\]

Thus even perfectly distinct products would not make this explicit family
satisfy a bounded-\(\kappa\) criterion.

Combining every pair of block levels does not repair the mass deficit. If
\(n+m=k\), then

\[
U_nV_m\subset(64\cdot30^k,81\cdot30^k)
\]

and the total number of ordered pairs over all \(n,m\ge1\) with \(n+m=k\)
is

\[
\sum_{n+m=k}|U_n||V_m|
=(k-1)8\cdot6^{k-2}
=\frac29(k-1)6^k.                                                 \tag{41}
\]

This is \(o(30^k)\). Summing (41) through level \(K\) gives
\(O(K6^K)=o(30^K)\) pair representations below the next product band.
By (17), this entire explicit block family cannot meet (P), regardless of
how small its off-diagonal collision energy is. This statement concerns only
the certified block family, not the full set \(G\).

### 6.3 What the finite probe establishes

For a rectangular block, the two normalizations are related by

\[
\lambda=\frac{E}{|U||V|},
\qquad
\kappa=\frac{ES}{|U|^2|V|^2}
=\lambda\frac{S}{|U||V|}.                                       \tag{42}
\]

The supplied computation exactly evaluates both quantities for finitely
many reservoirs with factors at most \(10^6\). Values of \(\lambda\) close
to \(1\) show that those finite products are diagonal-dominated. They do
not bound \(S/(|U||V|)\), do not give a constant valid at all later scales,
and do not address cutoffs between tested scales. Thinning one side by a
factor \(t\) leaves a diagonal-dominated \(\lambda\) roughly unchanged but
multiplies \(\kappa\) by roughly \(t\). No asymptotic conclusion follows
from the table alone.

## 7. Lemma dependency tree

```text
Goal: lower_density(G) > 0
|
+-- L1 [proved]: G is contained in residues 0 and 2 mod 3
|   |
|   +-- L2 [proved]: G0 * G2 - 1 is contained in G2
|       (cross-colour inputs are automatically distinct)
|       |
|       +-- L3 [proved]: translation/baseline inequality (3)
|
+-- E1 [proved]: representation identity (5)
|   |
|   +-- E2 [proved]: exact Cauchy--Schwarz bound (6)
|   |   |
|   |   +-- E3 [proved]: disjoint packed-energy lemma (P)
|   |       |
|   |       +-- A1 [OPEN]: aggregate annular inequality (A)
|   |           |
|   |           +-- sufficient M1 [OPEN]: M_k >= mu * 2^k uniformly
|   |           +-- sufficient M2 [OPEN]: E_k <= K * M_k uniformly
|   |               (M1 + M2 imply the concrete target (U))
|   |
|   +-- E4 [proved]: diagonal obstruction E >= M
|   +-- E5 [proved]: divisor bound E <= D(X) M
|
+-- C1 [proved]: colour transfer v -> 2v-1, with v != 2
|   +-- C2 [proved]: bounds (34)-(36), insufficient without |V| >> Z
|
+-- B1 [proved]: base-30 coloured reservoirs (37)-(39)
    +-- B2 [proved]: kappa >= (729/2) * 25^n
    +-- B3 [proved]: all-level pair supply O(K * 6^K) = o(30^K)

Frontier: prove (A), or the stronger uniform inequality (U), for the full
cross-colour relation or for an explicit packed family with linear total
pair mass. No supplied closure fact proves either requirement.
```

## 8. Adversarial audit checklist

1. **Cauchy--Schwarz:** energy uses ordered coloured pairs; the numerator is
   \((|U||V|)^2\), and the denominator includes the \(|U||V|\) diagonal.
2. **Product range:** dyadic factor windows give \((YZ/4,YZ]\); after closure
   the outputs lie in \((YZ/4-1,YZ-1]\). A cutoff \(N\) therefore permits
   \(YZ\le N+1\).
3. **Residue support:** products occupy only multiples of \(3\). This changes
   the theoretical minimum probe normalization from about \(4/3\) to about
   \(4\), as recorded in (23).
4. **Distinct inputs:** every \(G_0\)-by-\(G_2\) pair is valid. The map
   \(v\mapsto2v-1\) must exclude \(v=2\).
5. **No double counting:** reservoirs can be reused, but individual energy
   lower bounds can be added only after their product supports are made
   disjoint or their cross-energy is included.
6. **Lower density:** hypotheses must hold for every sufficiently large
   cutoff, or on a cofinal sequence with bounded multiplicative gaps. An
   arbitrary infinite subsequence is insufficient.
7. **Uniformity:** constants are independent of scale and block. Nonuniform
   exceptional blocks must contribute \(o(N)\) to the relevant weighted sum.
8. **Finite computation:** exact finite energies verify only those instances;
   they supply neither a liminf nor a uniform asymptotic constant.
