# SIB S7: Compactified FJ -> Endpoint-Fiber -> y=1 Six-Face Reduction (GPT-Pro, 2026-07-03)

Thread: sibling 6a45e152 ("Sibling Seed Proof Path"). Three replies, all exact-gated by
_claude_s7_y1_face_gate.py (ALL-PASS: identities I1/I3/I4/I5/I8, B=Y+eT, floor 95,
400 feasible Dx/Dq probes).

## Setup (S7 atom, old variables)
Variables a,b,c,d,e,f,x,y,u,v >= 1; m = xu+xv+yv; N = sum; Y = ac+bf+cf; Z = eY+df(b+c);
A = bd+cd+df+ac+ae+bf+be+cf+ce+ef; B = ac+ae+bf+be+cf+ce+ef (= Y + e(a+b+c+f));
S = a+b+c+d+e+f. Slacks: s1 = e-v, s2 = d+e-u-v, s3 = b+c-x-y, s4 = Y-m,
s5 = ae+bf+cf-m, s6 = ac+df+ef-m, s7 = ae+df+ef-m (all >= 0).
Target: Phi = 2(N^2-25m) - 75( x(u+v)A/Z + yvB/(eY) - S ) >= 0.

## Reply 1: compactified Fritz-John face certificate (superseded by reply 2's reduction)
Normalize sum = 1, theta = 1/N_old, variables >= theta >= 0; compact numerator
P = 2eYZ(1-25m) - 75 theta ( eY x(u+v)A + Z yvB - eYZ S ); for finite old points
P = eYZ theta^2 Phi. K compact => negative min exists if S7 false; FJ + conic
Caratheodory on the 10-dim tangent space => at most 11 active inequalities;
strict negativity encoded algebraically by P r^2 + 1 = 0. Raw count: active sets
<= 11 of 18 inequalities = 230,964 systems (too many => reply 2).
Central component (all-seven-tight): b=d=f=u=y=1, c=e=x=v=t, a = t+1-1/t;
Phi(t) = t^2(t+2)(t^3+2t^2+t+1)/P0(t) form, Sturm-positive (already closed).

## STATUS (prior exact progress, mine/Codex)
- theta = 0 projective boundary CLOSED: with A0=a+f, B0=b+c, D0=d+e, P0=x+y, Q0=u+v:
  m <= P0Q0, m <= A0B0, m <= A0D0, P0 <= B0, Q0 <= D0 => total >= 5 sqrt(m) => m <= 1/25
  (overlapping 5-block AM-GM, same shape as CERT-1).
- Central seven-tight curve Sturm-positive.
- Coefficient cones FAILED through degree 3 (y=1 face: degree 5) - do not retry.

## Reply 2: ENDPOINT-FIBER LEMMA (kills the 230,964 enumeration -> 14 faces)
P is linear in theta; freeze (a,...,f, p=x+y, q=u+v, theta): with rho=A/Z, sigma=B/(eY),
P/(eYZ) = C + K yu - H y where K = 50+75sigma > 0 => strictly increasing in u =>
fiber min at u = max(L, R/y); both branches linear in y => min at interval endpoint
or kink. FOURTEEN faces: y=theta, x=theta, or s_j=0 (j in {4,5,6,7}) with each of
{u=theta, v=theta, e-v=0(kink)}. 2 + 3*4 = 14 exact real-emptiness gates
(with P r^2 + 1 = 0 for strict negativity).

## Reply 3: y=1 FACE -> SIX GATES (Lemmas 1+2, PROVEN; identities exact-gated)
On y=1 (old variables), u = q-v: m = xq+v, N = S+1+x+q;
Phi = 2N^2 + 75S - C_A xq - C_B v, C_A = 50+75A/Z, C_B = 50+75B/(eY).   (1) [I1 PASS]
Cleared derivatives: R_x = Z dPhi/dx = 4ZN - q(50Z+75A)                 (3) [I3 PASS]
                     R_q = Z dPhi/dq = 4ZN - x(50Z+75A)                 (4) [I4 PASS]
LEMMA 1 (endpoint-derivative exclusion): on K_{y=1}, R_x >= 0 => Phi > 0 (Dx);
R_q >= 0 => Phi > 0 (Dq). Proof: Xi = eYZ Phi = eY x R_x + Z L_x,
L_x = eY(2N(N-2x)+75S) - (50eY+75B)v  (5) [I5 PASS]; similarly with q (8) [I8 PASS].
Bounds: B = Y+eT (T=a+b+c+f) => C_B v = 50v + 75 v/e + 75 vT/Y <= 50D+75+75T
(v<=e<=D=d+e, v<=m<=Y). For Dq: q <= D (s2), x <= b+c-1 (s3), so
2N(N-2q)+75S-C_B v >= 2(T+D+q+2)(T+2)+25D-75 >= 2*10*6+50-75 = 95 > 0
(T>=4, D>=2, q>=2) [floor PASS]. Dx analogous with N-2x >= a+d+e+f+q+2.
LEMMA 2 (exact three-step descent; at a negative point R_x<0, R_q<0 by Lemma 1):
Step A: x up (a..f,q,v fixed; m linear up) -> blocker s3=0 or s_j=0 (j=4..7);
  cannot stall at R_x=0 (Lemma 1 again since Phi stays < 0 while decreasing).
Step B: q up (v fixed, u=q-v up; s1,s3 unaffected) -> blocker s2=0 or s_j=0.
Step C: v up at fixed q (u=q-v down; dPhi/dv|_q = -C_B < 0) -> blocker u=1, s1=0,
  or s_j=0 (s2 fixed since q fixed).
RESULT - y=1 face proved once SIX systems are empty (Xi = eYZ Phi, r auxiliary,
Xi r^2 + 1 = 0 encodes Phi < 0):
  G1-G4: K_{y=1} AND s_j = 0 AND Xi r^2 + 1 = 0,  j = 4,5,6,7
  G5:    K_{y=1} AND s1 = s2 = s3 = 0 AND Xi r^2 + 1 = 0
  G6:    K_{y=1} AND u = 1 AND s2 = s3 = 0 AND Xi r^2 + 1 = 0
(K_{y=1}: y=1, all variables >= 1, s1..s7 >= 0.)

## REMAINING S7 PROGRAM (after these六 gates)
1. Script G1-G6 (Codex): real-emptiness per face - resultant/Groebner + Sturm on
   parametrized curves, or per-face positivity of Xi on the face (exact rational).
2. x=1 endpoint face: symmetric treatment (expect an analogous six-gate reduction;
   ask GPT-Pro if not symmetric).
3. The 12 capacity-endpoint compact faces from reply 2 (s_j=0 with u/v/kink at
   theta-level) - check whether the y=1/x=1 old-variable reductions + theta=0 closure
   already cover them (the 14-face statement was at compact level; y=theta face in old
   variables IS y=1 after un-normalizing theta=1/N... VERIFY this correspondence).
4. Assemble: theta=0 closed + 14-face covering + per-face emptiness => S7 proven.

## REPLY 4 (2026-07-03): x=1 SIX GATES + COVERAGE => S7 = 24 EMPTINESS GATES TOTAL
Exact-gated by _claude_s7_x1_face_gate.py (ALL-PASS: X1/Ry/Rv/I1/ID_case1/FL floor +
400-probe RB & XDy). On x=1 (u=q-v): m=q+yv, N=S+1+y+q, Phi = 2N^2+75S - C_A q - C_B yv.
R_y = eY dPhi/dy = 4eYN - v(50eY+75B); dPhi/dv|_q = -C_B y < 0 (no q-derivative needed).
(X-Dy): feasible & R_y>=0 => Phi>0, via Xi = ZyR_y + eY[Z(2N(N-2y)+75S) - q(50Z+75A)] and
RATIO BOUND C_A q <= 125D+75T (F = fRT+YH > 0, H=fR-R-f, case split D<=Y / D>Y with
identity (D+T)Z-DA = DY(e-1)+eT(Y-D)+d(fR(D+T)-D(R+f))); floor L_y >= 2(D+8)(D+6)-50D =
2(D-11/2)^2+71/2 > 0 (T>=4, q>=2, y<=b+c-1). Descent: Step1 y-up (blockers s3, s_j);
Step2 v-up fixed q (blockers u=1, s1, s_j). SIX x=1 GATES:
  K,x=1,s_j=0,Xi r^2+1=0 (j=4..7); K,x=1,s3=0,u=1; K,x=1,s3=0,s1=0.
COVERAGE (B): compact->old exact unnormalization (z^c = theta z^old; s_j homogeneous;
e-v=0 <=> s1=0): y=theta -> y=1, x=theta -> x=1, and the 12 capacity-endpoint faces ->
K, s_j=0, {u=1 | v=1 | s1=0}, j=4..7 (endpoint faces do NOT absorb them: u=1/v=1/e=v do
not force x=1 or y=1). FINAL S7 ASSEMBLY: theta=0 closed + central Sturm + y=1 (6 gates) +
x=1 (6 gates) + 12 residual gates = 24 real-emptiness checks TOTAL => S7 PROVEN.

## REPLY 5 (2026-07-03): TWELVE RESIDUAL FACES -> 12 STAT + 12 COR PROJECTED GATES
Residual-fiber convexity reduction, per face (j in {4..7}) x (E in {s1=0, u=1, v=1}):
FIBER: fix a..f,u,v (+E); on s_j=0: m = M_j (M_j is a..f-only), xq+yv = M_j, so
x(y) = (M_j - vy)/q, N(y) = N_0 + lambda y (lambda = 1 - v/q > 0); Phi(y) = quadratic in y,
POSITIVE leading coeff 2 lambda^2. Along the fiber: s_k = M_k - M_j constant (k /= j),
s1/s2 constant (u,v fixed), lower bounds fixed EXCEPT x,y; s3 = R - x - y varies.
=> negative minimum on the face sits at: y-window endpoint (x=1 or y=1 faces — ALREADY
CLOSED) OR the s3=0 corner OR the interior stationary point y*.
GATES per face (script derives Phi*, y*, window U symbolically, cleared by q e Y Z > 0;
strict negativity num(8 q^2 Phi*) r^2 + 1 = 0):
  STAT(j,E): projected constraints AND 1 < y* < U_{j,E} AND Phi* < 0 — empty.
  COR(j,E):  s3=0 corner, x = (M_j - vR)/u, y = (qR - M_j)/u (per-E specialization:
    s1=0: v=e, q=u+e; u=1: q=1+v, x = M_j - vR, y = (1+v)R - M_j; v=1: q=u+1),
    x,y >= 1 as constraints — empty.
Endpoint-projected constraint sets per E: s1=0: {vars>=1, d-u>=0, M_k>=M_j};
u=1: {v>=1, e-v>=0, d+e-1-v>=0, M_k>=M_j}; v=1: {u>=1, d+e-u-1>=0, M_k>=M_j; s1 auto}.
S7 TOTAL now: theta=0 + central Sturm + y=1 six + x=1 six + 12 STAT + 12 COR = 36 gates,
all <= 7 effective variables after projection/elimination. Codex: derive the quadratic-min
formulas in-script (do NOT transcribe from prose), verify fiber-invariance claims
symbolically as preflight, then run emptiness.
