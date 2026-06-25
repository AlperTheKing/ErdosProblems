# GPT (chat 6a3b5aba): REFUTES the geodesic/QFC25 congestion route; correct target = PCF25 (max-throughput)

## My geodesic-congestion reduction is FALSE (2 counterexamples)
1. THETA example: B = two internally disjoint u-v paths of length 4 and 6, M={uv}, tri-free, d_B=4.
   Unrestricted: split unit demand over both paths => rho = 1/2 (cut at u has 2 edges). Unique geodesic is
   the length-4 path => rho_geo = 1. So rho_geo > rho. "No stretch at one optimum" does NOT give rho=rho_geo.
2. DILUTION J_t: H = the K23-N13 gadget (rho=rho_geo=4/3, m=4, N=13). C = C5[t] (rho_geo=1, m=t^2, N=5t).
   Join H,C by ONE bridge edge crossing both cuts (no demand path can use it). Then N=5t+13, m=t^2+4,
   union cut maximum, rho_geo(J_t) = max(4/3,1) = 4/3. At t=16: N=93, m=260, bound=N^2/(25m)=8649/6500=1.3306
   < 4/3 = rho_geo. So rho_geo > bound: QFC25 is FALSE. Also Gamma=sum_M(d_B+1)^2=25m=6500, and
   rho_geo*Gamma=(4/3)*6500=8666.7 > 8649=N^2, so "rho_geo*Gamma<=N^2" is ALSO FALSE.
REASON: Gamma and m are ADDITIVE across separated regions, but max congestion is a LOCAL maximum. A large
C5[t] block drives N^2/(25m)->1 but does not reduce the fixed 4/3 congestion inside H. (My own uniform-
geodesic sweep independently found 4 violations at N=8,9: e.g. N=8 m=2 uniform maxload 1.5 > bound 1.28.)
=> the entire congestion / single-routing / QFC25 / MT25 reduction is DEAD. Restricting to geodesics is
unjustified (theta example).

## CORRECT REPLACEMENT: PCF25 (nonuniform, prize-collecting throughput)
mu(B,M) := max  sum_{e in M} sum_{P in P_e} f_{e,P}   (route a FRACTION f_e<=1 of each bad-edge demand over
simple B-paths, subject to unit capacity on each B-edge; NOT equal-rate). Each routed path P of demand e
gives an odd cycle e∪P with exactly one M-edge => mu-multiflow is a fractional odd-cycle packing of value mu,
so nu* >= mu. TARGET:
        PCF25:   mu(B,M) >= 25 m^2 / N^2 .
Then nu*(G) >= 25 tau^2/N^2  =>  tau <= (N/5) sqrt(nu*)  =>  (with unconditional nu*<=N^2/25)  tau<=N^2/25.
SURVIVES J_16: route all 256 demands inside C5[16], ignore H => mu >= 256 > 25*260^2/93^2 = 195.4. Uniform
concurrent flow failed only because it forced congested H-commodities to the same rate as C5-commodities.

## Exact finite dual (the next target)
mu(B,M) = min_{ell>=0} [ sum_{b in B} ell_b + sum_{uv in M} (1 - d^B_ell(u,v))_+ ].
For formalization WLOG 0 <= ell_b <= 1 (capping at 1 cannot increase the dual: a commodity with distance <1
uses no edge longer than 1; with distance >=1 the truncated penalty stays 0). So the surviving elementary
problem is TMT25 / PCF25: construct a nonuniform unit-capacity multiflow of total value 25m^2/N^2, OR prove
the dual inequality  sum_B ell_b + sum_M (1 - d^B_ell(u,v))_+ >= 25 m^2/N^2  for all ell:B->[0,1].
NO geodesic restriction, NO Guenin/Lehman. Targets (T') directly.
