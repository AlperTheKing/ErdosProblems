import math
c = 1.094272  # from SDP on C5[3]
print("c* =", c)
print("beta5 =", 5/(2+2*math.cos(math.pi/5)))
print("1/(2-2cos(2pi/5)) =", 1/(2-2*math.cos(2*math.pi/5)))
print("1/(2cos(pi/5)-... )")
print("2-2cos(2pi/5) =", 2-2*math.cos(2*math.pi/5))
print("(5-2*sqrt5)? ", )
print("cand 5/(2+2cos(pi/5)) - something")
# C5 eigenvalues of L: 2-2cos(2pi k/5), k=0..4
for k in range(5):
    print("k", k, "Llam=", 2-2*math.cos(2*math.pi*k/5))
# the tight extremal: deficit N-T. On C5[3], N=15, each part size 3.
# guess c* relation: maybe c* = beta5 * (something) or 1/(2*(1-cos(2pi/5)))
print("1/(2*(1-cos(2pi/5)))=", 1/(2*(1-math.cos(2*math.pi/5))))
print("ratio c*/beta5 =", c/(5/(2+2*math.cos(math.pi/5))))
# is c* = (1+sqrt5)/... golden?
phi=(1+math.sqrt(5))/2
print("phi=",phi,"1/phi=",1/phi, "phi-1=",phi-1)
print("c* vs (5+sqrt5)/... ", (5+math.sqrt(5)))
print("c* * (2-2cos(2pi/5)) =", c*(2-2*math.cos(2*math.pi/5)))
print("c* candidate exact 1/(2-2cos(2pi/5)):", 1/(2-2*math.cos(2*math.pi/5)))
