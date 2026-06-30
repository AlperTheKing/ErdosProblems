"""Test the bridge chain. main: N(N-row) >= var = Q - row^2/ell.
Chain A uses Q <= maxS_supp * row (L4-support). Then var <= maxS_supp*row - row^2/ell.
Bridge A:  N(N-row) >= maxS_supp*row - row^2/ell  ?   (if true on gate AND maxS_supp<=N, main follows)
Also test the cleaner combined claim using maxS_supp and ell relations."""
from fractions import Fraction as F
import _wf_var_3 as W

accs = W.battery()
n_rows = 0
fA = 0; fA_worst = None
# also record: is maxS_supp <= N always, and ell_f <= N, and row<=ell_f*maxS_supp?
mS_le_N_fail = 0
ell_le_N_fail = 0
# Bridge A2 (the real target): given var <= maxS_supp*row - row^2/ell and we want N(N-row)>=var.
for name, acc in accs:
    for r in acc:
        n_rows += 1
        N = F(r['n']); row = r['row']; ell = r['ellf']; mS = r['maxS_supp']
        if mS > N: mS_le_N_fail += 1
        if ell > N: ell_le_N_fail += 1
        ubvar = mS*row - row*row/ell
        if N*(N-row) - ubvar < 0:
            fA += 1
            d = (N*(N-row)-ubvar, name, r['n'], r['f'], str(row), str(ell), str(mS))
            if fA_worst is None or d[0] < fA_worst[0]: fA_worst = d
print("rows", n_rows)
print("maxS_supp<=N fails:", mS_le_N_fail)
print("ell_f<=N      fails:", ell_le_N_fail)
print("BRIDGE A  N(N-row) >= maxS_supp*row - row^2/ell  fails:", fA, "worst:", fA_worst)
