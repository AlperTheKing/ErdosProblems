CONTEXT:
We are working on Erdos #23 / a(30)=36.  The current route has two tracks.

TRACK A: low-codegree q-branch.
- q=15 is closed by V123.
- q=14, t=2, cap=74 is now closed.  The scalar audit
  `search23/q14_t2_scalar_audit.cpp` was updated through V332 and filtered to
  cap=74; it returns `cap74_rows=0` (V333).
- In particular, p16/e_R21, p15/e_R22, and p14/e_R23 cap74 layers are all
  recorded closed, including the final z8 p14/e_R23 categories.

TRACK B: direct rooted 30-vertex branch.
For each root degree r=4..9, target UNSAT for:
- G triangle-free and maximal triangle-free on 30 vertices;
- vertex 0 has degree r and fixed neighbourhood {1,...,r};
- every vertex has degree at least r;
- e(G)<=139;
- every cut has at least 37 monochromatic edges (beta>=37 cut condition).

The C++ rooted lazy-cut pilot:
`search23/campaign_rooted_r4_9_e109_139_w100_c20k_20260618_233808`
ran r=4..9, e=109..139 with 100 workers, 20 rounds, and 20k conflicts.
Result: 149/149 INCONCLUSIVE, 0 UNSAT, 0 SAT counterexamples.

STATUS:
Do not treat V333 as a full proof of a(30)=36 unless a bridge from the global
counterexample to the closed q15/q14/t2 branches is complete.  We need the next
mathematical/proof step, not just more compute.

QUESTION:
Please audit the proof dependency tree and answer this sharply:

1. Does closing q=15 and q=14,t=2,cap=74 already eliminate every possible
   global counterexample to a(30)=36?  If yes, state the exact missing bridge
   theorem and its proof outline with hypotheses.

2. If not, what is the smallest remaining branch?  Is it q=14 with t != 2,
   q<=13, a cap<74 reroot dependency, or the direct rooted r=4..9 target?

3. Give the highest-leverage next lemma/certificate.  It must be precise
   enough to implement or prove.  Prefer a structural theorem or small
   skeleton certificate over raising SAT conflict limits.

REQUIREMENTS:
- Be adversarial.  Do not assume a bound or branch closure unless it follows
  from the stated verified items.
- If direct rooted P1 is the right route, propose a sharper branch split than
  the current r,e lazy-cut campaign, because that pilot returned only
  INCONCLUSIVE.
- End with "weakest steps" and the exact facts we must verify in C++/Lean.
