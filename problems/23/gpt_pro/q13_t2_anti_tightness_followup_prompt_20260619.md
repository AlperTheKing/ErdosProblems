CONTEXT:
We are working on Erdős problem #23 / the low-codegree rooted finite route for proving a(30)=36.

The active branch is q=13, t=2, r0=8, with three root-colour common vertices C={c1,c2,c3}. There are Q=13 vertices in R, labelled by subsets L(r) of {1,2,3}. Let U_i={r in R: i in L(r)}. R-edges are allowed only between disjoint labels.

The exact verifier enforces:

```text
1. R is triangle-free; R-edges only join disjoint labels.
2. |U_i| >= 6 for each i.
3. For r notin U_i, d_R(r,U_i) >= 2.
4. alpha_r+|L(r)| >= 2 and beta_r+|L(r)| >= 2.
5. alpha_r+beta_r+d_R(r)+|L(r)| >= 8.
6. A/B states are independent in R.
7. R/R edge codegree is 0; R/R nonedge codegree is >=2.
8. A/B edge iff |N_R(a) cap N_R(b)|=0; A/B nonedge has >=2 common R-neighbours.
9. Same-side A/A and B/B codegrees, A/R and B/R codegrees.
10. Rooted Phi/Psi cut inequalities for beta(G)>=37.
11. Global cap: root_edges+U+p+e_R+M <= 139, where M=sum_r(alpha_r+beta_r).
```

Already verified computation:

```text
q13/r0=8/t=3 closed completely:
(A,B)=(5,7): 257/257 INFEASIBLE
(A,B)=(6,6): 256/256 INFEASIBLE
(A,B)=(7,5): 256/256 INFEASIBLE
```

For q13/r0=8/t=2,(A,B)=(6,7):

```text
C++ scalar prefilter leaves 1427 profiles.
First exact-state pass: 530 INFEASIBLE, 887 UNKNOWN, 10 not reached, 0 SAT.
Hard rerun on first 40 UNKNOWN, timeout=120s, total_workers=100: 40 UNKNOWN, 0 SAT.
```

You previously rejected my proposed terminal-reroot degree equality. I accept that: I am NOT counting terminal-closure results as proof.

I implemented your safe conditional anti-tightness cut:

```text
For r notin U_i:
D(r)+|U_i|+d_R(r,U_i) >= 17,
where D(r)=alpha_r+beta_r+d_R(r)+|L(r)|.
```

This was implemented as `--anti-tightness` and run WITHOUT terminal equality on the original first 40 hard q13/t2 profiles:

```text
timeout=60s, total_workers=100:
40 UNKNOWN, 0 SAT.
```

So anti-tightness is safe, but not enough at profile level.

Diagnostic only, NOT proof:
The invalid terminal-equality experiment reveals a rigid UNKNOWN core. With terminal equality, 13/40 hard profiles became INFEASIBLE and 27 remained UNKNOWN. Those 27 all have:

```text
c0=c1=c6=0
```

Thus only labels

```text
S2  = {2}
D12 = {1,2}
S3  = {3}
D13 = {1,3}
T   = {1,2,3}
```

occur. R-edges can only lie in:

```text
S2-D13, D12-S3, S2-S3.
```

The T vertices are isolated in R. Local domination forces:

```text
every S2 vertex has at least 2 neighbours in D13;
every D13 vertex has at least 2 neighbours in S2;
every D12 vertex has at least 2 neighbours in S3;
every S3 vertex has at least 2 neighbours in D12.
```

The optional block is S2-S3.

A row-split diagnostic under the invalid terminal equality closed 2691/2948 p/eR/M rows and left 257 UNKNOWN, 0 SAT. This cannot be counted, but it suggests the hard middle band is roughly:

```text
p=21..25, e_R=14..17
```

QUESTION:
Find the next mathematically safe P-free strengthening for the q13,t=2 five-label support

```text
S2, D12, S3, D13, T
```

with R-edges only in S2-D13, D12-S3, S2-S3 and T isolated.

I need a cut/lemma that does NOT use the rejected terminal degree equality. Ideally it also does NOT require the extra H14 reroot-closure assumption; if H14 or another frontier closure is needed, state exactly.

The output should be directly implementable in CP-SAT/C++ over alpha,beta,d_R,U_i,d_R(r,U_i), the three R-edge blocks, and/or small skeleton-level finite certificates.

Prefer one of:

1. a P-free capacity/degree/cut lemma that kills or sharply reduces this five-label core;
2. a safe row-level branch/certificate for p=21..25,e_R=14..17;
3. a stronger but still valid replacement for terminal closure.

REQUIREMENTS:
- Give one complete lemma/proof, not a broad sketch.
- Mark every extra assumption explicitly.
- Give exact CP-SAT/C++ constraints to add.
- If no safe structural cut exists, say so and propose the smallest exact finite branch to test next.
- End by listing the weakest steps of your own answer.
