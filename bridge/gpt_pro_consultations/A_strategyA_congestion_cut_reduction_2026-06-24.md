# Strategy A breakthrough: lemma (16) reduces to a SHARP COAREA/CUT inequality on ATOMS (no rotation)

Date 2026-06-24. Claude session. All numerics in bridge/flagsdp/ (scripts named below). The "signature
rotation" obstruction DISSOLVES once you pass to the LP saddle; the real open core is a single-cut coarea
inequality that is the multi-layer generalization of the PROVED coherent-P5 block lemma (sharp 25).

## 1. Saddle collapse: a SINGLE signature suffices (no mixing)
LP duality for (16): kappa* = max_{w>=0,|w|=1} min_{omega} sum_a w_a L_omega(a). For a FIXED min signature S
the private cycles are independent over e, so the inner min is
  min_S sum_{e in S} ( w_e + d^B_w(u_e,v_e) ),   d^B_w = w-shortest path in B=K-S.
AUDITED (strategy_a_probe.py, validate_single_sig.py): at the dual-optimal worst toll w*, EVERY signature
attains the same cost = kappa*, and a SINGLE signature achieves it. The prior "4/3 vs 6/5 rotation" was a
SUBOPTIMAL-toll artifact; at the saddle there is no mixing obstruction. (0 metric-vs-LP mismatch / 8 atoms.)

## 2. The worst toll is UNIFORM on its support => INTEGER reformulation
AUDITED (worst_toll_structure.py): w* is uniform on an edge subset E0. So (16) <=> integer statement:
  (INT)  for every edge subset E0:  min_S ( |S∩E0| + sum_{e in S} d^{B,E0}(e) )  <=  n^2 |E0| / (25 t),
d^{B,E0} = #E0-edges on the shortest E0-counting B-path. VERIFIED 0 violations over ALL subsets E0 of all
2-conn edge-critical tri-free atoms N<=8 (check_uniform_worst.py), worst ratio 1.0 at C5; K23 sampled max
ratio 0.71 (k23_int.py).

## 3. PRIMAL form: best-signature spread-geodesic routing -> the bound is QFC25 ON ATOMS
Route each bad edge e over ALL its shortest B-geodesics uniformly (all_geodesics_load). Each routed
geodesic + e is an odd cycle with C∩S={e} (private). Scale by 1/max(1,rho_B): feasible fractional
odd-cycle packing of value t/max(1,rho_B). rho_B = max B-edge congestion of the best signature's routing.
AUDITED (test_qfc_atoms.py, stress_fast.py): rho_B <= max{1, n^2/(25t)} with 0 violations over ~20 atoms
(all N<=9 critical atoms + K23-N13 + C5[q] + GP(7,2)/GP(7,3) n=14 + subdiv-K4 + perturbed C5[q]); TIGHT
only at C5[q]. GP(7,2): rho_B=1.5 <= 1.96.

### Why this is NOT GPT's refuted QFC25
The dilution J_t (K23 ⊕ C5[t] via ONE edge) that refuted QFC25 is NOT a 2-connected edge-critical ATOM
(it has a CUT VERTEX; test_qfc_atoms.py confirms 2-connected=False, edge-critical=False). By the PROVED
block-cut decomposition tau(G)=Σtau(G_i), nu*(G)=Σnu*(G_i), dilutions are handled block-by-block. The
congestion bound is only CLAIMED on atoms, where the refutation does not apply.

### Non-circular closure (normalization_check.py)
rho_B <= n^2/(25t) ALONE forces the theorem: nu*(K) >= t/max(1,rho_B), and unconditionally nu*(K)<=n^2/25
(Cauchy+cycle-degree, NO Guenin). If t>n^2/25 then n^2/(25t)<1 so rho_B<1 so max(1,rho_B)=1 and value t >
n^2/25 >= nu*, contradiction. Hence t<=n^2/25. No circularity.

## 4. DUAL collapse: the congestion bottleneck is a 0/1 CUT (the decisive simplification)
AUDITED (sparsest_cut_dual.py): the tight dual of the geodesic-congestion LP is a UNIFORM 0/1 B-edge
length, i.e. an actual B-edge cut F. AUDITED (cut_coarea_link.py, cut_inequality_verify.py): the max over
vertex BIPARTITIONS equals rho_B exactly. So the SOLE remaining open lemma is the

  ** SHARP COAREA / CUT INEQUALITY (the new open core) **
  for the best min signature S (B=K-S), for EVERY vertex bipartition W (F = delta_B(W)):
        X_F / |F|  <=  n^2 / (25 t),     X_F := sum_{e in S} min_{B-geodesic P of e} #(P ∩ F).
  Equivalently every B-cut F separates at most (n^2/(25t))|F| units of (geodesic-forced) bad-edge demand.

K23: |F|=6, X_F=8, 8/6=1.333 <= 1.69. C5[q]: the 5-layer/2-layer cut is tight at exactly 1.

### The worst cut IS layered (worst_cut_is_layered.py)
AUDITED: on C5, C5[2], Petersen, K23-N13 the worst bipartition W (max X_F/|F|) is a B-DISTANCE-PREFIX
from a small source set A (W={v: d_B(A,v)<=r}). K23 worst W = the source layer itself A={0,1,5,6}, r=0.
This is EXACTLY the layered regime where the proved coherent-P5 block AM-GM (5 pair-products) applies =>
strong evidence the worst cut is always a <=5-layer cut and the constant 25 transfers. CLOSING the lemma =
prove "worst geodesic-congestion cut is a <=5-layer distance-prefix cut", then apply block AM-GM.

## 5. Why the constant is 25 and how the block lemma plugs in
The CUT inequality is the MULTI-LAYER generalization of the PROVED coherent-P5 block lemma (L1,
P5_coherent_lemma_PROVED): for the layered cut F = E_B(L_i, L_{i+1}) (geodesic distance layers from a
source set A), X_F counts bad edges crossing the prefix and |F| <= a_i a_{i+1}; the five pair-products
(a0a1)(a1a2)(a2a3)(a3a4)(a4a0)=(a0..a4)^2 with AM-GM sum a_i<=N give the SHARP 25=5^2. The block lemma is
the SPECIAL CASE where F is one of these 5 layer-cuts and S is a single complete-bipartite block. The open
work is the GENERAL signature/cut version (the old (Sync) gap), now sharpened to: the best-signature
geodesic-cut ratio is maximized by a 5-LAYER cut, where the block AM-GM applies.

## STATUS
Erdos #23 Step-2 reduces (no Guenin/Lehman) to (CUT): a sharp B-cut coarea inequality on 2-connected
edge-critical tri-free atoms, with the constant 25 from the 5-pair-product AM-GM. Numerically TRUE with
margin everywhere (0 violations, ~20 atoms incl K23/GP(7,2)), tight only at C5[q]. NOT closed: a proof
that the worst cut is the 5-layer cut (or a direct sharp coarea bound) is the open frontier -- the same
synchronization difficulty as (Sync), but now in clean single-cut form linked to the proved block AM-GM.
Lean-friendly (finite, BFS distances, cut counting, AM-GM). All-or-nothing: NOT a closure.
