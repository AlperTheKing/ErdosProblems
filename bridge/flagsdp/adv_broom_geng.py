#!/usr/bin/env python3
"""Exhaustive geng scan of connected triangle-free graphs, piped through the harness.
We flag any tight (Gamma>=N^2) m>=2 connected-B instance with has_safe_peel False (obstruction),
and report near-tight ones (Gamma within a small band of N^2) for signal.
Reads graph6 lines from stdin. Usage:
  geng -c -t N | python adv_broom_geng.py N
where -t = triangle-free (girth>=4), -c connected.
"""
import sys
from peel_check import check_instance

def g6_decode(line):
    line=line.strip()
    if not line: return None
    data=line.encode()
    # standard graph6 decode
    p=0
    def getbyte():
        nonlocal p
        b=data[p]-63; p+=1; return b
    n=getbyte()
    if n==63:  # n>=63 not expected for our small N
        n=(getbyte()<<12)|(getbyte()<<6)|getbyte()
    adj=[set() for _ in range(n)]
    bits=[]
    while p<len(data):
        b=data[p]-63; p+=1
        for k in range(5,-1,-1):
            bits.append((b>>k)&1)
    idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]:
                adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

def main():
    band = float(sys.argv[1]) if len(sys.argv)>1 else 0.0  # fraction below N^2 to call 'near'
    cnt=0; obstr=0; near=0; tight_ok=0
    best_ratio=0.0; best_line=None
    for line in sys.stdin:
        dec=g6_decode(line)
        if dec is None: continue
        n,adj=dec
        cnt+=1
        r=check_instance(n,adj)
        if not r.get("ok") or not r.get("B_connected"): continue
        m=r.get("m") or 0
        if m<2: continue
        g=r.get("gamma"); n2=r.get("n2")
        if g is None or not n2: continue
        ratio=g/n2
        if ratio>best_ratio:
            best_ratio=ratio; best_line=(line.strip(),n,m,g,n2,r.get("has_safe_peel"))
        if r.get("ge_n2"):
            tight_ok+=1
            if r.get("has_safe_peel") is False:
                obstr+=1
                print(f"!!! OBSTRUCTION g6={line.strip()} N={n} m={m} gamma={g} n2={n2} "
                      f"safe_peel={r.get('has_safe_peel')} detail={r.get('detail')}")
            else:
                if tight_ok<=20:
                    print(f"tight-OK g6={line.strip()} N={n} m={m} gamma={g} safe_peel={r.get('has_safe_peel')}")
        elif band>0 and ratio>=1.0-band:
            near+=1
            if near<=30:
                print(f"near g6={line.strip()} N={n} m={m} gamma={g} n2={n2} ratio={ratio:.4f} "
                      f"safe_peel={r.get('has_safe_peel')}")
    print(f"# scanned={cnt} tight(ge_n2)&m>=2={tight_ok} obstructions={obstr} near={near} "
          f"best_ratio={best_ratio:.4f} best={best_line}")

if __name__=="__main__":
    main()
