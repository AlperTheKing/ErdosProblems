# Q34 to GPT Pro: k=5 moment cone SATURATES (no help beyond k=4); next step?

Sent via browser (chat 6a370bb0). Result reported:
- Added exact S5-reduced 5K1 cone (sanity vs P_sigma = 0; blocks 46,57,41,17,13,1 enforced ~1e-8).
- Full-band eta: k<=2 +4.3e-5 -> +4K1 +2.30e-5 (-2.0e-5) -> +4K1+5K1 +2.29e-5 (~-0.05e-5 only).
- MOMENT HIERARCHY SATURATED at ~+2.3e-5 > 0. Empirically = Q33 option (2): the residual is the
  P2 cut-relaxation floor (profile-cut <=2^k-DOF root-symmetric; profile-deficit 0.089 vs true maxcut 0.0156).

Asked: (a) k=6 or done? (b) if done: (i) tighten the CUT side at order 9 (non-profile/per-vertex/SDP
maxcut on the cut variable) OR (ii) exact-certify d_mono <= 2/25 + ~3e-5 + analytic stability (single
weakest stability inequality that closes the band given that upper bound)?
