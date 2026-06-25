# GPT Pro prompt draft — Erdős #23 q14/t3 asymmetric high-q branch

CONTEXT:
We are attacking Erdős #23 / `a(30)=36` via the low-codegree root route.
Let `xy` be a nonedge of minimum common-neighbour count `t=delta_2(G)`.
For a maximal triangle-free counterexample on 30 vertices with `beta(G)>=37`
and `e(G)<=139`, Wang--Yang--Zhao gives `t in {1,2,3}`.

Let

`C=N(x) cap N(y)`, `|C|=t`,
`A=N(x)\C`, `B=N(y)\C`, and
`R=V \ ({x,y} union A union B union C)`.

Verified status:

- q=15 high branch is closed by V123.  In that branch
  `r0=8,t=3,|A|=|B|=5,|R|=15`.
- q=14/t=2/cap74 terminal branch is closed by V333.  In that branch
  `r0=8,t=2,|A|=|B|=6,|R|=14`.
- A new C++ shape audit
  `search23/lowcodegree_highq_remaining_audit.cpp`
  shows that after V123 and V333, the only remaining `q>=14`
  coarse shapes are:

```text
r0  t  |A|  |B|  |R|
8   3   5    6    14
8   3   6    5    14
```

By symmetry we can focus on:

```text
t=3, |C|=3, |A|=5, |B|=6, |R|=14, r0=8.
```

Available root/maximality facts:

1. `A union C` and `B union C` are independent.
2. There are no `A-C` or `B-C` edges.
3. Every `a in A` has at least 3 neighbours in `B`, because `ay` is a nonedge
   and the root pair has minimum nonedge codegree 3.
4. Every `b in B` has at least 3 neighbours in `A`; hence
   `p=e(A,B) >= 18`.
5. For `r in R` and each `i in {1,2,3}` with `r not adjacent c_i`,
   `d_R(r,U_i) >= 3`, where `U_i=N_R(c_i)`.
6. For `r in R`, root-to-R visibility gives
   `|N_A(r)|+|label(r)| >= 3` and
   `|N_B(r)|+|label(r)| >= 3`.
7. If `rr' in E(R)`, then `r,r'` have disjoint neighbourhoods in each of
   `A`, `B`, and `C`.
8. The exact rooted cut formulae Phi/Psi from V11 are available.

QUESTION:
Can this `q=14,t=3,|A|=5,|B|=6` high-q branch be closed by a scalar or small
finite certificate analogous to the q15 shadow lemma?

Please do the following:

1. First try to prove a scalar contradiction using only label counts, the
   local `d_R(r,U_i)>=3` condition, `p>=18`, edge budget `e<=139`, and
   the rooted Phi/Psi cuts.
2. If scalar closure fails, identify the smallest exact finite certificate:
   what variables/states should be enumerated first, what are the strongest
   prefilters, and which branch should be attacked first?
3. Be explicit about whether zero-label R vertices are possible in this
   branch; do not silently assume every R vertex touches C.
4. Flag any step that depends on lower-q closure (`q<=13`) or cap<74 closure.
5. End with the weakest steps and the first C++ experiment to run.

REQUIREMENTS:
Give rigorous derivations.  Do not suggest broad direct rooted SAT unless it is
the only remaining option.  Prefer a compressed P-free/R-skeleton or exact
state certificate.  If you cannot close the branch, say so plainly and give the
minimal next verifier.
