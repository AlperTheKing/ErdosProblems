CONTEXT: Erdős #23 q=14/t=2 cap74 frontier. We continued after your prior advice.

VERIFIED NEW STATE:
- p=21 layer is fully closed:
  * z8 p21/eR16 closed by 10951 p21 fixed-P templates, category (0,0,0,16,0).
  * z4 p21/eR16 closed by two fixed-R skeletons C8 and C4+C4 across all 10951 p21 templates.
  * z6 p21/eR16 closed directly with forced category (0,0,0,12,4).
  * z5 p21/eR16 closed by 4506 category profiles: 4505 UNSAT after 10k/tail, last (0,0,0,10,6) UNSAT at 1M.
- p=20 layer is fully closed:
  * z8 p20/eR17 closed by p20 fixed-P templates for categories (ZZ,ZD)=(0,17),(1,16).
  * z6 p20/eR17 closed by category split: 4020 total, 4 tails at 1M.
  * z4 p20/eR17 closed by category split: 4491 total, 4 tails at 1M.
  * z5 p20/eR17 closed by category split: 5430 total, 5 tails at 1M.
- Current cap74 frontier is 33 rows, all p<=19:
  p=19/eR=18: z4,z5,z6,z8.
  p=18/eR=19: z3,z4,z5,z6,z8.
  p=17/eR=20: z2,z3,z4,z5,z6,z8.
  p=16/eR=21: z2,z3,z4,z5,z6,z8.
  p=15/eR=22: z2,z3,z4,z5,z6,z8.
  p=14/eR=23: z2,z3,z4,z5,z6,z8.
- Compute policy: max 100 CPU workers, RAM cap ~268GB.

QUESTION: What is the strongest next reduction for the p<=19 frontier?

Please prioritize:
1. Scalar/category-level row eliminations before SAT.
2. Which p=19 row to attack first, and whether no-category/category split/fixed-P is best.
3. Any new defect or capacity lemma that becomes stronger as p decreases and eR increases.
4. Exact C++ verifier constraints for the next row.

REQUIREMENTS:
- Label PROVED / FINITE-CERTIFICATE-NEEDED / CONJECTURED.
- Use only existing q=14/t=2 hypotheses: cap=74, p+e_R=37, local domination 2, terminal C-tight normalization, triangle-free/maximal codegree rules, rooted Phi/Psi cuts.
- End with the single next experiment target and the exact categories or constraints to hard-code.
