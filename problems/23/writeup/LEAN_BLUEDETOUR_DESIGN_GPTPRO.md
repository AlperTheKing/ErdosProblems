# BlueDetour/HBD/BankedUPO Lean Design (GPT-Pro, 2026-07-04, sibling 6a45e152; 21k
# full text in-thread — essentials)

PRINCIPLE (same as CDCore): search choices = emitted certificate traces; Lean proves
universal counting + arithmetic + assembly.
BlueDetour.lean: Row.isBlueStepEdge predicate -> rowDeletedBlueGraph (blueGraph minus
row edges; NO quotient components) -> RDComponent/RDComponentSet EMITTED with fields
{pairwise_disjoint, cover_univ (needed for row-load decomposition), connected, maximal
(needed for detour soundness)} -> partition sum lemmas -> detourCap per component, Upos
-> Row.RQ_le_N_add_Upos (R_Q <= N + U_Q+). Detour certificate layer: DetourPathCert /
DetourCapCert (+ optional import of Codex 136-row D-cert data).
HBD.lean: badInducedN/badCrossN counts; Bank25/BankQ (25-scaled INTEGER bank);
Bank25_increment_exact + increment_noBadCross (Inc-LB); fold induction; BDPlus S Q C
rhoL := Upos <= eta/2 - rhoL; HBDOverfullCert {rhoL, trace, coversPositive, arith
(reflective)}; HBDOverfullCert.sound (given overfull N < R_Q).
BankedUPO.lean: assembly = pure linarith given {R_Q <= N + Upos, Upos <= eta/2 - rhoL,
0 <= rhoL, 0 <= eta}; GershBound.of_row_le_N for non-overfull rows (R_Q <= N immediate).
Implementation order: BlueDetour defs -> partition lemmas -> RQ decomposition -> detour
certs -> HBD core -> HBDOverfullCert -> BankedUPO linarith assembly.
STATUS: with this, EVERY Branch-B Lean module has a blueprint (Darts/Distances/Gamma/
Row/BankL/PacketExchange/CDCore implemented; BlueDetour/HBD/BankedUPO + footprint layer
+ injection = remaining implementations).
