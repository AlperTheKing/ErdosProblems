"""Emit graph6 for the graphs whose exact bip the report claims (And(k), top-24 table)."""
import sys
from audit_f8_lib import cayleyZ, g6enc, trifree, edges, blowup, mk

out = open('audit_gen.g6', 'w')
names = open('audit_gen_names.txt', 'w')


def emit(name, g):
    assert trifree(*g), name
    s = g6enc(*g)
    out.write(s + "\n")
    names.write(f"{s}\t{name}\tn={g[0]}\tm={len(edges(*g))}\n")


for k in range(2, 11):
    n = 3 * k - 1
    emit(f"And({k})", cayleyZ(n, [1 + 3 * t for t in range(k)]))
# top-24 table entries with n<=30
c5 = cayleyZ(5, [1])
for t in range(1, 7):
    emit(f"C5[{t}^5]", blowup(*c5, [t] * 5))
emit("C5[5,5,5,5,6]", blowup(*c5, [5, 5, 5, 5, 6]))
emit("C5[4,4,4,4,5]", blowup(*c5, [4, 4, 4, 4, 5]))
emit("C5[5,6,6,6,6]", blowup(*c5, [5, 6, 6, 6, 6]))
emit("C10(1,4)", cayleyZ(10, [1, 4]))
emit("C10(2,3)", cayleyZ(10, [2, 3]))
emit("C15(1,4,6)", cayleyZ(15, [1, 4, 6]))
emit("C15(2,3,7)", cayleyZ(15, [2, 3, 7]))
emit("C20(1,4,6,9)", cayleyZ(20, [1, 4, 6, 9]))
emit("C20(2,3,7,8)", cayleyZ(20, [2, 3, 7, 8]))
emit("C25(1,4,6,9,11)", cayleyZ(25, [1, 4, 6, 9, 11]))
emit("C25(2,3,7,8,12)", cayleyZ(25, [2, 3, 7, 8, 12]))
emit("C30(1,4,6,9,11,14)", cayleyZ(30, [1, 4, 6, 9, 11, 14]))
emit("C30(2,3,7,8,12,13)", cayleyZ(30, [2, 3, 7, 8, 12, 13]))
emit("C13(1,5)", cayleyZ(13, [1, 5]))
emit("C13(2,3)", cayleyZ(13, [2, 3]))
emit("C13(4,6)", cayleyZ(13, [4, 6]))
emit("C26(1,5,8,12)", cayleyZ(26, [1, 5, 8, 12]))
emit("C26(2,3,10,11)", cayleyZ(26, [2, 3, 10, 11]))
# the true a(14)=7 witness found by the audit
from audit_f8_lib import g6dec
nW, aW = g6dec('L?`DAboU`w@{hS')
emit("a14witness=P13[2 at v10]", blowup(nW, aW, [2 if i == 10 else 1 for i in range(13)]))
emit("C13(1,5)[2,1^12]", blowup(*cayleyZ(13, [1, 5]), [2] + [1] * 12))
from itertools import combinations
V = list(combinations(range(5), 2))
emit("Petersen", mk(10, [(i, j) for i in range(10) for j in range(i + 1, 10)
                         if not set(V[i]) & set(V[j])]))
E = [(i, (i + 1) % 5) for i in range(5)]
for i in range(5):
    E += [(5 + i, (i + 1) % 5), (5 + i, (i - 1) % 5), (5 + i, 10)]
emit("Grotzsch", mk(11, sorted(set(tuple(sorted(e)) for e in E))))
out.close()
names.close()
print("written audit_gen.g6")
