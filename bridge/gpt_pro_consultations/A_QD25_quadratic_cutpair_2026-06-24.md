# GPT (chat 6a3b5aba): DECISION (A) -- a QUADRATIC CUT-PAIR certificate for the Connected-B Gamma Lemma

NOT ordinary electrical flow / multicommodity congestion (too strong; theta/series-parallel is exactly where
cut conditions fail to characterize multiflows). Give this ONE sharply-scoped attempt before formalizing.

## QCD -- tensorized cut domination (the core inequality)
For S subset V: b(S)=|delta_B(S)|, m(S)=|delta_M(S)|; CD says m(S)<=b(S). Choose nonneg cut weights a_S;
coverage of bad edge e: h_a(e) = sum_{S: e in delta_M(S)} a_S. Then
   sum_{e in M} h_a(e)^2 = sum_{S,T} a_S a_T |delta_M(S) ∩ delta_M(T)|
                        <= sum_{S,T} a_S a_T min{m(S),m(T)}
                        <= sum_{S,T} a_S a_T min{b(S),b(T)}.    (QCD)
=> IF cut weights a_S can be chosen with h_a(e) = ell_e (= d_B(e)+1) for all e AND
   sum_{S,T} a_S a_T min{b(S),b(T)} <= N^2, THEN Gamma = sum ell_e^2 <= N^2. [THE certificate to construct]

## Dual / energy-profile form (prevents the independent-cut overcount that killed earlier routes)
A COMMON nonneg energy profile z_r (r = boundary level), Z_k := sum_{r<=k} z_r, with sum_r z_r^2 <= 1
(Energy-dual). Level-capacity: sum_{e in delta_M(S)} y_e <= Z_{b(S)} for all S. Then the Connected-B Gamma
Lemma follows from
   (QD25)   sum_{e in M} ell_e y_e <= N   for every dual-feasible (y,z).
The SAME profile z governs every cut (no per-cut overcount). Cauchy gives Z_k <= sqrt(k) but keeping the
common profile is the point.

## The exact finite certificate (theta regime, boundary <= 3)
Elementary theta cuts: interval cuts inside one branch (B-boundary 2); transversal prefix cuts = an s-prefix
on every branch (B-boundary 3); endpoint cuts (boundary 1, degenerate). Construct nonneg multipliers alpha_S
on these with
   (Theta-cover)   sum_{S: e in delta_M(S)} alpha_S >= ell_e   for all e in M,
   (Theta-budget)  sum_S alpha_S Z_{b(S)} <= N.
Then sum_e ell_e y_e <= sum_S alpha_S sum_{e in delta_M(S)} y_e <= sum_S alpha_S Z_{b(S)} <= N. Because the
theta cuts have boundary <=3, this first case depends only on Z_1,Z_2,Z_3 (and the profile z at small levels).
[GPT's answer ENDS at specifying the certificate to construct -- it does NOT complete/prove it. Promising but
not a closure.]

## NEXT (my audit): test the QCD certificate numerically -- does exist a_S>=0 with h_a(e)=ell_e and
## sum a_S a_T min{b(S),b(T)} <= N^2, on C5[q] (tight, expect =N^2) + the theta witness c5paths20 + connected-B
## atoms? If yes (esp. equality at C5[q]), the quadratic-cut-pair route is validated. min{b,b} is a PSD kernel
## => convex QP. Then construct/verify the theta-cut multipliers alpha_S + profile z.
