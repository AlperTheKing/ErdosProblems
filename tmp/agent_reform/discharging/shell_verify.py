# Verify SHELL inequality (derived from maxcut optimality vs flipping T_A u T_B):
#   for any S subset of one side, U := C(S) (blue nbhd), W := C(U):
#   sum_U m + sum_W m <= e_blue(W, otherside \ U) + 2 e_mono(U) + 2 e_mono(W)
# Must hold for EVERY optimal cut (it is a theorem); check exact, incl. tightness at blow-up.
import sys, random
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\discharging")
from flow_check import (maxcut_enumerate, side_of, build_adj, petersen, grotzsch,
                        chvatal, clebsch, gp, blowup, C5, C7, rand_maximal_tf, rand_sparse_tf)

def check_graph(name, N, edges, n_rand_S=400, seed=1):
    rng = random.Random(seed)
    adj = build_adj(N, edges)
    mc, masks = maxcut_enumerate(N, edges, cap_cuts=25)
    fails = 0
    tights = 0
    trials = 0
    for mask in masks:
        side = side_of(mask, N)
        m = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(N)]
        for _ in range(n_rand_S // len(masks) + 1):
            sb = rng.randrange(2)
            side_verts = [v for v in range(N) if side[v] == sb]
            if not side_verts: continue
            k = rng.randrange(1, len(side_verts) + 1)
            S = set(rng.sample(side_verts, k))
            U = set(w for v in S for w in adj[v] if side[w] != sb)
            W = set(w for u in U for w in adj[u] if side[w] == sb)
            lhs = sum(m[v] for v in U) + sum(m[v] for v in W)
            leak = sum(1 for w in W for x in adj[w] if side[x] != sb and x not in U)
            emU = sum(1 for u in U for x in adj[u] if side[x] != sb and False)  # placeholder
            # e_mono(U): edges inside U (same side as U = other side of S)
            emU = sum(1 for u in U for x in adj[u] if x in U and x > u)
            emW = sum(1 for w in W for x in adj[w] if x in W and x > w)
            rhs = leak + 2 * emU + 2 * emW
            trials += 1
            if lhs > rhs:
                fails += 1
                print(f"  !! SHELL FAIL {name} mask={mask} S={sorted(S)} lhs={lhs} rhs={rhs}")
            elif lhs == rhs and lhs > 0:
                tights += 1
    print(f"{name}: trials={trials} fails={fails} nontrivial_tight={tights}")
    sys.stdout.flush()
    return fails

if __name__ == "__main__":
    total = 0
    total += check_graph("petersen", *petersen())
    total += check_graph("grotzsch", *grotzsch())
    total += check_graph("chvatal", *chvatal())
    total += check_graph("clebsch", *clebsch())
    total += check_graph("GP(9,2)", *gp(9, 2))
    total += check_graph("C5blow(3,3,3,3,3)", *blowup(C5, [3]*5))
    total += check_graph("C5blow(4,4,4,4,4)", *blowup(C5, [4]*4 + [4]))
    total += check_graph("C7blow2", *blowup(C7, [2]*7))
    # explicit tightness at blow-up: S = one mono class
    N, E = blowup(C5, [3]*5)
    adj = build_adj(N, E)
    mc, masks = maxcut_enumerate(N, E, cap_cuts=25)
    side = side_of(masks[0], N)
    m = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(N)]
    monos = [v for v in range(N) if m[v] > 0]
    sides_of_monos = set(side[v] for v in monos)
    for sb in sides_of_monos:
        S = set(v for v in monos if side[v] == sb)
        U = set(w for v in S for w in adj[v] if side[w] != sb)
        W = set(w for u in U for w in adj[u] if side[w] == sb)
        lhs = sum(m[v] for v in U) + sum(m[v] for v in W)
        leak = sum(1 for w in W for x in adj[w] if side[x] != sb and x not in U)
        emU = sum(1 for u in U for x in adj[u] if x in U and x > u)
        emW = sum(1 for w in W for x in adj[w] if x in W and x > w)
        print(f"blowup t=3 S=mono-class(side{sb},|S|={len(S)}): lhs={lhs} leak={leak} emU={emU} emW={emW} rhs={leak+2*emU+2*emW} TIGHT={lhs==leak+2*emU+2*emW}")
    for N_, seedlist in ((12, range(25)), (14, range(25)), (16, range(15))):
        for sd in seedlist:
            n, EE = rand_maximal_tf(N_, 3000 * N_ + sd)
            total += check_graph(f"maxTF_N{N_}_s{sd}", n, EE, n_rand_S=120, seed=sd)
    print(f"TOTAL SHELL FAILS = {total}")
