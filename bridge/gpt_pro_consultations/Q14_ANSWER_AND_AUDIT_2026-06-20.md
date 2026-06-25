# Q14 (Rung 5) — the charging inequality (★): GPT ANSWER + Step-2 AUDIT (2026-06-20)

Chat "Triangle-free Graph Inequality" `c/6a36dbf8-9a10-83ed-bfc0-b417b619a20f`, Kapsamlı Pro (reasoned
~70 min wall / "21m33s" shown). NARROW ask (Rung 5): a 2nd-moment / discharging / finite-LP handle on the
charging inequality (★) `Σ_v Σ_i|s_{v,i}| − 2Σε_v m_v ≥ 10e − (4/5)N²` at a 1-opt-stable φ.
**Verdict: SOUND, ALL load-bearing claims VERIFIED (`verify_q14_audit.py`). A RIGOROUS NEGATIVE RESULT
plus sharp local machinery.** CF still UNPROVEN; the local-charging route is now RULED OUT.

## What GPT delivered (all audited)
**1. Stable-neighborhood polytope.** x_v=(σ_1(φv),…,σ_5(φv))∈H_+={x∈{±1}^5:∏x_i=1}. r_{v,i}=−x_{v,i}s_{v,i},
ρ_{v,i}=r_{v,i}/d_v. Then F_v:=Σ_i|s_{v,i}|−2ε_v m_v = d_vΣ_iρ_{v,i}, Q_v:=Σ_i s_{v,i}²=d_v²‖ρ_v‖².
b_{vu}=−x_v⊙x_u∈H_−(odd parity) ⟹ ρ_v=(1/d_v)Σ_{u∈N(v)}b_{vu}∈conv(H_−). **1-opt-stable at v ⟺
r_{v,i}+r_{v,j}≥0 ∀i<j** (size-2 flips ⟹ size-4).
**2. Lemma 2 — P has 21 vertices:** P=conv(H_−)∩{ρ_i+ρ_j≥0} = conv({0}∪{e_i}∪{e_i+e_j}∪{h_i}), h_i=(−1,1,1,1,1).
Ineq form ρ_i≤1, ρ_i+ρ_j≥0, Σρ_i≤3. **4 types up to S_5:** (0⁵),(1,0⁴),(1,1,0³),(−1,1⁴), with
(t,q)=(Σρ,‖ρ‖²)=(0,0),(1,1),(2,2),(3,5).
**3. Sharp local 2nd-moment bounds (VERIFIED):** by convexity q≤(5/3)t and ‖ρ‖≤t ⟹ **F_v≥√Q_v** and
**F_v≥(3/5)Q_v/d_v**; 3/5 is the LARGEST universal coefficient (tight at type h_i: F_v=3d_v, Q_v=5d_v²).
**4. Exact global 2nd-moment identity (VERIFIED 0/150):** κ(u,w)=|N(u)∩N(w)|; x_u·x_w=4c(φu,φw)−3 ⟹
`Σ_v Q_v = 10e − 6W_0 + 2W_1 + 10W_2`, W_j=Σ_{c(φu,φw)=j}κ(u,w). Triangle-free ⟹ κ=0 on edges (wedge counts).
**KEY:** cost-zero endpoint pairs contribute −3, so independence does NOT make it positive term-by-term.
**5. Reduced subtarget (eq 9):** with R=Σ_v Q_v/d_v=8n_+−6e+8H_1+16H_2 (H_j weighted wedges, weight 1/d_v at
apex) and Σ_v F_v≥(3/5)R, the 2nd-moment route proves (★) **iff** `6H_1 + 12H_2 ≥ 17e − N² − 6n_+`.
**6. Finite per-type LP:** every linear argument in (d_v, F_v, normalized first moments) reduces to the 21
types — but provably CANNOT imply (★), by the falsification below.

## ★ THE NEGATIVE RESULT (VERIFIED, load-bearing)
**G = K_{16t,64t}** (complete bipartite, triangle-free, N=80t, e=1024t²=(4/25)N², **x=0.16 = band top, IN
BAND**). Put all 16 Clebsch labels UNIFORMLY on each shore (t per label small shore, 4t big shore). Since
`Σ_{A∈V(K)} σ_i(A)=0` (VERIFIED, 8 of 16 even subsets contain i), every vertex sees **s_{v,i}=0 ∀i** ⟹
F_v=0, Q_v=0, ρ_v=0. Every single-vertex relabel costs 3d_v/4 regardless of A ⟹ **φ is 1-opt-stable**.
But Σ_v F_v=0 while (★)'s RHS = 10e−(4/5)N² = (4/5)N²>0 ⟹ **(★) FAILS by 0.8N²**. cost(φ)=¾e=0.12N² ≫
RHS=(N²/5−e)/2=0.02N². **Nevertheless τ_K(G)=0** (2-color: shores → an adjacent Clebsch pair; VERIFIED cost 0).
⟹ **CF holds, but (★) fails at a 1-opt-stable labeling.** AUDIT (`verify_q14_audit.py`): all confirmed —
N=80,e=1024,x=0.16, max|s_{v,i}|=0, ties=True, cost=768=3e/4, needed ΣF_v≥5120, τ_K 2-coloring cost=0.

**CONCLUSION (GPT, verified):** "1-opt stability, local neighborhood types, and triangle-freeness ALONE
cannot yield (★)." A successful continuation MUST use that φ is a GLOBAL cost minimizer via genuinely
nonlocal recoloring comparisons; the 21-type polytope isolates where the global constraints must enter.

## META-FINDING (honest, important): all LOCAL routes to CF are now RULED OUT
Three independent local-certificate routes each fail on an explicit IN-BAND graph with **τ_K=0** (CF true)
but the local bound overshooting RHS:
- **Q12:** 4-template COVERAGE — witness Grötzsch=M(C5) weighted blow-up (x=0.1587).
- **Rung 4:** Q-deletion bound — witness uniform Grötzsch[5]+iso (x=0.159); loose constant 3/4.
- **Q14:** 1-opt local charging — witness K_{16,64} (x=0.16).
⟹ **CF is irreducibly GLOBAL** (consistent with: CF ⟺ the conjecture in the band). No purely-local
certificate suffices; a global optimizer / nonlocal argument (or a genuinely different decomposition) is
required. This is real understanding of WHY CF is hard, not a proof of CF.

## Next (Rung 6 options)
- The wedge inequality (9) `6H_1+12H_2 ≥ 17e−N²−6n_+` is concrete but requires GLOBAL optimality of φ
  (the K_{16,64} bad-stable labeling violates it; the global min does not) — a fresh narrow GPT question
  could target (9) AT THE GLOBAL MINIMIZER, or ask whether (9) holds for the specific φ achieving τ_K.
- Alternatively pivot off τ_K entirely (the local machinery is exhausted): direct global MaxCut/SDP, or a
  global stability argument near C5[n]. CF remains UNPROVEN; do NOT mark solved.
