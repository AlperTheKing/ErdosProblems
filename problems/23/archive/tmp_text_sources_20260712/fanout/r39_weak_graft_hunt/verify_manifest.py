"""Independent structural replay of the three surviving R39 max-cut grafts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r39_search", HERE / "search_bad_atom_grafts.py")
S = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = S
SPEC.loader.exec_module(S)


def main():
    data = json.loads((HERE / "manifest.json").read_text(encoding="ascii"))
    assert data["verdict"] == "BOUNDED_NO_WITNESS"
    assert data["enumeratedCutsFixedV0"] == 1 << 19
    assert data["counts"] == {"not_maxcut": 174433, "zero_minimum": 3}
    expected = {(2, 15), (3, 10), (4, 7)}
    assert {tuple(item["added"][0]) for item in data["zeroExamples"]} == expected
    for item in data["zeroExamples"]:
        added = {tuple(item["added"][0])}
        bad = S.BASE_BAD_SET | added
        edges = S.BASE_EDGES | added
        assert S.triangle_free(edges)
        assert S.exact_maxcut(edges)[0] == len(S.BLUE) == 20
        bads = tuple(sorted(bad))
        families = tuple(S.shortest_rows(*e) for e in bads)
        assert tuple(map(len, families)) == (2, 2, 1, 1, 1)
        choice = tuple(item["zeroChoice"])
        rows = tuple(families[i][choice[i]] for i in range(len(families)))
        ctx = S.p5.make_graph_context(S.N, S.BLUE, bad)
        result = S.evaluate(ctx, rows)
        assert result["defect"] == 0
        assert not result["state"].active_vertices
        assert sum(0 in row and 5 in row for row in rows) == 0
        assert S.cut_sigma(edges, bad, 0, 5) == (3, 2, 1)
    print("REPLAY=PASS maxcut_grafts=3 exact_tuple_minimum=0 active_scope=vacuous")


if __name__ == "__main__":
    main()
