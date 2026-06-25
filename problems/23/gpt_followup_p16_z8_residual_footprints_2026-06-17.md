CONTEXT: Erdős #23 q14/t2 cap74, active row z=8,d=6,p=16,e_R=21,(ZZ,ZD)=(0,21). Z has 8 zero vertices, D has 6 doubleton vertices. We already impose full local codegrees, exact A/B state law, checkerboard beta cuts + 489 rooted lazy cuts, terminal reroot touched-column equalities, Dprime != 5 reroot profile cut, outside-D visibility, touched c=4 inclusion propagation, and full tight-zero reroot scalar p*_z+eR*_z=37.

The current remaining branch is zero D-degree profile (n2,n3,n4,n5)=(5,2,0,1), touched footprint u=4. Tight zero count t=5, two untouched D-columns. We branched by tight-footprint column vector g_d=|N_T(d)|. Three vectors are INFEASIBLE quickly:
- counts n0,n1,n2,n3,n4 = (2,2,0,0,2), i.e. sorted touched vector (4,4,1,1)
- (2,1,1,1,1), i.e. (4,3,2,1)
- (2,0,3,0,1), i.e. (4,2,2,2)
Two vectors remain UNKNOWN:
- (2,1,0,3,0), i.e. sorted touched vector (3,3,3,1). This stayed UNKNOWN after 600s with 100 CP-SAT workers.
- (2,0,2,2,0), i.e. sorted touched vector (3,3,2,2). This stayed UNKNOWN after 180s.

Known structural facts in this branch:
- each touched D-column d satisfies c_d + m_d = 6 and c_d <= 4.
- untouched D-columns carry all D-excess; for t=5 the lower excess is >=5.
- one zero has D-degree 5; two zeros have D-degree 3; five zeros have D-degree 2.
- tight zeros z (degree-2 to D) satisfy m_z=6 and p*_z+eR*_z=37 under reroot at (c,z).
- for tight zero z with pair {a,b}=N_D(z), rerooted d' != 5, encoded as D' in {1,2,3,4,6}.

QUESTION: Give the next mathematically safe P-free strengthening that targets specifically the residual tight-footprint vectors (3,3,3,1) and (3,3,2,2). Prefer a scalar/skeleton/reroot lemma or a small branch parameter, not fixed A/B-template enumeration. State exact constraints that can be encoded in CP-SAT. Also say if one of these two footprint vectors should be impossible by hand.

REQUIREMENTS: Be rigorous. Only use the assumptions listed. Flag any step that relies on the cap<74/q<14 frontier closure. End with weakest steps.
