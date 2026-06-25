CONTEXT: Erdős #23 q14/t2 cap74, active row z=8,d=6,p=16,e_R=21,(ZZ,ZD)=(0,21). Verifier now has: exact A/B state law; full local codegrees; checkerboard + 489 rooted lazy cuts; terminal touched-column equality c_d+m_d=6; touched c_d<=4; outside-D visibility; touched c=4 inclusion; full tight-zero reroot scalar p*_z+eR*_z=37; reroot profile D' in {1,2,3,4,6}; reroot singleton balance D'+L'=6 and D'+R'=6; optional D'<=4 where skeleton-safe; tight-pair multiplicity branching.

We closed zero-degree profile (n2,n3,n4,n5)=(5,2,0,1) completely. Now active profile is (5,1,2,0), with t=5 tight zeros and u=4 touched D-columns. Pair-skeleton branching on the 11 isomorphism types closed 9 of 11. The only remaining UNKNOWN types are both non-split (3,3,2,2) tight-footprint skeletons:

D columns are labelled 8,9,10,11 touched; 12,13 untouched. Pair-count vector order is (8,9),(8,10),(8,11),(8,12),(8,13),(9,10),(9,11),(9,12),(9,13),(10,11),(10,12),(10,13),(11,12),(11,13),(12,13).

UNKNOWN A = 3322_non1:
  pair_counts = 0,0,2,0,0,2,0,0,0,1,0,0,0,0,0
  on touched columns: K(8,11)=2, K(9,10)=2, K(10,11)=1.
  degrees: c_T(8)=2,c_T(9)=2,c_T(10)=3,c_T(11)=3.

UNKNOWN B = 3322_non3:
  pair_counts = 0,1,1,0,0,1,2,0,0,0,0,0,0,0,0
  on touched columns: K(8,10)=1,K(8,11)=1,K(9,10)=1,K(9,11)=2.
  degrees: c_T(8)=2,c_T(9)=3,c_T(10)=2,c_T(11)=3.

Both were run with D'<=4 for all tight-zero reroots and stayed UNKNOWN after 600s with 100 workers. The split type and the other non-split type are INFEASIBLE.

QUESTION: Give the next mathematically safe P-free strengthening or branch that targets exactly these two residual pair-skeletons. Prefer a skeleton/reroot/excess lemma over more lazy cuts. State exact CP-SAT constraints. If one residual should be impossible by hand, prove it. If not, propose the smallest next branch parameter.

REQUIREMENTS: Use only the assumptions listed. Flag dependence on cap<74/q<14 frontier closure. Do not suggest fixed A/B-template enumeration. End with weakest steps.
