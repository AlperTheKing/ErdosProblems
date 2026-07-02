from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCAN = HERE / "_tmp_y1_capacity_basin_scan.py"


spec = importlib.util.spec_from_file_location("scan", SCAN)
scan = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(scan)


ALL_TIGHT = ("b1", "d1", "f1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1")
HIGH_A = ("a1", "b1", "d1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1")
HIGH_A_WEAK = ("a1", "b1", "d1", "s1", "s2", "s3", "s4", "s5", "u1")
XQ_A = ("f1", "s3", "s4", "s5", "s6", "s7", "u1")
XQ_B = ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1")
U1_S7_HIGH = ("a1", "c1", "d1", "e1", "f1", "s1", "s2", "s6", "s7", "u1", "v1", "x1")
XQ_S5_HIGH = ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1")
ALL_ONES = ("a1", "b1", "c1", "d1", "e1", "f1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1", "v1", "x1")


def classify(branch: str, cap: str, active: tuple[str, ...]) -> str:
    if active == ALL_TIGHT:
        return "CLOSED: seven-tight/low-active"
    if active == HIGH_A or active == HIGH_A_WEAK:
        return "CLOSED: high-boundary/all-ones endpoint family"
    if active == ALL_ONES:
        return "CLOSED: all-ones endpoint Phi=25"
    if branch == "xq" and active == XQ_A:
        return "CLOSED: xq survivor family A"
    if branch == "xq" and active == XQ_B:
        return "CLOSED: xq survivor family B"
    if branch == "u1" and cap == "s7" and active == U1_S7_HIGH:
        return "CLOSED: u1/s7 high boundary"
    if branch == "xq" and active == XQ_S5_HIGH:
        return "CLOSED: xq/s5 high boundary"
    # Families exactified from critical scans but not always produced by basin scan.
    if branch == "s2" and cap in {"s4", "s7"} and active == ("b1", "f1", "s1", "s5"):
        return "CLOSED: s2 critical survivor"
    if branch == "s3" and cap == "s5" and active == ("b1", "f1", "u1", "v1"):
        return "CLOSED: s3 critical survivor"
    return "OPEN/UNCLASSIFIED"


def main() -> None:
    bad = []
    for branch in scan.BRANCHES:
        print("BRANCH", branch)
        for cap in scan.CAPS:
            ranked = scan.run_one(cap, branch, starts=50)
            print(" ", cap, "clusters", len(ranked))
            for phi, active, count, _w, _xquv in ranked[:8]:
                label = classify(branch, cap, active)
                print("   ", label, "phi", round(phi, 9), "count", count, "active", active)
                if label.startswith("OPEN"):
                    bad.append((branch, cap, phi, active))
    if bad:
        print("UNCLASSIFIED")
        for row in bad:
            print(row)
    else:
        print("PASS active-set coverage scan: all observed clusters classified")


if __name__ == "__main__":
    main()





