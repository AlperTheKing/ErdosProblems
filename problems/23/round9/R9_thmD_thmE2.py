"""TASK 2 (step 4, CORRECTED) -- the blow-up master inequality, its correct
corollaries, the deficiency refinement, and the exact residual.

MASTER INEQUALITY (Theorem E, no hypotheses at all -- not even triangle-freeness).
Let V(H) = A_0 u ... u A_4 be ANY partition, y_m = x(A_m).  For i in Z_5 put
    BAD_i = weight of edges inside a class
          + weight of edges between classes at distance 2 whose centre is not i, i+1.
Then           psi(H,x)  <=  min_i ( y_i y_{i+1} + BAD_i ).
[cut i = classes {i,i+1,i+3} versus {i+2,i+4}.]

CORRECT COROLLARY:  BAD_i = 0 for EVERY i  (equivalently: every edge joins
consecutive classes, i.e. the partition is a homomorphism H -> C5)  ==>  psi <= 1/25.

The tempting corollary "BAD_i = 0 for SOME i ==> psi <= 1/25" is FALSE: it needs
min_{i in I_0} y_i y_{i+1} <= 1/25, and for I_0 of size 4 the weight
y = (1/6,1/4,1/6,1/4,1/6) gives min = 1/24 > 1/25.  (checked below)

DEFICIENCY REFINEMENT (uses triangle-freeness).  If the classes come from a
COMPLETE induced C5-blow-up B with W-vertices attached (m(v) legal), then with
   alpha_v = y_{m-1} - x(N(v) cap V_{m-1}),  beta_v = y_{m+1} - x(N(v) cap V_{m+1}),
   D_i = sum_{v in W_i} x_v beta_v  +  sum_{v in W_{i+1}} x_v alpha_v  >= 0,
one has        psi <= min_i ( yhat_i yhat_{i+1} - D_i + BAD_i ),
and triangle-freeness forces, for every BAD edge uv,
   uv inside W_m      :  alpha_u+alpha_v >= y_{m-1}  and  beta_u+beta_v >= y_{m+1},
   uv from W_m to W_{m+2} :  beta_u + alpha_v >= y_{m+1}.
So a bad edge always CREATES deficiency -- but only in the 2 cuts i in {m-1,m},
while it COSTS in 3 (distance 2) or 5 (distance 0) cuts.  That mismatch is the block.
"""
import itertools, random
from fractions import Fraction as Fr
import R9_thmD_lib as L
import R9_thmD_coverage as CV

FAIL = []


def part_bound(G, a, cls_of):
    """master inequality for an arbitrary 5-partition cls_of : vertex -> class.
    returns (min_i (y_i y_{i+1} + BAD_i), per-cut list, y)."""
    n, adj = G
    y = [0] * 5
    for v in range(n):
        y[cls_of[v]] += a[v]
    per = []
    for i in range(5):
        B = 0
        for u in range(n):
            for v in adj[u]:
                if v <= u:
                    continue
                du, dv = cls_of[u], cls_of[v]
                d = (du - dv) % 5
                if d == 0:
                    B += a[u] * a[v]
                elif d in (2, 3):
                    centre = (dv + 1) % 5 if d == 2 else (du + 1) % 5
                    if centre != i and centre != (i + 1) % 5:
                        B += a[u] * a[v]
        per.append(y[i] * y[(i + 1) % 5] + B)
    return min(per), per, y


def cut_weight(G, a, cls_of, i):
    n, adj = G
    side = {v: (0 if (cls_of[v] - i) % 5 in (0, 1, 3) else 1) for v in range(n)}
    return sum(a[u] * a[v] for u in range(n) for v in adj[u]
               if u < v and side[u] == side[v])


def hom_to_C5(G):
    """is there a partition with ALL edges between consecutive classes?  (H -> C5)"""
    n, adj = G
    asg = {}

    def bt(v):
        if v == n:
            return True
        for m in range(5):
            if all(((asg[u] - m) % 5) in (1, 4) for u in adj[v] if u in asg):
                asg[v] = m
                if bt(v + 1):
                    return True
                del asg[v]
        return False
    return dict(asg) if bt(0) else None


def rand_weights(n, q, k, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(k):
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        out.append(a)
    return out


if __name__ == '__main__':
    N = L.named_graphs()
    N['And(6)=G17'] = L.andrasfai(6)
    print("=" * 78)
    print("R. MASTER INEQUALITY: exact check psi <= min_i (y_i y_{i+1} + BAD_i)")
    print("   over RANDOM 5-partitions of random graphs (no hypotheses needed)")
    print("=" * 78)
    rnd = random.Random(5)
    bad = tot = 0
    import R9_thmD_adversarial as A
    for t in range(300):
        n = rnd.randint(5, 9)
        G = A.rand_trianglefree(n, t * 31 + 7, dens=rnd.random())
        if rnd.random() < .3:                     # also NON triangle-free graphs
            e = L.edges_of(G) + [(rnd.randrange(n), rnd.randrange(n))]
            e = [(u, v) for u, v in e if u != v]
            G = L.mkgraph(n, e)
        cls_of = {v: rnd.randrange(5) for v in range(n)}
        for a in rand_weights(n, 9, 12, seed=t) + [[1] * n]:
            if sum(a) == 0:
                continue
            b, per, y = part_bound(G, a, cls_of)
            for i in range(5):
                if cut_weight(G, a, cls_of, i) > per[i]:
                    FAIL.append(('master-cut', L.to_graph6(G), list(a), i)); bad += 1
            if L.psi_int(G, a) > b:
                FAIL.append(('master', L.to_graph6(G), list(a))); bad += 1
            tot += 1
    print("   %d (graph, partition, weight) instances, %d failures" % (tot, bad))

    print("=" * 78)
    print("S. The FALSE corollary, and the CORRECT one")
    print("=" * 78)
    y = [Fr(1, 6), Fr(1, 4), Fr(1, 6), Fr(1, 4), Fr(1, 6)]
    pr = [y[i] * y[(i + 1) % 5] for i in range(5)]
    print("   y = (1/6,1/4,1/6,1/4,1/6):  y_i y_{i+1} = %s" % [str(p) for p in pr])
    print("   min over ANY four cuts = 1/24 > 1/25  =>  'BAD_i=0 for some i' is NOT enough.")
    print("   For |I_0| = 2 consecutive (e.g. Wagner) : y=(1/3,1/3,0,0,1/3) gives min = 1/9.")
    print("   CORRECT criterion: BAD_i = 0 for all i, i.e. the partition is a hom H -> C5.")

    print("=" * 78)
    print("T. Which test graphs admit a homomorphism to C5 (=> psi <= 1/25 for ALL x)?")
    print("=" * 78)
    for name, G in N.items():
        h = hom_to_C5(G)
        print("   %-18s n=%2d : %s" % (name, G[0], "H -> C5  (SETTLED for all x)" if h
                                       else "no homomorphism to C5"))

    print("=" * 78)
    print("U. RESIDUAL: the best bound the master inequality can give, per graph")
    print("   maxbound(H) = max over x of min over (partition,i) of (y_i y_{i+1} + BAD_i)")
    print("   (a graph is settled for all x iff maxbound <= 1/25)")
    print("=" * 78)

    def best_over_partitions(G, a):
        """min over all admissible blow-up partitions AND all cuts."""
        n, adj = G
        best = None
        for C in L.induced_C5s(G):
            for cls in CV.blowups_from_C5(G, C):
                adm = CV.admissible(G, cls)
                inB = {v: m for m in range(5) for v in cls[m]}
                W = [v for v in range(n) if v not in inB]
                if any(not adm[v] for v in W):
                    continue
                for combo in itertools.product(*[adm[v] for v in W]):
                    cls_of = dict(inB)
                    cls_of.update(dict(zip(W, combo)))
                    b, per, y = part_bound(G, a, cls_of)
                    if best is None or b < best[0]:
                        best = (b, cls_of)
        return best

    for name in ['Wagner=And(3)', 'And(4)=G11', 'Petersen', 'Grotzsch']:
        G = N[name]
        n = G[0]
        q = 20 if n <= 11 else 14
        worst = None
        for a in rand_weights(n, q, 400, seed=99) + [[1] * n] + \
                 [[q // 5] * 5 + [0] * (n - 5)]:
            if sum(a) == 0:
                continue
            r = best_over_partitions(G, a)
            if r is None:
                continue
            b, cls_of = r
            val = Fr(b, sum(a) ** 2)
            if worst is None or val > worst[0]:
                worst = (val, list(a), Fr(L.psi_int(G, a), sum(a) ** 2))
        print("   %-14s : worst-x master bound = %s = %.5f   (psi there = %s)   1/25 = %.5f"
              % (name, worst[0], float(worst[0]), worst[2], 1 / 25))
    print("=" * 78)
    print("FAILURES: %d" % len(FAIL))
    for f in FAIL[:8]:
        print("   ", f)
