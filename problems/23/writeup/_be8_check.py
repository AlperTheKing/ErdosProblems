"""Targeted balanced-endpoint check on Codex's 8 known SPLIT-bad gamma-min cuts (block 129 note)."""
from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side

cases=[
 ("J?AAFAwe_}?","11111010000",(1,6)),
 ("J?AAFAwe_}?","11111110000",(1,6)),
 ("J?AAF@cm?}?","11111110000",(1,6)),
 ("J?ABCfG]@h?","11111100000",(0,5)),
 ("J?ABCdW{?{?","00001111110",(4,8)),
 ("J?AFCpc{?t?","00001011110",(4,7)),
 ("J?AFCpc{?t?","00001111110",(4,7)),
 ("J?b@b_wBuD?","10000111100",(0,5)),
]
def deg(adj,s,v):
    dM=sum(1 for u in adj[v] if s[u]!=s[v]); dB=sum(1 for u in adj[v] if s[u]==s[v]); return dM,dB
for g6,sst,f in cases:
    n,E=dec(g6); s=[int(c) for c in sst]
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    a,b=f
    dMa,dBa=deg(adj,s,a); dMb,dBb=deg(adj,s,b)
    bal_a=(dMa==dBa); bal_b=(dMb==dBb)
    print(f"{g6} {sst} f={f}: a(dM={dMa},dB={dBa},bal={bal_a})  b(dM={dMb},dB={dBb},bal={bal_b})  "
          f"slack_a={dBa-dMa} slack_b={dBb-dMb}  -> {'BALANCED-ENDPOINT' if (bal_a or bal_b) else 'SYMMETRIC-PAIR(slack1/1)'}")
