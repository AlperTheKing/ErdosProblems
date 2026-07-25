import json, sys, os
from collections import defaultdict

src = sys.argv[1]
d = json.load(open(src))
print("triples screened      :", d["n_triples"])
print("status                :", d["status"])
print("degree distribution   :", d["d"])
print("min h*_1 - h*_d (all) :", d["min_margin"], d["min_margin_trip"])
print("min margin d>=2       :", d["min_margin_d2"], d["min_margin_d2_trip"])
print("min margin d>=4       :", d["min_margin_d4"], d["min_margin_d4_trip"])
print("max h*_d              :", d["max_hd"], d["max_hd_trip"])
print("max h*_d  d>=4        :", d["max_hd_d4"], d["max_hd_d4_trip"])
print("h*_1 == 0 count       :", d["n_h1_zero"], d["n_h1_zero_by_d"])
print("max h*_d | h*_1==0    :", d["max_hd_given_h1_zero"], d["max_hd_given_h1_zero_trip"])
print("non-lattice certs     :", d["n_nonlattice_cert"], d["nonlattice_kinds"])
print("moment inconsistent   :", d["n_moment_inconsistent"])
print("audit failures        :", d["n_audit_fail"])
print("hits                  :", len(d["hits"]))
print("anomalies             :", len(d["anomalies"]))

def show(name, lim=None):
    m = defaultdict(dict)
    for k, v in d[name].items():
        a, b = k.split("|", 1)
        m[int(a)][b] = v
    print("\n%s   (rows: d)" % name)
    for dd in sorted(m):
        row = m[dd]
        def key(x):
            try: return (0, int(x))
            except ValueError: return (1 if x.startswith(">") else -1, 0)
        items = sorted(row.items(), key=lambda kv: key(kv[0]))
        if lim: items = items[:lim]
        print(" d=%d : %s" % (dd, ", ".join("%s:%d" % kv for kv in items)))

show("d_margin")
show("d_hd")
show("d_h1", 14)
show("d_hsum", 14)
show("d_c", 14)
