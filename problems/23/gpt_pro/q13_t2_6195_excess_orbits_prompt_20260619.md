CONTEXT:
We are working on the finite Erdős #23 target `a(30)=36`, specifically a
q13/t=2 rooted branch.  This is NOT yet the full general #23 bridge.

The active hard subcase is the canonical q13 profile `6195`, fixed R-skeleton
mask `0xfd8a30`, `e_R=12`, labels

`[2,2,2,3,3,4,4,4,5,5,5,7,7]`

where labels are bitmasks on three C-colours.  The fixed R-degrees are

`d_R = [2,2,2,3,3,2,2,2,2,2,2,0,0]`.

We use the exact A/B state-count quotient:

- legal states are independent subsets `I subset R` satisfying root-colour
  visibility, i.e. each C-colour support is met at least once;
- integer counts `A_I,B_I`, with `sum A_I=sum B_I=6`;
- `m_r = alpha_r+beta_r`, `alpha_r=sum_{I contains r} A_I`,
  `beta_r=sum_{I contains r} B_I`;
- exact `M=sum |I|(A_I+B_I)`;
- exact `p=sum_I A_I * sum_{J disjoint I} B_J`;
- intersection-one A/B state pairs are forbidden;
- typewise A/R, B/R, A/A, B/B, and R/R codegree constraints are all imposed;
- root-opposite constraints `d_P(a)>=2`, `d_P(b)>=2` are imposed typewise;
- full rooted Psi cuts over R-masks are imposed;
- H14 anti-tightness inequality `D_r+U_i+d_i(r)>=17` is imposed, but no
  unsupported terminal-touch equality is used.

For `p=25, M=60`, the per-column lower floors are

`floors = [5,5,5,3,3,5,5,5,4,4,4,5,5]`, sum `58`.

So we branched on excess-two vectors `e_r>=0`, `sum e_r=2`, enforcing
`m_r=floors_r+e_r`.

Computation:

- all 91 raw excess-two vectors were run at 300s; 10 raw vectors closed
  INFEASIBLE, 81 remained UNKNOWN;
- automorphism audit: 91 raw vectors form 21 orbits; the 10 raw closed vectors
  cover 3 full orbits, leaving 18 orbit representatives;
- rerun of the 18 reps at 600s with 6 x 16 workers and guarded lazy quotient
  cut separation returned `18/18 UNKNOWN`;
- quotient lazy cuts did not fire: every row reports
  `quotient_cuts=0`, `quotient_timeouts=0`, `quotient_checked_outer=0`;
  the master does not produce count candidates before timeout.

The 18 unresolved excess-two orbit representatives are:

```
0,0,0,0,0,0,0,0,0,0,0,0,2
0,0,0,0,0,0,0,0,0,0,0,1,1
0,0,0,0,0,0,0,0,0,0,1,0,1
0,0,0,0,0,0,0,0,0,1,1,0,0
0,0,0,0,0,0,0,1,0,0,0,0,1
0,0,0,0,0,0,0,1,0,0,1,0,0
0,0,0,0,0,0,0,2,0,0,0,0,0
0,0,0,0,0,0,1,1,0,0,0,0,0
0,0,0,0,1,0,0,0,0,0,0,0,1
0,0,0,0,1,0,0,0,0,0,1,0,0
0,0,0,0,1,0,0,1,0,0,0,0,0
0,0,0,0,2,0,0,0,0,0,0,0,0
0,0,0,1,1,0,0,0,0,0,0,0,0
0,0,1,0,0,0,0,0,0,0,0,0,1
0,0,1,0,0,0,0,0,0,0,1,0,0
0,0,1,0,0,0,0,1,0,0,0,0,0
0,0,1,0,1,0,0,0,0,0,0,0,0
0,1,1,0,0,0,0,0,0,0,0,0,0
```

QUESTION:
Do not suggest more blind timeout.  Find the single strongest next structural
cut or finite certificate that should close or sharply reduce these 18
excess-two orbit representatives.

Acceptable answers:

1. A rigorous hand lemma applying to all or many of the listed excess vectors.
2. A precise CP-SAT/PB constraint family, still P-free if possible, that is
   logically valid from the rooted q13/t=2 hypotheses and is likely to cut
   before candidate generation.
3. A small branching scheme over these excess vectors with a proof that each
   branch has a strictly stronger local obstruction than the current model.

Requirements:

- Be explicit about which hypotheses are used.
- Do not use the rejected terminal-touch equality.
- Do not assume a fixed A/B template unless you explain why the count quotient
  is insufficient.
- If you propose weighted quotient/min-cut cuts, give the exact static master
  constraints or a separation scheme that can fire before FEASIBLE candidates.
- End by listing the weakest step of your own proposal.
