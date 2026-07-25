import random, sys, itertools
sys.path.insert(0, r"C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\f1987d98-c6e4-47b0-90c4-e402adf2c40c\scratchpad\ktt")
import kt4

def parts(W, k):
    """all partitions of W into at most k parts (weakly decreasing, >=0)"""
    def rec(rem, mx, k):
        if k == 0:
            if rem == 0: yield ()
            return
        for t in range(min(rem, mx), -1, -1):
            for tail in rec(rem - t, t, k - 1):
                yield (t,) + tail
    return list(rec(W, W, k))

triples = []
# exhaustive small
for W in range(1, 11):
    for wl in range(0, W + 1):
        for lam in parts(wl, 4):
            for mu in parts(W - wl, 4):
                for nu in parts(W, 4):
                    triples.append((lam, mu, nu))
random.seed(7)
random.shuffle(triples)
sel = triples[:1200]

# random larger, biased to be nonzero: nu >= lam componentwise
rnd = []
while len(rnd) < 800:
    W = random.randint(12, 60)
    lam = tuple(sorted([random.randint(0, W // 3) for _ in range(4)], reverse=True))
    mu = tuple(sorted([random.randint(0, W // 3) for _ in range(4)], reverse=True))
    tot = sum(lam) + sum(mu)
    nu = tuple(sorted([random.randint(0, tot) for _ in range(4)], reverse=True))
    s = sum(nu)
    if s == 0: continue
    # rescale nu to have weight tot by adjusting largest part
    nu = list(nu)
    nu[0] += tot - s
    nu = tuple(sorted(nu, reverse=True))
    if any(nu[i] < lam[i] for i in range(4)): continue
    if any(nu[i] < mu[i] for i in range(4)): continue
    rnd.append((lam, mu, nu))

sel = sel + rnd
with open("val.batch", "w") as f:
    for lam, mu, nu in sel:
        f.write("%s;%s;%s\n" % (",".join(map(str, lam)), ",".join(map(str, mu)), ",".join(map(str, nu))))
with open("val.mine", "w") as f:
    for lam, mu, nu in sel:
        f.write("%d\n" % kt4.lr_coeff(lam, mu, nu))
nz = sum(1 for l in open("val.mine") if l.strip() != "0")
print("wrote", len(sel), "nonzero", nz)
