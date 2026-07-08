# gap#1 FULL-SUPPORT REDUCTION (GPT-Pro MAIN, 2026-07-08, in reply to Claude's STAGE-1/2/3 + family-sweep findings)

GPT-Pro: "This is the first genuinely simplifying structural reduction after the C18 correction." Given Claude's
validated facts (K2-closure, split identity, `sum_{u in V_X} T(u) = Gamma_X`, `R_local<0 => Demand=0`), gap#1
(PositiveSlackAbsorption_FullBank) reduces to ONE residual lemma about FULL-SUPPORT components.

## 1. ProperSupportAmbientAbsorption (|V_X| < N)  -- CLAIMED PROVEN
For a K2-closed component X with proper support (|V_X| < N):
- `R_full(X) = R_local(X) + (N-|V_X|)*T_X`,  `T_X = sum_{u in V_X}T(u) = sum_{e in X} ell(e)^2 = Gamma_X`.
- `R_full(X) = sum_{u in V_X} R[u] >= 0`.
- Canonical ambient token of X: support = V_X, tau = T_X = Gamma_X, so cap_X(v) = Gamma_X for every v not in V_X;
  total ambient capacity (N-|V_X|)*Gamma_X.
- Since `Demand_X <= Gamma_X` (Demand_X = Gamma_X - 25|X_atoms|), route ALL demand to a single external vertex v0:
  q(a,v0)=demand(a), else 0; check sum_a q(a,v0) = Demand_X <= Gamma_X = cap_X(v0).  =>  ambient covers all
  proper-support demand, support-constrained. NO C5, NO Ferrers Hall, NO LRS.
  Lean: theorem ProperSupportAmbientAbsorption (hProper: card(VX)<N) (hDemand: Demand X <= GammaX X)
        (hAtoms: forall a in X, AtomSupport a subseteq VX X) : exists flow, CheckAmbientFlow X flow = true.

  *** CLAUDE GATE CONCERN (to verify, falsifier-first): cap_X(v)=Gamma_X is a PER-(component,vertex) cap, NOT a
      global per-vertex cap. The REAL per-vertex ambient reserve is N-T(v) (Sigma_v (N-T(v)) = N^2-Gamma). If
      Gamma_X > N-T(v0) or multiple components share v0, the single-vertex routing DOUBLE-SPENDS v0's real reserve.
      SOUND test = GLOBAL max-flow: atoms -> door(25sigma) + external vertices v (v notin V_comp(a)) with cap N-T(v);
      only full-support (|V_X|=N) components should be infeasible. ***

## 2. R_local < 0 harmless  (Claude's finding, folded in): R_local(X)<0 => Demand(X)=0.

## 3. Minimality lever  no_nonneg_prunable_subcage_in_minNeg  -- CLAIMED (pure ledger algebra)
For minimal negative-balance cage C, proper subcage D with Prune C D = C' and
`Balance C = Balance C' + Balance D + PruneRemainder C D`, if `0<=Balance D` and `0<=PruneRemainder`, then
`Balance C' = Balance C - Balance D - PruneRemainder <= Balance C < 0` => C' is a proper negative-balance
descendant, contradicting minimality. So a tight full-support block (Balance D = 0) cannot be a proper subcage of a
minimal negative-balance cage; nor the selected cage (which has Balance C < 0). EXCLUDES the C_25 tight odd-cycle escape.

## 4. Full-support disjunction  (the residual)
theorem full_support_block_balance_nonneg_or_prunable (hFull: VX X = FullVertexSet) (hX: X in ComponentsOfCage C):
   0 <= BalanceOfComponent X  \/  exists D, ProperSubcage D C /\ Balance D < 0.
For minimal C the 2nd disjunct is impossible => full-support blocks inside the minimal cage are nonnegative.

## 5. THE SOLE REMAINING RESIDUAL = FullSupportC5Dominance
For a FULL-support component (|V_X|=N, Demand>0): Ambient=0, R_local=0, so need
   `C5Cap >= N^2 - 25 - 25*sigma`.
Calibration (odd cycle C_{2k+1}, one bad edge, sigma=1): C5Cap >= N^2-50; N=9 => >=31; N=25 => >=575.
GPT-Pro: "the C5/density bank should be the source" since 25*eta = N^2-25 (m=1) is also large. Claude's observed
`25*sigma+R_full` failures at long odd cycles ARE EXACTLY this full-support case (they calibrate FullSupportC5Dominance,
NOT failures of the ambient theorem).

## OVERALL PROOF SKELETON (GPT-Pro, sigma>0 minimal candidate C):
1. proper-support components: ProperSupportAmbientAbsorption (ambient).
2. full-support component with Demand>0: FullSupportC5Dominance  [THE OPEN RESIDUAL].
3. R_local<0 harmless (Demand=0).
4. K2-disjoint stability + ledger no-double-spend: add the component absorptions.
5. minimality lever: excludes tight full-support blocks from being minimal.
6. => Balance(C) >= 0 for every sigma>0 minimal candidate.  "Much smaller than the original full Hall theorem."

CLAUDE STATUS: exact-gating (1) [double-spend concern] + confirming (5) is the only residual. If (1) gates clean,
gap#1 has shrunk from the full support-restricted Hall to the SINGLE lemma FullSupportC5Dominance (C5 density bank on
a single long-geodesic-filling cage). Verbatim archive: this file; thread 6a4c8b1a.

## *** CLAUDE FALSIFICATION (2026-07-08, _claude_propersupport_ambient_gate.py) — claim (1) is UNSOUND as stated ***
GLOBAL max-flow (proper-support atoms -> external vertices v notin V_X, REAL per-vertex reserve cap(v)=N-T(v),
Sigma_v(N-T(v))=N^2-Gamma, NO door): proper-support demand is NOT ambient-absorbable on **544/71815** Gamma-min cages
(census N<=11). GPT-Pro's literal single-external-vertex route fails on 903 components.
HAND-VERIFIED minimal counterexample (cen8): a single ell=7 atom, |V_X|=7 (support fills 7 of 8 vertices) => exactly
ONE external vertex v0, real reserve cap(v0)=8-T(v0) <= 8, but Demand = 7^2-25 = 24 > 8. INFEASIBLE.
ROOT CAUSE: GPT-Pro's cap_X(v)=Gamma_X (=T_X) is FICTIONAL. The split R_full(X)=R_local(X)+(N-|V_X|)*T_X is an
ALGEBRAIC rewriting; R_full(X)=Sigma_{u in V_X}R[u] is reserve located at the component's INTERIOR vertices V_X, NOT
capacity physically available at external vertices. Routing demand to an external vertex v uses v's OWN reserve
N-T(v) <= N, which for an ell-atom (Gamma_X ~ ell^2) is ~ell times smaller than the claimed Gamma_X.
CONSEQUENCE: the clean reduction "proper-support => ambient alone; full-support => C5 alone" does NOT hold. Proper-
support components with high demand-to-external-reserve ALSO need the door/C5, so the residual is NOT full-support-only.
The full bank (door 25*sigma + ambient + C5) IS still feasible on all census (STAGE 2, 0 infeasible) — the DOOR does the
heavy lifting GPT-Pro's decomposition under-counted. So gap#1 remains the FULL mixed-bank Hall theorem, NOT a single
C5 lemma. The minimality lever (sec 3/4, pure ledger algebra) is independent and may still stand; sent back to GPT-Pro.

## GPT-Pro CONCEDES (2026-07-08, reply 5, 8902 char) — honest convergence to the FULL Hall theorem
"Yes -- I agree with all three corrections." Point by point:
- (A) cap_X(v)=Gamma_X was NOT a real per-vertex capacity ("confused a scalar component identity with a routable vertex
  capacity"). CORRECTED: cap_amb(v) = vertexSlack(v) = N - T(v), atom a uses v only when v notin V_a. "The real ambient
  capacity is O(N) per vertex, not O(ell^2) per external vertex." The interior->exterior transfer is FALSE in general
  (Claude's N=8 counterexample proves it). The split R_full=R_local+(N-|VX|)T_X is an ALGEBRAIC identity, NOT a routing
  theorem; R[u] is a residual token owned by INTERIOR structure, contributing to C5/Prune/rowDB caps only through an
  incidence-checked allocation -- never as spendable external-vertex capacity.
- (B) MINIMALITY LEVER STANDS (independent of the false split): Balance(C)=Balance(C')+Balance(D)+PruneRemainder,
  Balance(D)>=0, PruneRemainder>=0, Balance(C)<0 => Balance(C')<0 => proper prunable D can't exist in a minimal
  neg-balance cage. Valid with the corrected full bank Door+true-vertex-ambient+C5+Prune. [Claude: FORMALIZE THIS.]
- (C) The clean "proper-support => ambient alone" localization is FALSE. Survives only as ORIGIN CHECKS (K2-closure, split
  identity, R_local facts); the actual capacity SINKS are Door(25sigma) + true vertex slack(N-T(v)) + C5(25*mass(z)) +
  Prune(Balance(D)). RESIDUAL = the full-bank flow LP per cage/prefix; its Hall dual = the exact missing universal
  inequality: for every atom subset A, demand(A) <= cap(N(A)) with legal Door/Ambient/C5/Prune incidences.
  atom a=(e,j,mu), demand(a)=mu*(8j+24), V_a=annular support. THIS IS THE FULL support-restricted Hall theorem, no shortcut.

NET: gap#1 = the full mixed-bank support-restricted Hall theorem (Door+Ambient(N-T(v))+C5+Prune), exactly as before this
cycle. All shortcuts eliminated (door-only, companion-theta, tri-free, canonical-cap, LRS, full-support-localization).
SALVAGED NEW PIECE: the minimality lever (pure algebra) -> formalize in RouteBCAP.lean. P(gap#1 math) ~45-50 unchanged.

## GPT-Pro C5/DENSITY BANK construction (2026-07-08, reply 6, 8897 char) + Claude accounting
The C5 bank is NOT a pentagon count -- it is the DENSITY-RESERVE token normalized by the C5 extremal density 1/25:
   localEta(X)  eta_X = |V_X|^2/25 - m_X            (m_X = assigned bad-edge mass)
   fullSupportC5Mass(X) = eta_X - sigma_X
   fullSupportC5Cap(X)  = 25*(eta_X - sigma_X) = |V_X|^2 - 25*m_X - 25*sigma_X    [use max(0,.)]
The "25 = 5^2" enters because the global extremal target is m <= N^2/25 and the surplus target Sum(ell^2-25) <= 25*eta.
Incidence: for a full-support leaf, the C5 token is local to X and every surplus atom owned by X may spend it.
General cages: C5 mass allocated by a CHECKED density ledger, Sum_{z in I} mass(z) <= |V_I|^2/25 - m_I - sigma_I - pruned.
Lean: def localEta N m := N^2/25 - m; fullSupportC5Mass N m sigma := localEta - sigma; cap := 25*mass; use only when
0 <= fullSupportC5Mass. theorem fullSupport_leaf_absorbed_by_density (hDemand: demand <= N^2 - 25*m) ...

### *** CLAUDE: the LEAF case is CLOSED, NON-CIRCULARLY, via ell <= N (a graph fact, NOT the conjecture) ***
For a single-bad-edge leaf cage: ell = shortest odd cycle length <= N (the cycle has ell vertices <= |V|). So
Demand = ell^2 - 25 <= N^2 - 25 = Door + C5 (when C5Mass>=0), giving Balance = (N^2-25) - (ell^2-25) = N^2 - ell^2 >= 0.
When C5Mass < 0 (dense, sigma > N^2/25 - 1): Door = 25*sigma > N^2 - 25 >= Demand alone. EITHER WAY Balance >= 0.
So the GPT-Pro hypothesis `demand <= N^2 - 25*m` is, for a leaf, the GRAPH FACT ell<=N (m=1), not the conjecture -> NON-circular.
This CLOSES the tight full-support leaf case (odd cycles C_25.. that broke Claude's graph bank). CAVEAT: leaf = base
case only (single-bad-edge cages have beta=1, trivially <= N^2/25). The HARD CORE = the MULTI-ATOM density ledger
(demand(A) <= Door+C5+Prune for every atom subset, needing the LOCAL conjecture Gamma_A <= |U_A|^2 by INDUCTION via the
minimality lever) -- STILL OPEN. Claude gating leaf closure + formalizing fullSupport_leaf_absorbed_by_density.

## *** DEFINITIVE FINAL REDUCTION (GPT-Pro reply 7, 9983 char, 2026-07-08) -- gap#1 = ONE gateable lemma ***
Claude's circularity concern CONFIRMED and made precise. The safe induction CANNOT use the top cage's own density
reserve eta_C = |V_C|^2/25 - m_C (proving that IS the local square bound for C). Legal tokens for cage C: (1) Door
25*sigma(C); (2) true vertex ambient = nonneg parts of N-T(v), incidence-checked; (3) Prune = Balance(D) for STRICT
proper pruned descendants D, already certified; (4) independent base-density tokens (single-bad-edge full-support LEAF,
proved from ell<=|V|, Claude's fullSupport_leaf_absorbed_by_density). ILLEGAL: C's own unproved eta_C.
- (1) Balance(D)>=0 does NOT imply eta_D>=0 (different quantities; a subcage can be paid by external ambient/door).
  [Claude note: my eta_nonneg gate tested K2-support COMPONENTS (|V_X|>=5 => eta>=0 where Demand>0); GPT-Pro's eta_D is
   over the CAGE/PRUNE tree where singleton doors have eta_D<0 -- different decompositions, both consistent.]
- INDUCTION: measure rank(C)=#owned atoms (or inclusion rank in the terminal-cage forest). IH: all strict proper cages
  have checked nonneg balance / valid absorption certs. STEP = prove ReducedShellHall_NoTopEta for C:
     Demand(A) <= 25*sigma(A) + AmbientCap(A) + sum_{D proper} Balance(D) + BaseDensityCap(A)   for every prefix/subset A,
  with NO top eta_C token. The minimality lever (Claude-formalized no_nonneg_prunable_subcage_in_minNeg) removes all
  nonneg-prunable subcages => the minimal counterexample is a REDUCED SHELL to absorb by Door+ambient+base only.
- WELL-FOUNDED iff the reduced shell is covered without top eta_C. CIRCULAR iff the induction bottoms out at a
  MULTI-ATOM FULL-SUPPORT SHELL (support = all vertices => NO ambient room; not decomposable into proper prunable
  descendants; not an independent base leaf) whose only apparent capacity is its own eta_C.
- **THE SINGLE REMAINING RESIDUAL = MultiAtomFullSupportShell_absorbed_without_topEta.** DECISIVE OBSTRUCTION (exact):
  a reduced multi-atom full-support shell with Demand > Door + Prune + independent BaseDensity and no ambient room.
  GATE: search for multi-atom (m>=2) full-support (|V_X|=N) shells; if none arise, or all have Demand <= Door(+prune+base),
  the induction closes. If a genuine one with Demand > Door+Prune+Base exists, that is the circularity obstruction.
  Claude building _claude_multiatom_fullsupport_gate.py (falsifier-first).

## *** THE SINGLE FINAL LEMMA (GPT-Pro reply 8, 10452 char, 2026-07-08) ***
gap#1's ENTIRE remaining hard content = ONE named structural lemma. The split after Claude's gates:
- proper-support atoms (|V_X|<N): MIXED bank (door+ambient(N-T(v))+C5(eta_X>=0 where Demand>0, Claude-verified)+prune);
  ambient HELPS but does not dominate alone (Claude's falsification stands). Handled by the mixed-bank flow (ambient available).
- single full-support LEAF: base density, CLOSED + Lean-formalized (fullSupport_leaf_absorbed_by_density).
- MULTI-ATOM full-support reduced shell: the LAST circularity point (no ambient, |V_X|=N).
THE LEMMA (equivalent forms): ReducedFullSupportDoorDominance / NoReducedOverdoorFullSupportMultiShell:
   For a REDUCED (all prunable nonneg subcages + base leaves removed) Gamma-MINIMAL multi-atom full-support shell X,
      Gamma_X = sum_{e in X} ell(e)^2  <=  25 * b_X   (b_X = cut-edge count of the shell = 25*sigma+25m form),
   equivalently Demand_X <= Door_X, equivalently no reduced over-door full-support multi shell exists.
   With base/prune allowed: Gamma_X <= 25*b_X + PruneCap_X + BaseDensityCap_X (ReducedFullSupportHall_NoTopEta).
HONEST STATUS (GPT-Pro): NOT true for arbitrary max cuts -- NEEDS the reduced/Gamma-minimal/K2-shell hypotheses
(weak examples violate it without them). Minimality lever (Claude-formalized) removes prunable pieces but does NOT
prove Gamma_X<=25*b_X. Claude's gate (9956 multi-atom full-support, 74 long-atom, ALL Demand<=Door) = strong EVIDENCE
but not a proof. Missing structural reason is ONE of: (1) any over-door full-support shell admits a zero-slack
Gamma-DECREASING SWITCH => Gamma-minimality excludes it [most promising, connects to switch_connected machinery];
(2) it decomposes into prunable base/side-door blocks; (3) Ferrers/K2 structure forces enough cut edges when >=2 long
atoms share full support [Claude's gates suggest (3) in reduced shells]. Proof direction: contradiction (avg square-length
per cut edge too large under Gamma-min). Lean-ready: theorem NoReducedOverdoorFullSupportMultiShell (hMin, hReduced, hFull).
=> gap#1 = this single lemma + the proper-support mixed-bank feasibility. Base cases + minimality lever FORMALIZED.
