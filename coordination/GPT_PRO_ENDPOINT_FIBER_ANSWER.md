Use this endpoint-fiber reduction. It is exact, small, and removes the need to enumerate all FJ active sets.

Endpoint-fiber lemma

Work in the compact normalization

a+b+c+d+e+f+x+y+u+v=1,z
i
	​

≥θ,θ≥0.

Let

P=2eYZ(1−25m)−75θ(eYx(u+v)A+ZyvB−eYZ(a+b+c+d+e+f)).

Assume the θ=0 boundary is already closed.

Define

p=x+y,q=u+v,

and the four capacity polynomials

M
4
	​

=Y=ac+bf+cf,
M
5
	​

=ae+bf+cf,
M
6
	​

=ac+df+ef,
M
7
	​

=ae+df+ef.

Then the four product constraints are equivalent, on a fixed (a,b,c,d,e,f,p,q)-fiber, to

m=pq−yu≤M
∗
	​

,M
∗
	​

=min(M
4
	​

,M
5
	​

,M
6
	​

,M
7
	​

),

or

yu≥R:=pq−M
∗
	​

.

The linear endpoint constraints become

θ≤y≤p−θ,
θ≤u≤q−θ,
v=q−u≤e⟺u≥q−e.

So the fiber in (y,u) is

θ≤y≤p−θ,
L≤u≤U,L=max(θ,q−e),U=q−θ,
yu≥R.

Now set

α=
Z
A
	​

,β=
eY
B
	​

,S=a+b+c+d+e+f.

Since

m=pq−yu,yv=y(q−u),x(u+v)=xq=(p−y)q,

we get

eYZ
P
	​

=2(1−25m)−75θ(αxq+βyv−S).

Substituting x=p−y, v=q−u, and m=pq−yu, this becomes

eYZ
P
	​

=C+Kyu−Hy,

where

C=2−50pq−75θαpq+75θS,
K=50+75θβ>0,
H=75θ(β−α)q.

For fixed y, the expression is strictly increasing in u, because

∂
u
	​

(P/(eYZ))=Ky>0.

Therefore the fiber minimum uses

u(y)=max(L,
y
R
	​

).

The feasible y-interval is

J=[θ,p−θ]∩[
U
R
	​

,∞].

On the part where u(y)=R/y,

eYZ
P
	​

=C+KR−Hy,

which is linear in y. On the part where u(y)=L,

eYZ
P
	​

=C+(KL−H)y,

also linear in y. Hence the fiber minimum occurs at an endpoint of J, or at the single kink

L=
y
R
	​

.

Therefore every negative compact minimum can be moved, without increasing P, onto one of the following fourteen exact faces:

y=θ
	​


or

x=θ
	​


or, for some j∈{4,5,6,7},

s
j
	​

=0, u=θ
	​


or

s
j
	​

=0, v=θ
	​


or

s
j
	​

=0, v=e
	​

.

Here s
j
	​

=0 means m=M
j
	​

. The face v=e is s
1
	​

=0.

So the exact reduction is:

P<0⟹P<0 on one of these fourteen faces.
	​

(EF)
Resulting finite certificate

Let

H
0
	​

=a+b+c+d+e+f+x+y+u+v−1.

Let the compact feasible system be

H
0
	​

=0,
a−θ, b−θ, c−θ, d−θ, e−θ, f−θ, x−θ, y−θ, u−θ, v−θ, θ≥0,
s
1
	​

,…,s
7
	​

≥0.

Encode strict negativity by one auxiliary variable r:

−Pr
2
−1=0.

Then S7 for θ>0 is reduced to the following fourteen emptiness checks:

Two one-equation endpoint faces
H
0
	​

=0,K,y−θ=0,−Pr
2
−1=0

has no real solution.

H
0
	​

=0,K,x−θ=0,−Pr
2
−1=0

has no real solution.

Here K denotes all compact inequalities above.

Twelve two-equation capacity-endpoint faces

For every j∈{4,5,6,7}, check emptiness of

H
0
	​

=0,K,s
j
	​

=0,u−θ=0,−Pr
2
−1=0,
H
0
	​

=0,K,s
j
	​

=0,v−θ=0,−Pr
2
−1=0,
H
0
	​

=0,K,s
j
	​

=0,e−v=0,−Pr
2
−1=0.

That is only

2+3⋅4=14

exact real-algebraic gates.

Why this is enough

If S7 fails at θ>0, compactness plus the already-closed θ=0 boundary gives a negative compact minimum. Freeze

(a,b,c,d,e,f,p=x+y,q=u+v,θ).

The endpoint-fiber lemma moves the point inside that same fiber to one of the fourteen faces above, preserving all S7 constraints and not increasing P. Thus a negative point must exist on one of those fourteen faces.

Therefore proving the fourteen systems empty proves the full θ>0 S7 inequality, without enumerating the 230,964 raw FJ active systems.