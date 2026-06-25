CONTEXT:
We are attacking Erdős problem #23 through the finite target `a(30)=36`.
The current branch is a low-codegree q=15 certificate.  We need a new
hand-checkable pruning lemma, not a long brute-force run.

Verified setup:

- A counterexample can be assumed maximal triangle-free on 30 vertices with
  `e(G)<=139` and every cut having at least 37 monochromatic edges.
- By Wang--Yang--Zhao, a counterexample has a nonedge `xy` of codegree 1..3.
- In the q=15 branch rooted at such a pair:
  `|A|=|B|=5`, `|C|=3`, `|R|=15`.
- For `C={c1,c2,c3}` define `U_i=N_R(c_i)`.
- Each R-vertex has a nonempty label `L(r) subset {1,2,3}`, namely the set of
  `i` such that `r in U_i`.
- Labels are summarized as:
  `S_i` singleton `{i}`, `D_i` doubleton missing `i`, and `T` triple.
- R-edges are only allowed between disjoint labels.
- Verified local constraints:
  `|U_i|>=6`; each `U_i` is independent; each `r notin U_i` has at least
  3 neighbours in `U_i`; and the paired rooted cut inequalities hold.

Current scalar notation:

- `p=e(A,B)`.
- `e_R=e(R)`.
- `M=e(A union B, R)`.
- q=15 edge budget gives `16 + U + p + e_R + M <= 139`.
- The cap in the computations is an upper bound on `M`.

Verified computational facts:

The generic shape-family SAT verifier fixes the exact label multiset but leaves
all R-edges and all A/B-to-R incidences variable, enforcing:

- label support constraints;
- R triangle-freeness and allowed disjoint-label R-edges;
- A/B incidence constraints;
- degree constraints;
- common-neighbour constraints for R nonedges and A/B-R pairs.

It has already proved many cap-51/cap-52 profiles UNSAT.  The remaining cap-52
hard cases collapse to the same one-sided label pattern:

`s=(0,0,a)`, `d=(0,0,b)`, `t=c`.

That is: all singleton labels are `S_3`, all doubletons are `D_3={1,2}`, and
there are `c` triple-labelled vertices.  Therefore the only admissible R-edges
are between the `S_3` class and the `D_3` class; triple vertices are isolated
inside R.

Concrete hard cases isolated:

1. `(n1,n2,n3)=(7,6,2)`, shape `s=(0,0,7)`, `d=(0,0,6)`, `t=2`,
   `p=15`, `e_R>=31`, `M<=52` is UNKNOWN after 1,000,000 conflicts.
2. `(8,5,2)`, shape `s=(0,0,8)`, `d=(0,0,5)`, `t=2`,
   unknown for `p=16..20`, `e_R=47-p`, `M<=52`.
3. `(8,6,1)`, shape `s=(0,0,8)`, `d=(0,0,6)`, `t=1`,
   unknown for `p=15..20`, `e_R=48-p`, `M<=52`.
4. `(9,5,1)`, shape `s=(0,0,9)`, `d=(0,0,5)`, `t=1`,
   unknown for `p=16..20`, `e_R=49-p`, `M<=52`.

QUESTION:
Find a rigorous pruning lemma that rules out this one-sided label-collapse
family in the q=15 branch, or at least produces a strictly stronger compact
certificate than the generic SAT verifier.

Please focus on the abstract family:

- `a` vertices of label `S_3`;
- `b` vertices of label `D_3={1,2}`;
- `c` vertices of label `T={1,2,3}`;
- `a+b+c=15`;
- R-edges only between the `S_3` and `D_3` classes;
- each vertex outside `U_i` has at least 3 neighbours in `U_i`;
- all paired rooted cut inequalities must have at least 37 monochromatic
  edges after the root contribution.

Preferred outputs:

1. A hand proof that this one-sided family violates a rooted cut inequality or
   an A/B incidence/codegree constraint.
2. Or a compact additional inequality in `(a,b,c,p,e_R,M)` that kills the
   listed cases.
3. Or a smaller certificate construction that avoids enumerating all A/B-R
   incidences.

If the family may actually be feasible under the listed constraints, say so and
identify the missing constraint needed to kill it.  Be adversarial: do not give
a plausible sketch unless every step is justified.
