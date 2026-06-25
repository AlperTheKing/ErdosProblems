UPDATE: The p13/e24 clean z8d6 row is now fully closed by fixed-R incidence
SAT: 3888/3888 UNSAT. The p12/e25 clean z8d6 row is also closed: no-ZZ
branch 15680/15680 UNSAT at 1M conflicts, one-ZZ branch 2972/2972 UNSAT.

I added these scalar cuts and regenerated the q14/t2 scalar frontier. Max cap
is still 74 with 51 rows, all U=12 and p+e_R=37. Groups are:

- (z,s1,s2,d)=(2,6,6,0), p=12..17/eR=25..20;
- (3,5,5,1), p=12..18/eR=25..19;
- (4,4,4,2), p=12..21/eR=25..16;
- (5,3,3,3), p=12..21/eR=25..16;
- (6,2,2,4), p=12..21/eR=25..16;
- (8,0,0,6), p=14..21/eR=23..16.

So clean-shadow cap74 core is exhausted, but cap74 remains in the U=12,
p+eR=37 extremal band.

QUESTION: Give a rigorous next lemma or reduction for this U=12, p+e_R=37
cap74 band in q14/t2. Is this exactly the C-tight/reroot side? Can it be
eliminated by a short counting argument using U=12, p+eR=37, local label
constraints, and nonedge-codegree, or should I build a specific finite
verifier? Please give the sharpest hand-checkable invariant and the smallest
finite experiment if a hand proof is not available. End with weakest steps.
