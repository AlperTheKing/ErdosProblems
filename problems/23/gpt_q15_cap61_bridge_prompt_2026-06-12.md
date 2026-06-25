CONTEXT: Erdős problem #23.  For a triangle-free graph G, beta(G)=e(G)-maxcut(G)
and a(n)=max beta(G) over triangle-free n-vertex graphs.  We are trying to prove
the finite target a(30)=36, i.e. no triangle-free 30-vertex graph has beta >= 37.

KNOWN / VERIFIED:
1. BCL high-density and low-density reductions leave the hard medium-density
   window 109 <= e(G) <= 139 for a 30-vertex counterexample.
2. A low-codegree-root route was derived.  In the q=15 branch, after rooting at
   a minimum nonedge-codegree pair xy, the outside set R has |R|=15.  Each
   vertex of R has one of seven support labels relative to three matched
   pairs: singleton labels, doubleton labels, or triple label.
3. Current scalar notation:
   - p = number of forced edges inside the rooted core;
   - e_R = edges inside R;
   - U = n1 + 2 n2 + 3 n3, where n1/n2/n3 count singleton/doubleton/triple
     support labels in R;
   - M = e(A union B, R);
   - edge budget: 16 + U + p + e_R + M <= 139, so cap = 139 - 16 - U - p - e_R.
4. For every q=15 scalar profile up through cap <= 61, we now have verified
   fixed-label SAT UNSAT certificates using all paired rooted-cut inequalities.
   This is not heuristic: the static verifier returns CaDiCaL code 20 for every
   exact support-shape orbit and exact scalar case, with stderr=0.
5. Latest audit after closing cap<=61:
   remaining q=15 scalar jobs = 168.
   First open row is cap=62, p=20, e_R=17, U=24, profiles:
     (n1,n2,n3) = (7,7,1), (8,5,2), (9,3,3), (10,1,4).

STATUS:
The finite q=15 certificate line is alive and keeps proving new UNSAT bands,
but by itself it is becoming a long cap-by-cap enumeration.  I need a
mathematical bridge or a sharper pruning lemma, not just more brute force.

QUESTION:
Find the strongest rigorous hand-checkable lemma you can from the above data
that would either:

A. prove the q=15 branch cannot require cap >= 62, hence finish the q=15 branch
   without continuing raw cap-by-cap enumeration; OR
B. explain how "q=15 cap<=61 UNSAT plus the remaining cap=62+ profiles" plugs
   into a complete proof of a(30)=36; OR
C. if A/B are impossible, identify the exact missing structural obstruction and
   give one concrete next lemma or experiment that could decide it.

REQUIREMENTS:
- Do not assert the theorem is solved unless you give a complete argument.
- Use only facts stated above unless you explicitly mark an additional
  assumption or citation and say how to verify it.
- Be adversarial: point out where this low-codegree/q=15 route may be
  insufficient.
- Prefer inequalities or structural lemmas over instructions to run more SAT.
- End with a short list of the weakest steps in your own answer.
