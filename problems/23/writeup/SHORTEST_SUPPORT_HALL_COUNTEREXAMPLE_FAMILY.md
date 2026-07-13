# Infinite shortest-support Hall counterexample family

For each integer \(t\ge1\), let \(L,A,B,C,D,E,R\) be seven disjoint
independent sets of size \(t\), and let \(u,w,v\) be single vertices.
The graph \(G_t\) has all complete bipartite links along

\[
L-A-B-C-D-E-R,
\]

the complete link \(L-R\), and the thin channel

\[
L-u-w-v-R.
\]

Thus

\[
|V(G_t)|=7t+3,\qquad |E(G_t)|=7t^2+2t+2.
\]

## Theorem

For every \(t\ge1\), \(G_t\) is triangle-free and has a unique maximum
cut up to complementation. Its bad edges are exactly \(L\times R\), so

\[
\bip(G_t)=t^2,\qquad \operatorname{MaxCut}(G_t)=6t^2+2t+2.
\]

Every bad edge \(L_iR_j\) has the unique shortest blue geodesic

\[
L_i-u-w-v-R_j.
\]

The union of all shortest supports therefore has \(2t+2\) edges. For
\(t\ge3\),

\[
t^2>2t+2,
\]

so shortest-support Hall expansion fails. The ratio
\(t^2/(2t+2)\) tends to infinity.

## Proof certificate

Index each large class by \(\mathbb Z_t\). The cycles

\[
L_iA_jB_{i+j}C_iD_jE_{i+j}R_jL_i
\qquad (i,j\in\mathbb Z_t)
\]

are \(t^2\) pairwise edge-disjoint 7-cycles. Hence every cut has at least
\(t^2\) bad edges. The alternating class cut has exactly the \(t^2\)
edges of \(L-R\) bad.

At equality every edge outside the packed cycles must cross. These are
the thin-channel edges. Their crossing forces all of \(L\cup R\) onto one
shore and \(u,v\) onto the other, so all \(L-R\) edges are bad. This
determines the maximum cut up to complementation.

## Verification

Primary checker:

    python -B problems/23/writeup/_codex_support_hall_family_verify.py --max-t 8 --exact-max-t 5

Independent checker:

    python -B tmp/paper_family_independent/verify_family.py

The independent audit exhausts all cuts for \(t=1,2\), all twin-class
cut-count orbits for \(t=3,4\), and checks the structural certificate
through \(t=8\).

