The fixed-L gate is not proved or refuted here: I do not have either a uniform retained-edge argument or an actual infinite collision family with retained fraction tending to zero.

The strongest unconditional statement I can prove is the following. It rules out any refutation based on a bounded, polynomial, or insufficiently broad family of collision products, and it also rules out common-block pumping of finitely many collision templates.

Proved lemma: collisions must be exponentially dispersed

Let

Δ
k
	​

:={d∈D
k
	​

:8Q
k
+d+1∈C
k
	​

},

and put

a
k
	​

={
2,
4,
	​

ρ
k
	​

=2,
ρ
k
	​

=0.
	​


Thus

U
k
	​

={a
k
	​

(8Q
k
+d)+1:d∈Δ
k
	​

},V
k
	​

={3(8Q
k
+d)+2:d∈Δ
k
	​

}.

Set

ι
K
	​

:=∣I
K
	​

∣=⌊
3
2K
	​

⌋−⌈
3
K
	​

⌉+1.
Theorem

For every K≥2 and every product z,

r
K
	​

(z)≤τ(
2
v
2
	​

(z)
3
v
3
	​

(z)
z
	​

).
(1)

Moreover, for every fixed δ∈(0,1), there is an explicit finite constant A
δ
	​

 such that, for every set Z
K
	​

 of product values satisfying

∣Z
K
	​

∣≤60
(1−δ)K
,

one has

N
K
	​

1
	​

z∈Z
K
	​

∑
	​

r
K
	​

(z)≤
ι
K
	​

4A
δ
	​

	​

60
−δK/2
.
	​

(2)

In particular,

N
K
	​

1
	​

z∈Z
K
	​

∑
	​

r
K
	​

(z)⟶0.
(3)

Thus no collection of at most 60
(1−δ)K
 collision products can carry a positive fraction of the labelled edges.

1. Exact factor ranges and color separation

Every offset d∈D
k
	​

 satisfies

0≤d<Q
k
.
(4)

Indeed, if an affine word currently has slope M and offset d<M, applying L
m
	​

, where m∈{2,3,5}, gives offset

md+(m−2)≤m(M−1)+(m−2)=mM−2<mM.

Consequently,

ρ
k
	​

=2:
ρ
k
	​

=0:
	​

16Q
k
+1≤u≤18Q
k
−1,
32Q
k
+1≤u≤36Q
k
−3,
24Q
k
+2≤v≤27Q
k
−1.
	​

(5)

For an edge with labels i and j=K−i, it follows that

384Q
K
<uv<486Q
K
(ρ
i
	​

=2),
(6)

whereas

768Q
K
<uv<972Q
K
(ρ
i
	​

=0).
(7)

Hence two edges with the same product necessarily have the same first-factor color:

uv=u
′
v
′
⟹ρ
i
	​

=ρ
i
′
	​

.
(8)

In particular, their common coefficient a
i
	​

=a
i
′
	​

 is either 2 or 4.

2. Exact polynomial transversality

For an edge e=(i,d,e
0
	​

), with j=K−i, define

P
e
	​

(T)=(a(Q
i
T+d)+1)(3(Q
j
T+e
0
	​

)+2),
(9)

where a=a
i
	​

. Then

P
e
	​

(8)=uv.
(10)

Write

x=ad+1,y=3e
0
	​

+2.

Since d+1≡ρ
i
	​

(mod3), the choice of a gives

x≡0(mod3),x odd,
(11)

while

y≡2(mod3).
(12)

Expanding,

P
e
	​

(T)=3aQ
K
T
2
+B
e
	​

T+C
e
	​

,
(13)

where

B
e
	​

=aQ
i
y+3Q
j
x,C
e
	​

=xy.
(14)
Polynomial uniqueness

If two edges of the same total scale and the same color satisfy

P
e
	​

(T)=P
e
′
	​

(T)

as polynomials, then the labelled edges are identical.

To prove this, consider the two negative roots, whose absolute values are

aQ
i
x
	​

,
3Q
j
y
	​

.
(15)

A direct matching

aQ
i
x
	​

=
aQ
i
′
x
′
	​


gives

xQ
i
′
=x
′
Q
i
.

Because x,x
′
 are odd and v
2
	​

(Q)=3, comparison of 2-adic valuations gives

i=i
′
,

and then x=x
′
, hence d=d
′
. The remaining factor is then also identical.

A crossed matching would require

aQ
i
x
	​

=
3Q
j
′
y
′
	​

,

or

3Q
j
′
x=aQ
i
y
′
.
(16)

Let s=v
2
	​

(a)∈{1,2}. From x odd,

v
2
	​

(left side)=3j
′
,

whereas

v
2
	​

(right side)=3i+s+v
2
	​

(y
′
)≥3i+1.

Thus j
′
>i.

But 3∣x and 3∤y
′
, so

v
3
	​

(left side)=1+2j
′
+v
3
	​

(x)≥2j
′
+2,

whereas

v
3
	​

(right side)=2i.

Thus i>j
′
, a contradiction. Therefore crossed matching is impossible.

Consequence for numerical collisions

Put

s
K
	​

:=⌈
3
K
	​

⌉.

For every i∈I
K
	​

,

i≥s
K
	​

,K−i≥s
K
	​

.

Hence

Q
s
K
	​

∣B
e
	​

.
(17)

If two distinct edges satisfy

P
e
	​

(8)=P
e
′
	​

(8),

then their quadratic leading coefficients agree, and

P
e
	​

(T)−P
e
′
	​

(T)=(B
e
	​

−B
e
′
	​

)(T−8),
(18)

where

B
e
	​

−B
e
′
	​

∈Q
s
K
	​

Z∖{0}.
(19)

Equivalently, their zero-seed products satisfy

C
e
	​

≡C
e
′
	​

(mod8Q
s
K
	​

),C
e
	​


=C
e
′
	​

.
(20)

Since

0<C
e
	​

=xy<3aQ
K
≤12Q
K
,

this gives the unconditional pointwise estimate

r
K
	​

(z)≤1+
2
3
	​

Q
K−⌈K/3⌉
.
(21)

More importantly, (18) proves that every collision at the seed T=8 is transversal: two distinct edge templates cannot agree identically as affine-seed product functions.

3. Divisor injection, including all labels

For every k,

U
k
	​

⊂(16Q
k
,36Q
k
).
(22)

These intervals are disjoint for different k, because

16Q
k+1
=5760Q
k
>36Q
k
.
(23)

Within one U
k
	​

, the map d↦a
k
	​

(8Q
k
+d)+1 is injective. Thus, for fixed K and z, a labelled edge with product z is uniquely determined by its divisor u:

the size of u determines i;

u determines its offset d;

v=z/u;

j=K−i and injectivity of V
j
	​

 determine the other offset.

Every u∈U
i
	​

 is odd and divisible by 3. Every v∈V
j
	​

 satisfies

v≡2(mod3).

Therefore, in z=uv,

v
2
	​

(u)=0,v
3
	​

(u)=v
3
	​

(z).
(24)

Set

z
∘
:=
2
v
2
	​

(z)
3
v
3
	​

(z)
z
	​

.

Then

u⟼
3
v
3
	​

(z)
u
	​


injects the labelled product fiber into the divisors of z
∘
. This proves (1).

4. A uniform power bound for every fiber

For θ>0, define the finite constant

C
θ
	​

:=
p prime
p
θ
<2
	​

∏
	​

ν≥0
max
	​

(ν+1)p
−θν
.
(25)

For primes satisfying p
θ
≥2,

ν+1≤2
ν
≤p
θν
.

Consequently, for every positive integer n,

τ(n)≤C
θ
	​

n
θ
.
(26)

Since every product occurring here satisfies z<972Q
K
, equations (1) and (26) give

r
K
	​

(z)≤C
θ
	​

(972Q
K
)
θ
.
(27)

This estimate is uniform over all offsets and all cross-scale labels.

5. Exact exponential lower bound for N
K
	​


For a one-block word, apply six maps with multiset

{2,2,2,3,3,5}.

If the maps are applied in the order m
1
	​

,…,m
6
	​

, its offset is

d=
ℓ=1
∑
6
	​

(m
ℓ
	​

−2)
s=ℓ+1
∏
6
	​

m
s
	​

.
(28)

The 60=6!/(3!2!) permutations give the following 60 distinct offsets:

{
	​

23,25,31,38,40,43,46,49,50,58,61,62,68,70,73,76,79,80,83,86,
92,97,98,100,112,115,116,121,122,124,128,130,133,136,139,140,143,146,152,157,
158,160,163,166,172,184,193,194,196,200,220,223,224,229,230,232,241,242,244,248}.
	​

(29)

All lie in [0,Q−1].

Concatenating k such one-block maps gives offsets with base-Q expansion

d
1
	​

Q
k−1
+d
2
	​

Q
k−2
+⋯+d
k
	​

,d
ℓ
	​

∈D
1
	​

.
(30)

Uniqueness of base-Q expansion therefore gives

∣D
k
	​

∣≥60
k
.
(31)

All elements of H
k
	​

 are 0 or 2(mod3): in the original coordinate, the maps are h↦mh−1, and these two classes are preserved by m∈{2,3,5}. Hence the larger class satisfies

∣C
k
	​

∣≥
2
∣D
k
	​

∣
	​

≥
2
60
k
	​

.
(32)

It follows, with all labels retained, that

N
K
	​

	​

=
i∈I
K
	​

∑
	​

∣C
i
	​

∣∣C
K−i
	​

∣
≥
i∈I
K
	​

∑
	​

2
60
i
	​

2
60
K−i
	​

=
4
ι
K
	​

	​

60
K
.
	​

(33)

The endpoint count is exactly

ι
K
	​

=
⎩
⎨
⎧
	​

m+1,
m,
m+1,
	​

K=3m,
K=3m+1,
K=3m+2.
	​

(34)
6. Proof of exponential dispersion

Fix δ∈(0,1) and choose

θ
δ
	​

=
2logQ
δlog60
	​

.
(35)

Then

Q
θ
δ
	​

K
=60
δK/2
.

Put

A
δ
	​

=C
θ
δ
	​

	​

972
θ
δ
	​

.
(36)

Equation (27) becomes

r
K
	​

(z)≤A
δ
	​

60
δK/2
.
(37)

For any Z
K
	​

 with

∣Z
K
	​

∣≤60
(1−δ)K
,

we therefore have

z∈Z
K
	​

∑
	​

r
K
	​

(z)≤A
δ
	​

60
(1−δ/2)K
.
(38)

Dividing by (33) gives exactly

N
K
	​

1
	​

z∈Z
K
	​

∑
	​

r
K
	​

(z)≤
ι
K
	​

4A
δ
	​

	​

60
−δK/2
,

which proves (2).

7. No common-inner-block pumping

The polynomial argument also rules out the most direct type of infinite collision family.

Fix two distinct edge templates e,e
′
 of the same total scale and the same coefficient a. Let

R
ν
	​

(T)=Q
n
ν
	​

T+s
ν
	​


be any sequence of ray-word maps for which the values R
ν
	​

(8) are pairwise distinct. Compose R
ν
	​

 inside each of the four factor words of the two templates. The resulting two products are

P
e
	​

(R
ν
	​

(8)),P
e
′
	​

(R
ν
	​

(8)).
(39)

Since P
e
	​

−P
e
′
	​

 is a nonzero polynomial of degree at most one, equality

P
e
	​

(R
ν
	​

(8))=P
e
′
	​

(R
ν
	​

(8))

can hold for at most one ν.

Thus:

A fixed nontrivial collision template cannot be pumped indefinitely by a common inner ray block.
	​

(40)

This statement tracks the scale labels: composing an n
ν
	​

-block inside both factors changes

(i,K−i)⟼(i+n
ν
	​

,K−i+n
ν
	​

)

and the total scale from K to K+2n
ν
	​

.

Exact remaining gap

The theorem does not imply a fixed L. It excludes concentrated collision mechanisms, but it does not exclude the following dispersed possibility:

(1−o(1))N
K
	​


edges might be partitioned among exponentially many distinct products, each having multiplicity greater than L, while every individual fiber remains subexponential.

More precisely, if the proposed gate is false, then for every fixed L there is a sequence K
ν
	​

→∞ such that

N
K
ν
	​

	​

1
	​

z:r
K
ν
	​

	​

(z)≤L
∑
	​

r
K
ν
	​

	​

(z)⟶0.
(41)

The proved dispersion estimate forces, for every fixed δ>0,

∣{z:r
K
ν
	​

	​

(z)>L}∣>60
(1−δ)K
ν
	​

	​

(42)

for all sufficiently large ν.

Therefore an actual refutation cannot consist of one large fiber, finitely many collision morphisms, polynomially many collision families, or common-block pumping of fixed templates. It must produce exponentially many arithmetically distinct collisions at the special seed T=8.

What remains unproved is an anti-clustering theorem for that exponentially dispersed regime.
