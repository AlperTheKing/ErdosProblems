## Audit of the two existing cuts

### H14 anti-tightness

The cut

[
D(r)+|U_i|+d_R(r,U_i)\ge17
]

is safe provided H14 means the following genuinely reroot-invariant closure:

> Every exact-codegree-two nonedge whose endpoints both have degree (8) has already been excluded, regardless of the original label profile or rooted presentation.

It also requires the exact identities

[
d(c_i)=2+|U_i|,
\qquad
|N(r)\cap N(c_i)|=d_R(r,U_i).
]

No terminal degree statement follows from it.

### Isolated-support separation

The isolated-(T) lemma is safe. Its required assumptions are exactly:

1. (t) is genuinely isolated in (R);
2. A/R and B/R nonedges have total codegree at least (2);
3. (A\cup C) and (B\cup C) are independent, as follows from triangle-freeness and the root decomposition;
4. the A/B state incidences are actual adjacencies.

For (T), isolation follows because its label is ({1,2,3}), the only disjoint label is the empty label, and (c_0=0).

The main implementation risk is not mathematical but logical: if “(B_r\setminus B_t\neq\varnothing)” is represented by a Boolean, that Boolean must be equivalent to the difference being nonempty, not merely imply it. The strengthening below removes that issue entirely.

---

# Next strengthening: projected mixed-codegree separation

This is a direct extension of isolated-support separation to **every** (R)-vertex, including the forced bipartite blocks.

For (v\in R), define

[
A_v=N_A(v),\qquad B_v=N_B(v).
]

For (a\in A) and (b\in B), let their (R)-states be

[
X_a=N_R(a),\qquad Y_b=N_R(b).
]

## Lemma

For any distinct (r,t\in R):

### B-side form

If (b\in B_r\setminus B_t), then

[
\boxed{
|A_t\setminus A_r|
+
|Y_b\cap N_R(t)|
\ge2.
}
\tag{MC-B}
]

### A-side form

If (a\in A_r\setminus A_t), then

[
\boxed{
|B_t\setminus B_r|
+
|X_a\cap N_R(t)|
\ge2.
}
\tag{MC-A}
]

This uses no H14 assumption and no five-label-specific property.

## Proof of MC-B

Take (b\in B_r\setminus B_t). Thus

[
br\in E(G),\qquad bt\notin E(G).
]

The nonedge (bt) has at least two common neighbours.

We classify every common neighbour (w) of (b,t).

* (w) cannot be either root, because (t\in R) has no root adjacency.
* (w\notin C), because (B\cup C\subseteq N(y)) is independent.
* (w\notin B), because (B) is independent.
* If (w\in A), then (w\in A_t). Moreover (w\notin A_r): otherwise
  [
  br,rw,bw\in E(G)
  ]
  would form a triangle.
  Hence every common neighbour in (A) lies in
  [
  A_t\setminus A_r.
  ]
* If (w\in R), then (w\in Y_b\cap N_R(t)).

Consequently,

[
N(b)\cap N(t)
\subseteq
(A_t\setminus A_r)\cup(Y_b\cap N_R(t)).
]

The two sets lie in different vertex classes, so

[
|N(b)\cap N(t)|
\le
|A_t\setminus A_r|
+
|Y_b\cap N_R(t)|.
]

Since (bt) is a nonedge of codegree at least (2), MC-B follows.

MC-A is symmetric, using the nonedge (at). Its common B-neighbours must lie in (B_t\setminus B_r), while its common (R)-neighbours are (X_a\cap N_R(t)). ∎

---

## Skeleton-only corollary

Let

[
\pi_R(t\mid r)
==============

|N_R(t)\setminus N_R(r)|.
]

Then

[
B_r\setminus B_t\neq\varnothing
\Longrightarrow
|A_t\setminus A_r|+\pi_R(t\mid r)\ge2,
\tag{PN-B}
]

and symmetrically

[
A_r\setminus A_t\neq\varnothing
\Longrightarrow
|B_t\setminus B_r|+\pi_R(t\mid r)\ge2.
\tag{PN-A}
]

To see this, choose (b\in B_r\setminus B_t). Since (r\in Y_b) and (Y_b) is independent, every vertex of (Y_b\cap N_R(t)) lies outside (N_R(r)). This includes the possibility that the common (R)-neighbour is (r) itself, because (r\notin N_R(r)). Therefore

[
Y_b\cap N_R(t)
\subseteq
N_R(t)\setminus N_R(r).
]

The previous isolated-support lemma is precisely the case (\pi_R(t\mid r)=0).

---

# Why this directly targets the current profiles

The new information is strongest when two (R)-vertices have equal or nearly equal (R)-neighbourhoods.

### When (c_2=|S2|=2)

Every (h\in D13) has at least two neighbours in (S2), and (D13) has no other possible (R)-neighbour class. Hence

[
N_R(h)=S2
\qquad\text{for every }h\in D13.
]

Thus all (D13)-vertices are (R)-twins. For distinct (h,h'\in D13),

[
\pi_R(h\mid h')=0.
]

Therefore the full isolated-style separation applies between every ordered pair of (D13)-vertices:

[
B_{h'}\setminus B_h\neq\varnothing
\Longrightarrow
|A_h\setminus A_{h'}|\ge2,
]

and symmetrically on A/B.

### When (c_4=|S3|=2)

Likewise every (y\in D12) satisfies

[
N_R(y)=S3,
]

so the same full separation applies between all (D12)-vertices.

Eight of the ten top profiles you listed have either (c_2=2) or (c_4=2). Thus this cut reaches non-(T) vertices in most of the current high-frequency core; the existing isolated-support cut cannot do that.

I cannot safely claim a complete row closure from the displayed ((p,e_R,M)) data alone, because the result still depends on the detailed A/B support arrangements.

---

# Strongest CP-SAT encoding

Let

[
C_A(t,r)=|A_t\cap A_r|,
\qquad
C_B(t,r)=|B_t\cap B_r|.
]

Let

[
R_B(b,t)=|Y_b\cap N_R(t)|,
\qquad
R_A(a,t)=|X_a\cap N_R(t)|.
]

These are normally already present as components of the R/R and B/R or A/R codegree expressions.

For every ordered pair (r\ne t) and every (b\in B), add

[
\boxed{
\alpha_t-C_A(t,r)+R_B(b,t)
-2Y_{b,r}+2Y_{b,t}
\ge0.
}
\tag{CP-B}
]

For every ordered pair (r\ne t) and every (a\in A), add

[
\boxed{
\beta_t-C_B(t,r)+R_A(a,t)
-2X_{a,r}+2X_{a,t}
\ge0.
}
\tag{CP-A}
]

These inequalities require no trigger Boolean:

* if (Y_{b,r}=1) and (Y_{b,t}=0), CP-B becomes MC-B;
* in every other case its right-hand trigger contribution is (0) or negative, while
  [
  \alpha_t-C_A(t,r)+R_B(b,t)\ge0.
  ]

The A-side argument is identical.

Conceptual C++:

```cpp
for (int t = 0; t < q; ++t) {
  for (int r = 0; r < q; ++r) {
    if (r == t) continue;

    for (int b = 0; b < num_b; ++b) {
      // alpha[t]
      // - common_A_support[t][r]
      // + common_R_of_B_and_R[b][t]
      // - 2 * Y[b][r]
      // + 2 * Y[b][t] >= 0
      model.AddGreaterOrEqual(
          alpha[t]
          - common_a_rr[t][r]
          + common_r_br[b][t]
          - 2 * y_state[b][r]
          + 2 * y_state[b][t],
          0);
    }

    for (int a = 0; a < num_a; ++a) {
      model.AddGreaterOrEqual(
          beta[t]
          - common_b_rr[t][r]
          + common_r_ar[a][t]
          - 2 * x_state[a][r]
          + 2 * x_state[a][t],
          0);
    }
  }
}
```

If the C++ wrapper does not overload arithmetic in this form, build the same weighted `LinearExpr`.

If (R_B(b,t)) is not already available, define exact conjunctions

[
z_{btu}=Y_{b,u}\wedge e_{tu}
]

and set

[
R_B(b,t)=\sum_{u\in R}z_{btu}.
]

The symmetric construction gives (R_A(a,t)). With Boolean conjunctions, clauses or exact multiplication equalities may be used; CP-SAT operates over integer constraints, and products must be explicitly linearized or represented by `AddMultiplicationEquality`. ([Google for Developers][1])

For the current (6+6) convention this adds only

[
2\cdot13\cdot12\cdot6=1872
]

linear inequalities, with no new trigger variables if the existing common-neighbour terms are reused.

---

# Cheaper aggregate encoding

For a smaller skeleton/state-support layer, define

[
\Delta^B_{rt}=|B_r\setminus B_t|
=\beta_r-C_B(r,t),
]

and a Boolean (z^B_{rt}) satisfying

[
z^B_{rt}=1
\iff
\Delta^B_{rt}\ge1.
]

Since (|B|\le6), exact reification can be imposed by

```text
DeltaB[r][t] >= zB[r][t]
DeltaB[r][t] <= 6*zB[r][t].
```

Also define

[
\pi_R(t\mid r)
=d_R(t)-C_R(t,r),
]

where

[
C_R(t,r)=|N_R(t)\cap N_R(r)|.
]

Then add

[
\alpha_t-C_A(t,r)+\pi_R(t\mid r)
\ge2z^B_{rt}.
]

Add the symmetric A version.

This aggregate form is smaller, but the witness-resolved CP-B/CP-A inequalities are strictly stronger because they use the actual value of (R_B(b,t)), not the maximum possible private-neighbour count.

---

# Recommended finite experiment

Add the witness-resolved constraints under a new flag such as

```text
--mixed-codegree-projection
```

and rerun the 242 rows with:

```text
anti-tightness
class-uniform Psi
isolated-support
mixed-codegree-projection
```

at the same 30-second row timeout.

For implementation validation, first enable CP-B/CP-A only when (t\in T). That restriction should reproduce the mathematical content of isolated-support separation. Then enable it for all (t\in R). Report results separately for:

```text
c2=2 or c4=2
versus
c2>2 and c4>2.
```

A concentration of new closures in the first family would directly validate the skeleton-twin mechanism.

This is preferable to introducing another reroot assumption: it is a globally valid projection of constraints already in the verifier and attacks the exact interface where the current model must otherwise combine B/R or A/R codegree, triangle-freeness, and state overlap vertex by vertex.

## Weakest steps

1. The strengthening is logically redundant with the fully exact mixed-codegree model; its value is improved propagation, so no specific number of additional closures can be guaranteed without running it.

2. The variables (C_A,C_B,R_A,R_B) must represent the stated exact intersections. Using total A/R or B/R codegree in place of the (R)-only term would make the cut largely tautological.

3. The profile-twin consequences for (c_2=2) and (c_4=2) are exact, but they do not by themselves prove any complete ((p,e_R,M)) row infeasible.

4. The anti-tightness cut remains conditional on H14 being a complete reroot closure, rather than closure of only selected original-root profiles.

[1]: https://developers.google.com/optimization/cp/cp_solver?utm_source=chatgpt.com "CP-SAT Solver | OR-Tools"
