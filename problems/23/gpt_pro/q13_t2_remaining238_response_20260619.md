Audit

Anti-tightness is safe only under the accepted reroot-invariant H14 closure: H14 must exclude every degree-(8,8), codegree-two nonedge in the n=30 counterexample universe, not merely the original q=14 rows under a profile-specific cap.

Isolated-support separation is safe. It needs only that t is isolated in R, the standard rooted partition, triangle-freeness, and A/R–B/R nonedge codegree at least 2. In fact, the exact A/B law is not needed in its proof: if a∈A
t
	​

∩A
r
	​

 and b∈B
r
	​

, then ar,br,ab would be a triangle. The implementation trigger for a nonempty set difference must be an equivalence, not a one-way implication.

Next cut: A/B nonedge-rectangle wedge capacity

For r∈R, define

A
r
	​

=N
A
	​

(r),B
r
	​

=N
B
	​

(r),Q
r
	​

=A
r
	​

×B
r
	​

.

Let

q
r
	​

:=∣Q
r
	​

∣=α
r
	​

β
r
	​

,

and for distinct r,s,

a
rs
	​

:=∣A
r
	​

∩A
s
	​

∣,b
rs
	​

:=∣B
r
	​

∩B
s
	​

∣,o
rs
	​

:=a
rs
	​

b
rs
	​

=∣Q
r
	​

∩Q
s
	​

∣.

Finally let

N
AB
	​

:=∣A∣∣B∣−p.

In the code’s 6×6 convention,

N
AB
	​

=36−p.
Lemma: wedge capacity

If rs,rt∈E(R), with s

=t, then

q
r
	​

+q
s
	​

+q
t
	​

−o
st
	​

≤N
AB
	​

.
	​

(W)

This requires no frontier assumption, no terminal equality, and not even the prohibition on one-element A/B intersections.

Proof

Every pair (a,b)∈Q
r
	​

 has r∈X
a
	​

∩Y
b
	​

. Therefore ab is an A/B nonedge by the exact A/B law. Thus

Q
r
	​

⊆
E
(A,B)

for every r, where

∣
E
(A,B)∣=N
AB
	​

.

If rs∈E(R), triangle-freeness gives

A
r
	​

∩A
s
	​

=∅,B
r
	​

∩B
s
	​

=∅.

Indeed, an A-vertex adjacent to both r,s would form a triangle with rs, and similarly for a B-vertex. Hence

Q
r
	​

∩Q
s
	​

=∅.

Likewise rt∈E(R) gives

Q
r
	​

∩Q
t
	​

=∅.

The only possible overlap among Q
r
	​

,Q
s
	​

,Q
t
	​

 is therefore Q
s
	​

∩Q
t
	​

. Consequently,

∣Q
r
	​

∪Q
s
	​

∪Q
t
	​

∣
	​

=∣Q
r
	​

∣+∣Q
s
	​

∣+∣Q
t
	​

∣−∣Q
s
	​

∩Q
t
	​

∣
=q
r
	​

+q
s
	​

+q
t
	​

−o
st
	​

.
	​


This union lies inside the N
AB
	​

 A/B nonedges, proving (W). ∎

Why it fits the five-label core

Every non-T vertex is the centre of at least one such wedge:

r
S2
D13
D12
S3
	​

at least two forced neighbours
D13
S2
S3
D12.
	​

	​


Thus (W) applies throughout the nonisolated part of every remaining row.

For p=27, it becomes

q
r
	​

+q
s
	​

+q
t
	​

−o
st
	​

≤9.

For p=26,

q
r
	​

+q
s
	​

+q
t
	​

−o
st
	​

≤10.

These are tight capacities compared with the typical m
r
	​

=α
r
	​

+β
r
	​

 values in the high-p rows.

Strong static specialization when a forced shore has size two

Suppose X=S2 and H=D13. If either

∣X∣=2or∣H∣=2,

local domination forces R[X,H] to be complete bipartite.

For any complete bipartite R[P,Q], all cross rectangle intersections vanish. Bonferroni’s lower bound on each shore’s union therefore gives

v∈P∪Q
∑
	​

q
v
	​

−
{u,v}⊆P
∑
	​

o
uv
	​

−
{u,v}⊆Q
∑
	​

o
uv
	​

≤N
AB
	​

.
	​

(CB)
Proof

Because every uv∈P×Q is an R-edge,

Q
u
	​

∩Q
v
	​

=∅.

Hence

(
u∈P
⋃
	​

Q
u
	​

)∩
	​

v∈Q
⋃
	​

Q
v
	​

	​

=∅.

Both unions lie inside the A/B nonedge set. Therefore their cardinalities sum to at most N
AB
	​

.

For any finite family of sets,

	​

i
⋃
	​

S
i
	​

	​

≥
i
∑
	​

∣S
i
	​

∣−
i<j
∑
	​

∣S
i
	​

∩S
j
	​

∣.

Apply this separately to {Q
u
	​

:u∈P} and {Q
v
	​

:v∈Q}, then add the two lower bounds. This gives (CB). ∎

Add (CB) for:

(S2,D13)when c
2
	​

=2 or c
5
	​

=2,

and

(D12,S3)when c
3
	​

=2 or c
4
	​

=2.

Every one of the ten listed top UNKNOWN profiles has at least one such forced complete block.

For example, if

S2={x
1
	​

,x
2
	​

},

then every h∈D13 satisfies

q
h
	​

+q
x
1
	​

	​

+q
x
2
	​

	​

−o
x
1
	​

x
2
	​

	​

≤N
AB
	​

,

and the class-level cut is

q
x
1
	​

	​

+q
x
2
	​

	​

−o
x
1
	​

x
2
	​

	​

+
h∈D13
∑
	​

q
h
	​

−
{h,h
′
}⊆D13
∑
	​

o
hh
′
	​

≤N
AB
	​

.
Two almost-free multicover cuts

The existing prohibition

∣X
a
	​

∩Y
b
	​

∣

=1

gives two additional projections using the same q
r
	​

,o
rs
	​

 variables.

Every cell of Q
r
	​

 must occur in another Q
s
	​

, so

q
r
	​

≤
s

=r
∑
	​

o
rs
	​

.
	​

(DC)

Globally, if k
ab
	​

=∣X
a
	​

∩Y
b
	​

∣, then k
ab
	​

=0 or k
ab
	​

≥2. Since

r
∑
	​

q
r
	​

=
a,b
∑
	​

k
ab
	​


and

r<s
∑
	​

o
rs
	​

=
a,b
∑
	​

(
2
k
ab
	​

	​

),

the pointwise inequality

(
2
k
	​

)≥k−1(k≥2)

gives

r<s
∑
	​

o
rs
	​

≥
r
∑
	​

q
r
	​

−N
AB
	​

.
	​

(GM)

I would add (W), (CB), (DC), and (GM) under one flag because the product variables dominate the implementation cost.

Exact CP-SAT encoding

Reuse exact overlap variables if they already exist:

C++
common_a[r][s] = |A_r ∩ A_s|;
common_b[r][s] = |B_r ∩ B_s|;

They must be equalities, not lower bounds.

Create:

C++
std::vector<IntVar> rect(q);
std::vector<std::vector<IntVar>> rect_overlap(
    q, std::vector<IntVar>(q));

for (int r = 0; r < q; ++r) {
  rect[r] = model.NewIntVar(Domain(0, num_a * num_b))
                    .WithName(absl::StrCat("rect_", r));

  model.AddMultiplicationEquality(
      rect[r], {alpha[r], beta[r]});
}

for (int r = 0; r < q; ++r) {
  for (int s = r + 1; s < q; ++s) {
    rect_overlap[r][s] =
        model.NewIntVar(Domain(0, num_a * num_b))
             .WithName(absl::StrCat("rect_overlap_", r, "_", s));

    model.AddMultiplicationEquality(
        rect_overlap[r][s],
        {common_a[r][s], common_b[r][s]});
  }
}

Accessor:

C++
auto Overlap = [&](int r, int s) -> IntVar {
  if (r > s) std::swap(r, s);
  return rect_overlap[r][s];
};
Wedge cuts
C++
const int nonedges_ab = num_a * num_b - exact_p;

for (int r = 0; r < q; ++r) {
  for (int s = 0; s < q; ++s) {
    if (s == r) continue;

    for (int t = s + 1; t < q; ++t) {
      if (t == r) continue;

      model.AddLessOrEqual(
          rect[r] + rect[s] + rect[t] - Overlap(s, t),
          nonedges_ab)
          .OnlyEnforceIf({edge_r[r][s], edge_r[r][t]});
    }
  }
}

OnlyEnforceIf is appropriate here because the enforced constraint is linear and both literals must be true. Keep the multiplication equalities unconditional; current OR-Tools documentation describes OnlyEnforceIf as half-reification and notes that linear constraints support enforcement literals. 
GitHub
+1

Double-cover cuts
C++
for (int r = 0; r < q; ++r) {
  LinearExpr cover;
  for (int s = 0; s < q; ++s) {
    if (s != r) cover += Overlap(r, s);
  }
  model.AddLessOrEqual(rect[r], cover);
}
Global moment cut
C++
LinearExpr sum_rect;
LinearExpr sum_overlap;

for (int r = 0; r < q; ++r) {
  sum_rect += rect[r];
}

for (int r = 0; r < q; ++r) {
  for (int s = r + 1; s < q; ++s) {
    sum_overlap += rect_overlap[r][s];
  }
}

model.AddGreaterOrEqual(
    sum_overlap,
    sum_rect - nonedges_ab);

Also add, if not already present,

C++
model.AddGreaterOrEqual(
    sum_rect,
    2 * nonedges_ab);
Complete-block cut
C++
void AddCompleteBlockRectangleCut(
    CpModelBuilder& model,
    const std::vector<int>& left,
    const std::vector<int>& right,
    const std::vector<IntVar>& rect,
    const auto& Overlap,
    int nonedges_ab) {

  LinearExpr lhs;

  for (int v : left) lhs += rect[v];
  for (int v : right) lhs += rect[v];

  for (int i = 0; i < static_cast<int>(left.size()); ++i) {
    for (int j = i + 1; j < static_cast<int>(left.size()); ++j) {
      lhs -= Overlap(left[i], left[j]);
    }
  }

  for (int i = 0; i < static_cast<int>(right.size()); ++i) {
    for (int j = i + 1; j < static_cast<int>(right.size()); ++j) {
      lhs -= Overlap(right[i], right[j]);
    }
  }

  model.AddLessOrEqual(lhs, nonedges_ab);
}

Call it statically when a shore has size two. It is also worth explicitly fixing every cross R-edge to 1 in those rows, even though local domination already implies this.

Recommended experiment

Run a clean three-way ablation on the 242 rows:

A: wedge capacity only
B: complete-block capacity only
C: wedge + complete-block + double-cover + global moment

Use 30 seconds per row and first inspect p≥25, where N
AB
	​

≤11. Record results separately for:

forced K2,2 block
forced K2,m block with m>=3
no size-two forced shore

The cut is especially informative because all ten leading profiles fall in the first two categories. It remains fixed-P-free: no A/B templates are enumerated, and only exact support cardinalities and pair overlaps are used.

I cannot honestly claim a specific listed row is closed by these inequalities from the supplied aggregate data alone; the unknown rows do not include enough information about the (α
r
	​

,β
r
	​

) splits and pair overlaps to prove that by hand.

Weakest steps

These cuts are logical projections of the exact A/B state law, so their benefit is propagation rather than removal of any genuinely feasible exact-state model.

common_a and common_b must be exact intersection cardinalities. Using relaxed overlap bounds would invalidate the subtracted o
rs
	​

 terms.

The predicted usefulness for high-p rows is structural, not yet computationally verified.

Anti-tightness still depends on H14 being fully reroot-invariant; none of the rectangle cuts depends on H14.