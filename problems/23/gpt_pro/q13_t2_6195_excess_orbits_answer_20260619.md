ChatGPT said:I’ll target a cut that propagates directly from the fixed excess vector before any complete count assignment exists, then audit it against the exact quotient semantics.I’ll focus on a static master-level obstruction from the fixed skeleton and excess budget, avoiding any new timeout-driven or candidate-dependent layer.The quotient itself looks sound; the remaining issue is weak early propagation from bilinear cross-shore coupling. I’ll look for projections using fixed column totals before products are fixed.Thought for 23m 43sStrongest next move: project every state onto the forced C6=S2∪D13C_6=S2\cup D13C6​=S2∪D13
This projection alone closes all 18 excess-two representatives.
Let
X=S2={x0,x1,x2}={0,1,2},H=D13={h0,h1,h2}={8,9,10}.X=S2=\{x_0,x_1,x_2\}=\{0,1,2\},
\qquad
H=D13=\{h_0,h_1,h_2\}=\{8,9,10\}.X=S2={x0​,x1​,x2​}={0,1,2},H=D13={h0​,h1​,h2​}={8,9,10}.
For mask 0xfd8a30, the X−HX-HX−H block is
R[X,H]=K3,3−{x0h0,x1h1,x2h2}.R[X,H]=K_{3,3}-\{x_0h_0,x_1h_1,x_2h_2\}.R[X,H]=K3,3​−{x0​h0​,x1​h1​,x2​h2​}.
Thus R[X∪H]≅C6R[X\cup H]\cong C_6R[X∪H]≅C6​.
No terminal-reroot or terminal-touch equality is used below.
1. Projection lemma
For every legal A-state or B-state III, define
π(I)=I∩(X∪H).\pi(I)=I\cap(X\cup H).π(I)=I∩(X∪H).
Because III is independent in RRR, π(I)\pi(I)π(I) is an independent subset of K3,3−M3K_{3,3}-M_3K3,3​−M3​.
The possible projections are exactly:
P=2X∪2H∪{{x0,h0},{x1,h1},{x2,h2}},\mathcal P
=
2^X\cup2^H\cup
\bigl\{\{x_0,h_0\},\{x_1,h_1\},\{x_2,h_2\}\bigr\},P=2X∪2H∪{{x0​,h0​},{x1​,h1​},{x2​,h2​}},
with the empty set counted only once. Hence
∣P∣=8+8−1+3=18.|\mathcal P|=8+8-1+3=18.∣P∣=8+8−1+3=18.
Indeed, any mixed independent projection containing both an XXX-vertex and an HHH-vertex must be one of the three missing-matching pairs. If it contains xi,hix_i,h_ixi​,hi​, it cannot contain any further XXX- or HHH-vertex.
This is already a large reduction from the 648 full states.
2. The three missing matching pairs require two state witnesses
Put
Ωi={xi,hi}.\Omega_i=\{x_i,h_i\}.Ωi​={xi​,hi​}.
The pair xi,hix_i,h_ixi​,hi​ is a nonedge in RRR. Moreover:


L(xi)={2}L(x_i)=\{2\}L(xi​)={2} and L(hi)={1,3}L(h_i)=\{1,3\}L(hi​)={1,3} are disjoint, so they have no common neighbour in CCC;


NR(xi)=H∖{hi}N_R(x_i)=H\setminus\{h_i\}NR​(xi​)=H∖{hi​};


NR(hi)=X∖{xi}N_R(h_i)=X\setminus\{x_i\}NR​(hi​)=X∖{xi​};


hence NR(xi)∩NR(hi)=∅N_R(x_i)\cap N_R(h_i)=\varnothingNR​(xi​)∩NR​(hi​)=∅;


vertices of RRR have no adjacency to the two original roots.


Therefore all common neighbours of xi,hix_i,h_ixi​,hi​ lie in A∪BA\cup BA∪B. The R/R nonedge-codegree condition gives
AΩi+BΩi≥2,(1)\boxed{
A_{\Omega_i}+B_{\Omega_i}\ge2,
}
\tag{1}AΩi​​+BΩi​​≥2,​(1)
where AΩiA_{\Omega_i}AΩi​​ and BΩiB_{\Omega_i}BΩi​​ are the numbers of A- and B-states whose X∪HX\cup HX∪H projection is Ωi\Omega_iΩi​.
This is exact: Ωi\Omega_iΩi​ is the only independent X∪HX\cup HX∪H projection containing both xi,hix_i,h_ixi​,hi​.
3. Projected P-edge upper bound
For S∈PS\in\mathcal PS∈P, introduce projected multiplicities
aS=#{a∈A:π(Xa)=S},bS=#{b∈B:π(Yb)=S}.a_S=\#\{a\in A:\pi(X_a)=S\},
\qquad
b_S=\#\{b\in B:\pi(Y_b)=S\}.aS​=#{a∈A:π(Xa​)=S},bS​=#{b∈B:π(Yb​)=S}.
Then
∑S∈PaS=∑S∈PbS=6.(2)\sum_{S\in\mathcal P}a_S
=
\sum_{S\in\mathcal P}b_S
=6.
\tag{2}S∈P∑​aS​=S∈P∑​bS​=6.(2)
The six projected column sums are fixed:
∑S∋v(aS+bS)=mv,v∈X∪H.(3)\sum_{S\ni v}(a_S+b_S)=m_v,
\qquad v\in X\cup H.
\tag{3}S∋v∑​(aS​+bS​)=mv​,v∈X∪H.(3)
Define
pXH=∑S,T∈PS∩T=∅aSbT.(4)p_{XH}
=
\sum_{\substack{S,T\in\mathcal P\\S\cap T=\varnothing}}
a_Sb_T.
\tag{4}pXH​=S,T∈PS∩T=∅​∑​aS​bT​.(4)
Every actual A/B edge has disjoint full states. Consequently its X∪HX\cup HX∪H projections are also disjoint. Hence
p≤pXH.(5)\boxed{p\le p_{XH}.}
\tag{5}p≤pXH​.​(5)
Projection-disjoint pairs may still intersect in Y∪Z∪TY\cup Z\cup TY∪Z∪T, so (5) is only a necessary relaxation. That is exactly what makes it safe.
4. Exact finite certificate
For the excess-two branch,
(mx0,mx1,mx2,mh0,mh1,mh2)=(5,5,5,4,4,4)+eXH,(m_{x_0},m_{x_1},m_{x_2},m_{h_0},m_{h_1},m_{h_2})
=
(5,5,5,4,4,4)+e_{XH},(mx0​​,mx1​​,mx2​​,mh0​​,mh1​​,mh2​​)=(5,5,5,4,4,4)+eXH​,
where eXH≥0e_{XH}\ge0eXH​≥0 and
∑eXH≤2.\sum e_{XH}\le2.∑eXH​≤2.
I exhaustively optimized (4) subject only to (1)–(3) over the 18 projection types. The resulting upper bounds for the listed representatives, in their displayed order, are:
Representative numbersMaximum pXHp_{XH}pXH​1, 2, 5, 7, 8, 9, 11, 12, 13, 14, 16, 17213, 6, 102041915projection system infeasible1818
Thus every representative satisfies
p≤pXH≤21,p\le p_{XH}\le21,p≤pXH​≤21,
contradicting p=25p=25p=25.
Therefore:
All 18 unresolved (p,M)=(25,60) excess-two orbits are infeasible.\boxed{\text{All 18 unresolved }(p,M)=(25,60)\text{ excess-two orbits are infeasible.}}All 18 unresolved (p,M)=(25,60) excess-two orbits are infeasible.​
The fifteenth vector,
0,0,1,0,0,0,0,0,0,1,0,0,0
is already impossible before imposing ppp. Its excess lies on the adjacent pair x2,h1x_2,h_1x2​,h1​.
Stronger universal version
The same 18-type enumeration over all six-coordinate projected excess vectors satisfying
eXH≥0,∑eXH≤3e_{XH}\ge0,\qquad \sum e_{XH}\le3eXH​≥0,∑eXH​≤3
still gives
pXH≤21.(6)\boxed{p_{XH}\le21.}
\tag{6}pXH​≤21.​(6)
There are only
∑s=03(s+55)=84\sum_{s=0}^{3}\binom{s+5}{5}=84s=0∑3​(5s+5​)=84
such projected excess signatures.
Consequently the same certificate also closes, for this fixed skeleton:
(p,M)=(26,60)(p,M)=(26,60)(p,M)=(26,60)
and
(p,M)=(25,61),(p,M)=(25,61),(p,M)=(25,61),
because both require p>21p>21p>21, while M=61M=61M=61 gives total excess three and therefore projected excess at most three.
So the C6C_6C6​-projection certificate closes all three previously remaining canonical high-MMM cases.
5. Small CP-SAT master
This can be added independently of the 648 full-state variables, or linked to them as an aggregation layer.
Use 18 A-counts and 18 B-counts:
C++std::vector<IntVar> proj_a(18);std::vector<IntVar> proj_b(18);for (int s = 0; s < 18; ++s) {  proj_a[s] = model.NewIntVar(Domain(0, 6));  proj_b[s] = model.NewIntVar(Domain(0, 6));}model.AddEquality(LinearExpr::Sum(proj_a), 6);model.AddEquality(LinearExpr::Sum(proj_b), 6);
For each of the six vertices v∈X∪Hv\in X\cup Hv∈X∪H:
C++LinearExpr column_sum;for (int s = 0; s < 18; ++s) {  if (projection_mask[s] & (1 << v_local)) {    column_sum += proj_a[s];    column_sum += proj_b[s];  }}model.AddEquality(column_sum, exact_m[v_global]);
For the three missing-matching projection types:
C++for (int i = 0; i < 3; ++i) {  const int omega = matched_pair_projection_index[i];  model.AddGreaterOrEqual(      proj_a[omega] + proj_b[omega],      2);}
Only 18 products are necessary. Define the number of B-projections disjoint from each A-projection:
C++std::vector<IntVar> disjoint_b_count(18);std::vector<IntVar> projected_edges_from_type(18);for (int s = 0; s < 18; ++s) {  disjoint_b_count[s] =      model.NewIntVar(Domain(0, 6));  LinearExpr rhs;  for (int t = 0; t < 18; ++t) {    if ((projection_mask[s] & projection_mask[t]) == 0) {      rhs += proj_b[t];    }  }  model.AddEquality(disjoint_b_count[s], rhs);  projected_edges_from_type[s] =      model.NewIntVar(Domain(0, 36));  model.AddMultiplicationEquality(      projected_edges_from_type[s],      {proj_a[s], disjoint_b_count[s]});}IntVar projected_p =    model.NewIntVar(Domain(0, 36));model.AddEquality(    projected_p,    LinearExpr::Sum(projected_edges_from_type));
The necessary cut is
C++model.AddGreaterOrEqual(projected_p, exact_p);
For the present rows, the tiny projected model proves instead
projected_p <= 21,
so it closes before any full-state candidate is generated.
Linking it to the existing 648-state master
For each full legal state III, precompute its projection index
projection_index[I] = index of I ∩ (X ∪ H).
Then add:
C++for (int s = 0; s < 18; ++s) {  LinearExpr full_a;  LinearExpr full_b;  for (int I = 0; I < num_legal_states; ++I) {    if (projection_index[I] == s) {      full_a += A_count[I];      full_b += B_count[I];    }  }  model.AddEquality(proj_a[s], full_a);  model.AddEquality(proj_b[s], full_b);}
The projected layer then propagates without waiting for a complete 648-state count candidate.
6. Independent exhaustive checker
A proof checker does not need CP-SAT.
There are exactly
(18+6−16)=100,947\binom{18+6-1}{6}=100{,}947(618+6−1​)=100,947
six-element multisets of the 18 projection types for one shore.
A deterministic checker can:


Enumerate all 100,947 A-multisets.


Store each by its six projected column sums.


Record its three Ωi\Omega_iΩi​-multiplicities.


For target mXHm_{XH}mXH​, retrieve only B-multisets with complementary column sums.


Require
aΩi+bΩi≥2a_{\Omega_i}+b_{\Omega_i}\ge2aΩi​​+bΩi​​≥2
for all iii.


Compute
pXH=∑S∩T=∅aSbT.p_{XH}
=
\sum_{S\cap T=\varnothing}a_Sb_T.pXH​=S∩T=∅∑​aS​bT​.


Return the maximum.


This is a complete finite certificate over a relaxation of the full model. It neither enumerates a fixed A/B P-template nor uses the remaining seven RRR-columns.
7. Why this succeeds where the prior cuts did not
The rectangle and mixed-codegree projections work with individual RRR-columns or low-order overlaps. They do not exploit the following simultaneous structure:


X∪HX\cup HX∪H is a six-cycle;


every state projection is one of only 18 possibilities;


the three opposite pairs Ωi\Omega_iΩi​ must each occur at least twice among the twelve states;


the six projected columns already have total multiplicity at least 272727;


an A/B edge requires the two entire C6C_6C6​ projections to be disjoint.


Those four facts force at least fifteen of the 36 cross pairs to intersect already inside X∪HX\cup HX∪H. Hence at most 21 can remain candidates for P-edges, before examining Y,Z,TY,Z,TY,Z,T.
The full state-count solver was attempting to discover this through 648-state products and codegree implications. The 18-type projection exposes it directly.
Weakest steps


The numerical bound pXH≤21p_{XH}\le21pXH​≤21 is an exact finite-enumeration result rather than a short symbolic inequality. It should be accepted proof-grade only after checking the small independent enumerator or a proof-producing PB encoding.


The argument uses the standard rooted-partition fact that vertices of RRR are adjacent to neither original root, and that each label is the exact CCC-neighbourhood mask.


The stated index matching
(x0,h0)=(0,8),(x1,h1)=(1,9),(x2,h2)=(2,10)(x_0,h_0)=(0,8),\quad
(x_1,h_1)=(1,9),\quad
(x_2,h_2)=(2,10)(x0​,h0​)=(0,8),(x1​,h1​)=(1,9),(x2​,h2​)=(2,10)
depends on the given canonical mask’s allowed-edge bit order. The checker should derive the three missing matching edges directly from the fixed RRR-skeleton rather than hard-code them.

Sources