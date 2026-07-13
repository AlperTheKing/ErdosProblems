# P115: BC108 reduced to the invisible secondary-cycle budget

## Verdict

BC108 is not proved here, and no exact falsifier was found.  The arm-graph
problem does, however, admit a sharper linear-algebraic reduction which
removes the entire `p`-bank from the combinatorial part of the argument.

For every fold `F=(a,c,u,v)`, let

\[
 R_F=e_a+e_c+e_h-e_u-e_v\in\mathbb Q^{B\sqcup\{h\}}.       \tag{1}
\]

Let `M_F` be the matrix with rows `R_F`.  The actual endpoint realization
and the common-translation vector are two independent null vectors, so

\[
                 \operatorname {rank}_{\mathbb Q}M_F\le p-1. \tag{2}
\]

The reduction below attaches to all directed arm graphs one exact integer
rank `rho`.  It proves

\[
 \boxed{\rho\le \operatorname {rank}_{\mathbb Q}M_F\le p-1}. \tag{3}
\]

Consequently BC108 follows from the single strictly stronger inequality

\[
 \boxed{
   \sum_u(t_u-n_u)_+-\rho
       \le V_b+(-\delta)_+ .
 }
 \tag{KB115}
\]

Call this the **invisible secondary-cycle budget**.  Unlike BC108, KB115
does not have a free mark term: all cycle directions visible to the fold
equations have already been paid by the rank in (3).  Its left side is the
dimension still invisible after that payment.

KB115 has zero failures in the exact domains described in Section 6.  It is
not proved.  Thus P115 is a sharp reduction, not a proof of BC108 or of
Problem 864.

## 1. Arm boundary and cycle space

Use P108's directed arm graph `G_u`.  Its vertices are the folds

\[
 F_i=(a_i,c_i,u,v_i)
\]

of color `u`.  A loose triangle is an arc `T:i -> j`; its base fold is the
unique fold

\[
                 K(T)=(a_i,c_j,r_T,s_T).                 \tag{4}
\]

Let `C_1` be the rational vector space with the loose triangles as basis,
and let `C_0` have the folds as basis.  Define the block-diagonal directed
incidence map

\[
 \partial:C_1\longrightarrow C_0,
 \qquad \partial T=e_j-e_i.                              \tag{5}
\]

Thus `Z=ker partial` is the direct sum of the ordinary circulation spaces
of the arm graphs.  This definition includes signed undirected cycles; it
does not assume that a cycle follows every arc orientation.

Put

\[
                   X:=\sum_u(t_u-n_u)_+.                 \tag{6}
\]

For a color with `t_u>n_u`, the cycle-space dimension is at least
`t_u-n_u`: if `n'_u` vertices are incident with arcs and `c_u` is the
number of nonempty weak components, then

\[
 \dim Z_u=t_u-n'_u+c_u\ge t_u-n_u.                       \tag{7}
\]

Colors with `t_u<=n_u` contribute zero to (6).  Therefore

\[
                         X\le\dim Z.                     \tag{8}
\]

Equivalently, after choosing a spanning forest in every nonempty weak
component, `X` is the number of secondary cycle directions retained after
discarding enough free component-cycle directions.  This is the precise
cycle-decomposition meaning of the positive part in BC108.

More formally, because `dim Z>=X`, an `X`-dimensional subspace can be
chosen to contain `min(X,rho)` directions on which the map in Section 2 is
independent.  Its smallest possible invisible dimension is therefore
`max(0,X-rho)`, the quantity used below.

## 2. The base-fold visibility map

Define

\[
 A:C_1\longrightarrow\mathbb Q^{B\sqcup\{h\}},
 \qquad A(T)=R_{K(T)}.                                   \tag{9}
\]

The relevant rank is the rank of `A` restricted to circulations:

\[
 \rho:=\operatorname {rank}_{\mathbb Q}(A|_Z).          \tag{10}
\]

It is computable without constructing a cycle basis.  If matrices are
written with triangle columns, then elementary linear algebra gives

\[
 \boxed{
 \rho=\operatorname {rank}_{\mathbb Q}
       \begin{bmatrix}\partial\\A\end{bmatrix}
       -\operatorname {rank}_{\mathbb Q}\partial .
 }                                                       \tag{11}
\]

Indeed, choose a complement `W` to `ker partial`.  The map `partial` is
injective on `W`; after quotienting the image of `W`, the additional rank
of the stacked map is exactly the rank of `A` on `ker partial`.

Every column of `A` is a row of `M_F`.  Hence the image in (10) lies in the
row space of `M_F`, proving the first inequality in (3).

For the second inequality in (3), the vector which is `1` on every mark
coordinate and `0` on the `h` coordinate annihilates every row (1).  The
actual vector `(x)_{x in B},h` also annihilates every row.  Since `h>0`, the
two null vectors are independent.  There are `p+1` columns, so (2) follows.

## 3. Literal phase retained on every cycle

For a fold put

\[
                         q_F=a+c+b.                     \tag{12}
\]

For an arc `T:i -> j`, equations (4) and (12) give

\[
 q_{K(T)}-q_{F_i}=c_j-c_i,
 \qquad
 q_{K(T)}-q_{F_j}=a_i-a_j.                              \tag{13}
\]

If `z=(z_T)` is a circulation, the incidence balance at every arm vertex
implies both exact cancellations

\[
 \boxed{
   \sum_Tz_Tq_{K(T)}=\sum_Tz_Tq_{F_i}
                    =\sum_Tz_Tq_{F_j}.
 }                                                       \tag{14}
\]

For a directed simple cycle with every coefficient equal to one, (14) is
P108.2.  Formula (14) proves it for every signed cycle-space element and is
the reason for restricting (9) to `ker partial`.

Under the literal hole, every phase `q_F` is absent from the represented
positive-difference set.  Outside the hole, the exact correction bank is

\[
 V_b=|\{F:q_F\in\Delta^+(B)\}|.                        \tag{15}
\]

Thus the only part of the secondary cycle space not already seen by (9) is

\[
 \kappa_{115}:=\max\{0,X-\rho\}.                       \tag{16}
\]

KB115 is precisely

\[
                  \kappa_{115}\le V_b+(-\delta)_+.     \tag{17}
\]

This is a finite integer/rational statement about the fold matrix, the arm
incidence matrix, the literal phase labels, and the endpoint defect.  No
planarity, interval matching, or asymptotic notation remains.

## 4. KB115 implies BC108 and closes the P82 fold frontier

Assume KB115.  By (3),

\[
\begin{aligned}
 X
 &\le \rho+V_b+(-\delta)_+\\
 &\le p-1+V_b+(-\delta)_+\\
 &\le p+V_b+(-\delta)_+.
\end{aligned}                                           \tag{18}
\]

This is BC108, with one unit to spare whenever folds exist.

In the live positive-defect literal-hole regime, `V_b=0` and
`(-delta)_+=0`.  Hence

\[
 T_F=\sum_ut_u
 \le \sum_un_u+X
 \le C_S+p-1.                                          \tag{19}
\]

If `C_S>=epsilon p^2`, P82.2 gives `T_F>=eta(epsilon)p^3` for all
sufficiently large `p`, while (19) and `C_S<=p(p+1)/2` give `T_F=O(p^2)`.
This contradiction proves `C_S=o(p^2)`.  Therefore KB115 is sufficient for
the complete P82 removal step.

## 5. Why the precise map and both banks are necessary

### 5.1 Subtracting an arm row is false

A tempting normalization replaces (9) by

\[
                       A'(T)=R_{K(T)}-R_{F_i}.          \tag{20}
\]

It retains the scalar cycle cancellation but is too small.  On P106,

```text
X = 76,  rank(A'|Z) = 51,  V_1 = 20,  delta = 129.
```

Thus

\[
                 76-51=25>20=V_1+(-\delta)_+.          \tag{21}
\]

The same failure occurs with the head arm in place of the tail arm.  The
unsubtracted base-fold map (9), whose rank is `63` on P106, is load-bearing.

### 5.2 The collision bank cannot be deleted

For the exact positive-defect P106 row,

```text
(p,delta,X,rho,V_1) = (67,129,76,63,20).
```

Hence `X-rho=13>0`; KB115 without `V_b` is false even with positive defect.
The row is not a literal hole, exactly as required for this guardrail.

### 5.3 The negative-defect bank cannot be deleted

For the parity lift of P88,

```text
(p,delta,X,rho,V_1) = (60,-1201,69,58,0).
```

It is a literal hole, but `X-rho=11>0`.  Therefore the literal hole alone
does not prove the kernel budget; `(-delta)_+` is indispensable outside the
live positive-defect regime.

The original P88 row has the same arm graphs and `rho=58`, but has
`V_1=77` (or `V_2=74`) and positive defect.  The phase bank pays the same
eleven invisible dimensions before parity lifting; after lifting, the
negative-defect bank pays them.  This is the exact phase/scale dichotomy
which a phase-free arm-graph theorem cannot see.

### 5.4 Planarity remains unavailable

P88 and its parity lift have the same nonplanar arm graph at the principal
color.  Nothing in (5)--(18) uses planarity.  The reduction is ordinary
cycle-space linear algebra and remains valid for multicyclic nonplanar arm
graphs.

## 6. Exact audit

All ranks below were computed by integer Gaussian elimination modulo both
`1000003` and `1000033`; the two ranks agreed on every mandatory row.  A
nonzero modular minor is a rigorous lower bound for the stacked rational
rank.  The directed incidence rank is exactly `n'-c` over both the
rationals and these prime fields, so subtracting it in (11) preserves that
lower-bound direction.  This is the direction needed in (18).

| row | `X` | `rank partial` | `rho` | `V_b` | `(-delta)_+` | `X-rho-V-neg` |
|---|---:|---:|---:|---:|---:|---:|
| P75 | 3 | 16 | 9 | 0 | 0 | -6 |
| P94 | 24 | 75 | 40 | 0 | 0 | -16 |
| P98 | 23 | 71 | 38 | 0 | 0 | -15 |
| P105 | 45 | 95 | 56 | 0 | 1726 | -1737 |
| P88, `b=1` | 69 | 110 | 58 | 77 | 0 | -66 |
| P88, `b=2` | 69 | 110 | 58 | 74 | 0 | -63 |
| P88 parity lift | 69 | 110 | 58 | 0 | 1201 | -1190 |
| P106 | 76 | 120 | 63 | 20 | 0 | -7 |

Three broader exact gates were run.

1. Every one of the `1,857,024` width-30/translation phases from P108 was
   regenerated.  There are `6,132` rows with a loose triangle.  KB115 has
   zero failures.
2. All `785,508` original and parity-lift phases in the P98 parent-subset
   domain were regenerated.  Twenty-four have positive color excess; KB115
   has zero failures.  The largest residual is `-9`.
3. The full P106 compatibility graph on `2,401` individually admissible
   insertions was exhausted at target seven: `34,921,215` search nodes,
   `56` complete pairwise-compatible seven-cliques, and `17` internally
   Sidon seven-cliques.  KB115 has zero failures.  Its largest residual is
   `-4`, at additions

```text
{166,908,1728,3836,4748,5586,6224},
```

   where `(X,rho,V_1)=(72,59,17)`.  The target-eight search is exhaustive:
   `30,915,054` nodes and no pairwise-compatible eight-clique.

The rank used in the gates is computed directly from (11); no floating
point arithmetic, graph-planarity heuristic, or assumed cycle basis is
used.

## 7. Remaining lemma and claim boundary

The sole new proof target is KB115:

> For every endpoint-normalized integer Sidon fold system, the number of
> secondary arm-cycle directions invisible under the base-fold map is at
> most the number of represented literal phase labels plus the negative
> endpoint defect.

Equivalently, with `X`, `partial`, and `A` defined by (5)--(10), prove

\[
 X-
 \left(
 \operatorname {rank}_{\mathbb Q}
 \begin{bmatrix}\partial\\A\end{bmatrix}
 -\operatorname {rank}_{\mathbb Q}\partial
 \right)
 \le V_b+(-\delta)_+.                                  \tag{22}
\]

This is strictly sharper than BC108 and separates its mechanisms: cycle
decomposition produces `X`, fold rigidity pays `rho`, literal phase
collisions pay `V_b`, and only affine scale/endpoint slack is left for
`(-delta)_+`.  P106 and the P88 parity lift show independently that neither
correction can be removed.

P115 proves the reduction (22) `=>` BC108 `=>` the P82 fold conclusion.  It
does not prove (22), BC108, `C_S=o(p^2)`, or the full Erdos 864 theorem.
