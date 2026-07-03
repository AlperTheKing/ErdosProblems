# PacketExchange Lean Design (GPT-Pro, 2026-07-04, sibling thread 6a45e152 — full 16k
# text in-thread; essentials here)

TARGET (division-free, INT): 50 m_R + 25 h <= 2 r^2 + 25 d; rational corollary after.
LOCAL counting/exchange theorem — NO minimal-counterexample packaging needed.
Module: BranchB/PacketExchange.lean importing Darts/Gamma/Row/BankL; uses ONLY
flip_obadCount_eq + maxCut_sigma_nonneg (or nuK bridge); no CD imports.
DESIGN: POrient {pos, neg}; per-orientation OrientExchangeCert with INJECTION
exch : OrientSrc -> OrientTgt (Fintype.card_le_of_injective); source counts
25 m_R + 25 h_o + 25 delta_B(X_o); target r^2 + 25 d_o + 25 delta_M(X_o)
[SIGN CAUTION: delta_M on TARGET side, delta_B on SOURCE — reversed = wrong sign];
sigma >= 0 (maxCut) drops the boundary difference => 25 m_R + 25 h_o <= r^2 + 25 d_o;
sum over orientations (h = hN pos + hN neg, d likewise BY DEFINITION — no partition
lemma) => 50 m_R + 25 h <= 2 r^2 + 25 d.
PRACTICALITIES: Fin-indexed atoms (mAtom : Fin mN -> PacketMAtom) NOT Finset (Row S)
(DecidableEq pain); PairBox = ORDERED Fin r x Fin r (card exactly r^2); counting over
INT in multiplied form, coerce late; bridge lemma sigmaQ_nonneg_of_switch if going
through SwitchCert. Risk: the injection well-definedness proof obligations (exchange
map into pair box) = the core work; everything else mechanical.
