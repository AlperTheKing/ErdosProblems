I’ll first check whether the state-count quotient preserves all labeled constraints, then identify the smallest missing pair or triple correlation needed for a sound P-free certificate.

With fixed R, state multiplicities are a valid quotient of A/B row permutations; the main risk is weakening typewise products or used-state conditions into aggregates.

The quotient does not need a six-by-six matching variable. The key is exact cross-type products and activation of every active same-shore type pair, including duplicate-type pairs.

Thought for 26m 44s
Verdict

The state-count model is sound as a necessary relaxation. More strongly, for a fixed R-skeleton it becomes an exact quotient of the labelled A/B-state model once all constraints are imposed typewise.

There is no hidden six-by-six matching correlation: vertices having the same state are genuine twins, and the A/B adjacency between two state classes is complete or empty. Counts determine the entire graph.

There are, however, two points to audit before relying on exactness.

1. Smallest potentially missing constraint: opposite-root codegree

Your description mentions root-to-R codegrees and root-colour visibility, but does not explicitly mention the nonedges between an A-vertex and the B-root, or between a B-vertex and the A-root.

Let the original roots be x,y, with A⊆N(x)∖N(y) and B⊆N(y)∖N(x). For a∈A,

N(a)∩N(y)=N
B
	​

(a).

Indeed:

a is not adjacent to y;

y's possible common neighbours with a lie in C∪B;

no c∈C is adjacent to a, since x,a,c would be a triangle;

every b∈B adjacent to a is a common neighbour of a,y.

Since every nonedge has codegree at least t=2,

d
P
	​

(a)≥2(a∈A),
	​

d
P
	​

(b)≥2(b∈B).
	​

(RP)

For a used A-state I, define

d
B
	​

(I):=
J:I∩J=∅
∑
	​

B
J
	​

.

Then the count-level constraints are

A
I
	​

>0⟹d
B
	​

(I)≥2,
	​

(RP-A)

and symmetrically

B
J
	​

>0⟹d
A
	​

(J):=
I:I∩J=∅
∑
	​

A
I
	​

≥2.
	​

(RP-B)

These are stronger than the ordinary degree inequalities

∣I∣+d
B
	​

(I)≥7,

particularly for large states of size 6,7,8, which occur naturally in the high-M rows.

If your existing “root-side visibility” already includes d
P
	​

≥2, then this is not new. It should nevertheless be explicitly checked in the state-count implementation.

Encoding

With u
I
A
	​

↔A
I
	​

≥1,

C++
model.AddGreaterOrEqual(A[I], uA[I]);
model.AddLessOrEqual(A[I], 6 * uA[I]);

model.AddEquality(
    dB[I],
    Sum(B[J] for J with (I & J) == 0));

model.AddGreaterOrEqual(dB[I], 2)
    .OnlyEnforceIf(uA[I]);

Add the symmetric B-side constraint.

2. Exactness theorem for the state-count quotient

Let I be the legal states: independent subsets I⊆R satisfying the three root-colour visibility conditions and any other static row-local conditions.

Introduce

A
I
	​

,B
I
	​

∈{0,…,6},
I
∑
	​

A
I
	​

=
I
∑
	​

B
I
	​

=6.
Proposition

Suppose the count model enforces the constraints below for every used state and every used pair of state types. Then every integer count solution lifts to a labelled A/B-state solution satisfying all the corresponding exact-state constraints.

Proof

Create A
I
	​

 copies of every A-state I, and B
J
	​

 copies of every B-state J. Join each copy to precisely the vertices of its state in R. Between A and B, place all edges between the I-class and J-class exactly when

I∩J=∅.

Thus every A/B state-class pair induces either a complete bipartite graph or an empty bipartite graph. There is no choice of a matching or other row-level correlation.

All required codegrees are then determined by state types and multiplicities:

A/R codegree

For r∈
/
I, an A-vertex with state I and r have exactly

∣I∩N
R
	​

(r)∣+
J:I∩J=∅
r∈J
	​

∑
	​

B
J
	​


common neighbours. Therefore the exact typewise constraint is

∣I∩N
R
	​

(r)∣+
J:I∩J=∅
r∈J
	​

∑
	​

B
J
	​

≥2
	​

(AR)

whenever A
I
	​

>0. The B/R formula is symmetric.

A/A codegree

Two distinct A-vertices of states I,K have:

the A-root as one common neighbour;

∣I∩K∣ common R-neighbours;

one common B-neighbour for each B-state disjoint from I∪K.

Thus

1+∣I∩K∣+
J:J∩(I∪K)=∅
∑
	​

B
J
	​

≥2.
	​

(AA)

This must be activated when I

=K, A
I
	​

>0, and A
K
	​

>0.

For I=K and A
I
	​

≥2, it is automatic because every legal state is nonempty:

1+∣I∣≥2.

Hence no diagonal “two-copy” Boolean is required in this particular model. The B/B constraint is symmetric.

R/R codegree

For every fixed R-nonedge rs,

∣L(r)∩L(s)∣+∣N
R
	​

(r)∩N
R
	​

(s)∣+
I:{r,s}⊆I
∑
	​

(A
I
	​

+B
I
	​

)≥2.
	​

(RR)
A/B law

For every used cross-type pair I,J,

∣I∩J∣

=1.

If the intersection is empty, the entire I-J block consists of P-edges. If its size is at least two, every pair in the block has at least two common R-neighbours.

Consequently, once the typewise constraints are present, expanding the multiplicities gives a labelled assignment satisfying exactly the same local verifier conditions. ∎

Consequence

The count model does not need a variable saying which copy of I is paired with which copy of J. There is no pairing choice.

The minimal auxiliary information is:

u
I
A
	​

=[A
I
	​

>0] and u
J
B
	​

=[B
J
	​

>0], for activating constraints;

exact integer products needed to count complete A/B blocks.

3. Efficient exact count-level formulation

For every state I, precompute

D(I)={J:I∩J=∅},O
1
	​

(I)={J:∣I∩J∣=1}.

Define

d
B
	​

(I)=
J∈D(I)
∑
	​

B
J
	​

.

Then impose:

Exact P-count
p=
I
∑
	​

A
I
	​

d
B
	​

(I).
(P)

This needs only one product per A-state, rather than one product for every disjoint pair of state types.

C++
IntVar prod_I = model.NewIntVar(Domain(0, 36));

model.AddMultiplicationEquality(
    prod_I,
    {A[I], dB[I]});

model.AddEquality(Sum(prod_I), exact_p);

OR-Tools exposes exact integer multiplication equalities and allowed-assignment tables, so the product may alternatively be encoded by the 49 tuples (a,d,ad), 0≤a,d≤6. 
GitHub
+1

Forbidden singleton intersection
C++
model.AddEquality(
    Sum(B[J] for J in one_intersection[I]),
    0).OnlyEnforceIf(uA[I]);

The symmetric constraints are redundant mathematically but may improve propagation.

A/R multicover

For each r∈
/
I, let

δ
I
	​

(r)=max{0,2−∣I∩N
R
	​

(r)∣}.

Then

A
I
	​

>0⟹
J∈D(I)
r∈J
	​

∑
	​

B
J
	​

≥δ
I
	​

(r).
	​

(MC-AR)

This exact state-specific multicover is considerably stronger than aggregate mixed-codegree projections.

Same-side pair activation

For disjoint distinct states I,K,

A
I
	​

>0, A
K
	​

>0⟹
J:J∩(I∪K)=∅
∑
	​

B
J
	​

≥1.
	​

(MC-AA)
C++
model.AddGreaterOrEqual(common_b_neighbors[I][K], 1)
    .OnlyEnforceIf({uA[I], uA[K]});

Only disjoint I,K need constraints. If I∩K

=∅, their common root and common R-vertex already give codegree at least two.

These typewise A/R and A/A implications are the most important correlation constraints. Replacing them by sums averaged over all state types can produce false FEASIBLE count vectors.

4. Strongest additional P-free cut: exact weighted-quotient cut separation

Full Ψ(W) over R-masks may still miss cuts in which different A-state or B-state classes are placed on different sides. The strongest safe count-level strengthening is to separate all cuts of the weighted state quotient.

This uses no A/B template enumeration.

Twin-uniformity lemma

For fixed counts, all copies of one A-state I are independent vertices with identical open neighbourhoods. The same is true for every B-state class.

There exists a minimum-monochromatic-edge cut in which every such twin class lies entirely on one side.

Proof

Fix the sides of all vertices outside a twin class Q. Because Q is independent and all its vertices have identical external neighbours, every vertex of Q incurs the same monochromatic-edge cost on side zero and the same cost on side one. Moving all vertices of Q to the cheaper side cannot increase the total.

Starting with a minimum cut and uniformizing each twin class in turn preserves minimality. ∎

Therefore the exact minimum monochromatic edge count can be computed on a weighted quotient containing:

the two roots;

the three C-vertices;

the thirteen fixed R-vertices;

one node for every used A-state;

one node for every used B-state.

At most six A-types and six B-types can be used, so a candidate quotient has at most thirty nodes.

Exact cut inequality

Fix a binary side assignment σ for all quotient nodes. Let

[uv]
σ
	​

={
1,
0,
	​

σ(u)=σ(v),
σ(u)

=σ(v).
	​


The monochromatic-edge count is

F
σ
	​

=
	​

C
σ
	​

+
I
∑
	​

A
I
	​

([x,A
I
	​

]
σ
	​

+
r∈I
∑
	​

[r,A
I
	​

]
σ
	​

)
+
J
∑
	​

B
J
	​

([y,B
J
	​

]
σ
	​

+
r∈J
∑
	​

[r,B
J
	​

]
σ
	​

)
+
I∩J=∅
∑
	​

A
I
	​

B
J
	​

[A
I
	​

,B
J
	​

]
σ
	​

,
	​

(QCut)

where C
σ
	​

 is the fixed contribution from:

root-C edges;

C-R edges;

fixed R-edges.

The global hypothesis β(G)≥37 gives

F
σ
	​

≥37
	​

(QC)

for every quotient-side assignment σ.

This family strictly contains the currently used rooted masks unless the implementation of full Ψ already permits arbitrary A-state-type and B-state-type flips.

Lazy separation procedure

For an integer count candidate:

Construct the weighted quotient using only the used state types.

Solve its exact minimum-monochromatic-edge problem.

If the optimum is at most 36, record the violating side assignment.

Extend the assignment arbitrarily to unused state types.

Add the corresponding valid inequality F
σ
	​

≥37 to the count master.

Unused types must be assigned a side and included in the generated inequality. Simply omitting their nonnegative contributions would not generally produce a valid global cut.

Avoiding all pair products

For a fixed quotient cut σ, define

d
B
σ
	​

(I)=
J:I∩J=∅
σ(B
J
	​

)=σ(A
I
	​

)
	​

∑
	​

B
J
	​

.

Introduce

g
I
σ
	​

=A
I
	​

d
B
σ
	​

(I).

Then the P-edge contribution is merely

I
∑
	​

g
I
σ
	​

.

Thus one quotient cut requires at most one product per A-state, rather than products for all 56,000+ disjoint state-type pairs.

5. Specialized certificate for the three high-M cases

For the canonical 6195/e
R
	​

=12 skeleton,

R[Y,Z]=K
2,3
	​

,R[X,H]=K
3,3
	​

−M
3
	​

,R[X,Z]=∅.

Under independence and the three visibility conditions, the legal-state table has 648 states before any dynamic pruning.

The local column-degree floors are

m
r
	​

=α
r
	​

+β
r
	​

≥
⎩
⎨
⎧
	​

5,
3,
5,
4,
5,
	​

r∈X,
r∈Y,
r∈Z,
r∈H,
r∈T.
	​


Their sum is

3⋅5+2⋅3+3⋅5+3⋅4+2⋅5=58.

Hence introduce exact excess variables

e
r
	​

=m
r
	​

−b
r
	​

≥0.

Then:

r
∑
	​

e
r
	​

=2for M=60,

and

r
∑
	​

e
r
	​

=3for M=61.

This gives a particularly small exact branch certificate:

(p,M)=(25,60): branch on excess-two profiles;

(26,60): the same excess-two profiles;

(25,61): branch on excess-three profiles.

There are only

(
12
14
	​

)=91

raw excess-two vectors and

(
12
15
	​

)=455

raw excess-three vectors, before quotienting by the fixed-skeleton automorphism group. These are column-profile branches, not A/B templates.

For each branch, use:

exact state counts;

root-opposite d
P
	​

≥2;

exact typewise A/R and B/R multicovers;

exact typewise A/A and B/B constraints;

the eight fixed-R minimal separator cuts;

exact p,M,α,β, R/R codegrees, and anti-tightness;

full current Ψ;

lazy weighted-quotient cut separation if the master finds a candidate.

This is the smallest experiment with a decisive interpretation:

INFEASIBLE closes the branch without any A/B template enumeration.

FEASIBLE can be expanded mechanically into six labelled A-states and six labelled B-states. If the labelled verifier then rejects it, the discrepancy identifies an omitted typewise constraint; it cannot be blamed on an unspecified row matching.

For a proof-grade finite certificate, encode the count domains in unary or one-hot form and products by 49-entry tables, then emit an OPB/CNF UNSAT certificate checked independently. CP-SAT is well suited to finding the decomposition, but a separately checked PB/SAT proof is preferable for the final certificate.

Why this should outperform the labelled model

The labelled formulation repeatedly rediscovers the 6!×6! row symmetry. The count quotient removes it exactly. The three difficult cases have high M, so many labelled solutions differ only by permutations of repeated or near-repeated large states. Count variables represent that entire orbit once.

The quotient-cut separator also captures the main interaction absent from rectangle and moment projections: dense complete P-blocks between disjoint state classes can be exploited by cuts that flip selected state classes, even when every fixed R-mask Ψ cut survives.

Weakest steps

The root-opposite constraint d
P
	​

≥2 may already be included under your implementation’s “root-side visibility.” If so, it is an audit item rather than a new cut.

Exactness requires the A/R, B/R, A/A, and B/B constraints to be activated per used state type or used type pair. Aggregate versions alone are only relaxations.

The weighted-quotient cut family is rigorously valid, but it is not proved here that one of those cuts closes all three cases; that requires the proposed separation run.

H14 anti-tightness remains conditional on the previously accepted globally reroot-invariant q=14,t=2 closure. The state-count quotient and quotient-cut separation do not otherwise depend on H14.

Sources