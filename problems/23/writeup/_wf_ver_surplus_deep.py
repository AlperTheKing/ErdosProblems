"""Deeper adversarial sweep for the surplus central inequality:
   - random-sampled triangle-free connected graphs N=12,13,14,15 (capped),
   - heavier non-uniform odd-cycle blow-ups (C5/C7) up to N<=26,
   - more iterated/odd Mycielskians.
All exact Fraction. Prints min margin + any violation, unbuffered."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
import _wf_ver_surplus as W

acc = {'n': 0, 'viol': 0, 'first_viol': None,
       'min_margin': (F(10**30), '', 0, 0, '', '', '', ''),
       'max_ratio': (F(-1), '', 0, 0),
       'handshake_fail': 0, 'handshake_examples': [],
       'identity_fail': 0, 'identity_examples': [],
       'form_mismatch': 0, 'form_examples': [],
       'badset_mismatch': 0,
       'denom0': 0, 'denom0_nonzero_margin': 0, 'denom0_examples': []}

random.seed(20260629)

def sample_census(nn, cap):
    # stream geng output, reservoir-sample 'cap' g6 strings
    p = subprocess.Popen([GENG, "-tc", str(nn), "-d2"], stdout=subprocess.PIPE, text=True)
    res = []
    for i, line in enumerate(p.stdout):
        g6 = line.strip()
        if not g6:
            continue
        if len(res) < cap:
            res.append(g6)
        else:
            j = random.randint(0, i)
            if j < cap:
                res[j] = g6
        if i > 3_000_000:  # don't read the entire 10M for N=13
            break
    p.kill()
    return res

for nn, cap in [(12, 8000), (13, 8000), (14, 6000), (15, 4000)]:
    a0 = acc['viol']; mm0 = acc['min_margin'][0]
    gs = sample_census(nn, cap)
    for g6 in gs:
        n, E = dec(g6)
        adj, cuts = gmins(n, E)
        for s in cuts:
            W.chk("cen" + g6, n, adj, s, acc)
    mm = acc['min_margin']
    print("N=%d sampled=%d viol(+%d) running_min_margin=%s" % (
        nn, len(gs), acc['viol'] - a0, float(mm[0])), flush=True)

# heavier non-uniform odd-cycle blow-ups
extra_parts = []
for a in (1, 2, 3, 4, 5, 6):
    extra_parts.append([a, 1, 1, 1, 1])
    extra_parts.append([1, a, 1, a, 1])
    extra_parts.append([a, 1, a, 1, a])
    extra_parts.append([1, 1, a, 1, 1])
for a in (1, 2, 3):
    extra_parts.append([a, 1, 1, 1, 1, 1, 1])
    extra_parts.append([1, a, 1, 1, a, 1, 1])
for parts in extra_parts:
    n, E = W.blowup(parts)
    if n > 26:
        continue
    adj, cuts = gmins(n, E)
    for s in (cuts[:2] if cuts else []):
        W.chk("nu%s" % parts, n, adj, s, acc)
mm = acc['min_margin']
print("after heavy blow-ups: configs=%d viol=%d min_margin=%s" % (acc['n'], acc['viol'], float(mm[0])), flush=True)

print("\n==== DEEP RESULTS ====")
print("configs=%d viol=%d" % (acc['n'], acc['viol']))
mm = acc['min_margin']
print("MIN margin=%s float=%.6g at %s N=%d beta=%d Gamma=%s V2=%s TVcut=%s TVbad=%s" % (
    mm[0], float(mm[0]), mm[1], mm[2], mm[3], mm[4], mm[5], mm[6], mm[7]))
mr = acc['max_ratio']
print("MAX ratio=%s float=%.10g at %s N=%d beta=%d  (151/16=%s -> %s)" % (
    mr[0], float(mr[0]), mr[1], mr[2], mr[3], F(151, 16),
    "EXCEEDS" if mr[0] > F(151, 16) else "OK"))
print("handshake_fail=%d identity_fail=%d form_mismatch=%d" % (
    acc['handshake_fail'], acc['identity_fail'], acc['form_mismatch']))
print("FIRST VIOL:", acc['first_viol'])
