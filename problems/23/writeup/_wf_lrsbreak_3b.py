"""LRS BREAKER family #3 (extension): drive |M| toward the N^2/25 boundary.

The single/stacked two-lanes have |M|=4..16 << N^2/25, so the +N^2/25-|M| slack is enormous and the
LRS family wins by hundreds. The ONLY regime where the slack is tight is |M| ~ N^2/25, realized at the
C5[t] blow-up (the extremal). There, PATH/ROW/LRS are all EXACTLY tight (margin 0) by construction.

Adversarial idea: GRAFT a two-lane load-concentrator onto a near-extremal C5[t] so that we keep
|M| close to N^2/25 (small slack) but PERTURB the load to be non-uniform (push some per-edge avg above
the extremal value). If any bad edge's local avg overshoots while |M| stays high, PATH-LRS could break.

We test:
  (1) pure C5[t] blow-ups t=1..6  -> confirm exact tightness (margin 0) at the boundary.
  (2) C5[t] with a few bad edges REMOVED (lower |M| slightly, raises slack) and ADDED chord stress.
  (3) C5[t] x two-lane bridge hybrids.
All under the HARD CP-SAT GLOBAL-max gate. Exact Fraction.

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
from fractions import Fraction as F
from _wf_lrsbreak_3 import evaluate, build_two_lane
from _h import maxcut_all, Bconn, gmin


def c5_blowup(t):
    n = 5 * t; E = []
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((i * t + a, ((i + 1) % 5) * t + b))
    # parity side: classes 0..4 around C5; 2-coloring of C5 is not proper (odd), so use the gamma-min cut.
    return n, sorted(set((min(a, b), max(a, b)) for a, b in E))


def best_side(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    r = gmin(n, adj, maxcut_all(n, adj))
    if r is None:
        return None
    return r[0]


if __name__ == "__main__":
    print("=== family #3b: |M| -> N^2/25 boundary stress ===", flush=True)
    results = []

    print("\n--- pure C5[t] blow-ups (expect EXACT tightness margin 0 at boundary) ---", flush=True)
    for t in range(1, 7):
        n, E = c5_blowup(t)
        if n > 30:
            print(f"[C5[{t}]] N={n} skipped (CP-SAT maxcut_all 2^(n-1) too slow for side; >30)", flush=True)
            continue
        s = best_side(n, E)
        if s is None:
            print(f"[C5[{t}]] no gamma-min cut", flush=True)
            continue
        r = evaluate(f"C5[{t}]", n, E, s, tlimit=120)
        if r:
            results.append(r)

    print("\n--- C5[t] x two-lane bridge (raise local load while |M| stays moderate) ---", flush=True)
    for t in (2, 3):
        for L in (8,):
            n1, E1 = c5_blowup(t)
            s1 = best_side(n1, E1)
            if s1 is None:
                continue
            n2, E2, s2, _ = build_two_lane(L)
            E2s = [(a + n1, b + n1) for a, b in E2]
            # bridge a C5[t] vertex to an opposite-side two-lane vertex
            tgt = None
            for cand in range(n2):
                if s2[cand] != s1[0]:
                    tgt = cand + n1; break
            E = list(E1) + E2s + ([(0, tgt)] if tgt is not None else [])
            s = list(s1) + list(s2)
            n = n1 + n2
            if n > 80:
                print(f"[C5[{t}]+TL{L}] N={n} skipped (>80)", flush=True)
                continue
            r = evaluate(f"C5[{t}]+TL{L}", n, sorted(set((min(a,b),max(a,b)) for a,b in E)), s, tlimit=180)
            if r:
                results.append(r)

    print("\n=== SUMMARY 3b ===", flush=True)
    valid = [r for r in results if r['global_max'] and r['tf'] and r['bc']]
    print(f"configs={len(results)} GLOBAL-max-valid={len(valid)}", flush=True)
    for form, key in (('B2', 'b2'), ('PATH-LRS', 'path'), ('ROW-LRS', 'row'), ('LRS', 'lrs')):
        if valid:
            worst = min(valid, key=lambda r: r[key])
            brk = [r for r in valid if form in r['breaks']]
            print(f"  {form:9s}: min margin = {float(worst[key]):+.6f} at {worst['name']} "
                  f"(N={worst['N']},|M|={worst['m']})  breakers={len(brk)}", flush=True)
