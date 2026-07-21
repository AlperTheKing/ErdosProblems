#!/usr/bin/env python3
"""Independent Magma replay of the four DKP base-curve genera.

The input polynomials come from the exact factor-audit artifact.  Each affine
curve is projectively closed in Magma, then tested for irreducibility and
geometric genus.  The public calculator response and exact input are retained
for independent replay.  This script performs no parameter search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


CALCULATOR = "https://magma.maths.usyd.edu.au/xml/calculator.xml"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def magma_input(expression: str) -> str:
    polynomial = expression.replace("**", "^")
    return (
        "Q:=Rationals();\n"
        "A2<u,t>:=AffineSpace(Q,2);\n"
        f"C:=Curve(A2,{polynomial});\n"
        "P:=ProjectiveClosure(C);\n"
        "print IsIrreducible(P);\n"
        "print Genus(P);\n"
    )


def submit(code: str) -> tuple[bytes, ET.Element]:
    payload = urllib.parse.urlencode({"input": code}).encode("ascii")
    request = urllib.request.Request(CALCULATOR, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=75) as response:
        raw = response.read()
    return raw, ET.fromstring(raw)


def run(factor_audit: Path, output_dir: Path) -> dict[str, object]:
    source = json.loads(factor_audit.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for index, factor in enumerate(source["G"]["factors"], start=1):
        code = magma_input(factor["expanded"])
        raw, root = submit(code)
        input_path = output_dir / f"factor_{index}.m"
        response_path = output_dir / f"factor_{index}.xml"
        input_path.write_text(code, encoding="ascii", newline="\n")
        response_path.write_bytes(raw)

        headers = root.find("headers")
        results = root.find("results")
        if headers is None or results is None:
            raise AssertionError("calculator response lacks headers or results")
        lines = [(node.text or "") for node in results.findall("line")]
        nonempty = [line.strip() for line in lines if line.strip()]
        if nonempty != ["true", "5"]:
            raise AssertionError(f"factor {index}: unexpected Magma output {nonempty}")
        records.append(
            {
                "factor": index,
                "factor_sha256": factor["sha256"],
                "input_file": input_path.name,
                "input_sha256": sha256(code.encode("ascii")),
                "response_file": response_path.name,
                "response_sha256": sha256(raw),
                "magma_version": headers.findtext("version"),
                "calculator_time_seconds": headers.findtext("time"),
                "calculator_memory": headers.findtext("memory"),
                "is_irreducible": True,
                "geometric_genus": 5,
            }
        )
    return {
        "status": "PASS",
        "method": "independent Magma projective-closure genus replay",
        "calculator": CALCULATOR,
        "factor_audit_file": str(factor_audit),
        "factor_audit_sha256": sha256(factor_audit.read_bytes()),
        "factors": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("factor_audit", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = run(args.factor_audit, args.output_dir)
    output = args.output_dir / "magma_base_geometry_referee.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
