#!/usr/bin/env python3
"""Bind the exact edge-basis certificate to the fixed r=4 hive normal set."""

import json
import os
import sys

from q2_verify_basis_certificate import verify


HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "q2_basis_witness_certificate.json")
EXPECTED_R4_NORMALS = [
    [1, 0, 0], [-1, 1, 0], [-1, 0, 0], [0, -1, 0], [1, -1, 0],
    [0, 1, 0], [-1, 0, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1],
    [0, -1, 1], [0, 0, -1], [1, 0, -1], [0, 1, -1], [0, 0, 1],
]


def main():
    path = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else PATH
    with open(path, encoding="utf-8") as f:
        cert = json.load(f)
    if cert.get("normals") != EXPECTED_R4_NORMALS:
        raise AssertionError("certificate normal set is not the fixed r=4 hive normal set")
    verify(path)
    print("r4_normal_set=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
