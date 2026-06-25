#!/usr/bin/env python3
"""
EXACT order-6 pre-test (multiset enumeration, no Monte Carlo) for TWO blow-up graphons:
  (1) the bad-cut Clebsch  -> margin switch SHOULD fire (gsw@x > 0 => excluded). [desired]
  (2) the true extremal C5[n] with honest margin marks -> margin switch MUST NOT fire
      (gsw@x <= 0) and all localizers/basic-switch satisfied, ELSE the constraint is UNSOUND
      (it would exclude the real extremal => false bound).
Also prints d_edge for each (C5[n] has d_edge=0.40; the default SDP band (0.2486,0.32) does NOT
contain it -- flagged for the soundness audit).
Order-6 density of a balanced blow-up graphon = sum over size-6 multisets of base vertices,
weighted by the multinomial probability (6!/prod m!)/D^6, of the induced colored 6-graph.
"""
import numpy as np, itertools, math
import flag_engine as fe, flag_engine_col as fc, flag_engine_kcol as kc, flag_margin_sdp as ms

N = 6

def order6_density(D, adj, colf):
    """adj(p,q)->bool base adjacency on D vertices; colf(p)->4-color. Returns x over enumerated states."""
    states = order6_density.states
    key2idx = order6_density.key2idx
    x = np.zeros(len(states))
    miss = 0
    cache = {}
    for combo in itertools.combinations_with_replacement(range(D), 6):
        mult = {}
        for v in combo: mult[v] = mult.get(v, 0) + 1
        w = math.factorial(6)
        for m in mult.values(): w //= math.factorial(m)
        w /= D**6
        ck = cache.get(combo)
        if ck is None:
            Asub = [0]*6; csub = [colf(combo[i]) for i in range(6)]
            for i in range(6):
                for j in range(i+1, 6):
                    if combo[i] != combo[j] and adj(combo[i], combo[j]):
                        Asub[i] |= 1 << j; Asub[j] |= 1 << i
            ck = fc.canonical_col(6, Asub, csub, roots=0)
            cache[combo] = ck
        idx = key2idx.get(ck)
        if idx is None: miss += w; continue
        x[idx] += w
    return x, miss

print(f"enumerating N={N} 4-colored triangle-free states ...", flush=True)
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
key2idx = {}
for idx, (n, Ag, cg) in enumerate(states):
    key2idx[fc.canonical_col(n, Ag, cg, roots=0)] = idx
order6_density.states = states
order6_density.key2idx = key2idx
gsw = ms.margin_switch_vec(states); locs = ms.localizer_vecs(states)
dmono = ms.d_mono_vec(states); dedge = ms.d_edge_vec(states)
basic0 = 2*dmono - dedge
print(f"  states={len(states)}", flush=True)

def report(name, x, miss):
    print(f"\n=== {name} ===  (missing weight on non-tri-free/over-N states: {miss:.2e})")
    print(f"  d_edge = {dedge@x:.5f}   d_mono = {dmono@x:.5f}   (beta/N^2 = {(dmono@x)/2:.5f})")
    g = float(gsw@x)
    print(f"  MARGIN SWITCH gsw@x = {g:+.6f}")
    print(f"  basic side-sw0 (2dmono-dedge) = {basic0@x:+.5f}  [<=0 ok]")
    for c in range(4):
        lv = float(locs[c]@x)
        print(f"  localizer color {c} ({'A_L A_H B_L B_H'.split()[c]}): {lv:+.6f}  [{'OK<=0' if lv<=1e-9 else 'VIOLATED'}]")
    return g

# ---- (1) bad-cut Clebsch ----
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
Acl = [0]*16
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4: Acl[i] |= 1 << j
lab2idx = {labels[i]: i for i in range(16)}
def sub(*vs):
    m = 0
    for v in vs: m |= 1 << (v-1)
    return lab2idx[m]
A0 = {sub(), sub(1,2), sub(1,3), sub(2,3), sub(1,4), sub(2,4), sub(1,5), sub(2,5)}
def sdc(v): return 0 if v in A0 else 1
colcl = [0]*16
for v in range(16):
    dC = sum(1 for w in range(16) if (Acl[v] >> w) & 1 and sdc(w) != sdc(v))
    dM = sum(1 for w in range(16) if (Acl[v] >> w) & 1 and sdc(w) == sdc(v))
    colcl[v] = 2*sdc(v) + (0 if (dC-dM) <= 2 else 1)
xb, mb = order6_density(16, lambda p, q: bool((Acl[p] >> q) & 1), lambda p: colcl[p])
gb = report("bad-cut Clebsch blow-up [want gsw>0 EXCLUDED]", xb, mb)

# ---- (2) true extremal C5[n] with honest margin marks ----
# C5: 0-1-2-3-4-0. maxcut 2-coloring sideA={0,2,4}, sideB={1,3}; 1 mono super-edge (4,0).
# honest marks: parts 0,4 -> A_L(0); part2 -> A_H(1); parts1,3 -> B_H(3). (no B_L)
c5col = [0, 3, 1, 3, 0]
def c5adj(p, q): return (abs(p-q) == 1) or (abs(p-q) == 4)   # 5-cycle adjacency on 0..4
xc, mc = order6_density(5, c5adj, lambda p: c5col[p])
gc = report("C5[n] extremal blow-up [SOUNDNESS: gsw MUST be <=0]", xc, mc)

print("\n================ VERDICT ================")
print(f"bad-cut gsw@x = {gb:+.6f}  -> {'EXCLUDED at order-6 (good, N=6 can bite)' if gb>1e-6 else 'NOT excluded at order-6 (need N=7 or PSD localizers)'}")
print(f"C5[n]   gsw@x = {gc:+.6f}  -> {'SOUND (<=0, extremal survives)' if gc<=1e-6 else '*** UNSOUND: margin switch excludes the TRUE extremal! ***'}")
print("DONE")
