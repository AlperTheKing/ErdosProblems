"""Independent structural checks for the R38 bounded manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    raw = (HERE / "manifest.json").read_bytes()
    data = json.loads(raw)
    assert data["schema"] == "r38-weak-free-balanced-mutation-hunt-v1"
    assert data["verdict"] == "BOUNDED_ZERO_FAILURE"
    assert data["variantOffset"] == 0 and data["variantLimit"] == 5000
    assert data["counts"] == {"zero_displayed": 5000}
    assert len(data["records"]) == 5000
    assert not data["witnesses"]
    assert all(record["status"] == "zero_displayed" for record in data["records"])
    assert all(record["displayedDefect"] == 0 for record in data["records"])
    assert all(record["rowFamilySizes"] and min(record["rowFamilySizes"]) > 0 for record in data["records"])
    print("REPLAY=PASS")
    print("variants=5000 zero_displayed=5000 witnesses=0")
    print("manifest_sha256=" + hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
