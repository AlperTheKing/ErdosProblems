# GPT-Pro consult (Claude Step-2) — proving SPEC ρ(K)≤N after the finite-depth route died at N=23

## The fully reduced problem (everything below SPEC is a PROVEN exact identity)

Triangle-free graph G on N vertices, a fixed maximum cut; B = cut (bipartite) edges, M = bad (monochromatic) edges.
Triangle-free ⟹ every bad edge f=(a,b) closes an odd cycle of length ℓ(f)=d_B(a,b)+1 ≥ 5. For a bad edge f let
p_f(v) ∈ [0,1] be the fraction of shortest a–b B-geodesics through v (Σ_v p_f(v)=ℓ(f)). Let P be the V×M matrix
P[v,f]=p_f(v), and

  K := P Pᵀ,  K[v,w]=Σ_f p_f(v)p_f(w) ≥ 0,  with row sums (K·1)[v]=T(v):=Σ_f ℓ(f)p_f(v) ("load").

**Reduction (all proven, exact):** Γ:=Σ_f ℓ(f)² ≤ N²  ⟸  **SPEC: ρ(K) ≤ N**. [Proof: O:=PᵀP is PSD, ρ(O)=ρ(K);
ℓᵀOℓ = Σ_v T(v)² ≤ ρ(O)·Σℓ² = ρ(K)·Γ ≤ NΓ; Cauchy–Schwarz Σ_v T² ≥ (ΣT)²/N = Γ²/N (since ΣT=Γ); so Γ²/N ≤ NΓ
⟹ Γ ≤ N². Then triangle-free ℓ≥5 ⟹ β=|M| ≤ Γ/25 ≤ N²/25, the whole conjecture.] So **the entire remaining Erdős #23
is exactly SPEC: ρ(K) ≤ N.**

## What is proven about SPEC, and what just died

We attacked SPEC via A := N·I − K ⪰ 0, splitting V into overloaded O={T>N} and underloaded Q={T≤N}, using the Schur
complement E = A[O,O] − A[O,Q] A[Q,Q]⁻¹ A[Q,O]:
- **PROVEN:** the implication (cond1)+(cond3) ⟹ A ⪰ 0 ⟹ SPEC (Schur congruence + Sylvester inertia; non-circular).
- **PROVEN:** cond2 (E off-diagonal ≤ 0) is automatic given cond1 [E[o,o′] = −K[o,o′] − K[o,Q]·M·K[Q,o′] ≤ 0,
  M=(N·I−K_QQ)⁻¹ ≥ 0].
- **cond1** (A[Q,Q] nonsingular Stieltjes M-matrix) reduces to ONE connectivity lemma: K restricted to {T>0} is
  connected ("NO-Q-ONLY"); proven *given* that irreducibility via a Perron lever. Verified 0-exception census N≤11 +
  blow-ups N≤24 + random N≤15. (Codex's leg.)
- **cond3** (the true full-depth Schur row sum E·1_O = r_O + K[O,Q]·(N·I−K_QQ)⁻¹·r_Q ≥ 0, r=N−T) — **the genuine hard
  inequality.** (My leg.)

**What died (false-closure, caught exactly):** we had a finite-depth proxy "(k2): the k=2 Neumann truncation of cond3
≥ 0", verified 0-violation over census N≤11 + i.i.d. blow-ups N≤24. It is **FALSE** on the iterated Mycielskian
C5→Grötzsch(N=11)→Myc(Grötzsch)(N=23): at the overloaded high-incidence vertex o=22, (k2)·N² =
−10842333408378828581/28344980104623000 < 0 (exact). The first nonnegative Neumann depth there is k=3, and the
required depth grows with N — **no fixed finite Neumann depth proves cond3.** (The true full-depth row sum is still
+6.561 > 0 there, and ρ(K)=20.04 ≤ 23, so SPEC and the certificate hold; only the finite-depth proof strategy is dead.)

## Empirical structure of SPEC (exact + float, to guide the approach)

- ρ(K) ≤ N holds with strict margin everywhere EXCEPT the C5[t] / C_{2k+1}[t] blow-up extremals, where T ≡ N
  (uniform load), ρ(K)=N exactly, and the tight (null) eigenvector of N·I−K is the **constant vector** (Perron vector
  of K). Away from the extremal the margin GROWS (min-eig(N·I−K): 0 at extremal, +0.74 at N=11 near-extremal, +2.13 at
  N=22, +2.96 at N=23).
- No fixed-coefficient per-edge or per-pair SOS can certify SPEC: exact witness J???E?pNu? vertex o=9 needs per-edge
  constant κ ≥ 2.93 but the minimum-over-edges κ is 2.87 — SPEC survives there only because heavy edges (p_f(o)=1)
  correlate with large load-coupling. So the proof must use a **global correlation / anti-concentration** of the
  p_f-measure against the load field, not a local bound.
- Adding the B-graph Laplacian raises min-eig(N·I−K) (the soft mode is high-frequency on B, vanishing at the extremal
  where it is the constant vector).

## The two surviving routes (equivalent in strength; both = SPEC)

- **ROUTE A (one clean inequality):** ROWSUM-O — for every bad edge f, Σ_v p_f(v)·S(v) ≤ N, where S(v)=Σ_g p_g(v).
  Then Perron (O ≥ 0 symmetric) gives ρ(O) ≤ max row sum ≤ N. Survives N=23 (max row sum 19347/910 = 21.26 < 23).
- **ROUTE B:** cond1 (connectivity, Codex) + cond3 (true full-depth Schur row sum ≥ 0, me).

## My questions

1. **Which route, and which tool?** Given that (a) tightness occurs ONLY at the uniform-load C_{2k+1}[t] extremal with
   the constant null vector, and (b) no fixed-coefficient SOS works, is the right vehicle a **spectral comparison
   K ⪯ M** to an explicit odd-cycle / circulant "model operator" M with ρ(M)=N built from odd-girth ≥ 5 (so that
   N·I−K = (N·I−M) + (M−K) with both PSD)? If so, what is the canonical M for this geodesic-incidence K, and what is
   the key inequality making M−K ⪰ 0 (or M−K entrywise-dominant)?

2. **Or a stability/rigidity argument around the extremal:** since the only equality case is T≡N and the null mode is
   constant, can SPEC be proven by a quantitative "spectral gap from the extremal" — i.e. N − ρ(K) ≥ c·(deviation of T
   from uniform), exploiting that odd-girth ≥ 5 forbids the local configurations that would let a non-constant mode
   reach eigenvalue N? What is the cleanest deviation functional?

3. **For ROUTE A directly (ROWSUM-O):** Σ_v p_f(v)S(v) ≤ N is a correlation between the geodesic measure p_f (mass ℓ(f)
   on a shortest odd cycle's interval) and the total incidence field S. What odd-girth-≥5 structural fact bounds this
   correlation by N — is there a "corridor/interval separation" argument (bad-edge endpoints cannot share a B-neighbor,
   so distinct geodesic intervals overlap in a controlled way) that yields it non-circularly?

Please pick the single most promising of these and give the concrete key lemma to prove (and, if helpful, where odd-
girth ≥ 5 enters non-trivially — it must, since SPEC is false for general graphs).
