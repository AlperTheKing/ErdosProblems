# GPT Pro prompt — Erdős #23 q12/t2/r9 hard profile obstruction

SUPERSEDED NOTE (2026-06-19):
Do not use this prompt as-is.  The scalar-row audit below showed that the
claim "the scalar rows are tight/forced for each hard profile" is false.  Use
`problems/23/gpt_q12_t2_nozero_unknown_prompt_2026-06-19.md` instead; it
contains the corrected no-zero scalar UNKNOWN band.

CONTEXT:
We are attacking Erdős #23 / `a(30)=36` via the low-codegree-root route.
All current claims below are computationally verified unless marked as a
request.

Already closed:
- q15 by V123.
- q14/t2 by V333.
- q14/t3 by V337.
- q13/r0=9/t3/|A|=|B|=6/q=13 by V338.
- q12/r0=9/t3/|A|=6,|B|=7 and the side-swap by V339.

Current active obstruction:

```
r0=9, t=2, |A|=|B|=7, |R|=12.
```

Here `C={c1,c2}`.  R-vertices have labels in `{0,1,2,12}`,
encoded as masks:

```
c0 = zero label
c1 = label {1}
c2 = label {2}
c3 = label {1,2}
```

The scalar prefilter:

```
search23/q12_t2_r9_a7b7_scalar_prefilter.cpp
```

found:

```
profiles_total=455
profiles_survive=35
rows_survive=2865
```

The exact-state CP-SAT verifier:

```
search23/verify_q12_t2_r9_a7b7_profile_cpsat.py
```

contains:
- R skeleton realization with label-disjointness and R triangle-freeness;
- local domination `d_R(r,U_i) >= 2` for missing colours;
- exact A/B law: `|X_a cap Y_b|=0` iff `ab` is an A-B edge, otherwise
  `|X_a cap Y_b| >= 2`;
- R/R edge and nonedge codegree threshold `2`;
- R vertex degree at least `9`;
- A/B degree constraints `deg_B(a) >= 2`, `deg_A(b) >= 2`, and
  `deg_B(a)+|N_R(a)| >= 8`, `deg_A(b)+|N_R(b)| >= 8`;
- A-C and B-C nonedge codegree cuts
  `|N_R(a) cap U_i| >= 1`, `|N_R(b) cap U_i| >= 1`;
- all rooted Phi/Psi cut inequalities;
- safe symmetry breaking inside identical R-label blocks and within A/B sides.

Batch result:

```
14/35 profiles INFEASIBLE at 30s.
21/35 profiles remained UNKNOWN at 30s.
The 21 hard profiles rerun at 300s with 10 x 10 workers all remained UNKNOWN.
```

Hard profile list:

```text
idx c0 c1 c2 c3 U eR_lb eR_ub p eR M_lb M_ub
40  0 3 4 5 17 8  12 16 8  80 80
41  0 3 5 4 16 10 15 17 10 78 78
49  0 4 3 5 17 8  12 16 8  80 80
50  0 4 4 4 16 8  16 15 8  82 82
51  0 4 5 3 15 10 20 16 10 80 80
58  0 5 3 4 16 10 15 17 10 78 78
59  0 5 4 3 15 10 20 16 10 80 80
60  0 5 5 2 14 10 25 15 10 82 82
118 1 2 4 5 16 10 19 17 10 78 78
127 1 3 3 5 16 8  20 15 8  82 82
128 1 3 4 4 15 10 23 16 10 80 80
135 1 4 2 5 16 10 19 17 10 78 78
136 1 4 3 4 15 10 23 16 10 80 80
137 1 4 4 3 14 10 27 15 10 82 82
192 2 2 2 6 16 8  25 15 8  82 82
193 2 2 3 5 15 10 27 16 10 80 80
201 2 3 2 5 15 10 27 16 10 80 80
202 2 3 3 4 14 10 30 15 10 82 82
256 3 2 2 5 14 10 34 15 10 82 82
290 4 0 0 8 16 8  38 15 8  82 82
335 5 0 0 7 14 10 45 15 10 82 82
```

Notice the scalar rows are tight: for each hard profile, the displayed `p`,
`eR`, and `M` are forced at the lower/upper edge budget interface.

QUESTION:
Find the smallest mathematically safe structural cut that should be added
before more CP-SAT time.  Prefer a lemma that uses the tight scalar equalities
above, e.g. forced degree equalities, terminal-reroot equalities, Phi/Psi
equality cases, or a classification of the label profile shape.  Do not
suggest merely raising timeout.

Concrete deliverable requested:
1. State one or more precise lemmas that apply to all 21 hard profiles or to
   a named subfamily.
2. Give a rigorous proof or a finite certificate design small enough to
   implement.
3. Spell out exact CP-SAT/C++ constraints to add.
4. Mark any dependence on lower-q closure, cap<frontier closure, or reroot
   assumptions.
5. End with weakest steps.
