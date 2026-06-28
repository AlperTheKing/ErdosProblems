# Condition (1): A_QQ = N·I − K_QQ is a nonsingular Stieltjes M-matrix

Context (Schur-complement M-matrix certificate for SPEC: ρ(K) ≤ N, K = PPᵀ, P[v,f] = p_f(v)).
T = K·1 (loads), O = {v : T[v] > N} (overloaded), Q = V\O (underloaded, T[q] ≤ N), A = N·I − K.
Condition (1) asks: **A_QQ := N·I − K_QQ is a nonsingular symmetric M-matrix (Z-matrix with
entrywise-nonnegative inverse, i.e. Stieltjes ⟹ PSD)**, where K_QQ = K[Q,Q].

## What is PROVEN (rigorous, elementary)

**(P1) K_QQ ≥ 0 entrywise.** K[v,w] = Σ_f p_f(v)p_f(w) with p_f ≥ 0. ∎

**(P2) Row-sum bound.** For q ∈ Q,
  Σ_{q'∈Q} K[q,q'] ≤ Σ_{w∈V} K[q,w] = (K·1)[q] = T[q] ≤ N.
(The first inequality drops the nonnegative terms with w ∈ O; the last uses q ∈ Q underloaded.) ∎

**(P3) ρ(K_QQ) ≤ N.** K_QQ is entrywise nonnegative with all row sums ≤ N; for a nonnegative
matrix the spectral radius is ≤ the maximum row sum (Perron–Frobenius / ‖·‖_∞ bound). ∎

**(P4) A_QQ = N·I − K_QQ is a symmetric Z-matrix that is PSD and an M-matrix.** Off-diagonals
−K[q,q'] ≤ 0 (Z-matrix). By (P3) every eigenvalue λ of K_QQ satisfies λ ≤ ρ(K_QQ) ≤ N, and K_QQ
symmetric PSD gives 0 ≤ λ ≤ N, so N − λ ≥ 0: A_QQ ⪰ 0. A symmetric Z-matrix with ρ(offdiag-part)
≤ diagonal is an M-matrix. ∎

**(P5) Stieltjes ⟹ inverse ≥ 0, when nonsingular.** Classical: a nonsingular symmetric M-matrix
(equivalently a Z-matrix that is PD) has entrywise-nonnegative inverse (Stieltjes matrix). So
**(1) holds as soon as A_QQ is NONSINGULAR**, i.e. as soon as ρ(K_QQ) < N strictly. ∎

So condition (1) is equivalent to the single strict-spectral statement

> **(STRICT)  ρ(K_QQ) < N**   (for every triangle-free config with O ≠ ∅, B connected).

## Exact reduction of (STRICT) to a clean combinatorial lemma

Decompose Q into the connected components of the graph {q ~ q' : K[q,q'] > 0}. Because distinct
components carry no K_QQ mass between them, **A_QQ is block-diagonal across components**, so
det A_QQ = Π_C det(N·I_C − K_QQ|_C) and A_QQ is nonsingular iff every block is. (Verified exactly:
the per-component product of block determinants equals det A_QQ over the full census N ≤ 11.)

Within an irreducible (KQQ-connected) component C, the K_QQ|_C row sum at q equals
  s_q := Σ_{q'∈C} K[q,q'] = Σ_{q'∈Q} K[q,q'] = T[q] − leak[q],  leak[q] := Σ_{o∈O} K[q,o] ≥ 0.
By Perron–Frobenius for an irreducible nonnegative matrix, ρ(K_QQ|_C) ≤ max_q s_q ≤ N, **with
ρ(K_QQ|_C) = N iff all row sums in C equal N**, i.e. s_q = N for every q ∈ C. Since s_q = T[q] −
leak[q] with T[q] ≤ N and leak[q] ≥ 0, s_q = N forces **T[q] = N and leak[q] = 0** for all q ∈ C.

Call a component C **critical** if every q ∈ C has T[q] = N and leak[q] = 0. The above is an exact
equivalence:

> **ρ(K_QQ) < N  ⟺  no critical KQQ-component exists.**

A sufficient *per-vertex* condition is

> **(SAT-LEAK)  every saturated underloaded vertex (q ∈ Q, T[q] = N) has leak[q] > 0.**

SAT-LEAK ⟹ no vertex is simultaneously saturated and leak-free ⟹ no critical component ⟹ (STRICT)
⟹ condition (1). (A second, independent sufficient lemma also holds empirically:
**(O-ISO-SINGLETON)** every KQQ-component with leak ≡ 0 on it is a single vertex {q}; a singleton
block is N − K[q,q] ≥ N − S(q) ≥ N − T(q)/5 > 0, immediately giving (STRICT).)

## COMPLETE rigorous proof in the irreducible case (the irreducibility lever)

**Claim (critical ⟹ eigenvector vanishing on O).** If a critical KQQ-component C exists, then N is
an eigenvalue of the FULL matrix K with a nonnegative eigenvector x ≥ 0, x ≠ 0, that VANISHES on O.

*Proof.* C is **K-closed in V**: for q ∈ C and w ∉ C, if w ∈ O then leak[q] ≥ K[q,w] = 0 forces
K[q,w] = 0; if w ∈ Q\C then K[q,w] = 0 because C is a full KQQ-component. So K[q,w] = 0 ∀ q∈C, w∉C.
Let x ≥ 0 be the Perron eigenvector of the (irreducible) block K|_C, extended by 0 off C. For q ∈ C:
(Kx)[q] = Σ_{w∈C}K[q,w]x[w] = N x[q] (critical ⟹ row sums in C equal N ⟹ Perron root N). For w ∉ C:
(Kx)[w] = Σ_{q∈C}K[w,q]x[q] = Σ_{q∈C}K[q,w]x[q] = 0 (K-closedness, symmetry). Hence Kx = Nx; and
x = 0 on O since O ∩ C = ∅ (C ⊆ Q). ∎

**Theorem (condition (1), irreducible case — FULLY PROVEN).** If K restricted to its support
{v : T[v] > 0} is irreducible (i.e. the K-graph {v ~ w : K[v,w] > 0} is connected on the load-bearing
vertices), then ρ(K_QQ) < N, so A_QQ is a nonsingular Stieltjes M-matrix and condition (1) holds.

*Proof.* If not, ρ(K_QQ) = N (by P3 + PSD), so a critical component C exists and the Claim gives a
nonnegative eigenvector x ≥ 0 of K at eigenvalue N with x = 0 on O ≠ ∅. For an irreducible
nonnegative matrix, the ONLY eigenvalue admitting a nonnegative eigenvector is the Perron root
ρ(K) (Perron–Frobenius), and its eigenvector is strictly positive. So N = ρ(K) and x > 0 everywhere
on the support — contradicting x = 0 on O. ∎

This proves condition (1) outright whenever K is irreducible. **Exactly verified:** over the full
census N ≤ 11 the only K-graph disconnections are an isolated load-free vertex (T = 0, i.e. no
bad-edge geodesic passes through it) split off from one big component — never a nontrivial split
(K-graph DISCONNECTED counts at N=11: 98, ALL of the form [1, big]; in every case the size-1 piece is
a T=0 vertex). So in the census every load-bearing K-graph is connected ⟹ irreducible ⟹ condition (1)
proven. The residual (reducible) gap is the single combinatorial lemma:

> **(NO-Q-ONLY)  no K-graph V-component carrying a bad edge (size ≥ 5) lies entirely in Q,**

equivalently its weaker sufficient form **(NO-CRITICAL)** = "no SATURATED Q-only K-component". Both
are verified 0-violation over the full census N ≤ 11 (756 with-O graphs), overloaded blow-ups to
N ≤ 24, and 4 000 random triangle-free graphs per N for N = 12..16.

## Exact verification (Fraction arithmetic)

- Full triangle-free census **N ≤ 11** (90 842 connected graphs at N = 11; 756 of them have O ≠ ∅):
  - row-sum bound (P2): 0 violations;
  - per-component block-diagonal identity Π det(block) = det A_QQ: exact, 0 mismatch;
  - every block det > 0, inverse(A_QQ) ≥ 0: 0 violations;
  - **no critical component**: 0 (over all 756 with-O graphs);
  - **SAT-LEAK**: 0 violations (23 saturated underloaded vertices at N = 11, min leak +1.533);
  - **O-ISO-SINGLETON**: every O-isolated component is a singleton (max O-iso component size = 1).
- Overloaded blow-ups C·[t] to **N = 16, 18, 20, 22, 24, …** (G?bF`w, H?bBF_{, I?BD@g]Qo,
  J???E?pNu\?, J?`@C_W{Ck?, …): SAT-LEAK 0-violation (min leak among saturated +3.6 at N = 18),
  no critical component, all O-iso components singletons, block dets > 0, inverse ≥ 0.

Files: `_cond1_proof.py` (full exact cert + census), `_cond1_strict.py` (block-diagonal-by-component
reduction + no-critical-component), `_sat_leak.py` (SAT-LEAK census), `_blow_satleak.py` (blow-up
stress), `_crit_probe.py` (O-iso component sizes), `_sat_dump.py` (local structure of saturated
vertices). All EXACT rational.

## Status (summary)

1. **(P1)–(P5) PROVEN (elementary):** K_QQ ≥ 0, row sums ≤ N, ρ(K_QQ) ≤ N, A_QQ ⪰ 0 is a Z-matrix;
   condition (1) ⟺ ρ(K_QQ) < N (strict), and strictness ⟹ Stieltjes ⟹ inverse ≥ 0.
2. **Exact reduction PROVEN:** ρ(K_QQ) < N ⟺ no critical KQQ-component (per-component Perron).
3. **Irreducible case FULLY PROVEN:** if K|_{T>0} is irreducible, a critical component would give a
   nonnegative K-eigenvector at eigenvalue N vanishing on O ≠ ∅, contradicting Perron positivity.
   Hence condition (1) holds for every config whose load-bearing K-graph is connected.
4. **Coverage = entire verified range (EXACT, full census):** over the full census N ≤ 11
   (every connected triangle-free graph; 756 with O ≠ ∅) the load-bearing K-graph K|_{T>0} is
   connected with **0 exceptions at every N = 7..11** (`_load_connected.py`: K|_load DISCONNECTED = 0
   at N = 11 over all 756 with-O graphs); likewise for every overloaded blow-up tested to N ≤ 24
   (e.g. the N = 22 witness J???E?pNu\?[2]: det A_QQ = 1.495e21 > 0, inverse ≥ 0, K|_load
   irreducible). The only K-graph disconnections that occur are load-free T = 0 isolated vertices
   (split off as [1, big]), which lie outside L and do not affect irreducibility of K|_L. So the
   irreducible-case theorem proves condition (1) for the ENTIRE census + blow-up range — there is
   NO instance in the residual case.
5. **Residual gap (single combinatorial lemma):** prove that K|_{T>0} is connected in general,
   equivalently **(NO-Q-ONLY)** no bad-edge-carrying K-component lies entirely in Q (its sufficient
   weaker form: no SATURATED such component). Verified 0-violation over census N ≤ 11, blow-ups to
   N ≤ 24, and 4 000 random triangle-free graphs per N for N = 12..16. This is the same global
   odd-girth anti-concentration obstruction as ROWSUM-O: the local condition is consistent at the
   linear level; ruling it out is a connectivity/rigidity fact, not a local count. Deliberate
   2-gadget constructions (overloaded C5-blow-up + separate odd cycle) FAIL to realize a Q-only
   component — the min-Γ max-cut either removes all overload or merges the K-components — which is
   structural evidence that NO-Q-ONLY is a genuine theorem.

**Bottom line:** condition (1) is PROVEN for every triangle-free configuration with an irreducible
load-bearing K-graph (which is every instance in the full census N ≤ 11 and every blow-up tested to
N = 24). The certificate's condition (1) is therefore NOT an obstruction on any verified case; the
only thing standing between this and an unconditional proof of condition (1) is the connectivity
lemma NO-Q-ONLY, an anti-concentration fact of the same family as the main ROWSUM-O inequality.
