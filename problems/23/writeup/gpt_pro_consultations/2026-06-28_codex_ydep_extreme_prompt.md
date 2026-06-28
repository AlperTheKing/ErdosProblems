I am working on Erdős Problem #23. Step-1 finite certificates are done; the remaining conjecture is reduced to one inequality.

Core objects:

- G triangle-free, B a connected maximum cut graph, M bad edges.
- For a bad edge f=(a,b), ell(f)=d_B(a,b)+1. Shortest B-geodesics define p_f(v), with layer sets I_i(f), i=0..ell(f)-1, and sum_{v in I_i(f)} p_f(v)=1.
- S(v)=sum_g p_g(v), T(v)=sum_g ell(g)p_g(v).
- Need prove any equivalent form:
  ROWSUM-O: for every f, sum_g <p_f,p_g> = sum_v p_f(v) S(v) <= N.
  SPEC: rho(P^T P)<=N.
  LPD: for all y>=0,
    sum_f (sum_i sqrt(w_{f,i}))^2 <= N sum_v y_v,
    where w_{f,i}=sum_{v in I_i(f)} y_v p_f(v).
  CORR/Hellinger Hall equivalent:
    sum_f sum_{i<j} sqrt(w_{f,i} w_{f,j})
      <= 1/2 sum_v (N-S(v)) y_v.

Known dead routes:
- fixed cut-metric/Crofton certificates fail;
- ordinary subset Hall/maxflow too weak;
- fixed y-independent corridor flow is too rigid;
- alpha0/uniform y-dependent routing fails on hard graphs;
- over-broad O-K-SUPPORT/connected K-component claims are false on glued islands. Saturation-qualified statements only.

Current CAGE certificate route:

For each bad edge f and each layer pair i<j, choose a routing alpha from that layer-pair demand to B-edge gates e at gaps t in [i,j). The route polytope for each f has:

1. For every layer pair (i,j), sum_{eligible gates g} alpha_{ijg}=1.
2. For every gate g=(f,t,e), sum_{pairs crossing t and using e} alpha_{ijg}=H_t*pi_{t,e}, where pi_{t,e} is the fraction of shortest f-geodesics using e at gap t and H_t=sum_{i<=t<j}1/(j-i).

Given alpha, define per gate two vector measures A_g and B_g from the left/right layer distributions. A fixed CAGE certificate asks for ratios r_g>0 such that
  sum_g (r_g A_g(v)+r_g^{-1} B_g(v)) <= N-S(v) for all v.
Then AM-GM implies CORR.

New exact/algebraic facts:

1. Total surplus identity:
   total slack = N^2 - Gamma - sum_g m_g (r_g+r_g^{-1}-2),
   where m_g=H_t*pi_{t,e}. Thus extremals force r_g=1 on positive mass gates; strict cases fail only distributionally.

2. Fixed-r Farkas/Hall theorem:
   For fixed r, CAGE feasible iff for all lambda>=0,
     sum_f OT_f(lambda,r) <= sum_v lambda_v (N-S(v)),
   where OT_f transports unit layer-pair demand to gate capacities with cost
     r_g <lambda,p_{f,i}> + r_g^{-1}<lambda,p_{f,j}>.

3. y-dependent sufficient condition:
   For a fixed y, if there exists alpha(y) such that
     sum_g 2 sqrt((A_g.y)(B_g.y)) <= sum_v (N-S(v))y_v,
   then CORR holds for that y. For fixed y, this objective is concave in alpha on each f-polytope, so a minimum is attained at an extreme point.

Diagnostics:

- On hard graph I?BD@g]Qo, alpha0/uniform y-dependent route fails at its worst y by +0.027634728.
- Fixed adaptive CAGE alpha passes by -0.009481126 at that same y.
- Random extreme-point sampling per f improves to -0.015879155.
- On N=22 blow-up witness J???E?pNu\?[2], alpha0 fails by +0.144055985; fixed adaptive passes by -0.223890869; random extremes improve slightly to -0.226105772.

Observed support pattern on I?BD@g]Qo:

The hard graph has three bad edges, all ell=5. For each f, the sampled best extreme route is sparse: most layer pairs route to a single gate; only a few pairs split. Fractions are forced rational leftovers such as 35/36, 34/36, 11/12, 5/6, 3/4. This suggests the right y-dependent proof might be an interval-transport extreme-point rule or a Monge/uncrossing rule, not a smooth fixed-ratio rule.

Question:

Give one concrete proof direction or lemma that could turn the y-dependent extreme-point CAGE observation into CORR. I do not want a survey. I need a checkable statement: either

1. a deterministic construction of alpha(y) from the layer weights w_{f,i} and gate capacities H_t*pi_{t,e};
2. a min-max / dual certificate for the y-dependent extreme routing problem;
3. a Monge/uncrossing inequality showing a particular class of extreme routes suffices; or
4. a KKT-core obstruction whose infeasibility follows from triangle-free corridor disjointness.

Please state the proposed lemma precisely enough that I can send it to an exact verifier. Avoid suggesting already-refuted ordinary subset Hall, fixed y-independent flow, or broad K-component support claims.
