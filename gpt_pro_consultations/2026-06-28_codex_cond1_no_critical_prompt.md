# GPT-Pro consult prompt (Codex) — Schur condition (1), NO-CRITICAL / NO-Q-ONLY

I need one concrete new proof lemma, not a survey.

We are working on Erdős Problem #23, already reduced to the following spectral setup.

Let G be a triangle-free graph on N vertices with a fixed maximum cut. Let B be the cut-edge graph
(bipartite, connected), and let M be the bad/monochromatic edges. For each bad edge f=(a,b), define
ell(f)=d_B(a,b)+1 >= 5 and p_f(v)=fraction of shortest a-b B-geodesics through v. Let P[v,f]=p_f(v),

  K = P P^T,    K[v,w] = sum_f p_f(v)p_f(w) >= 0,
  T(v) = sum_w K[v,w] = sum_f ell(f)p_f(v).

The whole remaining conjecture would follow from SPEC: rho(K) <= N, equivalently ROWSUM-O:

  for every bad edge f,   sum_v p_f(v) S(v) <= N, where S(v)=sum_g p_g(v).

Claude is attacking ROWSUM-O / the full Schur row-sum. I am attacking Schur condition (1):

  A_QQ = N I - K_QQ is a nonsingular Stieltjes M-matrix,

where O={v:T(v)>N} and Q=V\O. The elementary part is done:

1. K_QQ >= 0 and every Q-row sum is <= T(q) <= N, so rho(K_QQ) <= N.
2. Therefore A_QQ is a symmetric singular-or-nonsingular M-matrix.
3. Decompose Q into K_QQ-components. In a component C, row sum at q is

     s_q = sum_{q' in C} K[q,q'] = T(q) - leak(q),
     leak(q)=sum_{o in O} K[q,o].

   Hence rho(K_C)=N iff every q in C has T(q)=N and leak(q)=0.

So condition (1) reduces exactly to:

  NO-CRITICAL: no K_QQ-component C has T(q)=N and leak(q)=0 for every q in C.

Equivalently, there is no nonzero nonnegative N-eigenvector of full K supported entirely in Q and vanishing on O.

Important verified facts:

* If the load-bearing K-graph {v:T(v)>0, edges K[v,w]>0} is connected, NO-CRITICAL follows by Perron-Frobenius:
  a critical component would give a nonnegative N-eigenvector vanishing on O, contradicting strict positivity of the
  Perron vector on an irreducible nonnegative matrix.
* Exact census N<=11, overloaded blowups to N<=24, random triangle-free tests: 0 exceptions. The load-bearing K-graph
  is connected whenever O is nonempty.
* SAT-LEAK is a sufficient but possibly too-strong form:

     every saturated underloaded q with T(q)=N has leak(q)>0.

  Exact census N<=11: 0 violations. Saturated examples show every bad-edge interval through q also touches O.

What is ruled out:

* The finite-depth Neumann / k2 proof of the Schur row-sum is false at N=23, Myc(Grotzsch); do not use fixed finite
  depth.
* Per-edge or fixed-coefficient local SOS proofs are false. The proof must use global odd-girth/triangle-free
  structure.
* A naive "critical component is a smaller counterexample" is not immediately valid because B-boundary edges to the
  outside may be what make the inherited cut maximal.

The exact structural meaning of leak=0:

  leak(q)=0 means no bad-edge interval contains both q and an overloaded vertex.

For a critical component C, every bad edge f whose interval/support meets C has its entire support disjoint from O;
also C is K-closed: K[q,w]=0 for q in C, w outside C. Thus all shortest-geodesic intervals touching C stay in a
load-saturated, O-invisible region.

Question:

Give one concrete lemma, with proof outline, that would rule out such a critical component using triangle-freeness
and maximum-cut/CD. Ideally one of:

1. Prove load-bearing K-connectivity when O is nonempty;
2. Prove SAT-LEAK: if T(q)=N then some bad-edge interval through q must also contain an overloaded vertex;
3. Prove a compact-support top-eigenvector obstruction: no nonzero x>=0 supported off O can satisfy Kx=Nx unless
   O is empty / uniform extremal;
4. Or identify a checkable additional inequality I can exact-test before investing in the proof.

Please avoid proposing:

* fixed finite Neumann truncation;
* per-edge bounds independent of the global interval family;
* applying the conjecture recursively to the component without handling inherited max-cut/CD;
* generic "use Perron" statements, since the irreducible case is already done.

I need a specific next lemma/certificate and how triangle-freeness enters.
