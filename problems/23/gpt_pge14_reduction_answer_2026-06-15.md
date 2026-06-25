PROVED: there is no m
r
	

≤6 baseline for all p≥14

Let

P=G[A,B],X
r
	

=N
A
	

(r),Y
r
	

=N
B
	

(r),m
r
	

=∣X
r
	

∣+∣Y
r
	

∣.

For every r∈R,

X
r
	

×Y
r
	

∩E(P)=∅,

because if a∈X
r
	

, b∈Y
r
	

, and ab∈E(P), then a,b,r form a triangle.

So X
r
	

∪Y
r
	

 is an independent set of the bipartite graph P. Since every A/B-vertex has at least two A−B neighbours,

δ(P)≥2.

If X⊆A, Y⊆B, and X∪Y is independent in P, then every vertex of X must send its at least two P-edges into B∖Y. Hence

∣B∖Y∣≥2whenever X

=∅.

Similarly,

∣A∖X∣≥2whenever Y

=∅.

Therefore

∣X∣+∣Y∣≤8.

Thus the correct universal bound is

m
r
	

≤8.
	


Moreover:

if m
r
	

=8, then necessarily ∣X
r
	

∣=∣Y
r
	

∣=4;

if p=21, then m
r
	

=8 is impossible, so m
r
	

≤7.

The last statement follows because an 8-state has a 4×4 empty rectangle X×Y. Then all 4⋅2 edges from X to B∖Y and all 2⋅4 edges from A∖X to Y are forced by minimum degree 2, and at most the remaining 2×2 block can be added. So p≤20.

So the p=13 defect proof cannot be copied blindly: for p≥14, some vertices may have m
r
	

=7 or 8, hence negative defect relative to the 6-baseline.

Still, the identity

r∈R
∑
	

(6−m
r
	

)=84−74=10
	


remains true. The issue is that individual 6−m
r
	

 can now be negative.

PROVED: edge-disjoint defect inequality

Define

Δ
r
	

:=6−m
r
	

.

For every R-edge rr
′
, triangle-freeness gives

X
r
	

∩X
r
′
	

=∅,Y
r
	

∩Y
r
′
	

=∅.

Therefore

m
r
	

+m
r
′
	

≤12,

so

Δ
r
	

+Δ
r
′
	

≥0for every rr
′
∈E(R).
	


This is the p≥14 replacement for “all defects are nonnegative.”

Consequences:

two vertices with m>6 cannot be adjacent in R;

a vertex with m=8, i.e. Δ=−2, can only be adjacent to vertices with Δ≥2;

a vertex with m=7, i.e. Δ=−1, can only be adjacent to vertices with Δ≥1.

This should be hard-coded as a pseudo-Boolean cut before SAT:

(6−m
r
	

)+(6−m
r
′
	

)≥0(rr
′
∈E
R
	

).
	


It is cheap and fully structural.

PROVED: terminal C-tight defect formula still works

If r∈
/
U
i
	

 and

d
R
	

(r,U
i
	

)=2,

then by the terminal q-minimal normalization,

deg(r)=8.

Since

deg(r)=d
R
	

(r)+∣ℓ(r)∣+m
r
	

,

where ℓ(r)⊆{1,2}, we get

m
r
	

=8−d
R
	

(r)−∣ℓ(r)∣.

Thus

Δ
r
	

=6−m
r
	

=d
R
	

(r)+∣ℓ(r)∣−2.
	


So every terminal C-tight vertex has a fixed nonnegative defect, even when other vertices may have m
r
	

>6.

In particular:

if z∈Z is C-tight, then

Δ
z
	

=d
R
	

(z)−2;

if s∈S
1
	

∪S
2
	

 is C-tight, then

Δ
s
	

=d
R
	

(s)−1.
PROVED: two terminal rows are eliminated immediately
Row (z,s
1
	

,s
2
	

,d,p,e
R
	

)=(2,6,6,0,17,20)

Here d=0, z=2, s
1
	

=s
2
	

=6, and e
R
	

=20.

Since D=∅, each zero vertex must have at least two S
1
	

-neighbours and at least two S
2
	

-neighbours. Thus

ZS
1
	

≥4,ZS
2
	

≥4.

Each singleton has at least two opposite-singleton neighbours, so

S
12
	

≥12.

Therefore

e
R
	

=ZZ+ZS
1
	

+ZS
2
	

+S
12
	

≥0+4+4+12=20.

Equality holds, since e
R
	

=20. Hence

ZZ=0,ZS
1
	

=4,ZS
2
	

=4,S
12
	

=12.

So every singleton has exactly two opposite-singleton neighbours, and every zero has exactly two S
1
	

- and two S
2
	

-neighbours. Thus every R-vertex is C-tight.

By terminal normalization, every R-vertex has degree 8. Hence the total degree over R would be

14⋅8=112.

But the actual R-degree sum is

r∈R
∑
	

deg(r)=U+cap+2e
R
	

=12+74+40=126.

Contradiction.

Therefore

(2,6,6,0,p,e
R
	

)=(2,6,6,0,17,20) is impossible in the terminal q=14 layer.
	

Row (z,s
1
	

,s
2
	

,d,p,e
R
	

)=(3,5,5,1,18,19)

Here d=1, z=3, s
1
	

=s
2
	

=5, and e
R
	

=19.

Each singleton needs two opposite-singleton neighbours, so

S
12
	

≥10.

For a zero vertex z, because there is one doubleton vertex D, the cheapest way to satisfy

d
R
	

(z,U
1
	

)≥2,d
R
	

(z,U
2
	

)≥2

uses one D-edge, one S
1
	

-edge, and one S
2
	

-edge. Thus each zero needs at least 3 incident edges into S
1
	

∪S
2
	

∪D, so the zero contribution is at least 9.

Therefore

e
R
	

≥10+9=19.

Again equality holds. Hence every singleton is C-tight, and every zero is tight to both colours. The only non-tight R-vertex is the unique doubleton D.

So the 13 non-doubleton vertices all have terminal degree 8, contributing

13⋅8=104

to the R-degree sum.

The actual total R-degree sum is

U+cap+2e
R
	

=12+74+38=124.

Thus the doubleton vertex would need degree

124−104=20.

But a doubleton vertex has:

2 neighbours in C;

at most 3 neighbours in Z, since only Z-D R-edges are allowed;

at most 8 neighbours in A∪B, by the universal m
r
	

≤8 bound.

So

deg(D)≤2+3+8=13,

contradiction.

Therefore

(3,5,5,1,p,e
R
	

)=(3,5,5,1,18,19) is impossible in the terminal q=14 layer.
	


These two rows should be removed without SAT.

PROVED: missing S
1
	

S
2
	

 graph controls the zero skeleton

Let

s=∣S
1
	

∣=∣S
2
	

∣=6−d.

Let H⊆S
1
	

×S
2
	

 be the set of missing S
1
	

S
2
	

-pairs:

H=(S
1
	

×S
2
	

)∖E
R
	

(S
1
	

,S
2
	

).

Since every singleton has at least two neighbours in the opposite singleton class,

Δ
H
	

(v)≤s−2for every v∈S
1
	

∪S
2
	

.

Now take a zero vertex z∈Z, and define

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

If u∈P
z
	

, v∈Q
z
	

, and uv∈E
R
	

(S
1
	

,S
2
	

), then u,z,v is a triangle. Hence

P
z
	

×Q
z
	

⊆H.
	


This is a universal zero-skeleton cut.

PROVED: special row-group consequences
Group (z,s
1
	

,s
2
	

,d)=(5,3,3,3)

Here s=3. Since every singleton has at least two opposite neighbours, H has maximum degree at most 1. Thus H is a matching.

This is exactly the matching lemma already used in the p=13,z=5 closure. It remains valid for every p≥14.

For this group, all future finite certificates should enumerate the missing matching H, not the S
1
	

S
2
	

-edge graph.

Group (z,s
1
	

,s
2
	

,d)=(6,2,2,4)

Here s=2. Every singleton must see both vertices on the opposite side, so

S
12
	

=4.
	


Thus H=∅.

Since P
z
	

×Q
z
	

⊆H=∅, every zero vertex satisfies

P
z
	

=∅orQ
z
	

=∅.

Local zero domination is

∣P
z
	

∣+∣F
z
	

∣≥2,∣Q
z
	

∣+∣F
z
	

∣≥2.

If ∣F
z
	

∣=0, then both P
z
	

 and Q
z
	

 must be nonempty, impossible.

If ∣F
z
	

∣=1, again both P
z
	

 and Q
z
	

 must be nonempty, impossible.

Therefore

∣F
z
	

∣≥2for every z∈Z.

Since ∣Z∣=6,

ZD≥12.
	


So in this group, every category must satisfy

S
12
	

=4,ZD≥12.
	


In the p=21,e
R
	

=16 row, this forces exactly

S
12
	

=4,ZD=12,

and all other R-edge categories are zero.

Group (z,s
1
	

,s
2
	

,d)=(8,0,0,6)

Here there are no singleton vertices. Thus R-edges are only of type ZZ and ZD.

For every zero vertex,

d
R
	

(z,U
1
	

)=d
R
	

(z,D)≥2,

and

d
R
	

(z,U
2
	

)=d
R
	

(z,D)≥2.

So

d
R
	

(z,D)≥2for all z∈Z.

Therefore

ZD≥16.
	


In the p=21,e
R
	

=16 row, this forces exactly

ZD=16,ZZ=0,

and every zero vertex has exactly two D-neighbours.

PROVED: singleton C-tight defect lower bound

This is the general version of the z=2 and z=5 defect arguments.

Let

s=∣S
1
	

∣=∣S
2
	

∣=6−d,x=S
12
	

.

For i=1,2, let t
i
	

 be the number of singleton vertices on side S
i
	

 with exactly two neighbours in the opposite singleton class.

These are exactly the C-tight singleton vertices.

Since a non-tight singleton has at least three opposite-singleton neighbours,

x≥2t
i
	

+3(s−t
i
	

)=3s−t
i
	

.

Therefore

t
i
	

≥max(0,3s−x).
	


Let

b
1
	

=ZS
1
	

,b
2
	

=ZS
2
	

.

On side S
i
	

, there are s−t
i
	

 non-tight vertices, and each can absorb at most z zero-neighbours. Hence at least

max{0, b
i
	

−z(s−t
i
	

)}

zero-singleton incidences must hit tight singleton vertices.

For each tight singleton s,

Δ
s
	

=d
R
	

(s)−1=1+d
R
	

(s,Z).

Thus the tight-singleton defect on side S
i
	

 is at least

D
i
	

(t
i
	

)=t
i
	

+max{0, b
i
	

−z(s−t
i
	

)}.
	


So the category-level lower bound is

D
sing
	

≥
t
1
	

∈[max(0,3s−x),s]
min
	

D
1
	

(t
1
	

)+
t
2
	

∈[max(0,3s−x),s]
min
	

D
2
	

(t
2
	

).
	


This is a sound cut. In branches where m
r
	

≤6 for all r, it can be compared directly with the total defect budget 10. In the general p≥14 branch, combine it with the edge-disjoint defect inequality

Δ
r
	

+Δ
r
′
	

≥0(rr
′
∈E
R
	

)

to control possible negative-defect vertices.

FINITE-CERTIFICATE-NEEDED: no scalar inequality is likely to eliminate all p≥14 rows

The basic scalar constraints still admit plausible skeletons. For example, in the row

(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(8,0,0,6,21,16),

the category structure is forced to

ZD=16,ZZ=0.

Each zero has exactly two D-neighbours and is C-tight to both colours. Terminal normalization then gives each zero degree 8, hence m
z
	

=6 and Δ
z
	

=0. The six D-vertices must carry the remaining 26 units of A/B-incidence.

This is not ruled out by category counting alone. Any contradiction must use the actual A/B-state realization, rectangle two-cover, R/R codegrees, or rooted cuts.

So the next proof layer should be a finite certificate, but not a broad fixed-graph enumeration.

FINITE-CERTIFICATE-NEEDED: the right p≥14 certificate format

The certificate should be indexed by four structural objects:

P-template+S
1
	

S
2
	

 missing graph H+Z/D skeleton+A/B-state assignment.
	

1. P-template layer

For fixed p, enumerate canonical bipartite graphs

P⊆A×B

with

∣A∣=∣B∣=6,e(P)=p,δ(P)≥2.

Split them by independence number:

α(P)∈{6,7,8}.

Facts to hard-code:

α(P)≤8;

if p=21, then α(P)≤7;

if α(P)=8, then the maximum independent set has type 4+4, and P has a 4×4 empty rectangle with the forced K
4,2
	

∪K
2,4
	

 boundary;

if α(P)=7, then the maximum independent set has type 3+4 or 4+3, giving a Hall-defect barrier.

For each P, precompute the state table

S(P)={(X,Y):X⊆A, Y⊆B, X×Y∩E(P)=∅}.

For every state s=(X,Y), record

m(s)=∣X∣+∣Y∣,Δ(s)=6−m(s).
2. S
1
	

S
2
	

 missing graph H

Do not enumerate S
1
	

S
2
	

-edges directly.

Enumerate

H=(S
1
	

×S
2
	

)∖E
R
	

(S
1
	

,S
2
	

)

subject to

∣H∣=s
2
−S
12
	

,

and

Δ
H
	

(v)≤s−2(v∈S
1
	

∪S
2
	

).

Special cases:

s=3: H is a matching.

s=2: H=∅.

s=0: no H.

This is usually much smaller than enumerating the full S
1
	

S
2
	

 graph.

3. Zero/D skeleton

For each zero vertex z, choose

P
z
	

⊆S
1
	

,Q
z
	

⊆S
2
	

,F
z
	

⊆D.

Enforce:

P
z
	

×Q
z
	

⊆H,
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

Also enumerate ZZ-edges. For every ZZ-edge zz
′
, triangle-freeness requires

P
z
	

∩P
z
′
	

=∅,
Q
z
	

∩Q
z
′
	

=∅,
F
z
	

∩F
z
′
	

=∅.

At this skeleton stage, compute all C-tight vertices and their forced terminal defects.

Reject if the skeleton already violates:

r∈T
∑
	

Δ
r
tight
	

+minimum forced edge-defect compensation>10.

The first term is explicit from

Δ
r
	

=d
R
	

(r)+∣ℓ(r)∣−2.

The second term is computed using the edge inequality

Δ
r
	

+Δ
r
′
	

≥0

over fixed R-edges.

4. A/B-state assignment

Assign each r∈R a state

s
r
	

=(X
r
	

,Y
r
	

)∈S(P).

Hard constraints:

r∈R
∑
	

Δ(s
r
	

)=10.

For every fixed R-edge rr
′
,

X
r
	

∩X
r
′
	

=∅,Y
r
	

∩Y
r
′
	

=∅.

Equivalently,

Δ(s
r
	

)+Δ(s
r
′
	

)≥0.

For every C-tight vertex r, enforce the exact terminal equality

Δ(s
r
	

)=d
R
	

(r)+∣ℓ(r)∣−2.

For zero vertices:

∣X
z
	

∣≥2,∣Y
z
	

∣≥2.

For singleton vertices:

∣X
s
	

∣≥1,∣Y
s
	

∣≥1.

For every r,

d
R
	

(r)+∣ℓ(r)∣+∣X
r
	

∣+∣Y
r
	

∣≥8.
5. Rectangle two-cover

For every missing A−B cell (a,b)∈
/
E(P),

∣{r∈R:a∈X
r
	

, b∈Y
r
	

}∣≥2.
	


For every A−B edge, every state already avoids it.

6. A/B-degree constraints

For every a∈A,

∣{r:a∈X
r
	

}∣≥7−deg
P
	

(a).

For every b∈B,

∣{r:b∈Y
r
	

}∣≥7−deg
P
	

(b).

Also every A/B-vertex must see both root colours through R-neighbours:

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

7. Full local codegrees

For every R-edge rr
′
, require full common-neighbour count 0:

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

For every R-nonedge rr
′
, require:

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

For A/A and B/B:

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
	

}∣≥1,
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

For missing A/R incidences, if a∈
/
X
r
	

,

∣N
P
	

(a)∩Y
r
	

∣+∣{u∈N
R
	

(r):a∈X
u
	

}∣≥2.

For missing B/R incidences, if b∈
/
Y
r
	

,

∣N
P
	

(b)∩X
r
	

∣+∣{u∈N
R
	

(r):b∈Y
u
	

}∣≥2.
8. Rooted cuts

For every W⊆R, impose exact cap74 rooted cuts.

Since

p+e
R
	

=37,

the Φ-cut is

M(W)+F
Φ
	

(W)≥∂
R
	

(W),

where

M(W)=
r∈W
∑
	

m
r
	

,
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
Which row to test first
FINITE-CERTIFICATE-NEEDED, but likely easiest

The first finite row I would test is

(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(8,0,0,6,21,16).
	


Reason:

there are no singleton vertices;

R-edges are only ZD;

local domination forces

ZD=16,ZZ=0;

every zero has exactly two D-neighbours;

every zero is C-tight to both colours, hence terminal degree 8;

therefore every zero has

m
z
	

=6,Δ
z
	

=0.

So the entire R-skeleton is just an 8×6 bipartite graph with every Z-row sum 2. The six D-vertices carry the full remaining defect:

d∈D
∑
	

Δ
d
	

=10.

Hard-code before SAT:

ZZ=0,ZD=16,d
R
	

(z,D)=2 ∀z∈Z,
m
z
	

=6 ∀z∈Z,
d∈D
∑
	

(6−m
d
	

)=10.

Also hard-code R/R nonedge codegrees for pairs z,z
′
∈Z:

∣N
D
	

(z)∩N
D
	

(z
′
)∣+∣X
z
	

∩X
z
′
	

∣+∣Y
z
	

∩Y
z
′
	

∣≥2.

This row has the smallest R-structure and should quickly validate whether the p≥14 P-template/state certificate is working.

Weakest steps and C++ checks
PROVED and should be hard-coded

Universal bound:

m
r
	

≤8,p=21⇒m
r
	

≤7.

Global defect identity:

r
∑
	

(6−m
r
	

)=10.

Edge-disjoint defect:

rr
′
∈E
R
	

⇒(6−m
r
	

)+(6−m
r
′
	

)≥0.

Terminal C-tight equality:

Δ
r
	

=d
R
	

(r)+∣ℓ(r)∣−2.

Row eliminations:

(2,6,6,0,p,e
R
	

)=(2,6,6,0,17,20)

and

(3,5,5,1,p,e
R
	

)=(3,5,5,1,18,19)

are impossible in the terminal q=14 layer.

Missing S
1
	

S
2
	

 skeleton:

P
z
	

×Q
z
	

⊆H.

Special group cuts:

(6,2,2,4):S
12
	

=4,ZD≥12.
(8,0,0,6):ZD≥16.
FINITE-CERTIFICATE-NEEDED

The remaining rows need P-template/state certificates. The checker should first test:

(z,s
1
	

,s
2
	

,d,p,e
R
	

)=(8,0,0,6,21,16),

with the forced ZD=16, ZZ=0, row-sum-2 Z-to-D skeleton, zero states fixed to m
z
	

=6, and full R/R, rectangle-cover, A/R, B/R, and rooted-cut constraints.