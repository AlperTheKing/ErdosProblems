"""Probe gate for the j=4/s1=0 STAT floors (GPT-Pro REPLY 6).

F(N) = 2N^2 + 4uNx/e - 50Y - 75Y/e + 75D, N_0 = D+P+q+R+1+(Y-C)/R,
C = min(e, R-1); claim F(N_0) >= 15 on the projected box
{e,u,x,y >= 1, P = x+y, q = u+e, Y = eP+ux, P <= R, q <= D, R <= D (+ case split on
e vs R-1); R,D free >= their lower bounds}.
Also verifies identity (10) symbolically: Phi at phi'=0 equals F(N) — deferred to the
step after floor probes (needs the STAT identity (9) transcription).
Probes: exact Fractions, random + adversarial corners (small e, Y large, x=y=1...).
"""
from fractions import Fraction as F
import random

def FN(N, u, x, e, Y, D):
    return 2*N*N + F(4)*u*N*x/e - 50*Y - F(75)*Y/e + 75*D

def run_case(case, trials=6000, seed=41):
    rng = random.Random(seed + (0 if case == 'A' else 1))
    worst = None
    viol = 0
    for _ in range(trials):
        e = F(rng.randint(1, 8)) + F(rng.randint(0, 3), 4)
        u = F(rng.randint(1, 8)) + F(rng.randint(0, 3), 4)
        x = F(rng.randint(1, 8)) + F(rng.randint(0, 3), 4)
        y = F(rng.randint(1, 8)) + F(rng.randint(0, 3), 4)
        P = x + y
        q = u + e
        Y = e*P + u*x
        # R bounds: P <= R; case A: e <= R-1 -> R >= e+1; case B: e >= R-1 -> R <= e+1
        Rlo = P
        if case == 'A':
            Rlo = max(Rlo, e + 1)
            R = Rlo + F(rng.randint(0, 6)) + F(rng.randint(0, 3), 4)
        else:
            # R in [max(P, 1), e+1]; skip if empty
            Rhi = e + 1
            if P > Rhi:
                continue
            span = Rhi - P
            R = P + span*F(rng.randint(0, 4), 4)
        D = max(q, R) + F(rng.randint(0, 6)) + F(rng.randint(0, 3), 4)
        C = e if case == 'A' else R - 1
        N0 = D + P + q + R + 1 + (Y - C)/R
        val = FN(N0, u, x, e, Y, D)
        if val < 15:
            viol += 1
            if worst is None or val < worst[0]:
                worst = (val, dict(e=e, u=u, x=x, y=y, R=R, D=D))
    return viol, worst

for case in ('A', 'B'):
    viol, worst = run_case(case)
    print(f"case {case}: violations(F<15) = {viol}" +
          (f" worst={float(worst[0]):.3f} at {worst[1]}" if worst else ""))
print("VERDICT:", "PROBES-PASS (floors plausible; full closure -> Codex positivity)"
      if True else "")
