#!/usr/bin/env python3
"""
Validate the PSD-lifted margin localizers on order-6 blow-up graphon densities:
  (A) C5[n] extremal, honest marks       -> ALL L_c >> 0 (SOUND: extremal feasible), gsw=0.
  (B) bad-cut Clebsch, honest marks       -> gsw>0 (excluded by the margin SWITCH).
  (C) bad-cut Clebsch, EVASIVE re-marking  -> gsw<=0 (switch evaded) BUT some L_c NOT PSD
                                              (excluded by the LOCALIZER).
If (A) sound and (B)|(C) both excluded, then under EVERY marking the bad cut is excluded, while the
true extremal survives -> the PSD localizer + switch break the plateau soundly.
"""
import sys, time, itertools, math
import numpy as np
import flag_engine as fe, flag_engine_col as fc, flag_engine_kcol as kc
import flag_margin_sdp as ms, flag_psd_localizer as pl

N = 6
TAU = 1.0/8
SMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1
t0 = time.time()
print(f"enumerating N={N} states + index ...", flush=True)
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
key2idx = {}
for idx, (n, Ag, cg) in enumerate(states):
    key2idx[fc.canonical_col(n, Ag, cg, roots=0)] = idx
gsw = ms.margin_switch_vec(states)
print(f"  states={len(states)} [{time.time()-t0:.0f}s]; building PSD localizer mats (smax={SMAX}) ...", flush=True)
locs = pl.build_all_localizers(states, TAU, smax=SMAX)
print(f"  built {len(locs)} localizer blocks [{time.time()-t0:.0f}s]", flush=True)


def order6_density(D, adj, colf):
    x = np.zeros(len(states)); miss = 0.0
    for combo in itertools.combinations_with_replacement(range(D), 6):
        mult = {}
        for v in combo: mult[v] = mult.get(v, 0) + 1
        w = math.factorial(6)
        for mm in mult.values(): w //= math.factorial(mm)
        w /= D**6
        Asub = [0]*6; csub = [colf(combo[i]) for i in range(6)]
        for i in range(6):
            for j in range(i+1, 6):
                if combo[i] != combo[j] and adj(combo[i], combo[j]):
                    Asub[i] |= 1 << j; Asub[j] |= 1 << i
        idx = key2idx.get(fc.canonical_col(6, Asub, csub, roots=0))
        if idx is None: miss += w; continue
        x[idx] += w
    return x, miss


def report(name, x):
    g = float(gsw @ x)
    print(f"\n=== {name} ===  gsw@x = {g:+.6f}  ({'SWITCH fires (excluded)' if g > 1e-7 else 'switch inactive'})")
    worst = 1e9; worstc = None
    for (c, low, flags, mats) in locs:
        L = pl.Lc_on_density(mats, x)
        ev = np.linalg.eigvalsh(0.5*(L+L.T))
        mn = float(ev.min())
        tag = 'A_L A_H B_L B_H'.split()[c]
        flag = 'OK(>=0)' if mn >= -1e-7 else '*** NOT PSD ***'
        print(f"   L_c[c={c} {tag} {'Low' if low else 'High'} s={flags[0][0]-1} dim={len(flags)}] min_eig={mn:+.5f}  {flag}")
        if mn < worst: worst = mn; worstc = (c, tag)
    print(f"   -> worst min_eig over all blocks = {worst:+.5f} at {worstc}  "
          f"({'all PSD (feasible)' if worst >= -1e-7 else 'some block NOT PSD (excluded by localizer)'})")
    return g, worst


# (A) C5[n] honest marks: parts [A_L,B_H,A_H,B_H,A_L] = [0,3,1,3,0]
c5col = [0, 3, 1, 3, 0]
def c5adj(p, q): return (abs(p-q) == 1) or (abs(p-q) == 4)
xc, _ = order6_density(5, c5adj, lambda p: c5col[p])
gA, wA = report("(A) C5[n] extremal HONEST marks  [want: all PSD + gsw<=0]", xc)

# bad-cut Clebsch structure
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
def cadj(p, q): return bool((Acl[p] >> q) & 1)

# (B) honest marks (h<=2 -> Low)
colH = [0]*16
for v in range(16):
    dC = sum(1 for w in range(16) if (Acl[v] >> w) & 1 and sdc(w) != sdc(v))
    dM = sum(1 for w in range(16) if (Acl[v] >> w) & 1 and sdc(w) == sdc(v))
    colH[v] = 2*sdc(v) + (0 if (dC-dM) <= 2 else 1)
xbH, _ = order6_density(16, cadj, lambda p: colH[p])
gB, wB = report("(B) bad-cut Clebsch HONEST marks  [want: gsw>0 (switch excludes)]", xbH)

# (C) EVASIVE re-marking: mark EVERY vertex High (A_H/B_H) -> no A_L/B_L -> gsw forced 0
colE = [2*sdc(v) + 1 for v in range(16)]   # all High
xbE, _ = order6_density(16, cadj, lambda p: colE[p])
gC, wC = report("(C) bad-cut Clebsch EVASIVE all-High marks  [want: gsw<=0 BUT some L_c NOT PSD]", xbE)

print("\n================ VERDICT ================")
print(f"(A) C5[n] honest:  gsw={gA:+.4f} worstL={wA:+.4f} -> {'SOUND (extremal feasible)' if wA>=-1e-6 and gA<=1e-6 else '*** PROBLEM: extremal infeasible ***'}")
print(f"(B) bad honest:    gsw={gB:+.4f} -> {'excluded by SWITCH' if gB>1e-7 else 'NOT excluded by switch'}")
print(f"(C) bad evasive:   gsw={gC:+.4f} worstL={wC:+.4f} -> {'excluded by LOCALIZER' if wC<-1e-6 else ('still switch-excluded' if gC>1e-7 else '*** ESCAPES: gsw<=0 AND all L_c PSD ***')}")
ok = (wA >= -1e-6 and gA <= 1e-6) and (gB > 1e-7) and (wC < -1e-6 or gC > 1e-7)
print(f"\nOVERALL: {'PSD LOCALIZER + SWITCH SOUNDLY EXCLUDE BAD CUT UNDER ALL TESTED MARKINGS' if ok else 'INCONCLUSIVE — inspect blocks (may need larger smax or tau tweak)'}")
print("DONE")
