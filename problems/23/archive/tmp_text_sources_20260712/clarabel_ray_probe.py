import clarabel
import numpy as np
from scipy.sparse import csc_matrix
# infeasible: x <= -1 and x >= 0 encoded as A x + s = b, s >= 0:
# [1]x + s1 = -1, [-1]x + s2 = 0.
P = csc_matrix((1,1), dtype=float)
q = np.array([0.0])
A = csc_matrix(np.array([[1.0],[-1.0]]))
b = np.array([-1.0, 0.0])
cones = [clarabel.NonnegativeConeT(2)]
settings = clarabel.DefaultSettings()
settings.verbose = False
solver = clarabel.DefaultSolver(P, q, A, b, cones, settings)
sol = solver.solve()
print('status', sol.status)
print('attrs', [a for a in dir(sol) if not a.startswith('_')])
print('x', sol.x)
print('z', sol.z)
print('s', sol.s)
print('ATz', A.T @ np.array(sol.z))
print('btz', float(b @ np.array(sol.z)))
