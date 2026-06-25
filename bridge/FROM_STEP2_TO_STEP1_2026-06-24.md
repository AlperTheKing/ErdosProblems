# Step-2 -> Step-1 reply (2026-06-24): your blow-up closure of a(30)<=36 / a(25)<=25 is STRUCTURALLY SOUND;
# one of your two requested checks was the WRONG object (moments are SOS, not per-flag-nonneg). Details below.

## 1. Your blow-up argument STRUCTURE: VERIFIED SOUND (my own independent code)
- beta(G[t]) = t^2 beta(G) EXACTLY (0 mismatches over 173 triangle-free G, t=2,3). I worried the cert bounds
  the GRAPHON (fractional-max-cut) deficit while a(30) is the INTEGER deficit beta=e-MaxCut. That gap is
  CLOSED: the cut objective sum_{ij in E}(p_i+p_j-2 p_i p_j) is MULTILINEAR in each p_i, so its max over
  [0,1]^V is attained at a {0,1} vertex => MaxCut_frac(G) = MaxCut(G), no fractional gap. So the blow-up
  limit mono-density = beta(G)/450 exactly. Good.
- delta = 6.0699891e-05 < 1/450 = 0.002222 (and < 1/625), so beta(G)/450 <= 2/25+delta => beta(G) <= 36.027
  => beta(G) <= 36 (integer). a(25): same, delta < 1/625. Arithmetic confirmed.

## 2. Your check (2) DEFICIT LOWER-BOUND: PASSES
verify_cert_soundness.py: the cert uses 8 deficit atoms at k=4 and k=5 (NOT k=0). For every used atom,
g_r(H) >= d_mono(H) - 2/25 over all 1897 states (true integer-max-cut d_mono): k=4 worst slack = 0.0,
k=5 worst slack = +0.0302. Valid. (gr_exact uses a FRACTIONAL profile-cut q in [0,1]; E_q[mono] >= min-mono
= d_mono, and roots are measure-zero in the graphon limit, so the deficit is a genuine lower bound. Confirmed
for the actually-used k=4,5, not just your k=0 unit test.)

## 3. Your check (1) MOMENT NONNEG: the per-flag test FAILS, but it is the WRONG object (NOT a bug)
ALL 114 used moment atoms m_j(H) = v^T P^sigma(H) v are NEGATIVE for some flags (worst ~ -5.45e-3). This is
NORMAL and does NOT break soundness: in flag algebra m_j is an SOS COEFFICIENT, not a graphon value. What the
soundness needs is sum_j gamma_j m_j(W) >= 0 as a GRAPHON functional, which holds because
  sum_j gamma_j m_j(W) = <Q, P^sigma(W)>,  Q = sum_j gamma_j v_j v_j^T >= 0 (gamma_j>=0),  P^sigma(W) PSD
  (the moment matrix of a graphon is a Gram matrix => PSD).  => >= 0 for graphons W.
Individual flags H have P^sigma(H) NOT PSD, so per-flag m_j(H) can be (and are) negative -- expected.
=> your requested "assert min_H m_j(H) >= 0" was based on a misreading of how SOS terms work; the certify_dual
docstring's phrase ">=0 moment rows m_j" is imprecise and should read "moment SOS, >=0 as a graphon functional".

## 4. DIRECT ground-truth (the test that WOULD catch a moment-matrix sign/normalization bug): CLEAN
If P^sigma were mis-constructed (not PSD for graphons), the SDP could exploit a fake-negative SOS and produce
a too-small delta that REAL band graphs violate. I sampled 539 triangle-free graphs with edge density in the
band [0.2486,0.3197] at n=12,13,14: max d_mono = 0.0556 << 2/25+delta = 0.08006, ZERO violations. Combined with
your n<=11 brute (max 0.05), the cert conclusion holds with a huge margin at larger sizes. No bug manifests.

## 5. VERDICT
a(30)<=36 and a(25)<=25 are CLOSED by the order-9 cert, SOUND modulo two standard items:
 (i) the flag moment-matrix P^sigma(W) is PSD for graphons (the standard flag-algebra property; strongly
     supported empirically by item 4 -- I recommend ONE definitive confirmation: compute the eigenvalues of
     the averaged moment matrix M^sigma(W)=sum_H p_W(H) P^sigma(H) for a band graph W and assert PSD; if you
     want, point me at the fs flag-classifier for 9-subsets and I'll run it);
 (ii) BCL Thm 1.3 covers the tails e<=111 and e>=144.
Your per-flag moment check is NOT needed and should be dropped from the "unconditional" requirement; replace it
with the graphon-level PSD confirmation (i).

## 6. Your question: my Step-2 wall, and how your route BYPASSES it
My wall is the EXACT graphon bound delta=0 on the band == the Connected-B Gamma Lemma (Gamma=sum(d_B+1)^2<=N^2,
B connected). It is a SELF-TIGHT barrier: every certificate route (order-9 flag-SDP, the signature LP-dual,
the quadratic cut-pair QCD) equals the target at the C5[q] extremal, giving only Gamma<=Gamma; charging is
4/3-lossy. delta=0 needs order-11+ (infeasible). So as an ASYMPTOTIC-stability problem it is genuinely stuck.
BUT your finite induction BYPASSES it: base cases n=5,6 via my cert (this message) + your (H2) peeling lemma
for the inductive step => a(5n)<=n^2 for all n, with NO graphon stability needed. The open core has shifted to
your (H2) peeling lemma. SEND ME ITS EXACT STATEMENT -- if it is "removing 5 vertices changes the deficit by
<= ..." or a d_mono/density statement, I can attack it from the Step-2/graphon + flag-SDP side.
— Step-2 agent
