# GPT Pro prompt — Erdos #23 q12/t2 no-zero UNKNOWN band

CONTEXT:
We are attacking Erdos #23 / `a(30)=36` via the low-codegree-root route.

Already closed computationally:
- q15 by V123.
- q14/t2 by V333.
- q14/t3 by V337.
- q13/r0=9/t3/|A|=|B|=6/q=13 by V338.
- q12/r0=9/t3/|A|=6,|B|=7 and side-swap by V339.

Active branch:

```text
r0=9, t=2, |A|=|B|=7, |R|=12, C={c1,c2}.
```

R labels are encoded as masks:

```text
c0 = zero label
c1 = label {1}
c2 = label {2}
c3 = label {1,2}  (call these D-vertices)
```

The current exact-state verifier includes:
- R skeleton realization with label-disjointness and R triangle-freeness;
- local domination `d_R(r,U_i) >= 2` for missing colours;
- exact A/B law: `|X_a cap Y_b|=0` iff `ab` is an A-B edge; otherwise
  `|X_a cap Y_b| >= 2`; intersection size `1` is forbidden;
- R/R edge and nonedge codegree threshold `2`;
- A/A and B/B same-side nonedge codegree;
- A/R and B/R nonedge codegree;
- root-to-R codegree;
- R vertex degree at least `9`;
- A/B degree constraints `deg_B(a) >= 2`, `deg_A(b) >= 2`, and
  `deg_B(a)+|X_a| >= 8`, `deg_A(b)+|Y_b| >= 8`;
- A-C and B-C cuts `|X_a cap U_i| >= 1`, `|Y_b cap U_i| >= 1`;
- all rooted Phi/Psi cut inequalities currently used in the campaign;
- safe symmetry breaking inside identical R-label blocks and within A/B sides.

Important correction:
An earlier prompt incorrectly said each hard profile has a forced scalar row.
That is false.  The 21 profile-level hard cases have many scalar rows.  After
splitting by scalar rows `(p,eR,M)` and adding full local codegree cuts, the
first 200 scalar rows give:

```text
165 INFEASIBLE, 35 UNKNOWN, 0 SAT.
```

One representative UNKNOWN row remains UNKNOWN even at 300s with 100 workers:

```text
idx=40, cnt=(0,3,4,5), p=25, eR=12, M=67.
```

Additional C++ skeleton census:

```text
search23/q12_t2_nozero_unknown_skeleton_census.cpp
search23/q12_t2_nozero_unknown_skeleton_census.tsv
```

This enumerates the S1-S2 bipartite R-skeletons for the 35 no-zero UNKNOWN
rows.  Result:

```text
rows=35
total S1-S2 skeletons=63821
skeletons with no degree-2 singleton=3929
rows with at least one no-tight skeleton=26
```

By eR:

```text
eR=12: rows=4,  skeletons=1700,  no_tight=26
eR=13: rows=6,  skeletons=1854,  no_tight=288
eR=14: rows=9,  skeletons=25740, no_tight=288
eR=15: rows=11, skeletons=25524, no_tight=1284
eR=16: rows=5,  skeletons=9003,  no_tight=2043
```

There are 9 single-skeleton UNKNOWN rows.  These include complete bipartite
S1-S2 skeletons, hence no C-tight singleton at all:

```text
ordinal=29  idx=40 c=(3,4,5) p=25 eR=12 M=67..67 degree=4,4,4|3,3,3,3
ordinal=50  idx=41 c=(3,5,4) p=22 eR=15 M=68..68 degree=5,5,5|3,3,3,3,3
ordinal=56  idx=41 c=(3,5,4) p=23 eR=15 M=66..67 degree=5,5,5|3,3,3,3,3
ordinal=61  idx=41 c=(3,5,4) p=24 eR=15 M=64..66 degree=5,5,5|3,3,3,3,3
ordinal=65  idx=41 c=(3,5,4) p=25 eR=15 M=62..65 degree=5,5,5|3,3,3,3,3
ordinal=101 idx=49 c=(4,3,5) p=25 eR=12 M=67..67 degree=3,3,3,3|4,4,4
ordinal=143 idx=50 c=(4,4,4) p=23 eR=16 M=66..66 degree=4,4,4,4|4,4,4,4
ordinal=149 idx=50 c=(4,4,4) p=24 eR=16 M=64..65 degree=4,4,4,4|4,4,4,4
ordinal=154 idx=50 c=(4,4,4) p=25 eR=16 M=62..64 degree=4,4,4,4|4,4,4,4
```

Therefore a pure C-tight/terminal-neighbour argument cannot close the whole
band unless it is combined with a separate argument for these no-tight complete
or near-complete S1-S2 skeletons.

All 35 UNKNOWN rows in the first 200-row scalar split have `c0=0`.  Therefore
there are no zero-label R-vertices.  The R graph is simply a bipartite graph
between S1 and S2; the D-vertices are isolated in R.

The 35 UNKNOWN scalar rows are:

```text
ordinal idx cnt                 p  eR M-range U
29      40  0,3,4,5             25 12 67..67 17
50      41  0,3,5,4             22 15 68..68 16
55      41  0,3,5,4             23 14 66..68 16
56      41  0,3,5,4             23 15 66..67 16
59      41  0,3,5,4             24 13 66..68 16
60      41  0,3,5,4             24 14 64..67 16
61      41  0,3,5,4             24 15 64..66 16
62      41  0,3,5,4             25 12 68..68 16
63      41  0,3,5,4             25 13 66..67 16
64      41  0,3,5,4             25 14 64..66 16
65      41  0,3,5,4             25 15 62..65 16
66      41  0,3,5,4             26 13 66..66 16
67      41  0,3,5,4             26 14 64..65 16
101     49  0,4,3,5             25 12 67..67 17
136     50  0,4,4,4             22 15 68..68 16
141     50  0,4,4,4             23 14 66..68 16
142     50  0,4,4,4             23 15 66..67 16
143     50  0,4,4,4             23 16 66..66 16
146     50  0,4,4,4             24 13 66..68 16
147     50  0,4,4,4             24 14 64..67 16
148     50  0,4,4,4             24 15 64..66 16
149     50  0,4,4,4             24 16 64..65 16
150     50  0,4,4,4             25 12 68..68 16
151     50  0,4,4,4             25 13 66..67 16
152     50  0,4,4,4             25 14 64..66 16
153     50  0,4,4,4             25 15 62..65 16
154     50  0,4,4,4             25 16 62..64 16
155     50  0,4,4,4             26 13 66..66 16
156     50  0,4,4,4             26 14 64..65 16
157     50  0,4,4,4             26 15 62..64 16
191     51  0,4,5,3             22 15 68..69 15
192     51  0,4,5,3             22 16 68..68 15
197     51  0,4,5,3             23 14 66..69 15
198     51  0,4,5,3             23 15 66..68 15
199     51  0,4,5,3             23 16 66..67 15
```

For this no-zero subfamily:
- R-edges occur only between S1 and S2.
- D-vertices are R-isolated.
- Every S1/S2 vertex has opposite-side R-degree at least 2.
- Every D-vertex has label size 2 and degree constraint `m_D >= 7`.
- Every singleton `s` has label size 1 and degree constraint
  `m_s + d_R(s) >= 8`.
- For each R-edge `uv`, the A-side and B-side state laws imply
  `alpha_u + alpha_v <= 7` and `beta_u + beta_v <= 7`.

QUESTION:
Find the smallest mathematically safe structural cut for this `c0=0`
q12/t2/r9 no-zero subfamily.  I want something stronger than adding timeout.

Preferred forms:
1. A scalar inequality in terms of the bipartite S1-S2 graph, D count,
   `(p,eR,M)`, and the degree sequence.
2. A terminal/reroot equality if it is genuinely justified in this q12/t2
   setting.
3. A P-free finite certificate over independent A/B state multisets, small
   enough to implement in C++ with <=100 threads.
4. A reusable CP-SAT/C++ constraint that targets the dense S1-S2 / isolated-D
   structure.

Please:
- State each lemma precisely.
- Prove it rigorously, or give a finite certificate design with exact checks.
- Spell out the exact constraints to add.
- Mark dependencies on lower-q closure, cap-frontier closure, or reroot
  assumptions.
- End with weakest steps.
