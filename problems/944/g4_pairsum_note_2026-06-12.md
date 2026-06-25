# G4 pair-sum squeeze — derivation note (Claude, 2026-06-12 ~15:45)
Status: rigorous-informal (pure arithmetic over Lean-verified L1 + audited L2);
numeric cross-check planned (see VERIFY at end). New relative to round-2/round-3
drafts: the three-pair SUM is exploited, not just one pair.

## Setting (= zero-budget setting, round-2 digest)
Minimal-shore H: Delta<=6, sum of deficiencies b(x)=6, kappa(X)>=8 for all proper
2<=|X|<=|V|-2. Unfrozen full v, witness psi (proper 3-colouring of H-v with N(v)
counts (2,2,2)), classes X_1,X_2,X_3. For each k, pair-graph P_k = H[X_i u X_j]
({i,j,k}={1,2,3}): q_k=|X_k|, p_k=|V(P_k)|=n-1-q_k, b_k=b(X_k), n=|V(H)|.
Facts used: L1 (Lean-verified): e(P_k) = 3(p_k-q_k)+b_k-4 = 3n-7+b_k-6q_k.
L2 (audited+23/23): sum_{C comp of P_k} kappa(C) = 6q_k+8-2b_k, kappa(C)=6|C|-2e(C).
Constraints: sum_k q_k = n-1, sum_k b_k = 6 (v full).

## PC1 (three-pair impossibility of the singleton/edge regime)
CLAIM: if every component of every P_k (k=1,2,3) has <=2 vertices, then n <= 4.
Hence for n>=5 (always: |V|>=9 in (FK)), AT EVERY unfrozen v and EVERY witness,
at least one pair-graph contains a component with >=3 vertices.
PROOF: components <=2 vtcs => e(P_k)=t_k (#edge-comps) and s_k+2t_k=p_k with
s_k>=0 => e(P_k) <= p_k/2. By L1: 3n-7+b_k-6q_k <= (n-1-q_k)/2
=> 11 q_k >= 5n-13+2b_k.   (*)
Sum (*) over k: 11(n-1) >= 15n-39+12 => 4n <= 16 => n <= 4.  QED
Remark: (*) alone is the per-pair inequality; the all-singleton extreme (G3,
q=(n-1)/2, b_k=4) satisfies it with slack 1/2 — consistent: in the G3 shape the
OTHER two pairs carry giant components (all 6q-6 cross edges), so PC1 is tight
in spirit: the contradiction needs all three pairs simultaneously.

## PC2 (linear mass in >=3-vertex components)
Let W_k = #vertices of P_k lying in components with >=3 vertices, R_k = #such
components. Using L2 with kappa(C)>=8 (minimal-shore) for these components,
kappa=6 (singletons), kappa=10 (edges), and s_k>=0:
   substitute s_k = p_k-2t_k-W_k into 6s_k+10t_k+sum kappa_{>=3} = 6q_k+8-2b_k:
   2t_k = 6p_k-6q_k-8+2b_k-6W_k+sum kappa_{>=3}; then t_k <= (p_k-W_k)/2 gives
   5p_k <= 6q_k+8-2b_k+5W_k-sum kappa_{>=3} <= 6q_k+8-2b_k+5W_k-8R_k.
=> 11q_k + 5W_k >= 5n-13+2b_k+8R_k per k; summing over k:
   sum_k W_k >= (4n-16)/5 + (8/5) sum_k R_k.
CONSEQUENCE: a linear (in n) vertex mass sits in >=3-vertex components of the
three pair-graphs. Since each vertex lies in exactly 2 pair-graphs, at least
(2/5)(n-4) distinct vertices lie in a >=3-vertex component of some pair.
With the F2/F5 censuses (kappa=8: >=19 vtcs; kappa=10: edge or >=18;
kappa=12: >=18 or the 2 b-stacked exceptions), every such component is
(a) kappa>=14 sparse-small/medium, (b) a kappa=12 exception (needs B_k<=2 and
>=4 deficiency stacked inside), or (c) BIG (>=18/19 vertices).

## GAP FLAGGED in the F5 menu ("EDGES or BIG" is too strong as stated)
The kappa>=14 family is NOT only P3/C4/K_{1,3}: e.g. K_{4,5} (m=9, e=20,
kappa=14), K_{4,4} (m=8, e=16, kappa=16), and all bipartite Delta<=6 graphs with
e <= 3m-7 up to m=17 are uncensused LIVE shapes. PC1/PC2 force >=3-vertex
components to exist; if the kappa=14/16 small-medium families (e=3m-7, 3m-8;
m=3..17) were locked-censused like kappa=10/12 (same threshold logic: locked>=7
=> dead under every deficiency assignment), the menu would collapse to
"BIG (>=17) or b-stacked exceptions", giving via PC2 immediate strong structure:
n bounded below by big-component sizes per pair. PROPOSED NEXT COMPUTE
(cheap for m<=13; same piece_hunt machinery): kappa=14 (e=3m-7) and kappa=16
(e=3m-8) bipartite locked censuses.

## VERIFY — DONE 2026-06-12 ~15:55 (pc_check.cpp, 8 threads)
- n=12 FULL stock (7,849 graphs): 1,572 (v,psi) witnesses, PC1 instances = 0,
  PC2 violations = 0, min PC2 slack = 8.
- n=13 FULL stock (367,860 graphs): 71,820 witnesses, PC1 instances = 0,
  PC2 violations = 0, min PC2 slack = 12.
- Status upgrade: PC1/PC2 = rigorous-informal (arithmetic over Lean-verified L1
  + audited L2) + VERIFIED NUMERICALLY on the complete n<=13 6-regular stock
  (deficiency-0 variant; PC1 b=0 bound is n<=7, so any instance at n=12,13
  would have refuted the algebra).
