I do not see a valid hand proof eliminating the two clean rows from D-only Φ-cuts alone. In fact, the rooted-cut layer gives a strong necessary inequality, but it is still compatible with cap 74 at the aggregate-incidence level. The missing obstruction is the exact A/B-R incidence realization together with the A-B edge/nonedge dichotomy.

Here is the clean reduction.

1. Specialize the clean z=8,d=6 row

We have

Z={r:L(r)=∅},∣Z∣=8,
D={r:L(r)={1,2}},∣D∣=6.

Thus

U
1
	​

=U
2
	​

=D,U=12.

The only possible R-edges are

Z−DandZ−Z.

There are no D−D edges.

Let

L:=e
R
	​

(Z,D),H:=e
R
	​

(Z,Z).

Then

e
R
	​

=L+H.

Cleanliness says every zero vertex has at least 3 neighbours in D. Hence

L=
z∈Z
∑
	​

d
D
	​

(z)≥8⋅3=24.

Therefore:

e
R
	​

=24⟹(L,H)=(24,0),

and

e
R
	​

=25⟹(L,H)=(25,0) or (24,1).

For the two cap 74 rows,

(p,e
R
	​

)=(13,24)or(12,25),

and in both cases

p+e
R
	​

=37.

That identity makes the rooted cuts especially sharp.

2. Exact Φ(W) formula in this row

Use the convention matching your reported bad Φ-cuts:

x,y on one side,A,B,W on the other side,

where W⊆R.

Define

M
A
	​

(W):=e(A,W),M
B
	​

(W):=e(B,W),
M(W):=M
A
	​

(W)+M
B
	​

(W),

and

k(W):=∣W∩D∣.

Let

∂
R
	​

(W)

be the number of R-edges with exactly one endpoint in W.

Then in the clean z=8,d=6 row,

Φ(W)=p+e
R
	​

−∂
R
	​

(W)+M(W)+2min(k(W),8−k(W)).
	​


Proof of the terms:

A-B edges are monochromatic, contributing p.

R-edges are monochromatic except the boundary edges, contributing e
R
	​

−∂
R
	​

(W).

A/B-R edges are monochromatic exactly when their R-endpoint lies in W, contributing M(W).

For each c
i
	​

, either put c
i
	​

 with A,B,W, costing k(W) label edges and no root edge, or put c
i
	​

 with x,y, costing 2 root edges plus 6−k(W) label edges. So one c
i
	​

 costs

min(k(W),2+6−k(W))=min(k(W),8−k(W)).

There are two c
i
	​

’s, giving

2min(k(W),8−k(W)).

Since p+e
R
	​

=37, the condition Φ(W)≥37 is equivalent to

M(W)≥∂
R
	​

(W)−2min(k(W),8−k(W)).
	​

(Φ-dom)

This is the clean cap-74 Φ-domination inequality.

3. D-only Φ-cuts

Now take W=S⊆D, and write

k=∣S∣,L(S):=e
R
	​

(S,Z),
M
D
	​

(S):=e(A∪B,S).

Because there are no D−D edges,

∂
R
	​

(S)=L(S).

Therefore the D-only Φ-cut is exactly

Φ(S)=p+e
R
	​

−L(S)+M
D
	​

(S)+2min(k,8−k).
	​


Since p+e
R
	​

=37,

Φ(S)≥37⟺M
D
	​

(S)+2min(k,8−k)≥L(S).
	​

(D-Φ)

Equivalently:

L(S)−M
D
	​

(S)≤2min(k,8−k).
	​


Explicitly,

k=∣S∣
1
2
3
4
5
6
	​

L(S)−M
D
	​

(S)≤
2
4
6
8
6
4
	​

	​


The total D-cut S=D gives

L−M
D
	​

(D)≤4,

so

M
D
	​

(D)≥L−4.
	​


Hence:

(p,e
R
	​

)=(13,24)⟹M
D
	​

(D)≥20,

and

(p,e
R
	​

)=(12,25), H=0⟹M
D
	​

(D)≥21,

while

(p,e
R
	​

)=(12,25), H=1⟹M
D
	​

(D)≥20.

This is a real structural requirement: the six doubleton vertices must carry roughly twenty or more A/B-incidences.

For individual doubletons d∈D, the singleton D-cut gives

M
D
	​

(d)≥d
Z
	​

(d)−2.
	​


For three doubletons S⊆D, which matches your bad analyzer masks,

M
D
	​

(S)≥L(S)−6.
	​


So a bad cut such as Φ=25 on a three-D mask means precisely that

L(S)−M
D
	​

(S)=12,

whereas the exact rooted cut allows at most 6.

4. Zero-side Φ-cuts

For T⊆Z, we have k(T)=0. Therefore (Φ-dom) gives

M(T)≥∂
R
	​

(T).
	​


Here

∂
R
	​

(T)=e
R
	​

(T,D)+e
R
	​

(T,Z∖T).

In particular, for a single zero vertex z,

M(z)≥d
R
	​

(z).
	​


Together with the xz and yz nonedge-codegree requirements,

d
A
	​

(z)≥2,d
B
	​

(z)≥2,

so

M(z)≥max(4,d
R
	​

(z)).
	​


This still does not contradict cap 74. In the e
R
	​

=24 clean case, every zero can have exactly three D-neighbours, so the stronger lower bound is just M(z)≥4, giving M(Z)≥32.

5. Exact Ψ(W) formula

For the opposite-root cut, put

x,B,R∖W

on one side and

y,A,W

on the other side. Swapping the two root sides exchanges A and B, so the dangerous value is the smaller of the two orientations.

For W⊆R, with

k(W)=∣W∩D∣,

the clean z=8,d=6 formula is

Ψ(W)=e
R
	​

−∂
R
	​

(W)+2+2min(k(W),6−k(W))+min{M
A
	​

(W)+M
B
	​

(R∖W), M
B
	​

(W)+M
A
	​

(R∖W)}.
	​


Explanation:

A-B edges cross, so they contribute 0.

R-edges contribute e
R
	​

−∂
R
	​

(W).

A/B-R monochromatic edges contribute one of the two displayed orientation sums.

Each c
i
	​

 contributes one root monochromatic edge, plus the smaller of the label edges to D∩W and D∖W. Since U
i
	​

=D, the two c
i
	​

’s contribute

2+2min(k(W),6−k(W)).

Thus Ψ(W)≥37 is equivalent to

min{M
A
	​

(W)+M
B
	​

(R∖W), M
B
	​

(W)+M
A
	​

(R∖W)}≥35−e
R
	​

+∂
R
	​

(W)−2min(k(W),6−k(W)).
	​

(Ψ-split)

The most important special case is W=Z. Then

k(W)=0,∂
R
	​

(Z)=L=e
R
	​

−H.

Therefore

min{M
A
	​

(Z)+M
B
	​

(D), M
B
	​

(Z)+M
A
	​

(D)}≥35−H.
	​

(Ψ
Z
	​

)

Equivalently, both inequalities must hold:

M
A
	​

(Z)+M
B
	​

(D)≥35−H,
	​

M
B
	​

(Z)+M
A
	​

(D)≥35−H.
	​


Adding them gives

M(A∪B,R)≥70−2H.

Since cap =74, this leaves only small slack:

H=0⟹M≥70,
H=1⟹M≥68.

So the exact rooted cuts are genuinely strong, but still not strong enough to force M>74.

6. Why D-only Φ-cuts do not eliminate the family

The D-only cuts force

M
D
	​

(D)≥L−4,

but this is compatible with cap 74.

For example, in the (p,e
R
	​

)=(13,24) row:

L=24,H=0,

so D-only Φ gives only

M
D
	​

(D)≥20.

The zero vertices already require at least

M
Z
	​

≥8⋅4=32.

Thus the rooted-cut lower bound gives roughly

M
Z
	​

+M
D
	​

≥52,

or, using Ψ
Z
	​

,

M≥70.

But cap is

M=74.

There is still slack 4. That slack is exactly where the aggregate rooted-cut layer fails to close the row.

7. Aggregate rooted-cut witness: rooted cuts alone are insufficient

Here is a concrete aggregate witness showing that the Φ/Ψ rooted-cut inequalities, even all of them, do not by themselves eliminate the (p,e
R
	​

)=(13,24) row.

Let

Z={z
0
	​

,…,z
7
	​

},D={d
0
	​

,…,d
5
	​

}.

Take the following Z−D edges:

N
D
	​

(z
0
	​

)
N
D
	​

(z
1
	​

)
N
D
	​

(z
2
	​

)
N
D
	​

(z
3
	​

)
N
D
	​

(z
4
	​

)
N
D
	​

(z
5
	​

)
N
D
	​

(z
6
	​

)
N
D
	​

(z
7
	​

)
	​

={d
0
	​

,d
1
	​

,d
4
	​

},
={d
1
	​

,d
4
	​

,d
5
	​

},
={d
0
	​

,d
3
	​

,d
5
	​

},
={d
0
	​

,d
2
	​

,d
4
	​

},
={d
1
	​

,d
2
	​

,d
3
	​

},
={d
2
	​

,d
3
	​

,d
5
	​

},
={d
0
	​

,d
1
	​

,d
3
	​

},
={d
2
	​

,d
4
	​

,d
5
	​

}.
	​


Then every zero vertex has D-degree 3, every doubleton vertex has Z-degree 4, and

e
R
	​

=24.

There are no Z−Z edges and no D−D edges.

Now assign aggregate A/B-incidence counts as follows:

M
A
	​

(z
i
	​

)=M
B
	​

(z
i
	​

)=3for every z
i
	​

∈Z.

For the doubletons, set

(M
A
	​

(d
0
	​

),M
B
	​

(d
0
	​

))=(3,2),
(M
A
	​

(d
1
	​

),M
B
	​

(d
1
	​

))=(2,3),

and

(M
A
	​

(d
j
	​

),M
B
	​

(d
j
	​

))=(2,2)for j=2,3,4,5.

Then

M
A
	​

(R)=37,M
B
	​

(R)=37,

so

M=74.

Also

p=13,e
R
	​

=24,p+e
R
	​

=37.

This aggregate object satisfies all Φ-cuts.

Indeed, take any W=T∪S, with

T⊆Z,S⊆D,∣T∣=τ,∣S∣=k.

The R-boundary is at most the sum of selected R-degrees:

∂
R
	​

(W)≤3τ+4k.

Also

M(W)=6τ+M
D
	​

(S).

The doubleton M-weights are

5,5,4,4,4,4.

So for a k-set S⊆D,

M
D
	​

(S)≥
⎩
⎨
⎧
	​

0,
4,
8,
12,
16,
21,
26,
	​

k=0,
k=1,
k=2,
k=3,
k=4,
k=5,
k=6.
	​


One checks

M
D
	​

(S)+2min(k,8−k)≥4k

for every 0≤k≤6. Hence

M(W)+2min(k,8−k)≥6τ+4k≥3τ+4k≥∂
R
	​

(W).

So Φ(W)≥37 for every W⊆R.

It also satisfies all Ψ-cuts. Let

Δ(W):=M
A
	​

(W)−M
B
	​

(W).

All zero vertices have Δ=0. Among doubletons, d
0
	​

 has Δ=1, d
1
	​

 has Δ=−1, and the others have Δ=0. Therefore

∣Δ(W)∣≤1

for every W⊆R. Since

M
A
	​

(R)=M
B
	​

(R)=37,

we have

min{M
A
	​

(W)+M
B
	​

(R∖W), M
B
	​

(W)+M
A
	​

(R∖W)}=37−∣Δ(W)∣≥36.

Also

e
R
	​

−∂
R
	​

(W)≥0

and

2+2min(k,6−k)≥2.

Therefore

Ψ(W)≥36+2=38

for every W⊆R.

So the rooted-cut layer alone is not enough.

The same construction also gives an aggregate witness for (p,e
R
	​

)=(12,25): add one extra Z−D edge, say z
0
	​

d
2
	​

, keep the same A/B-incidence weights, and set p=12. The cap is still 74, and the same Ψ proof works. The Φ proof only gains one possible extra boundary edge, which is still absorbed by the displayed D-weight table.

This is not claimed to be a valid full graph. It is an aggregate rooted-cut witness showing exactly why a hand proof from D-only Φ-cuts cannot work.

8. The exact missing obstruction

The missing condition is the realization of the A/B-incidences as actual neighbourhoods

N
A
	​

(r)⊆A,N
B
	​

(r)⊆B,

together with the A-B edge/nonedge rule.

For each pair a∈A, b∈B, define

ρ(a,b):=∣{r∈R:ar∈E, br∈E}∣.

Because A-B edges would form triangles through common R-neighbours, and because every A-B nonedge must have at least two common neighbours, we have the exact dichotomy

ab∈E(A,B)⟺ρ(a,b)=0,
	​


and

ab∈
/
E(A,B)⟺ρ(a,b)≥2.
	​


Equivalently,

ρ(a,b)

=1for every (a,b)∈A×B,
	​


and

p=#{(a,b):ρ(a,b)=0}.
	​


Thus the A/B-incidences must form a two-cover of exactly 36−p cells of the 6×6 A-B matrix by the rectangles

N
A
	​

(r)×N
B
	​

(r),

while leaving exactly p cells uncovered.

For the two hard rows:

p=13⟹23 cells must be covered at least twice and 13 cells uncovered,
p=12⟹24 cells must be covered at least twice and 12 cells uncovered.

No cell may be covered exactly once.

That condition is invisible to the scalar D-only Φ-cuts. It is also invisible to the aggregate rooted-cut witness above.

There are further compatibility constraints:

If rr
′
∈E
R
	​

, then triangle-freeness forces

N
A
	​

(r)∩N
A
	​

(r
′
)=∅,
	​


and

N
B
	​

(r)∩N
B
	​

(r
′
)=∅.
	​


For zero vertices,

∣N
A
	​

(z)∣≥2,∣N
B
	​

(z)∣≥2.
	​


Every a∈A and b∈B must hit D, because ac
i
	​

 and bc
i
	​

 are nonedges and U
i
	​

=D:

∀a∈A,N
R
	​

(a)∩D

=∅,
	​

∀b∈B,N
R
	​

(b)∩D

=∅.
	​


And the same A/B-incidence sets must also satisfy A-A, B-B, A-R, and B-R nonedge-codegree lower bounds.

But the central missing obstruction is the rectangle two-cover condition

ρ(a,b)∈{0}∪[2,∞),#{ρ=0}=p.
9. Targeted finite experiment

The right finite certificate is much smaller than brute-forcing all cap 41…74 rows.

For the clean z=8,d=6, cap 74 family, enumerate only the following.

First enumerate R:

For (p,e
R
	​

)=(13,24):

R is a Z−D graph with 24 edges,

every z∈Z has D-degree exactly 3, and there are no Z−Z edges.

For (p,e
R
	​

)=(12,25), either:

L=25, H=0,

or

L=24, H=1.

In the H=1 case, every zero vertex has D-degree exactly 3, and the two endpoints of the unique Z−Z edge must have disjoint D-neighbourhoods; otherwise a triangle zz
′
d appears.

Then enumerate only the A/B-incidence sets

N
A
	​

(r),N
B
	​

(r)⊆[6]

subject to:

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
∣N
A
	​

(z)∣≥2,∣N
B
	​

(z)∣≥2(z∈Z),
r∈R
∑
	​

(∣N
A
	​

(r)∣+∣N
B
	​

(r)∣)=74,

the exact Φ/Ψ inequalities above, and the rectangle rule

ρ(a,b):=∣{r:a∈N
A
	​

(r), b∈N
B
	​

(r)}∣

satisfies

ρ(a,b)

=1

for all 36 pairs, with

#{(a,b):ρ(a,b)=0}=p.

Then derive E(A,B) from ρ(a,b)=0 rather than choosing A-B edges independently.

After that, check the remaining nonedge-codegree constraints:

A−A,B−B,A−R,B−R.

This is the exact finite obstruction. If this tiny incidence-realization problem is UNSAT for the two rows, then the clean cap 74 family is closed. If it is SAT, the surviving model will identify which non-rooted codegree condition is still needed.

Weakest steps and assumptions

The Φ and Ψ formulae above use the stated root structure and the convention that W is placed with A,B in the Φ-cut. If your implementation uses the complementary convention, replace W by R∖W; the all-W inequalities are equivalent.

The aggregate rooted-cut witnesses are not asserted to be valid graphs. They only show that rooted-cut inequalities, including all D-only Φ-cuts, do not force a contradiction by themselves.

The extra condition needed is not another scalar cap inequality. It is the 6×6 rectangle compatibility:

ρ(a,b)=0 on exactly p cells,ρ(a,b)≥2 on all other cells.

That is the targeted finite condition to encode next.