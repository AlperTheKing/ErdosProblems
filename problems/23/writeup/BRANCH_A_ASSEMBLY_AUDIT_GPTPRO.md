# Branch-A / GERSH_{L=5} FINAL CONDITIONAL ASSEMBLY AUDIT (GPT-Pro, 2026-07-03)

Target: GERSH_{L=5}: ROWSUM(Q) <= N + eta. Chain: A1 + ODL => C5-RS => net-DW' =>
GERSH_{L=5} (PROVEN conditional).

## Tree (status per node)
1. C5-RS layer: 1.1 statement PROVEN from 1.2-1.5; 1.2 P=empty PROVEN; 1.3 P proper:
   X(P) <= (25/N+2/3)etabar via A1, 2/3<=1 => beta_P <= 1 comes FROM A1 (no separate
   dichotomy) — CERT-PENDING through A1; 1.4 P=Z5 needs ODL.
2. A1: 2.1 statement CERT-PENDING; 2.2 six-cone reduction PROVEN (dihedral); 2.3 six
   ConeCerts CERT-PENDING (failure = local PMTS cone repair); 2.4 four-mask 7/30
   CERT-PENDING (absorption works for any beta_4 <= 3/10 — slack 7/30 -> 3/10).
3. ODL full-mask tree: 3.1-3.5 overfull closure + Type A/B disposal PROVEN;
   3.6 interior non-passive classification PROVEN conditional on G1;
   3.7 door-count split (q=3 seed / q>=4 A1-5mask) PROVEN as bookkeeping conditional on
   Seed3; **3.8 q<3 EXCLUSION: PENDING (structural)**.
4. Seeds: 4.2.2 EQ CERT-1 PROVEN; 4.2.3 EQ CERT-2 CERT-PENDING (LP-1 + product/SOS
   fallback; failure = local cone repair); 4.2.4 EQ passive AM CERT-PENDING (3 layer
   master cubes x 11 EQ row templates, fallback 27 sigs x 11 rows); 4.2.7 V1/V3 cubes
   CERT-PENDING; 4.3.1 SIB S7 = 36 gates CERT-PENDING; 4.3.2 SIB AM (3 cubes x 13 rows,
   fallback 27x13) CERT-PENDING.
5. 4-door: 5.2 A1-5mask PROVEN conditional on 5.3 five 4-mask certs (=M4 cone);
   5.4 + N>=10 PROVEN.
6. AM passive: 6.1 reduction PROVEN; 6.2 27 signatures = 3 layers x (2^2-1)^2 PROVEN;
   6.3 master-cube uniformity PROVEN as reduction, certs pending.
7. Non-passive: 7.1-7.2 Type A/B PROVEN; 7.3 Type C (non-C5-hom) PENDING through G1;
   7.4 Type D PROVEN conditional on G1.
8. **8.1 G1 non-C5-hom non-overfull lemma: PENDING (structural)** — if active closure
   is not C5-hom then I(Q) <= N. Failure = branch redesign (Groetzsch-type components).

## 10. CERTIFICATE-PENDING ledger (the complete remaining list)
10.1 A1 six ConeCerts (PMTSCone) — failure local.
10.2/5.3 five 4-mask 7/30 ConeCerts — failure local (slack to 3/10).
**10.3 G1: overfull rows are C5-hom (equiv: non-C5-hom => not overfull) — STRUCTURAL;
     failure = new ODL branch.**
**10.4 q<3 exclusion: saturated overfull core has >=3 effective doors — STRUCTURAL;
     failure = 1/2-door branch.**
**10.5 Seed3: saturated 3-door overfull cores reduce to EQ or SIB — STRUCTURAL;
     failure = third seed family.**
10.6 EQ-CERT2 LP (seed-vanishing; product/SOS fallback) — failure local.
10.7 EQ-AM master Bernstein (3 cubes x 11 rows; fallback 27x11) — failure local.
10.8 SIB-S7 36-gate family — failure local.
10.9 SIB-AM master Bernstein (3 cubes x 13 rows; fallback 27x13) — failure local.

## 11. Proven ledger
C5-RS reduction, beta_P<=1-from-A1, uniform width N/5, C5-RS=>net-DW', net-DW'=>GERSH_{L=5},
door bookkeeping, 4-door N>=10, A1-5mask arithmetic, EQ height, EQ CERT-1, AM reduction,
master-cube formulation (+vertex refutation), Type A/B/D classification (cond. G1).

## ASSESSMENT (Claude)
Only 10.3/10.4/10.5 are STRUCTURAL (graph lemmas, branch-level risk if false); everything
else is polynomial-certificate work with local-repair failure modes. NEXT: (a) census
validation gates for G1/q<3/Seed3 (Codex — closure/saturation infra), (b) GPT-Pro proofs
for the three structural lemmas, G1 first.

## ADDENDUM (user-relayed authoritative text, 2026-07-03)
- Seed3 (4.1) EXPLICIT: saturated overfull C5-hom 3-door cores true-twin-contract to
  exactly EQ = I?BD@g]Qo or SIB = I?`FAo]]? (graph6; second may need backtick-escape
  check vs original). No third family = the pending claim.
- 1.5 net-DW' identity: 5 tau = N - 25 eta/N; sum_i max(s_i, m/w_i) = N - 25 eta/N +
  sum_i (s_i - tau)_+ <= N + eta. (Uniform width w_i = N/5, w_i w_{i+1} = N^2/25 >= m.)
- 4.2.5 tau_0: V2-attachment, L={3,5}, R={4,6}, true twin of bag 8; zero multipliers,
  coefficient-positive identities across 11 EQ rows. Status: proven-as-template,
  literal-list verification = the pending piece (Codex tau_0 PASS covers it; RawPoly
  re-emit pending).
- 4.2.6 V2 master cube pair variables: mu_34, mu_36, mu_54, mu_56 in [0,1]; covers 9
  V2-layer signatures x 11 row templates.
- 6.4 vertex-check refutation reason: row denominators depend on the signature (defect
  not affine/concave) => Bernstein or per-signature.
- 6.5 DEPENDENCY SEPARATION (PROVEN): AM M-certs feed ONLY passive-attachment
  monotonicity in EQ/SIB 3-door branches; NOT A1, NOT 4-door absorption, NOT CERT-1/2,
  NOT SIB-S7, NOT Branch B.
- 9.1 conditional theorem assumption list (verbatim ten): A1 six ConeCerts; five 4-mask
  7/30 ConeCerts; G1; DoorSat + non-passive classification; q<3 exclusion; Seed3;
  EQ-CERT2; EQ-AM M-certs; SIB-S7; SIB-AM M-certs.

## G1 REFUTED AS STATED -> G1' (pruned-core form) (GPT-Pro reply, 2026-07-03)
COUNTEREXAMPLE FAMILY (vertex one-sum): G_h = E_h (+)_t H where E_h = pure EQ h-blowup
(N_E = 10h, I_E(Q) = 32h/3, I-N = 2h/3) and H = Groetzsch-type non-C5-hom all-l5
B-connected gamma-min-maxcut component, glued at a bad-door endpoint t in H identified
with a row vertex q of Q. One-sum preserves: triangle-freeness; all-l5 (shortest paths
are simple, cannot pass the articulation vertex twice); maxcut + gamma additivity (no
cross edges; match sides at t via component complementation); B-connectedness. Terminal-
prefix closure from t pulls H into the active closure => closure NOT C5-hom, yet
I(Q) - N = 2h/3 - (n_H - 1 - s_H(t)) > 0 for large h. G1-as-stated FALSE.
PRUNING LEMMA (verified algebra): W = U (+)_t H, Q in U, s_H(t) <= |H| - 1 ==>
I_W(Q) - |W| <= I_U(Q) - |U|  [I_W = I_U + s_H(t), |W| = |U| + |H| - 1].
G1' (corrected statement): among closed overfull supports W containing Q choose one
MINIMAL with I_W(Q) > |W|; then W is C5-hom. Counterexample complies (appendage prunable).
CORRECTED ROUTE (step 3 = REMAINING OPEN PROOF): (1) minimal closed overfull support W;
(2) W has no prunable appendage; (3) any non-C5-hom all-l5 obstruction creates a prunable
appendage (s_H(t) <= |H|-1) OR a max-cut/Gamma-descent; (4) W C5-hom.
CASCADE: q<3 and Seed3 RESTATE on the pruned irreducible saturated core W (unpruned forms
vulnerable to tree-like appendages). Census gates must build PRUNED cores.
CIRCULARITY WATCH: step (3)'s s_H(t) <= |H|-1 must NOT be derived from GERSH/C5-RS
itself (it resembles a localized GERSH); needs an independent argument.

## G1' STEP 3 RESOLUTION (GPT-Pro reply 3, user-relayed authoritative, 2026-07-03)
VERDICT: step 3 NOT provable from switch calculus alone — pure descent claim FALSE
(Groetzsch/Mycielski blocks: tri-free, odd-girth 5, all-l5 under gamma-min cuts, no
C5-hom, NO automatic cut-improving flip or neutral Gamma-decreasing switch).
3a ARTICULATION PRUNING (PROVEN, one-line identity): W = U cup H, U cap H = {t}, Q in U,
s_H(t) <= |H|-1 ==> I_W(Q)-|W| <= I_U(Q)-|U|.
3a' MULTI-TERMINAL PRUNING (PROVEN): T = U cap H, s_H(Q cap T) <= |H|-|T| ==> same.
[Both verified by inspection: I_W-I_U = s_H(load), |W|-|U| = |H|-|T|.]
3b NCH-def (NEW THEOREM, the single remaining structural core): a closed all-l5 active
sub-support H attached through terminal set T, non-C5-hom, with NO completed-switch
descent (no negative cut slack, no negative neutral Gamma-slack) satisfies
  s_H(Q cap T) <= |H| - |T|   (NCH-def)
=> prunable by 3a'. NOT circular (local deficit statement, not C5-RS/ODL/GERSH).
NCH-cert (machine form): |H|-|T|-s_H(Q cap T) = Sigma alpha_S sigma(S) +
Sigma beta_S nu_K(S) + Sigma gamma_K delta_H(K) + R_H, all coefficients >= 0
(S = completed connected terminal-shadow switches internal to H; delta_H(K) = row-deleted
blue-component deficits; R_H = tri-free/noncrossing/twin residuals).
G1' THEOREM (PROVEN conditional on NCH-def): minimal closed overfull support W is C5-hom.
Proof: minimal non-C5-hom sub-support H; Case 1 (descent switch in H) contradicts
max-cut/gamma-min (H closed => switch valid in W); Case 2 (no descent) NCH-def + 3a'
prune contradicts minimality of W.
REMAINING OBSTRUCTION SHAPE (*): closed, all-l5, non-C5-hom, no maxcut-improving switch,
no Gamma-decreasing neutral switch, attached through T, TERMINAL-OVERLOADED
s_H(Q cap T) > |H|-|T|. Codex gates exactly this; absence => NCH-cert family exists.
SANITY-FIRST: compute s_H(Q cap T) vs |H|-|T| for concrete Groetzsch attachments — if
the model obstruction itself is terminal-overloaded, NCH-def is FALSE and needs repair.
STRUCTURAL LEDGER NOW: G1' <= NCH-def (open) + pruning (proven); q<3' + Seed3' (open,
on pruned cores); everything else local certificates.

## NCH-def -> TERMINAL-HALL REDUCTION (GPT-Pro reply 4, 2026-07-03)
PROVEN & SAFE: Terminal-Hall => NCH-def => pruning. TH(H,T,Q): for all U subset H\T,
D_T(U) <= |U| (Hall demand of rows-with-interior-in-U hitting T_Q; row interior supply
Int_T(P) = V(P)\T, terminal-hit weight a_T(P) = |V(P) cap T_Q|; s_H(T_Q) = weighted row
sum (1.1)). SHARP REMAINING THEOREM (NCH-Hall): non-C5-hom + no completed-switch descent
=> Terminal-Hall. Minimal Hall obstruction structure (3.1/3.2): no unused interior
vertex; proper subpackets tight => debt on packet boundary; full-packet deficit must be
paid by switch terms (terminal-shadow switch lemma).
CASE REDUCTIONS (Codex gates FIRST): |T|=1: rooted terminal-shadow flip; non-descent
outcome = coherent C5-labeling (extends to H — contradicts non-C5-hom); cert (5.1).
|T|=2: two-terminal corridor switch lemma; crossing shadows => switch, noncrossing =>
consistent C5-hom label propagation; cert (5.2) with CorrSlack(C) >= 0 corridor residuals.
GENUINE RESIDUAL (|T|>=3 or internally 2-connected rel T): terminal-overloaded
C5-critical block (*) — if Codex finds one, NCH-def FALSE.
IF FALSE (§7): repair = s_H <= |H|-|T|+c; caution: EQ seed has only 1/3 ODL slack, any
c>0 must be tracked downstream carefully.
GPT-Pro's own verdict: do NOT claim NCH-def until sanity-first rules out (*) on
Groetzsch attachments. NCH-cert form now with Hall slacks used INDUCTIVELY on proper
subpackets only (non-circular).

## q<3' + Seed3' -> FINITE CERTIFICATE PROGRAMS (GPT-Pro reply 5, 2026-07-03)
q<3' = 2Door-ODL: q<=2 => I(Q) <= N (strict unless eta=0 rigid blowup, excluded).
Door templates (up to C5-reversal/side-swap): D1 = {a0b0}; D2s = {a0b0, a0b1} (shared);
D2m = {a0b0, a1b1} (matching). Per template: UNIVERSAL QUOTIENT ConeCert family
(2Door-Cert): D_{D,R}(N_D(w) - I_{D,R}(w)) in Cone_D for every row template R;
Cone_D generators: shifted bags w_b = 1+x_b, prefix ineqs e(V_i,V_i+1) >= m_D,
bad-layer capacity m_D <= e(V4,V0), saturation signatures. NOT graph enumeration.
Seed3': door graphs (P4 [EQ/SIB pattern], K1,3, P2+E, 3E) x interior signatures
(<= 49 = (2^3-1)^2 per layer raw; filters F0 layer-rule / F1 doors-effective /
F2 saturation / F3 all-l5 no-shortcuts / F4 prefix ineqs shrink drastically).
Classifier outputs per enumerated quotient (each kernel-checkable): EQ-iso / SIB-iso /
NO_OVERFULL (ConeCert D_R(N - I_R) = P0 + Sigma F_j P_j) / NEG_SWITCH (sigma<0 or
sigma=0 & Gamma-descent) / PRUNABLE (s_H(Q cap T) <= |H|-|T|) / NOT_SATURATED /
FOUR_DOOR. K1,3 / P2+E / 3E excluded via these types. BOTH nodes now finite
certificate programs — Codex-executable.
STRUCTURAL LEDGER: NCH-Hall (T=1/T=2 certs + (*) hunt) is the ONLY remaining
non-certificate theorem; everything else = certificates.
## CERT-2 ALERT (Codex 11:28Z): LP-1 infeasible degrees 0-5 uniform + neg-repair 5/6;
LP-2 product fallback f4/p0, f4/p1, f5/p1 infeasible. 17578 target terms, deg 11,
4327 negative coeffs, seed check passes. Needs GPT-Pro redesign (sent).

## NCH T=1 THEOREM + (*) HUNT LIST (GPT-Pro, 2026-07-04)
T=1 THEOREM (non-circular, proof path complete): H closed, all-l5, attached at T={t},
no completed switch with negative cut slack or negative neutral gamma slack, H non-C5-hom
==> D_t(U) <= |U| for all U in H\{t}. PROOF: (1) TERMINAL rows (t an endpoint): each
counted row belongs to bad edge ta, a in U; zeta_{ta}(U) <= 1; simplicity =>
D_t^{term}(U) <= #bad-root-neighbors in U [PROVEN, 4 lines]. (2) NONTERMINAL Hall excess
must enter through blue root edges e = tu: REC capacity zeta_e(U) <= 1 needed; bad/blue
root channels disjoint (simple graph) => D_t(U) <= |U|. (3) REC violation => completed
rooted terminal shadow S_e(U) gives sigma < 0 or gamma-descent UNLESS neutral+gamma-flat.
(4) Neutral+flat => coherent C5-label propagation across closed H (triangle-free kills
triangles, all-l5 kills shorter odd cycles, gamma-min kills switches) => H C5-hom —
contradiction. Steps 3-4 = the rooted-shadow/label details (certificate-level; Codex
REC certs realize them). CALIBRATION: zeta margins 0 at Mycielski = REC tightness (one
unit of row mass per blue door) — consistent.
HUNT LIST (priorities): 7.3 WEIGHTED BLOWUPS of Myc — VERY HIGH (danger = asymmetric
weights inflating rows through T with |H\T| small; search: fix t, optimize s_H(t)-(|H|-1)
over integer weights 1..B, exhaustive B=2,3,4); 7.7 Hajos/Ore compositions of
C5-critical blocks — HIGH for T=2,3 (flow concentration at small separators);
7.2 iterated Myc M(Groetzsch), M(M(C7)) — HIGH at apex-rooted terminals;
Kneser-type — LOW-MED; random lifts — LOW.

## NCH T=2 CORRIDOR CERTIFICATE (GPT-Pro sibling, 2026-07-04)
LCM-cleared instance: rows P have integer demands beta_P > 0, doors e integer capacities
kappa_e > 0; zeta_K(U) = Sigma_{Doors(U)} kappa_e - Sigma_{Rows(U)} beta_P. Minimal T=2
obstruction: closed packet U, zeta_K(U) < 0, proper closed subpackets tight (=0), every
u in U on a positive row. TERMINAL SHADOWS: per row P and root t_r, oriented interval
I_r(P) = shortest terminal prefix from t_r-side into U; both-terminal rows have two.
CORRIDOR C: connected component of union of shadow intervals, closed under row-interval
closure + door closure; CorrSlack(C) = Sigma_{Doors(C)} kappa_e - Sigma_{Rows(C)} beta_P
(computable integer). PER-CORRIDOR CERTIFICATES (Codex emits one per corridor):
  NONNEG: CorrSlack(C) >= 0 (integer arithmetic);
  CROSS: crossing shadows I,J -> lens L -> S = Comp(L); verify delta_B(S) subset
    Doors(C) and Rows(C) subset {P : bad edge crosses S} => zeta_K(S) <= CorrSlack(C)
    < 0 contradicts max-cut;
  LABEL: emit phi : V(H(C)) -> Z5, verify edge-by-edge phi(a)-phi(b) = +-1 mod 5 =>
    C5-hom of the closed support — contradicts non-C5-hom.
Minimality distributes the global deficit to some corridor with CorrSlack < 0; a
CorrSlack<0 corridor must be CROSS or LABEL — both contradictions => (T2) holds.
HONEST RESIDUAL: OSC(a,b;t1,t2) head-on osculation — opposite-root shadows sharing a
first-exit blue edge in opposite directions (would force 2=0 mod 5, so LABEL fails
there). Local gate: produce two-sided switch S = Comp(S_a cup S_b) with zeta_K(S) <=
CorrSlack(C) < 0, OR certify no OSC corridor occurs in the attachment.
NET: T=2 needs NO subset sweeps — finite corridor certificates only.

## NCH T=1/T=2 AUTHORITATIVE ADDITIONS (user-relayed full texts, 2026-07-04)
T=1: REC-cert EXACT FORM: 1 - kappa_e(U) = alpha_e sigma(S_e) + beta_e nu_K(S_e) + R_e,
alpha,beta,R >= 0 — the finite local certificate family ('the zeta engine is effectively
proving REC'). Shadow completion rules (1-7): include u; segments beyond tu; B-connected
closure; terminal prefixes/suffixes; noncrossing; twins; EXCLUDE t. Equality analysis
(kappa_e = 1): forces new bad lengths exactly 5, shortest noncrossing segments, zero
residuals, UNIQUE label propagation; label disagreement => first-split/last-rejoin theta
=> triangle (excluded) / shorter odd cycle (excluded by all-l5) / gamma-neutral switch
(excluded by gamma-min). HUNT QUEUE (1-8): weighted Groetzsch FIRST, weighted M(C7/9/11),
iterated-Myc apex terminals, Hajos/Ore 2-terminal, Petersen/Kneser, M_k generalized,
Borsuk/Schrijver, random planted lifts. Expected: T=1 margins >= 0, equality only at
ordinary Myc-critical terminals. IF VIOLATED: repair = NEW non-C5-hom SEED BRANCH with
its own terminal-load certificate (named repair shape — not a collapse).
T=2: canonical row voltage l(p_i) = l(p_0) + i mod 5; interval voltage j-i (5). CROSSING
TYPES: I same-row alternating (a<c<=b<d); II theta (first split s, last rejoin r,
opposite orders along the two shadow branches; cert lists s, r, 3 branches); III = OSC.
(12) provenance: door injection (13) + Rows(U) subset crossing-rows (14, via minimal
lens + subpacket tightness: rows fully outside S would form a separated proper closed
tight packet). Noncrossing voltage balance via patterns A (disjoint: additive), B
(same-root nesting: additive; non-nested same-root = Type I), C (opposite-root corridor:
transfer kappa_C consistent else Type II), D (touching: same label; opposite-direction
shared edge = Type III/OSC). Partition identity nu_K(U) = Sigma_i CorrSlack(C_i).
Codex output per attachment: (T, {C_i}, Rows, Doors, CorrSlack, Cert in {NONNEG,
CROSS(I,J,L,S), LABEL(l), OSC(a,b)}).
