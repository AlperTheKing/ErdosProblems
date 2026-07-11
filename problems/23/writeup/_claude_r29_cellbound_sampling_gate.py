r"""CLAUDE falsifier-first SAMPLING gate for the d09 per-cell lower-bound formula on the reconstructed 2943 cage.

FORMULA under audit (d09/retry2): for a selector tuple with l local rows in region 0 and r local rows in region 1
(al=338-l, ar=338-r anchors):
    lb(l,r) = 20411 + 2*((al+ar) + max(0,al-1) + max(0,ar-1)) + 200*(ceil(l/27)+ceil(r/27)) + (4 if l==r==0 else 0)
CLAIM: every tuple in cell (l,r) has exact active-scoped score >= lb(l,r). Computationally verified as a CELL SCAN
(argmin (0,0)=23115) but the per-tuple validity is unproven. A single sampled tuple scoring BELOW its cell bound
FALSIFIES the formula and reopens the global minimum below 23115.

METHOD: for a spread of cells, sample tuples (choose which selectors go local + which of their 4 local rows,
deterministic seed), evaluate the EXACT score with TWO independent implementations (d09 verify.state and the lead
constructor's scoped_state), assert (i) impls agree, (ii) score >= lb(cell). Integer-only.
Run from repo root: python problems/23/writeup/_claude_r29_cellbound_sampling_gate.py
"""
import importlib.util
import random
import sys
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
D09V = ROOT / "tmp/fanout/r29_gate/d09/retry2/verify.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lb(l, r):
    al, ar = 338 - l, 338 - r
    c55 = 2 * ((al + ar) + max(0, al - 1) + max(0, ar - 1))
    covered = (l + 26) // 27 + (r + 26) // 27
    return 20411 + c55 + 200 * covered + (4 if l == r == 0 else 0)


def main():
    lead = load("r29_lead", LEAD)
    d09 = load("r29_d09_verify", D09V)
    data = lead.build()
    n = data["n"]
    start, stop = data["selectorStart"], data["selectorStop"]
    meta = data["selectorMeta"]
    base_rows = [tuple(r) for r in data["rows"]]
    # enumerate families once (d09's own shortest-path enumerator)
    adj = d09.adj(n, data["blue"])
    fams = []
    for i, atom in enumerate(data["atoms"][start:stop]):
        fam = d09.shortest(adj, *atom)
        anchors = [row for row in fam if 55 in row]
        locs = [row for row in fam if 55 not in row]
        assert len(anchors) == 676 and len(locs) == 4
        fams.append({"region": meta[i]["region"], "anchor": tuple(meta[i]["anchorRow"]), "locals": [tuple(x) for x in locs]})
    reg = {0: [i for i, f in enumerate(fams) if f["region"] == 0],
           1: [i for i, f in enumerate(fams) if f["region"] == 1]}
    assert len(reg[0]) == 338 and len(reg[1]) == 338

    rng = random.Random(29431)
    cells = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 2), (26, 0), (27, 0), (28, 0), (0, 27),
             (5, 5), (27, 27), (54, 27), (100, 50), (169, 169), (200, 150), (300, 300), (338, 0), (338, 338)]
    cells += [(rng.randrange(339), rng.randrange(339)) for _ in range(6)]
    fails = []
    checked = 0
    for (l, r) in cells:
        samples = 3 if (l, r) != (0, 0) else 1
        for s in range(samples):
            rows = list(base_rows)
            for region, k in ((0, l), (1, r)):
                idx = rng.sample(reg[region], k) if k else []
                for i in reg[region]:
                    fam = fams[i]
                    if i in idx:
                        rows[start + i] = fam["locals"][rng.randrange(4)]
                    else:
                        rows[start + i] = fam["anchor"]
            t = tuple(rows)
            s1 = d09.state(data, t)["score"]
            s2 = lead.scoped_state(data, t)["score"]
            bound = lb(l, r)
            ok = (s1 == s2) and (s1 >= bound)
            checked += 1
            tag = "PASS" if ok else "FAIL"
            print("cell(%3d,%3d) sample%d: score d09=%d lead=%d bound=%d margin=%+d %s"
                  % (l, r, s, s1, s2, bound, s1 - bound, tag), flush=True)
            if not ok:
                wit = {"cell": [l, r], "sample": s, "score_d09": s1, "score_lead": s2, "bound": bound,
                       "local_choices": [{"selector": i, "row": list(rows[start + i])}
                                          for i in range(676) if rows[start + i] != fams[i]["anchor"]]}
                fails.append(wit)
    print("=" * 76)
    if fails:
        import json
        out = Path(__file__).with_name("_claude_r29_cellbound_witnesses.json")
        best = min(fails, key=lambda w: w["score_d09"])
        out.write_text(json.dumps({"falsified_formula": "d09 per-cell lower bound",
                                   "all_anchor_claimed_min": 23115,
                                   "best_sampled_score": best["score_d09"],
                                   "witnesses": fails}, indent=1) + "\n", encoding="utf-8")
        print("VERDICT: CELL-BOUND FORMULA FALSIFIED on %d sample(s); best sampled score %d (< 23115 claimed min: %s)"
              % (len(fails), best["score_d09"], best["score_d09"] < 23115))
        print("witnesses -> %s" % out.name)
        print("=> the 23115 global-minimum certificate is INVALID; global min may lie below; reopen landscape.")
        sys.exit(1)
    print("VERDICT: %d sampled tuples across %d cells ALL respect the d09 cell bound; two implementations agree"
          % (checked, len(cells)))
    print("everywhere. Formula SURVIVES falsifier-first sampling (still needs the structural derivation; Codex L1).")


if __name__ == "__main__":
    main()
