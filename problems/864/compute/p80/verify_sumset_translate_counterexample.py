from collections import Counter
from hashlib import sha256


B = [
    0, 6, 13, 85, 89, 121, 141, 152, 196, 245,
    247, 257, 274, 327, 345, 370, 404, 418, 439, 444,
    472, 536, 558, 573, 581, 582, 620, 623, 639,
]
h = 640
p = len(B)

sums = Counter(x + y for i, x in enumerate(B) for y in B[i:])
diffs = Counter(y - x for i, x in enumerate(B) for y in B[i + 1 :])
folds = sorted(s for s in sums if s + h in sums)

assert min(B) == 0 and max(B) == h - 1
assert len(sums) == p * (p + 1) // 2 == 435
assert max(sums.values()) == 1
assert len(diffs) == p * (p - 1) // 2 == 406
assert max(diffs.values()) == 1
assert len(folds) == 58 > 2 * p - 1 == 57
assert sha256(",".join(map(str, B)).encode("ascii")).hexdigest() == (
    "cdd6607fd6bfcd330359251fc3ff89656"
    "b0f4087dd21772f2515ef392d90c3fb"
)

print({"p": p, "h": h, "C_S": len(folds), "bound": 2 * p - 1})
