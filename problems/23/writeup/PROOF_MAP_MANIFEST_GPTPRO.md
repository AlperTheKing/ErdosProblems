# Proof map + finite certificate manifest (GPT-Pro SIBLING, 2026-07-07)

DECODED-FAITHFUL transcription (letters-only decode; the exact LaTeX source stays in the SIBLING
thread — re-extract verbatim at paper-assembly time). This is the manuscript's "proof map" section:
theorem statement, GERSH program, the two row branches, and the full PROVEN/CERTIFIED/ROUTED manifest.

## Theorem
If G is a finite triangle-free graph on N vertices then beta(G) <= N^2/25, where
beta(G) = e(G) - maxcut(G). Equivalently, deleting at most N^2/25 edges makes G bipartite. In the
official formal-conjectures normalization, if |V(G)| <= n then the same result gives a bipartite
subgraph H <= G after deleting at most n^2 edges.

## The GERSH program
Fix a maximum cut B; M = bad edges, m = |M|. B chosen B-connected and Gamma-minimal among B-connected
maximum cuts. For a bad edge f: ell(f) = d_B(partial f) shortest-row length; cyc(f) = certified
shortest rows closing f. Rowwise target: ROWSUM(f) <= N + eta for f in M, eta = (N^2 - 25m)/25.
Row/Gamma aggregation theorem then gives Sum_{f in M} (ell(f)^2 - 25) <= 25 eta, hence
Gamma(B) = Sum ell(f)^2 = 25m + Sum(ell(f)^2 - 25) <= 25m + 25 eta = N^2. Since ell(f) >= 5 for every
bad edge, 25m <= Gamma(B) <= N^2. B a maximum cut => m = beta(G), therefore beta(G) <= N^2/25.

## The two row branches
- ell(f) = 5: Branch A proves C5-RS. For a length-5 row Q=(q0..q4) with loads s_i and active
  threshold tau = 5m/N, Branch A proves Sum_i (s_i - tau)_+ <= (1 + 25/N) eta; uniform-width net-DW'
  assembly gives I(Q) <= N + eta. Mask trichotomy:
    P = empty          => eta >= 0
    empty != P subsetneq Z/5Z  => six A1 proper mask cones
    P = Z/5Z           => ODL full-mask route tree
- ell(f) > 5: Branch B (Banked-UPO + cactus).

## Branch-A finite certificate manifest (PROVEN/CERTIFIED)
- route-tree correctness; terminal leaf providers CONE/Bank/Lens/NoOverfull : CERTIFIED (leaf ineqs)
- O14 EQ chart cover : CERTIFIED (108 chart rows, equality stratum, rung-2 charts)
- EQ-ODL1 divided-difference skips : CERTIFIED (P - P_bdry = F*band M, M>=0)
- EQ + sibling passive AM master cubes : CERTIFIED (BernsteinCube over 3x11 / 3x13)
- Sibling S7 : CERTIFIED (endpoint/residual-fiber finite gates)
- Seed3 + seven-cut quotient model : PROVEN/CERTIFIED (realization semantics + max-cut slacks)
- Terminal Hall/NCH route : CERTIFIED/ROUTED (T=1, T=2 terminal splitting)

## Bank0 internal certificates
- mass identity : PROVEN  Sum_v s(v) = 25m
- closure trace : CERTIFIED  (C1-C4 replay)
- owned corridor partition : CERTIFIED  nu0(U) = Sum_c nu0(c)
- CrossCap with a C5 fallback : CERTIFIED  N*sigma(S) <= nu0(c)

## Branch-B certificates
- PacketExchange : PROVEN  B_W(Q_res) <= eta
- cactus door-ownership wiring : CERTIFIED  Sum_C d_C <= d, each door counted once
- Banked-UPO : PROVEN  R_Q <= N + eta/2 - Sigma_L
- cactus input = strengthened peel invariant (SH'):  25 m_C <= r_C^2 + ... d_C, proved by the same
  two-orientation exchange calculus as PacketExchange. The BARE inequality m_C <= r_C^2/25 is FALSE
  and is NOT used. The d_C/2 credit is paid exactly once by the global PacketExchange term d/2 through
  the door-ownership wiring certificate.

## Checker soundness layer
All polynomial certificates consumed by proven checker-soundness theorems: Poly, PosCert, ConeCert,
CoeffCert, BernsteinSimplex, BernsteinCube. All graph/row/switch/completion/packet/corridor
certificates are literal finite data replayed by their named exact verifiers. Census and Gate-A runs
are VALIDATION ANNOTATIONS ONLY (not proof steps).

## Claude status note (2026-07-07)
Fully consistent with the compiled Lean skeleton (15 green increments) + the SH' resolution I gated
(Branch-B live risk dissolved). The ONE deepest still-open node is the GERSH aggregation's bank-reserve
residual (see LEAN_SOUNDNESS_AUDIT_GPTPRO.md): the manifest lists the aggregation as a theorem, but its
compiled-universal status hinges on the bank-reserve nonnegativity being a compiled Lean lemma vs
certified per-instance by the LRS artifact (task#16). MAIN answering (Q1 formula + Q2 compiled-vs-cert);
SIBLING cross-deriving the reserve independently.
