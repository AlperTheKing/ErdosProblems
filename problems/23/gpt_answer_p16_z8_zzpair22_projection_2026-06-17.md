For the dirty endpoint pair (2,2), the smallest safe move is not another rooted cut batch. Split off the zero skeleton and run a dirty-aware zero-skeleton projection cap. For the first footprint

F={8,9,10,11},

this gives a finite P-free certificate:

M≤66
	​


for every zero skeleton in this footprint, hence contradiction to M=74.

I would treat this as a FINITE-CERTIFICATE-NEEDED result until your C++/CP-SAT audit emits the per-orbit certificate. The lemmas below are proved; the M≤66 number is the finite projection certificate target.

1. PROVED: dirty endpoint separation

Dirty endpoints are fixed as

z
0
	​

:{8,9},z
1
	​

:{10,11},

with z
0
	​

z
1
	​

∈E(R).

By triangle-freeness:

N
D
	​

(z
0
	​

)∩N
D
	​

(z
1
	​

)=∅,

already true here, and no A/B vertex can see both dirty endpoints:

n
z
0
	​

,v
	​

+n
z
1
	​

,v
	​

≤1(v∈A∪B).
	​


Also, since both dirty endpoints are tight and γ(z
0
	​

)=γ(z
1
	​

)=1,

m
z
0
	​

	​

+γ(z
0
	​

)=6,m
z
1
	​

	​

+γ(z
1
	​

)=6,

so

m
z
0
	​

	​

=m
z
1
	​

	​

=5.
	​

CP-SAT encoding
sum_v n[z0,v] = 5
sum_v n[z1,v] = 5

for v in AUB:
    n[z0,v] + n[z1,v] <= 1

This partitions the 12 A/B vertices into:

S0 = neighbours of z0, size 5
S1 = neighbours of z1, size 5
O  = the remaining A/B vertices, size 2

You do not need to branch on this partition; it is already encoded by the n[z,v] variables.

2. PROVED: dirty-corrected zero–D visibility for the endpoints

For z
0
	​

={8,9}:

D
10
	​

 and D
11
	​

 already have one common neighbour with z
0
	​

, namely z
1
	​

;

D
12
	​

 and D
13
	​

 have no dirty correction.

Therefore:

v
∑
	​

n
z
0
	​

,v
	​

y
v,10
	​

≥1,
v
∑
	​

n
z
0
	​

,v
	​

y
v,11
	​

≥1,
v
∑
	​

n
z
0
	​

,v
	​

y
v,12
	​

≥2,
v
∑
	​

n
z
0
	​

,v
	​

y
v,13
	​

≥2.

Symmetrically, for z
1
	​

={10,11}:

v
∑
	​

n
z
1
	​

,v
	​

y
v,8
	​

≥1,
v
∑
	​

n
z
1
	​

,v
	​

y
v,9
	​

≥1,
v
∑
	​

n
z
1
	​

,v
	​

y
v,12
	​

≥2,
v
∑
	​

n
z
1
	​

,v
	​

y
v,13
	​

≥2.
CP-SAT encoding

Use product literals:

com[z,d,v] = n[z,v] AND y[v,d]

Then add:

sum_v com[z0,10,v] >= 1
sum_v com[z0,11,v] >= 1
sum_v com[z0,12,v] >= 2
sum_v com[z0,13,v] >= 2

sum_v com[z1,8,v]  >= 1
sum_v com[z1,9,v]  >= 1
sum_v com[z1,12,v] >= 2
sum_v com[z1,13,v] >= 2

These are just the local nonedge-codegree constraints with the dirty ZZ-correction made explicit. They are safe for the size-5 and size-6 footprints too.

3. PROVED: exact finite projection relaxation for a fixed zero skeleton

Fix a zero skeleton Z, meaning all eight zero D-rows are fixed and z
0
	​

z
1
	​

 is the unique ZZ-edge.

For footprint F={8,9,10,11}, the skeleton has:

z
0
	​

={8,9},z
1
	​

={10,11},

two additional clean tight rows P
2
	​

,P
3
	​

⊆F, and four degree-3 rows H
1
	​

,…,H
4
	​

.

For each A/B vertex, keep only its P-free projection:

S=N
D
	​

(v)⊆D,
U=N
Z
	​

(v)⊆Z.

Introduce integer variables:

N
S,U
	​

∈{0,…,12}.

Here N
S,U
	​

 is the number of A/B vertices with D-state S and zero-neighbour set U.

Allowed types must satisfy:

S

=∅,
z∈U⇒S∩N
D
	​

(z)=∅,
{z
0
	​

,z
1
	​

}⊈U.

The first condition is A/B root-D visibility. The second is triangle-freeness through a zero–D edge. The third is triangle-freeness through the dirty ZZ-edge.

Projection constraints

A/B vertex count:

sum_{S,U} N[S,U] = 12

Touched D-column counts for d∈F={8,9,10,11}:

sum_{S,U: d in S} N[S,U] = 6 - c[d]

Untouched D-column bounds for d∈{12,13}:

sum_{S,U: d in S} N[S,U] >= 6 - c[d]
sum_{S,U: d in S} N[S,U] <= 8

Dirty tight zero degrees:

sum_{S,U: z0 in U} N[S,U] = 5
sum_{S,U: z1 in U} N[S,U] = 5

Clean tight zero degrees:

for z in clean_tight_zeros:
    sum_{S,U: z in U} N[S,U] = 6

Degree-3 zero bounds:

for h in degree3_zeros:
    sum_{S,U: h in U} N[S,U] >= 5
    sum_{S,U: h in U} N[S,U] <= 8

Zero-zero nonedge codegrees: for every unordered zero pair {z,u}

={z
0
	​

,z
1
	​

},

req = 2 - |N_D(z) intersect N_D(u)|

if req > 0:
    sum_{S,U: z in U and u in U} N[S,U] >= req

Do not impose a nonedge-codegree constraint on the dirty adjacent pair {z
0
	​

,z
1
	​

}. The allowed-type rule already forbids an A/B vertex from seeing both.

Zero–D nonedge visibility with dirty correction:

for z in Z:
    for d in D \ N_D(z):
        dirty_corr = 0
        if z == z0 and d in N_D(z1): dirty_corr = 1
        if z == z1 and d in N_D(z0): dirty_corr = 1

        sum_{S,U: z in U and d in S} N[S,U] >= 2 - dirty_corr

Total-pair reroot cap: for every D-pair e={a,b} used by a tight zero, define

K
e
	​

=∣{z∈Z:e⊆N
D
	​

(z)}∣,
Q
e
	​

=
S,U:e⊆S
∑
	​

N
S,U
	​

.

Let

singleZ(e)=1

if some zero row contains exactly one endpoint of e.

Then add:

K[e] + Q[e] in {1,2,3,4,6}

and if singleZ(e):

K[e] + Q[e] <= 4

In CP-SAT, encode this directly as a domain on Q[e]:

allowed_q = [
    q for q in range(13)
    if K[e] + q in {1,2,3,4,6}
    and (not singleZ[e] or K[e] + q <= 4)
]

AddLinearExpressionInDomain(Q[e], Domain.FromValues(allowed_q))

Projection objective:

Mproj = sum_{S,U} (|S| + |U|) * N[S,U]

Every real solution maps to one feasible projection with

M=M
proj
	​

.

Therefore, if the projection has maximum at most U
Z
	​

, then the real branch satisfies:

M≤U
Z
	​

.

This is a relaxation: it ignores the A/B template, A/B internal edges, and the exact p=16 state law. So any contradiction from it is P-free and safe.

4. FINITE-CERTIFICATE-NEEDED: footprint {8,9,10,11} closes by M≤66

For the footprint

F={8,9,10,11},

the zero skeleton enumeration is:

z0 = {8,9}
z1 = {10,11}

z2,z3 = unordered clean degree-2 rows inside F

h1,h2,h3,h4 = unordered degree-3 rows in D

constraints:
    c_d <= 4 for d in F

Canonicalize under the group generated by:

8 <-> 9
10 <-> 11
(8,9) <-> (10,11) with z0 <-> z1
12 <-> 13

This leaves 1085 zero-skeleton orbits for F={8,9,10,11}.

The finite certificate to emit is:

for each canonical zero skeleton orbit:
    build the projection IP above
    either prove infeasible
    or maximize Mproj and record U_skeleton <= 66

Then the whole footprint has:

M≤66
	​


which contradicts:

M=74.

So the first footprint is closed by a finite P-free projection certificate, not by fixed A/B-template enumeration.

How to encode this in the main verifier

Once the certificate is audited, add the guarded cut:

if profile_4400
and dirty_rows_are_{8,9}_{10,11}
and touched_footprint == {8,9,10,11}:
    M <= 66

Since the row has:

M = 74

this closes the branch immediately.

5. Why I do not claim a hand-only skeleton contradiction

There are zero skeletons in this footprint that satisfy the static row constraints, touched-column bounds, dirty disjointness, and pair caps. For example:

z0 = {8,9}
z1 = {10,11}

clean tight:
    {8,9}
    {8,9}

degree-3:
    {8,9,12}
    {10,11,12}
    {10,11,12}
    {10,11,12}

This has touched footprint {8,9,10,11} and touched column loads

c
8
	​

=c
9
	​

=c
10
	​

=c
11
	​

=4.

It is not killed by zero-row data alone. What kills it is the A/B-to-R projection capacity: even after relaxing away the A/B template, M cannot reach 74.

So I would not spend time looking for a pure skeleton contradiction here. The obstruction is genuinely an A/B-projection capacity obstruction.

6. Reusable cuts for the size-5 and size-6 footprints

The same projection certificate works for:

F={8,9,10,11,12},
F={8,9,10,11,13},

and

F={8,9,10,11,12,13}.

By 12↔13, only one size-5 footprint needs to be generated.

For a size-5 footprint, say

F={8,9,10,11,12},

use exact touched-column counts for 8,9,10,11,12:

for d in [8,9,10,11,12]:
    sum_{S,U: d in S} N[S,U] = 6 - c[d]

and only lower/upper bounds for the untouched column 13:

sum_{S,U: 13 in S} N[S,U] >= 6 - c[13]
sum_{S,U: 13 in S} N[S,U] <= 8

For size 6, all columns are touched, so all six D-column counts are exact:

for d in [8,9,10,11,12,13]:
    sum_{S,U: d in S} N[S,U] = 6 - c[d]

The dirty corrections are unchanged:

z0={8,9}, z1={10,11}

dirty correction for z0 only on d=10,11
dirty correction for z1 only on d=8,9
no dirty correction on 12,13

The same total-pair cap remains valid for every tight pair, including clean tight pairs that use 12 or 13.

7. Direct live-verifier cuts worth adding before the projection guard

These are local and reusable. They may help the broad CP-SAT even without the projection certificate.

Dirty endpoint partition
sum_v n[z0,v] = 5
sum_v n[z1,v] = 5

for v in AUB:
    n[z0,v] + n[z1,v] <= 1
Endpoint-specific dirty zero–D visibility
sum_v (n[z0,v] AND y[v,10]) >= 1
sum_v (n[z0,v] AND y[v,11]) >= 1
sum_v (n[z0,v] AND y[v,12]) >= 2
sum_v (n[z0,v] AND y[v,13]) >= 2

sum_v (n[z1,v] AND y[v,8])  >= 1
sum_v (n[z1,v] AND y[v,9])  >= 1
sum_v (n[z1,v] AND y[v,12]) >= 2
sum_v (n[z1,v] AND y[v,13]) >= 2
Dirty endpoint triangle domains
for v in AUB:
    n[z0,v] + y[v,8] <= 1
    n[z0,v] + y[v,9] <= 1

    n[z1,v] + y[v,10] <= 1
    n[z1,v] + y[v,11] <= 1

These are logically implied by triangle-freeness, but explicit forms usually propagate better.

8. First concrete C++/CP-SAT experiment to run

Run a standalone certificate generator, not the full verifier:

--profile 4400
--dirty-endpoint-rows 8,9 10,11
--touched-footprint 8,9,10,11
--projection-cert
--target-M 74
--canonicalize-zero-skeletons

For each canonical zero skeleton orbit:

Build the projection variables N
S,U
	​

.

Add the constraints listed above.

Add:

Mproj >= 74

Prove UNSAT.

If you also maximize for logging, record:

max Mproj <= 66

for every orbit.

Expected certificate shape:

footprint {8,9,10,11}
canonical zero-skeleton orbits: 1085
for every orbit: projection with Mproj >= 74 is UNSAT
aggregate certified cut: M <= 66

After that passes, add the single guarded cut to the main verifier and move to the size-5 representative footprint.

Weakest assumptions used

The local lemmas use only:

triangle-freeness;

the unique dirty edge z
0
	​

z
1
	​

;

the fixed dirty rows z
0
	​

={8,9}, z
1
	​

={10,11};

local nonedge-codegree lower bound 2;

A/B root-D visibility;

dirty tight equality m
z
	​

+γ(z)=6 for d
D
	​

(z)=2.

The projection certificate uses only:

the fixed zero skeleton;

triangle-freeness;

A/B root-D visibility;

touched-column equality c
d
	​

+m
d
	​

=6 for touched columns;

m
r
	​

≤8;

tight zero equality m
z
	​

+γ(z)=6;

degree lower bound for non-tight zeros;

zero-zero nonedge codegrees, excluding the dirty adjacent pair;

zero-D nonedge visibility with the dirty correction;

total-pair reroot cap.

It does not use fixed A/B-template enumeration, exact A/B template selection, cap<74 closure, or lower-q closure except insofar as your already-audited dirty tight and touched-column equalities depend on them.