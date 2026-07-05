
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

# ===== E3 (sibling thread, 2026-07-05; reconstructed from transformed extraction) =====

E3. S7 sibling certificate statement made explicit.
Target section: Branch A, Section 2.6 (Sibling seed and S7); also anywhere S7 is cited
without its domain and slacks. Anchor: "by S7" / "the S7 inequality" / "the sibling
active-five certificate".
Replacement text:
The sibling active-five certificate is the following explicit S7 inequality.
Let a,b,c,d,e,f,x,y,u,v >= 1. Define
  m = x*u + x*v + y*v,
  N = a+b+c+d+e+f+x+y+u+v,
  Y = a*c + b*f + c*f,
  Z = e*Y + d*f*(b+c),
  A = b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f,
  B = a*c+a*e+b*f+b*e+c*f+c*e+e*f.
The row excess is IminusN [I - N]; the seventh slack is s7 = a*e + d*f + e*f - m.
S7 domain: a..v >= 1 and s1,...,s7 >= 0. Certified inequality:
  2*(N^2 - 25m) - 75*IminusN >= 0,
equivalently IminusN <= (2/75)(N^2-25m) = (2/3)(N^2/25 - m) = (2/3)*eta.
The rational-form denominator is positive on the domain (e > 0, Y > 0, Z > 0), so
clearing denominators preserves sign.
Proof = the archived endpoint-fiber and residual-fiber certificate: compactified
counterexample reduction sends every candidate negative point to endpoint or
capacity-endpoint faces; y=1 and x=1 endpoint faces reduced by endpoint-derivative
exclusions to finite face gates; the twelve residual capacity-endpoint faces (s_j=0,
j in {4,5,6,7}, with u=1, v=1, or s1=0) reduced by the residual-fiber quadratic
certificate to stationary and s3=0 corner gates; the four s1=0 stationary gates closed
analytically by certified floor inequalities F4A, F4B, F5, F6, F7; remaining gates
discharged by the exact S7 machine artifact.
Every citation to S7 means precisely this inequality, on this domain, with the seven
displayed slacks, after clearing the positive denominator.

# ===== E4 (sibling thread, 2026-07-05; reconstructed from transformed extraction) =====
# (sibling numbering; follows the CD-dictionary erratum I archived as E2)

E4. q<3-prime and Seed3-prime quotient model made explicit.
Target section: Branch A, Sections 2.7 (q<3-prime and Seed3-prime); also any place where
these certificates are described as informal finite quotient checks.
Anchor phrases: "the q<3-prime quotient check" / "the Seed3-prime seed check" /
"the quotient certificate verifies this case".

Replacement text:
The q<3-prime and Seed3-prime certificates are interpreted in the formal Seed10 quotient
model. A Seed10 quotient consists of: a map phi : V -> {0..9} (ten bags); bag weights
w_i = |phi^{-1}(i)|; a seed edge relation on the bags; a fixed cut side
side : {0..9} -> {0,1}; a C5-class map cls : {0..9} -> Z/5Z; a door list; and a finite
list of seed row templates R : {0,1,2,3,4} -> {0..9}.
A realization of the seed by the graph means: every graph edge projects to a seed edge;
every seed edge represents complete bipartite adjacency between its bags; no graph edge
between seed nonedges; vertex cut side agrees with bag side; vertex C5-class agrees with
bag class; every seed row template used by the certificate lifts to a certified row of
the graph. A seed row template is VALID when its four consecutive edges are cut edges in
the seed, its closing edge is a bad edge in the seed, and its C5 classes advance
monotonically around C5 up to reflection — checked from the literal seed data.
Weights satisfy N = sum_{i=0}^{9} w_i.
The seven-cut cone is NOT an abstract assumption. Each of its seven slacks is attached to
a witnessed seed cut X subset {0..9}. The slack polynomial is
  F_X(w) = sum_{ij in E_seed, i in X, j notin X, side(i) != side(j)} w_i w_j
         - sum_{ij in E_seed, i in X, j notin X, side(i) == side(j)} w_i w_j.
For a realized graph, F_X(w) = delta_B(phi^{-1}(X)) - delta_M(phi^{-1}(X)). Since the cut
is maximum, this is nonnegative — every seven-cut slack is a genuine max-cut switch slack.
The checker records the literal slack polynomial AND the seed cut witness X, verifies
slackLit = F_X(w) by exact polynomial equality; semantic nonnegativity follows from the
max-cut inequality on phi^{-1}(X).
Cone semantics of the Seed10 realization: w_i >= 0; N = sum w_i; each witnessed seven-cut
slack F_X(w) >= 0; any listed equality/seed-vanishing polynomial vanishes on the declared
quotient stratum. Every polynomial inequality in these sections is then certified by the
generic ConeCert, BernsteinSimplex, or BernsteinCube checker over this Seed10 realization.
No quotient inequality is used without a seed realization, a witnessed cut slack, and the
corresponding checker identity.

# ===== E5 (sibling thread, 2026-07-05; reconstructed from transformed extraction) =====

E5. Five-mask absorption branch routed through etaNonneg.
Target section: Branch A, Section 2.3 (Proper-mask A1 cones); also any coefficient-
comparison passage where the lift from the certified proper-mask coefficient to the
C5-RS coefficient uses eta >= 0.
Anchor phrases: "using eta >= 0" / "the 7/30-to-2/3 lift" / "the five-mask absorption
gives the required coefficient".

Replacement text:
The proper-mask A1 certificates are applied only AFTER the global scalar input
etaNonneg : eta >= 0 has been established. This scalar input is supplied by Bank0 in
the pure all-length-five case, and by Bank-L whenever a longer positive row exists.
The A1 cones do NOT prove eta >= 0.
Let A be a nonempty proper active mask (empty != A subsetneq Z/5Z) and define
X(A) = sum_{i in A} (s_i - tau). The A1 proper-mask cone certificate proves the
certified inequality X(A) <= (25/N + 2/3) * eta. Since etaNonneg gives eta >= 0, one
has (2/3)*eta <= eta, therefore X(A) <= (25/N + 1) * eta. For the active mask P = A,
sum_i (s_i - tau)_+ = X(A). Hence the proper-mask case of C5-RS follows:
sum_i (s_i - tau)_+ <= (1 + 25/N) * eta.
The logical order is essential: FIRST etaNonneg is supplied externally (Bank0 if all
bad edges have length 5; Bank-L if some positive row is longer); SECOND the six A1
proper-mask cones prove their certified coefficient; THIRD etaNonneg permits the
coefficient lift from 2/3 to 1. No empty-mask cone certificate is used to prove
eta >= 0, and no A1 cone is invoked before etaNonneg is available.
In the Branch-A input package the required scalar hypothesis is the field
etaNonneg : eta >= 0 — not a direct Bank0 hypothesis. Bank0 is one possible source of
etaNonneg; Bank-L is the other.
