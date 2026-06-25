CONTEXT: Erdős #23, q=15 layer in our finite proof search.  We work with
R-labels that are nonempty subsets of {1,2,3}.  Let n1,n2,n3 be the counts of
singleton, doubleton, triple labels, U=n1+2n2+3n3, p=e(A,B), eR=e(R), and
M=e(A union B,R).  The scalar budget is 16+U+p+eR+M<=139, so cap=139-16-U-p-eR.

VERIFIED SO FAR:
- cap<=53 q=15 is now closed by fixed-label SAT certificates using all paired
  rooted-cut inequalities.
- The certificates added all paired inequalities before solving, not lazily.
- The paired inequalities are, for every W subset R:
  (P1) 2*bd_R(W) <= eR + 55 - U - p + 2*m(W),
       where m(W)=sum_i min(#label-containing-i in W, #label-containing-i outside W).
  (P2) 2*bd_R(W) <= p + eR + 49 - U + g(W)+g(R\W),
       where g(W)=sum_i min(2 + #outside labels containing i, #inside labels containing i).
- Fixed-label SAT also enforces:
  disjoint-label R-edges only; every unavailable color has at least 3 neighbors
  of that color in R; row/column missing degree <=2 in the A-B missing graph F;
  degree/codegree AB/F conditions; triple labels are side-pure.

RECENT VERIFIED CUTS:
- cap53 (7,6,2), (8,5,2), (8,6,1), (9,5,1), (9,6,0), (10,5,0), (11,4,0),
  and residual (10,4,1) all UNSAT by these fixed-label paired cuts.
- First cap54 frontier after this is:
  1. (7,6,2), cap54, eR=44-p, p=15..20.
  2. Mixed later profiles include (7,7,1), (8,5,2), (8,6,1), (9,4,2), etc.
- cap54 (7,5,3), eR=43-p, p=15..20 has also just been closed:
  support orbits (0,0,7;0,0,5;t=3) and (1,3,3;0,2,3;t=3), all UNSAT.

QUESTION: Give a rigorous mathematical argument, not a SAT recipe, that explains
why these paired inequalities kill the cap54 frontier, starting with the exact
profile (n1,n2,n3)=(7,6,2), cap=54, eR=44-p, p=15..20.  Ideally prove a lemma
that covers the whole first cap54 band or a reusable family such as
cap c profiles with small n1 and n3>=2.

REQUIREMENTS:
1. Work from the definitions above only; do not assume unlisted SAT clauses.
2. If you use support shapes, list the necessary shape cases and give a human
   inequality proof for each, based on P1/P2 plus support constraints.
3. If a full proof is not reachable, isolate the smallest missing lemma and
   suggest the next computational certificate that would be most informative.
4. End by attacking your own argument and listing the weakest steps.
