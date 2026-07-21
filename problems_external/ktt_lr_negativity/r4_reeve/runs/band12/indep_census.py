#!/usr/bin/env python3
"""Independent exhaustive r=4 census with hive4.py, mirroring the C++ conventions:
   nu partition with <=4 parts of weight W; lam, mu sub-partitions of nu
   (componentwise) with |lam|+|mu|=W; mu >= lam as length-4 arrays.
Reports per-W: triples, band-12 count, dim histogram, min a_1 (band and all),
max V, and any negative coefficient.  Compared against runs/band12/census_W60.log.
"""
import sys, json
from fractions import Fraction
from multiprocessing import Pool
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve")
from hive4 import analyze, trim

def partitions4(W):
    out = []
    for a in range(W, 0, -1):
        for b in range(min(a, W - a), -1, -1):
            for c in range(min(b, W - a - b), -1, -1):
                d = W - a - b - c
                if d <= c:
                    out.append((a, b, c, d))
    if W == 0:
        out.append((0, 0, 0, 0))
    return out

def subparts(nu):
    """all partitions p (len-4, weakly decr) with p_i <= nu_i, grouped by weight"""
    res = {}
    for a in range(nu[0], -1, -1):
        for b in range(min(a, nu[1]), -1, -1):
            for c in range(min(b, nu[2]), -1, -1):
                for d in range(min(c, nu[3]), -1, -1):
                    res.setdefault(a + b + c + d, []).append((a, b, c, d))
    return res

def degenerate(p):
    q = [x for x in p if x > 0]
    if not q:
        return True
    for i in range(len(q) - 1):
        if q[i] == q[i + 1]:
            return True
    if all(x == 1 for x in q[1:]):
        return True
    return False

def strict(p):
    return p[0] > p[1] > p[2] > p[3] >= 0

def do_nu(args):
    W, nu = args
    sp = subparts(nu)
    dnu = degenerate(nu)
    total = band = 0
    dh = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
    dhb = dict(dh)
    mina1 = None; mina1_at = None
    mina1b = None; mina1b_at = None
    maxV = -1; maxV_at = None
    maxVh1 = -1; maxVh1_at = None
    maxh2 = -1; maxh2_at = None
    negs = []
    dim3_nonstrict = 0
    vfail = 0
    minany_b = None
    for a in range(0, W + 1):
        for lam in sp.get(a, []):
            dl = degenerate(lam)
            for mu in sp.get(W - a, []):
                if mu < lam:
                    continue
                total += 1
                inb = dl or dnu or degenerate(mu)
                if inb:
                    band += 1
                r = analyze(list(lam), list(mu), list(nu))
                d = r["dim"]
                dh[d] += 1
                if inb:
                    dhb[d] += 1
                if d < 0:
                    continue
                if not r.get("verified", True):
                    vfail += 1
                if d == 3 and not (strict(lam) and strict(mu) and strict(nu)):
                    dim3_nonstrict += 1
                P = trim(r["poly"])
                if len(P) > 1:
                    a1 = P[1]
                    if mina1 is None or a1 < mina1:
                        mina1, mina1_at = a1, (lam, mu, nu)
                    if inb and (mina1b is None or a1 < mina1b):
                        mina1b, mina1b_at = a1, (lam, mu, nu)
                if inb:
                    for cf in P[1:]:
                        if minany_b is None or cf < minany_b:
                            minany_b = cf
                if min(P) < 0:
                    negs.append((lam, mu, nu, [str(x) for x in P]))
                V = r["volume_normalized"]
                if d == 3:
                    if V > maxV:
                        maxV, maxV_at = V, (lam, mu, nu)
                    hs = r["hstar"]
                    if hs[1] == 0 and V > maxVh1:
                        maxVh1, maxVh1_at = V, (lam, mu, nu)
                    if hs[2] > maxh2:
                        maxh2, maxh2_at = hs[2], (lam, mu, nu)
    return dict(total=total, band=band, dh=dh, dhb=dhb,
                mina1=mina1, mina1_at=mina1_at, mina1b=mina1b, mina1b_at=mina1b_at,
                maxV=maxV, maxV_at=maxV_at, maxVh1=maxVh1, maxVh1_at=maxVh1_at,
                maxh2=maxh2, maxh2_at=maxh2_at, negs=negs,
                dim3_nonstrict=dim3_nonstrict, vfail=vfail, minany_b=minany_b)

def main():
    Whi = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    G = None
    rows = []
    with Pool(40) as pool:
        for W in range(1, Whi + 1):
            tasks = [(W, nu) for nu in partitions4(W)]
            agg = None
            for r in pool.imap_unordered(do_nu, tasks, chunksize=1):
                if agg is None:
                    agg = r
                    continue
                agg["total"] += r["total"]; agg["band"] += r["band"]
                for k in agg["dh"]:
                    agg["dh"][k] += r["dh"][k]; agg["dhb"][k] += r["dhb"][k]
                for key, atk in (("mina1", "mina1_at"), ("mina1b", "mina1b_at")):
                    if r[key] is not None and (agg[key] is None or r[key] < agg[key]):
                        agg[key], agg[atk] = r[key], r[atk]
                for key, atk in (("maxV", "maxV_at"), ("maxVh1", "maxVh1_at"), ("maxh2", "maxh2_at")):
                    if r[key] > agg[key]:
                        agg[key], agg[atk] = r[key], r[atk]
                if r["minany_b"] is not None and (agg["minany_b"] is None or r["minany_b"] < agg["minany_b"]):
                    agg["minany_b"] = r["minany_b"]
                agg["negs"] += r["negs"]
                agg["dim3_nonstrict"] += r["dim3_nonstrict"]; agg["vfail"] += r["vfail"]
            print("W=%-3d triples=%-9d band=%-9d dim3(all)=%-7d dim3(band)=%-4d "
                  "mina1(band)=%-6s maxV(all)=%-4s negs=%d vfail=%d ns3=%d"
                  % (W, agg["total"], agg["band"], agg["dh"][3], agg["dhb"][3],
                     agg["mina1b"], agg["maxV"], len(agg["negs"]), agg["vfail"],
                     agg["dim3_nonstrict"]), flush=True)
            rows.append((W, agg))
            if G is None:
                G = agg
            else:
                G["total"] += agg["total"]; G["band"] += agg["band"]
                for k in G["dh"]:
                    G["dh"][k] += agg["dh"][k]; G["dhb"][k] += agg["dhb"][k]
                for key, atk in (("mina1", "mina1_at"), ("mina1b", "mina1b_at")):
                    if agg[key] is not None and (G[key] is None or agg[key] < G[key]):
                        G[key], G[atk] = agg[key], agg[atk]
                for key, atk in (("maxV", "maxV_at"), ("maxVh1", "maxVh1_at"), ("maxh2", "maxh2_at")):
                    if agg[key] > G[key]:
                        G[key], G[atk] = agg[key], agg[atk]
                if agg["minany_b"] is not None and (G["minany_b"] is None or agg["minany_b"] < G["minany_b"]):
                    G["minany_b"] = agg["minany_b"]
                G["negs"] += agg["negs"]
                G["dim3_nonstrict"] += agg["dim3_nonstrict"]; G["vfail"] += agg["vfail"]
    print("=== CUMULATIVE W<=%d ===" % Whi)
    print("total", G["total"], "band", G["band"])
    print("dim hist all ", G["dh"])
    print("dim hist band", G["dhb"])
    print("min a1 band", G["mina1b"], G["mina1b_at"])
    print("min a1 all ", G["mina1"], G["mina1_at"])
    print("min coeff band (a1..a3)", G["minany_b"])
    print("max V all", G["maxV"], G["maxV_at"])
    print("max V h*1=0 all", G["maxVh1"], G["maxVh1_at"])
    print("record h*2 all", G["maxh2"], G["maxh2_at"])
    print("dim3 nonstrict", G["dim3_nonstrict"], "vfail", G["vfail"], "negs", len(G["negs"]))
    for n in G["negs"][:20]:
        print("NEG", n)

if __name__ == "__main__":
    main()
