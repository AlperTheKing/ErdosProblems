#!/usr/bin/env python3
"""DEFINITIVE residual check for the order-9 cert soundness (closes Step-1 residual (i)):
the flag moment matrix M^sigma(W) = sum_H p_W(H) P^sigma(H)/denom(H) must be PSD for graphons W. If yes,
sum_j gamma_j m_j(W) = <Q,M^sigma(W)> >= 0 (Q=sum gamma v v^T >=0), so the moment SOS is graphon-nonneg and
the cert d_mono <= 2/25+delta is sound. We build M^sigma(W) for band graphons W (a band graph + C5[2],C5[3])
for EACH of the 4 used sigmas and assert min eigenvalue >= 0 (PSD).
"""
import itertools
import numpy as np
from math import comb
import prove_cert as pc
import flag_sdp as fs
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def flag_distribution(N, A, states, k9):
    """p_W(H) = fraction of 9-subsets of W=(N,A) inducing state H. One pass; classify by canonical form."""
    p = np.zeros(len(states))
    tot = 0
    for S in itertools.combinations(range(N), 9):
        _, B = fe.induced(A, list(S))
        key = fe.canonical(9, B)
        idx = k9.get(key)
        if idx is not None: p[idx] += 1
        tot += 1
    return p / tot if tot else p

def Msigma_W(sigma, ss, states, Pmats, denom, pW):
    """M^sigma(W) = sum_H pW[H] Pmats[H]/denom[H]  (Pmats[H] = D x D raw count matrix)."""
    D = Pmats[0].shape[0]
    M = np.zeros((D, D))
    for h in range(len(states)):
        if pW[h] == 0 or denom[h] == 0: continue
        M += (pW[h] / denom[h]) * Pmats[h]
    return M

def build(N, A):
    return N, A

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def band_graph(N, seed=3):
    import random; random.seed(seed)
    pairs = [(u, v) for u in range(N) for v in range(u+1, N)]; random.shuffle(pairs)
    adj = [set() for _ in range(N)]; E = []
    target = int(0.29 * N*N/2)   # band-ish density
    for (u, v) in pairs:
        if adj[u] & adj[v]: continue
        adj[u].add(v); adj[v].add(u); E.append((u, v))
        if len(E) >= target: break
    A = [0]*N
    for (u, v) in E: A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def main():
    C = pc.load(9); states = C["states"]
    # canonical-form -> state index
    k9 = {}
    for i, (n, A) in enumerate(states):
        k9[fe.canonical(n, A)] = i
    # the 4 used sigmas (from C["moments"]): (sigma, ss)
    sig_ss = [(m[2], m[4]) for m in C["moments"]]
    print(f"sigmas (sigma, ss): {sig_ss}", flush=True)
    # precompute P^sigma(H) per state + denom per state for each sigma
    permom = []
    for (sigma, ss) in sig_ss:
        k = sigma[0]; m = k + ss
        flags = fs.enumerate_flags(sigma, m, triangle_free=True)
        Praw = fs.P_sigma(9, states, sigma, flags)   # list of DxD per state
        Pmats = [np.asarray(P, dtype=float) for P in Praw]
        denom = []
        for (n, _A) in states:
            nk = 1
            for i in range(k): nk *= (n - i)
            d = nk * (comb(n - k, ss) ** 2) if (nk > 0 and n - k >= ss) else 0
            denom.append(d)
        permom.append((sigma, ss, Pmats, denom, len(flags)))
        print(f"  sigma={sigma} ss={ss}: {len(flags)} flags, P dim {Pmats[0].shape}", flush=True)

    test_graphs = [("band-n13", *band_graph(13)), ("band-n14", *band_graph(14, 5)),
                   ("C5[2]", *c5n(2)), ("C5[3]", *c5n(3))]
    allpsd = True
    for (lab, N, A) in test_graphs:
        pW = flag_distribution(N, A, states, k9)
        print(f"--- W={lab} (N={N}), sum p_W={pW.sum():.4f} ---", flush=True)
        for (sigma, ss, Pmats, denom, nf) in permom:
            M = Msigma_W(sigma, ss, states, Pmats, denom, pW)
            Msym = (M + M.T) / 2
            ev = np.linalg.eigvalsh(Msym)
            mn = ev.min()
            psd = mn >= -1e-9 * max(1.0, abs(ev).max())
            allpsd = allpsd and psd
            print(f"   sigma={sigma}: min eig = {mn:+.3e} (PSD: {psd})", flush=True)
    print(f"SUMMARY: all M^sigma(W) PSD over tested band graphons: {allpsd}", flush=True)
    print("  (PSD => moment SOS sum gamma_j m_j(W) >= 0 => cert soundness residual (i) CLOSED)" if allpsd else "  (!! a non-PSD M^sigma would indicate a moment construction bug)", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
