I’ll focus on one executable sibling-row lemma: reduce the representative active5 inequality to finite qmax-face/KKT certificates, with explicit rational stationarity and a per-face algebraic remainder check.

Thought for 21m 3s

Use this as the next atom:

Sibling-fork seven-cut lemma

For the representative sibling row

Q=(1,6,8,4,9)

in the seed I?
F
ˋ
Ao]]? with side 0001111000, relabel the variables as

(a,b,c,d,e,f,x,y,u,v)=(w
0
	​

,w
3
	​

,w
4
	​

,w
5
	​

,w
6
	​

,w
8
	​

,w
1
	​

,w
2
	​

,w
7
	​

,w
9
	​

).

So the three bad products are

m=xu+xv+yv,N=a+b+c+d+e+f+x+y+u+v.

Define

Y=ac+bf+cf,
Z=eY+df(b+c)=ace+bef+cef+bdf+cdf,
A=bd+cd+df+ac+ae+bf+be+cf+ce+ef,
B=ac+ae+bf+be+cf+ce+ef.

Then for this row,

I(Q)−N=
Z
x(u+v)A
	​

+
eY
yvB
	​

−(a+b+c+d+e+f).

This is just the exact path-enumeration identity: the two bad edges (1,7),(1,9) share denominator Z, and the bad edge (2,9) has denominator eY=w
6
	​

(w
0
	​

w
4
	​

+w
3
	​

w
8
	​

+w
4
	​

w
8
	​

), matching your observed denominator.

Now prove the following standalone algebraic lemma.

Assume all variables are ≥1 and the following seven qmax-derived slacks are nonnegative:

s
1
	​

s
2
	​

s
3
	​

s
4
	​

s
5
	​

s
6
	​

s
7
	​

	​

=e−v≥0,
=d+e−u−v≥0,
=b+c−x−y≥0,
=ac+bf+cf−m≥0,
=ae+bf+cf−m≥0,
=ac+df+ef−m≥0,
=ae+df+ef−m≥0.
	​


Then

2(N
2
−25m)−75(
Z
x(u+v)A
	​

+
eY
yvB
	​

−(a+b+c+d+e+f))≥0.
	​

(S7)

Equivalently,

I(Q)−N≤
75
2
	​

(N
2
−25m)=
3
2
	​

(
25
N
2
	​

−m).

This lemma is stronger than the active-all-five row statement for this row, because it does not use the active-five inequalities.

Why these seven cuts are legitimate qmax slacks

In original w-variables:

s
1
	​

=e−v=w
6
	​

−w
9
	​


is the singleton cut slack for {2}, divided by w
2
	​

.

s
2
	​

=d+e−u−v=w
5
	​

+w
6
	​

−w
7
	​

−w
9
	​


is the singleton cut slack for {1}, divided by w
1
	​

.

s
3
	​

=b+c−x−y=w
3
	​

+w
4
	​

−w
1
	​

−w
2
	​


is the singleton cut slack for {9}, divided by w
9
	​

.

The four quadratic slacks are the qmax slacks of the following completed switch cuts:

s
4
	​

=ac+bf+cf−m=w
0
	​

w
4
	​

+w
3
	​

w
8
	​

+w
4
	​

w
8
	​

−m,
s
5
	​

=ae+bf+cf−m=w
0
	​

w
6
	​

+w
3
	​

w
8
	​

+w
4
	​

w
8
	​

−m,
s
6
	​

=ac+df+ef−m=w
0
	​

w
4
	​

+w
5
	​

w
8
	​

+w
6
	​

w
8
	​

−m,
s
7
	​

=ae+df+ef−m=w
0
	​

w
6
	​

+w
5
	​

w
8
	​

+w
6
	​

w
8
	​

−m.

So full qmax immediately implies the S7 feasible region. No coefficient cone over all 448 cuts is involved.

KKT face certificate to prove S7

Let

Φ=2(N
2
−25m)−75(
Z
x(u+v)A
	​

+
eY
yvB
	​

−(a+b+c+d+e+f)).

Let

D=eYZ>0,P=DΦ.

The exact KKT gate is:

For every active set

A⊆{a−1,b−1,c−1,d−1,e−1,f−1,x−1,y−1,u−1,v−1,s
1
	​

,…,s
7
	​

},

rank-pruned to at most 10 active gradients, test infeasibility of the semialgebraic system

g=0(g∈A),
g>0(g∈
/
A),
Φ<0,

and the rational KKT stationarity equations

D∂
i
	​

P−P∂
i
	​

D=D
2
g∈A
∑
	​

λ
g
	​

∂
i
	​

g(i=1,…,10),

with

λ
g
	​

≥0.

This is a finite exact gate over 17 inequalities, not over 448 qmax slacks.

The one nontrivial positive KKT face that should survive rank pruning is the seven-tight sibling fork face

s
1
	​

=s
2
	​

=s
3
	​

=s
4
	​

=s
5
	​

=s
6
	​

=s
7
	​

=0,

with lower-bound actives

b=d=f=u=y=1.

Solving those equations gives the one-parameter curve

b=d=f=u=y=1,
c=e=x=v=t,
a=t+1−
t
1
	​

,t≥1.

On this curve,

Φ(t)=
t
2
(t+2)(t
3
+2t
2
+t+1)
20t
7
−18t
6
−166t
5
+76t
4
+459t
3
+117t
2
−117t+4
	​

.

The denominator is positive for t≥1. The numerator

P
0
	​

(t)=20t
7
−18t
6
−166t
5
+76t
4
+459t
3
+117t
2
−117t+4

has

P
0
	​

(1)=375>0

and the exact Sturm gate to run is

SturmRoots(P
0
	​

,[1,∞))=0.

So this whole central face is positive.

The concrete gate

The next exact-testable proof atom is therefore:

S7 holds for all a,b,c,d,e,f,x,y,u,v≥1 satisfying s
1
	​

,…,s
7
	​

≥0.
	​


If S7 passes, the representative sibling worst row is closed immediately, because full qmax gives the seven slacks. Then the remaining sibling rows can be handled by the same row-enumeration template: derive their Y,Z,A,B identity, select the corresponding seven qmax slacks, and run the same KKT-face gate.

We need one concrete proof step for Erdős #23, not a survey. Current exact atom is the S7 sibling seed inequality.

Variables a,b,c,d,e,f,x,y,u,v >= 1. Define
m = x*u + x*v + y*v,
N = a+b+c+d+e+f+x+y+u+v,
Y = a*c + b*f + c*f,
Z = e*Y + d*f*(b+c),
A = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f,
B = a*c + a*e + b*f + b*e + c*f + c*e + e*f,
IminusN = x*(u+v)*A/Z + y*v*B/(e*Y) - (a+b+c+d+e+f).

S7 slacks:
s1=e-v >=0,
s2=d+e-u-v >=0,
s3=b+c-x-y >=0,
s4=Y-m >=0,
s5=a*e+b*f+c*f-m >=0,
s6=a*c+d*f+e*f-m >=0,
s7=a*e+d*f+e*f-m >=0.

Prove
Phi := 2*(N^2-25*m) - 75*IminusN >= 0.

Exact evidence: identity is verified. Integer grid [1,8]^10 checked 1,073,741,824 points, 195,658,681 feasible, no negative; best integer point all-ones with Phi=25. SLSQP multistart finds the continuous minimum near the all-seven-slack tight face:
b=d=f=u=y=1, c=e=x=v=t, a=t+1-1/t, t>=1,
where
Phi(t)=P0(t)/(t^2(t+2)(t^3+2t^2+t+1)),
P0=20t^7-18t^6-166t^5+76t^4+459t^3+117t^2-117t+4,
and exact Sturm shows P0 has no root on [1,infty), P0(1)=375.

Need the missing proof that no other feasible face can give Phi<0. Please give one concrete exact route: either (1) a monotonic reduction to the central face, with explicit variable moves preserving S7 and not increasing Phi, or (2) a finite KKT/active-face certificate small enough to implement exactly, specifying the active sets/equations and the positivity certificate to check. Avoid proposing numerical optimization or unsupported Hall/switch lemmas. If you think S7 is false, give a parametric or rational counterexample pattern.
Show more

I’ll give a finite exact certificate rather than another inequality guess: reduce to rank-minimal KKT systems, then discharge faces via multiplier signs and Sturm checks.

I’ll make the certificate smaller by exploiting the special x,y,u,v dependence: eliminate bad-edge variables first, then enumerate only S7/lower-bound faces.

Thought for 18m 18s

Use a compactified Fritz–John face certificate. It is cleaner than unbounded KKT on Φ, because it handles “other faces” and escape-to-infinity in one finite algebraic check.

Concrete next lemma: compact S7-FJ exclusion

Normalize by the old total N. Introduce normalized variables

a,b,c,d,e,f,x,y,u,v,θ

with

a+b+c+d+e+f+x+y+u+v=1,θ=
N
old
	​

1
	​

.

The old lower bounds w
i
	​

≥1 become

a,b,c,d,e,f,x,y,u,v≥θ,θ≥0.

Use the same homogeneous formulas

m=xu+xv+yv,
Y=ac+bf+cf,
Z=eY+df(b+c),
A=bd+cd+df+ac+ae+bf+be+cf+ce+ef,
B=ac+ae+bf+be+cf+ce+ef.

Define the compact polynomial

P=2eYZ(1−25m)−75θ(eYx(u+v)A+ZyvB−eYZ(a+b+c+d+e+f)).
	​


For every finite feasible point, i.e. θ>0,

P=eYZθ
2
Φ.

Since eYZ>0, proving P≥0 on the compact normalized feasible set proves S7.

The compact feasible set K is:

H:=a+b+c+d+e+f+x+y+u+v−1=0,
g
θ
	​

:=θ≥0,
g
a
	​

:=a−θ≥0,…,g
v
	​

:=v−θ≥0,

and the seven S7 slacks

g
1
	​

=e−v≥0,
g
2
	​

=d+e−u−v≥0,
g
3
	​

=b+c−x−y≥0,
g
4
	​

=Y−m≥0,
g
5
	​

=ae+bf+cf−m≥0,
g
6
	​

=ac+df+ef−m≥0,
g
7
	​

=ae+df+ef−m≥0.

So there are 18 inequality constraints:

G={g
θ
	​

,g
a
	​

,g
b
	​

,g
c
	​

,g
d
	​

,g
e
	​

,g
f
	​

,g
x
	​

,g
y
	​

,g
u
	​

,g
v
	​

,g
1
	​

,…,g
7
	​

}.
Exact face system to check

For every active set

A⊆G,∣A∣≤11,

check infeasibility over the reals of the following semialgebraic system:

H=0,
g=0(g∈A),
g≥0(g∈G),
P<0,

and the Fritz–John stationarity equations

λ
0
	​

∇P−
g∈A
∑
	​

λ
g
	​

∇g+μ∇H=0,
	​


with

λ
0
	​

≥0,λ
g
	​

≥0,

and normalization

λ
0
	​

+
g∈A
∑
	​

λ
g
	​

=1.
	​


The multiplier μ is free.

The active-set cutoff ∣A∣≤11 is enough by conic Carathéodory on the 10-dimensional tangent space H=0. Regular KKT points need at most 10 active inequalities; the extra one covers abnormal Fritz–John faces with λ
0
	​

=0.

For a purely algebraic implementation, encode the strict negativity by one auxiliary variable r:

−Pr
2
−1=0.

Then sign conditions are only

g≥0,λ
0
	​

≥0,λ
g
	​

≥0.

This gives a finite exact certificate:

∀A⊆G, ∣A∣≤11,RealSol(FJ
A
	​

∧K∧P<0)=∅.
	​

(FJ-S7)

If FJ-S7 passes, S7 is proved.

Central component to peel off first

The known central face becomes, in normalized variables,

b=d=f=y=u=θ,
c=e=x=v,
ac−c
2
−θc+θ
2
=0,
H=0.

Equivalently, with

t=
θ
c
	​

≥1,

the old variables are

b=d=f=u=y=1,c=e=x=v=t,a=t+1−
t
1
	​

.

On this component,

Φ(t)=
t
2
(t+2)(t
3
+2t
2
+t+1)
P
0
	​

(t)
	​

,

where

P
0
	​

(t)=20t
7
−18t
6
−166t
5
+76t
4
+459t
3
+117t
2
−117t+4.

The exact central-face certificate is:

P
0
	​

(1)=375>0,
SturmRoots(P
0
	​

,[1,∞))=0.

So the only positive-dimensional face already seen numerically is harmless.

Why this closes “no other face”

Assume S7 is false. Then some old feasible point has Φ<0. Normalize it. Since K is compact and P=eYZθ
2
Φ, the compact problem has a point with P<0. Hence P attains a negative minimum on K.

At that minimum, Fritz–John applies. After quotienting by the equality H=0, conic Carathéodory gives a Fritz–John certificate using at most 11 active inequalities. Therefore the point appears in one of the finitely many systems FJ
A
	​

 above.

Thus the exact proof obligation is only:

FJ
A
	​

∧K∧P<0is empty for every ∣A∣≤11,

plus the central Sturm check.

This is the concrete face-exclusion gate. It avoids coefficient cones entirely, does not assume monotonicity, and includes singular/abnormal faces and projective escape at θ=0.