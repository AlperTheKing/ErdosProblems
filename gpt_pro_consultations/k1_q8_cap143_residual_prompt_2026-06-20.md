CONTEXT:

We are proving the finite Step-1 theorem for Erdos Problem #23:

  a(30)=36, equivalently no 30-vertex triangle-free graph has
  beta(G)=e(G)-MaxCut(G) >= 37.

Do not try to prove the full Erdos #23 bridge; this is only the finite
30-vertex theorem.

Verified current global frontier:

1. By a uniform blow-up transfer of the published Balogh--Clemen--Lidicky
   density theorem, any 30-vertex counterexample must have

      112 <= e(G) <= 143.

   In particular, edge counts e<=111 and e>=144 are closed, conditional only
   on accepting the published BCL theorem.

2. The old rooted e109..139 campaign is NOT a certificate: it is
   149/149 INCONCLUSIVE.

3. The old q13/r0=8/t=2/a6b7 artifacts are invalid for n=30 because
   2+k+na+nb+q = 31.

4. A new conservative q<=13 low-codegree cap143-minus-cap139 shape audit had
   61 coarse shapes.  A generic scalar profile prefilter reduced all 61 to
   only six scalar-surviving shapes.  The two largest coarse blocks vanish:

      r0=8,t=2,q=5: 10/10 shapes, 0 scalar profiles
      r0=9,t=3,q=6:  8/8 shapes, 0 scalar profiles

5. The only new cap143 scalar-surviving shapes are:

      r0=8, k=t=1, q=8,
      (a,b)=(7,12),(8,11),(9,10),(10,9),(11,8),(12,7).

   Here x,y are the rooted nonedge, C={c} is their unique common neighbour,
   A=N(x)\{c}, B=N(y)\{c}, and R has q=8 vertices.
   The minimum degree parameter is r0=8.  The rooted nonedge codegree is k=t=1.

6. For each of the six (a,b) shapes, the generic scalar prefilter leaves exactly
   3 label profiles and 831 scalar rows, for 18 profiles and 4986 rows total.
   The only surviving R-label profiles are:

      (c0,c1)=(0,8), (1,7), (2,6),

   where c1 is the number of R-vertices adjacent to c, and c0 is the number
   not adjacent to c.

Artifacts:

  search23/lowcodegree_scalar_prefilter.cpp
  search23/lowcodegree_scalar_cap143_minus_cap139_summary.tsv
  search23/lowcodegree_scalar_r8_t1_q8_cap143_survivor_rows.tsv

Verified branch structure for k=1:

- R-labels are 0 or 1, according as an R-vertex is adjacent to c.
- Any two label-1 R-vertices are nonadjacent, otherwise they form a triangle
  through c.
- R-edges may only involve the c0 zero-label vertices.  Since c0<=2, the R
  skeleton is tiny.
- If z is a zero-label R-vertex, local domination gives at least one R-neighbour
  among the label-1 vertices.
- Every A vertex has at least one B-neighbour, and every B vertex has at least
  one A-neighbour, by the root-opposite nonedge codegree condition.
- More strongly, minimum degree 8 gives:

      for a in A: 1 + d_B(a) + d_R(a) >= 8,
      for b in B: 1 + d_A(b) + d_R(b) >= 8.

- For r in R:

      label_size(r) + d_R(r) + m_r >= 8,

  where m_r is its A/B incidence count.

- A/B edge law in this k=1 branch:

      a b is an edge iff N_R(a) cap N_R(b) = empty.

  If the intersection is nonempty, ab is a nonedge with at least one common
  R-neighbour.  Intersection size 1 is allowed because t=1.

UNSAFE / DO NOT USE:

- Do not use the previous "terminal-touch equality" or any claim that rerooting
  at a C-tight pair forces terminal neighbours to have degree 8.  GPT Pro
  already found that inference unsafe.  The safe replacement is only the
  H14 anti-tightness inequality in contexts where H14 has truly been proved.
  For this k=1 residual, please avoid relying on unverified reroot closures.

QUESTION:

Find the shortest rigorous next path for closing this entire k=1,q=8 residual.

I need one of:

1. A hand structural contradiction proving no such 30-vertex triangle-free
   graph can have beta>=37, using only the verified constraints above.

2. A small exact finite certificate architecture for this branch that avoids
   broad rooted SAT.  Ideally exploit c0<=2 and the state-count quotient.
   Please specify exact variables and constraints, including how to enforce
   beta(G)>=37 / all cuts, and how to independently check the certificate.

3. A stronger scalar or cut lemma that reduces the 4986 scalar rows further.

Be adversarial.  If a proposed proof step depends on an unproved global
reroot closure, flag it.  End by listing the weakest assumptions in your answer.
