# GPT-Pro (Claude's chat "Spectral Inequality Proof") — ρ(K)≤N route: ODD-CYCLE CIRCULANT MAJORANT + GREEN-CAPACITY DOMINATION

Retrieved 2026-06-28 by Claude via Claude-in-Chrome. chatgpt.com/c/6a40e163-609c-83eb-90b0-72643ecbc55b, Kapsamlı Pro, "Thought 13m 7s".

## The route: K ⪯ M := diag(T) − L_ω ⪯ N·I

**Local canonical model.** For a bad edge f=ab, ℓ=ℓ(f); each shortest B-geodesic Q=(v0=a,...,v_{ℓ-1}=b) closed with
ba gives an odd cycle C(f,Q) of length ℓ. Cycle Laplacian L_{C_ℓ}, J_ℓ=11ᵀ. Sharp odd-cycle coeff
a*_ℓ := ℓ/(2+2cos(π/ℓ)); then J_ℓ + a*_ℓ L_{C_ℓ} ⪯ ℓ I_ℓ. RATIONAL weaker coeff (use this for exact testing):
   ā_ℓ := ℓ³/(4(ℓ²−2))  ≤ a*_ℓ  (ℓ≥5 odd),  and  J_ℓ + ā_ℓ L_{C_ℓ} ⪯ ℓ I_ℓ.   Note ā_ℓ > ℓ/4 (bipartite baseline).

**Edge traffic.** τ_f(e) := Pr_{Q∈P_f}(e ∈ E(C(f,Q))). So τ_f(f)=1; for e∈B, τ_f(e)=fraction of f's shortest
geodesics using e; τ_f(e)=0 for other bad edges. L_{τ_f} = weighted Laplacian with weights τ_f(e). Local comparison:
   (LC)   p_f p_fᵀ + ā_{ℓ(f)} L_{τ_f} ⪯ ℓ(f) diag(p_f).
[Automatic: p_f p_fᵀ = E[q_Q]E[q_Q]ᵀ ⪯ E[q_Q q_Qᵀ], q_Q = incidence vector of cycle C(f,Q).]

**Global.** ω(e) := Σ_{f∈M} ā_{ℓ(f)} τ_f(e); L_ω weighted Laplacian on B∪M. Since Σ_f ℓ(f)diag(p_f)=diag(T):
   (1)   K + L_ω ⪯ diag(T),  i.e.  K ⪯ M := diag(T) − L_ω.   [M−K PSD, NOT entrywise-nonneg.]

## KEY LEMMA to prove/exact-test
**(GCD) ODD-CYCLE GREEN-CAPACITY DOMINATION:  L_ω + diag(N−T) ⪰ 0,  i.e.  L_ω ⪰ diag(T−N).**
Combined with (1): K ⪯ diag(T) − L_ω ⪯ N·I ⟹ ρ(K) ≤ N. QED SPEC.

**Schur-capacity form (best exact diagnostic).** O={T>N}, Q=V\O, D_O=diag(T−N on O), R_Q=diag(N−T on Q).
   (CAP)  L_{ω,OO} − L_{ω,OQ} (L_{ω,QQ} + R_Q)† L_{ω,QO} ⪰ D_O.
(L_{ω,QQ}+R_Q is the Green operator on the non-overloaded region, grounded by deficit N−T>0 + the ω-boundary;
its effective capacity on O must dominate the overload diagonal. Finite-depth Neumann of (L_{ω,QQ}+R_Q)† loses long
Mycielski corridors — that is why the (k2) finite-depth proxy failed at N=23; the full Green kernel is the global object.)

**Stability (STAB).** H:=L_ω+diag(N−T). NI−K = (M−K) + H. For Perron u≥0 of K:
   N−ρ(K) = uᵀ(M−K)u/uᵀu + uᵀHu/uᵀu  ≥ λ_min(L_ω + diag(N−T)).
Right deviation functional = Green-capacitary ground energy λ_min(L_ω+diag(N−T)), NOT raw Σ(T−N)². Equality forces the
constant mode on every positive-traffic cycle component + Hu=0 ⟹ T≡N ⟹ uniform C_{2k+1}[t] blow-up (the extremal).

## EXACT-TESTABLE CERTIFICATE (Claude's job)
Per instance: compute τ_f(e) ∀ f∈M, e∈B∪M; ω(e)=Σ_f [ℓ(f)³/(4(ℓ(f)²−2))] τ_f(e); H=L_ω+diag(N−T); CHECK H ⪰ 0.
Stronger: replace ā_ℓ by a*_ℓ=ℓ/(2+2cos(π/ℓ)) (real algebraic). If the rational version passes ⟹ clean exact cert.
File to write: _gcd.py.
