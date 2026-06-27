#!/usr/bin/env python3
"""Faster confirmation scan: only run the EXPENSIVE harness on graphs whose edge count is high enough
that Gamma could plausibly be near N^2 (a necessary condition for a tight obstruction is a fairly dense
triangle-free graph). We pre-filter on m_edges before calling check_instance. For each graph6 line we
compute n and edge count cheaply; only if edges >= thresh do we call the full harness.
Also we look for ANY safe_peel=False (not just tight) and report the max Gamma/N^2 among those."""
import sys
from peel_check import check_instance
from adv_broom_geng import g6_decode

def main():
    thresh_frac=float(sys.argv[1]) if len(sys.argv)>1 else 0.0  # min edges as frac of n^2/4 (bip max)
    cnt=0; ran=0; obstr=0
    best_tight=0.0; best_tight_line=None
    best_false=0.0; best_false_line=None
    sp_false_tight=0
    for line in sys.stdin:
        dec=g6_decode(line)
        if dec is None: continue
        n,adj=dec; cnt+=1
        edges=sum(len(a) for a in adj)//2
        # bipartite (triangle-free max cut) upper bound on dense-ness; require >= frac of n^2/4
        if edges < thresh_frac*(n*n/4.0): continue
        ran+=1
        r=check_instance(n,adj)
        if not (r.get('ok') and r.get('B_connected')): continue
        m=r.get('m') or 0
        if m<2: continue
        g=r.get('gamma'); n2=r.get('n2')
        if not g or not n2: continue
        ratio=g/n2; sp=r.get('has_safe_peel')
        if sp is False and ratio>best_false:
            best_false=ratio; best_false_line=(line.strip(),n,m,g,n2)
        if r.get('ge_n2'):
            if ratio>best_tight: best_tight=ratio
            if sp is False:
                obstr+=1
                print(f"!!! OBSTRUCTION g6={line.strip()} N={n} m={m} gamma={g} n2={n2} sp={sp}")
            else:
                print(f"tight-OK g6={line.strip()} N={n} m={m} gamma={g} sp={sp}")
    print(f"# scanned={cnt} harness-ran={ran} obstructions={obstr} "
          f"max_ratio_among_safe_peel_False={best_false:.4f} at {best_false_line}")

if __name__=="__main__":
    main()
