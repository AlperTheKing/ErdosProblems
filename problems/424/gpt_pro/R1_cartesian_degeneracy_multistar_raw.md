# GPT-Pro 5.6: Cartesian degeneracy and multi-star replacement

## Prompt

We now focus on one precise lemma for the same set G.

Let G be the least subset of the positive integers containing 2,3 and satisfying xy-1 in G whenever x,y in G are distinct. Put
G0 = G intersect 3N,   G2 = G intersect {n : n = 2 mod 3}.
Then every a in G0 and b in G2 are automatically distinct, and ab-1 lies in G2.

For finite U,V define the multiplicative energy
E(U,V) = #{(u,v,u',v') in U x V x U x V : uv = u'v'}.
If all products are at most X and
E(U,V) <= C |U|^2 |V|^2 / X,
then Cauchy-Schwarz gives |UV| >= X/C and hence positive lower density for G.

Exact data for full dyadic windows U=G0 intersect (Y/2,Y], V=G2 intersect (Z/2,Z] up to 10^6 show E/(|U||V|) between 1.006 and 1.125; balanced kappa=E*YZ/(|U|^2|V|^2) decreases from about 239 to 105 over Y=Z=10^3 to 10^5. However Ford's multiplication-table theorem rules out a bounded kappa for generic balanced integer windows. Fixed finite affine subsystems, periodic cores, and generic polynomial-growth bootstraps have already been rigorously excluded.

Please give exactly one load-bearing mathematical result:

(A) prove a closure-specific, variable-scale reservoir theorem: explicit constants C,c>0 and a construction, for every sufficiently large X, of U_X subset G0 and V_X subset G2 with uv<=X, |U_X||V_X|>=cX, and E(U_X,V_X)<=C|U_X||V_X|; or

(B) prove a precise obstruction showing that this reservoir statement cannot follow from the presently known closure facts, and replace it by a strictly weaker concrete lemma that still implies |G intersect [1,X]|>=cX.

The construction may use scale-dependent multipliers from G, but it must preserve distinct inputs and must not assume positive density, random divisor independence, or an unproved stability statement. Check every quantifier and the Cauchy-Schwarz normalization. A proof, a rigorous counterexample to (A), or a corrected theorem with a complete mechanism is useful; a route survey is not.
Show more

## Response (raw browser text)

Theorem — Cartesian reservoirs are necessarily degenerate; the correct weaker object is a multi-star reservoir

Write

δ
∗
	​

:=Q(1/log2)=1−
log2
1+loglog2
	​

=0.086071…

and, for sufficiently large t,

Φ(t):=(logt)
δ
∗
	​

(loglogt)
3/2
.

There are absolute constants K
0
	​

,m
0
	​

>0 such that, uniformly for n≥m≥m
0
	​

,

	​

{ab:1≤a≤m, 1≤b≤n}
	​

≤K
0
	​

Φ(m)
mn
	​

.
(1)

Indeed, the generalized multiplication-table theorem identifies the rectangular table with a divisor-in-an-interval count, and the k=1 Ford estimate evaluates that count uniformly throughout m≤n. 
dms.umontreal.ca
+1

The following two conclusions hold.

1. Degeneracy of every Cartesian reservoir

For every c,C>0, there is a constant B=B(c,C) with the following property.

If X≥1 and nonempty finite sets U,V⊂N satisfy

uv≤X(u∈U, v∈V),
(2)
∣U∣∣V∣≥cX,
(3)

and

E(U,V)≤C∣U∣∣V∣,
(4)

then

min(maxU,maxV)≤B.
(5)

One may take, after enlarging K
0
	​

,m
0
	​

 in (1),

B(c,C)=max{m
0
	​

,⌈e
e
⌉,⌈exp((K
0
	​

C/c)
1/δ
∗
	​

)⌉}.
(6)

Consequently, if such U
X
	​

⊂G
0
	​

, V
X
	​

⊂G
2
	​

 exist for every sufficiently large X, then already

∣G∩[1,X]∣≥
B(c,C)
c
	​

X
(7)

for every sufficiently large X. In particular, an A-type reservoir cannot be a genuinely two-growing-scale mechanism: one of its sides must remain in a fixed finite interval, and then its cardinality condition alone already contains the desired positive-density conclusion.

2. Strictly weaker replacement: a multi-star reservoir

Suppose there are constants η>0 and L≥0 such that, for every sufficiently large X, one can find a finite set

D
X
	​

⊂G
0
	​


and, for every d∈D
X
	​

, a finite set

V
d,X
	​

⊂G
2
	​

∩[1,X/d]

satisfying

M
X
	​

:=
d∈D
X
	​

∑
	​

∣V
d,X
	​

∣≥ηX,
(8)

and

d,e∈D
X
	​

d

=e
	​

∑
	​

∣dV
d,X
	​

∩eV
e,X
	​

∣≤LM
X
	​

.
(9)

Then, for every sufficiently large X,

∣G
2
	​

∩[1,X]∣≥
1+L
η
	​

X.
(10)

Thus this non-Cartesian condition directly gives positive lower density, with the explicit constant η/(1+L).

Proof

Put

M=maxU,N=maxV,m=min(M,N),n=max(M,N),

and

P=∣U∣∣V∣.

Because the pair (M,N) itself belongs to U×V, condition (2) gives

MN≤X.

Hence (3) implies

P≥cX≥cMN=cmn.
(11)

Also

UV⊆{ab:1≤a≤m, 1≤b≤n}.

By Cauchy–Schwarz,

E(U,V)≥
∣UV∣
P
2
	​

.
(12)

If m≥m
0
	​

, equations (1), (11), and (12) give

P
E(U,V)
	​

≥
∣UV∣
P
	​

≥
K
0
	​

mn
PΦ(m)
	​

≥
K
0
	​

c
	​

Φ(m).
(13)

Comparing this with (4),

Φ(m)≤
c
K
0
	​

C
	​

.
(14)

For m≥e
e
,

Φ(m)=(logm)
δ
∗
	​

(loglogm)
3/2
≥(logm)
δ
∗
	​

.

Thus (14) gives

m≤exp((K
0
	​

C/c)
1/δ
∗
	​

).

Together with the case m<m
0
	​

, this proves (5) and (6).

Now assume U⊂G
0
	​

, V⊂G
2
	​

. If M≤B, then

∣V∣≥
∣U∣
cX
	​

≥
B
cX
	​

.

Moreover V⊂[1,X], since N≤X/M≤X. Therefore

∣G∩[1,X]∣≥∣V∣≥
B
cX
	​

.

If N≤B, the identical argument with U and V interchanged gives the same conclusion. This proves (7). Notice that the closure operation was not used here: once Ford forces one side to be bounded, membership of U,V in G already proves density.

For the multi-star statement, define, for n≤X,

r
X
	​

(n):=#{d∈D
X
	​

:n∈dV
d,X
	​

}.

Every pair (d,b), with b∈V
d,X
	​

, contributes once, so

n≤X
∑
	​

r
X
	​

(n)=M
X
	​

.
(15)

Moreover,

n≤X
∑
	​

r
X
	​

(n)
2
	​

=
d,e∈D
X
	​

∑
	​

∣dV
d,X
	​

∩eV
e,X
	​

∣
=
d∈D
X
	​

∑
	​

∣V
d,X
	​

∣+
d,e∈D
X
	​

d

=e
	​

∑
	​

∣dV
d,X
	​

∩eV
e,X
	​

∣
≤(1+L)M
X
	​

.
	​

(16)

Let

P
X
	​

:={n≤X:r
X
	​

(n)>0}.

Cauchy–Schwarz with the correct normalization gives

M
X
2
	​

=(
n∈P
X
	​

∑
	​

r
X
	​

(n))
2
≤∣P
X
	​

∣
n≤X
∑
	​

r
X
	​

(n)
2
≤∣P
X
	​

∣(1+L)M
X
	​

.

Therefore

∣P
X
	​

∣≥
1+L
M
X
	​

	​

≥
1+L
η
	​

X.
(17)

For every n∈P
X
	​

, there are d∈G
0
	​

 and b∈G
2
	​

 with n=db. Since

d≡0(mod3),b≡2(mod3),

we have d

=b automatically. Hence the defining closure rule applies with distinct inputs and gives

n−1=db−1∈G
2
	​

.

The map n↦n−1 is injective and n−1<X, so (17) proves (10).

Finally, the replacement is genuinely weaker than the Cartesian condition. Given an A-type reservoir, set

D
X
	​

=U
X
	​

,V
d,X
	​

=V
X
	​

(d∈U
X
	​

).

Then M
X
	​

=∣U
X
	​

∣∣V
X
	​

∣, and

d

=e
∑
	​

∣dV
X
	​

∩eV
X
	​

∣=E(U
X
	​

,V
X
	​

)−∣U
X
	​

∣∣V
X
	​

∣≤(C−1)M
X
	​

.

Thus A is the special case η=c, L=C−1.

The converse fails even as a residue-compatible combinatorial assertion. To see this, let

T=⌊X/3⌋,Y=(logT)
1/3
.

All but o(T) integers m≤T possess a factorization

m=ab,a,b≥Y.

Indeed, the number without such a factorization is at most

Y
3
+
r<Y
∑
	​

π(T/r)≪Y
3
+
log(T/Y)
T(1+logY)
	​

=o(T).
(18)

For (18), if m≥Y
3
 and its largest prime factor p≥Y, failure forces m=rp with r<Y; if p<Y, multiplying prime factors until the product first exceeds Y gives a divisor between Y and Y
2
, whose complementary divisor exceeds Y.

Restrict to m≡2(mod3). There are

3
T
	​

−o(T)=
9
X
	​

−o(X)

such m with a factorization m=ab, a,b≥Y. Since m≡2(mod3), exactly one factor is 2(mod3); call that factor b, and call the other a. Select one such factorization for every m, and take the edges

(3a,b).

Their products 3m are pairwise distinct, all are at most X, and the two coordinates lie respectively in 3N and 2mod3. Thus the multi-star conditions hold with L=0 and, eventually, η=1/10, while every coordinate is at least Y→∞. By the first part, no fixed-c,C Cartesian reservoir can be supported on these vertices. This witness is only to establish strictness of the corrected combinatorial hypothesis; it is not asserted that these vertices belong to G.

This proves option (B): bounded-energy Cartesian reservoirs of linear mass are necessarily bounded-side and hence circular, whereas the multi-star overlap lemma is a strictly weaker, correctly normalized condition that preserves x

=y and still yields an explicit positive lower density.
