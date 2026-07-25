#!/usr/bin/env python
import sys, json, collections

recs = []
for fn in sys.argv[1:]:
    for line in open(fn):
        line = line.strip()
        if line:
            recs.append(json.loads(line))

st = collections.Counter(r.get("status") for r in recs)
print("records", len(recs), dict(st))

ok = [r for r in recs if r.get("status") == "OK"]
print("OK", len(ok))
print("d histogram", dict(collections.Counter(r["d"] for r in ok)))
print("r histogram", dict(collections.Counter(r["r"] for r in ok)))

# audit flags
bad = [r for r in ok if not (r.get("heldout_ok") and r.get("hstar_roundtrip_ok")
                             and r.get("interior_check_ok") and r.get("hstar_1_identity_ok")
                             and r.get("moment_criteria_consistent"))]
print("audit failures:", len(bad))
for r in bad[:5]:
    print("  ", r["lam"], r["mu"], r["nu"])

neg = [r for r in ok if r.get("NEG")]
t0 = [r for r in ok if r.get("TIER0")]
jp = [r for r in ok if r.get("JACKPOT")]
print("NEG", len(neg), "TIER0", len(t0), "JACKPOT", len(jp))

hn = [r for r in ok if not r.get("hstar_nonneg")]
print("h* with a negative entry:", len(hn))

dge4 = [r for r in ok if r["d"] >= 4]
print("d>=4 records:", len(dge4))

def key(r):
    return (r["lam"], r["mu"], r["nu"])

# best h*_d
bd = max(ok, key=lambda r: (r["hstar_d"] if r["hstar_d"] is not None else -1))
print("max h*_d =", bd["hstar_d"], key(bd), "d=", bd["d"], "h*=", bd["hstar"])

# min h*_1 - h*_d  (overall and restricted to d>=4)
def marg(r):
    if r["hstar_1"] is None or r["hstar_d"] is None:
        return None
    return r["hstar_1"] - r["hstar_d"]

with_m = [(marg(r), r) for r in ok if marg(r) is not None]
mn = min(with_m, key=lambda x: x[0])
print("min h*_1-h*_d =", mn[0], key(mn[1]), "d=", mn[1]["d"], "h*=", mn[1]["hstar"])
hist = collections.Counter(m for (m, r) in with_m)
print("margin histogram (lowest 12):", sorted(hist.items())[:12])

w4 = [(m, r) for (m, r) in with_m if r["d"] >= 4]
if w4:
    mn4 = min(w4, key=lambda x: x[0])
    print("min margin among d>=4:", mn4[0], key(mn4[1]), "d=", mn4[1]["d"], "h*=", mn4[1]["hstar"])
    print("  d>=4 margin hist (lowest 10):",
          sorted(collections.Counter(m for (m, r) in w4).items())[:10])

# h*_1 == 0 records
z = [r for r in ok if r["hstar_1"] == 0]
print("h*_1 == 0 records:", len(z), " of which d>=4:", sum(1 for r in z if r["d"] >= 4))
print("  h*_d values among them:", dict(collections.Counter(r["hstar_d"] for r in z)))
zz = sorted(set((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]), r["d"], tuple(r["hstar"])) for r in z))
for q in zz[:25]:
    print("   ", q)
print("  (total distinct h*_1=0 shapes:", len(zz), ")")

# sum h*
print("min Sum h* over d>=4:", min((r["hstar_sum"], key(r)) for r in dge4) if dge4 else None)
print("u2 criterion margins: min (u2_mean) not computed here")
