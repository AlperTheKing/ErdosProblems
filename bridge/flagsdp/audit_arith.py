from fractions import Fraction as F

LO = F(1243, 5000)
HI = F(3197, 10000)
T  = F(2, 25)

maxPhi_num = 12045893274065266971721
maxPhi_den = 198450000000000000000000000
delta = F(maxPhi_num, maxPhi_den)

print("=== Constants ===")
print("LO =", LO, "=", float(LO))
print("HI =", HI, "=", float(HI))
print("T  =", T, "=", float(T))
print("delta =", delta, "=", float(delta))
print()

# (1) Band coverage for N=30. density(e) = e/450 = 2e/30^2
N30 = 30
print("=== (1) Band coverage N=30, density(e)=e/450 ===")
print("N^2/2 =", N30**2//2, "; 2/N^2 =", F(2, N30**2), "; check e/450 == 2e/N^2:", F(1,450)==F(2,N30**2))
e_lo, e_hi = 112, 143
print(f"density({e_lo}) = {F(e_lo,450)} = {float(F(e_lo,450))}")
print(f"density({e_hi}) = {F(e_hi,450)} = {float(F(e_hi,450))}")
print(f"112/450 >= LO ? {F(112,450) >= LO}   (112/450={F(112,450)}, LO={LO})")
print(f"143/450 <= HI ? {F(143,450) <= HI}   (143/450={F(143,450)}, HI={HI})")
print(f"e<=111 -> density<=LO ? density(111)={F(111,450)} <= LO ? {F(111,450) <= LO}")
print(f"e>=144 -> density>=HI ? density(144)={F(144,450)} >= HI ? {F(144,450) >= HI}")
# No-gap check: edge band [112,143]; tail thresholds. Confirm 111 < LO boundary and 112 first >= LO
print(f"  boundary: is 111/450 < LO strictly? {F(111,450) < LO};  is 112 the smallest e with e/450>=LO? "
      f"{F(111,450) < LO and F(112,450) >= LO}")
print(f"  is 144/450 > HI strictly? {F(144,450) > HI};  is 143 the largest e with e/450<=HI? "
      f"{F(144,450) > HI and F(143,450) <= HI}")
print()

# (2) integrality: (25/2) n^2 delta < 1 for n=36, >=1 for n=37
print("=== (2) Integrality (25/2) n^2 delta ===")
for n in (36, 37):
    val = F(25,2) * n*n * delta
    print(f"n={n}: (25/2)*{n}^2*delta = {val} = {float(val)}  ;  < 1 ? {val < 1}  ;  >= 1 ? {val >= 1}")
print()

# (3) beta<=N^2/25 <=> d_mono=2 beta/N^2 <= 2/25
print("=== (3) Normalization beta<=N^2/25 <=> d_mono<=2/25 ===")
# d_mono = 2 beta / N^2.  beta <= N^2/25  <=>  2 beta/N^2 <= 2/25
# symbolic check across a few N with rational beta thresholds
ok = True
for N in (25, 30, 45, 100):
    thr_beta = F(N*N, 25)
    # d_mono at beta=thr_beta
    dmono = F(2, N*N) * thr_beta
    if dmono != F(2,25):
        ok = False
        print(f"  N={N}: MISMATCH d_mono={dmono}")
print(f"  beta=N^2/25 -> d_mono = 2/25 exactly for all tested N: {ok}")
print(f"  T (the d_mono bound used) == 2/25 ? {T == F(2,25)}")
print()

# (4) delta < 1/450
print("=== (4) delta < 1/450 (a(30) margin) ===")
print(f"delta = {float(delta)} ; 1/450 = {float(F(1,450))} ; delta < 1/450 ? {delta < F(1,450)}")
print(f"  exact: delta - 1/450 = {delta - F(1,450)} (negative => holds)")
print()

# (5) OEIS A389646: a(5)=1,a(10)=4,a(15)=9,a(20)=16
print("=== (5) a(5n)=n^2 sanity ===")
vals = {5:1,10:4,15:9,20:16}
allok = True
for fivn, claimed in vals.items():
    n = fivn//5
    if n*n != claimed:
        allok=False
    print(f"  a({fivn}) claimed {claimed}; (5n with n={n}) n^2={n*n}; match {n*n==claimed}")
print(f"  all match 1,4,9,16: {allok}")
print()

# Bonus: re-derive the n<=36 boundary purely. integer beta <= n^2 + (25/2) n^2 delta.
# floor of n^2 + epsilon == n^2 iff epsilon < 1.
print("=== Bonus: largest n with (25/2)n^2 delta < 1 ===")
n = 1
while F(25,2)*n*n*delta < 1:
    n += 1
print(f"  first n failing (>=1): {n}; so holds for n<= {n-1}")
