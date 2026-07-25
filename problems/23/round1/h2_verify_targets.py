"""H2 (ii): build the family's best graphs at the target orders and emit them for
INDEPENDENT exact verification (exhaustive 2^(N-1) maxcut in claude_exact_bip.exe).

Weights come from the exhaustive/hill-climbed blow-up optimisation (h2_opt.exe).
Everything here is integer arithmetic.
"""
from h2_lib import *
from h2_blowup_theory import bip_blowup, bip_blowup_full


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i - 1) % 5), (5 + i, (i + 1) % 5), (5 + i, 10)]
    return 11, sorted({(min(a, b), max(a, b)) for a, b in E})


CASES = []
gn, ge = grotzsch()
# N = 24: Grotzsch blow-up with weights (2^10, 4)  -- the doubled N=12 extremal
CASES.append(("N24_grotzsch_2x10_4", gn, ge, [2] * 10 + [4]))
# N = 26: Grotzsch blow-up, best weights found
CASES.append(("N26_grotzsch", gn, ge, [1, 1, 1, 4, 4, 0, 0, 1, 5, 4, 5]))
# N = 24 / 26 best plain C5 blow-ups, for comparison
CASES.append(("N24_C5_55554", 5, C5_EDGES, [5, 5, 5, 5, 4]))
CASES.append(("N26_C5_65555", 5, C5_EDGES, [6, 5, 5, 5, 5]))
# N = 12 extremal itself, as a Grotzsch blow-up
CASES.append(("N12_grotzsch_1x10_2", gn, ge, [1] * 10 + [2]))
# N = 27 (frac 0.16 target, N = 2 mod 5): the +1 gain over C5 blow-ups
CASES.append(("N27_grotzsch", gn, ge, [3, 4, 2, 1, 1, 3, 4, 2, 1, 1, 5]))
CASES.append(("N27_C5_66555", 5, C5_EDGES, [6, 6, 5, 5, 5]))
# N = 49 / 51 (frac 0.04 targets): best C5 and best Grotzsch scaling
CASES.append(("N49_C5_1010101009", 5, C5_EDGES, [10, 10, 10, 10, 9]))
CASES.append(("N51_C5_1110101010", 5, C5_EDGES, [11, 10, 10, 10, 10]))

if __name__ == "__main__":
    out = open("h2_targets.txt", "w")
    for name, bn, be, w in CASES:
        N, adj, offs = blowup(bn, be, w)
        assert N == sum(w)
        tf = is_triangle_free(N, adj)
        b_id = bip_blowup(bn, be, w)
        m = num_edges(N, adj)
        g6 = g6_encode(N, adj)
        print(f"{name}\tN={N}\tm={m}\ttriangle_free={tf}\tbip_identity={b_id}\t"
              f"N^2/25={N*N/25:.4f}\t25bip/N^2={25*b_id/(N*N):.6f}")
        print(f"    g6 = {g6}")
        out.write(g6 + "\n")
    out.close()
    print("\ngraph6 written to h2_targets.txt (one per line, in the order above)")
