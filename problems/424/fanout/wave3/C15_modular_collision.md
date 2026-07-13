# C15: exact modular collision-tax gate for the fixed affine subsystem

## Verdict

The exact inclusion-exclusion residue cap is far too weak for a scalar density
induction. At the strongest tested modulus \(M=30^4=810000\), it would require
a density floor greater than

\[
30\beta_M={26929\over33750}=0.797896296296\ldots,
\]

whereas the fixed affine subsystem has computed density below \(0.2\).
Consequently this scalar modular route is dead. A viable modular proof would
need statewise occupancy or a coupled pair-correlation recurrence.

This version corrects the triple-overlap audit: the three parent images meet
when \(6t,10t,15t\) are present, not when \(2t,3t,5t\) are present. The
correction is exact but numerically too small to change the verdict.

## Exact residue cap

Let \(B\) be the orbit under \(T_2,T_3,T_5\), and let \(R_M\) be its exact
residue orbit modulo \(M\). The Boolean recurrence has collision tax

\[
\Delta=P_{23}+P_{25}+P_{35}-P_{235}.
\]

Define

\[
\begin{aligned}
c_{23}&=\#\{t\bmod M:2t,3t\in R_M\},\\
c_{25}&=\#\{t\bmod M:2t,5t\in R_M\},\\
c_{35}&=\#\{t\bmod M:3t,5t\in R_M\},\\
c_{235}&=\#\{t\bmod M:6t,10t,15t\in R_M\}.
\end{aligned}
\]

Periodic counting gives

\[
\Delta(X)\le \beta_M X+O(M),
\qquad
\beta_M=
{c_{23}\over6M}+{c_{25}\over10M}+{c_{35}\over15M}
-{c_{235}\over30M}.
\]

A scalar strong induction with a density floor \(c\) therefore needs
\(\beta_M<c/30\).

## Exact results

| \(M\) | \(|R_M|\) | \(c_{23}\) | \(c_{25}\) | \(c_{35}\) | \(c_{235}\) | \(\beta_M\) | \(30\beta_M\) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 16 | 7 | 11 | 11 | 1 | \(89/900\) | \(89/30\) |
| 900 | 389 | 115 | 139 | 199 | 6 | \(173/3375\) | \(346/225\) |
| 27000 | 10150 | 2229 | 2966 | 3480 | 44 | \(26959/810000\) | \(26959/27000\) |
| 810000 | 275033 | 54131 | 74383 | 76799 | 1106 | \(26929/1012500\) | \(26929/33750\) |

In decimals the four \(\beta_M\) values are approximately

\[
0.098888889,\quad0.051259259,\quad0.033282716,\quad0.026596543.
\]

The decreasing finite trend is not extrapolated.

## Reproduction

~~~powershell
python problems/424/compute/wave3/C15_modular_collision/modular_collision.py --max-power 4
~~~

The script constructs every residue orbit exactly and asserts every integer
in the table.
