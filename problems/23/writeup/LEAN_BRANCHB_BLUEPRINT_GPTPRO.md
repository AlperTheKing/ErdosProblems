# Lean 4 Branch-B Formalization Blueprint (GPT-Pro, 2026-07-03, thread 6a450f06)

Core recommendation: mathlib SimpleGraph for graphs/walks, but OWN certificate-oriented
row/path records for all row-local algebra (Walk/dist only as existence/minimality bridges).

## 1. Definition stack
- ORDERED DARTS, not Sym2, for flip algebra: darts G = (univ x univ).filter Adj;
  obadCount = darts filtered same-side, card. (Unordered = obadCount/2; keep doubled
  or normalize later.) Flip identity IN INT (avoid Nat subtraction):
  (obadCount(flip c S) : Z) - obadCount c = oBoundaryBlue c S - oBoundaryBad c S.
  Max-cut => 0 <= oBoundaryBlue - oBoundaryBad = doubled sigma(S) >= 0.
- CutState bundle: {cut, maxCut : forall c', obad cut <= obad c', BConnected,
  gamma, gamma_eq, gammaMin : forall c' (same obad, BConnected), gammaOf cut <= gammaOf c'}.
  Rows NOT inside CutState (derived certificate objects, separate).
- Row record (vector-indexed, NOT raw Walk): {L : N, hL : 5 <= L, q : Fin L -> V,
  inj, bad_end : IsBad (q 0) (q last), blue_step : forall i, IsBlue (q i) (q i+1),
  shortest : forall P : BPath (q 0) (q last), L-1 <= P.len}.
  Bridges: Row.toWalk, Row.len_eq_dist. Intervals [i,i+2], lane counts = finite sums over Fin.
- SwitchCert record: {S, oldBad newBlue : Finset Edge, correctness props,
  oldLenSq = sum ell^2, newLenSq = sum lambda^2, nu = newLenSq - oldLenSq (Z),
  K = oldLenSq, nuK = nu + K*sigma, nuK_nonneg}. nuK_nonneg proof: sigma=0 via gammaMin;
  sigma>=1 via nu >= -K.

## 2. op2 witness (the shortestness/tri-free interaction point)
AVOID the general odd-closed-walk theorem. Instead:
- switchedWitnessPath: suffix (outside S, blue stays blue) + bad edge g (crossing S,
  becomes blue) + prefix (inside S, blue stays blue) — concatenated BPath in flip c S
  joining the new bad edge's endpoints; shortestness of the OLD row controls its length.
- badEdge_ell_ge_five (triFree) : ell = dist_B + 1; ell /= 1 (no loops); ell /= 3
  (B-path length 2 + bad edge = triangle); same-side endpoints => B-distance even => >= 4
  => ell >= 5. TerminalPrefixWitness structure {g, P : BadRow, t, inS_prefix, outS_suffix};
  boundary_blue_becomes_bad lemma.

## 3. Dependency-ordered modules
L0: Util/RatNat (casting N->Z->Q staged lemmas).
L1: Graph/Cut (IsBlue/IsBad, flip, SIMP LEMMA SET: flip_side_mem/not_mem,
    same_flip_same_region, diff_flip_cross_boundary — then simp [IsBad,IsBlue] closes
    most flip-status goals); Graph/Darts (obadCount, flip_obadCount_eq,
    maxCut_sigma_nonneg — FIRST LOAD-BEARING FILE); Graph/Distances (BPath, bridge to
    Walk, ell, ell_ge_five; only file depending on SimpleGraph.Metric);
    Graph/Gamma (gammaOf, CutState, SwitchCert, nuK_nonneg).
L2: Rows/Row (endpoints, blue edges, nodup, parity, shortestness bridge);
    Rows/Intervals (raw [i,i+2] intervals, sigma_i^0, rowNeighbor_card_le_two,
    rowNeighbor_two_eq_dist — spacing).
L3: BranchB/PacketExchange (MinimalCounterexampleHyp class or explicit IH param;
    two-orientation boundary lemma; Q for final ineq);
    BranchB/PressureIdentity (pure ring: -Delta_Q = rho_Q - P_Q, sparse identity);
    BranchB/RawLaneCoarea (spacing, d = n1 + 2n2, P_Q <= kappa_L sum sigma_i^0 for
    L=7,9,11; L>=13 case; nlinarith per L).
L4: BranchB/CD/CompletionOps (inductive CompletionOp | bSegment | terminalPrefix |
    noncrossing | twinClosure | flat5Extraction; per-op op_residual_nonneg,
    op_sigma_loss_le_residual); CD/Telescope; Cells/Fan (Pi_fan <= |dB(F_u)|),
    Cells/SHPrime (m_out <= r^2/25 + d/2), Cells/Ledger.
L5: BranchB/BlueDetour (rowDeletedBlueGraph, components, T_Q(K), U_Q+, decomposition);
    HBD (increment lemma); BankedUPO (Bank-L + H_BD + ledger => R_Q <= N + eta/2 - ...);
    GershLong (=> GERSH_{L>5}).

## 4. Certificate infrastructure (Branch-A track)
Data + ONE generic verified checker (reflective), NOT per-cert tactic scripts:
- ConeCert {lhs rhs : RawPoly, proofNorm : normalize lhs = normalize rhs (by rfl on
  literal lists — have the GENERATOR output already-normalized lists), nonnegPieces};
  coneCert_sound proven once.
- BernsteinCert {degree, coeffs, coeffs_nonneg}; bernstein_nonneg_on_cube proven once.
- decide kernel-checkable but slow; native_decide OUT. rfl-on-literal-lists is best.

## 5. Risk order (confirms mine, one adjustment)
(1) Flip calculus + row infrastructure ~60 percent — get nuK_nonneg EARLY (used everywhere;
same layer as flip calculus). (2) Packet exchange mechanical after (1) (main issue:
IH packaging + boundary orientation). (3) CD op2/op3 ~30 percent — do AFTER SwitchCert
stabilizes; completion as CERTIFICATE TRACES, not algorithms. (4) Lane coarea/Bank-L
assembly = arithmetic (nlinarith). (5) Polynomial certificates = separate track.

## 6. Pitfalls
- N counts, Z flip differences, Q final inequalities — NEVER mix in one theorem; staged.
- Bool cuts: simp lemma set, no per-proof case splitting.
- DecidableRel: variable at file top, classical inside proofs, explicit instances if slow.
- Avoid G.induce in core files; predicate inducedAdj (S) u v = Adj u v AND u,v in S.

## 7. FIRST MILESTONE
theorem bankL_from_lane_cert (st : CutState G) (Q : Row G st.cut)
  (hL : Q.L in {7,9,11}) (hp : p = 1) (hh : h = 0) (hP : 0 < P_Q)
  (cert : LaneCoareaCert st Q) : -Delta_Q >= 0
— checks spacing + raw coarea + CD telescope + nuK_nonneg + arithmetic; must NOT know how
Codex found cert. "Once this compiles, the rest of Branch-B is assembly."
