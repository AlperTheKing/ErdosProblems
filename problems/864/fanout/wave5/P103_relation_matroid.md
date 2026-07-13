# P103: relation-matroid audit and a global weighted pivot

## Verdict

The direct `GF(2)` relation-matroid strengthening is false.  Let `A` be the
fold-by-triangle matrix whose column for a loose triangle has a one in each
of its three supporting fold rows.  The proposed bound

\[
             \dim\ker A\leq V_b                                      \tag{1}
\]

fails on 19 of the 4,170 P88 translation rows.  The worst row is

\[
 (\gamma,b,C_S,T_F,\operatorname{rank}A,
   \dim\ker A,V_b)=(41,2,181,232,160,72,63).             \tag{2}
\]

Thus (1) misses by nine although the scalar P101 inequality has slack 12.
Changing signs or nonzero weights on the same three support entries cannot
repair this route: P95's literal-hole row has structural support rank 105
for 116 triangle columns.

There is also no weaker theorem saying that every support dependence forces
a phase-collided fold.  On the P94 literal-hole maximum row,

\[
 (C_S,T_F,\operatorname{rank}_{GF(2)}A,
   \dim\ker A,V_b)=(142,116,105,11,0).                  \tag{3}
\]

The insertion maximum similarly has `(51,37,36,1,0)`.  These are exact
counterexamples to support-row independence under the literal hole.

The correct matroid quantity is the index

\[
 \dim\ker A-\dim\operatorname{coker}A=T_F-C_S.          \tag{4}
\]

Consequently P101 is exactly the global index statement

\[
 \dim\ker A-\dim\operatorname{coker}A\leq V_b,          \tag{5}
\]

not the nullity statement (1).  For (2), the cokernel has dimension 21, so
the index is `72-21=51<=63`.  For (3), it is `11-37=-26<=0`.  This explains
both the failed nullity charge and why unused folds in other components can
pay a global component deficit.

No proof of (5), P101, or C84 is obtained here.

## 1. Exact support-matroid audit

For every loose triangle, order its supporting folds as in P83:

\[
\begin{array}{ll}
 F_0=(a,c,r,s),     &a+c+h=r+s,\\
 F_Z=(a,z,u,w),     &a+z+h=u+w,\\
 F_X=(x,c,u,y),     &x+c+h=u+y.
\end{array}                                             \tag{6}
\]

The support column is

\[
                    e_{F_0}+e_{F_Z}+e_{F_X}.            \tag{7}
\]

Exact bit elimination over `GF(2)` gives:

* all 1,583,738 unrestricted width-30 rows: support nullity zero;
* all 4,170 P88 translation rows: 1,280 support-dependent rows and 19
  failures of (1);
* the largest P88 support nullity: 72, on (2);
* the P94 literal-hole ranks in (3) and the following sentence.

The first line explains why the false strengthening survived the small
unrestricted corpus.  The P94 rows show independently that the obstruction
is not caused only by phase collisions.

More generally, any matrix whose triangle column is supported only on
`{F_0,F_Z,F_X}` has rank at most the maximum matching size of that support
bipartite graph.  P95 gives matching size 105 on the 116-column row (3).
Therefore no orientation, field change, or nonzero reweighting confined to
the three support folds can establish triangle independence there.

## 2. A genuinely global relation matrix

There is a separate global algebraic pivot which passes the current exact
gate.  It is not a proof of P101, but its conjectural rank bound is already
strong enough to close P82.

Let `K` be a field of characteristic neither two nor three and, for a fold
`F=(alpha,gamma,rho,sigma)`, put

\[
 q(F)=e_\alpha+e_\gamma-e_\rho-e_\sigma\in K^B.         \tag{8}
\]

Subtracting the three formal fold equations in (6) gives the two short
additive relations

\[
\begin{split}
 L_1&=q(F_Z)-q(F_X)
     =e_a+e_z+e_y-e_x-e_c-e_w,\\
 L_2&=q(F_0)-q(F_Z)
     =e_c+e_u+e_w-e_z-e_r-e_s.                          \tag{9}
\end{split}
\]

Their numerical contents are exactly

\[
                 a+z+y=x+c+w,\qquad
                 c+u+w=z+r+s.                           \tag{10}
\]

Put `d=a+c+b`, the phase label of `F_0`, and assign to the triangle the
global vector

\[
 W_\tau=(e_{F_0}+e_{F_Z}+e_{F_X},
          L_1,L_2,dL_1,dL_2)
 \in K^{\mathcal F}\mathbin\oplus(K^B)^4.              \tag{11}
\]

The four mark blocks couple triangles in different support components.
They are therefore not constrained by P95's support matching rank.

### Weighted relation lemma (open)

For every endpoint-normalized integer Sidon fold system, the vectors
`(W_tau)` are linearly independent over `Q`.

If this lemma holds, dimension counting gives

\[
                  T_F\leq C_S+4p.                       \tag{12}
\]

Since `C_S<=p(p+1)/2`, (12) gives `T_F=O(p^2)` uniformly.  P82.2 would then
force `C_S=o(p^2)`.  Thus this lemma closes the fold frontier even without
using the literal hole, but it is presently an unproved theorem-strength
claim and does not establish the sharper exact P101 inequality.

The choice of `b` does not affect the rank in (11).  Replacing `b` by
`b+1` replaces each `dL_i` block by `dL_i+L_i`, an invertible block-column
operation.

## 3. Exact weighted gate

Sparse elimination modulo the prime 1,000,003 gives full row rank for:

* all 2,085 P88 translated fold systems, representing all 4,170 `b`-rows;
* the 640 P88 systems whose plain support matrix is dependent;
* P75, with `(p,C_S,T_F,rank)=(26,51,25,25)`;
* the P94 translation maximum, with `(104,142,116,116)`;
* the P94 insertion maximum, with `(26,51,37,37)`.

Full row rank modulo this prime is an exact rational independence
certificate for each tested integer matrix: a maximal minor is nonzero
modulo the prime and hence is a nonzero integer.  The sweep is a finite gate,
not a proof of the weighted relation lemma.

For a proof, let `S` denote (7), let

\[
 O_1e_\tau=e_{F_Z}-e_{F_X},\qquad
 O_2e_\tau=e_{F_0}-e_{F_Z},                             \tag{13}
\]

let `Qe_F=q(F)`, and let `D` be diagonal with entry `d_tau`.  The exact
remaining algebraic obligation is

\[
 \ker S\cap\ker(QO_1)\cap\ker(QO_2)
 \cap\ker(QO_1D)\cap\ker(QO_2D)=\{0\}.                 \tag{14}
\]

Equation (14) is genuinely global and retains both formal fold differences
and their first phase moment.  Proving it, or finding a counterexample, is
the next relation-matroid frontier.

## 4. Reproduction and claim boundary

Run

```powershell
python -m py_compile `
  problems/864/compute/p103/audit_relation_matroid.py `
  problems/864/compute/p103/audit_weighted_relations.py
python -B problems/864/compute/p103/audit_relation_matroid.py `
  --max-width 30 `
  --output problems/864/compute/p103/relation_matroid.json
python -B problems/864/compute/p103/audit_weighted_relations.py `
  --workers 16 `
  --output problems/864/compute/p103/weighted_relations.json
```

The proved negative statements are (1)--(3), the index identity (4), the
formal fold identities (8)--(10), and the conditional implication from the
weighted relation lemma to (12) and P82 closure.  Neither (5), weighted
independence, `T_F<=C_S+V_b`, nor `C_S=o(p^2)` is claimed as proved.
