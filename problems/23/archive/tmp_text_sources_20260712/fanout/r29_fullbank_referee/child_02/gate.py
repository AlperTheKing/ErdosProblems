#!/usr/bin/env python3
"""Exact symbolic R29 hub-demand gate; printed choices are samples only."""
import json
from hashlib import sha256
HUBS=(0,1,2); NSEL=676; NROWS=680
DATA={h:{"collision":6650,"hit":1,"d_pair":0,"d_load":0,"d_degree":0,"d_active":0} for h in HUBS}
def demand(choice):
    assert len(choice)==NSEL and all(0<=x<NROWS for x in choice)
    assert all(all(d[k]==0 for k in ("d_pair","d_load","d_degree","d_active")) for d in DATA.values())
    per={str(h):DATA[h]["collision"]+DATA[h]["hit"] for h in HUBS}
    return {"changed":sum(x!=0 for x in choice),"per_hub":per,"demand":sum(per.values())}
def main():
    samples={"all_anchor":[0]*NSEL,"all_first_nonanchor":[1]*NSEL,"all_last":[679]*NSEL,"alternating_extremes":[0 if i%2==0 else 679 for i in range(NSEL)],"single_last":[679]+[0]*(NSEL-1)}
    out={"status":"SAMPLES_ONLY","selector_space":str(NROWS**NSEL),"symbolic_zero_delta":True,"samples":{n:demand(c) for n,c in samples.items()}}
    encoded=json.dumps(out,sort_keys=True,indent=2)+"\n"; print(encoded,end="")
    print("OUTPUT_SHA256",sha256(encoded.encode()).hexdigest())
if __name__=="__main__": main()
