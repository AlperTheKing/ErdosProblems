#!/usr/bin/env python3
"""
make_manifest.py -- assemble runs/band11/manifest.json from the band-11 logs.
Parses the BAND11 REPORT blocks emitted by band11_vcscan[2].exe and records
exact integers only (no floats decide anything).
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # ktt_lr_negativity/


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse(path):
    txt = open(path).read()
    out = {"log": os.path.relpath(path, ROOT).replace("\\", "/")}
    m = re.search(r"valid dim<=3 polytopes[^=]*= (\d+)", txt)
    if m:
        out["valid_polytopes"] = int(m.group(1))
    m = re.search(r"NEGATIVE-a1 triples = (\d+)", txt)
    if m:
        out["negative_a1"] = int(m.group(1))
    m = re.search(r"min 6a1 = (-?\d+)\s+\(V=(-?\d+) c=(-?\d+)\) at (.*)", txt)
    if m:
        out["min_6a1"] = int(m.group(1))
        out["min_6a1_V"] = int(m.group(2))
        out["min_6a1_c"] = int(m.group(3))
        out["min_6a1_gaps"] = m.group(4).strip()
    m = re.search(r"max V = (-?\d+) \(c=(-?\d+) 6a1=(-?\d+)\) at (.*)", txt)
    if m:
        out["max_V"] = int(m.group(1))
        out["max_V_c"] = int(m.group(2))
        out["max_V_6a1"] = int(m.group(3))
        out["max_V_gaps"] = m.group(4).strip()
    m = re.search(r"MAX V/c = (-?\d+)/(\d+) \(6a1=(-?\d+) h3=(-?\d+)\) at (.*)", txt)
    if m:
        out["max_V_over_c"] = "%s/%s" % (m.group(1), m.group(2))
        out["max_V_over_c_6a1"] = int(m.group(3))
        out["max_V_over_c_h3"] = int(m.group(4))
        out["max_V_over_c_gaps"] = m.group(5).strip()
    m = re.search(r"MAX V/\(c\+h3\) = (-?\d+)/(\d+) \(V=(-?\d+) c=(-?\d+) h3=(-?\d+) 6a1=(-?\d+)\).*at (.*)", txt)
    if m:
        out["max_V_over_c_plus_h3"] = "%s/%s" % (m.group(1), m.group(2))
        out["max_V_over_c_plus_h3_data"] = {
            "V": int(m.group(3)), "c": int(m.group(4)),
            "h3": int(m.group(5)), "six_a1": int(m.group(6)),
            "gaps": m.group(7).strip()}
    m = re.search(r"MAX V at c=4 \(h\*_1=0\) = (-?\d+) at (.*?)\s+\[", txt)
    if m:
        out["max_V_at_c4"] = int(m.group(1))
        out["max_V_at_c4_gaps"] = m.group(2).strip()
    tbl = {}
    for mm in re.finditer(r"c=\s*(\d+) Vmax=\s*(-?\d+) 6a1=(-?\d+)\s+(a=.*)", txt):
        tbl[int(mm.group(1))] = {"Vmax": int(mm.group(2)),
                                 "six_a1": int(mm.group(3)),
                                 "gaps": mm.group(4).strip()}
    if tbl:
        out["max_V_at_fixed_c"] = {str(k): v for k, v in sorted(tbl.items())}
    m = re.search(r"^(EXHAUSTIVE|SIMPLEX|CLIMB|RAND|SMALLC) (.*)$", txt, re.M)
    if m:
        out["mode"] = m.group(1)
        out["mode_args"] = m.group(2).strip()
    return out


def main():
    runs = []
    for p in sorted(glob.glob(os.path.join(HERE, "*.log"))):
        runs.append(parse(p))
    files = {}
    for rel in ["r4_reeve/band11_vcscan.cpp", "r4_reeve/band11_vcscan.exe",
                "r4_reeve/band11_vcscan2.exe", "r4_reeve/band11_xcheck.py",
                "r4_reeve/band11_lranchor.py", "r4_reeve/hive4.py",
                "engine/lr_hive.exe", "engine/engineB_lrrule.py"]:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            files[rel] = sha256(p)
    man = json.load(open(os.path.join(HERE, "_manifest_head.json"))) \
        if os.path.exists(os.path.join(HERE, "_manifest_head.json")) else {}
    man["runs"] = runs
    man["artifact_sha256"] = files
    json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"),
              indent=1, sort_keys=False)
    print("wrote manifest.json with %d runs, %d artifacts" % (len(runs), len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
