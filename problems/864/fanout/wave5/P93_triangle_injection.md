# P93: triangle injection audit and the phase-collision frontier

## Verdict

I do not prove or falsify the hole-conditioned candidate

\[
                         T_F(B,h)\le C_S(B,h).                 \tag{C84}
\]

The proposed support-fold injection is false (P95), and the larger one-step
hexagon target is also false (P92).  Two further global repairs fail exactly:
leaf peeling leaves a 2-core with more triangles than folds, and charging in
the order of the shared high mark has seven archived counterexamples.

There is a useful exact correction to an attempted simplification.  C84 is
**not** a pure ordered complementary-interval theorem.  An endpoint Sidon set
with positive defect has `C_S=182` and `T_F=200`; its unique nontrivial
triangle component has 165 folds and 200 triangles.  It fails both literal
holes.  Thus the phase hypothesis is essential.

The sharp surviving statement exposed by these tests is

\[
 T_F\le C_S+V_b,\qquad
 V_b=|\{(a,c,u,v)\in\mathcal F:a+c+b\in\Delta^+(B)\}|. \tag{1}
\]

The literal hole gives `V_b=0`, so (1) would prove C84.  It has zero failures
in the exact corpora reported below, but no global phase-collision charge is
proved here.  Equation (1) is therefore a candidate, not a lemma.

## 1. Complementary interval form

Every canonical fold

\[
 a+c+h=u+v,\qquad a\le c<u\le v                       \tag{2}
\]

is equivalently a nested pair of represented intervals

\[
 [c,u]\subset[a,v],\qquad (u-c)+(v-a)=h.              \tag{3}
\]

Because `B` is Sidon, every positive length has at most one representing
interval.  Hence a fold is uniquely indexed by its inner length `d=u-c`;
its outer interval is the unique interval of length `h-d`.

For a loose triangle, retain the P83 notation

\[
\begin{array}{lll}
F_0=(a,c,u+R,s),&F_Z=(a,c+Z,u,s+R+Z),
&F_X=(a+X,c,u,s+R+X).                                  \tag{4}
\end{array}
\]

Thus the three folds share, respectively, their outer left endpoint `a`,
their inner left endpoint `c`, and their inner right endpoint `u`.  This is
the exact three-arm compatibility that any proof of (1) must retain.

## 2. Exact failure of the pure-order claim

Take `h=3286` and

```text
B={0,122,163,328,351,488,499,528,553,681,837,838,920,941,
1051,1070,1117,1322,1340,1414,1449,1520,1608,1613,1617,
1715,1853,1866,1925,2057,2074,2153,2173,2240,2320,2380,
2475,2521,2564,2596,2598,2654,2788,2815,2839,2901,2950,
2958,3026,3070,3076,3131,3170,3184,3200,3212,3215,3222,
3248,3285}.
```

All 1,830 diagonal-inclusive unordered sums and all 1,770 positive
differences are distinct.  Exact enumeration gives

\[
 p=60,\quad \delta=2085>0,\quad C_S=182,\quad T_F=200. \tag{5}
\]

The loose-triangle hypergraph has one component with 165 fold vertices and
200 triangle edges, so even the componentwise pure-order form fails by 35.
For both `b=1` and `b=2`, `Delta+(B)` meets `B+B+b`; this does not falsify
the original C84.

## 3. Failed global charges

On the P94 maximum hole row `(C_S,T_F)=(142,116)`, all 116 non-isolated
folds form one component with 116 triangles.  Its iterative degree-at-most-one
peeling leaves 64 folds and 75 triangles.  Consequently neither support Hall
matching nor leaf induction proves the component count.

Grouping triangles by the shared high mark `u` suggests the prefix charge

\[
 \sum_{q\le U}T(q)\le\sum_{q\le U}C(q).                \tag{6}
\]

It is false.  Among 313,863 archived positive-defect literal holes there are
seven failures.  The maximum prefix excess is one, at

\[
 (p,h,b,\delta,C_S,T_F)=(104,14526,2,1647,135,93),
 \quad U=12312.                                        \tag{7}
\]

Thus a valid charge cannot be a nested deadline assignment in any one fold
coordinate.  P92 and P95 separately show that enlarging each triangle only
to its three support folds or its one-step signed hexagon still violates
Hall.

## 4. Exact audits and boundary

`compute/p93/audit_triangle_components.py` checks every positive-defect
literal-hole translation of all 2,526 P86 archived rulers.  It covers
313,863 holes, finds zero component failures, records the sharp `116=116`
component, the `75-64=11` 2-core excess, and the seven prefix failures.

`compute/p93/verify_pure_order_counterexample.py` independently reconstructs
all sums, differences, folds, triangles, components, defect, and both failed
literal-hole tests for (5).  Run

```powershell
python -m py_compile problems/864/compute/p93/*.py
python -B problems/864/compute/p93/verify_pure_order_counterexample.py
python -B problems/864/compute/p93/audit_triangle_components.py --workers 16
```

The exact data support (1), including the unrestricted width-30 and P88
translation scans supplied with this wave.  They do not prove (1), C84, or a
componentwise hole theorem.  The remaining proof obligation is a total,
nonlocal charge from loose triangles to all canonical folds, with a second
unit of capacity allowed exactly at the phase-collision folds counted by
`V_b`.
