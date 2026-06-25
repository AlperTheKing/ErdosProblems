# GPT Pro BREAKTHROUGH idea (new chat 6a3b5aba): optimal-cut geodesic cosystole

Genuinely different route -- DON'T bound beta directly; re-encode via the GEOMETRY of one optimal cut.

## Setup
Pick a maximum cut V = X u Y. B = E(X,Y) (cut/good edges, BIPARTITE), M = E(X)+E(Y) (monochromatic/bad
edges). |M| = beta(G).

## Key structural facts (from max-cut optimality + triangle-free)
For every bad edge uv in M:
 - u,v lie in the SAME connected component of B. (Else flipping one component would cut uv without
   spoiling any B-edge -> better cut, contradiction.)
 - d_B(u,v) is EVEN and >= 4. (Same side => even; distance 2 => triangle u-w-v.)
 - So every bad edge is an ODD CHORD of B, with shortest certificate cycle length
   ell(uv) = d_B(u,v) + 1  in  {5, 7, 9, ...}.

## The new INVARIANT and target lemma
   Gamma(G,X,Y) = sum_{uv in M} ell(uv)^2.
   TARGET (GC):  Gamma(G,X,Y) <= N^2   for some maximum cut.
MECHANISM: ell >= 5 => ell^2 >= 25 => Gamma >= 25|M| = 25 beta. So Gamma <= N^2 ==> beta <= N^2/25.
Tight: balanced C5-blowup has every bad edge at d_B=4 (ell=5), Gamma = 25*(N^2/25) = N^2 (EXACT).
C7-blowup: ell=7, Gamma = 49*(N^2/49) = N^2, gives beta = N^2/49 < N^2/25.

## FIRST concrete lemma to attack (sharp, falsifiable, orthogonal to SDP/radius/codegree wall)
**P5-chord expansion lemma.** G = B u M triangle-free, B bipartite (sides X,Y), M subset of within-side
pairs, cut-domination (CD): for all S subset V, e_M(S, Sbar) <= e_B(S, Sbar) [max-cut optimality].
Assume every bad edge has d_B(u,v) = 4. Then |M| <= N^2/25.
EQUIVALENT (the separation form to implement first):
   If d_B(u,v)=4 for every uv in M and 25|M| > N^2, find S with e_M(S,Sbar) > e_B(S,Sbar).

## Proof strategy (coarea / min-cut)
Each bad edge's P5 certificate path has 5 "layers"; cut-domination forces all 5 layers >= the bad-edge
mass (flip U => |A|>=|V|; flip V => |D|>=|U|; flips of U u A, V u D symmetric). Balanced sharp case: all
5 layers equal mass => N >= 5 sqrt(|U||V|) => |U||V| <= N^2/25. Full lemma = non-block coarea: if 5-layer
expansion fails, the failed layer-prefix is an explicit improving flip S. General: |M_{2r}| <= N^2/(2r+1)^2;
mixed case by Cauchy/convexity over B-components. Then: P5-chord expansion => geodesic-square inequality
=> 25 beta(G) <= N^2.

## FIRST ACTION (per GPT): implement + computationally test the separation lemma (it is FALSIFIABLE).
