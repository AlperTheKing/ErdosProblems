# GPT: Coherent P5-block lemma PROVED (sharp 25); full P5 gap = (Sync). chat 6a3b5aba.

## PROVED -- Coherent P5 separation lemma
Notation: dH(S) := E_H(S, V minus S) for H in {B,M}. Let A subset V, F (oriented bad edges) with:
  (u,v) in F  =>  u in A, uv in M, dB(A,v)=4   (coherence (Coh)); no underlying bad edge twice; q=|F|.
Layers L_i = {x: dB(A,x)=i}, prefixes P_i = L_0 ... L_i (i=0..3), a_i=|L_i|.

CLAIM: 25q > N^2  =>  exists i in {0,1,2,3} with |dM(P_i)| > |dB(P_i)|  (P_i an improving switch).

PROOF:
 (1) every F-edge crosses every prefix (first end in A=L_0 subset P_i, second in L_4 subset complement) => |dM(P_i)| >= q.
 (2) B-edges change dB(A,.) by <=1 => dB(P_i) = E_B(L_i, L_{i+1}) => |dB(P_i)| <= a_i a_{i+1}.
 (3) q <= a_0 a_4  (F subset L_0 x L_4).
 (4) If a_i a_{i+1} >= q for all i=0,1,2,3, then with (3) the FIVE pair-products
     (a0 a1)(a1 a2)(a2 a3)(a3 a4)(a4 a0) = (a0 a1 a2 a3 a4)^2 >= q^5. AM-GM: a0..a4 <= (N/5)^5 (disjoint, sum<=N).
     => q^5 <= (N/5)^10 => (25q)^5 <= (N^2)^5 => 25q <= N^2, contradiction.
 (5) so some i has a_i a_{i+1} < q => |dM(P_i)| >= q > a_i a_{i+1} >= |dB(P_i)|.  QED.
The sharp constant 25 = 5^2 comes from the 5-cycle of pair-product inequalities. Lean-ready.

## The GAP: per-edge dB(u,v)=4 does NOT give a single coherent (A, F) with q=|M|.
Obstructions: (a) coherence would force M bipartite (CD does not imply this); (b) multi-source
contamination -- a target v can be at distance 2 from another source u' in A while its own partner is at
distance 4, so that bad edge falls into L_2 and stops crossing later prefixes.

## COUNTEREXAMPLE to the global-layering mechanism (NOT to the P5 bound)
M = C5 on x_0..x_4 (edges x_i x_{i+1}). For each i add y_i,z_i,w_i and B-path Q_i: x_i-y_i-z_i-w_i-x_{i+1}
(internally + edge disjoint). X={x_i,z_i}, Y={y_i,w_i}. Triangle-free; every bad edge has dB=4; CD holds
(each crossed bad edge forces an edge of its disjoint Q_i to cross => injection dM(S) into dB(S)). But M=C5
is NOT bipartite, so NO global A places one endpoint of every bad edge in L_0 and the other in L_4. N=20,
m=5, 25m=125 < 400=N^2 (so the P5 bound itself is fine; only the global-layering MECHANISM is refuted).

## The exact missing lemma (Sync) -- the genuinely hard target now
If 25|M| > N^2, then exist A subset V and oriented F subset M with coherence (u in A, dB(A,v)=4) and
  25|F| > n_A^2,  where n_A := sum_{i=0..4} |L_i(A)|.   (Sync)
Then the coherent lemma returns an improving prefix. Full chain:
  25|M|>N^2  =(Sync)=>  25|F|>n_A^2  =(five layers, PROVED)=>  exists S: |dM(S)|>|dB(S)|.
The second implication is DONE. (Sync) is the open core.

## Coarea form of the same gap
CD  <=>  sum_{uv in M} |f(u)-f(v)| <= sum_{uv in B} |f(u)-f(v)|  for all f: V->R  (layer-cake integral of CD).
Coherent family: f_A(v)=min(dB(A,v),4) stretches every F-edge by exactly 4, threshold cuts = the prefixes.
For arbitrary M, each bad edge has its own potential dB(u,.); combining them into ONE scalar f is exactly
the synchronization gap. Next target = (Sync), not more prefix manipulation.
