I’ll focus only on the y=1 face and shrink it to an exact scriptable reduction, eliminating (x,u,v) via endpoint/capacity structure rather than derivative cones. The goal is a small active-face certificate whose only positive-dimensional survivor is the already-closed all-seven-tight manifold.

Thought for 13m 7s

Use this six-face reduction for the y=1 endpoint face. It is exact, avoids derivative cones, and gives a small scripted target.

Set

q=u+v,S=a+b+c+d+e+f,

so on y=1,

m=xq+v,N=S+1+x+q.

Also define

C
A
	​

:=50+
Z
75A
	​

,C
B
	​

:=50+
eY
75B
	​

.

Then

Φ=2N
2
+75S−C
A
	​

xq−C
B
	​

v.
(1)

Equivalently, after clearing denominators,

Π:=eYZΦ=eYZ(2N
2
+75S)−eY(50Z+75A)xq−Z(50eY+75B)v.
(2)

The key reduction is:

y=1, Φ<0⟹Φ<0 on one of the six faces
	​

s
4
	​

=0,s
5
	​

=0,s
6
	​

=0,s
7
	​

=0,(s
1
	​

=s
2
	​

=s
3
	​

=0),(u=1, s
2
	​

=s
3
	​

=0).
	​

(Y1-6)

So the next exact proof obligation is only these six faces.

Lemma 1: positive endpoint derivatives are impossible at a negative point

On y=1, define the cleared derivatives

R
x
	​

:=Z∂
x
	​

Φ=4ZN−q(50Z+75A),
(3)
R
q
	​

:=Z∂
q
	​

Φ=4ZN−x(50Z+75A).
(4)

Then the following exact statement holds:

K
y=1
	​

∧R
x
	​

≥0⟹Φ>0,
	​

(Dx)
K
y=1
	​

∧R
q
	​

≥0⟹Φ>0.
	​

(Dq)

Here K
y=1
	​

 means y=1, variables ≥1, and s
1
	​

,…,s
7
	​

≥0.

Proof of D
x
	​


Use

Π=eYxR
x
	​

+Z(eY(2N(N−2x)+75S)−(50eY+75B)v).
(5)

So if R
x
	​

≥0, it is enough to prove

L
x
	​

:=eY(2N(N−2x)+75S)−(50eY+75B)v>0.
(6)

Now write

T:=a+b+c+f,D:=d+e.

Since

B=Y+eT,

we have

C
B
	​

v=50v+75
e
v
	​

+75
Y
vT
	​

.

From feasibility,

v≤e,v≤Y,e≤D,

where v≤Y follows from

v≤xq+v=m≤Y.

Therefore

C
B
	​

v≤50D+75+75T.
(7)

Also

x≤b+c−1,q≥2,

so

N−2x=S+1+q−x≥a+d+e+f+q+2.

And since x≥1,

N=S+1+x+q≥T+D+q+2.

Thus

2N(N−2x)+75S−C
B
	​

v

is at least

2(T+D+q+2)(a+d+e+f+q+2)+75(T+D)−(50D+75+75T).

That equals

2(T+D+q+2)(a+d+e+f+q+2)+25D−75.

Since

T≥4,D≥2,q≥2,a+d+e+f+q+2≥8,

the lower bound is at least

2⋅10⋅8+50−75=135>0.

Hence L
x
	​

>0, so Π>0, hence Φ>0. This proves D
x
	​

.

Proof of D
q
	​


Similarly,

Π=eYqR
q
	​

+Z(eY(2N(N−2q)+75S)−(50eY+75B)v).
(8)

If R
q
	​

≥0, it is enough to prove

L
q
	​

:=eY(2N(N−2q)+75S)−(50eY+75B)v>0.
(9)

Again use

C
B
	​

v≤50D+75+75T.
(10)

Now q≤d+e=D by s
2
	​

≥0, and x≥1, so

N−2q=S+1+x−q=T+D+1+x−q≥T+2.

Also

N=S+1+x+q≥T+D+q+2.

Therefore

2N(N−2q)+75S−C
B
	​

v

is at least

2(T+D+q+2)(T+2)+75(T+D)−(50D+75+75T).

That is

2(T+D+q+2)(T+2)+25D−75.

With T≥4,D≥2,q≥2, this is at least

2⋅10⋅6+50−75=95>0.

So L
q
	​

>0, hence Π>0, hence Φ>0. This proves D
q
	​

.

Lemma 2: exact descent to six faces

Assume y=1, S7 feasibility, and Φ<0.

By Lemma 1,

R
x
	​

<0,R
q
	​

<0.
(11)
Step A: push x upward

Hold

a,b,c,d,e,f,q,v

fixed and increase x.

Only these constraints can become tight:

s
3
	​

=b+c−1−x,

or one of

s
4
	​

,s
5
	​

,s
6
	​

,s
7
	​

,

because m=xq+v increases linearly in x.

Since R
x
	​

<0, Φ strictly decreases until one of those blockers is hit. It cannot stop at R
x
	​

=0, because Lemma 1 would give Φ>0, contradicting monotone descent from a negative point.

Thus we reach a negative point with

s
3
	​

=0ors
j
	​

=0 for some j∈{4,5,6,7}.
(12)
Step B: push q=u+v upward

Hold

a,b,c,d,e,f,x,v

fixed and increase q, i.e. increase u=q−v.

Only these constraints can become tight:

s
2
	​

=d+e−q,

or one of

s
4
	​

,s
5
	​

,s
6
	​

,s
7
	​

,

because m=xq+v increases linearly in q.

Since R
q
	​

<0, Φ strictly decreases until one of those blockers is hit. Again it cannot stop at R
q
	​

=0, by Lemma 1.

Thus we reach a negative point with

s
2
	​

=0ors
j
	​

=0 for some j∈{4,5,6,7}.
(13)
Step C: push v upward at fixed q

Hold

a,b,c,d,e,f,x,q

fixed and increase v, so u=q−v decreases.

From (1),

∂
v
	​

Φ∣
q
	​

=−C
B
	​

=−(50+
eY
75B
	​

)<0.
(14)

So Φ strictly decreases while feasible.

Only these constraints can become tight:

u=1,
s
1
	​

=e−v=0,

or one of

s
4
	​

,s
5
	​

,s
6
	​

,s
7
	​

,

because m=xq+v increases linearly in v.

Thus we reach a negative point with

u=1ors
1
	​

=0ors
j
	​

=0 for some j∈{4,5,6,7}.
(15)

Combining (12), (13), and (15):

If any capacity slack s
4
	​

,s
5
	​

,s
6
	​

,s
7
	​

 becomes tight, we are on one of the four capacity faces.

If no capacity slack is tight, then the three endpoint blockers force

s
3
	​

=0,s
2
	​

=0,s
1
	​

=0

or

s
3
	​

=0,s
2
	​

=0,u=1.

Hence the six-face reduction Y1-6 follows.

Exact scripted target after the reduction

Clear denominators with

Π=eYZΦ.

Since eYZ>0, the y=1 face is proved once the following six systems are empty:

K
y=1
	​

,s
4
	​

=0,Π<0,
K
y=1
	​

,s
5
	​

=0,Π<0,
K
y=1
	​

,s
6
	​

=0,Π<0,
K
y=1
	​

,s
7
	​

=0,Π<0,
K
y=1
	​

,s
1
	​

=s
2
	​

=s
3
	​

=0,Π<0,
K
y=1
	​

,u=1, s
2
	​

=s
3
	​

=0,Π<0.

For an algebraic emptiness script, replace Π<0 by

−Πr
2
−1=0.

So the six exact gates are:

K
y=1
	​

∧F=0∧(−Πr
2
−1=0) has no real solution
	​


for

F∈{s
4
	​

,s
5
	​

,s
6
	​

,s
7
	​

},

plus

K
y=1
	​

∧s
1
	​

=s
2
	​

=s
3
	​

=0∧(−Πr
2
−1=0) has no real solution,
	​

K
y=1
	​

∧u=1, s
2
	​

=s
3
	​

=0∧(−Πr
2
−1=0) has no real solution.
	​


This is the smallest clean reduction I see: it turns the y=1 face into four single-capacity faces plus two endpoint-saturated faces, and the derivative exclusions are proved by the elementary inequalities above, not by coefficient cones.