# Support-to-multiplicity obstruction note

Date: 2026-06-11.

Targeted lemma:

- for a boundary-support-critical touched `(A,B)`-Kempe component `K` containing
  the mate `a'`, type `(1,1)` should imply `e_H(K,C) <= 4`;
- type `(2,2)` should imply `e_H(K,C) <= 2`.

I do not see a proof from the current verified inputs. The exact obstruction is
that the boundary-support lemma is boolean in the third-colour support
`R_C(K)`: it sees whether a vertex of `K` has at least one `C`-neighbour, but
not how many such neighbours it has. Six-regularity still allows several
`C`-edges at a single supported vertex.

Abstract local countermodels:

1. Type `(1,1)`: let `K` be one edge `xy`, where `x=a'` is the `A`-terminal
   mate and `y` is a `B`-terminal. Both touch `v`. Give both `x` and `y` four
   neighbours in colour class `C`. Then `deg_G(x)=deg_G(y)=1+1+4=6`, the
   component is balanced of type `(1,1)`, and `e_H(K,C)=8`. Under `L_a` plus
   the support-forbid-C rule, both `x` and `y` have list `{B}`, so the edge
   `xy` is uncolourable. Thus boundary-support-criticality holds while the
   desired bound fails.

2. Type `(2,2)`: let `K=K_{2,2}` with `A`-terminals `a,a'` and `B`-terminals
   `b,b'`, all touching `v`. Give each vertex of `K` at least one `C`-neighbour
   (up to three each while preserving degree 6). With all four vertices in
   `R_C(K)`, the lists for `L_a` become `a:{A,B}` and `a',b,b':{B}`; the
   `K_{2,2}` edges force an immediate conflict. Already with one `C`-edge per
   vertex, `e_H(K,C)=4>2`; with degree saturation, `e_H(K,C)=12`.

These are not claimed to be full targets. They are local models showing that
support-to-multiplicity needs an additional genuinely quantitative hypothesis,
such as a bound on the number of `C`-neighbours per support vertex, or a proof
that multiple `C`-neighbours at a support vertex force a separate target
violation.

Comparable-neighbour exclusion does not by itself remove the models: choose the
third-colour neighbours and their outside neighbourhoods distinctly, so no
nonadjacent pair has nested open neighbourhoods. The six terminal
list-criticalities are also qualitative unless one proves a new compatibility
statement tying their support sets together.

