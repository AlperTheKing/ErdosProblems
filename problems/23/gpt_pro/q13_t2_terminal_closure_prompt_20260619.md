CONTEXT:
We are working on the low-codegree/rooted finite proof route for Erdős problem #23 / the target a(30)=36.  The active hard branch is the q=13, t=2 rooted branch with three root-colour common vertices C={c1,c2,c3}.  There are Q=13 vertices in R, labelled by subsets L(r) of {1,2,3}; U_i={r in R: i in L(r)}.  Edges inside R are allowed only between disjoint labels.

The concrete branch currently stuck is:

```text
q=13, k=3, r0=8, t=2, |A|=6, |B|=7.
```

The exact verifier already enforces:

```text
1. R is triangle-free, and R-edges only join disjoint labels.
2. |U_i| >= r0-2 = 6 for each i.
3. For r notin U_i, d_R(r,U_i) >= t = 2.
4. For every r, alpha_r+|L(r)| >= 2 and beta_r+|L(r)| >= 2,
   where alpha_r=|N_A(r)| and beta_r=|N_B(r)|.
5. For every r, alpha_r+beta_r+d_R(r)+|L(r)| >= 8.
6. A/B states are independent in R.
7. R/R edge codegree is 0; R/R nonedge codegree is >=2.
8. A/B edge iff |N_R(a) cap N_R(b)|=0; A/B nonedge has >=2 common R-neighbours.
9. Same-side A/A and B/B codegrees, A/R and B/R codegrees.
10. The rooted Phi/Psi cut inequalities for beta(G)>=37.
11. Global edge cap: root_edges+U+p+e_R+M <= 139, where M=sum_r(alpha_r+beta_r).
```

Recent verified computation:

```text
q13/r0=8/t=3 closed completely:
(A,B)=(5,7): 257/257 profiles INFEASIBLE
(A,B)=(6,6): 256/256 profiles INFEASIBLE
(A,B)=(7,5): 256/256 profiles INFEASIBLE
```

For q13/r0=8/t=2,(A,B)=(6,7), a C++ scalar prefilter leaves 1427 profiles.  The first exact-state pass gives:

```text
530 INFEASIBLE
887 UNKNOWN
10 not reached before process timeout
0 SAT
```

A hard rerun on the first 40 UNKNOWN profiles with 120s each, total 100 workers, gives:

```text
40/40 UNKNOWN
0 SAT
```

Typical hard UNKNOWN label-count vectors c0..c7 include:

```text
0,0,2,2,2,2,0,5
0,0,2,2,3,3,0,3
0,0,2,3,2,2,0,4
0,0,2,4,2,4,0,1
0,0,3,2,3,4,0,1
```

Here mask 0 is label empty, mask 1 is {1}, mask 2 is {2}, ..., mask 7 is {1,2,3}.

ADDENDUM AFTER A TERMINAL-CLOSURE TEST:
I implemented the candidate terminal-closure as an experimental CP-SAT flag.  On 40 hard UNKNOWN profiles:

```text
timeout=30s, total_workers=100, with terminal-closure:
13 INFEASIBLE
27 UNKNOWN
0 SAT

rerun the 27 with timeout=120s:
27 UNKNOWN
0 SAT
```

The remaining 27 profiles have a very rigid common support:

```text
c0=c1=c6=0
```

So only labels

```text
{2}, {1,2}, {3}, {1,3}, {1,2,3}
```

occur.  Let

```text
S2  = label {2}
D12 = label {1,2}
S3  = label {3}
D13 = label {1,3}
T   = label {1,2,3}.
```

Then R-edges can only lie in the three bipartite blocks:

```text
S2-D13, D12-S3, S2-S3.
```

The triple-labelled T vertices are isolated in R.  Local domination forces:

```text
every S2 vertex has at least 2 neighbours in D13;
every D13 vertex has at least 2 neighbours in S2;
every D12 vertex has at least 2 neighbours in S3;
every S3 vertex has at least 2 neighbours in D12.
```

The optional block is S2-S3.  Examples of the remaining 27 profiles are:

```text
c2,c3,c4,c5,c7 =
2,2,2,2,5
2,2,2,3,4
2,3,3,3,2
2,4,4,3,0
3,2,3,4,1
```

If terminal-closure is valid but insufficient, please focus on this residual support pattern.  Is there a P-free capacity/degree/cut lemma for this five-label structure that forces M below the required value or otherwise contradicts the edge cap/cut constraints?

QUESTION:
Find the smallest mathematically safe structural strengthening for this q=13,t=2 branch, preferably P-free (not enumerating A/B templates), that can be added to the verifier and plausibly kills the UNKNOWN core.

The candidate I want you to audit first is the following terminal-reroot closure:

Let r in R be C-tight on colour i, meaning r notin U_i and

```text
d_R(r,U_i)=2.
```

Let P=N_R(r) cap U_i={s1,s2}.  Reroot at the nonedge (r,c_i), whose two common neighbours are s1,s2.  Is it valid in this q13/t2 frontier to impose:

```text
alpha_r+beta_r+d_R(r)+|L(r)| = 8
```

and also, for each terminal common neighbour s in P,

```text
alpha_s+beta_s+d_R(s)+|L(s)| = 8 ?
```

Equivalently, can every C-tight vertex and every terminal neighbour touched by a C-tight pair be forced degree-tight in the original graph?

If yes:
1. Give a rigorous proof, spelling out exactly what frontier/closure assumptions are needed.
2. State the exact CP-SAT/C++ constraints to add.
3. Explain whether this should apply globally to q13/t2 or only in specific profile rows.

If no:
1. Identify the precise gap or counter-scenario.
2. Propose the next safest P-free cut instead.

REQUIREMENTS:
- Do not give a broad proof sketch.  I need one cut/lemma with a complete argument.
- Use only assumptions that are actually present above, or explicitly flag any extra frontier closure assumption.
- End with the weakest steps of your own answer.
