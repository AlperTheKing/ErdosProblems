"""Exact rigidity quantification.

1. BI-STUCK ATOMS (owners v=0, m=1): atoms not incident to either owner such
   that NO row avoids both owners. In any v-profile state their row contains m
   (avoids v); in any m-profile state it contains v (avoids m) -> the row MUST
   differ between any v-profile state and any m-profile state.
   => min Hamming distance between the two owners' profile-state sets >= count.
   (Single-pivot rotor edge impossible iff count >= 2; census already 0.)
2. Also: incident-stuck refinement and hub-visit decomposition of stuck rows.
3. Hub onto-structure at each zero-vector (owner, active): first steps of
   Inc(x0) atoms (forced tail contributions) vs tail edges; coverage-supplied
   hub edges per pair fiber.
"""

from __future__ import annotations

import json

from fixtures import load_all, adjacency, norm
from profiles import owner_table, first_step


def bi_stuck(circ, v, m):
    inc = {i for i, a in enumerate(circ.atoms)
           if v in (a["u"], a["v"]) or m in (a["u"], a["v"])}
    stuck = []
    for i, a in enumerate(circ.atoms):
        if i in inc:
            continue
        if all(v in r or m in r for r in a["rows"]):
            stuck.append({"atom": i, "pair": [a["u"], a["v"]],
                          "rows": [list(r) for r in a["rows"]]})
    return stuck


def hub_structure(circ, w, x0):
    adj = adjacency(circ.n, circ.support)
    tail = [z for z in adj[x0] if z != w]
    inc_x0 = [i for i, a in enumerate(circ.atoms) if x0 in (a["u"], a["v"])]
    inc_w = {i for i, a in enumerate(circ.atoms) if w in (a["u"], a["v"])}
    rec = {"owner": w, "active": x0, "tailDirs": tail,
           "incHubAtoms": []}
    for i in inc_x0:
        a = circ.atoms[i]
        # selected rows must avoid w (hub atoms can't be incident to w:
        # w,x0 adjacent -> different shores -> (w,x0) not an atom)
        assert i not in inc_w
        steps = sorted({first_step(r, x0) for r in a["rows"] if w not in r})
        rec["incHubAtoms"].append({"atom": i, "pair": [a["u"], a["v"]],
                                   "wAvoidingFirstSteps": steps})
    return rec


def main():
    out = {}
    for name, c in load_all().items():
        if c.n == 0 or name == "r34deg":
            continue
        rec = {}
        rec["biStuck_v0_m1"] = bi_stuck(c, 0, 1)
        rec["biStuckCount"] = len(rec["biStuck_v0_m1"])
        tab = owner_table(c)
        rec["hub"] = []
        for w, actives in tab.items():
            for x, vec in actives.items():
                if vec == (0, 0, 0, 0):
                    rec["hub"].append(hub_structure(c, w, x))
        out[name] = rec
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
