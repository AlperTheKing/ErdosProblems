Your previous answer rendered as only the single letter "I", so I cannot use it. Please answer fully.

CONTEXT: Erdős problem #23.  For a triangle-free graph G, beta(G)=e(G)-maxcut(G), and a(n)=max beta(G) over triangle-free n-vertex graphs.  We are trying to prove the finite target a(30)=36, i.e. no triangle-free 30-vertex graph has beta >= 37.

VERIFIED COMPUTATIONAL STATE:
- BCL high-density and low-density reductions leave a hard medium-density window 109 <= e(G) <= 139 for a 30-vertex counterexample.
- In the low-codegree-root q=15 branch, we use scalar parameters p, e_R, U=n1+2 n2+3 n3, and M=e(A union B,R), with edge budget 16+U+p+e_R+M <= 139.
- Static fixed-label SAT with all paired rooted-cut inequalities has now verified UNSAT for all exact support-shape orbits through the following q=15 frontier:
  - all cap <= 62 closed;
  - cap=63 rows closed for:
    (8,6,1)/(9,4,2)/(10,2,3), e_R=37-p;
    (9,5,1)/(10,3,2)/(11,1,3), e_R=38-p;
    (9,6,0)/(10,4,1)/(11,2,2)/(12,0,3), e_R=39-p.
- Latest audit after those cuts: 108 q=15 scalar jobs remain. First open row is cap=63, p=20, e_R=20, U=20, profiles (10,5,0), (11,3,1), (12,1,2).

STATUS: This finite certificate line is still producing verified UNSAT bands, but it is not yet a general proof.  I need a rigorous mathematical bridge or a sharper pruning lemma.

QUESTION: Give the strongest hand-checkable lemma or proof plan you can that would either:
A. prove that the q=15 branch cannot require the remaining cap>=63 rows, finishing q=15 without raw cap-by-cap enumeration; or
B. explain exactly how these q=15 finite certificates plug into a complete proof of a(30)=36; or
C. if A/B are not currently justified, identify the exact missing structural obstruction and one concrete next lemma/experiment that decides it.

REQUIREMENTS:
- Do not assert a(30)=36 is solved unless you give a complete proof.
- Use only facts stated above unless clearly marked as an extra assumption.
- Be adversarial: point out why the current q=15 route may be insufficient.
- Prefer inequalities/structural lemmas over "run more SAT".
- End with weakest steps in your own answer.
