#!/usr/bin/env python3
"""Extract candidate_graphs from the H2 workflow output JSON, write each as an
edge-list file, and run the independent verifier h2_check_edgelist.exe on each.
This independently confirms the agents' claimed (beta, min-5-set-drop) and directly
tests H2 (min 5-set drop <= 2n-1?) -- the agents' own harnesses are not trusted."""
import json
import subprocess
import os
import sys

OUT = r"C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\461052bb-8cbc-4d9f-996c-62e0fcc0bfcb\tasks\wvmhf35rm.output"
EXP = r"E:\Projects\ErdosProblems\bridge\experiments"
CHECKER = os.path.join(EXP, "h2_check_edgelist.exe")

with open(OUT, "r", encoding="utf-8") as f:
    data = json.load(f)

cands = data["result"]["candidate_graphs"]
print(f"loaded {len(cands)} candidate graphs\n")

for i, c in enumerate(cands):
    n = c["n"]  # actually N (vertex count) per our schema usage
    edges = c["edges"]
    desc = c["description"][:70]
    claimed = c.get("claimed_beta", "?")
    # determine N: max vertex index + 1 (the 'n' field holds N in the agents' output)
    maxv = 0
    for e in edges:
        maxv = max(maxv, e[0], e[1])
    N = maxv + 1
    fn = os.path.join(EXP, f"cand_{i:02d}.txt")
    with open(fn, "w") as g:
        g.write(f"{N}\n")
        for e in edges:
            g.write(f"{e[0]} {e[1]}\n")
    print(f"=== candidate {i:02d} | from={c['from']} | claimed_beta={claimed} | N={N}")
    print(f"    {desc}")
    try:
        r = subprocess.run([CHECKER, fn], capture_output=True, text=True, timeout=120)
        print("   ", r.stdout.strip().replace("\n", "\n    "))
    except subprocess.TimeoutExpired:
        print("    TIMEOUT")
    print()
