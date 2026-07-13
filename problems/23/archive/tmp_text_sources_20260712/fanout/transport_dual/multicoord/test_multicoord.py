"""Exact pooled multi-coordinate capacity test; integer data promoted to Fraction."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[4]
ART = ROOT / "tmp/fanout/transport_dual/accounting/default.json"

def Q(x):
    return F(int(x), 1)

def check_artifact(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    cs=obj["coordinates"]
    rec=[]
    for c in cs:
        t=c["componentTransport"]
        d=Q(t["demand"])
        cap=Q(t["outsideCapacity"])+Q(t["sourceCapacity"])
        rec.append({"index":c["index"],"demand":str(d),"capacity":str(cap),"coordinate_ok":d<=cap})
    D=sum((Q(c["componentTransport"]["demand"]) for c in cs),F())
    C=sum((Q(c["componentTransport"]["outsideCapacity"])+Q(c["componentTransport"]["sourceCapacity"]) for c in cs),F())
    return {"path":str(path.relative_to(ROOT)),"coordinates":rec,"pooled_demand":str(D),
            "pooled_capacity":str(C),"pooled_ok":D<=C}

def minimal_borrower():
    # Search by total mass, then coordinate count and lexicographic tuple.
    for mass in range(0,17):
        for n in range(1,5):
            for vals in product(range(5), repeat=2*n):
                ds=vals[:n]; cs=vals[n:]
                if sum(ds)+sum(cs)!=mass: continue
                pooled=sum(map(Q,ds))<=sum(map(Q,cs))
                separate=all(Q(d)<=Q(c) for d,c in zip(ds,cs))
                if pooled and not separate:
                    return {"coordinates":n,"demand":list(ds),"capacity":list(cs),
                            "total_mass":mass,"pooled":True,"coordinatewise":False}
    raise AssertionError("search bound exhausted")

result={"arithmetic":"fractions.Fraction only","artifacts":[check_artifact(ART)],
        "artifact_count":1,"coordinate_records":3,"minimal_borrowing_witness":minimal_borrower()}
out=Path(__file__).with_name("RESULT.json")
out.write_text(json.dumps(result,sort_keys=True,indent=2)+chr(10),encoding="utf-8")
print(json.dumps(result,sort_keys=True))
