"""Investigate discrepancy: _charge2 said max sum_C S = N over actual geodesics in cyc[f],
but _charge4_c5 (which uses the SAME cyc[f] iteration) found sum_C S - N = +0.6667 at I?BD@g]Qo f=(7,9) C=[7,5,8,6,9].
Check: is [7,5,8,6,9] actually a geodesic in cyc[(7,9)]? Print all geodesics of f=(7,9) and their S-sums."""
from fractions import Fraction as F
from _h import dec, loads

g6="I?BD@g]Qo"
n,E=dec(g6); info=loads(n,E)
print("n=",info['n'],"M=",info['M'])
def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}
M=info['M']
pfs={f:pf_vec(info,f) for f in M}
S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(info['n'])}
print("S=",{v:str(S[v]) for v in range(info['n'])})
f=(7,9)
if f not in info['cyc']:
    # maybe stored as (9,7)? M entries
    for ff in M:
        if set(ff)=={7,9}: f=ff
print("f=",f,"ell=",info['ell'][f])
print("geodesics of f:")
for P in info['cyc'][f]:
    print("  ",P, "sum_C S=", str(sum(S[v] for v in P)), float(sum(S[v] for v in P)))
print("N=",info['n'])
# Also the specific path [7,5,8,6,9]
print("path [7,5,8,6,9] sum S =", str(sum(S[v] for v in [7,5,8,6,9])))
