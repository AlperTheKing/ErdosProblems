"""Transform Bank-L v2 row certificates into pressure-cover certificates.

Target is P_Q^+ rather than -Delta_Q.  For P_Q <= 0 the row is packet-free.
For P_Q > 0, this emitter prefers the prefix-coarea terminal interval term when
present; otherwise it reweights the existing v2 detour/nuK term to contribute
exactly P_Q.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def parse_frac(s) -> F:
    if isinstance(s, int):
        return F(s)
    if isinstance(s, str):
        return F(s)
    raise TypeError(s)


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def key(r: dict) -> str:
    return json.dumps({"name": r["name"], "n": r["n"], "f": r["f"], "row": r["row"]}, sort_keys=True)


def load_prefix(path: Path) -> dict[str, dict]:
    out = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("certificate", {}).get("status") == "SAT":
                out[key(rec)] = rec
    return out


def reweight_term(term: dict, target: F) -> dict:
    value = parse_frac(term["value"])
    if value <= 0:
        raise ValueError(term)
    coeff = target / value
    out = {k: v for k, v in term.items() if k not in ("coeff", "contribution")}
    out["coeff"] = frac_s(coeff)
    out["contribution"] = frac_s(coeff * value)
    return out


def prefix_term(rec: dict) -> dict:
    term = rec["certificate"]["terms"][0]
    return {
        "kind": "lane_prefix_nuK",
        "source_kind": term.get("kind"),
        "i": term.get("i"),
        "value": term["value"],
        "coeff": term["coeff"],
        "contribution": term["contribution"],
        "verts": term.get("verts"),
        "sigma": term.get("sigma"),
        "nu": term.get("nu"),
        "K_S": term.get("K_S"),
        "terminal": term.get("terminal"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v2", default="tmp/bankl_lcb_certs_n11_v2.jsonl")
    ap.add_argument("--prefix", default="tmp/bankl_lane_prefix_coarea_n11.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    args = ap.parse_args()

    prefix = load_prefix(Path(args.prefix))
    acc: Counter = Counter()
    first_fail = None
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.v2).open("r", encoding="utf-8") as fh, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            Pq = parse_frac(r["P_Q"])
            rec = {
                "schema": "bankl_pressure_cover_cert_v1",
                "name": r["name"],
                "n": r["n"],
                "m": r["m"],
                "f": r["f"],
                "row": r["row"],
                "L": r["L"],
                "p": r["row_packet_p"],
                "h": r["row_packet_h"],
                "d": r["row_packet_d"],
                "r": r["row_packet_r"],
                "P_Q": r["P_Q"],
                "rho_Q": r["rho_Q"],
                "pressure_sign": r["pressure_sign"],
                "source_certificate_kind": r["certificate_kind"],
            }
            if Pq <= 0:
                kind = "tight" if Pq == 0 else "packet_free"
                terms = []
                verified = True
                target = F(0)
            else:
                target = Pq
                pk = prefix.get(key(r))
                if pk is not None:
                    kind = "lane_prefix_nuK"
                    terms = [prefix_term(pk)]
                elif r.get("certificate_terms"):
                    src = r["certificate_terms"][0]
                    src_kind = src.get("kind", r["certificate_kind"])
                    kind = "detour" if src_kind == "detour" else "connected_nuK" if src.get("terminal") is False else "nuK"
                    terms = [reweight_term(src, target)]
                else:
                    kind = "FAIL"
                    terms = []
                total = sum(parse_frac(t["contribution"]) for t in terms)
                verified = total == target
            rec["pc_kind"] = kind
            rec["target"] = frac_s(target)
            rec["terms"] = terms
            rec["verified"] = verified
            if not verified or kind == "FAIL":
                acc["fail"] += 1
                if first_fail is None:
                    first_fail = rec
            acc["rows"] += 1
            acc[f"kind:{kind}"] += 1
            acc[f"sign:{r['pressure_sign']}"] += 1
            out.write(json.dumps(rec, sort_keys=True) + "\n")
    summary = {
        "output": str(out_path),
        "rows": acc["rows"],
        "fail": acc["fail"],
        "kinds": {k.removeprefix("kind:"): v for k, v in sorted(acc.items()) if k.startswith("kind:")},
        "signs": {k.removeprefix("sign:"): v for k, v in sorted(acc.items()) if k.startswith("sign:")},
        "first_fail": first_fail,
    }
    print(json.dumps(summary, sort_keys=True))
    print("PASS pressure-cover certificate transform" if acc["fail"] == 0 else "FAIL pressure-cover certificate transform")


if __name__ == "__main__":
    main()
