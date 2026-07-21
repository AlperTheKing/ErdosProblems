# Root-depth-only surplus bound: exact counterexample

The active-component capacity cannot be replaced by its rooted eccentricity.
On graph6

    \hCGGC@?G?_@?@??_?G?@_?C??_??G??C??@???G???_??@?_?@C???????G???@????C

the exact parameters are `n=29,g=17,r=e=8,D=13`.  For the shortest cycle

    K={6,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23,24},

take `x=15,h=1,m=14,z=7`.  The x-component is

    H={0,1,2,3,4,5,15,16,25,26,27,28}.

It has `|E_H cap W|=13`.  Its maximum distance from the auxiliary root in
`J_z(H)` is only `R_z(H)=7`, so the tempting depth-only x-surplus inequality

    |E_H cap W| <= 2(R_z(H)-h)

reads `13<=12` and is false.  Exact induced rooted capacity is much larger:
`mu_z(H)=11`, so the actual capacity inequality has slack `7`.

Thus any proof of the active-component bound must use branching inside the
maximum rooted induced tree, not just the deepest rooted geodesic.
