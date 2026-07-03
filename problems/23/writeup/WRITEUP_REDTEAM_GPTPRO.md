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
