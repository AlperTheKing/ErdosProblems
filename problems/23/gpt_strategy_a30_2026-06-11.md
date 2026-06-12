CONTEXT:
We are attacking Erdős problem #23.  For a triangle-free graph G, let
beta(G)=e(G)-maxcut(G), the minimum number of edges to delete to make G
bipartite.  Let a(n)=max beta(G) over triangle-free n-vertex graphs.
Erdős conjectured a(5m)<=m^2, sharp for the balanced blow-up of C5.

VERIFIED LOCAL RESULTS:
1. a(25)=25 has a T1 proof in our workspace:
   assume beta(G)>=26 on 25 vertices.  BCL high-density theorem forces
   e(G)<=95.  Delete two vertices of degree <=7; the vertex-deletion inequality
   beta(G-v)>=beta(G)-floor(d(v)/2) gives a 23-vertex triangle-free graph with
   beta>=20 and e<=95.  McKay/OEIS a(23)=20 extremal catalogue has six graphs,
   all with at least 100 edges. Contradiction.
2. For a(30)=36, a counterexample would be triangle-free on 30 vertices with
   beta>=37.  BCL high-density gives e<=139.  Thus min degree <=9.
3. If min degree r<=3, deleting a min-degree vertex gives a 29-vertex graph
   with beta>=36, contradicting the BCL global bound floor(29^2/23.5)=35.
   So only r=4..9 remain in our rooted finite search.
4. A blunt SAT/CEGAR search over 29-vertex beta>=33, e<=139 is too broad and
   stalled.  Rooted 30-vertex branches r=8,9 at high edge counts were
   inconclusive under limited SAT budgets.

CURRENT QUESTION:
Find a mathematical route to prove a(30)=36 or produce a sharper finite
certificate that is substantially smaller than brute-force rooted SAT.

Please attack this as a proof problem, not a compute-only problem.

Possible directions:
- Can the a(25)=25 proof be strengthened using McKay's 23-vertex extremal
  catalogue plus three/four vertex deletions with degree-sum constraints?
- Can a 30-vertex counterexample with beta>=37 and e<=139 be forced into a
  medium/high-density stability structure close to a C5 blow-up, then ruled out
  by integer part sizes?
- Can the BCL/Andrásfai-Erdős-Sós low-degree theorem or known triangle-free
  max-cut inequalities force a deletion set S of size 5 with
  sum_{deleted in order} floor(d_current(v)/2) <= 11, reducing to a(25)=25?
- Is there a degree-sequence or discharging lemma: every triangle-free
  30-vertex graph with e<=139 and beta>=37 has a reducible vertex/edge/structure?

REQUIREMENTS:
- Give rigorous lemmas with proof sketches detailed enough to verify.
- Clearly separate known theorems from new candidate lemmas.
- If you propose using literature, name exact theorem/hypotheses; flag uncertain
  citations.
- If no proof route is visible, propose the smallest finite certificate or
  targeted computation that would be genuinely informative.
- End with weakest steps and go/no-go route assessment for #23.
