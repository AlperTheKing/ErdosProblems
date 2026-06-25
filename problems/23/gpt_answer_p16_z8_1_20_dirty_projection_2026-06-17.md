The next safe cut for (w=1) should be a **dirty-safe total-pair reroot cap**. It is smaller than a full projection certificate, it is P-free, and it immediately kills the old local witness row-count branch.

The key correction is: for (w>0), reroot formulas must count the unique (ZZ)-edge explicitly, but for a tight zero (z) with (N_D(z)={a,b}), the doubleton count after rerooting is still expressible by a very small original-coordinate quantity.

---

# 1. PROVED: dirty-safe total-pair reroot cap

Let

[
e={a,b}\subset D.
]

Define the **total zero pair multiplicity**

[
K_e:=|{z\in Z: a,b\in N_D(z)}|,
]

and the A/B double-state count

[
Q_e:=|{v\in A\cup B: v\sim a,\ v\sim b}|.
]

Suppose (z\in Z) is tight and

[
N_D(z)=e.
]

Reroot at ((c,z)), where (c) is one of the original two common neighbours.

Then the new common-neighbour pair is (e={a,b}). The doubletons in the rerooted (R^*) are exactly:

1. the other original (C)-vertex;
2. old zero vertices other than (z) that contain both (a,b);
3. A/B vertices that contain both (a,b).

If (z) is dirty, its unique (ZZ)-neighbour is in (B^*), not (R^*). But that neighbour is disjoint from (N_D(z)={a,b}) by triangle-freeness, so it would not have contributed to the doubleton count anyway.

Therefore

[
\boxed{D'_z=K_e+Q_e.}
]

Since the dirty-aware reroot profile still has

[
D'_z\in{1,2,3,4,6},
]

we get the safe pair-domain cut:

[
\boxed{K_e+Q_e\in{1,2,3,4,6}}
]

for every pair (e) used by at least one tight zero.

In particular:

[
K_e\le 6.
]

Moreover, if there is any zero (u\neq z) with exactly one of (a,b), then (u) remains in (R^*) and contributes a singleton. Hence (D'_z=6) is impossible. So in that case:

[
\boxed{K_e+Q_e\le 4.}
]

This singleton guard is stronger than the old “non-isolated tight pair” guard, because it sees **all zero rows**, not only tight rows.

---

# 2. Exact CP-SAT encoding for the total-pair cap

For every unordered D-pair (e={a,b}), introduce:

```text
bothZ[z,e] = x[z,a] AND x[z,b]
bothAB[v,e] = y[v,a] AND y[v,b]
singleZ[z,e] = (x[z,a] + x[z,b] == 1)
```

Then:

```text
K[e] = sum_z bothZ[z,e]
Q[e] = sum_v bothAB[v,e]
```

Let:

```text
hasTight[e] = OR_z (dD[z] == 2 AND x[z,a] == 1 AND x[z,b] == 1)
hasZeroSingleton[e] = OR_z singleZ[z,e]
```

Add:

```text
hasTight[e]  =>  K[e] + Q[e] in {1,2,3,4,6}
hasTight[e] AND hasZeroSingleton[e]  =>  K[e] + Q[e] <= 4
```

In OR-Tools style, the first is:

```text
model.AddLinearExpressionInDomain(
    K[e] + Q[e],
    cp_model.Domain.FromValues([1,2,3,4,6])
).OnlyEnforceIf(hasTight[e])
```

The second can be guarded by a conjunction literal:

```text
guard[e] = hasTight[e] AND hasZeroSingleton[e]
model.Add(K[e] + Q[e] <= 4).OnlyEnforceIf(guard[e])
```

This is safe with one (ZZ)-edge.

---

# 3. PROVED: the old local witness row counts are already impossible

Old narrowed witness:

```text
degree-2 rows:
  (8,13)^1
  (10,11)^3

degree-3 rows:
  (10,11,12)^4
```

Take the D-pair

[
e={10,11}.
]

Every one of the three tight rows ((10,11)) contains (e), and every one of the four degree-3 rows ((10,11,12)) also contains (e). Hence

[
K_{10,11}=7.
]

Since (e) is used by tight zeros, the pair-domain cut requires

[
K_{10,11}+Q_{10,11}\in{1,2,3,4,6}.
]

But

[
K_{10,11}+Q_{10,11}\ge 7.
]

Contradiction.

So that narrowed old witness row-count branch is P-free infeasible before any A/B-template enumeration.

Also, if your (c_d) means total zero-to-D column load, the same branch has

[
c_{10}=c_{11}=7,
]

which violates the touched-column bound (c_d\le4). If the solver still reports UNKNOWN on that exact row-count branch, the missing propagation is likely one of these two totals: either (K_{10,11}) is not linked to all zero rows, or touched (c_d) is not being computed as total zero-column load.

---

# 4. PROVED: dirty-aware footprint capacity cut

This is the broad scalar cut I would add for all (w=1) zero-degree profiles.

Let

[
t:=|{z\in Z:d_D(z)=2}|
]

be the number of tight zeros. In the four profiles:

[
t\in{4,5,6}.
]

Let (T_D\subseteq D) be the set of D-columns touched by at least one tight zero, and let

[
U_D:=D\setminus T_D,
\qquad
k:=|U_D|.
]

Let

[
c_U:=\sum_{d\in U_D} c_d.
]

Let

[
r_T:=|{z:d_D(z)=2,\ \gamma(z)=1}|
]

be the number of dirty endpoints that are tight zeros.

For tight zeros, the dirty-aware terminal equality gives

[
m_z+\gamma(z)=6,
]

so

[
\sum_{z:d_D(z)=2} m_z=6t-r_T.
]

For the (8-t) non-tight zeros, only use the safe upper bound

[
m_z\le 8.
]

Thus

[
\sum_{z\in Z}m_z
\le
6t-r_T+8(8-t)
=============

64-2t-r_T.
]

For D-columns touched by tight zeros,

[
m_d=6-c_d.
]

For untouched D-columns, use only

[
m_d\le8.
]

Since

[
\sum_{d\in D}c_d=20,
]

we get

[
\sum_{d\in D}m_d
\le
\sum_{d\in T_D}(6-c_d)+8k
=========================

# 6(6-k)-(20-c_U)+8k

16+2k+c_U.
]

Therefore:

[
\boxed{
M\le 80-2t-r_T+2k+c_U.
}
]

Since the branch has (M=74), every feasible branch must satisfy

[
\boxed{
2k+c_U\ge 2t-6+r_T.
}
]

This is a cheap P-free cut.

---

## Consequences by zero-degree profile

### Profile ((4,4,0,0))

Here (t=4). The cut is:

[
M\le72-r_T+2k+c_U.
]

So if all six columns are touched by tight zeros, then (k=c_U=0), and

[
M\le72-r_T\le72,
]

contradicting (M=74).

Thus in profile ((4,4,0,0)), any surviving branch must have at least one D-column not touched by any tight zero, and must satisfy:

[
2k+c_U\ge2+r_T.
]

### Profile ((5,2,1,0))

Here (t=5). The cut is:

[
M\le70-r_T+2k+c_U.
]

So every surviving branch must satisfy:

[
2k+c_U\ge4+r_T.
]

### Profiles ((6,0,2,0)) and ((6,1,0,1))

Here (t=6). The cut is:

[
M\le68-r_T+2k+c_U.
]

So every surviving branch must satisfy:

[
2k+c_U\ge6+r_T.
]

In particular, if (k\le1), then (2k+c_U\le4) because only the two non-tight zeros can hit untouched columns. Hence all (t=6) branches with at most one untouched D-column close immediately.

---

# 5. Exact CP-SAT encoding for the footprint capacity cut

Branch by the tight-footprint set (T_D). This is small: at most (2^6) masks, and many are impossible.

For a fixed footprint mask:

```text
Touched = fixed subset of D
Untouched = D \ Touched
k = len(Untouched)
cU = sum_{d in Untouched} c[d]
```

Let:

```text
rT = sum_z tight[z] AND dirty[z]
```

where:

```text
tight[z] = (dD[z] == 2)
dirty[z] = gamma[z] == 1
```

Then add:

```text
M <= 80 - 2*t - rT + 2*k + cU
```

Since (M=74), you can add the equivalent necessary condition:

```text
2*k + cU >= 2*t - 6 + rT
```

The upper-bound form is more auditable because it directly follows from the proof.

---

# 6. PROVED: zero-D visibility must keep the dirty correction

For (w=1), the safe zero-D nonedge visibility constraint is:

[
x_{z,d}=0
\Longrightarrow
\sum_{v\in A\cup B}n_{z,v}y_{v,d}
+
\sum_{u\in Z\setminus{z}}\eta_{z,u}x_{u,d}
\ge2.
]

Since (w=1), the second sum has at most one nonzero term. It is exactly the dirty correction: if the unique (ZZ)-neighbour of (z) sees (d), it supplies one common neighbour for the nonedge ((z,d)).

CP-SAT:

```text
abcom[z,d,v] = n[z,v] AND y[v,d]
zzcom[z,d,u] = eta[z,u] AND x[u,d]

sum_v abcom[z,d,v] + sum_u zzcom[z,d,u] >= 2 * (1 - x[z,d])
```

This should remain active even inside the projection certificate below.

---

# 7. FINITE-CERTIFICATE-NEEDED: zero-skeleton projection cap with one ZZ edge

I do not see a scalar-only contradiction for the whole ((1,20)) category. After the pair cap and footprint cut, there are still scalar-consistent zero skeletons.

A scalar-consistent example in profile ((4,4,0,0)):

```text
dirty endpoints:
  {8,9,13} -- {10,11,12}

tight rows:
  {8,10}
  {8,11}
  {9,10}
  {11,12}

remaining degree-3 rows:
  {9,12,13}
  {10,11,13}
```

Column loads are:

[
c=(3,3,4,4,3,3),
]

the dirty rows are disjoint, no tight pair has excessive total pair multiplicity, and the tight footprint leaves column (13) untouched. The footprint capacity cut gives only

[
M\le77,
]

so scalar capacity alone does not close it.

Therefore the next safe certificate is a finite zero-skeleton projection. This is still P-free: it does not enumerate A/B templates or A/B edge patterns.

---

## Projection variables

Fix a zero skeleton:

* zero rows (R_z=N_D(z));
* the unique (ZZ)-edge (\eta_{uv}=1).

For every allowed A/B projection type ((S,U)), introduce an integer variable

[
N_{S,U}\in{0,\dots,12}.
]

Here:

[
S\subseteq D
]

is the D-state of an A/B vertex, and

[
U\subseteq Z
]

is the set of zero neighbours of that A/B vertex.

Allow ((S,U)) only if:

```text
S != empty
for z in U:
    S ∩ R_z = empty
if eta[u,v] = 1:
    not (u in U and v in U)
```

The first condition is A/B D-visibility. The second is triangle-freeness through a zero-D edge. The third is triangle-freeness through the dirty (ZZ)-edge.

---

## Projection constraints

### A/B vertex count

```text
sum_{S,U} N[S,U] = 12
```

### D-column counts

For touched D-columns:

```text
sum_{S,U: d in S} N[S,U] = 6 - c[d]
```

For untouched D-columns:

```text
sum_{S,U: d in S} N[S,U] >= 6 - c[d]
sum_{S,U: d in S} N[S,U] <= 8
```

The lower bound is the D-vertex degree lower bound. The upper bound is (m_r\le8).

### Zero A/B degrees

For tight zeros:

```text
sum_{S,U: z in U} N[S,U] = 6 - gamma[z]
```

For non-tight zeros:

```text
sum_{S,U: z in U} N[S,U] >= 8 - dD[z] - gamma[z]
sum_{S,U: z in U} N[S,U] <= 8
```

### Zero-zero nonedge codegrees

For every zero pair (z,u) with (\eta_{z,u}=0):

```text
req = 2 - |R_z ∩ R_u|
if req > 0:
    sum_{S,U: z in U and u in U} N[S,U] >= req
```

For the dirty adjacent pair, do not impose a nonedge-codegree constraint; instead the allowed-type rule already forbids an A/B vertex from seeing both endpoints.

### Zero-D nonedge visibility with dirty correction

For every (z\in Z) and every (d\notin R_z):

```text
dirty_corr[z,d] = sum_{u in Z} eta[z,u] * 1_{d in R_u}

sum_{S,U: z in U and d in S} N[S,U] >= 2 - dirty_corr[z,d]
```

Since (w=1), `dirty_corr[z,d]` is (0) or (1).

### Total-pair reroot cap

For every D-pair (e={a,b}):

```text
K[e] = number of zero rows R_z with {a,b} subset R_z
Q[e] = sum_{S,U: a in S and b in S} N[S,U]
hasTight[e] = whether some tight zero has row {a,b}
singleZ[e] = whether some zero row contains exactly one of a,b
```

Then:

```text
if hasTight[e]:
    K[e] + Q[e] in {1,2,3,4,6}

if hasTight[e] and singleZ[e]:
    K[e] + Q[e] <= 4
```

This is the projection version of the dirty-safe reroot cap.

### Objective

```text
Mproj = sum_{S,U} (|S| + |U|) * N[S,U]
```

For each zero skeleton, solve:

```text
maximize Mproj
```

If the optimum is (\le73), add the guarded certificate cut:

```text
this_zero_skeleton => M <= optimum
```

Since the branch has (M=74), that zero skeleton closes.

This projection is a relaxation of the full CP-SAT verifier. Therefore any bound it proves is safe.

---

# 8. Smallest branch order for ((1,20))

Use this order before any fixed A/B-template enumeration:

1. Branch on zero-degree profile:

```text
(4,4,0,0)
(5,2,1,0)
(6,0,2,0)
(6,1,0,1)
```

2. Branch on dirty endpoint degree pair. Since dirty rows are disjoint, the only possible pairs are:

```text
(2,2), (2,3), (2,4), (3,3)
```

In profile ((6,1,0,1)), the degree-5 zero cannot be dirty, because a degree-5 D-row has complement size (1), while the dirty neighbour must have D-degree at least (2).

3. Branch on tight-footprint mask (T_D), and immediately apply:

```text
M <= 80 - 2*t - rT + 2*k + cU
```

4. Add the dirty-safe total-pair cap:

```text
hasTight[e] => K[e] + Q[e] in {1,2,3,4,6}
hasTight[e] AND singleZ[e] => K[e] + Q[e] <= 4
```

5. Only for remaining zero skeletons, run the zero-skeleton projection IP above.

The smallest hard residual to test first is:

```text
profile = (4,4,0,0)
dirty endpoint degrees = (3,3)
dirty rows are complementary 3-sets
tight footprint has at least one untouched column
2*k + cU >= 2
all tight pairs satisfy the total-pair cap
```

This is the least constrained scalar case because no tight zero is dirty, the dirty edge gives the maximum zero-D visibility correction, and untouched D-columns can carry extra A/B degree.

---

# Weakest assumptions used

The total-pair cap uses:

1. triangle-freeness;
2. the unique dirty (ZZ)-edge being disjoint in D-rows;
3. A/B D-visibility;
4. dirty-aware tight-zero reroot profile:
   [
   D'\in{1,2,3,4,6};
   ]
5. the reroot identity
   [
   D'_z=K_e+Q_e.
   ]

The footprint capacity cut uses:

1. (M=\sum_{r\in R}m_r=74);
2. (m_r\le8);
3. (ZD=20);
4. dirty-aware tight-zero equality:
   [
   d_D(z)=2\Rightarrow m_z+\gamma(z)=6;
   ]
5. touched-column equality:
   [
   d\text{ touched by a tight zero}\Rightarrow c_d+m_d=6.
   ]

The projection certificate uses only P-free data: zero rows, the unique (ZZ)-edge, triangle-freeness, local zero-zero and zero-D nonedge codegrees with dirty correction, A/B D-visibility, touched-column equality, (m_r\le8), and the dirty-safe total-pair reroot cap.

No fixed A/B-template enumeration is used.
