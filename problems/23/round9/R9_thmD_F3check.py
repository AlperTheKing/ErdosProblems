"""Direct randomised check of the pure-algebra step (F3) of Theorem F:

   z_0..z_4 >= 0 with sum z = 1-rho ;  K_0..K_4 >= 0 with 25*sum K_i <= 1-(1-rho)^10
   ==>  min_i ( z_i z_{i+1} + K_i )  <=  1/25 .

Exact rational arithmetic; adversarial choices of z (extreme, balanced, degenerate) and of
the distribution of the K-budget (all in one cut, in two cuts, uniform).
"""
import random
from fractions import Fraction as Fr

def test(rho, z, K):
    return min(z[i] * z[(i + 1) % 5] + K[i] for i in range(5)) <= Fr(1, 25)

if __name__ == '__main__':
    rnd = random.Random(20260726)
    bad = []
    N = 0
    for trial in range(200000):
        rho = Fr(rnd.randrange(0, 400), 1000)
        S = 1 - rho
        # z: random composition of S, sometimes exactly balanced, sometimes degenerate
        mode = trial % 4
        if mode == 0:
            z = [S / 5] * 5
        elif mode == 1:
            w = [rnd.randrange(0, 50) for _ in range(5)]
            if sum(w) == 0:
                continue
            z = [S * Fr(t, sum(w)) for t in w]
        elif mode == 2:
            w = [rnd.randrange(0, 3) for _ in range(5)]      # many zeros
            if sum(w) == 0:
                continue
            z = [S * Fr(t, sum(w)) for t in w]
        else:
            z = [S / 5 + Fr(rnd.randrange(-40, 41), 10000) for _ in range(4)]
            z.append(S - sum(z))
            if min(z) < 0:
                continue
        budget = (1 - (1 - rho) ** 10) / 25
        if budget < 0:
            continue
        sub = trial % 3
        if sub == 0:                                   # all budget in the worst cut
            j = min(range(5), key=lambda i: z[i] * z[(i + 1) % 5])
            K = [Fr(0)] * 5
            K[j] = budget
        elif sub == 1:                                 # split over the two cheapest cuts
            order = sorted(range(5), key=lambda i: z[i] * z[(i + 1) % 5])
            K = [Fr(0)] * 5
            K[order[0]] = budget / 2
            K[order[1]] = budget / 2
        else:                                          # random split
            w = [rnd.randrange(0, 10) for _ in range(5)]
            if sum(w) == 0:
                continue
            K = [budget * Fr(t, sum(w)) for t in w]
        assert 25 * sum(K) <= 1 - (1 - rho) ** 10
        N += 1
        if not test(rho, z, K):
            bad.append((rho, z, K))
            if len(bad) > 3:
                break
    print("(F3) exact random check: %d admissible (rho, z, K) triples, %d failures" % (N, len(bad)))
    for b in bad:
        print("   FAIL", b)
    # the extremal witness: budget concentrated, z balanced  -> equality case
    rho = Fr(0)
    z = [Fr(1, 5)] * 5
    K = [Fr(0)] * 5
    print("   equality case rho=0, z balanced, K=0 : min_i = %s (= 1/25)"
          % min(z[i] * z[(i + 1) % 5] + K[i] for i in range(5)))
