CONTEXT: Erdős #23 q=14/t=2 cap74 frontier. We just closed the first p>=14 finite row you suggested.

VERIFIED NEW STATE:
- Row closed: (z,s1,s2,d,p,e_R,cap)=(8,0,0,6,21,16,74).
- Local domination forces the only R category: (ZZ,ZS1,ZS2,ZD,S12)=(0,0,0,16,0), every zero has exactly two D-neighbours.
- Enumerated canonical p=21 A-B templates: 10951.
- Fixed-P exact-M terminal-degree/R-degree/RR-codegree solver checked all templates at 10k conflicts: UNSAT=10951, SAT=0, UNKNOWN=0.
- Current cap74 frontier now 40 rows:
  z4 p=21..14/e_R=16..23; z5 p=21..14/e_R=16..23; z6 p=21..14/e_R=16..23; z8 p=20..14/e_R=17..23; plus z3 p=18..14/e_R=19..23; z2 p=17..14/e_R=20..23.
- Generic p14 z8 and z6 tails stalled in high-ZD bands, so fixed-P/template certificates seem better than raw scalar SAT.

QUESTION: Choose the next single row/subrow to attack that should maximize probability of closure per compute minute. Give a rigorous reduction and exact C++ verifier constraints.

Please prioritize:
1. Any scalar/category-level row eliminations analogous to the z8 p21 row.
2. If finite-certificate-needed, specify exact row, forced R-category/skeleton restrictions, A-B template family p, and constraints to hard-code before SAT.
3. Whether to proceed descending in z8 p=20,19,... or attack z6/z5/z4 p=21 first.

REQUIREMENTS:
- Label each claim PROVED / FINITE-CERTIFICATE-NEEDED / CONJECTURED.
- Use only the q=14/t=2 hypotheses already in this thread: cap=74, p+e_R=37 for frontier, local domination threshold 2, terminal C-tight normalization, triangle-free/maximal codegree rules, rooted Phi/Psi cuts.
- End with the single next experiment command-level target: (z,s1,s2,d,p,e_R), category restrictions, template p, and verifier additions.
