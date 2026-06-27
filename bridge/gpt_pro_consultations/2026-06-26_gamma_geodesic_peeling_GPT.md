# GPT Pro: GEODESIC ODD-CYCLE PEELING for the Connected-B Gamma Lemma (theta regime)

Chat 6a3e68cf, "Graph Theory Problem". GPT Pro (Comprehensive), thought 10m56s. Drove the browser myself.

## The angle (NOT theta-contraction)
A literal theta-ear contraction is the WRONG primitive: the tight witness c5paths20 already has N²−Γ=0, so any
strictly-deficit-decreasing op turns a tight valid object into a negative-deficit one unless it also removes the
correct Γ-mass. The op must be EQUALITY-PRESERVING on C5[q]-type tightness and strict only off the extremal family.

## The structural primitive = GEODESIC ODD-CYCLE PEELING
For a bad edge uv∈M, take a shortest B-geodesic P = u=v_0,v_1,…,v_{ℓ-1}=v (ℓ=d_B(u,v)+1). Then P+uv is an odd
cycle of length ℓ in G with exactly ONE bad edge. C := V(P), |C|=ℓ. DELETE C; recompute B-distances and Γ in G−C.
Let L(C) := Γ(G) − Γ(G−C).

The right equality step is "remove one whole C5 unit": N² − (N−5)² = 10N−25 is exactly the Γ-mass lost by one
C5-transversal in the extremal blow-up. On C5[q] (N=5q, |C|=5): the lost bad edges are exactly 2q−1, each ℓ=5,
so L(C) = 25(2q−1) = 50q−25 = 10N−25 = 2·5N−25. EQUALITY-preserving on C5[q] incl. q=4 (N=20).

## THE LEMMA TO PROVE (the new target)
> Every connected-B theta-regime instance with Γ ≥ N² contains a SAFE geodesic odd-cycle peel C with
>   L(C) ≤ 2|C|N − |C|².
Then (N²−Γ) → ((N−|C|)²−Γ(G−C)) is non-increasing (0→0 on tight family, strict elsewhere) ⟹ induction to
smaller N ⟹ base case. Replaces "flatten theta into one 5-shell certificate" with "peel one balanced C5-atom,
let the theta persist at smaller N."

## CONCRETE FIRST TEST — Safe 5-peel lemma for c5paths20
In c5paths20 (N=20, Γ=400) there is a bad edge uv∈M with d_B(u,v)=4 and a shortest B-geodesic
u=v_0,v_1,v_2,v_3,v_4=v such that, for C={v_0..v_4}:
 (1) G−C still satisfies CUT-DOMINATION:  δ_{M−C}(S) ≤ δ_{B−C}(S)  ∀ S⊆V∖C;
 (2) every remaining bad edge lies in a single connected component of B−C;
 (3) Γ(G−C) = 225, i.e. L(C) = 400−225 = 175 = 2·5·20 − 5².
So the peel gives (20,400) → (15,225), with 20²−Γ=0 → 15²−Γ'=0.

## EXACT CHECK TO IMPLEMENT
For each candidate shortest bad geodesic P: C=V(P), s=|C|. Compute B'=B[V∖C], M'=M[V∖C].
Check cut-domination exactly: ∀S⊆V∖C, |δ_{M'}(S)| ≤ |δ_{B'}(S)|  (equivalently the obstruction form
  δ_B(S) − δ_M(S) ≥ e_B(S,C) − e_M(S,C)  ∀S⊆V∖C).
Recompute distances in B' (component by component), Γ' = Σ_{ab∈M'} (d_{B'}(a,b)+1)².
ACCEPT the peel if Γ − Γ' ≤ 2sN − s². For c5paths20 restrict first to s=5 (d_B=4); target s=5,Γ=400,Γ'=225,L=175.
If no peel works, the failing case is the next structural obstruction to study.

## NEXT (my plan, per [[gpt-pro-decides-path]])
1. Build c5paths20 explicitly (ear_invariant.py has the theta witness).
2. Implement the peel test: enumerate shortest bad geodesics, peel C, check (1)(2)(3) + L≤2sN−s².
3. If it passes on c5paths20, sweep ALL connected-B theta instances (N≤11..) for the existence of a safe peel
   (the lemma). A single instance with Γ≥N² and NO safe peel = the new obstruction.

---
## MY EMPIRICAL PROBE (cd_probe.py) — while GPT reasons on the proof (2026-06-26)
Fixed a double-subtraction bug (CD-in-(G-C) is just delta_{B'}(S)>=delta_{M'}(S), NO extra edges-to-C term).
For a FIXED bad edge, enumerated ALL odd B-cycles through it (shortest + longer), peeled each:
- C5[2]: |C|=5 SHORTEST CD-min=0 (OK) L=75<=75 SAFE; |C|=7 CD-min=0 L=100>91 UNSAFE; |C|=9 CD-min=0 L=100>99 UNSAFE.
- C5[3]: |C|=5 SHORTEST CD-min=0 (OK) L=125<=125 SAFE; |C|=7 CD-min=-1 (CD BREAKS) L=175>161 UNSAFE.
FINDINGS: (1) shortest peel CD-preserved with EQUALITY (min delta_{B'}-delta_{M'}=0) at the same S where the
original CD is tight, loss e_B-e_M=0 there => equality-preservation (GPT's design goal) is automatic on C5[q].
(2) 'SHORTEST is essential' is enforced primarily by condition (iii) L<=2|C|N-|C|^2: a shortest geodesic deletes
the MINIMAL |C|=d_B+1 vertices for Gamma-mass ~ |C|^2 per bad edge; longer odd cycles delete more vertices
w/o proportional Gamma-drop => L overshoots (and CD can also break). So minimality is a Gamma-ACCOUNTING
necessity. The crux of proving (iii) = bounding distance-growth of remaining bad edges after deleting C
(condition (ii), no disconnection) so Gamma' doesn't drop too much.
