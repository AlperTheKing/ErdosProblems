We are working on Erdős Problem #23 in the delta=0 reduction.  The global
conjecture has been reduced to one scalar inequality, but the current proof
route is a descent/Hall lemma inside a terminal-shadow switch.  I need one
concrete proof idea for the exact finite sublemma below.  Please do not propose
generic Hall, leakage, or arbitrary prefix-union inequalities; those have been
exact-refuted.

Context.

We have a triangle-free graph with a connected maximum cut.  Let B be cut/blue
edges and M be bad/monochromatic edges.  For a bad edge f, cyc[f] is the set of
shortest B-geodesics closing f into an odd cycle, ell(f) is the odd-cycle
length.  A terminal-shadow switch S is a vertex set such that every crossing
bad edge f in C=delta_M(S) sees S as a terminal prefix/suffix on every shortest
row, and every boundary blue edge e in E=delta_B(S) is witnessed by at least one
crossing bad edge: e is the first B-edge by which some terminal shortest row of
f exits S.  This gives a witness bipartite graph between crossing bad edges C
and boundary blue exits E:

  f ~ e iff f witnesses e.

The descent machine is already proven: if this witness graph has an SDR
saturating E and one strict length surplus, the switch lowers Gamma, so a
Gamma-minimal cut cannot have the negative residual R[v]<0.  Thus it remains
to prove the SDR/Hall statement for the selected seed+moat switch.

Known false routes.

1. Arbitrary connected subdiagram leakage (PL) is false.  Component balance
   plus max-cut does not imply Hall.  A concrete H?AFBo] example has full
   witness graph K_{2,2} but a connected subdiagram with beta=0<mu=1.
2. Arbitrary prefix hull / side-door Hall is false outside the right selected
   domain; alien-door fan models exist.
3. The shortcut "after rare stage0 every unmatched minimum-lambda exit is
   universal to longer bad edges" is false.  There are 19/182 exact failures.

Current exact-gated theorem.

For a completed seed+moat switch S selected from an R[v]<0 site:

Let
  F = delta_M(S), E = delta_B(S), Wit(e) = {f in F : f witnesses e},
  lambda(e) = min_{f in Wit(e)} ell(f).

Let
  L0 = min_{f in F} ell(f),
  F0 = {f in F : ell(f)=L0},
  F1 = F \ F0,
  E0 = {e in E : lambda(e)=L0}.

Stage0 matching:
  match F0 into E0 with minimum cost, where cost of exit e is
  deg1(e)=|Wit(e) cap F1|, so the matching consumes exits least useful to
  longer bad edges first.  Delete the used exits.  Restrict the witness graph
  to F1 and the remaining exits.

Exact gate:

  python problems/23/writeup/_codex_residual_terminal_block_gate.py \
    --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

returns:

  tested=182, status={'ok': 182}, VERDICT PASS.

Two-terminal swap theorem to prove.

In every residual connected component after stage0:

  (TT) Every non-universal residual exit e has a defect orientation

          inside(e) -> tau(e),

       where inside(e) is the S-side endpoint of the boundary exit e, and
       tau(e) is the common S-terminal of all longer bad edges missed by e.
       We have inside(e) != tau(e).  All defect orientations in one residual
       component use at most two terminal vertices total.  The missed sets are
       pairwise disjoint.

This implies the residual component is balanced with a complement that is a
disjoint union of at most two exit-centered stars, hence Hall/SDR follows.

Exact gate:

  python problems/23/writeup/_codex_residual_two_terminal_gate.py \
    --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

returns:

  tested=182, status={'ok': 182}, VERDICT PASS.

Exact examples of sparse residual matrices:

3x3/8:
  111
  111
  11.

4x4/14:
  1.11
  .111
  1111
  1111

4x4/12:
  111.
  11.1
  111.
  11.1

The 4x4/12 example shows leftover minimum-lambda exits need not be universal:
one exit with inside terminal 12 misses the two longer rows based at terminal
13, and the other exit with inside terminal 13 misses the two longer rows based
at terminal 12.  This is exactly a two-terminal swap.

Desired proof decomposition.

TT1: No mixed-terminal defect.
  A residual exit cannot miss longer rows based at two distinct S-terminals.
  This should follow from shortest-geodesic no-crossing / triangle-free:
  otherwise two terminal row families route around the same boundary exit and
  form either a shorter B-geodesic or a theta graph with an odd shortcut.

TT2: No overlapping defects.
  Two residual exits cannot both be missed by the same longer crossing bad edge.
  Equivalently, the missing sets M(e) are pairwise disjoint.  Geometrically,
  a fixed terminal row cannot avoid two residual side exits of the completed
  switch without becoming a shorter trapped/lens row.

TT3: No third terminal vertex after rare stage0.
  If three disjoint terminal-block defects survive, then the F0-E0 stage0
  matching should admit an alternating exchange that consumes a more-rare exit
  and reduces the deg1 cost, contradicting the rare-exit matching.

Question.

Please give one rigorous, local proof route for TT1/TT2/TT3.  I need a
concrete lemma or exchange argument that is exact-testable from the objects
above.  Avoid re-proposing arbitrary subdiagram leakage, scalar Hall, or
"all leftover short exits are universal"; all three are false.
