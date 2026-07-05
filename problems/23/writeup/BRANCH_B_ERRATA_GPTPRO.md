
# ===== BRANCH-B ERRATA F1-F4 (sibling thread, 2026-07-04; verbatim modulo notation) =====

F1. Location: Part IV, Sections 4.5, 4.9, and Theorem 4.11. Replacement text:
The HBD and protected-cell estimates are used only through the CombinedHBD
certificate. The argument no longer spends an eta/2 bank separately for the
blue-detour residual and again for the protected cells. For an overfull row Q, the
protected-cell extraction decomposes the row contribution as
    R_Q <= N + U_{Q,res} + Sigma_fan + Sigma_cell.
Here U_{Q,res} is the positive blue-detour residual after protected-cell
extraction, Sigma_fan is the fan ledger contribution, and Sigma_cell is the total
protected-cell contribution, including the cactus and SH-prime pieces. The
CombinedHBD certificate supplies one bank inequality:
    2(U_{Q,res} + Sigma_fan + Sigma_cell + rho_L) <= B(W_Q^res),
where W_Q^res is the residual blue-detour packet after protected-cell extraction
and rho_L >= 0 is the ledger reserve. The packet-exchange theorem gives
B(W_Q^res) <= eta. Combining the two inequalities gives
    U_{Q,res} + Sigma_fan + Sigma_cell <= eta/2 - rho_L.
Substituting into the PeelSplit decomposition yields the Banked-UPO bound
    R_Q <= N + eta/2 - rho_L.
Thus the eta/2 bank is spent exactly once, through the single residual packet
W_Q^res. The formerly isolated cactus-plus-SH-prime protected-cell estimate
Pi_cell <= eta d/2 is subsumed into Sigma_cell inside CombinedHBD and is never
spent separately. All protected-cell charges, fan charges, and residual detour
charges are paid by the same CombinedHBD inequality before packet exchange is
applied. Theorem 4.11 reads: if the PeelSplit certificate, the CombinedHBD
certificate, and the packet-exchange certificate are all valid for Q, then
R_Q <= N + eta/2 - rho_L; proof = the single chain
R_Q <= N + U_{Q,res} + Sigma_fan + Sigma_cell <= N + (1/2)B(W_Q^res) - rho_L
<= N + eta/2 - rho_L. No additional protected-cell eta/2 estimate is invoked.

F2. Location: Part III, op5 completion operation paragraph. Replacement text:
For op5, the protected UNIT-FLAT5 atom has a transfer charge. The contribution
25 pi(A) attached to a protected UNIT-FLAT5 atom is not paid inside the CD
completion telescope. The CD completion records the local completion residuals
and transfers this protected-flat contribution into the protected-cell ledger.
In the global accounting it appears as part of Sigma_cell. It is then paid by
CombinedHBD through the single inequality
2(U_{Q,res} + Sigma_fan + Sigma_cell + rho_L) <= B(W_Q^res). Thus op5 does not
spend a CD residual bank for 25 pi(A). The CD trace transfers the charge to
Sigma_cell, and CombinedHBD pays it together with the fan, cactus, SH-prime,
and residual blue-detour charges.

F3. Location: Branch-B pruning sections. Replacement text:
All pruning certificates are stated with the ambient bank of the original graph.
If G is the original graph, then eta_G = (N_G^2 - 25 m_G)/25 is fixed throughout
the pruning argument. For a support S and row Q, define the ambient ODL excess
    E_G(S,Q) = I_S(Q) - |S| - eta_G.
The ambient bank eta_G is not recomputed after pruning.
AmbientPrune bridge lemma. Let H be a prunable appendage glued to the rest of
the support along T, with no cross edges except through the prescribed gluing
set, and suppose the row load in the removed part satisfies
I_{H minus T}(Q) <= |H minus T|. Let S be the unpruned support and
S' = S minus (H minus T) the pruned support. Then E_G(S,Q) <= E_G(S',Q).
Indeed, I_S(Q) - I_{S'}(Q) = I_{H minus T}(Q) <= |H minus T|, while
|S| - |S'| = |H minus T|; subtracting the same ambient eta_G on both sides gives
E_G(S,Q) - E_G(S',Q) = (load difference) - (size difference) <= 0. Therefore a
certificate proving E_G(S',Q) <= 0 on the minimal pruned core also proves
E_G(S,Q) <= 0 on the unpruned support. In particular, for any support W inside
V(G), the ambient conclusion is I_W(Q) <= |W| + eta_G <= N_G + eta_G. Pruning is
monotone only for the ambient excess E_G, not for a recomputed smaller-graph
bank.

F4. Location: every Gate-A passage in Branch-B. Replacement text:
Gate-A is an exhaustive exact validation annotation on the census instances, not
a proof ingredient. It records that the stated certificate inequality was checked
on every enumerated instance in the Gate-A battery and that the emitted data
match the declared schema. The proof obligation is discharged by the named
certificate family cited here, not by Gate-A itself.
[Standard per-mention sentence: tail cut at extraction boundary; full text in
thread 6a45e152 — re-extract if needed at document assembly time.]


# ===== E2 (sibling thread, 2026-07-05; reconstructed from transformed extraction) =====

E2. CD lambda_a positive-part residuals and the 24-signature dictionary.
Target section: Part III, 3.3 (CD completion operations and telescope); also any
Branch-B section that treats the CD residuals rho_a as already decomposed or
automatically nonnegative dictionary charges.
Anchor phrases (old text): "the CD residuals are the 24-signature rows" /
"rho_a is paid by the signature dictionary" / "the 24 signatures give the CD telescope".

Replacement text:
The CD completion telescope and the 24-signature dictionary are TWO SEPARATE
certificate layers.
For each completion operation a, the trace records the exchange quadruple
    (e_B(X_a, I_a), e_M(X_a, I_a), e_B(X_a, O_a), e_M(X_a, O_a)),
where I_a is the carrier before the operation, X_a is the added set, and
O_a = V \ (I_a u X_a). The signed sigma loss is
    q_a = e_B(X_a,I_a) - e_M(X_a,I_a) - e_B(X_a,O_a) + e_M(X_a,O_a),
so that q_a = sigma(I_a) - sigma(I_a u X_a).
The positive-part residual attached to the operation is rho_a = 25 * max(0, q_a).
The CD telescope proves
    25*sigma(I_0) <= sigma_K(S) + SUM_a rho_a.
This is the telescope theorem. It uses only the exchange quadruple identities, the
definition of rho_a, and the final completion dominance inequality. It does NOT by
itself decompose the residuals rho_a into the finite signature atoms.
The decomposition of the residuals is a SECOND certificate theorem. For every
operation a, the trace records a core signature id sig(a) in {1,...,24} and an
integer environment env(a). The 24-signature dictionary certificate proves the
exact identity rho_a = Dict_{sig(a)}(env(a)). Each dictionary row is a nonnegative
linear combination of the declared core-signature atoms. Hence
    SUM_a rho_a = SUM_a Dict_{sig(a)}(env(a))
is an exact nonnegative dictionary charge.
Thus the CD part of the proof has the two-step form: the telescope supplies the
positive-part residuals; the dictionary supplies their finite nonnegative
decomposition. BOTH certificate layers are required.
