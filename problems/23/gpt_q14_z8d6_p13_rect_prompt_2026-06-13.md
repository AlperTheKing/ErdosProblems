CONTEXT: Erdős problem #23 / a(30)=36 proof attempt, q=14,t=2 branch.
q=15 is closed by the local shadow lemma. In q14/t2 the remaining clean
high-cap obstruction has labels z=8 zero-label R-vertices and d=6
doubleton-label R-vertices (s1=s2=0). The hardest cap74 rows are
(p,e_R)=(13,24) and (12,25).

For p=13,e_R=24, clean shadow forces the R graph to be bipartite Z-D with
each of the 8 zero vertices adjacent to exactly 3 of the 6 D vertices, no
Z-Z edges. I enumerated zero/D isomorphism classes: 3888 canonical R
matrices. Every one passes the fixed paired rooted-cut scalar test with
minimum margin 4, so paired cuts alone do not reduce R.

A fixed-R incidence SAT solver using the rectangle condition
rho(a,b)=|{r: a-r and b-r}|, rho!=1 for all 36 A/B cells, exactly p
zero-rho cells, plus all remaining A-A, B-B, A-R, B-R nonedge-codegree
constraints is expensive: sample 200 R graphs at 20k conflicts gives
36 UNSAT, 164 UNKNOWN, no SAT; 50 graphs at 200k gives 11 UNSAT,
39 UNKNOWN, no SAT. Exact rooted cuts are checked lazily; most UNKNOWNs
hit conflicts before reaching many rooted cuts.

STATUS: Verified facts: q15 closed; q14/t2 cap<=43 closed by exact
fixed-label batches; p13/e24 z8d6 R quotient = 3888, paired_ok=3888
margin=4. Failed: D-only rooted cuts and slab cuts are not enough / too
heavy as static CNF. Need a mathematical lemma, not broad cap sweeping.

QUESTION: For the p=13,e_R=24 clean z8d6 case, can you find a rigorous
hand lemma that combines the rectangle two-cover condition with the 8x6
row-sum-3 R structure to rule out all configurations, or at least derive
a much smaller finite obstruction than 3888 R graphs? Please focus on a
statement I can verify computationally/Lean later. If no proof, give the
sharpest invariant or branching lemma. End by listing weakest steps.
