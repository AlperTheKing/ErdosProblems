I am working on a proof sublemma in the reduction of Erdős Problem #23.
Please focus on the exact lemma below; do not propose broad LP/cut-metric
certificates, generic Menger arguments, or census-only evidence.

Setup.

Let G be a finite triangle-free graph. Fix a maximum cut whose cut-edge graph
B is connected; among those cuts choose one minimizing

    Gamma = sum_{bad edge f} ell(f)^2,

where bad edges M are monochromatic edges and ell(f)=d_B(a,b)+1 for f=(a,b).

For a bad edge f, let p_f(v) be the fraction of shortest B-geodesics between
the endpoints of f that pass through v. Define

    T(v) = sum_f ell(f) p_f(v).

For a cut edge e in B define geodesic traffic

    mu(e) = sum_f sum_{shortest B-geodesics P for f using e}
            ell(f) / #(shortest B-geodesics for f).

We have the exact handshake identity

    sum_{e incident to v, e in B} mu(e) = 2 T(v) - D(v),

where D(v)=sum_{bad edges f incident to v} ell(f).

The target lemma, exact-tested with no violations, is:

    SAT-ZMU-CLASS:
    If mu(uv)=0 and T(u)=N=|V(G)|, then T(v)=0 and O is empty,
    where O={x:T(x)>N}.

This immediately implies the Schur/M-matrix condition needed in the reduction:
a critical K-component has T=N on all vertices and its B-boundary edges have
mu=0, so SAT-ZMU-CLASS would force O empty.

Known facts and guardrails.

1. The stronger statement "mu(e)=0 implies a T=0 endpoint" is false. There is
   a glued C5 + Myc(C7) bridge with O nonempty and a zero-mu bridge whose
   endpoints have positive non-saturated loads 5 and 15/2.

2. The target only concerns a saturated endpoint T=N.

3. Exact evidence:
   - Full census through N=11 and many blowups/gadgets: no violations.
   - Non-vacuous examples exist. In N=10 there are 146 saturated-zero-mu
     incidences; all are O-empty and the other endpoint has T=0.
   - In N=11 there is 1 such incidence, same behavior.

4. Important correction: the T=0 endpoint need not be a B-leaf. Example:

      graph6 I??CF@wFo, N=10
      side = [0,0,0,1,1,1,1,1,0,0]
      bad edges M = [(1,8),(2,8)]
      loads T = [0,5,5,5,5,0,0,10,10,10]
      zero-mu cut edge (7,0), with T(7)=10=N and T(0)=0.
      Bdeg(0)=2, so not a leaf.
      mu on B edges:
      (0,7)=0, (0,6)=0, (5,9)=0, (6,9)=0,
      and the positive geodesic core uses (1,7),(2,7),(7,9),(3,8),
      (3,9),(4,8),(4,9).

   Thus the correct picture is a zero-load, zero-traffic B-subnetwork, not
   necessarily a pendant vertex. Deleting all T=0 vertices is not stable:
   for I??CF@wFo, deleting vertices with T=0 changes the recomputed gamma-min
   Gamma from 50 to 25.

5. If T(v)=0 then v has no bad-edge degree and every incident B-edge has
   zero traffic. This is immediate from the definitions and handshake.

Please give one concrete proof idea for SAT-ZMU-CLASS or a sharper lemma that
would imply it. The desired mechanism is likely gamma-minimality: if O were
nonempty and a saturated vertex had an unused incident B-corridor, perhaps one
can switch the zero-traffic subnetwork or reroute the max cut to lower Gamma
without decreasing cut size. But the non-leaf example above means a simple
pendant deletion proof is invalid.

I need a mathematically safe lemma stated explicitly, preferably in terms of:

    - a zero-traffic B-subgraph Z={vertices/edges with T=0 or mu=0},
    - max-cut domination delta_M(A) <= delta_B(A),
    - Gamma-minimality among connected-B maximum cuts,
    - or a local cut switch that preserves maximum cut size but reduces Gamma.

Please avoid suggesting anything that would be refuted by I??CF@wFo.
