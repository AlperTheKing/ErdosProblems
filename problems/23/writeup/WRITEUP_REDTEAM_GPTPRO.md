# Referee Red-Team over Both Writeups (GPT-Pro, 2026-07-04; 11.5k full text in thread
# 6a450f06). VERDICT: 3 BLOCKERs + 13 FIXes — interface/documentation defects, no
# confirmed false statements.

BLOCKER 1 — eta >= 0 UNSTATED in Branch-A coefficient comparisons (BA-I 4.2/5.3/9.2,
BA-IV 6): X(A) <= (25/N + beta)eta with beta <= 1 => X(A) <= (25/N+1)eta and the
4X <= 5(25/N+7/30)eta vs 4(1+25/N) comparison BOTH require eta >= 0. Branch-B proves
eta >= 2rho_L > 0 via Bank-L for L>5 rows; Branch-A has NO stated eta >= 0. Note
eta >= 0 <=> 25m <= N^2 is near-target (circularity risk!). Fix options: upstream
theorem; local all-l5 bank lemma (candidate: C5-hom cyclic prefix products n_i n_{i+1}
>= m => N >= 5 sqrt(m) — CERT-1/4-door style); or restate PMTS targets at full
coefficient. MY NOTE: the Lean lemmas (netDW_assembly, a1_5mask_absorption,
bankedUPO_implies_gersh) already carry 0 <= eta as EXPLICIT hypotheses — formal side
honest; the assembly must DISCHARGE them.
BLOCKER 2 — pruning preserves overfullness but NOT full-graph ODL: the return step
(pruned core W bounds => ambient ODL) unwritten; fix: eta-monotonicity bridge
(I_W - |W| <= I_U - |U| AND eta_U <= eta_W) or state that ALL core certificates use
AMBIENT N, m, eta (convention declaration).
BLOCKER 3 — Branch-B protected-cell residual may double-spend eta/2 (BB-IV 4.5/4.9/
T4.11 + BB-III op5): U_Q+ <= eta/2 - rho_L and Pi_cell <= eta d/2 must be ONE combined
peel inequality, not two separate eta/2 spends. (The op5 25pi(A) handoff note suggests
the ledger nets correctly — needs the single stated inequality.)
FIXes (selected): 4 Gate-A = validation annotation; 5 CD rho_a positive-part residuals
vs 24-signature dictionary — state the decomposition theorem explicitly; 8 S7 statement
under-specified for referees (include s1..s7 defs + domain + reduction statement or
cite machine artifact); 9 q<3'/Seed3' need the formal quotient model stated; 15 eta>=0
echo in 5mask branch; 16 rename HBD Lemma 4.10 to 'HBD certificate implication'
(certificate assumption explicit).

# ============ REPAIRS (GPT-Pro reply, 2026-07-03, main thread 6a450f06) ============
# Full 7.3k reply; three repairs remove the blocker-level defects. Gated my side:
# _claude_exactmask_identity_gate.py ALL PASS (clearing identity all 32 masks, empty-
# mask form, exact coeff 75N(1+25/N)/25=3N+75, assembly X(P)=sum(s_i-tau)_+ 2000 rows).

REPAIR 1 (B1) — ExactMask: restate active-mask C5-RS at the EXACT final coefficient,
for EVERY mask A subseteq Z5 (including empty and full):
    X(A) := sum_{i in A}(s(q_i)-tau) <= (1+25/N)eta,   tau=5m/N, eta=(N^2-25m)/25.
Cleared by 75N (ExactMask-Cone):
    D_A^1 := (75+3N)(N^2-25m) - 75N sum_J |A cap J| y_J + 375|A|m  in  PMTSCone*(A),
where PMTSCone*(A) = old PMTS cone (sigma(h,I), y_J, rho_* generators) PLUS optional
ACTIVE-MASK SIGN GENERATORS x_i := s_i - tau >= 0 (i in A), -x_i >= 0 (i notin A),
valid because the cert is applied ONLY at the active mask A = P := {i : s_i > tau}.
KEY: A = empty instance reads 0 <= (1+25/N)eta, i.e. D_empty^1 = (75+3N)(N^2-25m) in
PMTSCone*(empty) PROVES eta >= 0 (from row structure + all-s_i<=tau sign gens) rather
than assuming it. C5-RS derivation: P=empty branch = the empty instance; P nonempty
branch = ExactMask at A=P since sum(s_i-tau)_+ = X(P). NO beta<=1 comparison, NO
7/30->2/3 lift (that lift used etabar>=0 — now dead; each mask has its own exact cert).
CONSISTENCY: original C5-RS census 0-fail (814292 L5-multi rows) ALREADY implies
eta >= 0 held on every instance (LHS >= 0). NEW OBLIGATIONS (Codex): re-emit cones at
(75+3N) w/ sign generators for 8 dihedral classes: empty, {0},{0,1},{0,2},{0,1,2},
{0,1,3},{0,1,2,3}, Z5. Risk isolated to empty/full-mask LP feasibility at symbolic N.

REPAIR 2 (B2) — AmbientPrune: ALL certificates stated with AMBIENT bank
eta_G = (N_G^2 - 25 m_G)/25. Ambient ODL excess E_G(S,Q) := I_S(Q) - |S| - eta_G,
goal E_G <= 0. Bridge lemma: W = U cup H, T = U cap H, no edge joins U\T to H\T,
appendage condition s_H(Q\T) <= |H\T|  ==>  E_G(W,Q) <= E_G(U,Q).
Proof: load diff I_W - I_U = s_H(Q\T); size diff |W|-|U| = |H|-|T|; subtract the SAME
ambient eta_G. Consequence: minimal pruned core U with ambient cert I_U <= |U| + eta_G
extends to any W (re-attach appendages), and W subseteq V(G) gives |W| <= N_G, so
I_W <= N_G + eta_G. Pruning is support-side bookkeeping; eta stays global. (Matches the
NCH pruning criterion s_H <= |H|-|T|; load additivity I_W = I_U + s_H(Q\T) is the
definition-level obligation for appendages glued along T with no cross edges.)

REPAIR 3 (B3) — CombinedHBD: replace the two separate eta/2 statements (BB-IV 4.5
U_Q+ <= eta/2 - rho_L and 4.9 Pi_cell <= eta d/2) with ONE combined bank certificate:
    PeelSplit:    R_Q <= N + U_{Q,res} + Sigma_fan + Sigma_cell
    CombinedHBD:  2(U_{Q,res} + Sigma_fan + Sigma_cell + rho_L) <= B(W_Q^res)
where W_Q^res = residual blue-detour packet after protected-cell extraction. Packet
exchange gives B(W_Q^res) <= eta, hence U_{Q,res}+Sigma_fan+Sigma_cell+rho_L <= eta/2,
hence Banked-UPO R_Q <= N + eta/2 - rho_L in ONE step — the eta/2 bank spent EXACTLY
once. Fan ledger Sigma_fan <= sum B(F_u) folds in; the isolated cactus+SH-prime cell
estimate is NOT spent separately (subsumed). op5: the 25pi(A) per protected UNIT-FLAT5
atom is NOT paid inside CD; it transfers into Sigma_cell and is paid by CombinedHBD.

ERRATA (writeup): BB-IV 4.5/4.9/Thm 4.11 -> single CombinedHBD statement + one-step
Banked-UPO derivation; BB-III op5 -> explicit transfer note; BA all coefficient-
comparison sections (4.2/5.3/9.2, IV-6) -> ExactMask-Cone at (75+3N), drop beta<=1 and
7/30->2/3 lift; BA pruning sections -> AmbientPrune + ambient-eta convention line.

# ======= REPAIR 1 SUPERSEDED -> REPAIRED-REPAIR (GPT-Pro, 2026-07-03, same thread) =======
# I asked for the explicit empty-mask combination; GPT-Pro answered honestly:

EMPTY-MASK PMTS LP IS INFEASIBLE. Separating assignment: treat cone variables as free
abstract nonneg values; N=5, m=2 (tau=2), y_J=0, s_i=0, sigma=0, rho=0 — every
generator nonneg ((tau-s_i)=2>=0) but D_empty=(75+3N)(N^2-25m)=90(25-50)=-2250<0.
No coefficient-nonneg identity can exist. The sign generators upper-bound loads
(wrong m-sign); NOTHING row-local carries the global bank. ExactMask-as-stated DEAD
for A=empty; the (75+3N) re-emission program CANCELLED.

FINAL B1 STRUCTURE (C5RS-final):   Bank0 + A1_proper + ODL_full  ==>  C5-RS
  Bank0:  N^2 - 25m >= 0  (eta>=0), a SEPARATE scalar bank theorem, proven by the
          SAME structural split as ODL (not row-local PMTS):
   (i)  C5-hom saturated components — PROVEN IN REPLY: max-cut prefix inequalities
        n_i n_{i+1} >= m_C (i in Z5) => prod_i n_i^2 >= m_C^5 => prod n_i >= m_C^{5/2}
        => (AM-GM) N_C = sum n_i >= 5 (prod n_i)^{1/5} >= 5 sqrt(m_C)
        => m_C <= N_C^2/25; components have disjoint supports => sum_C m_C
        <= (1/25) sum N_C^2 <= (1/25)(sum N_C)^2 <= N^2/25.
        [MY NOTE: the summing step needs (a) every bad edge in exactly one component
        (K-partition, true by defn) and (b) support disjointness across components —
        pin K-adjacency = support interaction in the writeup.]
   (ii) non-C5-hom components — NCH-def/pruning branch (same tree as ODL).
   (iii) EQ/SIB seed cores + passive attachments — scalar bank certificates added to
        the seed packages (EQ: CERT-1-style conic; SIB: possibly implied by S7 —
        check; saturated 4-door C5-hom cores: same prefix-product AM-GM).
  A1_proper: the SIX EXISTING proper-mask cones at (75+2N) (2/3-coefficient) stand;
        with Bank0, X(A) <= (25/N+2/3)eta <= (1+25/N)eta is legal again.
  ODL_full: A=Z5 is X(Z5) = I(Q) - 5tau <= (1+25/N)eta <=> I(Q) <= N + eta = ODL
        exactly; handled by the existing seed/AM/A1-5mask ODL tree. FULL MASK IS
        GENUINELY REQUIRED: the EQ seed has P = Z5.
  Empty mask: Bank0 directly (0 <= (1+25/N)eta).
  Revised C5-RS proof: P=empty -> Bank0; P proper nonempty -> A1(P)+Bank0-lift;
        P=Z5 -> ODL.
  If ConeCert-driven checking is kept: add B0 := N^2-25m as an explicit generator to
  every mask cone, discharged ONLY by the Bank0 theorem (never run a mask LP without
  it where the bank is needed).

CODEX RETASK POSTED 01:15Z: stop empty-mask LP; Bank0 census gate + seed bank certs;
six cones original spec; CombinedHBD re-gate; ambient-eta audit.

# ===== SIBLING SECOND OPINION (independent, thread 6a45e152, 2026-07-03) =====
CONVERGES with main: (1) sign generators cleared = 5m - N s_i >= 0 carry +m (wrong
sign); y_J/rho give no m upper bound; the ONLY generator family able to carry a global
m-bound is max-cut switch slacks sigma(S) = dB(S) - dM(S) >= 0. Mechanism if ConeCert
is kept: a mask-independent SWITCH-COVER family {S_a, lambda_a >= 0} with
    sum lambda_a dM(S_a) >= 25 c m   (weighted bad-edge 25-cover)
    sum lambda_a dB(S_a) <= c N^2    (blue budget)
=> 25m <= N^2 via sigma >= 0 termwise. (2) Without it, empty-mask infeasible/near-
circular — MATCHES main separating assignment. (3) Fallback min-counterexample route:
assume m > N^2/25, all-l5 row with all s_i <= tau; TOTAL MASS IDENTITY sum_v s(v) = 5m
(each l=5 geodesic distributes mass 5; avg load = tau) forces overload off-row; close
overload support under terminal shadows; dichotomy (a) shadows cross => completed
switch sigma < 0 contradicting max-cut/gamma-min; (b) no crossing => C5-label
propagation => C5-hom quotient => AM-GM => m <= N^2/25. Same NCH/T=1-style machinery
as the main thread's structural split. CROSS-VALIDATION: two independent designs agree
on the Bank0 shape.

# ===== MY GATE DATA (2026-07-03) =====
_claude_bank0_component_gate.py: N<=9 named+census: GLOBAL Bank0 0-fail (2098 pure-l5
cuts, min margin +14); LOCAL m_C <= |supp|^2/25 REFUTED (8 fails, margin -1; witness
H?AFBo] theta component m_C=2 |supp|=7). N=10: GLOBAL 0-fail min margin EXACTLY 0 at
I?rFf_{N? (N=10, m=4 — the C5[2] extremal, TIGHT); local fails 119, worst -14
(m_C=2, |supp|=6). N=11 running. CONSEQUENCE: per-component summing route DEAD;
ambient forcing (outside-support vertices) is essential; relayed to main thread for
corrected skeleton.

# ===== BANK0 CORRECTED SKELETON: BANK-BLOCK THEOREM (main thread, 2026-07-03) =====
Bank0 proved by DISJOINT C5-BANK-BLOCK COVER, not K-component support.

THEOREM 1.1 (algebraic, gateable): if bad edges partition into blocks M_1..M_t and
each block kappa has FIVE DISJOINT vertex classes B_{k,0..4} (blocks pairwise disjoint)
with (a) every assigned bad edge in the B_{k,4}--B_{k,0} layer, (b) class products
n_{k,i} n_{k,i+1} >= m_k (all i in Z5, cyclic), then per block m_k <= |B_k|^2/25
(prefix-product AM-GM) and summing over disjoint blocks m <= (sum|B_k|)^2/25 <= N^2/25.

C5-BANK CLOSURE (the structural construction):
 2.1 initial row support labeled by row position V_0..V_4 (bad edges in V_4--V_0);
 2.2 PREFIX-DEFECT CLOSURE: for cyclic prefix P_i = V_0..V_i, if internal blue
     capacity e(V_i,V_{i+1}) < m_C then max-cut (sigma(P_i) >= 0, dM(P_i) = m_C)
     FORCES blue exits from P_i to outside; assign each such exit vertex to class
     V_{i+1} (supplies missing V_i--V_{i+1} capacity); close under row-segment
     consistency (C5-labels step +-1 over blue edges); repeat until
     e(cl_i, cl_{i+1}) >= m_C for i = 0..3   (2.1);
 2.3 BAD-DOOR SATURATION: absorbing a stabilizer that exposes a bad edge absorbs
     that bad edge + all its shortest rows into the same block (may merge
     K-components);
 2.4 LABEL-CONFLICT ROUTING: inconsistent C5-labels => closure is non-C5-hom =>
     routed to NCH-def/pruning branch (or non-C5-hom seed branch if hunt finds one);
 2.5 MERGE-ON-OVERLAP: closures sharing a vertex merge => final blocks disjoint.

WHY PREFIX INEQUALITIES HOLD IN THE CLOSURE: saturation => no assigned bad edge
crosses out; dM(P_i) = m_k exactly; every needed blue exit internalized to next
class => e(B_{k,i}, B_{k,i+1}) >= m_k => products >= m_k.

THETA WITNESS RESOLVED (worked in-reply): labels V_0={1,2} V_1={6} V_2={8} V_3={3,4}
V_4={7}; prefix P_1={1,2,6} has dM=2 but internal blue e({6},{8})=1 => deficit =>
blue exit (0,6) absorbed, 0 -> V_2; row-segment consistency pulls 5 (blue (0,5),(5,8))
-> V_1; final B_0={1,2} B_1={5,6} B_2={0,8} B_3={3,4} B_4={7}, |B|=9, products
4,4,4,2,2 >= 2; 25m = 50 <= 81 = |B|^2. Outside vertices = exactly the forced
stabilizers. (The witness graph is in fact C5-hom; its closure is the whole graph.)

SEED BRANCHES (sec 7): EQ = small saturated bank block; CERT-1 proves the STRONGER
bank N^2 - 25m >= 25. SIB: seed-bank certificate to include (check if S7 implies).
4-door saturated C5-hom cores: closure gives N >= 10 + local bank products.

PMTS INTERFACE (sec 8): cones may include scalar generator B_0 := N^2 - 25m,
discharged EXTERNALLY by the bank-block theorem; empty-mask cert D = (75+3N)B_0;
proper-mask comparisons sign-safe given B_0 >= 0; full mask = ODL. Interface:
Bank0 + A1_proper + ODL => C5-RS  (unchanged).

CERTIFICATE FORMAT (sec 6, for Codex): per block: classes B_{k,0..4}, assigned bad
set M_k, proofs (bad edges in 4--0 layer; e(B_{k,i},B_{k,i+1}) >= m_k; disjointness).
GATE (sec 9): do NOT gate the false support inequality; gate the BANK-BLOCK cover
existence: closure algorithm on census pure-l5 cuts; report covered vs NCH-routed.
NON-CIRCULAR: uses only max-cut sigma >= 0 + all-l5 rows; no C5-RS, no ODL, no GERSH.

# ===== BANK0 SIBLING SKELETON: MINIMAL-COUNTEREXAMPLE DICHOTOMY (thread 6a45e152, 2026-07-03) =====
Assume 25m > N^2 with B-connected gamma-min max cut, tri-free, ALL bad edges l=5.

1 MASS IDENTITY (formal): p_f(v) = |{P in R_f : v in P}|/|R_f|, sum_v p_f = 5 (rows
  have 5 vertices); s(v) = sum_f p_f(v); sum_v s(v) = 5m. Pressure Pi(U) = 5s(U)-N|U|;
  Pi(V) = 25m - N^2 > 0 at a counterexample. Cleared Hall slack nu0(U) = N|U|-5s(U);
  nu0(V) = N^2-25m. BANK0 = nu0(V) >= 0. nu0 is the global m-carrier replacing the
  dead empty-mask cone.
2 CLOSURE RULES: C1 row-interval closure (two row vertices => interval between);
  C2 row-family closure (same terminal-shadow type => all rows of f); C3 BLUE-DETOUR
  closure (blue row edge xy with B-detour in row-deleted blue graph => internal detour
  vertices added) — THE rule that absorbs the theta witness (detour 6-0-5-8 for row
  edge 6-8 pulls 0,5 into the packet; theta is NOT a standalone component); C4
  terminal-shadow completion (= the T=1/T=2 terminal machinery: terminal prefix,
  first exit, completed switch/corridor closure).
3 MINIMAL POSITIVE PACKET: choose closed U minimal with Pi(U) > 0; proper closed
  subpackets have Pi <= 0 (nu0 >= 0) — "Bank0 Hall obstruction" (Gate 3).
4 CORRIDOR DECOMPOSITION: nu0(U) = sum_C nu0(C); some corridor nu0(C) < 0 (Gate 4).
5 CROSS CASE: crossing shadows => lens => completed switch S with integer certificate
  N sigma(S) <= nu0(C) < 0 => sigma(S) < 0 contradicts max-cut (Gate 5: lens, switch,
  capacity/injection map, row-demand cover).
6 NONCROSSING => LABEL: every row imposes lambda(p_i) = lambda(p_0)+i (mod 5); blue
  edges +-1; bad edges close 4->0. NONCROSSING LEMMA: no crossing/head-on osculation
  => every voltage cycle sums 0 => consistent lambda: V(C) -> Z5 (Gate 6: spanning-
  tree potential + per-edge checks). OSC = explicit T=3-style finite residual gate
  (Gate 7), not hidden.
7 EXTENSION THEOREM: closed noncrossing deficient packet in a minimal counterexample
  = ALL of V. Proof: B-connected boundary edge xy (x in U): Case 1 terminal exit =>
  C4 adds y; Case 2 detour edge => C3 adds y (theta lands here); Case 3 y row-
  invisible (s(y)=0) pure blue support => DEAD-TAIL PEEL: deleting preserves
  hypotheses (m same, N smaller => 25m > N^2 stronger), contradicts minimality.
8 GLOBAL LABEL => AM-GM: whole graph labeled; every edge between adjacent classes;
  e_i <= n_i n_{i+1}; MAX-CUT VS THE FIVE C5-TEMPLATE CUTS (make only class-pair
  (i,i+1) monochromatic; within-class edges impossible under hom-label) =>
  cut(T_i) = e(G) - e_i <= e(G) - m => m <= e_i FOR EVERY i (19) — precise provenance
  of the prefix inequalities. Multiply: m^5 <= prod e_i <= (prod n_i)^2; AM-GM =>
  m <= N^2/25 (20). Equality exactly at balanced blowups — matches C5[t] tight data.
GATES 1-7 enumerated (mass, closure trace, Hall obstruction, corridor sum, CROSS,
LABEL, OSC). CONVERGENCE w/ main bank-block skeleton: same endpoint (C5-labels +
product AM-GM); main closure = C3/C4 here; main label-conflict routing = CROSS/OSC
certificates WITH contradiction content; sibling adds the minimal-counterexample
frame forcing U = V (removes main's disjointness bookkeeping) + dead-tail peel.
MY NOTE: template-cut step (19) is 5-line sound given a global hom-label (verified
reasoning: T_i uncuts exactly e_i, maximality of B gives m <= e_i). Hardness now
concentrated in: closure/minimality machinery, CROSS capacity map, noncrossing
voltage lemma — all reusing the existing T=1/T=2 corridor stack.

# ===== RECONCILED CANONICAL BANK0 PLAN (main thread referee + merge, 2026-07-03) =====
REFEREE VERDICTS on sibling skeleton:
 (a) DEAD-TAIL PEEL: NOT SOUND AS STATED (deleting a vertex can break max-cutness,
     gamma-minimality, l=5, B-conn). SAFE REPLACEMENT = BLUE-PENDANT PEEL LEMMA:
     Y = connected blue-only appendage attached through a SINGLE vertex t
     (N_G(Y minus t) inside Y, Y cap U = {t}), no bad edge in Y minus t, on no rows:
     delete Y minus t: bad edges + length-5 witnesses survive, B-conn survives
     (pendant), m same, N smaller, so 25m > N^2 persists: smaller counterexample.
     Valid ONLY for blue-pendant tails, not arbitrary row-invisible support.
 (b) C2 ROW-FAMILY CLOSURE: needs definition before use. Safe def: same bad-edge
     door / oriented terminal door class + terminal prefix/suffix in same
     orientation + same first blue exit, relative to current packet U.
 (c) CORRIDOR ADDITIVITY: FIX — must include a partition (each shared vertex
     assigned to exactly ONE corridor) or explicit fractional weights
     omega_{C,v} >= 0 summing to 1 per vertex; then nu0(U) = sum_C nu0(C) exact.
     CERT-NEEDED (bookkeeping once specified).
 (d) CROSSCAP nu0(C) - N sigma(S) >= 0: nontrivial, NOT derived in the skeleton;
     needs a terminal-shadow coarea certificate (row-load mass to dM(S), vertex
     capacity to dB(S), completion residuals). CERT-NEEDED.
 (e) Frames: global min-counterexample skeleton = primary for pure all-l5 Bank0
     (any L>5 row gives eta >= (L^2-25)/25 via Bank-L); bank-block = the local
     certificate form / mixed-cut-friendly extraction.
RECONCILED LEMMAS 1-8 with tags:
 L1 mass+pressure identities (sum s = 5m; Pi(V) = 25m - N^2) — PROVEN.
 L2 minimal closed positive packet (C1-C4 closure; C2 per (b)) — GATE-NEEDED.
 L3 corridor partition additivity (per (c)) — CERT-NEEDED.
 L4 CROSS gives max-cut contradiction via CrossCap (per (d)) — CERT-NEEDED.
 L5 noncrossing gives coherent voltage — CERT-NEEDED, SHARED WITH NCH-HALL.
 L6 extension U = V (C4 absorb / C3 absorb / blue-pendant peel) — GATE-NEEDED.
 L7 global label, template cuts m <= e_i, AM-GM, Bank0 — PROVEN (my gate).
 L8 bank-block algebra + cover extraction — algebra PROVEN, cover GATE-NEEDED.
ASSEMBLY: minimal counterexample, L2, L3, negative corridor, then L4 (cross) or
L5+L6 (label, U=V), then L7/L8, so 25m <= N^2 — contradiction. QED conditional on
the CERT/GATE items. Final tags: mass PROVEN; pressure PROVEN; bank-block algebra
PROVEN; theta PROVEN; dead-tail peel FALSE, blue-pendant repair; C2 FIX given;
corridor additivity CERT; CrossCap CERT; voltage LABEL CERT (shared NCH);
bank-block cover GATE.

# ===== SIBLING LEMMAS A + B (thread 6a45e152, 2026-07-03) =====
LEMMA A — ROW MONOTONICITY: PROVEN, UNCONDITIONAL. For ANY C5-hom lambda and any
length-5 row P with bad closing edge p4p0: the five steps eps_i in {+1,-1} around
the closed 5-cycle sum to 0 mod 5; integer sums of five signs lie in
{-5,-3,-1,1,3,5}; only -5 and +5 are 0 mod 5, so ALL FIVE SIGNS ARE EQUAL, i.e.
lambda(p_j) = lambda(p_0) + sigma j with one sign sigma. NO shortestness needed.
MY CHECK: exhaustive 32-pattern enumeration, 0 violations. Lean-trivial (decide).
LEMMA B — NONCROSSING gives VOLTAGE CONSISTENCY: reduced to PRIMITIVE-LENS finite
case system. Voltage graph strands: row intervals (alpha = j-i), terminal shadows,
D-cert detours (explicit internal labels), bad closures (alpha = 1; row path
voltage 4 = -1 mod 5, consistent: full row cycle = 5 = 0), completed corridor
segments. Primitive-lens reduction: a minimal nonzero closed walk contains a
primitive nonzero lens (two internally disjoint chains x to y, no proper sublens).
CASES with finite gates and named outcomes:
 RR (row vs row): same endpoint order and unequal voltage gives SHORTER_ROW (blue
   replacement contradicts shortestness); opposite order gives TYPE_II crossing.
   Gate over 0<=i<j<=4, 0<=k<4, j-i not k mod 5: SHORTER_ROW, THETA_CROSS,
   TRIANGLE — identical to T=1/T=2 first-split/last-rejoin row-theta analysis.
 RB (row vs bad closure): ROW_CYCLE_ZERO base; alternatives give
   SHORTER_BAD_GEODESIC or THETA_CROSS.
 RD/TD/DD (detours): D-cert must certify same endpoint voltage as the replaced row
   segment (theta witness detour 6-0-5-8 emitted as D-cert pulls 0,5 in);
   DD reduces via first-split/last-rejoin to RD or CROSS.
 TT same-root: NESTED_ZERO, DISJOINT, or TYPE_I_CROSS.
 TT opposite-root: SAME_TRANSFER_ZERO, TYPE_I/II_CROSS, or OSC_HEAD_ON (shared
   edge in opposite directions forces 2 = 0 mod 5 — impossible as a label case,
   MUST route to OSC).
 TR: same-row-direction additivity zero, else row-theta crossing.
 OSC types: OSC0 same-direction shared edge (merge, zero); OSC1 opposite-direction
   shared first-exit edge (TRUE residual — completed switch with negative slack or
   local impossibility); OSC2 vertex touch nonalternating (split into two smaller
   zero loops by minimality); OSC3 vertex touch alternating (= crossing); OSC4
   triple (laminar split, cross, or head-on). Only OSC1 and OSC4_HEAD_ON are true
   residuals; the rest are deterministic reductions.
PROOF OF LEMMA B: minimal nonzero walk, primitive lens, case classification; every
outcome contradicts minimality or a noncrossing/non-OSC assumption; hence no
nonzero cycle; spanning-tree potential defines lambda. Reuses the T=1/T=2 engine.


# ===== L4 CROSSCAP DESIGN (main thread, 2026-07-03) =====
CrossCap = CAPACITY IDENTITY, certified as an INTEGER FLOW (not a scalar estimate):
    5 s(C) + N dB(S)  <=  N|C| + N dM(S)          (CrossCap, == nu0(C) - N sigma(S) >= 0)
Completed switch S = LensComp(C; Pa, Pb) — EXACTLY the T=2 CROSS corridor completion
(lens = two shortest rows + terminal entrances + first split/last rejoin + exit doors;
if completion needs outside vertices, corridor enlarges by the closure rule first).
Lens classified into the same 7 primitive types + OSC0-4 subtypes as Lemma B.
INTEGER FORM: clear row denominators by D = lcm |cyc(g)|; row-load atoms (g, P, v, d)
carry demand; capacities DN per corridor vertex + DN per bad boundary edge; summing
demands vs capacities gives D-scaled CrossCap. Exact residual:
    D(nu0(C) - N sigma(S)) = R_flow + R_OSC + R_prot + R_twin + R_term + R_nc >= 0 (5.1)
each residual nonnegative; R_OSC nonzero only in OSC1/OSC4-head-on. Flow provenance:
noncrossing row-load atoms route to vertex slots (closure C1-C3 guarantee presence);
blue cancellation units route to witnessed slots (terminal-witnessed, detour-witnessed,
noncrossing-closed, protected-cell-routed).
ENGINE REUSE: same lens classifier as T=2; CrossCap = SECOND CERTIFICATE MODE of the
T=2 CROSS emitter (output pressure functional nu0(C) - N sigma(S) instead of the
terminal Hall functional U - D_T(U)). No new geometric cases. Hard gates = 7 lens
types x {OSC1, OSC4-head-on}; other OSC cases reduce (OSC0 flow, OSC2 noncrossing
residual, OSC3 terminal residual, other OSC4 LABEL/NONNEG).
FALLBACK accepted by checker: a_C sigma(S) <= nu0(C) with any a_C > 0 (same
contradiction sigma(S) < 0).
CHECKER FIELDS: corridor set C; switch S (and enlarged C' if closure grew); lens type;
OSC subtype; completion trace (terminal/noncrossing/detour/twin/protected); D;
integer atom list (g,P,v,d); dB(S) list; dM(S) list; residual decomposition values.

# ===== L6 REPAIRED + L3 PARTITION SPEC (sibling thread, 2026-07-03) =====
REPAIRED LEMMA 6 (extension): in an N-minimal Bank0 counterexample with closed packet
U, Pi(U) > 0, LABEL corridor certificate (voltage-consistent lambda on U), and all
BLUE-HANDLE residual gates discharged: U = V. Proof structure:
 1 Outside component Y of B[V-U] with a row-visible vertex: row-family/terminal-shadow
   closure absorbs (or CROSS/OSC applies) — contradiction with closure.
 2 Y row-invisible, single-attached: BLUE-PENDANT PEEL (no bad edge deleted, all
   length-5 witnesses survive, m unchanged, N drops, B-conn survives through t,
   25m > N^2 persists) — contradicts N-minimality.
 3 Y row-invisible, MULTI-ATTACHED: shortest attachment-to-attachment blue path
   through Y = blue detour between U-vertices a, b. Label-compatible: C3 absorbs —
   contradiction with closure. NOT label-compatible: finite BLUE-HANDLE gates:
   BH2 (a-y-b, s(y)=0, lambda(b)-lambda(a) = +-1 — unreachable by two +-1 steps):
     outcomes BH2_CROSS (completed switch N sigma <= nu0 < 0) | BH2_OSC | BH2_FORBID
     (local impossibility from triangle-free + row/door structure).
     HONEST NOTE: triangle-free + max-cut ALONE do NOT forbid BH2 (sigma({y}) =
     degB(y) >= 0 harmless; tri-free only makes a,b nonadjacent). Genuine gate.
   BH3 (length-3 analog).
 4 Assembly: no outside Y exists; B connected: U = V.
L3 CORRIDOR PARTITION SPEC: geometric corridor supports hat-C_c (may overlap at
articulation vertices) vs OWNED CORES V_c: pairwise disjoint, partition U, canonical
assignment of shared vertices (shared types SH0-SH4). nu0 accounting on owned cores:
nu0(c) = N|V_c| - 5 s(V_c) (row-atom form available), exact additivity
nu0(U) = sum_c nu0(c) BY PARTITION even when geometric supports overlap.
CROSS/LABEL/OSC certificates run on geometric support, deficits computed on owned
core. VERIFIER OBLIGATIONS: OWN_IN_GEOM (V_c inside hat-C_c); OWN_PARTITION;
LOAD_ACCOUNT (nu0 additivity); CLAIM_NONEMPTY (every v in U claimed geometrically);
SHARED_TYPE (every multiply-claimed vertex has SH0-SH4 type).

# ===== BANK0 DESIGN PHASE CLOSED (my assessment, 2026-07-03) =====
All L1-L8 items now PROVEN or reduced to finite machine certificates on the EXISTING
T=1/T=2 corridor engine + census gates: L1 PROVEN; L2 closure trace gate (B0-5);
L3 partition cert (spec above, B0-6); L4 CrossCap integer-flow cert (T=2 second mode);
L5 voltage LABEL cert (primitive-lens gates, B0-4); L6 PROVEN modulo BH2/BH3 gates
(B0-7); L7 PROVEN + FORMALIZED (Bank0Algebra.lean); L8 algebra PROVEN + FORMALIZED,
cover extraction gate. No unreduced mathematical gaps remain in Bank0.


# ===== SEED-BANK COMPLETION: BANK0 100% ROUTED (main thread, 2026-07-04) =====
SIB-CERT1:  N^2 - 25m >= 25, sharp at all-ones SIB seed (N=10, m=3, 100-75=25).
INDEPENDENT of S7 (S7 proves the SIB ODL/KKT inequality — different direction;
Bank0 assembly cites SIB-CERT1 directly). Grouped AM-GM proof parallel to EQ-CERT1:
classes V0={1,2} V1={5,6} V2={0,8} V3={3,4} V4={7,9}; bad mass m = w1w7+w1w9+w2w9;
grouped U=w0+w8, V=w3+w4, Z=w5+w6, X=w1+w2, Y=w7+w9; A=U+V+Z, B=X+Y, N=A+B, T=m+1.
Generators (max-cut flips on the SIB quotient): G12 = w0w6+w5w8+w6w8-m >= 0,
G23 = w0w4+w3w8+w4w8-m >= 0, GV = V-X >= 0, GZ = Z-Y >= 0, plus w_i >= 1.
Product bounds: UZ-T = G12+(w0w5-1); UV-T = G23+(w0w3-1); XY-T = w2w7-1;
VZ-XY = Z*GV + X*GZ; hence UZ,UV,XY,VZ >= T. Block SOS: UA = A^2-9T =
(1/2)[(U-V)^2+(U-Z)^2+(V-Z)^2] + 3[(UV-T)+(UZ-T)+(VZ-T)] >= 0;
UB = B^2-4T = (X-Y)^2 + 4(XY-T) >= 0. Conic core (same as EQ):
(AB+6T)((A+B)^2-25T) = UA(AB+14T) + UB(AB+24T) + 2 UA UB; AB+6T > 0 =>
N^2 >= 25T = 25(m+1) => SIB-CERT1. MY GATE _claude_sib_cert1_gate.py: ALL PASS
(7 identities exact sympy; 4594 generator-feasible spot points all >= 25; sharp
at all-ones). Remaining provenance item (Codex): G12/G23/GV/GZ as genuine SIB-
quotient max-cut flips (same status as EQ CERT-1 generators).
PASSIVE ATTACHMENTS: no new bad door => m unchanged, N increases =>
N_ext^2 - 25 m_ext >= N_seed^2 - 25 m_seed >= 25. No separate certificate needed.
2DOOR ROUTING: 2Door-ODL handles row overload (q<=2 => I(Q) <= N) but NOT scalar
bank; saturated C5-hom q<=2 cores route Bank0 through the C5-BANK-BLOCK cover
(prefix-defect closure + saturation + merge => n_i n_{i+1} >= m_alpha => AM-GM).
NCH pruning only for non-C5-hom closures or prunable non-C5 attachments.
SEED3 ROUTING TABLE (7 outputs): EQ -> EQ-CERT1 (PROVEN); SIB -> SIB-CERT1
(PROVEN); NO_OVERFULL -> BankBlock (I<=N does NOT imply bank); NEG_SWITCH ->
branch impossible (sigma<0 contradicts max-cut, or sigma=0 & nu<0 contradicts
Gamma-min); PRUNABLE -> NCH/pruning + reduced-core bank w/ ambient bookkeeping;
NOT_SATURATED -> absorb + rerun (not terminal); FOUR_DOOR -> BankBlock (ODL side
routes A1-5mask). FINAL DEPENDENCY TABLE: EQ/EQ-ODL1+EQ-CERT1; SIB/S7+SIB-CERT1;
passive/AM+seed-bank; q<=2/2Door+BankBlock; q>=4/A1-5mask+BankBlock; NO_OVERFULL/
I<=N+BankBlock; NEG_SWITCH impossible; PRUNABLE pruning+reduced; NOT_SATURATED
rerun; non-C5-hom/NCH-def or new seed branch (hunt).
=> BANK0 ARCHITECTURE HAS NO UNROUTED CASE. Remaining Bank0 obligations are all
machine certificates: closure-trace gate, partition cert, CrossCap mode, voltage
lens gates, BH2/BH3, bank-block cover extraction, NCH branch (own program).

