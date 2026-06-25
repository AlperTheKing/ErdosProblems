PROVED: delete two non-p19 rows immediately if still present

These two rows should not remain in the frontier:

(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

)=(2,6,6,0,17,20)

and

(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

)=(3,5,5,1,18,19).

In both rows, the local lower bound on e
R
	​

 is tight. Therefore all relevant non-doubleton vertices are C-tight, terminal normalization forces degree 8, and the resulting R-degree sum contradicts

r∈R
∑
	​

deg(r)=U+cap+2e
R
	​

.

So before any new template run, remove those two rows from the scalar frontier if they are still listed.

PROVED: p19 rows are all “slack-2” skeleton rows

For the four p19 rows,

p=19,e
R
	​

=18.

Each group has a local minimum e
R
	​

=16, so p19 is exactly two R-edges above the local floor.

Let

E
Z
	​

:=ZS
1
	​

+ZS
2
	​

+ZD.

Then the p19 category restrictions are:

row group	local floor	exact p19 slack equation
(z,s
1
	​

,s
2
	​

,d)=(4,4,4,2)	E
Z
	​

≥8, S
12
	​

≥8	
ZZ+(E
Z
	​

−8)+(S
12
	​

−8)=2
	​


(5,3,3,3)	E
Z
	​

≥10, S
12
	​

≥6	
ZZ+(E
Z
	​

−10)+(S
12
	​

−6)=2
	​


(6,2,2,4)	ZD≥12, S
12
	​

=4	
ZZ+ZS
1
	​

+ZS
2
	​

+(ZD−12)=2
	​


(8,0,0,6)	ZD≥16	
ZZ+(ZD−16)=2
	​


These are sound category cuts and should be applied before SAT. They are especially useful because they keep p19 skeletons close to the already-closed p20/p21 skeletons.

Recommended next row
FINITE-CERTIFICATE-NEEDED, but best compute/minute target

Attack:

(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

,cap)=(8,0,0,6,19,18,74).
	​


This is the best next row because:

there are no singleton vertices;

the category split has only three cases;

R-edges are only ZZ and ZD;

many zero vertices are terminal C-tight with exact m
z
	​

;

the p20/p21 z8 solvers already validate this style of certificate;

it tests the new p19 A−B template family on the simplest remaining R-structure.

I would not attack z4/z5/z6 p19 first. They have singleton skeletons and more category branching. I would also not descend z8 all the way blindly; first close z8 p19, then decide whether p18 z8 or p19 z6 is cheaper based on tail behavior.

PROVED: exact z8 p19 category split

For

(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

)=(8,0,0,6,19,18),

there are no singletons, so the only allowed R-edge categories are

ZZ,ZD.

Each zero vertex must satisfy

d
R
	​

(z,D)≥2.

Thus

ZD≥8⋅2=16.

Since

ZZ+ZD=e
R
	​

=18,

the only categories are:

(ZZ,ZD)=(0,18),(1,17),(2,16).
	​


This is the whole category frontier for the row.

PROVED: terminal zero constraints in z8 p19

For z∈Z, write

q
z
	​

:=d
R
	​

(z,D),h
z
	​

:=d
R
	​

(z,Z).

Then

d
R
	​

(z)=q
z
	​

+h
z
	​

.

If

q
z
	​

=2,

then z is tight to both colours because

d
R
	​

(z,U
1
	​

)=d
R
	​

(z,U
2
	​

)=d
R
	​

(z,D)=2.

By terminal normalization,

deg(z)=8.

Since z has zero label,

m
z
	​

=∣X
z
	​

∣+∣Y
z
	​

∣=8−d
R
	​

(z)=8−q
z
	​

−h
z
	​

.

So for every zero with q
z
	​

=2,

m
z
	​

=6−h
z
	​

.
	​


In particular:

if q
z
	​

=2,h
z
	​

=0, then m
z
	​

=6;

if q
z
	​

=2,h
z
	​

=1, then m
z
	​

=5;

if q
z
	​

=2,h
z
	​

=2, then m
z
	​

=4.

Also, for every zero vertex, regardless of tightness,

∣X
z
	​

∣≥2,∣Y
z
	​

∣≥2.
	​


These should be hard-coded.

PROVED: exact degree distributions by category
Category A: (ZZ,ZD)=(2,16)

Here

z∈Z
∑
	​

q
z
	​

=16

and every q
z
	​

≥2. Hence

q
z
	​

=2∀z∈Z.

So every zero vertex is C-tight.

Therefore

m
z
	​

=8−d
R
	​

(z)=8−(2+h
z
	​

)=6−h
z
	​

.

Summing over all zero vertices:

z∈Z
∑
	​

m
z
	​

=8⋅6−
z∈Z
∑
	​

h
z
	​

=48−2ZZ=48−4=44.

Since cap is 74, the six doubletons satisfy

d∈D
∑
	​

m
d
	​

=30.
	​


This is the most constrained category and should be tested first.

Category B: (ZZ,ZD)=(1,17)

Here exactly one unit of ZD-degree is above the floor. Thus the zero D-degrees are

(3,2,2,2,2,2,2,2)

up to permutation.

The seven zeros with q
z
	​

=2 are terminal C-tight and have exact

m
z
	​

=6−h
z
	​

.

The one zero with q
z
	​

=3 is not necessarily C-tight, so only the general constraints apply:

∣X
z
	​

∣≥2,∣Y
z
	​

∣≥2,d
R
	​

(z)+m
z
	​

≥8.
Category C: (ZZ,ZD)=(0,18)

Here the zero D-degree excess is 2. Thus the zero D-degree distribution is either

(4,2,2,2,2,2,2,2)

or

(3,3,2,2,2,2,2,2).

All zeros with q
z
	​

=2 are terminal C-tight and have

m
z
	​

=6.

The zeros with q
z
	​

>2 are not automatically terminal tight.

This category is likely the hardest among the three because it has the most non-tight zero slack.

PROVED: p19 state-size bound

For any p19 A−B template P=G[A,B], every R-state satisfies

X
r
	​

×Y
r
	​

∩E(P)=∅.

Since δ(P)≥2, the universal independent-state bound is

m
r
	​

=∣X
r
	​

∣+∣Y
r
	​

∣≤8.
	​


Moreover, if m
r
	​

=8, then necessarily

∣X
r
	​

∣=∣Y
r
	​

∣=4.

The p19 case permits m=8, unlike p21, so the state table must include m=8 states. But m=8 states are structurally special: they are exactly 4×4 empty rectangles in P.

Hard-code:

m
r
	​

≤8∀r.
	​


And for m
r
	​

=8, require state type

(∣X
r
	​

∣,∣Y
r
	​

∣)=(4,4).
	​

PROVED: edge-defect compatibility

Define

Δ
r
	​

:=6−m
r
	​

.

Then

r∈R
∑
	​

Δ
r
	​

=14⋅6−74=10.

For every R-edge rr
′
, triangle-freeness forces

X
r
	​

∩X
r
′
	​

=∅,Y
r
	​

∩Y
r
′
	​

=∅.

Therefore

m
r
	​

+m
r
′
	​

≤12,

so

Δ
r
	​

+Δ
r
′
	​

≥0for every rr
′
∈E
R
	​

.
	​


This is important in p19 because some vertices may have negative defect, i.e. m
r
	​

=7 or 8. Add this as a cheap PB cut before full state checking.

PROVED: ZD capacity cut

For each d∈D, define

Z(d):=N
R
	​

(d)∩Z.

Let

U
A
	​

(d):=
z∈Z(d)
⋃
	​

X
z
	​

,
U
B
	​

(d):=
z∈Z(d)
⋃
	​

Y
z
	​

.

For every ZD-edge zd, triangle-freeness gives

X
d
	​

∩X
z
	​

=∅,Y
d
	​

∩Y
z
	​

=∅.

Therefore

X
d
	​

⊆A∖U
A
	​

(d),
Y
d
	​

⊆B∖U
B
	​

(d),

and hence

m
d
	​

≤12−∣U
A
	​

(d)∣−∣U
B
	​

(d)∣.
	​


This is the main capacity cut for the z8 p19 row. It was decisive in the p21 z4 row and should be hard-coded here.

FINITE-CERTIFICATE-NEEDED: p19 template family

For the next run, enumerate canonical A−B templates

P⊆A×B

with

∣A∣=∣B∣=6,e(P)=19,δ(P)≥2.

For each canonical P, precompute the state table

S(P)={(X,Y):X⊆A, Y⊆B, X×Y∩E(P)=∅}.

Hard-filter:

m=∣X∣+∣Y∣≤8.

Record for each state:

m,Δ=6−m,∣X∣,∣Y∣.

Also record whether it is an m=8 state, i.e. a 4+4 empty rectangle.

Exact C++ verifier constraints for the next row
Target row
(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

,cap)=(8,0,0,6,19,18,74).
	​

Category split

Run exactly these three categories:

(ZZ,ZD)=(2,16),(1,17),(0,18).
	​


Recommended order:

(ZZ,ZD)=(2,16);

(ZZ,ZD)=(1,17);

(ZZ,ZD)=(0,18).

The first has all zeros terminal tight and should be fastest.

R-skeleton enumeration

For each category, enumerate canonical R-skeletons on

Z
8
	​

∪D
6
	​


with:

∣E(Z)∣=ZZ,
∣E(Z,D)∣=ZD,
d
R
	​

(z,D)≥2∀z∈Z.

Triangle-free skeleton cuts:

For every ZZ-edge zz
′
,

N
D
	​

(z)∩N
D
	​

(z
′
)=∅.

Also reject any R-triangle in Z, although with ZZ≤2 this is automatic unless the enumerator is general.

Terminal zero equalities

For every zero z with

d
R
	​

(z,D)=2,

hard-code:

m
z
	​

=8−d
R
	​

(z)=8−d
R
	​

(z,D)−d
R
	​

(z,Z).
	​


Equivalently:

∣X
z
	​

∣+∣Y
z
	​

∣=6−d
R
	​

(z,Z).
	​


Also:

∣X
z
	​

∣≥2,∣Y
z
	​

∣≥2.
	​


For zeros with d
R
	​

(z,D)>2, impose only:

∣X
z
	​

∣≥2,∣Y
z
	​

∣≥2,
d
R
	​

(z)+m
z
	​

≥8.
Doubleton degree lower bounds

For every d∈D,

deg(d)=2+d
R
	​

(d,Z)+m
d
	​

≥8.

So hard-code:

m
d
	​

≥6−d
R
	​

(d,Z).
	​


Also:

m
d
	​

≤8.
	​

Cap equality

Hard-code exact cap:

z∈Z
∑
	​

m
z
	​

+
d∈D
∑
	​

m
d
	​

=74.
	​


For category (ZZ,ZD)=(2,16), additionally hard-code:

z∈Z
∑
	​

m
z
	​

=44,
d∈D
∑
	​

m
d
	​

=30.
	​


For the other categories, compute the fixed contribution from all d
D
	​

(z)=2 zeros and leave the non-tight zeros variable.

Edge-disjointness

For every R-edge rr
′
, enforce:

X
r
	​

∩X
r
′
	​

=∅,Y
r
	​

∩Y
r
′
	​

=∅.
	​


Also add the cheap defect cut:

(6−m
r
	​

)+(6−m
r
′
	​

)≥0.
	​


This is redundant if exact disjointness is encoded, but useful as early propagation.

ZD capacity cut

For each d∈D, compute

U
A
	​

(d)=
z∼d
⋃
	​

X
z
	​

,
U
B
	​

(d)=
z∼d
⋃
	​

Y
z
	​

.

Hard-code:

X
d
	​

∩U
A
	​

(d)=∅,Y
d
	​

∩U
B
	​

(d)=∅.
	​


And, as a PB bound,

m
d
	​

≤12−∣U
A
	​

(d)∣−∣U
B
	​

(d)∣.
	​

Full R/R codegree checks

For every R-edge rr
′
, enforce full common-neighbour count 0:

∣ℓ(r)∩ℓ(r
′
)∣+∣X
r
	​

∩X
r
′
	​

∣+∣Y
r
	​

∩Y
r
′
	​

∣+∣N
R
	​

(r)∩N
R
	​

(r
′
)∣=0.

In this row:

D−D nonedges are automatically satisfied by label overlap 2;

Z−Z nonedges require:

∣N
D
	​

(z)∩N
D
	​

(z
′
)∣+∣N
Z
	​

(z)∩N
Z
	​

(z
′
)∣+∣X
z
	​

∩X
z
′
	​

∣+∣Y
z
	​

∩Y
z
′
	​

∣≥2;

Z−D nonedges require:

∣N
Z
	​

(z)∩N
Z
	​

(d)∣+∣X
z
	​

∩X
d
	​

∣+∣Y
z
	​

∩Y
d
	​

∣≥2.

Here N
Z
	​

(d) means zero neighbours of d.

Rectangle two-cover

For every missing A−B cell

(a,b)∈
/
E(P),

enforce:

∣{r∈R:a∈X
r
	​

, b∈Y
r
	​

}∣≥2.
	​


Every actual A−B edge is avoided by the state table.

A/B degree constraints

For every a∈A,

∣{r:a∈X
r
	​

}∣≥7−deg
P
	​

(a).
	​


For every b∈B,

∣{r:b∈Y
r
	​

}∣≥7−deg
P
	​

(b).
	​


Every A/B-vertex must see both root colours through R. Since only D-vertices carry both colours in this row, this becomes:

∀a∈A,∃d∈D with a∈X
d
	​

,
	​

∀b∈B,∃d∈D with b∈Y
d
	​

.
	​


Actually this single condition gives both colours at once because every d∈D has label {1,2}.

A/A and B/B codegrees

For a,a
′
∈A, a

=a
′
:

∣N
P
	​

(a)∩N
P
	​

(a
′
)∣+∣{r:a,a
′
∈X
r
	​

}∣≥1.
	​


For b,b
′
∈B:

∣N
P
	​

(b)∩N
P
	​

(b
′
)∣+∣{r:b,b
′
∈Y
r
	​

}∣≥1.
	​

A/R and B/R nonedge codegrees

For a∈
/
X
r
	​

:

∣N
P
	​

(a)∩Y
r
	​

∣+∣{u∈N
R
	​

(r):a∈X
u
	​

}∣≥2.
	​


For b∈
/
Y
r
	​

:

∣N
P
	​

(b)∩X
r
	​

∣+∣{u∈N
R
	​

(r):b∈Y
u
	​

}∣≥2.
	​

Rooted cuts

Use all exact Φ/Ψ cuts.

Since

p+e
R
	​

=37,

the Φ-cut is:

M(W)+F
Φ
	​

(W)≥∂
R
	​

(W),
	​


where

M(W)=
r∈W
∑
	​

m
r
	​

,
F
Φ
	​

(W)=
i=1
∑
2
	​

min(∣U
i
	​

∩W∣, 8−∣U
i
	​

∩W∣).

Here U
1
	​

=U
2
	​

=D, so this simplifies to:

F
Φ
	​

(W)=2min(∣D∩W∣, 8−∣D∩W∣).
	​


The two Ψ-cuts are:

e
R
	​

−∂
R
	​

(W)+F
Ψ
	​

(W)+M
A
	​

(W)+M
B
	​

(R∖W)≥37,
	​

e
R
	​

−∂
R
	​

(W)+F
Ψ
	​

(W)+M
B
	​

(W)+M
A
	​

(R∖W)≥37,
	​


where

F
Ψ
	​

(W)=2+2min(∣D∩W∣, 6−∣D∩W∣).
CONJECTURED: expected difficulty order inside z8 p19

Expected easiest to hardest:

(ZZ,ZD)=(2,16)<(1,17)<(0,18).

Reason:

(2,16): all zeros have D-degree 2, so all zero states are exact terminal states.

(1,17): exactly one zero has D-degree 3, giving one non-tight zero.

(0,18): either one zero has D-degree 4, or two zeros have D-degree 3, giving the most non-tight slack.

Next after z8 p19

If z8 p19 closes cleanly, next target should be:

(z,s
1
	​

,s
2
	​

,d,p,e
R
	​

)=(6,2,2,4,19,18).
	​


It has:

S
12
	​

=4,

and

ZZ+ZS
1
	​

+ZS
2
	​

+(ZD−12)=2.

But I would not run it before z8 p19 because z6 has singleton-zero edges and more skeleton branching.

Single next experiment target

Run:

row = (z=8,s1=0,s2=0,d=6,p=19,eR=18,cap=74)
	​


with categories:

(ZZ,ZD) in {(2,16),(1,17),(0,18)}
	​


using:

canonical p=19 A-B templates with e(P)=19, δ(P)≥2.
	​


Hard-code before SAT:

d
R
	​

(z,D)≥2∀z∈Z
	​

d
R
	​

(z,D)=2⇒m
z
	​

=8−d
R
	​

(z)
	​

∣X
z
	​

∣≥2, ∣Y
z
	​

∣≥2∀z∈Z
	​

m
d
	​

≥6−d
R
	​

(d,Z)∀d∈D
	​

r∈R
∑
	​

m
r
	​

=74
	​

X
d
	​

∩
z∼d
⋃
	​

X
z
	​

=∅,Y
d
	​

∩
z∼d
⋃
	​

Y
z
	​

=∅
	​

m
d
	​

≤12−
	​

z∼d
⋃
	​

X
z
	​

	​

−
	​

z∼d
⋃
	​

Y
z
	​

	​

	​


plus full R/R, rectangle two-cover, A/R, B/R, A/A, B/B, and rooted Φ/Ψ constraints.