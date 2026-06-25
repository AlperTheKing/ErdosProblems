Recommended strengthening

The best next move is a combination of:

Exact root-pair transposition, which makes idx344 redundant with idx270 and makes idx360 self-dual.

The open-neighborhood cut at each E-vertex, projected to a cheap degree cap before state enumeration and retained in exact form inside the count quotient.

The second item is the genuinely useful new cut: unlike the current Ψ/U families over W⊆R, it colors only those A/B copies whose states contain the chosen E-vertex.

1. Exact transposition of the two root pairs

Let the original nonedge roots be x,y, with common neighbors c
1
	​

,c
2
	​

. Since D=∅,

N(c
1
	​

)∩N(c
2
	​

)={x,y}.

Indeed:

c
1
	​

c
2
	​

∈
/
E(G), by triangle-freeness through x;

no A-vertex is adjacent to c
i
	​

, by the triangle x−a−c
i
	​

−x;

no B-vertex is adjacent to c
i
	​

, similarly through y;

an R-vertex adjacent to both c
1
	​

,c
2
	​

 would be labelled D, and there are none.

Hence c
1
	​

,c
2
	​

 are themselves an exact-codegree-two root pair.

Rerooting at c
1
	​

,c
2
	​

 gives

A
†
=S
1
	​

,B
†
=S
2
	​

,R
†
=A∪B∪E.

Relative to the new common neighbors x,y:

old A receives label S
1
†
	​

;

old B receives label S
2
†
	​

;

old E remains E
†
.

Thus the profile transformation is

(q,a,b;c
0
	​

,c
1
	​

,c
2
	​

,0)⟼(a+b+c
0
	​

,c
1
	​

,c
2
	​

;c
0
	​

,a,b,0).

Consequently,

idx270⟷idx344
	​

,
idx360⟷idx360
	​

.

So, provided the K2/T2 branch is existential over exact-codegree-two root pairs rather than tied to a distinguished root-selection predicate, idx344 should not be searched at all. Closing idx270 closes idx344 automatically.

Scalar transposition map

Write

h
t
i
	​

e
0
	​

M
E
	​

M
i
	​

	​

=e(S
1
	​

,S
2
	​

),
=e(E,S
i
	​

),t=t
1
	​

+t
2
	​

,
=e(E),
=e(A∪B,E),
=e(A∪B,S
i
	​

).
	​


Then under transposition,

p
†
e
R
†
	​

M
1
†
	​

M
2
†
	​

M
†
	​

=h,
=p+M
E
	​

+e
0
	​

,
=M
1
	​

+t
1
	​

,
=M
2
	​

+t
2
	​

,
=M−M
E
	​

+t.
	​

	​


These identities are exact and count-quotient compatible:

M
E
	​

=
I
∑
	​

∣I∩E∣A
I
	​

+
J
∑
	​

∣J∩E∣B
J
	​

,

and similarly for M
1
	​

,M
2
	​

.

Every existing sound scalar/profile filter should therefore be imposed both on the original tuple and on the transposed tuple. A small AddAllowedAssignments table over

(p
†
,e
R
†
	​

,M
1
†
	​

,M
2
†
	​

)

is enough. The table must come from exhaustive safe scalar constraints, not from the reported sample ranges.

For self-dual idx360, an immediate symmetry break is

e
R
	​

≤p+M
E
	​

+e
0
	​

.
	​


On equality, add p≤h. One of the two root orientations always satisfies this lexicographic condition.

2. Main new cut: the open-neighborhood cut
Lemma

For every vertex v in a triangle-free graph with β(G)≥37,

u∈N(v)
∑
	​

d(u)≤e(G)−37.
	​

(ND)
Proof

Triangle-freeness makes N(v) independent. Consider the bipartition

N(v) 
	​

 V(G)∖N(v).

Every edge incident with N(v) crosses this cut, and there are no edges internal to N(v). Hence the number of uncut edges is exactly

e(G)−
u∈N(v)
∑
	​

d(u).

Since every cut leaves at least β(G)≥37 uncut edges, (ND) follows.

This uses no terminal-touch equality, no C-tight endpoint equality, and no H14 anti-tightness.

Cheap degree-cap projection

If the current audited reduction includes δ(G)≥R
0
	​

, then (ND) implies

R
0
	​

d(v)≤e(G)−37.
	​

(ND-R
0
	​

)

For the current R
0
	​

=8,

8d(v)≤e(G)−37.
	​

(ND8)

Because e(G)≤143,

d(v)≤⌊
8
143−37
	​

⌋=13.

This gives a dynamic upper-degree window in addition to the current lower-degree window.

For every used A-state I,

d
A
	​

(I)=1+∣I∣+
J:I∩J=∅
∑
	​

B
J
	​

,

so add, conditionally on A
I
	​

>0,

8(1+∣I∣+
J:I∩J=∅
∑
	​

B
J
	​

)≤e(G)−37.
	​


Likewise for B
J
	​

>0. For every r∈R, unconditionally,

8(λ
r
	​

+d
R
	​

(r)+α
r
	​

+β
r
	​

)≤e(G)−37,
	​


where λ
r
	​

∈{0,1} is its C-label size in these branches.

These constraints are linear apart from the existing support reification.

3. Specialization to an E-vertex

Let z∈E. Define

t
z
	​

=d
R
	​

(z,S
1
	​

)+d
R
	​

(z,S
2
	​

),ε
z
	​

=d
R
	​

(z,E∖{z}).

Since z is empty-labelled,

d
G
	​

(z)=α
z
	​

+β
z
	​

+t
z
	​

+ε
z
	​

.

Moreover,

α
z
	​

β
z
	​

d
R
	​

(z,S
1
	​

)
d
R
	​

(z,S
2
	​

)
	​

=codeg(x,z)≥2,
=codeg(y,z)≥2,
=codeg(c
1
	​

,z)≥2,
=codeg(c
2
	​

,z)≥2.
	​


Thus the projected neighborhood cut is

8(α
z
	​

+β
z
	​

+t
z
	​

+ε
z
	​

)≤e(G)−37.
	​

(E-ND8)

In particular,

α
z
	​

+β
z
	​

+t
z
	​

+ε
z
	​

≤13,

and hence

t
z
	​

+ε
z
	​

≤9.
	​


If the two E-vertices are adjacent in idx360, then ε
z
	​

=1, so t
z
	​

≤8.

Immediate branch compression

Using only the edge cap, for one E-vertex:

t
z
	​

+ε
z
	​

	Minimum possible e(G)
4	101
5	109
6	117
7	125
8	133
9	141
≥10	impossible

It also sharply bounds the (α
z
	​

,β
z
	​

) branch:

α
z
	​

+β
z
	​

≤⌊
8
e(G)−37
	​

⌋−t
z
	​

−ε
z
	​

.

At the cap e(G)≤143:

t
z
	​

+ε
z
	​

=9 forces (α
z
	​

,β
z
	​

)=(2,2);

t
z
	​

+ε
z
	​

=8 allows only sums at most 5;

t
z
	​

+ε
z
	​

=7 allows only sums at most 6.

That is a small exact branch decomposition before any state-support materialization.

4. Profile-specific task floors

Let

F=a+b+4+U,e(G)=F+p+M+e
R
	​

.

For idx270 and idx344, F=29. There is one E-vertex and ε
z
	​

=0, so

p+M≥8(α
z
	​

+β
z
	​

+t
z
	​

)+8−e
R
	​

.
	​


Using only α
z
	​

,β
z
	​

≥2,

p+M≥40+8t
z
	​

−e
R
	​

.
	​

(270-floor)

Since e
R
	​

=h+t
z
	​

, this can also be written

p+M≥40+7e
R
	​

−8h.

For idx360, F=28, so for each E-vertex z,

p+M≥8(α
z
	​

+β
z
	​

+t
z
	​

+ε
z
	​

)+9−e
R
	​

,
	​


and coarsely,

p+M≥41+8(t
z
	​

+ε
z
	​

)−e
R
	​

.
	​

(360-floor)

These are ideal generator-level filters. If p is already fixed, update M_floor directly.

5. Exact count-quotient version

The projected ND8 cut is cheap, but the exact neighborhood cut is stronger and does not require the δ≥8 assumption.

Let

b
⊥
	​

(I)=
J:I∩J=∅
∑
	​

B
J
	​

,a
⊥
	​

(J)=
I:I∩J=∅
∑
	​

A
I
	​

.

Reuse the current product variables

Q
I
	​

=A
I
	​

b
⊥
	​

(I),R
J
	​

=B
J
	​

a
⊥
	​

(J).

They are the total numbers of A-B edges incident with the corresponding state classes.

For r∈R, let

d(r)=λ
r
	​

+d
H
	​

(r)+α
r
	​

+β
r
	​

.

For z∈E, define

D
N
	​

(z)=
	​

I:z∈I
∑
	​

((1+∣I∣)A
I
	​

+Q
I
	​

)
+
J:z∈J
∑
	​

((1+∣J∣)B
J
	​

+R
J
	​

)
+
r∈N
H
	​

(z)
∑
	​

d(r).
	​


Then add the exact linear inequality

D
N
	​

(z)≤e(G)−37.
	​

(Exact-E-ND)

There is no double counting of an A-B edge: if I∩J=∅, the states cannot both contain z.

A direct CP-SAT sketch is:

Python
Run
edge_total = fixed_edges + eR + M + p

for z in empty_vertices:
    neigh_degree = 0

    for I in A_states_containing[z]:
        neigh_degree += (1 + popcount(I)) * A[I]
        neigh_degree += AB_edges_from_A_state[I]   # A[I] * b_perp(I)

    for J in B_states_containing[z]:
        neigh_degree += (1 + popcount(J)) * B[J]
        neigh_degree += AB_edges_from_B_state[J]   # B[J] * a_perp(J)

    for r in skeleton_neighbors[z]:
        neigh_degree += (
            label_size[r]
            + skeleton_degree[r]
            + alpha[r]
            + beta[r]
        )

    model.Add(neigh_degree <= edge_total - 37)

A rejection certificate is especially simple: output z, its quotient neighborhood-degree sum, and the explicit cut N(z)∣V∖N(z).

6. Optional dual min-cut separator

After transposition, put

Q=A∪B∪E.

For v∈Q, let d
i
	​

(v) be its number of neighbors in old S
i
	​

, and let

ℓ(v)={
1,
0,
	​

v∈A∪B,
v∈E.
	​


For every W⊆Q, the three dual unpaired cuts are

F
1
	​

(W)
F
2
	​

(W)
F
3
	​

(W)
	​

=2+d
1
	​

(Q∖W)+d
2
	​

(W)+ℓ(W)+u
Q
	​

(W),
=2+d
1
	​

(W)+d
2
	​

(Q∖W)+ℓ(W)+u
Q
	​

(W),
=h+d
1
	​

(W)+d
2
	​

(W)+ℓ(W)+u
Q
	​

(W),
	​


where

u
Q
	​

(W)=e(Q[W])+e(Q[Q∖W]).

Each must be at least 37.

Since Q−E is bipartite with parts A,B, fixing the at most two E-bits and complementing the B-bits turns separation into an ordinary s-t min-cut:

idx270: 3⋅2=6 min-cuts per quotient candidate;

idx360: 3⋅4=12 min-cuts.

Twin copies of one state need not be split: the objective is linear in that class count when the other classes are fixed, so an all-or-none optimum exists.

This is only worth implementing separately if the existing “full weighted state-quotient cut” does not already separate arbitrary cuts over state classes, or if it currently runs only after the large task grid has been materialized.

Execution order

Remove idx344 from the search. Prove it only through idx270 by transposition.

On idx270, add the skeleton rejection t
z
	​

≤9, the dynamic floor (270-floor), and branch early on (α
z
	​

,β
z
	​

).

Add Exact-E-ND to the monolithic count master.

Apply every safe scalar profile filter again to the transposed scalar tuple.

Run idx360 with two E-neighborhood cuts and the self-dual symmetry break.

I would not claim these cuts alone close idx270. They should, however, eliminate idx344 entirely and compress the high-E-degree portion of idx270/360 before the hundreds-of-millions task expansion. The exact neighborhood inequality is unconditional; only its 8d(v) projection assumes the already-audited δ(G)≥8 reduction.
