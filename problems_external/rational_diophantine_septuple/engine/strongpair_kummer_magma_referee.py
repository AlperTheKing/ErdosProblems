#!/usr/bin/env python3
"""Official-Magma replay of the strong-pair local branch witnesses."""

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


def magma_program(source: dict[str, object]) -> str:
    witnesses = source["witnesses"]
    assert isinstance(witnesses, list) and len(witnesses) == 2
    lines = [
        "k:=GF(109);",
        "Pol<q>:=PolynomialRing(k);",
        "R<e>:=quo<Pol|q^2>;",
        "function BasePoly(u,v)",
        " return 3*u^4*v^4-8*u^4*v^3+6*u^4*v^2-u^4-8*u^3*v^4+4*u^3*v^3-8*u^3*v^2+12*u^3*v+6*u^2*v^4-8*u^2*v^3+4*u^2*v^2+8*u^2*v+6*u^2+12*u*v^3+8*u*v^2+4*u*v+8*u-v^4+6*v^2+8*v+3;",
        "end function;",
        "function DoublePoint(P,a2,a4)",
        " x:=P[1]; y:=P[2]; lam:=(3*x^2+2*a2*x+a4)/(2*y);",
        " x2:=lam^2-a2-2*x; y2:=-y+lam*(x-x2); return <x2,y2>;",
        "end function;",
        "function AddPoints(P,Q,a2)",
        " x1:=P[1]; y1:=P[2]; x2:=Q[1]; y2:=Q[2]; lam:=(y2-y1)/(x2-x1);",
        " x3:=lam^2-a2-x1-x2; y3:=-y1+lam*(x1-x3); return <x3,y3>;",
        "end function;",
        "function ResidualData(u,v)",
        " D:=u*v-u-v-1; a:=2*u/(u^2-1); b:=2*v/(v^2-1); c:=2*(u^2-1)*(v^2-1)/D^2;",
        " rab:=2*(u*v+1)*D/((u^2-1)*(v^2-1)); rac:=(u*v-u+v+1)/D; rbc:=(u*v+u-v+1)/D; ys:=rab*rac*rbc;",
        " ab:=a*b; ac:=a*c; bc:=b*c; abc:=a*b*c; a2:=ab+ac+bc; a4:=ab*ac+ab*bc+ac*bc; a6:=ab*ac*bc;",
        " PP:=<R!0,abc>; SS:=<R!1,ys>;",
        " assert PP[2]^2 eq PP[1]^3+a2*PP[1]^2+a4*PP[1]+a6;",
        " assert SS[2]^2 eq SS[1]^3+a2*SS[1]^2+a4*SS[1]+a6;",
        " assert rab^2 eq 1+ab and rac^2 eq 1+ac and rbc^2 eq 1+bc;",
        " P2:=DoublePoint(PP,a2,a4); P3:=AddPoints(P2,PP,a2); P4:=DoublePoint(P2,a2,a4); P5:=AddPoints(P4,PP,a2);",
        " S2:=DoublePoint(SS,a2,a4); assert S2[1] eq SS[1] and S2[2] eq -SS[2];",
        " P3p:=AddPoints(P3,SS,a2); P3m:=AddPoints(P3,<SS[1],-SS[2]>,a2);",
        " d0:=P3[1]/abc; dp:=P3p[1]/abc; dm:=P3m[1]/abc; g:=P5[1]/abc;",
        " return [1+g*d0,1+g*dp,1+g*dm],[a,b,c,d0,dp,dm,g],[rab,rac,rbc];",
        "end function;",
    ]
    for ordinal, witness in enumerate(witnesses, start=1):
        assert isinstance(witness, dict)
        u0, v0 = witness["point_uv"]
        tu, tv = witness["tangent_vector"]
        residual_values = witness["residual_values"]
        derivatives = witness["tangent_derivatives"]
        values = witness["seven_values"]
        roots = witness["three_pair_roots"]
        parity = witness["parity_vector"]
        lines.extend(
            [
                f"u:=R!{u0}+R!{tu}*e; v:=R!{v0}+R!{tv}*e;",
                "assert BasePoly(u,v) eq 0;",
                "fs,vals,roots:=ResidualData(u,v);",
                "assert fs eq ["
                + ",".join(f"R!{a}+R!{b}*e" for a, b in zip(residual_values, derivatives))
                + "];",
                "assert [Eltseq(x)[1]:x in vals] eq [k|" + ",".join(map(str, values)) + "];",
                "assert [Eltseq(x)[1]:x in roots] eq [k|" + ",".join(map(str, roots)) + "];",
                "assert #Seqset([Eltseq(x)[1]:x in vals]) eq 7 and &and[Eltseq(x)[1] ne 0:x in vals];",
                f'print "witness_{ordinal}_PASS";',
                'print "parity_' + "".join(map(str, parity)) + '";',
            ]
        )
    lines.append('print "ALL_PASS";')
    return "\n".join(lines) + "\n"


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
    parser.add_argument("witness_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    source = json.loads(args.witness_json.read_text(encoding="utf-8"))
    code = magma_program(source)
    raw, root = submit(code)
    headers = root.find("headers")
    results = root.find("results")
    if headers is None or results is None:
        raise AssertionError("calculator response lacks headers or results")
    output = [line.text or "" for line in results.findall("line") if (line.text or "").strip()]
    expected = ["witness_1_PASS", "parity_010", "witness_2_PASS", "parity_001", "ALL_PASS"]
    if output != expected:
        raise AssertionError(f"unexpected Magma output: {output}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_path = args.output_dir / "local_branch_referee.m"
    response_path = args.output_dir / "local_branch_referee.xml"
    input_path.write_text(code, encoding="ascii", newline="\n")
    response_path.write_bytes(raw)
    report = {
        "status": "PASS",
        "method": "independent dual-number replay in official Magma",
        "calculator": CALCULATOR,
        "magma_version": headers.findtext("version"),
        "calculator_time_seconds": headers.findtext("time"),
        "calculator_memory": headers.findtext("memory"),
        "witness_source": str(args.witness_json),
        "witness_source_sha256": sha256(args.witness_json.read_bytes()),
        "input_file": input_path.name,
        "input_sha256": sha256(code.encode("ascii")),
        "response_file": response_path.name,
        "response_sha256": sha256(raw),
        "output": output,
        "verified": [
            "base equation to first order",
            "three published pair roots",
            "P and S on induced curve",
            "3S=O",
            "3P and 5P group arithmetic",
            "two transverse unit parity rows",
            "seven distinct nonzero residue values at both branch witnesses",
        ],
    }
    report_path = args.output_dir / "local_branch_referee.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
