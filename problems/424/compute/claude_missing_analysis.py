"""Erdos 424 — missing-set structure at B (Claude acceptance lane).
Missing = allowed (n % 3 != 1, n >= 2) but not in G. Exact closure per G0.
Reports: per-decade missing counts, largest missing element seen, longest RUN of
consecutive allowed-but-missing integers, missing residue profile mod 9/12,
and smallest 40 missing elements (structure eyeball).
"""
import bisect, sys, hashlib
from collections import Counter

B = int(sys.argv[1]) if len(sys.argv) > 1 else 10**7
pool = [2, 3]; inset = {2, 3}; work = [2, 3]
while work:
    x = work.pop()
    lim = (B + 1) // x
    idx = bisect.bisect_right(pool, lim)
    for y in pool[:idx]:
        if y == x: continue
        z = x * y - 1
        if z <= B and z not in inset:
            inset.add(z); bisect.insort(pool, z); work.append(z)

missing = [n for n in range(2, B + 1) if n % 3 != 1 and n not in inset]
print("B =", B, " |G| =", len(inset), " |missing allowed| =", len(missing))
dec = 10
while dec <= B:
    lo, hi = dec // 10 if dec > 10 else 2, dec
    cnt = sum(1 for n in missing if lo < n <= hi)
    allowed = sum(1 for n in range(lo + 1, hi + 1) if n % 3 != 1)
    print(f"  ({lo},{hi}]: missing {cnt} / allowed {allowed}  frac {cnt/max(allowed,1):.4f}")
    dec *= 10
# longest run of consecutive allowed-missing (allowed integers adjacent in the allowed ordering)
allowed_sorted = missing
best_run, cur, prev = 1, 1, None
best_end = None
for n in missing:
    if prev is not None:
        gap_allowed = (n - prev) - ((n - prev) // 3)  # allowed count strictly between, approx via pattern
        consecutive = (n - prev in (1, 2)) and not any((prev < m < n and m % 3 != 1 and m in inset) for m in range(prev + 1, n))
        if n - prev <= 3 and consecutive:
            cur += 1
            if cur > best_run: best_run, best_end = cur, n
        else:
            cur = 1
    prev = n
print("longest consecutive-allowed missing run:", best_run, "ending at", best_end)
print("largest missing element:", missing[-1] if missing else None)
print("smallest 40 missing:", missing[:40])
for m in (9, 12):
    print(f"missing mod {m}:", dict(sorted(Counter(n % m for n in missing).items())))
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
