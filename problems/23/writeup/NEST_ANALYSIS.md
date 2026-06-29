# GPT-Pro NEST proposal — exact analysis (2026-06-28)

GPT-Pro (my chat, user-relayed) proposed NEST as a spectral-upgrade target for M-avg:
   NEST:  <S_A, S_B> <= N|B|   for all  B <= A <= M,   S_F(v)=sum_{f in F} p_f(v).
with a layer-cake proof NEST => SPEC (rho(O)<=N) and a "hot-core bundle" proof of M-avg via unit edge
congestion. Verdict after exact testing: NEST is EQUIVALENT to ROWSUM-O (not stronger), and the bundle
proof's crux (unit congestion) is FALSE.

## (1) NEST <=> ROWSUM-O  (so it is NOT a strengthening)
Algebra: A<=M => S_A <= S_M pointwise (p_f>=0). For B<=A:
   <S_A,S_B> <= <S_M,S_B> = sum_{g in B} <S_M,p_g> = sum_{g in B} ROWSUM(g) <= N|B|   if ROWSUM-O holds.
So ROWSUM-O => NEST; singleton B={f},A=M gives NEST => ROWSUM-O. EQUIVALENT.
Empirical (_nest_congestion_gate.py, exact): census N<=11, NEST-FAIL = ROWSUM-FAIL = 0 on every cut (never one
without the other). The layer-cake NEST=>SPEC is a re-derivation of the Perron row-sum bound, no new content.
Proving NEST = proving ROWSUM-O, equally hard.

## (2) Unit edge congestion W(x,y)<=1 is FALSE (the bundle-proof crux)
W(x,y) := sum_{f in M} (fraction of f-geodesics using edge xy)  [edge analog of vertex load S].
The BUNDLE-MAVG proof needs W<=1 to get S_i(x)<=|L_{i+1}|. Exact gate:
   census maxW: N7=1, N8=3/2, N9=2, N10=2, N11=7/3 (GROWS with N); CONG-FAIL N8=8..N11=58069.
   witnesses: K??CB@OBDOAp=2, K??CE@A{?]Fc=13/5, GDSKVG=3/2, M(Grotzsch)N23=13487/8190~1.65.
Fails from N=8, at NESTED/OVERLAPPING geodesics. Witness K??CB@OBDOAp (nested unique-path, ROWSUM tight=N):
edges (4,9),(4,10),(5,9),(5,11) carry W=2 (the two bad edges (6,11),(10,11) share sub-path 4-9-5-11).
=> the "coherent bundle with unit congestion" hypothesis does NOT hold at the hard nested cases; the HOT-CORE
BUNDLE LEMMA cannot be applied there. AND congestion is NOT even bounded by a constant: maxW grows with N
(7/3 at N=11, 13/5 at the band witness), so no factor-c congestion salvage works either.

## (3) Correct & keepable
- GPT-Pro's 3x3 PSD counterexample (1^T O1=16<=30=N|M| but rho>10) correctly shows M-avg alone does NOT give
  SPEC. Confirms M-avg insufficient (already known).
- The density-maximal HOT-CORE framework (a minimal M-avg counterexample has every edge hot) is a SOUND
  reduction; it just needs a per-core handle other than unit congestion (which is false). Open whether any
  handle works -- and even if it does it only proves M-avg (avg-only, insufficient for SPEC).

## Net
No breakthrough. NEST = ROWSUM-O repackaged; unit-congestion crux refuted at nested-overlap geodesics (same
structure that killed the variance strengthening, where ROWSUM is tight). Congestion is bounded by 2 in the
census (structural fact, factor-2 too weak). Same impasse, new angle. Files: _nest_congestion_gate.py.
