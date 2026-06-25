A useful new reduction is a C-tight reroot / clean-shadow dichotomy.

It does not solve the q=14,t=2 branch by itself, but it gives a real scalar strengthening on the “clean” side and identifies the exact obstruction on the remaining side.

1. First small scalar fact: p≥12

This is not in your listed scalar constraints, though your exact verifier may already enforce it.

For a∈A, the pair ay is a nonedge. Its common neighbours are exactly the B-neighbours of a:

N(a)∩N(y)=N
B
	​

(a).

Indeed, y is adjacent only to B∪C, while a is not adjacent to y, not adjacent to C, and A is independent. Since every nonedge has at least 2 common neighbours,

d
B
	​

(a)≥2.

Summing over the six vertices of A,

p=e(A,B)=
a∈A
∑
	​

d
B
	​

(a)≥12.

Similarly every b∈B has d
A
	​

(b)≥2.

So throughout the q=14,t=2 branch,

p≥12.
	​


This matters only when e
R
	​

 is forced large.

2. Define C-tight vertices

Write

u
i
	​

=∣U
i
	​

∣.

For r∈R∖U
i
	​

, the nonedge c
i
	​

r has common neighbours exactly

N
R
	​

(r)∩U
i
	​

.

There are no common neighbours through x,y,A,B, or the other c
j
	​

. Hence

codeg(c
i
	​

,r)=d
R
	​

(r,U
i
	​

).

The default local condition is therefore

d
R
	​

(r,U
i
	​

)≥2.

Call r∈R∖U
i
	​

 i-tight if

d
R
	​

(r,U
i
	​

)=2.

The new dichotomy is:

Either there is a C-tight R-vertex, or all r∈R∖U
i
	​

 satisfy d
R
	​

(r,U
i
	​

)≥3.
	​


The second side gives a stronger q=14 shadow lemma.

3. Clean C-shadow lemma

Assume the clean condition:

∀i∈{1,2}, ∀r∈R∖U
i
	​

,d
R
	​

(r,U
i
	​

)≥3.

Then

e
R
	​

≥3max(s
1
	​

,s
2
	​

)+η(d)z,
	​


where

η(d)=
⎩
⎨
⎧
	​

6,
5,
4,
3,
	​

d=0,
d=1,
d=2,
d≥3.
	​

Proof

A vertex of type S
1
	​

={1} lies outside U
2
	​

, so under the clean assumption it has at least 3 R-neighbours in U
2
	​

. But S
1
	​

-vertices can only be adjacent to S
2
	​

-vertices inside U
2
	​

=S
2
	​

∪D, because S
1
	​

−D edges are forbidden by triangle-freeness through c
1
	​

. Therefore

e(S
1
	​

,S
2
	​

)≥3s
1
	​

.

Similarly,

e(S
1
	​

,S
2
	​

)≥3s
2
	​

.

Thus

e(S
1
	​

,S
2
	​

)≥3max(s
1
	​

,s
2
	​

).

Now take a zero-label vertex r∈Z. It lies outside both U
1
	​

 and U
2
	​

, so it must have at least 3 neighbours in U
1
	​

=S
1
	​

∪D and at least 3 neighbours in U
2
	​

=S
2
	​

∪D.

If r uses k neighbours in D, those k edges count simultaneously toward both requirements. The remaining deficits are

(3−k)
+
	​

toward S
1
	​

,

and

(3−k)
+
	​

toward S
2
	​

.

So r has at least

k+(3−k)
+
	​

+(3−k)
+
	​


incident edges to S
1
	​

∪S
2
	​

∪D. Minimizing over 0≤k≤d gives exactly

η(d)=
⎩
⎨
⎧
	​

6,
5,
4,
3,
	​

d=0,
d=1,
d=2,
d≥3.
	​


Summing over all z zero vertices gives at least η(d)z edges incident from Z to S
1
	​

∪S
2
	​

∪D. These edges are disjoint from the S
1
	​

−S
2
	​

 edges already counted. Hence

e
R
	​

≥e(S
1
	​

,S
2
	​

)+e(Z,S
1
	​

∪S
2
	​

∪D)≥3max(s
1
	​

,s
2
	​

)+η(d)z.

That proves the lemma.

4. Scalar consequence for clean rows

On the clean side,

e
R
	​

≥3max(s
1
	​

,s
2
	​

)+η(d)z.

Together with p≥12, this gives

cap=123−U−p−e
R
	​

≤111−U−(3max(s
1
	​

,s
2
	​

)+η(d)z).

So every clean row must satisfy

cap≤111−U−3max(s
1
	​

,s
2
	​

)−η(d)z.
	​


This is a genuine new scalar filter. It is strictly stronger than the listed

e
R
	​

≥2max(s
1
	​

,s
2
	​

)+h(d)z

whenever the row has no C-tight R-vertex.

5. What happens at cap 74

At cap 74,

74=123−U−p−e
R
	​

,

and since p+e
R
	​

≥37, we must have

U=12,p+e
R
	​

=37.

Also p≥12, so

e
R
	​

≤25.

Now U=12 forces

∣U
1
	​

∣=∣U
2
	​

∣=6.

Equivalently,

(z,d,s
1
	​

,s
2
	​

)=(d+2,d,6−d,6−d),

with the locally feasible cases

d=0,1,2,3,4,6.

The clean-shadow lower bound gives:

d
0
1
2
3
4
6
	​

(z,d,s
1
	​

,s
2
	​

)
(2,0,6,6)
(3,1,5,5)
(4,2,4,4)
(5,3,3,3)
(6,4,2,2)
(8,6,0,0)
	​

e
R
	​

≥3max(s
1
	​

,s
2
	​

)+η(d)z
30
30
28
24
24
24
	​

	​


Since cap 74 also has e
R
	​

≤25, the clean rows with d=0,1,2 are impossible.

Thus the only clean cap-74 survivors are

(z,d,s
1
	​

,s
2
	​

)∈{(5,3,3,3),(6,4,2,2),(8,6,0,0)},
	​


and for each of them,

(e
R
	​

,p)∈{(24,13),(25,12)}.
	​


So cap 74 is reduced to six clean scalar rows.

All other cap-74 rows must contain a C-tight R-vertex.

6. Rerooting meaning of the tight obstruction

Suppose r∈R∖U
i
	​

 is i-tight:

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

r is a nonedge with exactly two common neighbours. Let

P=N
R
	​

(r)∩U
i
	​

,∣P∣=2.

Use c
i
	​

r as a new low-codegree root. Then the new common-neighbour set is P. The new A-side has size

∣N(c
i
	​

)∖P∣=deg(c
i
	​

)−2=(2+u
i
	​

)−2=u
i
	​

.

The new B-side has size

deg(r)−2.

So the new residual size is

q
′
=30−2−2−u
i
	​

−(deg(r)−2)=28−u
i
	​

−deg(r).

Since u
i
	​

≥6 and deg(r)≥8,

q
′
≤14.

Moreover,

q
′
<14

unless

u
i
	​

=6anddeg(r)=8.

Therefore:

A C-tight R-vertex either reroots to a smaller q branch,
	​


or it is an extremal tight witness with

u
i
	​

=6,deg(r)=8.
	​


This is the exact missing obstruction.

If your global proof tree already closes all t=2 branches with q<14, then in the q=14 branch one may choose xy among minimum-codegree nonedges with q minimal. Under that extra choice, every C-tight R-vertex must satisfy

u
i
	​

=6,deg(r)=8.

That is a strong structural reduction for the tight side.

7. Asymmetric q-minimal version

Under the extra assumption that the root xy is chosen q-minimal among all t=2 roots, and that smaller q branches are already closed, one gets a partially clean shadow automatically.

Define

λ
i
	​

={
3,
2,
	​

u
i
	​

>6,
u
i
	​

=6.
	​


Then every r∈R∖U
i
	​

 satisfies

d
R
	​

(r,U
i
	​

)≥λ
i
	​

.

The same counting proof gives

e
R
	​

≥max(λ
2
	​

s
1
	​

,λ
1
	​

s
2
	​

)+zη
λ
1
	​

,λ
2
	​

	​

(d),
	​


where

η
λ
1
	​

,λ
2
	​

	​

(d)=
0≤k≤d
min
	​

[k+(λ
1
	​

−k)
+
	​

+(λ
2
	​

−k)
+
	​

].

This is weaker than the fully clean 3,3 shadow, but it is available after q-minimal rerooting without assuming the absence of all tight C-R pairs.

8. Why this still does not close q14/t2 by hand

The clean-shadow lemma does not prove cap ≤40. The zero/doubleton-heavy rows survive.

The hard clean cap-74 survivors are exactly the rows

(5,3,3,3),(6,4,2,2),(8,6,0,0),

with

(e
R
	​

,p)=(24,13)or(25,12).

These are not killed by scalar counting because the extra R-edges can be placed in the Z−D part, while p drops to the minimum range allowed by p≥12. The scalar budget still permits enough A/B-R incidence.

The obstruction is therefore not merely label-counting. It is the exact compatibility of:

A/B-R incidences,

with

R-edges,

and with

A-B edges.

The two key triangle-free incompatibilities are:

rr
′
∈E
R
	​

⟹N
A
	​

(r)∩N
A
	​

(r
′
)=∅,N
B
	​

(r)∩N
B
	​

(r
′
)=∅,

and

ab∈E(A,B)⟹N
R
	​

(a)∩N
R
	​

(b)=∅.

The scalar profile does not see these intersections.

9. Targeted finite experiment

Split the remaining q=14,t=2 jobs into two batches.

Batch I: clean C-shadow

Add the static scalar cut

e
R
	​

≥3max(s
1
	​

,s
2
	​

)+η(d)z.

Then cap 74 collapses to the six rows

	​

(z,d,s
1
	​

,s
2
	​

,e
R
	​

,p)
=(5,3,3,3,24,13), (5,3,3,3,25,12),
=(6,4,2,2,24,13), (6,4,2,2,25,12),
=(8,6,0,0,24,13), (8,6,0,0,25,12).
	​


Run the exact fixed-label verifier only on these clean high-cap survivors.

Batch II: C-tight reroot side

Add a canonical witness

r∈R∖U
i
	​

,d
R
	​

(r,U
i
	​

)=2.

If using q-minimal rooting and smaller q branches are closed, also impose

u
i
	​

=6,deg(r)=8.

Then pin the two common neighbours

P=N
R
	​

(r)∩U
i
	​

,∣P∣=2.

The label cases are tiny:

For i=1,

r∈Z∪S
2
	​

.

If r∈S
2
	​

, then its two U
1
	​

-neighbours must lie in S
1
	​

, because S
2
	​

−D edges are forbidden.

If r∈Z, its two U
1
	​

-neighbours may lie in S
1
	​

∪D.

The i=2 cases are symmetric.

This is much smaller than the raw cap 41…74 frontier and directly attacks the obstruction that prevents a hand scalar closure.

Weakest steps and assumptions

The clean-shadow inequality itself is unconditional once the clean condition

d
R
	​

(r,U
i
	​

)≥3

is assumed.

The rerooting reduction uses the additional proof-tree assumption that q<14 t=2 branches are already closed, or that the chosen root is q-minimal among all t=2 nonedges. Without that, a C-tight vertex is not a contradiction; it is only a certificate that the current root was not the most reduced one.

The lemma does not close q=14,t=2. The remaining obstruction is precisely the C-tight side plus the clean zero/doubleton-heavy rows above.