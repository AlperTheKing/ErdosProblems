# P91: the four-part fold-shadow K4 shortcut is false

For `b=1`, a fold `a+c+h=u+v` can be written

`a+c+(H-v)+(H-u)=H-1`, where `H=h-1`.

It is tempting to put the four coordinates in four labelled parts, join all
six pairs occurring in a fold, and use graph removal on the resulting
edge-disjoint canonical `K4`s. The missing assertion would be that the
literal hole excludes every noncanonical `K4`.

The P75 positive-defect literal-hole row falsifies this. Its 51 folds have
all six two-coordinate projections injective, but their four-part shadow has
106 `K4`s: 51 canonical and 55 noncanonical. For example,

`(a,c,H-v,H-u)=(3,329,10,356)`

is a noncanonical clique. Its coordinate sum is 698 rather than the
forbidden endpoint phase 987, so the unweighted clique condition loses the
phase exactly as the three-part loose-triangle shadow does.

Exact verifier: `compute/p91/verify_fourpart_k4_counterexample.py`.
