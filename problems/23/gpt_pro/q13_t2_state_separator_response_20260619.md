Verdict

The next smallest safe move is a state-separator capacity cut. It targets the part the rectangle projections miss: the p A/B edges, rather than only the 36−p nonedge cells.

It needs no new frontier closure, no H14 beyond cuts already using H14, and no terminal-degree assertion.

1. Adversarial audit of existing cuts

The isolated-T cut is safe provided:

T is genuinely isolated in R. Here that follows from L(T)={1,2,3}, the disjoint-label edge rule, and c
0
	​

=0.

The support-difference trigger is an equivalence, not merely a one-way implication.

The A/R and B/R codegree terms are exact.

The exact A/B law is actually stronger than needed for its proof; triangle-freeness already excludes an A-vertex simultaneously adjacent to r, b, and the relevant common-neighbour configuration.

The H14 anti-tightness cut remains conditional on H14 excluding every degree-(8,8), codegree-two reroot, independently of the original rooted profile. Nothing below uses H14.

The rectangle cuts are safe if every overlap variable is exact. Their failure is structural, not evidence of invalidity.

2. Forced complete-block state separators

Write

X=S2,Y=D12,Z=S3,H=D13.

Then

U
1
	​

=Y∪H∪T,U
2
	​

=X∪Y∪T,U
3
	​

=Z∪H∪T.

Every A-state and every B-state is independent in R and intersects all three U
i
	​

.

Lemma 1: complete Y−Z block

If R[Y,Z] is complete bipartite, then

K
H
	​

:=H∪T
	​


intersects every A-state and every B-state.

Proof

Let S⊆R be a legal A-state or B-state, and suppose

S∩(H∪T)=∅.

Since S∩U
1
	​


=∅, it must contain a vertex of Y. Since S∩U
3
	​


=∅, it must contain a vertex of Z.

But every Y−Z pair is an R-edge, contradicting independence of S. Therefore

S∩(H∪T)

=∅.

∎

Local domination makes Y−Z complete whenever

∣Y∣=2or∣Z∣=2.

Indeed, if ∣Y∣=2, every Z-vertex needing at least two Y-neighbours sees all of Y; the other case is symmetric.

Lemma 2: complete X−H block

If R[X,H] is complete bipartite, then

K
Y
	​

:=Y∪T
	​


intersects every A-state and every B-state.

Proof

If a legal independent state S avoided Y∪T, visibility in U
1
	​

 would force S∩H

=∅, while visibility in U
2
	​

 would force S∩X

=∅. Completeness of X−H would contradict independence. ∎

This block is complete whenever

∣X∣=2or∣H∣=2.

Thus every one of the previously listed ten largest profile families has at least one of these separators. In particular, profile 6195 has ∣Y∣=2, so H∪T is a state separator in all twenty rows, not just e
R
	​

=12.

3. State-separator capacity lemma

Let K⊆R intersect every legal A-state and B-state.

For a∈A, write

X
a
	​

=N
R
	​

(a),d
P
	​

(a)=∣N
B
	​

(a)∣.

For r∈R, let

β
r
	​

=∣{b∈B:r∈Y
b
	​

}∣.
Lemma 3

For every a∈A,

d
P
	​

(a)≤
r∈K∖X
a
	​

∑
	​

β
r
	​

.
	​

(SC-A)

Symmetrically, for every b∈B,

d
P
	​

(b)≤
r∈K∖Y
b
	​

∑
	​

α
r
	​

.
	​

(SC-B)
Proof

Consider an A/B edge ab.

Because K intersects every B-state,

Y
b
	​

∩K

=∅.

Since ab is an edge, the exact A/B law gives

X
a
	​

∩Y
b
	​

=∅.

Therefore

Y
b
	​

∩(K∖X
a
	​

)

=∅.

Thus every B-neighbour b of a contributes at least one incidence to

r∈K∖X
a
	​

∑
	​

β
r
	​

.

Different neighbours may contribute several incidences or the same R-column, but this only overcounts. Hence

d
P
	​

(a)≤
r∈K∖X
a
	​

∑
	​

β
r
	​

.

The B-side statement is symmetric. ∎

This is the missing interaction: it bounds each A/B edge degree using the opposite shore’s capacity on a mandatory state transversal.

Degree-combined form

In the r
0
	​

=8 branch,

d
G
	​

(a)=1+∣X
a
	​

∣+d
P
	​

(a)≥8,

so

d
P
	​

(a)+∣X
a
	​

∣≥7.

Combining this with SC-A gives

∣X
a
	​

∣+
r∈K∖X
a
	​

∑
	​

β
r
	​

≥7.
	​

(DS-A)

Likewise,

∣Y
b
	​

∣+
r∈K∖Y
b
	​

∑
	​

α
r
	​

≥7.
	​

(DS-B)

The raw SC-A/SC-B cuts require no use of minimum degree. DS-A/DS-B additionally use the ordinary A/B vertex degree floor inherent in r
0
	​

=8.

Global cheap form

Let

q
r
	​

=α
r
	​

β
r
	​

.

Summing SC-A over a∈A gives

p≤
r∈K
∑
	​

(∣A∣−α
r
	​

)β
r
	​

.

Therefore

p+
r∈K
∑
	​

q
r
	​

≤∣A∣
r∈K
∑
	​

β
r
	​

.
	​

(GSC-A)

Symmetrically,

p+
r∈K
∑
	​

q
r
	​

≤∣B∣
r∈K
∑
	​

α
r
	​

.
	​

(GSC-B)

In the 6+6 code convention, both coefficients are 6.

These are almost free because the rectangle implementation already has exact q
r
	​

.

4. Exact CP-SAT encoding

Assume the verifier already has

C++
x[a][r]       // r in X_a
y[b][r]       // r in Y_b
p_ab[a][b]    // A/B edge
z[a][b][r]    // x[a][r] AND y[b][r], exact

Then

y[b][r] - z[a][b][r]

equals y
br
	​

 when r∈
/
X
a
	​

, and equals 0 when r∈X
a
	​

.

No new auxiliary variables are needed.

C++
void AddStateSeparatorCapacity(
    CpModelBuilder& model,
    const std::vector<int>& separator,
    const std::vector<std::vector<BoolVar>>& x,
    const std::vector<std::vector<BoolVar>>& y,
    const std::vector<std::vector<BoolVar>>& p_ab,
    const std::vector<std::vector<std::vector<BoolVar>>>& z) {

  const int num_a = x.size();
  const int num_b = y.size();
  const int q = x[0].size();

  // A-state cuts.
  for (int a = 0; a < num_a; ++a) {
    LinearExpr p_degree;
    for (int b = 0; b < num_b; ++b) {
      p_degree += p_ab[a][b];
    }

    LinearExpr separator_capacity;
    for (int r : separator) {
      for (int b = 0; b < num_b; ++b) {
        separator_capacity += y[b][r] - z[a][b][r];
      }
    }

    // SC-A.
    model.AddLessOrEqual(p_degree, separator_capacity);

    // DS-A: explicit projection of minimum degree + SC-A.
    LinearExpr state_size;
    for (int r = 0; r < q; ++r) {
      state_size += x[a][r];
    }
    model.AddGreaterOrEqual(state_size + separator_capacity, 7);
  }

  // B-state cuts.
  for (int b = 0; b < num_b; ++b) {
    LinearExpr p_degree;
    for (int a = 0; a < num_a; ++a) {
      p_degree += p_ab[a][b];
    }

    LinearExpr separator_capacity;
    for (int r : separator) {
      for (int a = 0; a < num_a; ++a) {
        separator_capacity += x[a][r] - z[a][b][r];
      }
    }

    // SC-B.
    model.AddLessOrEqual(p_degree, separator_capacity);

    // DS-B.
    LinearExpr state_size;
    for (int r = 0; r < q; ++r) {
      state_size += y[b][r];
    }
    model.AddGreaterOrEqual(state_size + separator_capacity, 7);
  }
}

Add the global versions as well:

C++
LinearExpr q_on_k;
LinearExpr alpha_on_k;
LinearExpr beta_on_k;

for (int r : separator) {
  for (int a = 0; a < num_a; ++a) {
    alpha_on_k += x[a][r];
  }
  for (int b = 0; b < num_b; ++b) {
    beta_on_k += y[b][r];
  }
  for (int a = 0; a < num_a; ++a) {
    for (int b = 0; b < num_b; ++b) {
      q_on_k += z[a][b][r];
    }
  }
}

LinearExpr total_p;
for (int a = 0; a < num_a; ++a) {
  for (int b = 0; b < num_b; ++b) {
    total_p += p_ab[a][b];
  }
}

model.AddLessOrEqual(
    total_p + q_on_k,
    num_a * beta_on_k);

model.AddLessOrEqual(
    total_p + q_on_k,
    num_b * alpha_on_k);

These are ordinary integer-linear CP-SAT constraints. 
Google for Developers

Recommended flag:

--state-separator-capacity

Static activation rules:

if |D12| == 2 or |S3| == 2:
    add separator D13 union T

if |S2| == 2 or |D13| == 2:
    add separator D12 union T
5. Exact e
R
	​

=12 reduction for profile 6195

For

(∣X∣,∣Y∣,∣Z∣,∣H∣,∣T∣)=(3,2,3,3,2),

local domination and e
R
	​

=12 force the entire R-skeleton.

First,

R[Y,Z]=K
2,3
	​

,

contributing six edges.

The 3×3 block X−H has minimum degree at least two on both shores, so it has at least six edges.

Since the total is exactly twelve,

e(X,Z)=0,e(X,H)=6.

Every vertex of the X−H block consequently has degree exactly two. Thus

R[X,H]=K
3,3
	​

−M,

where M is a perfect matching.

There are six labelled choices for M, but they form one orbit under permutations inside H or X. Therefore the six fixed masks need only one canonical representative:

x
i
	​

h
j
	​

∈E(R)⟺i

=j.

This safely replaces the twelve former runs by seven exact cases:

p
25
26
	​

M
58,59,60,61
58,59,60.
	​

	​

6. Complete minimal separator family for the canonical skeleton

Let the missing matching be

x
i
	​

h
i
	​

∈
/
E(R),i=0,1,2.

Let

Y={y
0
	​

,y
1
	​

},T={t
0
	​

,t
1
	​

}.

The inclusion-minimal subsets of R meeting every legal state are exactly the following eight sets.

First,

K
∗
	​

=T∪H.
	​


Then, for each proper subset J⊊{0,1,2},

K
J
	​

=T∪Y∪{h
i
	​

:i∈J}∪{x
i
	​

:i∈
/
J}.
	​


There are seven proper subsets J, hence eight separators in total.

Proof that this list is complete

The singleton states

{t
0
	​

},{t
1
	​

}

are independent and meet every U
i
	​

. Hence every state transversal must contain both t
0
	​

,t
1
	​

.

For each i, the following are legal states:

{x
i
	​

,h
i
	​

},{y
0
	​

,h
i
	​

},{y
1
	​

,h
i
	​

}.

Therefore, if a transversal omits h
i
	​

, it must contain

x
i
	​

, y
0
	​

, y
1
	​

.

If it contains all three h
i
	​

, minimality gives T∪H.

Otherwise at least one h
i
	​

 is omitted, forcing both y
0
	​

,y
1
	​

; for every i, minimality then chooses exactly one of

h
i
	​

,x
i
	​

,

with x
i
	​

 forced whenever h
i
	​

 is omitted. This gives precisely K
J
	​

.

To verify that every K
J
	​

 hits every legal state, consider a T-free legal state S. It contains some h
i
	​

. If h
i
	​

∈K
J
	​

, it is hit. Otherwise i∈
/
J. Visibility in U
2
	​

 forces S to contain either a Y-vertex or an X-vertex. The only X-vertex independent from h
i
	​

 is x
i
	​

. Both Y and x
i
	​

 belong to K
J
	​

, so S∩K
J
	​


=∅.

Thus the list is exact.

Add SC-A/SC-B and DS-A/DS-B for all eight separators in the canonical e
R
	​

=12 model.

7. Recommended finite experiment

Run the following ablation.

Pass A: all 238 rows

Add only the statically forced complete-block separators:

D13 union T  when |D12|=2 or |S3|=2
D12 union T  when |S2|=2 or |D13|=2

Use the per-state capacity cuts, not only the global sums.

Pass B: profile 6195, e
R
	​

=12

Use:

one canonical R-skeleton
seven exact (p,M) cases
all eight minimal state separators
full Psi masks, not only class-uniform masks
anti-tightness
all existing exact codegrees

With q=13, full Ψ means only 2
13
=8192 masks. Once R is fixed, all R-boundary terms are constants, so this is the right small setting in which to test non-class-uniform rooted cuts.

For a proof-grade closure:

Verify independently that the six skeletons form one orbit.

Verify by a 2
13
-mask checker that the eight displayed sets are exactly the minimal legal-state transversals.

Split the seven (p,M) cases exactly.

Produce an independently checkable UNSAT certificate for every case, rather than relying solely on a timeout-sensitive CP-SAT status.

If the seven cases remain UNKNOWN after these cuts, the next architecture change should be a canonical fixed-skeleton state-table SAT encoding, not another moment projection.

Why the rectangle cuts did not close the rows

The rectangle cuts see

Q
r
	​

=A
r
	​

×B
r
	​

,

so they describe only A/B nonedges.

They discard two decisive features:

Higher-order concentration. Many Q
r
	​

 can pile onto the same small collection of nonedge cells. Pairwise Bonferroni and second moments become weak when triple and higher intersections are large.

Visible disjoint-state capacity. A/B edges require two full states to be disjoint, while both states must still hit all three U
i
	​

. The rectangle inequalities do not measure whether an A-state has enough opposite-shore incidence remaining on a mandatory state separator to support its required P-degree.

The separator cut captures exactly this second interaction:

large P-degree⟹large opposite-shore capacity outside the current state.

That is why it is materially different from wedge, global moment, isolated-T, and mixed-codegree projections, despite also being logically implied by the complete exact model.

Weakest steps

The separator-capacity inequalities are projections of constraints already present in the exact verifier. Their mathematical validity is unconditional, but their computational benefit is not guaranteed.

The combined DS-A/DS-B form assumes the standard r
0
	​

=8 A/B degree inequality 1+∣X
a
	​

∣+d
P
	​

(a)≥8. The raw SC-A/SC-B cuts do not need this assumption.

The eight-separator classification is specific to the canonical profile-6195 e
R
	​

=12 skeleton. The simpler D13∪T separator applies to all profile-6195 rows.

No exact row is claimed closed before the proposed rerun. The rigorous hand reduction obtained here is the six-to-one skeleton orbit reduction and the complete separator classification.