The strongest safe next reduction for (w>0), starting with ((ZZ,ZD)=(1,20)), is **not** to reuse the (w=0) tight-zero formulas. The safe replacement is:

[
\textbf{dirty-aware tight-zero rerooting + exact zero–D nonedge visibility + a zero-skeleton projection cap.}
]

I would implement this before any fixed A/B-template enumeration.

---

# 1. Notation for the (w=1) category

Let

[
Z={z_1,\dots,z_8},\qquad D={8,9,10,11,12,13}.
]

Use:

[
x_{z,d}=1 \iff z\sim d,
]

[
\eta_{z,u}=1 \iff z\sim u\quad(z,u\in Z),
]

[
n_{z,v}=1 \iff z\sim v\quad(v\in A\cup B),
]

[
y_{v,d}=1 \iff v\sim d.
]

Define:

[
d_D(z):=\sum_{d\in D}x_{z,d},
]

[
\gamma(z):=\sum_{u\in Z\setminus{z}}\eta_{z,u},
]

[
m_z:=\sum_{v\in A\cup B}n_{z,v},
]

[
c_d:=\sum_{z\in Z}x_{z,d},
]

[
m_d:=\sum_{v\in A\cup B}y_{v,d}.
]

For ((ZZ,ZD)=(1,20)):

```text
sum_{z<u} eta[z,u] = 1
sum_{z,d} x[z,d] = 20
```

The unique (ZZ)-edge has two dirty endpoints; all other zeros are clean.

---

# 2. PROVED: the (ZZ)-edge endpoints have disjoint D-rows

If (\eta_{z,u}=1), then for every (d\in D),

[
x_{z,d}+x_{u,d}\le 1.
]

Otherwise (z,u,d) would form a triangle.

### CP-SAT encoding

```text
for z<u in Z:
    for d in D:
        eta[z,u] + x[z,d] + x[u,d] <= 2
```

Also, no A/B vertex can be adjacent to both endpoints of a (ZZ)-edge:

```text
for z<u in Z:
    for v in AUB:
        eta[z,u] + n[z,v] + n[u,v] <= 2
```

This is essential for (w>0). It replaces several (ZZ=0)-only shortcuts.

---

# 3. PROVED: exact zero–D nonedge visibility with a (ZZ)-correction

For a zero (z) and a D-column (d) with (x_{z,d}=0), the pair ((z,d)) is a nonedge. Its common neighbours can only be:

1. A/B vertices (v) with (n_{z,v}=1) and (y_{v,d}=1);
2. (ZZ)-neighbours (u) of (z) with (x_{u,d}=1).

Thus the safe (w>0) replacement for outside-D visibility is:

[
\boxed{
x_{z,d}=0
\Longrightarrow
\sum_{v\in A\cup B} n_{z,v}y_{v,d}
+
\sum_{u\in Z\setminus{z}}\eta_{z,u}x_{u,d}
\ge 2.
}
]

For (w=0), the second term vanishes and this becomes the old outside-D visibility cut.

### CP-SAT encoding

Introduce:

```text
abcom[z,d,v] = n[z,v] AND y[v,d]
zzcom[z,d,u] = eta[z,u] AND x[u,d]
```

Then:

```text
for z in Z:
    for d in D:
        if x[z,d] == 0:
            sum_v abcom[z,d,v] + sum_u zzcom[z,d,u] >= 2
```

Guarded linear form:

```text
sum_v abcom[z,d,v] + sum_u zzcom[z,d,u] >= 2 * (1 - x[z,d])
```

This is safe and should be added globally for all (w\ge1).

---

# 4. PROVED, with frontier-dependence flagged: dirty-aware reroot for (d_D(z)=2)

Let (z\in Z) satisfy

[
d_D(z)=2,\qquad N_D(z)={a,b}.
]

Reroot at ((c,z)), where (c) is one original (C)-vertex.

The new common-neighbour set is still exactly:

[
C^*={a,b}.
]

This remains true even if (z) has a (ZZ)-neighbour, because zero vertices are not adjacent to (c).

The new A-side is:

[
A^*={x,y}\cup (D\setminus{a,b}),
]

so

[
|A^*|=6.
]

The new B-side is:

[
B^*=N_{A\cup B}(z)\cup N_Z(z).
]

Therefore:

[
|B^*|=m_z+\gamma(z).
]

## 4.1 Terminal equality

If the (q<14) frontier is already closed, then (B^*) cannot have size (>6). The minimum-degree lower bound gives

[
m_z+d_D(z)+\gamma(z)\ge8,
]

so with (d_D(z)=2),

[
m_z+\gamma(z)\ge6.
]

Hence:

[
\boxed{d_D(z)=2\Longrightarrow m_z+\gamma(z)=6.}
]

### Dependence

This equality depends on the audited closure of the (q<14) reroot frontier. Without that closure, only

[
m_z+\gamma(z)\ge6
]

is safe.

### CP-SAT encoding

```text
if dD[z] == 2:
    m_z + gamma[z] = 6
```

or guarded by a literal `tightD2[z]`.

---

# 5. PROVED, with cap-frontier dependence: touched-column equality survives, but only with dirty-aware rerooting

Let (z) be as above with (N_D(z)={a,b}). Define:

[
\sigma_d:=c_d+m_d.
]

In the rerooted instance, the new label-weight (U^*) relative to (C^*={a,b}) is exactly:

[
U^*=\sigma_a+\sigma_b.
]

Reason: for each (d\in{a,b}), the vertices of (R^*) adjacent to (d) are:

* the other original (C)-vertex;
* all old zero neighbours of (d) except the root (z);
* all old A/B neighbours of (d).

This gives:

[
(c_d-1)+m_d+1=c_d+m_d=\sigma_d.
]

If (z) has a (ZZ)-neighbour, that neighbour lies in (B^*), not (R^*), and by triangle-freeness it is not adjacent to (a) or (b). So the formula is unchanged.

The D-column degree lower bound gives:

[
\sigma_d=c_d+m_d\ge6.
]

If the cap(<74) reroot frontier is closed, then (U^*>12) is impossible. Hence:

[
\sigma_a+\sigma_b=12.
]

Together with (\sigma_a,\sigma_b\ge6), this yields:

[
\boxed{c_a+m_a=6,\qquad c_b+m_b=6.}
]

### Dependence

This touched-column equality depends on cap(<74) reroot closure. Without that closure, the safe statement is only:

[
c_a+m_a\ge6,\qquad c_b+m_b\ge6.
]

### CP-SAT encoding

For every (d_D(z)=2) zero with (N_D(z)={a,b}):

```text
c[a] + mD[a] = 6
c[b] + mD[b] = 6
```

guarded by the `tightD2[z]` row literal and the cap-frontier certificate.

---

# 6. PROVED: the old (p^*+e_R^*=37) formula is unsafe, but the set-based formula is safe

For (w>0), do **not** use the old (ZZ=0) closed form for (p^*_z,e^*_{R,z}). If (z) has a (ZZ)-neighbour (u), then (u\in B^*), and edges from (u) to (D\setminus{a,b}) contribute to (p^*). The old formula omits these terms.

The safe definition is set-based.

For (d_D(z)=2), (N_D(z)={a,b}):

[
A^*={x,y}\cup(D\setminus{a,b}),
]

[
B^*=N_{A\cup B}(z)\cup N_Z(z),
]

[
R^*=V(G)\setminus\bigl({c,z}\cup C^*\cup A^*\cup B^*\bigr).
]

Then impose:

[
\boxed{p^*_z+e^*_{R,z}=37}
]

using the actual edge sets:

[
p^*_z=e(A^*,B^*),
]

[
e^*_{R,z}=e(R^*).
]

### Expanded safe formula for (p^*_z)

[
p^*_z
=====

m_z
+
\sum_{d\in D\setminus{a,b}}\sum_{v\in A\cup B} n_{z,v}y_{v,d}
+
\sum_{u\in Z\setminus{z}}\eta_{z,u}
\sum_{d\in D\setminus{a,b}}x_{u,d}.
]

The last term is exactly the dirty (ZZ)-neighbour correction.

### Expanded safe formula for (e^*_{R,z})

[
e^*_{R,z}
=========

\sum_{\alpha\in A,\ \beta\in B}
P_{\alpha,\beta}(1-n_{z,\alpha})(1-n_{z,\beta})
]

[
+
\sum_{u\in Z\setminus{z}}
\sum_{v\in A\cup B}
n_{u,v}(1-\eta_{z,u})(1-n_{z,v})
]

[
+
\sum_{{u,u'}\subseteq Z\setminus{z}}
\eta_{u,u'}(1-\eta_{z,u})(1-\eta_{z,u'}).
]

The final term is also important: if (z) is clean, the unique (ZZ)-edge elsewhere remains inside (R^*) and contributes to (e_R^*).

### CP-SAT encoding

Use auxiliary AND literals for products such as:

```text
resAB[z,v] = 1 - n[z,v]
resZ[z,u]  = 1 - eta[z,u]
```

and for products:

```text
ab_res_edge[z,a,b] = P[a,b] AND resAB[z,a] AND resAB[z,b]
zero_ab_res_edge[z,u,v] = n[u,v] AND resZ[z,u] AND resAB[z,v]
zz_res_edge[z,u,u2] = eta[u,u2] AND resZ[z,u] AND resZ[z,u2]
```

Then impose:

```text
pstar[z] + eRstar[z] = 37
```

guarded by `tightD2[z]`.

---

# 7. PROVED: corrected reroot profile (D',L',R')

For (d_D(z)=2), (N_D(z)={a,b}), define:

[
D'_z
====

1
+
\sum_{u\in Z\setminus{z}}(1-\eta_{z,u})x_{u,a}x_{u,b}
+
\sum_{v\in A\cup B}(1-n_{z,v})y_{v,a}y_{v,b}.
]

The (+1) is the other original (C)-vertex, which becomes doubleton relative to ({a,b}).

Similarly:

[
L'_z
====

\sum_{u\in Z\setminus{z}}(1-\eta_{z,u})x_{u,a}(1-x_{u,b})
+
\sum_{v\in A\cup B}(1-n_{z,v})y_{v,a}(1-y_{v,b}),
]

[
R'_z
====

\sum_{u\in Z\setminus{z}}(1-\eta_{z,u})(1-x_{u,a})x_{u,b}
+
\sum_{v\in A\cup B}(1-n_{z,v})(1-y_{v,a})y_{v,b}.
]

Then the safe reroot profile constraints are:

```text
Dprime[z] in {1,2,3,4,6}
Dprime[z] + Lprime[z] = 6
Dprime[z] + Rprime[z] = 6
```

For a non-isolated tight pair, the old skeleton-safe cut also survives:

```text
Dprime[z] <= 4
```

because if (D'_z=6), then (L'_z=R'_z=0). Any other tight zero sharing exactly one endpoint with ({a,b}) remains in (R^*) and contributes a singleton. It cannot be the (ZZ)-neighbour of (z), since a (ZZ)-neighbour of (z) is disjoint from (N_D(z)) by triangle-freeness.

---

# 8. PROVED: basic (w=1) scalar consequences

Since (ZD=20) and every zero has (d_D(z)\ge2),

[
\sum_{z\in Z}(d_D(z)-2)=20-16=4.
]

Therefore there are at least four zeros with (d_D(z)=2).

The unique (ZZ)-edge has only two endpoints, so at least two of the (d_D=2) zeros are clean.

The sorted D-degree pair of the two dirty endpoints must be one of:

[
(2,2),\quad (2,3),\quad (2,4),\quad (3,3).
]

Reason: the two dirty D-rows are disjoint and each has size at least (2), so their total size is at most (6).

### CP-SAT branch

Let (u,v) be the unique (ZZ)-edge endpoints. Branch on:

```text
(dD[u], dD[v]) in {(2,2), (2,3), (2,4), (3,3)}
```

up to order.

This is the first small P-free branch I would add for ((1,20)).

---

# 9. PROVED: scalar-only arguments do not close ((1,20))

A pure scalar or zero-row argument cannot close ((1,20)) by itself. Here is a zero skeleton satisfying the basic row sums, (ZZ)-disjointness, (ZD=20), and plausible touched-column equalities.

Let the unique (ZZ)-edge join:

[
u={8,9,10},
\qquad
v={11,12,13}.
]

Let four clean tight zeros be:

[
t_1={8,11},\quad
t_2={8,12},\quad
t_3={9,11},\quad
t_4={10,13}.
]

Let the two remaining clean non-tight zeros be:

[
h_1={9,12,13},
\qquad
h_2={10,11,12}.
]

Then:

[
\sum_z d_D(z)=20,
]

the dirty rows are disjoint, and the D-column loads are:

[
c=(3,3,3,4,4,3).
]

All six D-columns are touched by clean tight zeros, so touched equality would give:

[
m_D=(3,3,3,2,2,3),
]

which is scalar-consistent.

The zero lower bounds are also scalar-consistent:

* four clean tight zeros require (m_z=6);
* two dirty degree-3 endpoints require (m_z\ge4);
* two clean degree-3 zeros require (m_z\ge5).

The scalar lower total is:

[
(3+3+3+2+2+3)+4\cdot6+2\cdot4+2\cdot5=58<74.
]

So there is no contradiction from scalar sums alone. A finite projection or full CP-SAT certificate is needed.

---

# 10. FINITE-CERTIFICATE-NEEDED: P-free projection cap for ((1,20))

The right certificate before fixed A/B-template enumeration is the same kind of projection cap used successfully in (w=0), but with the (ZZ)-edge included.

For a fixed zero skeleton (\mathcal Z), define integer variables:

[
N_{S,U}\in{0,\dots,12},
]

where:

[
\varnothing\ne S\subseteq D,
]

[
U\subseteq Z.
]

Here (S) is the D-state of an A/B vertex and (U) is the set of zero neighbours of that A/B vertex.

Allow ((S,U)) only if:

### Triangle compatibility with D

[
z\in U\Longrightarrow S\cap N_D(z)=\varnothing.
]

### Triangle compatibility with the (ZZ)-edge

If (\eta_{z,u}=1), then:

[
{z,u}\nsubseteq U.
]

### A/B visibility

[
S\ne\varnothing.
]

Then impose:

```text
sum_{S,U} N[S,U] = 12
```

D-column counts:

```text
for d in D:
    sum_{S,U: d in S} N[S,U] = m_d        # if d is touched by a D-tight zero
    sum_{S,U: d in S} N[S,U] >= 6 - c_d  # otherwise only degree lower
    sum_{S,U: d in S} N[S,U] <= 8
```

For every (d_D(z)=2) zero, impose:

```text
sum_{S,U: z in U} N[S,U] = 6 - gamma[z]
```

For every other zero:

```text
sum_{S,U: z in U} N[S,U] >= 8 - dD[z] - gamma[z]
sum_{S,U: z in U} N[S,U] <= 8
```

Zero-zero nonedge codegrees:

```text
for zero pair z<u:
    if eta[z,u] == 0:
        req = 2 - |N_D(z) intersect N_D(u)|
        if req > 0:
            sum_{S,U: z in U and u in U} N[S,U] >= req
```

Adjacent (ZZ)-pairs do not get a nonedge-codegree lower bound; instead, they already have:

```text
no type U may contain both endpoints
```

Reroot profile constraints for every (d_D(z)=2) zero with row ({a,b}):

```text
Dprime[z] =
    1
  + number of residual zero rows containing both a,b
  + sum_{S,U: z not in U and a in S and b in S} N[S,U]

Lprime[z] =
    number of residual zero rows containing a not b
  + sum_{S,U: z not in U and a in S and b not in S} N[S,U]

Rprime[z] =
    number of residual zero rows containing b not a
  + sum_{S,U: z not in U and a not in S and b in S} N[S,U]

Dprime[z] in {1,2,3,4,6}
Dprime[z] + Lprime[z] = 6
Dprime[z] + Rprime[z] = 6
```

If the tight pair is non-isolated:

```text
Dprime[z] <= 4
```

Projection objective:

```text
M_proj = sum_{S,U} (|S| + |U|) * N[S,U]
```

For each zero skeleton (\mathcal Z), solve:

```text
maximize M_proj
```

If the optimum is (\le73), add the guarded branch cut:

```text
skeleton_Z => M <= optimum
```

Since the real branch has:

```text
M = 74
```

that skeleton closes.

This certificate is P-free: it does not remember A/B templates, A/B edges, or fixed A/B incidence matrices.

---

# 11. Smallest residual branch to test first

The smallest hard residual branch is:

[
\boxed{
\text{dirty endpoint degrees }(3,3),
\quad
N_D(u)\sqcup N_D(v)=D,
\quad
\text{clean profile }4\text{ degree-2 zeros}+2\text{ degree-3 zeros}.
}
]

Canonical form:

```text
ZZ endpoints:
    u = {8,9,10}
    v = {11,12,13}

clean zeros:
    four rows of size 2
    two rows of size 3
```

This is the least constrained (w=1) branch because:

* neither dirty endpoint is (d_D=2), so no dirty tight reroot is available;
* the dirty endpoints help each other’s zero–D visibility across three columns;
* only four clean tight reroots are present;
* the total clean excess is minimal.

### Next CP-SAT branch inside this residual

Branch on the pair-skeleton of the four clean degree-2 zeros:

```text
pair_counts over the 15 D-pairs, sum = 4
```

Then branch on the two clean degree-3 rows only if the projection cap does not close the pair-skeleton.

For each such zero skeleton, add the projection cap above. This is the next finite certificate I would run before any A/B template enumeration.

---

# Weakest assumptions

The reductions above use only:

1. triangle-freeness;
2. (ZZ=1), (ZD=20);
3. root-to-R D-visibility for A/B vertices;
4. local zero–D and zero–zero nonedge-codegree lower bound (2);
5. (m_r\le8);
6. D-column degree lower bound (c_d+m_d\ge6);
7. zero degree lower bound (m_z+d_D(z)+\gamma(z)\ge8);
8. audited (q<14) closure for the equality (m_z+\gamma(z)=6) when (d_D(z)=2);
9. audited cap(<74) closure for touched-column equality (c_d+m_d=6);
10. audited q14/t2 reroot profile closure for (D'\in{1,2,3,4,6}), (D'+L'=D'+R'=6), and (p^*+e_R^*=37).

No fixed A/B-template enumeration is used.
