CONTEXT: Erdős #23 / a(30)=36, q=14/t=2 cap74 branch.

VERIFIED so far:
- q=15 branch closed.
- q=14/t=2 p12/eR25 rows closed.
- q=14/t=2 p13/eR24 rows z2,z3,z4,z5,z6 closed.
- p21/eR16 closed for z4,z5,z6,z8.
- p20/eR17 closed for z4,z5,z6,z8.
- p19/eR18 closed for z8,z6,z4; z5/p19 is currently running fixed-P templates for the final 8 categories.
- Two scalar rows were removed by terminal degree-sum:
  (z,s1,s2,d,p,eR)=(2,6,6,0,17,20) and (3,5,5,1,18,19).

Current cap74 frontier after those VERIFIED cuts, assuming z5/p19 closes:
- p=18,eR=19: z=4,5,6,8.
- p=17,eR=20: z=3,4,5,6,8.
- p=16,eR=21: z=2,3,4,5,6,8.
- p=15,eR=22: z=2,3,4,5,6,8.
- p=14,eR=23: z=2,3,4,5,6,8.

Hypotheses available:
- q=14/t=2, cap=74, U=12, p+eR=37.
- labels are Z,S1,S2,D with U=s1+s2+2d.
- R-edge categories are ZZ,ZS1,ZS2,ZD,S12.
- local domination lower bound 2.
- terminal C-tight normalization: if r notin U_i and d_R(r,U_i)=2, then deg(r)=8.
- triangle-free/maximal codegree rules, A/B rectangle cover, A/R,B/R,R/R codegrees, rooted Phi/Psi cuts.
- Existing solver can check category rows, fixed p-template rows, and p-template+fixedR rows.

STATUS:
Pure category SAT/UNSAT computation is working but can be slow. We need new hand reductions so we do not brute force p18..p14 blindly.

QUESTION:
Give the strongest PROVED structural reductions for the remaining p<=18 cap74 frontier.

Focus especially on:
1. terminal degree-sum contradictions analogous to the two removed rows;
2. scalar/category lower bounds that remove whole rows before SAT;
3. exact slack equations/category restrictions for p18/eR19 rows;
4. which single next row should be attacked after p19 closes, and exactly what categories/constraints to hard-code.

REQUIREMENTS:
- Label every item PROVED / FINITE-CERTIFICATE-NEEDED / CONJECTURED.
- Use only the hypotheses listed above.
- Do not claim a row is closed unless the argument is complete.
- End with one concrete next experiment target and the exact category manifest formula.
