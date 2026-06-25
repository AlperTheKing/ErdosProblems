#!/usr/bin/env python3
"""
Phase F2: PSD-LIFTED margin localizers (GPT Q16 step-3), replacing the weak averaged-scalar form.

For each color c and threshold tau, build the localizing moment matrix over rooted indicator flags
F_i (root = a single vertex of color c, plus s free vertices):
    L_c(x)[i,j] = << [[ F_i F_j (H_sigma - tau) ]] >>          (High colors: enforce margin >= tau)
    L_c(x)[i,j] = << [[ F_i F_j (tau - H_sigma) ]] >>          (Low  colors: enforce margin <= tau)
where H_sigma(root r) = (cutdeg(r) - monodeg(r))/(n-1) is the margin density at r (cut/mono by SIDE).
Requiring L_c >> 0 is implied, for a graphon W, by margin(r) >= tau (resp <= tau) on all color-c roots
(L_c(W) = ∫ (margin(r)-tau) q(r) q(r)^T dr >> 0 when the weight is >= 0). So honest marks keep L_c >> 0
(SOUND), while a DISHONEST re-marking (Low vertex with margin > tau) makes the weight negative and breaks
PSD -> the localizer forbids the re-marking the SDP would otherwise use to evade the margin switch.

This is the per-vertex (PSD) tie between abstract color and true margin; the old localizer_vecs only tied
the color-AVERAGED margin, which the SDP could satisfy while mislabeling vertices.
"""
import itertools
import numpy as np
import flag_engine as fe
import flag_engine_col as fc
import flag_sdp_col as fs
import flag_margin_sdp as ms

def side(c): return c // 2


def root_margin(n, A, col, r):
    """Margin density at root r: (cutdeg - monodeg)/(n-1), cut/mono by side."""
    cut = mono = 0
    sr = side(col[r]); Ar = A[r]
    for w in range(n):
        if w != r and (Ar >> w) & 1:
            if side(col[w]) != sr: cut += 1
            else: mono += 1
    return (cut - mono) / (n - 1) if n > 1 else 0.0


def localizer_flags(c, m, triangle_free=True):
    """Rooted colored flags for root type sigma_c = (single vertex colored c) on m vertices."""
    sigma = (1, [0], (c,))
    return ms.enumerate_flags_kcol(sigma, m, triangle_free=triangle_free)


def psd_localizer_mats(states, c, tau, flags, low):
    """Per-state matrices Q_c(state) with L_c(x) = sum_state x_state Q_c(state), realizing
         L_c[i,j] = << [[ F_i F_j (H_sigma - tau) ]] >>   (High, low=False)
         L_c[i,j] = << [[ F_i F_j (tau - H_sigma) ]] >>   (Low,  low=True)
       H_sigma is a degree-1 rooted flag density: a SEPARATE fresh vertex u disjoint from the F_i,F_j
       extension vertices, contributing +1 if u is a cut-neighbour of the root, -1 if a mono-neighbour,
       0 if a non-neighbour. Using a disjoint u (not the within-window margin) preserves the
       integral_(margin(r)-tau) q(r) q(r)^T structure so honest graphons stay PSD (SOUND).
       Vertices used: root(1) + S_a(s) + S_b(s) + u(1) = 2s+2 (<= N required)."""
    k = 1
    m = flags[0][0]; s = m - k
    t = len(flags)
    flagidx = {fc.canonical_col(fm, fA, fcol, roots=k): i for i, (fm, fA, fcol) in enumerate(flags)}
    mats = []
    for (n, Ah, colh) in states:
        M = np.zeros((t, t))
        for r in range(n):
            if colh[r] != c:
                continue
            sr = side(colh[r]); Ar = Ah[r]
            rest = [v for v in range(n) if v != r]
            subs = list(itertools.combinations(rest, s))
            idxs = [flagidx.get(fs._flagkey_col(Ah, colh, (r,), S, k), -1) for S in subs]
            ssets = [set(S) for S in subs]
            for a in range(len(subs)):
                ia = idxs[a]
                if ia < 0: continue
                Sa = ssets[a]
                for b in range(len(subs)):
                    ib = idxs[b]
                    if ib < 0: continue
                    if Sa & ssets[b]: continue
                    used = {r} | Sa | ssets[b]
                    acc = 0.0
                    for u in rest:
                        if u in used: continue
                        if (Ar >> u) & 1:
                            wH = 1.0 if side(colh[u]) != sr else -1.0   # cut: +1, mono: -1
                        else:
                            wH = 0.0
                        acc += (tau - wH) if low else (wH - tau)
                    M[ia, ib] += acc
        mats.append(M)
    return mats


# colors: 0=A_L,1=A_H,2=B_L,3=B_H ; Low marks {0,2} (margin<=tau), High {1,3} (margin>=tau)
def color_is_low(c): return (c % 2) == 0


def build_all_localizers(states, tau, smax, ncol=4, triangle_free=True):
    """Return list of (color, low, flags, mats) for every color and flag order s=1..smax."""
    N = states[0][0]
    out = []
    for c in range(ncol):
        low = color_is_low(c)
        for s in range(1, smax + 1):
            m = 1 + s
            if 2 * s + 2 > N:    # root + 2 disjoint s-flags + 1 fresh H_sigma vertex u
                continue
            flags = localizer_flags(c, m, triangle_free=triangle_free)
            if len(flags) < 1:
                continue
            mats = psd_localizer_mats(states, c, tau, flags, low)
            out.append((c, low, flags, mats))
    return out


def Lc_on_density(mats, x):
    """L_c(x) = sum_state x_state mats[state]  (assemble the localizing matrix for a given density x)."""
    t = mats[0].shape[0]
    L = np.zeros((t, t))
    for xi, M in zip(x, mats):
        if xi != 0.0:
            L += xi * M
    return L


if __name__ == "__main__":
    # quick self-test: flag counts for each root color at N=6
    import flag_engine_kcol as kc
    print("=== PSD localizer self-test (flag counts) ===")
    for c in range(4):
        for s in (1, 2):
            fl = localizer_flags(c, 1 + s)
            print(f"  color {c} ({'A_L A_H B_L B_H'.split()[c]}) s={s} (m={1+s}): {len(fl)} rooted flags")
    print("DONE")
