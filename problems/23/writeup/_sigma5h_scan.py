"""Find and characterize the super-levels where sigma_s > 5|H_s| (termwise cap FAILS).

Scan census gamma-min connected-B max cuts (N<=10) plus lane families.
For each cut and each super-level s (H_s={T>s}), compute sigma_s = dB-dM and h=|H_s|.
Record the WORST ratio sigma_s/h and any level with sigma_s > 5 h.
Also record, at such a violating level, the value of s relative to N and to theta=(N+eta)/2,
and whether it is a LOW band (2s <= N) or HIGH band, and the running-prefix slack there.

Goal: confirm (a) termwise sigma<=5h fails; (b) it fails only in a regime where the
prefix bank is already positive; and characterize the failure regime (low vs high s).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def boundary(n, adj, side, Hset):
    dB = 0; dM = 0
    for u in Hset:
        for v in adj[u]:
            if v in Hset:
                continue
            if side[u] != side[v]:
                dB += 1
            else:
                dM += 1
    return dB, dM


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n); m = len(M)
    eta = F(n * n, 25) - m
    theta = (N + eta) / 2
    levs = sorted(set([F(0)] + [t for t in T]))
    for k in range(len(levs) - 1):
        s = levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB, dM = boundary(n, adj, side, Hset)
        sig = dB - dM
        acc['levels'] += 1
        ratio = F(sig, h)
        if ratio > acc['maxratio'][0]:
            acc['maxratio'] = (ratio, name, n, m, str(s), h, str(sig), str(N), str(theta))
        if sig > 5 * h:
            acc['viol'] += 1
            lowband = (2 * s <= N)
            highband = (2 * s >= (N + eta))  # past theta*2
            rec = (name, n, m, str(s), h, str(sig), 'LOW' if lowband else ('HIGH' if highband else 'MID'),
                   str(s), str(theta), str(N))
            if len(acc['examples']) < 12:
                acc['examples'].append(rec)
            # bucket by band
            key = 'LOW' if lowband else ('HIGH' if highband else 'MID')
            acc['viol_band'][key] = acc['viol_band'].get(key, 0) + 1


def main():
    acc = dict(levels=0, viol=0, maxratio=(F(0), '', 0, 0, '', 0, '', '', ''),
               examples=[], viol_band={})
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: viol so far={acc['viol']}", flush=True)
    print("\n=== sigma_s > 5 h scan ===")
    print(f"levels scanned = {acc['levels']}")
    print(f"termwise sigma>5h violations = {acc['viol']}")
    print(f"violations by band = {acc['viol_band']}")
    print(f"max sigma/h ratio = {acc['maxratio'][0]} at {acc['maxratio'][1:]}")
    print("examples (name,n,m,s,h,sig,band,s,theta,N):")
    for e in acc['examples']:
        print("  ", e)


if __name__ == "__main__":
    main()
