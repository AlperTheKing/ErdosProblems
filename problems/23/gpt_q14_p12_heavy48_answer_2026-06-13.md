The highest-leverage next step is not another category-count inequality. It is an exact **S1–S2 reconstruction lemma**. It removes the main source of the (721{,}009) fixed-(R) quotient explosion: the (S_1S_2) graph should not be enumerated. Once the zero/singleton incidences and the (A/B)-states are fixed, every (S_1S_2) edge is forced.

This is especially targeted at the heavy ((ZZ=0,ZD=3)) block, where the quotient mass is mostly the many possible (S_1S_2) graphs.

---

# 1. Universal dichotomy: common-neighbour count determines adjacency

Use only triangle-freeness and the minimum nonedge-codegree (2) condition.

For any two vertices (u,v), let

[
\kappa(u,v):=|N(u)\cap N(v)|.
]

Then:

[
\boxed{
uv\in E(G)\implies \kappa(u,v)=0,
}
]

because otherwise (u,v) and a common neighbour form a triangle.

Also,

[
\boxed{
uv\notin E(G)\implies \kappa(u,v)\ge 2,
}
]

because every nonedge has at least two common neighbours.

Therefore every pair satisfies the exact trichotomy:

[
\boxed{
\kappa(u,v)=0 \Longrightarrow uv\in E(G),
}
]

[
\boxed{
\kappa(u,v)=1 \Longrightarrow \text{impossible},
}
]

[
\boxed{
\kappa(u,v)\ge 2 \Longrightarrow uv\notin E(G).
}
]

This is the key missing cut.

---

# 2. Exact S1–S2 reconstruction lemma

Fix (u\in S_1) and (v\in S_2). Define

[
X_r:=N_A(r),\qquad Y_r:=N_B(r)
]

for (r\in R).

Let

[
Z(u,v):=|{z\in Z:zu\in E_R,\ zv\in E_R}|.
]

Since (u) has label ({1}) and (v) has label ({2}), they have no common (C)-neighbour. They also have no common neighbour among (x,y,D,S_1,S_2). The only possible common neighbours of (u) and (v) are:

[
A\text{-vertices hit by both},
]

[
B\text{-vertices hit by both},
]

and zero vertices adjacent to both.

Thus

[
\boxed{
\kappa(u,v)
===========

|X_u\cap X_v|+|Y_u\cap Y_v|+Z(u,v).
}
]

Hence:

[
\boxed{
uv\in E_R
\iff
|X_u\cap X_v|+|Y_u\cap Y_v|+Z(u,v)=0.
}
\tag{S1S2-reconstruct}
]

Also:

[
\boxed{
|X_u\cap X_v|+|Y_u\cap Y_v|+Z(u,v)=1
\quad\text{is impossible.}
}
\tag{S1S2-one-forbidden}
]

And if the value is at least (2), then (uv) is forced to be a nonedge.

So the (S_1S_2) graph is not an independent object. It is determined by the zero-neighbour matrix and the (A/B)-states.

This is the strongest next reduction.

---

# 3. Consequences for the ((ZZ=0,ZD=3)) block

In the heavy block

[
ZZ=0,\qquad ZD=3,
]

the unique doubleton vertex (D) is adjacent to all three zero vertices, and the zero vertices are pairwise nonadjacent.

For each (z\in Z), define

[
P_z:=N_R(z)\cap S_1,\qquad Q_z:=N_R(z)\cap S_2.
]

Local domination gives

[
|P_z|\ge 1,\qquad |Q_z|\ge 1,
]

because the (D)-edge supplies one neighbour containing each colour, and each zero vertex still needs one additional (S_1)- and one additional (S_2)-neighbour.

Triangle-freeness gives:

[
\boxed{
uv\notin E_R
\quad
\text{whenever }
u\in P_z,\ v\in Q_z.
}
]

Equivalently, the (S_1S_2) graph avoids the union of zero-forbidden rectangles

[
\mathcal F_Z:=\bigcup_{z\in Z}P_z\times Q_z.
]

But the reconstruction lemma gives more. Define

[
C_{uv}:=|{z\in Z:u\in P_z,\ v\in Q_z}|.
]

Then for every (u\in S_1), (v\in S_2):

[
\boxed{
uv\in E_R
\iff
C_{uv}=0,\quad X_u\cap X_v=\varnothing,\quad Y_u\cap Y_v=\varnothing.
}
]

The forbidden-one condition becomes:

[
\boxed{
C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|\ne 1.
}
]

So the heavy (S_1S_2) graph is exactly

[
\boxed{
E_R(S_1,S_2)
============

{uv:C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|=0}.
}
]

Therefore the category count

[
S_1S_2=x
]

is equivalent to the state equation

[
\boxed{
x=
#{(u,v)\in S_1\times S_2:
C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|=0}.
}
\tag{H-count}
]

The local domination constraints for singleton vertices become:

[
\boxed{
\forall u\in S_1,\quad
#{v\in S_2:
C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|=0}\ge 2,
}
\tag{S1-local}
]

[
\boxed{
\forall v\in S_2,\quad
#{u\in S_1:
C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|=0}\ge 2.
}
\tag{S2-local}
]

These three equations replace enumeration of all (S_1S_2) graphs.

That is the main reduction.

---

# 4. Immediate static cuts from the reconstruction lemma

For every pair ((u,v)\in S_1\times S_2):

## Case 1: (C_{uv}=0)

Then

[
uv\in E_R
\iff
|X_u\cap X_v|+|Y_u\cap Y_v|=0.
]

If (uv) is not an edge, then the overlap must be at least (2):

[
uv\notin E_R
\implies
|X_u\cap X_v|+|Y_u\cap Y_v|\ge 2.
]

Overlap exactly (1) is impossible.

## Case 2: (C_{uv}=1)

The pair (uv) cannot be an edge because that would form a triangle through the unique common zero neighbour.

As a nonedge, it needs at least two common neighbours. Since it already has exactly one zero common neighbour, it must have at least one (A/B)-common neighbour:

[
\boxed{
C_{uv}=1
\implies
|X_u\cap X_v|+|Y_u\cap Y_v|\ge 1.
}
]

## Case 3: (C_{uv}\ge 2)

Then (uv) is automatically a valid nonedge from the zero common-neighbours alone. No (A/B)-overlap is forced.

So the whole (S_1S_2) layer can be encoded by these three local overlap rules plus the edge-count equation.

---

# 5. Why this targets the largest quotient mass

The fixed-(R) quotient explosion is caused mostly by the many possible (S_1S_2) graphs.

But after the reconstruction lemma, the (S_1S_2) graph is determined by:

1. the zero-neighbourhood matrix (C_{uv}), and
2. the (A/B)-states of the ten singleton vertices.

So the new finite object is not a fixed (R)-graph. It is a **zero-skeleton plus state assignment**.

For ((ZZ=0,ZD=3)), the zero-skeleton consists only of the six sets

[
P_z\subseteq S_1,\qquad Q_z\subseteq S_2,\qquad z\in Z,
]

with

[
\sum_z |P_z|=ZS_1,\qquad
\sum_z |Q_z|=ZS_2,
]

[
|P_z|\ge 1,\qquad |Q_z|\ge 1.
]

The (S_1S_2) graph is then reconstructed by the state equation above.

This should be much smaller than enumerating all (S_1S_2)-quotient representatives.

---

# 6. The disconnected (A!-!B) state space

The (A!-!B) graph (P=G[A,B]) is (2)-regular with (p=12), and the already checked lemma says (P) is disconnected. Thus only three templates remain:

[
C_8+C_4,\qquad C_6+C_6,\qquad C_4+C_4+C_4.
]

For a fixed template (P), define the finite state set

[
\mathcal S(P):=
{(X,Y):X\subseteq A,\ Y\subseteq B,\ X\times Y\cap E(P)=\varnothing}.
]

These are exactly the possible (A/B)-neighbourhood states of an (R)-vertex.

The state counts you already have are:

[
|\mathcal S(C_8+C_4)|=329,
]

[
|\mathcal S(C_6+C_6)|=324,
]

[
|\mathcal S(3C_4)|=343.
]

For each state (s=(X,Y)), define

[
m(s):=|X|+|Y|.
]

Every valid model assigns one state (s_r\in\mathcal S(P)) to each (r\in R).

---

# 7. Exact finite verifier after S1–S2 reconstruction

The verifier should enumerate **zero-skeletons**, not fixed (R)-graphs.

For each of the (48) heavy categories and each disconnected (A!-!B) template, do the following.

## 7.1 Zero/D/singleton skeleton

Enumerate only the edges involving (Z) and (D):

[
ZZ,\quad ZD,\quad ZS_1,\quad ZS_2.
]

Do this canonically under

[
S_3\text{ on }Z,\qquad S_5\text{ on }S_1,\qquad S_5\text{ on }S_2,
]

and also colour-swap symmetry when (ZS_1=ZS_2).

The skeleton must satisfy:

[
|E(Z,Z)|=ZZ,
]

[
|E(Z,D)|=ZD,
]

[
|E(Z,S_1)|=ZS_1,
]

[
|E(Z,S_2)|=ZS_2.
]

Local zero domination:

[
\forall z\in Z,\qquad
|N(z)\cap S_1|+\mathbf 1_{zD\in E}\ge 2,
]

[
\forall z\in Z,\qquad
|N(z)\cap S_2|+\mathbf 1_{zD\in E}\ge 2.
]

Triangle-free skeleton conditions:

If (zz'\in E), then

[
N(z)\cap S_1\cap N(z')=\varnothing,
]

[
N(z)\cap S_2\cap N(z')=\varnothing,
]

and not both (zD,z'D) are edges.

No (S_1S_2) graph is enumerated at this stage.

## 7.2 State variables

For each (r\in R), choose one state

[
s_r=(X_r,Y_r)\in\mathcal S(P).
]

Label-dependent lower bounds:

For (z\in Z),

[
|X_z|\ge 2,\qquad |Y_z|\ge 2.
]

For (s\in S_1\cup S_2),

[
|X_s|\ge 1,\qquad |Y_s|\ge 1.
]

For (D), no (x/y)-codegree lower bound is needed from this source.

Degree lower bounds:

[
d_R(r)+|\ell(r)|+m(s_r)\ge 8.
]

Here (d_R(r)) is not fully known until (S_1S_2) is reconstructed, so for (S_1,S_2) it is computed from the reconstructed edge relation.

Cap equality:

[
\boxed{
\sum_{r\in R}m(s_r)=74.
}
]

## 7.3 Fixed-edge triangle constraints

For every skeleton edge (rr') among

[
ZZ,\quad ZD,\quad ZS_1,\quad ZS_2,
]

require

[
X_r\cap X_{r'}=\varnothing,
]

[
Y_r\cap Y_{r'}=\varnothing.
]

Also require that the skeleton edge has no other common (R)-neighbour. Equivalently, its full common-neighbour count must be zero.

This is just the universal dichotomy applied to fixed skeleton edges.

## 7.4 Reconstruct (S_1S_2)

For every (u\in S_1), (v\in S_2), define

[
q_{uv}:=
Z(u,v)+|X_u\cap X_v|+|Y_u\cap Y_v|.
]

Require

[
\boxed{q_{uv}\ne 1.}
]

Define

[
\boxed{
H_{uv}=1\iff q_{uv}=0.
}
]

Then impose the category count

[
\boxed{
\sum_{u\in S_1,\ v\in S_2}H_{uv}=S_1S_2.
}
]

And singleton local domination:

[
\boxed{
\forall u\in S_1,\qquad \sum_{v\in S_2}H_{uv}\ge 2,
}
]

[
\boxed{
\forall v\in S_2,\qquad \sum_{u\in S_1}H_{uv}\ge 2.
}
]

This replaces all enumeration of (S_1S_2) graphs.

## 7.5 A/B degree constraints

Since each (A)- or (B)-vertex has one root neighbour and two (A!-!B) neighbours, it needs at least five (R)-neighbours:

[
\boxed{
\forall a\in A,\qquad
|{r:a\in X_r}|\ge 5,
}
]

[
\boxed{
\forall b\in B,\qquad
|{r:b\in Y_r}|\ge 5.
}
]

Every (A/B)-vertex must also see both root colours through (R)-neighbours:

[
\boxed{
\forall a\in A,\qquad
\exists r\in S_1\cup D\text{ with }a\in X_r,
}
]

[
\boxed{
\forall a\in A,\qquad
\exists r\in S_2\cup D\text{ with }a\in X_r,
}
]

and similarly for every (b\in B).

## 7.6 Rectangle two-cover of missing (A!-!B) cells

For every missing (A!-!B) cell ((a,b)\notin E(P)),

[
\boxed{
|{r\in R:a\in X_r,\ b\in Y_r}|\ge 2.
}
]

For every (A!-!B) edge ((a,b)\in E(P)), this count is automatically zero because every state satisfies

[
X_r\times Y_r\cap E(P)=\varnothing.
]

This is the usual rectangle condition, but now over one of only three (P)-templates.

## 7.7 Same-side (A!-!A) and (B!-!B) nonedge codegrees

For (a,a'\in A), (a\ne a'), the pair (aa') already has (x) as a common neighbour, so it needs at least one more common neighbour. Thus require:

[
\boxed{
|N_P(a)\cap N_P(a')|
+
|{r:a,a'\in X_r}|
\ge 1.
}
]

Similarly,

[
\boxed{
|N_P(b)\cap N_P(b')|
+
|{r:b,b'\in Y_r}|
\ge 1.
}
]

## 7.8 Missing (A!-!R) and (B!-!R) incidences

For (a\in A) and (r\in R) with (a\notin X_r), the common neighbours of (a) and (r) are:

1. (B)-vertices adjacent to (a) in (P) and lying in (Y_r);
2. (R)-neighbours (u) of (r) with (a\in X_u).

So require:

[
\boxed{
|N_P(a)\cap Y_r|
+
|{u\in N_R(r):a\in X_u}|
\ge 2.
}
]

Here (N_R(r)) includes the skeleton edges plus reconstructed (S_1S_2) edges.

Similarly, for (b\in B) and (r\in R) with (b\notin Y_r),

[
\boxed{
|N_P(b)\cap X_r|
+
|{u\in N_R(r):b\in Y_u}|
\ge 2.
}
]

## 7.9 All (R!-!R) nonedge codegrees

Once (S_1S_2) is reconstructed, the full (R)-graph is known. For every nonedge (rr') in (R), require:

[
\boxed{
|\ell(r)\cap \ell(r')|
+
|X_r\cap X_{r'}|
+
|Y_r\cap Y_{r'}|
+
|N_R(r)\cap N_R(r')|
\ge 2.
}
]

For every edge (rr'), the same quantity must be zero. This is already enforced for skeleton edges and automatically for reconstructed (S_1S_2) edges by (q_{uv}=0), but it is safest to check it uniformly.

## 7.10 Rooted cuts

For every (W\subseteq R), impose the exact cap74 rooted cuts.

Since

[
p+e_R=37,
]

the (\Phi)-cut has the simple form:

[
\boxed{
M(W)+F_\Phi(W)\ge \partial_R(W),
}
]

where

[
M(W)=\sum_{r\in W}m(s_r),
]

[
\partial_R(W)=e_R(W,R\setminus W),
]

and

[
F_\Phi(W)=\sum_{i=1}^2 \min\bigl(|U_i\cap W|,\ 8-|U_i\cap W|\bigr).
]

For the opposite-root (\Psi)-cuts, impose both orientations:

[
\boxed{
e_R-\partial_R(W)+F_\Psi(W)+M_A(W)+M_B(R\setminus W)\ge 37,
}
]

[
\boxed{
e_R-\partial_R(W)+F_\Psi(W)+M_B(W)+M_A(R\setminus W)\ge 37,
}
]

where

[
M_A(W)=\sum_{r\in W}|X_r|,
\qquad
M_B(W)=\sum_{r\in W}|Y_r|,
]

and

[
F_\Psi(W)=2+\sum_{i=1}^2\min\bigl(|U_i\cap W|,\ 6-|U_i\cap W|\bigr).
]

There are only (2^{14}=16384) masks, so this is small at the state-checking level.

---

# 8. Certificate format

The cleanest proof certificate is a finite collection of unsatisfiability certificates indexed by:

[
\text{category profile}\quad \times\quad
\text{(A!-!B) template}\quad \times\quad
\text{zero-skeleton orbit}.
]

For each item, output:

1. the category profile;
2. the (A!-!B) template:
   [
   C_8+C_4,\quad C_6+C_6,\quad\text{or}\quad 3C_4;
   ]
3. the canonical zero/D/singleton skeleton;
4. the state table hash for (\mathcal S(P));
5. a checked UNSAT certificate for the state constraints above.

The certificate can be either:

* a VeriPB proof, because all constraints are pseudo-Boolean after table expansion; or
* a custom backtracking certificate whose leaves are refuted by one of the explicit inequalities:

  * cap sum violation,
  * (S_1S_2)-reconstruction count violation,
  * forbidden (q_{uv}=1),
  * missing rectangle two-cover,
  * (A/B)-degree failure,
  * (A!-!R), (B!-!R), or (R!-!R) codegree failure,
  * rooted cut violation.

This is not a black-box fixed-(R) SAT proof. The (S_1S_2) graph is derived, not guessed.

The number of top-level cases should drop from

[
721{,}009
]

fixed-(R) quotients to roughly:

[
48\text{ category profiles}
\times
3\text{ }A!-!B\text{ templates}
\times
{\text{zero-skeleton orbits}}.
]

The heavy (S_1S_2) graph enumeration disappears.

---

# 9. Optional conditional reroot cut

This one is useful but must be marked conditional.

The clean-shadow bound for this row is

[
e_R\ge 30,
]

but here

[
e_R=25.
]

So every valid model has at least one (C)-tight pair.

If (r\in R\setminus U_i) satisfies

[
d_R(r,U_i)=2,
]

then rerooting at the nonedge (c_i r) gives

[
q'=22-\deg(r).
]

Hence:

[
\deg(r)>8\implies q'<14.
]

So, **conditional on the (q<14) branches being closed or delegated**, every terminal (q=14) obstruction satisfies:

[
\boxed{
d_R(r,U_i)=2\implies \deg(r)=8.
}
]

Then the singleton (\Phi)-cut gives:

[
\boxed{
d_R(r,U_i)=2\implies d_R(r)\le 4.
}
]

This is a strong additional (R)-side filter, but it depends on the reroot branch being accepted in the proof tree. Do not use it as an unconditional contradiction.

---

# 10. What this gives for the ((ZZ=0,ZD=3)) block

For ((ZZ=0,ZD=3)), the skeleton is just:

[
P_z=N(z)\cap S_1,\qquad Q_z=N(z)\cap S_2,\qquad z\in Z,
]

with

[
|P_z|\ge 1,\qquad |Q_z|\ge 1.
]

Define

[
C_{uv}=|{z:u\in P_z,\ v\in Q_z}|.
]

Then the entire (S_1S_2) graph is forced by

[
uv\in E_R
\iff
C_{uv}+|X_u\cap X_v|+|Y_u\cap Y_v|=0.
]

Therefore the largest category

[
(ZZ,ZS_1,ZS_2,ZD,S_1S_2)=(0,4,4,3,14)
]

is no longer “all (80{,}386) quotient (R)-graphs.” It becomes:

* choose the zero-skeleton ((P_z,Q_z)_{z\in Z}) with total sizes (4,4);
* choose one of the three (A!-!B) templates;
* assign (A/B)-states to the fourteen (R)-vertices;
* reconstruct (S_1S_2) and check that exactly (14) pairs have zero common-neighbour count.

That is the right proof object.

---

# Weakest steps

I do **not** claim a hand contradiction for all (48) heavy categories.

The rigorous new lemma is the (S_1S_2)-reconstruction rule:

[
uv\in E_R
\iff
Z(u,v)+|X_u\cap X_v|+|Y_u\cap Y_v|=0.
]

This is unconditional and follows only from triangle-freeness and minimum nonedge-codegree (2).

The proposed verifier is still finite/computational, but it is much smaller and more structural than checking (721{,}009) fixed-(R) representatives. Its proof certificate should be indexed by category, (A!-!B) template, and zero-skeleton orbit, not by full (R)-graph quotient.

The optional tight-degree cut

[
d_R(r,U_i)=2\Rightarrow d_R(r)\le 4
]

is conditional on routing (\deg(r)>8) cases to already-closed or separately verified (q<14) branches.
