"""Emit graph6 for C5[n] blow-ups (input to Q5_bip.exe)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Q5_lib import blowup_C5


def g6_encode(n, adj):
    assert n <= 62
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out


if __name__ == "__main__":
    for k in range(1, 7):
        n, adj = blowup_C5(k)
        print(k, n, g6_encode(n, adj))
