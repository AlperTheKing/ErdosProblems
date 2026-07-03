# SIB-AM Master-Cube Spec (GPT-Pro, 2026-07-04, main thread; full text in thread 6a450f06)

SIB SEED: graph6 I?`FAo]]? ; edges {04,06,15,16,17,19,26,29,37,38,39,47,48,49,58,68};
cut side 0001111000; bad doors M_SIB = {17,19,29}; C5 classes V0={1,2}, V1={5,6},
V2={0,8}, V3={3,4}, V4={7,9}; active row Q* = (1,6,8,4,9); all-ones: I(Q*) = 31/3,
N = 10, I-N = 1/3 (smaller excess than EQ's 2/3).

13 ROW TEMPLATES: door 17: (1,5,8,3,7),(1,5,8,4,7),(1,6,8,3,7),(1,6,8,4,7),(1,6,0,4,7);
door 19: same interiors ->9: (1,5,8,3,9),(1,5,8,4,9),(1,6,8,3,9),(1,6,8,4,9),(1,6,0,4,9);
door 29: (2,6,8,3,9),(2,6,8,4,9),(2,6,0,4,9). [2 connects only to 6.]

LAYERS: V1={5,6}, V2={0,8}, V3={3,4} attachments with pair variables mu_ab (left/right
pairs), attachment weight z, existence monomial chi(P) = mu_ab per attachment path.
Universal generator: D_g = Sigma_seed prod w_u + Sigma_att chi(P) z prod w_u;
N_{g,v} same rule with W_tau = z. Degree profile: mu <= 3, rho <= 4
(rho = z/(1+z) compactification as in EQ). Certificate: P_{tau,R} = P_0 + Sigma G_j P_j
+ eta-generator P_8, Bernstein in (mu, rho).
KEY STRUCTURE: V1 and V2 keep D_17 = D_19 COMMON after attachment (easier); V2
full-universal signature L={5,6}, R={3,4} is a TRUE TWIN of bag 8 = the SIB analogue of
EQ's tau_0 calibration class. **V3 = HARDEST layer**: attachments may connect 7 and 9
differently => D_17^{V3} /= D_19^{V3} in general => extra binding pressure expected.
FALLBACK ORDER if a master cube fails: V2 twin -> V1 -> V2 non-twin -> V3 two-path ->
V3 one-path (hardest).
DELIVERABLE: 3 layers x 13 seed row templates, programmatic construction (no
hand-expansion), binding rows evaluated at the SIB calibration point.
