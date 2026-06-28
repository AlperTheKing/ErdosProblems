We are proving the remaining delta=0 step of Erdos Problem #23 for triangle-free graphs. Please focus on one concrete lemma, not a survey.

Setup:
- Let G be triangle-free on N vertices.
- Fix a maximum cut whose cut-edge graph B is connected, and among such cuts choose one minimizing
  Gamma = sum_{f in M} ell(f)^2, where M is the set of monochromatic/bad edges and
  ell(f)=d_B(a,b)+1 for bad edge f=(a,b).
- For bad edge f, p_f(v) is the fraction of shortest B-geodesics from a to b passing through v.
- Define K(v,w)=sum_f p_f(v)p_f(w) and T(v)=sum_w K(v,w)=sum_f ell(f)p_f(v).
- Let O={v:T(v)>N}. For Schur condition (1), it is enough to prove that there is no critical K-component entirely in Q=V\O.

Candidate lemma, exact-tested with rational arithmetic:
For every full K-component C with C cap O empty,
    sum_{v in C} (N - T(v)) >= d_B(C),
where d_B(C) is the number of B-edges crossing from C to V\C.
Equivalently, since a full K-component contains whole bad-edge geodesic supports,
    Gamma_C + d_B(C) <= N |C|.

This passed:
- full triangle-free census N<=11 locally;
- Claude independent stress: named graphs, overloaded blow-ups, N=22 witness, Myc(Grotzsch) N=23, Myc(C7) N=15, full N<=10.

Important dead ends:
- Pointwise strengthening T(v)+deg_B(v,V\C)<=N is false.
- Pointwise route N-T(v) >= deg_B(v)-inc_cut(v), where inc_cut is geodesic B-incidence at v, is false at N=8 graph G?`F`w.
- In all tested graphs with O nonempty, nontrivial proper Q-only K-components do not occur; so the lemma is a hypothetical underload-isoperimetry needed to rule them out, not an observed frequent structure.

Need:
Give one plausible proof mechanism for the underload-isoperimetry lemma above, or a sharper sufficient lemma just for the critical case:
    if C is a proper full K-component, C cap O empty, d_B(C)>0, then not all T(v)=N on C.

Useful facts:
- If C is a full K-component, no bad-edge geodesic support straddles C. Thus every bad edge either contributes entirely inside C or is disjoint from C.
- Therefore boundary B-edges crossing C carry zero shortest-geodesic traffic for bad edges supported in C.
- Max-cut gives for every X: delta_M(X)<=delta_B(X).
- Gamma-minimum among connected-B maximum cuts may be needed; boundary B-edges unused by the K-component feel like they should force strict slack or allow a lower-Gamma cut if C were internally saturated.

Please propose a concrete lemma/argument that can be exact-tested, ideally in terms of max-cut first variation, Gamma-minimality, or a Hall/transport charging of boundary B-edges to underload inside C.
