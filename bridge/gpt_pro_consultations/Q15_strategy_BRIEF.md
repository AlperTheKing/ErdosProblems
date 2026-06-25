# Q15 BRIEF — STRATEGIC: what is the most promising route to prove CF (Step 2 of Erdős #23)?

User-directed: the τ_K/Clebsch local route is exhausted; ask GPT Pro how to proceed and follow its advice.
This is a STRATEGY question (not a single lemma): given everything proved and ruled out below, what is the
most promising route to a COMPLETE proof of CF (hence Step 2), and what is the concrete FIRST provable lemma
on that route? Audit-grade; be honest about feasibility.

## Problem
Erdős #23: triangle-free G on N=5n vertices ⟹ β(G)=e−MaxCut(G) ≤ n², sharp at the balanced C5-blow-up C5[n].
A finite computation (Step 1, in progress) gives the base a(30)=36. Step 2 (this) must prove the general-n
reduction. We reduced Step 2's open core to **CF**: for triangle-free G, e edges, N vtx, band x=e/N²∈[0.1243,0.16],
`τ_K(G) ≤ RHS:=(N²/5−e)/2`, where K=Clebsch graph (16 even subsets of [5], A~B iff |A△B|=4) and
`τ_K(G)=min_{φ:V→V(K)} Σ_{uv∈E}(4−|φ(u)△φ(v)|)/2`. CF ⟺ sup over band tri-free G of R(G)=τ_K/RHS ≤ 1
(R blow-up-invariant). CF ⟹ Step 2 via the 5-cut bound β ≤ (e+2τ_K)/5 and blow-up transfer (all proved+audited).

## PROVED + AUDITED (machine-verified)
- 5-cut bound β≤(e+2τ_K)/5; blow-up homogeneity τ_K(F[k])=k²τ_K(F); CF⟹β≤N²/25=n², equality ⟺ C5[n].
- τ_K(G) ≤ e−4e²/N² (density-only); τ_K ≤ (3/2)β; A7: {C3,C5}-free ⟹ β≤N²/32 (handles the C5-free corner).
- Clebsch character structure c(A,B)=(3+Σσ_iσ_i)/4; exact star-extension Q(d)=3⌊d/4⌋+[d%4∈{2,3}];
  per-vertex recursion τ_K(G)≤τ_K(G−v)+Q(d_v); Lemma: every 2-centre ball N[x]∪N[y] of a tri-free graph is
  Clebsch-hom; Mycielski recursion τ_K(M(G))≤3τ_K(G)+Q(n) ⟹ iterated Mycielskians have R→0.
- Local CHARGING identity at a 1-opt-stable φ: 8cost(φ)=Σ_v(3d_v−Σ_i|s_{v,i}|+2ε_v m_v), s_{v,i}=Σ_{u∈N(v)}σ_i(φu).
- 21-vertex stable-neighborhood polytope; sharp 2nd-moment bound F_v≥(3/5)Q_v/d_v (3/5 optimal); global
  identity Σ_v Q_v=10e−6W_0+2W_1+10W_2.

## EVIDENCE CF IS TRUE (machine-verified)
- Finite census: ALL triangle-free in-band graphs N≤12 (~804k) have R≤0.40, 0 with R>1.
- Hardest non-Clebsch-hom case (5-chromatic Mycielskian M(M(C5))): R=0.402. Worst R found anywhere ≈0.40.
- At the GLOBAL τ_K-minimizer, the charging inequality (★) F≥10e−0.8N² HOLDS on every graph tested (incl.
  the cases that broke local routes). So CF appears robustly TRUE with margin (≈0.40·RHS).

## RULED OUT (each: an explicit IN-BAND graph with τ_K=0 — CF true — where the local certificate overshoots RHS)
1. **4-template flag COVERAGE** (edge/C5/Petersen/Clebsch rooted certs, order ≤18): FALSE — witness the
   Grötzsch=M(C5) weighted blow-up (x=0.159, τ_K=0); a primal-witness graphon kills any order-≤18 flag-SDP.
2. **Vertex/2-centre-ball DELETION bound** (Σ Q(d_j)): too loose — witness uniform Grötzsch[5]+iso; the
   constant 3/4 per boundary edge ⟹ (3/4)·(deletion-distance Θ(N))·N = Θ(N²), same order as RHS but loose.
3. **1-opt local CHARGING** (the inequality (★) at a 1-opt-stable φ): FALSE — witness K_{16,64} (x=0.16) with
   all 16 labels uniform per shore is 1-opt-stable with ΣF_v=0 (so (★) fails by 0.8N²) yet τ_K=0.
4. **2nd-moment route via F≥(3/5)R** (eq 9: 6H_1+12H_2≥17e−N²−6n_+): too lossy — fails even at the GLOBAL
   minimizer on most graphs, although (★) itself holds there. The (3/5) coefficient (tight only at one vertex
   type) loses too much when summed.

## META-FINDING (we believe, and want your judgment)
CF is **irreducibly global**: no purely-local / flag-of-bounded-order / single-vertex-stable certificate can
prove it — each fails on an explicit τ_K=0 in-band witness. CF is essentially equivalent to the conjecture in
the band. The hard part is purely PROVING (★)/CF at the GLOBAL minimizer (it holds there but with no local
certificate). Also refuted earlier: frustration-stability ("small τ_K ⟹ near-C5[n]") — small τ_K only forces
the Clebsch-HOM class, which strictly contains non-extremal blow-ups (e.g. C5[m]⊔K_{r,r}, τ_K=0).

## THE STRATEGIC QUESTION
Given all the above, what is the MOST PROMISING route to a complete, rigorous proof of CF (or directly of
β≤n² for band triangle-free graphs), and what is the concrete FIRST provable lemma on that route? Please
assess these candidates and/or propose a better one, with honest feasibility:
(a) the exact PEELING lemma β(G)≤β(G−S)+2n−1 for a 5-set S (induction ⟹ n²) — we have a finite test (Λ₅)
    with 0 violations on all blow-up bases r≤10, but a factor-~2.5 obstruction: the optimal cut must extract
    >50% of the edges meeting the removed C5-transversal, and greedy gives only 50%;
(b) a STABILITY theorem (a notion that DOES force proximity to C5[n], unlike Clebsch-hom) + exact finite cleanup;
(c) a direct flag-algebra SDP for β=e−MaxCut≤N²/25 (MaxCut is not a subgraph density — is there a valid
    flag/Lagrangian formulation, e.g. via the cut-norm or a vertex-weighting, that certifies exactly?);
(d) a global potential / discharging for (★) at the τ_K-minimizer that uses 2-opt (swap) stability, not just
    1-opt — the K_{16,64} bad labeling is 1-opt-stable but NOT 2-opt-stable; does 2-opt stability + triangle-
    freeness close (★)?
(e) something else entirely (spectral, entropy/container, a different target graph than Clebsch, weighted
    symmetrization with a proved unweighted conversion, …).

Deliverable: a prioritized recommendation with the single most promising route, the concrete first lemma to
prove on it, and the main risk. I will machine-check any concrete lemma on small graphs.
