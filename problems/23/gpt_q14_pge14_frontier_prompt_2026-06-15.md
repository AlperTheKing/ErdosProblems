CONTEXT: We are working on Erdős problem #23 / a(30)=36, in the q=14, t=2 low-codegree branch. Please focus only on the remaining cap74 frontier below. We need a rigorous structural cut or a sharply reduced finite certificate, not a broad enumeration.

GLOBAL SETUP:
- There are two C-vertices, so R has 14 vertices labelled by subsets of {1,2}.
- Let z = number of zero-label vertices Z.
- Let s1 = number of singleton {1} vertices S1.
- Let s2 = number of singleton {2} vertices S2.
- Let d = number of doubleton {1,2} vertices D.
- U = s1 + s2 + 2d = total C-label incidence.
- p = e(A,B).
- e_R = e(R).
- cap = sum_{r in R} (|X_r|+|Y_r|) = 123 - p - e_R - U.
- We are on cap=74 and p+e_R=37.

VERIFIED CLOSED:
- q=15 is closed.
- q=14/t=2 p=12/e_R=25 cap74 rows are closed.
- q=14/t=2 p=13/e_R=24 rows z2,z3,z4,z5,z6 are closed by finite certificates.
- The z5 p13 proof used the matching lemma: because |S1|=|S2|=3 and each singleton sees at least two opposite singletons, missing S1-S2 pairs form a matching; zero rectangles P_z x Q_z must lie inside that matching.

CURRENT FRONTIER AFTER V218:
All remaining cap74 rows have p>=14. The exact scalar frontier is:

1. (z,s1,s2,d)=(2,6,6,0): 4 rows, p=14..17, e_R=23..20.
2. (3,5,5,1): 5 rows, p=14..18, e_R=23..19.
3. (4,4,4,2): 8 rows, p=14..21, e_R=23..16.
4. (5,3,3,3): 8 rows, p=14..21, e_R=23..16.
5. (6,2,2,4): 8 rows, p=14..21, e_R=23..16.
6. (8,0,0,6): 8 rows, p=14..21, e_R=23..16.

LOCAL HYPOTHESES / CONSTRAINTS:
- R-edges occur only between disjoint C-labels:
  allowed types: ZZ, ZS1, ZS2, ZD, S1S2. No edges touching D except from Z; no same-label or intersecting-label edge.
- U1=S1 union D has size at least 6; U2=S2 union D has size at least 6.
- For every zero z, d_R(z,U1)>=2 and d_R(z,U2)>=2. More generally the q-minimal local domination constraints are imposed.
- For s in S1, d_R(s,S2)>=2 when S2 is nonempty; similarly for S2.
- Terminal q-minimal normalization: if r notin U_i and d_R(r,U_i)=2, then deg(r)=8.
- For any C-tight vertex, delta_r = 6 - m_r = d_R(r)+|label(r)|-2, whenever the p>=14 situation still gives m_r<=6 or an appropriate defect baseline. Be careful: the p=13 proof of m_r<=6 used the (3,2,2,2,2,2) A-B degree sequence; for p>=14 this may need a different baseline.
- Triangle-freeness and maximality impose:
  * every R-edge has full common-neighbour count 0;
  * every R-nonedge has full common-neighbour count at least 2;
  * every missing A-B cell is covered by at least two rectangles X_r x Y_r;
  * A/R and B/R nonedge-codegrees at least 2;
  * rooted Phi/Psi cuts over all W subset R.

KNOWN COMPUTATIONAL ENGINE:
- Generic exact-M terminal solver can triage a fixed scalar row/category, but p>=14 has many A-B templates.
- For p=13 there were exactly 14 canonical A-B templates. For p>=14 we need either a structural cut, or a finite certificate over canonical A-B degree/template families.

QUESTION:
Find the strongest rigorous next reduction for the p>=14 cap74 frontier.

Please attack in this order:
1. Is there a scalar/category-level inequality that eliminates all p>=14 rows, or at least one whole row group?
2. Can the p=13 defect baseline be replaced by a p>=14 defect/overlap baseline using p+e_R=37 and cap=74?
3. For each group, what is the right small finite certificate parameterization? For example, A-B graph degree sequences/templates, missing S1-S2 structure, zero/D skeleton, or R-skeleton cuts.
4. Which single remaining row is most likely to close first computationally, and what exact constraints should be hard-coded before SAT?

REQUIREMENTS:
- Mark claims PROVED / CONJECTURED / FINITE-CERTIFICATE-NEEDED.
- Use only the hypotheses listed here.
- If a lemma depends on a new baseline like m_r<=k, prove it or mark it as finite-certificate-needed.
- End with the weakest steps and exactly what C++ verifier/checker should test first.
