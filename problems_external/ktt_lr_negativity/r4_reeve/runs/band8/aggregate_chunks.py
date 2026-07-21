#!/usr/bin/env python3
"""
aggregate_chunks.py -- merge the Cw-slice reports of the exhaustive band-8
gap-class census into one band-level record.

The slices Cw = 0..90 PARTITION the band region (every gap class realised by a
triple with |nu| in [61,90] has Cw <= 90 and lands in exactly one slice), so the
merge is exact: counters add, extrema take the best over slices.
"""
import glob
import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

ARG_RE = re.compile(r"lam=\((.*?)\) mu=\((.*?)\) nu=\((.*?)\)")


def parse_arg(line):
    m = ARG_RE.search(line)
    if not m:
        return None
    return [[int(x) for x in g.split(",")] for g in m.groups()]


def parse_chunk(path):
    d = {"hist": {}, "maxVc": {}, "hits": []}
    lines = open(path).read().splitlines()
    for i, ln in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if "classes=" in ln:
            for tok in ln.split("]")[1].split():
                k, v = tok.split("=")
                d[k] = int(v)
        elif "min6a1=" in ln and "min6a1_at" not in ln:
            m = re.search(r"min6a1=(-?\d+) \(V=(-?\d+)\)", ln)
            d["min6a1"] = int(m.group(1)); d["min6a1_V"] = int(m.group(2))
            d["argmin6a1"] = parse_arg(nxt)
        elif re.search(r"\] maxV=", ln):
            d["maxV"] = int(ln.split("maxV=")[1]); d["argmaxV"] = parse_arg(nxt)
        elif "maxV_hstar1_zero=" in ln:
            d["maxV_h1z"] = int(ln.split("=")[-1]); d["argmaxV_h1z"] = parse_arg(nxt)
        elif "max_hstar2=" in ln:
            d["max_hstar2"] = int(ln.split("=")[-1]); d["argmax_hstar2"] = parse_arg(nxt)
        elif "maxV_at_c=" in ln:
            m = re.search(r"maxV_at_c=(\d+) : V=(-?\d+)", ln)
            d["maxVc"][int(m.group(1))] = (int(m.group(2)), parse_arg(ln))
        elif "hist6a1" in ln:
            _, k, v = ln.split("]")[1].split()
            d["hist"][int(k)] = int(v)
        elif "min_2a2=" in ln:
            m = re.search(r"min_2a2=(-?\d+)  NEG_a2=(\d+)", ln)
            d["min_2a2"] = int(m.group(1)); d["neg_a2"] = int(m.group(2))
            d["argmin2a2"] = parse_arg(nxt)
        elif "max_V_over_L1plus_hstar3" in ln:
            m = re.search(r"= (\d+)/(\d+)", ln)
            d["ratN"] = int(m.group(1)); d["ratD"] = int(m.group(2))
            d["argmaxrat"] = parse_arg(nxt)
        elif "min6a1_at_V_ge_100=" in ln:
            m = re.search(r"min6a1_at_V_ge_100=(-?\d+) \(V=(-?\d+)\)", ln)
            d["minBig"] = int(m.group(1)); d["minBigV"] = int(m.group(2))
            d["argminBig"] = parse_arg(nxt)
        elif " HIT " in ln:
            d["hits"].append(ln.strip())
    return d


def main():
    paths = sorted(glob.glob(os.path.join(HERE, "chunk_Cw*.log")))
    chunks = []
    for p in paths:
        if os.path.getsize(p) == 0:
            print("SKIP (empty, still running?):", os.path.basename(p))
            continue
        c = parse_chunk(p)
        c["_file"] = os.path.basename(p)
        chunks.append(c)
    if not chunks:
        print("no chunk logs")
        return 1
    G = {"classes": 0, "band_triples_covered": 0, "nonempty": 0, "dim3": 0, "NEG": 0,
         "neg_a2": 0, "hist": {}, "maxVc": {}, "hits": []}
    for c in chunks:
        for k in ("classes", "band_triples_covered", "nonempty", "dim3", "NEG"):
            G[k] += c.get(k, 0)
        G["neg_a2"] += c.get("neg_a2", 0)
        for k, v in c["hist"].items():
            G["hist"][k] = G["hist"].get(k, 0) + v
        for k, (v, a) in c["maxVc"].items():
            if k not in G["maxVc"] or v > G["maxVc"][k][0]:
                G["maxVc"][k] = (v, a)
        G["hits"] += c["hits"]
        for key, arg, better in (("min6a1", "argmin6a1", min), ("maxV", "argmaxV", max),
                                 ("maxV_h1z", "argmaxV_h1z", max),
                                 ("max_hstar2", "argmax_hstar2", max),
                                 ("min_2a2", "argmin2a2", min),
                                 ("minBig", "argminBig", min)):
            if key not in c:
                continue
            if key not in G or better(G[key], c[key]) == c[key] and G[key] != c[key]:
                G[key] = c[key]
                G[arg] = c[arg]
                if key == "min6a1":
                    G["min6a1_V"] = c["min6a1_V"]
                if key == "minBig":
                    G["minBigV"] = c["minBigV"]
        if "ratN" in c:
            if "ratN" not in G or Fraction(c["ratN"], c["ratD"]) > Fraction(G["ratN"], G["ratD"]):
                G["ratN"], G["ratD"], G["argmaxrat"] = c["ratN"], c["ratD"], c["argmaxrat"]
    G["min_a1_exact"] = str(Fraction(G["min6a1"], 6))
    G["max_V_over_L1plus_hstar3"] = str(Fraction(G["ratN"], G["ratD"]))
    G["chunks"] = [c["_file"] for c in chunks]
    G["hist"] = {str(k): G["hist"][k] for k in sorted(G["hist"])}
    G["maxVc"] = {str(k): G["maxVc"][k] for k in sorted(G["maxVc"])}
    with open(os.path.join(HERE, "band_aggregate.json"), "w") as f:
        json.dump(G, f, indent=1)
    print(json.dumps({k: G[k] for k in ("classes", "band_triples_covered", "nonempty", "dim3",
                                        "NEG", "min6a1", "min_a1_exact", "maxV", "maxV_h1z",
                                        "max_hstar2", "max_V_over_L1plus_hstar3", "neg_a2",
                                        "min_2a2")}, indent=1))
    print("chunks merged:", len(chunks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
