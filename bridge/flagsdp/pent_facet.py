"""
CUT-METRIC / PENTAGONAL angle, concrete test.

SETUP of the cut-metric reformulation:
  A 'cut' on V is S subset V, with semimetric d_S(x,y)=|1_S(x)-1_S(y)| (=1 iff exactly one of x,y in S).
  An L1 / cut metric is rho = sum_S lambda_S d_S, lambda_S>=0.
  Hypermetric (pentagonal) inequalities: for integer b_1..b_n with sum b_i = 1,
     sum_{i<j} b_i b_j rho(x_i,x_j) <= 0   holds for every L1 metric rho.
  The 5-point pentagonal case b=(1,1,1,-1,-1): sum over the K5 of b_i b_j rho_ij <= 0.

  The C5 graph metric is the canonical pentagonal-TIGHT metric:
  on C5 vertices 0..4, with b=(1,1,1,-1,-1) placed so the +'s are an independent set... let me just
  search the C5 shortest-path metric for the b-assignment giving equality (Q_b=0), as the prompt's
  'naive 5-subset min Q_b = -2' suggests the naive one is slack.

We test: which integer/biased weight vectors b make Q_b := sum_{i<j} b_i b_j d_C5(i,j) maximal (->0),
and whether a 'w-biased' (non sum-to-1) variant is tight.
"""
import itertools, numpy as np

# C5 shortest-path metric
d=np.zeros((5,5),int)
for i in range(5):
    for j in range(5):
        d[i,j]=min((i-j)%5,(j-i)%5)
print("C5 metric:\n",d)

def Q(b):
    s=0
    for i in range(5):
        for j in range(i+1,5):
            s+=b[i]*b[j]*d[i,j]
    return s

# naive pentagonal: b in {+1,+1,+1,-1,-1} permutations
best=-99; bestb=[]
for b in set(itertools.permutations([1,1,1,-1,-1])):
    q=Q(b)
    if q>best: best=q; bestb=[b]
    elif q==best: bestb.append(b)
print("\nnaive sum=1 pentagonal {3x+1,2x-1}: max Q_b =", best, " achieved by", bestb[:3])
# also the (2,-1,-1,-1,... ) hypermetric forms with sum=1, |b| up to 2
best2=-99; bestb2=[]
for b in itertools.product([-2,-1,0,1,2],repeat=5):
    if sum(b)!=1: continue
    q=Q(b)
    if q>best2: best2=q; bestb2=[b]
    elif q==best2 and len(bestb2)<8: bestb2.append(b)
print("all sum=1, |b|<=2 hypermetric: max Q_b =", best2, " by", bestb2[:8])
