#!/usr/bin/env python3
"""fam11 aggregation: margin = h*_1 - h*_d as a function of weight."""
import sys, os, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))

def load():
    recs = []
    for p in sorted(glob.glob(os.path.join(HERE, "*.jsonl"))):
        if os.path.basename(p) in ("pool_stage1.jsonl",):
            continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if "lam" in r:
                r["_src"] = os.path.basename(p)
                recs.append(r)
    return recs

def main():
    tags = {}
    tp = os.path.join(HERE, "fam11.tags.json")
    if os.path.exists(tp):
        tags = json.load(open(tp))
    recs = load()
    ok = [r for r in recs if r.get("status") == "OK"]
    status = collections.Counter(r.get("status") for r in recs)
    best_hd = None
    best_margin = None
    hits = []
    ladder = collections.defaultdict(list)
    for r in ok:
        d = r["d"]
        h1, hd = r.get("hstar_1"), r.get("hstar_d")
        W = sum(r["nu"])
        key = "%s;%s;%s" % (",".join(map(str, r["lam"])),
                            ",".join(map(str, r["mu"])),
                            ",".join(map(str, r["nu"])))
        tag = tags.get(key, ["E:rand", W])[0]
        if h1 is None or hd is None:
            continue
        m = h1 - hd
        if best_hd is None or hd > best_hd[0]:
            best_hd = (hd, key, d, r["c"])
        if d >= 2 and (best_margin is None or m < best_margin[0]):
            best_margin = (m, key, d, r["c"], h1, hd)
        ladder[tag].append((W, d, r["c"], h1, hd, m,
                            r.get("hstar_sum")))
        if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG"):
            hits.append(r)
    # margin vs weight trend, per structured arm
    trends = {}
    for tag, rows in sorted(ladder.items()):
        if tag.startswith("E:"):
            continue
        rows.sort()
        trends[tag] = [{"W": w, "d": d, "c": c, "h1": h1, "hd": hd, "margin": m}
                       for (w, d, c, h1, hd, m, hs) in rows]
    # random-arm margin statistics by weight band
    band = collections.defaultdict(lambda: [None, None, 0])
    for tag, rows in ladder.items():
        if not tag.startswith("E:"):
            continue
        for (w, d, c, h1, hd, m, hs) in rows:
            b = "W<=60" if w <= 60 else ("W<=130" if w <= 130 else
                                         ("W<=280" if w <= 280 else "W>280"))
            e = band[b]
            e[0] = m if e[0] is None else min(e[0], m)
            e[1] = hd if e[1] is None else max(e[1], hd)
            e[2] += 1
    out = {
        "records": len(recs), "ok": len(ok),
        "status": dict(status),
        "best_hstar_d": best_hd,
        "min_margin_d_ge_2": best_margin,
        "hits": len(hits),
        "random_bands": {k: {"min_margin": v[0], "max_hstar_d": v[1],
                             "n": v[2]} for k, v in sorted(band.items())},
        "min_margin_by_dim": {},
    }
    bydim = {}
    for r in ok:
        d = r["d"]
        h1, hd = r.get("hstar_1"), r.get("hstar_d")
        if h1 is None or hd is None:
            continue
        m = h1 - hd
        if d not in bydim or m < bydim[d][0]:
            bydim[d] = (m, "%s;%s;%s" % (",".join(map(str, r["lam"])),
                                         ",".join(map(str, r["mu"])),
                                         ",".join(map(str, r["nu"]))), r["c"])
    out["min_margin_by_dim"] = {str(k): v for k, v in sorted(bydim.items())}
    json.dump({"summary": out, "trends": trends},
              open(os.path.join(HERE, "aggregate.json"), "w"), indent=1)
    with open(os.path.join(HERE, "hits.jsonl"), "w") as fh:
        for h in hits:
            fh.write(json.dumps(h) + "\n")
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
