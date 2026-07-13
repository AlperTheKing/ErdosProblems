# C22: universal closure contraction is false

## Candidate

Let \(S\) be any subset of the allowed integers

\[
\mathcal A=\{n\ge 2:n\not\equiv1\pmod3\}
\]

containing \(2,3\) and closed under \(a,b\in S\), \(a<b\) implying
\(ab-1\in S\).  Put \(M_S(X)=|\mathcal A\cap[2,X]\setminus S|\), and
let \(R_S(X)\) count those holes \(n\le X\) for which \(n+1=ab\) has an
allowed factorization \(2\le a<b\).  The proposed universal inequality was

\[
R_S(X)\le M_S(\lfloor(X+1)/2\rfloor)
          +M_S(\lfloor(X+1)/3\rfloor).                 \tag{C22}
\]

The true least generated set \(G\) satisfies (C22) at every cutoff through
\(10^9\), but forward closure alone does not imply it.

## Exact counterexample

An exact CP-SAT optimization over every finite closed \(S\) at a fixed
cutoff finds the first violation at \(X=362\):

\[
R_S(362)=6,\qquad M_S(181)=3,\qquad M_S(121)=2.
\]

Thus the excess is \(1\).  The 37 allowed holes are

```text
6, 11, 146, 182, 186, 192, 198, 200, 210, 216, 218, 222, 228,
236, 240, 246, 252, 258, 270, 272, 276, 282, 288, 290, 291, 300,
306, 308, 312, 318, 326, 330, 336, 342, 348, 360, 362.
```

The model is genuinely forward-closed.  It is not the least closure of
\(\{2,3\}\): 34 included nonseed values have no included parent pair,
starting with

```text
8, 12, 18, 20, 21, 24, 30, 32, 36, 38, 42, 48, 54, 56, ...
```

At \(X=5000\), the exact optimum has excess 43, with

\[
R=105,\qquad M(2500)=41,\qquad M(1667)=21.
\]

## Consequence

Any proof of the C16 contraction for the actual set must use grounded
minimal generation: every nonseed member has a finite derivation tree from
\(2,3\) through strictly smaller factors.  A proof using only the Horn
implications

\[
s_a\wedge s_b\Longrightarrow s_{ab-1}
\]

cannot work.

## Reproduction

```powershell
python problems/424/compute/wave3/C22_universal_contraction_sat/universal_contraction_sat.py `
  --limit 5000 --workers 64 --time-limit 600 `
  --output problems/424/compute/wave3/C22_universal_contraction_sat/result_5000.json

python problems/424/compute/wave3/C22_universal_contraction_sat/scan_first_failure.py `
  --start 4 --stop 5000 --workers 64 --time-limit-per-cutoff 30 `
  --output problems/424/compute/wave3/C22_universal_contraction_sat/first_failure.json
```

The first command independently replays every closure constraint after
solving.  The second proves optimality at every cutoff from 4 through 362.
