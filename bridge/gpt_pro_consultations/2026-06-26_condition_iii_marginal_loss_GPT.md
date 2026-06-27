# GPT Pro: condition (iii) = the MARGINAL-LOSS lemma (chat 6a3e68cf) — the right framing + reduction to two inequalities

GPT Pro (Comprehensive), drove browser. Answer to "prove cond (iii) mass bound; right bad-edge choice;
does tri-free+shortest cap incident mass?". Directly resolves the M(Grotzsch) per-geodesic (iii)-violation.

## REFRAME: marginal-loss, not raw incident-mass
Condition (iii) should be stated for the NET loss, not raw mass:
   L(C) = mu(C) - Delta(C) <= 2hN - h^2 ,   h=|C|.     [ML]
   mu(C)    = sum_{f in M: f cap C != empty} ell(f)^2       (incident mass, incl. peeled edge h^2)
   Delta(C) = sum_{f in M: f cap C = empty} (ell_{G-C}(f)^2 - ell_G(f)^2) >= 0   (survivor distance-growth)
Identity (verified): Gamma(G)-Gamma(G-C) = mu(C) - Delta(C) = L(C). So my code's L=Gamma-Gamma' IS the marginal loss.

## RIGHT CHOICE of bad edge (answer to Q1)
Choose the shortest B-geodesic cycle MINIMIZING the marginal overshoot
   ov(C) = L(C) - (2|C|N - |C|^2)    (equivalently MAXIMIZING the post-peel surplus Gamma(G-C)-(N-|C|)^2).
NOT minimum ell (min ell is only a secondary tie-breaker to kill internal bad chords). This is the exact
induction potential. [Explains M(Grotzsch): the +20 geodesics are WRONG choices; the min-overshoot C has
L-bound=-130 (huge slack). Arbitrary choice fails; min-overshoot choice works.]

## Q2 (does tri-free + shortest cap incident mass?) — NO, not at the ell^2 level
Tri-free + shortest give: no B-chords of C; no mixed adjacent attachments (z v_i in B => z v_{i±1} not in M);
no shared B-neighbor for a bad pair (xy in M => x,y no common B-nbr); and the UNWEIGHTED bound (CD on {v}:
d_M(v)<=d_B(v); cycle-degree sum_{v in C} d_B(v) <= N(h-1)/2):
   |M_C| <= N(h-1)/2 - 1.
But they do NOT prove the ell^2-weighted  mu(C) <= 2hN-h^2 . A vertex of C can support several long bad edges.

## REDUCTION to TWO inequalities (both tight on C5[q])
Decomposition: for f in F(C):={incident bad edges != peeled}, ell(f)^2 = h*ell(f) + (ell(f)^2 - h*ell(f)), so
   mu(C) <= h^2 + h*A(C) + H(C),   A(C):=sum_{F(C)} ell(f),  H(C):=sum_{F(C)} (ell(f)^2 - h*ell(f))_+ .
Hence (ML) follows from:
   (A')  ANCHORED LENGTH:    A(C) = sum_{f in F(C)} ell(f) <= 2(N-h).
   (LEP) LONG-EDGE PAYMENT:  H(C) = sum_{f in F(C)} (ell(f)^2 - h*ell(f))_+ <= Delta(C).
Then mu(C) <= h^2 + 2h(N-h) + Delta(C) = 2hN - h^2 + Delta(C), i.e. mu(C)-Delta(C) <= 2hN-h^2 = (iii). QED-modulo.
GPT self-corrected (A): on C5[q] the peeled transversal touches 2q-2 external bad edges each ell=5, so
A(C)=10q-10=2(N-h) (NOT N-h — original (A) was too strong by factor 2). On C5[q]: A=2(N-h), H=0, Delta=0 (all tight).

Two overshoot causes, separately detected: too-many-equal-length edges => A(C)>2(N-h); long edges => H(C)>Delta(C).

## STATUS: a clean reduction, NOT a proof
(A') and (LEP) are the two remaining open lemmas for condition (iii). GPT also sketched an EXCHANGE inequality
(minimality of the chosen C: if an incident f is too expensive, peel C_f instead — lower overshoot) + a
sub-tightness certificate (Gamma<N^2 excludes overshoot at/above tight; thin-neck excluded structurally) to
drive (A')+(LEP). Not completed.

## MY AUDIT (next): verify (A') and (LEP) hold for the MIN-OVERSHOOT choice on C5[q], n8, M(Petersen),
M(Grotzsch), and a census sweep. Both tight on C5[q]; if they hold on M(Grotzsch) for the right choice, the
reduction is sound and the (+20) wrong-choice geodesics are irrelevant.
