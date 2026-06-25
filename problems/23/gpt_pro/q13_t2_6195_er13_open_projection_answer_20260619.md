Result

The missing projected constraint is the typewise projected A/R and B/R multicover.

For the representative mask 0xfd8a38, adding this one family to the existing six-column projection certificate gives

p≤p
XH
	​

≤20.
	​


Thus it closes both p=24 and p=25, for every local excess allocation of total at most 5. Since the eighteen open masks are the same K
3,3
	​

 minus a two-edge matching class up to relabelling, the certificate applies to all eighteen.

No H14, terminal equality, Ψ-cut, same-side codegree, or fixed A/B template is needed.

1. Why the constraint is valid

Set

K=X∪H={0,1,2,8,9,10}.

For 0xfd8a38, the edges in K are

08,09,010,18,110,28,29.

The block D12−S3 is forced to be K
2,3
	​

, contributing six edges. Since e
R
	​

=13 and X−H already contributes seven edges, there are no optional X−S3 edges. Consequently,

N
R
	​

(r)⊆Kfor every r∈K.
	​

(1)

Let P be the seventeen projected independent sets listed in the question. Define projected counts

a
S
	​

=
I:I∩K=S
∑
	​

A
I
	​

,b
S
	​

=
J:J∩K=S
∑
	​

B
J
	​

(S∈P).

For S∈P and r∈K∖S, define

λ(S,r)=∣S∩N
R
	​

(r)∣

and

C
B
(S,r)=
T∈P
r∈T, S∩T=∅
	​

∑
	​

b
T
	​

.
Projected mixed-codegree lemma

For every S∈P,

a
S
	​

>0⟹C
B
(S,r)≥max{0,2−λ(S,r)}(r∈K∖S).
	​

(PMC-A)

Symmetrically,

b
S
	​

>0⟹C
A
(S,r)≥max{0,2−λ(S,r)}.
	​

(PMC-B)
Proof

Suppose a
S
	​

>0, and choose an A-vertex a whose full state I=N
R
	​

(a) satisfies

I∩K=S.

Fix r∈K∖S. Then ar is a nonedge, so its codegree is at least 2.

Its common neighbours can only be:

vertices of R in I∩N
R
	​

(r);

B-vertices b such that ab∈E(G) and br∈E(G).

There are no other possibilities:

neither root is adjacent to r;

A is independent;

a has no neighbour in C, since A∪C lies in the neighbourhood of the A-root and G is triangle-free.

By (1),

∣I∩N
R
	​

(r)∣=∣S∩N
R
	​

(r)∣=λ(S,r).

If a B-vertex b is a common neighbour of a,r, its full state J satisfies

r∈JandI∩J=∅,

the latter because ab is an A/B edge. Therefore its projection T=J∩K satisfies

r∈T,S∩T=∅.

Hence the actual number of common B-neighbours is at most C
B
(S,r). Thus

2≤∣N(a)∩N(r)∣≤λ(S,r)+C
B
(S,r),

which proves PMC-A. PMC-B is symmetric. ∎

The projection may count B-states that intersect I outside K, so it can overestimate the available B common neighbours. That only makes PMC-A a relaxation; it cannot invalidate it.

2. Why the previous p
XH
	​

=28 optimum is spurious

One projected extremizer producing 28 uses, on one shore, a state of projection

S={0,1}.

Consider r=9. In the fixed skeleton,

N
R
	​

(9)∩K={0,2},

so

λ({0,1},9)=1.

PMC-A therefore requires at least one opposite-shore projected state that:

contains 9;

is disjoint from {0,1}.

The p
XH
	​

=28 extremizer has no such opposite state. Hence the corresponding A/R nonedge has only the single common R-neighbour 0, violating codegree at least 2.

The symmetric defect occurs for projection {0,2} against vertex 10.

Thus the bound 28 survives only because the old checker enforced projected R/R coverage but did not enforce projected A/R and B/R coverage.

3. Exact finite certificate

I enumerated the following relaxation.

For each shore, enumerate all multisets of six elements from the seventeen projected types:

(
6
17+6−1
	​

)=(
6
22
	​

)=74,613.

For every pair of A/B projected multisets impose:

exact projected column sums;

the two internal R/R requirements

a
{1,9}
	​

+b
{1,9}
	​

≥2,a
{2,10}
	​

+b
{2,10}
	​

≥2;

PMC-A and PMC-B for every used projected type and every omitted local vertex;

no other full-state constraints.

All local targets

(4,5,5,3,4,4)+e,e∈Z
≥0
6
	​

,∑e≤5

were checked. There are

(
6
11
	​

)=462

such targets.

Of these:

454 have no projected count solution at all;

only 8 survive;

the largest projected disjoint-pair capacity is 20.

Surviving local target (m
0
	​

,m
1
	​

,m
2
	​

,m
8
	​

,m
9
	​

,m
10
	​

)	Maximum p
XH
	​


(4,5,5,4,4,4)	18
(5,5,5,3,4,4)	18
(4,5,5,4,4,5)	16
(4,5,5,4,5,4)	16
(5,5,6,3,4,4)	16
(5,6,5,3,4,4)	16
(4,5,5,4,5,5)	20
(5,6,6,3,4,4)	14

In particular, the floor target

(4,5,5,3,4,4)

is itself infeasible after PMC-A/B.

Every actual A/B edge has disjoint K-projections, so

p≤p
XH
	​

≤20.

Therefore

p=24 and p=25 are both impossible.
	​


The certificate uses neither the A/B intersection-one prohibition nor root-opposite, A/A, B/B, Ψ, anti-tightness, or any outside-K column. It is consequently a relaxation of the current exact verifier.

The standalone checker and its recorded output are here:

C++ projected mixed-codegree checker

Certificate output

4. Exact CP-SAT constraints

Introduce projected counts and exact usage indicators:

a
S
	​

,b
S
	​

∈{0,…,6},u
S
A
	​

,u
S
B
	​

∈{0,1}.

Channel them by

u
S
A
	​

≤a
S
	​

≤6u
S
A
	​

,u
S
B
	​

≤b
S
	​

≤6u
S
B
	​

.
(2)

For each S∈P and r∈K∖S, precompute

δ(S,r)=max{0,2−∣S∩N
R
	​

(r)∣}.

Add

T∈P
r∈T, S∩T=∅
	​

∑
	​

b
T
	​

≥δ(S,r)u
S
A
	​

	​

(3)

and symmetrically

T∈P
r∈T, S∩T=∅
	​

∑
	​

a
T
	​

≥δ(S,r)u
S
B
	​

.
	​

(4)

For this seventeen-type system there are only 58 nontrivial implications per shore:

30 with right side 1;

28 with right side 2.

Conceptual C++:

C++
for (int s = 0; s < num_projection_types; ++s) {
  model.AddGreaterOrEqual(proj_a[s], used_a[s]);
  model.AddLessOrEqual(proj_a[s], 6 * used_a[s]);

  model.AddGreaterOrEqual(proj_b[s], used_b[s]);
  model.AddLessOrEqual(proj_b[s], 6 * used_b[s]);

  const int S = projection_mask[s];

  for (int r = 0; r < 6; ++r) {
    if (S & (1 << r)) continue;

    const int local_common =
        std::popcount(static_cast<unsigned>(
            S & local_neighbor_mask[r]));

    const int deficit = std::max(0, 2 - local_common);
    if (deficit == 0) continue;

    LinearExpr candidate_b;
    LinearExpr candidate_a;

    for (int t = 0; t < num_projection_types; ++t) {
      const int T = projection_mask[t];

      if ((T & (1 << r)) && ((S & T) == 0)) {
        candidate_b += proj_b[t];
        candidate_a += proj_a[t];
      }
    }

    model.AddGreaterOrEqual(
        candidate_b, deficit * used_a[s]);

    model.AddGreaterOrEqual(
        candidate_a, deficit * used_b[s]);
  }
}

This uses only ordinary integer-linear channeling; no product variable is required for PMC-A/B. OR-Tools documents Boolean channeling and half-reified linear constraints through OnlyEnforceIf, although the fully linear form above is simpler. 
Google for Developers

Link the projected counts to the full state-count master by

C++
for (int s = 0; s < num_projection_types; ++s) {
  LinearExpr aggregate_a;
  LinearExpr aggregate_b;

  for (int I = 0; I < num_full_states; ++I) {
    if (projection_index[I] == s) {
      aggregate_a += A_count[I];
      aggregate_b += B_count[I];
    }
  }

  model.AddEquality(proj_a[s], aggregate_a);
  model.AddEquality(proj_b[s], aggregate_b);
}

After accepting the small certificate, the strongest static row cut is simply

profile 6195
AND e_R = 13
AND X-H is K3,3 minus a two-edge matching
AND total excess <= 5
    ==> p <= 20.

That cut closes all eighteen open masks immediately.

Weakest steps

The numerical bound p
XH
	​

≤20 is an exhaustive finite certificate, not a short symbolic inequality. Its proof status depends on auditing the small standalone checker.

For each of the eighteen masks, one must independently verify that the seven X−H edges form K
3,3
	​

 minus two disjoint edges and that the forced six D12−S3 edges leave no X−S3 edge. This is what guarantees N
R
	​

(r)⊆K.

The argument relies on the row fact that total excess is at most 5. If a later row permits larger total excess, its additional local targets must be checked separately.

PMC-A/B is logically implied by the full typewise A/R and B/R constraints. Its advantage is projection and early propagation, rather than a new graph-theoretic restriction.