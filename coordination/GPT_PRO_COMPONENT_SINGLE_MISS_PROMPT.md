We are proving the remaining K2T Hall/SDR lemma in the Erdős #23 delta=0 proof.

Do not propose arbitrary leakage/subdiagram inequalities, guard-petal identities, scalar Hall, or broad switch certificates; these were exact-disproven. I need one proof atom for the component-local residual theorem below.

Setup:

- G is triangle-free.
- We fix a connected-B maximum cut; B=cut edges, M=bad monochromatic edges.
- For each bad edge f, ell(f)=d_B(endpoints)+1>=5 and cyc[f] is the set of shortest B-geodesics joining its endpoints.
- S is a selected completed seed+moat terminal-shadow switch from a vertex with R[v]<0.
- C=delta_M(S), E=delta_B(S). S is neutral: |C|=|E|.
- Terminal-shadow property: for every f in C and every Q in cyc[f], oriented from the endpoint tau_f inside S, Q cap S is an initial terminal prefix, exits S exactly once through some e in E, and then stays outside S.
- Wit(e)={f in C : some shortest f-geodesic exits S through e}. lambda(e)=min_{f in Wit(e)} ell(f).
- Safety for noncrossing bad edges holds, but the current residual theorem mostly uses C/E/Wit.

Stage0:

- L0=min_{f in C} ell(f).
- F0={f in C : ell(f)=L0}; F1=C\F0.
- E0={e in E : lambda(e)=L0}.
- Match F0 into E0 with minimum total rare cost deg_F1(e)=|Wit(e) cap F1|. Delete the used exits.
- Let R be the remaining exits. Consider the residual bipartite graph H between F1 and R, with f~e iff f in Wit(e).

Exact facts already verified on the full live domain:

1. Every residual connected component (A,B) of H is balanced: |A|=|B|.
2. Every non-universal exit e in B is witnessed by at least two rows f in A.
3. The following stronger component-local single-miss theorem passes exact tests:

   For every residual connected component (A,B), every f in A misses at most one e in B.

Together these imply Hall:
- If B\Y has size >=2, every f sees some exit outside Y, so no f is trapped in Y.
- If B\Y={e}, trapped f are exactly those missing e; since e has degree at least 2, at most |A|-2=|Y|-1 rows are trapped.

Important guardrail:
The single-miss statement is false globally. Exact diagnostic:
global row_miss_count={0:923,1:72,3:18,8:48}, but component_row_miss_count={0:989,1:72}.
So the proof must use residual component separation. A row may miss many exits in different components.

The 72 component-local singleton misses split into:
- 40 long-lambda singleton misses: missed exit has lambda(e)=ell(f)=7 in the tested atoms.
- 32 min-lambda singleton misses: missed exit has lambda(e)=L0=5 while f has ell(f)=7.

Request:
Give a rigorous combinatorial proof of the component-local single-miss theorem, or the smallest exact-testable lemma that implies it.

The proof should use:
- terminal-prefix shortest-geodesic geometry,
- triangle-free / odd-girth >=5,
- residual connectedness in H,
- and the rare stage0 minimum-cost property only where needed.

A plausible split:

(A) Long-lambda miss: If one longer row f misses two long-lambda exits e1,e2 in the same residual component, then the terminal prefixes and component witness paths create a theta/lens giving a shorter B-geodesic for some crossing bad edge or a triangle.

(B) Min-lambda miss: If one longer row f misses two minimum-lambda exits in the same residual component, then those exits lie in the same side block that f avoids, and rare stage0 should have consumed all but at most one of them; otherwise an alternating exchange in the F0-E0 matching lowers total deg_F1.

Please do not merely restate Hall. I need a proof mechanism for why two missed exits cannot remain in one residual component.
