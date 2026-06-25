CONTEXT

We are proving the finite theorem H1 for Erdős #23:

No triangle-free graph G on 30 vertices has beta(G)=e(G)-MaxCut(G) >= 37.

Do not try to prove full Erdős #23; this is only the n=30 finite theorem.

Verified current state:

1. BCL density ranges transfer to n=30 by uniform blow-up.
   Hence edge counts e<=111 and e>=144 are excluded, conditional on accepting
   the published BCL density theorem. The remaining edge window is e=112..143.

2. The earlier direct rooted campaign for r=4..9, e=109..139 is NOT a proof:
   its raw summary is 149/149 INCONCLUSIVE.

3. High-q low-codegree frontier:
   - q=15 closed.
   - q=14, T=2 closed.
   - q=14, T=3 closed.

4. q=13, K=3, T=3 closed for visible valid branches:
   - r0=9, A=B=6 closed.
   - r0=8, (A,B)=(5,7),(6,6),(7,5) closed.

5. The previously attacked q=13, K=3, T=2, A=6, B=7 branch is invalid for
   n=30 because 2+K+A+B+q = 2+3+6+7+13 = 31.
   All q13_t2_r8_a6b7 solver outputs are diagnostic only.

6. The experimental terminal-touch / terminal_closure equalities are rejected.
   Do not use:
     C-tight r => D(r)=8
     terminal neighbour touched by C-tight r => D(s)=8
   GPT Pro previously found this mathematically unjustified.

Allowed safe reroot cut:

For r not in U_i,

  D(r)+|U_i|+d_R(r,U_i) >= 17,

where D(r)=alpha_r+beta_r+d_R(r)+|L(r)|. This is conditional on the closed
q14/T=2 degree-(8,8) reroot branch. It is an anti-tightness inequality, not a
degree equality.

CURRENT FRONTIER

After fixing the vertex-count error, the valid q=13,K=3,T=2,r0=8 cases have
A+B=12, namely:

  (A,B)=(5,7),(6,6),(7,5).

I patched the scalar prefilter to accept edge cap 143 and ran:

  q13_t3_r9_scalar_prefilter.exe 8 2 5 7 143
  q13_t3_r9_scalar_prefilter.exe 8 2 6 6 143
  q13_t3_r9_scalar_prefilter.exe 8 2 7 5 143

The conservative scalar prefilter reports:

  (5,7): profiles_survive=1427, rows_survive=576607
  (6,6): profiles_survive=1427, rows_survive=556394
  (7,5): profiles_survive=1427, rows_survive=493254

So the valid T=2 frontier is too large for row-by-row CP-SAT. We need a
structural compression or a much sharper scalar/profile filter.

Existing exact-state verifier architecture:

- R label profiles are counts c_0..c_7 over subsets of {1,2,3}.
- R edges only allowed between disjoint labels.
- Local domination: if r misses colour i, then d_R(r,U_i) >= T.
- Here K=3, q=13, T=2, r0=8, N=30, and A+B=12.
- A/B state variables X_a,Y_b subset R.
- Exact A/B law in the verifier:
    |X_a cap Y_b|=0 iff A-B edge,
    |X_a cap Y_b|=1 forbidden,
    |X_a cap Y_b|>=2 means A-B nonedge.
- Full local codegrees are encoded: R/R, A/R, B/R, A/A, B/B.
- Rooted Phi/Psi cuts can be imposed.
- State-count quotient verifier exists and is sound when typewise constraints
  are imposed. It was effective only for a special profile 6195.
- Defect-block projection cuts, class-Psi cuts, isolated-support cuts,
  rectangle/global projections exist but were targeted to the invalid
  a6b7 universe or one profile family.

WHAT I NEED

Find the next rigorous, high-leverage way to shrink or close the valid
q=13,K=3,T=2,r0=8,A+B=12 frontier.

Please give concrete structural lemmas or exact finite certificates. I prefer:

1. A scalar/profile theorem that eliminates most or all of the 1427 profiles
   before A/B state search.

2. A canonical decomposition of the T=2 profiles into a small number of label
   support families analogous to the old five-label 6195 family.

3. A P-free quotient certificate usable across whole profile families, not
   one fixed R-skeleton at a time.

4. A way to exploit edge window e=112..143 and beta>=37 that was not present
   in the older q13 verifier.

5. A falsification check: is the valid T=2 frontier actually impossible by a
   simpler argument, or could there be local SAT witnesses requiring the
   direct rooted/stability route instead?

REQUIREMENTS

- Do not use the rejected terminal_closure equalities.
- If you propose a reroot consequence, state exactly which already-closed
  frontier it depends on and avoid circular use.
- Be explicit about whether a claim is proved, conjectural, or a finite
  certificate recipe.
- Give the weakest safe next experiment if no hand lemma is visible.
- End by listing the weakest steps of your own answer.
