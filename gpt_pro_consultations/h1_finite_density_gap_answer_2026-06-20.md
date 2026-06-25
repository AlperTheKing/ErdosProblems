Main conclusion

The asymptotic BCL hypothesis does not leave the two large finite gaps stated in the prompt.

A uniform blow-up transfers BCL’s large-n density theorem back to finite graphs. After applying the density normalization correctly, the only edge counts not covered by BCL or the existing finite 109−139 certificate are

e(G)∈{140,141,142,143}.
	​


In particular:

74≤e(G)≤108 is already closed rigorously.
	​


The key distinction is between density measured as e/(
2
n
	​

) and the blow-up-invariant quantity e/n
2
.

1. Finite-transfer lemma for asymptotic density theorems

For an integer t≥1, let G[t] be the uniform t-blow-up of G: replace each vertex by an independent class of size t, and each edge by a K
t,t
	​

.

Lemma 1: exact scaling
e(G[t])=t
2
e(G),β(G[t])=t
2
β(G).
(1)
Proof

Only the second identity needs proof.

Let the vertices of G be v
1
	​

,…,v
n
	​

, and suppose a cut of G[t] places a
i
	​

 of the t copies of v
i
	​

 on its first side. The contribution of a blown-up edge v
i
	​

v
j
	​

 to the cut is

a
i
	​

(t−a
j
	​

)+(t−a
i
	​

)a
j
	​

.

For fixed a
j
	​

, this is affine in a
i
	​

. Therefore a
i
	​

 can be replaced by either 0 or t, whichever does not decrease the cut. Repeating for every class produces a cut at least as large in which every class lies entirely on one side.

Such class-uniform cuts are precisely blow-ups of cuts of G. Hence

MaxCut(G[t])=t
2
MaxCut(G),

which proves (1). ∎

BCL prove, for sufficiently large N, that

β(H)≤
25
N
2
	​


whenever

e(H)≤0.2486(
2
N
	​

)ore(H)≥0.3197(
2
N
	​

).

They also prove the global large-N bound β(H)≤N
2
/23.5. 
arXiv
 Their paper explicitly notes that homogeneous N
2
-bounds can be transferred to smaller orders by blow-ups. 
arXiv

Now let G have n=30 vertices and m edges. Its t-blow-up has density

(
2
30t
	​

)
e(G[t])
	​

=
(
2
30t
	​

)
t
2
m
	​

=
30(30t−1)
2tm
	​

⟶
450
m
	​

.
(2)

Consequently:

Low-density transfer

If

450
m
	​

<0.2486,

then for all sufficiently large t, G[t] lies in the BCL low-density range. Since

450(0.2486)=111.87,

this holds for every integer

m≤111.

If β(G)≥37, then by Lemma 1,

β(G[t])≥37t
2
>36t
2
=
25
(30t)
2
	​

,

contradicting BCL. Therefore

m≤111⟹β(G)≤36.
	​

(3)

This rigorously closes the entire requested low range 74≤m≤108.

High-density transfer

Similarly, if

450
m
	​

>0.3197,

then sufficiently large blow-ups lie in the BCL high-density range. Since

450(0.3197)=143.865,

this holds for every integer

m≥144.

Therefore

m≥144⟹β(G)≤36.
	​

(4)

The unknown asymptotic threshold n
0
	​

 is harmless: choose t after both the density inequality and 30t≥n
0
	​

 hold.

The thresholds 111 and 144 are strict and exact for this argument. It does not cover m=112 through the low theorem or m=143 through the high theorem.

2. BCL also bounds the possible value of a counterexample

The global BCL bound transfers in the same way:

t
2
β(G)=β(G[t])≤
23.5
(30t)
2
	​

.

Therefore every finite triangle-free graph on 30 vertices satisfies

β(G)≤
23.5
900
	​

<39.

Since β(G) is integral,

β(G)≤38.
	​

(5)

Thus a counterexample to H1 must have

β(G)∈{37,38}.
	​

(6)

Combining the finite transfer with the audited medium certificate gives:

edge range
e≤111
112≤e≤139
144≤e≤225
140≤e≤143
	​

status
BCL finite transfer
existing finite rooted certificate
BCL finite transfer
only remaining density gap.
	​

	​


This assumes the finite manifest really covers every valid 112−139 branch after removing the invalid 31-vertex rows.

3. Exact structural reduction for 140≤e≤143

Let G have 140≤e(G)≤143 and β(G)≥37.

Add triangle-free admissible edges until obtaining a maximal triangle-free supergraph H. Adding one edge cannot decrease β, because

MaxCut(G+e)≤MaxCut(G)+1,

and hence

β(G+e)≥β(G).
(7)

If e(H)≥144, equation (4) gives β(H)≤36, a contradiction. Therefore

140≤e(H)≤143.
(8)

This resolves the previous maximalization circularity: maximalization cannot escape into an unproved high-density range.

Because H is maximal triangle-free, every nonedge has at least one common neighbour. If every nonedge had codegree at least 4, the trusted Wang–Yang–Zhao input would make H homomorphic to C
5
	​

.

For a C
5
	​

-homomorphic graph, partition the edges according to the five edges of the target C
5
	​

. Deleting the smallest block makes the target a path and therefore makes the graph bipartite. Hence

β(H)≤
5
e(H)
	​

<29,

again impossible.

Thus:

Residual-root lemma. Every remaining counterexample has a maximal triangle-free representative H satisfying

e(H)∈{140,141,142,143},β(H)∈{37,38},

and containing a nonedge of codegree

t∈{1,2,3}.

This is exactly the setting of the existing rooted machinery, now with only four edge totals rather than a broad high-density range.

4. Shortest route using the existing rooted verifier

Regenerate the rooted scalar frontier with:

e(G)∈{140,141,142,143},t∈{1,2,3},

and no BCL-derived cap of 139.

For every root branch enforce the exact identities

2+t+∣A∣+∣B∣+q=30
(9)

and

e(G)=2t+∣A∣+∣B∣+U+p+e
R
	​

+M.
(10)

Here U is the number of C-R edges and M=e(A∪B,R).

The row generator should filter on exact total edge counts rather than merely using a cap:

Python
Run
assert 2 + t + na + nb + q == 30

root_edges = 2 * t + na + nb
total_edges = root_edges + U + p + e_R + M

model.AddAllowedAssignments(
    [total_edges],
    [[140], [141], [142], [143]],
)

All existing trusted cuts remain available. The terminal-touch equality remains excluded.

This route likely requires the least new code. The first action should be only scalar/profile generation, not a long solver run. It will show the exact number of new rows introduced by raising the high endpoint from 139 to 143.

5. Independent P-free certificate for the four edge counts

A direct planted-maximum-cut PB model would provide a valuable independent certificate and avoid all rooted profile bookkeeping.

For each

m∈{140,141,142,143},b∈{37,38},

fix a maximum-cut partition P∪
P
ˉ
, with ∣P∣=s≤15. Relabeling permits P={0,…,s−1}.

Introduce one Boolean variable

x
uv
	​

∈{0,1}

for every unordered vertex pair, so there are 435 edge variables.

Exact graph constraints

Triangle-free:

x
uv
	​

+x
uw
	​

+x
vw
	​

≤2(u<v<w).
(11)

Exact edge count:

u<v
∑
	​

x
uv
	​

=m.
(12)

Exact defect of the planted cut:

u<v
u,v∈P or u,v∈
P
ˉ
	​

∑
	​

x
uv
	​

=b.
(13)

Thus its cut size is m−b, between 102 and 106.

Exact maximum-cut condition

For S⊆V, let δ(S) be its edge boundary. Flipping all vertices of S changes the planted defect by

−
uv∈δ(S)
u,v initially on same side
	​

∑
	​

x
uv
	​

+
uv∈δ(S)
u,v initially on opposite sides
	​

∑
	​

x
uv
	​

.

Therefore the planted partition is a maximum cut exactly when, for every S,

uv∈δ(S)
P(u)

=P(v)
	​

∑
	​

x
uv
	​

−
uv∈δ(S)
P(u)=P(v)
	​

∑
	​

x
uv
	​

≥0.
	​

(14)

Pre-add all inequalities with 1≤∣S∣≤4. There are only

(
1
30
	​

)+(
2
30
	​

)+(
3
30
	​

)+(
4
30
	​

)=31930

of them, and they propagate before any complete graph candidate is found.

The ∣S∣=1 inequalities are the familiar local-optimality conditions

d
cross
	​

(v)≥d
internal
	​

(v).
(15)
Lazy exact separation

After an integer candidate is produced:

Compute its exact maximum cut.

If a better cut exists, let S be the symmetric difference between that cut and the planted cut.

Add inequality (14) for this S.

Resolve.

If no violated inequality exists, the planted cut is genuinely maximum and the candidate is an actual falsification of H1.

This is exact CEGAR, not heuristic cutting-plane logic.

Maximality strengthening

Because the residual-root lemma permits restriction to maximal triangle-free graphs, introduce

z
uvw
	​

=x
uw
	​

∧x
vw
	​


and impose, for every u<v,

x
uv
	​

+
w

=u,v
∑
	​

z
uvw
	​

≥1.
(16)

Thus every pair is either an edge or has a common neighbour.

Standard conjunction linearization is

z
uvw
	​

≤x
uw
	​

,z
uvw
	​

≤x
vw
	​

,z
uvw
	​

≥x
uw
	​

+x
vw
	​

−1.
(17)
Side-size branches

Since the planted cut contains m−b crossing edges,

s(30−s)≥m−b.

Hence only the following 93 branches occur:

s=4,…,15 when m−b≤104;

s=5,…,15 when m−b∈{105,106}.

That fits almost exactly into the available 100-worker budget.

Proof-grade output

CP-SAT can be used to discover violated flip inequalities, but the final certificate should consist of:

the complete branch manifest (m,b,s);

all accumulated inequalities (14);

an OPB or CNF encoding of (11)–(17);

a VeriPB, DRAT, or LRAT-checked UNSAT proof for every branch.

The inner MaxCut solver does not need to be trusted in the final proof: every cut it produces is merely used to add a universally valid inequality, and the final proof checker verifies the resulting finite model.

6. Recommended order of work

The density gap should be rewritten as:

Only e=140,141,142,143 remain.
	​


Then:

Regenerate the rooted scalar frontier for those four exact edge counts and t=1,2,3. This is the smallest immediate experiment.

In parallel, run the 93 planted-cut PB branches as an independent certificate.

Do not spend further compute on 74−108 or 144+; those ranges are already eliminated by the finite blow-up transfer.

Weakest steps

This argument assumes the BCL large-n theorem itself is accepted as valid. It removes the unknown n
0
	​

; it does not independently reverify their flag-algebra calculation.

The transfer requires strict limiting density inequalities. That is why the exact conclusions are m≤111 and m≥144, and why m=143 is not included.

The statement that the only remaining range is 140−143 assumes the audited rooted certificates genuinely cover every valid 112−139 branch after deletion of the invalid 31-vertex rows.

The planted-cut model is mathematically exact, but its runtime is not yet known. The smallest next experiment is the scalar regeneration for exact e=140,141,142,143; it will immediately reveal whether extending the existing rooted certificate by four edge counts is easier than the independent PB route.