CONTEXT: We are working on Erdős problem #23 / a(30)=36, in the q=14, t=2 low-codegree branch. Please focus only on the finite terminal row below. We need a rigorous structural cut/lemma, not a broad SAT sweep.

ROW: z=5, s1=3, s2=3, d=3, p=13, e_R=24, cap=74.

R has 14 vertices partitioned by C-labels:
- Z: 5 zero-label vertices.
- S1: 3 vertices with label {1}.
- S2: 3 vertices with label {2}.
- D: 3 vertices with label {1,2}.
Thus U1=S1 union D has size 6 and U2=S2 union D has size 6.

Allowed R-edges are only between disjoint labels, so only these category types can occur:
ZZ, ZS1, ZS2, ZD, S1S2.
No edges touch D except from Z.

The current scalar category parameters are:
ZZ, ZS1, ZS2, ZD, S12 with
ZZ + ZS1 + ZS2 + ZD + S12 = e_R = 24.

The A-B graph P=G[A,B] has p=13 and row/column degree sequence (3,2,2,2,2,2) on both A and B. We already enumerated 14 canonical P-templates. For every r in R, define X_r=N_A(r), Y_r=N_B(r), m_r=|X_r|+|Y_r|. Since X_r x Y_r avoids E(P), and P has min degree 2 with only one degree-3 vertex on each side, we proved m_r <= 6 for every r. Because cap=sum m_r=74 over 14 R-vertices, define delta_r=6-m_r and have:

  sum_{r in R} delta_r = 10.

Terminal q-minimal normalization: if r notin U_i and d_R(r,U_i)=2, then deg(r)=8. Hence for any C-tight vertex,

  delta_r = d_R(r) + |label(r)| - 2.

Consequences:
- For z in Z, if d_R(z,U1)=2 or d_R(z,U2)=2, then delta_z=d_R(z)-2.
- For s in S1, C-tight means d_R(s,S2)=2, and then delta_s=d_R(s)-1. Since S1 only connects to Z and S2, this is delta_s = 1 + z(s), where z(s)=d_R(s,Z). Same for S2.
- For zero z, local constraints are d_R(z,U1)=d_R(z,S1)+d_R(z,D) >=2 and d_R(z,U2)=d_R(z,S2)+d_R(z,D) >=2.
- For s in S1, d_R(s,S2)>=2. For s in S2, d_R(s,S1)>=2.
- R/R edge codegree must be 0, R/R nonedge codegree at least 2, including label intersection, A/B intersections, and common R-neighbours.
- For A/B states, every missing A-B cell must be covered by at least two rectangles X_r x Y_r. A/R and B/R nonedge codegrees and rooted Phi/Psi cuts are also imposed in the solver.

WHAT IS VERIFIED ALREADY:
- q=15 is closed.
- q=14/t=2 p=12/eR25 is closed.
- q=14/t=2 p=13/eR24 rows z=2, z=3, z=4 are closed. z=2 used a hand defect-budget reduction plus 14 P-template SAT certificates. z=3 and z=4 used P-template splits.
- Current scalar frontier after those closures has 43 cap74 rows. The next row is exactly this z=5,p=13,eR=24 row. It has 13,585 category profiles before template splitting.
- A generic exact-M terminal triage is currently running over all 13,585 profiles at 10k conflicts with 100 workers. Early completed profiles show many UNSAT plus UNKNOWN; no SAT so far.

QUESTION: Find the strongest rigorous hand reduction for the z=5,p=13,eR=24,cap=74 row. In particular:
1. Derive category-level inequalities using the defect budget and terminal C-tight formula. Can any ranges of (ZZ,ZS1,ZS2,ZD,S12) be eliminated outright?
2. Is there a small analogue of the z2 p13 defect proof that forces contradiction for large ZD, small ZZ, or high S12?
3. Can you identify a narrow residual band and the exact finite certificate variables/cuts needed for it?
4. If you propose a lemma, give a complete proof with all edge cases. If no proof, say precisely what finite obstruction remains.

REQUIREMENTS:
- Be adversarial. Do not assume the SAT encoding is correct.
- Use only the hypotheses listed above.
- Label every claim as PROVED, CONJECTURED, or FINITE-CERTIFICATE-NEEDED.
- End by listing the weakest steps in your own answer and which parts should be checked by a C++ verifier.
