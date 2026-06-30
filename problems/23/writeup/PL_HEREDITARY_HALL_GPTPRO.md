# [REFUTED 2026-06-30] GPT-Pro: the hereditary paid-leakage inequality (PL) -> Hall -> #23

**STATUS: REFUTED.** (PL) beta(D)>=mu(D) is FALSE (independent _pl_gate.py + hand-verify): H?AFBo] N9 side 111110000,
v=1, switch S={0,1,5,6}, subdiagram D={(5,8),(1,7),(2,6)}: U_D={0,1,5,6}, beta=0 < mu=1 (the other bad edge (6,8) crosses
U_D with no compensating blue leak). 27 failures census N9/10. Internally inconsistent: GPT-Pro's injection proves beta<=mu
(opposite of the stated beta>=mu), and beta<=mu gives |L_D|<=|R_D|, the WRONG direction for Hall-on-bdyB. The Hall lemma is
TRUE (validated; here literally K_{2,2}) but this proof is wrong. Kept only as a documented dead route. ---


Source: GPT-Pro chat 6a436806, 2026-06-30. Candidate PROOF of the sole open lemma (the Hall/SDR condition
on the terminal-shadow witness graph). MUST be exact-verified (gate (PL)) + rigor-checked before trusting.

## Setup
For a neutral switch S, the witness bipartite graph W:
  L = crossM(S) (bad edges with one endpoint in S),  R = bdyB(S) (blue/cut edges with one endpoint in S),
  f -- e  iff  bad edge f WITNESSES blue edge e (some shortest f-geodesic, oriented from f's endpoint inside S,
  has S as a terminal prefix and EXITS S through e).  lambda(e) = min over f witnessing e of ell(f).
PROVEN: flipping neutral terminal-shadow-valid S changes Gamma by -Psi(S), Psi = sum_{crossM} ell^2 - sum_{bdyB} lambda^2.
Psi(S) > 0  <=>  the witness graph has an SDR saturating bdyB (Hall) with one strict (length-domination is FREE since
lambda(e) = min witness length).

## Why component-balance is NOT enough (GPT-Pro)
A balanced connected bipartite graph can fail Hall: L={a,b,c}, R={1,2,3}, edges a1,a2,a3,b3,c3 -- connected, balanced,
but {1,2} has only neighbour a, no matching saturating R. So Codex's component identity (delta_M(U_C)=Y_C, delta_B(U_C)=X_C
=> balance |X_C|=|Y_C|) does NOT close Hall. The missing input is HEREDITARY.

## The exact Hall lemma (PL) -- hereditary paid leakage
For a connected subgraph D of W (NOT just a full component), L_D = crossM in D, R_D = bdyB in D, and
  U_D := union over (f,e) in E(D) of { terminal prefix inside S of a shortest f-geodesic exiting through e }.
Then U_D subset S; every f in L_D crosses U_D and every e in R_D crosses U_D. Define
  beta(D) := | delta_B(U_D) \ R_D |   (blue leak),   mu(D) := | delta_M(U_D) \ L_D |   (bad leak).
**(PL):  beta(D) >= mu(D)  for every connected witness subdiagram D.**
Equivalently | delta_B(U_D) | - | delta_M(U_D) | >= | R_D | - | L_D |. (For a whole component the verified identity gives
beta(C)=mu(C)=0; (PL) is the hereditary strengthening.) GPT-Pro: "once (PL) is proved, Hall follows in three lines."

## Proof of (PL) -- odd-girth shortest-path injection (GPT-Pro)
Construct an INJECTION blue-leak -> bad-leak. For each blue leak (a blue edge in delta_B(U_D) not in R_D): the geodesic
witnessing it -- the closing odd cycle of the relevant bad edge g -- must contain a bad edge crossing U_D that is NOT one
of the declared L_D bad edges (i.e. a bad leak). Otherwise one of three forbidden configurations arises:
  (i) a geodesic witnessing an edge of R_D from a bad edge OUTSIDE L_D -- contradicts D being a connected component;
  (ii) a strictly shorter odd cycle -- contradicts the definition (shortestness) of ell(g);
  (iii) an odd cycle of length 3 -- contradicts triangle-freeness.
So assign the blue leak to the first such bad leak. INJECTIVITY: theta-graph argument -- if two distinct blue leaks were
assigned to the same bad leak, the two terminal-prefix detours + the common bad closing edge form a theta graph with two
different blue routes between the same parity classes; one resulting odd cycle is shorter than the relevant ell(g),
contradicting shortestness. Hence beta(D) >= mu(D). QED(PL).

Mechanism in one line: a blue leak WITHOUT a new bad leak creates a forbidden shorter odd cycle (odd-girth >= 5) or triangle.

## (PL) => Hall (three lines)
If Y subset bdyB were Hall-deficient (its witness neighbourhood N(Y) in crossM has |N(Y)|<|Y|), take D = the connected
witness subdiagram on Y u N(Y); then R_D=Y, L_D=N(Y), |R_D|>|L_D|, so (PL) forces |delta_B(U_D)|-|delta_M(U_D)| >= |R_D|-|L_D| > 0,
but max-cut neutrality bounds it -- contradiction. [exact form to be verified] => Hall holds => SDR => Psi(S)>0 => contradiction
with gamma-min => R[v]>=0 => rho(K2)<=N => Gamma<=N^2 => #23.

## STATUS: CANDIDATE PROOF -- must exact-gate (PL) on the R<0 domain (H?AFBo] family) + rigor-check the injection + the
## (PL)=>Hall step. GPT-Pro has produced plausible-but-wrong proofs before (harmonic-shadow bridge, level-set). Verify.
