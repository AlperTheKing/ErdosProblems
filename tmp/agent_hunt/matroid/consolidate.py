"""Consolidated canonical artifact for the matroid-lens hunt (single JSON + SHA)."""

from __future__ import annotations

import hashlib
import io
import json
import sys
from contextlib import redirect_stdout

import circuit_axioms
import fiber_forcing
import profiles
import rigidity
import transition_census
from fixtures import load_all, adjacency
from profiles import owner_table


def capture(mod):
    buf = io.StringIO()
    with redirect_stdout(buf):
        mod.main()
    txt = buf.getvalue()
    # transition_census prints "name {json}" lines; others pure json
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        out = {}
        # reparse concatenated "name {...}" blocks
        idx = 0
        while idx < len(txt):
            brace = txt.find("{", idx)
            if brace < 0:
                break
            name = txt[idx:brace].strip()
            depth = 0
            for j in range(brace, len(txt)):
                if txt[j] == "{":
                    depth += 1
                elif txt[j] == "}":
                    depth -= 1
                    if depth == 0:
                        out[name] = json.loads(txt[brace:j + 1])
                        idx = j + 1
                        break
        return out


def shared_hub_theorem_check():
    """Exact check of the t-uniform shared-d2-hub theorem hypotheses+conclusions
    on the fixtures where they apply."""
    res = {}
    for name, c in load_all().items():
        if c.n == 0 or name == "r34deg":
            continue
        adj = adjacency(c.n, c.support)
        tab = owner_table(c)
        zeros = [(w, x) for w, actives in tab.items()
                 for x, vec in actives.items() if vec == (0, 0, 0, 0)]
        rec = []
        for (w, s) in zeros:
            hyp_d2 = len(adj[s]) == 2
            others = [z for z in adj[s] if z != w]
            co_owner = (len(others) == 1 and others[0] in tab)
            inc_s = [i for i, a in enumerate(c.atoms) if s in (a["u"], a["v"])]
            t = 5
            rec.append({
                "owner": w, "active": s, "hubDegree": len(adj[s]),
                "hubD2": hyp_d2, "hubCoOwned": co_owner,
                "incHubCount": len(inc_s),
                "incHub_ge_t_minus_1": len(inc_s) >= t - 1,
            })
        res[name] = rec
    return res


def main():
    payload = {
        "schema": "matroid-lens-hunt-v1",
        "fixtures": {
            "hit298": "t5_classifier_v_l9_r9_1000.json (canonical c1d474d7...)",
            "hit264": "t5_live_x_classifier_v_l9_r9_5000.json (canonical 6595501f...)",
            "nearcand": "R46 sec.8 construction (18 vtx, 30 atom triangles)",
            "r34deg": "R34 degenerate 5-atom/4-edge abstract circuit",
            "t4abs": "t4_support_circuit_hit.json (abstract 16/15)",
        },
        "circuitAxioms": capture(circuit_axioms),
        "profiles": capture(profiles),
        "fiberForcing": capture(fiber_forcing),
        "rigidity": capture(rigidity),
        "transitionCensus": capture(transition_census),
        "sharedHubTheoremCheck": shared_hub_theorem_check(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           default=str)
    payload["canonicalSha256"] = hashlib.sha256(
        canonical.encode("ascii")).hexdigest()
    with open("matroid_lens_results.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, sort_keys=True, default=str)
    print("canonicalSha256:", payload["canonicalSha256"])
    print("sharedHubCheck:", json.dumps(payload["sharedHubTheoremCheck"]))


if __name__ == "__main__":
    main()
