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

## GPT-Pro reply 9 (2026-07-08, 9322 char) -- HONEST: "I would not yet claim a proof." The switch-existence lemma + certificate.
gap#1 final lemma, EQUIVALENT switch form:
  theorem OverdoorFullSupportSwitchExistence (hReduced, hFull: VX=FullVertexSet, hMulti: 2<=AtomCount, hOver: 25*b_X < Gamma_X):
     exists W, ZeroSlackSwitch W /\ ConnectedAfterSwitch W /\ GammaAfter W < GammaBefore.   (then Gamma-min => contradiction).
  NOT implied by K2-closure/Ferrers/max-cutness alone -- the remaining structural lemma. GPT-Pro does NOT prove existence.
CANDIDATE SWITCH W (graph-computable): for every pair of bad edges e=ab, f=cd in the SAME K2-component, shortest geodesics
  P_e, P_f, form Theta(e,f)=P_e union P_f + endpoint bad edges; search BALANCED Ferrers/pair-door intervals of Theta. (Connects
  to the earlier pair-door machinery: pairDoor_metric_stability, pairTypeBTheta_gammaDrop_pos.)
SWITCH CERTIFICATE (S1-S6, exact, graph-computable): S1 sigma(W)=0 (zero-slack); S2 delta(W) boundary; S3 B^W connected
  (spanning-tree cert); S4 M^W=(M\Kill(W)) union Born(W), Kill=M cap delta(W), Born=B cap delta(W); S5 stable-edge length
  accounting; S6 DeltaGamma(W)=Gamma(B^W)-Gamma(B)<0. EXACT DeltaGamma:
    Gamma(B)-Gamma(B^W) = sum_{e in M cap delta(W)} ell_B(e)^2 + sum_{e in M\delta(W)}(ell_B(e)^2-ell_{B^W}(e)^2)
                          - sum_{d in B cap delta(W)} ell_{B^W}(d)^2.
  [Claude's _claude_gamma_switch_verifier.py eval_switch computes Gamma(B),Gamma(B^W) DIRECTLY = this, self-check PASS.]
FALSIFIER-FIRST GATE (GPT-Pro sec 8): for an over-door full-support shell, enumerate W (pair-door Ferrers intervals /
  small-boundary cuts), check sigma(W)=0 + B^W connected + Gamma(B^W)<Gamma(B). If found => switch cert; if NONE found with
  Gamma_X>25*b_X => the DECISIVE OBSTRUCTION. Option 1 (this switch) is conceptually closest to Gamma-minimality.
CLAUDE STATUS: verifier READY; TESTING BOTTLENECK = need OVER-DOOR full-support shells (Gamma_X>25*b_X), which need large N
  (single atom N>=25; multi-atom irreducible = hard to construct) -- they do NOT arise in small Gamma-min census cuts (all
  Demand<=Door). gap#1 = OverdoorFullSupportSwitchExistence: sharply stated, checkable, UNPROVEN (GPT-Pro's honest status). P~52.

## GPT-Pro reply 10 (2026-07-08) -- OPTION-3 CLEAN FINAL STRUCTURE. gap#1 = 2 atomic obligations.
"Your reduction is now at the right granularity." Full-support shell splits into:
  LONG single-edge leaves (ell>=25): handled by base density [Claude: fullSupport_leaf_absorbed_by_density, DONE].
  SHORT remainder S (all ell<=23): satisfy ShortRowCutEdgeHall.
=> Gamma_X <= 25*b_X + BaseDensityCap_X + PruneCap_X  (ReducedFullSupportHall_NoTopEta, NO top eta_C).
TWO ATOMIC OBLIGATIONS (Lean interfaces given):
  (i) LongAtoms_are_prunable_base_leaves: e in X, ell(e)>=25 => IsPrunableBaseLeaf.
  (ii) ShortRowCutEdgeHall (THE clean single inequality): for every subset A of short rows,
         sum_{e in A} ell(e)^2 <= 25 * |union_{e in A} P_e|   (P_e = canonical shortest-row cut edges).
     = max-flow: sources=rows demand ell(e)^2, sinks=cut edges capacity 25 each, row e -> c iff c in P_e. Feasible <=> Hall.
     Per-row it is ell^2<=25(ell-1) [Claude atom_sq_le_25_shortAtom, DONE]; the SUBSET form rules out cut-edge DOUBLE-SPEND
     when rows share cut edges. GATE (GPT-Pro sec 8): max-flow feasibility; if INFEASIBLE, print the obstructing subset A =
     the exact candidate for a switch/reducibility proof. Weak hyps: over-door likely possible; reduced Gamma-min: data says NO.
RECONCILIATION (my earlier concern): the bank is Door(25 per cut edge) + Base + Prune, NO top eta_C -- so the relevant
  quantity IS Gamma_X<=25*b_X (+base+prune), NOT |V_X|^2. The C5=25(eta-sigma) with C5<0 => door-only, and the cut-edge Hall
  (25/edge) is the door capacity. So Gamma_X<=25*b_X is correct (door=cut-edge capacity 25 each). Concern resolved.
CLAUDE: building _claude_shortrow_hall_gate.py = the DEFINITIVE obligation-(ii) gate (exact subset Hall via max-flow).
  atom_sq_le_25_shortAtom + fullSupport_doorDominance_of_shortAtoms FORMALIZED (the per-row + aggregate); the SUBSET Hall
  (no double-spend) is the remaining structural lemma. P(gap#1 math)~53-55.

## 2026-07-08 CONVERGENCE: both atomic obligations reduce to ONE switch lemma (Gamma-decreasing switch existence).
### Obligation (ii) -- multi-agent adversarial WORKFLOW (11 agents, 775k tok):
- FOUND A GATE BUG: my ShortRowCutEdgeHall used ONE canonical geodesic per bad edge => lemma is FALSE as written.
  COUNTEREXAMPLE C5[3] (N=15, tri-free, Gamma-min all 70 max cuts tie Gamma=225): 9 bad edges ell=5, sum ell^2=225 >
  200=25*|union canonical P_e| (union=8). My census gate MISSED it (C5[t] N=15 not in census/even-chord battery).
- CORRECTED lemma = SPREADING-FEASIBILITY (all shortest B-geodesics, demand spreads): max-flow source e demand ell^2,
  sink cut-edge c cap 25, arc e->c iff c on SOME shortest geodesic of e. FEASIBLE on C5[3] (225=225 TIGHT) + all tested.
- REDUCES TO: a congestion-SPREADABILITY bound under Gamma-min: min over fractional geodesic selections of max per-cut-edge
  weighted load <= 25, tight at C5[t]. Structural reason: an over-congested cut edge (load>25 after optimal spread) is the
  site of a Gamma-DECREASING zero-slack re-cut, contradicting Gamma-minimality. BINDING REGIME ell in [13,23] (N>=23,
  slack s(23)=21 tiny) UNTESTED = the genuine remaining risk. The gamma-min-switch decisive step is UNPROVEN.
### Obligation (i) -- GPT-Pro reply 11 (LongAtom_reduces_or_switches):
- ell>=25 rows CANNOT be paid by their own row cut edges; must be a prunable base leaf OR create a Gamma-decreasing switch.
- Prunable base leaf D_e: Balance(D_e)>=0 via ell(e)<=|V(D_e)| (geodesic cycle in D_e) => ell^2-25<=|V(D_e)|^2-25<=25*sigma+baseCap.
  NON-circular (uses ell<=|V(D_e)|, not the density conjecture).
- ENTANGLED long atoms CAN exist under WEAK hyps (a long bad edge shares geodesic support, not a clean prune unit). Under
  reduced Gamma-min: DISJUNCTION theorem LongAtom_reduces_or_switches -- either prunes OR a Gamma-decreasing switch exists.
### => UNIFYING RESIDUAL of gap#1 = the Gamma-DECREASING SWITCH EXISTENCE (zero-slack, connected, Delta_Gamma<0) under
Gamma-minimality: any over-congested (ii) / entangled-long (i) configuration admits it, contradicting minimality. This is
the "NoLongSideDoorAnnulus / annular first-split" switch (the S1 re-audit WALL), now re-derived as the single unifying core.
EMPIRICALLY BULLETPROOF (no such config arises in any tested Gamma-min cut) but the EXPLICIT switch W (with controlled global
effect on other rows' ell) is UNPROVEN. P(gap#1 math)~53-55.

## GPT-Pro reply 12 (2026-07-08) -- DEFINITIVE: the switch lemma is a base-leaf-OR-switch DISJUNCTION; gap#1 = S1 WALL GENERALIZED.
- My 'over-congested edge => Gamma-decreasing switch' is FALSE. COUNTEREXAMPLE: odd cycle C_N (N>=25). ell=N, Gamma=N^2, every
  cut edge load N^2/(N-1)>25; Gamma-MINIMAL (every max cut has one bad edge length N); any zero-slack switch just MOVES the bad
  edge to another cycle edge, still length N => Delta_Gamma=0 (NOT <0). So NO Gamma-decreasing switch -- but C_N is a BASE LEAF.
- CORRECT lemma (disjunction): FullSupportHallFailure_baseLeaf_or_switch -- a Hall failure => base leaf OR Gamma-decreasing switch.
  Named form ReducedNonBaseGeodesicHall: (hMin, hReduced, hGammaMin, hFull, hMulti, hNoBase: no prunable base leaf D exists)
  => ShortestGeodesicSpreadingFeasible X 25. [matches Claude's corrected gate: all shortest geodesics, demand ell^2, cap 25.]
- The infeasibility certificate is a DUAL cut-edge weight y (NOT a single congested edge). Candidate switch from the dual:
  Y={c: y(c)>0}, tight row family A_y, H_y = union of y-shortest geodesics; compute Ferrers/laminar decomposition of row
  overlaps in H_y; candidate switches = minimal balanced intervals W; check sigma(W)=0, B^W connected, Gamma(B^W)<Gamma(B).
  If W exists => Gamma-min contradiction; if not, the dual obstruction must be a base leaf. GRAPH-COMPUTABLE (LP dual + laminar).
- *** RELATION TO S1: for the theta/pair-door subclass the switch W IS EXACTLY the S1 first-split/last-rejoin interval (S2
  supplies intermediate-door/triangle/shorter-blue-row alternatives, non-door killed by triangle-free + shortestness). BUT the
  full geodesic Hall obstruction can be MORE GLOBAL than a single S1 theta. So the S1 door is a LOCAL INSTANCE of the switch
  theorem, NOT the whole theorem. gap#1 = the S1 WALL GENERALIZED to a global dual-obstruction switch theorem. ***
- Base-leaf split confirmed: ell<=23 => ell^2<=25(ell-1) payable [atom_sq_le_25_shortAtom DONE]; ell>=25 => single-row over-
  congestion = odd-cycle base leaf, handled by base density/prune [fullSupport_leaf_absorbed_by_density DONE], NOT by a switch.

### DEFINITIVE gap#1 END-STATE (2026-07-08): gap#1 = ReducedNonBaseGeodesicHall = the global Gamma-decreasing switch theorem
(base-leaf-OR-switch), which GENERALIZES the S1 annular-first-split door (S1 = its local theta instance). FORMALIZED
(RouteBCAP.lean, 8 axiom-clean): minimality lever, leaf absorption, short-atom bound, door-dominance derivation. EMPIRICALLY
BULLETPROOF: corrected SPREADING-FEASIBILITY feasible on 71820 Gamma-min cages incl C5[t] tight family. OPEN CORE: the global
switch existence (dual-obstruction laminar balanced interval with Delta_Gamma<0, controlled global effect) -- graph-computable,
checkable, UNPROVEN. Binding regime ell in [13,23] N>=23 untested. P(gap#1 math)~50-52; P(full Lean)~12-20.

## GPT-Pro reply 13 (2026-07-08) -- BLUNT STRATEGIC VERDICT on gap#1's provability.
VERDICT: gap#1 is a REAL reduction (NOT logically equivalent to beta<=N^2/25 -- it is sharply structured, lives only inside the
reduced full-support shell after door/ambient/prune/base-leaf/short-row reductions), BUT in DIFFICULTY it is "very close to the
heart of the conjecture" -- NOT "just an assembly lemma." Current techniques prove the LOCAL theta case (one first-split/last-
rejoin theta -> S2 disjunction -> triangle+shorter-row die -> intermediate door/switch -> Gamma drop) but are NOT yet enough
for the GLOBAL entangled multi-row case. Option-3 (Gamma_X<=25b_X / spreading feasibility) = primal/Hall; Option-1 (Hall fail =>
switch) = dual/Gamma-min; they are the SAME obstruction from opposite sides (Hall fail -> dual y -> overloaded laminar interval
-> switch). LOCAL->GLOBAL gap = 4 parts: G1 (minimal dual Hall obstruction y has a Ferrers/laminar interval W = global "first
split"); G2 (balancedness sigma(W)=0 from dual-minimality/reduced-shell); G3 (B^W connected); G4 (Delta_Gamma<0 via affected-row cert).
KEY SUB-LEMMA (for proof dev) = MinimalDualDefectIntervalSwitch; CLEAN assembly theorem = ReducedNonBaseGeodesicHall (hMin,
hReduced, hGammaMin, hFull, hNonBase => ShortestGeodesicSpreadingFeasible X 25). BEST NEXT GATE (do NOT prove all at once):
given a dual Hall obstruction y for a reduced nonbase full-support shell, does a laminar interval W of y-tight geodesics exist
with sigma(W)=0, B^W connected, Gamma(B^W)<Gamma(B)? Algorithm: solve spreading LP; if infeasible extract dual y; build y-tight
geodesic laminar arrangement; enumerate intervals W; check sigma/conn/DeltaGamma. A single infeasible shell with NO such W =
DECISIVE OBSTRUCTION; every infeasible non-Gamma-min shell producing W + no Gamma-min shell infeasible = the exact empirical theorem.
STRATEGIC: gap#1 is a genuine HARD open research theorem (the global laminar-switch, close to the conjecture's heart), NOT
closeable with current techniques for the global case -- likely a substantial (multi-round/month) problem. Documented open core.

## GPT-Pro reply 14 (2026-07-08) -- G1 structure. BLUNT: G1 is NOT automatic from LP duality.
The missing proof is an UNCROSSING theorem for dual-tight shortest rows. G1 milestone =
  DualTightGeodesicUncrossing: crossing y-tight geodesics can be UNCROSSED without increasing y-cost, UNLESS they already
  expose a base leaf or a Gamma-decreasing zero-slack switch. If proved, G1 follows by a crossing-minimal tight-geodesic
  representation of the dual obstruction. (Spreading LP: q_e = ell(e)^2/(ell(e)-1); rows spread over all shortest geodesics.)
The HARDEST part of the whole switch theorem is still likely G4 (controlled global Gamma effect after the switch). G1 nontrivial.

### DEFINITIVE OPEN-CORE MAP (2026-07-08): gap#1 = ReducedNonBaseGeodesicHall = the global Gamma-decreasing SWITCH theorem,
decomposed into: G1 DualTightGeodesicUncrossing (nontrivial, the entry point) -> G2 balancedness sigma(W)=0 -> G3 B^W connected
-> G4 controlled global Gamma effect (the HARDEST). Generalizes S1 first-split (= local theta instance). Each of G1-G4 is
genuine hard research; G4 is the crux. FORMALIZED base cases (8 axiom-clean). Empirically bulletproof (71820 cages incl C5[t]).
CONCLUSION: gap#1 is a multi-month research problem; the full 4-conjunct proof is not closeable in an autonomous run.
This is the honest documented end-state of the whole-day gap#1 arc. P(gap#1 math)~50; P(full Lean)~12-20.

## INTENSIVE ATTACK (2026-07-08 evening, user: keep going) -- CONVERGED on the PRECISE crux (StableGain / G4).
Three parallel attacks (6-angle adversarial workflow + GPT-Pro reply 16 + Claude crossing-geodesic gate) CONVERGED:
- CLAUDE crossing gate (_claude_crossing_geodesic_gate.py): crossings of bad-edge-pair shortest geodesics DO ARISE in
  Gamma-min cuts (8896/71833 cages) but are BENIGN (Gamma-min => no Gamma-decreasing switch). SELF-CAUGHT a FLAWED proxy:
  my "shortcutting" test compared d_B of re-paired endpoints on the ORIGINAL cut (!=  born-edge recut Delta_Gamma, which
  needs the FLIP W + born edges = actual G-edges same-side in B^W). Retracted. Sound evidence stays SPREADING-FEASIBILITY.
- GPT-Pro reply 16: BornEdgeRecutGammaDrop is NOT provable from "two y-tight geodesics cross" alone -- the endpoint-swap can
  fail to correspond to actual born GRAPH EDGES or raise Gamma through other rows (INDEPENDENTLY confirms Claude's retraction).
  Correct milestone: crossing + VALID PAIR-DOOR RECUT CERTIFICATE => strict Gamma-drop. The switch set W is NOT the lens
  interior; it is a COMPONENT of B\{d0,d1} with delta_B(W)={d0,d1}, delta_M(W)={e,f} (pair-door boundary), B^W connected.
  EXACT Gamma identity: Gamma(B)-Gamma(B^W) = ell(e)^2+ell(f)^2 - ell(d0)^2-ell(d1)^2 + StableGain(W),
  StableGain(W) = sum_{h notin {e,f}} (ell_B(h)^2 - ell_{B^W}(h)^2). STRICT DROP iff local saving > -StableGain.
- *** THE CRUX = StableGain(W) >= 0 (G4, controlled global effect): the recut must not LENGTHEN other bad rows enough to
  kill the local square saving. IRREDUCIBLE OPEN LEMMA = DualHallObstruction_baseLeaf_or_certifiedSwitch. ***
GATEABLE ALGORITHM (GPT-Pro, graph-computable, no metric-stability assumption): for candidate cut-edge pairs {d0,d1} from
the two crossing paths, W = component of B\{d0,d1}; check e,f cross W, delta_B(W)={d0,d1}, delta_M(W)={e,f}, B^W connected,
Gamma(B^W)<Gamma(B) by EXACT ell recomputation. If such W always exists for dual Hall obstructions (except base leaves) =
the exact empirical theorem. CAVEAT: dual obstructions don't arise in Gamma-min cuts (spreading feasible) => needs over-
congested/N>=23 configs to run on (the same testing wall). gap#1 crux = StableGain-controlled pair-door recut (G4), multi-month.

### 6-ANGLE ADVERSARIAL WORKFLOW (13 agents, 954k tok) -- SHARPENS the crux to R-A (balanced-door forcing). The arc CLOSES onto the pair-door.
NO counterexample. Findings:
- (D) base-leaf cutoff PROVEN EXACT: q(ell)=ell^2/(ell-1) <= 25 iff ell <= 23 (roots 1.04, 23.96; q23=24.045, q25=26.04);
  ell>=25 over-capacity => forced base leaf. [= Claude's formalized atom_sq_le_25_shortAtom.]
- (C) strict Gamma-drop is FALSE as a general statement -- KEY INSIGHT: two crossing y-tight geodesics share equal arcs of
  length d=d(x,y); the endpoint-swap drops TOTAL alternating length by exactly 2d, BUT Gamma=sum ell^2 is CONVEX, so a length
  drop != a Gamma drop. An ASYMMETRIC crossing RAISES Gamma: dGamma=+104 at arms (11,2,2,11,1); +48 at (13,13)->(19,5). The
  recut works ONLY for BALANCED crossings => the {L,L+2}->[L,L] door, dGamma=-(4L+4)<0 (verified L=5..23).
- (A)/(B) the naive endpoint-swap W={s,u} is REFUTED (breaks max-cut in 77% of census crossings; born pairs are non-edges in
  ~78-90%; independently confirms Claude's retraction + GPT-Pro). Correct W = the LENS = symmetric difference of the odd cycles
  C_e=P_e+e, C_f=P_f+f. delta_cut=0 <=> balanced boundary of the lens (=GPT-Pro G2, existence OPEN).
- *** THE WHOLE LEMMA REDUCES TO ONE PRIMITIVE R-A (balanced-door forcing): in a Gamma-min connected max cut of a triangle-
  free (odd-girth>=5) non-base shell (all ell<=23), every Y-TIGHT crossing (delta_cut=0 lens) has BALANCED born lengths
  a^2+b^2 < ell(e)^2+ell(f)^2 -- i.e. is forced into the {L,L+2}->[L,L] door -- never the long-arm-absorbing profile. ***
- *** THE ARC CLOSES: R-A's balanced door with dGamma=-(4L+4) IS the pairTypeBTheta_gammaDrop_pos / {L,L+2} pair-door recut
  from the session's OPENING Route-B work. gap#1's global crux = the pair-door/annular {L,L+2} door forcing, now under
  y-tightness + Gamma-minimality (the S1/S2 pair-door machinery, generalized). ***
- DECISIVE OBSTRUCTION GATE: enumerate Gamma-min cuts with >=2 bad edges ell in [13,23], N>=23; for each delta_cut=0
  opposite-order crossing compute born cut-path lengths via the LENS W and test a^2+b^2 < ell(e)^2+ell(f)^2. ONE unbalanced
  y-tight crossing in a real Gamma-min graph = DECISIVE OBSTRUCTION. Untested: census stops at N<=11 (only ell=5). CORRECTION:
  the C5[t] 'no crossing' claim is FALSE (C5[t] Gamma-min cuts DO cross, Gamma-neutrally + non-y-tightly) -- keep only the
  y-tightness qualifier. gap#1 crux = R-A (y-tight crossing => balanced {L,L+2} door), decisively gateable at N>=23.

### GPT-Pro reply 17 + Claude R-A arm gate -- crux = NET POSITIVITY LocalSaving+StableGain>0 (StableGain>=0 is FALSE, exact-verified).
- GPT-Pro: StableGain(W)>=0 is FALSE. Correct universal target = LocalSaving(W) + StableGain(W) > 0 (the real G4 lemma).
  Only stable rows whose shortest geodesic USES d0 or d1 can lengthen (limited, 2 edges removed) but they CAN.
  EXACT EXAMPLE (Claude-VERIFIED via eval_switch): 10-vertex tri-free graph, 3 bad edges all ell=5, W={a,c,b} zero-slack
  (dcut=0), stable row h=A-B lengthens ell 5->9 => StableGain = 25-81 = -56, dGamma = +56 (recut RAISES Gamma). So a clean
  two-door zero-slack recut can badly increase Gamma. edges=[(0,5),(5,2),(2,6),(6,1),(0,8),(8,4),(4,7),(3,9),(9,1),(2,3),(5,7),(0,1)].
- CLAUDE R-A arm gate (_claude_ra_arm_gate.py): workflow dGamma formula VALIDATED (two forms agree, 21063 tuples);
  18351 BALANCED (dGamma<0 switch works) vs 2712 UNBALANCED (dGamma>=0 switch FAILS, long-arm-absorbing).
- *** THREE-WAY CONVERGENCE: gap#1 irreducible crux = LocalSaving(W)+StableGain(W) > 0 for the dual-obstruction pair-door
  recut W, UNDER y-tightness + Gamma-minimality (= R-A = G4). The local switch DEMONSTRABLY FAILS without this structure
  (2712 unbalanced profiles + verified StableGain=-56). The whole gap#1 = this ONE net-positivity lemma; the arc closes
  onto the {L,L+2} pair-door / pairTypeBTheta machinery. Maximally precise, exact-verified, genuinely HARD (multi-month). ***

## GPT-Pro reply 15 (2026-07-08) -- G1 COLLAPSES INTO G4. The switch theorem is MONOLITHIC.
BLUNT: DualTightGeodesicUncrossing (G1) in the fixed-commodity form is NOT provable and is the WRONG milestone. Standard
path uncrossing either (1) preserves endpoints but doesn't remove the order-crossing, OR (2) removes the crossing by
swapping TERMINAL PAIRINGS -- but then the new paths are NOT geodesics for the same bad edges e,f; they are candidate rows
for the BORN bad edges after a recut. So case-2 IS the switch geometry: "uncrossing" and "Gamma-decreasing switch" are the
SAME operation from two sides. => G1 is NOT an easy preliminary lemma; it is ENTANGLED with G4. The clean residual is NOT a
standalone laminarity theorem but the monolithic disjunction:
   DualHallObstruction_baseLeaf_or_switch: a dual Hall obstruction for a reduced nonbase full-support shell exposes a base
   leaf OR a zero-slack connected Gamma-decreasing switch (endpoint-swapped recut).
### FINAL HONEST END-STATE (2026-07-08, tonight): gap#1 = DualHallObstruction_baseLeaf_or_switch, a MONOLITHIC hard theorem
(no easy G1 entry; the uncrossing = the switch = the born-edge recut). = ReducedNonBaseGeodesicHall. Generalizes S1 first-split.
Base cases FORMALIZED (8 axiom-clean). Empirically bulletproof (71820 cages). NEXT ATTACK (user plan): GPT-5.6 + Fable-5
tomorrow on the monolithic switch (attack the born-edge recut directly: for a dual Hall obstruction, either a base leaf or a
terminal-pairing swap that keeps the cut maximum, stays connected, and strictly drops Gamma). P(gap#1 math)~50.

================================================================================
## GPT-Pro REPLY 18 (2026-07-08) — DUAL-OBSTRUCTION SWITCH = DualDefectCoareaSwitch
================================================================================

CONTEXT: I sent GPT-Pro my StableGain(W) = -56 counterexample (graph with W={5,2,6},
dcut=0, dgamma=+56, StableGain=-56) asking whether it refutes the monolithic switch
lemma. GPT-Pro's verbatim-extracted answer:

### 10. Final answer (verbatim)
"Your StableGain=-56 example is spreading-feasible, so it does not contradict the
dual-obstruction switch theorem. The dual-selected W is not arbitrary; it must come
from a positive dual-defect."

GPT-Pro independently re-derived that my -56 graph has max cut-edge load
2*25/4 = 25/2 < 25 (geodesics h:A-a-c-b-B, e:c-b-B-g-E, f:a-A-p-q-F all fit under
cap 25) => it is SPREADING-FEASIBLE => there is NO dual Hall obstruction on it =>
the switch theorem says nothing about it. CONFIRMS my own finding (I verified the
-56 cut is submaximal (9<10) AND spreading-feasible).

### The correct lemma statement (Lean signature, verbatim §9)
theorem DualHallObstruction_baseLeaf_or_certifiedSwitch
    (rowDB : RowDB) (C : TerminalCage) (X : K2Component) (y : CutEdgeWeight)
    (hDual   : ViolatesShortestGeodesicHall rowDB X y)
    (hReduced: ReducedShell rowDB C)
    (hNoBase : NoPrunableBaseLeaf rowDB C X)
    (hGammaMin : GammaMinimalAmongConnectedMaximumCuts rowDB) :
    exists W : VertexSet,
      ZeroSlackSwitch rowDB W /\
      ConnectedAfterSwitch rowDB W /\
      GammaOfCut rowDB (switchCut rowDB W) < GammaOfCut rowDB.currentCut
Per-instance certs (replace existential): checkZeroSlackSwitch W = true,
checkConnectedAfterSwitch W = true, checkGammaDropByRecompute W = true.

### The EXACT Gamma identity (verbatim §, still the anchor)
Gamma(B) - Gamma(B^W) = ell_B(e)^2 + ell_B(f)^2 - ell_{B^W}(d0)^2 - ell_{B^W}(d1)^2
                        + StableGain(W)
StableGain(W) = sum_{h stable} (ell_B(h)^2 - ell_{B^W}(h)^2)   [CAN be negative: -56]
So the theorem MUST prove: LocalSaving(W) + StableGain(W) > 0 for the dual-selected W.

### §7 Why dual obstruction might force net positivity (THE PROOF ARCHITECTURE, verbatim)
"The only plausible structural reason is a coarea identity:
  DualDefect(y) = weighted average over candidate switches W of
                    [LocalSaving(W) + StableGain(W)]  +  nonnegative residuals.
If the dual defect is positive, at least one switch has positive exact Gamma drop.
This is analogous to proving a max-flow min-cut theorem by sweeping level sets of a
potential. The stable-row losses are not ignored; they must appear with signs in the
coarea identity."

The proof does NOT prove StableGain(W) >= 0 per-W (FALSE). It proves that AVERAGED over
the dual-selected laminar sweep, local savings dominate all stable losses => one interval
must be strictly good (averaging / coarea).

### HONEST STATUS (my assessment)
GPT-Pro frames the coarea identity as "the only PLAUSIBLE structural reason" — i.e. a
RESEARCH CONJECTURE, not a proof. The identity itself is UNPROVEN. This is the SAME
verdict as before: gap#1's crux (Gamma <= N^2 via GERSH spreading-feasibility) is a
genuine multi-month research theorem. The advance from reply 18 is a SHARP, TESTABLE
proof target: the dual-defect coarea identity.

### NEXT DECISIVE TEST (the counterfactual question)
The switch theorem's premise is hDual = ViolatesShortestGeodesicHall (a spreading-
INFEASIBLE Gamma-min max-cut component). EMPIRICALLY (all my gates) this premise NEVER
occurs: 0 infeasible on 71820 census cages + blowup families. If infeasibility is
IMPOSSIBLE for a real Gamma-min max-cut (because it would locally violate the
conjecture), the theorem is inherently PROOF-BY-CONTRADICTION and the coarea identity
is the unproven mechanism converting "assume infeasible" into "Gamma-decreasing switch
exists". Decisive gate: exhaustively search for ANY spreading-infeasible Gamma-min
max-cut component. Result pending in _claude_infeasible_premise_gate.py.

================================================================================
## DECISIVE PREMISE GATE (2026-07-08) — SWITCH-THEOREM PREMISE IS COUNTERFACTUAL
================================================================================
File: _claude_infeasible_premise_gate.py  (EXACT rational demand, HiGHS LP = true Hall test)

QUESTION: GPT-Pro reply 18's switch lemma has hypothesis hDual=ViolatesShortestGeodesicHall
(a spreading-INFEASIBLE per-K2-component of a triangle-free Gamma-min max cut). The whole GERSH
proof is by contradiction: infeasible component => Gamma-decreasing switch => not Gamma-min. Does
the premise EVER occur? Tested the STRICTEST form: per-K2-component (cannot borrow other components'
cut-edge capacity), all-shortest-geodesics max-flow, demand ell(e)^2, cut-edge cap 25.

RESULT (71910 per-K2-components: census N<=11 + C5[t] t<=6 + even-chord N=18..30 + bare odd C_n to N=31):
  * ratio-INFEASIBLE (Gamma_X > 25 b_X): 0
  * LP-INFEASIBLE (full Hall fails): 0
  * MAX tightness ratio rho_X = Gamma_X/(25 b_X) = 529/550 ~ 0.9618  @ C_23, a SINGLE-atom odd cycle
    (ell=23, Gamma_X=529=23^2, b_X=22=ell-1). This is EXACTLY the ell^2 <= 25(ell-1) boundary.
  * MULTI-atom components: total ratio <= 121/250 ~ 0.484 (census). Over 2x slack everywhere.

INTERPRETATION (crux reframing):
  1. The switch-theorem premise NEVER occurs on a real Gamma-min max cut => it is COUNTERFACTUAL.
     Proof-by-contradiction of a universally-true statement still needs the full deductive argument,
     but NO empirical gate can confirm/refute the switch theorem (its premise is empty). Further
     gating of the switch is pointless; the argument must be purely deductive.
  2. The TIGHTEST real case is the SINGLE-atom odd cycle C_23: rho = ell^2/(25(ell-1)), -> 1 as
     ell -> 23.96 (root of ell^2=25(ell-1)). At ell=23 rho=529/550<1; ell=25 would be rho>1 but is a
     BASE LEAF (ell>23, excluded). Single-atom story is FULLY Lean-closed:
        ell<=23: atom_sq_le_25_shortAtom (ell^2 <= 25(ell-1) = 25 b_X)              [PROVEN]
        ell>=25: leaf_demand_le_of_ell_le_N + fullSupport_leaf_absorbed_by_density  [PROVEN framework]
  3. The ONLY open piece is MULTI-atom components (>=2 atoms sharing cut edges): the genuine Hall
     condition. Equivalent form (doc line 210): NO cut edge carries load > 25 in the optimal spread
     (BOUNDED CONGESTION). Empirically 2x slack. This is a DIRECT per-component capacity bound, NOT a
     coarea sweep over a vacuous premise.

REFRAMED TARGET for tomorrow (GPT-5.6 / Fable-5):
  Prove the multi-atom bounded-congestion Hall: for a K2-component X (>=2 atoms) of a triangle-free
  Gamma-min max cut, the optimal fractional spread of demands {ell(e)^2} over shortest-geodesic cut
  edges keeps every cut-edge load <= 25. Equivalently sum_{e in S} ell(e)^2 <= 25 |union_{e in S} P_e|
  for every subset S (Hall/Gale-Hoffman). Large empirical slack (>=2x) suggests a SOFT counting /
  triangle-free-girth argument, not the delicate DualDefectCoareaSwitch. The coarea/switch is one
  (hard, counterfactual-premise) proof route; the direct bounded-congestion Hall is the cleaner one.

================================================================================
## COMPLETE MIN-MAX-LOAD EXTREMAL CHARACTERIZATION (2026-07-08) — HANDOFF FOR GPT-5.6/FABLE-5
================================================================================
Gates: _claude_infeasible_premise_gate.py, _claude_minmaxload_gate.py, _claude_multiatom_congestion_probe.py,
       + census multi-atom scan + pentagon-book B_k probe. EXACT rational demand, HiGHS min-max-load LP.

L* := min achievable MAX cut-edge load when demands {ell(e)^2} are fractionally spread over shortest-geodesic cut
edges (feasibility at cap 25 <=> L* <= 25 <=> spreading-Hall holds). By b-matching LP duality:
   L* = max_{S subset of atoms} [ sum_{e in S} ell(e)^2 ] / | union_{e in S} P_e |.

THE COMPLETE PICTURE (triangle-free Gamma-min MAXIMUM cuts):
  (1) SINGLE-atom component = odd cycle C_ell: L* = ell^2/(ell-1). Monotone increasing in ell; max short atom
      ell=23 => 529/22 = 24.0455 < 25; ell=25 => 625/24 = 26.04 > 25 but ell>=25 is a BASE LEAF (excluded, absorbed
      by density). This is the TRUE GLOBAL EXTREMAL. FULLY LEAN-PROVEN: atom_sq_le_25_shortAtom (ell<=23) +
      leaf_demand_le_of_ell_le_N (ell>=25).
  (2) MULTI-atom components: census N<=11 max L* = 10.0000 (N=10 graph g6=I?AAD@wF_, atoms (3,9),(4,9) both ell=5
      incident to vertex 9, two pentagons sharing 3 geodesic cut edges, b_X=5). PLATEAUS at 10.0 across N=10 AND
      N=11 (24349 multi-atom comps). C5[t] blow-up family: L* = 6.25 for ALL t (large-N multi-atom stays LOW).
      => multi-atom congestion is BOUNDED WELL UNDER 25 and under the single-atom global max (24.05).
  (3) PREMISE L*>25 (ViolatesShortestGeodesicHall): NEVER occurs (0 / 71910 per-K2-components incl binding regime).

THE MAX-CUT SUPPRESSION MECHANISM (the structural reason, 3 independent confirmations):
  Every attempt to CONSTRUCT a high-congestion multi-atom component is defeated because max-cutness MINIMIZES the
  number of atoms (uncut same-side edges) and refuses forced geodesic-sharing:
   (a) THETA graphs Theta(a,b,c) [170 tested, N<=24]: 0 multi-atom components -- the 3-path frustration always
       resolves to a SINGLE bad edge (one long odd cycle), never 2 sharing a geodesic.
   (b) PENTAGON-BOOK B_k (k pentagons hand-built to share a 3-edge spine, predicted L* -> 25k/(k+3) -> 25): the MAX
       CUT COLLAPSES to ONE atom; L* actually DECREASES with k (B_2:4.17 ... B_9:1.25). Max cut takes 1 defect not k.
   (c) SYMMETRIC generalized Petersen GP(n,2) [N<=22]: many ell=5 atoms but WELL-SPREAD, b_X large, L*=6.25.
  Interpretation: a high-congestion config would admit a RECOLORING (switch) that reduces BOTH atom-count AND Gamma
  -- i.e. it violates max-cut/Gamma-min optimality. THIS is exactly GPT-Pro's DualHallObstruction switch: the switch
  existence IS the formalization of "max-cutness suppresses high congestion". The switch premise is counterfactual
  precisely because max-cutness already forbids the configuration.

HONEST STATUS: the multi-atom bounded-congestion L*<=25 is a GENUINE obligation (NOT reducible to the single-atom
lemma: multi-atom L*=10 > 6.25 = same-ell single envelope), but the true GLOBAL extremal is the single-atom C_23
(Lean-proven), and multi-atom is empirically suppressed to <=10. A PROOF still needs either (i) GPT-Pro's switch/
coarea (deductive, counterfactual-premise), or (ii) a direct "max cut minimizes atom count => bounded congestion"
structural theorem. The direct route (ii) is the cleaner target: prove that no triangle-free MAX cut has a K2-
component with L* > 25, via the suppression mechanism (a Gamma-decreasing recoloring exists otherwise). 2x+ slack
everywhere suggests this is provable by a soft optimality argument, not a delicate sweep.

TOMORROW (GPT-5.6/Fable-5) SHARP TARGET: prove BoundedCongestion: for a triangle-free MAXIMUM cut that is Gamma-
minimal, every K2-component has min-max cut-edge load L* <= 25. Equivalent Hall form + the max-cut suppression
mechanism (constructions above) are the evidence. The single-atom case is DONE (Lean); only multi-atom remains,
with the global extremal already below 25 and multi-atom suppressed to <=10.

================================================================================
## GPT-Pro REPLY 19 (2026-07-08) — FERRERS SHORTEST-ROUTING replaces the switch (CONVERGENCE)
================================================================================
GPT-Pro AGREES the switch is not the route. "The corrected spreading result suggests a much cleaner route than the
global switch theorem." NEW decomposition of the multi-atom Hall:

STEP 0 (normalize): d_e = ell(e)-1, rho_e = ell(e)^2/(25 d_e). Routing ell^2 over a shortest path of length d_e with
cut-edge cap 25 == routing rho_e units along a shortest B-geodesic with cut-edge cap 1.
  ell<=23 => rho_e <= 1 (ell=23: 529/550, matches my max ratio EXACTLY). ell>=25 => rho_e>1 = BASE LEAF (density thm).

STEP 1 (CAPACITY / CUT CONDITION -- PROVEN, two lines): for every vertex subset U,
  DemandCross(U) = sum_{e crossing U} rho_e <= sum_{e crossing U} 1 = M_cut(U) <= B_cut(U) = |delta_B(U)|.
  The middle inequality M_cut(U) <= B_cut(U) IS max-cutness (flip U: Delta_cut = M_cut(U)-B_cut(U) <= 0). rho_e<=1 is
  the ell<=23 reduction. => the full undirected cut condition holds SOFTLY. "This is the soft reason the multi-atom
  spreading LP has so much slack. The square-length difficulty disappears after the ell<=23 reduction."
  [CLAUDE NOTE: this is a genuine two-line proof of the capacity half, using only max-cut + ell<=23. No empirical gate needed.]

STEP 2 (REALIZABILITY -- the ONLY remaining theorem): FerrersShortestRouting_cutCondition_complete. Can the cut-condition
routing be realized using ONLY shortest B-geodesics? Shortest-routing polytope:
  x(e,P)>=0 ; sum_{P in Rows(e)} x(e,P) = rho_e ; sum_{e,P: c in P} x(e,P) <= 1  for every cut edge c.
  Version A (consecutive-ones): an ordering of cut edges s.t. every shortest path's edge set is an INTERVAL and each
    commodity's shortest paths form an interval-convex family => path-edge matrix is TU/interval-balanced => prefix
    Hall (=cut condition) is SUFFICIENT.
  Version B (laminar min-cut): shortest-geodesic routing feasible iff cut conditions hold, for interval/Ferrers systems.
GPT-Pro HONEST (sec 8): "much softer than the global switch theorem, but it still needs a real theorem: Ferrers
shortest-routing cut conditions are sufficient. This is a known type of statement for interval/Ferrers/consecutive-
ones systems, and it is plausibly formalizable." Final: "FerrersShortestRouting_cutCondition_complete replaces the
global switch theorem as the best final route for the multi-atom Hall."

SPLIT (structurally natural, non-circular):
  ell<=23  -> cut-edge/Ferrers shortest-routing (capacity PROVEN, realizability = FerrersShortestRouting)
  ell>=25  -> base density/prune (Lean-PROVEN leaf_demand_le) or switch/reducibility

CLAUDE CONVERGENCE: this matches my extremal characterization -- multi-atom L* suppressed to <=10 BECAUSE max-cutness
gives the cut condition with slack. The DECISIVE next test = does the shortest-geodesic path-edge incidence matrix
have the consecutive-ones (interval) property? (Version A). Gate: _claude_c1p_ferrers_gate.py (brute edge-ordering
search for small multi-atom components, incl the L*=10 extremal g6=I?AAD@wF_).

--- C1P GATE RESULT (2026-07-08, _claude_c1p_ferrers_gate.py) ---
Version A (consecutive-ones / interval-TU) is NOT the universal mechanism:
  L*=10 extremal g6=I?AAD@wF_ : C1P YES (1/1)
  census N=8 : 6 multi-atom tested, 1 C1P, 5 NOT-C1P
  census N=9 : 29 tested, 5 C1P, 24 NOT-C1P
  census N=10: 231 tested, 44 C1P, 187 NOT-C1P  (~80% NOT-C1P)
All are FEASIBLE (L*<=25) yet ~80% lack the path-C1P structure => the shortest-geodesic path-edge matrix is generally
NOT an interval matrix. Cut-condition-SUFFICIENCY holds (feasibility does) but NOT via Version A TU. Feasibility comes
from the EDGE-LEVEL b-matching freedom (demand ell^2 splits over ALL shortest-geodesic cut edges), not path-intervals.
CONSEQUENCE: FerrersShortestRouting must be proved via Version B (laminar min-cut) OR by closing the gap between
GPT-Pro's PROVEN vertex-cut condition (sum_{e crossing U} rho_e <= |delta_B(U)|) and the b-matching ROW-SUBSET Hall
(sum_{e in S} ell^2 <= 25|union P_e(S)|) that actually governs feasibility -- these are DIFFERENT cut families; the
reduction vertex-cut => row-subset-Hall is the real open step. Retasking GPT-Pro on this exact gap.

================================================================================
## GPT-Pro REPLY 20 (2026-07-08) — FRACTIONAL CUT-COVER bridge (the correct one)
================================================================================
C1P failing rules out interval/TU but NOT a direct proof. The correct bridge = a FRACTIONAL CUT-COVER certificate.

TARGET (row-subset b-matching Hall): for S subset of bad rows of K2-component X, w_e = ell(e)^2/25,
  E(S) = union of cut edges on >=1 shortest B-geodesic of some e in S. Want  sum_{e in S} ell(e)^2 <= 25 |E(S)|.

CERTIFICATE (CutCoverCert): weights lambda_U >= 0 on VERTEX cuts U with
  (COVER)      forall e in S:  sum_{U separates endpoints(e)} lambda_U  >=  ell(e)^2 / 25
  (CONGESTION) forall cut edge c in B:  sum_{U : c in delta_B(U)} lambda_U  <=  indicator(c in E(S)).

PROOF (exact, no C1P) -- given the certificate:
  sum_{e in S} ell^2/25 <= sum_{e in S} sum_{U sep e} lambda_U = sum_U lambda_U |delta_M(U) cap S|
     <= sum_U lambda_U |delta_M(U)|  <=(MAXCUT)  sum_U lambda_U |delta_B(U)|
     = sum_{c in B} sum_{U: c in delta_B(U)} lambda_U  <= |E(S)|.
  x25 => row-subset Hall. ONLY graph input = max-cutness |delta_M(U)| <= |delta_B(U)|.

LEAN SHAPE: checkCutCover (verify COVER+CONGESTION, Bool) + checkCutCover_sound (the summation, PROVABLE per-instance)
+ residual ShortestRowCutCover_exists (universal existence). GPT-Pro: multi-atom max ratio ~0.48 => cut-cover has
SLACK, "may be easier to construct than the primal path flow".

CLAUDE ASSESSMENT: by LP duality (Farkas), ShortestRowCutCover_exists <=> row-subset Hall (EQUIVALENT), so this is
certification-grade (per-instance exhibit+check, exact) UNLESS there is a CANONICAL geometric construction of lambda_U.
Natural candidate = DISTANCE-BALL cuts U_{v,r}={cut-dist(v,.)<=r} along geodesic LAYERS = the old COAREA measure
resurfacing. Decisive test = does a canonical ball-cut lambda satisfy COVER+CONGESTION universally? Gate: _claude_cutcover_ballcut_gate.py.

--- PATH-ROUTING vs B-MATCHING GATE RESULT (_claude_pathrouting_vs_bmatching_gate.py) ---
GPT-Pro reply 19's STRONGER path model (rho_e=ell^2/(25(ell-1)) along whole shortest geodesic PATHS, cap 1):
FEASIBLE (L*_path<=1) on ALL 24350 multi-atom components, MAX L*_path = 0.5 (2x slack) at the N=10 extremal.
=> FerrersShortestRouting CONCLUSION empirically true even where C1P fails; the route is VIABLE, needs Version B proof.

--- BALL-CUT CUT-COVER RESULT (_claude_cutcover_ballcut_gate.py, GRAPH-metric balls) ---
Canonical GRAPH-distance ball cuts U_{v,r}={u:dist_G(v,u)<=r} with delta_B(U) subset E(S): FEASIBLE 24262/24349
multi-atom components (99.64%), INFEASIBLE 87 (0.36%, first at N=10 two ell=5). So plain graph-metric balls are
ALMOST but NOT fully sufficient. NEXT refinement: CUT-METRIC balls (BFS using ONLY cut edges) -- their boundaries are
exactly geodesic layers, the natural canonical family for shortest-geodesic routing. Testing in _claude_cutmetric_ballcut_gate.py.

================================================================================
## DECISIVE: GPT-Pro REPLY 20 CUT-COVER IS UNSOUND (2026-07-08, Claude falsifier)
================================================================================
_claude_stubborn19_cutfamily_gate.py + hand-verification on g6=J?AAD@oV?]? (N=11):

The fractional CUT-COVER certificate of reply 20 is INFEASIBLE even with ALL 2^n cuts on >=19 census components,
WHILE the target Hall holds. Smallest witness: K2-component atoms=(4,10),(5,9) both ell=5, |E(S)|=5.
  * Hall HOLDS: Gamma_X = 50 <= 125 = 25|E(S)|; min-max-load L* = 10 <= 25 (b-matching FEASIBLE).
  * Cut-cover INFEASIBLE (all 2^11 cuts): atom (5,9) has ZERO cuts U separating it with delta_B(U) subset E(S).
    Reason: any vertex-cut separating 5 and 9 crosses a cut edge OUTSIDE E(S) (the rest of the graph), which the
    CONGESTION condition (sum lambda = 0 for c not in E(S)) FORBIDS. So COVER for (5,9) (sum lambda >= 1) is
    unsatisfiable. The delta_B(U) subset E(S) restriction is FORCED by CONGESTION and kills all separating cuts.

CONSEQUENCE: reply 20's ShortestRowCutCover_exists is STRICTLY STRONGER than row-subset Hall and PROVABLY FALSE on
real components. The soundness direction (cert => Hall, checkCutCover_sound) is a VALID one-way implication, but the
certificate DOES NOT EXIST where Hall holds, so it CANNOT prove Hall universally. GPT-Pro conflated graph VERTEX-cuts
(delta_M/delta_B) with the b-matching's (atoms -> geodesic cut edges) bipartite structure; the correct LP dual of the
b-matching Hall is a fractional bipartite vertex cover of the (atom, cut-edge) incidence, NOT a graph vertex-cut cover.
=> reply 20 route DEAD. Reply 19 path-routing (feasible 24350/24350, 2x slack) and reply 18 switch (counterfactual
premise) remain; the honest target is the b-matching row-subset Hall proven DIRECTLY (max_S sum ell^2/|E(S)| <= 25).

STATUS: gap#1 multi-atom Hall remains OPEN; the cut-cover reframing was a WRONG turn (caught by exact gate). The
capacity vertex-cut condition (max-cut |dM(U)|<=|dB(U)| + rho<=1) is still PROVEN but does NOT bridge to row-subset
Hall via this cut-cover. Single-atom Lean-proven; multi-atom = genuine open theorem. P(gap#1 math) ~48.

--- GPT-Pro REPLY 21 (2026-07-08) — CONVERGES with the falsifier ---
Reply 21 proposed the "canonical family" = all cuts U with delta_B(U) subset E_short(S) = unions of components of
Q_S = B \ E_short(S). This is EXACTLY the family my Gate-1 (_claude_stubborn19_cutfamily_gate) enumerated and found
INFEASIBLE on all 19 stubborn N=11 components. GPT-Pro itself flagged the caveat:
  sec 2: "this cut-cover proof is only a SUFFICIENT mechanism for row-edge Hall. It may be stronger than necessary."
  sec 6: "Cut-cover LP ... is NOT obviously equivalent to b-matching Hall. It may be STRICTLY STRONGER."
  sec 9: "I cannot currently turn these [soft heuristics] into a rigorous inequality without essentially proving
          ShortestSupportExpansion. A local 'how many rows through one edge' bound is FALSE in tight blow-ups ...
          the soft proof should be GLOBAL EXPANSION, not local congestion."
  sec 10 Gate 1 = quotient-cut cover (my gate: DEAD), Gate 2 = per-instance primal b-matching q(e,c) cert (robust
          Lean path but cannot close the UNIVERSAL theorem -- infinite component family).
CONVERGED HONEST STATE: gap#1 multi-atom = ShortestSupportExpansion: for a triangle-free MAX cut, sum_{e in S}
ell(e)^2 <= 25|E_short(S)| for every row subset S. HOLDS on 71910 comps, 2x slack. NO working universal proof route
from today's GPT-Pro replies: 18 switch (counterfactual premise 0/71910), 19 path-routing (true but proof = same open
expansion), 20/21 cut-cover (UNSOUND -- strictly stronger, fails on 19). Genuine OPEN combinatorial expansion theorem;
general shortest-path multicommodity has O(log k) flow-cut gap so cut-condition alone does NOT suffice -- the constant
25=5^2 must come from girth-5 + geodesic + max-cut structure. Sent GPT-Pro the known-vs-open question (reply 22 pending).
P(gap#1 math) ~45-48 (honest; cut-cover detour closed, core expansion untouched).

================================================================================
## ADVERSARIAL AUDIT WORKFLOW (2026-07-08, wf_e07ead3d-7ae, 10 agents, 515k tok) — INDEPENDENT VERDICT
================================================================================
Six claims audited (high effort), load-bearing ones re-verified by independent skeptics. Results:

PROVEN SOLIDLY (survived audit; C3 survived BOTH audit + skeptic):
  * C1 capacity: for a MAX cut, |delta_M(U)| <= |delta_B(U)| for EVERY vertex set U (flip U changes cut by
    |delta_M(U)|-|delta_B(U)| <= 0). Exact, unconditional. LOAD-BEARING, correct.
  * C2: rho_e = ell^2/(25(ell-1)) <= 1 iff ell in [5,23]; first failure ell=24 (576>575). Exact.
  * C3 cut-cover SOUNDNESS (sufficiency ONLY): feasible lambda => sum ell^2 <= 25|E(S)|, weak-duality chain exact
    (Fubini valid since S subset M; C1 step; congestion forces off-E(S) sums to 0). Proves feasible=>Hall, NOT existence.
  * C5: L* = max_S sum ell^2/|E(S)| (Gale-Hoffman); single-atom ell^2<=25(ell-1) points WRONG way for multi-atom;
    two ell=5 with |E(S)|=5 give 10 > 6.25 => multi-atom is a GENUINELY separate obligation. LOAD-BEARING, correct.

FLAWED (route-killing):
  * C4 circularity: FLAWED. Cover-existence is NOT the LP-dual of Hall. Farkas-dualizing the cover LP gives cut-
    incidence multipliers with per-cut constraint sep_S(U) <= |delta_B(U) cap E(S)|, which FAILS exactly when two
    atoms' geodesics cross a cut at a SHARED edge (sep=2>1) = the multi-atom overlap regime. So cover is STRICTLY
    STRONGER than Hall (flow-cut gap) and can be INFEASIBLE where Hall holds (= my Gate-1 falsifier, independently
    re-derived by BOTH auditor and skeptic). Cut-cover reframing is circular-where-equal, strictly-harder-where-not:
    NOT a genuine reduction. DEAD.
  * C6 known-vs-open: FLAWED -- MY FRAMING WAS WRONG (important correction). The b-matching is SINGLE-COMMODITY
    (atom charge ell^2 absorbed by ANY cut edge in P_e; fungible sinks cap 25; no designated targets). So the O(log k)
    MULTICOMMODITY flow-cut gap / Okamura-Seymour / Hu / planarity reasoning is a CATEGORY ERROR -- irrelevant. By
    MFMC/Gale-Hoffman, feasibility <=> the inequality (both directions, no gap, no planarity). That equivalence is
    VACUOUS (proves neither side). The genuine open content = the EXTREMAL INEQUALITY sum ell^2 <= 25|E(S)| HOLDS on
    these graphs, matched by NO known theorem = OPEN extremal combinatorics.

SYNTHESIS: cutcover = CIRCULAR/strictly-stronger (not a reduction); residual = OPEN; P(gap#1 math) = 45. No decisive
obstruction to the TRUTH (bulletproof: 0/71910, 2x slack), but a decisive obstruction to the cut-cover PROOF ROUTE.
SHARPEST NEXT ATTACK (workflow): abandon cut-cover; prove L* = max_S sum ell^2/|E(S)| <= 25 DIRECTLY by discharging/
exchange on the density-maximizing S*: (1) EXCHANGE LEMMA -- extremal S* is a union of SHORT (ell=5-dominated) atoms
(swap out a long/high-charge atom without decreasing density; observed tight/near-tight = two-ell=5-sharing-3-edges +
C5[t]); (2) on short-atom S*, bound ell=5 shortest-geodesic sharing per cut edge via triangle-free girth-5 geometry
(no two shortest 4-edge geodesics between distinct bad pairs overlap in >k edges without a short even cycle) => local
load bound summing to L*<=25.
TENSION to watch: GPT-Pro reply 21 sec 9 warns a NAIVE local per-edge bound is FALSE in blow-ups (feasibility needs
spreading over ALL geodesics); the exchange step (1) restricting to the EXTREMAL S* is what must make the local step (2)
valid. VALIDATION GATE: is the density-max S* always short-atom-dominated? -> _claude_extremal_subset_gate.py.
CORRECTION TO MY GPT-Pro MESSAGES: I wrongly invoked the multicommodity O(log k) gap; the problem is single-commodity,
so the open content is the inequality itself, an extremal-combinatorics fact (not a flow-sufficiency question).

================================================================================
## GPT-Pro REPLY 22 + EXCHANGE GATE (2026-07-08) — TRIPLE CONVERGENCE: ShortestSupportExpansion is OPEN
================================================================================
GPT-Pro reply 22 VERDICT (converges with the audit workflow AND my gates):
"ShortestSupportExpansion is NOT a known off-the-shelf multicommodity theorem ... a GENUINE NEW combinatorial theorem
for this project." Rules out every standard tool: max-flow/min-cut (single-commodity, vacuous), Okamura-Seymour (not
planar/cofacial + shortest-geodesic not arbitrary paths), general multicommodity (nonconstant gaps), C1P (empirically
false), vertex-cut/quotient-cut-cover (my Gate-1 falsifier = "DECISIVE ... this bridge is FALSE"), tree/median.
sec 2: "The true expansion is NOT simply a weighted sum of vertex-cut inequalities. It is a property of the row-edge
SUPPORT HYPERGRAPH ... The proof must reason about that support hypergraph directly."
sec 5 (KEY, contradicts the workflow's local step): "Is there a softer local congestion bound? PROBABLY NOT in a
simple per-edge form. 'No cut edge lies in too many shortest supports' is FALSE -- C5[t] blow-ups have very high local
sharing. Feasibility comes from the ability to SPREAD over many shortest geodesics, not from low local incidence. The
true quantity is GLOBAL EXPANSION: large row set -> large union of shortest-support edges."
sec 6: needs the COMBINATION reduced-nonbase K2 + all-shortest-geodesic support + Gamma-minimality/no-recut + no
prunable base leaf. Target: MinimalShortestSupportObstruction_reduces_or_switches OR directly ShortestSupportExpansion.
"This is a research theorem, not an invocation of a known multicommodity-flow result."

EXCHANGE GATE (_claude_extremal_subset_gate.py, census N<=11): the GLOBAL density-max multi-atom subset is
sum ell^2/|E(S)| = 10 at ells=[5,5] (N=10); NO mixed/long subset exceeds it (mixed [5,7] gives 37/7~5.29 < 10). So the
density-max S* IS short-atom (ell=5) dominated -- the workflow's EXCHANGE LEMMA SPIRIT HOLDS. (The gate's "26 long-beats-
short / CHALLENGED" is an artifact: mixed-only components have no all-ell=5 pair so "best all-short"=0 is beaten
trivially; those densities are LOW.) 26 mixed-length multi-atom comps exist at N=11; none beat 10.

WORKFLOW vs GPT-Pro RECONCILED: workflow attack = (1) exchange to short-atom S* [SUPPORTED by gate] + (2) local girth-5
per-edge bound [GPT-Pro: FALSE, C5[t] high local sharing]. Correct synthesis: step (1) stands; step (2) must be GLOBAL
EXPANSION of the ell=5 support hypergraph: |E_short(S)| >= (1/25) sum ell^2 = |S| for ell=5 sets (a Hall/SDR/expander
condition; empirically |E_short(S)| >= 2.5|S| since density<=10). So the CLEAN OPEN TARGET:

  SHORTESTSUPPORTEXPANSION (ell=5 core): for a reduced-nonbase K2-component of a triangle-free Gamma-min MAX cut, the
  bipartite incidence (ell=5 bad edges) -- (their shortest-geodesic cut edges) satisfies |E_short(S)| >= |S| for every
  atom subset S (Hall/expander). Plus single long atoms (Lean-proven ell^2<=25(ell-1)) + base leaves (density) handle
  ell>=7. This is the genuine open research theorem; empirically 2.5x slack.

TRIPLE-CONVERGED HONEST STATE: gap#1 multi-atom = ShortestSupportExpansion, OPEN research theorem, no off-the-shelf
proof, GLOBAL expansion mechanism. P(gap#1 math) ~45. Clean handoff for GPT-5.6/Fable-5 tomorrow.

--- ELL=5 SUPPORT-OVERLAP GROUND TRUTH (_claude_ell5_overlap_gate.py, census N<=11 + C5[t]) ---
Structural facts for the ShortestSupportExpansion proof (feeds proof-attack workflow + tomorrow):
- |P_e| (geodesic cut edges per ell=5 atom) distribution: {4:7067, 6:12083, 7:3174, 8:13279, 9:61400}. MOST atoms
  have LARGE support (9); |P_e|=4 (single geodesic) is the minority = the BINDING/tight case.
- |P_e cap P_f| overlaps range 0..105 (huge in C5[t]); max d(c)=49 (one cut edge on 49 atoms' supports in C5[t]).
- DISTINCT atoms with EQUAL supports P_e==P_f: 1772; NESTED (subset): 2196. => the NAIVE SDR (assign each atom a
  distinct edge, injective by support) is BLOCKED -- distinct atoms genuinely share/repeat supports.
- BUT density<=10 (verified) => any support shared by j atoms has size >= 2.5j (a support of size m is shared by at
  most 0.4m atoms; two |P_e|=4 atoms share <=3, never 4). So Hall |E_short(S)|>=|S| holds via SUPPORT LARGENESS, not
  small overlap. This is the exact content of GLOBAL expansion: large row set forced onto proportionally large edge union.
CONSEQUENCE FOR THE PROOF: the mechanism is NOT "few atoms per edge" (max d(c)=49) NOR "small pairwise overlap"
(up to 105); it is that each atom's support is LARGE (>=4, typically >=6) and the girth-4/max-cut structure prevents
too many atoms from collapsing onto a small common support. The clean sub-lemma to prove: a set of ell=5 atoms sharing
a common support of size m has at most ~0.4m members (equivalently |E_short(S)| >= 2.5|S|), from girth-4 + max-cut.

================================================================================
## GPT-Pro REPLY 23 (2026-07-08) — MINIMAL-HALL-OBSTRUCTION route for Ell5SupportExpansion
================================================================================
Clean target restated: Ell5SupportExpansion -- reduced nonbase K2-comp of triangle-free Gamma-min MAX cut, every set
S of ell=5 atoms: |E_short(S)| >= |S|. "Not a known theorem; a new expansion theorem, but MUCH more approachable than
the global switch because all rows have length 4 and any Hall obstruction has a rigid local form."

PROOF SKELETON (GPT-Pro's "cleanest route", NOT spectral/entropy):
 1. minimal_hall_obstruction_no_private_edge (PURE finite-set algebra, Lean-ready): a MINIMAL Hall obstruction S has
    |S| = |E(S)|+1 (tight incidence 2-core) and every row's support edges are all SHARED (no private edge). [STANDARD
    minimal-counterexample reduction -- correct.]
 2. P4P4_shared_edge_classification (THE first local theorem to gate): two ell=5 rows e,f sharing a cut edge c fall
    into EXACTLY 4 types: (I) C5BookParallel, (II) S1ThetaPattern, (III) ReducibleSubcagePattern, (IV) ForbiddenShortcut.
 3. In a minimal obstruction every row has all 4 P4 edges shared; classify: Type II => S1/S2 door/switch/reducible =>
    impossible in reduced Gamma-min (uses "GammaMin + local recut theorem"); Type III => contradicts reducedness;
    Type IV => contradicts triangle-free/shortestness. => ALL sharing is Type I C5-book parallel.
 4. C5BookSupportExpansion: a union of C5-book blocks has |S| <= |E_short(S)|. => contradiction.
 5. Reduction from general S: DensityMaximizedByEll5Subset (my exchange gate confirms density-max is all-ell=5);
    ell=7..23 rows via single-row ell^2<=25(ell-1) + extra private support / base/theta reduction.

CLAUDE ASSESSMENT: this is a CLEANER DECOMPOSITION (Lean-tractable, gate-able) but does NOT escape the switch -- step 3
Type-II => contradiction uses the SAME S1/S2 theta-switch/local-recut primitive that the earlier S1 re-audit flagged as
a GENUINE OPEN WALL (and whose premise is counterfactual). So the minimal-obstruction route RE-LOCALIZES the open switch
to the Type-II case rather than removing it. Genuine progress: (a) minimal-obstruction reduction is standard+Lean-ready;
(b) C5-book expansion is explicit/tractable; (c) the OPEN residual is now the 4-type classification EXHAUSTIVENESS + the
Type-II theta contradiction (= the switch primitive). CHECKABLE: is P4P4_shared_edge_classification exhaustive? (needs
GPT-Pro's exact geometric type definitions to gate). Also note my overlap ground truth: ell=5 rows have LARGE, often
EQUAL/heavily-overlapping supports (|P_e| up to 9, |P_e cap P_f| up to 105) -- the single-chosen-P4 classification must
handle multi-geodesic rows carefully. P(gap#1 math) ~45 (route cleaner + more Lean-tractable, but core switch primitive
persists at Type II).

================================================================================
## PROOF-ATTACK WORKFLOW (2026-07-08, wf_82f1381a-8a5, 6 agents, 539k tok) — MAJOR VERIFIED ADVANCE
================================================================================
Five independent proof strategies attacked Ell5SupportExpansion (|E_short(S)|>=|S| for ell=5 atoms). honest_status:
STRONG_PARTIAL (no complete proof, but substantial RIGOROUS partials; several cross-verified by my exact gates):

RIGOROUS UNCONDITIONAL RESULTS (proofs in tasks/wgb1dsh9j.output):
 - RIGIDITY (girth): |P_e|=4 => e has a UNIQUE 4-edge geodesic whose degree-1 vertices are exactly {u,v}; so P_e
   determines e. Hence distinct atoms with |P_e|=4 never have equal support. (Explains my overlap gate: equal-support
   pairs are all MULTI-geodesic.)
 - OVERLAP (girth): two distinct atom geodesics share <=3 edges; =3 forces consecutive + shared endpoint = the ratio-5/2
   extremal.
 - HALL FOR |S|<=5: UNCONDITIONAL (from |P_e|>=4 + rigidity). Tight (ratio 5/2 at |S|=2). First open card |S|=6.
 - HALL FOR |S|<=8: RIGOROUS computer-assisted. Minimal violator's geodesic graph F is connected with m=|S|-1 edges
   (<=8 vertices); nauty enumeration of ALL connected graphs on <=8 vertices gives max(D4(F)-m) = -1 (D4=#distance-4
   pairs), contradicting the required m+1<=D4(F). Counting saturates at m=8 (double-star tree, D4=m+1).
 - MINIMAL-VIOLATOR STRUCTURE: a minimal Hall violator S has |E_short(S)|=|S|-1=m; F=(V,E_short(S)) CONNECTED bipartite
   with m edges; S = m+1 distinct red edges on F-distance-4 pairs; m+1<=D4(F).
 - MAX-CUT VERTEX CONDITIONAL CLOSURE: if NO "excess" blue edge is incident to V(F) outside F, then Sum_{V(F)} blue-deg
   = 2m < 2(m+1) = Sum #atoms-incident contradicts red-deg<=blue-deg => Hall. So a minimal violator MUST carry >=2
   excess blue-edge endpoints at V(F). SHORTCUT LEMMA: any excess blue edge xz has d_blue(z,x')!=3 for every atom
   partner x' of x.
 - THEOREM A (incidence-Hall, local max-cut): every bad-edge set injects into cut edges INCIDENT to endpoints
   (e_M(W)<=e_B(W)+d_B(W)/2). WEAKER (rep may be non-geodesic).

THE CLEAN REDUCTION (all 5 strategies CONVERGED on this):
 - LOSSLESS CAUCHY-SCHWARZ: |E_short(S)|>=T^2/Q, so target <== m*Q<=T^2  (Q=Sum_c d(c)^2, T=Sum_e|P_e|=Sum_c d(c),
   d(c)=#atoms through c). Per-atom SUFFICIENT lemma L2: g(e)=Sum_{c in P_e} d(c) <= (T/m)|P_e|  ==> m*Q<=T^2 (sum).
 - NECESSITY OF STRUCTURE: m*Q<=T^2 is FALSE for abstract set systems -- a 14-atom unit-geodesic SUNFLOWER through one
   edge gives R=16/17<1. So girth+max-cut ESSENTIAL; the crux = SUNFLOWER-FREENESS (max-cut+girth forbid many
   small-|P_e| atoms through one cut edge).
 - CLAUDE EXACT VERIFICATION (_claude_mQ_leq_T2_gate.py): 0 failures of m*Q<=T^2 on census N<=11 subset-checks;
   min T^2/(mQ) = 16/7 = 2.2857; max L2 ratio = 7/16 = 0.4375. EXACTLY reproduces the workflow's 16/7 and 7/16.
   VALIDATED with 2.29x slack.

THE IRREDUCIBLE OPEN CORE (converged by ALL 5 strategies + GPT-Pro + my cut-cover falsifier):
 prove m*Q<=T^2 / L2 / sunflower-freeness from girth-4+max-cut. Obstruction: a minimal violator needs a single-flip
 cut-cover certificate = one side of a 2-colouring of the ATOM-GRAPH on endpoints W; but that triangle-free atom-graph
 can contain ODD CYCLES, so no single-flip certificate exists (INDEPENDENTLY RE-DERIVES my cut-cover falsification).
 Needs a global augmenting-path/switch argument -- the same "switch existence" node. Door-only strengthening FALSE
 (C_18, inner geodesic edges needed); local per-edge congestion FALSE (C5[t]); spectral fails (corridor sigma_2/sigma_1
 ->1 is forbidden by girth for NON-spectral reasons).

NET: gap#1 open core is now (a) PROVEN for |S|<=8, (b) reduced to the clean scalar inequality m*Q<=T^2 (verified 2.29x
slack) with crisp per-atom sufficient lemma L2 (7/16), (c) obstruction pinpointed = sunflower-freeness = the global
switch (odd cycles in atom-graph). Triple cross-confirmation of the switch core. P(gap#1 math) ~47-48 (de-risked: clean
scalar target + |S|<=8 proven, but the switch core persists). Files: _claude_mQ_leq_T2_gate.py, _claude_ell5_overlap_gate.py.

================================================================================
## GPT-Pro REPLY 24 (2026-07-08) — P4SharedSupportDichotomy (relayed by user)
================================================================================
GPT-Pro CONFIRMS the multi-geodesic concern: proof must be on the FULL shortest-support hypergraph E_e = union of ALL
length-4 geodesics of e (NOT one chosen P4). Correct no-private-edge lemma (Lean-ready):
  minimal_hall_obstruction_full_support_shared: minimal obstruction S has |S|=|E_short(S)|+1 and for every e in S,
  E_e subset E_short(S \ {e}) (every cut edge on ANY shortest geodesic of e is on some geodesic of another row).

4-TYPE LOCAL CLASSIFICATION of a sharing witness (e,f,P,Q,c0), P,Q length-4 geodesics sharing cut edge c0:
  I  C5BookParallel: POSITION-COMPATIBLE -- exists layer map lambda:V->{0..4}, common vertices/edges at SAME index,
     NO order inversion (no p_i=q_j, p_k=q_l with i<k but j>l). The layered C5-blow-up pattern.
  II S1ThetaPattern: order inversion OR shared edge at DIFFERENT positions => reduced first-split/last-rejoin theta
     (two internally-disjoint B-arms between split s and rejoin r, alternating bad-endpoint attachment). THE HARD branch.
  III ReducibleSubcagePattern: exposes a prunable proper subcage D (B[D],B[C\D] connected, Balance(D)>=0 by base-leaf/
     absorption/certified-descendant). Certificate-based.
  IV ForbiddenShortcutPattern: contains a triangle OR a B-walk of length<=2 between an atom's endpoints (=> triangle).
     Killed by triangle-free + ell=true-shortest.
Classification theorem P4SharedSupport_classification (I or II or III or IV) -- FINITE, gate-able by enumerating all
equality/order patterns among p0..p4,q0..q4. NOTE: I vs II is essentially a DICHOTOMY on position-compatibility; the
CONTENT is Type-II elimination.

GLOBAL PROOF SHAPE (sec 10): minimal obstruction => every support edge shared => classify each witness => IV contradicts
triangle-free, III contradicts reducedness/minimality, II eliminated by local theta theorem => ALL Type I C5-book =>
C5BookSupportExpansion (|S|<=|E_short(S)|) => contradiction.

IRREDUCIBLE HARDEST (GPT-Pro sec 11-12): (c) Type-II theta recut = S1ThetaPattern_eliminates (S1Theta => Reducible OR
Forbidden OR zero-slack connected Gamma-decreasing local recut => False). "Partly re-imports the old switch primitive
but in a MUCH SMALLER form (two ell=5 P4 rows, one finite first-split theta) -- likely finite/tractable, NOT the full
G4 global metric-stability." Ranking: hardest=S1ThetaPattern_eliminates, middle=classification exhaustiveness (gateable),
easiest=C5BookSupportExpansion (layered Hall). Final packaged primitive P4SharedSupportDichotomy (Type-II eliminated
internally). No named theorem covers it -- project-specific finite local classification.

CLAUDE ASSESSMENT + CONVERGENCE WITH THE PROOF-ATTACK WORKFLOW:
- GPT-Pro's route (min-obstruction -> P4 classification -> C5-book) and my workflow's route (min-obstruction -> Cauchy-
  Schwarz -> scalar m*Q<=T^2 / sunflower-freeness) BOTH start from the minimal obstruction and BOTH bottom out at the
  SAME core: GPT-Pro's Type-II theta = my workflow's odd-cycle-in-atom-graph / sunflower (single-flip certificate absent).
- SYNTHESIS: m*Q<=T^2 holds BECAUSE real supports are Type-I C5-book-parallel (which satisfy C5BookSupportExpansion);
  only Type-II (order inversion) could create a sunflower/violation, and Type-II is Gamma-min-forbidden (theta recut).
- The two routes are COMPLEMENTARY: workflow = analytic scalar form (cleaner to verify, per-atom L2 7/16, 2.29x slack);
  GPT-Pro = structural geometric form (finite classification, gate-able). Type-II elimination = the shared irreducible core.
- DECISIVE CHECKABLE: do Type-II (order-inverted) P4-sharing witnesses OCCUR in real triangle-free Gamma-min max cuts?
  If (near-)NONE => classification collapses to Type-I + Type-IV, expansion follows from C5BookSupportExpansion (easiest)
  => route essentially closes empirically. If Type-II occur => must verify they are reducible/recut. Gate: _claude_p4_typeI_typeII_gate.py.
P(gap#1 math) ~47-48 (two convergent routes, irreducible = Type-II theta / sunflower-freeness = the same switch node).

================================================================================
## GPT-Pro REPLY 25 (2026-07-08) — COMPLETE ell=5 PROOF PLAN; open core = S1ThetaPattern_eliminates ALONE
================================================================================
CORRECTION (important): m*Q<=T^2 is NOT lossless for Hall. Cauchy gives |E_short(S)|>=T^2/Q, so m*Q<=T^2 is SUFFICIENT
for Hall but NOT NECESSARY (the sunflower violates m*Q<=T^2 yet satisfies Hall via many private edges). So m*Q<=T^2 is a
STRONGER anti-sunflower statement than Hall needs -- do NOT make it the final theorem. [Claude: my Lean lemma
card_support_ge_of_mQ_le_Tsq captures exactly the SUFFICIENT direction m*Q<=T^2 => Hall, which is correct/honest; the
"lossless" label from the workflow was imprecise -- it is a sufficient (stronger) route, not an equivalence.]

FASTEST RIGOROUS ROUTE (GPT-Pro): minimal Hall obstruction + P4 sharing classification (NOT Cauchy/L2/spectral).
COMPLETE PROOF PLAN for Ell5SupportExpansion (sec 8):
  1. minimal_hall_obstruction (full-support no-private-edge): |S|=|E_short(S)|+1, E_e subset E_short(S\{e}) for all e.
     [= a 2-core of the full P4 support hypergraph.]  *** CLAUDE FORMALIZED: Ell5CSReduction.minimal_hall_obstruction_no_private_edge (axiom-clean). ***
  2. For each e, each geodesic P in Rows4(e), each edge c in P: pick sharing witness (f,Q); apply P4SharedSupport_classification (4 types, FINITE/gateable).
  3. ForbiddenShortcut witness => contradiction (triangle-free).
  4. Reducible witness => contradiction (reducedness).
  5. S1Theta witness => contradiction by S1ThetaPattern_eliminates.   *** THE ONLY GENUINELY OPEN LEMMA (= Type-II theta = the switch). ***
  6. => every witness C5BookParallel => supports layer-compatible => decompose into C5BookBlocks.
  7. C5BookSupportExpansion blockwise => |S| <= |E_short(S)|, contradiction.

C5BookSupportExpansion PROOF (GPT-Pro, sec 5, CLEAN + rigorous): for a C5-book with rows oriented L0->L4, take U = the
L0-endpoint set A. Every row crosses U => |S| <= |delta_M(U)|. MAX-CUT vertex inequality => |delta_M(U)| <= |delta_B(U)|
[= Claude's proven CAPACITY lemma]. Book boundary closure => delta_B(U) subset E_short(S). Chain => |S| <= |E_short(S)|.
"C5BookSupportExpansion is NOT the hard part. The hard part is proving every minimal obstruction reduces to closed C5
books" (= step 5, S1ThetaPattern_eliminates). CLAUDE FORMALIZED the abstract chain: Ell5CSReduction.c5book_support_expansion.

NET HONEST STATE: Ell5SupportExpansion reduces to ONE open lemma S1ThetaPattern_eliminates (Type-II theta recut/reducible/
forbidden trichotomy for two ell=5 P4 rows with an order-inversion sharing). Everything else is PROVABLE/FORMALIZED:
minimal-obstruction (compiled), C5-book (compiled abstract + max-cut inequality), classification (finite/gateable),
Forbidden/Reducible (triangle-free/reduced). Type-II abundant (~45% census) so S1ThetaPattern_eliminates is NON-vacuous
= the genuine switch core, TRIPLE-confirmed. P(gap#1 math) ~48 (open core = ONE finite-ish local theta lemma; the whole
scaffold is provable). Tomorrow GPT-5.6/Fable-5: prove S1ThetaPattern_eliminates.

================================================================================
## GPT-Pro REPLY 26 (2026-07-08) — S1ThetaPattern_eliminates is FALSE; residual = BalancedNeutralTheta_book_or_reducible
================================================================================
IMPORTANT CORRECTION (GPT-Pro, honest): S1ThetaPattern_eliminates (Type-II theta => Gamma-DECREASING recut) is FALSE for
the balanced ell=5 case. For two OLD rows both length 5, a clean zero-slack pair-door recut kills two 5-rows and births
two bad edges of length >=5; if born ell=5, the local square contribution is NEUTRAL: 5^2+5^2 -> 5^2+5^2, DeltaGamma=0.
[CLAUDE VERIFIED arithmetically: the earlier Gamma-DECREASE -(4L+4) was for UNEQUAL {L,L+2} rows -> [L,L]; two EQUAL
ell=5 rows -> two ell=5 = neutral. So Gamma-minimality alone CANNOT eliminate the balanced neutral ell=5 theta.]

CORRECTED local theorem S1ThetaPattern_outcome: a non-book P4 sharing yields ONE of:
  - max-cut-forbidden switch (delta_M > delta_B), OR ForbiddenShortcut (triangle/shorter-row), OR ReducibleSubcage,
    OR it is actually C5BookParallel.
The HARD RESIDUAL = the BALANCED NEUTRAL THETA. Exact isolated pattern **BalancedNeutralAlternatingP4Theta**:
  (1) shore W with delta_B(W)=2, delta_M(W)=2; (2) the two born B-doors after switching also have ell=5; (3) no
  triangle / no shorter B-walk; (4) the switch is Gamma-NEUTRAL (Gamma(B^W)=Gamma(B) locally); (5) NOT position-
  compatible under the naive layer test. "Not killed by Gamma-minimality."

SOLE OPEN LEMMA (sharper than before): **BalancedNeutralTheta_book_or_reducible** -- the balanced neutral alternating
ell=5 P4 theta is either C5-book-parallel (secretly position-compatible under a subtler layer map) or REDUCIBLE
(prunable proper subcage). If it is NEITHER, it is the TRUE LOCAL OBSTRUCTION (the wall). GPT-Pro did NOT resolve this.

WHOLE-PROOF STATUS: minimal obstruction => no-private-edge => classify witnesses => Forbidden/Reducible contradict;
non-book => BalancedNeutralTheta_book_or_reducible (OPEN) => all C5-book => C5BookSupportExpansion (PROVEN, GPT-Pro
sec 10: |S|<=|delta_M(A)|<=|delta_B(A)| subset E_short(S)) => contradiction. So gap#1 = BalancedNeutralTheta_book_or_reducible ALONE.

CLAUDE ASSESSMENT: this is a real, honest development -- the Gamma-decrease elimination FAILED for the balanced case
(the route is MORE DELICATE than reply 25 implied); the fallback (book-or-reducible) is a finite local question but
UNRESOLVED. Connects to my Type-I/II gate: Type-II (non-position-compatible) witnesses are ABUNDANT (~45% census) yet
Hall holds -- GPT-Pro's claim is that those are all book-or-reducible; my naive layer test flags them non-book, so they
must be REDUCIBLE (needs the cage/pruning machinery to verify) OR book under a subtler map. DECISIVE OPEN GATE: do
balanced-neutral-theta witnesses that are NEITHER book NOR reducible exist in real reduced Gamma-min max cuts? (needs
reducibility/prunable-subcage checker). P(gap#1 math) ~45 (down slightly: hard lemma corrected, route more delicate,
open core = a specific finite pattern whose book-or-reducibility is unproven). Tomorrow GPT-5.6/Fable-5: resolve
BalancedNeutralTheta_book_or_reducible.

================================================================================
## GPT-Pro REPLY 27 (2026-07-08) — THE WALL, DEFINITIVELY ISOLATED: the IMPURE BALANCED NEUTRAL LENS
================================================================================
GPT-Pro HONEST: "I do not have a complete proof of BalancedNeutralTheta -> C5BookParallel OR ReducibleSubcage for all
ambient rowDB configurations. What can be proved cleanly is the PURE neutral lens case. The remaining irreducible
pattern is an IMPURE BALANCED NEUTRAL LENS: the two-row theta is neutral, not book-compatible, but every natural lens
contains additional owned atoms so the obvious subcage is not immediately nonnegative. THAT IS THE EXACT LOCAL WALL."

Three angles attempted:
 (A) NEUTRAL-RECUT MONOVARIANT BookDefect(S) = #non-position-compatible sharing witnesses. A neutral recut is a local
     2-switch that OFTEN turns an order-inverted P4 pair into layer-compatible => reduces BookDefect in the PURE two-row
     lens. But GLOBALLY it can INCREASE elsewhere; "plausible but NOT proven -- it can CYCLE unless a real monovariant
     Phi is found. I do not currently know that theorem."
 (B) DIRECT REDUCIBILITY: the balanced neutral theta certificate = doors d0,d1; lens component W of B\{d0,d1} with
     delta_B(W)={d0,d1}, delta_M(W)={e,f}, ell_B(e)=ell_B(f)=5, born ell_{B^W}(d0)=ell_{B^W}(d1)=5, B[W]+B[parent\W]
     connected => |B^W|-|B| = |delta_M(W)|-|delta_B(W)| = 0 (NEUTRAL, no Gamma-min contradiction). The PURE lens
     (OwnedPositiveSurplus(W)=0) IS reducible/provable. The IMPURE lens (extra owned atoms in W) = WALL.
 (C) reducedness-forbids: not resolved.

SOLE OPEN LEMMA (Lean sig, GPT-Pro sec 7): BalancedNeutralTheta_book_or_reducible (rowDB C e f P Q ... hReduced:
ReducedShell, hMin: MinimalNegBalance, hGammaMin) : C5BookParallel \/ ReducibleSubcagePattern. "If true =>
BalancedNeutralTheta -> book OR reducible. If FALSE => it gives the EXACT COUNTER-PATTERN to Ell5SupportExpansion."
Consumed by P4SharedSupportDichotomy (Type-II eliminated internally by this lemma).

*** CLAUDE DECISIVE META-OBSERVATION: the impure balanced neutral lens lives inside a HYPOTHETICAL deficient
(MinimalNegBalance = negative-reserve) cage. But NO deficient cage exists in a real graph (the conjecture holds:
Gamma<=N^2 everywhere). So -- exactly like the earlier switch premise and the ViolatesShortestGeodesicHall premise --
the impure balanced neutral lens is a COUNTERFACTUAL object: it cannot be exhibited or tested on any real
triangle-free Gamma-min max cut (they have no deficient cages). Its book-or-reducibility must be proven DEDUCTIVELY in
the hypothetical deficient-cage world, NOT empirically gated. This is why every empirical battery shows Hall feasible
everywhere and no gate can reach the binding case. ***

DEFINITIVE END-STATE of today's gap#1 investigation: the entire crux is isolated to ONE counterfactual local pattern
-- the impure balanced neutral ell=5 lens in a reduced minimal-neg-balance shell -- whose reducibility (existence of a
nonneg prunable subcage despite the extra owned atoms) is the sole open question. GPT-Pro cannot close it; it is a
genuine research theorem. NOT gate-able (counterfactual). P(gap#1 math) ~45. Tomorrow GPT-5.6/Fable-5: prove (or refute)
BalancedNeutralTheta_book_or_reducible for the impure lens. LEAN: 8 axiom-clean scaffolding thms compiled
(Ell5CSReduction.lean); the open lemma + max-cut vertex inequality + graph-fact wiring remain.

================================================================================
## ARXIV SCAN (2026-07-08, user-requested: new papers to break gap#1) — FRONTIER + STRATEGIC INSIGHT
================================================================================
STATE OF THE ART on Erdos n^2/25 (every triangle-free G bipartite-izable by <= n^2/25 edge deletions; sharp at C5[N/5]):
- Balogh-Clemen-Lidicky (arXiv 2103.14179, 2021, "Max Cuts in Triangle-free Graphs"): flag-algebra/DENSITY approach.
  PROVEN for edge-density <= 0.2486 OR >= 0.3197; general bound n^2/23.5 (was n^2/18). MEDIUM-DENSITY BAND
  [0.2486, 0.3197] is OPEN -- the frontier of the density method.
- OUR paper (arXiv 2606.28041, 2026, per-root-MaxCut envelope + blow-up integrality): a(5n)=n^2 for n<=40 (N<=200), EXACT.
- Related/adjacent: "The Spectrum of Triangle-free Graphs" (2204.00093, signless-Laplacian q_n <= 15n/94 via
  ratio of induced P3 to P4 paths -- a NEW spectral technique, different quantity); "10 Problems for Partitions of
  Triangle-free Graphs" (2203.15764); "Balanced bipartite distance of K4-free graphs" (2605.05346, 2026);
  "Dense halves in K4-free" (2412.13485). NO 2025-2026 paper with a technique that directly resolves our
  impure-balanced-neutral-lens / geodesic-support-Hall crux -- the field is slow, two orthogonal approaches (BCL density
  + our exact charging) are the only substantial ones.

STRATEGIC INSIGHT (not a new paper, but combining existing results) -- COULD narrow gap#1:
- BCL already proved the conjecture OUTSIDE density [0.2486, 0.3197]. So a full delta=0 proof only needs the MEDIUM band.
- Our gap#1 route (GERSH -> geodesic-Hall -> impure balanced neutral lens) is UNIFORM over ALL triangle-free Gamma-min
  max cuts. If RESTRICTED to medium density, the TIGHT extremal C5[t] (density -> 2/5 = 0.4, in BCL's PROVEN high range)
  is ABSENT, so surplus is strictly sub-extremal (< n^2/25) with genuine SLACK. The impure lens is a DEFICIENT-CAGE
  (negative-reserve, TIGHT) phenomenon; away from the extremal it may be provably ABSENT => the lens/wall could vanish
  in the medium band. CANDIDATE: prove BalancedNeutralTheta_book_or_reducible ONLY for medium-density (or show deficient
  cages need density -> 0.4), then invoke BCL outside. CAVEAT: project task history (#10-12: BCL-window, order-9
  cut-deficit localizer, "close order-9 MEDIUM band eta=+4.3e-5") shows we ALREADY hit a wall in the medium band via
  flag algebras -- the medium band is genuinely hard for BOTH approaches, so this is not a free win, but re-plumbing our
  charging route to only fire in the medium band (with the BCL slack) is a fresh angle worth GPT-5.6/Fable-5.
- SECOND ANGLE: the signless-Laplacian / induced-P3:P4-ratio spectral method (2204.00093) is adjacent to our geodesic-
  support structure (P4 = the ell=5 geodesic; P3 = a sub-path); a spectral/ratio bound on the support hypergraph could
  be an alternative to the combinatorial lens. Worth exploring tomorrow.
VERDICT: no off-the-shelf new paper breaks the wall; the two fresh cross-pollination angles (medium-band restriction via
BCL; induced-path-ratio spectral) are the takeaways for tomorrow's escalation.

--- DENSITY-HARDNESS GATE RESULT (_claude_density_hardness_gate.py, census N<=10; N=11 confirming) ---
Tightness t = beta/(N^2/25) = 25 beta/N^2 (conjecture <=> t<=1; extremal t=1), bucketed by BCL density bands:
  LOW    (d<=0.2486): max t = 0.500, ZERO near-tight (t>=0.9).
  MEDIUM (0.2486..0.3197): max t = 0.617, ZERO near-tight. [multi-atom L*=10 occurs here but at t=0.617 = SLACK]
  HIGH   (d>=0.3197): max t = 1.000 (the C5[t]-like TIGHT extremals), near-tight graphs ALL here.
C5[t] extremal density = 2/5 -> 0.4 (and C5[1]=0.5, C5[2]=0.44), ALWAYS high band.

=> STRATEGIC REFRAME (KEY takeaway for tomorrow, from the arXiv scan + this gate):
The gap#1 WALL -- the impure balanced neutral lens -- lives in a DEFICIENT cage (t>1, near-tight). Near-tightness is
a HIGH-DENSITY phenomenon (census: t=1 only at density>=0.44). BCL already PROVED the conjecture for density>=0.3197.
So a hypothetical counterexample (t>1) CANNOT be high-density (BCL) NOR low-density (BCL) => it must be MEDIUM-density.
But medium-density triangle-free graphs are FAR FROM TIGHT (census t<=0.617, big slack). So the deficient cage / impure
lens should be ABSENT in the medium band. => DON'T prove the counterfactual impure-lens lemma (hard); instead prove
t<=1 for MEDIUM density DIRECTLY (where there's slack) and invoke BCL for density outside [0.2486,0.3197]. This BYPASSES
the gap#1 lens entirely. The medium band is the genuinely open region (BCL + our old flag-algebra attempt both stuck
there), but our GERSH charging route restricted to medium density -- with the BCL slack and no near-tightness -- never
meets the deficient cage. CANDIDATE tomorrow: re-plumb GERSH to fire only in [0.2486,0.3197]; show deficient cages force
density>=0.3197 (=> BCL); OR a direct medium-band charging bound with the observed slack.
CAVEAT: census N<=11 is small (density coarse); the medium-band slack is empirical, not a proof -- but the CORRELATION
(tightness = high-density) is robust and consistent across N=5..10 and matches C5[t] being high-density.

--- N=11 CONFIRMATION (102405 census graphs): MEDIUM band max t=0.620 (0 near-tight), HIGH band max t=1.000 (near-tight only). VERDICT printed: STRATEGIC ANGLE SUPPORTED. Medium-band restriction is the top wall-breaking candidate. ---

--- MEDIUM-BAND ARITHMETIC SHARPENING (2026-07-08): deficient ell=5 cage => Gamma=25m>n^2 => m=#bad-edges>n^2/25 (C5[t] is EXACTLY n^2/25, reserve 0). Max-cut |cut|>=e/2 => m=beta<=e/2 => e>2n^2/25 => d>4/25=0.16 (TRIVIAL). Need to push d>=0.3197 (BCL high band) using TRIANGLE-FREE structure (girth>=4 forces more cut edges per bad edge / limits bad-edge packing). Empirically deficient/tight = d>=0.44. The GAP 0.16->0.3197 is the exact target: prove "triangle-free deficient cage => d(G)>=0.3197" => BCL closes medium band, impure lens BYPASSED. Sent to GPT-Pro reply 29. ---

================================================================================
## GPT-Pro REPLY 29 (2026-07-08) — MEDIUM-BAND BYPASS DOES NOT WORK (honest retraction)
================================================================================
CLAUDE proposed (from arXiv scan): a counterexample must be medium-density (BCL covers the tails); if a DEFICIENT cage
(impure-lens host) forces high density, BCL closes it => lens BYPASSED. GPT-Pro RIGOROUS VERDICT: THE BYPASS DOES NOT
WORK. Two independent failures:
 1. DEFICIENCY = LENGTH-SQUARE density, NOT edge-density. Deficient cage: Gamma_C = sum ell^2 > n_C^2. For ell=5,
    |M_C| > n_C^2/25 (dense in bad edges), but that is NOT edge-density. COUNTEREXAMPLE: one long odd cycle (1 bad edge,
    ell=n) has Gamma=n^2 (tight) with only O(n) edges. Long atoms make sum ell^2 large using O(n_C) edges. So
    "deficient => d >= 0.3197" is FALSE from current facts. (My trivial arithmetic d>0.16 is all that holds; the gap
    0.16->0.3197 CANNOT be closed by deficiency alone.)
 2. LOCAL-to-GLOBAL: even a proven local lemma e(C) >= 0.3197*binom(|C|,2) would NOT place the whole graph G in BCL's
    GLOBAL high-density tail (a locally-dense substructure can sit inside a globally-medium graph).
KEY STRUCTURAL POINT: for C5-BOOK cages, |B_C| = 4|M_C| => local density ~0.4 (dense). BUT "the impure balanced neutral
lens is precisely the NON-BOOK case where this clean relation is NOT automatic." So the lens configurations are exactly
the ones that EVADE density-forcing -- the density observation fails precisely where the wall is.
REQUIRED (both as hard as the original, unproved global-aggregation statements):
  deficientCage_forces_global_high_density  OR  mediumDensity_no_deficient_cage (= "medium-density version of the conjecture itself").
BOTTOM LINE: the BCL density band is useful CONTEXT but does NOT bypass the impure lens. The bypass RELOCATES the
difficulty to an equally-hard global aggregation statement. MEDIUM-BAND ANGLE = DEAD END for gap#1 (a genuine reframe
worth checking -- falsifier-first -- but it does not provide an easier route). The impure balanced neutral lens
(BalancedNeutralTheta_book_or_reducible) REMAINS the crux for GPT-5.6/Fable-5. Residual value: confirmed the difficulty
is genuine + the lens = exactly the non-book (density-non-forcing) case. P(gap#1 math) ~45 (unchanged).
