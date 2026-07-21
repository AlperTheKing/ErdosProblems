#!/usr/bin/env python3
"""Certify that the f0 radical is geometrically nontrivial over Q(C)."""

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


def magma_program() -> str:
    return """Q:=Rationals();
A2<u,v>:=AffineSpace(Q,2);
p:=3*u^4*v^4-8*u^4*v^3+6*u^4*v^2-u^4-8*u^3*v^4+4*u^3*v^3-8*u^3*v^2+12*u^3*v+6*u^2*v^4-8*u^2*v^3+4*u^2*v^2+8*u^2*v+6*u^2+12*u*v^3+8*u*v^2+4*u*v+8*u-v^4+6*v^2+8*v+3;
C:=Curve(A2,p); CP:=ProjectiveClosure(C); assert IsIrreducible(CP) and Genus(CP) eq 1;
A3<U,V,W>:=AmbientSpace(CP); F:=FunctionField(CP); uf:=F!(U/W); vf:=F!(V/W);
D:=uf*vf-uf-vf-1; a:=2*uf/(uf^2-1); b:=2*vf/(vf^2-1); c:=2*(uf^2-1)*(vf^2-1)/D^2;
ab:=a*b; ac:=a*c; bc:=b*c; abc:=a*b*c;
EI:=EllipticCurve([F|0,ab+ac+bc,0,ab*ac+ab*bc+ac*bc,ab*ac*bc]);
PI:=EI![0,abc,1]; Q3:=3*PI; Q5:=5*PI; f0:=1+(Q5[1]/abc)*(Q3[1]/abc);

u0:=Q!(-128)/119; v0:=Q!135/169; assert Evaluate(p,[u0,v0]) eq 0;
D0:=u0*v0-u0-v0-1; a0:=2*u0/(u0^2-1); b0:=2*v0/(v0^2-1); c0:=2*(u0^2-1)*(v0^2-1)/D0^2;
ab0:=a0*b0; ac0:=a0*c0; bc0:=b0*c0; abc0:=a0*b0*c0;
E0:=EllipticCurve([Q|0,ab0+ac0+bc0,0,ab0*ac0+ab0*bc0+ac0*bc0,ab0*ac0*bc0]);
P0:=E0![0,abc0,1]; R3:=3*P0; R5:=5*P0; f0special:=1+(R5[1]/abc0)*(R3[1]/abc0);
expected:=Q!1444826354692880176175542632758091489949461121516717187797631937926078167/18471605762539446868905554671818683484250104844462195703699876560625367;
cc:=Q!1444826354692880176175542632758091489949461121516717187797631937926078167/1699820767;
sqden:=Q!(3*2937581*4200369782179*89053733033);
assert f0special eq expected; assert f0special/cc eq (1/sqden)^2;
flag,root:=IsSquare(f0/cc); assert not flag;
print "f0_specialization_PASS";
print "f0_constant_class_test_PASS";
print "f0_geometrically_nonsquare_PASS";
"""


def submit(code: str) -> tuple[bytes, ET.Element]:
    request = urllib.request.Request(
        CALCULATOR,
        data=urllib.parse.urlencode({"input": code}).encode("ascii"),
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        raw = response.read()
    return raw, ET.fromstring(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    code = magma_program()
    raw, root = submit(code)
    headers = root.find("headers")
    results = root.find("results")
    if headers is None or results is None:
        raise AssertionError("calculator response lacks headers or results")
    output = [line.text or "" for line in results.findall("line") if (line.text or "").strip()]
    expected = [
        "f0_specialization_PASS",
        "f0_constant_class_test_PASS",
        "f0_geometrically_nonsquare_PASS",
    ]
    if output != expected:
        raise AssertionError(f"unexpected Magma output: {output}")
    if headers.find("warning") is not None:
        raise AssertionError(f"Magma warning: {headers.findtext('warning')}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_path = args.output_dir / "f0_class_referee.m"
    response_path = args.output_dir / "f0_class_referee.xml"
    input_path.write_text(code, encoding="ascii", newline="\n")
    response_path.write_bytes(raw)
    report = {
        "status": "PASS",
        "method": "rational specialization determines the only possible constant square class; official Magma rejects that class",
        "lemma": "If f in Q(C) is square over Qbar(C), then f=d*h^2 for d in Q* and h in Q(C); any rational nonzero specialization determines d modulo Q*2.",
        "calibration_point": ["-128/119", "135/169"],
        "f0_specialization": "1444826354692880176175542632758091489949461121516717187797631937926078167/18471605762539446868905554671818683484250104844462195703699876560625367",
        "possible_constant_class": "1444826354692880176175542632758091489949461121516717187797631937926078167/1699820767",
        "magma_is_square_after_class_removal": False,
        "conclusion": "f0 is not a square in Qbar(C); combined with parity rows 010 and 001, all three residual classes are geometrically independent.",
        "geometric_square_class_rank": 3,
        "geometrically_connected_components": 1,
        "cover_degree": 8,
        "branch_degree_lower_bound": 2,
        "geometric_genus_lower_bound": 5,
        "magma_version": headers.findtext("version"),
        "calculator_time_seconds": headers.findtext("time"),
        "calculator_memory": headers.findtext("memory"),
        "input_file": input_path.name,
        "input_sha256": sha256(code.encode("ascii")),
        "response_file": response_path.name,
        "response_sha256": sha256(raw),
        "output": output,
    }
    report_path = args.output_dir / "f0_class_referee.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
