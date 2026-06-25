PROVED: remove two rows before any further SAT

If these have not already been hard-coded, the following terminal rows should be deleted immediately:

(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(2,6,6,0,17,20),
(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(3,5,5,1,18,19).

The proof is the same terminal-tight equality argument from the earlier reduction: in each row the local lower bounds on R-edges are tight, so all non-doubleton R-vertices become C-tight, hence terminal degree 8. The resulting R-degree sum contradicts

r∈R
∑
	

deg(r)=U+cap+2e
R
	

.

So if V218 still lists them, the first action is to remove them from the scalar frontier.

Recommended next finite target
FINITE-CERTIFICATE-NEEDED, but highest leverage

Attack:

(z,s
1
	

,s
2
	

,d,p,e
R
	

,cap)=(4,4,4,2,21,16,74).
	


This should be the next row before descending z8 to p=20.

Reason:

It uses the already-enumerated p=21 A−B template family.

The R-category is forced.

The Z-to-D skeleton is forced.

The S
1
	

S
2
	

 graph has only two canonical forms.

The terminal defect budget forces exact A/B-state sizes for Z and singleton vertices.

There is a strong new zero-union capacity cut:

	

z∈Z
⋃
	

X
z
	

	

+
	

z∈Z
⋃
	

Y
z
	

	

≤7.

That makes this row structurally smaller than z8,p=20 and probably smaller than z6,p=21.

PROVED: the z4,p21 R-category is forced

Consider

(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(4,4,4,2,21,16).

Let

x=S
12
	

.

Each S
1
	

-vertex has at least two S
2
	

-neighbours, so

x≥4⋅2=8.

Similarly from the S
2
	

-side.

For a zero vertex z, write

P
z
	

=N
R
	

(z)∩S
1
	

,Q
z
	

=N
R
	

(z)∩S
2
	

,F
z
	

=N
R
	

(z)∩D.

Since ∣D∣=2, local domination says

∣P
z
	

∣+∣F
z
	

∣≥2,
∣Q
z
	

∣+∣F
z
	

∣≥2.

The minimum number of R-edges from one zero vertex into S
1
	

∪S
2
	

∪D is 2, achieved only when

∣F
z
	

∣=2,P
z
	

=Q
z
	

=∅.

Therefore the zero vertices contribute at least

4⋅2=8

non-ZZ R-edges.

Hence

e
R
	

=ZZ+ZS
1
	

+ZS
2
	

+ZD+S
12
	

≥0+8+8=16.

But here e
R
	

=16. Therefore equality holds everywhere:

ZZ=0,ZS
1
	

=0,ZS
2
	

=0,ZD=8,S
12
	

=8.
	


Moreover:

every zero vertex is adjacent to both D-vertices;

every singleton vertex has exactly two neighbours on the opposite singleton side;

the S
1
	

S
2
	

-graph is 2-regular on 4+4 vertices.

Thus the S
1
	

S
2
	

 graph has only two canonical possibilities:

C
8
	

orC
4
	

+C
4
	

.
	

PROVED: exact terminal state sizes in this row

For every zero vertex z∈Z,

d
R
	

(z,U
1
	

)=2,d
R
	

(z,U
2
	

)=2.

So every zero is C-tight. Terminal normalization gives

deg(z)=8.

Since zero vertices have no C-label and d
R
	

(z)=2,

m
z
	

=∣X
z
	

∣+∣Y
z
	

∣=8−2=6.

Also xz and yz nonedge-codegree force

∣X
z
	

∣≥2,∣Y
z
	

∣≥2.

So for every z∈Z,

m
z
	

=6,∣X
z
	

∣≥2,∣Y
z
	

∣≥2.
	


For every singleton vertex s∈S
1
	

∪S
2
	

, it has exactly two opposite-singleton neighbours. Hence it is C-tight, and terminal normalization gives

deg(s)=8.

Since ∣ℓ(s)∣=1 and d
R
	

(s)=2,

m
s
	

=8−1−2=5.

Also xs and ys nonedge-codegree force

∣X
s
	

∣≥1,∣Y
s
	

∣≥1.

Thus

m
s
	

=5,∣X
s
	

∣≥1,∣Y
s
	

∣≥1.
	


The cap identity gives

r∈R
∑
	

m
r
	

=74.

The four zero vertices contribute

4⋅6=24.

The eight singleton vertices contribute

8⋅5=40.

Therefore the two doubleton vertices must contribute

m
d
1
	

	

+m
d
2
	

	

=10.
	


Equivalently,

(6−m
d
1
	

	

)+(6−m
d
2
	

	

)=2.
	

PROVED: p=21 gives m
r
	

≤7

For any r∈R, X
r
	

×Y
r
	

 avoids E(A,B). Hence X
r
	

∪Y
r
	

 is an independent set of the A−B graph P.

If m
r
	

=8, then the universal δ(P)≥2 condition forces

∣X
r
	

∣=∣Y
r
	

∣=4.

Then P has an empty 4×4 rectangle. So all P-edges lie outside that rectangle, in at most

36−16=20

cells. But p=21, contradiction.

Therefore

p=21⟹m
r
	

≤7∀r∈R.
	


For the two doubletons in the target row, this means

m
d
j
	

	

≤7,

and together with m
d
1
	

	

+m
d
2
	

	

=10, the possible pairs are

(3,7),(4,6),(5,5),(6,4),(7,3).
PROVED: zero-union capacity cut

In this row, each doubleton vertex is adjacent to every zero vertex.

For an R-edge zd, triangle-freeness forces

X
z
	

∩X
d
	

=∅,Y
z
	

∩Y
d
	

=∅.

Define

U
A
Z
	

:=
z∈Z
⋃
	

X
z
	

,U
B
Z
	

:=
z∈Z
⋃
	

Y
z
	

.

Then for each d∈D,

X
d
	

⊆A∖U
A
Z
	

,
Y
d
	

⊆B∖U
B
Z
	

.

Therefore

m
d
	

≤12−∣U
A
Z
	

∣−∣U
B
Z
	

∣.

Since

m
d
1
	

	

+m
d
2
	

	

=10,

we get

2(12−∣U
A
Z
	

∣−∣U
B
Z
	

∣)≥10.

Thus

∣U
A
Z
	

∣+∣U
B
Z
	

∣≤7.
	


But each zero state has size 6, so

∣U
A
Z
	

∣+∣U
B
Z
	

∣≥6.

Hence only two cases are possible:

∣U
A
Z
	

∣+∣U
B
Z
	

∣=6or7.
	


If the union size is 6, then all four zero vertices have exactly the same A/B-state.

If the union size is 7, each zero state is a 6-subset of a fixed 7-coordinate set.

This is the main reason this row should close quickly.

Why this row before z8,p20 or z6,p21
PROVED / FINITE-CERTIFICATE-NEEDED comparison
z8,p20
(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(8,0,0,6,20,17).

Local domination gives

ZD≥16.

So the categories are only

(ZZ,ZD)=(0,17)or(1,16).

This is small, but it requires a new p=20 A−B template family. Also p=20 allows m
r
	

=8, unlike p=21, so the state space is looser.

z6,p21
(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(6,2,2,4,21,16).

This row is also forced:

S
12
	

=4,ZD=12,ZZ=ZS
1
	

=ZS
2
	

=0.

But the Z-to-D skeleton is a 6×4 bipartite graph with every zero row-sum 2, so there are still nontrivial ZD-skeleton orbits.

z4,p21
(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(4,4,4,2,21,16).

This has:

ZD=8

and because ∣D∣=2, every zero is adjacent to both doubletons. So the zero-to-doubleton skeleton is completely fixed.

The only R-skeleton choice is:

S
1
	

S
2
	

=C
8
	

orC
4
	

+C
4
	

.

Therefore

z4,p21
	


has the smallest structural branching among the unclosed p≥14 rows using already-cached p=21 templates.

Exact C++ verifier constraints for the next run
Target
(z,s
1
	

,s
2
	

,d,p,e
R
	

,cap)=(4,4,4,2,21,16,74).
	

Forced category

Hard-code:

(ZZ,ZS
1
	

,ZS
2
	

,ZD,S
12
	

)=(0,0,0,8,8).
	

R-skeletons

Use exactly two S
1
	

S
2
	

 skeletons:

C
8
	

	


and

C
4
	

+C
4
	

	

.

Also hard-code:

each zero is adjacent to both doubletons;

no zero-zero edges;

no zero-singleton edges;

no singleton-doubleton edges;

no doubleton-doubleton edges.

A−B template family

Use the already enumerated canonical p=21 A−B templates:

10951 templates
	


with δ(P)≥2.

For each template P, precompute the state table

S(P)={(X,Y):X⊆A, Y⊆B, X×Y∩E(P)=∅}.

Hard-filter states by m=∣X∣+∣Y∣≤7.

State constraints

For every zero vertex z:

∣X
z
	

∣+∣Y
z
	

∣=6,∣X
z
	

∣≥2,∣Y
z
	

∣≥2.
	


For every singleton vertex s∈S
1
	

∪S
2
	

:

∣X
s
	

∣+∣Y
s
	

∣=5,∣X
s
	

∣≥1,∣Y
s
	

∣≥1.
	


For the two doubletons d
1
	

,d
2
	

:

∣X
d
1
	

	

∣+∣Y
d
1
	

	

∣+∣X
d
2
	

	

∣+∣Y
d
2
	

	

∣=10.
	


Also

∣X
d
j
	

	

∣+∣Y
d
j
	

	

∣≤7
	


for each j.

Zero-union cut

Hard-code:

6≤
	

z∈Z
⋃
	

X
z
	

	

+
	

z∈Z
⋃
	

Y
z
	

	

≤7.
	


Equivalently, branch into:

zero-union size 6
	


and

zero-union size 7
	

.

If union size 6, all four zero states are identical.

For each doubleton d, require:

X
d
	

∩
z∈Z
⋃
	

X
z
	

=∅,
	

Y
d
	

∩
z∈Z
⋃
	

Y
z
	

=∅.
	


This follows from the ZD-edge disjointness and should be imposed before generic edge checks.

R-edge common-neighbour zero checks

For every R-edge rr
′
, enforce:

∣ℓ(r)∩ℓ(r
′
)∣+∣X
r
	

∩X
r
′
	

∣+∣Y
r
	

∩Y
r
′
	

∣+∣N
R
	

(r)∩N
R
	

(r
′
)∣=0.
	


In this row, the important edge types are:

Z−D;

S
1
	

−S
2
	

.

For Z−D, the only nontrivial part is A/B-disjointness, already strengthened by the zero-union cut.

For S
1
	

−S
2
	

, enforce:

X
s
	

∩X
t
	

=∅,Y
s
	

∩Y
t
	

=∅

for every S
1
	

S
2
	

-edge.

R/R nonedge-codegree checks

After fixing the S
1
	

S
2
	

 skeleton, enforce for every R-nonedge rr
′
:

∣ℓ(r)∩ℓ(r
′
)∣+∣X
r
	

∩X
r
′
	

∣+∣Y
r
	

∩Y
r
′
	

∣+∣N
R
	

(r)∩N
R
	

(r
′
)∣≥2.
	


Important special cases to hard-code for speed:

Z−Z

Every pair of zero vertices shares both doubletons as common R-neighbours, so Z−Z nonedges are automatically satisfied.

Z−S

There are no zero-singleton R-edges and no common R-neighbours. Label overlap is 0. Therefore require:

∣X
z
	

∩X
s
	

∣+∣Y
z
	

∩Y
s
	

∣≥2
	


for every z∈Z, s∈S
1
	

∪S
2
	

.

missing S
1
	

S
2
	

 pairs

For s∈S
1
	

, t∈S
2
	

, if st∈
/
E
R
	

, then there is no label overlap and no common R-neighbour. Therefore require:

∣X
s
	

∩X
t
	

∣+∣Y
s
	

∩Y
t
	

∣≥2.
	

S−D

For s∈S
i
	

, d∈D, the label overlap is 1. There are no common R-neighbours. Therefore require:

∣X
s
	

∩X
d
	

∣+∣Y
s
	

∩Y
d
	

∣≥1.
	

D−D

The two doubletons have label overlap 2, so their R/R nonedge-codegree is automatically satisfied.

Rectangle two-cover

For every missing A−B cell (a,b)∈
/
E(P), enforce:

∣{r∈R:a∈X
r
	

, b∈Y
r
	

}∣≥2.
	


Every A−B edge is automatically avoided by the state table.

A/B-degree constraints

For each a∈A:

∣{r:a∈X
r
	

}∣≥7−deg
P
	

(a).
	


For each b∈B:

∣{r:b∈Y
r
	

}∣≥7−deg
P
	

(b).
	


Also every A/B-vertex must see both root colours through R:

∀a∈A,∃r∈S
1
	

∪D with a∈X
r
	

,
∀a∈A,∃r∈S
2
	

∪D with a∈X
r
	

,

and similarly for every b∈B.

A/A, B/B, A/R, B/R codegrees

For a,a
′
∈A, a

=a
′
:

∣N
P
	

(a)∩N
P
	

(a
′
)∣+∣{r:a,a
′
∈X
r
	

}∣≥1.
	


For b,b
′
∈B:

∣N
P
	

(b)∩N
P
	

(b
′
)∣+∣{r:b,b
′
∈Y
r
	

}∣≥1.
	


For a∈
/
X
r
	

:

∣N
P
	

(a)∩Y
r
	

∣+∣{u∈N
R
	

(r):a∈X
u
	

}∣≥2.
	


For b∈
/
Y
r
	

:

∣N
P
	

(b)∩X
r
	

∣+∣{u∈N
R
	

(r):b∈Y
u
	

}∣≥2.
	

Rooted cuts

Use all exact Φ/Ψ cuts lazily or statically.

Since

p+e
R
	

=37,

the Φ-cut is:

M(W)+F
Φ
	

(W)≥∂
R
	

(W),
	


where

M(W)=
r∈W
∑
	

(∣X
r
	

∣+∣Y
r
	

∣),
F
Φ
	

(W)=
i=1
∑
2
	

min(∣U
i
	

∩W∣, 8−∣U
i
	

∩W∣).

The two Ψ-orientations are:

e
R
	

−∂
R
	

(W)+F
Ψ
	

(W)+M
A
	

(W)+M
B
	

(R∖W)≥37,
	

e
R
	

−∂
R
	

(W)+F
Ψ
	

(W)+M
B
	

(W)+M
A
	

(R∖W)≥37,
	


where

F
Ψ
	

(W)=2+
i=1
∑
2
	

min(∣U
i
	

∩W∣, 6−∣U
i
	

∩W∣).
Suggested priority after this row

Run z4,p21 as above.

Then run z6,p21:

(6,2,2,4,21,16),

with forced

(ZZ,ZS
1
	

,ZS
2
	

,ZD,S
12
	

)=(0,0,0,12,4).

Then run z8,p20:

(8,0,0,6,20,17),

with categories

(ZZ,ZD)=(0,17)or(1,16).

This needs p=20 template enumeration and allows m=8, so I would not do it before the forced p=21 rows.

Command-level next experiment target
row = (z=4,s1=4,s2=4,d=2,p=21,eR=16,cap=74)
	


Hard-code:

category = (ZZ=0, ZS1=0, ZS2=0, ZD=8, S12=8)
	


Use:

P-templates = canonical p=21 templates, count 10951
	


Use exactly two R-skeletons:

S12-skeleton in {C8, C4+C4}
	


Add before SAT:

m
z
	

=6 ∀z∈Z,m
s
	

=5 ∀s∈S
1
	

∪S
2
	

,m
d
1
	

	

+m
d
2
	

	

=10
	

6≤
	

Z
⋃
	

X
z
	

	

+
	

Z
⋃
	

Y
z
	

	

≤7
	

X
d
	

∩
Z
⋃
	

X
z
	

=∅,Y
d
	

∩
Z
⋃
	

Y
z
	

=∅(d∈D)
	


Then enforce full R/R, rectangle two-cover, A/R, B/R, A/A, B/B, and rooted Φ/Ψ checks.