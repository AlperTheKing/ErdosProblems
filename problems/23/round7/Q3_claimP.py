"""Q3 round 7 -- exact test of CLAIM P, the pentagon inequality behind Theorem Q3-1.

CLAIM P.  For every m in the 5-simplex,
        sum_{i in Z5} m_i m_{i+1}  +  (5/4) * min_i m_i m_{i+1}   <=   1/4 .

Equality at m = (1/5,...,1/5)  (1/5 + 1/20 = 1/4)  and at m = (1/2,1/2,0,0,0)  (1/4 + 0).
In integer form with m = k/K:   4*sum k_i k_{i+1} + 5*min_i k_i k_{i+1} <= K^2 .

The script checks this exhaustively on the rational grid of denominator K (exact integers) and
reports every violation together with the worst slack.
"""
import sys
from itertools import product


def test(K):
    worst = None
    viol = []
    for k0 in range(K + 1):
        for k1 in range(K + 1 - k0):
            for k2 in range(K + 1 - k0 - k1):
                for k3 in range(K + 1 - k0 - k1 - k2):
                    k4 = K - k0 - k1 - k2 - k3
                    k = (k0, k1, k2, k3, k4)
                    pr = [k[i] * k[(i + 1) % 5] for i in range(5)]
                    lhs = 4 * sum(pr) + 5 * min(pr)
                    slack = K * K - lhs
                    if worst is None or slack < worst[0]:
                        worst = (slack, k)
                    if slack < 0:
                        viol.append((slack, k))
    return worst, viol


if __name__ == '__main__':
    for K in [int(a) for a in sys.argv[1:]] or [40, 60]:
        worst, viol = test(K)
        print('K=%d  worst slack (K^2 - lhs) = %d at k=%s   violations: %d'
              % (K, worst[0], worst[1], len(viol)))
        for v in viol[:10]:
            print('   VIOLATION slack=%d k=%s' % v)
