We are working on Erdős Problem #23 in a graphon/blow-up proof pipeline. Please do not propose finite SAT/census enumeration; the finite step is already done. I need one concrete proof idea for the lemma below.

Setting:

Let G be a triangle-free graph on N vertices. Fix a maximum cut whose cut-edge graph B is connected, and among those choose a cut minimizing

    Gamma = sum_{f in M} ell(f)^2,

where M is the set of same-side edges ("bad edges"), and ell(f)=dist_B(a,b)+1 for f=ab in M, with dist_B measured in the connected cut graph B. For each bad edge f=ab, let P_f be the set of shortest B-geodesics from a to b. Define

    p_f(v) = (# shortest B-geodesics in P_f containing v) / |P_f|.

The load is

    T(v) = sum_{f in M} ell(f) p_f(v).

Define the positive kernel

    K(v,w) = sum_{f in M} ell(f)^2 p_f(v) p_f(w)

up to the usual normalization; equivalently K(v,w)>0 iff some bad-edge geodesic support contains both v and w. Let O={v:T(v)>N}. A positive-K component is a connected component of the graph on vertices with T>0 where v~w iff K(v,w)>0.

For a B-edge e=xy, define its geodesic traffic

    mu(e)=sum_{f in M} sum_{P in P_f: e is a consecutive edge of P} ell(f)/|P_f|.

Thus mu(e)=0 means no shortest odd-cycle geodesic uses that cut edge.

Verified facts:

1. The target SPEC/rho(K)<=N is reduced to three Schur/M-matrix conditions. Condition (1) is equivalent to excluding a critical Q-only K-component: no positive-K component C disjoint from O may have T(v)=N for all v in C.

2. If C is such a critical component, every B-boundary edge from C is zero-mu, and the endpoint in C has T=N. Therefore the following lemma proves condition (1).

Main candidate lemma (SAT-ZMU-CONN):

    In any connected-B maximum cut minimizing Gamma, if O is nonempty and a zero-mu B-edge e=uv has T(u)=N, then the positive-K component of u intersects O.

This is tie-invariant: exact verification found 0 violations for every gamma-min cut in the full N<=11 triangle-free census, plus a known N=12 tie-caveat graph, blow-ups, Mycielskians, and glued-island adversarial constructions.

Useful exact identity:

    sum_{B-edges e incident to v} mu(e) = 2*T(v) - D(v),

where D(v)=sum_{bad edges f incident to v} ell(f). This handshake alone is not enough because one incident B-edge could have mu=0 while the others carry the traffic.

Equivalent/weaker fallback that still proves condition (1):

For every positive-K component C disjoint from O, define

    deficit(C)=N*|C|-sum_{v in C} T(v).

Let sat_boundary(C) be the number of B-boundary edges xy with x in C, y outside C, and T(x)=N. Candidate:

    deficit(C) >= sat_boundary(C).

This weaker pooled inequality also excludes a critical Q-only component because then deficit(C)=0 and B-connectedness with O nonempty gives sat_boundary(C)>=1. Exact scans: no violations in selected-load full N<=11; Claude is stress-testing broader gates.

Known dead ends / caveats:

- Full ZMU is false: a zero-mu B-edge can have both endpoints with positive T.
- The stronger statement "zero-mu edge with saturated endpoint forces O empty" is false for some equal-Gamma cuts; a tie-caveat graph has T(u)=N on a zero-mu leaf edge while u is K-connected to O. That is why SAT-ZMU-CONN is the right tie-invariant statement.
- Deleting the T=0 dead region is not stable. In an O-empty N=10 example, a zero-load B-subnetwork forces the gamma-min cut; deleting it changes Gamma.
- Pure per-vertex deficit is false; if a proof exists, it likely uses gamma-minimality/max-cut switching or a component/coarea argument.

Request:

Give one concrete route to prove SAT-ZMU-CONN or the weaker SAT-BOUNDARY-DEFICIT. I want a lemma with a proof skeleton that uses gamma-minimality of the cut and the geodesic definitions above. Avoid broad surveys and avoid finite checking. If your route needs a computable intermediate inequality, state it explicitly so I can exact-test it.
