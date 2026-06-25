# GPT Pro Consultation — Erdos #23 STEP-1 a(30)<=36: closing min-degree r=4,5,6,7 (establishing delta>=8)

STEP-1 FINITE ONLY. Do NOT address the all-n conjecture. Goal: prove a(30) <= 36,
i.e. NO triangle-free graph G on 30 vertices has beta(G) = e(G) - MaxCut(G) >= 37.
Assume such G exists for contradiction; WLOG edge-maximal triangle-free.

## Established reductions (please take as given, but flag if any looks unsound)
1. Uniform blow-up transfer: G[t] (each vertex -> independent set of size t) is
   triangle-free on 30t vertices with beta(G[t]) = t^2 * beta(G) = 37 t^2 and
   density(G[t]) -> e(G)/450. With BCL (Balogh-Clemen-Lidicky) Thm 1.3 density
   bounds this makes e(G) <= 111 (low-density) and e(G) >= 144 (high-density)
   impossible. So the surviving window is 112 <= e(G) <= 143.
   [BCL global PROVEN bound: beta(H) <= |V(H)|^2 / 23.5 for large |V(H)|.]
2. A min-degree vertex v has degree r <= floor(2*143/30) = 9.
3. r <= 3 CLOSED: delete v; by beta(G) <= beta(G-v) + floor(deg v /2),
   beta(G-v) >= 37 - floor(r/2) >= 36 on 29 vertices. Blow-up (G-v)[t] gives
   beta >= 36 t^2 > (29t)^2 / 23.5 = 35.787 t^2, contradicting BCL-global
   (rigorous via t->inf; no finite-n use of an asymptotic theorem).
   ===> QUESTION 0: is this r<=3 argument correct?

## The finite enumeration
We reroot at an exact-codegree-2 nonedge (K=2, T=2 model, four R-labels
E/S1/S2/D) and exhaustively close 387 profile-side instances over q=6..14 by
exact state-count CP-SAT (every instance INFEASIBLE; zero FEASIBLE found so far).
**This enumeration assumes / covers only min-degree branches r0 in {8,9}.**

## THE PROBLEM (the question)
To conclude a(30)<=36 from the 387-instance closure we must also rule out a
medium-window (112<=e<=143, beta>=37) counterexample of MINIMUM DEGREE
r = 4, 5, 6, or 7. Equivalently: establish delta(G) >= 8.

Obstacles already found (so please go beyond these):
- Single deletion + blow-up FAILS for r=4..7: beta(G-v) >= 37 - floor(r/2) is
  35 (r=4,5) or 34 (r=6,7); since 35, 34 <= 35.787, no contradiction with
  BCL-global on 29 vertices.
- Pure deletion / min-degree arithmetic DP leaves r=4,5,6,7 with open edge slices.
- Andrasfai-Erdos-Sos (triangle-free, delta > 2N/5 = 12 => bipartite) only gives
  delta(G) <= 12 (an upper cap; wrong direction).

QUESTION: give the cleanest RIGOROUS route to close r=4,5,6,7 (establish
delta>=8). Candidate directions to evaluate (pick/repair the best, or propose
your own):
  (a) iterated deletion to 29,28,... vertices with a finite a(29)/a(28) bound
      (does a clean finite bound a(29)<=34, a(28)<=..., follow from blow-up +
      BCL, or need its own enumeration?);
  (b) a finite min-degree lemma forcing delta>=8 for triangle-free beta>=37 on
      30 vertices (any known theorem? e.g. a quantitative
      Andrasfai-Erdos-Sos / chromatic-threshold result giving structure, not just
      bipartiteness?);
  (c) extend the K=2,T=2 reroot enumeration to r0 in {4,5,6,7} (what is the
      blow-up in instance count / feasibility?);
  (d) a stability/maximality argument (edge-maximal triangle-free => structure
      that forces delta>=8 in the medium window);
  (e) it is a genuine gap requiring its own dedicated finite certificate.

Give the key inequality / structural lemma for the recommended route, and
explicitly flag any step that is only heuristic vs rigorous. Keep it to Step-1
(a(30)<=36) — finite, exact.
