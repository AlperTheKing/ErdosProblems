For this exact row,

(z,s
1
	​

,s
2
	​

,d)=(3,5,5,1),p=12,e
R
	​

=25,M=cap=74,

I do not see a safe scalar-only contradiction. But there is a strong next reduction: the A−B graph being exactly 2-regular makes every R-vertex an independent set in a 2-factor, and the equality M=74 forces many maximum independent-set rectangles. Combined with the C-tight/reroot condition, this gives a small exact verifier that is much sharper than the current fixed-R incidence SAT.

Below is the clean lemma package.

1. Notation

Let

P:=G[A,B],

so P is a 2-regular bipartite graph on A∪B, with ∣A∣=∣B∣=6 and

e(P)=p=12.

Let

F:=(A×B)∖E(P)

be the 24 missing A−B cells.

For r∈R, define

X
r
	​

:=N
A
	​

(r)⊆A,Y
r
	​

:=N
B
	​

(r)⊆B,

and

m
r
	​

:=∣X
r
	​

∣+∣Y
r
	​

∣.

For the R-category counts, write

a:=ZZ,b:=ZS
1
	​

,c:=ZS
2
	​

,f:=ZD,x:=S
1
	​

S
2
	​

.

Thus

a+b+c+f+x=25.
2. Rectangle lemma for the 2-regular A−B graph

For every r∈R,

m
r
	​

≤6.
	​


Moreover, equality m
r
	​

=6 has a rigid component-orientation form.

Proof

If a∈X
r
	​

 and b∈Y
r
	​

, then r hits both a and b. Therefore ab cannot be an A−B edge, otherwise abr would be a triangle. Hence

X
r
	​

×Y
r
	​

⊆F.

Equivalently, X
r
	​

∪Y
r
	​

 is an independent set in the 2-regular bipartite graph P.

Since every a∈A has P-degree 2, the number of P-edges leaving X
r
	​

 is

2∣X
r
	​

∣.

None of these edges can land in Y
r
	​

, so all of them land in B∖Y
r
	​

. But B∖Y
r
	​

 has total P-degree

2(6−∣Y
r
	​

∣).

Therefore

2∣X
r
	​

∣≤2(6−∣Y
r
	​

∣),

so

∣X
r
	​

∣+∣Y
r
	​

∣≤6.

If equality holds, then all P-edges incident with B∖Y
r
	​

 come from X
r
	​

, and symmetrically all P-edges incident with A∖X
r
	​

 land in Y
r
	​

. Thus on each cycle component of the 2-factor P, the set X
r
	​

∪Y
r
	​

 selects exactly one side of that component. In other words, for each cycle component C of P, a maximum rectangle chooses either the A-side of C or the B-side of C.

That proves the lemma.

3. Immediate consequence: P is disconnected and at least four R-vertices have m
r
	​

=6

Since

M=e(A∪B,R)=74

and every m
r
	​

≤6,

r∈R
∑
	​

(6−m
r
	​

)=14⋅6−74=10.

So at least four R-vertices satisfy

m
r
	​

=6.

Indeed, if at most three vertices had m
r
	​

=6, then

M≤3⋅6+11⋅5=73,

contradicting M=74.

Now suppose P were connected, i.e. a single 12-cycle. Then the only maximum independent sets of P are A and B. Hence a vertex r with m
r
	​

=6 would have either

(X
r
	​

,Y
r
	​

)=(A,∅)

or

(X
r
	​

,Y
r
	​

)=(∅,B).

But every zero-labelled vertex has

∣X
r
	​

∣≥2,∣Y
r
	​

∣≥2,

and every singleton-labelled vertex has

∣X
r
	​

∣≥1,∣Y
r
	​

∣≥1.

Thus none of the 13 non-doubleton vertices can have m
r
	​

=6 if P is connected. The single doubleton vertex can contribute at most one m
r
	​

=6 vertex, so

M≤13⋅5+1⋅6=71,

contradiction.

Therefore:

P is disconnected.
	​


So the A−B graph has only three possible cycle types:

C
8
	​

+C
4
	​

,C
6
	​

+C
6
	​

,C
4
	​

+C
4
	​

+C
4
	​

.
	​


This is already a major reduction: the finite checker should not enumerate arbitrary A−B graphs. It only needs these three canonical 2-factor templates.

4. Category-tightness lemma

This is the sharpest R-category invariant I see for the current row.

Define a singleton vertex to be C-tight if its opposite-singleton degree is exactly 2. Thus

s∈S
1
	​

 is tight⟺d
R
	​

(s,S
2
	​

)=2,

and

s∈S
2
	​

 is tight⟺d
R
	​

(s,S
1
	​

)=2.

Define a zero vertex z∈Z to be tight to colour i if

d
R
	​

(z,U
i
	​

)=2.

Let

T
S
	​

:=#{tight singleton vertices},

and

T
Z
	​

:=#{(z,i):z∈Z, i∈{1,2}, d
R
	​

(z,U
i
	​

)=2}.

Then every configuration with category counts (a,b,c,f,x) satisfies

T
S
	​

≥max(0, 30−2x),
	​


and

T
Z
	​

≥max(0, x+a−f−7).
	​

Proof for T
S
	​


Each of the ten singleton vertices has opposite-singleton degree at least 2. A non-tight singleton has opposite-singleton degree at least 3.

The sum of opposite-singleton degrees over all singleton vertices is

2x,

because each S
1
	​

S
2
	​

-edge contributes once to an S
1
	​

-vertex and once to an S
2
	​

-vertex.

If T
S
	​

=t, then

2x≥2t+3(10−t)=30−t.

Therefore

t≥30−2x.

Since t≥0, we get

T
S
	​

≥max(0,30−2x).
Proof for T
Z
	​


For z∈Z, define

q
1
	​

(z):=d
R
	​

(z,U
1
	​

),q
2
	​

(z):=d
R
	​

(z,U
2
	​

).

Each q
i
	​

(z)≥2. A zero-colour pair (z,i) is tight exactly when q
i
	​

(z)=2; otherwise q
i
	​

(z)≥3.

The total zero-colour incidence is

z∈Z
∑
	​

(q
1
	​

(z)+q
2
	​

(z)).

A ZS
1
	​

-edge contributes 1, a ZS
2
	​

-edge contributes 1, and a ZD-edge contributes 2, because the doubleton vertex lies in both U
1
	​

 and U
2
	​

. Hence

z∈Z
∑
	​

(q
1
	​

(z)+q
2
	​

(z))=b+c+2f.

If T
Z
	​

=t, then

b+c+2f≥2t+3(6−t)=18−t.

Therefore

t≥18−(b+c+2f).

Using

b+c=25−a−f−x,

we get

18−(b+c+2f)=18−(25−a−f−x+2f)=x+a−f−7.

So

T
Z
	​

≥max(0,x+a−f−7).

That proves the lemma.

5. Terminal reroot cut

This row is necessarily on the C-tight side.

Indeed, the clean-shadow bound for d=1,z=3,s
1
	​

=s
2
	​

=5 is

e
R
	​

≥3⋅5+5⋅3=30,

but here

e
R
	​

=25.

So at least one C-tight pair exists.

Now suppose r∈R∖U
i
	​

 is tight to colour i:

d
R
	​

(r,U
i
	​

)=2.

Then c
i
	​

r is a nonedge with exactly two common neighbours. Rerooting at c
i
	​

r gives

q
′
=22−deg(r),

because ∣U
i
	​

∣=6 in the cap74 equality layer.

Thus:

deg(r)>8⟹q
′
<14.

So, in a terminal q=14 verifier after q<14 has been closed or delegated, every C-tight vertex must satisfy

deg(r)=8.
	​


Now use the singleton Φ-cut W={r}. In the cap74 equality layer,

p+e
R
	​

=37,

and the singleton Φ-cut gives

m
r
	​

+∣ℓ(r)∣≥d
R
	​

(r),

where ℓ(r) is the C-label of r.

If deg(r)=8, then

m
r
	​

+∣ℓ(r)∣+d
R
	​

(r)=8.

Combining,

8−d
R
	​

(r)≥d
R
	​

(r),

so

d
R
	​

(r)≤4.
	​


Therefore the terminal q=14 layer has the following exact R-only cut:

d
R
	​

(r,U
i
	​

)=2⟹d
R
	​

(r)≤4.
	​


If a proposed R-graph violates this, it is not a terminal q=14 obstruction; it reroots to q<14.

This cut should be added before any A/B-incidence SAT.

6. What the extreme UNKNOWN profile forces

For the extreme profile

ZZ=0,ZS
1
	​

=3,ZS
2
	​

=3,ZD=3,S
1
	​

S
2
	​

=16,

we have

a=0,f=3,x=16.

The tightness lemma gives

T
S
	​

≥max(0,30−32)=0,

and

T
Z
	​

≥16+0−3−7=6.

There are exactly six zero-colour pairs (z,i), so all of them are tight.

Also, because ZD=3, every zero vertex is adjacent to the unique doubleton vertex. Since ZS
1
	​

=3 and ZS
2
	​

=3, and each zero vertex needs at least one S
1
	​

-neighbour and one S
2
	​

-neighbour in addition to D, every zero vertex has exactly

d
R
	​

(z)=3.

In the terminal q=14 layer, every zero vertex then has

deg(z)=8,

so

m
z
	​

=8−d
R
	​

(z)=5.

Thus the extreme profile forces:

all three zero vertices have m
z
	​

=5 and are tight to both colours.
	​


This is a very strong finite constraint.

7. Neighbour-union capacity lemma

This is the main incidence cut I would add next.

For r∈R, define

A(r):=
u∈N
R
	​

(r)
⋃
	​

X
u
	​

⊆A,

and

B(r):=
u∈N
R
	​

(r)
⋃
	​

Y
u
	​

⊆B.

Since ru∈E
R
	​

 implies that r and u cannot share an A-neighbour or a B-neighbour, we have

X
r
	​

∩X
u
	​

=∅,Y
r
	​

∩Y
u
	​

=∅

for every u∈N
R
	​

(r). Hence

X
r
	​

⊆A∖A(r),

and

Y
r
	​

⊆B∖B(r).

Therefore

m
r
	​

=∣X
r
	​

∣+∣Y
r
	​

∣≤12−∣A(r)∣−∣B(r)∣.

On the other hand, the degree and root-codegree constraints give a lower bound for m
r
	​

. Define

L(r):=
⎩
⎨
⎧
	​

max(4, 8−d
R
	​

(r)),
max(2, 7−d
R
	​

(r)),
max(0, 6−d
R
	​

(r)),
	​

r∈Z,
r∈S
1
	​

∪S
2
	​

,
r∈D.
	​


The terms 4,2,0 come from the xr and yr nonedge-codegree requirements:

zero label: at least 2 neighbours in A and at least 2 in B;

singleton label: at least 1 in A and at least 1 in B;

doubleton label: no such lower bound from xr,yr, because the two C-vertices already supply the two common neighbours.

The terms 8−d
R
	​

(r), 7−d
R
	​

(r), 6−d
R
	​

(r) come from

d
R
	​

(r)+∣ℓ(r)∣+m
r
	​

≥8.

So every valid model satisfies

m
r
	​

≥L(r).

Combining the upper and lower bounds gives:

∣A(r)∣+∣B(r)∣≤12−L(r).
	​

(Neighbour-capacity)

This is exact and very cheap to encode once R is fixed and A/B-states are tabled.

Extreme profile consequence

In the extreme profile, the unique D-vertex is adjacent to all three zero vertices. It has

d
R
	​

(D)=3,

so

L(D)=6−3=3.

Therefore

∣A(D)∣+∣B(D)∣≤9.

But

A(D)=X
z
1
	​

	​

∪X
z
2
	​

	​

∪X
z
3
	​

	​

,

and

B(D)=Y
z
1
	​

	​

∪Y
z
2
	​

	​

∪Y
z
3
	​

	​

.

Each zero vertex has m
z
	​

=5. Hence the three zero A/B-sets have total size

m
z
1
	​

	​

+m
z
2
	​

	​

+m
z
3
	​

	​

=15.

The capacity cut forces their union size to be at most 9. Equivalently, the three zero incidence sets must have at least 6 units of overlap on the A-side and B-side combined.

So the extreme profile is not just “three arbitrary zero rectangles of size 5”; it requires

∣X
z
1
	​

	​

∪X
z
2
	​

	​

∪X
z
3
	​

	​

∣+∣Y
z
1
	​

	​

∪Y
z
2
	​

	​

∪Y
z
3
	​

	​

∣≤9.
	​


This is the first exact cut I would add.

8. Maximum-rectangle neighbour lemma

Let P have cycle components

C
1
	​

,…,C
k
	​

.

If m
r
	​

=6, then X
r
	​

∪Y
r
	​

 chooses exactly one side of each cycle component. Encode this choice by an orientation vector

σ
r
	​

∈{A,B}
k
.

Define 
σ
r
	​

	​

 to be the complementary orientation.

If rr
′
∈E
R
	​

, then

X
r
′
	​

⊆A∖X
r
	​

,Y
r
′
	​

⊆B∖Y
r
	​

.

Therefore:

m
r
	​

=6, rr
′
∈E
R
	​

⟹X
r
′
	​

∪Y
r
′
	​

⊆I
σ
r
	​

	​

	​

,
	​


where I
σ
r
	​

	​

	​

 is the maximum independent set corresponding to the complementary component orientation.

In particular,

m
r
	​

=m
r
′
	​

=6, rr
′
∈E
R
	​

⟹σ
r
′
	​

=
σ
r
	​

	​

.
	​


This is much stronger than the raw disjointness clauses. It turns m=6 vertices into component-orientation states.

For the three possible P-types:

C
8
	​

+C
4
	​

: only two mixed maximum orientations are usable by zero/singleton vertices;

C
6
	​

+C
6
	​

: again only two mixed maximum orientations are usable;

C
4
	​

+C
4
	​

+C
4
	​

: six mixed maximum orientations are usable, arranged in three complementary pairs.

Since at least four R-vertices have m
r
	​

=6, this orientation cut should be substantial.

9. Why I would not expect a short scalar contradiction

The extreme profile already shows why scalar counting alone is weak.

For

(ZZ,ZS
1
	​

,ZS
2
	​

,ZD,S
1
	​

S
2
	​

)=(0,3,3,3,16),

all three zero vertices are terminal tight and have m
z
	​

=5. This is compatible with

M=74

because the remaining ten singleton vertices plus the doubleton vertex can still carry

74−3⋅5=59

incidences, and their total maximum is

11⋅6=66.

The contradiction, if present, is not in the scalar totals. It is in the simultaneous realization of:

X
r
	​

∪Y
r
	​

 as independent sets of a disconnected 2-factor P,
R-edge disjointness of X,Y,

the rectangle two-cover of F, and the local nonedge-codegree constraints.

So I would not spend more time searching for a category-only inequality. The correct next object is a small state verifier.

10. Smallest finite verifier specification

This verifier is not a broad SAT sweep. It uses the 2-factor structure of A−B and tabled independent-set states.

Step 1: enumerate only three A−B templates

By the disconnectedness lemma, P is one of:

C
8
	​

+C
4
	​

,C
6
	​

+C
6
	​

,C
4
	​

+C
4
	​

+C
4
	​

.

Discard C
12
	​

.

For each template, precompute all states

s=(X
s
	​

,Y
s
	​

)

such that

X
s
	​

×Y
s
	​

⊆F.

Each state has weight

m(s):=∣X
s
	​

∣+∣Y
s
	​

∣≤6.

In a canonical labelled template, the number of raw independent-set states is only about 330. After label lower bounds, it is smaller.

Step 2: enumerate terminal R-graphs, not A/B-incidences

For each of the 124 UNKNOWN category profiles, enumerate R-graphs satisfying:

allowed edge types only:

ZZ, ZS
1
	​

, ZS
2
	​

, ZD, S
1
	​

S
2
	​

;

exact category counts:

(a,b,c,f,x);

R-triangle-free;

local domination:

r∈
/
U
i
	​

⟹d
R
	​

(r,U
i
	​

)≥2;

terminal tight cut:

d
R
	​

(r,U
i
	​

)=2⟹d
R
	​

(r)≤4.

If an R-graph violates the terminal tight cut, do not keep it in the terminal q=14 verifier; reroot it to q<14.

Step 3: assign one independent-set state to each R-vertex

For each r∈R, choose a state

s
r
	​

=(X
r
	​

,Y
r
	​

).

Allowed states depend on the label:

if r∈Z:

∣X
r
	​

∣≥2,∣Y
r
	​

∣≥2;

if r∈S
1
	​

∪S
2
	​

:

∣X
r
	​

∣≥1,∣Y
r
	​

∣≥1;

if r∈D: no x/y-codegree lower bound from A/B, but still enforce degree lower.

Also enforce

m
r
	​

≥L(r),

where L(r) is the lower bound from the neighbour-capacity lemma.

Finally enforce

r∈R
∑
	​

m
r
	​

=74.
Step 4: R-edge compatibility table

For every rr
′
∈E
R
	​

, require

X
r
	​

∩X
r
′
	​

=∅,

and

Y
r
	​

∩Y
r
′
	​

=∅.

This is just a precomputed forbidden-pair table on states.

Also add the stronger maximum-rectangle orientation rule:

m
r
	​

=6, rr
′
∈E
R
	​

⟹X
r
′
	​

∪Y
r
′
	​

⊆I
σ
r
	​

	​

	​

.

This follows from the same disjointness but is a much stronger propagation rule.

Step 5: A/B-degree constraints

Each A-vertex and each B-vertex needs at least five R-neighbours:

r∈R
∑
	​

1[a∈X
r
	​

]≥5(a∈A),
r∈R
∑
	​

1[b∈Y
r
	​

]≥5(b∈B).

Also every A/B-vertex must see both root colours through R-neighbours:

∀a∈A,∃r∈S
1
	​

∪D with a∈X
r
	​

,
∀a∈A,∃r∈S
2
	​

∪D with a∈X
r
	​

,

and similarly for every b∈B.

Step 6: rectangle two-cover of the 24 missing cells

For every (a,b)∈F, enforce

r∈R
∑
	​

1[a∈X
r
	​

, b∈Y
r
	​

]≥2.

For every (a,b)∈E(P), the coverage is automatically zero because every state satisfies

X
r
	​

×Y
r
	​

⊆F.

This exactly encodes:

ρ(a,b)=0 on the 12 A−B edges,

and

ρ(a,b)≥2 on the 24 A−B nonedges.
Step 7: same-side A−A and B−B nonedge codegrees

For a,a
′
∈A, a

=a
′
, the pair aa
′
 is a nonedge. It already has x as a common neighbour. So it needs at least one additional common neighbour, either in B through P, or in R. Enforce:

∣N
P
	​

(a)∩N
P
	​

(a
′
)∣+
r∈R
∑
	​

1[a,a
′
∈X
r
	​

]≥1.

Similarly, for b,b
′
∈B,

∣N
P
	​

(b)∩N
P
	​

(b
′
)∣+
r∈R
∑
	​

1[b,b
′
∈Y
r
	​

]≥1.
Step 8: A−R and B−R missing-incidence codegrees

For a∈A and r∈R with a∈
/
X
r
	​

, enforce

∣N
P
	​

(a)∩Y
r
	​

∣+
u∈N
R
	​

(r)
∑
	​

1[a∈X
u
	​

]≥2.

The first term counts common neighbours in B. The second counts common neighbours in R.

Similarly, for b∈B and r∈R with b∈
/
Y
r
	​

, enforce

∣N
P
	​

(b)∩X
r
	​

∣+
u∈N
R
	​

(r)
∑
	​

1[b∈Y
u
	​

]≥2.

These are exact local common-neighbour constraints.

Step 9: optional but recommended R−R nonedge codegrees

For nonadjacent r,r
′
∈R, enforce

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
)∣≥2.

This is the exact minimum-codegree condition for R−R nonedges.

Step 10: rooted cuts

Finally, check the paired rooted cuts exactly. Since R has only 14 vertices, the 2
14
 masks are small in this state model. They can be checked lazily, but after the state constraints above, the candidate count should be far smaller than in the raw SAT encoding.

11. The most useful new cuts to add immediately

If you want the smallest incremental changes before rebuilding the verifier, add these three cuts.

Cut A: disconnected A−B

Reject the C
12
	​

 A−B type.

Equivalently:

P

=C
12
	​

.
Cut B: terminal tight R-degree

For every r∈R∖U
i
	​

,

d
R
	​

(r,U
i
	​

)=2⟹d
R
	​

(r)≤4.

If this fails, reroot to q<14.

Cut C: neighbour-union capacity

For every r∈R,

∣
u∈N
R
	​

(r)
⋃
	​

X
u
	​

∣+∣
u∈N
R
	​

(r)
⋃
	​

Y
u
	​

∣≤12−L(r).

In particular, in the extreme profile,

∣X
z
1
	​

	​

∪X
z
2
	​

	​

∪X
z
3
	​

	​

∣+∣Y
z
1
	​

	​

∪Y
z
2
	​

	​

∪Y
z
3
	​

	​

∣≤9.

This is likely the most effective new exact check for the stubborn ZZ=0,ZD=3,S
1
	​

S
2
	​

=16 profile.

Weakest steps

I do not claim a full hand contradiction for the p=12,e
R
	​

=25 row. The scalar totals still have enough slack.

The strongest rigorous hand conclusions are:

P is disconnected,
r∈R
∑
	​

(6−m
r
	​

)=10,
#{r:m
r
	​

=6}≥4,
T
S
	​

≥max(0,30−2S
1
	​

S
2
	​

),
T
Z
	​

≥max(0,S
1
	​

S
2
	​

+ZZ−ZD−7),

and, in the terminal q=14 layer,

d
R
	​

(r,U
i
	​

)=2⟹d
R
	​

(r)≤4.

The remaining obstruction is exact incidence realization over the three disconnected A−B 2-factor templates. The smallest decisive finite check is the state verifier above: precompute independent-set states of C
8
	​

+C
4
	​

, C
6
	​

+C
6
	​

, and 3C
4
	​

; assign one state to each R-vertex; enforce R-edge disjointness, rectangle two-cover, local nonedge-codegrees, and rooted cuts.