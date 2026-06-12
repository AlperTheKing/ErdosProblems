CONTEXT:
We are attacking Erdős #944 / Dirac k=4,r=1. A target means a finite
6-regular graph G which is 4-vertex-critical and has no critical edge
(i.e. no edge e such that G-e is 3-colourable). We want to prove no target
exists.

VERIFIED LEMMAS:
1. Local multiplicity: for every v and every 3-colouring phi of H=G-v, the
six neighbours of v have colour multiplicities (2,2,2).
2. Kempe balance: for any colour pair A,B and any (A,B)-Kempe component K in
H, if a_K=|K cap A cap N(v)| and b_K=|K cap B cap N(v)|, then a_K=b_K.
3. Accounting: for colour classes A,B,C in H,
   sum_{K in K_AB} |delta_G(K)| = 6|C|+2, cyclically.
4. Comparable same-colour non-neighbour reducibility: if x,y are nonadjacent
same-colour vertices in a deleted colouring and N(x)\{v} subset N(y)\{v}
(or reverse), the colouring extends after identifying/recolouring, so this is
impossible in a target.
5. Global terminal-list-criticality: fix v, H=G-v, and a in N(v). If A is the
colour assigned to v, define L_a on H by L_a(a)={A,B,C}, L_a(x)={B,C} for
x in N(v)\{a}, and L_a(x)={A,B,C} otherwise. Since edge va is not critical,
H is not L_a-colourable; since G is vertex-critical, every proper induced
subgraph of H is L_a-colourable. Thus H is globally inclusion-minimal
L_a-uncolourable.

BLOCKER:
We still cannot prove K6:
there exist v, phi, and a colour pair such that a non-singleton two-colour
Kempe component K touching N(v) has |delta_G(K)|=6.

QUESTION:
Please attack exactly this implication:

Assume, for contradiction, that G is a target and for one fixed v and every
3-colouring phi of H=G-v, every non-singleton two-colour Kempe component
touching N(v) has boundary at least 8. Combine the three Kempe decompositions
with the global terminal-list-criticality of H for the six terminal list
assignments L_a.

Can you derive a contradiction? The desired output is either:

1. a rigorous proof of K6 under the stated hypotheses; or
2. a precise explanation of why these hypotheses are still insufficient,
   preferably by constructing an abstract combinatorial countermodel to the
   Kempe/accounting/list-critical constraints; or
3. a strictly smaller lemma whose proof would finish K6 and is not just a
   restatement of no-critical-edge or vertex-criticality.

REQUIREMENTS:
- Do not re-prove only the local multiplicity/Kempe balance/accounting lemmas;
  those are already verified.
- If using list-critical graph theory, state the theorem exactly and cite only
  results you are confident exist.
- Focus on the interaction between whole-H L_a-criticality and Kempe
  expansion. One-pair averaging is known to be too weak.
- End by listing the weakest steps in your answer and whether you believe this
  route can realistically close #944.
