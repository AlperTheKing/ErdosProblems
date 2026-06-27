# GPT Pro: SHELL-LEMMA RETRACTED — the rigorous target is a TRANSPORTATION-SLACK / DEFECT-OVERLAP theorem (chat 6a3e68cf)

GPT Pro (Comprehensive), drove browser. Answer to "give the rigorous Defective Shell Extraction Lemma".
VERDICT: GPT RETRACTS its own earlier shell sketch. HONEST + IMPORTANT (project discipline: plausible != proved).

## What is FALSE (the retraction)
The proposed   prefix-defect eta  =>  a_i a_{i+1} >= q + eta/h^2   DOES NOT FOLLOW from CD + shortestness.
- Defective AM-GM is valid CONDITIONAL on the product inequalities a_i a_{i+1} >= q+eta/h^2; but CD+shortestness
  do NOT imply those products. The extraction step is "false in this raw form."
- There is NO canonical scalar h-shell assignment a_0..a_{h-1} that avoids the missing global layering in the
  THETA regime. Three natural definitions all fail:
  (A) endpoint BFS shells L_i={z: d_B(v_0,z)=i}: rigorous but give only the WEAKER (BFS-shell) inequality,
      not the uniform q+eta/h^2 product.
  (B) residue shells: the wraparound A_0--A_{h-1} cut-edges (introduced BY the theta regime) spoil the
      single-interface products needed for AM-GM.
  (C) nearest-contact shells: shortestness controls B-chords + multiple attachments, but does NOT force an
      edge between two outside vertices to have nearest contacts at ADJACENT positions => no clean interfaces.
- The prefix-defect inequality is LINEAR signed transport into C; a quadratic shell product needs much more.

## What IS rigorous (safe to formalize now) — the PREFIX-DEFECT TRANSPORT LEMMA
For a shortest bad geodesic C=v_0..v_{h-1} and a residual CD-obstruction S subset R=V\C with defect
eta=delta_{M[R]}(S)-delta_{B[R]}(S)>0:
   **e^sigma(C\P_i, S) + e^sigma(P_i, R\S) >= eta**    for 0 <= i < h-1.     [PROVED from CD]
(e^sigma(A,D)=e_B(A,D)-e_M(A,D); P_i={v_0..v_i}.) SHORTESTNESS is exactly what removes the positive B-chord
terms (a non-shortest path with a B-shortcut chord crossing P_i makes delta_{B[C]}(P_i)-delta_{M[C]}(P_i)>0 and
the inequality weakens/fails — exactly my N=11 non-shortest counterexample). Triangle-freeness: z v_i in B =>
z v_{i±1} not in M; xy in M => x,y no shared B-neighbor (prevent local fake support, but still don't force the
transport through a particular shell interface).

## The OPEN target — TRANSPORTATION-SLACK / DEFECT-OVERLAP THEOREM
   **prefix transport of size eta  =>  N^2 - Gamma(G) >= eta.**
Proves the LOCAL form D(C) <= N^2-Gamma(G) for each fixed shortest C (min-form suffices for induction; my data
supports the local form). MECHANISM = DEFECT-OVERLAP LEMMA: a residual improving shore S creates eta units of
bad surplus in R; original CD blocks it only via signed attachments from BOTH S and R\S into C, distributed
along C crossing every prefix. In single-block C5[q] the transport is perfectly PARALLEL => NO deficit. In an
unsafe example the transport is NON-PARALLEL: another bad edge's shortest cycle OVERLAPS the chosen cycle in a
proper path; THAT overlap is exactly what lowers Gamma below N^2. Defect-overlap lemma (to formalize): C shortest
bad geodesic, S max residual obstruction defect eta => there is a family F of >= eta bad-edge units whose
shortest cycles non-parallel-overlap C, contributing >= eta square-deficit.

## STATUS (honest)
- Master inequality Gamma+D*<=N^2 AND local D(C)<=N^2-Gamma: NUMERICALLY VALIDATED 0 violations N<=11
  (master_ineq.py) — UNCHANGED, still the right statement.
- PROOF: the shell-product route is DEAD (false step). New rigorous target = transportation-slack theorem
  (prefix transport eta => deficit >= eta) via defect-overlap. The prefix-defect transport lemma IS proved.
- The first-variation dF<0 at the C5 extremal (verify_c5_firstvar.py, given to Step-1) is UNAFFECTED — it is a
  separate exact result (strict local max), only first-order; it does NOT depend on the retracted shell step.

## MY NEXT (audit+compute)
1. VERIFY the prefix-defect transport lemma e^sig(C\P_i,S)+e^sig(P_i,R\S)>=eta on obstruction instances (N=8,
   near-tight) — confirm the rigorous foundation.
2. TEST the defect-overlap mechanism: for D(C)=eta>0 instances, exhibit the >=eta non-parallel cycle overlap
   and check deficit N^2-Gamma >= eta (= my already-validated local form).
3. Relay the HONEST correction to Step-1 (shell step false; their dF<0 still valid).
