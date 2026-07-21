# W144 eta-realizer Steiner audit

Date: 2026-07-18.

## Status

This note does **not** prove or refute W144, and it does not prove or refute the
eta-realizer Steiner lemma

    some x with d(x,C(G))=eta belongs to a (g-1)-set S
    with d_G(S)>=g-2+eta.                                  (ER)

It records the exact direct bridge, a proved center-geodesic configuration, and
the first exchange that remains unsupported.  No weaker surrogate is opened.

## 1. Exact bridge

Let `S` have `g-1` vertices and let `H` be a vertex-minimal induced connected
subgraph containing `S`.  The already proved minimal-connector cycle lemma says
that a cycle in `H` would have at most `|S|=g-1` vertices, contradicting girth
`g`.  Hence `H` is a tree.  If (ER) holds, then

    |V(H)|=|E(H)|+1>=d_G(S)+1>=g-1+eta,

which is exactly W144 for `g>=5`.  Thus (ER), not an all-root strengthening, is
a sufficient closing lemma.

When `eta=0`, (ER) is immediate: every `(g-1)`-set containing any prescribed
vertex has Steiner distance at least `g-2`.  The rest of this note assumes
`eta>=1`.

## 2. Proved center-geodesic configuration

Fix an eta-realizer `x`, a nearest center `c`, and an `x`--`c` geodesic

    P: x=p_0,p_1,...,p_eta=c.

Put `p=p_(eta-1)` and `r=rad(G)`.  The vertex `p` is not central, since otherwise
`d(x,C)<=eta-1`.  Therefore `ecc(p)>=r+1`.  Choose `y` with
`d(p,y)>=r+1`.  Since `p` is adjacent to the central vertex `c`,

    r+1 <= d(p,y) <= 1+d(c,y) <= r+1.

Consequently

    d(c,y)=r,        d(p,y)=r+1.                             (2.1)

Choose a `c`--`y` geodesic

    Q: c=q_0,q_1,...,q_r=y.

Then `P` and `Q` meet only at `c`.  Indeed, if `p_i=q_j!=c`, geodesicity gives
`j=d(c,p_i)=eta-i`, and the route through that common vertex gives

    d(p,y) <= (eta-1-i)+(r-j)=r-1,

contradicting (2.1).  Moreover, for every `j`,

    d(p,q_j)=j+1,                                            (2.2)

because the route through `c` is an upper bound and (2.1), applied with the
remaining `q_j`--`y` segment, is the matching lower bound.

There are two further exact consequences when `2eta<g`.

1. `P` is the unique `x`--`c` geodesic: two distinct such geodesics contain a
   cycle of length at most `2eta<g`.
2. There is no edge from `p_i in P-{c}` to `q_j in Q-{c}`.  Such an edge would
   give, by (2.2), `j+1<=eta-i`, while the cycle consisting of that edge and
   the two center segments has length `eta-i+j+1`.  Hence this cycle has length
   at most `2(eta-i)<=2eta<g`, a contradiction.

These statements use the ordinary center essentially; they are stronger than
the previously known mere disjointness of two selected geodesics.

## 3. The extremal connector attempt and its exact gap

In the subrange `2eta<g` and `r>=g-2`, the preceding configuration suggests the
exact-size terminal set

    S_0={x,c,q_2,q_3,...,q_(g-2)}.

It has `g-1` vertices and contains the eta-realizer `x`.  Omitting `q_1`, and
using the proved absence of `P`--`Q` cross edges, shows that the induced graph on

    V(P) union {q_2,...,q_(g-2)}

is disconnected.  Thus the fixed geodesic `P` cannot be the entire nonterminal
part of a connector with only `eta-1` nonterminals.

This does **not** finish the argument.  Let `T` be an arbitrary connector of
`S_0`, let `R` be its unique `x`--`c` path, let `L=|E(R)|`, and let `a` be the
number of terminals among `q_2,...,q_(g-2)` lying internally on `R`.  Every
other one of these terminals needs at least one edge outside `R`, so

    |E(T)| >= L+(g-3-a).                                    (3.1)

To exclude `|E(T)|<=g-3+eta`, one must prove

    L-a >= eta+1                                             (3.2)

for every alternative `R`; the unique geodesic `P` is already excluded by the
disconnection above.  Girth only forces an alternative path to participate in
a cycle of length at least `g`.  It does not by itself charge one unit for each
selected `q_j` lying on that path.  Those terminals can be internal to a longer
route and exactly cancel its extra edges in (3.1).

Statement (3.2) is the first unsupported exchange.  It is a disguised
single-pair terminal charge, one of the shortcuts already excluded in the
registered route.  Proving it would require a genuinely global argument that
replaces a terminal-rich alternative path by a connector with more
nonterminals; none of the proved center facts above supplies that replacement.
For `r<g-2`, one additionally needs terminals from several branches, which is
the same global issue rather than a separate smaller lemma.

Under the direct-proof guard, the argument stops here.  It would be incorrect
to infer geodesicity of `R` merely from the bound of `eta-1` nonterminals,
because terminals lying internally on `R` are not counted as Steiner vertices.

## 4. Exact computation

The existing stronger all-root audit covers every connected girth-at-least-five
graph through order 13: 52,000 graphs and 663,650 rooted instances, with no
failure and minimum slack zero.  As an independent rerun for this audit,
`test_steiner_vertex_fast.py --min-n 5 --max-n 9 --workers 8` checked

    124 graphs, 1,068 rooted instances, 0 failures, minimum slack 0.

This evidence includes (ER) but is not a proof.  No counterexample to (ER) was
found, and no claim of closure is made.