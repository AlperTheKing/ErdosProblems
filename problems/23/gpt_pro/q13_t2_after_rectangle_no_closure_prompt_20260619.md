CONTEXT: Erdős Problem #23 finite n=30 reduction, q=13/r0=8/t=2 five-label core.

We are still in the support

  c0=c1=c6=0,
  labels S2={2}, D12={1,2}, S3={3}, D13={1,3}, T={1,2,3},

with R-edges only in S2-D13, D12-S3, and optionally S2-S3.

Safe cuts already in verifier:

1. Exact A/B state law:
   A_i B_j edge iff |X_i cap Y_j|=0; |X_i cap Y_j|=1 forbidden.
2. Full R/R, A/R, B/R, A/A, B/B codegree checks.
3. Root-side visibility.
4. Exact p, e_R, M row.
5. Psi rooted cuts, often class-uniform only.
6. H14 anti-tightness:
   for r notin U_i,
     D(r)+|U_i|+d_R(r,U_i) >= 17.
   This remains conditional on full reroot-invariant H14.
7. Isolated-T support cut.
8. Aggregate mixed-codegree cut.

We do NOT use terminal-reroot equality or terminal-touch equality. Those are rejected.

NEW COMPUTATIONAL FACTS:

After unioning safe post-class-Psi closures, the remaining exact rows are:

  search23/q13_t2_r8_a6b7_postcuts_remaining.tsv
  238 UNKNOWN rows, 25 cnt families.

Largest family:

  cnt=(0,0,3,2,3,3,0,2), profile 6195,
  20 exact rows,
  e_R=12..21, p=16..26, Mmin=49..59, Mmax=60..61.

Full witness-resolved mixed-codegree projection on this largest family:

  search23/q13_t2_r8_a6b7_topfamily_6195_witness_full_45.tsv
  0 INFEASIBLE, 20 UNKNOWN, 0 SAT.

R-skeleton count for the largest family:

  allowed_edges = 24
  all_skeletons = 16,777,216
  local_skeletons = 17,408

e_R distribution:

  12: 6
  13: 72
  14: 387
  15: 1234
  16: 2601
  17: 3816
  18: 3990
  19: 2988
  20: 1584
  21: 576
  22: 135
  23: 18
  24: 1

Fixed-R-mask exact verifier on the six local e_R=12 skeletons of profile 6195,
for the two corresponding rows

  p=25, M=58..61
  p=26, M=58..60

gave:

  0 INFEASIBLE, 12 UNKNOWN, 0 SAT
  timeout=60s per fixed skeleton, workers=100.

I implemented your proposed A/B nonedge-rectangle projection cuts:

  Wedge: if rs,rt in E(R), q_r+q_s+q_t-o_st <= 36-p.
  Complete-block Bonferroni cut for forced complete R-blocks.
  Global moment:
    sum q_r >= 2(36-p),
    sum o_rs >= sum q_r - (36-p).

High-p audit on the 49 remaining rows with p>=25:

  wedge only:              0 INFEASIBLE, 49 UNKNOWN, 0 SAT.
  complete+global only:    0 INFEASIBLE, 49 UNKNOWN, 0 SAT.
  wedge+complete+global:   0 INFEASIBLE, 49 UNKNOWN, 0 SAT.

QUESTION:

The previous safe projections are correct but not strong enough for closure.
Find the next smallest mathematically safe move.

Requirements:

1. Do not use terminal-reroot equality or terminal-touch equality.
2. Prefer a fixed-skeleton or state-separator certificate for the top family,
   especially e_R=12 where only six R-skeletons exist.
3. If you propose a lemma, give a rigorous proof from existing exact-state
   constraints, triangle-freeness, codegree, rooted cuts, or H14 anti-tightness.
4. If no lemma is visible, propose the single most informative next finite
   experiment, with exact variables/constraints and expected diagnostic value.
5. Be adversarial: explain why rectangle projections failed to close high-p
   rows, and what missing interaction they do not capture.
